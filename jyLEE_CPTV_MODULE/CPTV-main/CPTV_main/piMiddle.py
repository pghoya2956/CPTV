from socket import *
import os
import threading
import cv2
import time

VIDEO_STATE = 'cur'
SEND_WAIT = False

SEM = threading.Semaphore(1)

class RecordingVideo():
    def __init__(self, saveTime=30):
        self.saveTime = saveTime

        # self.cap = cv2.VideoCapture("data/sample2.mp4")
        self.cap = cv2.VideoCapture(0)

        if not self.cap.isOpened():
            print("Camera open failed!")
            exit()

        # fourcc 값 받아오기, *는 문자를 풀어쓰는 방식, *'mp4v' == 'm', 'p', '4', 'v'
        self.fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        # self.main()

    def recordCam(self, state):
        try:
            videoName = state + 'Cam.mp4'
            recorder = cv2.VideoWriter(videoName, self.fourcc, 30, (640, 480))

            if not recorder.isOpened():
                print(state + 'video File open failed!')
                self.cap.release()
                exit()

            stime = time.time()
            while True:
                if (time.time() - stime) > self.saveTime:
                    break

                ret, frame = self.cap.read()  # 카메라의 ret, frame 값 받아오기
                if not ret:
                    break

                recorder.write(frame)
                cv2.imshow(state, frame)
                if cv2.waitKey(1) & 0xFF == 27:  # esc를 누르면 강제 종료
                    break
            recorder.release()
            cv2.destroyAllWindows()
        except Exception as e:
            print("recordCam : ", e)
            pass

    def main(self, tID):
        global VIDEO_STATE

        while True:  # 무한 루프
            try:
                if VIDEO_STATE == 'cur' and not SEND_WAIT:
                    self.recordCam('prev')
                    VIDEO_STATE = 'prev'
                elif VIDEO_STATE == 'prev' and not SEND_WAIT:
                    self.recordCam('cur')
                    VIDEO_STATE = 'cur'
            except Exception as e:
                # self.cap.release()
                # self.cap = cv2.VideoCapture(0)
                print("RecordingVideo main : ", e)

class WebClient():
    def __init__(self):
        # for Web client
        self.WEB_HOST = '192.168.0.6'
        self.WEB_PORT = 22041
        self.WEB_ADDR = (self.WEB_HOST, self.WEB_PORT)
        self.webClient = socket(AF_INET, SOCK_STREAM)  # 서버에 접속하기 위한 소켓을 생성한다.
        self.webClient.connect(self.WEB_ADDR)  # 서버에 접속을 시도한다.
        print('Web Socket connect!')

        # pi server
        # self.HOST = '127.0.0.1'
        self.HOST = '192.168.0.6'
        self.PORT = 22042
        self.ADDR = (self.HOST, self.PORT)
        self.BUFSIZ = 16

        # server socket for jetson nano
        self.serverSocket = socket(AF_INET, SOCK_STREAM)
        self.serverSocket.bind(self.ADDR)
        print('bind')
        self.serverSocket.listen(100)
        print('listen')
        self.clientSocket, addr_info = self.serverSocket.accept()
        print('accept')

        self.prevFin = False
        self.curFin = False
        self.msgDictionary = []

    def recvMsg(self, tID):
        global SEND_WAIT, SEND_COUNT

        while True:
            try:
                if not self.prevFin and not self.curFin:
                    message = self.clientSocket.recv(self.BUFSIZ)
                    print(message)

                if message:
                    SEND_WAIT = True
                    SEM.acquire()

                    if VIDEO_STATE=='prev' and not self.prevFin:
                        self.SendData(VIDEO_STATE, message)
                        self.prevFin = True
                    elif VIDEO_STATE=='cur' and not self.curFin:
                        self.SendData(VIDEO_STATE, message)
                        self.curFin = True

                    SEM.release()
                    SEND_WAIT = False

                if self.prevFin and self.curFin:
                    self.prevFin = False
                    self.curFin = False
                    message = 0

                print("Recording")

            except Exception as e:
                print("recvMsg : ", e)
                pass

    def SendData(self, filename, message):
        # saved file
        filename = filename + 'Cam.mp4'
        self.msgDictionary = ({'preamble': message[0:4],
                               'id': message[4],
                               'level': message[5],
                               'length': message[6:10]})

        # message 파싱 후 ftp 파일 업로드 하고 이름을 파싱한 대로 변경하기
        newFileName = str(time.time()) + '_' + str(self.msgDictionary['id']) + \
                      '_' + str(self.msgDictionary['level']) + '.mp4'

        self.webClient.send(newFileName.encode())
        self.webClient.recv(self.BUFSIZ)

        try:    # 파일 없는 초기 경우 예외처리
            f = open(filename, 'rb')
            filesize = os.path.getsize(filename)
            self.webClient.send(str(filesize).encode())

            startSending = self.webClient.recv(self.BUFSIZ).decode()
            if startSending == 'start':
                data = f.read(filesize)
                self.webClient.send(data)
                f.close()

                print("Send Complete")
        except Exception as e:
            print("SendData : ", e)
            pass

if __name__ == '__main__':
    try:
        # record video and audio
        p1 = RecordingVideo(saveTime=3)
        p2 = WebClient()

        # Threading
        t1 = threading.Thread(target=p1.main, args=(1,))
        t2 = threading.Thread(target=p2.recvMsg, args=(2,))

        threads = [t1, t2]

        for th in threads:
            th.daemon = True
            th.start()

        for th in threads:
            th.join()

    except Exception as e:
        print("__main__ : ", e)
