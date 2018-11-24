# MENU CONTROLLER
# This creates a menu with a list of menu items, with title and
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
#
# CONTEXT:
# list of 2-tuples: (name, value)
#
# RETURN VALUE:
# None -> do nothing
# str  -> select item
# True -> exit


# COMPUTED VALUES
def render_list_line(l, i, sel):
    if 0 <= i < len(l):
        cursor = '>' if sel else ' '
        number = str(i+1) if i < 10 else ' '
        return number + cursor + l[i][0][:14]
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


def selected_item(state, l):
    if 0 <= state["selection_index"] < len(l):
        return l[state["selection_index"]][1]
    else:
        return None


# MUTATIONS
def go_up(state, l):
    new_state = dict(state)
    new_state["selection_index"] = prev_selection_index(state, l)
    new_state["screen_position"] = updated_screen_position(new_state)
    return new_state


def go_down(state, l):
    new_state = dict(state)
    new_state["selection_index"] = next_selection_index(state, l)
    new_state["screen_position"] = updated_screen_position(new_state)
    return new_state


def go_to(state, l, i):
    new_state = dict(state)
    if 0 <= i < len(l):
        new_state["selection_index"] = i
        new_state["screen_position"] = updated_screen_position(new_state)
        return new_state
    else:
        return state


# INITIAL STATE
def init_state():
    return {
        "selection_index": 0,
        "screen_position": 0,
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
            new_state = go_up(state, context)
        elif key == 'D':
            new_state = go_down(state, context)
        elif key == 'C':
            done = True
        elif key == 'B':
            launch = selected_item(state, context)
        elif str(key).isdigit():
            i = int(key) - 1
            if i == -1:
                i = 9
            if i < len(context):
                new_state = go_to(state, context, i)
                launch = selected_item(state, context)

    return new_state, setting_changes, log_entries, messages, done, launch


def get_outputs(inputs, state, settings, context):
    outputs = {
        "relay1":      False,
        "relay2":      False,
        "relay3":      False,
        "alarm":       False,
        "line1":       "",
        "line2":       "",
    }

    outputs['line1'], outputs['line2'] = render_list(context, state['screen_position'], state['selection_index'])

    return outputs
