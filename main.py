#!/usr/bin/python
import controller
import test_controller
import sys
import RPi.GPIO as GPIO
from max6675 import MAX6675, MAX6675Error
import time
from twilio.rest import Client 
from gpiozero import DigitalInputDevice
import Adafruit_DHT
import json
import lcd
import keypad


# INITIAL SETUP ---------------------------------------------------------------------
print("Starting up...")
# check if we're in testing mode
TESTING = False
if len(sys.argv) == 2:
    if sys.argv[1] == "test":
        TESTING = True

# load settings
with open('settings.json', 'r') as f:
    SETTINGS = json.load(f)

# load initial state
with open('init_state.json', 'r') as f:
    STATE = json.load(f)

# load initial outputs
with open('init_outputs.json', 'r') as f:
    OUTPUTS = json.load(f)

# reset all GPIO
GPIO.cleanup()

# initialize keypad
KEYPAD = keypad.Keypad(
    SETTINGS["keypad_characters"],
    SETTINGS["keypad_row_pins"],
    SETTINGS["keypad_col_pins"])

# initialize PIR
GPIO.setup(SETTINGS["pir_pin"], GPIO.IN)

# initialize thermocouple
THERMOCOUPLE = MAX6675(
    SETTINGS["max6675_cs_pin"],
    SETTINGS["max6675_clock_pin"],
    SETTINGS["max6675_data_pin"],
    SETTINGS["max6675_units"])

# initialize twilio
TWILIO_CLIENT = Client(SETTINGS["twilio_account_sid"], SETTINGS["twilio_auth_token"])

# initialize gas sensor
GAS_SENSOR = DigitalInputDevice(SETTINGS["gas_pin"])

# initialize LCD
LCD = lcd.LCD(
    SETTINGS["lcd_rs"],
    SETTINGS["lcd_e"],
    SETTINGS["lcd_d4"],
    SETTINGS["lcd_d5"],
    SETTINGS["lcd_d6"],
    SETTINGS["lcd_d7"],
    SETTINGS["lcd_chr"],
    SETTINGS["lcd_cmd"],
    SETTINGS["lcd_chars"],
    SETTINGS["lcd_line_1"],
    SETTINGS["lcd_line_2"])

# initialize relays
for i in range(1, 5):
    x = "relay" + str(i) + "_pin"
    if x in SETTINGS and SETTINGS[x] > 0:
        GPIO.setup(SETTINGS[x], GPIO.OUT)
        GPIO.output(SETTINGS[x], 1)


# FUNCTIONS -------------------------------------------------------------------------
def max6675_temp():
    temp = THERMOCOUPLE.get()
    return temp


def is_motion():
    return GPIO.input(SETTINGS["pir_pin"])


def log(message):
    now = '[' + time.strftime("%c") + '] '
    with open('main.log', 'a') as f:
        if not TESTING:
            f.write(now + message)
        print(now + message)


def send_message(message):
    try:
        TWILIO_CLIENT.messages.create(from_=SETTINGS["twilio_from"], to=SETTINGS["twilio_to"], body=message)
    except:
        log("Error sending message over Twilio!")


def temp_hum_sensor():
    return Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, SETTINGS["dht_pin"])


def gas_sensor():
    return not GAS_SENSOR.value


# MAIN LOOP -------------------------------------------------------------------------
log("Started up.")
if TESTING:
    log("(testing mode)")

while True:
    # read inputs
    temphum = temp_hum_sensor()
    inputs = {
        "temp_outside":  max6675_temp(),
        "temp_inside":   temphum[1],
        "humidity":      temphum[0],
        "gas":           gas_sensor(),
        "motion":        is_motion(),
        "keys":          KEYPAD.get_keys(),
        "timestamp":     time.time()}
    KEYPAD.clear_keys()

    # call controller
    result = None
    if TESTING:
        result = test_controller.controller(inputs, OUTPUTS, STATE, SETTINGS)
    else:
        result = controller.controller(inputs, OUTPUTS, STATE, SETTINGS)
    output_changes, state_changes, setting_changes, messages, log_entries = result

    # update outputs
    for otp in output_changes:
        OUTPUTS[otp] = output_changes[otp]
        log('Output "' + otp + '" changed to ' + str(output_changes[otp]))

    # write outputs
    LCD.write_both(OUTPUTS['line1'], OUTPUTS['line2'])
    for i in range(1, 5):
        x = "relay" + str(i) + "_pin"
        y = 0 if OUTPUTS["relay" + str(i)] else 1
        if x in SETTINGS and SETTINGS[x] > 0:
            GPIO.output(SETTINGS[x], y)

    # update state
    for param in state_changes:
        STATE[param] = state_changes[param]
        log('Parameter "' + param + '" changed to ' + str(state_changes[param]))

    # handle settings changes
    if len(setting_changes) > 0:
        for setting in setting_changes:
            SETTINGS[setting] = setting_changes[setting]
            log('Setting "' + setting + '" changed to ' + str(setting_changes[setting]))
        if not TESTING:
            with open('settings.json', 'r') as f:
                json.dump(SETTINGS, sort_keys=True, indent=4)

    # handle log entries
    for entry in log_entries:
        log(entry)

    # send messages
    for message in messages:
        send_message(message)
        log('Sent message: ' + str(message))

