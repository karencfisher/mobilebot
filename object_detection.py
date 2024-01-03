import cv2
import time
from pathlib import Path
from picamera.array import PiRGBArray
from picamera import PiCamera
from talker import talker


class ObjectDetection:
    def __init__(self, objects, threshold, flag, commandQueue, display=True):
        self.flag = flag
        self.commandQueue = commandQueue
        self.objects = objects
        self.threshold = threshold
        self.display = display
        self.looking = True
        
        
        self.talker = talker()

        configPath = 'model/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
        weightsPath = 'model/frozen_inference_graph.pb'
        self.net = cv2.dnn_DetectionModel(weightsPath, configPath)
        self.net.setInputSize(320,320)
        self.net.setInputScale(1.0/ 127.5)
        self.net.setInputMean((127.5, 127.5, 127.5))
        self.net.setInputSwapRB(True)

        with open('model/coco.names') as FILE:
            self.class_names = FILE.read().rstrip("\n").split("\n")


    def __getObjects(self, img):
        classIds, confs, bbox = self.net.detect(img, confThreshold=self.threshold, nmsThreshold=0.2)
        objectInfo = []
        if len(classIds) != 0:
            for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
                className = self.class_names[classId - 1]
                if className in self.objects:
                    objectInfo.append([box, className])
        return objectInfo

    def run(self):
        camera = PiCamera()
        camera.resolution = (320, 320)
        camera.framerate = 32
        raw_capture = PiRGBArray(camera, size=(320, 320))
        time.sleep(0.1)
        
        start_time = time.time()
        frame_count = 0

        for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
            img = frame.array
            objectInfo = self.__getObjects(img)
            # print(objectInfo)
            
            self.__dispatch(objectInfo, img)
            
            if self.display:
                frame_count += 1
                fps = round(frame_count / (time.time() - start_time), 2)
                cv2.putText(img, str(fps) + " FPS", (20, 20), 
                             cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 255), 2)

                cv2.imshow("output", img)
                cv2.waitKey(1)
                
            raw_capture.truncate(0)
                
            if not self.flag.value:
                break

        if self.display:
            cv2.destroyAllWindows()
        camera.close()
            
    def __dispatch(self, objectInfo, img):
        if len(objectInfo) == 0:
            if not self.looking:
                self.talker.talk("I no longer see the cat!")
                # self.commandQueue.put(('resume', None))
                self.looking = True
            return
        
        largest = 0
        for index in range(len(objectInfo)):
            area = objectInfo[index][0][2] * objectInfo[index][0][3]
            if area > largest:
                largest = area
                largest_index = index
            
        if self.display:
            for index in range(len(objectInfo)):
                if index == largest_index:
                    color = (0, 0, 255)
                else:
                    color = (255, 0, 0)
                cv2.rectangle(img, objectInfo[index][0], color=color, thickness=2)
                
        if self.looking:
            self.commandQueue.put(('halt', None))
            self.looking = False
            self.talker.talk("I see the cat!")
            
           
#        center_x = objectInfo[largest_index][0][0] + objectInfo[largest_index][0][2] / 2
#        if objectInfo[largest_index][0][2] >= 115 * 0.8:
#            self.commandQueue.put('stop')
#        elif center_x < 115 - objectInfo[largest_index][0][2] / 2:
#            self.commandQueue.put(('veer_right', None))
#        elif center_x > 115 + objectInfo[largest_index][0][2] / 2:
#            self.commandQueue.put(('veer_left', None))
#        else:
#            self.commandQueue.put(('forward', None))
        


