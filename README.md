# runtimetest
Python script to record flashlight runtime using a Raspberry Pi and a TSL2591.
# limitations
Maximum lux of the sensor is 88,000. If the lux recorded by the sensor is too high, you should adjust your setup so less light is hitting the sensor.
The test will run for a maximum of 24 hours.
# hardware setup
This test uses a raspberry pi and the sensor. An optional LED can be added for status indication. No screen is required if you're starting tests over ssh. An internet connection is required for timing.
![wiring diagram](https://github.com/bmengineer-gear/runtimetest/blob/master/runtimetestwiringdiagram.png)
# test setup
To perform a test with the finished hardware, you'll need a setup that directs some of the light from a flashlight to the sensor. Even a room will work, but objects moving around (including you) can affect the results, as can anyone turning on a light. I use a box for this reason.
It's important that the light is turned on to the desired mode within 5 seconds of starting the test, that the light is the only light source hitting the sensor, and that test setup remains stationary while the test is running.
# planned changes
- Add option to record IR mode for IR lights
- Add option to customize output to the terminal while running
- Add more indicating LEDs with clear functions
- Switch from sloppy delays to scheduling
