#!/usr/bin/env python
# encoding: utf-8

"""
Switch-port stats monitoring

"""
__author__ = 'Daniel'

# Import libraries
import os
import sys
import subprocess
import argparse
import time
import datetime
import re
import httplib
import json

localhost = "127.0.0.1"
delta_sec = 2  # seconds to delay in time.sleep
col_print_freq = 10

import sys
import re
import httplib
import json
import time
from datetime import datetime

class RestClient(object):
  def __init__(self, server):
    self.server = server

  def list_port_stats(self, switch):
    self.path = '/wm/core/switch/%s/port/json' % switch
    ret = self.rest_call({}, 'GET', print_ret=False)
    return json.loads(ret[2])[switch]

  def rest_call(self, data, action, print_ret=True):
    headers = {
      'Content-type': 'application/json',
      'Accept': 'application/json',
      }
    body = json.dumps(data)
    conn = httplib.HTTPConnection(self.server, 8080)
    conn.request(action, self.path, body, headers)
    response = conn.getresponse()
    ret = (response.status, response.reason, response.read())
    if print_ret:
      print >>sys.stderr, ret
    conn.close()
    return ret

class PortStat(object):
  def __init__(self, **kw):
    self.collisions = int(kw["collisions"])
    self.receiveBytes = int(kw["receiveBytes"])
    self.receiveCRCErrors = int(kw["receiveCRCErrors"])
    self.receiveDropped = int(kw["receiveDropped"])
    self.receiveErrors = int(kw["receiveErrors"])
    self.receiveFrameErrors = int(kw["receiveFrameErrors"])
    self.receiveOverrunErrors = int(kw["receiveOverrunErrors"])
    self.receivePackets = int(kw["receivePackets"])
    self.transmitBytes = int(kw["transmitBytes"])
    self.transmitDropped = int(kw["transmitDropped"])
    self.transmitErrors = int(kw["transmitErrors"])
    self.transmitPackets = int(kw["transmitPackets"])

def get_port_stats(localhost, dpid, *ports):
  """
  """
  ret = {}
  restc = RestClient(localhost)

  for stat_d in restc.list_port_stats(dpid):
    if stat_d["portNumber"] not in ports:
      continue
    ret[int(stat_d["portNumber"])] = PortStat(**stat_d)
  return ret

def portStatsMonitor():
  """
  if len(sys.argv) < 3:
    print "usage: %s <dpid> <port...>" % sys.argv[0]
    sys.exit(-1)
  dpid = sys.argv[1]
  try:
    ports = map(int, sys.argv[2:])
  except ValueError:
    print "invalid port number(s): %s" % ports
    sys.exit(-1)
  """
  if os.path.exists('./path.json'):
     path_line = open('./path.json', 'r')
     line = path_line.readline()
     path_line.close()
     print "LINES", line

  else:
     print "Invalid path!"
     sys.exit(-1)

  for parsedData in json.loads(line):
     try:
        identifier = parsedData["requestID"]
        print "PATHID: ", identifier

     except:
        dpid = parsedData["switch"]
        ports = []
        ports.append(int(parsedData["port1"]))
        ports.append(int(parsedData["port2"]))

        print dpid, "\n"
        print ports, "\n"


  try:
    l = [get_port_stats(localhost, dpid, *ports), None, ]
    i = 1
    j = 0
    col_title = ("  ").join([k.rjust(7) for k in ["rx_mbps", "rx_pps", "rx_drop", "rx_err", "tx_mbps", "tx_pps", "tx_drop", "tx_err", ]])


    while True:
      time.sleep(delta_sec)
      l[(i%2)] = get_port_stats(localhost, dpid, *ports)
      if not j % col_print_freq:
        # print "-" *22 + "+" + ("-" * 72 + "+") * len(l[i%2].keys())
        print " "*21 + " ".join([("DPID %s" % dpid).center(71)])   #for port in sorted(l[i%2].keys())])
        print " "*21 + (" " + col_title + " ") #* len(l[((i%2)/2)].keys())
        # print "-" *22 + "+" + ("-" * 72 + "+") * len(l[i%2].keys())

      #print " %s " % datetime.today().strftime("%H:%M:%S"),

      for port in sorted(l[i%2].keys()):
        print " %s " % datetime.today().strftime("%H:%M:%S"),
        print "port %s" % port,
        stat = l[i%2][port]
        stat_last = l[(i-1)%2][port]
        mbps_in = (stat.receiveBytes - stat_last.receiveBytes) * 8.0 / delta_sec / 2**20
        pps_in = (stat.receivePackets - stat_last.receivePackets) / delta_sec
        dropped_in = (stat.receiveDropped - stat_last.receiveDropped) / delta_sec
        errors_in = (stat.receiveErrors - stat_last.receiveErrors) / delta_sec
        mbps_out = (stat.transmitBytes - stat_last.transmitBytes) * 8.0 / delta_sec / 2**20
        pps_out = (stat.transmitPackets - stat_last.transmitPackets) / delta_sec
        dropped_out = (stat.transmitDropped - stat_last.transmitDropped) / delta_sec
        errors_out = (stat.transmitErrors - stat_last.transmitErrors) / delta_sec
        #if mbps_out > 15.0:
            #print "QoS Violation Detected"
        print "%8.1f %8d %8d %8d %8.1f %8d %8d %8d" % (mbps_in, pps_in, dropped_in, errors_in, mbps_out, pps_out, dropped_out, errors_out)+"\n",
      print " "
      sys.stdout.flush()
      i += 1
      j += 1
  except (KeyboardInterrupt, SystemExit):
    sys.exit(0)

if __name__ == '__main__':
  portStatsMonitor()
