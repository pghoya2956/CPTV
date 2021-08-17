import struct
import time
import threading

import cv2
import numpy as np
import speech_recognition as sr

SEM = threading.Semaphore(1)

# video
cap = cv2.VideoCapture('data/fight_sample.mp4')
# cap = cv2.VideoCapture('data/sample2.mp4')
# cap = cv2.VideoCapture(0)

def protocolMsg(id, level, length, data=None):
    # protocol message
    preamble = b'\x43\x50\x54\x56'  # ascii CPTV
    id = bytes([int(id)])  # camera id
    level = bytes([int(level)])  # danger behavior level
    length = struct.pack(">I", int(length)) # big endian
    header = preamble + id + level + length
    message = header

    if data:
        message += data

    return message

class WatchingStranger():
    def __init__(self, socket=None):
        self.socket = socket

        # tracker list
        self.trackerTypes = ['BOOSTING', 'MIL', 'KCF', 'TLD', 'MEDIANFLOW', 'GOTURN', 'MOSSE', 'CSRT']
        # kernel for morphology => 커널 크기를 조절하면 검은 구멍을 메우는 정도가 달라짐
        self.k = cv2.getStructuringElement(cv2.MORPH_RECT, (11, 11))
        # set rectangle color
        self.roiColor = (0, 255, 0)
        self.dangerColor = (0, 0, 255)

        # Load Yolo
        self.net_human = cv2.dnn.readNet("yolo/yolov3-spp.weights", "yolo/yolov3-spp.cfg")
        self.classes_human = []
        with open("yolo/coco.names", "r") as f:
            self.classes_human = [line.strip() for line in f.readlines()]
        self.layer_names_human = self.net_human.getLayerNames()
        self.output_layers_human = [self.layer_names_human[i[0] - 1] for i in self.net_human.getUnconnectedOutLayers()]

        ret, frame = cap.read()

        self.height, self.width, self.channels = frame.shape
        self.x, self.y, self.w, self.h = cv2.selectROI('DangerROI', frame, False)
        if self.w and self.h:
            self.originROI = [(self.x, self.y), (self.x+self.w, self.y+self.h)]
        cv2.destroyAllWindows()

        # 배경 제거 객체 생성
        self.fgbg = cv2.createBackgroundSubtractorMOG2(varThreshold=100)

        self.detectTime = 0
        self.detection = False
        self.tracking = False
        self.detectFrames = 0
        self.detectDuration = 5     # roi에서 이상 행동 감지 정의 시간
        self.tolerance = 0.7

        self.trackingDuration = 120     # tracking 후 수상한 사람 정의 시간
        self.reChkPeriod = 60       # tracking 객체 사람인지 아닌지 재탐색 주기

        # protocol message
        self.message = protocolMsg(id=1, level=1, length=0)

    def CreateTrackerByName(self, trackerType):
        # Create a tracker based on tracker name
        if trackerType == self.trackerTypes[0]:
            tracker = cv2.legacy.TrackerBoosting_create()
        elif trackerType == self.trackerTypes[1]:
            tracker = cv2.legacy.TrackerMIL_create()
        elif trackerType == self.trackerTypes[2]:
            tracker = cv2.legacy.TrackerKCF_create()
        elif trackerType == self.trackerTypes[3]:
            tracker = cv2.legacy.TrackerTLD_create()
        elif trackerType == self.trackerTypes[4]:
            tracker = cv2.legacy.TrackerMedianFlow_create()
        elif trackerType == self.trackerTypes[5]:
            tracker = cv2.legacy.TrackerGOTURN_create()
        elif trackerType == self.trackerTypes[6]:
            tracker = cv2.legacy.TrackerMOSSE_create()
        elif trackerType == self.trackerTypes[7]:
            tracker = cv2.legacy.TrackerCSRT_create()
        else:
            tracker = None
            print('Incorrect tracker name')
            print('Available trackers are:')
            for t in self.trackerTypes:
                print(t)

        return tracker

    def CheckStranger(self, frame):
        '''
        :return: roi should be returned nparray for if brunch in main func
        '''
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        roi = np.zeros(shape=5)

        roiFrame = frame[self.y:self.y + self.h, self.x:self.x + self.w]

        # 배경 제거 마스크 계산
        # 미리 설정된 roi만 배경차분으로 움직임 검출
        self.fgmask = self.fgbg.apply(roiFrame)
        # GaussianBlur 노이즈 제거
        blur = cv2.GaussianBlur(self.fgmask, (0, 0), 1.0)
        # closing => 희색 오브젝트에 있는 작은 검은색 구멍들을 메우는데 사용
        closing = cv2.morphologyEx(blur, cv2.MORPH_CLOSE, self.k)
        # binarization + Otsu thresholding
        ret, self.fgmask = cv2.threshold(closing, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        if self.fgmask.mean() != 127:
            # Frame*tolerance 이상의 프레임 탐지시 검출
            if not self.detection and not self.tracking and (self.detectFrames < (self.fps * self.detectDuration * self.tolerance)):
                # roi 안에 디텍션이 되었을 때 detectFrames 카운트
                self.detectFrames += 1
                print("There is something")
            elif not self.detection and not self.tracking:
                # 정해진 프레임(시간) 이상 움직임 감지되었을 때
                self.detection = True
                self.detectFrames = 0
                self.detectTime = time.time()
                print("Tic Toc")    # test

            # Stranger Detection의 Definition은 detectDuration 시간 이상 움직임이 감지된 경우
            if self.detection and ((time.time() - self.detectTime) > self.detectDuration):
                self.detectFrames = 0
                self.detection = False
                roi = roiFrame
                print("Try to Detect Human obj")    # test

        return roi

    def DetectHuman(self, frame):
        roi = []

        if len(frame):
            height, width, channels = frame.shape

            # Detecting objects locations(outs)
            blob = cv2.dnn.blobFromImage(frame, 0.00392, (320, 320), (0, 0, 0), True, crop=False)
            self.net_human.setInput(blob)
            outs = self.net_human.forward(self.output_layers_human)

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
                    label = str(self.classes_human[class_ids[i]])
                    if label == 'person':
                        x, y, w, h = boxes[i]
                        roi.append([self.x+x-20, self.y+y-15, w*2, h])
                        break
            if roi:
                # Select boxes
                bboxes = []

                for coordinate in range(len(roi)):
                    bbox = roi[coordinate]
                    bboxes.append(bbox)

                return bboxes

        return 0

    def CreateTracker(self, frame, bboxes):
        # Specify the tracker type
        trackerType = "MOSSE"

        # Create MultiTracker object
        multiTracker = cv2.legacy.MultiTracker_create()

        # Initialize MultiTracker
        for bbox in bboxes:
            try:
                multiTracker.add(self.CreateTrackerByName(trackerType), frame, bbox)
            except:
                pass

        return multiTracker

    def TraceStranger(self, frame, tracker):
        self.tracking = True
        chaseTime = time.time() - self.trackingStartTime

        # get updated location of objects in subsequent frames
        success, boxes = tracker.update(frame)

        # draw tracked objects
        for i, newbox in enumerate(boxes):
            # 60초에 한 번 tracking 중인 객체가 사람인지 아닌지 판단
            # 프레임에서 벗어났다면 사람이 아니라고 정의
            if (time.time()-self.trackingStartTime)%self.reChkPeriod < 1:
                x = int(newbox[0:1])
                y = int(newbox[1:2])
                w = int(newbox[2:3])
                h = int(newbox[3:4])
                reChkROI = frame[y:y + h, x:x + w]
                if not self.DetectHuman(reChkROI):
                    self.tracking = False
                    chaseTime = 0

            p1 = (int(newbox[0]), int(newbox[1]))
            p2 = (int(newbox[0] + newbox[2]), int(newbox[1] + newbox[3]))
            cv2.rectangle(frame, p1, p2, self.dangerColor, 3, 1)        # stranger tracker 사각형 그리기
            cv2.putText(frame, '{0:0.1f} Sec'.format((time.time() - self.trackingStartTime)),
                        (int(newbox[0]), int(newbox[1]) + 30), cv2.FONT_HERSHEY_PLAIN, 2, self.dangerColor, 3)

        return chaseTime

    def main(self, tID):
        try:
            bboxes = []
            chaseTime = 0
            multiTracker = 0

            while cap.isOpened():
                SEM.acquire()
                ret, frame = cap.read()
                SEM.release()

                if not ret:
                    break

                roi = self.CheckStranger(frame)

                if (roi.mean() != 0) and not self.tracking:
                    bboxes = self.DetectHuman(roi)

                if bboxes and not self.tracking:
                    multiTracker = self.CreateTracker(frame, bboxes)
                    self.trackingStartTime = time.time()
                    print('DANGEROUS!!!')   # test

                if multiTracker:
                    chaseTime = self.TraceStranger(frame, multiTracker)

                if chaseTime > self.trackingDuration:
                    print('Really Really DANGEROUS!!!') # test
                    bboxes = []
                    chaseTime = 0
                    multiTracker = 0
                    self.tracking = False
                    if self.socket != None:
                        self.socket.send(self.message)

                if not self.tracking:
                    bboxes = []
                    chaseTime = 0
                    multiTracker = 0

                cv2.rectangle(frame, self.originROI[0], self.originROI[1], self.roiColor, 2)  # 기존 roi 사각형 그리기, test
                cv2.putText(frame, 'Target Place', self.originROI[0], cv2.FONT_HERSHEY_PLAIN, 2, self.roiColor, 2)  # test
                cv2.imshow('stranger', frame)   # test
                cv2.imshow('bgsub', self.fgmask)    # test
                if cv2.waitKey(1) & 0xff == 27: # test
                    break   # test

        except Exception as e:
            print(e)
            cv2.destroyAllWindows()
            cap.release()

class DetectingViolence():
    def __init__(self, socket=None):
        self.socket = socket

        # Load fight model
        self.net_fight = cv2.dnn.readNet("yolo/fight.weights", "yolo/fight.cfg")
        self.classes_fight = []
        with open("yolo/fight.names", "r") as f:
            self.classes_fight = [line.strip() for line in f.readlines()]
        self.layer_names_fight = self.net_fight.getLayerNames()
        self.output_layers_fight = [self.layer_names_fight[i[0] - 1] for i in self.net_fight.getUnconnectedOutLayers()]

        # set rectangle color
        self.dangerColor = (0, 0, 255)

        # protocol message
        self.message = protocolMsg(id=1, level=4, length=0)

    def DetectFight(self):
        stime = time.time()

        while cap.isOpened():
            SEM.acquire()
            ret, frame = cap.read()
            SEM.release()

            if not ret:
                break

            # if len(frame) and (time.time()-stime) % 1.5 < 1:
            if (time.time()-stime) % 1.5 < 1:
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
                        if label == 'fight':
                            print(label)    # test
                            x, y, w, h = boxes[i]   # test
                            cv2.rectangle(frame, (x, y), (x + w, y + h), self.dangerColor, 3, 1)  # stranger tracker 사각형 그리기, test
                            if self.socket != None:
                                self.socket.send(self.message)
                            break

            cv2.imshow('fight', frame)  # test
            if cv2.waitKey(1) & 0xff == 27:     # test
                break       # test

    def main(self, tID):
        self.DetectFight()

class VoiceDetection():
    def __init__(self, socket=None):
        self.socket = socket

        self.init_rec = sr.Recognizer()
        self.wordList = ['경찰', '불러', '살려',
                    '무서워', '제발', '누구',
                    '그만', '어딜', '도망',
                    '뭐야', '놔', '놓으',
                    '뭐야', '죽을', '죽어',
                    '뒤질', '뒤지고', '맞을',
                    '따라와', '따라', '조용',
                    '닥쳐', '죽여', '살고',
                    '싫어', '하지마', '하지'
                    '아파', '때려', '때리']

        # protocol message
        self.message = protocolMsg(id=1, level=4, length=0)

        print("Let's speak!!")

    def parseVoice(self):
        try:
            with sr.Microphone() as source:
                print("Tell something")
                audio_data = self.init_rec.record(source, duration=5)
                print("Recognizing your text.............")
                text = self.init_rec.recognize_google(audio_data, language='ko-KR')

                # text에 경찰이라는 단어가 포함되면 위치를 출력(0 이상), 아니면 -1 출력
                sign = text.split(' ')  # 띄어쓰기 기준으로 파싱

                for word in sign:  # sign 리스트 인덱스 요소를 하나식 반환
                    wordDetection = list(filter(lambda x: word in x, self.wordList))
                    if wordDetection:
                        if self.socket != None:
                            self.socket.send(self.message)
                        print(word)     # test
                        break

        except Exception as e:
            print(e)
            pass

    def main(self, tID):
        try:
            while True:
                self.parseVoice()
        except Exception as e:
            print(e)
