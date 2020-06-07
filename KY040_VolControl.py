#!/usr/bin/env python
# The KY040 source is from https://github.com/conradstorz/KY040
# and helped me a lot! Thanks!

# ----------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------
import RPi.GPIO as GPIO
import os, time

# ----------------------------------------------------------------------
# Defines
# ----------------------------------------------------------------------
CLOCKPIN = 5
DATAPIN = 6
SWITCHPIN = 13

# ----------------------------------------------------------------------
# Globals
# ----------------------------------------------------------------------
global soundLevel
global mute

class KY040:

    CLOCKWISE = 0
    ANTICLOCKWISE = 1
    DEBOUNCE = 12

    def __init__(self, clockPin, dataPin, switchPin, rotaryCallback, switchCallback):
        #persist values
        self.clockPin = clockPin
        self.dataPin = dataPin
        self.switchPin = switchPin
        self.rotaryCallback = rotaryCallback
        self.switchCallback = switchCallback

        #setup pins
        GPIO.setup(clockPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(dataPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(switchPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def start(self):
        GPIO.add_event_detect(self.clockPin, GPIO.FALLING, callback=self._clockCallback, bouncetime=self.DEBOUNCE)
        GPIO.add_event_detect(self.switchPin, GPIO.FALLING, callback=self.switchCallback, bouncetime=self.DEBOUNCE)

    def stop(self):
        GPIO.remove_event_detect(self.clockPin)
        GPIO.remove_event_detect(self.switchPin)
    
    def _clockCallback(self, pin):
        if GPIO.input(self.clockPin) == 0:
            self.rotaryCallback(GPIO.input(self.dataPin))

    def _switchCallback(self, pin):
        if GPIO.input(self.switchPin) == 0:
            self.switchCallback(GPIO.input(self.switchPin))

# ----------------------------------------------------------------------
# volume callbacks
# ----------------------------------------------------------------------
def readVolume():
    value = os.popen("amixer get Master|grep -o [0-9]*%|sed 's/%//'|uniq").read()
    return int(value)

def rotaryChange(direction):
    volume_step = 5
    volume = readVolume()
    if direction == 1:
        os.system("sudo amixer set Master -- "+str(min(100,max(0,volume + volume_step)))+"%")
    else:
        os.system("sudo amixer set Master -- "+str(min(100,max(0,volume - volume_step)))+"%")
def switchPressed(mute):
     if mute == 0:
         soundLevel = readVolume()
         os.system("sudo amixer set Master -- "+str(min(100,max(0,0)))+"%")
         mute = 1
     else:
         os.system("sudo amixer set Master -- "+str(min(100,max(0,0)))+"%")
         mute = 0

# ----------------------------------------------------------------------
# "Main" start...
# ----------------------------------------------------------------------
# start with 50% sound level
os.system("sudo amixer set Master -- "+str(min(100,max(0,50)))+"%")

GPIO.setmode(GPIO.BCM)
    
ky040 = KY040(CLOCKPIN, DATAPIN, SWITCHPIN, rotaryChange, switchPressed)
ky040.start()
 
try:
    while True:
        time.sleep(0.05)

except KeyboardInterrupt:
    ky040.stop()
    GPIO.cleanup()