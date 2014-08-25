#!/usr/bin/env python
# encoding: utf-8

__author__ = 'Dani'

import json
import networkx as nx
from MCP import plot_path

with open("PFinput.json", 'r') as PFinput:
    reqData = json.load(PFinput)
    print reqData
    reqId = reqData['requestID']
    srcAddress = reqData['ip-src']
    dstAddress = reqData['ip-dst']
    reqAlarm = reqData['alarm']
    reqParameters = reqData['parameters']

    reqBand = reqData['parameters']['bandwidth']
    reqDelay = reqData['parameters']['delay']
    reqJitter = reqData['parameters']['jitter']
    reqPLoss = reqData['parameters']['packet-loss']

    rtTopo = reqData['topology']

    """
    reqJitter = reqData[0]['attachmentPoint'][0]['port']
    reqPLoss = reqData[0]['attachmentPoint'][0]['port']
    """
    print "QoS Request ID: %s" % reqId
    print "QoS Request SOURCE address: %s" % srcAddress
    print "QoS Request DESTINATION address: %s" % dstAddress
    print "QoS Request ALARM flag: %s" % reqAlarm
    print "QoS Request PARAMETERS: %s" % reqParameters

    print "QoS Request BANDWIDTH: %s" % reqBand
    print "QoS Request DELAY: %s" % reqDelay
    print "QoS Request JITTER: %s" % reqJitter
    print "QoS Request PACKET-LOSS: %s" % reqPLoss

    print "QoS Request TOPOLOGY: %s" % rtTopo

    """
    print "SOURCE DPID: %s" % srcSwitch
    print "SOURCE PORT: %s" % srcPort
    """

    for i in range(len(reqData)):
        topoSrcSwitch = reqData['topology'][i]['src-switch']
        topoSrcPort = reqData['topology'][i]['src-port']
        topoDstSwitch = reqData['topology'][i]['dst-switch']
        topoDstPort = reqData['topology'][i]['dst-port']
        edgeBand = reqData['topology'][i]['bandwidth']
        edgeDelay = reqData['topology'][i]['delay']
        edgeJitter = reqData['topology'][i]['jitter']
        edgePLoss = reqData['topology'][i]['packet-loss']

        print "edge SOURCE SWITCH: %s" % topoSrcSwitch
        print "edge SOURCE PORT: %s" % topoSrcPort
        print "edge TARGET SWITCH: %s" % topoDstSwitch
        print "edge TARGET PORT: %s" % topoDstPort
        print "edge BANDWIDTH: %s" % edgeBand
        print "edge DELAY: %s" % edgeDelay
        print "edge JITTER: %s" % edgeJitter
        print "edge PACKET-LOSS: %s" % edgePLoss + "\n"




# graph builder
G = nx.MultiGraph()

for i in range(len(rtTopo)):
    edgeSrcSwitch = rtTopo[i]['src-switch']
    edgeDstSwitch = rtTopo[i]['dst-switch']
    edgeSrcPort = rtTopo[i]['src-port']
    edgeDstPort = rtTopo[i]['dst-port']
    key = str(edgeSrcSwitch)+"-"+str(edgeDstSwitch)
    print edgeSrcSwitch, "\n"
    print edgeDstSwitch, "\n"
    print edgeSrcPort, "\n"
    print edgeDstPort, "\n"
    print key

    G.add_edge(edgeSrcSwitch, edgeDstSwitch, key=str(key), srcPort=edgeSrcPort, dstPort=edgeDstPort)

print list(G.nodes(data=True))
print G.edges(None, data=True, keys=True)


plot_path(G)








# main vars
delta_sec = 2        # seconds to delay in time.sleep
check_freq = 10     # seconds to check requests