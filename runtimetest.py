# runtimetest.py
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
import argparse
import sys

# Initialize the I2C bus and the sensor, setup the LEDs
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_tsl2591.TSL2591(i2c)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT) #RunningLED
GPIO.setup(27, GPIO.OUT) #WritingLED
GPIO.setup(22, GPIO.OUT) #EndingLED

GPIO.output(17, GPIO.HIGH)
GPIO.output(27, GPIO.LOW)
GPIO.output(22, GPIO.LOW)

# Define functions
def writereadingsgetlux(filename, t):
    lux = sensor.lux
    #visible = sensor.visible
    #infrared = sensor.infrared
    with open (filename, "a") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow([t, lux])
    return lux
def statusLEDblink(state):
    if state == 1:
        GPIO.output(17, GPIO.HIGH)
        state = 0
    else:
        GPIO.output(17, GPIO.LOW)
        state = 1
    return state
def writingLEDblink(state):
    if state == 1:
        GPIO.output(27, GPIO.HIGH)
        state = 0
    else:
        GPIO.output(27, GPIO.LOW)
        state = 1
    return state
def timestamp():
    t = time.localtime()
    currenttime = time.strftime("%H:%M:%S ", t)
    return currenttime

# Parse inputs
parser = argparse.ArgumentParser()
parser.add_argument('-o','--outputfile', help='Filename for the csv output. If left blank, filename will be a timestamp')
parser.add_argument('-d','--duration',type=float,help='Duration of the test in minutes. If left blank, test will run for up to 24 hours.')
parser.add_argument('-i','--interval',type=float,help='Delay between measurements in seconds. Will set to one second if not specified. Delay is halved during the 30s sampling period at the beginning of the test.')
parser.add_argument('-tp','--terminationpercentage',type=float,help='Percentage to stop recording at. If left blank, test will run until the duration has passed.')
parser.add_argument('-pp','--printpercentage',type=float,help="Percent change between printed updates to the terminal. By default, the output will print every 5%%. Set to 100 if you don't want to see these updates.")
parser.add_argument('-pd','--printdelay',type=float,help="Minutes between printed updates to the terminal. By default, updates will be based on -printpercentage and not time.")
args = parser.parse_args()
if args.outputfile:
    filename = args.outputfile
    filenamesuffix = filename[-4:]
    if filenamesuffix != '.csv':
        GPIO.output(17, GPIO.LOW)
        GPIO.output(27, GPIO.LOW)
        GPIO.output(22, GPIO.HIGH)
        sys.exit("Error: Output filename must end in '.csv'. Please try again with an appropriate filename.")
else:
    filename = strftime("%Y%m%dTest.csv",gmtime())
if args.duration:
    testduration = args.duration * 60.0
else:
    testduration = 86400.0
if args.interval:
    delay = args.interval
else:
    delay = 1.0
if args.terminationpercentage:
    terminationpercentage = args.terminationpercentage
    autoterm = 1
else:
    terminationpercentage = -1.0
    autoterm = 0
if args.printpercentage:
    printpercentage = args.printpercentage
else:
    printpercentage = 5.0
if args.printdelay:
    printdelay = args.printdelay * 60.0
else:
    printdelay = testduration

# Check for file conflicts
if os.path.isfile(filename):
    print ("{}{} already exists. Checking for an an available name to avoid overwriting something important...".format(timestamp(),filename))
    newfilename = filename
    filesuffix = 1
    while os.path.isfile(newfilename):
        newfilename = filename.strip(".csv") + str(filesuffix) + ".csv"
        filesuffix += 1
    filename = newfilename
print ("{}Saving as {}".format(timestamp(),filename))

# Add header row
with open (filename, "a") as f:
    writer = csv.writer(f, delimiter=",")
    writer.writerow(["time", "lux"])
    state = writingLEDblink(1)

# Constants
sensorceiling = 88000.0
ANSIlux = sensorceiling
nextprintpercent = 95
tstart = time.time()

# Get a baseline reading
baselinesum = 0
for i in range(5):
    lux = sensor.lux
    baselinesum += lux
    time.sleep(1.0)
baselinelux = baselinesum / 5
thresholdlux = baselinelux * 3

print ("{}Ready to start the test. Turn on the light now.".format(timestamp()))

# Wait to detect some light at least triple the baseline
statusstate = 0
while lux < thresholdlux:
    lux = sensor.lux
    statusstate = statusLEDblink(statusstate)
    time.sleep(0.5)

print ("{}Light detected. Recording started.".format(timestamp()))
GPIO.output(17, GPIO.HIGH)
tstart = time.time()
t30seconds = tstart + 30.0
tterminate = tstart + testduration

# Sampling period where max is set
samplingluxmin = sensorceiling
samplingluxmax = 0.0
t = time.time()
while t < t30seconds:
    t = time.time()
    lux = writereadingsgetlux(filename, t)
    state = writingLEDblink(state)
    if lux < samplingluxmin:
        samplingluxmin = lux
    if lux > samplingluxmax:
        samplingluxmax = lux
    time.sleep(delay/2)
ANSIlux = lux
if ANSIlux == 88000.0:
    print("{}Sensor is saturated. The light is too bright to measure with your current setup. Consider adding a filter between the source and the sensor. The test will continue, but will be cut off at the high end.".format(timestamp()))

print("{}Sampling period complete. The output at 30s was {:.1f} lux. Sampling period max = {:.1f} lux, min = {:.1f} lux.".format(timestamp(), ANSIlux, samplingluxmax, samplingluxmin))
testdurationminutes = testduration / 60.0
cutofflux = ANSIlux * terminationpercentage / 100.0
if autoterm == 1:
    print ("\tThe test will run for {:.0f} minutes, or until it reaches {:.1f} lux ({}% of the output at 30s). Or until you stop it.".format(testdurationminutes, cutofflux, terminationpercentage))
else:
    print("\tThe test will run for {:.0f} minutes, or until you stop it.".format(testdurationminutes))

# Main recording code
printedpercent = 100
nextprinttime = t + printdelay
while t < tterminate:
    t = time.time()
    lux = writereadingsgetlux(filename, t)
    state = writingLEDblink(state)
    percentofANSIlux = lux / ANSIlux * 100.0
    if autoterm == 1 and percentofANSIlux <= terminationpercentage:
        autoterm = 0
        tremaining = (t - tstart) * 0.05
        if (t + tremaining) < tterminate:
            tterminate = t + tremaining
        minutesremaining = (tterminate - t) / 60.0
        print("{}Output has reached {:.0f}% ({:.0f} lux), which is at or below your {}% target. The test will run for {:.1} minutes before ending itself.".format(timestamp(), percentofANSIlux, lux, terminationpercentage, minutesremaining))
    elif t >= nextprinttime or abs(percentofANSIlux - printedpercent) >= printpercentage:
        print("{}Output is at {:.0f}% ({:.0f} lux)".format(timestamp(),percentofANSIlux, lux))
        printedpercent = percentofANSIlux
        nextprinttime = t + printdelay
    time.sleep(delay)
print("{}Test complete".format(timestamp()))
GPIO.output(17, GPIO.LOW)
GPIO.output(22, GPIO.LOW)
GPIO.output(27, GPIO.HIGH)
