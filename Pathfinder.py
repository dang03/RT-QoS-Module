#!/usr/bin/env python
# encoding: utf-8

"""
Pathfinder: main application implementing QoS Algorithm adapted from Suitable Path Process (SPG)
Requirements:
...

"""
__author__ = 'Daniel'

# Import libraries
import os
import io
import subprocess
import argparse

import networkx as nx
import matplotlib.pyplot as plt
import numpy
from networkx.readwrite import json_graph
import json
import datetime
import time
import sys
from PathDrawer import to_edge_path
from fractions import Fraction
from collections import defaultdict
from MCP import *


# main vars
delta_sec = 2        # seconds to delay in time.sleep
check_freq = 10     # seconds to check requests
k_sel = 3            # selected k path


# def startTime
startTime = time.time()
print "SPG Start Time: ", datetime.datetime.now()

# parse controller address.
# Syntax:
#   *ALGORITHM* --controller {IP:REST_PORT}
"""
parser = argparse.ArgumentParser(description='Suitable Path Generator')
parser.add_argument('--controller', dest='controllerRestIp', action='store', default='localhost:8080', help='controller IP:RESTport, e.g., localhost:8080 or A.B.C.D:8080')
args = parser.parse_args()
print args, "\n"

controllerRestIp = args.controllerRestIp
"""

class mcolors:
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.OKGREEN = ''
        self.FAIL = ''
        self.ENDC = ''

# first check if a local db file exists, which needs to be updated after add/delete
# disabled qosDb checks
"""
if os.path.exists('./qosDb.json'):
    qosDb = open('./qosDb.json', 'r')
    lines = qosDb.readlines()
    qosDb.close()
else:
    lines = {}
    print "QoS database file not found. Creating new empty database.\n"
    with open('qosDb.json', 'wb') as qosDb:
        json.dump(lines, qosDb)
"""

#
# enabled new request interface (based on requestLoader.py) to load required data from request

with open("PFinput.json", 'r') as PFinput:
    reqData = json.load(PFinput)
    #print reqData
    reqID = reqData['requestID']
    srcAddress = reqData['src']     # retrieve source and destination device points
    dstAddress = reqData['dst']
    reqAlarm = reqData['alarm']     # Check if request is a re-route / duplicated request
    reqParameters = reqData['parameters']

    rtTopo = reqData['topology']

k = []      # Stacks number of constraints used to calculate a path


# The following code section can be used to enable request ID uniqueness, allowing
# the duplicity check for served requests or active QoS paths. A file cache or database
# is needed to check for stored requests ID.
"""
with open('./qosDb.json') as qosDb:
    print "QoS-Request ID: %s\n" % reqID
    for line in qosDb:
        data = json.loads(line)
        dataID = data.get('requestID', [])
        #print(data)

        if dataID == reqID:
            if reqAlarm == 0:
                print mcolors.FAIL + "QoS Request ID: %s already exists. A new ID is required to initialize.\n" % reqID
                duration = time.time()-startTime
                print "SPG End Time: ", duration, " seconds"
                sys.exit()
    if reqAlarm != 0:
        print mcolors.OKGREEN + "QoS Request Alarm: %s re-route requested\n" % reqID, mcolors.ENDC
"""

print "QoS Request SOURCE address: %s" % srcAddress
print "QoS Request DESTINATION address: %s" % dstAddress

print mcolors.OKGREEN + "QoS-Request core data loaded succesfully\n", mcolors.ENDC


# QoS-Request requested parameters parsing: Bandwidth, delay, jitter and packet-loss supported
# A not-requested parameter must be declared as a 0 value on the requested parameters section
# or may be excluded from the request.
# k is an array needed to count requested parameters for the MCP computation

if 'bandwidth' in reqParameters:
    reqBand = reqData['parameters']['bandwidth']
    if reqBand is not 0:
        print "Requested minimum bandwidth: %s" % reqBand
        k.append('bandwidth')

if 'delay' in reqParameters:
    reqDelay = reqData['parameters']['delay']
    if reqDelay is not 0:
        print "Requested maximum delay: %s" % reqDelay
        k.append('delay')

if 'jitter' in reqParameters:
    reqJitter = reqData['parameters']['jitter']
    if reqJitter is not 0:
        print "Requested maximum jitter: %s" % reqJitter
        k.append('jitter')

if 'packet-loss' in reqParameters:
    reqPacketLoss = reqData['parameters']['packet-loss']
    if reqPacketLoss is not 0:
        print "Requested maximum packet-loss: %s" % reqPacketLoss, "%"
        k.append('packet-loss')


print "Number of constraints: %s\n" % len(k)
print mcolors.OKGREEN + "QoS-Request requested parameters loaded\n", mcolors.ENDC


# Parse and load end-to-end attachment points of source - destination
# For each end point, switch DPID/switch ID and port number/port ID is required.
# If switch DPID/port number is provided, then every other switch in ['topology'] must provide
# its DPID/port numbers (or switchID/port IDs for switchID/port ID case)
try:
    srcSwitch = srcAddress['srcSwitch']
    srcPort = srcAddress['srcPort']

except:
    print mcolors.FAIL + "Error: SRC attachment point could not be loaded!"
    duration = time.time()-startTime
    print "SPG End Time: ", duration, " seconds"
    sys.exit()


try:
    dstSwitch = dstAddress['dstSwitch']
    dstPort = dstAddress['dstPort']

except:
    print mcolors.FAIL + "Error: DST attachment point could not be loaded!"
    duration = time.time()-startTime
    print "SPG End Time: ", duration, " seconds"
    sys.exit()


print "SRC switch: ", srcSwitch, "\n", "SRC port: ", srcPort, "\n", "DST switch: ", dstSwitch, "\n", "DST port: ", dstPort

# Create empty topology multiGraph to add nodes and edges
G = nx.MultiGraph()


# graph builder
for i in range(len(rtTopo)):
    edgeSrcSwitch = rtTopo[i]['src-switch']
    edgeDstSwitch = rtTopo[i]['dst-switch']
    edgeSrcPort = rtTopo[i]['src-port']
    edgeDstPort = rtTopo[i]['dst-port']
    key = str(edgeSrcSwitch)+"-"+str(edgeDstSwitch)
    edgeBand = rtTopo[i]['bandwidth']
    edgeDelay = rtTopo[i]['delay']
    edgeJitter = rtTopo[i]['jitter']
    edgePLoss = rtTopo[i]['packet-loss']
    print edgeSrcSwitch, "\n"
    print edgeDstSwitch, "\n"
    print edgeSrcPort, "\n"
    print edgeDstPort, "\n"
    print key

    G.add_edge(edgeSrcSwitch, edgeDstSwitch, key=str(key), srcPort=edgeSrcPort, dstPort=edgeDstPort, bandwidth=edgeBand, delay=edgeDelay, jitter=edgeJitter, packetLoss=edgePLoss)

print list(G.nodes(data=True))
print G.edges(None, data=True, keys=True)

e2e = []
e2e.append(srcSwitch)
e2e.append(dstSwitch)

plot_path(G, None, e2e, None, None, None)


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


print("Topology data loaded")

#######################################################################
# Read topology QoS related parameters to apply QoS request constraints:
# For BANDWIDTH required constraint (Bottleneck QoS parameter - Critical)
print "STEP-1 Process"

#print mcolors.OKGREEN+"Checking link availability... [Bandwidth constraint]\n"+mcolors.ENDC

if 'bandwidth' in k:
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
    hostList = [srcSwitch, dstSwitch]

    plot_path(G, None, hostList, eOK, eFail, 'bandwidth')


################################################################################
# SPG algorithm Step 1: search and delete those links not meeting QoS constraints

# Remove edges - Bottleneck QoS parameters. Links that does not satisfy bandwidth
# constraints are removed from the graph. Minimum bandwidth rule: available_bandwidth
# value must be GREATER than requested value to avoid removing


    for u, v, data in G.edges_iter(data=True):
        if data['bandwidth'] <= reqBand:
            G.remove_edge(u, v)

hostList = [srcSwitch, dstSwitch]
plot_path(G, None, hostList, None, None, 'bandwidth')


################################################################################
# Connectivity check between source to destination nodes
isPath = nx.has_path(G, srcSwitch, dstSwitch)

if isPath:
    print mcolors.OKGREEN+"Feasible path available... [Bandwidth constraint]\n"+mcolors.ENDC


else:
    print mcolors.FAIL+"Failure: No path available\n"+mcolors.ENDC
    sys.exit()


# Remove edges - additive QoS parameters: If provided and requested, links that does
# not satisfy other constraints of additive class are removed from the graph.
# Removing rule: Additive QoS parameters value must be LESS than requested value to
# avoid removing

# Load Additive QoS from topology to graph weights: find requested constraints and add the statistics data to the graph
# For DELAY, JITTER, PACKET-LOSS required constraint (Additive QoS parameter)
# Other parameters GENERIC GRAPH COST (disabled)

if 'delay'or 'jitter' or 'packet-loss' in k:
    topoSrcSwitch = None
    topoDstSwitch = None
    with open("topology.json") as topologyData:
            parsedData = json.load(topologyData)
            for i in range(len(parsedData)):
                    topoSrcSwitch = parsedData[i]['src-switch']
                    topoDstSwitch = parsedData[i]['dst-switch']

                    try:
                        edgeDelay = parsedData[i]['delay']
                    except:
                        pass

                    try:
                        edgeJitter = parsedData[i]['jitter']
                    except:
                        pass

                    try:
                        edgePacketLoss = parsedData[i]['packet-loss']
                    except:
                        pass

                    if G.has_edge(topoSrcSwitch, topoDstSwitch):
                        try:
                            G.add_edge(topoSrcSwitch, topoDstSwitch, key=topoSrcSwitch+topoDstSwitch, delay=edgeDelay)
                        except:
                            pass

                        try:
                            G.add_edge(topoSrcSwitch, topoDstSwitch, key=topoSrcSwitch+topoDstSwitch, jitter=edgeJitter)
                        except:
                            pass

                        try:
                            G.add_edge(topoSrcSwitch, topoDstSwitch, key=topoSrcSwitch+topoDstSwitch, packetLoss=edgePacketLoss)
                        except:
                            pass

"""
                #print "edge: %s - %s, delay: %s, packet-loss: %s" % (topoSrcSwitch, topoDstSwitch, edgeDelay, edgePacketLoss)
                print "edge: %s - %s" % (topoSrcSwitch, topoDstSwitch), G.get_edge_data(topoSrcSwitch, topoDstSwitch, key=topoSrcSwitch+topoDstSwitch)
"""

for link in G.edges(data=True):
    print "LINK", link

# First selection wave: delete links not meeting requested requirements
"""
On a first approach, every constraint will be treated as a predefined named constraint:
i.e. this step only works for: delay, jitter, packet-loss constraints, if they are delivered
Further implementation may work with any kind of constraint (Additive-class).
"""
#TODO: Handle exceptions for not found dict keys

if 'delay' in k:
    for u, v, data in G.edges_iter(data=True):
        if data['delay'] > reqDelay:
            G.remove_edge(u, v)

if 'jitter' in k:
    for u, v, data in G.edges_iter(data=True):
        if data['delay'] > reqJitter:
            G.remove_edge(u, v)

if 'packet-loss' in k:
    for u, v, data in G.edges_iter(data=True):
        #print data
        if data['packetLoss'] > reqPacketLoss:
            G.remove_edge(u, v)

"""
for u, v, data in G.edges_iter(data=True):
    if data['cost'] <= reqCost:
        G.remove_edge(u, v)
"""

"""
for constraint in k:
    for u, v, data in G.edges_iter(data=True):
    if data[constraint] <= reqCost:
        G.remove_edge(u, v)
"""

plot_path(G, None, hostList, None, None, 'bandwidth')



################################################################################
# SPG algorithm Step 2: search all suitable paths meeting QoS constraints
# src and dst path check - Check path connection between src and dst

################################################################################
# Connectivity check between source to destination nodes
isPath = nx.has_path(G, srcSwitch, dstSwitch)

global maxPath  # will store result of QoS path
global length   # and total cost-length value of QoS path

# If isPath returns True, there's src-dst connection on topology graph
# Calculate all feasible paths meeting requested requirements, then select the optimal path
if isPath:
    print "STEP-2 Process"
    print mcolors.OKGREEN+"Searching feasible paths available...\n"+mcolors.ENDC

    """
    CODE PART for Path computation algorithms: here can be applied various algorithms from
    MCP.py file, such AkLP algorithm for k-longest-paths or ALP for longest path computation
    """


    if len(k) == 1:
        # Creates copy of the graph
        M = nx.MultiGraph(G)
        # Single constraint request; list(k) can contain any requested QoS parameter
        # Calculate path total bandwidth per minimum hop count, selects kth path
        if 'bandwidth' in k:
            #AkLP
            kPaths, kCosts = AkLP(M, srcSwitch, dstSwitch, k_sel, 'bandwidth')
            print "PATH", kPaths
            print "COST", kCosts

            #ALP
            """
            maxPath, length = ALP(M, srcSwitch, dstSwitch, 'bandwidth')
            print "path", maxPath
            print "cost", length
            """

            maxPath, length = path_select(kPaths, kCosts, len(kPaths))


        # Calculate minimum delay k paths
        if 'delay' in k:
            #AkSP
            kPaths, kCosts = AkSP(M, srcSwitch, dstSwitch, k_sel, 'delay')
            print "PATH", kPaths
            print "COST", kCosts

            maxPath, length = path_select(kPaths, kCosts, 1)

        # Calculate minimum jitter k paths,
        if 'jitter' in k:
            #AkSP
            kPaths, kCosts = AkSP(M, srcSwitch, dstSwitch, k_sel, 'jitter')
            print "PATH", kPaths
            print "COST", kCosts

            maxPath, length = path_select(kPaths, kCosts, 1)

        # Calculate minimum packet-loss k paths
        if 'packet-loss' in k:
            #AkSP
            kPaths, kCosts = AkSP(M, srcSwitch, dstSwitch, k_sel, 'packetLoss')
            print "PATH", kPaths
            print "COST", kCosts

            maxPath, length = path_select(kPaths, kCosts, 1)

        plot_path(M, maxPath, hostList, None, None, 'bandwidth')

        print "QoS path = %s\n" % maxPath
        print "QoS length = %s\n" % length

    else:
        #Means that len(k) is greater than 1
        #So stAggregator must be applied to deal with the MCP
        print mcolors.OKGREEN+"MCP: Searching feasible paths available... Multiple Constraints Path\n"+mcolors.ENDC

        M = stAggregate(G)
        for edge in M.edges_iter(data=True):
            print "Aggregated Cost", edge

        plot_path(M, None, hostList, None, None, 'total')


        """
        pos = nx.spring_layout(G)    # positions for all nodes
        nx.draw_networkx_nodes(G, pos, node_size=700, node_color='b')
        nx.draw_networkx_nodes(G, pos, nodelist=hostList, node_color='y', node_shape='s')

        nx.draw_networkx_edges(G, pos, width=2, alpha=1)
        nx.draw_networkx_edge_labels(G, pos, font_size=10, edge_labels=edgeLabels, font_family='sans-serif')
        nx.draw_networkx_labels(G, pos, font_size=20, font_family='sans-serif')

        plt.axis('off')
        plt.savefig("/home/i2cat/Documents/test.png")   # save as png
        plt.show()  # display
        """

        kPaths, kCosts = AkSP(M, srcSwitch, dstSwitch, k_sel, 'total')

        print "QoS k paths = %s\n" % kPaths
        print "QoS k lengths = %s\n" % kCosts

        maxPath, length = path_select(kPaths, kCosts, 1)

        plot_path(M, maxPath, hostList, None, None, 'total')

        print "QoS path = %s\n" % maxPath
        print "QoS length = %s\n" % length


else:
    print mcolors.FAIL + "Failure: No path available\n"+mcolors.ENDC
    sys.exit()



# First version of yen's k-shortest path applied for a generic edge weight(disabled)
"""
res, cos_res = yen_networkx(M, '00:00:01', '00:00:06', 4, 'weight')
print "res", res
print "cos_res", cos_res

path = list(nx.all_simple_paths(M, '00:00:01', '00:00:06', 'weight'))
print path

ultimate_cost, ultimate_path = maxLength_path(M, res, 'weight')
print "path", ultimate_path
print "cost", ultimate_cost
"""

# Earlier bandwidth computation trick for SPG for bidirectional dijkstra application (disabled)
"""
M = nx.MultiGraph(G)
for (u, v, d) in M.edges(data=True):
    d['bandwidth'] = Fraction.from_float(1/d['bandwidth'])

# Shortest path calculation: returns a list of nodes(switches) to push a route
print M.edges(data=True)
length, maxPath = nx.bidirectional_dijkstra(M, srcSwitch, dstSwitch, weight='bandwidth')
print "QoS path = %s\n" % maxPath
"""


#################################################################################
#################################################################################
# Pathfinder - Path Application
# Path Pusher: send one flow mod per pair of Access Point in path
# using StaticFlowPusher REST API

        # IMPORTANT NOTE: current Floodlight StaticflowEntryPusher
        # assumes all flow entries to have unique name across all switches
        # (this will most possibly be relaxed later), but for now we
        # encode each flow entry's name with both switch dpid, qos request-id
        # and flow type ( consider flows: forward/reverse, farp/rarp)
#TODO: disable flow pusher - return output (QoS path switch-port), and disable queue... DONE
#dynamic configuration

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
                if edgeSrcSwitch == srcSwitch:

                    # Switch Queues Configuration
                    """
                    srcSwitchName = G.node[srcSwitch]['name']
                    print srcSwitchName

                    configString += " -- set Port %s-eth%s qos=@newqos" % (srcSwitchName, srcPort)
                    configString += " -- set Port %s-eth%s qos=@newqos" % (srcSwitchName, edgeSrcPort)
                    """
                    qosNode = {'switch': srcSwitch, 'port1': srcPort, 'port2': edgeSrcPort}
                    auxPath.append(qosNode)
                    print auxPath

                    #switch is the source host connected switch
                    """
                    command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-ip\":\"%s\", \"dst-ip\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"enqueue=%s:1\"}' http://%s/wm/staticflowentrypusher/json" % (srcSwitch, edgeSrcSwitch+"-"+edgeDstSwitch+".f", srcAddress, dstAddress, "0x800", srcPort, edgeSrcPort, controllerRestIp)
                    result = os.popen(command).read()
                    print command

                    command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"output=%s\"}' http://%s/wm/staticflowentrypusher/json" % (srcSwitch, edgeSrcSwitch+"-"+edgeDstSwitch+".farp", "0x806", srcPort, edgeSrcPort, controllerRestIp)
                    result = os.popen(command).read()
                    print command

                    command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-ip\":\"%s\", \"dst-ip\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"enqueue=%s:1\"}' http://%s/wm/staticflowentrypusher/json" % (srcSwitch, edgeSrcSwitch+"-"+edgeDstSwitch+".r", dstAddress, srcAddress, "0x800", edgeSrcPort, srcPort, controllerRestIp)
                    result = os.popen(command).read()
                    print command

                    command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"output=%s\"}' http://%s/wm/staticflowentrypusher/json" % (srcSwitch, edgeSrcSwitch+"-"+edgeDstSwitch+".rarp", "0x806", edgeSrcPort, srcPort, controllerRestIp)
                    result = os.popen(command).read()
                    print command
                    """
                    if edgeDstSwitch != dstSwitch:
                        midSwitches[edgeDstSwitch].append(edgeDstPort)

                elif edgeSrcSwitch == dstSwitch and edgeSrcSwitch not in checkedList:

                    # Switch Queues Configuration
                    """
                    dstSwitchName = G.node[dstSwitch]['name']
                    print dstSwitchName
                    configString += " -- set Port %s-eth%s qos=@newqos" % (dstSwitchName, dstPort)
                    configString += " -- set Port %s-eth%s qos=@newqos" % (dstSwitchName, edgeSrcPort)
                    """

                    qosNode = {'switch': dstSwitch, 'port1': dstPort, 'port2': edgeSrcPort}
                    auxPath.append(qosNode)
                    print auxPath

                    #switch is the destination host connected switch
                    """
                    command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-ip\":\"%s\", \"dst-ip\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"enqueue=%s:1\"}' http://%s/wm/staticflowentrypusher/json" % (dstSwitch, edgeSrcSwitch+"-"+edgeDstSwitch+".f", srcAddress, dstAddress, "0x800", edgeSrcPort, dstPort, controllerRestIp)
                    result = os.popen(command).read()
                    print command

                    command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"output=%s\"}' http://%s/wm/staticflowentrypusher/json" % (dstSwitch, edgeSrcSwitch+"-"+edgeDstSwitch+".farp", "0x806", edgeSrcPort, dstPort, controllerRestIp)
                    result = os.popen(command).read()
                    print command

                    command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-ip\":\"%s\", \"dst-ip\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"enqueue=%s:1\"}' http://%s/wm/staticflowentrypusher/json" % (dstSwitch, edgeDstSwitch+"-"+edgeSrcSwitch+".r", dstAddress, srcAddress, "0x800", dstPort, edgeSrcPort, controllerRestIp)
                    result = os.popen(command).read()
                    print command

                    command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"output=%s\"}' http://%s/wm/staticflowentrypusher/json" % (dstSwitch, edgeDstSwitch+"-"+edgeSrcSwitch+".rarp", "0x806", dstPort, edgeSrcPort, controllerRestIp)
                    result = os.popen(command).read()
                    print command
                    """
                    if edgeDstSwitch != srcSwitch:
                        midSwitches[edgeDstSwitch].append(edgeDstPort)


                elif edgeDstSwitch == dstSwitch and edgeDstSwitch not in checkedList:

                    # Switch Queues Configuration
                    """
                    dstSwitchName = G.node[dstSwitch]['name']
                    print dstSwitchName
                    configString += " -- set Port %s-eth%s qos=@newqos" % (dstSwitchName, dstPort)
                    configString += " -- set Port %s-eth%s qos=@newqos" % (dstSwitchName, edgeSrcPort)
                    """

                    qosNode = {'switch': dstSwitch, 'port1': dstPort, 'port2': edgeSrcPort}
                    auxPath.append(qosNode)
                    print auxPath

                    #switch is the destination host connected switch
                    """
                    command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-ip\":\"%s\", \"dst-ip\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"enqueue=%s:1\"}' http://%s/wm/staticflowentrypusher/json" % (dstSwitch, edgeDstSwitch+"-"+dstSwitchName+".f", srcAddress, dstAddress, "0x800", edgeDstPort, dstPort, controllerRestIp)
                    result = os.popen(command).read()
                    print command

                    command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"output=%s\"}' http://%s/wm/staticflowentrypusher/json" % (dstSwitch, edgeDstSwitch+"-"+dstSwitchName+".farp", "0x806", edgeDstPort, dstPort, controllerRestIp)
                    result = os.popen(command).read()
                    print command

                    command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-ip\":\"%s\", \"dst-ip\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"enqueue=%s:1\"}' http://%s/wm/staticflowentrypusher/json" % (dstSwitch, edgeDstSwitch+"-"+dstSwitchName+".r", dstAddress, srcAddress, "0x800", dstPort, edgeDstPort, controllerRestIp)
                    result = os.popen(command).read()
                    print command

                    command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"output=%s\"}' http://%s/wm/staticflowentrypusher/json" % (dstSwitch, edgeDstSwitch+"-"+dstSwitchName+".rarp", "0x806", dstPort, edgeDstPort, controllerRestIp)
                    result = os.popen(command).read()
                    print command
                    """
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
        """
        midSwitchName = G.node[midSwitch]['name']
        print midSwitchName
        configString += " -- set Port %s-eth%s qos=@newqos" % (midSwitchName, str(midPorts[0]))
        configString += " -- set Port %s-eth%s qos=@newqos" % (midSwitchName, str(midPorts[1]))
        """

        qosNode = {'switch': midSwitch, 'port1': str(midPorts[0]), 'port2': str(midPorts[1])}
        auxPath.append(qosNode)
        print auxPath

        #push midSwitches flowmods
        """
        command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-ip\":\"%s\", \"dst-ip\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"enqueue=%s:1\"}' http://%s/wm/staticflowentrypusher/json" % ((str(midSwitch)), (str(midSwitch))+"-"+(str(midPorts[0]))+".f", srcAddress, dstAddress, "0x800", (str(midPorts[0])), (str(midPorts[1])), controllerRestIp)
        result = os.popen(command).read()
        print command

        command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"output=%s\"}' http://%s/wm/staticflowentrypusher/json" % ((str(midSwitch)), (str(midSwitch))+"-"+(str(midPorts[0]))+".farp", "0x806", (str(midPorts[0])), (str(midPorts[1])), controllerRestIp)
        result = os.popen(command).read()
        print command

        command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-ip\":\"%s\", \"dst-ip\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"enqueue=%s:1\"}' http://%s/wm/staticflowentrypusher/json" % ((str(midSwitch)), (str(midSwitch))+"-"+(str(midPorts[1]))+".r", dstAddress, srcAddress, "0x800", (str(midPorts[1])), (str(midPorts[0])), controllerRestIp)
        result = os.popen(command).read()
        print command

        command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"output=%s\"}' http://%s/wm/staticflowentrypusher/json" % ((str(midSwitch)), (str(midSwitch))+"-"+(str(midPorts[1]))+".rarp", "0x806", (str(midPorts[1])), (str(midPorts[0])), controllerRestIp)
        result = os.popen(command).read()
        print command
        """
"""
queueDb = open('./queueDb.txt', 'a')
print "config string:", configString
queueString = "sudo ovs-vsctl%s -- --id=@newqos create QoS type=linux-htb other-config:max-rate=30000000 queues=0=@q0,1=@q1 -- --id=@q0 create Queue other-config:max-rate=30000000 other-config:priority=1 -- --id=@q1 create Queue other-config:min-rate=20000000 other-config:priority=8" % configString
qResult = os.popen(queueString).read()
print "queue string:", queueString
print "qResult:", qResult
queueDb.write(qResult+"\n")
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
print "\n" + mcolors.OKGREEN + "QOS PATH: %s\n" % qosPath, mcolors.ENDC


if os.path.exists('./path.json'):
    pathRes = open('./path.json', 'r')
    lines = pathRes.readlines()
    pathRes.close()
else:
    lines = {}

qosPath.append({"requestID": reqID})
pathRes = open('./path.json', 'w')
to_serial = qosPath
serial = json.dumps(to_serial)
#serial = json.dumps(to_serial, indent=2, separators=(',', ': '))
pathRes.write(serial+"\n")


################################################################################
# store created circuit attributes in local ./qosDb.json
datetime = time.asctime()
qosDb = open('./qosDb.json', 'a')
circuitParams = {'requestID': reqID, 'ip-src': srcAddress, 'ip-dst': dstAddress, 'bandwidth': reqBand, 'datetime': datetime}
str = json.dumps(circuitParams)
qosDb.write(str+"\n")
duration = time.time()-startTime
print("SPG End Time ", duration, " seconds")
