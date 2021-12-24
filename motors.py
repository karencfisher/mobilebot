import RPi.GPIO as GPIO
import time

from configuration import *


class MotorControl:
    def __init__(self):
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
                
    def stop(self):
        pins = [self.left_forward, self.right_forward,
                self.left_reverse, self.right_reverse]
        GPIO.output(pins, GPIO.LOW)
        self.left_pwm.ChangeDutyCycle(STANDARD_SPEED)
        self.right_pwm.ChangeDutyCycle(STANDARD_SPEED)
        
    def change_speed(left, right):
        self.left_pwm.ChangeDutyCycle(left)
        self.right_pwm.ChangeDutyCycle(right)
        
    def start(self, direction, duration=-1):
        if direction == 'forward':
            GPIO.output([self.left_forward, self.right_forward],
                        GPIO.HIGH)
            GPIO.output([self.left_reverse, self.right_reverse],
                        GPIO.LOW)
            
        elif direction == 'reverse':
            GPIO.output([self.left_reverse, self.right_reverse],
                        GPIO.HIGH)
            GPIO.output([self.left_forward, self.right_forward],
                        GPIO.LOW)
            
        elif direction == 'spin_left':
            GPIO.output([self.right_forward, self.left_reverse],
                        GPIO.HIGH)
            GPIO.output([self.left_forward, self.right_reverse],
                        GPIO.LOW)
        
        elif direction == 'spin_right':
            GPIO.output([self.left_forward, self.right_reverse],
                        GPIO.HIGH)
            GPIO.output([self.left_reverse, self.right_forward],
                        GPIO.LOW)
            
        elif direction == 'soft_left':
            speed = STANDARD_SPEED * 1.2
            self.right_pwm.ChangeDutyCycle(speed)
            GPIO.output([self.left_forward, self.right_forward],
                        GPIO.HIGH)
            GPIO.output([self.left_reverse, self.right_reverse],
                        GPIO.LOW)
            
        elif direction == 'soft_right':
            speed = STANDARD_SPEED * 1.2
            self.left_pwm.ChangeDutyCycle(speed)
            GPIO.output([self.left_forward, self.right_forward],
                        GPIO.HIGH)
            GPIO.output([self.left_reverse, self.right_reverse],
                        GPIO.LOW)
            
        elif direction == 'hard_left':
            speed = STANDARD_SPEED * 1.40
            self.right_pwm.ChangeDutyCycle(speed)
            GPIO.output([self.left_forward, self.right_forward],
                        GPIO.HIGH)
            GPIO.output([self.left_reverse, self.right_reverse],
                        GPIO.LOW)
            
        elif direction == 'hard_right':
            speed = STANDARD_SPEED * 1.40
            self.left_pwm.ChangeDutyCycle(speed)
            GPIO.output([self.left_forward, self.right_forward],
                        GPIO.HIGH)
            GPIO.output([self.left_reverse, self.right_reverse],
                        GPIO.LOW)
            
        if duration > -1:
            time.sleep(duration)
            self.stop()
            
    def shutdown(self):
        motors = GPIOPins['motors']
        for key in motors.keys():
            GPIO.output(list(motors[key].values()), GPIO.LOW)
        self.left_pwm.ChangeDutyCycle(STANDARD_SPEED)
        self.right_pwm.ChangeDutyCycle(STANDARD_SPEED)
            
            
            
if __name__ == '__main__':
    import easygui as eg
    
    directions = {'f': 'forward',
                  'r': 'reverse',
                  'hl': 'hard_left',
                  'hr': 'hard_right',
                  'sl': 'soft_left',
                  'sr': 'soft_right',
                  'spl': 'spin_left',
                  'spr': 'spin_right'}
    
    GPIO.setmode(GPIO.BCM)
    mc = MotorControl()
    while True:
        output = eg.enterbox("F, R, HL, HR, SL, SR, SPL, SPR, X to exit")
        if output.lower() == 'x':
            break
        mc.start(directions[output.lower()], duration=0.5)
        
    mc.shutdown()
    GPIO.cleanup()
    
    
    