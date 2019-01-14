# ENTER TIME CONTROLLER
# This allows a user to enter a time of the day, in hours, minutes, and AM/PM
#
# INPUTS:
# temp_inside
# temp_outside
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
# action(start_in_minutes, end_in_minutes) -> function(inputs, state, settings) -> new_state, setting_changes


def time_in_minutes(t):
    hour = t["hour"]
    minute = t["minute"]
    pm = t["pm"]

    hour = hour % 12 + (12 if pm else 0)

    return 60 * hour + minute


# INITIAL STATE
def init_state():
    return {
        "start": {
            "hour": 12,
            "minute": 0,
            "pm": False,
        },
        "end": {
            "hour": 12,
            "minute": 0,
            "pm": False,
        },
        "start_selected": True,
        "selected": "hour"
    }


# EVENT HANDLER
def handle_event(event, inputs, state, settings, context):
    new_state = dict(state)
    setting_changes = {}
    log_entries = []
    messages = []
    done = False
    launch = None

    if event[0] == 'press':
        key = event[1]
        if key == 'A':
            if state["selected"] == "hour":
                new_state["start_selected"] = not state["start_selected"]
                new_state["selected"] = "pm"
            elif state["selected"] == "minute":
                new_state["selected"] = "hour"
            else:
                new_state["selected"] = "minute"
        elif key == 'D':
            if state["selected"] == "hour":
                new_state["selected"] = "minute"
            elif state["selected"] == "minute":
                new_state["selected"] = "pm"
            else:
                new_state["start_selected"] = not state["start_selected"]
                new_state["selected"] = "hour"
        elif key == 'C':
            done = True
        elif key == 'B':
            done = True
            launch = context(time_in_minutes(state["start"]), time_in_minutes(state["end"]))
        elif str(key).isdigit():
            tname = "start" if state["start_selected"] else "end"
            if state["selected"] == "pm":
                new_state[tname]["pm"] = int(key) > 1
            else:
                val = state[tname][state["selected"]]
                new_val_concat = int(str(val) + str(key))
                new_val_concat_valid = False
                if state["selected"] == "hour" and 1 <= new_val_concat <= 12:
                    new_val_concat_valid = True
                elif state["selected"] == "minute" and 0 <= new_val_concat < 60:
                    new_val_concat_valid = True
                if new_val_concat_valid:
                    new_state[tname][state["selected"]] = new_val_concat
                elif int(key) > 0:
                    new_state[tname][state["selected"]] = int(key)

    return new_state, setting_changes, log_entries, messages, done, launch


def get_outputs(inputs, state, settings, context):
    t = state["start"] if state["start_selected"] else state["end"]
    hour = t["hour"]
    minute = t["minute"]
    pm = t["pm"]

    hour = ' ' + str(hour) if len(str(hour)) == 1 else str(hour)
    minute = '0' + str(minute) if len(str(minute)) == 1 else str(minute)

    if state["selected"] == "hour":
        line2 = "[" + str(hour) + "]: " + str(minute) + "  " + ("PM" if pm else "AM") + " "
    elif state["selected"] == "minute":
        line2 = " " + str(hour) + " :[" + str(minute) + "] " + ("PM" if pm else "AM") + " "
    else:
        line2 = " " + str(hour) + " : " + str(minute) + " [" + ("PM" if pm else "AM") + "]"

    return {
        "line1": "On between..." if state["start_selected"] else "...and",
        "line2": line2 + "->" if state["start_selected"] else "->" + line2
    }
