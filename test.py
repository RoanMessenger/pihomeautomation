#!/usr/bin/python
import controller
import time
import json
from flask import Flask
from flask_socketio import SocketIO, send

# load settings
with open('settings.json', 'r') as f:
    SETTINGS = json.load(f)

# load initial state
with open('init_state.json', 'r') as f:
    STATE = json.load(f)

# load initial outputs
with open('init_outputs.json', 'r') as f:
    OUTPUTS = json.load(f)

inputs = {
    'pressed_key': None,
    'motion': False,
    'gas': False,
    'temp_inside': 0.0,
    'temp_outside': 0.0,
    'humidity': 0.0,
}

app = Flask(__name__)
socketio = SocketIO(app)


@socketio.on('message')
def handleMessage(msg):
    global pressed_key, inputs
    if isinstance(msg, dict):
        for i in msg:
            print(i + ': ' + str(msg[i]))
            inputs[i] = msg[i]
    else:
        print('Pressed ' + str(msg))
        inputs['pressed_key'] = msg


if __name__ == '__main__':
    socketio.run(app)


while True:
    # read inputs
    inputs['timestamp'] = time.time()

    # call controller
    result = controller.controller(inputs, OUTPUTS, STATE, SETTINGS)
    output_changes, state_changes, setting_changes, messages, log_entries = result

    # update outputs
    for otp in output_changes:
        OUTPUTS[otp] = output_changes[otp]
        print('Output "' + otp + '" changed to ' + str(output_changes[otp]))

    # update state
    for param in state_changes:
        STATE[param] = state_changes[param]
        print('Parameter "' + param + '" changed to ' + str(state_changes[param]))

    # handle settings changes
    if len(setting_changes) > 0:
        for setting in setting_changes:
            SETTINGS[setting] = setting_changes[setting]
            print('Setting "' + setting + '" changed to ' + str(setting_changes[setting]))

    # handle log entries
    for entry in log_entries:
        print(entry)

    # send messages
    for message in messages:
        print('Sent message: ' + str(message))

