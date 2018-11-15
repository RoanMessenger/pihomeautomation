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


# STATE:
selection_index = 0
screen_position = 0
selection_index_stack = []
screen_position_stack = []
path = []


# COMPUTED VALUES
def render_list_line(l, i, sel):
    if 0 <= i < len(l):
        cursor = '>' if sel else ' '
        number = str(i+1) if i < 10 else ' '
        return number + cursor + l[i]['name'][:14]
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


def active_item():
    global path
    context = menu()
    for i in path:
        if 'submenu' in context and 0 <= i < len(context['submenu']):
            context = context['submenu'][i]
        else:
            return None
    return context


def selected_item():
    global selection_index
    ai = active_item()
    if 'submenu' in ai:
        if 0 <= selection_index < len(ai['submenu']):
            return ai['submenu'][selection_index]
        else:
            return None
    else:
        return None


def render_item(item):
    if 'submenu' in item:
        return render_list(item['submenu'])
    elif 'renderer' in item:
        return item['renderer']()
    else:
        return "Render error", ""


# MUTATIONS
def go_up():
    global selection_index, screen_position
    ai = active_item()
    if 'submenu' in ai:
        selection_index = prev_selection_index(ai['submenu'])
        screen_position = updated_screen_position(ai['submenu'])


def go_down():
    global selection_index, screen_position
    ai = active_item()
    if 'submenu' in ai:
        selection_index = next_selection_index(ai['submenu'])
        screen_position = updated_screen_position(ai['submenu'])


def go_back():
    global path, selection_index, screen_position
    if len(path) > 0:
        path.pop()
        selection_index = selection_index_stack.pop()
        screen_position = screen_position_stack.pop()


def enter_selected_item():
    global path, selection_index, screen_position
    si = selected_item()
    if 'submenu' in si or 'renderer' in si:
        path.append(selection_index)
        selection_index_stack.append(selection_index)
        screen_position_stack.append(screen_position)
        selection_index = 0
        screen_position = 0
    if 'action' in si:
        si['action']()


def enter_item_by_number(n):
    global selection_index, screen_position
    ai = active_item()
    if 'submenu' in ai and 1 <= n <= len(ai['submenu']):
        selection_index = n-1
        screen_position = updated_screen_position(ai['submenu'])
        enter_selected_item()


# EVENT HANDLER
def handle_event(event, inputs, outputs, settings):
    global selection_index, screen_position
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
            enter_selected_item()
        elif key == 'C':
            go_back()
        elif str(key).isdigit():
            enter_item_by_number(int(key))

    output_changes['line1'], output_changes['line2'] = render_item(active_item())

    return output_changes, setting_changes, messages, log_entries

