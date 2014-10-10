#!/usr/bin/env python
# encoding: utf-8



__author__ = 'Dani'

# Import libraries
import os
import argparse
import json
import sys
import Pathfinder
import random
import re
import httplib
import time
from datetime import datetime

delta_sec = 2  # seconds to delay in time.sleep

class mcolors:
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.OKGREEN = ''
        self.FAIL = ''
        self.ENDC = ''



def request_builder(controller):

    # Get all the edges/links
    command = "curl -s http://%s//wm/topology/links/json" % controller
    rtTopo = json.loads((os.popen(command).read()))
    print rtTopo
    print command+"\n"


    for link_d in rtTopo:

                link_d['bandwidth'] = random.randrange(20, 30)
                link_d['delay'] = random.uniform(0.2, 0.8)
                link_d['jitter'] = random.uniform(0.1, 0.4)
                link_d['packet-loss'] = random.randrange(1, 10)



    return rtTopo


# if __name__ == '__main__':

# parse controller address.
# Syntax:
# *FLOODLIGHT* --controller {IP:REST_PORT}
# Usage from CLI, e.g.: python Adapter.py --input request.json

parser = argparse.ArgumentParser(description='Suitable Path Generator')
parser.add_argument('--controller', '-c', dest='controllerRestIp', action='store', default='localhost:8080',
                    help='controller IP:RESTport, e.g., localhost:8080 or A.B.C.D:8080')
parser.add_argument('--file', '-f', dest='topoFile', default=None,
                    help='Optional topology file path, e.g., pathfinder/topoFile.json', metavar='FILE')
args = parser.parse_args()
print args, "\n"

global topofile


# INPUT: First it checks if a local request source file exists, called request.json for testing purposes,
# that will include QoS requirements plus necessary data unavailable from the controller

controllerRestIp = args.controllerRestIp

while True:
    time.sleep(delta_sec)

    topology = request_builder(controllerRestIp)

    """
    testRequest_body = str({"src": {"srcSwitch": "00:00:00:00:00:00:00:05", "srcPort": 3}, "dst": {"dstSwitch": "00:00:00:00:00:00:00:06", "dstPort": 3}, "requestID": "r3qu357", "parameters": { "delay": 0, "bandwidth": 8, "packet-loss": 0, "jitter": 0},)
    testRequest_topo = {"topology": rtTopo}
    """

    print "Creating new request file.\n"
    with open('PFinput3.json', 'wb') as PFtester:
        json.dump(topology, PFtester, indent=4)
        PFtester.close()
