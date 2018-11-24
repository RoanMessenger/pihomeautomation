# CONTROLLER
# This receives inputs, state, and settings as an input, and produces a set 
# of outputs, state changes, setting changes, messages to be sent, and log
# entries as output
#
# INPUTS:
# external_temp_count
# external_temp_1, 2, 3...
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

import menu_controller


def programs(inputs, state, settings):
    return {
        "main_menu": (menu_controller, [
            ("Toggle Relay One", None),
            ("Toggle Relay Two", None),
            ("Toggle Relay Three", None),
            ("Network Settings", "netset"),
            ("Alert Settings", None),
            ("Alarm System", None),
            ("Relay Schedule", None),
            ("Relay Triggers", None),
        ]),
        "netset": (menu_controller, [
            ("Available Networks", None),
            ("Network Status", None),
        ]),
    }


#launch a program
def launch_prog(inputs, state, settings, prog):
    new_state = dict(state)
    progs = programs(inputs, state, settings)
    if prog in progs:
        new_state['stack'].append((prog, progs[prog][0].init_state()))
        return new_state
    else:
        return state


#quit current program
def quit_active_prog(state):
    new_state = dict(state)
    if len(state['stack']) > 0:
        new_state['stack'].pop()
        return new_state
    else:
        return state


# INITIAL STATE
def init_state():
    return {
        'stack': [],
    }


# EVENT HANDLER
def handle_event(event, inputs, state, settings):
    new_state = dict(state)
    setting_changes = {}
    log_entries = []
    messages = []
    print(state)

    if len(state['stack']) == 0:
        #stack empty, launch main menu
        new_state = launch_prog(inputs, state, settings, 'main_menu')
    else:
        frame = state['stack'][-1]
        program = programs(inputs, state, settings)[frame[0]]
        new_prog_state, settings_changes, log_entries, messages, done, launch =\
            program[0].handle_event(event, inputs, frame[1], settings, program[1])
        new_state['stack'][-1] = (frame[0], new_prog_state)
        if done:
            new_state = quit_active_prog(state)
        if launch:
            new_state = launch_prog(inputs, state, settings, launch)

    return new_state, setting_changes, log_entries, messages


def get_outputs(inputs, state, settings):
    if len(state['stack']) > 0:
        progs = programs(inputs, state, settings)
        frame = state['stack'][-1]
        if frame[0] in progs:
            return progs[frame[0]][0].get_outputs(inputs, frame[1], settings, progs[frame[0]][1])
        else:
            return {
                "relay1": False,
                "relay2": False,
                "relay3": False,
                "alarm": False,
                "line1": "**Invalid",
                "line2": "Program**",
            }
    else:
        return {
            "relay1": False,
            "relay2": False,
            "relay3": False,
            "alarm": False,
            "line1": "**No Active",
            "line2": "Program**",
        }
