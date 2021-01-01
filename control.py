import queue
import csv
import time

import RPi.GPIO as GPIO

from configuration import *
from basic_sensors import SensorsPoll
from motors import MotorControl
from dataLog import DataLog


class RobotControl:
    def __init__(self):    
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(GPIOPins['run_led'], GPIO.OUT)
        self.sp = SensorsPoll()
        self.mc = MotorControl()
        self.data_log = DataLog()
        self.running = False
        self.reverse = False
        self.start_time = None
    
    def run(self, commandQueue):
        while True:
            try:
                command = commandQueue.get(False)
            except queue.Empty:
                command = None
                
            if command is not None:
                if command == 'exit' or command == 'x':
                    print('exiting...')
                    GPIO.output(GPIOPins['run_led'], GPIO.LOW)
                    self.running = False
                    break
                elif command == 'stop' or command == 's':
                    print('halted')
                    GPIO.output(GPIOPins['run_led'], GPIO.LOW)
                    self.running = False
                elif command == 'run' or command == 'r':
                    self.start_time = time.time()
                    print('running...')
                    GPIO.output(GPIOPins['run_led'], GPIO.HIGH)
                    self.running = True
                
            if self.running: 
                sensor_data = self.sp.ping()
                print(sensor_data)
                elapsed = time.time() - self.start_time
                self.dispatch(elapsed, sensor_data)
            else:
                self.mc.stop()
        print('exiting thread...')
        

    def shutdown(self):
        self.mc.shutdown()
        GPIO.cleanup()
        

    def dispatch(self, elapsed, sensor_data):                  
        if sensor_data['front_rf'] < MINIMUM_DISTANCE:
            print('stopped')
            self.mc.stop()
            action = 'stopped'
        else:
            print('going forward')
            self.mc.start('forward')
            action = 'forward'

        self.data_log.log_data(elapsed, sensor_data, action)
        
            
    def get_log(self):
        return self.data_log
            
    
                   
    
    