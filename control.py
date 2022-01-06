from multiprocessing import Process, Value, Queue
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

        self.flag = Value('i', 1)
        self.sensorData = Queue()
        if ASYNCHRONOUS:
            sp = SensorsPoll(True, self.flag, self.sensorData)
            sensor_process = Process(target=sp.run)
            self.processes = [sensor_process]

            self.motorQueue = Queue()
            mc = MotorControl(True, self.flag, self.motorQueue)
            motor_process = Process(target=mc.run)
            self.processes.append(motor_process)
        else:
            self.sp = SensorsPoll()
            self.mc = MotorControl()

        #self.data_log = DataLog()
        self.running = False
        self.start_time = None
        self.state = 'stopped'
    
    def run(self, commandQueue):
        if ASYNCHRONOUS:
            for process in self.processes:
                process.start()
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
                    if ASYNCHRONOUS:
                        self.motorQueue.put('stop')
                    else:
                        self.mc.run(command='stop')
                    self.running = False
                    self.state = 'stopped'
                elif command == 'run' or command == 'r':
                    self.start_time = time.time()
                    print('running...')
                    GPIO.output(GPIOPins['indicators']['run_led'], GPIO.HIGH)
                    self.running = True

            if self.running:
                try:
                    if ASYNCHRONOUS:
                        sensorData = self.sensorData.get_nowait()
                    else:
                        sensorData = self.sp.run()
                    print(sensorData)
                    elapsed = time.time() - self.start_time
                    self.dispatch(elapsed, sensorData)
                    #time.sleep(.5)
                except:
                    self.shutdown()
            
        print('exiting thread...')
       

    def shutdown(self):
        if ASYNCHRONOUS:
            self.motorQueue.put('stop')
            self.flag.value = 0
            for process in self.processes:
                process.join()
        else:
            self.mc.run(command='stop')
        GPIO.cleanup()
        

    def dispatch(self, elapsed, sensor_data):
        # Collision, so back off
        if sensor_data['left_ir'] or sensor_data['right_ir']:
            self.state = 'reverse'
            
        # Avoid collision, making sure we have clearance to turn,
        # length or robot wheel axis to rear is < 15 cm
        elif (sensor_data['front_rf'] < MINIMUM_DISTANCE or
          sensor_data['left_rf'] < MINIMUM_DISTANCE or
          sensor_data['right_rf'] < MINIMUM_DISTANCE):
            direction = random.randint(0, 1)
            self.state = 'spin_left' if direction < 0.5 else 'spin_right'
            
        # default go ahead
        else:
            self.state = 'forward'
                
        if ASYNCHRONOUS:
            self.motorQueue.put(self.state)
        else:
            self.mc.run(command=self.state)
        #self.data_log.log_data(elapsed, sensor_data, self.state)
        
            
    def get_log(self):
        return self.data_log
            
    
                   

       