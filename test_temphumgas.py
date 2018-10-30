import time
from twilio.rest import Client 
from gpiozero import DigitalInputDevice
import Adafruit_DHT

GASPIN = 14
DHTPIN = 10

account_sid = '' 
auth_token = '' 
client = Client(account_sid, auth_token) 
gas = DigitalInputDevice(GASPIN)
 
def sendMessage(message):
	message = client.messages.create(from_='', to='', body =message) 
	print(message.sid)
def tempHumSensor():
	return Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, DHTPIN)
def gasSensor():
	return not gas.value

while True:
	if (gasSensor()):
		sendMessage("")
	print(tempHumSensor())
	time.sleep(5)
