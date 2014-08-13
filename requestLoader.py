#!/usr/bin/env python
# encoding: utf-8


__author__ = 'Dani'

import json
import os
import argparse

parser = argparse.ArgumentParser(description='Suitable Path Generator')
parser.add_argument('--controller', dest='controllerRestIp', action='store', default='localhost:8080', help='controller IP:RESTport, e.g., localhost:8080 or A.B.C.D:8080')
args = parser.parse_args()
print args, "\n"

controllerRestIp = args.controllerRestIp


with open("PFinput.json", 'r') as PFinput:
    reqData = json.load(PFinput)
    print reqData
    srcAddress = reqData['ip-src']
    dstAddress = reqData['ip-dst']
    srcSwitch = reqData[0]['attachmentPoint'][0]['switchDPID']
    srcPort = reqData[0]['attachmentPoint'][0]['port']
    print "QoS Request SOURCE address: %s" % srcAddress
    print "QoS Request DESTINATION address: %s" % dstAddress
    print "SOURCE DPID: %s" % srcSwitch
    print "SOURCE PORT: %s" % srcPort

"""

"""



"""
command = "curl -s http://%s//wm/core/controller/switches/json" % args.controllerRestIp
result = os.popen(command).read()
print command+"\n"
print result
"""
"""
for parsedResult in json.loads(result):
    switchID = parsedResult['dpid']
    switchName = parsedResult['ports'][0]['name']
    print switchID
    print switchName
"""

"""
with open("topology.json") as topologyData:
            parsedData = json.load(topologyData)
            for i in range(len(parsedData)):
                    topoSrcSwitch = parsedData[i]['src-switch']
                    topoDstSwitch = parsedData[i]['dst-switch']
                    edgeBand = parsedData[i]['bandwidth']

                    if G.has_edge(topoSrcSwitch, topoDstSwitch):
                        G.add_edge(topoSrcSwitch, topoDstSwitch, key=topoSrcSwitch+topoDstSwitch, bandwidth=edgeBand)
                    print "edge: %s - %s, bandwidth: %s, key: %s" % (topoSrcSwitch, topoDstSwitch, edgeBand, topoSrcSwitch+topoDstSwitch)

"""