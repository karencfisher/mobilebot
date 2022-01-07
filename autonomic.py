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


class Autonomic:
    def __init__(self, flag, commandQueue):
        self.flag = flag
        self.commandQueue = commandQueue
        self.sp = SensorsPoll()
        self.mc = MotorControl()
        self.start_time = time.time()
        self.state = 'stop'
        self.running = False

    def run(self):
        print("Start autonomic process")
        while self.flag.value:
            if not self.commandQueue.empty():
                command, duration = self.commandQueue.get(False)
                if command == 'halt':
                    self.mc.run(command='stop')
                    self.state = 'stop'
                    self.running = False
                elif command == 'resume':
                    self.running = True
                else:
                    self.mc.run(command=command)
                    if duration is not None:
                        time.sleep(duration)
            elif self.running:
                sensorData = self.sp.run()
                print(sensorData)
                elapsed = time.time() - self.start_time
                self.dispatch(elapsed, sensorData)
        self.mc.run(command='stop')
        print('Ending autonomic process')   

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