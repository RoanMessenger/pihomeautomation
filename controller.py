# CONTROLLER
# This receives inputs, state, and settings as an input, and produces a set 
# of outputs, state changes, setting changes, messages to be sent, and log
# entries as output
#
# INPUTS:
# external_temps
# temp_inside
# humidity
# gas
# motion
# keys
# timestamp
#
# OUTPUTS:
# line1
# line2
# relay1
# relay2
# relay3
# alarm


def menu():
    return {
        'name': 'Main Menu',
        'submenu': [
            {
                'name': "Toggle Relay 1",
            },
            {
                'name': "Toggle Relay 2",
            },
            {
                'name': "Toggle Relay 3",
            },
            {
                'name': "Network Settings",
                'submenu': [
                    {
                        'name': "Available Networks",
                        'submenu': [
                            {'name': "Test network 1"},
                            {'name': "Test network 2"},
                        ],
                    },
                    {'name': "Network Status"},
                ],
            },
            {
                'name': "Alert Settings",
                'submenu': [
                    {'name': "Add Number"},
                    {'name': "5555554444"},
                    {'name': "5555556666"},
                ],
            },
            {
                'name': "Alarm System",
                'submenu': [
                    {'name': 'Enable'},
                    {'name': 'Set Code'},
                    {
                        'name': 'Alarm Delay',
                        'submenu': [
                            {'name': '10 Seconds'},
                            {'name': '30 Seconds'},
                            {'name': '1 Minute'},
                            {'name': '2 Minutes'},
                        ],
                    }
                ],
            },
            {
                'name': "Relay Schedule",
                'submenu': [
                    {'name': 'Relay 1'},
                    {'name': 'Relay 2'},
                    {'name': 'Relay 3'},
                ],
            },
            {
                'name': "Relay Triggers",
                'submenu': [
                    {'name': 'Relay 1'},
                    {'name': 'Relay 2'},
                    {'name': 'Relay 3'},
                ],
            },
        ],
    }


# COMPUTED VALUES
def render_list_line(l, i, sel):
    if 0 <= i < len(l):
        cursor = '>' if sel else ' '
        number = str(i+1) if i < 10 else ' '
        return number + cursor + l[i]['name'][:14]
    else:
        return ''


def render_list(l, sp, sel):
    if 0 <= sel < len(l) and (0 <= sp < (len(l) - 1) or (sp == 0 and len(l) == 1)):
        return render_list_line(l, sp,  sel == sp),\
               render_list_line(l, sp+1, sel == sp+1)
    else:
        return 'List Error!', ''


def next_selection_index(state, l):
    return (state["selection_index"]+1) % len(l)


def prev_selection_index(state, l):
    return (state["selection_index"]-1) % len(l)


def updated_screen_position(state):
    if state["screen_position"] > state["selection_index"]:
        return state["selection_index"]
    elif state["screen_position"]+1 < state["selection_index"]:
        return state["selection_index"] - 1
    else:
        return state["screen_position"]


def active_item(state):
    context = menu()
    for i in state["path"]:
        if 'submenu' in context and 0 <= i < len(context['submenu']):
            context = context['submenu'][i]
        else:
            return None
    return context


def selected_item(state):
    ai = active_item(state)
    if 'submenu' in ai:
        if 0 <= state["selection_index"] < len(ai['submenu']):
            return ai['submenu'][state["selection_index"]]
        else:
            return None
    else:
        return None


def render_item(state, item):
    if 'submenu' in item:
        return render_list(item['submenu'], state["screen_position"], state["selection_index"])
    else:
        return "Render error", ""


# MUTATIONS
def go_up(state):
    new_state = dict(state)
    ai = active_item(state)
    if 'submenu' in ai:
        new_state["selection_index"] = prev_selection_index(state, ai['submenu'])
        new_state["screen_position"] = updated_screen_position(new_state)
        return new_state
    else:
        return state


def go_down(state):
    new_state = dict(state)
    ai = active_item(state)
    if 'submenu' in ai:
        new_state["selection_index"] = next_selection_index(state, ai['submenu'])
        new_state["screen_position"] = updated_screen_position(new_state)
        return new_state
    else:
        return state


def go_back(state):
    new_state = dict(state)
    if len(state["path"]) > 0:
        new_state["path"] = list(state["path"])
        new_state["path"].pop()
        new_state["selection_index_stack"] = list(state["selection_index_stack"])
        new_state["selection_index"] = new_state["selection_index_stack"].pop()
        new_state["screen_position_stack"] = list(state["screen_position_stack"])
        new_state["screen_position"] = new_state["screen_position_stack"].pop()
        return new_state
    else:
        return state


def enter_selected_item(state):
    new_state = dict(state)
    si = selected_item(state)
    if 'submenu' in si:
        new_state["path"] = list(state["path"])
        new_state["path"].append(state["selection_index"])
        new_state["selection_index_stack"] = list(state["selection_index_stack"])
        new_state["selection_index_stack"].append(state["selection_index"])
        new_state["screen_position_stack"] = list(state["screen_position_stack"])
        new_state["screen_position_stack"].append(state["screen_position"])
        new_state["selection_index"] = 0
        new_state["screen_position"] = 0
        return new_state
    else:
        return state


def enter_item_by_number(state, n):
    new_state = dict(state)
    ai = active_item(state)
    if 'submenu' in ai and 1 <= n <= len(ai['submenu']):
        new_state["selection_index"] = n-1
        new_state["screen_position"] = updated_screen_position(new_state)
        return enter_selected_item(new_state)
    else:
        return state


# INITIAL STATE
def init_state():
    return {
        "selection_index": 0,
        "screen_position": 0,
        "selection_index_stack": [],
        "screen_position_stack": [],
        "path": [],
    }


# EVENT HANDLER
def handle_event(event, inputs, state, settings):
    new_state = dict(state)
    setting_changes = {}
    log_entries = []
    messages = []

    if event[0] == 'press':
        key = event[1]
        if key == 'A':
            new_state = go_up(state)
        elif key == 'D':
            new_state = go_down(state)
        elif key == 'B':
            new_state = enter_selected_item(state)
        elif key == 'C':
            new_state = go_back(state)
        elif str(key).isdigit():
            new_state = enter_item_by_number(state, int(key))

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

    outputs['line1'], outputs['line2'] = render_item(state, active_item(state))

    return outputs
