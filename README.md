# mobilebot

Developing basic code for a two wheel differential drive mobile robot, running on a Raspberry Pi 3 SBC. 

![Screenshot](images/mobilebot2.jpg)

## Features

Modified from mobile robot kit from 42 Electronics (https://42electronics.com/)

Raspberry PI 3b SBC.

"Headless" control using VNC

3 18650 rechargeable Li-ion batteries, providing 11.25 volts for motors and 5 volts (through convertor) to RPi.

2 DC gearbox motors and wheels. 

3 Ultrasonic Rangefinder sensors, forward, to left and right at 45 degrees of center.  

2 IR proximity sensors on the front, at 30% angles  

1 forward facing camera  

## Components

![diagram](images/Mobilebot_diagram.jpeg)

**UI** - Allows start/stop of robot, or exit.

**Visual Process** - Will accept visual data from camera for object detection and can direct robot towards/away from 
objects. Will over ride the "autonomic" process to provide more goal oriented navigation.

**Autonomic Process** - Basic obstacle avoidance using data from Ultrasonic and IR sensors. Motor control. Navigation
is by simple rules with some stochastic variation.

