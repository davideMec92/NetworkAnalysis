import snap

# get total lines of the input file
def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

#Creazione Grafo G
G = snap.TNGraph.New()

#Directory database grafi
source_dir = "Networks database/"

#Nome con estensione del file sorgente
filename = source_dir + "eco-everglades.txt"

#Ottengo lunghezza file
file_lenght = file_len( filename )

reading_line = 1
progress = ""

#Lettura file sorgente
with open(filename) as f:

    for line in f:

        # Get reading progress percentage
        progress_percentage = (100 * reading_line)/file_lenght

        print("Progress: " + str(progress) + " " + str( reading_line ) + "/" + str(file_lenght) + " " + str(int(progress_percentage)) + "%")

        if line[0] != "#":

            #nodes = line.split("\t")
            nodes = line.split(" ")

            if( G.IsNode( int( nodes[0] ) ) == False and G.IsNode( int( nodes[1] ) ) == False ):
                G.AddNode(int(nodes[0]))
                G.AddNode(int(nodes[1]))
            elif( G.IsNode( int( nodes[0] ) ) == False and G.IsNode( int( nodes[1] ) ) == True ):
                G.AddNode(int(nodes[0]))
            elif( G.IsNode( int( nodes[0] ) ) == True and G.IsNode( int( nodes[1] ) ) == False ):
                G.AddNode(int(nodes[1]))

            G.AddEdge(int(nodes[0]), int(nodes[1]))
            #print( "Nodo 1: " + str(nodes[0]) + "\n")
            #print( "Nodo 2: " + str(nodes[1]) + "\n")

        reading_line = reading_line + 1

print("Building graph finished successfully!")
print("Drawing graph..")

# Need to create a layout when doing
# separate calls to draw nodes and edges
snap.DrawGViz(G, snap.gvlDot, "graph.png", "graph 1")
