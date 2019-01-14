# PROMPT CONTROLLER
# This creates a prompt asking the user for input, executing programs or actions on key presses
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
# {
#    "text": "Ask question",
#    "choices": [
#        ('Name', None || 'program_name' || action_function)
#    ]
# }


# INITIAL STATE
def init_state():
    return {
        "start_time": None
    }


# EVENT HANDLER
def handle_event(event, inputs, state, settings, context):
    new_state = dict(state)
    setting_changes = {}
    log_entries = []
    messages = []
    done = False
    launch = None

    if state["start_time"] is None:
        new_state["start_time"] = int(inputs["timestamp"])

    if event[0] == 'press' and str(event[1]).isdigit():
        n = int(event[1])
        if len(context["choices"]) >= n:
            action = context["choices"][n-1][1]
            done = True
            launch = action

    return new_state, setting_changes, log_entries, messages, done, launch


def get_outputs(inputs, state, settings, context):
    line2_full = ""
    for i in range(len(context['choices'])):
        line2_full += str(i+1) + ':' + str(context['choices'][i][0]) + '  '
    if state["start_time"] is not None:
        offset1 = ((int(inputs["timestamp"]) - state["start_time"]) * 5) % len(context["text"])
        offset2 = ((int(inputs["timestamp"]) - state["start_time"]) * 5) % len(line2_full)
    else:
        offset1 = 0
        offset2 = 0

    line1_offset = (context["text"] + '  ' + context['text'])[offset1:offset1+16]
    line2_offset = (line2_full + line2_full)[offset2:offset2+16]

    return {
        "line1": line1_offset if len(context["text"]) > 16 else context["text"],
        "line2": line2_offset if len(line2_full) > 16 else line2_full
    }
