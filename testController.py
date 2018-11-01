### TEST CONTROLLER ###
# This tests all the functions of the hardware, messaging system, state system, 
# and settings system found in main.py

# INPUTS:
# temp_outside
# temp_inside
# humidity
# gas
# motion
# keys
# timestamp

# OUTPUTS:
# line1
# line2
# relay1
# relay2
# relay3
# relay4

def controller(inputs, state, settings):
    outputs         = {}
    stateChanges    = {}
    settingChanges  = {}
    messages        = []
    logEntries      = []

    if not 'testing_timer' in state or not 'test_setting' in settings or not 'testing_relay' in state:
        logEntries.push("Initializing test... (if you see this multiples times, something is broken!)")
        logEntires.push("Testing messaging system...")
        messages.push("Messaging system test.")
        settingChanges['test_setting'] = True
        stateChanges['testing_timer']  = inputs['timestamp']
        stateChanges['testing_relay']  = 1
    
    elif inputs['timestamp'] - state['testing_timer'] > 2.0:
        stateChanges['testing_timer'] = inputs['timestamp']
        logEntries.push("")
        logEntries.push("Testing Raspberry PI Home Security System (should repeat every 2s):")

        logEntires.push("INPUTS:")
        for inp in inputs:
            logEntires.push('  ' + inp + ': ' + inputs[inp])

        outputs['line1']  = 'Testing Relay ' + state['testing_relay']
        outputs['line2']  = '' + inputs['timestamp']
        outputs['relay1'] = False
        outputs['relay2'] = False
        outputs['relay3'] = False
        outputs['relay4'] = False
        outputs['relay' + state['testing_relay']] = True
        stateChanges['testing_relay'] = state['testing_relay'] + 1
        if stateChanges['testing_relay'] == 5:
            stateChanges['testing_relay'] = 1

        logEntires.push("OUTPUTS:")
        for otp in outputs:
            logEntires.push('  ' + otp + ': ' + outputs[otp])
        
        logEntries.push("-----------------------------------------------------")

    return (outputs, stateChanges, settingChanges, messages, logEntries)

