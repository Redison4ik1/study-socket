# echo-client.py

import socket
import time
from random import randrange


HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

index = 1
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        my_str = f"Hello, world {index}"
        s.sendall(my_str.encode())
        data = s.recv(1024)

        print(f"Received {data!r}")
        index += 1
        # time.sleep(randrange(6))
        time.sleep(randrange(6)/100)
