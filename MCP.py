#!/usr/bin/env python
# encoding: utf-8

__author__ = 'Dani'

import networkx as nx

def path_length(graph, path, weight=None):
    pathLength = 0
    for i in range(len(path)):
        if i > 0:
            if graph.has_edge(path[i - 1], path[i]):
                edge = graph.get_edge_data(path[i - 1], path[i])
                #print "edge", edge[0]
                try:
                    pathLength += edge[0][weight]
                except:
                    # no weight attribute, then edge counter
                    pathLength += 1

    return pathLength


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
            print spurNode
            # Sequence of nodes from source to spur node of previous k-shortest path
            rootPath = A[k-1][:i]

            # Store removed edges
            removedEdges = []

            for path in A:
                    if len(path) - 1 > i and rootPath == path[:i]:
                        # remove links that are part of the previous shortest path which share the same root path
                        edge = graph.get_edge_data(path[i], path[i+1])
                        if len(edge) == 0:
                            continue # deleted edge
                        edge = edge[0]
                        removedEdges.append((path[i], path[i+1], edge))
                        graph.remove_edge(path[i], path[i+1])

            # calculate the spur path from spur node to the sink
            spurPath = list(nx.all_shortest_paths(graph, spurNode, target, weight=weights))[0]
            print "root", rootPath
            print "spur", spurPath

            if len(spurPath) > 0:
                # Complete path is made up from root path and spur path
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
        Cost = path_length(graph, path[i], weight)
        if Cost > totalCost:
            totalCost = Cost
            maximumPath = path[i]
    return totalCost,  maximumPath


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




M = nx.MultiGraph()

M.add_edge('00:00:01', '00:00:02', srcPort='edgeSrcPort', dstPort='edgeDstPort', weight=7, cost=3)
M.add_edge('00:00:01', '00:00:04', srcPort='edgeSrcPort', dstPort='edgeDstPort', weight=19, cost=3)
M.add_edge('00:00:01', '00:00:06', srcPort='edgeSrcPort', dstPort='edgeDstPort', weight=24, cost=3)
M.add_edge('00:00:02', '00:00:03', srcPort='edgeSrcPort', dstPort='edgeDstPort', weight=12, cost=3)
M.add_edge('00:00:02', '00:00:04', srcPort='edgeSrcPort', dstPort='edgeDstPort', weight=10, cost=3)
M.add_edge('00:00:01', '00:00:03', srcPort='edgeSrcPort', dstPort='edgeDstPort', weight=12, cost=3)
M.add_edge('00:00:04', '00:00:06', srcPort='edgeSrcPort', dstPort='edgeDstPort', weight=3, cost=3)
M.add_edge('00:00:03', '00:00:06', srcPort='edgeSrcPort', dstPort='edgeDstPort', weight=11, cost=3)
M.add_edge('00:00:01', '00:00:05', srcPort='edgeSrcPort', dstPort='edgeDstPort', weight=5, cost=3)
M.add_edge('00:00:02', '00:00:05', srcPort='edgeSrcPort', dstPort='edgeDstPort', weight=18, cost=3)
M.add_edge('00:00:03', '00:00:05', srcPort='edgeSrcPort', dstPort='edgeDstPort', weight=19, cost=3)


res, cos_res = yen_networkx(M, '00:00:01', '00:00:06', 4, 'weight')
print "res", res
print "cos_res", cos_res

path = list(nx.all_simple_paths(M, '00:00:01', '00:00:06', 'weight'))
print path

ultimate_cost, ultimate_path = maxLength_path(M, res, 'weight')
print "path", ultimate_path
print "cost", ultimate_cost

"""
camino = ['00:00:01']
cgraph = nx.Graph(M)
for node in cgraph.nodes_iter():
        cgraph.add_node(node, visited='0')
longestPath(cgraph, '00:00:01', '00:00:06', 'weight')
"""