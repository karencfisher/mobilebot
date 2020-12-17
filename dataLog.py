import csv

class DataLog:
    def __init__(self):
        self.log = []
    
    def log_data(self, sensor_data, action):
        self.log.append([sensor_data['left_rf'],
                         sensor_data['front_rf'],
                         sensor_data['right_rf'],
                         sensor_data['left_ir'],
                         sensor_data['right_ir'],
                         sensor_data['gyro'],
                         sensor_data['accel'],
                         action])
        
    def dump(self, filepath):
        headers = ['left_rf',
                   'front_lf',
                   'right_rf',
                   'left_ir',
                   'right_ir',
                   'gyro',
                   'accel',
                   'action']
        
        with open(filepath, 'w') as csvfile:   
            csvwriter = csv.writer(csvfile)  
            csvwriter.writerow(headers)    
            csvwriter.writerows(self.log)
            
    def load(self, filepath):
        with open(filepath, 'r') as csvfile:
            data = csv.reader(csvfile)
            for i, line in enumerate(data):
                if i > 0:
                    self.log.append(line)