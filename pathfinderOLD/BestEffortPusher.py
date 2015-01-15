#!/usr/bin/env python
# encoding: utf-8

__author__ = 'Daniel'

import os
from collections import defaultdict


def flow_pusher(srcAddress, dstAddress, controllerRestIp, path, midSwitches):

    for k, v in path:
        midSwitches[k].append(v)
    print midSwitches


    for midSwitch, midPorts in midSwitches.iteritems():

        print "%s - %s, %s" % (str(midSwitch), str(midPorts[0]), str(midPorts[1]))

        #push midSwitches flowmods
        command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-ip\":\"%s\", \"dst-ip\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"enqueue=%s:0\"}' http://%s/wm/staticflowentrypusher/json" % ((str(midSwitch)), (str(midSwitch))+".f", srcAddress, dstAddress, "0x800", (str(midPorts[0])), (str(midPorts[1])), controllerRestIp)
        result = os.popen(command).read()
        print command

        command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-ip\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"output=%s\"}' http://%s/wm/staticflowentrypusher/json" % ((str(midSwitch)), (str(midSwitch))+".farp", srcAddress, "0x806", (str(midPorts[0])), (str(midPorts[1])), controllerRestIp)
        result = os.popen(command).read()
        print command


        command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-ip\":\"%s\", \"dst-ip\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"enqueue=%s:0\"}' http://%s/wm/staticflowentrypusher/json" % ((str(midSwitch)), (str(midSwitch))+".r", dstAddress, srcAddress, "0x800", (str(midPorts[1])), (str(midPorts[0])), controllerRestIp)
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
        command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-ip\":\"%s\", \"dst-ip\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"enqueue=%s:%s\"}' http://%s/wm/staticflowentrypusher/json" % ((str(midSwitch)), (str(midSwitch))+".f00", srcAddress, dstAddress, "0x800", (str(midPorts[0])), (str(midPorts[1])), (str(queue)), controllerRestIp)
        result = os.popen(command).read()
        print command

        command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-ip\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"output=%s\"}' http://%s/wm/staticflowentrypusher/json" % ((str(midSwitch)), (str(midSwitch))+".f00arp", srcAddress, "0x806", (str(midPorts[0])), (str("all")), controllerRestIp)
        result = os.popen(command).read()
        print command

        command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-ip\":\"%s\", \"dst-ip\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"enqueue=%s:%s\"}' http://%s/wm/staticflowentrypusher/json" % ((str(midSwitch)), (str(midSwitch))+".r00", dstAddress, srcAddress, "0x800", (str(midPorts[1])), (str(midPorts[0])), (str(queue)), controllerRestIp)
        result = os.popen(command).read()
        print command

        command = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"src-ip\":\"%s\", \"ether-type\":\"%s\", \"cookie\":\"0\", \"priority\":\"32768\", \"ingress-port\":\"%s\",\"active\":\"true\", \"actions\":\"output=%s\"}' http://%s/wm/staticflowentrypusher/json" % ((str(midSwitch)), (str(midSwitch))+".r00arp", dstAddress, "0x806", (str(midPorts[1])), (str("all")), controllerRestIp)
        result = os.popen(command).read()
        print command

    return

def set_queue_0():
    # OVS switch Queues Configuration

    queueString = "sudo ovs-vsctl -- set Port s1-eth25 qos=@newqos -- set Port s1-eth26 qos=@newqos -- set Port s1-eth2 qos=@newqos -- set Port s1-eth3 qos=@newqos -- --id=@newqos create QoS type=linux-htb other-config:max-rate=100000000 queues=0=@q0 -- --id=@q0 create Queue other-config:max-rate=100000000"
    qResult = os.popen(queueString).read()
    print queueString
    print qResult

    return

def set_queue_1():
    # OVS switch Queues Configuration

    queueString = "sudo ovs-vsctl -- set Port s2-eth1 qos=@newqos -- set Port s2-eth12 qos=@newqos -- set Port s2-eth3 qos=@newqos -- set Port s1-eth25 qos=@newqos -- set Port s1-eth26 qos=@newqos -- set Port s1-eth2 qos=@newqos -- set Port s1-eth3 qos=@newqos -- --id=@newqos create QoS type=linux-htb other-config:max-rate=100000000 queues=1=@q1 -- --id=@q1 create Queue other-config:min-rate=80000000"
    qResult = os.popen(queueString).read()
    print queueString
    print qResult

    return

def set_queue_2():
    # OVS switch Queues Configuration

    queueString = "sudo ovs-vsctl -- -- set Port s1-eth25 qos=@newqos -- set Port s1-eth26 qos=@newqos -- set Port s1-eth2 qos=@newqos -- set Port s1-eth3 qos=@newqos -- set Port s3-eth1 qos=@newqos -- set Port s3-eth2 qos=@newqos -- set Port s3-eth10 qos=@newqos -- --id=@newqos create QoS type=linux-htb other-config:max-rate=100000000 queues=2=@q2 -- --id=@q2 create Queue other-config:min-rate=20000000"
    qResult = os.popen(queueString).read()
    print queueString
    print qResult

    return



#################################################

if __name__ == '__main__':

    controllerRestIp = "127.0.0.1:8080"

    path_h1_h2 = [("00:00:00:00:00:00:00:01", 3), ("00:00:00:00:00:00:00:01", 4)]
    path_h3_h2 = [("00:00:00:00:00:00:00:02", 3), ("00:00:00:00:00:00:00:02", 1), ("00:00:00:00:00:00:00:01", 1), ("00:00:00:00:00:00:00:01", 4)]
    path_h4_h2 = [("00:00:00:00:00:00:00:03", 3), ("00:00:00:00:00:00:00:03", 1), ("00:00:00:00:00:00:00:01", 2), ("00:00:00:00:00:00:00:01", 4)]

    """
    midSwitches = defaultdict(list)

    srcAddress = "10.0.0.2"
    dstAddress = "10.0.0.3"

    #set_queue_0()

    flow_pusher(srcAddress, dstAddress, controllerRestIp, path_h1_h2, midSwitches)


    midSwitches = defaultdict(list)

    srcAddress = "10.0.0.4"
    dstAddress = "10.0.0.3"

    #set_queue_1()

    flow_pusher_q(srcAddress, dstAddress, controllerRestIp, path_h3_h2, midSwitches, 1)
    """
    midSwitches = defaultdict(list)

    srcAddress = "10.0.0.5"
    dstAddress = "10.0.0.3"

    set_queue_2()

    flow_pusher_q(srcAddress, dstAddress, controllerRestIp, path_h4_h2, midSwitches, 2)
