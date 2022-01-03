STANDARD_SPEED = 50
INCREMENT = STANDARD_SPEED * 0.2
MINIMUM_DISTANCE = 30
SAMPLES = 10


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
    
    'left': {'l_fwd': None, 'l_rev': None, 'r_fwd': None, 'r_rev': None,
                  'left_accel': 0, 'right_accel': INCREMENT},
    
    'right': {'l_fwd': None, 'l_rev': None, 'r_fwd': None, 'r_rev': None,
                  'left_accel': INCREMENT, 'right_accel': 0},
}