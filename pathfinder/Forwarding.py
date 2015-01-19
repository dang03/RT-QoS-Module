#!/usr/bin/env python
# encoding: utf-8

__author__ = 'Daniel'

import os
import json
import random
from collections import defaultdict


def get_ports(controllerIp):
    command = "curl -s http://%s//wm/core/controller/switches/json" % controllerIp
    result = os.popen(command).read()
    print command + "\n"

    nodeList = list()
    portName = list()

    for parsedResult in json.loads(result):
        switchID = parsedResult['dpid']
        for portNames in parsedResult['ports'][1:]:
            portName.append(portNames['name'])

        switchName = parsedResult['ports'][0]['name']
        nodeList.append(({'switch_DPID': switchID,
                         'sw_name': switchName}))
        print nodeList
        print portName

    return nodeList, portName


def set_queues_all(controllerIp):

    queuesDict ={}
    nodeList, portName = get_ports(controllerIp)

    configString = ""

    for eth in portName:
        configString += " -- set Port %s qos=@newqos" % eth


    ########################################################
    ##################### QUEUE CONFIG #####################

    """ Number of queues """    # Max of 8
    num_queues = 8

    """ Topology Maximum Bit-rate """    # 1 MB = 1000000
    maximum = 1000000

    """ Queue 0 """     # Best-Effort queue, only maximum bit-rate settings
    max_rate = 1
    priority = 1

    """ Queue 1 """
    min_rate1 = 100
    priority1 = 8

    """ Queue 2 """
    min_rate2 = 80
    priority2 = 8

    """ Queue 3 """
    min_rate3 = 75
    priority3 = 8

    """ Queue 4 """
    min_rate4 = 125
    priority4 = 8

    """ Queue 5 """
    min_rate5 = 65
    priority5 = 8

    """ Queue 6 """
    min_rate6 = 85
    priority6 = 8

    """ Queue 7 """
    min_rate7 = 1
    priority7 = 8

    ########################################################
    ########################################################

    queueBody = " -- --id=@newqos create QoS type=linux-htb other-config:max-rate=%s " % maximum
    queueBody += "queues="
    for x in range(num_queues):
        if num_queues > 8:
            raise IOError
        if num_queues == 1:
            queueBody += "%s=@q%s" % (x, x)
        elif x == num_queues-1:
            queueBody += "%s=@q%s" % (x, x)
        else:
            queueBody += "%s=@q%s," % (x, x)

    queueBody += " --"
    configString += queueBody
    for x in range(num_queues):
        if x == 0:
            configString += " --id=@q%s create Queue other-config:min-rate=%s other-config:priority=%s" % (x, max_rate, priority)
        elif x == 1:
            configString += " -- --id=@q%s create Queue other-config:min-rate=%s other-config:priority=%s" % (x, min_rate1, priority1)
            key = "q%s" % x
            queuesDict[key] = "%s" % min_rate1
        elif x == 2:
            configString += " -- --id=@q%s create Queue other-config:min-rate=%s other-config:priority=%s" % (x, min_rate2, priority2)
            key = "q%s" % x
            queuesDict[key] = "%s" % min_rate2
        elif x == 3:
            configString += " -- --id=@q%s create Queue other-config:min-rate=%s other-config:priority=%s" % (x, min_rate3, priority3)
            key = "q%s" % x
            queuesDict[key] = "%s" % min_rate3
        elif x == 4:
            configString += " -- --id=@q%s create Queue other-config:min-rate=%s other-config:priority=%s" % (x, min_rate4, priority4)
            key = "q%s" % x
            queuesDict[key] = "%s" % min_rate4
        elif x == 5:
            configString += " -- --id=@q%s create Queue other-config:min-rate=%s other-config:priority=%s" % (x, min_rate5, priority5)
            key = "q%s" % x
            queuesDict[key] = "%s" % min_rate5
        elif x == 6:
            configString += " -- --id=@q%s create Queue other-config:min-rate=%s other-config:priority=%s" % (x, min_rate6, priority6)
            key = "q%s" % x
            queuesDict[key] = "%s" % min_rate6
        elif x == 7:
            configString += " -- --id=@q%s create Queue other-config:min-rate=%s other-config:priority=%s" % (x, min_rate7, priority7)
            key = "q%s" % x
            queuesDict[key] = "%s" % min_rate7
        else:
            raise IOError

    print "config string:", configString

    queueString = "sudo ovs-vsctl%s" % configString
    qResult = os.popen(queueString).read()
    print "queue string:", queueString
    print "qResult:", qResult
    return queuesDict

def queue_selector(request, queueDict):
    chosen = None
    aux = 0
    for queue, value in queueDict.items():
        print queue, value, request
        res = int(value) - request
        if res == 0:
            return queue
        elif aux == 0:
            aux = res
            chosen = queue
        elif aux > res > 0:
            aux = res
            chosen = queue
        else:
            continue
    print "Queue, aux", chosen, aux, ":", request
    return chosen

def smart_flow_pusher(srcAddress, dstAddress, controllerRestIp, path, request, queueDict):

    midSwitches = defaultdict(list)

    q = []
    qname = queue_selector(request, queueDict)
    q[:1] = qname

    for device in path:
        print "device", device
        switch = device['switch']
        port1 = device['portA']
        port2 = device['portB']

        midSwitches[switch].append(port1)
        midSwitches[switch].append(port2)

    print "result", midSwitches


    for midSwitch, midPorts in midSwitches.iteritems():

        print "%s - %s, %s" % (str(midSwitch), str(midPorts[0]), str(midPorts[1]))

        #push midSwitches flowmods
        command = "sudo curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-ip\":\"%s\", \"dst-ip\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"enqueue=%s:%s\"}' http://%s/wm/staticflowentrypusher/json" % ((str(midSwitch)), str(random.randrange(0, 1000))+(str(midSwitch))+".f", srcAddress, dstAddress, "0x800", (str(midPorts[0])), (str(midPorts[1])), (str(q[1])), controllerRestIp)
        result = os.popen(command).read()
        print command

        command = "sudo curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-ip\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"output=%s\"}' http://%s/wm/staticflowentrypusher/json" % ((str(midSwitch)), str(random.randrange(0, 1000))+(str(midSwitch))+".farp", srcAddress, "0x806", (str(midPorts[0])), (str("all")), controllerRestIp)
        result = os.popen(command).read()
        print command

        command = "sudo curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-ip\":\"%s\", \"dst-ip\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"enqueue=%s:%s\"}' http://%s/wm/staticflowentrypusher/json" % ((str(midSwitch)), str(random.randrange(0, 1000))+(str(midSwitch))+".r", dstAddress, srcAddress, "0x800", (str(midPorts[1])), (str(midPorts[0])), (str(q[1])), controllerRestIp)
        result = os.popen(command).read()
        print command

        command = "sudo curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-ip\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"output=%s\"}' http://%s/wm/staticflowentrypusher/json" % ((str(midSwitch)), str(random.randrange(0, 1000))+(str(midSwitch))+".rarp", dstAddress, "0x806", (str(midPorts[1])), (str("all")), controllerRestIp)
        result = os.popen(command).read()
        print command

    return


########################################################################################


#if __name__ == '__main__':

    #curl -i -H "Content-Type: application/xml" -vX POST-d @circuitRequest.xml http://84.88.40.146:5000/pathfinder/provisioner

    #controllerIp = "127.0.0.1:8080"

    #midSwitches = defaultdict(list)


    #queues = set_queues_all(controllerIp)
    #smart_flow_pusher(srcAddress, dstAddress, controllerIp, path_h3_h2, midSwitches, 80, queues)
