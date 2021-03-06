 
import sys
import socket
import select
import Elgamal as eg
import time
import pyaes
import hashlib
import threading
from threading import Thread
try:
    import Tkinter as tk
    import ScrolledText as tkst
except ImportError:
    import tkinter as tk
    import tkinter.scrolledtext as tkst

from tkinter import END, LEFT, RIGHT, TOP, BOTTOM, BOTH, Y, NE, NS, NSEW, W, E, YES
from tkinter import ttk
from tkinter.font import Font
from tkinter import VERTICAL, HORIZONTAL
import textwrap
import random

RUNNING = True
HOST = '127.0.0.1'
S_HOST = '127.0.0.1'
RECV_BUFFER = 4096 
PORT = 80
S_PORT = 80

    
class introWindow(tk.Frame):
    

    def __init__(self, master, frame_look={}, **look):
        #define our send function that takes input and sends it over the wire
        #while also writing what we said to the text box
        def send(event=''):
            try:
                #get the message from the field
                msg = 'Bob: ' + self.my_msg.get()
                #clear the field
                self.my_msg.set("")

                #print(msg)
                #we want to print the message from us to the screen as well

                self.msg_list.insert(tk.END, msg)
                self.msg_list.see(tk.END)
                msg = pyaes.AESModeOfOperationCTR(self.hashed).encrypt(msg)
                self.client_socket.send(msg)
            #here is the errors we can run into, all are close and destroy the interface
            except (KeyboardInterrupt, EOFError,ConnectionResetError, OSError):
                self.client_socket.close()
                self.destroy()
                return 0
            #send the message over the wire
            return 0

        #this is just a useful template frame with nice settings
        args = dict(relief=tk.SUNKEN, border=1)
        args.update(frame_look)
        tk.Frame.__init__(self, master, **args)

        args = {'relief': tk.FLAT}
        args.update(look)

        #we want a scrollable viewer
        #make a frame for it
        self.messages_frame = tk.Frame(self)

        #make our scroll boi
        
        self.my_msg = tk.StringVar()  # For the messages to be sent.
        self.my_msg.set("Type your messages here.")

        self.scrollbar = tk.Scrollbar(self.messages_frame)  # To navigate through past messages.
        # Following will contain the messages.
        self.msg_list = tk.Listbox(self.messages_frame, height=15, width=50, yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.msg_list.pack(side=tk.LEFT, fill=tk.BOTH)
        self.msg_list.pack()
        

        #setup our entry frame to house the text box and button
        self.entry_frame = tk.Frame(self)
        self.entry_field = tk.Entry(self.entry_frame,textvariable=self.my_msg)
        self.entry_field.bind("<Return>", send)
        self.entry_field.pack()
        self.send_button = tk.Button(self.entry_frame,text="Send", command=send)
        self.send_button.pack()
        self.messages_frame.pack()
        self.entry_frame.pack()
        #self.msg_list.insert(tk.END, 'Waiting on connection.')
        self.client_socket, self.hashed= self.chat_server()
        #self.msg_list.insert(tk.END, 'connection received')
        #our initial gui setup is done
        self.msg_list.insert(tk.END, "Welcome to the chat program.")
        self.msg_list.insert(tk.END, "These are you keys: (Compare with your partner)")
        self.msg_list.insert(tk.END, int.from_bytes(self.hashed, byteorder='big', signed=False))        
        #make listen thread
        t = Thread(target = self.listen, daemon=True).start()



    def listen(self):
        try:
            while True:
                message = self.client_socket.recv(4096)
                try:
                    if message.decode() == '':
                        print('killed em')
                        self.client_socket.close()
                        raise SystemExit
                        return 0
                except UnicodeDecodeError:
                    pass    
                message = pyaes.AESModeOfOperationCTR(self.hashed).decrypt(message)
                m_list = textwrap.wrap(message.decode(),width=48)
                for m in m_list:
                    self.msg_list.insert(tk.END,m)
                    self.msg_list.see(tk.END)
                #self.msg_list.insert(tk.END,message.decode())
        except (KeyboardInterrupt, EOFError,ConnectionResetError, OSError):
            self.client_socket.close()

    def chat_server(self):
        try:
            #create the sending socket
            client_socket = socket.socket()
            client_socket.connect((S_HOST, S_PORT))
            print('client connected')
            
            print('connected')
            #print("connected")
            #print(c)
            #print(addr)
            
            #time to setup the preamble
            #since I connected I wait to get the public keys
            #I need a prime
            keys = client_socket.recv(4096).decode()
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

            return (client_socket, hashed)
            '''
            t = Thread(target = listen, args=(c,hashed,))
            t.start()
            t2 = Thread(target = write, args=(client_socket,hashed),daemon=True)
            t2.start()
            
            #listen_socket.close()
            while threading.active_count() > 2:
                pass
            '''
        except (KeyboardInterrupt,EOFError,ConnectionResetError):
            #RUNNING = False
            
            #client_socket.close()
            print('dead mate')
            return 0
        return 0



if __name__ == '__main__':        
    win = tk.Tk()
    win.title('Intro')

    dentry = introWindow(win, font=('Helvetica', 40, tk.NORMAL), border=0)
    dentry.pack()

        
    #win.bind('<Return>', lambda e: print(dentry.get()))
    win.mainloop()
#chat_server()