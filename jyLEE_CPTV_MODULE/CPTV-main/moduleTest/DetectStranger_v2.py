import cv2
import numpy as np
import time

cap = cv2.VideoCapture('fight.mp4')
# cap = cv2.VideoCapture('sample.mp4')
# cap = cv2.VideoCapture(0)

class WatchingStranger():
    def __init__(self):
        # tracker list
        self.trackerTypes = ['BOOSTING', 'MIL', 'KCF', 'TLD', 'MEDIANFLOW', 'GOTURN', 'MOSSE', 'CSRT']
        # kernel for morphology => 커널 크기를 조절하면 검은 구멍을 메우는 정도가 달라짐
        self.k = cv2.getStructuringElement(cv2.MORPH_RECT, (11, 11))
        # set rectangle color
        self.roiColor = (0, 255, 0)
        self.dangerColor = (0, 0, 255)

        # Load Yolo
        self.net = cv2.dnn.readNet("yolov3-spp.weights", "yolov3-spp.cfg")
        self.classes = []
        with open("coco.names", "r") as f:
            self.classes = [line.strip() for line in f.readlines()]
        self.layer_names = self.net.getLayerNames()
        self.output_layers = [self.layer_names[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]

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
        self.detectDuration = 5
        self.tolerance = 0.7

        self.trackingDuration = 120

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
            if not self.detection and not self.tracking and (self.detectFrames < (self.fps * self.detectDuration * self.tolerance)):
                # roi 안에 디텍션이 되었을 때 detectFrames 카운트
                self.detectFrames += 1
                print("There is something")
            elif not self.detection and not self.tracking:
                # 정해진 프레임(시간) 이상 움직임 감지되었을 때
                self.detection = True
                self.detectFrames = 0
                self.detectTime = time.time()
                print("Tic Toc")

            # Stranger Detection의 Definition은 detectDuration 시간 중 tolerance 이상 움직임이 감지된 경우
            if self.detection and ((time.time() - self.detectTime) > self.detectDuration):
                self.detectFrames = 0
                self.detection = False
                roi = roiFrame
                print("Try to Detect Human obj")

        return roi

    def DetectHuman(self, frame):
        roi = []

        if len(frame):
            height, width, channels = frame.shape

            # Detecting objects locations(outs)
            blob = cv2.dnn.blobFromImage(frame, 0.00392, (320, 320), (0, 0, 0), True, crop=False)
            self.net.setInput(blob)
            outs = self.net.forward(self.output_layers)

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
                    label = str(self.classes[class_ids[i]])
                    if label == 'person':
                        x, y, w, h = boxes[i]
                        roi.append([self.x+x, self.y+y, w, h])
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
            if (time.time()-self.trackingStartTime)%60 < 0:
                x = int(boxes[0][0])
                y = int(boxes[0][1])
                w = int(boxes[0][2])
                h = int(boxes[0][3])
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

    def main(self):
        try:
            bboxes = []
            chaseTime = 0
            multiTracker = 0

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                roi = self.CheckStranger(frame)

                if (roi.mean() != 0) and not self.tracking:
                    bboxes = self.DetectHuman(roi)

                if bboxes and not self.tracking:
                    multiTracker = self.CreateTracker(frame, bboxes)
                    self.trackingStartTime = time.time()
                    print('DANGEROUS!!!')

                if multiTracker:
                    chaseTime = self.TraceStranger(frame, multiTracker)

                if chaseTime > self.trackingDuration:
                    print('Really Really DANGEROUS!!!')
                    bboxes = []
                    chaseTime = 0
                    multiTracker = 0
                    self.tracking = False
                    # send socket message

                cv2.rectangle(frame, self.originROI[0], self.originROI[1], self.roiColor, 2)  # 기존 roi 사각형 그리기
                cv2.putText(frame, 'Target Place', self.originROI[0], cv2.FONT_HERSHEY_PLAIN, 2, self.roiColor, 2)
                cv2.imshow('frame', frame)
                cv2.imshow('bgsub', self.fgmask)
                if cv2.waitKey(1) & 0xff == 27:
                    break
        except Exception as e:
            print(e)
            cap.release()
            cv2.destroyAllWindows()

if __name__ == '__main__':
    p1 = WatchingStranger()
    p1.main()
