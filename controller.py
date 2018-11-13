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


def handle_event(event, inputs, outputs, settings):
    output_changes = {}
    setting_changes = {}
    messages = []
    log_entries = []

    # TODO: write controller

    return output_changes, setting_changes, messages, log_entries

