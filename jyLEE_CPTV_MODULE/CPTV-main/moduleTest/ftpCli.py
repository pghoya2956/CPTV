import ftplib
import os
import time

filename = "curCam.mp4"
ftp = ftplib.FTP()

ftp.connect("127.0.0.1", 21)
ftp.login("CPTV_admin", "2204")
ftp.cwd("./")

myfile = open(filename, 'rb')
ftp.storbinary('STOR ' + filename, myfile)
newFileName = str(time.time()) + '_.mp4'
ftp.rename(filename, newFileName)

myfile.close()
ftp.close