import CPTV

if __name__ == '__main__':
    # 모듈 객체 생성
    # p1 = CPTV.WatchingStranger()
    # p2 = CPTV.DetectingViolence()
    p3 = CPTV.VoiceDetection()
    # p4 = CPTV.DetectingWeapon()

    # module test
    # p1.main(1)
    # p2.main(2)
    p3.main(3)
    # p4.main(4)

    # # Threading test
    # t1 = threading.Thread(target=p1.main, args=(1,))
    # t2 = threading.Thread(target=p2.main, args=(2,))
    # t3 = threading.Thread(target=p3.main, args=(3,))
    #
    # threads = [t1, t2, t3]
    #
    # for th in threads:
    #     th.daemon = True
    #     th.start()
    #
    # for th in threads:
    #     th.join()
