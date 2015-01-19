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
#import io
#import subprocess
#import argparse
import networkx as nx
#import matplotlib.pyplot as plt
#import numpy
#from networkx.readwrite import json_graph
import json
import datetime
import time
import sys
#from fractions import Fraction
from PathDrawer import to_edge_path
#from pathfinder.PathDrawer import to_edge_path
from MCP import *
#from pathfinder.MCP import *
from collections import defaultdict



# main vars
#delta_sec = 2        # seconds to delay in time.sleep
#check_freq = 10     # seconds to check requests


# Switch sort to provide QoS path from source to destination
def path_sort(path, aux):
    sortedPath = []
    for i in range(len(path)):
        #print "i", path[i]
        for j in range(len(aux)):

            #print aux[j]['switch']
            if path[i] == aux[j]['switch']:

                sortedPath.append(aux[j])

            else:
                continue
    return sortedPath

def pathfinder_algorithm_from_file():
    with open("PFinput.json", 'r') as PFinput:

        reqData = json.load(PFinput)

        return pathfinder_algorithm(reqData)



def pathfinder_algorithm(reqData):

    global reqBand
    global reqDelay
    global reqJitter
    global reqPacketLoss
    k_sel = 1            # CUSTOMIZABLE VALUE: selected k path

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

    reqID = reqData['requestID']
    srcAddress = reqData['src']     # retrieve source and destination device points
    dstAddress = reqData['dst']
    #reqAlarm = reqData['alarm']     # Check if request is a re-route / duplicated request
    reqParameters = reqData['parameters']

    rtTopo = reqData['topology']

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

    k = []      # Stacks number of constraints used to calculate a path

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


    print "Number of constraints: %s" % len(k)
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
        return "Error: SRC attachment point could not be loaded!"


    try:
        dstSwitch = dstAddress['dstSwitch']
        dstPort = dstAddress['dstPort']

    except:
        print mcolors.FAIL + "Error: DST attachment point could not be loaded!"
        duration = time.time()-startTime
        print "SPG End Time: ", duration, " seconds"
        return "Error: DST attachment point could not be loaded!"


    print "SRC switch: ", srcSwitch, "\n", "SRC port: ", srcPort, "\n", "DST switch: ", dstSwitch, "\n", "DST port: ", dstPort
    print mcolors.OKGREEN + "QoS-Request e2e points loaded\n", mcolors.ENDC


    # Create empty topology multiGraph to add nodes and edges
    G = nx.MultiGraph()


    # Graph structure creation from QoS-Request data (rtTopo)
    for i in range(len(rtTopo)):
        # Get all the edges/links
        edgeSrcSwitch = rtTopo[i]['src-switch']
        edgeDstSwitch = rtTopo[i]['dst-switch']
        edgeSrcPort = rtTopo[i]['src-port']
        edgeDstPort = rtTopo[i]['dst-port']
        key = str(edgeSrcSwitch)+"::"+str(edgeSrcPort)+"-"+str(edgeDstSwitch)+"::"+str(edgeDstPort)
        # Link QoS parameters
        edgeBand = rtTopo[i]['bandwidth']
        edgeDelay = rtTopo[i]['delay']
        edgeJitter = rtTopo[i]['jitter']
        edgePLoss = rtTopo[i]['packet-loss']
        print edgeSrcSwitch
        print edgeDstSwitch
        print edgeSrcPort
        print edgeDstPort
        print key, "\n"

        # NetworkX graph automatically adds nodes to the graph through edge information
        G.add_edge(edgeSrcSwitch, edgeDstSwitch, key=str(key), srcPort=edgeSrcPort, dstPort=edgeDstPort, bandwidth=edgeBand, delay=edgeDelay, jitter=edgeJitter, packetLoss=edgePLoss)

        # In older Pathfinder versions, nodes could store information such 'switch name'
        # for switch-queue applications
    print list(G.nodes(data=True))
    print G.edges(None, data=True, keys=True)

    e2e = []
    e2e.append(srcSwitch)
    e2e.append(dstSwitch)

    #plot_path(G, None, e2e, None, None, None)


    print mcolors.OKGREEN + "Topology graph structure loaded\n", mcolors.ENDC

    #######################################################################
    # Read topology QoS related parameters to apply QoS request constraints:
    #######################################################################
    # SPG algorithm Step 1: search and delete those links not meeting QoS constraints
    # For BANDWIDTH required constraint (Bottleneck QoS parameter - Critical)

    print "STEP-1 Process"

    #print mcolors.OKGREEN+"Checking link availability... [Bandwidth constraint]\n"+mcolors.ENDC

    if 'bandwidth' in k:

        eOK = [(u, v) for (u, v, d) in G.edges(data=True) if d['bandwidth'] > reqBand]
        eFail = [(u, v) for (u, v, d) in G.edges(data=True) if d['bandwidth'] <= reqBand]
        hostList = [srcSwitch, dstSwitch]

        # plot topology graph structure (optional)
        #plot_path(G, None, None, hostList, eOK, eFail, 'bandwidth')


        # Remove edges - Bottleneck QoS parameters. Links that does not satisfy bandwidth
        # constraints are removed from the graph. Minimum bandwidth rule: available_bandwidth
        # value must be GREATER than requested value to avoid removing
        """
        for u, v, data in G.edges_iter(data=True):
            if data['bandwidth'] <= reqBand:
                G.remove_edge(u, v)
        """
        # Now step-I considers multiedges between two nodes
        for u, v, key, data in G.edges_iter(data=True, keys=True):
            if data['bandwidth'] <= reqBand:

                G.remove_edge(u, v, key=key)


    hostList = [srcSwitch, dstSwitch]
    # plot topology graph structure (optional)
    #plot_path(G, None, None, hostList, None, None, 'bandwidth')


    ################################################################################
    # Connectivity check between source to destination nodes
    isPath = nx.has_path(G, srcSwitch, dstSwitch)

    if isPath:
        print mcolors.OKGREEN+"Feasible path available... [Bandwidth constraint]\n"+mcolors.ENDC

    else:
        print mcolors.FAIL+"Failure: No path available\n"+mcolors.ENDC
        return "Failure: No path available"


    # Remove edges - additive QoS parameters: If provided and requested, links that does
    # not satisfy other constraints of additive class are removed from the graph.
    # Removing rule: Additive QoS parameters value must be LESS than requested value to
    # avoid removing

    # Load Additive QoS from topology to graph weights: find requested constraints and add the statistics data to the graph
    # For DELAY, JITTER, PACKET-LOSS required constraint (Additive QoS parameter)
    # Other parameters GENERIC GRAPH COST (disabled)

    # First selection wave: delete links not meeting requested requirements
    """
    On a first approach, every constraint will be treated as a predefined named constraint:
    i.e. this step only works for: delay, jitter, packet-loss constraints, if they are delivered
    Further implementation may work with any kind of constraint (Additive-class).
    """

    if 'delay' in k:
        for u, v, key, data in G.edges_iter(data=True, keys=True):
            if data['delay'] > reqDelay:
                G.remove_edge(u, v, key=key)

    if 'jitter' in k:
        for u, v, key, data in G.edges_iter(data=True, keys=True):
            if data['delay'] > reqJitter:
                G.remove_edge(u, v, key=key)

    if 'packet-loss' in k:
        for u, v, key, data in G.edges_iter(data=True, keys=True):
            #print data
            if data['packetLoss'] > reqPacketLoss:
                G.remove_edge(u, v, key=key)

    """
    for u, v, data in G.edges_iter(data=True):
        if data['cost'] <= reqCost:
            G.remove_edge(u, v)
    """
    # Connectivity check between source to destination nodes
    isPath = nx.has_path(G, srcSwitch, dstSwitch)

    if isPath:
        print mcolors.OKGREEN+"Feasible path available... [Additive constraints]\n"+mcolors.ENDC

    else:
        print mcolors.FAIL+"Failure: No path available [Additive constraints]\n"+mcolors.ENDC
        return "Failure: No path available (Additive constraints)"

    # plot topology graph structure (optional)
    #plot_path(G, None, None, hostList, None, None, 'bandwidth')

    ################################################################################
    # SPG algorithm Step 2: search all suitable paths meeting QoS constraints
    # src and dst path check - Check path connection between src and dst

    ################################################################################

    global maxPath  # vars to store result of QoS path
    global length   # and total cost-length value of QoS path
    global keyPath  # and distinct edge keys for multiedges and port assignation

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
                #Use of AkLP algorithm for k-longest paths

                kPaths, kKeys, kCosts = AkLP(M, srcSwitch, dstSwitch, k_sel, 'bandwidth')
                print "PATH", kPaths
                print "COST", kCosts
                print "KEYS", kKeys


                #Optional use of ALP algorithm for the longest path
                """
                kPaths, kKeys, kCosts = ALP(M, srcSwitch, dstSwitch, 'bandwidth')
                print "PATH", kPaths
                print "COST", kCosts
                print "KEYS", kKeys
                """

                maxPath, keyPath, length = path_select(kPaths, kKeys, kCosts, len(kPaths))


            # Calculate minimum delay k paths
            elif 'delay' in k:
                #Use of AkSP algorithm for k-shortest paths
                kPaths, kKeys, kCosts = AkSP(M, srcSwitch, dstSwitch, k_sel, 'delay')
                print "PATH", kPaths
                print "COST", kCosts
                print "KEYS", kKeys

                maxPath, keyPath, length = path_select(kPaths, kKeys, kCosts, 1)


            # Calculate minimum jitter k paths,
            elif 'jitter' in k:
                #AkSP
                kPaths, kKeys, kCosts = AkSP(M, srcSwitch, dstSwitch, k_sel, 'jitter')
                print "PATH", kPaths
                print "COST", kCosts
                print "KEYS", kKeys

                maxPath, keyPath, length = path_select(kPaths, kKeys, kCosts, 1)


            # Calculate minimum packet-loss k paths
            elif 'packet-loss' in k:
                #AkSP
                kPaths, kKeys, kCosts = AkSP(M, srcSwitch, dstSwitch, k_sel, 'packetLoss')
                print "PATH", kPaths
                print "COST", kCosts
                print "KEYS", kKeys

                maxPath, keyPath, length = path_select(kPaths, kKeys, kCosts, 1)

            # plot topology graph structure (optional)
            #plot_path(M, maxPath, keyPath, hostList, None, None, 'bandwidth')

            print "QoS path = %s\n" % maxPath
            print "QoS key path = %s\n" % keyPath
            print "QoS length = %s\n" % length

        else:
            #Means that len(k) is greater than 1
            #So stAggregator must be applied to deal with the MCP
            print mcolors.OKGREEN+"MCP: Searching feasible paths available... Multiple Constraints Path\n"+mcolors.ENDC

            M = stAggregate(G)
            for edge in M.edges_iter(data=True, keys=True):
                print "Aggregated Cost", edge

            # plot topology graph structure (optional)
            #plot_path(M, None, None, hostList, None, None, 'total')


            kPaths, kKeys, kCosts = AkSP(M, srcSwitch, dstSwitch, k_sel, 'total')

            print "QoS k paths = %s\n" % kPaths
            print "QoS k lengths = %s\n" % kCosts
            print "QoS k Keys = %s\n" % kKeys

            maxPath, keyPath, length = path_select(kPaths, kKeys, kCosts, 1)

            #plot_path(M, maxPath, keyPath, hostList, None, None, 'total')

            print "QoS path = %s\n" % maxPath
            print "QoS key path = %s\n" % keyPath
            print "QoS length = %s\n" % length


    else:
        print mcolors.FAIL + "Failure: No path available\n"+mcolors.ENDC
        return "Failure: No path available"


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
    # Pathfinder - Path Builder
    # Port assignation per edge and node
    #

            # IMPORTANT NOTE: current Floodlight StaticflowEntryPusher
            # assumes all flow entries to have unique name across all switches
            # (this will most possibly be relaxed later), but for now we
            # encode each flow entry's name with both switch dpid, qos request-id
            # and flow type ( consider flows: forward/reverse, farp/rarp)
    # Disabled flow pusher - returns output (QoS path switch-port), and disables queues... DONE
    # dynamic configuration

    auxPath = []    # auxiliar to store path ports
    linkKey = None

    print "switches to configure: %s" % maxPath

    #edgeFormat = True
    auxPath2 = []   #an alternative list for QOS path in edge format style

    if length != 0:
        getEdgePath = to_edge_path(maxPath, M)
        print "PATH(edge format)", getEdgePath

        midSwitches = defaultdict(list)
        idx = 0

        #if len(getEdgePath) == 1:
                    #getEdgePath.append(getEdgePath[0])

        # Get node end points for each edge in maxPath list to first check if maxPath nodes are
        # bound to the edge keys from keyPath list and its matching
        for idx in range(len(getEdgePath)):

            node1, node2 = getEdgePath[idx]
            #print "2nodes", node1, node2

            for idx in range(len(keyPath)):

                #print "keypath", keyPath, idx, range(len(keyPath))

                linkKey = keyPath[idx]
                #linkKey = keyPath
                #print "linkKey", linkKey

                if linkKey in G.get_edge_data(node1, node2):
                    #print "FOUND:", linkKey, "=", node1, node2
                    break
            # For the maxPath node and keyPath key matching, next step is to split edge key string to
            # get switch::port data for each edge in its correct order

            edgePoints = linkKey.split('-')
            #print "edgePoints", edgePoints

            edgeSrc = edgePoints[0].split('::')
            edgeDst = edgePoints[1].split('::')

            #print "edgeSrc", edgeSrc
            #print "edgeDst", edgeDst


            # Then the switch::ports items are parsed and added to the final QoS path response
            # Get all the links switch::ports data first
            edgeSrcSwitch = edgeSrc[0]
            edgeDstSwitch = edgeDst[0]
            edgeSrcPort = edgeSrc[1]
            edgeDstPort = edgeDst[1]

            print "edgeSrcSwitch", edgeSrcSwitch
            print "edgeDstSwitch", edgeDstSwitch
            print "edgeSrcPort", edgeSrcPort
            print "edgeDstPort", edgeDstPort
            #print key, "\n"

            configString = ""
            checkedList = []    #the check list is unused


            if edgeSrcSwitch == srcSwitch:
                    qosNode2 = {'switch': srcSwitch, 'port': srcPort}, ({'endpoint': 'endpointA'})
                    auxPath2.append(qosNode2)
                    print "auxPath2 append", auxPath2


            elif edgeDstSwitch == srcSwitch:
                    qosNode2 = {'switch': srcSwitch, 'port': srcPort}, ({'endpoint': 'endpointA'})
                    auxPath2.append(qosNode2)
                    print "auxPath2 append", auxPath2

            elif edgeSrcSwitch == dstSwitch:
                    qosNode2 = {'switch': dstSwitch, 'port': dstPort}, ({'endpoint': 'endpointB'})
                    auxPath2.append(qosNode2)
                    print "auxPath2 append", auxPath2


            if edgeDstSwitch == dstSwitch:
                    qosNode2 = {'switch': dstSwitch, 'port': dstPort}, ({'endpoint': 'endpointB'})
                    auxPath2.append(qosNode2)
                    print "auxPath2 append", auxPath2

            qosNode2 = ({'switch': edgeSrcSwitch, 'port': edgeSrcPort}, {'switch': edgeDstSwitch, 'port': edgeDstPort})
            auxPath2.append(qosNode2)
            print "auxPath2 append", auxPath2

            """
            qosNode2 = {'switch': edgeDstSwitch, 'port': edgeDstPort}
            auxPath2.append(qosNode2)
            """


            if (edgeSrcSwitch == node1 or node2) and (edgeDstSwitch == node1 or node2):
                        print edgeSrcSwitch, edgeDstSwitch
                        print edgeSrcPort, edgeDstPort
                        if edgeSrcSwitch == srcSwitch:
                            """
                            # Switch Queues Configuration
                            srcSwitchName = G.node[srcSwitch]['name']
                            print srcSwitchName

                            configString += " -- set Port %s-eth%s qos=@newqos" % (srcSwitchName, srcPort)
                            configString += " -- set Port %s-eth%s qos=@newqos" % (srcSwitchName, edgeSrcPort)
                            """
                            qosNode = {'switch': srcSwitch, 'portA': srcPort, 'portB': edgeSrcPort}
                            auxPath.append(qosNode)
                            print "auxPath append", auxPath

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

                            else:
                                qosNode = {'switch': dstSwitch, 'portA': dstPort, 'portB': edgeDstPort}
                                auxPath.append(qosNode)
                                print "auxPath append", auxPath


                        elif edgeSrcSwitch == dstSwitch and edgeSrcSwitch not in checkedList:
                            """
                            # Switch Queues Configuration
                            dstSwitchName = G.node[dstSwitch]['name']
                            print dstSwitchName
                            configString += " -- set Port %s-eth%s qos=@newqos" % (dstSwitchName, dstPort)
                            configString += " -- set Port %s-eth%s qos=@newqos" % (dstSwitchName, edgeSrcPort)
                            """

                            qosNode = {'switch': dstSwitch, 'portA': dstPort, 'portB': edgeSrcPort}
                            auxPath.append(qosNode)
                            print "auxPath append", auxPath

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

                            qosNode = {'switch': dstSwitch, 'portA': dstPort, 'portB': edgeDstPort}
                            auxPath.append(qosNode)
                            print "auxPath append", auxPath

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

                        elif edgeDstSwitch == srcSwitch and edgeDstSwitch not in checkedList:

                            # Switch Queues Configuration
                            """
                            srcSwitchName = G.node[srcSwitch]['name']
                            print dstSwitchName
                            configString += " -- set Port %s-eth%s qos=@newqos" % (srcSwitchName, srcPort)
                            configString += " -- set Port %s-eth%s qos=@newqos" % (srcSwitchName, edgeSrcPort)
                            """

                            qosNode = {'switch': srcSwitch, 'portA': srcPort, 'portB': edgeDstPort}
                            auxPath.append(qosNode)
                            print "auxPath append", auxPath

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
                            if edgeSrcSwitch != dstSwitch:
                                midSwitches[edgeSrcSwitch].append(edgeSrcPort)



                        else:
                            #switch is between other switches; create a dict with switch - ports (midSwitch : port-pair)
                            #maxPath contains route order, then midSwitches are stored in path order
                            midSwitches[edgeSrcSwitch].append(edgeSrcPort)
                            midSwitches[edgeDstSwitch].append(edgeDstPort)

        print "midswitches", midSwitches

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

                qosNode = {'switch': midSwitch, 'portA': str(midPorts[0]), 'portB': str(midPorts[1])}
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
        #queueDb = open('./queueDb.txt', 'a')
        print "config string:", configString
        queueString = "sudo ovs-vsctl%s -- --id=@newqos create QoS type=linux-htb other-config:max-rate=30000000 queues=0=@q0,1=@q1 -- --id=@q0 create Queue other-config:max-rate=30000000 other-config:priority=1 -- --id=@q1 create Queue other-config:min-rate=20000000 other-config:priority=8" % configString
        qResult = os.popen(queueString).read()
        print "queue string:", queueString
        print "qResult:", qResult
        queueDb.write(qResult+"\n")
        """


        qosPath = path_sort(maxPath, auxPath)
        print "\n" + mcolors.OKGREEN + "QOS PATH: %s\n" % qosPath, mcolors.ENDC

        # The alternative style path refers to a link/edge composed path. Pathfinder is able
        # to return a result in this format too. If this is needed, next code must be enabled:
        #
        # qosPath = auxPath2
        #
        print "Alternative style", auxPath2

    else:
        qosPath = [{'switch': srcSwitch, 'portA': srcPort, 'portB': dstPort}]
        print "QoS Path of a single device: ", qosPath


    if os.path.exists('./path.json'):
        pathRes = open('./path.json', 'r')
        lines = pathRes.readlines()
        pathRes.close()

    else:
        lines = {}
        print "Path log file not found. Creating new log file.\n"
        with open('path.json', 'wb') as path_log:
            json.dump(lines, path_log)

    # requestID is an optional field but must be provided
    #qosPath.append({"requestID": reqID, "srcIP": srcAddress, "dstIP": dstAddress})    # requestID may be provided along with the QoS path list
    pathRes = open('./path.json', 'w')
    to_serial = qosPath
    serial = json.dumps(to_serial)
    #serial = json.dumps(to_serial, indent=2, separators=(',', ': '))
    pathRes.write(serial+"\n")


    ################################################################################
    # store created circuit attributes in local ./qosDb.json

    date_time = time.asctime()
    #qosDb = open('./pathfinder/qosDb.json', 'a')
    #circuitParams = {'requestID': reqID, 'src': srcAddress, 'dst': dstAddress, 'qos': reqParameters, 'datetime': date_time}
    #crtParams = json.dumps(circuitParams)
    #qosDb.write(crtParams+"\n")

    duration = time.time()-startTime
    print("SPG End Time ", duration, " seconds")

    return qosPath
    #return auxPath2

if __name__ == '__main__':
    result = pathfinder_algorithm_from_file()
    print "result", result
