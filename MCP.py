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
import random
import matplotlib.pyplot as plt


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


def AkSP(grapho, source, target, num_k, weights):
    graph = nx.MultiGraph(grapho)
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
    maxAvgAux =0


    # Initialize lists to store potential Kth longest path
    A_costs = []
    B = []

    # all simple paths from source to destination
    A = list(nx.all_simple_paths(graph, source, target))  # [0]]

    print "A", A

    i = 0
    for path in A:
        print "path1", path

        print "INDEX", [A.index(path)]
        cost = path_length(graph, A[A.index(path)], weight)
        print "cost", cost
        avgCost = cost / (len(path) - 1)

        if avgCost > maxAvgAux:
            maxAux = cost
            maxAvgAux = avgCost

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
    maxAvgCost = 0
    iteration = 0

    for path in nx.all_simple_paths(graph, source, target):
        totalAux = 0
        iteration += 1


        edgePath = to_edge_path(path, graph)
        print "PATH", edgePath
        for edge in edgePath:
            edge1, edge2 = edge
            print edge1, edge2

            edgeData = graph.get_edge_data(edge1, edge2)
            sedgeData = edgeData.items()[0]
            print "SEDGE", sedgeData

            try:
                new_length = sedgeData[1][weight]
                totalAux += new_length

                print "hop-count", (len(path)-1)
#
                print "TOTALAUX", totalAux
                print "preMAXCOST", maxCost
                print "EDGEPATH", edgePath

                if edge == edgePath[(len(edgePath)-1)]:

                    avgAux = totalAux / (len(path) - 1)
                    if avgAux > maxAvgCost:
                        maxCost = totalAux
                        maxAvgCost = avgAux
                        maxPath = edgePath
            except:
                print "ERROR!"

    print "ITERATION", iteration
    print "TOTAL", maxCost
    print "AVGTOTAL", maxAvgCost
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
MCP edge stats Aggregator Function for multiple constraints graph and QoS requests
"""
def stAggregate(graph):
    newGraph = nx.MultiGraph()

    for edge in nx.edges_iter(graph):
        print 'EDGE', edge
        edge1, edge2 = edge
        total = 1

        try:
            delay = graph[edge1][edge2][0]['delay']
            print 'delay', delay
            if delay == 0:
                delay = 1

            total = total * delay
        except:
            continue

        try:
            jitter = graph[edge1][edge2][0]['jitter']
            print 'jitter', jitter
            if jitter == 0:
                jitter = 1

            total = total * jitter
        except:
            pass

        try:
            ploss = graph[edge1][edge2][0]['packet-loss']
            print 'packet-loss', ploss
            if ploss == 0:
                ploss = 1

            total = total * ploss
        except:
            pass

        try:
            bandwidth = graph[edge1][edge2][0]['bandwidth']
            print 'bandwidth', bandwidth
            if bandwidth == 0:
                bandwidth = 1

            total = total / bandwidth
        except:
            pass

        print "Total", total
        newGraph.add_edge(edge1, edge2, total=total)

    for link in newGraph.edges_iter(data=True):
        print "newGraph.edge", link

    for node in newGraph.nodes_iter(data=True):
        print "newGraph.node", node

    return newGraph

"""
MCP Aggregation function only for testing purposes
"""
def stAggregate_test(graph):
    newGraph = nx.MultiGraph()

    for edge in nx.edges_iter(graph):
        print 'EDGE', edge
        edge1, edge2 = edge
        total = 1

        try:
            delay = graph[edge1][edge2]['delay']
            print 'delay', delay
            if delay == 0:
                delay = 1

            total = total * delay
        except:
            continue

        try:
            jitter = graph[edge1][edge2]['jitter']
            print 'jitter', jitter
            if jitter == 0:
                jitter = 1

            total = total * jitter
        except:
            pass

        try:
            ploss = graph[edge1][edge2]['packet-loss']
            print 'packet-loss', ploss
            if ploss == 0:
                ploss = 1

            total = total * ploss
        except:
            pass

        try:
            bandwidth = graph[edge1][edge2]['bandwidth']
            print 'bandwidth', bandwidth
            if bandwidth == 0:
                bandwidth = 1

            total = total / bandwidth
        except:
            pass

        print "Total", total
        newGraph.add_edge(edge1, edge2, total=total)

    for link in newGraph.edges_iter(data=True):
        print "newGraph.edge", link

    for node in newGraph.nodes_iter(data=True):
        print "newGraph.node", node

    return newGraph


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
"""
print M.edges()
"""
H = nx.MultiGraph(M)

"""
agGraph = stAggregate(M)

res, cos_res = AkSP(agGraph, '00:00:05', '00:00:06', 5, 'total')
print "res", res
print "cos_res", cos_res
"""


A = nx.complete_graph(8)

for edge in A.edges_iter(data=True):
    edge1, edge2, nfo = edge
    bnd = random.randrange(1, 100)
    dly = random.uniform(1, 10)
    jtr = random.uniform(1, 5)
    pls = random.randrange(0, 100)
    A.add_edge(edge1, edge2, bandwidth=bnd, delay=dly, jitter=jtr, loss=pls)


agGraph = stAggregate_test(A)

for edge in agGraph.edges_iter(data=True):
    print "aggregated", edge


res, cos_res = AkLP(agGraph, random.randrange(1, 2), random.randrange(3, 8), 3, 'total')
print "res", res
print "cos_res", cos_res




"""
visited=[]
lonpa = longestPath(M, '00:00:05', '00:00:06', 'weight')
print "longest", lonpa
"""

"""
res, cos_res = AkSP(M, '00:00:05', '00:00:06', 3, 'delay')
print "res", res
print "cos_res", cos_res
"""

"""
res, cos_res = AkLP(M, '00:00:05', '00:00:06', 5, 'bandwidth')
print "PATH", res
print "COST", cos_res
"""

"""
res, cos_res = ALP(M, '00:00:05', '00:00:06', 'bandwidth')
print "path", res
print "cost", cos_res
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


def plot_path(agGraph, maxPath):
    e2e = []
    source = maxPath[0]
    destination = maxPath[(len(maxPath)-1)]
    e2e.append(source)
    e2e.append(destination)
    print maxPath
    for i in range(len(maxPath)-1):
        print "is there path from", maxPath[i], maxPath[i+1], "?", agGraph.has_edge(maxPath[i], maxPath[i+1])
    maxPathList = to_edge_path(maxPath)
    print maxPathList
    eFail = [(u, v) for (u, v, d) in agGraph.edges(data=True)]

    print eFail

    pos = nx.spring_layout(agGraph)    # positions for all nodes
    nx.draw_networkx_nodes(agGraph, pos, node_size=700, node_color='b')
    nx.draw_networkx_nodes(agGraph, pos, nodelist=maxPath, node_size=700, node_color='r')
    nx.draw_networkx_nodes(agGraph, pos, nodelist=e2e, node_color='y', node_shape='s')

    nx.draw_networkx_edges(agGraph, pos, edgelist=maxPathList, width=6, alpha=1, edge_color='r')
    nx.draw_networkx_edges(agGraph, pos, edgelist=eFail, width=2, alpha=0.5)


    nx.draw_networkx_labels(agGraph, pos, font_size=20, font_family='sans-serif')


    plt.axis('off')
    plt.savefig(("/home/i2cat/Documents/test.png"))  # save as png
    plt.show()  # display


maxPath, length = path_select(res, cos_res, len(res))
print maxPath


plot_path(agGraph, maxPath)