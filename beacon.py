#!/usr/bin/python

from Adafruit_IO import MQTTClient
from Adafruit_IO.errors import AdafruitIOError
from time import sleep
from gpiozero import LED
from pygame import mixer
import pygame
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


class ConnectState:
    Disconnected, Connecting, Connected, PendingReconnect = range(4)

	
	
	
class Beacon(object):

	led = LED(17)	
	connectState = ConnectState.Disconnected
	failConnectCount = 0
	configData = None
	client = None
	soundDir = '/boot/beacon/sounds/'
	
	def __init__(self):
		logging.info("Beacon service initialized")
		self.led.on()
		sleep(1)
		self.led.off()
		
		with open('/boot/beacon/config.json') as data_file:    
			self.configData = json.load(data_file)
		#need to account for no json data loaded
		
		if self.configData.get("directories"):
			dirObj = self.configData["directories"]
			if dirObj.get("sound"):
				soundDir = dirObj["sound"]
				
		
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
			
	
	def message(self, client, feed_id, payload):
		msgStr = 'Feed {0} received new value: {1}'.format(feed_id, payload)
		log_data = ""
		with open('/home/pi/share/beacon.log', 'r') as myfile:
			log_data=myfile.read().replace('\n', '')
		if log_data.find(msgStr) == -1:
			logging.info(msgStr)
			messageData = None
			try:
				messageData = json.loads(payload)
			except:
				pass
			sound = None
			if self.configData.get("sounds"):
				sound = self.configData["sounds"]["default"]
			if messageData is not None and messageData.get("sound"):
				sound = self.configData["sounds"][messageData["sound"]]
			if sound is not None:
				mixer.init()
				mixer.music.set_volume(1)
				mixer.music.load(self.soundDir + sound)
				mixer.music.play()
			blinkCount = int(messageData.get("blinkCount") or 1)
			blinkRate = float(messageData.get("blinkRate") or 5)
			print blinkCount
			print blinkRate
			for i in range(0,blinkCount):
				self.led.on()
				sleep(blinkRate)
				self.led.off()
				sleep(blinkRate)

	def connected(self, client):
		logging.info("Connected to Adafruit IO")
		self.connectState = ConnectState.Connected
		self.failConnectCount = 0
		self.client.subscribe(self.configData["feeds"]["receive"]) # or change to whatever name you used	
				
	def disconnected(self, client):
		logging.info('Disconnected from AdafruitIO')
		self.connectState = ConnectState.Disconnected
		self.reconnect();
	
	def connect(self):
		logging.info("init connect to Adafruit IO")
		self.connectState = ConnectState.Connecting
		try:
			self.client.connect()
		except Error as e:
			logging.exception("Exception from Adafruit client connect")
			self.reconnect()

	def reconnect(self):
		self.failConnectCount += 1
		logging.info('pending Adafruit IO reconnect - failcount=' + str(self.failConnectCount))
		self.connectState = ConnectState.Connecting
		sleep(10)
		self.connect()
	
beacon = Beacon()		
