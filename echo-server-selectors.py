import selectors
import socket
import time
from collections import deque
from typing import Dict

HOST = "127.0.0.1"
PORT = 65432

sel = selectors.DefaultSelector()

global_queue: Dict[tuple, deque] = {}


def accept(sock: socket, mask):
    conn, addr = sock.accept()  # Should be ready
    print(f'Connected by {conn.getpeername()}')
    conn.setblocking(False)
    global_queue[addr] = deque()
    sel.register(conn, selectors.EVENT_READ | selectors.EVENT_WRITE, process)
    # sel.register(conn, selectors.EVENT_READ, process)


def process(conn: socket, mask: int):
    addr = conn.getpeername()
    if mask & selectors.EVENT_READ:
        data = conn.recv(1024)  # Should be ready
        if data:
            global_queue[addr].append(data)
            print(f"{addr[0]}:{addr[1]} > Receive data: {data}")

        else:
            print(f"Disconnected by {addr}")
            sel.unregister(conn)
            conn.close()
            del global_queue[addr]

    if mask & selectors.EVENT_WRITE:
        if queue := global_queue[addr]:
            conn.send(queue.popleft())
            print(f"{addr[0]}:{addr[1]} > Send data")


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.bind((HOST, PORT))
    sock.listen(1)
    sock.setblocking(False)
    sel.register(sock, selectors.EVENT_READ, accept)

    try:
        while True:
            events = sel.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)
            time.sleep(0.5)     # if we use selectors.EVENT_WRITE without sleep then CPU is 100%
    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")
    finally:
        sel.close()