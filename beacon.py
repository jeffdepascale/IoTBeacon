#!/usr/bin/python

from Adafruit_IO import MQTTClient
from Adafruit_IO.errors import AdafruitIOError
import time
import threading
from time import sleep
import gpiozero
from gpiozero import RGBLED
from gpiozero import Button
from pygame import mixer
import logging
import sys
import string
import json

logging.basicConfig(level=logging.DEBUG, filename="/home/pi/share/beacon.log", filemode="a+",
								format="%(asctime)-15s %(levelname)-8s %(message)s")

def global_except_hook(exctype, value, traceback):
	logging.info(value);
	sys.__excepthook__(exctype, value, traceback)
				
sys.excepthook = global_except_hook

testing = False
args = sys.argv[1:]		
if "-t" in args:
	testing = True
	logging.info("test mode")


class ConnectState:
    Disconnected, Connecting, Connected, PendingReconnect = range(4)

class LedDisplayRule(object):
	
	r = g = b = 0
	blinkCount = blinkRate= 1
	pulse = False
	persistent = False
	
	def __init__(self, _r, _g, _b, _blinkCount, _blinkRate, _pulse= False, _persistent = False):
		self.r = _r
		self.g = _g
		self.b = _b
		self.blinkCount = _blinkCount
		self.blinkRate = _blinkRate
		self.pulse = _pulse
		self.persistent = _persistent
	
	
class Beacon(object):

	connectState = ConnectState.Disconnected
	failConnectCount = 0
	configData = None
	client = None
	soundDir = '/boot/beacon/sounds/'
	rgbLED = None
	button = None
	buttonHoldTime = None	
	persistentLedRule = None
	
	def __init__(self):
		logging.info("Beacon service initialized")
		
		with open('/boot/beacon/config.json') as data_file:    
			self.configData = json.load(data_file)
		#need to account for no json data loaded
		
		if(self.configData.get("gpio")):
			gpioData = self.configData["gpio"]
			
			if gpioData.get("button"):
				self.button = Button(int(gpioData["button"]))
				self.button.when_released = self.buttonReleased
				self.button.when_held = self.buttonHeld
			else:
				logging.error("config json gpio object missing required button id")
			
			if gpioData.get("red_led") and gpioData.get("green_led") and gpioData.get("blue_led"):				
				self.rgbLED = RGBLED(int(gpioData["red_led"]), int(gpioData["green_led"]), int(gpioData["blue_led"]), False, (0,0,0), True)
			else:
				logging.error("config json gpio object missing required redled, greenled, and blueled ids")
				
		else:
			logging.error("config json missing require gpio object")
		
		if self.configData.get("directories"):
			dirObj = self.configData["directories"]
			if dirObj.get("sound"):
				soundDir = dirObj["sound"]
		
		self.ledDisplay(LedDisplayRule(0, 1, 0, 1, 1))
		sleep(1)

		self.client = MQTTClient(self.configData["credentials"]["username"], self.configData["credentials"]["key"])
		self.client.on_connect    = self.connected
		self.client.on_disconnect = self.disconnected
		self.client.on_message    = self.message	
		
		while True:
			if self.connectState == ConnectState.Disconnected:
				self.connect()
			elif self.connectState == ConnectState.PendingReconnect:
				self.reconnect()
			try:
				self.client.loop()
			except RuntimeError:
				logging.exception("runtime error caught from mqtt client loop")
				self.reconnect()
			
	def buttonHeld(self):
		self.buttonHoldTime = time.time()
	
	def buttonReleased(self):
		if self.buttonHoldTime is not None:
			heldTime = time.time() - self.buttonHoldTime + 1
			self.buttonHoldTime = None
		else:
			mixer.music.stop()
			mixer.quit()
			self.stopLED()
			self.persistentLedRule = None
			
	
	def message(self, client, feed_id, payload):
		msgStr = 'Feed {0} received new value: {1}'.format(feed_id, payload)
		log_data = ""
		with open('/home/pi/share/beacon.log', 'r') as myfile:
			log_data=myfile.read().replace('\n', '')
		if log_data.find(msgStr) == -1 or testing:
			logging.info(msgStr)
			messageData = None
			try:
				messageData = json.loads(payload)
			except:
				pass
			sound = None
			volume = 1				
			redVal = 0
			greenVal = 1
			blueVal = 0
			blinkCount = 1
			blinkRate = 1
			persistent = False
			pulse = False
			if self.configData.get("sounds"):
				sound = self.configData["sounds"]["default"]
			if messageData is not None:
				if messageData.get("sound"):
					sound = self.configData["sounds"][messageData["sound"]]
				if messageData.get("persistent") and str(messageData["persistent"]).lower() == "true":
					persistent = True
				if messageData.get("volume") is not None:
					volume = float(messageData.get("volume"))
				if messageData.get("blinkCount") is not None:
					blinkCount = int(messageData.get("blinkCount"))
				if messageData.get("blinkRate") is not None:
					blinkRate = float(messageData.get("blinkRate"))		
				if messageData.get("pulse") is not None and str(messageData["pulse"]).lower() == "true":
					pulse = True
				if messageData.get("color") is not None:
					try:
						colorArr = str(messageData.get("color")).split("/")
						redVal = float(colorArr[0])
						greenVal = float(colorArr[1])
						blueVal = float(colorArr[2])
					except:
						pass
						
			if sound is not None:
				mixer.init()
				mixer.music.set_volume(volume)
				mixer.music.load(self.soundDir + sound)
				mixer.music.play()
			self.ledDisplay(LedDisplayRule(redVal, greenVal, blueVal, blinkCount, blinkRate, pulse, persistent))
	
	def stopLED(self):
		self.rgbLED._stop_blink()
		self.rgbLED.off()
	
	def ledDisplay(self, rule):
		self.stopLED()
		blinkCount = rule.blinkCount
		if(rule.persistent):
			blinkCount=None
			self.persistentLedRule = rule
		if(rule.pulse):
			self.rgbLED.pulse(fade_in_time=rule.blinkRate, fade_out_time=rule.blinkRate, on_color=(rule.r, rule.g, rule.b), off_color=(0, 0, 0), n=blinkCount, background=True)
		else:
			self.rgbLED.blink(on_time=rule.blinkRate, off_time=rule.blinkRate, fade_in_time=0, fade_out_time=0, on_color=(rule.r, rule.g, rule.b), off_color=(0, 0, 0), n=blinkCount, background=True)
		
	def connected(self, client):
		logging.info("Connected to Adafruit IO")
		self.connectState = ConnectState.Connected
		self.failConnectCount = 0
		self.client.subscribe(self.configData["feeds"]["receive"]) 	
				
	def disconnected(self, client):
		logging.info('Disconnected from AdafruitIO')
		self.connectState = ConnectState.Disconnected
		self.reconnect();
	
	def connect(self):
		logging.info("init connect to Adafruit IO")
		self.connectState = ConnectState.Connecting
		try:
			self.client.connect()
		except Exception as e:
			logging.exception("Exception from Adafruit client connect")
			self.reconnect()

	def reconnect(self):
		self.failConnectCount += 1
		logging.info('pending Adafruit IO reconnect - failcount=' + str(self.failConnectCount))
		self.connectState = ConnectState.Connecting
		sleep(10)
		self.connect()
	
beacon = Beacon()		
