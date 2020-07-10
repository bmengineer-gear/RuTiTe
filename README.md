# RuTiTe
Python script to record flashlight runtime test (RuTiTe) using a Raspberry Pi and a TSL2591.
# Installation
To install this script, just copy rutite.py to the directory you're working in. You'll need to have python3 installed along with the following dependencies:
- time
- math
- os
- csv
- board
- busio
- adafruit_tsl2591
- RPi
- argparse
- sys
- matplotlib
# Usage
At it's most basic, you can just run `python3 rutite.py`, and this script will fire up. It will print out to the terminal to let you know when it's ready for you to turn on a light and start the test, and record the runtime to a .csv file.
## Options
If you want to get fancy, there's plenty of configurability available.
- `-i` sets the interval between recordings, so `python3 rutite.py -i 0.5` would record a measurement every half second, instead of the default once per second.
- `-o` sets the output file name, so `python3 rutite.py -o flashlighttest.csv` would save the results in a file named flashlighttest.csv. If this isn't used, a timestamp will be used as the file name.
- `-d` sets the maximum duration the test will run for in minutes. `python3 rutite.py -d 15` If this isn't specified, the test won't stop automatically after a certain time.
- `-tp` sets the percent to terminate the test at. If you wanted the test to stop after the output reaches 10% of what it was at 30 seconds, you would run `python3 rutite.py -tp 10`. Note that when it reaches the set level, it keeps recording for a bit longer.
- `-pp` and `pd` both determine how often updates are printed to the terminal. If you wanted an update every time the output had changed by 10%, or every 30 minutes (whichever came first), you would run `python3 rutite.py -pp 10 -pd 30`.
- `-r` records relative time alongside the absolute time. If you're plotting the results afterwards, this makes sure the graph will start at 0 - but it will make the recorded file size a bit bigger.
- `-g` outputs a plot when the script is done. Right now this only works when either `-d`, `-tp`, or both is used and you let the script run until it's done.
## Example
I ran the following test of the highest mode of a lumintop FW1A:
```
pi@rpi0:~ $ python3 runtimetestandplot.py -o FW1Aturbo.csv -i 0.3 -d 5 -g 'FW1A Turbo' -pp 10
```
As a result I got the following printed out in the terminal:
```
15:14:16 Saving as FW1Aturbo.csv
15:14:18 Ready to start the test. Turn on the light now.
```
At this point I turned on the light in the mode I wanted to test:
```
15:14:24 Light detected. Recording started.
15:14:55 Sampling period complete. The output at 30s was 1931.6 lux. Sampling period max = 2159.3 lux, min = 1903.9 lux.
	The test will run until you stop it, or it has recorded for 5 minutes, or it reaches 193.2 lux (10.0% of the output at 30s).
15:15:13 Output is at 90% (1732 lux)
15:15:17 Output is at 79% (1523 lux)
15:15:27 Output is at 69% (1324 lux)
15:15:36 Output is at 58% (1125 lux)
15:16:10 Output is at 48% (930 lux)
15:17:27 Output is at 38% (734 lux)
15:19:24 Test complete
```
All done! I now have two files in my directory - `FW1Aturbo.csv` and `FW1A Turbo.png`.
The csv file looks something like this:
```
time,lux,absolute time,lumens
1594408465.550655,2159.2926719999996,,2159.2926719999996
1594408466.3578901,2142.548352,,2142.548352
1594408467.1652982,2131.97952,,2131.97952
...
```
and the image looks like this:
![example plot](https://github.com/bmengineer-gear/RuTiTe/blob/state-machine/exampleplot.png)
# Limitations
Maximum lux of the sensor is 88,000. If the lux recorded by the sensor is too high, you should adjust your setup so less light is hitting the sensor.
The test will run for a maximum of 24 hours unless a longer period is specified.
# Hardware Setup
This test uses a raspberry pi and the sensor. I've added LEDs to my setup for quick status indication at a glance, but these are completely optional. No screen is required if you're starting tests over ssh. An internet connection is required for timing.
![wiring diagram](https://github.com/bmengineer-gear/runtimetest/blob/master/runtimetestwiringdiagram.png)
I've replaced the first LED with a green one on my own setup.
# Test Setup
To perform a test with the finished hardware, you'll need a setup that directs some of the light from a flashlight to the sensor. Even a room will work, but objects moving around (including you) can affect the results, as can anyone turning on a light. I use a box for this reason.
It's important that the light being tested is the only light source hitting the sensor, and that test setup remains stationary while the test is running.
# Planned Changes
- Add option to record IR mode for IR lights
- Switch from sloppy delays to scheduling
# Known Issues
- If the light exceeds the sensor ceiling, the script will crash. If this happens, uncomment `#sensor.gain = adafruit_tsl2591.GAIN_LOW` in the code, and try again. If it still happens, you need to adjust your setup so less light reaches the sensor.
- Plotting doesn't work if you manually stop the test
