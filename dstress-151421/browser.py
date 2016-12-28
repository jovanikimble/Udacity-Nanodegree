import socket
import sys

HOST = 'localhost'
PORT = 10036
ADDR = (HOST, PORT)
BUFSIZE = 4096

conn = socket.create_connection(ADDR)
msg = sys.argv[1]
conn.send(msg)

# Receive data from the server.
data = conn.recv(BUFSIZE)
print(data)
with open('gen.html', 'w') as f:
    f.write(data)

conn.close()