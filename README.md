# IoTBeacon
IoT beacon notification receiver and trigger built on AdaFruit IO and IFTTT

# Hardware
A walkthrough of an example hardware device for this software can be found at instructables.com

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

+ sounds - if present, requires at least one element named default, with the name of an mp3 or wav file in the sounds directory. Other elements can be added with other names that can be used to trigger different sounds for events. See message syntax below. 

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

Signup at io.adafruit.com and setup two feeds - one for inbound, one for outbound. the names of the feeds, your username, and your key all go into the config file. The key can be found under settings -> manage AIO keys.

# IFTTT Setup

To trigger actions in IFTTT from button presses on the device, configure an applet to listen to AdafruitIO on your outbound feed. To trigger actions to your device from IFTTT, configure an applet to send a message to AdafruitIO on your inbound channel. 

For a trigger, configure the value to be equal to the string defined in the commands array in the config JSON.

Message json syntax for inbound is below.

## Message JSON Options 

### Required

+ type - not used by the app, but important for logging, to differentiate sources and unique the requests.
+ timestamp - needed to uniquely identify the request. Look at the available ingredients for the IFTTT integration if triggering from there, the name may vary based on the integration.

### Optional
+ sound - the name of the sound to be played - this is the key name from the key value pair in the sounds object from the config file. 
+ persistent - adding this element and setting it to "true" will continue to blink the LED until the button is pressed to stop it. Defaults to false.
+ volume  - optionally set a volume level. This is relative to the system volume (which can be set via [alsamixer](http://blog.scphillips.com/posts/2013/01/sound-configuration-on-raspberry-pi-with-alsa/), a float value between 0 and 1. 
+ blinkrate - rate of LED blink in seconds, float value. Defaults to 1. 
+ blinkcount - integer value of how many times to blink the LED. Defaults to 1. 
+ pulse - adding this element and setting it to "true" will make the LED fade in/out instead of a binary on/off blink. Defaults to false. 
+ color - 3 float values between 0 and 1, with forward slashes delimiting, for red, green, and blue, respectively. So for example, 1/0/0 would be solid red. 1/0/1 would be purple. Note that LED's do vary in the intensity values. Commonly for example red will run higher intensity, so purple may be better defined as .3/0/1,trial and error will get the color you are looking for. Defaults to 0/1/0 - green.

# Button Hold Triggers

Holding the button for more than 5 seconds will trigger the unit to restart. 

# Logging

A file named beacon.log will be created in the same directory as beacon.py

# Launch Flags

1. -t - testing mode. Launching with this flag currently allows for the following:
	+ Adafruit IO currently always resends the last event for a feed when subscribing. IoTBeacon tracks this and does not replay an event that has previously come through. The testing flag will bypass this, which is useful for testing as an event will always trigger on launch.

# Current Limitations

Currently, this build assumes a common annode led. Common cathode will be supported in a future build. 
