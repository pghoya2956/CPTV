from socket import *
import ftplib
import threading
import cv2
import time

VIDEO_STATE = 'cur'
SEND_WAIT = False

class RecordingVideo():
    def __init__(self, saveTime=30):
        self.saveTime = saveTime

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
            print(e)
            pass

    def main(self, tID):
        global VIDEO_STATE

        try:
            while True:  # 무한 루프
                if VIDEO_STATE == 'cur' and not SEND_WAIT:
                    self.recordCam('prev')
                    VIDEO_STATE = 'prev'
                elif VIDEO_STATE == 'prev' and not SEND_WAIT:
                    self.recordCam('cur')
                    VIDEO_STATE = 'cur'

        except Exception as e:
            self.cap.release()
            print(e)

class FTPClient():
    def __init__(self):
        # pi server
        self.HOST = '127.0.0.1'
        self.PORT = 2204
        self.ADDR = (self.HOST, self.PORT)
        self.BUFSIZ = 10

        # server socket for jetson nano
        self.serverSocket = socket(AF_INET, SOCK_STREAM)
        # 소켓 주소 정보 할당
        self.serverSocket.bind(self.ADDR)
        print('bind')
        # 연결 수신 대기 상태
        self.serverSocket.listen(100)
        print('listen')
        # 연결 수락
        self.clientSocket, addr_info = self.serverSocket.accept()
        print('accept')

        # for Web server
        self.WEB_HOST = '127.0.0.1'
        self.WEB_PORT = 21

        # for Web FTP server
        self.id = 'CPTV_admin'
        self.passwd = '2204'

        self.prevFin = False
        self.curFin = False
        self.msgDictionary = []

    def recvMsg(self, tID):
        global SEND_WAIT, SEND_COUNT

        while True:
            if not self.prevFin and not self.curFin:
                message = self.clientSocket.recv(self.BUFSIZ)
                print(message)

            if message:
                SEND_WAIT = True
                if VIDEO_STATE=='prev' and not self.prevFin:
                    self.SendData(VIDEO_STATE, message)
                    self.prevFin = True
                elif VIDEO_STATE=='cur' and not self.curFin:
                    self.SendData(VIDEO_STATE, message)
                    self.curFin = True
                SEND_WAIT = False
            if self.prevFin and self.curFin:
                self.prevFin = False
                self.curFin = False
                message = 0


    def SendData(self, filename, message):
        # saved file
        filename = filename + 'Cam.mp4'

        self.msgDictionary = ({'preamble': message[0:4],
                               'id': message[4],
                               'level': message[5],
                               'length': message[6:10]})

        self.ftp = ftplib.FTP()
        self.ftp.connect(self.WEB_HOST, self.WEB_PORT)
        self.ftp.login(self.id, self.passwd)
        self.ftp.cwd("./")

        self.myfile = open(filename, 'rb')
        self.ftp.storbinary('STOR ' + filename, self.myfile)

        # message 파싱 후 ftp 파일 업로드 하고 이름을 파싱한 대로 변경하기
        newFileName = str(time.time()) + '_' + str(self.msgDictionary['id']) + \
                      '_' + str(self.msgDictionary['level']) + '.mp4'
        self.ftp.rename(filename, newFileName)

        self.myfile.close()
        self.ftp.close

if __name__ == '__main__':
    # record video and audio
    p1 = RecordingVideo(saveTime=3)
    p2 = FTPClient()

    # Threading
    t1 = threading.Thread(target=p1.main, args=(1,))
    t2 = threading.Thread(target=p2.recvMsg, args=(2,))
    t1.daemon = True
    t2.daemon = True

    t1.start()
    t2.start()

    while True:
        time.sleep(1)  # thread 간의 우선순위 관계 없이 다른 thread에게 cpu를 넘겨줌(1 일때)
        pass  # sleep(0)은 cpu 선점권을 풀지 않음

