#!/usr/bin/env python
# encoding: utf-8

"""
This is a testing python file with examples
of the Graph and MultiDiGraph class
"""
__author__ = 'Daniel'

# Import specific libraries for testing
import os
import sys
import subprocess
import json
import io
import time
from networkx.readwrite import json_graph
import networkx as nx
import matplotlib.pyplot as plt
import argparse
import json
import httplib2
import Port_stats
from PathDrawer import to_edge_path
from fractions import Fraction
from collections import defaultdict

# parse controller address.
# Syntax:
#   *ALGORITHM* --controller {IP:REST_PORT}

parser = argparse.ArgumentParser(description='Suitable Path Generator')
parser.add_argument('--controller', dest='controllerRestIp', action='store', default='localhost:8080', help='controller IP:RESTport, e.g., localhost:8080 or A.B.C.D:8080')
args = parser.parse_args()
print args, "\n"

controllerRestIp = args.controllerRestIp

class mcolors:
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'

    def disable(self):
        self.OKGREEN = ''
        self.FAIL = ''

# first check if a local db file exists, which needs to be updated after add/delete
if os.path.exists('./qosDb.json'):
    qosDb = open('./qosDb.json', 'r')
    lines = qosDb.readlines()
    qosDb.close()
else:
    lines = {}
    print "QoS database file not found. Creating new empty database.\n"
    with open('qosDb.json', 'wb') as qosDb:
        json.dump(lines, qosDb)

print(lines)

# load qos request ID to compare with qosDb and check its availability

reqID = None
reqBand = None
reqDelay = None     # Data gathering not yet implemented
reqPacketLoss = None
reqJitter = None    # Not used, QoS parameter to consider
reqCost = None      # Not used, QoS link average state
k = 0               # Number of constraints used to calculate a path
with open('./qosDb.json') as qosDb:
    for line in qosDb:
        data = json.loads(line)
        dataID = data.get('requestID', [])
        print(data)
        with open("QoS_Request.json") as qosRequest:
            reqData = json.load(qosRequest)
            reqID = reqData['requestID']
            print "QoS Request ID: %s\n" % reqID
        if dataID == reqID:
            print mcolors.FAIL + "QoS Request ID: %s already exists. Use new ID to create.\n" % reqID
            sys.exit()

    with open("QoS_Request.json") as qosRequest:
        reqData = json.load(qosRequest)
        if reqData['bandwidth']:
            reqBand = reqData['bandwidth']
            print "Requested minimum bandwidth: %s" % reqBand
            k += 1
        if reqData['delay']:
            reqDelay = reqData['delay']
            print "Requested maximum delay: %s" % reqDelay
            k += 1
        if reqData['packet-loss']:
            reqPacketLoss = reqData['packet-loss']
            print "Requested maximum packet-loss: %s" % reqPacketLoss
            k += 1
        print "Number of constraints: %s\n" % k
        print("QoS Request data loaded.\n")


# retrieve source and destination device attachment points
    # using DeviceManager rest API
with open("QoS_Request.json") as qosRequest:
    reqData = json.load(qosRequest)
    srcAddress = reqData['ip-src']
    dstAddress = reqData['ip-dst']
    print "QoS Request SOURCE address: %s" % srcAddress
    print "QoS Request DESTINATION address: %s" % dstAddress


command = "curl -s http://%s/wm/device/?ipv4=%s" % (args.controllerRestIp, srcAddress)
result = os.popen(command).read()
parsedResult = json.loads(result)
print command+"\n"
try:
    srcSwitch = parsedResult[0]['attachmentPoint'][0]['switchDPID']
    srcPort = parsedResult[0]['attachmentPoint'][0]['port']

except:
    print mcolors.FAIL + "Error: Controller could not find SRC attachment point!"
    sys.exit()

command = "curl -s http://%s/wm/device/?ipv4=%s" % (args.controllerRestIp, dstAddress)
result = os.popen(command).read()
parsedResult = json.loads(result)
print command+"\n"
try:
    dstSwitch = parsedResult[0]['attachmentPoint'][0]['switchDPID']
    dstPort = parsedResult[0]['attachmentPoint'][0]['port']

except:
    print mcolors.FAIL + "Error: Controller could not find DST attachment point!"
    sys.exit()

print srcSwitch, "\n", srcPort, "\n", dstSwitch, "\n", dstPort

# Create empty topology multiGraph to add nodes and edges
G = nx.MultiGraph()


# Get all the nodes/switches
command = "curl -s http://%s//wm/core/controller/switches/json" % args.controllerRestIp
result = os.popen(command).read()
print command+"\n"
print result
for parsedResult in json.loads(result):
    switchID = parsedResult['dpid']
    switchName = parsedResult['ports'][0]['name']
    print switchID
    print switchName

    G.add_node(switchID, name=switchName)


# Get all the edges/links
command = "curl -s http://%s//wm/topology/links/json" % args.controllerRestIp
rtTopo = os.popen(command).read()
print command+"\n"
for parsedResult in json.loads(rtTopo):
    edgeSrcSwitch = parsedResult['src-switch']
    edgeDstSwitch = parsedResult['dst-switch']
    edgeSrcPort = parsedResult['src-port']
    edgeDstPort = parsedResult['dst-port']
    print edgeSrcSwitch, "\n"
    print edgeDstSwitch, "\n"
    print edgeSrcPort, "\n"
    print edgeDstPort, "\n"
    G.add_edge(edgeSrcSwitch, edgeDstSwitch, key=edgeSrcSwitch+edgeDstSwitch, srcPort=edgeSrcPort, dstPort=edgeDstPort)

# read topology QoS related parameters to apply QoS request constraints
# BANDWIDTH requirement

topoSrcSwitch = 0
topoDstSwitch = 0
edgeBand = 0
with open("topology.json") as topologyData:
        parsedData = json.load(topologyData)
        for i in range(len(parsedData)):
                topoSrcSwitch = parsedData[i]['src-switch']
                topoDstSwitch = parsedData[i]['dst-switch']
                edgeBand = parsedData[i]['bandwidth']
                if G.has_edge(topoSrcSwitch, topoDstSwitch):
                    G.add_edge(topoSrcSwitch, topoDstSwitch, key=topoSrcSwitch+topoDstSwitch, bandwidth=edgeBand)
                print "edge: %s - %s, bandwidth: %s, key: %s" % (topoSrcSwitch, topoDstSwitch, edgeBand, topoSrcSwitch+topoDstSwitch)

eOK = [(u, v) for (u, v, d) in G.edges(data=True) if d['bandwidth'] > reqBand]
eFail = [(u, v) for (u, v, d) in G.edges(data=True) if d['bandwidth'] <= reqBand]

# labels
hostList = [srcSwitch, dstSwitch]
edgeLabels = {}
edgeLabels.update((nx.get_edge_attributes(G, 'bandwidth')))

pos = nx.spring_layout(G)    # positions for all nodes
nx.draw_networkx_nodes(G, pos, node_size=700)
nx.draw_networkx_nodes(G, pos, nodelist=hostList, node_color='y', node_shape='s')

nx.draw_networkx_edges(G, pos, edgelist=eOK, width=6, alpha=1)
nx.draw_networkx_edges(G, pos, edgelist=eFail, width=6, alpha=0.5, edge_color='b', style='dashed')

nx.draw_networkx_edge_labels(G, pos, font_size=10, edge_labels=edgeLabels, font_family='sans-serif')
nx.draw_networkx_labels(G, pos, font_size=20, font_family='sans-serif')

plt.axis('off')
plt.savefig("/home/i2cat/Documents/test.png")   # save as png
plt.show()  # display

print G.edges(data=True)

################################################################################
# Path Pusher: send one flow mod per pair of APs in route
# SPG algorithm Step 1: search and delete those links not meeting QoS constraints
# Remove edges - Links that does not satisfy bandwidth constraints are removed from the graph

for u, v, data in G.edges_iter(data=True):
    if data['bandwidth'] <= reqBand:
        G.remove_edge(u, v)


# labels
hostList = [srcSwitch, dstSwitch]
edgeLabels = {}
edgeLabels.update((nx.get_edge_attributes(G, 'bandwidth')))

pos = nx.spring_layout(G)    # positions for all nodes
nx.draw_networkx_nodes(G, pos, node_size=700)
nx.draw_networkx_nodes(G, pos, nodelist=hostList, node_color='y', node_shape='s')

nx.draw_networkx_edges(G, pos, width=6, alpha=1)
nx.draw_networkx_edge_labels(G, pos, font_size=10, edge_labels=edgeLabels, font_family='sans-serif')
nx.draw_networkx_labels(G, pos, font_size=20, font_family='sans-serif')

plt.axis('off')
plt.savefig("/home/i2cat/Documents/test.png")   # save as png
plt.show()  # display

# SPG algorithm Step 2: search all suitable paths meeting QoS constraints
# src and dst path check - Check path connection between src and dst
isPath = nx.has_path(G, srcSwitch, dstSwitch)
if isPath:
    print "Searching best path available...\n"


else:
    print "ERROR!!! No path available\n"
    sys.exit()


if isPath and k > 1:
    print "Step 2: MCP process"

#else:
# Single constraint request; suitable bandwidth requested
   # Calculate maximum bandwidth per link,

"""
maxLength = None
M = nx.MultiGraph()
for (u, v, d) in G.edges(data=True):
           if d['bandwidth'] >= maxLength:
               maxLength = d['bandwidth']
               if (u, v) not in maxPath:
                   maxPath.append((u, v))
M.add_edges_from(maxPath)
hasPath = nx.has_path(M, srcSwitch, dstSwitch)
"""
M = nx.MultiGraph(G)
for (u, v, d) in M.edges(data=True):
   d['bandwidth'] = Fraction.from_float(1/d['bandwidth'])
# Shortest path calculation: returns a list of nodes(switches) to push a route
print M.edges(data=True)

length, maxPath = nx.bidirectional_dijkstra(M, srcSwitch, dstSwitch, weight='bandwidth')
# paths = nx.all_simple_paths(M, srcSwitch, dstSwitch)
# print (list(paths))


print "QoS path = %s\n" % maxPath
print "QoS Cost = %s\n" % length

# labels
hostList = [srcSwitch, dstSwitch]
edgeLabels = {}
edgeLabels.update((nx.get_edge_attributes(G, 'bandwidth')))

"""
# list of edges (switches) used to push flowmods
maxPathList = [(u, v) for (u, v) in G.edges() if u in maxPath and v in maxPath]
maxPathList = set(list(maxPathList))
"""
maxPathList = to_edge_path(maxPath)
print "maxPathList: %s" % maxPathList

#list of other feasible edges, but not the optimum path
#otherPathList = [(u, v) for (u, v) in G.edges() if (u, v) not in maxPathList]

"""
for (u, v) in G.edges():
    if u in maxPath and v in maxPath:
            print (u, v)
"""
pos = nx.spring_layout(G)    # positions for all nodes
nx.draw_networkx_nodes(G, pos, node_size=700)
nx.draw_networkx_nodes(G, pos, nodelist=hostList, node_color='y', node_shape='s')


nx.draw_networkx_edges(G, pos, edgelist=maxPathList, width=6, alpha=1)
#nx.draw_networkx_edges(G, pos, edgelist=otherPathList, width=6, alpha=0.5, edge_color='b', style='dashed')

nx.draw_networkx_edge_labels(G, pos, font_size=10, edge_labels=edgeLabels, font_family='sans-serif')
nx.draw_networkx_labels(G, pos, font_size=20, font_family='sans-serif')


plt.axis('off')
plt.savefig(("/home/i2cat/Documents/test.png"))  # save as png
plt.show()  # display



################################################################################
# Multi-constraint path finder; find a feasible path satisfying multiple constraints
# Additive weights: find requested constraints and add them to the graph
topoSrcSwitch = None
topoDstSwitch = None
with open("topology.json") as topologyData:
        parsedData = json.load(topologyData)
        for i in range(len(parsedData)):
                topoSrcSwitch = parsedData[i]['src-switch']
                topoDstSwitch = parsedData[i]['dst-switch']
                edgeDelay = parsedData[i]['delay']
                edgePacketLoss = parsedData[i]['packet-loss']
                if G.has_edge(topoSrcSwitch, topoDstSwitch):
                    G.add_edge(topoSrcSwitch, topoDstSwitch, key=topoSrcSwitch+topoDstSwitch, delay=edgeDelay, packetLoss=edgePacketLoss)
                print "edge: %s - %s, delay: %s, packet-loss: %s" % (topoSrcSwitch, topoDstSwitch, edgeDelay, edgePacketLoss)

print G.edges(data=True)

# First selection wave: delete links not meeting requested requirements
"""
On a first approach, every constraint will be treated as a predefined named constraint:
i.e. this step only works for delay, packet-loss if they are delivered
In future improve implementation, this should work with any kind of constraint.
"""

for u, v, data in G.edges_iter(data=True):
    if data['delay'] > reqDelay:
        G.remove_edge(u, v)

for u, v, data in G.edges_iter(data=True):
    if data['packetLoss'] > reqPacketLoss:
        G.remove_edge(u, v)

"""
for u, v, data in G.edges_iter(data=True):
    if data['cost'] <= reqCost:
        G.remove_edge(u, v)

for u, v, data in G.edges_iter(data=True):
    if data['anyConstraint'] <= reqAnyConstraint:
        G.remove_edge(u, v)
"""
# Second selection wave: calculate all feasible paths meeting requested requirements
isPath = nx.has_path(G, srcSwitch, dstSwitch)
delayPaths = None
packetLossPaths = None

print isPath
if isPath:
    print "Searching feasible paths available...\n"
    delayPaths = ([p for p in nx.all_shortest_paths(G, srcSwitch, dstSwitch, 'delay')])
    packetLossPaths = ([p for p in nx.all_shortest_paths(G, srcSwitch, dstSwitch, 'packetLoss')])

    print delayPaths
    print packetLossPaths


else:
    print mcolors.FAIL + "ERROR!!! No path available\n"
    sys.exit()

################################################################################
# Path Pusher: send one flow mod per pair of APs in route
# using StaticFlowPusher rest API

        # IMPORTANT NOTE: current Floodlight StaticflowEntryPusher
        # assumes all flow entries to have unique name across all switches
        # this will most possibly be relaxed later, but for now we
        # encode each flow entry's name with both switch dpid, qos request-id
        # and flow type ( consider flows: forward/reverse, farp/rarp)
auxPath = []    # auxiliar to store path ports

print "switches to configure: %s" % maxPath
configString = ""
checkedList = []
idx = 0
midSwitches = defaultdict(list)
for nodeSwitch in maxPath:
    if idx == (len(maxPath)-1):
        nextNodeSwitch = maxPath[idx-1]
    else:
        idx = (idx + 1)
        nextNodeSwitch = maxPath[idx]
        for parsedResult in json.loads(rtTopo):
            edgeSrcSwitch = parsedResult['src-switch']
            edgeDstSwitch = parsedResult['dst-switch']
            edgeSrcPort = parsedResult['src-port']
            edgeDstPort = parsedResult['dst-port']
            if edgeSrcSwitch == nodeSwitch and edgeDstSwitch == nextNodeSwitch:
                print edgeSrcSwitch, edgeDstSwitch
                print edgeSrcPort, edgeDstPort
                if edgeSrcSwitch == srcSwitch and edgeSrcSwitch not in checkedList:

                    # Switch Queues Configuration

                    srcSwitchName = G.node[srcSwitch]['name']
                    print srcSwitchName
                    configString += " -- set Port %s-eth%s qos=@newqos" % (srcSwitchName, srcPort)
                    configString += " -- set Port %s-eth%s qos=@newqos" % (srcSwitchName, edgeSrcPort)

                    qosNode = {'switch': srcSwitch, 'port1': srcPort, 'port2': edgeSrcPort}
                    auxPath.append(qosNode)
                    print auxPath

                    #switch is the source host connected switch
                    command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-ip\":\"%s\", \"dst-ip\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"output=%s\"}' http://%s/wm/staticflowentrypusher/json" % (srcSwitch, edgeSrcSwitch+"-"+edgeDstSwitch+".f", srcAddress, dstAddress, "0x800", srcPort, edgeSrcPort, controllerRestIp)
                    result = os.popen(command).read()
                    print command

                    command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"output=%s\"}' http://%s/wm/staticflowentrypusher/json" % (srcSwitch, edgeSrcSwitch+"-"+edgeDstSwitch+".farp", "0x806", srcPort, edgeSrcPort, controllerRestIp)
                    result = os.popen(command).read()
                    print command

                    command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-ip\":\"%s\", \"dst-ip\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"output=%s\"}' http://%s/wm/staticflowentrypusher/json" % (srcSwitch, edgeSrcSwitch+"-"+edgeDstSwitch+".r", dstAddress, srcAddress, "0x800", edgeSrcPort, srcPort, controllerRestIp)
                    result = os.popen(command).read()
                    print command

                    command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"output=%s\"}' http://%s/wm/staticflowentrypusher/json" % (srcSwitch, edgeSrcSwitch+"-"+edgeDstSwitch+".rarp", "0x806", edgeSrcPort, srcPort, controllerRestIp)
                    result = os.popen(command).read()
                    print command
                    if edgeDstSwitch != dstSwitch:
                        midSwitches[edgeDstSwitch].append(edgeDstPort)


                elif edgeSrcSwitch == dstSwitch and edgeSrcSwitch not in checkedList:
                    # Switch Queues Configuration
                    dstSwitchName = G.node[dstSwitch]['name']
                    print dstSwitchName
                    configString += " -- set Port %s-eth%s qos=@newqos" % (dstSwitchName, dstPort)
                    configString += " -- set Port %s-eth%s qos=@newqos" % (dstSwitchName, edgeSrcPort)

                    qosNode = {'switch': dstSwitch, 'port1': dstPort, 'port2': edgeSrcPort}
                    auxPath.append(qosNode)
                    print auxPath

                                #switch is the destination host connected switch
                    command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-ip\":\"%s\", \"dst-ip\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"output=%s\"}' http://%s/wm/staticflowentrypusher/json" % (dstSwitch, edgeSrcSwitch+"-"+edgeDstSwitch+".f", srcAddress, dstAddress, "0x800", edgeSrcPort, dstPort, controllerRestIp)
                    result = os.popen(command).read()
                    print command

                    command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"output=%s\"}' http://%s/wm/staticflowentrypusher/json" % (dstSwitch, edgeSrcSwitch+"-"+edgeDstSwitch+".farp", "0x806", edgeSrcPort, dstPort, controllerRestIp)
                    result = os.popen(command).read()
                    print command

                    command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-ip\":\"%s\", \"dst-ip\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"output=%s\"}' http://%s/wm/staticflowentrypusher/json" % (dstSwitch, edgeDstSwitch+"-"+edgeSrcSwitch+".r", dstAddress, srcAddress, "0x800", dstPort, edgeSrcPort, controllerRestIp)
                    result = os.popen(command).read()
                    print command

                    command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"output=%s\"}' http://%s/wm/staticflowentrypusher/json" % (dstSwitch, edgeDstSwitch+"-"+edgeSrcSwitch+".rarp", "0x806", dstPort, edgeSrcPort, controllerRestIp)
                    result = os.popen(command).read()
                    print command
                    if edgeDstSwitch != srcSwitch:
                        midSwitches[edgeDstSwitch].append(edgeDstPort)


                elif edgeDstSwitch == dstSwitch and edgeDstSwitch not in checkedList:
                    # Switch Queues Configuration
                    dstSwitchName = G.node[dstSwitch]['name']
                    print dstSwitchName
                    configString += " -- set Port %s-eth%s qos=@newqos" % (dstSwitchName, dstPort)
                    configString += " -- set Port %s-eth%s qos=@newqos" % (dstSwitchName, edgeSrcPort)

                    qosNode = {'switch': dstSwitch, 'port1': dstPort, 'port2': edgeSrcPort}
                    auxPath.append(qosNode)
                    print auxPath

                                #switch is the destination host connected switch
                    command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-ip\":\"%s\", \"dst-ip\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"output=%s\"}' http://%s/wm/staticflowentrypusher/json" % (dstSwitch, edgeDstSwitch+"-"+dstSwitchName+".f", srcAddress, dstAddress, "0x800", edgeDstPort, dstPort, controllerRestIp)
                    result = os.popen(command).read()
                    print command

                    command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"output=%s\"}' http://%s/wm/staticflowentrypusher/json" % (dstSwitch, edgeDstSwitch+"-"+dstSwitchName+".farp", "0x806", edgeDstPort, dstPort, controllerRestIp)
                    result = os.popen(command).read()
                    print command

                    command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-ip\":\"%s\", \"dst-ip\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"output=%s\"}' http://%s/wm/staticflowentrypusher/json" % (dstSwitch, edgeDstSwitch+"-"+dstSwitchName+".r", dstAddress, srcAddress, "0x800", dstPort, edgeDstPort, controllerRestIp)
                    result = os.popen(command).read()
                    print command

                    command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"output=%s\"}' http://%s/wm/staticflowentrypusher/json" % (dstSwitch, edgeDstSwitch+"-"+dstSwitchName+".rarp", "0x806", dstPort, edgeDstPort, controllerRestIp)
                    result = os.popen(command).read()
                    print command
                    if edgeSrcSwitch != srcSwitch:
                        midSwitches[edgeSrcSwitch].append(edgeSrcPort)


                else:
                    #switch is between other switches; create a dict with switch - ports (midSwitch : port-pair)
                    #maxPath contains route order, then midSwitches are stored in path order
                    midSwitches[edgeSrcSwitch].append(edgeSrcPort)
                    midSwitches[edgeDstSwitch].append(edgeDstPort)

print midSwitches
for midSwitch, midPorts in midSwitches.iteritems():
    if midSwitch not in checkedList:

        print "%s - %s, %s" % (str(midSwitch), str(midPorts[0]), str(midPorts[1]))
        # Switch Queues Configuration
        midSwitchName = G.node[midSwitch]['name']
        print midSwitchName
        configString += " -- set Port %s-eth%s qos=@newqos" % (midSwitchName, str(midPorts[0]))
        configString += " -- set Port %s-eth%s qos=@newqos" % (midSwitchName, str(midPorts[1]))

        qosNode = {'switch': midSwitch, 'port1': str(midPorts[0]), 'port2': str(midPorts[1])}
        auxPath.append(qosNode)
        print auxPath

        #push midSwitches flowmods
        command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-ip\":\"%s\", \"dst-ip\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"output=%s\"}' http://%s/wm/staticflowentrypusher/json" % ((str(midSwitch)), (str(midSwitch))+"-"+(str(midPorts[0]))+".f", srcAddress, dstAddress, "0x800", (str(midPorts[0])), (str(midPorts[1])), controllerRestIp)
        result = os.popen(command).read()
        print command

        command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"output=%s\"}' http://%s/wm/staticflowentrypusher/json" % ((str(midSwitch)), (str(midSwitch))+"-"+(str(midPorts[0]))+".farp", "0x806", (str(midPorts[0])), (str(midPorts[1])), controllerRestIp)
        result = os.popen(command).read()
        print command


        command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-ip\":\"%s\", \"dst-ip\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"output=%s\"}' http://%s/wm/staticflowentrypusher/json" % ((str(midSwitch)), (str(midSwitch))+"-"+(str(midPorts[1]))+".r", dstAddress, srcAddress, "0x800", (str(midPorts[1])), (str(midPorts[0])), controllerRestIp)
        result = os.popen(command).read()
        print command

        command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"output=%s\"}' http://%s/wm/staticflowentrypusher/json" % ((str(midSwitch)), (str(midSwitch))+"-"+(str(midPorts[1]))+".rarp", "0x806", (str(midPorts[1])), (str(midPorts[0])), controllerRestIp)
        result = os.popen(command).read()
        print command

"""
print configString
queueString = "sudo ovs-vsctl%s -- --id=@newqos create QoS type=linux-htb queues=0=@q0 -- --id=@q0 create Queue other-config:min-rate=10000000 other-config:max-rate=10000000" % configString
qResult = os.popen(queueString).read()
print queueString
print qResult
"""

"""
command = "curl -s http://%s/wm/topology/route/%s/%s/%s/%s/json" % (controllerRestIp, srcSwitch, srcPort, dstSwitch, dstPort)
result = os.popen(command).read()
parsedResult = json.loads(result)

print command+"\n"
print result+"\n"
"""

# Switch sort to provide QoS path from source to destination
def path_sort(path, aux):
    sortedPath = []
    for i in range(len(path)):
        print "i", path[i]
        for j in range(len(aux)):

            print aux[j]['switch']
            if path[i] == aux[j]['switch']:

                sortedPath.append(aux[j])

            else:
                continue
    return sortedPath

qosPath = path_sort(maxPath, auxPath)
print "QOS PATH:", qosPath





################################################################################
# store created circuit attributes in local ./qosDb.json
qosDb = open('./qosDb.json', 'a')
datetime = time.asctime()
circuitParams = {'requestID': reqID, 'ip-src': srcAddress, 'ip-dst': dstAddress, 'bandwidth': reqBand, 'datetime': datetime}
str = json.dumps(circuitParams)
qosDb.write(str+"\n")


"""
command="curl -s http://%s/wm/core/switch/all/flow/json| python -mjson.tool" % (controllerRestIp)
result = os.popen(command).read()
print command + "\n" + result
"""
"""
command = "curl -s http://%s/wm/staticflowentrypusher/clear/all/json" % (controllerRestIp)
result = os.popen(command).read()
print command + "\n" + result
"""


