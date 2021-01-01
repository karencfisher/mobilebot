import csv

class DataLog:
    def __init__(self):
        self.log = []
    
    def log_data(self, time_stamp, sensor_data, action):
        self.log.append([time_stamp,
                         sensor_data['left_rf'],
                         sensor_data['front_rf'],
                         sensor_data['right_rf'],
                         sensor_data['left_ir'],
                         sensor_data['right_ir'],
                         sensor_data['gyro_x'],
                         sensor_data['gyro_y'],
                         sensor_data['gyro_z'],
                         sensor_data['accel_x'],
                         sensor_data['accel_y'],
                         sensor_data['accel_z'],
                         action])
        
    def dump(self, filepath):
        headers = ['time_stamp',
                   'left_rf',
                   'front_rf',
                   'right_rf',
                   'left_ir',
                   'right_ir',
                   'gyro_x',
                   'gyro_y',
                   'gyro_z',
                   'accel_x',
                   'accel_y',
                   'accel_z',
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