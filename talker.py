import os

class talker():
    
    def __init__(self, pin=18, voice='en', gender='f', speed=115):
        self.pin = pin
        self.voice = voice
        self.gender = gender
        self.speed = str(speed)
        os.system('gpio -g mode ' + str(self.pin) + ' ALT5')
    
    def talk(self, text):
        settings = '-v' + self.voice + '+' + self.gender + '4 -s' + self.speed
        command = 'espeak ' + settings + ' \"' + text +'\" 2>/dev/null'
        os.system(command)
        
    def cleanup(self):
        os.system('gpio -g mode ' + str(self.pin) + ' in')
        

def main():
    t = talker(speed=100)
    t.talk('This is a test. It is only a test. I have nothing to say to you anyway')
    t.cleanup()
    
if __name__ == '__main__':
    main()