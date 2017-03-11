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


logging.basicConfig(level=logging.DEBUG, filename="/home/pi/share/launch", filemode="a+",
								format="%(asctime)-15s %(levelname)-8s %(message)s")
								

def global_except_hook(exctype, value, traceback):
		logging.error(value);
		if str(value).find("Adafruit") != -1:
			connectState = ConnectState.PendingReconnect
			pass
		else:
			sys.__excepthook__(exctype, value, traceback)
				
sys.excepthook = global_except_hook


class ConnectState:
    Disconnected, Connecting, Connected, PendingReconnect = range(4)

	
	
	
class Beacon(object):

	led = LED(17)	
	connectState = ConnectState.Disconnected
	failConnectCount = 0
	client = None
	
	def __init__(self):
		logging.info("Beacon service initialized")
		
		self.led.on()
		sleep(1)
		self.led.off()
		
		self.client = MQTTClient('Jdepascale', 'ee0b91b182134253987e863af9be67ac')

		self.client.on_connect    = self.connected
		self.client.on_disconnect = self.disconnected
		self.client.on_message    = self.message	
		
		while True:
			if self.connectState == ConnectState.Disconnected:
				self.connect()
			elif self.connectState == ConnectState.PendingReconnect:
				self.reconnect()
			self.client.loop()
	
	def message(self, client, feed_id, payload):
		msgStr = 'Feed {0} received new value: {1}'.format(feed_id, payload)
		log_data = ""
		with open('/home/pi/share/launch', 'r') as myfile:
			log_data=myfile.read().replace('\n', '')
		if log_data.find(msgStr) == -1:
			logging.info(msgStr)
			mixer.init()
			mixer.music.load('/home/pi/share/notification.mp3')
			mixer.music.set_volume(1)
			mixer.music.play()
			self.led.on()
			sleep(5)
			self.led.off()
			mixer.quit()

	def connected(self, client):
		logging.info("connected")
		self.connectState = ConnectState.Connected
		self.failConnectCount = 0
		self.client.subscribe('cameraevent') # or change to whatever name you used	
				
	def disconnected(self, client):
		logging.info('Disconnected from AdafruitIO')
		self.connectState = ConnectState.Disconnected
		self.reconnect();
	
	def connect(self):
		logging.info("connect")
		self.connectState = ConnectState.Connecting
		try:
			self.client.connect()
		except AdafruitIOError as e:
			logging.error(e)
			self.reconnect()

	def reconnect(self):
		self.failConnectCount += 1
		logging.info('pending reconnect - failcount=' + str(self.failConnectCount))
		self.connectState = ConnectState.Connecting
		sleep(10)
		self.connect()
	
beacon = Beacon()		
