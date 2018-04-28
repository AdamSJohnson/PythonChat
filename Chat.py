 
import sys
import socket
import select
import Elgamal as eg
import time
import pyaes
import hashlib
import threading
from threading import Thread
RUNNING = True
HOST = '127.0.0.1'
S_HOST = '127.0.0.1'
RECV_BUFFER = 4096 
PORT = 80
S_PORT = 81
def chat_server():
    try:
        keys = eg.elgamal_generate_keys()
        p = keys[0]
        g = keys[1]
        a = keys[2]
        g_a = keys[3]
        print(keys)
        #create the listening socket
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        listen_socket.bind((HOST, PORT))
        listen_socket.listen(1000)
        c, addr = listen_socket.accept()
        print('connected')
        #create the sending socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, S_PORT))
        #print("connected")
        #print(c)
        #print(addr)
        print('client connected')
        #since I was the one connected to the protocol is I send my 
        #public keys

        #send p,g,g_a
        message = str(p) + ',' + str(g) + ',' + str(g_a)
        client_socket.send(message.encode('UTF-8'))
        

        #get the other client's public half
        g_b = int(c.recv(4096))

        g_a_b = pow(g_b,a,p)
        print(g_a_b)
        hashed = hashlib.sha256(str(g_a_b).encode('UTF-8')).digest()

        # A 16-byte, 24-byte and 32-byte key, respectively
        key_16 = hashed[:16]
        aes = pyaes.AESModeOfOperationCTR(hashed)

        test = 'test'
        test = aes.encrypt(test)
        aes = pyaes.AESModeOfOperationCTR(hashed)
        test = aes.decrypt(test)
        print((test.decode()))
        t = Thread(target = listen, args=(c,hashed,))
        t.start()
        t2 = Thread(target = write, args=(client_socket,hashed),daemon=True)
        t2.start()
        
        #listen_socket.close()
        while threading.active_count() > 2:
            a = 1
        
    except (KeyboardInterrupt,EOFError,ConnectionResetError):
        RUNNING = False
        
        client_socket.close()
               

        print('dead mate')

    '''
    while True:
        message = input()
        client_socket.send(message.encode('UTF-8'))
        message = c.recv(4096)
        print(message.decode())
    '''

def listen(listen_socket,hashed):
    
    try:
        while True:
            message = listen_socket.recv(4096)
            try:
                if message.decode() == '':
                    print('killed em')
                    listen_socket.close()
                    raise SystemExit
                    return 0
            except UnicodeDecodeError:
                pass    
            message = pyaes.AESModeOfOperationCTR(hashed).decrypt(message)
            print(message.decode())
    except (KeyboardInterrupt, EOFError,ConnectionResetError):
        listen_socket.close()
        

def write(write_socket, hashed):
    
    try:
        while True:
            message = input()
            #print(message)
            message = pyaes.AESModeOfOperationCTR(hashed).encrypt(message)
            write_socket.send(message)
    except (KeyboardInterrupt, EOFError,ConnectionResetError):
        write_socket.close()
        return 0
        


#chat_server()