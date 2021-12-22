STANDARD_SPEED = 50
MINIMUM_DISTANCE = 30


GPIOPins = {
    'ultrasonicRF': {
        'left': {
            'trigger': 25,
            'echo' : 12
        },

        'right': {
            'trigger': 5,
            'echo': 6
        },
        
        'front': {
            'trigger': 4,
            'echo': 17
        }
    },
    
    'IRSensors': {  
        'left': 22,
        'right': 27
    },

    'motors': {
        'left': {
            'enable': 21,
            'drive_n': 16,
            'drive_p': 20
        },
        
        'right': {
            'enable': 13,
            'drive_n': 19,
            'drive_p': 26
        }
    },
    
    'run_led': 24,
}
