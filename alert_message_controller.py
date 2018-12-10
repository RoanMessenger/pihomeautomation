# ALERT MESSAGE CONTROLLER
# This creates a message on the screen, along with an alarm which can be dismissed by any key
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
#
# CONTEXT:
# (str, str) -> lines 1 and 2 of message to display


# INITIAL STATE
def init_state():
    return {
        "first_run": True,
        "old_relay_mode": None,
    }


# EVENT HANDLER
def handle_event(event, inputs, state, settings, context):
    new_state = dict(state)
    setting_changes = {}
    log_entries = []
    messages = []
    done = False
    launch = None

    if state["first_run"]:
        new_state["first_run"] = False
        new_state["old_relay_mode"] = settings["relay2_mode"]
        setting_changes["relay2_mode"] = "on"

    elif event[0] == 'press':
        # launch the main menu if any key is pressed
        setting_changes["relay2_mode"] = state["old_relay_mode"]
        done = True

    return new_state, setting_changes, log_entries, messages, done, launch


def get_outputs(inputs, state, settings, context):
    outputs = {
        "line1":       context[0],
        "line2":       context[1]
    }

    return outputs
