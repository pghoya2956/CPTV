import socket                   # Import socket module
import time

s = socket.socket()             # Create a socket object
host = '127.0.0.1'              # Get local machine name
port = 22041                    # Reserve a port for your service every new transfer wants a new port or you must wait.
s.bind((host, port))            # Bind to the port
s.listen(5)  # Now wait for client connection.
print('Server listening....')
conn, addr = s.accept()  # Establish connection with client.
print('Socket connect!')

while True:
    newName = conn.recv(64)
    if len(newName) > 0:
        newName = newName.decode()
        newName = newName.split('_')
        fileName = time.strftime('%Y-%m-%d_%I_%M_%S%p', time.localtime(float(newName[0]))) + "_" + newName[1] + "_" + newName[2]
        print("File Name : ", fileName)

        conn.send('get'.encode())
        fsize = int(conn.recv(32).decode())
        print("fsize : ", fsize)

        conn.send('start'.encode())

        with open(fileName, 'wb') as f:
            print('receiving data...')

            data = conn.recv(fsize)

            # write data to a file
            f.write(data)

        newName = 0
        fsize = 0
        print('Done receive')
conn.close()
