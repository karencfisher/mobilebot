'''
 Interfaces for basic sensors, ultra sonice rangefinder
 and IR Obstacle sensor
'''

import time

import RPi.GPIO as GPIO
import numpy as np

from GPIOPins import GPIOPins



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
        
    def ping(self):
        '''
        Get a single reading
        Returns:
            distance in CM
        '''
        
        # trigger ping
        GPIO.output(self.trigger, GPIO.HIGH)
        time.sleep(.00001)
        GPIO.output(self.trigger, GPIO.LOW)
        
        # wait for echo
        while GPIO.input(self.echo) == False:
            start_time = time.time()
        
        while GPIO.input(self.echo) == True:
            stop_time = time.time()        
        
        # Calculate distance
        elapsed_time = stop_time - start_time
        d = (elapsed_time * 34300) / 2
        
        return d
    
    def getAvgRange(self, samples, delay):
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
            d = self.ping()
            ranges.append(d)
            time.sleep(delay)
    
        distance = np.mean(ranges)
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
    def __init__(self):
        self.usrf = []
        self.ir = []
        
        usrfs = GPIOPins['ultrasonicRF']
        for key in usrfs.keys():
            pins = usrfs[key]
            sensor = UltrasonicRF(pins['echo'], pins['trigger'])
            self.usrf.append(sensor)
            
        irs = GPIOPins['IRSensors']
        for key in irs.keys():
            pin = irs[key]
            self.ir.append(IRProximity(pin))
            
    def ping(self):
        output = []
        for sensor in self.usrf:
            output.append(sensor.getAvgRange(5, .05))
        for sensor in self.ir:
            output.append(sensor.ping())
        return output
                          


# Test Code
if __name__ == "__main__":
    
    GPIO.setmode(GPIO.BCM)
    sp = SensorsPoll()
    
    try:
        while True:
            print(sp.ping())
            time.sleep(.25)
    
    except KeyboardInterrupt:
        pass
    
    finally:
        GPIO.cleanup()
                          
