import threading
from socket import *
import CPTV

# socket
HOST = '127.0.0.1'
PORT = 22042
ADDR = (HOST, PORT)

if __name__ == '__main__':
    try:
        clientSocket = socket(AF_INET, SOCK_STREAM)     # 서버에 접속하기 위한 소켓을 생성한다.
        clientSocket.connect(ADDR)  # 서버에 접속을 시도한다.
        print('Socket connect')

        # 모듈 객체 생성
        p1 = CPTV.WatchingStranger(clientSocket)
        p2 = CPTV.DetectingViolence(clientSocket)
        p3 = CPTV.VoiceDetection(clientSocket)

        # Threading
        t1 = threading.Thread(target=p1.main, args=(1,))
        t2 = threading.Thread(target=p2.main, args=(2,))
        t3 = threading.Thread(target=p3.main, args=(3,))

        threads = [t1, t2, t3]

        for th in threads:
            th.daemon = True
            th.start()

        for th in threads:
            th.join()

    except Exception as e:
        # 소켓 종료
        clientSocket.send(str(e).encode())  # 서버에 메시지 전달
        clientSocket.close()
