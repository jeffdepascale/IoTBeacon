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
 
led = LED(17)
launched = False
failConnectCount = 0
logging.basicConfig(level=logging.DEBUG, filename="/home/pi/share/launch", filemode="a+",
                        format="%(asctime)-15s %(levelname)-8s %(message)s")
						

def global_except_hook(exctype, value, traceback):
	logging.error(value);
	sys.__excepthook__(exctype, value, traceback)

sys.excepthook = global_except_hook

def connected(client):
	logging.info("subscribed")
	client.subscribe('cameraevent') # or change to whatever name you used	

def message(client, feed_id, payload):
	logging.info('Feed {0} received new value: {1}'.format(feed_id, payload))
	global launched
	global failConnectCount
	failConnectCount = 0
	if launched == False:
		launched = True
	else:
		mixer.init()
		mixer.music.load('/home/pi/share/notification.mp3')
		mixer.music.set_volume(1)
		mixer.music.play()
		led.on()
		sleep(5)
		led.off()
		mixer.quit()

def disconnected(client):
	logging.info('Disconnected from AdafruitIO')
	reconnect()

def connect():
	try:
		client.connect()
	except AdafruitIOError as e:
		logging.error(e)
		reconnect()
	

def reconnect():
	global failConnectCount
	failConnectCount += 1
	if failConnectCount > 4:
		sys.exit(1);
	else:
		logging.info('reconnecting - failcount=' + str(failConnectCount))
		sleep(1)
		connect()
	
led.on()
sleep(1)
led.off()		
		
client = MQTTClient('Jdepascale', 'ee0b91b182134253987e863af9be67ac')

# Setup the callback functions defined above.
client.on_connect    = connected
client.on_message    = message

connect()
client.loop_blocking()
