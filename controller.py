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
import screensaver_controller
import alert_message_controller


def cycle_relay_mode(n):
    def cycle_relay_n_mode(inputs, state, settings):
        key = 'relay' + str(n) + '_mode'
        if key not in settings or settings[key] == 'off':
            return state, {key: 'auto'}
        elif settings[key] == 'auto':
            return state, {key: 'on'}
        else:
            return state, {key: 'off'}
    return cycle_relay_n_mode


def relay_listing(n, settings):
    key = 'relay' + str(n) + '_mode'
    if key not in settings or settings[key] == 'off':
        return "Relay "+str(n)+": OFF"
    elif settings[key] == 'auto':
        return "Relay "+str(n)+": AUTO"
    else:
        return "Relay "+str(n)+": ON"


def main_menu(settings):
    return [
        (relay_listing(1, settings), cycle_relay_mode(1)),
        (relay_listing(2, settings), cycle_relay_mode(2)),
        (relay_listing(3, settings), cycle_relay_mode(3)),
        ("Network Settings", "network_settings"),
        ("Alert Settings", "alert_settings"),
        ("Alarm System", "alarm_system"),
        ("Relay Schedule", "relay_schedule"),
        ("Relay Triggers", "relay_triggers"),
    ]


def alert_menu(settings):
    menu = [("Add Number", "add_number")]
    if "alert_numbers" in settings:
        for alnum in settings['alert_numbers']:
            menu.append((alnum['number'], alnum['number'] + "_settings"))
    return menu


def alarm_time_menu(settings):
    if 'alarm' in settings and 'time_choices' in settings['alarm'] and 'time' in settings['alarm']:
        menu = []
        for tc in settings['alarm']['time_choices']:
            menu.append(('(*) '+tc['name'] if settings['alarm']['time'] == tc['seconds'] else '( ) '+tc['name'],
                         'set_alarm_time_'+str(tc['seconds'])))
        return menu
    else:
        return [("No Choices!", None)]


def format_minutes(m):
    h = m // 60
    m = m % 60
    ampm = "AM" if h < 12 else "PM"
    h = h % 12
    h = 12 if h == 0 else h
    h = str(h)
    m = str(m)
    m = "0"+m if len(m) == 1 else m
    return h+":"+m+ampm


def relay_schedule_menu(rs):
    menu = []
    if 'on_ranges' in rs:
        for i, r in enumerate(rs['on_ranges']):
            menu.append((format_minutes(r['start'])+'-'+format_minutes(r['end']),
                         "relay"+str(rs['relay'])+"_schedule"+str(i)))
    menu.append(("Add On-Range", "relay"+str(rs['relay'])+"_add_range"))
    return menu


def relay_triggers_menu(rt):
    menu = []
    if 'triggers' in rt:
        for i, t in enumerate(rt['triggers']):
            menu.append((t['input']+t['comparison']+str(t['value']),
                "relay"+str(rt['relay'])+"_trigger"+str(i)))
    menu.append(("Add Trigger", "relay"+str(rt['relay'])+"_add_trigger"))
    return menu


def programs(inputs, state, settings):
    progs = {
        "gas_alert": (alert_message_controller, ("Warning:", "GAS DETECTED!")),
        "screensaver": (screensaver_controller, "main_menu"),
        "main_menu": (menu_controller, main_menu(settings)),
        "network_settings": (menu_controller, [
            ("Available Networks", "available_networks"),
            ("Network Status", "network_status"),
        ]),
        "alert_settings": (menu_controller, alert_menu(settings)),
        "alarm_system": (menu_controller, [
            ("Disable Alarm" if settings['alarm']['enabled'] else "Enable Alarm", "toggle_alarm"),
            ("Set Code", "set_alarm_code"),
            ("Grace Period", "alarm_time_choices"),
        ]),
        "alarm_time_choices": (menu_controller, alarm_time_menu(settings)),
        "relay_schedule": (menu_controller, [
            ("Relay One", "relay1_schedule"),
            ("Relay Two", "relay2_schedule"),
            ("Relay Three", "relay3_schedule"),
        ]),
        "relay_triggers": (menu_controller, [
            ("Relay One", "relay1_triggers"),
            ("Relay Two", "relay2_triggers"),
            ("Relay Three", "relay3_triggers"),
        ]),
    }

    # add in relay schedule menus
    if 'relay_schedules' in settings:
        for rs in settings['relay_schedules']:
            progs['relay'+str(rs['relay'])+'_schedule'] = (menu_controller, relay_schedule_menu(rs))

    # add in relay schedule menus
    if 'relay_triggers' in settings:
        for rt in settings['relay_triggers']:
            progs['relay'+str(rt['relay'])+'_triggers'] = (menu_controller, relay_triggers_menu(rt))

    # add in alert settings menus
    if 'alert_numbers' in settings:
        for alnum in settings['alert_numbers']:
            progs[alnum['number'] + '_settings'] = (menu_controller, [
                ("[X] Alarm" if alnum['alarm'] else "[ ] Alarm", alnum['number'] + '_toggle_alarm'),
                ("[X] Gas Sensor" if alnum['gas'] else "[ ] Gas Sensor", alnum['number'] + '_toggle_gas'),
                ("[X] Temp Alert" if alnum['temp'] else "[ ] Temp Alert", alnum['number'] + '_toggle_temp'),
                ("Delete Number", alnum['number'] + '_delete'),
            ])

    return progs


# launch a program
def launch_prog(inputs, state, settings, prog):
    new_state = dict(state)
    if callable(prog):
        # it's a function performing some action
        new_state, setting_changes = prog(inputs, state, settings)
        return new_state, setting_changes
    else:
        progs = programs(inputs, state, settings)
        if prog in progs:
            new_state['stack'].append((prog, progs[prog][0].init_state()))
            return new_state, {}
        else:
            return state, {}


# quit current program
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
        'last_user_input': 0,
        'first_run': True,
    }


# EVENT HANDLER
def handle_event(event, inputs, state, settings):
    new_state = dict(state)
    setting_changes = {}
    log_entries = []
    messages = []
    timed_out = False

    # keep track of menu timeout status
    if event[0] == 'press':
        # user input received, update time
        new_state['last_user_input'] = inputs['timestamp']
    elif event[0] == 'change' and event[1] == 'timestamp' and event[3] - state['last_user_input'] > settings['menu_timeout_seconds']:
        # we have exceeded the menu timeout, we need to clear the stack
        timed_out = True

    # if gas sensor on, push alert onto stack
    if event[0] == 'change' and event[1] == 'gas' and event[3]:
        new_state, _ = launch_prog(inputs, new_state, settings, 'gas_alert')

    # if stack is empty, or we've timed out, clear stack and launch screensaver
    elif len(state['stack']) == 0 or (timed_out and len(state['stack']) > 1):
        # stack empty, launch screen saver
        new_state["stack"] = []
        new_state, _ = launch_prog(inputs, new_state, settings, 'screensaver')

    # HANDLE PROGRAM STACK ---------------------------------------------------------------------------------------------
    frame = new_state['stack'][-1]
    program = programs(inputs, new_state, settings)[frame[0]]
    new_prog_state, setting_changes, log_entries, messages, done, launch =\
        program[0].handle_event(event, inputs, frame[1], settings, program[1])
    new_state['stack'][-1] = (frame[0], new_prog_state)
    if done:
        new_state = quit_active_prog(new_state)
    if launch:
        new_state, other_setting_changes = launch_prog(inputs, new_state, settings, launch)
        setting_changes.update(other_setting_changes)
    # ------------------------------------------------------------------------------------------------------------------

    # keep track of last motion detected and last gas sensor reading times
    if inputs['motion']:
        # motion sensor is active, record this as last time it went off
        setting_changes['last_motion'] = inputs['timestamp']
    if inputs['gas']:
        # gas sensor is active, record this as last time it went off
        setting_changes['last_gas'] = inputs['timestamp']

    # make a note of when we booted
    if state['first_run']:
        setting_changes['running_since'] = inputs['timestamp']
        new_state['first_run'] = False

    return new_state, setting_changes, log_entries, messages


def get_outputs(inputs, state, settings):
    outputs = {
        "relay1": 'relay1_mode' in settings and settings['relay1_mode'] == 'on',
        "relay2": 'relay2_mode' in settings and settings['relay2_mode'] == 'on',
        "relay3": 'relay3_mode' in settings and settings['relay3_mode'] == 'on',
        "alarm": True if 'alarm_active' in settings and settings['alarm_active'] else False,
        "line1": "",
        "line2": "",
    }

    if len(state['stack']) > 0:
        progs = programs(inputs, state, settings)
        frame = state['stack'][-1]
        if frame[0] in progs:
            prog_outputs = progs[frame[0]][0].get_outputs(inputs, frame[1], settings, progs[frame[0]][1])
            outputs["line1"] = prog_outputs["line1"]
            outputs["line2"] = prog_outputs["line2"]
        else:
            outputs["line1"] = "**Invalid"
            outputs["line2"] = "Program**"
    else:
        outputs["line1"] = "**No Active"
        outputs["line2"] = "Program**"

    return outputs
