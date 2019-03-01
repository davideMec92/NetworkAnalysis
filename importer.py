import networkx as nx
import utils.file as uf
import os
import re
import sys
import utils.main as max_clique_algorithm
import utils.mail as mailUtils
from time import gmtime, strftime
import plotly
import plotly.plotly as py
import plotly.graph_objs as go

#Autenticazione con il servizio plotly
plotly.tools.set_credentials_file(username='tuamadre', api_key='bR4rv1Yzg7wBI6Ot2Jb7')

#Creazione Grafo G
G = nx.Graph()

#Directory database grafi
source_dir = "Networks"

output_log_dir = "log"

now = strftime("%Y_%m_%d_%H_%M_%S", gmtime())

#Nome con estensione del file sorgente
#filename = source_dir + "/socfb-Simmons81/socfb-Simmons81.txt" #OK
#filename = source_dir + "/ca-CondMat/ca-CondMat.txt" #OK
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
output_csv_degree_sequence = open( output_dir + "/" + output_log_dir + "/" + str( os.path.basename( filename ).split(".")[0] + "_degree_sequence_" + now + ".csv" ), "w")
output_csv_local_clustering_coefficient = open( output_dir + "/" + output_log_dir + "/" + str( os.path.basename( filename ).split(".")[0] + "_local_clustering_coefficient_" + now + ".csv" ), "w")

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

print("Calculating degree sequence.. ")

degree_sequence = {}

for node in G.nodes():
  degree_sequence[node] = G.degree[ node ]

#Riordino gradi nodi dal maggiore al minore, come da definizione di degree sequence
sorted_degree_sequence = sorted( degree_sequence.items(), key=lambda x: x[1] )

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

print( "Calculating maximum k core number.. ")
maximum_k_core_number = nx.k_core(G)

print( "Calculating maximum clique.." )
args = { 'path': filename, 'time' : 100000000, 'graph' : G }
maximum_clique = max_clique_algorithm.start_maximum_clique_calc( args )[0]

print(" Total nodes:  " + str( tot_nodes ) )
print(" Total edges:  " + str( tot_edges ) )
print(" Density:  " + str( density ) )
print(" Maximum degree: " + str( max_node_degree ) )
print(" Minimum degree: " + str( min_node_degree ) )
print(" Average degree: " + str( average_degree ) )
print(" Degree sequence: " + str( degree_sequence ) )
print(" Number of triangles: " + str( tot_triangles ) )
print(" Global clustering coefficient (Transitivity): " + str( global_clustering_coefficient ) )
print(" Average clustering coefficient: " + str( avg_clustering_coefficient ) )
print(" Degree assortativity coefficient: " + str( degree_assortativity_coefficient ) )
print(" Average triangles formed by a edge: " + str( triangles_formed_by_a_edge ) )
print(" Maximum k-core number: " + str( nx.number_of_nodes(maximum_k_core_number )) )
print(" Maximum clique number: " + str( len(maximum_clique) ) )
print(" Maximum clique nodes: " + str( maximum_clique ) )

#Write results to log file
output_file_log.write(" Total nodes:  " + str( tot_nodes ) + "\n" )
output_file_log.write(" Total edges:  " + str( tot_edges ) + "\n" )
output_file_log.write(" Density:  " + str( density ) + "\n" )
output_file_log.write(" Maximum degree: " + str( max_node_degree ) + "\n" )
output_file_log.write(" Minimum degree: " + str( min_node_degree ) + "\n" )
output_file_log.write(" Average degree: " + str( average_degree ) + "\n" )
output_file_log.write(" Degree sequence: " + str( degree_sequence ) + "\n" )
output_file_log.write(" Number of triangles: " + str( tot_triangles ) + "\n" )
output_file_log.write(" Global clustering coefficient (Transitivity): " + str( global_clustering_coefficient ) + "\n" )
output_file_log.write(" Local clustering coefficient : " + str( local_clustering_coefficient ) + "\n" )
output_file_log.write(" Average clustering coefficient: " + str( avg_clustering_coefficient ) + "\n" )
output_file_log.write(" Degree assortativity coefficient: " + str( degree_assortativity_coefficient ) + "\n" )
output_file_log.write(" Average triangles formed by a edge: " + str( triangles_formed_by_a_edge ) + "\n" )
output_file_log.write(" Maximum k-core number: " + str( nx.number_of_nodes(maximum_k_core_number )) + "\n" )
output_file_log.write(" Maximum clique number: " + str( len(maximum_clique) ) + "\n" )
output_file_log.write(" Maximum clique nodes: " + str( maximum_clique ) + "\n" )

output_csv_local_clustering_coefficient.write("Node, Local Clustering Coefficient \n")
                 
local_cluestering_plot_x = []
local_cluestering_plot_y = []
                 
for key, value in local_clustering_coefficient.items():
  local_cluestering_plot_x.append( key )
  local_cluestering_plot_y.append( value )
  output_csv_local_clustering_coefficient.write(str(key) + "," + str(value) + "\n")
  
trace1 = {"x": local_cluestering_plot_x, 
          "y": local_cluestering_plot_y, 
          "marker": {"color": "blue", "size": 12}, 
          "mode": "markers", 
          "name": "Local Clustering", 
          "type": "scatter"
}

data = [trace1]
layout = {"title": "Local Clustering Coefficient - " + str( os.path.basename( filename ).split(".")[0] ), 
          "xaxis": {"title": "Nodes"}, 
          "yaxis": {"title": "Local Clustering Coefficient"}}

fig = go.Figure(data=data, layout=layout)
py.plot(fig, filename = str( os.path.basename( filename ).split(".")[0] + "_local_clustering_coefficient") )
                 
output_csv_degree_sequence.write("Node, Degree \n")

for key, value in degree_sequence.items():
  output_csv_degree_sequence.write(str(key) + "," + str(value) + "\n")
  
degree_sequence_plot_x = []
degree_sequence_plot_y = []

degree_distribution_plot_x = []
degree_distribution_plot_y = []

cont = 0

k_degree = min_node_degree
n_k_nodes = 0

for degree in sorted_degree_sequence:
  
  degree_sequence_plot_x.append( cont )
  degree_sequence_plot_y.append( degree[1] )
  
  #Incremento numeri nodi con grado uguale a k
  if( k_degree == degree[1] ):
    n_k_nodes = n_k_nodes + 1
  elif( degree[1] > k_degree ): #Caso in cui il grado attuale sia stato superato, memorizzo e aggiorno variabili k_degree
    
    #Calcolo probabilità P(k)
    p_k = n_k_nodes/tot_nodes
    
    #Inserisco variabili in array per grafico
    degree_distribution_plot_x.append( k_degree )
    degree_distribution_plot_y.append( p_k )
    
    #Aggiorno varibiale grado k
    k_degree = degree[1]
    
    #Resetto count nodi con k_degree
    n_k_nodes = 0
  
  cont = cont + 1

# Create a trace
trace = go.Scatter(
    x = degree_sequence_plot_x,
    y = degree_sequence_plot_y
)

data = [trace]

layout = {"title": "Degree sequence - " + str( os.path.basename( filename ).split(".")[0] ), 
          "xaxis": {"title": "Sequence"}, 
          "yaxis": {"title": "Node Degree"}}

fig = go.Figure(data=data, layout=layout)

py.plot(data, filename = str( os.path.basename( filename ).split(".")[0] + "_degree_sequence") )


# Create a trace
trace = go.Bar(
    x = degree_distribution_plot_x,
    y = degree_distribution_plot_y
)

data = [trace]

layout = {"title": "Degree distribution - " + str( os.path.basename( filename ).split(".")[0] ), 
          "xaxis": {"title": "Node Degree"}, 
          "yaxis": {"title": "P(k)"}}

fig = go.Figure(data=data, layout=layout)

py.plot(data, filename = str( os.path.basename( filename ).split(".")[0] + "_degree_distribution") )

now = strftime("%Y_%m_%d_%H_%M_%S", gmtime())

output_file_log.write("Task completed successfully at " + str( now ) + "\n" )
