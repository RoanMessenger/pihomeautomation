# SCREENSAVER CONTROLLER
# This creates series of screens showing the state of the system which rotate automatically
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
# str -> program to run when any key is pressed

from datetime import datetime


def next_screen_index(i):
    return (i+1) % 5


# INITIAL STATE
def init_state():
    return {
        "screen_index": -1,
        "last_change": 0,
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
        # launch the main menu if any key is pressed
        launch = context
    elif event[0] == 'change' and event[1] == 'timestamp':
        # the time changed, check if we need to flip to next screen
        duration = 3
        if 'screensaver_duration' in settings:
            duration = settings['screensaver_duration']
        else:
            setting_changes['screensaver_duration'] = duration
        t = event[3]
        if t - state['last_change'] >= duration:
            new_state['last_change'] = t
            new_state['screen_index'] = next_screen_index(state['screen_index'])

    return new_state, setting_changes, log_entries, messages, done, launch


def get_outputs(inputs, state, settings, context):
    outputs = {
        "relay1":      False,
        "relay2":      False,
        "relay3":      False,
        "alarm":       False,
        "line1":       datetime.utcfromtimestamp(inputs["timestamp"]).strftime('%m/%d %H:%M:%S'),
        "line2":       "",
    }
    last_gas = "Never"
    last_motion = "Never"
    running_since = "Unknown"
    if 'last_gas' in settings:
        last_gas = datetime.utcfromtimestamp(settings["last_gas"]).strftime('%m/%d %H:%M:%S')
    if 'last_motion' in settings:
        last_motion = datetime.utcfromtimestamp(settings["last_motion"]).strftime('%m/%d %H:%M:%S')
    if 'running_since' in settings:
        running_since = datetime.utcfromtimestamp(settings["running_since"]).strftime('%m/%d %H:%M:%S')

    if state['screen_index'] == 0:
        outputs['line1'] = "Last Gas Sensor:"
        outputs['line2'] = last_gas
    elif state['screen_index'] == 1:
        outputs['line1'] = "Last Motion:"
        outputs['line2'] = last_motion
    elif state['screen_index'] == 2:
        outputs['line1'] = "Running Since:"
        outputs['line2'] = running_since
    elif state['screen_index'] == 3:
        outputs['line2'] = "Temp Inside: " + str(inputs['temp_inside'])
    elif state['screen_index'] == 4:
        outputs['line2'] = "Humidity: " + str(inputs['humidity'])

    return outputs
