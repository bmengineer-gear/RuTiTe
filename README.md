# RuTiTe
Python script to record flashlight runtime test (RuTiTe) using a Raspberry Pi and a TSL2591.
# limitations
Maximum lux of the sensor is 88,000. If the lux recorded by the sensor is too high, you should adjust your setup so less light is hitting the sensor.
The script can only record so many times per second, as it's limited by the time it takes to get the values and write them to the file.
# hardware setup
This test uses a raspberry pi and the sensor. An optional LED can be added for status indication. No display is required if you're starting tests over ssh. An internet connection is required for timing.
![wiring diagram](https://github.com/bmengineer-gear/runtimetest/blob/master/runtimetestwiringdiagram.png)
I've replaced the first LED with a green one on my own setup. The LEDs are completely optional, and the script will run fine without them.
# test setup
To perform a test with the finished hardware, you'll need a setup that directs some of the light from a flashlight to the sensor. Even a room will work, but objects moving around (including you) can affect the results, as can anyone turning on a light. I use a box for this reason.
It's important that the light is turned on to the desired mode within 5 seconds of starting the test, that the light is the only light source hitting the sensor, and that test setup remains stationary while the test is running.
# planned changes
- Add option to record IR mode for IR lights
- Switch from sloppy delays to scheduling
- Add web sever to view test live
- Add script to plot results
