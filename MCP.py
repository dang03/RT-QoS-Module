#!/usr/bin/env python
# encoding: utf-8

__author__ = 'Dani'

"""
Critical functions and computation algorithms for Pathfinder main process
Functions and algorithms are NetworkX graph based
"""

import networkx as nx
from PathDrawer import to_edge_path, to_node_path
import json


"""
Algorithm for edge cost computation - critical for AKSP and AKLP algorithms
Returns the total cost of an end-to-end path
"""
# returns a path length, such as hop count
def path_length(graph, path, weight=None):
    pathLength = 0

    for i in range(len(path) - 1):
        print "edge1:", path[i]
        print "edge2:", path[i + 1]
        print graph.has_edge(path[i], path[i + 1])
        if graph.has_edge(path[i], path[i + 1]) or graph.has_edge(path[i + 1], path[i]):

            edge = graph.get_edge_data(path[i], path[i + 1])
            print "edge:", edge
            edge = edge.items()[0]
            print edge
            try:
                new_length = edge[1][weight]
                pathLength += new_length
                print "COSTE1:", pathLength
            except:
                # no weight attribute, then edge counter
                pathLength += 1
                print "COSTE2:", pathLength

        print graph.has_edge(path[i], path[i + 1])
    print "COSTE3:", pathLength
    return pathLength


"""
Function used for loop detection in AKSP and AKLP graph algorithms
"""
# detect loops on a graph
def has_loop(rootPath, spurPath):
    loop = False
    for x in rootPath:
        print "X", x
        for y in spurPath:
            print "Y", y
            if x == y:
                loop = True
    return loop

# path selector from k-path list


"""
Comment
"""


def path_select(res, cos_res, kPath):
    kRange = range(len(res))
    kCheck = len(res)
    print "rango:", kRange
    print "check:", kCheck
    print "k:", kPath
    if kPath <= 0 or kPath > kCheck:
        print "ERROR: Invalid k value"
        path = None
        pathCost = None


    else:
        path = res[kPath - 1]
        pathCost = cos_res[kPath - 1]

    return path, pathCost


"""
AKSP Algorithm: Adaptation to NetworkX of Yen's K-shortest-paths
FINAL VERSION:
num_k: number of solutions to find (iteration of returned path)
weights: edge cost to compute

"""


def AkSP(graph, source, target, num_k, weights):
    import Queue

    # shortest path from source to destination
    A = [list(nx.all_shortest_paths(graph, source, target, weight=weights))[0]]
    print "A", A
    A_costs = [path_length(graph, A[0], weights)]
    print "A-costs", A_costs

    # Initialize heap to store potential Kth shortest path
    B = Queue.PriorityQueue()

    for k in range(1, num_k):
        print range(1, num_k)
        print "Kini!!!", k
        # The spur node ranges from first node to next to last node in shortest path
        try:
            for i in range(len(A[k - 1]) - 1):

                loop = False
                # Spur node is retrieved from previous k-shortest path, k -1
                spurNode = A[k - 1][i]
                print "SPURNODE", spurNode
                # Sequence of nodes from source to spur node of previous k-shortest path
                rootPath = A[k - 1][:i]
                print "ROOTPATH", rootPath
                """
                for u, v, edata in graph.edges(data=True):
                    print u, v, edata
                """
                # Store removed edges
                removedEdges = []

                for path in A:
                    print "for path in A", A
                    if len(path) - 1 > i and rootPath == path[:i]:
                        # remove links that are part of the previous shortest path which share the same root path
                        edge = graph.get_edge_data(path[i], path[i + 1])

                        print "EDGE", edge

                        print "PATH!", path[i]
                        print "PATH!+1", path[i + 1]

                        if edge is None or len(edge) == 0:
                            print "deleted edge"
                            continue  # deleted edge

                        edge = edge.items()  # [0]
                        print "EDGE-DEL", (path[i], path[i + 1], edge)
                        removedEdges.append((path[i], path[i + 1], edge))
                        graph.remove_edge(path[i], path[i + 1])
                        try:
                            graph.remove_edge(path[i], path[i + 1])
                        except:
                            print "REMOVED", graph.get_edge_data(path[i], path[i + 1])

                # calculate the spur path from spur node to the sink
                print "removedEdges", removedEdges
                print "spurnode", spurNode
                print "target", target
                for u, v, edata in graph.edges(data=True):
                    print u, v, edata

                try:
                    spurPath = list(nx.all_shortest_paths(graph, spurNode, target, weight=weights))[0]
                    print "spur", spurPath
                except:
                    spurPath = []

                if len(spurPath) > 0:
                    # Complete path is made up from root path and spur path
                    no_valid = has_loop(rootPath, spurPath)
                    if no_valid:
                        print "HAS_LOOP"
                        loop = True
                        continue
                    totalPath = rootPath + spurPath
                    print "total", totalPath
                    print "WEIGHT", weights
                    totalPathCost = path_length(graph, totalPath, weights)
                    # add the potential k-shortest path to the heap
                    B.put((totalPathCost, totalPath))

                # add back the edges that were removed from the graph
                for u, v, edata in graph.edges(data=True):
                    print u, v, edata
                print "printremoved", removedEdges

                for removedEdge in removedEdges:
                    print "REMOVE", removedEdge
                    node_start, node_end, data = removedEdge
                    print "node start", node_start
                    print "node end", node_end
                    print "data", data
                    data1, data2 = data
                    print data1
                    print data2
                    key, attributes = data1
                    print "GRAFO", graph.get_edge_data(node_start, node_end)
                    graph.add_edge(node_start, node_end, key=key, **attributes)
                    print "GRAFO2", graph.get_edge_data(node_start, node_end)
                    key, attributes = data2
                    graph.add_edge(node_start, node_end, key=key, **attributes)
                    print "GRAFO3", graph.get_edge_data(node_start, node_end)
                    print range(1, num_k)
                    print "added!!!"

        except:
            while True:

                try:
                    cost_, path_ = B.get_nowait()
                except:
                    break

                print cost_, path_

                if path_ not in A:
                    # Found new path to add
                    A.append(path_)
                    A_costs.append(cost_)
                    break

            return A, A_costs

        # Sort the potential k-shortest paths by cost
        # B is already sorted
        # Add the lowest cost path that becomes the k-shortest path
        while True:

            try:
                cost_, path_ = B.get_nowait()
            except:
                break

            print cost_, path_

            if path_ not in A:
                # Found new path to add
                A.append(path_)
                A_costs.append(cost_)
                break

    return A, A_costs





"""
AKLP Algorithm: NetworkX K-longest-paths computation algorithm
FINAL VERSION:
num_k: number of solutions to find (iteration of returned path)
weights: edge cost to compute

"""


def AkLP(graph, source, target, num_k, weight):
    maxPath = None
    maxCost = 0
    maxAux = 0

    import Queue

    # Initialize heap to store potential Kth shortest path
    A_costs = []
    B = []

    # shortest path from source to destination
    A = list(nx.all_simple_paths(graph, source, target))  # [0]]

    print "A", A

    i = 0
    for path in A:
        print "path1", path

        print "INDEX", [A.index(path)]
        cost = path_length(graph, A[A.index(path)], weight)
        print "cost", cost

        if cost > maxAux:
            maxAux = cost
            A_costs.insert(i, maxAux)
            print "maxAUX", maxAux

            i += 1
            print i
            B.append(path)


    print "RANGO", len(B)
    if len(B) <= num_k:
        print "Bfinal", B
        print "Afinal", A_costs
        return B, A_costs

    else:
        while len(B) > num_k:
            print "A-costs", A_costs
            print "B", B
            B.pop(0)
            A_costs.pop(0)
        print "Bfinal", B
        print "Afinal", A_costs
        return B, A_costs



def ALP(graph, source, target, weight):
    maxPath = None
    maxCost = 0


    for path in nx.all_simple_paths(graph, source, target):
        totalAux = 0

        edgePath = to_edge_path(path, H)
        print "PATH", edgePath
        for edge in edgePath:
            edge1, edge2 = edge
            print edge1, edge2

            edgeData = H.get_edge_data(edge1, edge2)
            sedgeData = edgeData.items()[0]
            print "SEDGE", sedgeData

            try:
                new_length = sedgeData[1][weight]
                totalAux += new_length
                print "TOTALAUX", totalAux
                if totalAux > maxCost:
                    maxCost = totalAux
                    maxPath = edgePath
            except:
                print "ERROR!"


    print "TOTAL", maxCost
    maxPath = to_node_path(maxPath)
    print "PATH", maxPath
    return maxPath, maxCost



def maxLength_path(graph, path, weight):
    totalCost = 0
    maximumPath = None
    for i in range(len(path)):
        print "paths:", path[i]
        parsed_path = path[i]
        print "pathPARSE:", parsed_path

        print "-------------------"
        Cost = path_length(graph, parsed_path, weight)
        print "-------------------"
        if Cost > totalCost:
            totalCost = Cost
            print "Total:", totalCost
            maximumPath = path[i]
    return maximumPath, totalCost


def longestPath(graph, source, target, weight, visited=None):
    """
    Requires global list for visited nodes
    """
    dist = 0
    maxa = 0

    print source
    if not visited:
        print "vacia"
        visited = []
        visited.append(source)
        print visited

    else:
        visited.append(source)
        print "visited", visited
        print "stops"

    print "visitaos", visited
    print "NODE DATA", graph.nodes(data=True)
    node_edges = graph.edges(source, data=True)
    print "NODE EDGES", node_edges
    for edge in node_edges:
        print edge
        endNode = edge[1]
        print "endNode", endNode

        if endNode not in visited:
            print "no visitao"

            print "entra!", edge[2][weight]
            dist = edge[2][weight] + longestPath(graph, endNode, target, weight, visited)
            print "dist", dist
            if dist > maxa:
                maxa = dist

    visited.remove(source)
    print "MAXA IS=", maxa
    return maxa


"""
------------------------------------------------------------------------------
$$$TEST ZONE$$$
------------------------------------------------------------------------------
"""

M = nx.MultiGraph()

M.add_edge('00:00:05', '00:00:06', srcPort='edgeSrcPort', dstPort='edgeDstPort', bandwidth=4, delay=0.7, jitter=0.5, loss=30)
M.add_edge('00:00:06', '00:00:05', srcPort='edgeSrcPort', dstPort='edgeDstPort', bandwidth=4, delay=0.7, jitter=0.5, loss=30)
M.add_edge('00:00:05', '00:00:07', srcPort='edgeSrcPort', dstPort='edgeDstPort', bandwidth=30, delay=0.3, jitter=0.1, loss=10)
M.add_edge('00:00:07', '00:00:05', srcPort='edgeSrcPort', dstPort='edgeDstPort', bandwidth=30, delay=0.3, jitter=0.1, loss=10)
M.add_edge('00:00:05', '00:00:08', srcPort='edgeSrcPort', dstPort='edgeDstPort', bandwidth=11, delay=0.3, jitter=0.3, loss=20)
M.add_edge('00:00:08', '00:00:05', srcPort='edgeSrcPort', dstPort='edgeDstPort', bandwidth=11, delay=0.3, jitter=0.3, loss=20)
M.add_edge('00:00:06', '00:00:07', srcPort='edgeSrcPort', dstPort='edgeDstPort', bandwidth=11, delay=0.9, jitter=0.8, loss=40)
M.add_edge('00:00:07', '00:00:06', srcPort='edgeSrcPort', dstPort='edgeDstPort', bandwidth=11, delay=0.9, jitter=0.8, loss=40)
M.add_edge('00:00:06', '00:00:08', srcPort='edgeSrcPort', dstPort='edgeDstPort', bandwidth=30, delay=0.4, jitter=0.2, loss=20)
M.add_edge('00:00:08', '00:00:06', srcPort='edgeSrcPort', dstPort='edgeDstPort', bandwidth=30, delay=0.4, jitter=0.2, loss=20)
M.add_edge('00:00:07', '00:00:08', srcPort='edgeSrcPort', dstPort='edgeDstPort', bandwidth=30, delay=0.2, jitter=0.1, loss=5)
M.add_edge('00:00:08', '00:00:07', srcPort='edgeSrcPort', dstPort='edgeDstPort', bandwidth=30, delay=0.2, jitter=0.1, loss=5)

"""
M.add_edge('00:00:04', '00:00:06', srcPort='edgeSrcPort', dstPort='edgeDstPort', weight=3, cost=2)
M.add_edge('00:00:03', '00:00:06', srcPort='edgeSrcPort', dstPort='edgeDstPort', weight=11, cost=3)
M.add_edge('00:00:01', '00:00:05', srcPort='edgeSrcPort', dstPort='edgeDstPort', weight=5, cost=4)
M.add_edge('00:00:02', '00:00:05', srcPort='edgeSrcPort', dstPort='edgeDstPort', weight=18, cost=2)
M.add_edge('00:00:03', '00:00:05', srcPort='edgeSrcPort', dstPort='edgeDstPort', weight=19, cost=3)
"""
print M.edges()

H = nx.MultiGraph(M)


"""
def MCP Aggregator Function
"""

newGraph =nx.MultiGraph()
for edge in nx.edges_iter(M):
    print 'EDGE', edge
    edge1, edge2 = edge
    total = 0

    try:
        delay = M[edge1][edge2][0]['delay']
        print 'delay', delay
        total =+ delay
    except:
        continue

    try:
        jitter = M[edge1][edge2][0]['jitter']
        print 'jitter', jitter
        total =+ jitter
    except:
        pass

    try:
        ploss = M[edge1][edge2][0]['packet-loss']
        print 'packet-loss', ploss
    except:
        pass

    try:
        bandwidth = M[edge1][edge2][0]['bandwidth']
        print 'bandwidth', bandwidth
        total = total / bandwidth
    except:
        pass

    print "Total", total
    newGraph.add_edge(edge1, edge2, total=total)

for link in newGraph.edges_iter(data=True):
    print "newGraph.link", link

for node in newGraph.nodes_iter(data=True):
    print "newGraph.node", node



res, cos_res = AkSP(newGraph, '00:00:05', '00:00:06', 3, 'total')
print "res", res
print "cos_res", cos_res







"""
visited=[]
lonpa = longestPath(M, '00:00:05', '00:00:06', 'weight')
print "longest", lonpa
"""

"""
camino, coste = AkLP(M, '00:00:05', '00:00:06', 2, 'weight')
print "RESULTAO", camino
print "RESULTAO", coste
"""

"""
camino, coste = ALP(M, '00:00:05', '00:00:06', 'delay')
print "RESULTAO", camino
print "RESULTAO", coste
"""






"""
N = nx.MultiGraph(M)
res, cos_res = yen_networkx(N, '00:00:01', '00:00:03', 4, 'weight')
print "res2", res
print "cos_res2", cos_res
"""

"""
path = list(nx.all_simple_paths(M, '00:00:01', '00:00:06', 'cost'))
print path
"""

"""
ultimate_path, ultimate_cost = maxLength_path(H, res, 'weight')
print "path", ultimate_path
print "cost", ultimate_cost, "\n"
"""

"""
ulti_path, ulti_cost = path_select(res, cos_res, 4)
print "path", ulti_path
print "cost", ulti_cost
"""

