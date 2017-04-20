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

## Required

+ gpiodata - This object must contain the following four elements, with a value of the corresponding GPIO pin number: red_led, blue_led, green_led, button.

+ adafruit_io - This object must contain two sub objects: credentials - This object must contain the elements "key" and "username". feeds - this object must contain the elements "inbound" and "outbound"

## Optional

+ directories - This object currently supports only the element "sound". 

+ commands - An array of text strings that can be triggered from button presses.

## example json

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

# Current Limitations

Currently, this build assumes a common annode led. Common cathode will be supported in a future build. 
