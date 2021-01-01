'''
 Interfaces for basic sensors, ultrasonic rangefinder,
 IR Obstacle sensor, and IMU (gyro/accel)
'''

import time

import RPi.GPIO as GPIO
import numpy as np
from mpu6050 import mpu6050

from configuration import GPIOPins



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
    
    
class GyroAccel:
    def __init__(self):
        self.accel_gyro = mpu6050(0x68)
        
    def ping(self):
        gyro = self.accel_gyro.get_gyro_data()
        accel = self.accel_gyro.get_accel_data()
        return gyro, accel
        
        
class SensorsPoll:
    '''
    Collects data from all the basic sensors
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
        self.gyro_accel = GyroAccel()
            
    def ping(self):
        output = {}
        for key in self.usrf.keys():
            output[key + '_rf'] = self.usrf[key].getAvgRange(10)
        for key in self.ir.keys():
            output[key + '_ir'] = self.ir[key].ping()
        gyro, accel = self.gyro_accel.ping()
        for key in ['x', 'y', 'z']:
            output['gyro_' + key] = gyro[key]
            output['accel_' + key] = accel[key]
        return output
                          


# Test Code
if __name__ == "__main__":
    
    GPIO.setmode(GPIO.BCM)
    sp = SensorsPoll()
    count = 0
    start = time.time()
    
    try:
        while True:
            print(sp.ping())
#            time.sleep(.1)
            count += 1
    
    except KeyboardInterrupt:
        pass
    
    finally:
        print(round(count // (time.time() - start), 2), 'samples per second')
        GPIO.cleanup()
                          
