#!/usr/bin/python
import controller
import time
import json


# INITIAL SETUP ---------------------------------------------------------------------
# load settings
with open('settings.json', 'r') as f:
    SETTINGS = json.load(f)

# load initial state
with open('initState.json', 'r') as f:
    STATE = json.load(f)


# TESTS -----------------------------------------------------------------------------
inputs = {}
inputs["temp_outside"] = nil
inputs["temp_inside"]  = nil
inputs["humidity"]     = nil
inputs["gas"]          = nil
inputs["motion"]       = nil
inputs["keys"]         = nil
inputs["timestamp"]    = nil

# call controller
result = controller.controller(inputs, STATE, SETTINGS)
outputs         = result[0]
stateChanges    = result[1]
settingChanges  = result[2]
messages        = result[3]
logEntries      = result[4]

