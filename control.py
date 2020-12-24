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
        GPIO.setup(24, GPIO.OUT)
        self.sp = SensorsPoll()
        self.mc = MotorControl()
        self.data_log = DataLog()
        self.running = False
        self.reverse = False
    
    def run(self, commandQueue):
        while True:
            try:
                command = commandQueue.get(False)
            except queue.Empty:
                if not self.running:
                    continue
                command = None
                
            if command is not None:
                if command == 'exit':
                    print('exiting...')
                    GPIO.output(24, GPIO.LOW)
                    self.mc.stop()
                    self.running = False
                    break
                elif command == 'stop':
                    print('halted')
                    GPIO.output(24, GPIO.LOW)
                    self.running = False
                elif command == 'run':
                    print('running...')
                    GPIO.output(24, GPIO.HIGH)
                    self.running = True
                
            if self.running: 
                sensor_data = self.sp.ping()
                print(sensor_data)
                self.dispatch(sensor_data)
        print('exiting thread...')
        

    def shutdown(self):
        self.mc.shutdown()
        GPIO.cleanup()

    def dispatch(self, sensor_data):
        if (sensor_data['front_rf'] < 40 or 
            sensor_data['left_ir'] or
            sensor_data['right_ir'] and
            not self.reverse):
            print('obstacle detected')    
            self.mc.start('reverse')
            self.reverse = True
            action = 'reverse'
        elif self.reverse:
            if (sensor_data['front_rf'] > 40 and
                sensor_data['left_rf'] > 40 and
                sensor_data['right_rf'] > 40):
                self.mc.start('hard_left')
                time.sleep(3)
                self.mc.stop()
                self.reverse = False
                action = 'hard-left'
                print('hard left')
            else:
                action = 'reverse'
                print('reverse')
        else:
            print('going forward')
            self.mc.start('forward')
            action = 'forward'
        self.data_log.log_data(sensor_data, action)
            
    def get_log(self):
        return self.data_log
            
    
                   
    
    