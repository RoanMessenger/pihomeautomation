# TEST CONTROLLER
# This tests all the functions of the hardware, messaging system, state system, 
# and settings system found in main.py
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

from datetime import datetime

SECONDS_BETWEEN_TESTS = 4


def init_state():
    return {
        "first_run": True,
        "testing_relay": 1,
        "last_test_time": 0,
        "message": "",
    }


def handle_event(event, inputs, state, settings):
    new_state = dict(state)
    setting_changes = {}
    log_entries = []
    messages = []

    # Listen for time change events (which run once per second)
    if event[0] == 'change' and event[1] == 'timestamp':
        # this will run once, at the beginning
        if state["first_run"]:
            log_entries.append("Initializing test... (if you see this multiples times, something is broken!)")
            log_entries.append("Testing messaging system...")
            log_entries.append("")
            messages.append("Messaging system test.")
            setting_changes['test_setting'] = True
            new_state["first_run"] = False
        elif 'test_setting' not in settings:
            log_entries.append("WARNING: settings are not being saved correctly!!")

        # see if it's time to change to a new relay/alarm
        if event[3] - state["last_test_time"] >= SECONDS_BETWEEN_TESTS:
            # reset timer
            new_state["last_test_time"] = inputs['timestamp']

            # go to next relay / alarm
            new_state["testing_relay"] = state["testing_relay"] + 1
            if new_state["testing_relay"] == 5:
                new_state["testing_relay"] = 1

            # update the message
            if new_state["testing_relay"] != 4:
                new_state["message"] = "Testing Relay " + str(new_state["testing_relay"])
            else:
                new_state["message"] = "Testing Alarm"

        # print status
        log_entries.append("Testing Raspberry PI Home Security System (should repeat every 2s):")
        for inp in inputs:
            log_entries.append('  ' + inp + ': ' + str(inputs[inp]))
        log_entries.append("-----------------------------------------------------")
        log_entries.append("")

    elif event[0] == 'change' and event[1] != 'timestamp' and event[2] is not None:
        new_state["message"] = str(event[1]) + " is now " + str(event[3])

    elif event[0] == 'press':
        new_state["message"] = "Pressed " + str(event[1])

    return new_state, setting_changes, log_entries, messages


def get_outputs(inputs, state, settings):
    outputs = {
        "relay1": False,
        "relay2": False,
        "relay3": False,
        "alarm": False,
        "line1": "",
        "line2": "",
    }

    # turn on relay / alarm
    if state["testing_relay"] != 4:
        outputs['relay' + str(state["testing_relay"])] = True
    else:
        outputs['alarm'] = True

    outputs["line1"] = datetime.utcfromtimestamp(inputs["timestamp"]).strftime('%m/%d %H:%M:%S')
    if len(state["message"]) > 16:
        msg = state["message"]
        msg_words = msg.split()
        line1 = ""
        line2 = ""
        while len(msg_words) > 0 and len(line1) + len(msg_words[-1]) + 1 <= 16:
            line1 += msg_words.pop(0) + " "
        while len(msg_words) > 0:
            line2 += msg_words.pop(0) + " "
        outputs["line1"] = line1
        outputs["line2"] = line2
    else:
        outputs["line2"] = state["message"]

    return outputs
