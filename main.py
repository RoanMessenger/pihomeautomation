#!/usr/bin/python
import controller
import rpi_gpio
import RPi.GPIO as GPIO
from max6675 import MAX6675, MAX6675Error
import time
from twilio.rest import Client 
from gpiozero import DigitalInputDevice
import Adafruit_DHT
import json


# INITIAL SETUP ---------------------------------------------------------------------
log("Initializing...")

# load settings
with open('settings.json', 'r') as f:
    SETTINGS = json.load(f)

# load initial state
with open('initState.json', 'r') as f:
    STATE = json.load(f)

# reset all GPIO
GPIO.cleanup() #reset all GPIO

# initialize keypad
FACTORY = rpi_gpio.KeypadFactory()
KEYPAD = factory.create_keypad(keypad=SETTINGS["keypad_characters"], row_pins=SETTINGS["keypad_row_pins"], col_pins=SETTINGS["keypad_col_pins"])
PRESSED_KEYS = []
KEYPAD.registerKeyPressHandler(handleKey)

# initialize PIR
GPIO.setmode(GPIO.BOARD) #Set GPIO to pin numbering
GPIO.setup(SETTINGS["pir_pin"], GPIO.IN) #Setup GPIO pin PIR as input

# initialize LCD
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM) # Use BCM GPIO numbers
GPIO.setup(SETTINGS["lcd_e"], GPIO.OUT) # Set GPIO's to output mode
GPIO.setup(SETTINGS["lcd_rs"], GPIO.OUT)
GPIO.setup(SETTINGS["lcd_d4"], GPIO.OUT)
GPIO.setup(SETTINGS["lcd_d5"], GPIO.OUT)
GPIO.setup(SETTINGS["lcd_d6"], GPIO.OUT)
GPIO.setup(SETTINGS["lcd_d7"], GPIO.OUT)
lcd_init()

# initialize thermocouple
THERMOCOUPLE = MAX6675(SETTINGS["max6675_cs_pin"], SETTINGS["max6675_clock_pin"], SETTINGS["max6675_data_pin"], SETTINGS["max6675_units"])

# initialize twilio
TWILIO_CLIENT = Client(SETTINGS["twilio_account_sid"], SETTINGS["twilio_auth_token"])

# initialize gas sensor
GAS_SENSOR = DigitalInputDevice(SETTINGS["gas_pin"])

# TODO: initialize relay inputs


# MAIN LOOP -------------------------------------------------------------------------
log("Starting main loop...")
while True:
    # read inputs
    temphum = temptempHumSensor()
    inputs = {}
    inputs["temp_outside"] = max6675Temp()
    inputs["temp_inside"]  = temphum[1]
    inputs["humidity"]     = temphum[0]
    inputs["gas"]          = gasSensor()
    inputs["motion"]       = isMotion()
    inputs["keys"]         = PRESSED_KEYS
    PRESSED_KEYS = []

    # call controller
    result = controller.controller(STATE, SETTINGS, inputs)
    newState        = result[0]
    outputs         = result[1]
    settingsChanges = result[2]
    messages        = result[3]

    # write outputs
    if 'messages' in outputs:
        for message in outputs['messagesToSend']:
            sendMessage(message)
    writeToScreen(outputs['line1'], outputs['line2'])
    setRelay(1, outputs['relay1']);
    setRelay(2, outputs['relay2']);
    setRelay(3, outputs['relay3']);
    setRelay(4, outputs['relay4']);

    # set state to newState
    STATE = newState

    # handle settings changes
    if len(settingsChanges) > 0:
        for setting in settingsChanges:
            SETTINGS[setting] = settingsChanges[setting]
            log(setting + ' changed to ' + settingsChanges[setting])
        with open('settings.json', 'r') as f:
            json.dump(SETTINGS, sort_keys=True, indent=4)

    # handle log messages
    for message in messages:
        log(message)


# FUNCTIONS -------------------------------------------------------------------------
def handleKey(key):
    PRESSED_KEYS.push(key)

def setRelay(num, value):
    # TODO: implement setting relays
    return
    
def max6675Temp():
    temp = THERMOCOUPLE.get()
    THERMOCOUPLE.cleanup()
    return temp

def isMotion():
    return GPIO.input(SETTINGS["pir_pin"])

def writeToScreen(line1, line2):
    lcd_text(line1,SETTINGS["lcd_line_1"])
    lcd_text(line2,SETTINGS["lcd_line_2"])

def log(message):
    now = '[' + time.strftime("%c") + '] '
    with open('main.log', 'a') as f:
        f.write(now + message)
        print(now + message)

def sendMessage(message):
    message = client.messages.create(from_='', to='', body =message) 

def tempHumSensor():
    return Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, DHTPIN)

def gasSensor():
    return not gas.value

# Initialize and clear display
def lcd_init():
	lcd_write(0x33,LCD_CMD) # Initialize
	lcd_write(0x32,LCD_CMD) # Set to 4-bit mode
	lcd_write(0x06,LCD_CMD) # Cursor move direction
	lcd_write(0x0C,LCD_CMD) # Turn cursor off
	lcd_write(0x28,LCD_CMD) # 2 line display
	lcd_write(0x01,LCD_CMD) # Clear display
	time.sleep(0.0005) # Delay to allow commands to process

def lcd_write(bits, mode):
# High bits
	GPIO.output(LCD_RS, mode) # RS

	GPIO.output(LCD_D4, False)
	GPIO.output(LCD_D5, False)
	GPIO.output(LCD_D6, False)
	GPIO.output(LCD_D7, False)
	if bits&0x10==0x10:
		GPIO.output(LCD_D4, True)
	if bits&0x20==0x20:
		GPIO.output(LCD_D5, True)
	if bits&0x40==0x40:
		GPIO.output(LCD_D6, True)
	if bits&0x80==0x80:
		GPIO.output(LCD_D7, True)

	# Toggle 'Enable' pin
	lcd_toggle_enable()

	# Low bits
	GPIO.output(LCD_D4, False)
	GPIO.output(LCD_D5, False)
	GPIO.output(LCD_D6, False)
	GPIO.output(LCD_D7, False)
	if bits&0x01==0x01:
		GPIO.output(LCD_D4, True)
	if bits&0x02==0x02:
		GPIO.output(LCD_D5, True)
	if bits&0x04==0x04:
		GPIO.output(LCD_D6, True)
	if bits&0x08==0x08:
		GPIO.output(LCD_D7, True)

	# Toggle 'Enable' pin
	lcd_toggle_enable()

def lcd_toggle_enable():
	time.sleep(0.0005)
	GPIO.output(LCD_E, True)
	time.sleep(0.0005)
	GPIO.output(LCD_E, False)
	time.sleep(0.0005)

def lcd_text(message,line):
	# Send text to display
	message = message.ljust(LCD_CHARS," ")

	lcd_write(line, LCD_CMD)

	for i in range(LCD_CHARS):
		lcd_write(ord(message[i]),LCD_CHR)
