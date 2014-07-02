#!/usr/bin/env python
# encoding: utf-8

__author__ = 'Dani'

import networkx as nx



# returns a path length, as hop count
def path_length(graph, path, weight=None):
    pathLength = 0

    for i in range(len(path)-1):
        print "edge1:", path[i]
        print "edge2:", path[i+1]
        print graph.has_edge(path[i], path[i+1])
        if graph.has_edge(path[i], path[i+1]) or graph.has_edge(path[i+1], path[i]):

            edge = graph.get_edge_data(path[i], path[i+1])
            print "edge:", edge
            try:
                pathLength += edge[0][weight]
                print "COSTE1:", pathLength
            except:
                # no weight attribute, then edge counter
                pathLength += 1
                print "COSTE2:", pathLength

        print graph.has_edge(path[i], path[i+1])
    print "COSTE3:", pathLength
    return pathLength

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
        path = res[kPath-1]
        pathCost = cos_res[kPath-1]

    return path, pathCost








"""
Adaptation to NetworkX Yen's K-shortest-paths
FINAL VERSION:
num_k: number of solutions
weights: cost to compute

"""
def yen_networkx(graph, source, target, num_k, weights):
    import Queue

    # shortest path from source to destination
    A = [list(nx.all_shortest_paths(graph, source, target, weight=weights))[0]]
    print "A", A
    A_costs = [path_length(graph, A[0], weights)]
    print "A-costs", A_costs

    # Initialize heap to store potential Kth shortest path
    B = Queue.PriorityQueue()

    for k in range(1, num_k):
        # The spur node ranges from first node to next to last node in shortest path
        for i in range(len(A[k-1])-1):
            # Spur node is retrieved from previous k-shortest path, k -1
            spurNode = A[k-1][i]
            print "SPURNODE", spurNode
            # Sequence of nodes from source to spur node of previous k-shortest path
            rootPath = A[k-1][:i]
            print "ROOTPATH", rootPath

            # Store removed edges
            removedEdges = []

            for path in A:
                    if len(path) - 1 > i and rootPath == path[:i]:
                        # remove links that are part of the previous shortest path which share the same root path
                        edge = graph.get_edge_data(path[i], path[i+1])
                        print "EDGE", edge
                        print "PATH!", path[i]
                        print "PATH!+1", path[i+1]
                        if edge is None or len(edge) == 0:
                            continue    # deleted edge
                        edge = edge[0]
                        removedEdges.append((path[i], path[i+1], edge))
                        graph.remove_edge(path[i], path[i+1])

            # calculate the spur path from spur node to the sink
            spurPath = list(nx.all_shortest_paths(graph, spurNode, target, weight=weights))[0]
            print "spur", spurPath

            if len(spurPath) > 0:
                # Complete path is made up from root path and spur path
                no_valid = has_loop(rootPath, spurPath)
                if no_valid:
                    continue
                totalPath = rootPath + spurPath
                print "total", totalPath
                totalPathCost = path_length(graph, totalPath, weights)
                # add the potential k-shortest path to the heap
                B.put((totalPathCost, totalPath))

            # add back the edges that were removed from the graph
            for removedEdge in removedEdges:
                node_start, node_end, attributes = removedEdge
                graph.add_edge(node_start, node_end, **attributes)


        # Sort the potential k-shortest paths by cost
        # B is already sorted
        # Add the lowest cost path that becomes the k-shortest path
        while True:
            cost_, path_ = B.get()
            if path_ not in A:
                # Found new path to add
                A.append(path_)
                A_costs.append(cost_)
                break

    return A, A_costs



def maxLength_path(graph, path, weight):
    totalCost = 0
    maximumPath = None
    for i in range(len(path)):
        print "CAMINACO:", path[i]
        parsed_path = path[i]
        print "CAMINOPARSE:", parsed_path

        print "-------------------"
        Cost = path_length(graph, parsed_path, weight)
        print "-------------------"
        if Cost > totalCost:
            totalCost = Cost
            print "COSTACO:", totalCost
            maximumPath = path[i]
    return maximumPath, totalCost


def longestPath(graph, source, target, weight):
    dist = 0
    maxa = 0

    graph.add_node(source, visited='1')
    print "NODE DATA", graph.nodes(data=True)
    node_edges = graph.edges(source, data=True)
    print "NODE EDGES", node_edges
    for edge in node_edges:
        print edge
        endNode = edge[1]
        print "endNode", endNode

        if graph.node[endNode]['visited'] == '0':
            if endNode == target:
                dist = edge[2][weight]
                print "dist", dist
                if dist > maxa:
                    maxa = dist


            else:
                print "entra!", edge[2][weight]
                dist = edge[2][weight] + longestPath(graph, endNode, target, weight)
                print "dist", dist
                if dist > maxa:
                    maxa = dist



    graph.add_node(source, visited='0')
    print "MAXA IS=", maxa
    return maxa

"""
---------------------------------------
"""

M = nx.MultiGraph()

M.add_edge('00:00:01', '00:00:02', srcPort='edgeSrcPort', dstPort='edgeDstPort', weight=7, cost=3)
M.add_edge('00:00:01', '00:00:04', srcPort='edgeSrcPort', dstPort='edgeDstPort', weight=19, cost=4)
M.add_edge('00:00:01', '00:00:06', srcPort='edgeSrcPort', dstPort='edgeDstPort', weight=24, cost=2)
M.add_edge('00:00:02', '00:00:03', srcPort='edgeSrcPort', dstPort='edgeDstPort', weight=12, cost=5)
M.add_edge('00:00:02', '00:00:04', srcPort='edgeSrcPort', dstPort='edgeDstPort', weight=10, cost=4)
M.add_edge('00:00:01', '00:00:03', srcPort='edgeSrcPort', dstPort='edgeDstPort', weight=12, cost=1)
M.add_edge('00:00:04', '00:00:06', srcPort='edgeSrcPort', dstPort='edgeDstPort', weight=3, cost=2)
M.add_edge('00:00:03', '00:00:06', srcPort='edgeSrcPort', dstPort='edgeDstPort', weight=11, cost=3)
M.add_edge('00:00:01', '00:00:05', srcPort='edgeSrcPort', dstPort='edgeDstPort', weight=5, cost=4)
M.add_edge('00:00:02', '00:00:05', srcPort='edgeSrcPort', dstPort='edgeDstPort', weight=18, cost=2)
M.add_edge('00:00:03', '00:00:05', srcPort='edgeSrcPort', dstPort='edgeDstPort', weight=19, cost=3)


H = nx.MultiGraph(M)
res, cos_res = yen_networkx(M, '00:00:01', '00:00:06', 4, 'cost')
print "res", res
print "cos_res", cos_res

"""
path = list(nx.all_simple_paths(M, '00:00:01', '00:00:06', 'cost'))
print path
"""


ultimate_path, ultimate_cost = maxLength_path(H, res, 'cost')
print "path", ultimate_path
print "cost", ultimate_cost, "\n"

ulti_path, ulti_cost = path_select(res, cos_res, 4)
print "path", ulti_path
print "cost", ulti_cost



"""
camino = ['00:00:01']
cgraph = nx.Graph(M)
for node in cgraph.nodes_iter():
        cgraph.add_node(node, visited='0')
longestPath(cgraph, '00:00:01', '00:00:06', 'weight')
"""