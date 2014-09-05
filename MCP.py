#!/usr/bin/env python
# encoding: utf-8

__author__ = 'Dani'

"""
Critical functions and computation algorithms for Pathfinder main process
Functions and algorithms are NetworkX graph based
"""

__all__ = ['multiEdgeKey',
           'path_length',
           'path_select',
           'plot_path',
           'maxLength_path',
           'longestPath',
           'AkLP',
           'ALP',
           'AkSP',
           'has_loop',
           'stAggregate',
           'stAggregate_test']

import networkx as nx
from networkx.readwrite import json_graph
from PathDrawer import to_edge_path, to_node_path
import json
import os
import random
import matplotlib.pyplot as plt


def multiEdgeKey(path, graph):
    # returns a path in edge-key format
    key_path = []
    edgePath = to_edge_path(path, graph)
    print "PATH", edgePath

    for edge in edgePath:
        edge1, edge2 = edge
        print "nodes", edge1, edge2

        edgeData = graph.get_edge_data(edge1, edge2)
        print "edgeData", edgeData

        print "RANGO", range(len(edgeData))
        num_edges = len(edgeData) / 2
        print num_edges

        # each node connection has two edge layers or multiple edges, select the edge with higher cost
        max_length = 0
        for i in range(len(edgeData)):
            if i % 2 == 0:
                kedgeData = edgeData.keys()[i]
                print "KEDGE", kedgeData
                key_path.append(kedgeData)

                """
                edgeSrcPort = sedgeData[1]['srcPort']
                edgeDstPort = sedgeData[1]['dstPort']
                print "srcPORT", edgeSrcPort
                print "dstPORT", edgeDstPort
                """
    return key_path


"""
                aux_length = sedgeData[1][weight]

                # if a higher cost found, updates the max value
                if aux_length > max_length:
                    print "UPDATES max_length"
                    max_length = aux_length

                    maxPath.append({"switch": edge1})
                    maxPath.append({"port": edgeSrcPort})
                    maxPath.append({"switch": edge2})
                    maxPath.append({"port": edgeDstPort})
"""

"""
Algorithm for edge cost computation - critical for AKSP and AKLP algorithms
Returns the total cost of an end-to-end path
"""
# returns a path length, such as hop count
def path_length(graph, path, weight=None, algorithm=None):
    pathLength = 0
    multiPathLength = []
    keyPath = []


    for i in range(len(path) - 1):
        print "given_path", path
        node1 = path[i]
        node2 = path[i + 1]
        print "edge1:", path[i]
        print "edge2:", path[i + 1]
        print graph.has_edge(path[i], path[i + 1])
        if graph.has_edge(path[i], path[i + 1]) or graph.has_edge(path[i + 1], path[i]):

            edge = graph.get_edge_data(path[i], path[i + 1])
            print "edge:", edge

            num_edges = len(edge) / 2
            print "num_edges", num_edges

            if num_edges > 1:

                nodeback1 = None
                nodeback2 = None

                selEdge_cost = None
                selKey = None

                keyPathe = []

                for i in range(len(edge) / 2):

                    edgekey = edge.keys()[i]
                    print "edge key", edgekey
                    print weight
                    #print "item", graph.edge[node1][node2][edgekey][weight]
                    try:
                        if algorithm == 'AkLP':
                            edge_cost = graph.edge[node1][node2][edgekey][weight]
                            print "edge's cost", edge_cost

                            if selEdge_cost is None:
                                selEdge_cost = edge_cost
                                selKey = edgekey


                            elif edge_cost > selEdge_cost:
                                selEdge_cost = edge_cost
                                print "stored_cost", selEdge_cost
                                selKey = edgekey
                                print "stored_key", selKey


                        elif algorithm == 'AkSP':
                            edge_cost = graph.edge[node1][node2][edgekey][weight]

                            if selEdge_cost is None:
                                selEdge_cost = edge_cost
                                selKey = edgekey

                            elif edge_cost < selEdge_cost:
                                selEdge_cost = edge_cost
                                print "stored_cost", selEdge_cost
                                selKey = edgekey
                                print "stored_key", selKey


                        else:
                            new_length = graph.edge[node1][node2][edgekey][weight]
                            multiPathLength.append(new_length)

                            print "COSTEe1:", multiPathLength
                            keyPathe.append(edgekey)
                            print "keyPathe:", keyPathe



                    except:
                        # no weight attribute, then edge counter
                        if node1 != nodeback1 and node2 != nodeback2:
                            pathLength += 1
                            print "COSTEe2:", pathLength
                            keyPathe.append(edgekey)
                        else:
                            keyPathe.append(edgekey)
                            continue

                    nodeback1 = node1
                    nodeback2 = node2

                if (selEdge_cost or selKey) is not None:
                    multiPathLength.append(selEdge_cost)
                    keyPathe.append(selKey)

                keyPath.append(keyPathe)
                print "edge ENDED", multiPathLength, keyPathe, keyPath
                print "ending pathLength", pathLength


            else:
                print "current pathLength", pathLength
                edge = edge.items()[0]
                print "edge items", edge
                # print "item", edge[1][weight]
                try:
                    edgekey = edge[0]
                    print "edge key", edgekey
                    new_length = edge[1][weight]
                    pathLength += new_length
                    keyPath.append(edgekey)
                    print "COSTE1:", pathLength
                    print "keyPath:", keyPath
                    print "ismultipath..", multiPathLength

                except:
                    # no weight attribute, then edge counter
                    pathLength += 1
                    keyPath.append(edgekey)
                    print "COSTE2:", pathLength

    if multiPathLength:

        if algorithm is None:
            # not implemented; algorithm = None will return the end-to-end sum of all edges
            # recommended for weight = None to return the hop-count
            for l in range(len(multiPathLength)):
                 multiPathLength[l] += pathLength

            print "return", multiPathLength, keyPath
            return multiPathLength, keyPath

        else:
            for j in range(len(multiPathLength)):
                pathLength += multiPathLength[j]
                print "final sum", pathLength
            print "return", pathLength, keyPath
            return pathLength, keyPath

    else:
        print "return", pathLength, keyPath
        return pathLength, keyPath


# ####################

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


#####################
# path selector from k-path list
"""
Enables to select custom path item from result list and checks its validity
"""


def path_select(res, key_res, cos_res, kPath):
    kRange = range(len(res))
    kCheck = len(res)
    print "rango:", kRange
    print "check:", kCheck
    print "k:", kPath
    if kPath <= 0 or kPath > kCheck:
        print "ERROR: Invalid k value"
        path = None
        pathCost = None
        keys = None

    else:
        path = res[kPath - 1]
        pathCost = cos_res[kPath - 1]
        keys = key_res[kPath - 1]
    return path, keys, pathCost

#####################
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
    A_costs, A_keys = path_length(graph, A[0], weights, 'AkSP')
    A_costs = [A_costs]
    print "A-costs", A_costs
    print "A-keys", A_keys

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
                    totalPathCost, totalPathKeys = path_length(graph, totalPath, weights, 'AkSP')
                    # add the potential k-shortest path to the heap
                    print "2_costs", totalPathCost
                    print "2_keys", totalPathKeys
                    B.put((totalPathCost, totalPathKeys, totalPath))

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
                    cost_, keys_, path_ = B.get_nowait()
                except:
                    break

                print cost_, keys_, path_

                if path_ not in A:
                    # Found new path to add
                    A.append(path_)
                    A_costs.append(cost_)
                    A_keys.append(keys_)
                    break

            return A, A_keys, A_costs

        # Sort the potential k-shortest paths by cost
        # B is already sorted
        # Add the lowest cost path that becomes the k-shortest path
        while True:

            try:
                cost_, keys_, path_ = B.get_nowait()
            except:
                break

            print cost_, keys_, path_

            if path_ not in A:
                # Found new path to add
                A.append(path_)
                A_costs.append(cost_)
                A_keys.append(keys_)
                break

    return A, A_keys, A_costs


#####################
"""
AKLP Algorithm: NetworkX K-longest-paths computation algorithm
FINAL VERSION:
num_k: number of solutions to find (iteration of returned path)
weights: edge cost to compute
returns lists of nodes paths, edge-key paths and the total cost
of each path, ordered by avg. cost
"""


def AkLP(graph, source, target, num_k, weight):
    maxPath = None
    maxCost = 0
    maxAux = 0
    maxAvgAux = 0


    # Initialize lists to store potential Kth longest path
    A_costs = []
    B = []
    C_keys = []

    # all simple paths from source to destination
    A = list(nx.all_simple_paths(graph, source, target))  # [0]]
    print "A", A

    i = 0
    for path in A:
        print "path1", path

        #print "INDEX", [A.index(path)]
        print "algo", A[A.index(path)]
        #cost = path_length(graph, A[A.index(path)])
        cost, edgeKeys = path_length(graph, A[A.index(path)], weight, 'AkLP')
        print "cost", cost
        print "keys", edgeKeys
        avgCost = cost / (len(path) - 1)

        if avgCost > maxAvgAux:
            maxAux = cost
            maxAvgAux = avgCost

            A_costs.insert(i, maxAux)
            print "maxAUX", maxAux

            i += 1
            print i
            B.append(path)
            C_keys.append(edgeKeys)

    print "RANGO", len(B)
    if len(B) <= num_k:
        print "Bfinal", B
        print "Afinal", A_costs
        print "Cfinal", C_keys
        return B, C_keys, A_costs

    else:
        while len(B) > num_k:
            print "A-costs", A_costs
            print "B", B
            B.pop(0)
            A_costs.pop(0)
            C_keys.pop(0)
        print "Bfinal", B
        print "Afinal", A_costs
        print "Cfinal", C_keys
        return B, C_keys, A_costs



#####################

def ALP(graph, source, target, weight):
    global maxPath
    maxCost = 0
    maxAvgCost = 0
    maxKey = None
    iteration = 0

    # For each end-to-end path, total edge cost is calculated. Then node-pah and edge-key-path are
    # stored to return plus the total cost as a result
    for path in nx.all_simple_paths(graph, source, target):
        #maxPath = []
        keyPath = []
        edgeKey = None

        totalAux = 0
        iteration += 1
        print "paaath", path

        edgePath = to_edge_path(path, graph)
        print "PATH", edgePath

        for edge in edgePath:
            edge1, edge2 = edge
            print "nodes", edge1, edge2

            edgeData = graph.get_edge_data(edge1, edge2)
            print "edgeData", edgeData

            print "RANGO", range(len(edgeData))
            # each node connection has two edge layers or multiple edges, select the edge with higher cost
            max_length = 0
            for i in range(len(edgeData)):
                if i % 2 == 0:
                    sedgeData = edgeData.items()[i]
                    print "SEDGE", sedgeData

                    edgeKey = edgeData.keys()[i]
                    edgeSrcPort = sedgeData[1]['srcPort']
                    edgeDstPort = sedgeData[1]['dstPort']
                    print "edgeKey", edgeKey
                    print "srcPORT", edgeSrcPort
                    print "dstPORT", edgeDstPort

                    aux_length = sedgeData[1][weight]

                    # if a higher cost found, updates the max value
                    if aux_length > max_length:
                        print "UPDATES max_length"
                        max_length = aux_length
                        """
                        maxPath.append({"switch": edge1})
                        maxPath.append({"port": edgeSrcPort})
                        maxPath.append({"switch": edge2})
                        maxPath.append({"port": edgeDstPort})
                        """

            try:
                new_length = max_length
                totalAux += new_length

                print "UPDATE KEY LIST"
                keyPath.append(edgeKey)

                print "hop-count", (len(path) - 1)
                print "TOTALAUX", totalAux
                print "preMAXCOST", maxCost
                print "EDGEPATH", edgePath

                print edge, "==", edgePath[(len(edgePath) - 1)], "?"

                if edge == edgePath[(len(edgePath) - 1)]:
                    avgAux = totalAux / (len(path) - 1)
                    print "avgAux", avgAux
                    print "maxAvgCost", maxAvgCost

                    if avgAux > maxAvgCost:
                        print "UPDATES costs"
                        maxCost = totalAux
                        maxAvgCost = avgAux
                        maxPath = edgePath
                        print "UPDATE maxKey"
                        maxKey = keyPath

            except:
                print "ERROR!"

    print "ITERATION", iteration
    print "TOTAL", maxCost
    print "AVGTOTAL", maxAvgCost
    # uncomment to enable path result as a node path
    maxPath = to_node_path(maxPath)
    print "PATH", maxPath
    print "maxkeyPath", maxKey
    return maxPath, maxKey, maxCost


#####################


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


#####################


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

#####################


"""
MCP edge stats Aggregator Function for multiple constraints graph and QoS requests
"""
#TODO: Hint for possible errors while aggregating QoS parameters that cannot be loaded from edge dict

def stAggregate(graph):
    newGraph = nx.MultiGraph()

    for edge1, edge2, key, data in graph.edges_iter(data=True, keys=True):
        print 'EDGE', edge1, "-", edge2, ":", key, data

        total = 1

        try:
            delay = graph[edge1][edge2][key]['delay']

            """
            print edgeData.keys()[0]
            print edgeData.values()[0]
            print edgeData.items()[0]
            delay = edgeData.keys()[0]['delay']
            """

            print 'delay', delay
            if delay == 0:
                delay = 1

            total = total * delay

        except:
            continue

        try:
            jitter = graph[edge1][edge2][key]['jitter']
            print 'jitter', jitter
            if jitter == 0:
                jitter = 1

            total = total * jitter
        except:
            pass

        try:
            ploss = graph[edge1][edge2][key]['packet-loss']
            print 'packet-loss', ploss
            if ploss == 0:
                ploss = 1

            total = total * ploss
        except:
            pass

        try:
            bandwidth = graph[edge1][edge2][key]['bandwidth']
            print 'bandwidth', bandwidth
            if bandwidth == 0:
                bandwidth = 1

            total = total / bandwidth
        except:
            pass

        print "Total", total
        newGraph.add_edge(edge1, edge2, key=key, total=total)

    for link in newGraph.edges_iter(data=True, keys=True):
        print "newGraph.edge", link

    for node in newGraph.nodes_iter(data=True):
        print "newGraph.node", node

    return newGraph


#####################
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


#####################

def plot_path(agGraph, maxPath=None, e2e=None, eOK=None, eFail=None, qos=None):
    #edgeLabels = {}

    if e2e is None and maxPath is not None:
        e2e = []
        source = maxPath[0]
        destination = maxPath[(len(maxPath) - 1)]
        e2e.append(source)
        e2e.append(destination)

    if maxPath is not None:
        for i in range(len(maxPath) - 1):
            print "is there path from", maxPath[i], maxPath[i + 1], "?", agGraph.has_edge(maxPath[i], maxPath[i + 1])

        maxPathList = to_edge_path(maxPath)
        print maxPathList

        if eFail is None:
            eFail = [(u, v) for (u, v, d) in agGraph.edges(data=True)]

        print eFail

        edgeLabels = dict([((u, v,), d[qos])
                        for u, v, d in agGraph.edges(data=True)])


        #print "HERE", edgeLabels.update((nx.get_edge_attributes(agGraph, qos)))
        #edgeLabels.update((nx.get_edge_attributes(agGraph, qos)))

        pos = nx.spring_layout(agGraph)  # positions for all nodes
        nx.draw_networkx_nodes(agGraph, pos, node_size=700, node_color='b')
        nx.draw_networkx_nodes(agGraph, pos, nodelist=maxPath, node_size=700, node_color='r')
        nx.draw_networkx_nodes(agGraph, pos, nodelist=e2e, node_color='y', node_shape='s')

        nx.draw_networkx_edges(agGraph, pos, edgelist=maxPathList, width=6, alpha=0.6, edge_color='r')
        nx.draw_networkx_edges(agGraph, pos, edgelist=eFail, width=2, alpha=0.5)

        nx.draw_networkx_edge_labels(agGraph, pos, font_size=10, edge_labels=edgeLabels, font_family='sans-serif')
        nx.draw_networkx_labels(agGraph, pos, font_size=20, font_family='sans-serif')

        plt.axis('off')
        plt.savefig(("/home/i2cat/Documents/test.png"))  # save as png
        plt.show()  # display

    else:
        edgeLabels = dict([((u, v,), d[qos])
                        for u, v, d in agGraph.edges(data=True)])

        pos = nx.spring_layout(agGraph)  # positions for all nodes
        nx.draw_networkx_nodes(agGraph, pos, node_size=700, node_color='b')
        nx.draw_networkx_nodes(agGraph, pos, nodelist=e2e, node_color='y', node_shape='s')

        if eOK is not None:
            nx.draw_networkx_edges(agGraph, pos, edgelist=eOK, width=2, alpha=1)
        else:
            nx.draw_networkx_edges(agGraph, pos, width=2, alpha=1)
        if eFail is not None:
            nx.draw_networkx_edges(agGraph, pos, edgelist=eFail, width=2, alpha=0.5, edge_color='b', style='dashed')

        nx.draw_networkx_edge_labels(agGraph, pos, font_size=10, edge_labels=edgeLabels, font_family='sans-serif')
        nx.draw_networkx_labels(agGraph, pos, font_size=20, font_family='sans-serif')

        plt.axis('off')
        plt.savefig(("/home/i2cat/Documents/test.png"))  # save as png
        plt.show()  # display


"""
------------------------------------------------------------------------------
$$$TEST ZONE$$$
------------------------------------------------------------------------------
"""

M = nx.MultiGraph()


M.add_edge('00:00:05', '00:00:06', key='k1', srcPort='A', dstPort='B', bandwidth=4, delay=0.7, jitter=0.5, loss=30)
M.add_edge('00:00:06', '00:00:05', key='k2', srcPort='B', dstPort='A', bandwidth=4, delay=0.7, jitter=0.5, loss=30)

M.add_edge('00:00:05', '00:00:06', key='k13', srcPort='A2', dstPort='B2', bandwidth=8, delay=0.4, jitter=0.5, loss=20)
M.add_edge('00:00:06', '00:00:05', key='k14', srcPort='B2', dstPort='A2', bandwidth=8, delay=0.4, jitter=0.5, loss=20)

M.add_edge('00:00:05', '00:00:07', key='k3', srcPort='C', dstPort='D', bandwidth=30, delay=0.3, jitter=0.1, loss=10)
M.add_edge('00:00:07', '00:00:05', key='k4', srcPort='D', dstPort='C', bandwidth=30, delay=0.3, jitter=0.1, loss=10)
M.add_edge('00:00:05', '00:00:08', key='k5', srcPort='E', dstPort='F', bandwidth=11, delay=0.3, jitter=0.3, loss=20)
M.add_edge('00:00:08', '00:00:05', key='k6', srcPort='F', dstPort='E', bandwidth=11, delay=0.3, jitter=0.3, loss=20)
M.add_edge('00:00:06', '00:00:07', key='k7', srcPort='G', dstPort='H', bandwidth=11, delay=0.9, jitter=0.8, loss=40)
M.add_edge('00:00:07', '00:00:06', key='k8', srcPort='H', dstPort='G', bandwidth=11, delay=0.9, jitter=0.8, loss=40)
M.add_edge('00:00:06', '00:00:08', key='k9', srcPort='I', dstPort='J', bandwidth=30, delay=0.4, jitter=0.2, loss=20)
M.add_edge('00:00:08', '00:00:06', key='k10', srcPort='J', dstPort='I', bandwidth=30, delay=0.4, jitter=0.2, loss=20)
M.add_edge('00:00:07', '00:00:08', key='k11', srcPort='K', dstPort='L', bandwidth=30, delay=0.2, jitter=0.1, loss=5)
M.add_edge('00:00:08', '00:00:07', key='k12', srcPort='L', dstPort='K', bandwidth=30, delay=0.2, jitter=0.1, loss=5)

"""
M.add_edge('00:00:05', '00:00:06', key='5-6:1', srcPort='1', dstPort='2', bandwidth=15, delay=0.7, jitter=0.5, loss=30)
M.add_edge('00:00:06', '00:00:05', key='6-5:1', srcPort='2', dstPort='1', bandwidth=15, delay=0.7, jitter=0.5, loss=30)
M.add_edge('00:00:05', '00:00:06', key='5-6:2', srcPort='2', dstPort='1', bandwidth=11, delay=0.3, jitter=0.5, loss=30)
M.add_edge('00:00:06', '00:00:05', key='6-5:2', srcPort='1', dstPort='2', bandwidth=11, delay=0.3, jitter=0.5, loss=30)
M.add_edge('00:00:06', '00:00:07', key='6-7:1', srcPort='1', dstPort='1', bandwidth=13, delay=0.3, jitter=0.5, loss=30)
M.add_edge('00:00:07', '00:00:06', key='7-6:1', srcPort='1', dstPort='1', bandwidth=13, delay=0.3, jitter=0.5, loss=30)
"""
"""
data = json_graph.node_link_data(M)
dato = json_graph.adjacency_data(M)


for u, v, data in M.edges_iter(data=True):
    print(u, v, data)
"""

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

"""
pathlist = list(nx.all_simple_paths(M, '00:00:05', '00:00:08', 'bandwidth'))
for path in pathlist:
    test_path = multiEdgeKey(path, M)
    length = path_length(M, path, 'bandwidth')
    print "FINAL COST", test_path, ":", length
"""

"""
H = nx.MultiGraph(M)
"""
"""
agGraph = stAggregate_test(M)
"""
"""
res, cos_res = AkSP(agGraph, '00:00:05', '00:00:06', 5, 'total')
print "res", res
print "cos_res", cos_res
"""

"""
A = nx.dorogovtsev_goltsev_mendes_graph(2)

for edge in A.edges_iter(data=True):
    edge1, edge2, nfo = edge
    bnd = random.randrange(1, 100)
    dly = random.uniform(1, 10)
    jtr = random.uniform(1, 5)
    pls = random.randrange(0, 100)
    A.add_edge(edge1, edge2, bandwidth=bnd, delay=dly, jitter=jtr, loss=pls)
"""

"""
agGraph = stAggregate(M)

for edge in agGraph.edges_iter(data=True, keys=True):
    print "aggregated", edge
"""

"""
res, key_res, cos_res = AkLP(M, '00:00:05', '00:00:07', 3, 'bandwidth')
print "res", res
print "key_res", key_res
print "cos_res", cos_res

x, y, z = path_select(res, key_res, cos_res, len(res)-1)
print "Found", x, "node-path, defined by", y, "edges, with", z, "total cost value."
"""

"""
visited=[]
lonpa = longestPath(M, '00:00:05', '00:00:06', 'weight')
print "longest", lonpa
"""

"""
res, key_res, cos_res = AkSP(M, '00:00:05', '00:00:08', 3, 'bandwidth')
print "res", res
print "key_res", key_res
print "cos_res", cos_res

x, y, z = path_select(res, key_res, cos_res, 2)
print "Found", x, "node-path, defined by", y, "edges, with", z, "total cost value."
"""

"""
res, cos_res = AkLP(M, '00:00:05', '00:00:06', 1, 'bandwidth')
print "PATH", res
print "COST", cos_res
"""
"""
for u, v, key, data in M.edges_iter(data=True, keys=True):
        if data['bandwidth'] <= 11:
            print "node start", u
            print "node end", v
            print "key", key
            print "data", data

            M.remove_edge(u, v, key=key)

print M.edges(data=True)
"""


res, key_res, cos_res = ALP(M, '00:00:05', '00:00:06', 'bandwidth')
print "path", res
print "key_res", key_res
print "cost", cos_res

path_JSON = json.dumps(res)
print path_JSON


"""
command = "curl -s http://127.0.0.1:5000/pathfinder/"
result = os.popen(command).read()
print command+"\n"
print json.loads(result)
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

"""
maxPath, keyPath, length = path_select(res, key_res, cos_res, len(res))
print 'selectedPATH', maxPath
print 'selectedKeyPATH', keyPath
print 'selectedCOST', length
"""
plot_path(M, None, None, None, None, 'bandwidth')
