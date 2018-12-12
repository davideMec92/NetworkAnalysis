import networkx as nx
import utils.file as uf
#import matplotlib.pyplot as plt
import os

#Creazione Grafo G
G = nx.Graph()

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

            nodes = line.split( separator )

            #Verifico che il nodo u non esista già nel grafo G
            if( G.has_node( nodes[0] ) == False ):
                G.add_node( nodes[0] )

            #Verifico che il nodo v non esista già nel grafo G
            if( G.has_node( nodes[1] ) == False ):
                G.add_node( nodes[1] )

            #Verifico che l'edge (u,v) non esista già nel grafo G
            if( G.has_edge( nodes[0], nodes[1] ) == False ):
                G.add_edge(nodes[0], nodes[1])

            #print( "Nodo 1: " + str(nodes[0]) + "\n")
            #print( "Nodo 2: " + str(nodes[1]) + "\n")

        reading_line = reading_line + 1

print("Building graph finished successfully! \n")

print("Data relative to Graph G named: " + str( os.path.basename( filename ) ) )

#Ottengo numero totale nodi
tot_nodes = G.number_of_nodes()

#Ottengo numero totale connessioni
tot_edges = G.number_of_edges()

total_connections = ( tot_nodes * ( tot_nodes - 1 ) )/2

#Ottengo densità Grafo G
density = tot_edges/total_connections

max_node_degree = None
node_degree_sum = 0

print("Calculating maximum degree..")

for node in G.nodes():

    #Ottengo grado nodo i-esimo
    tmp_degree = G.degree( node )

    #Verifico che non si siano verificati errori
    if( tmp_degree is not None ):

        node_degree_sum += tmp_degree

        if( max_node_degree is None ):
            max_node_degree = tmp_degree
        elif( tmp_degree > max_node_degree ):
            max_node_degree = tmp_degree
            print("Found new maximum degree: " + str( tmp_degree ))


average_degree = node_degree_sum/tot_nodes


print( "dict: " + str( list(nx.enumerate_all_cliques(G).values()) ) )

print("Calculating total triangles..")
triangles_dict = nx.triangles( G )
tot_triangles = 0
#tot_triangles = [c for c in nx.cycle_basis(G) if len(c)==3]


for node_key in triangles_dict:
    tot_triangles += triangles_dict[node_key]

#degree_assortativity_coefficient = nx.degree_assortativity_coefficient(G)

print(" Total nodes:  " + str( tot_nodes ) )
print(" Total edges:  " + str( tot_edges ) )
print(" Density:  " + str( density ) )
print(" Maximum degree: " + str( max_node_degree ) )
print(" Average degree: " + str( average_degree ) )
print(" Number of triangles: " + str( tot_triangles ) )

#print(" Degree assortativity coefficient: " + str( degree_assortativity_coefficient ) )

"""print("Drawing graph..")

# Need to create a layout when doing
# separate calls to draw nodes and edges
nx.draw(G)
plt.show()"""
