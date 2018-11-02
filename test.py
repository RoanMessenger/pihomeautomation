#!/usr/bin/python
import controller
import time
import json


# INITIAL SETUP ---------------------------------------------------------------------
# load settings
with open('settings.json', 'r') as f:
    SETTINGS = json.load(f)

# load initial state
with open('init_state.json', 'r') as f:
    STATE = json.load(f)

# load initial outputs
with open('init_outputs.json', 'r') as f:
    OUTPUTS = json.load(f)


# TESTS -----------------------------------------------------------------------------
inputs = {
    "temp_outside":  None,
    "temp_inside":   None,
    "humidity":      None,
    "gas":           None,
    "motion":        None,
    "keys":          None,
    "timestamp":     None
}

# call controller
output_changes, state_changes, setting_changes, messages, log_entries = controller.controller(inputs, STATE, SETTINGS)
