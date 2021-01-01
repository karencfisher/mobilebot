import queue, threading

import easygui as eg

from control import RobotControl


robot_control = RobotControl()
log = robot_control.get_log()
result = eg.enterbox("Enter existing log file")
if result is not None:
    log.load(result)

command_queue = queue.Queue()
control_thread = threading.Thread(target=robot_control.run,
                                  args=(command_queue,))
control_thread.start()
print('control thread started')

while True:
    command = eg.enterbox("command: 'run (r)', 'stop (s)', 'exit (x)'")
    command_queue.put(command)
    if command == 'exit' or command == 'x':
        control_thread.join()
        robot_control.shutdown()
        break
print('exited')

log.dump('test.csv')
    
        



