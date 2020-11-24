import networkx as nx
from random import choice
from collections import Counter
import time
import os

def writeTofile(file, text):
    f = open(file,"a+") 
    f.write(text+'\n')
    f.close() 
    
    
def doubleSweepLowerBound(G):
    r = choice(list(G))

    bfs_r = nx.bfs_edges(G, r)
    bfs_r_list = [r] + [v for u, v in bfs_r]
    a = bfs_r_list[-1] #with the maximum distance

    bfs_a = nx.bfs_edges(G, a)
    bfs_a_list = [a] + [v for u, v in bfs_a]
    b = bfs_a_list[-1]
    
    dslb = nx.shortest_path_length(G, source=a, target=b)
    return dslb


def fringeUpperBound(G, mtub):
    #Let r, a, and b be the vertices identified by double sweep
    r = choice(list(G))

    bfs_r = nx.bfs_edges(G, r)
    bfs_r_list = [r] + [v for u, v in bfs_r]
    a = bfs_r_list[-1] #with the maximum distance

    bfs_a = nx.bfs_edges(G, a)
    bfs_a_list = [a] + [v for u, v in bfs_a]
    b = bfs_a_list[-1]

    #u is halfway along a and b.
    u_index = int(len(bfs_a_list)/2)
    u = bfs_a_list[u_index]

    #Compute the BFS-tree Tu and its eccentricity ecc(u).
    T_u = nx.bfs_tree(G,u)
    #T_u with ties broken arbitrarily
    T_u = nx.DiGraph.to_undirected(T_u)
    
    T_d_u_v = nx.single_source_shortest_path_length(G, u)  #Let ecc(u) = max d(u, v) be eccentricity of u ∈ V ;
    ecc_u = max(T_d_u_v.values())
    
    if mtub:
        return nx.diameter(T_u)

    #F(u) = the set of vertices v ∈ V such that d(u,v) = ecc(u). leaf nodes of T_u, do not need cutoff
    d_u_v = nx.single_source_shortest_path_length(T_u, u) #cutoff: Depth to stop the search. Only paths of length <= cutoff are returned.

    F_u = []
    for v in reversed(list(d_u_v.keys())):
        if d_u_v[v] == ecc_u:
            F_u.append(v)
        if len(F_u)>50000:
            break
#             return nx.diameter(T_u)

    #If |F(u)| > 1, find the BFS-tree Tz for each z ∈ F(u), and compute B(u)
    #B(u): B(u) = max{ ecc(z) | z∈F(u) }.
    ecc_z = [nx.eccentricity(G, z) for z in F_u]
    B_u = max(ecc_z)

    if len(F_u) > 1 and B_u == 2*ecc_u - 1:        
        return 2*ecc_u - 1
    elif len(F_u) > 1 and B_u < 2*ecc_u - 1:  
        return 2*ecc_u - 2
    
    return nx.diameter(T_u)


def randomTreeUpperBound(G):
    # select a random node r
    r = choice(list(G))
    # returns the diameter of T_r
    T_r = nx.bfs_tree(G,r)
    T_r = nx.DiGraph.to_undirected(T_r)
    return nx.diameter(T_r)


def highestDegreeTreeUpperBound(G):
    # select r with highest degree
    r = sorted(G.degree, key=lambda x: x[1], reverse=True)[0][0]
    # returns the diameter of T_r
    T_r = nx.bfs_tree(G,r)
    T_r = nx.DiGraph.to_undirected(T_r)
    return nx.diameter(T_r)

datasetList = []
for file in os.listdir("data/"):
    if file.endswith(".txt"):
        dataset = file[:-4]
        datasetList.append(dataset)
        # print(os.path.join("data/", file))

for dataset in datasetList:
    # dataset = 'ca-GrQc'
    print('running....', dataset)
    FileName="data/"+ dataset + '.txt'
    recordFile = "record/"+ dataset + '_record.txt'
    os.makedirs(os.path.dirname(recordFile), exist_ok=True)

    Graphtype=nx.Graph()
    G = nx.read_edgelist(FileName, create_using=Graphtype, nodetype=int)

    writeTofile(recordFile, dataset)
    writeTofile(recordFile, "number of nodes: "+ str(G.number_of_nodes()))
    writeTofile(recordFile, "number of edges: "+ str(G.number_of_edges()))

    connected = nx.is_connected(G)
    if not connected:
    #     print("G is not connected!")
        connected_component_subgraphs = (G.subgraph(c) for c in nx.connected_components(G))
        G = max(connected_component_subgraphs, key=len)

    writeTofile(recordFile, "number of nodes l.c.c: "+ str(G.number_of_nodes()))
    writeTofile(recordFile, "number of edges l.c.c: "+ str(G.number_of_edges()))

    experimentNum = 10
    executionNum = 10
    writeTofile(recordFile, "experimentNum: "+ str(experimentNum))
    writeTofile(recordFile, "executionNum: "+ str(executionNum))

    writeTofile(recordFile, 'experimentNum' + ','+ 'executionNum' + ","+ 'dslb')
    for i in range(0, experimentNum):
        for j in range(0, executionNum):
            dslb = doubleSweepLowerBound(G)
            writeTofile(recordFile, str(i) + ','+ str(j) + ","+ str(dslb))

    writeTofile(recordFile, 'experimentNum' + ','+ 'executionNum' + ","+ 'fub')
    for i in range(0, experimentNum):
        for j in range(0, executionNum):
            fub = fringeUpperBound(G, mtub = False)
            writeTofile(recordFile, str(i) + ','+ str(j) + ","+ str(fub))

    writeTofile(recordFile, 'experimentNum' + ','+ 'executionNum' + ","+ 'mtub')
    for i in range(0, experimentNum):
        for j in range(0, executionNum):
            mtub = fringeUpperBound(G, mtub = True)
            writeTofile(recordFile, str(i) + ','+ str(j) + ","+ str(mtub))

    writeTofile(recordFile, 'experimentNum' + ','+ 'executionNum' + ","+ 'rtub')
    for i in range(0, experimentNum):
        for j in range(0, executionNum):
            rtub = randomTreeUpperBound(G)
            writeTofile(recordFile, str(i) + ','+ str(j) + ","+ str(rtub))

    writeTofile(recordFile, 'experimentNum' + ','+ 'executionNum' + ","+ 'hdtub')
    for i in range(0, experimentNum):
        for j in range(0, executionNum):
            hdtub = highestDegreeTreeUpperBound(G)
            writeTofile(recordFile, str(i) + ','+ str(j) + ","+ str(hdtub))

