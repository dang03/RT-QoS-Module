# Application's Main files: These files are required
Adapter.py
API.py
MCP.py
PathDrawer.py
Pathfinder.py
setup.py

# INFO:
Pathfinder module is divided into three main Python files (Adapter.py, API.py, Pathfinder.py)
plus other critical functions python files (PathDrawer.py, MCP.py).
Pathfinder module requires the next input files: request.json and topology.json
Input files provided may be used as examples.


Adapter.py: Gathers input data from Floodlight SDN Controller, request.json and topology.json to
build a QoS Request that API.py and Pathfinder.py can understand.
Usage: 'python Adapter.py -r request.json -t topology.json'


API.py: Exposes a web service to call Pathfinder.py and provides basic functionalities to
send a QoS Request(PFinput.json) and retrieve a path(path.json)
Usage: 'curl -i -H "Content-Type: application/json" -X POST -d '{"test":"data"}' http://127.0.0.1:5000/pathfinder/run_app2'
       'curl -i -H "Content-Type: application/json" -X POST --data-binary @/pathfinder/PFinput.json http://127.0.0.1:5000/pathfinder/run_app2'
       'curl -i -H "Content-Type: application/json" -vX POST -d @PFinput.json http://127.0.0.1:5000/pathfinder/run_app2'


Pathfinder.py: Main algorithm that requires an input request file (PFinput.json) that returns
a port-swith-port style end-to-end path. It also supports edge style end-to-end path (see code to enable).
Usage: python Pathfnder.py (It will require a PFinput.json file on the same module folder)