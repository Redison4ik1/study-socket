import socket
import threading

HOST = "127.0.0.1"
PORT = 65432


def echo(conn, addr):
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                print(f"Disconnected by {addr}")
                break
            print(f"{addr[0]}:{addr[1]} > Receive data: {data}")
            conn.sendall(data)


threads = list()
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    while True:
        conn, addr = s.accept()
        print(f"Connected by {addr}")
        t = threading.Thread(target=echo, args=(conn,addr))
        threads.append(t)
        t.start()
