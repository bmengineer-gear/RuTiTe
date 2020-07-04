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

if __name__ == "__main__":
    # Initialize the I2C bus and the sensor, setup the LEDs
    i2c = busio.I2C(board.SCL, board.SDA)
    sensor = adafruit_tsl2591.TSL2591(i2c)
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)  
    ready_led = 17
    running_led = 27
    complete_led = 22
    GPIO.setup(ready_led, GPIO.OUT)
    GPIO.setup(running_led, GPIO.OUT)
    GPIO.setup(complete_led, GPIO.OUT)
    GPIO.output(ready_led, GPIO.HIGH)
    GPIO.output(running_led, GPIO.LOW)
    GPIO.output(complete_led, GPIO.LOW)

    # Define functions
    def write_to_csv(filename, t, lux):
        with open (filename, "a") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow([t, lux])
    def blink_led(pin):
        GPIO.output(pin, not GPIO.input(pin))
    def current_timestamp():
        return time.strftime("%H:%M:%S ", time.localtime())

    # Parse inputs
    parser = argparse.ArgumentParser()
    parser.add_argument('-o','--outputfile', default=strftime('%Y%m%dTest.csv',time.localtime()), help='filename for the csv output')
    parser.add_argument('-d','--duration', type=float, default = 0.0, help='duration of the test in minutes')
    parser.add_argument('-i','--interval', type=float, default=1.0, help='interval between measurements in seconds (halved during the 30s sampling period at the beginning of the test)')
    parser.add_argument('-tp','--terminationpercentage', type=float, default=100.0, help='percent output to stop recording at')
    parser.add_argument('-pp','--printpercentage', type=float, default=0.0, help='percent change between printed updates to the terminal')
    parser.add_argument('-pd','--printdelay', type=float, default=0.0, help='minutes between printed updates to the terminal')
    args = parser.parse_args()
    filename = args.outputfile
    test_duration = args.duration * 60.0
    delay = args.interval
    termination_percentage = args.terminationpercentage
    percent_change_to_print = args.printpercentage
    time_between_prints = args.printdelay * 60

    # Check for file conflicts
    if filename[-4:] != '.csv':
        sys.exit("Error: Output filename must end in '.csv'. Please try again with an appropriate filename.")
    if os.path.isfile(filename):
        print ("{}{} already exists. Checking for an an available name to avoid overwriting something important...".format(current_timestamp(),filename))
        new_filename = filename
        file_suffix = 1
        while os.path.isfile(new_filename):
            new_filename = filename.strip(".csv") + str(file_suffix) + ".csv"
            file_suffix += 1
        filename = new_filename
    print ("{}Saving as {}".format(current_timestamp(),filename))

    # Add header row
    with open (filename, "a") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(["time", "lux"])
        blink_led(running_led)

    # Main loop
    sensor_ceiling = 88000.0 
    state = 'set_baseline'
    baseline_sum = 0.0
    n = 0
    while state != 'exit':
        lux = sensor.lux
        t = time.time()
        if state == 'set_baseline':
            n += 1
            baseline_sum += lux
            if n == 5:
                threshold_lux = baseline_sum / 5.0 * 3.0
                state = 'waiting_for_threshold'
                print ("{}Ready to start the test. Turn on the light now.".format(current_timestamp()))
            time.sleep(1.0)

        if state == 'waiting_for_threshold':
            if lux >= threshold_lux:
                state = 'sampling_period'
                GPIO.output(ready_led, GPIO.HIGH)
                t_test_start = time.time()
                t_sampling_complete = t_test_start + 30.0
                t_test_complete = t_test_start + test_duration
                sampling_lux_min = sensor_ceiling
                sampling_lux_max = 0.0
                print ("{}Light detected. Recording started.".format(current_timestamp()))
            else:
                blink_led(ready_led)
                time.sleep(0.5)

        if state == 'sampling_period':
            if t < t_sampling_complete:
                write_to_csv(filename, t, lux)
                blink_led(running_led)
                if lux < sampling_lux_min:
                    sampling_lux_min = lux
                if lux > sampling_lux_max:
                    sampling_lux_max = lux
                time.sleep(delay/2.0)
            else:
                state = 'main_recording'
                lux_at_30s = lux
                if lux_at_30s == sensor_ceiling:
                    print("{}Sensor is saturated. The light is too bright to measure with your current setup. Consider adding a filter between the source and the sensor. The test will continue, but will be cut off at the high end.".format(current_timestamp()))
                print("{}Sampling period complete. The output at 30s was {:.1f} lux. Sampling period max = {:.1f} lux, min = {:.1f} lux.".format(current_timestamp(), lux_at_30s, sampling_lux_max, sampling_lux_min))
                text_to_print = '\tThe test will run until you stop it'
                if test_duration != 0.0:
                    text_to_print += ', or it has recorded for {:.0f} minutes'.format(test_duration/60)
                if termination_percentage != 100.0:
                    termination_output = lux_at_30s * termination_percentage / 100
                    text_to_print += ', or it reaches {:.1f} lux ({}% of the output at 30s)'.format(termination_output, termination_percentage)
                print(text_to_print + '.')
                last_printed_percent = 100.0
                last_print_time = t

        if state == 'main_recording':
            write_to_csv(filename, t, lux)
            blink_led(running_led)
            percent_output = lux / lux_at_30s * 100.0
            if test_duration != 0.0 and t >= t_test_complete:
                state = 'exit'
            elif termination_percentage != 100.0 and percent_output <= termination_percentage:
                termination_percentage = 100.0
                t_remaining = (t - t_test_start) * 0.05
                print("{}Output has reached {:.0f}% ({:.0f} lux), which is at or below your {}% target.".format(current_timestamp(), percent_output, lux, termination_percentage))
                last_print_time = t
                last_printed_percent = percent_output
                if test_duration == 0.0 or (t + t_remaining) <= test_duration:
                        t_test_complete = t + t_remaining
                        test_duration = t_remaining
                else:
                    t_remaining = test_duration - t
                print("\tJust collecting a bit more data. The test will end in {:.1f} minutes.".format(t_remaining/60))
            elif time_between_prints != 0.0 and (t - last_print_time) > time_between_prints:
                print("{}Output is at {:.0f}% ({:.0f} lux)".format(current_timestamp(),percent_output, lux))
                last_print_time = t
                last_printed_percent = percent_output
                time.sleep(delay)
            elif percent_change_to_print != 0.0 and abs(percent_output - last_printed_percent) >= percent_change_to_print:
                print("{}Output is at {:.0f}% ({:.0f} lux)".format(current_timestamp(),percent_output, lux))
                last_print_time = t
                last_printed_percent = percent_output
                time.sleep(delay)
            else:
                time.sleep(delay)
   
    print("{}Test complete".format(current_timestamp()))
    GPIO.output(ready_led, GPIO.LOW)
    GPIO.output(running_led, GPIO.LOW)
    GPIO.output(complete_led, GPIO.HIGH)
