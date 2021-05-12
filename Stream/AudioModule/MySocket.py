import socket
import numpy as np

import ctypes
from ctypes import cdll
lib = cdll.LoadLibrary("/home/pi/Documents/AudioModule/wrap.so")


class UdpServer:
    
    def __init__(self,buffer_size = 4410):
        self.udpServer = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.BUFFSIZE = 128*4 # byte esp32 send 128 sample per chunk
        self.buffer_intSize = buffer_size
        self.res = np.zeros(shape = self.BUFFSIZE//4 ,dtype = int)


    def bind(self, localIP, localPort):
        print('in bind',self.udpServer)
        self.udpServer.bind((localIP, localPort))
        print("UDP server up and listening")

    def recv(self):
        
     
        buf, addr = self.udpServer.recvfrom(self.BUFFSIZE)
        i = 0 
        res_index = 0
        buf_size = len(buf)
        
        while i < buf_size :
            if buf[i] != 0 :
                i += 1
                continue

            intType = lib.c_intFrom4char(buf[i-3],buf[i-2],buf[i-1],buf[i])
            i += 4

            self.res[res_index] = intType
            res_index += 1

        return self.res , res_index
 
