import networkx as nx
import utils.file as uf
#import matplotlib.pyplot as plt
import os
import re
import sys
import utils.max_clique.main as max_clique_algorithm

#Creazione Grafo G
G = nx.Graph()

#Directory database grafi
source_dir = "Networks"

#Nome con estensione del file sorgente
#filename = source_dir + "/soc-academia/soc-academia.txt"
#filename = source_dir + "/socfb-A-anon/socfb-A-anon.txt"
#filename = source_dir + "/socfb-UCF52/socfb-UCF52.txt" #OK
#filename = source_dir + "/soc-youtube-growth/youtube.txt"
#filename = source_dir + "/soc-twitter-follows/soc-twitter-follows.txt" #OK
filename = source_dir + "/ca-AstroPh/ca-AstroPh.txt"#OK
#filename = source_dir + "/wiki-vote/Wiki-Vote.txt"

#Separatore nodi file di input grafo G
separator = " ";
#separator = "	";
#separator = ",";

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

            #print( "Nodo 1: " + str(nodes[0]) + "\n")
            #print( "Nodo 2: " + str(nodes[1]) + "\n")

        reading_line = reading_line + 1

print("Building graph finished successfully! \n")

#'test' : source_dir + '/output'
args = { 'path': filename, 'time' : 10000, 'graph' : G }

max_clique_algorithm.start_maximum_clique_calc( args )

sys.exit("Uscita programmata")

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

tot_triangles = 0

triangles_search_count = 1

#Analizzo i nodi del Grafo G
"""for node in G.nodes():

    #Ottengo cliques nodo
    node_cliques = nx.cliques_containing_node(G, node)

    print("\nRicerca triangoli per nodo : " + str(node) + " - " + str( triangles_search_count ) + "/" + str( tot_nodes ) + " \n")

    print("node_cliques: " + str( node_cliques ))

    #Ricerca cliques per nodo analizzato
    for i,j in node_cliques:

        search_clique_node = None

        if( i != node ):
            search_clique_node = i
        elif( j != node ):
            search_clique_node = j

        #print("Clique trovato i: " + str(i) + ", j: " + str(j) + "\n" )

        #Ricerca di un eventuale edge tra i nodi connessi al nodo analizzato
        for k,q in node_cliques:

            #In caso di ricerca sullo stesso nodo passo al prossimo
            if( k == search_clique_node or q == search_clique_node ):
                continue

            #print("Ricerca edge per nodo: " + str(search_clique_node) + "\n")

            search_edge_node = None

            if( k != node ):
                search_edge_node = k
            elif( q != node ):
                search_edge_node = q

            if( G.has_edge( search_clique_node, search_edge_node ) == True ):
                print( "Trovato triangolo tra i vertici: " + str( node ) + ", " + str( search_clique_node ) + ", " + str( search_edge_node ) )
                tot_triangles = tot_triangles + 1
            #else:
                #print( "Nessun edge presente tra: " + str( search_clique_node ) + ", " + str(search_edge_node) )

    print("Triangoli totali trovati: " + str( tot_triangles ) )
    triangles_search_count = triangles_search_count + 1"""

print("Calculating total triangles..")
#triangles_dict = nx.triangles( G )

#print("dict: " + str(triangles_dict))

"""for node in triangles_dict:
    for n_triangles in node:
        print("Nodo: " + str(node) + " - Triangoli: " + str(n_triangles))
        tot_triangles += int(n_triangles)"""

#tot_triangles = [c for c in nx.cycle_basis(G) if len(c)==3]

for node in G.nodes():
    tot_triangles += nx.triangles(G,node)

"""for node_key in triangles_dict:
    print( "Entro qui" )
    tot_triangles += triangles_dict[node_key]"""

#A = nx.convert.to_dict_of_dicts( G )
#B = nx.adjacency_matrix(G)
#nx.write_adjlist(G,"test.adjlist")
#print("adjacency_matrix: " + str(A))
#f = open("adjacency_matrix.txt", "w")
#f.write(str(A))

degree_assortativity_coefficient = nx.degree_assortativity_coefficient(G)
avg_clustering_coefficient = nx.average_clustering(G)
triangles_formed_by_a_edge = tot_triangles/tot_edges
maximum_k_core_number = nx.k_core(G)
graph_maximal_clique = nx.make_max_clique_graph(G)

print(" Total nodes:  " + str( tot_nodes ) )
print(" Total edges:  " + str( tot_edges ) )
print(" Density:  " + str( density ) )
print(" Maximum degree: " + str( max_node_degree ) )
print(" Average degree: " + str( average_degree ) )
print(" Number of triangles: " + str( tot_triangles ) )
print(" Average clustering coefficient: " + str( avg_clustering_coefficient ) )
print(" Degree assortativity coefficient: " + str( degree_assortativity_coefficient ) )
print(" Average triangles formed by a edge: " + str( triangles_formed_by_a_edge ) )
print(" Maximum k-core number: " + str( nx.number_of_nodes(maximum_k_core_number )) )
print(" Maximal clique: " + str(graph_maximal_clique))

"""print("Drawing graph..")

# Need to create a layout when doing
# separate calls to draw nodes and edges
nx.draw(G)
plt.show()"""
