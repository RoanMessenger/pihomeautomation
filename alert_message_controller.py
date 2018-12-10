# ALERT MESSAGE CONTROLLER
# This creates a warning message and activates the buzzer or alarm, which can be dismissed by pressing any key
#
# INPUTS:
# temp_inside
# humidity
# gas
# motion
# timestamp
#
# OUTPUTS:
# line1
# line2
# relay1
# relay2
# relay3
# alarm
#
# CONTEXT:
# str -> message to display

from datetime import datetime


# INITIAL STATE
def init_state():
    return { }


# EVENT HANDLER
def handle_event(event, inputs, state, settings, context):
    new_state = dict(state)
    setting_changes = {}
    log_entries = []
    messages = []
    done = False
    launch = None

    if event[0] == 'press':
        # launch the main menu if any key is pressed
        done = True

    return new_state, setting_changes, log_entries, messages, done, launch


def get_outputs(inputs, state, settings, context):
    outputs = {
        "relay1":      False,
        "relay2":      False,
        "relay3":      False,
        "alarm":       True,
        "line1":       "Warning!",
        "line2":       context
    }

    return outputs
