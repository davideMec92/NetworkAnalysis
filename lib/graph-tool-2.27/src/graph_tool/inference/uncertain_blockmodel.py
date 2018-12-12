#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# graph_tool -- a general graph manipulation python module
#
# Copyright (C) 2006-2018 Tiago de Paula Peixoto <tiago@skewed.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import division, absolute_import, print_function
import sys
if sys.version_info < (3,):
    range = xrange

from .. import _degree, _prop, Graph, GraphView, libcore, _get_rng, \
    PropertyMap, edge_endpoint_property

from .. dl_import import dl_import
dl_import("from . import libgraph_tool_inference as libinference")

from . blockmodel import *
from . nested_blockmodel import *
from . blockmodel import _bm_test

def get_uentropy_args(kargs):
    ea = get_entropy_args(kargs, ignore=["latent_edges", "density"])
    uea = libinference.uentropy_args(ea)
    uea.latent_edges = kargs.get("latent_edges", True)
    uea.density = kargs.get("density", True)
    return uea

class UncertainBaseState(object):
    r"""Base state for uncertain network inference."""

    def __init__(self, g, nested=True, state_args={}, bstate=None,
                 self_loops=False, init_empty=False):

        self.g = g

        if bstate is None:
            if init_empty:
                self.u = Graph(directed=g.is_directed())
                self.u.add_vertex(g.num_vertices())
                self.eweight = self.u.new_ep("int", val=1)
            elif "g" in state_args:
                self.u = state_args.pop("g")
                self.eweight = state_args.pop("eweight",
                                              self.u.new_ep("int", val=1))
            else:
                self.u = g.copy()
                self.eweight = self.u.new_ep("int", val=1)
        else:
            self.u = bstate.g
            if nested:
                self.eweight = bstate.levels[0].eweight
            else:
                self.eweight = bstate.eweight
        self.u.set_fast_edge_removal()

        self.self_loops = self_loops
        N = self.u.num_vertices()
        if self.u.is_directed():
            if self_loops:
                M = N * N
            else:
                M = N * (N - 1)
        else:
            if self_loops:
                M = (N * (N + 1)) / 2
            else:
                M = (N * (N - 1)) / 2

        self.M = M

        if bstate is None:
            if nested:
                state_args["state_args"] = state_args.get("state_args", {})
                state_args["state_args"]["eweight"] = self.eweight
                state_args["sampling"] = True
                self.nbstate = NestedBlockState(self.u, **dict(state_args,
                                                               sampling=True))
                self.bstate = self.nbstate.levels[0]
            else:
                self.nbstate = None
                self.bstate = BlockState(self.u, eweight=self.eweight,
                                         **state_args)
        else:
            if nested:
                self.nbstate = bstate
                self.bstate = bstate.levels[0]
            else:
                self.nbstate = None
                self.bstate = bstate

        edges = self.g.get_edges()
        edges = numpy.concatenate((edges,
                                   numpy.ones(edges.shape,
                                              dtype=edges.dtype) * (N + 1)))
        self.slist = Vector_size_t(init=edges[:,0])
        self.tlist = Vector_size_t(init=edges[:,1])

        init_q_cache()

    def get_block_state(self):
        """Return the underlying block state, which can be either
        :class:`~graph_tool.inference.blockmodel.BlockState` or
        :class:`~graph_tool.inference.nested_blockmodel.NestedBlockState`.
        """
        if self.nbstate is None:
            return self.bstate
        else:
            return self.nbstate

    def entropy(self, latent_edges=True, density=True, **kwargs):
        """Return the entropy, i.e. negative log-likelihood."""
        if self.nbstate is None:
            S = self._state.entropy(latent_edges, density) + \
                self.bstate.entropy(**kwargs)
        else:
            S = self._state.entropy(latent_edges, density) + \
                self.nbstate.entropy(**kwargs)

        if kwargs.get("test", True) and _bm_test():
            assert not isnan(S) and not isinf(S), \
                "invalid entropy %g (%s) " % (S, str(args))

            args = kwargs.copy()
            args["test"] = False
            state_copy = self.copy()
            Salt = state_copy.entropy(latent_edges, density, **args)

            assert math.isclose(S, Salt, abs_tol=1e-8), \
                "entropy discrepancy after copying (%g %g %g)" % (S, Salt,
                                                                  S - Salt)
        return S

    def virtual_remove_edge(self, u, v, entropy_args={}):
        dentropy_args = dict(self.bstate._entropy_args, **entropy_args)
        entropy_args = get_uentropy_args(dentropy_args)
        return self._state.remove_edge_dS(int(u), int(v), entropy_args)

    def virtual_add_edge(self, u, v, entropy_args={}):
        dentropy_args = dict(self.bstate._entropy_args, **entropy_args)
        entropy_args = get_uentropy_args(dentropy_args)
        return self._state.add_edge_dS(int(u), int(v), entropy_args)

    def _algo_sweep(self, algo, r=.5, **kwargs):

        kwargs = kwargs.copy()
        beta = kwargs.get("beta", 1.)
        niter = kwargs.get("niter", 1)
        verbose = kwargs.get("verbose", False)
        slist = self.slist
        tlist = self.tlist
        dentropy_args = dict(self.bstate._entropy_args,
                             **kwargs.get("entropy_args", {}))
        entropy_args = get_uentropy_args(dentropy_args)
        kwargs.get("entropy_args", {}).pop("latent_edges", None)
        kwargs.get("entropy_args", {}).pop("density", None)
        state = self._state
        mcmc_state = DictState(locals())

        if _bm_test():
            Si = self.entropy(**dentropy_args)

        if self.nbstate is None:
            self.bstate._clear_egroups()
        else:
            self.nbstate._clear_egroups()
        if numpy.random.random() < r:
            edges = True
            dS, nattempts, nmoves = self._mcmc_sweep(mcmc_state)
        else:
            edges = False
            if self.nbstate is None:
                dS, nattempts, nmoves = algo(self.bstate, **kwargs)
            else:
                dS, nattempts, nmoves = algo(self.nbstate, **kwargs)

        if _bm_test():
            Sf = self.entropy(**dentropy_args)
            assert math.isclose(dS, (Sf - Si), abs_tol=1e-8), \
                "inconsistent entropy delta %g (%g): %s %s" % (dS, Sf - Si, edges,
                                                               str(dentropy_args))

        return dS, nattempts, nmoves

    def mcmc_sweep(self, r=.5, **kwargs):
        r"""Perform sweeps of a Metropolis-Hastings acceptance-rejection sampling MCMC to
        sample network partitions and latent edges. The parameter ``r```
        controls the probability with which edge move will be attempted, instead
        of partition moves. The remaining keyword parameters will be passed to
        :meth:`~graph_tool.inference.blockmodel.BlockState.mcmc_sweep`.
        """

        return self._algo_sweep(lambda s, **kw: s.mcmc_sweep(**kw),
                                r=r, **kwargs)

    def multiflip_mcmc_sweep(self, r=.5, **kwargs):
        r"""Perform sweeps of a multiflip Metropolis-Hastings acceptance-rejection
        sampling MCMC to sample network partitions and latent edges. The
        parameter ``r``` controls the probability with which edge move will be
        attempted, instead of partition moves. The remaining keyword parameters
        will be passed to :meth:`~graph_tool.inference.blockmodel.BlockState.multiflip_mcmc_sweep`.
        """

        return self._algo_sweep(lambda s, **kw: s.multiflip_mcmc_sweep(**kw),
                                r=r, **kwargs)

    def get_edge_prob(self, u, v, entropy_args={}, epsilon=1e-8):
        r"""Return conditional posterior probability of edge :math:`(u,v)`."""
        entropy_args = dict(self.bstate._entropy_args, **entropy_args)
        ea = get_uentropy_args(entropy_args)
        return self._state.get_edge_prob(u, v, ea, epsilon)

    def get_edges_prob(self, elist, entropy_args={}, epsilon=1e-8):
        r"""Return conditional posterior probability of an edge list, with
        shape :math:`(E,2)`."""
        entropy_args = dict(self.bstate._entropy_args, **entropy_args)
        ea = get_uentropy_args(entropy_args)
        elist = numpy.asarray(elist, dtype="uint64")
        probs = numpy.zeros(elist.shape[0])
        self._state.get_edges_prob(elist, probs, ea, epsilon)
        return probs

    def get_graph(self):
        r"""Return the current inferred graph."""
        if self.self_loops:
            u = GraphView(self.u, efilt=self.eweight.fa > 0)
        else:
            es = edge_endpoint_property(self.u, self.u.vertex_index, "source")
            et = edge_endpoint_property(self.u, self.u.vertex_index, "target")
            u = GraphView(self.u, efilt=numpy.logical_and(self.eweight.fa > 0,
                                                          es.fa != et.fa))
        return u

    def collect_marginal(self, g=None):
        r"""Collect marginal inferred network during MCMC runs.

        Parameters
        ----------
        g : :class:`~graph_tool.Graph` (optional, default: ``None``)
            Previous marginal graph.

        Returns
        -------
        g : :class:`~graph_tool.Graph`
            New marginal graph, with internal edge :class:`~graph_tool.PropertyMap`
            ``"eprob"``, containing the marginal probabilities for each edge.

        Notes
        -----
        The posterior marginal probability of an edge :math:`(i,j)` is defined as

        .. math::

           \pi_{ij} = \sum_{\boldsymbol A}A_{ij}P(\boldsymbol A|\boldsymbol D)

        where :math:`P(\boldsymbol A|\boldsymbol D)` is the posterior
        probability given the data.

        """

        if g is None:
            g = Graph(directed=self.g.is_directed())
            g.add_vertex(self.g.num_vertices())
            g.gp.count = g.new_gp("int", 0)
            g.ep.count = g.new_ep("int")

        if "eprob" not in g.ep:
            g.ep.eprob = g.new_ep("double")

        u = self.get_graph()
        libinference.collect_marginal(g._Graph__graph,
                                      u._Graph__graph,
                                      _prop("e", g, g.ep.count))
        g.gp.count += 1
        g.ep.eprob.fa = g.ep.count.fa
        g.ep.eprob.fa /= g.gp.count
        return g

class UncertainBlockState(UncertainBaseState):
    r"""The inference state of an uncertain graph, using the stochastic block model
    as a prior.

    Parameters
    ----------
    g : :class:`~graph_tool.Graph`
        Measured graph.
    q : :class:`~graph_tool.PropertyMap`
        Edge probabilities in range :math:`[0,1]`.
    q_default : ``float`` (optional, default: ``0.``)
        Non-edge probability in range :math:`[0,1]`.
    aE : ``float`` (optional, default: ``NaN``)
        Expected total number of edges used in prior. If ``NaN``, a flat
        prior will be used instead.
    nested : ``boolean`` (optional, default: ``True``)
        If ``True``, a :class:`~graph_tool.inference.nested_blockmodel.NestedBlockState`
        will be used, otherwise
        :class:`~graph_tool.inference.blockmodel.BlockState`.
    state_args : ``dict`` (optional, default: ``{}``)
        Arguments to be passed to
        :class:`~graph_tool.inference.nested_blockmodel.NestedBlockState` or
        :class:`~graph_tool.inference.blockmodel.BlockState`.
    bstate : :class:`~graph_tool.inference.nested_blockmodel.NestedBlockState` or :class:`~graph_tool.inference.blockmodel.BlockState`  (optional, default: ``None``)
        If passed, this will be used to initialize the block state
        directly.
    self_loops : bool (optional, default: ``False``)
        If ``True``, it is assumed that the uncertain graph can contain
        self-loops.

    References
    ----------
    .. [peixoto-reconstructing-2018] Tiago P. Peixoto, "Reconstructing networks
       with unknown and heterogeneous errors" :arxiv:`1806.07956`

    """

    def __init__(self, g, q, q_default=0., aE=numpy.nan, nested=True, state_args={},
                 bstate=None, self_loops=False, **kwargs):

        super(UncertainBlockState, self).__init__(g, nested=nested,
                                                  state_args=state_args,
                                                  bstate=bstate,
                                                  self_loops=self_loops,
                                                  **kwargs)
        self._q = q
        self._q_default = q_default

        self.p = (q.fa.sum() + (self.M - g.num_edges()) * q_default) / self.M

        self.q = self.g.new_ep("double", vals=log(q.fa) - log1p(-q.fa))
        self.q.fa -= log(self.p) - log1p(-self.p)
        if q_default > 0:
            self.q_default = log(q_default) - log1p(q_default)
            self.q_default -= log(self.p) - log1p(-self.p)
        else:
            self.q_default = -numpy.inf

        self.S_const = (log1p(-q.fa[q.fa<1]).sum() +
                        log1p(-q_default) * (self.M - self.g.num_edges())
                        - self.M * log1p(-self.p))

        self.aE = aE
        if numpy.isnan(aE):
            self.E_prior = False
        else:
            self.E_prior = True

        self._state = libinference.make_uncertain_state(self.bstate._state,
                                                        self)
    def __getstate__(self):
        return dict(g=self.g, q=self._q, q_default=self._q_default,
                    aE=self.aE, nested=self.nbstate is not None,
                    bstate=(self.nbstate.copy() if self.nbstate is not None else
                            self.bstate.copy()), self_loops=self.self_loops)

    def __setstate__(self, state):
        self.__init__(**state)

    def copy(self, **kwargs):
        """Return a copy of the state."""
        return UncertainBlockState(**dict(self.__getstate__(), **kwargs))

    def __copy__(self):
        return self.copy()

    def __setstate__(self, state):
        self.__init__(**state)

    def __repr__(self):
        return "<UncertainBlockState object with %s, at 0x%x>" % \
            (self.nbstate if self.nbstate is not None else self.bstate,
             id(self))

    def _mcmc_sweep(self, mcmc_state):
        return libinference.mcmc_uncertain_sweep(mcmc_state,
                                                 self._state,
                                                 _get_rng())

class MeasuredBlockState(UncertainBaseState):
    r"""The inference state of a measured graph, using the stochastic block model as
    a prior.

    Parameters
    ----------
    g : :class:`~graph_tool.Graph`
        Measured graph.
    n : :class:`~graph_tool.PropertyMap`
        Edge property map of type ``int``, containing the total number of
        measurements for each edge.
    x : :class:`~graph_tool.PropertyMap`
        Edge property map of type ``int``, containing the number of
        positive measurements for each edge.
    n_default : ``int`` (optional, default: ``1``)
        Total number of measurements for each non-edge.
    x_default : ``int`` (optional, default: ``1``)
        Total number of positive measurements for each non-edge.
    fn_params : ``dict`` (optional, default: ``dict(alpha=1, beta=1)``)
        Beta distribution hyperparameters for the probability of missing
        edges (false negatives).
    fp_params : ``dict`` (optional, default: ``dict(mu=1, nu=1)``)
        Beta distribution hyperparameters for the probability of spurious
        edges (false positives).
    aE : ``float`` (optional, default: ``NaN``)
        Expected total number of edges used in prior. If ``NaN``, a flat
        prior will be used instead.
    nested : ``boolean`` (optional, default: ``True``)
        If ``True``, a :class:`~graph_tool.inference.nested_blockmodel.NestedBlockState`
        will be used, otherwise
        :class:`~graph_tool.inference.blockmodel.BlockState`.
    state_args : ``dict`` (optional, default: ``{}``)
        Arguments to be passed to
        :class:`~graph_tool.inference.nested_blockmodel.NestedBlockState` or
        :class:`~graph_tool.inference.blockmodel.BlockState`.
    bstate : :class:`~graph_tool.inference.nested_blockmodel.NestedBlockState` or :class:`~graph_tool.inference.blockmodel.BlockState`  (optional, default: ``None``)
        If passed, this will be used to initialize the block state
        directly.
    self_loops : bool (optional, default: ``False``)
        If ``True``, it is assumed that the uncertain graph can contain
        self-loops.

    References
    ----------
    .. [peixoto-reconstructing-2018] Tiago P. Peixoto, "Reconstructing networks
       with unknown and heterogeneous errors" :arxiv:`1806.07956`
    """

    def __init__(self, g, n, x, n_default=1, x_default=0,
                 fn_params=dict(alpha=1, beta=1), fp_params=dict(mu=1, nu=1),
                 aE=numpy.nan, nested=True, state_args={}, bstate=None,
                 self_loops=False, **kwargs):

        super(MeasuredBlockState, self).__init__(g, nested=nested,
                                                 state_args=state_args,
                                                 bstate=bstate, **kwargs)

        self.aE = aE
        if numpy.isnan(aE):
            self.E_prior = False
        else:
            self.E_prior = True

        self.n = n
        self.x = x
        self.n_default = n_default
        self.x_default = x_default
        self.alpha = fn_params.get("alpha", 1)
        self.beta = fn_params.get("beta", 1)
        self.mu = fp_params.get("mu", 1)
        self.nu = fp_params.get("nu", 1)

        self._state = libinference.make_measured_state(self.bstate._state,
                                                       self)

    def __getstate__(self):
        return dict(g=self.g, n=self.n, x=self.x, n_default=self.n_default,
                    x_default=self.x_default,
                    fn_params=dict(alpha=self.alpha, beta=self.beta),
                    fp_params=dict(mu=self.mu, nu=self.nu), aE=self.aE,
                    nested=self.nbstate is not None,
                    bstate=(self.nbstate if self.nbstate is not None
                            else self.bstate), self_loops=self.self_loops)

    def __setstate__(self, state):
        self.__init__(**state)

    def copy(self, **kwargs):
        """Return a copy of the state."""
        return MeasuredBlockState(**dict(self.__getstate__(), **kwargs))

    def __repr__(self):
        return "<MeasuredBlockState object with %s, at 0x%x>" % \
            (self.nbstate if self.nbstate is not None else self.bstate,
             id(self))

    def _mcmc_sweep(self, mcmc_state):
        return libinference.mcmc_measured_sweep(mcmc_state,
                                                self._state,
                                                _get_rng())

    def set_hparams(self, alpha, beta, mu, nu):
        """Set edge and non-edge hyperparameters."""
        self._state.set_hparams(alpha, beta, mu, nu)
        self.alpha = alpha
        self.beta = beta
        self.mu = mu
        self.nu = nu

    def get_p_posterior(self):
        """Get beta distribution parameters for the posterior probability of missing edges."""
        T = self._state.get_T()
        M = self._state.get_M()
        return M - T + self.alpha, T + self.beta

    def get_q_posterior(self):
        """Get beta distribution parameters for the posterior probability of spurious edges."""
        N = self._state.get_N()
        X = self._state.get_X()
        T = self._state.get_T()
        M = self._state.get_M()
        return X - T + self.mu, N - X - (M - T) + self.nu

class MixedMeasuredBlockState(UncertainBaseState):
    r"""The inference state of a measured graph with heterogeneous errors, using the
    stochastic block model as a prior.

    Parameters
    ----------
    g : :class:`~graph_tool.Graph`
        Measured graph.
    n : :class:`~graph_tool.PropertyMap`
        Edge property map of type ``int``, containing the total number of
        measurements for each edge.
    x : :class:`~graph_tool.PropertyMap`
        Edge property map of type ``int``, containing the number of
        positive measurements for each edge.
    n_default : ``int`` (optional, default: ``1``)
        Total number of measurements for each non-edge.
    x_default : ``int`` (optional, default: ``1``)
        Total number of positive measurements for each non-edge.
    fn_params : ``dict`` (optional, default: ``dict(alpha=1, beta=10)``)
        Beta distribution hyperparameters for the probability of missing
        edges (false negatives).
    fp_params : ``dict`` (optional, default: ``dict(mu=1, nu=10)``)
        Beta distribution hyperparameters for the probability of spurious
        edges (false positives).
    aE : ``float`` (optional, default: ``NaN``)
        Expected total number of edges used in prior. If ``NaN``, a flat
        prior will be used instead.
    nested : ``boolean`` (optional, default: ``True``)
        If ``True``, a :class:`~graph_tool.inference.nested_blockmodel.NestedBlockState`
        will be used, otherwise
        :class:`~graph_tool.inference.blockmodel.BlockState`.
    state_args : ``dict`` (optional, default: ``{}``)
        Arguments to be passed to
        :class:`~graph_tool.inference.nested_blockmodel.NestedBlockState` or
        :class:`~graph_tool.inference.blockmodel.BlockState`.
    bstate : :class:`~graph_tool.inference.nested_blockmodel.NestedBlockState` or :class:`~graph_tool.inference.blockmodel.BlockState`  (optional, default: ``None``)
        If passed, this will be used to initialize the block state
        directly.
    self_loops : bool (optional, default: ``False``)
        If ``True``, it is assumed that the uncertain graph can contain
        self-loops.

    References
    ----------
    .. [peixoto-reconstructing-2018] Tiago P. Peixoto, "Reconstructing networks
       with unknown and heterogeneous errors" :arxiv:`1806.07956`
    """

    def __init__(self, g, n, x, n_default=1, x_default=0,
                 fn_params=dict(alpha=1, beta=10), fp_params=dict(mu=1, nu=10),
                 aE=numpy.nan, nested=True, state_args={}, bstate=None,
                 self_loops=False, **kwargs):

        super(MixedMeasuredBlockState, self).__init__(g, nested=nested,
                                                      state_args=state_args,
                                                      bstate=bstate, **kwargs)
        self.aE = aE
        if numpy.isnan(aE):
            self.E_prior = False
        else:
            self.E_prior = True

        self.n = n
        self.x = x
        self.n_default = n_default
        self.x_default = x_default
        self.alpha = fn_params.get("alpha", 1)
        self.beta = fn_params.get("beta", 10)
        self.mu = fp_params.get("mu", 1)
        self.nu = fp_params.get("nu", 10)

        self._state = None

        self.q = self.g.new_ep("double")
        self.sync_q()

        self._state = libinference.make_uncertain_state(self.bstate._state,
                                                        self)

    def sync_q(self):
        ra, rb = self.transform(self.n.fa, self.x.fa)
        self.q.fa = log(ra) - log(rb)
        dra, drb = self.transform(self.n_default, self.x_default)
        self.q_default = log(dra) - log(drb)

        self.S_const = (self.M - self.g.num_edges()) * log(drb) + log(rb).sum()

        if self._state is not None:
            self._state.set_q_default(self.q_default)
            self._state.set_S_const(self.S_const)

    def transform(self, na, xa):
        ra = scipy.special.beta(na - xa + self.alpha, xa + self.beta) / scipy.special.beta(self.alpha, self.beta)
        rb = scipy.special.beta(xa + self.mu, na - xa + self.nu) / scipy.special.beta(self.mu, self.nu)
        return ra, rb

    def set_hparams(self, alpha, beta, mu, nu):
        """Set edge and non-edge hyperparameters."""
        self.alpha = alpha
        self.beta = beta
        self.mu = mu
        self.nu = nu
        self.sync_q()

    def __getstate__(self):
        return dict(g=self.g, n=self.n, x=self.x, n_default=self.n_default,
                    x_default=self.x_default,
                    fn_params=dict(alpha=self.alpha, beta=self.beta),
                    fp_params=dict(mu=self.mu, nu=self.nu), aE=self.aE,
                    nested=self.nbstate is not None,
                    bstate=(self.nbstate if self.nbstate is not None
                            else self.bstate), self_loops=self.self_loops)

    def __setstate__(self, state):
        self.__init__(**state)

    def copy(self, **kwargs):
        """Return a copy of the state."""
        return MixedMeasuredBlockState(**dict(self.__getstate__(), **kwargs))

    def __copy__(self):
        return self.copy()

    def __setstate__(self, state):
        self.__init__(**state)

    def __repr__(self):
        return "<MixedMeasuredBlockState object with %s, at 0x%x>" % \
            (self.nbstate if self.nbstate is not None else self.bstate,
             id(self))

    def _algo_sweep(self, algo, r=.5, h=.1, hstep=1, **kwargs):
        if numpy.random.random() < h:
            hs = [self.alpha, self.beta, self.mu, self.nu]
            j = numpy.random.randint(len(hs))

            f_dh = [max(0, hs[j] - hstep), hs[j] + hstep]
            pf = 1./(f_dh[1] - f_dh[0])

            old_hs = hs[j]
            hs[j] = f_dh[0] + numpy.random.random() * (f_dh[1] - f_dh[0])

            b_dh = [max(0, hs[j] - hstep), hs[j] + hstep]
            pb = 1./min(1, hs[j])

            latent_edges = kwargs.get("entropy_args", {}).get("latent_edges", True)
            density = False

            Sb = self._state.entropy(latent_edges, density)
            self.set_hparams(*hs)
            Sa = self._state.entropy(latent_edges, density)

            if Sa < Sb or numpy.random.random() < exp(-(Sa-Sb) + log(pb) - log(pf)):
                return (Sa-Sb, 1, 1)
            else:
                hs[j] = old_hs
                self.set_hparams(*hs)
                return (0., 1, 0)
        else:
            return super(MixedMeasuredBlockState, self)._algo_sweep(algo, r, **kwargs)

    def _mcmc_sweep(self, mcmc_state):
        return libinference.mcmc_uncertain_sweep(mcmc_state,
                                                 self._state,
                                                 _get_rng())
