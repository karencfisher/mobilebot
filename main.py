import queue, threading

import easygui as eg

from control import RobotControl


robot_control = RobotControl()
command_queue = queue.Queue()
control_thread = threading.Thread(target=robot_control.run,
                                  args=(command_queue,))
control_thread.start()
print('control thread started')

while True:
    command = eg.enterbox("command: 'run', 'stop', 'exit'")
    command_queue.put(command)
    if command == 'exit':
        control_thread.join()
        robot_control.shutdown()
        break
print('exited')

log = robot_control.get_log()
log.dump('test.csv')
    
        



