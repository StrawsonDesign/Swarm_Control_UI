# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 13:13:43 2016

@author: FailingToFocus
"""
from multiprocessing import Process, Pipe
import threading
import tkMessageBox # for messageboxes 
import Tkinter as tk
from PIL import ImageTk , Image # for image conversion
import cv2 # OpenCV for video handling
import tkFont # for fonts
from time import strftime,sleep # for sleep
from collections import deque # for ring buffer
import socket # for sending across UDP packets 

class Send(threading.Thread):
    def __init__(self, conn):
		threading.Thread.__init__(self)
		self.conn = conn
		#self.conn.send([42, None, 'hello'])
		#self.conn.close()
		global receviedPacketBuffer # Must declare gloabl varibale prior to assigning values
		global receviedPacketBufferLock
		receviedPacketBuffer= deque([], 10)
		receviedPacketBufferLock = threading.Lock()
		print "Initialized Ring Buffer as size of", 10
		#self.isBufferBusy=0
		print "Buffer is : ", receviedPacketBuffer, "\n"
		#self.conn.send([42, None, 'hello'])
		#self.conn.send([receviedPacketBuffer])
		#self.conn.close()
    
    def run(self):
        for i in xrange(5): # replace by reading head
            #sleep(1)
            try:
                if receviedPacketBufferLock.acquire(1):
					receviedPacketBuffer.append(i)
					#print "Buffer is : ", receviedPacketBuffer, "\n"
					self.conn.send([42, None, 'hello'])					
                #else:
                    #print "Lock was not ON"
            finally:
				receviedPacketBufferLock.release()
				#self.conn.close()
                    
class Send2(threading.Thread):
    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.conn = conn  
        self.conn.send([84, None, 'hi'])
        #self.conn.close()
    
def f(conn1,conn2):
	Thread = Send(conn1)
	Thread2 = Send2(conn2)
	Thread2.setDaemon(True)
	Thread.setDaemon(True)
	Thread.start()
	Thread2.start()
	Thread2.join()
	Thread.join()

if __name__ == '__main__':
	lock = multiprocessing.Lock()
    parent_conn, child_conn = Pipe()
    parent_conn2, child_conn2 = Pipe()
    p = Process(target=f, args=(child_conn,child_conn2))
    p.start()
    print "The parent 1: ", parent_conn.recv()   # prints "[42, None, 'hello']"
    print "The parent 2: ", parent_conn2.recv()   # prints "[42, None, 'hello']"
    p.join()