import select
from datetime import datetime
from socket import socket, AF_INET, SOCK_STREAM
import time
from collections import deque
from typing import Dict, List

HOST: str = "127.0.0.1"
PORT: int = 65432

global_queue: Dict[tuple, deque] = {}

with socket(AF_INET, SOCK_STREAM) as server_sock:
    server_sock.bind((HOST, PORT))
    server_sock.listen(100)
    server_sock.setblocking(False)

    read_socks: List[socket] = [server_sock]
    write_socks: List[socket] = []
    err_socks: List[socket] = []

    try:
        while True:
            read_conns, write_conns, _ = select.select(read_socks, write_socks, err_socks)
            for conn in read_conns:
                if conn == server_sock:
                    new_conn, address = conn.accept()
                    new_conn.setblocking(False)
                    print(f'Connected by {address}')
                    read_socks.append(new_conn)
                    global_queue[address] = deque()
                else:
                    address: tuple = conn.getpeername()
                    data: bytes = conn.recv(1024)  # Should be ready
                    if data:
                        global_queue[address].append(data)
                        print(f"{datetime.now()} {address[0]}:{address[1]} > Receive data: {data}")
                        if conn not in write_socks:
                            write_socks.append(conn)
                    else:
                        if conn in write_socks:
                            write_socks.remove(conn)
                        read_socks.remove(conn)
                        conn.close()
                        del global_queue[address]
                        print(f"Disconnected by {address}")

            for conn in write_conns:
                address: tuple = conn.getpeername()
                if queue := global_queue[address]:
                    conn.send(queue.popleft())
                    print(f"{datetime.now()} {address[0]}:{address[1]} > Send data")

            time.sleep(0.01)     # if we use select without sleep then CPU is 100%

    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")