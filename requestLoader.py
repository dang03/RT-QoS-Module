#!/usr/bin/env python
# encoding: utf-8


__author__ = 'Dani'

import json

with open("QoS_Request.json") as qosRequest:
    reqData = json.load(qosRequest)
    srcAddress = reqData['ip-src']
    dstAddress = reqData['ip-dst']
    print "QoS Request SOURCE address: %s" % srcAddress
    print "QoS Request DESTINATION address: %s" % dstAddress


command = "curl -s http://%s/wm/device/?ipv4=%s" % (args.controllerRestIp, srcAddress)
result = os.popen(command).read()
try:
    parsedResult = json.loads(result)
    print command+"\n"

    srcSwitch = parsedResult[0]['attachmentPoint'][0]['switchDPID']
    srcPort = parsedResult[0]['attachmentPoint'][0]['port']





command = "curl -s http://%s//wm/core/controller/switches/json" % args.controllerRestIp
result = os.popen(command).read()
print command+"\n"
print result
for parsedResult in json.loads(result):
    switchID = parsedResult['dpid']
    switchName = parsedResult['ports'][0]['name']
    print switchID
    print switchName


    
with open("topology.json") as topologyData:
            parsedData = json.load(topologyData)
            for i in range(len(parsedData)):
                    topoSrcSwitch = parsedData[i]['src-switch']
                    topoDstSwitch = parsedData[i]['dst-switch']
                    edgeBand = parsedData[i]['bandwidth']

                    if G.has_edge(topoSrcSwitch, topoDstSwitch):
                        G.add_edge(topoSrcSwitch, topoDstSwitch, key=topoSrcSwitch+topoDstSwitch, bandwidth=edgeBand)
                    print "edge: %s - %s, bandwidth: %s, key: %s" % (topoSrcSwitch, topoDstSwitch, edgeBand, topoSrcSwitch+topoDstSwitch)

