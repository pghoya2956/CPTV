import socket                   # Import socket module

s = socket.socket()             # Create a socket object
host = '192.168.0.24'   # Get local machine name
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
        conn.send('get'.encode())
        fsize = int(conn.recv(32).decode())
        conn.send('start'.encode())

        with open(newName, 'wb') as f:
            print('receiving data...')

            data = conn.recv(fsize)

            # write data to a file
            f.write(data)

        newName = 0
        fsize = 0
        print('Done receive')
conn.close()
