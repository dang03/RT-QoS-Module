#!/usr/bin/env python
# encoding: utf-8

__author__ = 'Dani'

import os
# Using Flask since Python doesn't have built-in session management
from flask import Flask, session, render_template, jsonify
# Our target library
import requests
import json

app = Flask(__name__)


# Generate a secret random key for the session
app.secret_key = os.urandom(24)


"""
#############
REST service
#############
HTTP Method     URI                     Action
------------    --------------------    -------
index           /pathfinder/
GET             /pathfinder/get_path    Retrieve latest found QoS path
GET             /pathfinder/get_qosDb   Retrieve stored QoS paths
POST            /pathfinder/...         ...
...


"""

# Query last Pathfinder result: returns last QoS path returned
@app.route('/pathfinder/get_path')
def get_path():
    #url = ''
    # example to actually run
    #url = 'https://api.github.com/users/runnable'

    # this issues a GET to the url. replace "get" with "post", "head",
    # "put", "patch"... to make a request using a different method
    #r = requests.get(url)

    if os.path.exists('./path.json'):
        pathRes = open('./path.json', 'r')
        r = pathRes.readlines()
        pathRes.close()
    else:
        r = {}

    return json.dumps(r, indent=4)

# Query qosDb log
@app.route('/pathfinder/get_qosDb')
def get_qosDb():

    if os.path.exists('./qosDb.json'):
        qosDb = open('./qosDb.json', 'r')
        r = qosDb.readlines()
        qosDb.close()
    else:
        r = {}

    return json.dumps(r, indent=4)






@app.route('/pathfinder/run_app')
def run_app():
    """
    url = ''
    # example to actually run
    # url = 'http://httpbin.org/post'

    data = {'a': 10, 'b': [{'c': True, 'd': False}, None]}
    # example of JSON data
    #data = {'a': 10, 'b': [{'c': True, 'd': False}, None]}
    headers = {'Content-Type': 'application/json'}

    r = requests.post(url, data=json.dumps(data), headers=headers)

    return json.dumps(r.json(), indent=4)
    """
    queueString = "sudo python Pathfinder.py"
    result = os.popen(queueString).read()
    return result

# Define a route for the webserver
@app.route('/pathfinder/')
def index():
    #return render_template('index.html')

    json_index = {'Pathfinder REST API Index':{'Methods':[{'get_path': "Query last QoS path returned"}, {'get_qosDb': "Query QoS log returned"}, {'example': "More to be implemented"}]}}

    return jsonify(json_index)




if __name__ == '__main__':
    app.run(
        # host="0.0.0.0",
        #port=int("80")
        debug=True
    )

"""
# testing REST requests
r = requests.get("http://weather.yahooapis.com/forecastrss", params = {"w":"753692", "u":"c"})
if r.status_code == 200:
    print r.text
"""
