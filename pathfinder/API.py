#!/usr/bin/env python
# encoding: utf-8

__author__ = 'Dani'


# This REST API is a proof of concept and restful capabilites test for Pathfinder

# Using Flask micro-framework, since Python doesn't have built-in session management

from flask import Flask, jsonify, make_response, request
import flask_restful
import traceback
import json
import os
from pathfinder.Pathfinder import pathfinder_algorithm, pathfinder_algorithm_from_file

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
...


"""

# REQUESTS dispatching
# Query last Pathfinder result: returns last QoS path returned

@app.route('/pathfinder/get_path', methods=['GET'])
def get_path():
    #url = ''
    # example to actually run
    #url = 'https://api.github.com/users/runnable'

    # this issues a GET to the url. replace "get" with "post", "head",
    # "put", "patch"... to make a request using a different method
    #r = requests.get(url)

    if os.path.exists('./pathfinder/path.json'):
        with open('./pathfinder/path.json', 'r') as path:

            res = json.load(path, encoding='utf8')
            path.close()

            res = jsonify(PATH=res)
            return res
    else:
        flask_restful.abort(404)


# Query qos-Db log
@app.route('/pathfinder/get_qos_log', methods=['GET'])
def get_qos_log():
    res = []

    if os.path.exists('./qosDb.json'):
        qosDb = open('./qosDb.json', 'r')
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

    result = pathfinder_algorithm_from_file()

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

    result = pathfinder_algorithm(PFinput)

    #return json.dumps(result, indent=4), 200
    return jsonify(PATH=result), 200



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
             'example': "More to be implemented"}
        ]
    }}

    return jsonify(json_index)




if __name__ == '__main__':
    app.run(
        # host="0.0.0.0",
        #port=int("80")
        debug=False
    )

"""
# testing REST requests
r = requests.get("http://weather.yahooapis.com/forecastrss", params = {"w":"753692", "u":"c"})
if r.status_code == 200:
    print r.text
"""
