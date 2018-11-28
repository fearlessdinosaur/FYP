import socket as sock
from threading import Thread
import json
def listener():
    host = '127.0.0.1'
    port = 8494
    x = 1
    with sock.socket(sock.AF_INET,sock.SOCK_STREAM) as s:
        s.bind((host,port))
        s.listen(5)
        
            
        while 1:
            conn,addr = s.accept()
            print("connection Accepted")
            connections.update({conn:""})
            Thread(target=takeClient, args=(conn,)).start()

def takeClient(conn):
    while True:
        name = connections[conn]
        msg = conn.recv(1024).decode()
        parts = json.loads(msg)
        print(parts["code"])
        if(parts["code"] == 0):
            connections[conn] = parts["Message"]
            name = connections[conn]
        if(parts["code"] == 1):
            print(name+":"+parts["Message"])
            broadcast(name+":"+parts["Message"])

def broadcast(msg):
    for conn in connections:
            conn.send(msg.encode())

connections = {}
listener()    
