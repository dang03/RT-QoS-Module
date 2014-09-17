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
import sys
#from collections import defaultdict




# parse controller address.
# Syntax:
# *FLOODLIGHT* --controller {IP:REST_PORT}
# Usage from CLI, e.g.: python Adapter.py --input request.json

parser = argparse.ArgumentParser(description='Suitable Path Generator')
parser.add_argument('--controller', '-c', dest='controllerRestIp', action='store', default='localhost:8080',
                    help='controller IP:RESTport, e.g., localhost:8080 or A.B.C.D:8080')
parser.add_argument('--request', '-r', dest='fileName', default=None,
                    help='Optional request file path, e.g., pathfinder/request.json', metavar='FILE')
parser.add_argument('--topo', '-t', dest='topoStats', default=None,
                    help='Optional topology file path, e.g., pathfinder/topology.json', metavar='FILE')
args = parser.parse_args()
print args, "\n"


controllerRestIp = args.controllerRestIp
inputfile = args.fileName
tpofile = args.topoStats


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
        RElines = PFinput.readlines()
        PFinput.close()

    else:
        raise Exception("The file %s does not exist" % args.fileName)

    print(RElines)


if args.topoStats is not None:

    if os.path.exists(args.topoStats):
        PFtopo = open(args.topoStats, 'r')
        TOlines = PFtopo.readlines()
        PFtopo.close()

    else:
        raise Exception("The file %s does not exist" % args.topoStats)

    print(TOlines)


# load request data to build up output PFinput.json
global srcAddress
global dstAddress
parameters = {}

#global reqID
#global reqAlarm    # Check if request is a re-route / duplicated request
global reqBand
global reqDelay    # Data gathering not yet implemented
global reqPacketLoss
global reqJitter   # Not used, QoS parameter to consider
#global reqCost     # Not used, QoS link average state
               # To stack number of constraints used to calculate a path

# Load request.json data from file to turn JSON object into python and parse data
with open('request.json') as qosRequest:
    reqData = json.load(qosRequest)
    reqID = reqData['requestID']
    # reqAlarm = reqData['alarm']
    print "reqData", reqData
    #print "QoS Request ID: %s\n" % reqID

    # Source and destination data parsing
    # A source point or address is required by PF input
    if 'ip-src' in reqData:
        if reqData['ip-src']:
            srcAddress = reqData['ip-src']

            print "QoS Request SOURCE address: %s" % srcAddress

        else:
            raise Exception(mcolors.FAIL + "Source address is not valid" + mcolors.ENDC)
            #reqBand = reqData['bandwidth']
            #print "Requested minimum bandwidth: %s" % reqBand
            #k.append('bandwidth')
    else:
        raise Exception(mcolors.FAIL + "Source address not found" + mcolors.ENDC)

    # A destination point or address is required by PF input
    if 'ip-dst' in reqData:
        if reqData['ip-dst']:
            dstAddress = reqData['ip-dst']

            print "QoS Request DESTINATION address: %s" % dstAddress

        else:
            raise Exception(mcolors.FAIL + "Destination address is not valid" + mcolors.ENDC)
            #print "Requested minimum bandwidth: %s" % reqBand
            #k.append('bandwidth')
    else:
        raise Exception(mcolors.FAIL + "Destination address not found" + mcolors.ENDC)


    # QoS requirements data parsing; a QoS stat must be higher than '0' to be requested
    # Bandwidth
    if 'bandwidth' in reqData:
        #if reqData['bandwidth'] is not 0:
            reqBand = reqData['bandwidth']
            print "Requested minimum bandwidth: %s" % reqBand
            parameters.update({"bandwidth": reqBand})

    # Delay
    if 'delay' in reqData:
        #if reqData['delay'] is not 0:
            reqDelay = reqData['delay']
            print "Requested maximum delay: %s" % reqDelay
            parameters.update({"delay": reqDelay})

    # Jitter
    if 'jitter' in reqData:
        #if reqData['jitter'] is not 0:
            reqJitter = reqData['jitter']
            print "Requested maximum jitter: %s" % reqJitter
            parameters.update({"jitter": reqJitter})

    # Packet-Loss
    if 'packet-loss' in reqData:
        #if reqData['packet-loss'] is not 0:
            reqPacketLoss = reqData['packet-loss']
            print "Requested maximum packet-loss: %s" % reqPacketLoss, "%"
            parameters.update({"packet-loss": reqPacketLoss})

    # Request may provide an ID, it will be included in the PF input
    if 'requestID' in reqData:
        if reqData['requestID']:
            ReqID = reqData['requestID']



    # A request may include additional data fields, such an alarm flag for duplicated
    # QoS requests. To add more data fields, just add next code lines for each additional
    # string data field, e.g. 'alarm':
    """
    if 'alarm' in reqData:
        if reqData['alarm']:
            additionalData = reqData['alarm']

    """

    print(mcolors.OKGREEN + "QoS Request data loaded.\n" + mcolors.ENDC)



# retrieve source and destination device attachment points
# using Floodlight's DeviceManager REST API

command = "curl -s http://%s/wm/device/?ipv4=%s" % (args.controllerRestIp, srcAddress)
result = os.popen(command).read()
try:
    parsedResult = json.loads(result)
    print command + "\n"

    srcSwitch = parsedResult[0]['attachmentPoint'][0]['switchDPID']
    srcPort = parsedResult[0]['attachmentPoint'][0]['port']

except:
    print mcolors.FAIL + "Error: Controller could not find SRC attachment point!" + mcolors.ENDC
    sys.exit()

command = "curl -s http://%s/wm/device/?ipv4=%s" % (args.controllerRestIp, dstAddress)
result = os.popen(command).read()
parsedResult = json.loads(result)
print command + "\n"
try:
    dstSwitch = parsedResult[0]['attachmentPoint'][0]['switchDPID']
    dstPort = parsedResult[0]['attachmentPoint'][0]['port']

except:
    print mcolors.FAIL + "Error: Controller could not find DST attachment point!" + mcolors.ENDC
    sys.exit()

print srcSwitch, "\n", srcPort, "\n", dstSwitch, "\n", dstPort

print "SRC switch: ", srcSwitch, "\n", "SRC port: ", srcPort, "\n", "DST switch: ", dstSwitch, "\n", "DST port: ", dstPort


# Get all the nodes/switches
"""
Available switch information fields from Floodlight controller:

{
"inetAddress":"/127.0.0.1:57246",
"role":null,
"ports":[
    {"hardwareAddress":"26:7d:b5:d6:63:40",
    "portNumber":65534,
    "config":1,
    "currentFeatures":0,
    "advertisedFeatures":0,
    "supportedFeatures":0,
    "peerFeatures":0,
    "name":"s6",
    "state":1}
],
"buffers":256,
"featuresReplyFromSwitch":{
    "transactionId":8,
    "cancelled":false,
    "done":true
},
"connectedSince":1410862280715,
"capabilities":199,
"tables":-1,
"actions":4095,
"dpid":"00:00:00:00:00:00:00:06",
"attributes":{
    "supportsOfppFlood":true,
    "FastWildcards":4194303,
    "DescriptionData":{
        "serialNumber":"None",
        "hardwareDescription":"Open vSwitch",
        "softwareDescription":"1.4.6",
        "datapathDescription":"None",
        "manufacturerDescription":"Nicira Networks, Inc.",
        "length":1056},
    "supportsOfppTable":true}
}
"""
command = "curl -s http://%s//wm/core/controller/switches/json" % args.controllerRestIp
result = os.popen(command).read()
print command + "\n"
print result
nodeList = list()
for parsedResult in json.loads(result):
    switchID = parsedResult['dpid']
    switchName = parsedResult['ports'][0]['name']
    print switchID
    print switchName
    nodeList.append(({'switch_DPID': switchID,
                     'sw_name': switchName}))
    print nodeList


# Get all the edges/links
command = "curl -s http://%s//wm/topology/links/json" % args.controllerRestIp
rtTopo = json.loads((os.popen(command).read()))
print rtTopo
print command+"\n"
"""
edgeList = list()
for parsedResult in json.loads(rtTopo):
    edgeSrcSwitch = parsedResult['src-switch']
    edgeDstSwitch = parsedResult['dst-switch']
    edgeSrcPort = parsedResult['src-port']
    edgeDstPort = parsedResult['dst-port']
    edgeSrcPortState = parsedResult['']
    edgeDstPortState = parsedResult['']
    edgeType = parsedResult['']
    print edgeSrcSwitch, "\n"
    print edgeDstSwitch, "\n"
    print edgeSrcPort, "\n"
    print edgeDstPort, "\n"
    edgeList.append({"src-switch": edgeSrcSwitch,
                     "src-port": edgeSrcPort,
                     "src-port-state": edgeSrcPortState,
                     "dst-switch": edgeDstSwitch,
                     "dst-port": edgeDstPort,
                     "dst-port-state": edgeDstPortState,
                     "type": edgeType})
"""

# The topology QoS stats data must be stored on a file, or called as a parameter by
# Adapter.py, just as the request data.

with open("topology.json") as topo_json:
    topo_stats = json.load(topo_json)
    # reqID = reqData['requestID']
    #reqAlarm = reqData['alarm']
    print "topoStats", topo_stats

    for link_s in topo_stats:
        linkSrcSwitch = link_s['src-switch']
        linkDstSwitch = link_s['dst-switch']
        linkSrcPort = link_s['src-port']
        linkDstPort = link_s['dst-port']
        for link_d in rtTopo:
            if linkSrcSwitch == link_d['src-switch'] and linkSrcPort == link_d['src-port'] and linkDstSwitch == link_d['dst-switch'] and linkDstPort == link_d['dst-port']:

                link_d['bandwidth'] = link_s['bandwidth']
                link_d['delay'] = link_s['delay']
                link_d['jitter'] = link_s['jitter']
                link_d['packet-loss'] = link_s['packet-loss']



input_data = {"requestID": reqID, "src": {"srcSwitch": srcSwitch, "srcPort": srcPort}}

input_data["dst"] = {"dstSwitch": dstSwitch, "dstPort": dstPort}

input_data["parameters"] = parameters

input_data["topology"] = rtTopo


# OUTPUT: A local request source file may exists, called PFinput2.json for testing purposes
# It will store the PFinput file, as a output result to be sent to Pathfinder REST API
# or locally processed by Pathfinder algorithm
print "Creating new request file.\n"
with open('PFinput2.json', 'wb') as PFinput2:
        json.dump(input_data, PFinput2, indent=4)
        PFinput2.close()

