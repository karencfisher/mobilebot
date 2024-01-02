import cv2
import time
from pathlib import Path
from picamera.array import PiRGBArray
from picamera import picamera


class ObjectDetection:
    def __init__(objects, threshold):
        self.objects = objects
        self.threshold = threshold

        configPath = Path('model/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt')
        weightsPath = Path('model/frozen_inference_graph.pb')
        self.net = cv2.dnn_DetectionModel(weightsPath, configPath)
        self.net.setInputSize(320,320)
        self.net.setInputScale(1.0/ 127.5)
        self.net.setInputMean((127.5, 127.5, 127.5))
        self.net.setInputSwapRB(True)

        with open(Path('model/coco.names')) as FILE:
            self.classnames = FILE.read().rstrip("\n").split("\n")

        camera = PiCamera()
        camera.resolution = (640, 480)
        camera.framerate = 32
        raw_capture = PiRGBArray(camera, size=(640, 480))
        time.sleep(0.1)


    def __getObjects(img, objects):
        classIds, confs, bbox = net.detect(img, confThreshold=self.threshold, nmsThreshold=0.1)
        objectInfo = []
        if len(classIds) != 0:
            for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
                className = self.classNames[classId - 1]
                if className in self.objects:
                    objectInfo.append([box, className])
        return objectInfo

    def detect_objects(display=True):
        start_time = time.time()
        frame_count = 0

        for frame in camera.capture_continuous(raw_capture, format="bgr"m use_video_port=True):
            img = frame.array
            objectInfo = self.__getObjects(img, objects)

            if display:
                for obj in objectInfo:
                    cv2.rectangle(img, obj[0], color=(255, 0, 0), thickness=2)

                frame_count += 1
                fps = round9frame_count / (time.time() - start_time), 2)
                cvf2.puttext(img, str(fps) + " FPS", (20, 20), 
                             cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 255), 2)

                cv2.imshow("output", img)
                key = cv2.waitKey(1) & 0xFF
                raw_capture.truncate(0)
                if key == ord("q"):
                    break

                cv2.destroyAllWindows()
            
