 
import sys
import socket
import select
import Elgamal as eg
import random
import pyaes
import hashlib
import threading
from threading import Thread
HOST = '127.0.0.1'
S_HOST = '127.0.0.1'
RECV_BUFFER = 4096 
PORT = 81
S_PORT = 80
RUNNING = True
def chat_server():
    try:
        #create the sending socket
        client_socket = socket.socket()
        client_socket.connect((S_HOST, S_PORT))
        print('client connected')
        #create the listening socket
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listen_socket.bind((HOST, PORT))
        listen_socket.listen(10)
        c, addr = listen_socket.accept()
        print('connected')
        #print("connected")
        #print(c)
        #print(addr)
        
        #time to setup the preamble
        #since I connected I wait to get the public keys
        #I need a prime
        keys = c.recv(4096).decode()
        keys = keys.split(',')
        p = int(keys[0])
        #I need a g value
        g = int(keys[1])
        #i need a g_a value
        g_a = int(keys[2])
        #generate my secret b
        b = random.getrandbits(128)
        #generate my public half
        g_b = pow(g, b, p)
        print(g_b)
        #time.sleep(100)
        #send my public half
        client_socket.send(str(g_b).encode('UTF-8'))
        #make the shared secret
        g_a_b = pow(g_a, b, p)

        print(g_a_b)
        # The SHA256 hash algorithm returns a 32-byte string
        hashed = hashlib.sha256(str(g_a_b).encode('UTF-8')).digest()

        # A 16-byte, 24-byte and 32-byte key, respectively
        key_16 = hashed[:16]
        aes = pyaes.AESModeOfOperationCTR(hashed)
        test = 'test'
        test = aes.encrypt(test)
        aes = pyaes.AESModeOfOperationCTR(hashed)

        test = aes.decrypt(test)
        print((test.decode()))
        Thread(target = listen, args=(c,hashed,), daemon=True).start()
        Thread(target = write, args=(client_socket,hashed)).start() 
        '''
        while True:
            
            message = input()
            message = pyaes.AESModeOfOperationCTR(hashed).encrypt(message)
            client_socket.send(message)

            message = c.recv(4096)
            message = pyaes.AESModeOfOperationCTR(hashed).decrypt(message)
            print(message.decode())'''
    except KeyboardInterrupt:
        RUNNING = False
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
