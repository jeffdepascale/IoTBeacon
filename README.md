# IoTBeacon
IoT beacon notification receiver and trigger built on AdaFruit IO and IFTTT

# Hardware
A walkthrough of an exampke hardware device for this software can be found at instructables.com

# OS Setup

Raspbian Jessie Lite is a good starting point: https://www.raspberrypi.org/downloads/raspbian/



# Installation

IoTBeacon requires a json configuration file named beacon.json in the same directory. It also assumes audio files are stored in a subdirectory names "sounds", though this can be overriden in config (see below).

Nice and simple for testing:
```
python beacon.py
```
install required dependencies, which includes:
+ [Adafruit IO](https://github.com/adafruit/io-client-python)
+ [GPIOZero](https://gpiozero.readthedocs.io/en/stable/)
+ [PyGame](https://www.pygame.org/)


For running on startup automatically, this can be set up as a service following the details here: https://learn.adafruit.com/running-programs-automatically-on-your-tiny-computer/systemd-writing-and-enabling-a-service

# Configuration File Options

The json file has a mix of require dand optional values:

### Required

+ gpiodata - This object must contain the following four elements, with a value of the corresponding GPIO pin number: red_led, blue_led, green_led, button.

+ adafruit_io - This object must contain two sub objects: credentials - This object must contain the elements "key" and "username". feeds - this object must contain the elements "inbound" and "outbound". Inbound defines the feed that the unit will listen on, outbound is the feed it will report triggers to. 

### Optional

+ directories - This object currently supports only the element "sound". 

+ commands - An array of text strings that can be triggered from button presses.

### example json

```json
{
	"gpio": {
		"button": "24",
		"red_led": "23",
		"green_led": "17",
		"blue_led": "27"
	},
	"adafruit_io":{
		"credentials": {
			"key": "[YOUR KEY]",
			"username": "[YOUR USERNAME]"
		},
		"feeds": {
			"inbound": "beacon-inbound",
			"outbound": "beacon-outbound"
		}
	},
	"commands":[
		"command1",
		"command2"
	],
	"sounds": {
		"default": "notification.mp3",
		"notification": "notification.mp3",
		"alert":"alert.wav"
	}
}
```
# Adafruit IO Steup

# IFTTT Setup

To trigger actions in IFTTT from button presses on the device, configure an applet to listen to AdafruitIO on your outbound feed. To trigger actions to your device from IFTTT, configure an applet to send a message to AdafruitIO on your inbound channel. 

For a trigger, configure the value to be equal to the string defined in the commands array in the config JSON.

Message json syntax for inbound is below.

### Message JSON Options 



# Button Hold Triggers

Holding the button for more than 5 seconds will trigger the unit to restart. 

# Sounds


# Logging

A file named beacon.log will be created in the same directory as beacon.py

# Launch Flags

1. -t - testing mode. Launching with this flag currently allows for the following:
	+ Adafruit IO currently always resends the last event for a feed when subscribing. IoTBeacon tracks this and does not replay an event that has previously come through. The testing flag will bypass this, which is useful for testing as an event will always trigger on launch.

# Current Limitations

Currently, this build assumes a common annode led. Common cathode will be supported in a future build. 
