#!/usr/bin/env python
# encoding: utf-8

"""
Adapter App: Collects data from different sources to build up a QoS request that
 Pathfinder algorithm can understand.

"""

__author__ = 'Dani'

# Import libraries
import os
import argparse
import json
import time
import sys
from collections import defaultdict

import networkx as nx



# parse controller address.
# Syntax:
#   *FLOODLIGHT* --controller {IP:REST_PORT}

parser = argparse.ArgumentParser(description='Suitable Path Generator')
parser.add_argument('--controller', dest='controllerRestIp', action='store', default='localhost:8080', help='controller IP:RESTport, e.g., localhost:8080 or A.B.C.D:8080')
parser.add_argument('--input', dest='fileName', default='None', help='Optional request file path, e.g., pathfinder/request.json', metavar='FILE')
parser.add_argument('--topo', dest='topoStats', default='None', help='Optional topology file path, e.g., pathfinder/topology.json', metavar='FILE')
args = parser.parse_args()
print args, "\n"

controllerRestIp = args.controllerRestIp
inputfile = args.fileName


class mcolors:
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.OKGREEN = ''
        self.FAIL = ''
        self.ENDC = ''

#
# INPUT: First it checks if a local request source file exists, called request.json for testing purposes,
# that will include QoS requirements plus necessary data unavailable from the controller
if args.fileName is not None:

    # if os.path.exists('./request.json'):
    if os.path.exists(args.fileName):
        # PFinput = open('./request.json', 'r')
        PFinput = open(args.fileName, 'r')
        lines = PFinput.readlines()
        PFinput.close()

    else:
        raise Exception("The file %s does not exist" % args.fileName)

    print(lines)



"""
# OUTPUT: A local request source file may exists, called PFinput2.json for testing purposes
# It will store the PFinput file, as a output result to be sent to Pathfinder REST API
# or locally processed by Pathfinder algorithm

if os.path.exists('./PFinput2.json'):
    PFinput = open('./PFinput2.json', 'r')
    lines = PFinput.readlines()
    PFinput.close()

else:
    lines = {}
    print "QoS-Request file not found. Creating new request file.\n"
    with open('PFinput2.json', 'wb') as PFinput:
        json.dump(lines, PFinput)

print(lines)


"""

# load request data to build up output PFinput.json

reqID = None
reqAlarm = None     # Check if request is a re-route / duplicated request
reqBand = None
reqDelay = None     # Data gathering not yet implemented
reqPacketLoss = None
reqJitter = None    # Not used, QoS parameter to consider
reqCost = None      # Not used, QoS link average state
k = []               # To stack number of constraints used to calculate a path

"""
#TODO: change to new input data structure (PFinput.json)
with open("QoS_Request.json") as qosRequest:
    reqData = json.load(qosRequest)
    reqID = reqData['requestID']
    reqAlarm = reqData['alarm']
    print "QoS Request ID: %s\n" % reqID
"""
"""
    if dataID == reqID:
        if reqAlarm == 0:
            print mcolors.FAIL + "QoS Request ID: %s already exists. A new ID is required to initialize.\n" % reqID
            duration = time.time()-startTime
            print "SPG End Time: ", duration, " seconds"
            sys.exit()
    if reqAlarm != 0:
        print mcolors.OKGREEN + "QoS Request Alarm: %s re-route requested\n" % reqID, mcolors.ENDC
"""
"""
    with open("QoS_Request.json") as qosRequest:
        reqData = json.load(qosRequest)

        if 'bandwidth' in reqData:
            if reqData['bandwidth'] is not 0:
                reqBand = reqData['bandwidth']
                print "Requested minimum bandwidth: %s" % reqBand
                #k.append('bandwidth')

        if 'delay' in reqData:
            if reqData['delay'] is not 0:
                reqDelay = reqData['delay']
                print "Requested maximum delay: %s" % reqDelay
                #k.append('delay')

        if 'jitter' in reqData:
            if reqData['jitter'] is not 0:
                reqJitter = reqData['jitter']
                print "Requested maximum jitter: %s" % reqJitter
                #k.append('jitter')

        if 'packet-loss' in reqData:
            if reqData['packet-loss'] is not 0:
                reqPacketLoss = reqData['packet-loss']
                print "Requested maximum packet-loss: %s" % reqPacketLoss, "%"
                #k.append('packet-loss')


        print("QoS Request data loaded.\n")



# retrieve source and destination device attachment points
# using Floodlight's DeviceManager REST API

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

print "SRC switch: ", srcSwitch, "\n", "SRC port: ", srcPort, "\n", "DST switch: ", dstSwitch, "\n", "DST port: ", dstPort

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


print("Topology data loaded")

#######################################################################
"""