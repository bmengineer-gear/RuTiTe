# runtimetest.py
# Record TSL2591 sensor to csv every 300 ms
from time import strftime, gmtime, sleep
import time
import math
import os.path
from os import path
import csv
import board
import busio
import adafruit_tsl2591
import RPi.GPIO as GPIO

#Initialize the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)
#Initialize the sensor
sensor = adafruit_tsl2591.TSL2591(i2c)
#Setup LED
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)

def writereadingsgetlux(filename, t):
    lux = sensor.lux
    #visible = sensor.visible
    #infrared = sensor.infrared
    with open (filename, "a") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow([t, lux])
    return lux

def LEDblink(duration, state): 
    if state == "ON":
        GPIO.output(18, GPIO.HIGH)
        time.sleep(duration)
        GPIO.output(18, GPIO.LOW)
    else:
        GPIO.output(18, GPIO.LOW)
        time.sleep(duration)
        GPIO.output(18, GPIO.HIGH)

def timestamp():
    t = time.localtime()
    currenttime = time.strftime("%H:%M:%S ", t)
   return currenttime

filename = strftime("%Y%m%dTest.csv",gmtime())
if os.path.isfile(filename):
    newfilename = filename
    filesuffix = 1
    while os.path.isfile(newfilename):
        newfilename = filename.strip(".csv") + str(filesuffix) + ".csv"
        filesuffix += 1
    filename = newfilename

print ("{}Saving as {}".format(timestamp(),filename))

with open (filename, "a") as f:
    writer = csv.writer(f, delimiter=",")
    writer.writerow(["time", "lux"])

sensorceiling = 88000.0
ANSIlux = sensorceiling
nextprintpercent = 95
tstart = time.time()
t5seconds = tstart + 5.0
t35seconds = tstart + 35.0
tterminate = tstart + 86400.0 #max 24 hour test duration

t = time.time()
while t < t5seconds:
    t = time.time()
    lux = writereadingsgetlux(filename, t)
    LEDblink(.05, "ON")
    time.sleep(.95)

while t < t35seconds:
    t = time.time()
    lux = writereadingsgetlux(filename, t)
    if lux < ANSIlux:
        ANSIlux = lux
    LEDblink(.05, "ON")
    time.sleep(.95)
if ANSIlux == 88000.0:
    print("{}Sensor is saturated. The light is too bright to measure with your current setup.".format(timestamp()))

GPIO.output(18, GPIO.HIGH)
blinking = "OFF"
print ("{}ANSI lux = {}".format(timestamp(),ANSIlux))
while t < tterminate:
    t = time.time()
    lux = writereadingsgetlux(filename, t)
    percentofANSIlux=lux/ANSIlux*100
    if percentofANSIlux < nextprintpercent:
        tsincestart = t - tstart
        print("{}{:.0f}% of {:.0f} after {:.0f} seconds at t={}".format(timestamp(),percentofANSIlux, ANSIlux, tsincestart,t))
        while nextprintpercent > percentofANSIlux:
            nextprintpercent -= 5
        if nextprintpercent < 10:#Runtime test is done, measure for a bit longer then stop the test
            GPIO.output(18, GPIO.HIGH)
            blinking = "ON"
            tremaining = (t - tstart)/10
            if tremaining > 3600:
                tremaining = 3600
            minutesremaining = tremaining/60
            tterminate = tstart + tremaining
            print("{}Test will end in {:.1f} minutes".format(timestamp(),minutesremaining))
    LEDblink(.1, blinking)
    time.sleep(.8)
print("{}Test complete".format(timestamp()))
