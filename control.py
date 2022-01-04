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
                    self.running = False
                    self.state = 'stopped'
                elif command == 'run' or command == 'r':
                    self.start_time = time.time()
                    print('running...')
                    GPIO.output(GPIOPins['indicators']['run_led'], GPIO.HIGH)
                    self.running = True

            if self.running:
                try:
                    if not self.sensorData.empty():
                        sensorData = self.sensorData.get_nowait()
                        print(sensorData)
                        elapsed = time.time() - self.start_time
                        self.dispatch(elapsed, sensorData)  
                except:
                    self.shutdown()
            
        print('exiting thread...')
       

    def shutdown(self):
        self.flag.value = 0
        for process in self.processes:
            process.join()
        GPIO.cleanup()
        

    def dispatch(self, elapsed, sensor_data):
        # Avoid collision, making sure we have clearance to turn,
        # length or robot wheel axis to rear is < 15 cm
        if sensor_data['front_rf'] < MINIMUM_DISTANCE:
            if (sensor_data['left_rf'] <= 15 and sensor_data['right_rf'] <= 15):
                self.state = 'reverse'
            elif sensor_data['right_rf'] <= 15:
                self.state = 'spin_right'
            else:
                self.state = 'spin_left'
            
        # Keep distance from sides, or veer away from side
        elif self.state in ['forward', 'reverse', 'right', 'left']:
            if (sensor_data['left_rf'] <= 15):
                self.state = 'right'   
            elif (sensor_data['right_rf'] <= 15):
                self.state = 'left'
            
        # default go ahead
        else:
            self.state = 'forward'
                
        self.motorQueue.put(self.state)
        #self.data_log.log_data(elapsed, sensor_data, self.state)
        
            
    def get_log(self):
        return self.data_log
            
    
                   

       