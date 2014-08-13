#!/usr/bin/env python
# encoding: utf-8

__author__ = 'Dani'

import json

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
    mistery = reqData['topology'][0]['src-switch']

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
    print "QoS Request MISTERY: %s" % mistery

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



# main vars
delta_sec = 2        # seconds to delay in time.sleep
check_freq = 10     # seconds to check requests