# All settings for the robot

# speed settings (in terns of duty cycles for PWM
# control of motors
STANDARD_SPEED = 50
INCREMENT = STANDARD_SPEED * 0.2

# interval between pinging sensors (in seconds)
INTERVAL = 0.5

# Minumum distance in front before turning
WARNING_DISTANCE = 30
MINIMUM_DISTANCE = 15

# difference in distance suggesting we're stuck
STUCK_THRESHOLD = 2

# Number of seconds before we determine robot is stuck
STUCK_TIMEOUT = 5

# Number of samples from ultrasonic sensors to average
SAMPLES = 10

# GPIO pin assignments
GPIOPins = {
    'ultrasonicRF': {
        'left': {'trigger': 25, 'echo' : 12},
        'right': {'trigger': 5, 'echo': 6},
        'front': {'trigger': 4, 'echo': 17}
    },
    
    'IRSensors': {'left': 22, 'right': 27},
    'motors': {
        'left': {'enable': 21, 'drive_n': 16, 'drive_p': 20},
        'right': {'enable': 13, 'drive_n': 19, 'drive_p': 26}
    },
    
    'indicators': {'run_led': 24}
}

# Defining different behaviors for the motors. Motor directions 1, 0, or None if no change
# in direction. Accel settings are adjustments to PWM cycle duty for each motor (speed). 0 if
# standard speed, -INCREMENT to deccelerate by that ratio, or INCREMENT to accelerate by same.
MotorSettings = {
    'stop': {'l_fwd': 0, 'l_rev': 0, 'r_fwd': 0, 'r_rev': 0, 'left_accel': 0, 'right_accel': 0},
    
    'forward': {'l_fwd': 1, 'l_rev': 0, 'r_fwd': 1, 'r_rev': 0, 'left_accel': 0, 'right_accel': 0},
    
    'reverse': {'l_fwd': 0, 'l_rev': 1, 'r_fwd': 0, 'r_rev': 1, 'left_accel': 0, 'right_accel': 0},
    
    'accelerate': {'l_fwd': None, 'l_rev': None, 'r_fwd': None, 'r_rev': None,
                   'left_accel': INCREMENT, 'right_accel': INCREMENT},
    
    'decelerate': {'l_fwd': None, 'l_rev': None, 'r_fwd': None, 'r_rev': None,
                   'left_accel': -INCREMENT, 'right_accel': -INCREMENT},
    
    'spin_left': {'l_fwd': 0, 'l_rev': 1, 'r_fwd': 1, 'r_rev': 0, 'left_accel': 0, 'right_accel': 0},
    
    'spin_right': {'l_fwd': 1, 'l_rev': 0, 'r_fwd': 0, 'r_rev': 1, 'left_accel': 0, 'right_accel': 0},

    'veer_left': {'l_fwd': None, 'l_rev': None, 'r_fwd': None, 'r_rev': None,
                  'left_accel': 0, 'right_accel': INCREMENT},
    
    'veer_right': {'l_fwd': None, 'l_rev': None, 'r_fwd': None, 'r_rev': None,
                  'left_accel': INCREMENT, 'right_accel': 0},
    
    'left': {'l_fwd': 0, 'l_rev': 0, 'r_fwd': 1, 'r_rev': 0, 'left_accel': 0, 'right_accel': 0},
    
    'right': {'l_fwd': 1, 'l_rev': 0, 'r_fwd': 0, 'r_rev': 0, 'left_accel': 0, 'right_accel': 0}
}
