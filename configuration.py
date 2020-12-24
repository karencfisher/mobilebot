STANDARD_SPEED = 70


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
            'drive_n': 20,
            'drive_p': 16
        },
        
        'right': {
            'enable': 13,
            'drive_n': 26,
            'drive_p': 19
        }
    }
}
