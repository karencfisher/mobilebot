import queue
import csv

import RPi.GPIO as GPIO

from configuration import *
from basic_sensors import SensorsPoll
from motors import MotorControl
from dataLog import DataLog


class RobotControl:
    def __init__(self):    
        GPIO.setmode(GPIO.BCM)
        self.sp = SensorsPoll()
        self.mc = MotorControl()
        self.data_log = DataLog()
        self.running = False
    
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
                    self.running = False
                    break
                elif command == 'stop':
                    print('halted')
                    self.running = False
                elif command == 'run':
                    print('running...')
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
        if sensor_data['front_rf'] < 20:
            print('obstacle detected stopping')    
            self.mc.stop()
            action = 'stop'
        else:
            print('going forward')
            self.mc.start('forward')
            action = 'forward'       
        self.data_log.log_data(sensor_data, action)
            
    def get_log(self):
        return self.data_log
            
    
                   
    
    