# IoTBeacon
IoT beacon notification receiver and trigger built on AdaFruit IO and IFTTT

# Hardware
A walkthrough of an exampke hardware device for this software can be found at instructables.com

# OS Setup

Raspbian Jessie Lite is a good starting point: https://www.raspberrypi.org/downloads/raspbian/

# Installation

Nice and simple for testing:
```
python beacon.py
```
install required dependencies, which includes:
+ [Adafruit IO](https://github.com/adafruit/io-client-python)
+ [GPIOZero](https://gpiozero.readthedocs.io/en/stable/)
+ [PyGame](https://www.pygame.org/)


For running on startup automatically, this can be set up as a service following the details here: https://learn.adafruit.com/running-programs-automatically-on-your-tiny-computer/systemd-writing-and-enabling-a-service

# Configuration
