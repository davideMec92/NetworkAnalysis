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

Per il corretto funzionamento dello script è necessario avere **Python ver 3.* ** e installare i seguenti pacchetti e/o librerie:

In molti casi, l'installazione delle librerie e/o pacchetti necessari, può essere resa molto semplice utilizzando lo strumento **pip** di Python

  #Esempio di installazione su ambiente Linux utilizzando il gestore pacchetti apt (Versione per Python 3)
  sudo apt-get install python3-pip


- **NetworkX** ( https://networkx.github.io/ )

  #Installazione mediante pip3
  pip3 install networkx

- **Numpy**

```bash
#Installazione mediante pip3
pip3 install numpy
```
## Utilizzo
Il software è facilmente eseguibile mediante il comando:
```bash
#Indicare come argomento il nome del file (con relativa estensione) contenente il dataset da analizzare
python3 graph_analizer.py <nome_file.estensione>
```

I file contenti il dataset vanno collocati all'interno della directory ***networks/***. Successivamente, dopo avere analizzato il grafo, lo script produrrà un file all'interno della directory ***output/*** recante il nome del file indicato in input.
