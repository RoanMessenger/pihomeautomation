# CONTROLLER
# This receives inputs, state, and settings as an input, and produces a set 
# of outputs, state changes, setting changes, messages to be sent, and log
# entries as output
#
# INPUTS:
# temp_outside
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


MENU = {
    "Toggle Relay 1": None,
    "Toggle Relay 2": None,
    "Toggle Relay 3": None,
    "Network Settings": {
        "Available Networks": [
            "Chris's Network",
            "nickerson1",
        ],
        "Network Status": None,
    },
    "Alert Settings": [
        "Add Number",
        "9026353140",
        "9026246256",
    ],
    "Alarm System": {
        'Enable': None,
        'Set Code': None,
        'Alarm Delay': [
            '10 Seconds',
            '30 Seconds',
            '1 Minute',
            '2 Minutes',
        ],
    },
    "Relay Schedule": [
        'Relay 1',
        'Relay 2',
        'Relay 3',
    ],
    "Relay Triggers": [
        'Relay 1',
        'Relay 2',
        'Relay 3',
    ],
}

# STATE:
selection_index = 0
screen_position = 0
selection_index_stack = []
screen_position_stack = []
path = []
first_render = True


# COMPUTED VALUES
def render_list_line(l, i, sel):
    if 0 <= i < len(l):
        cursor = '>' if sel else ' '
        number = str(i+1) if i < 10 else ' '
        return number + cursor + l[i][:14]
    else:
        return ''


def render_list(l):
    global selection_index, screen_position
    if 0 <= selection_index < len(l) and (0 <= screen_position < (len(l) - 1) or (screen_position == 0 and len(l) == 1)):
        return render_list_line(l, screen_position, selection_index == screen_position),\
               render_list_line(l, screen_position+1, selection_index == screen_position+1)
    else:
        return 'List Error!', ''


def next_selection_index(l):
    global selection_index
    return (selection_index+1) % len(l)


def prev_selection_index(l):
    global selection_index
    return (selection_index-1) % len(l)


def updated_screen_position(l):
    global selection_index, screen_position
    if screen_position > selection_index:
        return selection_index
    elif screen_position+1 < selection_index:
        return selection_index - 1
    else:
        return screen_position


def active_menu():
    global MENU, path
    context = MENU
    for item in path:
        if item in context:
            context = context[item]
        else:
            return []
    return context


def active_menu_list():
    am = active_menu()
    if type(am) is list:
        return am
    elif type(am) is dict:
        return list(am.keys())


def selected_item():
    global selection_index
    aml = active_menu_list()
    if 0 <= selection_index < len(aml):
        return aml[selection_index]
    else:
        return None


def selected_submenu():
    am = active_menu()
    if type(am) is list:
        return None
    elif selected_item() in am:
        return am[selected_item()]
    else:
        return None


# MUTATIONS
def go_up():
    global selection_index, screen_position
    selection_index = prev_selection_index(active_menu_list())
    screen_position = updated_screen_position(active_menu_list())


def go_down():
    global selection_index, screen_position
    selection_index = next_selection_index(active_menu_list())
    screen_position = updated_screen_position(active_menu_list())


def go_back():
    global path, selection_index, screen_position
    if len(path) > 0:
        path.pop()
        selection_index = selection_index_stack.pop()
        screen_position = screen_position_stack.pop()


def enter_submenu():
    global path, selection_index, screen_position
    if selected_submenu() and selected_item():
        path.append(selected_item())
        selection_index_stack.append(selection_index)
        screen_position_stack.append(screen_position)
        selection_index = 0
        screen_position = 0


# EVENT HANDLER
def handle_event(event, inputs, outputs, settings):
    global selection_index, screen_position, MENU, first_render
    output_changes = {}
    setting_changes = {}
    messages = []
    log_entries = []

    if event[0] == 'press':
        key = event[1]
        if key == 'A':
            go_up()
        elif key == 'D':
            go_down()
        elif key == 'B':
            enter_submenu()
        elif key == 'C':
            go_back()

    output_changes['line1'], output_changes['line2'] = render_list(active_menu_list())

    return output_changes, setting_changes, messages, log_entries

