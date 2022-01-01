from multiprocessing import Process, Value, Queue
import csv
import time

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
        sp = SensorsPoll(self.flag, self.sensorData)
        sensor_process = Process(target=sp.run)
        self.processes = [sensor_process]

        self.motorQueue = Queue()
        mc = MotorControl(self.flag, self.motorQueue)
        motor_process = Process(target=mc.run)
        self.processes.append(motor_process)

        self.data_log = DataLog()
        self.running = False
        self.start_time = None
        self.state = 'stopped'
    
    def run(self, commandQueue):
        for process in self.processes:
            process.start()
        while True:
            if commandQueue.full():
                command = commandQueue.get(False)
                if command == 'exit' or command == 'x':
                    print('exiting...')
                    GPIO.output(GPIOPins['indicators']['run_led'], GPIO.LOW)
                    self.flag.value = 0
                    for process in self.processes:
                        process.join()
                    self.running = False
                    break
                elif command == 'stop' or command == 's':
                    print('halted')
                    GPIO.output(GPIOPins['indicators']['run_led'], GPIO.LOW)
                    self.running = False
                    self.state = 'stopped'
                elif command == 'run' or command == 'r':
                    self.start_time = time.time()
                    print('running...')
                    GPIO.output(GPIOPins['indicators']['run_led'], GPIO.HIGH)
                    self.running = True
                
            if self.running:
                if self.sensorData.full():
                    sensorData = self.sensorData.get_nowait()
                    print(self.sensorData)
                    elapsed = time.time() - self.start_time
                    self.dispatch(elapsed, self.sensorData)
            else:
                self.motorQueue.put('stop')
        print('exiting thread...')
        

    def shutdown(self):
        self.mc.shutdown()
        GPIO.cleanup()
        

    def dispatch(self, elapsed, sensor_data):
        if self.state == 'stopped':
            if (sensor_data['front_rf'] > MINIMUM_DISTANCE or
                    not sensor_data['right_ir'] or not
                    sensor_data['left_ir']):
                print('going forward')
                self.motorQueue.put('forward')
                action = 'forward'
                self.state = 'forward'
            else:
                action = 'stopped'
            
        elif self.state == 'forward':
            if (sensor_data['front_rf'] <= MINIMUM_DISTANCE or
                    sensor_data['right_ir'] or sensor_data['left_ir']):
                self.mc.stop()
                print('reverse')
                self.motorQueue.put('reverse')
                action = 'reverse'
                self.state= 'reverse'
            else:
                action = 'forward'
                
        elif self.state == 'reverse':
            if sensor_data['front_rf'] > MINIMUM_DISTANCE:
                print('spin left')
                self.motorQueue.put('spin_left')
                action = 'spin_left'
                self.state = 'spin_left'
            else:
                action = 'reverse'
                
        elif self.state =='spin_left':
            time.sleep(.2)
            print('forward')
            self.motorQueue.put('forward')
            action = 'forward'
            self.state = 'forward'
            
        else:
            action = self.state
                

        self.data_log.log_data(elapsed, sensor_data, action)
        
            
    def get_log(self):
        return self.data_log
            
    
                   
    
    