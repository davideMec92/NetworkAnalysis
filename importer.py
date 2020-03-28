import networkx as nx
import utils.file as uf
import os
import re
import sys
import utils.main as max_clique_algorithm
import utils.mail as mailUtils
from time import gmtime, strftime

#Creazione Grafo G
G = nx.Graph()

#Directory database grafi
source_dir = "networks"

output_log_dir = "log"

now = strftime("%Y_%m_%d_%H_%M_%S", gmtime())

filename = source_dir + "/soc-gplus/soc-gplus.txt" #OK

#Separatore nodi file di input grafo G
separator = " ";

#Ottengo lunghezza file
file_lenght = uf.file_len( filename )

output_dir = "output/" + str( os.path.basename( filename ).split(".")[0] )

#Creazione directory di output risultati
if not os.path.exists(output_dir + "/"):
  os.makedirs(output_dir + "/")

#Creazione directory di output log
if not os.path.exists(output_dir + "/" + output_log_dir + "/"):
  os.makedirs(output_dir + "/" + output_log_dir + "/")

output_file_log = open( output_dir + "/" + output_log_dir + "/" + str( os.path.basename( filename ).split(".")[0] + "_" + now + ".log" ), "w")

reading_line = 1
progress = ""

output_file_log.write( "Starting building graph G.. at " + str( now ) + " \n" )

#Lettura file sorgente
with open(filename) as f:

    for line in f:

        # Get reading progress percentage
        progress_percentage = (100 * reading_line)/file_lenght

        print("Progress: " + str(progress) + " " + str( reading_line ) + "/" + str(file_lenght) + " " + str(int(progress_percentage)) + "%")

        if line[0] != "#":

            nodes = line.split( separator )

            node_i = re.findall("\d+", nodes[0])[0]
            node_j = re.findall("\d+", nodes[1])[0]

            #Verifico che il nodo u non esista già nel grafo G
            if( G.has_node( node_i ) == False ):
                G.add_node( node_i )

            #Verifico che il nodo v non esista già nel grafo G
            if( G.has_node( node_j ) == False ):
                G.add_node( node_j )

            #Verifico che l'edge (u,v) non esista già nel grafo G
            if( G.has_edge( node_i, node_j ) == False ):
                edge = (node_i, node_j)
                G.add_edge( *edge )

        reading_line = reading_line + 1


output_file_log.write("Building graph G finished successfully! \n")

print("Building graph finished successfully! \n")

output_file_log.write("Data relative to Graph G named: " + str( os.path.basename( filename ) ) + "\n" )

print("Data relative to Graph G named: " + str( os.path.basename( filename ) ) )

#Ottengo numero totale nodi
print( "Calculating number of nodes" )
tot_nodes = G.number_of_nodes()

#Ottengo numero totale connessioni
print( "Calculating number of edges" )
tot_edges = G.number_of_edges()

print( "Calculating graph density.." )
total_connections = ( tot_nodes * ( tot_nodes - 1 ) )/2

#Ottengo densità Grafo G
density = tot_edges/total_connections

max_node_degree = None
min_node_degree = None
node_degree_sum = 0

print("Calculating maximum and minimum degree..")

for node in G.nodes():

    #Ottengo grado nodo i-esimo
    tmp_degree = G.degree( node )

    #Verifico che non si siano verificati errori
    if( tmp_degree is not None ):

        node_degree_sum += tmp_degree

        if( max_node_degree is None ): #Inizializzazione variabili
            max_node_degree = tmp_degree
            min_node_degree = tmp_degree
        elif( tmp_degree > max_node_degree ): #Confronto con massimo temporaneo
            max_node_degree = tmp_degree
        elif( tmp_degree < min_node_degree ): #Confronto con minimo temporaneo
            min_node_degree = tmp_degree

#Calcolo grado medio nodi grafo G
print("Calculating average degree..")
average_degree = node_degree_sum/tot_nodes

tot_triangles = 0

print("Calculating total triangles..")

for node in G.nodes():
    tot_triangles += nx.triangles(G,node)

print( "Calculating assortativity coefficient.. " )
degree_assortativity_coefficient = nx.degree_assortativity_coefficient(G)

print( "Calculating global clustering coefficient (Transitivity).. ")
global_clustering_coefficient = nx.transitivity(G)

print( "Calculating local clustering coefficient.. ")
local_clustering_coefficient = {}

for node in G.nodes():
  local_clustering_coefficient[node] = nx.clustering(G,node)

print( "Calculating average clustering coefficient.. ")
avg_clustering_coefficient = nx.average_clustering(G)

print( "Calculating triangles formed by a edge..")
triangles_formed_by_a_edge = tot_triangles/tot_edges

print( "Calculating maximum k core subgraph.. ")
maximum_k_core_subgraph = nx.k_core(G)

maximum_k_core_number = None

for node in maximum_k_core_subgraph.nodes():

    # Ottengo grado nodo i-esimo
    tmp_degree = maximum_k_core_subgraph.degree(node)

    # Verifico che non si siano verificati errori
    if (tmp_degree is not None):
        if (maximum_k_core_number is None):  # Inizializzazione variabili
            maximum_k_core_number = tmp_degree
        elif (tmp_degree < maximum_k_core_number):  # Confronto con minimo temporaneo
            maximum_k_core_number = tmp_degree

print( "Calculating maximum clique.." )
args = { 'path': filename, 'time' : 100000000, 'graph' : G }
maximum_clique = max_clique_algorithm.start_maximum_clique_calc( args )[0]

print(" Total nodes:  " + str( tot_nodes ) )
print(" Total edges:  " + str( tot_edges ) )
print(" Density:  " + str( density ) )
print(" Maximum degree: " + str( max_node_degree ) )
print(" Minimum degree: " + str( min_node_degree ) )
print(" Average degree: " + str( average_degree ) )
print(" Number of triangles: " + str( tot_triangles ) )
print(" Global clustering coefficient (Transitivity): " + str( global_clustering_coefficient ) )
print(" Average clustering coefficient: " + str( avg_clustering_coefficient ) )
print(" Degree assortativity coefficient: " + str( degree_assortativity_coefficient ) )
print(" Average triangles formed by a edge: " + str( triangles_formed_by_a_edge ) )
print(" Maximum k-core number: " + str( maximum_k_core_number ) )
print(" Maximum clique number: " + str( len(maximum_clique) ) )
print(" Maximum clique nodes: " + str( maximum_clique ) )

#Write results to log file
output_file_log.write(" Total nodes:  " + str( tot_nodes ) + "\n" )
output_file_log.write(" Total edges:  " + str( tot_edges ) + "\n" )
output_file_log.write(" Density:  " + str( density ) + "\n" )
output_file_log.write(" Maximum degree: " + str( max_node_degree ) + "\n" )
output_file_log.write(" Minimum degree: " + str( min_node_degree ) + "\n" )
output_file_log.write(" Average degree: " + str( average_degree ) + "\n" )
output_file_log.write(" Number of triangles: " + str( tot_triangles ) + "\n" )
output_file_log.write(" Global clustering coefficient (Transitivity): " + str( global_clustering_coefficient ) + "\n" )
output_file_log.write(" Local clustering coefficient : " + str( local_clustering_coefficient ) + "\n" )
output_file_log.write(" Average clustering coefficient: " + str( avg_clustering_coefficient ) + "\n" )
output_file_log.write(" Degree assortativity coefficient: " + str( degree_assortativity_coefficient ) + "\n" )
output_file_log.write(" Average triangles formed by a edge: " + str( triangles_formed_by_a_edge ) + "\n" )
output_file_log.write(" Maximum k-core number: " + str( maximum_k_core_number ) + "\n" )
output_file_log.write(" Maximum clique number: " + str( len(maximum_clique) ) + "\n" )
output_file_log.write(" Maximum clique nodes: " + str( maximum_clique ) + "\n" )

now = strftime("%Y_%m_%d_%H_%M_%S", gmtime())

output_file_log.write("Task completed successfully at " + str( now ) + "\n" )
