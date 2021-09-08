from socket import *
import struct
import speech_recognition as sr

# socket
HOST = '127.0.0.1'
PORT = 10000
BUFSIZE = 12
ADDR = (HOST, PORT)

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

class VoiceDetection():
    def __init__(self, socket):
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
                        self.socket.send(self.message)
                        print(word)
                        break

        except Exception as e:
            print(e)
            pass

    def main(self):
        try:
            while True:
                self.parseVoice()
        except Exception as e:
            print(e)

if __name__ == '__main__':
    clientSocket = socket(AF_INET, SOCK_STREAM)# 서버에 접속하기 위한 소켓을 생성한다.\
    clientSocket.connect(ADDR)  # 서버에 접속을 시도한다.
    clientSocket.send('Hello!'.encode())  # 서버에 메시지 전달

    p2 = VoiceDetection(clientSocket)
    p2.main()

    # 소켓 종료
    socket.close()
