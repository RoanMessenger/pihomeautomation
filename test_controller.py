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
# alarm

from datetime import datetime

SECONDS_BETWEEN_TESTS = 4

first_run = True
testing_relay = 1
last_test_time = 0
testing_print_cycle = False


def handle_event(event, inputs, outputs, settings):
    global testing_relay, last_test_time, testing_print_cycle, first_run
    output_changes = {}
    setting_changes = {}
    messages = []
    log_entries = []

    # Listen for time change events (which run once per second)
    if event[0] == 'change' and event[1] == 'timestamp' and event[3] - last_test_time >= SECONDS_BETWEEN_TESTS:
        # this will run once, at the beginning
        if first_run:
            log_entries.append("Initializing test... (if you see this multiples times, something is broken!)")
            log_entries.append("Testing messaging system...")
            log_entries.append("")
            messages.append("Messaging system test.")
            setting_changes['test_setting'] = True
            first_run = False
        elif 'test_setting' not in settings:
            log_entries.append("WARNING: settings are not being saved correctly!!")

        # reset timer
        last_test_time = inputs['timestamp']

        # turn off last relay / alarm
        if testing_relay != 4:
            output_changes['relay' + str(testing_relay)] = False
        else:
            output_changes['alarm'] = False

        # go to next relay / alarm
        testing_relay += 1
        if testing_relay == 5:
            testing_relay = 1

        # turn on next relay / alarm
        if testing_relay != 4:
            output_changes['relay' + str(testing_relay)] = True
        else:
            output_changes['alarm'] = True

        # update screen output
        output_changes["line1"] = datetime.utcfromtimestamp(inputs["timestamp"]).strftime('%m/%d %H:%M:%S')
        if testing_relay != 4:
            output_changes["line2"] = "Testing Relay " + str(testing_relay)
        else:
            output_changes["line2"] = "Testing Alarm"

        # print status
        log_entries.append("Testing Raspberry PI Home Security System (should repeat every 2s):")
        for inp in inputs:
            log_entries.append('  ' + inp + ': ' + str(inputs[inp]))
        log_entries.append("-----------------------------------------------------")
        log_entries.append("")

    elif event[0] == 'change' and event[1] != 'timestamp' and event[2] is not None:
        output_changes["line1"] = str(event[1])
        output_changes["line2"] = "Changed To " + str(event[3])

    elif event[0] == 'press':
        output_changes["line2"] = "Pressed " + str(event[1])

    return output_changes, setting_changes, messages, log_entries

