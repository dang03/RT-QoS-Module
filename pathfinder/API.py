#!/usr/bin/env python
# encoding: utf-8

__author__ = 'Dani'


# This REST API is a proof of concept and restful capabilites test for Pathfinder

# Using Flask micro-framework, since Python doesn't have built-in session management

import traceback
import json
import os

from flask import Flask, jsonify, make_response, request
import flask_restful
from BeautifulSoup import BeautifulSoup

import Pathfinder
import Adapter
import tester

#from pathfinder.Pathfinder import pathfinder_algorithm, pathfinder_algorithm_from_file

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True
api = flask_restful.Api(app)


# Generate a secret random key for the session
app.secret_key = os.urandom(24)


mime_types = {'json_renderer': ('application/json',),
              'xml_renderer': ('application/xml', 'text/xml',
                                'application/x-xml',)}          # xml could be an alternative data format


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)



@app.errorhandler(Exception)
def internal_error(error):
    """
    app.logger.error("Exception:\n" + str())
    """
    message = dict(status=500, message='Internal Server Error: ' + str(traceback.format_exc()))
    resp = jsonify(message)
    resp.status_code = 500

    return make_response(resp, 500)



"""
#############
REST service
#############
HTTP Method     URI                     Action
------------    --------------------    -------
index           /pathfinder/
GET             /pathfinder/get_path    Retrieve latest found QoS path
GET             /pathfinder/get_qos_log Retrieve stored QoS paths
GET, POST       /pathfinder/run_app     Trigger pathfinder to return a QoS path
POST            /pathfinder/run_app2    Send a request to summon pathfinder to return a QoS path
POST            /pathfinder/provisioner Send an XML request to summon pathfinder to return a QoS path

...


"""

# REQUESTS dispatching
# Query last Pathfinder result: returns last QoS path returned

@app.route('/pathfinder/get_path', methods=['GET'])
def get_path():

    if os.path.exists('./path.json'):
        with open('./path.json', 'r') as path:

            res = json.load(path, encoding='utf8')
            path.close()

            res = jsonify(PATH=res)
            return res
    else:
        flask_restful.abort(404)


@app.route('/pathfinder/example', methods=['GET'])
def example():
    res = str(NotImplemented)
    return res


# Query qos-Db log
@app.route('/pathfinder/get_qos_log', methods=['GET'])
def get_qos_log():
    res = []

    if os.path.exists('./pathfinder/qosDb.json'):
        qosDb = open('./pathfinder/qosDb.json', 'r')
        for line in qosDb:
            res.append(json.loads(line))

        qosDb.close()

        return jsonify(LOG=res)
        #return json.dumps(json.JSONDecoder().decode(r))

    else:
        flask_restful.abort(404)


"""
if os.path.exists('./path.json'):
        with open('./path.json', 'r') as path:
            # r = pathRes.readlines()
            res = json.load(path, encoding='utf8')
            path.close()

            res = json_renderer(data=res)
            return res
"""

#@app.route('/pathfinder/run_app', methods=['POST'])
@app.route('/pathfinder/run_app', methods=['GET', 'POST'])
def run_app():
    """
    usage: curl -i -H "Content-Type: application/json" -X POST http://127.0.0.1:5000/pathfinder/run_app
    url = ''
    # example to actually run
    # url = 'http://httpbin.org/post'

    data = {}
    # example of JSON data
    #data = {'a': 10, 'b': [{'c': True, 'd': False}, None]}
    headers = {'Content-Type': 'application/json'}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    return json.dumps(r.json(), indent=4)
    """

    result = Pathfinder.pathfinder_algorithm_from_file()

    return jsonify(PATH=result), 200


@app.route('/pathfinder/run_app2', methods=['POST'])
def run_app2():
    """
    usage:
    curl -i -H "Content-Type: application/json" -X POST -d '{"test":"data"}' http://127.0.0.1:5000/pathfinder/run_app2
    curl -i -H "Content-Type: application/json" -X POST --data-binary @/pathfinder/PFinput.json http://127.0.0.1:5000/pathfinder/run_app2
    curl -i -H "Content-Type: application/json" -vX POST -d @PFinput.json http://127.0.0.1:5000/pathfinder/run_app2
    """

    if not request.json:
        flask_restful.abort(400)

    PFinput = request.json

    result = Pathfinder.pathfinder_algorithm(PFinput)

    #return json.dumps(result, indent=4), 200
    return jsonify(PATH=result), 200


@app.route('/pathfinder/provisioner', methods=['POST'])
def provisioner():
    """
    *NOT DEFINED YET* usage:
    curl -i -H "Content-Type: application/xml" -X POST --data-binary @/pathfinder/circuitRequest.xml http://127.0.0.1:5000/pathfinder/provisioner
    curl -i -H "Content-Type: application/xml" -vX POST -d @circuitRequest.xml http://127.0.0.1:5000/pathfinder/provisioner
    """
    if request.headers['Content-Type'] == 'application/xml':

        #parse data from XML input to python
        parsed_data = BeautifulSoup(request.data)

        #E2E ip addresses and ports
        src_ip = parsed_data.source.address.string
        dst_ip = parsed_data.destination.address.string
        src_port = parsed_data.source.linkport.string #considering
        dst_port = parsed_data.destination.linkport.string #considering

        #label = parsed_data.label.string

        # requested QoS parameters
        max_delay = int(parsed_data.qos_policy.maxlatency.string)
        max_jitter = int(parsed_data.qos_policy.maxjitter.string)
        max_pLoss = int(parsed_data.qos_policy.maxpacketloss.string)
        min_band = int(parsed_data.qos_policy.minthroughput.string)

        #identify the request
        req_id = "FIBRE-test"

        #request input data
        input_data = {"requestID": req_id, "ip-src": src_ip, "ip-dst": dst_ip, "src-port": src_port, "dst-port": dst_port, "bandwidth": min_band, "delay": max_delay, "packet-loss": max_pLoss, "jitter": max_jitter}

        #return jsonify(input_data), 200

        #recover topology file from: manually set or tester.py
        with open('pathfinder/PFinput3.json', 'r') as PFtopo:
           topofile = json.load(PFtopo)
           PFtopo.close()

        adapted_request = Adapter.adapter('localhost:8080', input_data, topofile)

        with open('pathfinder/PFtest.json', 'wb') as PFtester:
            json.dump(adapted_request, PFtester, indent=4)
            PFtester.close()

        print "Adapted request", adapted_request
        #return jsonify(adapted_request), 200

        result = Pathfinder.pathfinder_algorithm(adapted_request)

        with open('pathfinder/path.json', 'wb') as PFpath:
            json.dump(result, PFpath, indent=4)
            PFpath.close()

        tester.forwarder(result, 'localhost:8080')

        #return json.dumps(result, indent=4), 200
        return jsonify(PATH=result), 200



        #return str(src_ip+"\n"+dst_ip+"\n"+src_port+"\n"+dst_port+"\n"+label+"\n"+max_delay+"\n")


    else:
        flask_restful.abort(400)

    #PFinput = circuitRequest.xml

    #result = Pathfinder.pathfinder_algorithm(PFinput)

    #return json.dumps(result, indent=4), 200
    #return jsonify(PATH=result), 200



# Define a route for the webserver
@app.route('/pathfinder/')
def index():
    #return render_template('index.html')

    json_index = {'Pathfinder REST API Index': {
        'Methods': [
            {'get_path': "Query last QoS path returned",
             'get_qos_log': "Query QoS log returned",
             'run_app': "Run Pathfinder for a locally stored QoS request",
             'run_app2': "Mode2 not available through web, only on CLI ",
             'provisioner': "Mode3 not available through web, only on CLI",
             'example': "More to be implemented"}
        ]
    }}

    return jsonify(json_index)




if __name__ == '__main__':
    app.run(
        host="84.88.40.146",
        port=int("5000"),
        debug=False
    )

"""
# testing REST requests
r = requests.get("http://weather.yahooapis.com/forecastrss", params = {"w":"753692", "u":"c"})
if r.status_code == 200:
    print r.text
"""
