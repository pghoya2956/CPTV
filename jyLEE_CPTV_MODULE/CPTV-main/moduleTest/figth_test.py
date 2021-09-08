import cv2
import numpy as np
import time

# video
# cap = cv2.VideoCapture('data/fight.mp4')
cap = cv2.VideoCapture('fight_sample2.mp4')
# cap = cv2.VideoCapture(0)

class WatchingStranger():
    def __init__(self):

        # kernel for morphology => 커널 크기를 조절하면 검은 구멍을 메우는 정도가 달라짐
        self.k = cv2.getStructuringElement(cv2.MORPH_RECT, (11, 11))
        # set rectangle color
        self.roiColor = (0, 255, 0)
        self.dangerColor = (0, 0, 255)

        # Load Yolo
        self.net_fight = cv2.dnn.readNet("yolo/fight.weights", "yolo/fight.cfg")
        self.classes_fight = []
        with open("yolo/fight.names", "r") as f:
            self.classes_fight = [line.strip() for line in f.readlines()]
        self.layer_names_fight = self.net_fight.getLayerNames()
        self.output_layers_fight = [self.layer_names_fight[i[0] - 1] for i in self.net_fight.getUnconnectedOutLayers()]

    def DetectFight(self):
        stime = time.time()

        while cap.isOpened():
            ret, frame = cap.read()

            # if len(frame) and (time.time()-stime) % 1.5 < 1:
            if len(frame) and (time.time()-stime) > 50:
                height, width, channels = frame.shape

                # Detecting objects locations(outs)
                blob = cv2.dnn.blobFromImage(frame, 0.00392, (320, 320), (0, 0, 0), True, crop=False)
                self.net_fight.setInput(blob)
                outs = self.net_fight.forward(self.output_layers_fight)

                # Showing informations on the screen
                class_ids = []
                confidences = []
                boxes = []
                for out in outs:
                    for detection in out:
                        scores = detection[5:]
                        class_id = np.argmax(scores)
                        confidence = scores[class_id]
                        if confidence > 0.5:
                            # Object detected
                            center_x = int(detection[0] * width)
                            center_y = int(detection[1] * height)
                            w = int(detection[2] * width)
                            h = int(detection[3] * height)
                            # Rectangle coordinates
                            x = int(center_x - w / 2)
                            y = int(center_y - h / 2)
                            boxes.append([x, y, w, h])
                            confidences.append(float(confidence))
                            class_ids.append(class_id)

                # 노이즈제거 => 같은 물체에 대한 박스가 많은것을 제거(Non maximum suppresion)
                indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

                '''
                Box : 감지된 개체를 둘러싼 사각형의 좌표
                Label : 감지된 물체의 이름
                Confidence : 0에서 1까지의 탐지에 대한 신뢰도
                '''
                # font = cv2.FONT_HERSHEY_PLAIN
                for i in range(len(boxes)):
                    if i in indexes:
                        label = str(self.classes_fight[class_ids[i]])
                        if label != 'person':
                            print(label)
                            x, y, w, h = boxes[i]
                            cv2.rectangle(frame, (x, y), (x+w, y+h), self.dangerColor, 3, 1)  # stranger tracker 사각형 그리기

            cv2.imshow('frame', frame)
            if cv2.waitKey(1) & 0xff == 27:
                break

p1 = WatchingStranger()
p1.DetectFight()