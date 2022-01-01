from multiprocessing import Process, Queue

import easygui as eg

from control import RobotControl


robot_control = RobotControl()
log = robot_control.get_log()
result = eg.enterbox("Enter existing log file")
if result is not None:
    log.load(result)

command_queue = Queue()
control_process = Process(target=robot_control.run,
                                  args=(command_queue,))
control_process.start()
print('control process started')

while True:
    command = eg.enterbox("command: 'run (r)', 'stop (s)', 'exit (x)'")
    command_queue.put(command)
    if command == 'exit' or command == 'x':
        control_process.join()
        robot_control.shutdown()
        break
print('exited')

log.dump('test.csv')
    
        



