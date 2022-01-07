import csv
import time
import random

try:
    import RPi.GPIO as GPIO
except (RuntimeError, ModuleNotFoundError):
    import fake_rpigpio.utils
    fake_rpigpio.utils.install()
    import RPi.GPIO as GPIO

from configuration import *
from basic_sensors import SensorsPoll
from motors import MotorControl
from dataLog import DataLog


class RobotControl:
    def __init__(self):    
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(GPIOPins['indicators']['run_led'], GPIO.OUT)

        self.sp = SensorsPoll()
        self.mc = MotorControl()

        #self.data_log = DataLog()
        self.running = False
        self.start_time = None
        self.state = 'stopped'
    
    def run(self, commandQueue):
        while True:
            if not commandQueue.empty():
                command = commandQueue.get(False)
                if command == 'exit' or command == 'x':
                    print('exiting...')
                    GPIO.output(GPIOPins['indicators']['run_led'], GPIO.LOW)
                    self.running = False
                    self.shutdown()
                    break
                elif command == 'stop' or command == 's':
                    print('halted')
                    GPIO.output(GPIOPins['indicators']['run_led'], GPIO.LOW)
                    self.mc.run(command='stop')
                    self.running = False
                elif command == 'run' or command == 'r':
                    self.start_time = time.time()
                    print('running...')
                    GPIO.output(GPIOPins['indicators']['run_led'], GPIO.HIGH)
                    self.running = True

            if self.running:
                try:
                    sensorData = self.sp.run()
                    print(sensorData)
                    elapsed = time.time() - self.start_time
                    self.dispatch(elapsed, sensorData)
                    #time.sleep(.5)
                except Exception as inst:
                    self.shutdown()
                    raise
            
        print('exiting thread...')
       

    def shutdown(self):
        self.mc.run(command='stop')
        GPIO.cleanup()
        

    def dispatch(self, elapsed, sensor_data):
        # Collision, so back off
        if sensor_data['left_ir'] or sensor_data['right_ir']:
            state = 'reverse'
            duration = None
            
        # Avoid collision, making sure we have clearance to turn,
        # length or robot wheel axis to rear is < 15 cm
        elif sensor_data['left_rf'] < MINIMUM_DISTANCE:
                state = 'spin_left'
                duration = 0.5
            
        elif sensor_data['right_rf'] < MINIMUM_DISTANCE:
            state = 'spin_right'
            duration = 0.5
        
        
        elif sensor_data['front_rf'] < MINIMUM_DISTANCE:
            option = random.choice(['spin_left', 'spin_right'])
            state = option
            duration = 0.5
            
        # default go ahead
        else:
            state = 'forward'
            duration = None
                
        if state != self.state:
            self.mc.run(command=state)
            if duration is not None:
                time.sleep(duration)
            self.state = state
            
        #self.data_log.log_data(elapsed, sensor_data, self.state)
         
    def get_log(self):
        return self.data_log
            
    
                   

       