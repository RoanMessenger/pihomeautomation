# TEST CONTROLLER
# This tests all the functions of the hardware, messaging system, state system, 
# and settings system found in main.py
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
# relay4


def controller(inputs, outputs, state, settings):
    output_changes = {}
    state_changes = {}
    setting_changes = {}
    messages = []
    log_entries = []

    # this will run once, at the beginning
    if 'testing_timer' not in state or 'test_setting' not in settings or 'testing_relay' not in state:
        log_entries.push("Initializing test... (if you see this multiples times, something is broken!)")
        log_entries.push("Testing messaging system...")
        messages.push("Messaging system test.")
        setting_changes['test_setting'] = True
        state_changes['testing_timer'] = inputs['timestamp']
        state_changes['testing_print_cycle'] = False
        state_changes['testing_relay'] = 1
    
    # this will run every 2 seconds
    elif inputs['timestamp'] - state['testing_timer'] > 2.0:
        state_changes['testing_timer'] = inputs['timestamp']
        output_changes['relay' + state_changes['testing_relay']] = False
        state_changes['testing_relay'] = state['testing_relay'] + 1
        if state_changes['testing_relay'] == 5:
            state_changes['testing_relay'] = 1
        output_changes['relay' + state_changes['testing_relay']] = True
        state_changes['testing_print_cycle'] = True

    # this will run the next cycle after the one above
    elif state['testing_print_cycle']:
        state_changes['testing_print_cycle'] = False
        log_entries.push("")
        log_entries.push("Testing Raspberry PI Home Security System (should repeat every 2s):")
        log_entries.push("INPUTS:")
        for inp in inputs:
            log_entries.push('  ' + inp + ': ' + inputs[inp])
        log_entries.push("OUTPUTS:")
        for otp in outputs:
            log_entries.push('  ' + otp + ': ' + outputs[otp])
        log_entries.push("-----------------------------------------------------")
        log_entries.push("")

    return output_changes, state_changes, setting_changes, messages, log_entries

