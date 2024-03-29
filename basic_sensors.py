'''
 Interfaces for basic sensors, ultrasonic rangefinder,
 IR Obstacle sensor, and IMU (gyro/accel)
'''

import time

try:
    import RPi.GPIO as GPIO
except (RuntimeError, ModuleNotFoundError):
    import fake_rpigpio.utils
    fake_rpigpio.utils.install()
    import RPi.GPIO as GPIO
import numpy as np

from configuration import *


class UltrasonicRF:
    def __init__(self, echo, trigger):
        '''
        Initialize object
        
        Inputs:
            echo - GPIO pin for echo
            trigger - GPIO pin fo trigger
        '''
        self.echo = echo
        self.trigger = trigger
        
        GPIO.setup(self.trigger, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN) 
        
    def ping(self, timeout=0.01):
        '''
        Get a single reading
        Returns:
            distance in CM
            
        exception:
            if times out, raises TimeoutError
        '''
        
        # trigger ping
        GPIO.output(self.trigger, GPIO.HIGH)
        time.sleep(.001)
        GPIO.output(self.trigger, GPIO.LOW)
        
        # wait for echo
        begin = time.time()
        while GPIO.input(self.echo) == False:
            if time.time() - begin > timeout:
                raise TimeoutError('timeout')
        start_time = time.time()
        
        while GPIO.input(self.echo) == True:
            if time.time() - begin > timeout:
                raise TimeoutError('timeout')
        stop_time = time.time()
            
        # Calculate distance
        elapsed_time = stop_time - start_time
        d = (elapsed_time * 34300) / 2 
        return d
    
    def getAvgRange(self, samples):
        '''
        Average of set number of pings
        Inputs:
            samples - number of samples to average
            delay - delay between pings, seconds (or fraction
                    thereof)
        Returns:
            Averaged distance in CM
        '''
        
        ranges = []
        for i in range(samples):
            try:
                d = self.ping()
            except TimeoutError:
                continue
            else:
                ranges.append(d)
    
        if len(ranges) > 0:
            distance = np.mean(ranges)
        else:
            distance = np.NAN
            
        return distance
    
    
class IRProximity:
    def __init__(self, pin):
        '''
        Initialization
        Input:
            pin - GPIO input to get signal from sensor (pull down if
                  detecting obstacle)
        '''
        
        self.pin = pin
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    
    def ping(self):
        '''
        Poll the IR sensor
        Return:
            True if triggered, otherwise False
        '''
        
        return not GPIO.input(self.pin)
        
        
class SensorsPoll:
    '''
    Collects data from all the basic sensors and posts for other
    processes to consume

    flag: shared memory, boolean, consumes flag. True to run, False to exit.
    data: queue to send sensor data
    '''
    def __init__(self):
        self.usrf = {}
        self.ir = {}
        
        usrfs = GPIOPins['ultrasonicRF']
        for key in usrfs.keys():
            pins = usrfs[key]
            sensor = UltrasonicRF(pins['echo'], pins['trigger'])
            self.usrf[key] = sensor
            
        irs = GPIOPins['IRSensors']
        for key in irs.keys():
            pin = irs[key]
            self.ir[key] = IRProximity(pin)
     
    def run(self):
        output = {}
        for key in self.usrf.keys():
            output[key + '_rf'] = self.usrf[key].getAvgRange(SAMPLES)
        for key in self.ir.keys():
            output[key + '_ir'] = self.ir[key].ping()
        return output
    
                          


