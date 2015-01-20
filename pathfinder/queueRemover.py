#!/usr/bin/env python
# encoding: utf-8

"""
Queue management: control of ovs-vsctl configured interface QoS and port Queues.

"""
__author__ = 'Daniel'

# Import libraries
import os
import io
import subprocess
import argparse
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from networkx.readwrite import json_graph
import json
import datetime
import time
import sys
from fractions import Fraction
from collections import defaultdict


def find_all(a_str, sub_str):
    start = 0
    b_starts = []
    while True:
        start = a_str.find(sub_str, start)
        if start == -1: return b_starts
        b_starts.append(start)
        start += 1

"""
qos = find_all(qResult, "uuid")
print qos
"""



def delete_qos(uuid):
    with open('./queueDb.txt') as queueDb:
        print uuid
        for line in queueDb:
            print line
            if uuid in line:
                command = "sudo ovs-vsctl destroy QoS %s" % uuid
                quResult = (os.popen(command).read())
                print command+"\n"
                print quResult
                queueDb.close()
                sys.exit()

    print "No QoS found"
    queueDb.close()
    sys.exit()


def delete_queue(quuid):
    with open('./queueDb.txt') as queueDb:
        print quuid
        for line in queueDb:
            print line
            if quuid in line:
                command = "sudo ovs-vsctl destroy Queue %s" % quuid
                quResult = (os.popen(command).read())
                print command+"\n"
                print quResult
                queueDb.close()
                sys.exit()

    print "No Queue found"
    queueDb.close()
    sys.exit()

def delete_queues():
    print "Removing OVS stored policies and queues:"
    with open('./queueDb.txt') as queueDb:
        for line in queueDb:
            print line
            command = "sudo ovs-vsctl destroy QoS %s" % line
            quResult = (os.popen(command).read())
            print command+"\n"
            print quResult
            command = "sudo ovs-vsctl destroy Queue %s" % line
            quResult = (os.popen(command).read())
            print command+"\n"
            print quResult

    wipe = []
    newCache = open('./queueDb.txt', 'w')
    newCache.writelines(wipe)
    print "Done"
    queueDb.close()
    newCache.close()


def wipe_queues():
    print "Removing all OVS QoS and queues:"
    qResult = 1
    while qResult != "":
        command = "sudo ovs-vsctl list QoS | grep \"_uuid\" | awk '{ print $3 }'"
        qResult = os.popen(command).read()
        print "command", command+"\n"
        print "qResult", qResult

        command = "sudo ovs-vsctl destroy QoS %s" % qResult
        quResult = (os.popen(command).read())
        print command+"\n"
        print quResult

    quResult = 1
    while quResult != "":
        command = "sudo ovs-vsctl list Queue | grep \"_uuid\" | awk '{ print $3 }'"
        quResult = (os.popen(command).read())

        #parsedResult = json.loads(result)
        print command+"\n"
        print "RESUL", quResult

        command = "sudo ovs-vsctl destroy Queue %s" % quResult
        quResult2 = (os.popen(command).read())
        print quResult2

    wipe = []
    newCache = open('./queueDb.txt', 'w')
    newCache.writelines(wipe)
    newCache.close()
    print "Done"

"""
qosPolicies = open('./qosDb.json', 'a')
qosidenti = {'uuid': qResult}
str = json.dumps(qosidenti)
qosPolicies.write(str+"\n")
"""

"""
# Queue removing example
to_delete = "0ccbc148-6886-41cb-87f0-f4a7cdcbe456"
delete_qos(to_delete)
delete_queue(to_delete)
"""

print "Waiting to clear... "
#delete_queues()
cap = 8
for x in xrange(cap):
    wipe_queues()
    x += 1

print "Flow rules... "
command = "sudo curl -s http://127.0.0.1:8080/wm/staticflowentrypusher/clear/all/json"
result = os.popen(command).read()
print command+"\n"
print result+"\n"+"Done"
print "Mininet topology... "
command = "sudo mn -c"
result = os.popen(command).read()
print command+"\n"
print result+"\n"+"Done"
