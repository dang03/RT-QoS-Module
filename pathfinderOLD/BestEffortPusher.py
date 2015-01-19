#!/usr/bin/env python
# encoding: utf-8

__author__ = 'Daniel'

import os
import json
import random
from collections import defaultdict


def flow_pusher(srcAddress, dstAddress, controllerRestIp, path, midSwitches):

    for k, v in path:
        midSwitches[k].append(v)
    print midSwitches


    for midSwitch, midPorts in midSwitches.iteritems():

        print "%s - %s, %s" % (str(midSwitch), str(midPorts[0]), str(midPorts[1]))

        #push midSwitches flowmods
        command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-ip\":\"%s\", \"dst-ip\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"output=%s\"}' http://%s/wm/staticflowentrypusher/json" % ((str(midSwitch)), (str(midSwitch))+".f", srcAddress, dstAddress, "0x800", (str(midPorts[0])), (str(midPorts[1])), controllerRestIp)
        result = os.popen(command).read()
        print command

        command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-ip\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"output=%s\"}' http://%s/wm/staticflowentrypusher/json" % ((str(midSwitch)), (str(midSwitch))+".farp", srcAddress, "0x806", (str(midPorts[0])), (str(midPorts[1])), controllerRestIp)
        result = os.popen(command).read()
        print command


        command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-ip\":\"%s\", \"dst-ip\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"output=%s\"}' http://%s/wm/staticflowentrypusher/json" % ((str(midSwitch)), (str(midSwitch))+".r", dstAddress, srcAddress, "0x800", (str(midPorts[1])), (str(midPorts[0])), controllerRestIp)
        result = os.popen(command).read()
        print command

        command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-ip\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"output=%s\"}' http://%s/wm/staticflowentrypusher/json" % ((str(midSwitch)), (str(midSwitch))+".rarp", dstAddress, "0x806", (str(midPorts[1])), (str(midPorts[0])), controllerRestIp)
        result = os.popen(command).read()
        print command

    return

def flow_pusher_q(srcAddress, dstAddress, controllerRestIp, path, midSwitches, queue):

    for k, v in path:
        print k, v
        midSwitches[k].append(v)
    print "result", midSwitches


    for midSwitch, midPorts in midSwitches.iteritems():

        print "%s - %s, %s" % (str(midSwitch), str(midPorts[0]), str(midPorts[1]))

        #push midSwitches flowmods
        command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-ip\":\"%s\", \"dst-ip\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"enqueue=%s:%s\"}' http://%s/wm/staticflowentrypusher/json" % ((str(midSwitch)), str(random.randrange(0, 1000))+(str(midSwitch))+".f", srcAddress, dstAddress, "0x800", (str(midPorts[0])), (str(midPorts[1])), (str(queue)), controllerRestIp)
        result = os.popen(command).read()
        print command

        command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-ip\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"output=%s\"}' http://%s/wm/staticflowentrypusher/json" % ((str(midSwitch)), str(random.randrange(0, 1000))+(str(midSwitch))+".farp", srcAddress, "0x806", (str(midPorts[0])), (str("all")), controllerRestIp)
        result = os.popen(command).read()
        print command

        command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-ip\":\"%s\", \"dst-ip\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"enqueue=%s:%s\"}' http://%s/wm/staticflowentrypusher/json" % ((str(midSwitch)), str(random.randrange(0, 1000))+(str(midSwitch))+".r", dstAddress, srcAddress, "0x800", (str(midPorts[1])), (str(midPorts[0])), (str(queue)), controllerRestIp)
        result = os.popen(command).read()
        print command

        command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-ip\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"output=%s\"}' http://%s/wm/staticflowentrypusher/json" % ((str(midSwitch)), str(random.randrange(0, 1000))+(str(midSwitch))+".rarp", dstAddress, "0x806", (str(midPorts[1])), (str("all")), controllerRestIp)
        result = os.popen(command).read()
        print command

    return

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

def set_queues():
    # OVS switch Queues Configuration

    queueString = "sudo ovs-vsctl -- set Port s1-eth25 qos=@newqos -- set Port s1-eth26 qos=@newqos -- set Port s1-eth2 qos=@newqos -- set Port s1-eth3 qos=@newqos -- set Port s2-eth1 qos=@newqos -- set Port s2-eth12 qos=@newqos -- set Port s2-eth3 qos=@newqos -- set Port s1-eth3 qos=@newqos -- set Port s3-eth1 qos=@newqos -- set Port s3-eth2 qos=@newqos -- set Port s3-eth10 qos=@newqos" \
                  " -- --id=@newqos create QoS type=linux-htb other-config:max-rate=100000000 queues=0=@q0,1=@q1,2=@q2 -- --id=@q0 create Queue other-config:max-rate=100000000 other-config:priority=1 -- --id=@q1 create Queue other-config:min-rate=50000000 other-config:priority=8 -- --id=@q2 create Queue other-config:min-rate=20000000 other-config:priority=8"
    qResult = os.popen(queueString).read()
    print queueString
    print qResult

    return

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
            configString += " --id=@q%s create Queue other-config:min-rate=%s other-config:priority=%s" % (x, min_rate1, priority1)
            key = "q%s" % x
            queuesDict[key] = "%s" % min_rate1
        elif x == 2:
            configString += " --id=@q%s create Queue other-config:min-rate=%s other-config:priority=%s" % (x, min_rate2, priority2)
            key = "q%s" % x
            queuesDict[key] = "%s" % min_rate2
        elif x == 3:
            configString += " --id=@q%s create Queue other-config:min-rate=%s other-config:priority=%s" % (x, min_rate3, priority3)
            key = "q%s" % x
            queuesDict[key] = "%s" % min_rate3
        elif x == 4:
            configString += " --id=@q%s create Queue other-config:min-rate=%s other-config:priority=%s" % (x, min_rate4, priority4)
            key = "q%s" % x
            queuesDict[key] = "%s" % min_rate4
        elif x == 5:
            configString += " --id=@q%s create Queue other-config:min-rate=%s other-config:priority=%s" % (x, min_rate5, priority5)
            key = "q%s" % x
            queuesDict[key] = "%s" % min_rate5
        elif x == 6:
            configString += " --id=@q%s create Queue other-config:min-rate=%s other-config:priority=%s" % (x, min_rate6, priority6)
            key = "q%s" % x
            queuesDict[key] = "%s" % min_rate6
        elif x == 7:
            configString += " --id=@q%s create Queue other-config:min-rate=%s other-config:priority=%s" % (x, min_rate7, priority7)
            key = "q%s" % x
            queuesDict[key] = "%s" % min_rate7
        else:
            raise IOError

    print "config string:", configString

    queueString = "sudo ovs-vsctl%s" % configString
    #qResult = os.popen(queueString).read()
    print "queue string:", queueString
    #print "qResult:", qResult
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

def smart_flow_pusher(srcAddress, dstAddress, controllerRestIp, path, midSwitches, request, queueDict):

    for k, v in path:
        print k, v
        midSwitches[k].append(v)
    print "result", midSwitches
    q = []
    qname = queue_selector(request, queueDict)
    q[:1] = qname
    for midSwitch, midPorts in midSwitches.iteritems():

        print "%s - %s, %s" % (str(midSwitch), str(midPorts[0]), str(midPorts[1]))

        #push midSwitches flowmods
        command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-ip\":\"%s\", \"dst-ip\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"enqueue=%s:%s\"}' http://%s/wm/staticflowentrypusher/json" % ((str(midSwitch)), str(random.randrange(0, 1000))+(str(midSwitch))+".f", srcAddress, dstAddress, "0x800", (str(midPorts[0])), (str(midPorts[1])), (str(q[1])), controllerRestIp)
        result = os.popen(command).read()
        print command

        command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-ip\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"output=%s\"}' http://%s/wm/staticflowentrypusher/json" % ((str(midSwitch)), str(random.randrange(0, 1000))+(str(midSwitch))+".farp", srcAddress, "0x806", (str(midPorts[0])), (str("all")), controllerRestIp)
        result = os.popen(command).read()
        print command

        command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-ip\":\"%s\", \"dst-ip\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"enqueue=%s:%s\"}' http://%s/wm/staticflowentrypusher/json" % ((str(midSwitch)), str(random.randrange(0, 1000))+(str(midSwitch))+".r", dstAddress, srcAddress, "0x800", (str(midPorts[1])), (str(midPorts[0])), (str(q[1])), controllerRestIp)
        result = os.popen(command).read()
        print command

        command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-ip\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"output=%s\"}' http://%s/wm/staticflowentrypusher/json" % ((str(midSwitch)), str(random.randrange(0, 1000))+(str(midSwitch))+".rarp", dstAddress, "0x806", (str(midPorts[1])), (str("all")), controllerRestIp)
        result = os.popen(command).read()
        print command

    return

def set_queue_0():
    # OVS switch Queues Configuration

    queueString = "sudo ovs-vsctl -- set Port s1-eth25 qos=@newqos -- set Port s1-eth26 qos=@newqos -- set Port s1-eth2 qos=@newqos -- set Port s1-eth3 qos=@newqos -- --id=@newqos create QoS type=linux-htb other-config:max-rate=100000000 queues=0=@q0 -- --id=@q0 create Queue other-config:max-rate=100000000 other-config:priority=1"
    qResult = os.popen(queueString).read()
    print queueString
    print qResult

    return

def set_queue_1():
    # OVS switch Queues Configuration

    queueString = "sudo ovs-vsctl -- set Port s2-eth1 qos=@newqos -- set Port s2-eth12 qos=@newqos -- set Port s2-eth3 qos=@newqos -- set Port s1-eth25 qos=@newqos -- set Port s1-eth26 qos=@newqos -- set Port s1-eth2 qos=@newqos -- set Port s1-eth3 qos=@newqos -- --id=@newqos create QoS type=linux-htb other-config:max-rate=100000000 queues=1=@q1 -- --id=@q1 create Queue other-config:min-rate=50000000 other-config:priority=8"
    qResult = os.popen(queueString).read()
    print queueString
    print qResult

    return

def set_queue_2():
    # OVS switch Queues Configuration

    queueString = "sudo ovs-vsctl -- -- set Port s1-eth25 qos=@newqos -- set Port s1-eth26 qos=@newqos -- set Port s1-eth2 qos=@newqos -- set Port s1-eth3 qos=@newqos -- set Port s3-eth1 qos=@newqos -- set Port s3-eth2 qos=@newqos -- set Port s3-eth10 qos=@newqos -- --id=@newqos create QoS type=linux-htb other-config:max-rate=100000000 queues=2=@q2 -- --id=@q2 create Queue other-config:min-rate=20000000 other-config:priority=8"
    qResult = os.popen(queueString).read()
    print queueString
    print qResult

    return


########################################################################################


if __name__ == '__main__':

    # curl -i -H "Content-Type: application/xml" -vX POST-d @circuitRequest.xml http://84.88.40.146:5000/pathfinder/provisioner

    controllerIp = "127.0.0.1:8080"

    path_h1_h2 = [("00:00:00:00:00:00:00:01", 3), ("00:00:00:00:00:00:00:01", 4)]
    path_h3_h2 = [("00:00:00:00:00:00:00:02", 3), ("00:00:00:00:00:00:00:02", 1), ("00:00:00:00:00:00:00:01", 1), ("00:00:00:00:00:00:00:01", 4)]
    path_h4_h2 = [("00:00:00:00:00:00:00:03", 3), ("00:00:00:00:00:00:00:03", 1), ("00:00:00:00:00:00:00:01", 2), ("00:00:00:00:00:00:00:01", 4)]

    """
    set_queues()

    midSwitches = defaultdict(list)

    srcAddress = "10.0.0.2"
    dstAddress = "10.0.0.3"

    #set_queue_0()

    flow_pusher(srcAddress, dstAddress, controllerIp, path_h1_h2, midSwitches)


    midSwitches = defaultdict(list)

    srcAddress = "10.0.0.4"
    dstAddress = "10.0.0.3"

    #set_queue_1()

    flow_pusher_q(srcAddress, dstAddress, controllerIp, path_h3_h2, midSwitches, 1)
    """

    midSwitches = defaultdict(list)

    srcAddress = "10.0.0.5"
    dstAddress = "10.0.0.3"

    #set_queue_2()

    #flow_pusher_q(srcAddress, dstAddress, controllerIp, path_h4_h2, midSwitches, 2)

    queues = set_queues_all(controllerIp)
    smart_flow_pusher(srcAddress, dstAddress, controllerIp, path_h3_h2, midSwitches, 80, queues)
