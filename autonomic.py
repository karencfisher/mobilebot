import time
import random
import numpy as np

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
from talker import talker


class Distances:
    '''
    Basically, a circular buffer, which we can get the mean and
    variance of the values it contains.
    '''
    def __init__(self, n_max):
        self.data = np.zeros(shape=(n_max, 3), dtype='float')
        self.n_count = 0
        self.n_max = n_max

    def push(self, data):
        self.data[self.n_count % self.n_max, :] = data
        self.n_count += 1
        
    def get_stats(self):
        '''
        Get mean and variance of values
        If the buffer is not yet full (warmed up) we return
        None.
        '''
        if self.n_count < self.n_max - 1:
            return None
        variance = np.std(self.data, axis=0)
        return variance


class Autonomic:
    def __init__(self, flag, commandQueue):
        self.flag = flag
        self.commandQueue = commandQueue
        self.sp = SensorsPoll()
        self.mc = MotorControl()
        self.start_time = time.time()
        self.state = 'stop'
        self.running = False
        self.log = DataLog()
        self.distances = Distances(10)
        self.talker = talker()

    def run(self):
        print("Start autonomic process")
        while self.flag.value:
            if not self.commandQueue.empty():
                command, duration = self.commandQueue.get(False)
                if command == 'halt':
                    self.halt()
                elif command == 'resume':
                    self.running = True
                else:
                    self.mc.run(command=command)
                    if duration is not None:
                        time.sleep(duration)
            elif self.running:
                sensorData = self.sp.run()
                self.distances.push([sensorData['left_rf'], 
                                     sensorData['front_rf'],
                                     sensorData['right_rf']])
                elapsed = time.time() - self.start_time
                state = self.dispatch(sensorData)

                vars = self.distances.get_stats()
                if vars is None:
                    sensorData['left_var'] = np.nan
                    sensorData['front_var'] = np.nan
                    sensorData['right_var'] = np.nan
                else:
                    sensorData['left_var'] = vars[0]
                    sensorData['front_var'] = vars[1]
                    sensorData['right_var'] = vars[2]

                print(sensorData, state)
                self.log.log_data(elapsed, sensorData, state)

                if vars is not None and np.any(vars < 1):
                    print('Stuck!')
                    self.talker.talk('Help me! I am stuck!')
                    self.log.log_data(elapsed, sensorData, [('stuck', None)])
                    self.halt()

        self.mc.run(command='stop')
        print('Ending autonomic process')

    def halt(self):
        self.mc.run(command='stop')
        self.state = 'stop'
        self.running = False
        self.log.dump('autonomic.csv')   

    def dispatch(self, sensor_data):

        # Collision, so back off
        if sensor_data['left_ir'] or sensor_data['right_ir']:
            states = [('reverse', None)]
            
        elif sensor_data['front_rf'] < MINIMUM_DISTANCE:
            option = random.choice(['left', 'right'])
            states = [('reverse', 0.5), (option, 1)]
            
        elif sensor_data['left_rf'] < MINIMUM_DISTANCE:
            states = [('reverse', 0.5), ('right', 1)]
            
        elif sensor_data['right_rf'] < MINIMUM_DISTANCE:
            states = [('reverse', 0.5), ('left', 1)]   
            
        # Avoid collision, making sure we have clearance to turn,
        # length or robot wheel axis to rear is < 15 cm
        elif sensor_data['front_rf'] < WARNING_DISTANCE:
            option = random.choice(['left', 'right'])
            states = [(option, 1)]
            
        elif sensor_data['left_rf'] < WARNING_DISTANCE:
            states = [('right', 1)]
            
        elif sensor_data['right_rf'] < WARNING_DISTANCE:
            states = [('left', 1)]
            
        # default go ahead (add some stochastic behavior)
        else:
            option = random.randint(1, 100)
            if option <= 80:
                states = [('forward', None)]
            elif option <= 90:
                states = [('veer_left', None)]
            else:
                states = [('veer_right', None)]
                
        # execute
        for state, duration in states:
            if state != self.state:
                self.mc.run(command=state)
                self.state = state
            if duration is not None:
                time.sleep(duration)
        return states
