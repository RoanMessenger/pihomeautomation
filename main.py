#!/usr/bin/python
import controller
import copy
import test_controller
import sys
import RPi.GPIO as GPIO
import time
# from twilio.rest import Client
from gpiozero import DigitalInputDevice
import Adafruit_DHT
import json
import lcd
import keypad
from w1thermsensor import W1ThermSensor

# INITIAL SETUP ---------------------------------------------------------------------
print("Starting up...")
GPIO.setmode(GPIO.BCM)

# check if we're in testing mode
testing = False
if len(sys.argv) == 2:
    if sys.argv[1] == "test":
        testing = True
cont = test_controller if testing else controller
state = cont.init_state()

# setup DS18B20 external temp sensor
ext_temp_sensor = W1ThermSensor()
ext_temp = None

# load settings
with open('settings.json', 'r') as f:
    settings = json.load(f)

# initialize keypad
KEYPAD = keypad.Keypad(
    settings["keypad_characters"],
    settings["keypad_row_pins"],
    settings["keypad_col_pins"])

# initialize PIR
GPIO.setup(settings["pir_pin"], GPIO.IN)

# initialize twilio
# TWILIO_CLIENT = Client(settings["twilio_account_sid"], settings["twilio_auth_token"])

# initialize gas sensor
GAS_SENSOR = DigitalInputDevice(settings["gas_pin"])

# initialize LCD
LCD = lcd.LCD(
    settings["lcd_rs"],
    settings["lcd_e"],
    settings["lcd_d4"],
    settings["lcd_d5"],
    settings["lcd_d6"],
    settings["lcd_d7"],
    settings["lcd_chr"],
    settings["lcd_cmd"],
    settings["lcd_chars"],
    settings["lcd_line_1"],
    settings["lcd_line_2"])

# initialize relays and alarm
for i in range(1, 4):
    x = "relay" + str(i) + "_pin"
    if x in settings and settings[x] > 0:
        GPIO.setup(settings[x], GPIO.OUT)
        GPIO.output(settings[x], 1)
if "alarm_pin" in settings and settings["alarm_pin"] > 0:
    GPIO.setup(settings["alarm_pin"], GPIO.OUT)
    GPIO.output(settings["alarm_pin"], 1)

# initialize DHT11 sensor
DHT11_TEMP = None
DHT11_HUM = None


# FUNCTIONS -------------------------------------------------------------------------
def is_motion():
    return GPIO.input(settings["pir_pin"]) == 1


def log(m):
    now = '[' + time.strftime("%c") + '] '
    with open('main.log', 'a') as f:
        if not testing:
            f.write(now + m)
        print(now + m)


# def send_message(m):
    # try:
        # TWILIO_CLIENT.messages.create(from_=settings["twilio_from"], to=settings["twilio_to"], body=m)
    # except:
        # log("Error sending message over Twilio!")


def temp_hum_sensor():
    global DHT11_TEMP
    global DHT11_HUM
    t, h = Adafruit_DHT.read(Adafruit_DHT.DHT11, settings["dht_pin"])
    if t is not None and h is not None:
        DHT11_TEMP = t
        DHT11_HUM = h
    return DHT11_TEMP, DHT11_HUM


def gas_sensor():
    return not GAS_SENSOR.value


# MAIN LOOP -------------------------------------------------------------------------
log("Started up.")
if testing:
    log("(testing mode)")
old_inputs = {}
inputs = {}
last_temp_hum_read = 0.0
while True:
    events = []

    # if a key is being pressed, generate an event for it
    keys = KEYPAD.get_keys()
    KEYPAD.clear_keys()
    for key in keys:
        events.append(("press", key))

    # read new inputs if no keys have been pressed
    if len(events) == 0 and time.time() - last_temp_hum_read > settings["temp_hum_period"]:
        temp_hum_sensor()
        ext_temp = ext_temp_sensor.get_temperature()
        last_temp_hum_read = time.time()
    elif len(events) > 0:
        last_temp_hum_read = time.time()

    old_inputs = inputs
    inputs = {
        "temp_inside":         DHT11_TEMP,
        "humidity":            DHT11_HUM,
        "temp_outside":        ext_temp,
        "gas":                 gas_sensor(),
        "motion":              is_motion(),
        "timestamp":           int(time.time())}

    # for each change in inputs, generate event
    for i in inputs:
        if i not in old_inputs:
            events.append(("change", i, None, inputs[i]))
        elif inputs[i] != old_inputs[i]:
            events.append(("change", i, old_inputs[i], inputs[i]))
    for i in old_inputs:
        if i not in inputs:
            events.append(("change", i, old_inputs[i], None))

    # call controller for each event
    for e in events:
        state, setting_changes, log_entries, messages = cont.handle_event(e, inputs, state, copy.deepcopy(settings))

        # handle settings changes
        if len(setting_changes) > 0:
            for setting in setting_changes:
                settings[setting] = setting_changes[setting]
                log('Setting "' + setting + '" changed to ' + str(setting_changes[setting]))
            if not testing:
                with open('settings.json', 'w') as f:
                    json.dump(settings, f, sort_keys=True, indent=4)

        # handle log entries
        for entry in log_entries:
            log(entry)

        # send messages
        # for message in messages:
            # send_message(message)
            # log('Sent message: ' + str(message))

    # write outputs
    outputs = cont.get_outputs(inputs, state, settings)
    LCD.write_both(outputs['line1'], outputs['line2'])
    for i in range(1, 4):
        x = "relay" + str(i) + "_pin"
        y = 0 if outputs["relay" + str(i)] else 1
        if x in settings and settings[x] > 0:
            GPIO.output(settings[x], y)
    a = 0 if outputs["alarm"] else 1
    if "alarm_pin" in settings and settings["alarm_pin"] > 0:
        GPIO.output(settings["alarm_pin"], a)
