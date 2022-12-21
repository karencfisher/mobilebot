import time
import easygui as eg

from multiprocessing import Process, Value, Queue

try:
    import RPi.GPIO as GPIO
except (RuntimeError, ModuleNotFoundError):
    import fake_rpigpio.utils
    fake_rpigpio.utils.install()
    import RPi.GPIO as GPIO

from configuration import *
from autonomic import Autonomic


class RobotControl:
    def __init__(self):    
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(GPIOPins['indicators']['run_led'], GPIO.OUT)

        self.flag = Value('i', 1)
        self.autoQueue = Queue()
        self.autonomic = Autonomic(self.flag, self.autoQueue)
        self.autonomicProcess = Process(target=self.autonomic.run)
        self.running = True
    
    def run(self):
        self.autonomicProcess.start()
        while self.running:
            command = eg.enterbox("command: 'run (r)', 'stop (s)', 'exit (x)'")
            if command == 'exit' or command == 'x':
                print('exiting...')
                self.autoQueue.put(('halt', None))
                GPIO.output(GPIOPins['indicators']['run_led'], GPIO.LOW)
                self.shutdown()
                self.running = False
            elif command == 'stop' or command == 's':
                print('halting...')
                GPIO.output(GPIOPins['indicators']['run_led'], GPIO.LOW)
                self.autoQueue.put(('halt', None))
            elif command == 'run' or command == 'r':
                self.start_time = time.time()
                self.autoQueue.put(('resume', None))
                print('running...')
                GPIO.output(GPIOPins['indicators']['run_led'], GPIO.HIGH)
       
    def shutdown(self):
        self.autoQueue.put(('halt', None))
        self.flag.value = 0
        self.autonomicProcess.join()
        GPIO.cleanup()
        
def main():
    control = RobotControl()
    control.run()
            
if __name__ == '__main__':
    main() 
                   

       