#!/usr/bin/python
import controller
import copy
import test_controller
import time
import json
from flask import Flask
from flask_socketio import SocketIO, send
import sys
import os
import webbrowser

print("Starting up...")

# check if we're in testing mode
testing = False
if len(sys.argv) == 2:
    if sys.argv[1] == "test":
        print("(testing mode)")
        testing = True

# load settings
with open('settings.json', 'r') as f:
    settings = json.load(f)

inputs = {}
cont = test_controller if testing else controller
state = cont.init_state()

app = Flask(__name__)
socketio = SocketIO(app)


# serve client
@app.route("/")
def index():
    with open('test.html', 'r') as f:
        return f.read()


@socketio.on('message')
def handle_message(msg):
    global inputs, state, settings, testing

    # generate event(s)
    events = []
    if isinstance(msg, dict):
        for i in msg:
            if i not in inputs:
                events.append(("change", i, None, msg[i]))
            elif msg[i] != inputs[i]:
                events.append(("change", i, inputs[i], msg[i]))
        inputs = msg
    else:
        events.append(("press", msg))

    # call controller for each event
    for e in events:
        print('EVENT: ' + str(e))

        state, setting_changes, log_entries, messages = cont.handle_event(e, inputs, state, copy.deepcopy(settings))

        # handle settings changes
        if len(setting_changes) > 0:
            for setting in setting_changes:
                settings[setting] = setting_changes[setting]
                print('Setting "' + setting + '" changed to ' + str(setting_changes[setting]))

        # handle log entries
        for entry in log_entries:
            print('LOG: ' + entry)

        # send messages
        for message in messages:
            send(message)
            print('Sent message: ' + str(message))

    # send output changes to server
    send(cont.get_outputs(inputs, state, settings))


# open web browser to test client
# webbrowser.open('http://127.0.0.1:5000')
print("Navigate to http://127.0.0.1:5000/ to access testing interface.")

# start server
if __name__ == '__main__':
    socketio.run(app)
