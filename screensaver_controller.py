# SCREENSAVER CONTROLLER
# This creates series of screens showing the state of the system which rotate automatically
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
# str -> program to run when any key is pressed

from datetime import datetime


def next_screen_index(i):
    return (i+1) % 6


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
        "line1":       datetime.fromtimestamp(inputs["timestamp"]).strftime('%m/%d %I:%M:%S%p'),
        "line2":       "",
    }
    last_gas = "Never"
    last_motion = "Never"
    running_since = "Unknown"
    if 'last_gas' in settings:
        last_gas = datetime.fromtimestamp(settings["last_gas"]).strftime('%m/%d %I:%M:%S%p')
    if 'last_motion' in settings:
        last_motion = datetime.fromtimestamp(settings["last_motion"]).strftime('%m/%d %I:%M:%S%p')
    if 'running_since' in settings:
        running_since = datetime.fromtimestamp(settings["running_since"]).strftime('%m/%d %I:%M:%S%p')

    if state['screen_index'] == 0:
        outputs['line2'] = "Temp Inside: " + str(inputs['temp_inside'])
    elif state['screen_index'] == 1:
        outputs['line2'] = "Temp Outside: " + str(inputs['temp_outside'])
    elif state['screen_index'] == 2:
        outputs['line2'] = "Humidity: " + str(inputs['humidity'])
    elif state['screen_index'] == 3:
        outputs['line1'] = "Last Gas Sensor:"
        outputs['line2'] = last_gas
    elif state['screen_index'] == 4:
        outputs['line1'] = "Last Motion:"
        outputs['line2'] = last_motion
    elif state['screen_index'] == 5:
        outputs['line1'] = "Running Since:"
        outputs['line2'] = running_since

    return outputs
