import networkx as nx
import utils.file as uf
#import matplotlib.pyplot as plt
import os

#Creazione Grafo G
G = nx.DiGraph()

#Directory database grafi
source_dir = "Networks"

#Nome con estensione del file sorgente
filename = source_dir + "/soc-academia/soc-academia.txt"

#Separatore nodi file di input grafo G
separator = " ";

#Ottengo lunghezza file
file_lenght = uf.file_len( filename )

reading_line = 1
progress = ""

#Lettura file sorgente
with open(filename) as f:

    for line in f:

        # Get reading progress percentage
        progress_percentage = (100 * reading_line)/file_lenght

        print("Progress: " + str(progress) + " " + str( reading_line ) + "/" + str(file_lenght) + " " + str(int(progress_percentage)) + "%")

        if line[0] != "#":

            nodes = line.split(" ")
            G.add_edge(nodes[0], nodes[1])
            #print( "Nodo 1: " + str(nodes[0]) + "\n")
            #print( "Nodo 2: " + str(nodes[1]) + "\n")

        reading_line = reading_line + 1

print("Building graph finished successfully!")

print("Data relative to Graph G named: " + str( os.path.basename( filename ) ) )

#Ottengo numero totale nodi
tot_nodes = G.number_of_nodes()

#Ottengo numero totale connessioni
tot_edges = G.number_of_edges()

total_connections = ( tot_nodes * ( tot_nodes - 1 ) )/2

#Ottengo
density = tot_edges/total_connections

print(" Total nodes:  " + str( tot_nodes ) )
print(" Total edges:  " + str( tot_edges ) )
print(" Density:  " + str( density ) )

"""print("Drawing graph..")

# Need to create a layout when doing
# separate calls to draw nodes and edges
nx.draw(G)
plt.show()"""
