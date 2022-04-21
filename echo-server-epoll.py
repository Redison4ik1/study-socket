import select
from datetime import datetime
from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR
import time
from collections import deque
from typing import Dict, List

HOST: str = "127.0.0.1"
PORT: int = 65432

global_queue: Dict[int, deque] = {}
connections: Dict[int, socket] = {}

with socket(AF_INET, SOCK_STREAM) as server_sock:
    server_sock.bind((HOST, PORT))
    server_sock.listen(100)
    server_sock.setblocking(False)

    epoll = select.epoll()
    epoll.register(server_sock.fileno(), select.EPOLLIN)

    try:
        while True:
            events = epoll.poll(1)
            for fileno, event in events:
                # print(fileno)
                if fileno == server_sock.fileno():
                    new_conn, address = server_sock.accept()
                    print(f'Connected by {address} fd {new_conn.fileno()}')
                    connections[new_conn.fileno()] = new_conn
                    global_queue[new_conn.fileno()] = deque()
                    epoll.register(new_conn.fileno(), select.EPOLLIN)
                    continue

                address: tuple = connections[fileno].getpeername()
                if event & select.EPOLLIN:
                    if data := connections[fileno].recv(1024):
                        global_queue[fileno].append(data)
                        print(f"{datetime.now()} {address} > Receive data: {data}")
                        epoll.modify(fileno, select.EPOLLOUT)
                    else:
                        epoll.unregister(fileno)
                        connections[fileno].close()
                        del global_queue[fileno]
                        print(f"Disconnected by {address}")

                elif event & select.EPOLLOUT:
                    if global_queue[fileno]:
                        connections[fileno].send(global_queue[fileno].popleft())
                        print(f"{datetime.now()} {address} > Send data")
                    else:
                        epoll.modify(fileno, select.EPOLLIN)

    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")