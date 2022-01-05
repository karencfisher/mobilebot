try:
    import RPi.GPIO as GPIO
except (RuntimeError, ModuleNotFoundError):
    import fake_rpigpio.utils
    fake_rpigpio.utils.install()
    import RPi.GPIO as GPIO

import time

from configuration import *


class MotorControl:
    '''
    Motor control process

    flag: boolean shared value, consumed. True to run, False to exit
    commandQueue: queue to listen for changes to motor behavior
    '''
    def __init__(self, asynchronous=False, flag=None, commandQueue=None):
        self.flag = flag
        self.commandQueue = commandQueue
        self.synch = not asynchronous
        motors = GPIOPins['motors']
        for key in motors.keys():
            GPIO.setup(list(motors[key].values()), GPIO.OUT)
            GPIO.output(list(motors[key].values()), GPIO.LOW)
            
            if key == 'left':
                self.left_pwm = GPIO.PWM(motors[key]['enable'], 1000)
                self.left_pwm.start(STANDARD_SPEED)
                self.left_forward = motors[key]['drive_p']
                self.left_reverse = motors[key]['drive_n']
            else:
                self.right_pwm = GPIO.PWM(motors[key]['enable'], 1000)
                self.right_pwm.start(STANDARD_SPEED)
                self.right_forward = motors[key]['drive_p']
                self.right_reverse = motors[key]['drive_n']
                
    def run(self, command=None):
        if not self.synch:
            print('start motors process')
        while self.synch or self.flag.value:
            if not self.synch:
                # Wait for a change
                if self.commandQueue.empty():
                    continue
                command = self.commandQueue.get_nowait()

            # Look up the settings
            settings = MotorSettings[command]
            print('motor process:', command)

            # Implement changes
            self.left_pwm.ChangeDutyCycle(STANDARD_SPEED + settings['left_accel'])
            self.right_pwm.ChangeDutyCycle(STANDARD_SPEED + settings['right_accel'])
            if settings['l_fwd'] is not None:
                GPIO.output(self.left_forward, settings['l_fwd'])
            if settings['l_rev'] is not None:
                GPIO.output(self.left_reverse, settings['l_rev'])
            if settings['r_fwd'] is not None:
                GPIO.output(self.right_forward, settings['r_fwd'])
            if settings['r_rev'] is not None:
                GPIO.output(self.right_reverse, settings['r_rev'])
                
            if self.synch:
                return

        print('end motor process')