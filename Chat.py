 
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
        Thread(target = listen, args=(c,hashed,),daemon=True).start()
        Thread(target = write, args=(client_socket,hashed)).start()
        '''while True:
                                    message = c.recv(4096)
                                    message = pyaes.AESModeOfOperationCTR(hashed).decrypt(message)
                                    print(message.decode())
                                    message = input()
                                    message = pyaes.AESModeOfOperationCTR(hashed).encrypt(message)
                                    client_socket.send(message)'''
    except KeyboardInterrupt:

        
        print('dead mate')


    '''
    while True:
        message = c.recv(4096)
        print(message.decode())
        message = input()
        client_socket.send(message.encode('UTF-8'))
    '''

def listen(listen_socket,hashed):
    
    try:
        while True:
            message = listen_socket.recv(4096)
            message = pyaes.AESModeOfOperationCTR(hashed).decrypt(message)
            print(message.decode())
    except KeyboardInterrupt:
        listen_socket.close()
        
        raise KeyboardInterrupt
        return 0
def write(write_socket, hashed):
    
    try:
        while True:
            message = input()
            message = pyaes.AESModeOfOperationCTR(hashed).encrypt(message)
            write_socket.send(message)
    except KeyboardInterrupt:
        write_socket.close()
        
        raise KeyboardInterrupt
        return 0
#chat_server()