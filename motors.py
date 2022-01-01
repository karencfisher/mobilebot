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
    def __init__(self, flag, commandQueue):
        self.flag = flag
        self.commandQueue = commandQueue
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
                
    def run(self):
        print('start motors process')
        while self.flag.value:
            # Wait for a change
            if self.commandQueue.empty():
                continue
            command = self.commandQueue.get_nowait()

            # Look up the settings
            settings = MotorSettings[command]
            print(f'motor process: {command}')

            # Implement changes
            self.left_pwm.ChangeDutyCycle(STANDARD_SPEED + settings['left_accel'])
            self.right_pwm.ChangeDutyCycle(STANDARD_SPEED + settings['right_accel'])
            GPIO.output(self.left_forward, settings['l_fwd'])
            GPIO.output(self.left_reverse, settings['l_rev'])
            GPIO.output(self.right_forward, settings['r_fwd'])
            GPIO.output(self.right_reverse, settings['r_rev'])

        # Make sure motors off before exiting
        GPIO.output(self.left_forward, 0)
        GPIO.output(self.left_reverse, 0)
        GPIO.output(self.right_forward, 0)
        GPIO.output(self.right_reverse, 0)
        print('end motor process')