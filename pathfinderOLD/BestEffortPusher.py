#!/usr/bin/env python
# encoding: utf-8

__author__ = 'Daniel'

import os
from collections import defaultdict

srcAddress = "10.0.0.3"
dstAddress = "10.0.0.4"
controllerRestIp = "127.0.0.1:8080"

path = [("00:00:00:00:00:00:00:07", 3), ("00:00:00:00:00:00:00:07", 2), ("00:00:00:00:00:00:00:08", 1), ("00:00:00:00:00:00:00:08", 3)]
midSwitches = defaultdict(list)

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

"""
queueString = "sudo ovs-vsctl -- set Port s7-eth2 qos=@newqos -- set Port s7-eth3 qos=@newqos -- set Port s8-eth3 qos=@newqos -- set Port s8-eth1 qos=@newqos -- --id=@newqos create QoS type=linux-htb other-config:max-rate=10000000 queues=0=@q0,1=@q1 -- --id=@q0 create Queue other-config:max-rate=5000000 -- --id=@q1 create Queue other-config:min-rate=8000000"
qResult = os.popen(queueString).read()
print queueString
print qResult
"""
