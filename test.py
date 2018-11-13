#!/usr/bin/python
import controller
import test_controller
import time
import json
from flask import Flask
from flask_socketio import SocketIO, send
import sys
import os

print("Starting up...")

# check if we're in testing mode
TESTING = False
if len(sys.argv) == 2:
    if sys.argv[1] == "test":
        print("(testing mode)")
        TESTING = True

# load settings
with open('settings.json', 'r') as f:
    SETTINGS = json.load(f)

# load initial outputs
with open('init_outputs.json', 'r') as f:
    OUTPUTS = json.load(f)

inputs = {}

app = Flask(__name__)
socketio = SocketIO(app)


@socketio.on('message')
def handleMessage(msg):
    global inputs, OUTPUTS, SETTINGS, TESTING

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

        if TESTING:
            result = test_controller.handle_event(e, inputs, OUTPUTS, SETTINGS)
        else:
            result = controller.handle_event(e, inputs, OUTPUTS, SETTINGS)
        output_changes, setting_changes, messages, log_entries = result

        # update outputs
        for otp in output_changes:
            OUTPUTS[otp] = output_changes[otp]
            print('Output "' + otp + '" changed to ' + str(output_changes[otp]))

        # send output changes to server
        if len(output_changes) > 0:
            send(OUTPUTS)

        # handle settings changes
        if len(setting_changes) > 0:
            for setting in setting_changes:
                SETTINGS[setting] = setting_changes[setting]
                print('Setting "' + setting + '" changed to ' + str(setting_changes[setting]))

        # handle log entries
        for entry in log_entries:
            print('LOG: ' + entry)

        # send messages
        for message in messages:
            print('Sent message: ' + str(message))


if __name__ == '__main__':
    socketio.run(app)
