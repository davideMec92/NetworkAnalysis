# Network Analysis

Il presente software è stato realizzato, in linguaggio **Python**, per il calcolo di specifici valori su grafi.

Nello specifico i valori calcolati sono:

- Numero totale di nodi
- Numero totale di archi
- Densità
- Grado massimo dei nodi
- Grado minimo dei nodi
- Grado medio dei nodi
- Numero di triangoli
- Transitività
- Clustering coefficient medio
- Grado di assortatività
- Numero medio di triangoli formati da un arco
- K-core massimo
- Calcolo della cricca massimale (Maximum clique). Per il calcolo di sub-grafo rappresentante la cricca massimale lo script realizzato utilizza la seguente libreria https://github.com/donfaq/max_clique/blob/master/main.py

## Prerequisiti

Per il corretto funzionamento dello script è necessario avere <b>Python ver 3.* </b> e installare i seguenti pacchetti e/o librerie:

Nota: In molti casi, l'installazione delle librerie e/o pacchetti necessari, può essere resa molto semplice utilizzando lo strumento **pip** di Python

 <pre><code><b>#Esempio di installazione su ambiente Linux utilizzando il gestore pacchetti apt (Versione per Python 3)</b>
 sudo apt-get install python3-pip</code></pre>



- **NetworkX** ( https://networkx.github.io/ )

    <pre><code><b>#Installazione mediante pip3</b>
    pip3 install networkx</code></pre>

- **Numpy**
    <pre><code><b>#Installazione mediante pip3</b>
    pip3 install numpy</code></pre>

## Utilizzo
Il software è facilmente eseguibile mediante il comando:
<pre><code><b>#Indicare come argomento il nome del file (con relativa estensione) contenente il dataset da analizzare</b>
python3 graph_analizer.py <nome_file.estensione></code></pre>

I file contenenti i dataset vanno collocati all'interno della directory <b>networks/</b>. Successivamente, dopo avere analizzato il grafo, lo script produrrà un file all'interno della directory <b>output</b> recante il nome del file indicato in input.

##Credits
Lo script è liberamente utilizzabile, è stato realizzato per scopi didattici da:

<i>Davide Nunzio Maccarrone</i>  <b>davidemaccarrone@studio.unibo.it</b>
<i>Bruno Quintero Panaro</i> <b>bruno.quinteropanaro@studio.unibo.it</b>
