// graph-tool -- a general graph modification and manipulation thingy
//
// Copyright (C) 2006-2018 Tiago de Paula Peixoto <tiago@skewed.de>
//
// This program is free software; you can redistribute it and/or
// modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 3
// of the License, or (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program. If not, see <http://www.gnu.org/licenses/>.

#ifndef GRAPH_BLOCKMODEL_MULTIFLIP_MCMC_HH
#define GRAPH_BLOCKMODEL_MULTIFLIP_MCMC_HH

#include "config.h"

#include <vector>
#include <algorithm>

#include "graph_tool.hh"
#include "../support/graph_state.hh"
#include "graph_blockmodel_util.hh"
#include <boost/mpl/vector.hpp>

namespace graph_tool
{
using namespace boost;
using namespace std;

#define MCMC_BLOCK_STATE_params(State)                                         \
    ((__class__,&, mpl::vector<python::object>, 1))                            \
    ((state, &, State&, 0))                                                    \
    ((E,, size_t, 0))                                                          \
    ((beta,, double, 0))                                                       \
    ((c,, double, 0))                                                          \
    ((d,, double, 0))                                                          \
    ((a1,, double, 0))                                                         \
    ((an,, double, 0))                                                         \
    ((entropy_args,, entropy_args_t, 0))                                       \
    ((mproposals, & ,std::vector<size_t>&, 0))                                 \
    ((maccept, & ,std::vector<size_t>&, 0))                                    \
    ((allow_vacate,, bool, 0))                                                 \
    ((verbose,, bool, 0))                                                      \
    ((niter,, size_t, 0))


template <class State>
struct MCMC
{
    GEN_STATE_BASE(MCMCBlockStateBase, MCMC_BLOCK_STATE_params(State))

    template <class... Ts>
    class MCMCBlockState
        : public MCMCBlockStateBase<Ts...>
    {
    public:
        GET_PARAMS_USING(MCMCBlockStateBase<Ts...>,
                         MCMC_BLOCK_STATE_params(State))
        GET_PARAMS_TYPEDEF(Ts, MCMC_BLOCK_STATE_params(State))

        template <class... ATs,
                  typename std::enable_if_t<sizeof...(ATs) ==
                                            sizeof...(Ts)>* = nullptr>
        MCMCBlockState(ATs&&... as)
           : MCMCBlockStateBase<Ts...>(as...),
            _g(_state._g),
            _groups(num_vertices(_state._bg)),
            _vpos(get(vertex_index_t(), _state._g),
                  num_vertices(_state._g)),
            _rpos(get(vertex_index_t(), _state._bg),
                  num_vertices(_state._bg))
        {
            _state.init_mcmc(_c,
                             (_entropy_args.partition_dl ||
                              _entropy_args.degree_dl ||
                              _entropy_args.edges_dl));
            for (auto v : vertices_range(_state._g))
            {
                if (_state._vweight[v] > 0)
                    add_element(_groups[_state._b[v]], _vpos, v);
                _N++;
            }

            for (auto r : vertices_range(_state._bg))
            {
                if (_state._wr[r] > 0)
                    add_element(_vlist, _rpos, r);
            }
        }

        typename state_t::g_t& _g;

        std::vector<std::vector<size_t>> _groups;
        typename vprop_map_t<size_t>::type::unchecked_t _vpos;
        typename vprop_map_t<size_t>::type::unchecked_t _rpos;

        std::vector<size_t> _vlist;
        std::vector<size_t> _vs;

        size_t _null_move = null_group;

        size_t _nproposals = 0;
        size_t _N = 0;

        size_t node_state(size_t r)
        {
            return r;
        }

        bool skip_node(size_t r)
        {
            return _groups[r].empty();
        }

        size_t node_weight(size_t)
        {
            return _vs.size();
        }

        template <class RNG>
        size_t sample_m(size_t n, RNG& rng)
        {
            if (n == 1)
                return 1;

            std::bernoulli_distribution single(_a1);
            if (single(rng))
                return 1;

            if (n == 2)
                return 2;

            std::bernoulli_distribution merge(_an);
            if (merge(rng))
                return n;

            std::uniform_int_distribution<size_t> split(2, n - 1);
            return split(rng);
        }

        double log_pm(size_t m, size_t n)
        {
            if (n == 1)
                return 0;
            if (m == 1)
                return log(_a1);
            if (m == n)
            {
                if (n == 2)
                    return log1p(-_a1);
                return log1p(-_a1) + log(_an);
            }
            return log1p(-_a1) + log1p(-_an) - log(n-2);
        }

        template <class RNG>
        size_t move_proposal(size_t r, RNG& rng)
        {
            size_t m = sample_m(_groups[r].size(), rng);

            if (!_allow_vacate && _groups[r].size() == m)
                return null_group;

            assert(m <= _groups[r].size());

            _nproposals += m;
            _vs.clear();

            while (_vs.size() < m)
            {
                size_t v = uniform_sample(_groups[r], rng);
                _vs.push_back(v);
                remove_element(_groups[r], _vpos, v);
            }

            for (auto v : _vs)
                add_element(_groups[r], _vpos, v);

            size_t v = uniform_sample(_vs, rng);
            size_t s = _state.sample_block(v, _c, _d, rng);

            if (s >= _groups.size())
            {
                _groups.resize(s + 1);
                _rpos.resize(s + 1);
            }

            if (!_state.allow_move(r, s) || s == r)
                return null_group;

            if (!_groups[s].empty() || _groups[r].size() > m)
                _mproposals[m]++;
            return s;
        }

        std::tuple<double, double>
        virtual_move_dS(size_t r, size_t nr)
        {
            double dS = 0, a = 0;
            size_t m = _vs.size();

            a -= log_pm(m, _groups[r].size());
            a += log_pm(m, _groups[nr].size() + m);
            a -= -lbinom(_groups[r].size(), m);
            a += -lbinom(_groups[nr].size() + m, m);

            int B = _vlist.size();
            a -= -log(B);
            if (_groups[r].size() == m)
                B--;
            if (_groups[nr].empty())
                B++;
            a += -log(B);

            if (m == 1)
            {
                auto v = _vs.front();
                dS = _state.virtual_move(v, r, nr, _entropy_args);
                double pf = _state.get_move_prob(v, r, nr, _c, _d, false);
                double pb = _state.get_move_prob(v, nr, r, _c, _d, true);
                a += log(pb) - log(pf);
            }
            else
            {
                _state._egroups_enabled = false;
                double pf = 0, pb = 0;
                for (auto v : _vs)
                    pf += _state.get_move_prob(v, r, nr, _c, _d, false);
                pf /= m;
                for (auto v : _vs)
                {
                    dS += _state.virtual_move(v, r, nr, _entropy_args);
                    _state.move_vertex(v, nr);
                }
                for (auto v : _vs)
                    pb += _state.get_move_prob(v, nr, r, _c, _d, false);
                pb /= m;
                a += log(pb) - log(pf);
                for (auto v : _vs)
                    _state.move_vertex(v, r);
                _state._egroups_enabled = true;
            }
            return std::make_tuple(dS, a);
        }

        void perform_move(size_t r, size_t nr)
        {
            if (!_groups[nr].empty() || _groups[r].size() > _vs.size())
                _maccept[_vs.size()]++;
            if (_state._wr[nr] == 0)
                add_element(_vlist, _rpos, nr);
            for (auto v : _vs)
            {
                _state.move_vertex(v, nr);
                remove_element(_groups[r], _vpos, v);
                add_element(_groups[nr], _vpos, v);
            }
            if (_state._wr[r] == 0)
                remove_element(_vlist, _rpos, r);
        }

        bool is_deterministic()
        {
            return false;
        }

        bool is_sequential()
        {
            return false;
        }

        auto& get_vlist()
        {
            return _vlist;
        }

        double get_beta()
        {
            return _beta;
        }

        size_t get_niter()
        {
            if (_nproposals < _niter * _N)
                return std::numeric_limits<size_t>::max();
            return 0;
        }

        void step(size_t, size_t)
        {
        }
    };
};


} // graph_tool namespace

#endif //GRAPH_BLOCKMODEL_MCMC_HH
