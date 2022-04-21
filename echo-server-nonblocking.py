import socket
import threading
import time
from _socket import SocketType
from typing import Tuple

HOST = "127.0.0.1"
PORT = 65432


def echo(conn: SocketType, addr: Tuple):
    with conn:
        while True:
            try:
                data = conn.recv(1024)
            except BlockingIOError:
                time.sleep(1)
                continue

            if not data:
                print(f"Disconnected by {addr}")
                break

            print(f"{addr[0]}:{addr[1]} > Receive data: {data}")
            conn.sendall(data)


threads = list()
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    s.setblocking(False)

    while True:
        try:
            connection, address = s.accept()
        except BlockingIOError:
            time.sleep(1)
            continue

        connection.setblocking(False)
        print(f"Connected by {address}")

        t = threading.Thread(target=echo, args=(connection, address))
        threads.append(t)
        t.start()









