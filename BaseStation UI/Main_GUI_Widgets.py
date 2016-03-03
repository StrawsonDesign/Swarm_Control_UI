import Tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
# matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg #, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
#import matplotlib.animation as animation
from PIL import ImageTk , Image # for image conversion
import cv2 # OpenCV for video handling
import tkFont, threading, Queue, tkMessageBox
from time import strftime, sleep
from collections import deque
import socket # for sending across UDP packets 
from multiprocessing.sharedctypes import Value, Array
from ctypes import Structure, c_double, c_short, c_long
from multiprocessing import Process, Lock #multiprocessing

from argparse import ArgumentParser

from pymavlink import mavutil

allDronesList=['Othrod','The Great Goblin','Boldog','Ugluk','Bolg','Orcobal','More Orcs','Orc1','Orc2','Orc3','Orc4']
activeDronesList=['Othrod','Ugluk','Bolg','Orcobal'] 
		
class listener(threading.Thread):
    def __init__(self,sizeOfBuffer, Packets, startLogging, stopLogging, UDPmaster, msgIDs):
		threading.Thread.__init__(self)
		#global receviedPacketBuffer # Must declare gloabl varibale prior to assigning values
		#global receviedPacketBufferLock
		self.receviedPacketBuffer= deque([], sizeOfBuffer)
		self.receviedPacketBufferLock = threading.Lock()
		print "Initialized Ring Buffer as size of", sizeOfBuffer
		#self.isBufferBusy=0
		self.Packets = Packets
		self.sizeOfBuffer = sizeOfBuffer
		self.startLogging = startLogging
		self.stopLogging = stopLogging
		self.UDPmaster = UDPmaster
		self.msgIDs = msgIDs
		
    def logger(self):
		outfile='testfile.txt'
		self.log_dummy=open(outfile,"w",1) # use a = append mode, buffering set to true
		print "file", outfile, "is opened"

		print "The packet delivered is: " + str(self.Packets[:])
		tempData=""
		m=0
		#while m<20: # change this
		#sleep(1)
		#if self.receviedPacketBufferLock.acquire(0):
			#try:
		i = 0
		for i in xrange(self.sizeOfBuffer): # empty the entire list
		#self.listenerobject.isBufferBusy=1
			data=strftime("%c") + "\t" + str(self.Packets[i]) + "\n"
			tempData=tempData+data
			print "Packet: " + str(self.Packets[i])
			i += 1
	#except IndexError:
		#print "Index Error occured, couldn't pop left on an empty deque"
		
	#finally:
		#receviedPacketBufferLock.release()
		print "Released Packet:" + str(self.Packets[:]) #This is the packet that should be released to the plotter
		m += 1
		#print "M is", m
		if m%self.sizeOfBuffer==0:
			self.log_dummy.write(tempData)
			print "WROTE TO DISK"
			tempData=""
			
    def run(self):
		i = 0

		for i in xrange(30): # replace by reading head
		#while i < 100:
			i = i + 1
			sleep(1)
			try:
				if self.receviedPacketBufferLock.acquire(1):
					#print "Buffer is : ", self.receviedPacketBuffer, "\n"
					#self.receviedPacketBuffer.append(i)
					msg = self.UDPmaster.recv_msg() #This should recv the message then parse it
					#self.receviedPacketBuffer.append(msg)
					self.receviedPacketBuffer += msg
					#self.receviedPacketBufferMsgId.append(msg.get_msgId())
					self.receviedPacketBufferMsgId += msg.get_msgId()
				else:
					print "Lock was not ON"
				
			finally:
				self.receviedPacketBufferLock.release()
				print "Released Buffer is: ", self.receviedPacketBuffer, "\n"
				print "Released Buffer msg IDs is: ", self.receviedPacketBufferMsgId, "\n"
				if i%self.sizeOfBuffer==0:
					for x in xrange(self.sizeOfBuffer):
						val = self.receviedPacketBuffer.popleft()
						self.Packets[x] = val
						self.msgIDs[x] = self.receviedPacketBufferMsgId.popleft()
						#print "Just popped " + str(val) + '\n'
					print 'Packet Buffer: ' + str(self.Packets[:]) + '\n'
					print 'MSGIds: ' + str(self.msgIDs[:]) +'\n'
					print 'Call Logger'
										
					if self.startLogging.value == 1 and self.stopLogging.value == 0:
						self.logger()
					else:
						print "Don't need to record data yet"

class myUAVThreadClass(threading.Thread):
	def __init__(self,master):
		threading.Thread.__init__(self)
		myUAVFrame = tk.Frame(master)
		myUAVFrame.place(x=0,y=0,width=w,height=h)
		# myUAVFrame.grid(row = 0,
						# column = 0,
						# rowspan = 1,
						# columnspan = 1,
						# sticky = tk.S + tk.N + tk.W + tk.E)
		# myUAVFrame.rowconfigure(0, weight = 1)
		# myUAVFrame.columnconfigure(0, weight = 1)
		# myUAVFrame.columnconfigure(1, weight = 1)
		# myUAVFrame.columnconfigure(2, weight = 1)
		# myUAVFrame.columnconfigure(3, weight = 1)
		
		batteryLife = 75
		signalStrength = 86
		upTime = 524.53
		myUAV = 'Hot'
		
		batteryLabel = tk.Label(myUAVFrame, text = "Battery Life: %d" % batteryLife)
		signalLabel = tk.Label(myUAVFrame, text = "Signal Strength: %d" % signalStrength)
		upTimeLabel = tk.Label(myUAVFrame, text = "Up Time: %f [s]" % upTime)
		myUAVName = tk.Label(myUAVFrame, text = "UAV Name: %s" % myUAV)
		
		# batteryLabel.grid(row = 0, column = 0, sticky = tk.N + tk.S + tk.W + tk.E)
		# signalLabel.grid(row = 0, column = 1, sticky = tk.N + tk.S + tk.W + tk.E)
		# upTimeLabel.grid(row = 0, column = 2, sticky = tk.N + tk.S + tk.W + tk.E)
		# myUAVName.grid(row = 0, column = 3, sticky = tk.N + tk.S + tk.W + tk.E)
		
		batteryLabel.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
		signalLabel.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
		upTimeLabel.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
		myUAVName.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
		
		# myUAV_batteryFrame = tk.Frame(myUAVFrame)
		# myUAV_batteryFrame.grid(row = 0, sticky = tk.N + tk.S + tk.W + tk.E)
		# myUAV_signalStrengthFrame = tk.Frame(myUAVFrame)
		# myUAV_signalStrengthFrame.grid(row = 1, sticky = tk.N + tk.S + tk.W + tk.E)
		# myUAV_UpTimeFrame = tk.Frame(myUAVFrame)
		# myUAV_UpTimeFrame.grid(row = 0, sticky = tk.N + tk.S + tk.W + tk.E)
		# myUAV_NameFrame = tk.Frame(myUAVFrame)
		# myUAV_NameFrame.grid(row = 0, sticky = tk.N + tk.S + tk.W + tk.E)
        
        # testButton=tk.Button(myUAVFrame,
                            # text='Overwrite',
                            # command=self.quit())
        # testButton.grid(row=0, 
                        # column=0,
                        # rowspan=1,
                        # columnspan=1,
                        # sticky = tk.N+tk.S+tk.W+tk.E)

	def run(self):
		i=0
		while i<6:
			print 'i is =',i
			# print '# active threads in MyUAV loop are',threading.enumerate()
			sleep(5)
			i+= 1	
			
class otherdrones(threading.Thread):
    def __init__(self,master):
		threading.Thread.__init__(self)
		#otherDroneFrame=tk.Frame(master)
		otherDroneCanvas = tk.Canvas(master) # to add scroll bar
		otherDroneCanvas.place(x=w,y=0,width=screenW-w,height=h)
		# otherDroneCanvas.grid(row=0,
						# column=1,
						# rowspan=1,
						# columnspan=3,
						# sticky=tk.N+tk.S+tk.W+tk.E)
		# otherDroneCanvas.rowconfigure(0,weight=1)
		#self.updateActiveDrones(droneFrame)
		# Intialize places for
		i=0 # counter for referencing objects in the list
		self.allDroneDict=dict() # initalizing empty dictionary 
		for orc in allDronesList:
			# otherDroneCanvas.columnconfigure(i,weight=1)
			self.allDroneDict[orc]=tk.Button(otherDroneCanvas,text=orc, bg = "gray14", fg="snow")
			self.allDroneDict[orc].pack(side=tk.LEFT,fill=tk.BOTH,expand=1)
			# self.allDroneDict[orc].grid(row=0,column=i,sticky=tk.N+tk.S+tk.E+tk.W)
			i=i+1

		# scrollBarOtherDrones = AutoScrollbar(otherDroneCanvas,orient=tk.HORIZONTAL)
		# scrollBarOtherDrones.grid(row=1,columnspan=i,sticky=tk.E+tk.W)

    def run(self):
        sleep(2) # remove this eventually
        i=1
        while 1:
            self.updateActiveDrones()
            if (i%60)==0: # print every 30 seconds - thread is alive
                print "Updated Active Drones in the vicinity" 
            i=i+1
            sleep(0.5) # sleep for 500ms before updating

    def updateActiveDrones(self):
        # add missing key error exceptions here
        for orc in activeDronesList:
            self.allDroneDict[orc].configure(bg='green', fg='black')
			
class loggingThreadClass(threading.Thread):
	
	def __init__(self, master, startBool, stopBool):
		threading.Thread.__init__(self)
		loggingFrame = tk.Frame(master)
		h_dash=int((screenH-h-int(0.33*vidH))/5)-5# height of each setting box
		loggingFrame.place(x=w+vidW,y=h+int(0.33*vidH),width=screenW-vidW-w,height=screenH-h-int(0.33*vidH)-25)
		# loggingFrame.grid(row = 2, 
						# column = 3,
						# rowspan = 1,
						# columnspan = 1,
						# sticky = tk.S + tk.N + tk.W + tk.E)
		# loggingFrame.rowconfigure(2, weight = 1)
		# loggingFrame.rowconfigure(3, weight = 1)
		# loggingFrame.rowconfigure(4, weight = 1)
		# loggingFrame.rowconfigure(5, weight = 1)
		# loggingFrame.rowconfigure(6, weight = 1)
		# loggingFrame.rowconfigure(7, weight = 1)
		# loggingFrame.columnconfigure(4, weight = 1)
		
		log_attitudeBoxFrame = tk.Frame(loggingFrame)
		# log_attitudeBoxFrame.grid(row = 2, column = 4, sticky = tk.N + tk.S + tk.W + tk.E)
		log_positionBoxFrame = tk.Frame(loggingFrame)
		# log_positionBoxFrame.grid(row = 3, column = 4, sticky = tk.N + tk.S + tk.W + tk.E)
		log_velocityBoxFrame = tk.Frame(loggingFrame)
		# log_velocityBoxFrame.grid(row = 4, column = 4, sticky = tk.N + tk.S + tk.W + tk.E)
		log_batteryBoxFrame = tk.Frame(loggingFrame)
		# log_batteryBoxFrame.grid(row = 5, column = 4, sticky = tk.N + tk.S + tk.W + tk.E)
		
		log_startButtonFrame = tk.Frame(loggingFrame)
		# log_startButtonFrame.grid(row = 6, column = 4, sticky = tk.N + tk.S + tk.W + tk.E)
		log_stopButtonFrame = tk.Frame(loggingFrame)
		# log_stopButtonFrame.grid(row = 7, column = 4, sticky = tk.N + tk.S + tk.W + tk.E)
		
		log_attitudeBoxFrame.place(x=0, y=0,width=w, height=h_dash)
		log_positionBoxFrame.place(x=0, y=h_dash, width=w, height=h_dash)
		log_velocityBoxFrame.place(x=0, y=2*h_dash, width=w, height=h_dash)
		log_batteryBoxFrame.place(x=0, y=3*h_dash, width=w, height=h_dash)
		
		log_startButtonFrame.place(x=0, y=4*h_dash, width=w, height=h_dash)
		log_stopButtonFrame.place(x=0, y=5*h_dash, width=w, height=h_dash)
		
		log_iattitude = tk.IntVar()
		log_iposition = tk.IntVar()
		log_ivelocity = tk.IntVar()
		log_ibattery = tk.IntVar()
		
		log_attitudeCheckButton = tk.Checkbutton(log_attitudeBoxFrame, text = 'Attitude', variable = log_iattitude, command = lambda : self.logVariables('Attitude', log_iattitude.get()))
		log_positionCheckButton = tk.Checkbutton(log_positionBoxFrame, text = 'Position', variable = log_iposition, command = lambda : self.logVariables('Position', log_iposition.get()))
		log_velocityCheckButton = tk.Checkbutton(log_velocityBoxFrame, text = 'Velocity', variable = log_ivelocity, command = lambda : self.logVariables('Velocity', log_ivelocity.get()))
		log_batteryCheckButton = tk.Checkbutton(log_batteryBoxFrame, text =  'Battery', variable = log_ibattery, command = lambda : self.logVariables('Battery', log_ibattery.get()))
		
		log_attitudeCheckButton.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
		log_positionCheckButton.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
		log_velocityCheckButton.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
		log_batteryCheckButton.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
		
		log_startButton = tk.Button(log_startButtonFrame, text = 'Record', command = self.startRecording)
		log_stopButton = tk.Button(log_stopButtonFrame, text = 'Stop', command = self.stopRecording)
		
		log_startButton.pack(side = tk.BOTTOM, fill = tk.BOTH, expand = 1)
		log_stopButton.pack(side = tk.BOTTOM, fill = tk.BOTH, expand = 1)
		
		self.loggingVariables = []
		self.startLogging = startBool
		self.stopLogging = stopBool
		
		#global startLogging
		#global stopLogging
		#startLogging = False
		#stopLogging = False
	
	# def record_data(self, listeningThread):
		
		# file = 'testfile.txt'
		# self.listenerobject = listeningThread
		# self.logfile = open(file, 'w',1)
		# print "The file", file, "has been opened"
		
		# try:
			# while 1:
				# sleep(0.1)				
				# if len(self.listenerobject.receviedPacketBuffer)>0:
					# data=strftime("%c")+"\t"+str(self.listenerobject.receviedPacketBuffer.popleft())+"\n"
					# self.logfile.write(data)
					
		# except IndexError:
			# print "No elements in the Buffer"
			
		# return self.logfile
		
	# def stop_recording(self,log_recordButton):	
			# self.logfile.close()
			# print file + "is not open"
		
	def Stop(self):
		self.quit()     # stops mainloop
		self.destroy()  # this is necessary on Windows to prevent
							# Fatal Python Error: PyEval_RestoreThread: NULL tstate

	def startRecording(self):
		self.startLogging.value = 1
		self.stopLogging.value = 0
		print 'Start Recording Data'
		#print 'Start Bool: ' + str(self.startLogging.value) + '\n'
		#print 'Stop Bool: ' + str(self.stopLogging.value) + '\n'
		
	def stopRecording(self):
		self.startLogging.value = 0
		self.stopLogging.value = 1
		print 'Stop Recording Data'
		#print 'Start Bool: ' + str(self.startLogging.value) + '\n'
		#print 'Stop Bool: ' + str(self.stopLogging.value) + '\n'
		
	def logVariables(self, var_Name, var_State):
	
		if var_State == 1:
			self.loggingVariables.append(var_Name)
			print self.loggingVariables
			
		elif var_State == 0:
			ivar_Name = self.loggingVariables.index(var_Name)
			self.loggingVariables.pop(ivar_Name)
			print self.loggingVariables
		
		self.Log_names = self.loggingVariables
		print "Log names: " + str(self.Log_names)
		
	def run(self):
		pass
		
class settingsThreadClass(threading.Thread):
    def __init__(self,master):
		threading.Thread.__init__(self)
		settingsFrame=tk.Frame(master)
		h_dash=int((screenH-h-int(0.66*vidH))/5)-5# height of each setting box
		settingsFrame.place(x=0,y=h+int(0.66*vidH),width=w,height=screenH-h-int(0.66*vidH))
		print h+int(0.66*vidH),screenH-h-int(0.66*vidH), h_dash,screenH-h-int(0.66*vidH)-4*h_dash
		# settingsFrame.grid(row=3,
			# column=0,
			# sticky=tk.N+tk.S+tk.E+tk.W)
		# settingsFrame.rowconfigure(0, weight=1)
		# settingsFrame.rowconfigure(1, weight=1)
		# settingsFrame.rowconfigure(2, weight=1)
		# settingsFrame.columnconfigure(0, weight=1)

		# Mapping modes are : SLAM (0) or VICON pos input (1)
		# Flight modes are : Altitude (2) vs Manual Thrust (3) vs POS hold (4)
		# Pilot reference mode: global (5), First Person View (6), PPV (7)
		# Control mode: User (8) , Auto land (9), Come back home (10), Circle Mode (11)

		killButton=tk.Button(settingsFrame, text="Kill Drone", command = killDroneMethod, bg ="red")
		# killButton.grid(row=0,sticky=tk.N+tk.S+tk.E+tk.W)
		mappingModeFrame=tk.Frame(settingsFrame)
		# mappingModeFrame.grid(row=1,sticky=tk.N+tk.S+tk.E+tk.W)
		flightModeFrame=tk.Frame(settingsFrame)
		# flightModeFrame.grid(row=2,sticky=tk.N+tk.S+tk.E+tk.W)
		pilotReferenceModeFrame=tk.Frame(settingsFrame)
		# pilotReferenceModeFrame.grid(row=3,sticky=tk.N+tk.S+tk.E+tk.W)
		controlModeFrame=tk.Frame(settingsFrame)
		# controlModeFrame.grid(row=4,sticky=tk.N+tk.S+tk.E+tk.W)

		killButton.place(x=0,y=0,width=w,height=h_dash)
		mappingModeFrame.place(x=0,y=h_dash,width=w,height=h_dash)
		flightModeFrame.place(x=0,y=2*h_dash,width=w,height=h_dash)
		pilotReferenceModeFrame.place(x=0,y=3*h_dash,width=w,height=h_dash)
		controlModeFrame.place(x=0,y=4*h_dash,width=w,height=h_dash)

		m=tk.IntVar()
		f=tk.IntVar()
		p=tk.IntVar()   
		c=tk.IntVar()   

		# default flight modes
		m.set(0) #mappingMode = 0    
		f.set(4) #flightMode = 4
		p.set(5) #pilotReferenceMode=5
		c.set(8) #controlMode= 8

		mappingModeRadioButton0=tk.Radiobutton(mappingModeFrame, text="SLAM", variable=m, 
								value=0,indicatoron=0,
								state=tk.ACTIVE, command=lambda : sendSettingPacket(m.get(),f.get(),p.get(),c.get()))
		mappingModeRadioButton1=tk.Radiobutton(mappingModeFrame, text="VICON position input", 
								variable=m,
								value=1,indicatoron=0,
								command=lambda : sendSettingPacket(m.get(),f.get(),p.get(),c.get()))
		mappingModeRadioButton0.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)
		mappingModeRadioButton1.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)

		flightModeRadioButton2=tk.Radiobutton(flightModeFrame, text="Altitude", variable=f, value=2,
								indicatoron=0,
								state=tk.ACTIVE, # set as default
								command=lambda : sendSettingPacket(m.get(),f.get(),p.get(),c.get()))
		flightModeRadioButton3=tk.Radiobutton(flightModeFrame, text="Manual Thrust", variable=f, value=3,
								indicatoron=0,command=lambda : sendSettingPacket(m.get(),f.get(),p.get(),c.get()))
		flightModeRadioButton4=tk.Radiobutton(flightModeFrame, text="POS hold", variable=f, value=4,
								indicatoron=0,
								command=lambda : sendSettingPacket(m.get(),f.get(),p.get(),c.get()))
		flightModeRadioButton2.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)
		flightModeRadioButton3.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)
		flightModeRadioButton4.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)

		pilotReferenceModeRadioButton5=tk.Radiobutton(pilotReferenceModeFrame, text="Global", variable=p, value=5,
											indicatoron=0,
											state=tk.ACTIVE,
											command=lambda : sendSettingPacket(m.get(),f.get(),p.get(),c.get()))
		pilotReferenceModeRadioButton6=tk.Radiobutton(pilotReferenceModeFrame, text="First Person View",
											variable=p, value=6,indicatoron=0,
											command=lambda : sendSettingPacket(m.get(),f.get(),p.get(),c.get()))
		pilotReferenceModeRadioButton7=tk.Radiobutton(pilotReferenceModeFrame, text="PPV", variable=p,
											value=7,indicatoron=0,
											command=lambda : sendSettingPacket(m.get(),f.get(),p.get(),c.get()))
		pilotReferenceModeRadioButton5.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)
		pilotReferenceModeRadioButton6.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)
		pilotReferenceModeRadioButton7.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)

		controlModeRadioButton8=tk.Radiobutton(controlModeFrame, text="User", variable=c,
											value=8,indicatoron=0,
											command=lambda : sendSettingPacket(m.get(),f.get(),p.get(),c.get()))
		controlModeRadioButton9=tk.Radiobutton(controlModeFrame, text="Auto Land", variable=c,
											value=9,indicatoron=0,
											command=lambda : sendSettingPacket(m.get(),f.get(),p.get(),c.get()))
		controlModeRadioButton10=tk.Radiobutton(controlModeFrame, text="Return Home", variable=c,
											value=10,indicatoron=0,
											command=lambda : sendSettingPacket(m.get(),f.get(),p.get(),c.get()))
		controlModeRadioButton11=tk.Radiobutton(controlModeFrame, text="Hover", variable=c,
											value=11,indicatoron=0,
											command=lambda : sendSettingPacket(m.get(),f.get(),p.get(),c.get()))
		controlModeRadioButton8.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)
		controlModeRadioButton9.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)
		controlModeRadioButton10.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)
		controlModeRadioButton11.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)
		
class statisticsThreadClass(threading.Thread):
	
	def __init__(self, master, PlotPacket,A):
		threading.Thread.__init__(self)
		statisticsFrame = tk.Frame(master)
		#h_dash=int((screenH-h-int(0.16*vidH))/5)-5# height of each setting box
		statisticsFrame.place(x=0,y=h,width=w,height=int(0.66*vidH))
		statisticsFrame.configure(bg='green')
		# statisticsFrame.grid(row = 2,
								# column = 0,
								# rowspan = 2,
								# columnspan = 1)
		# statisticsFrame.rowconfigure(2, weight = 1)
		# statisticsFrame.columnconfigure(0, weight = 1)

		plotFrame = tk.Frame(statisticsFrame)
		plotFrameh=int(0.5*vidH)
		plotFrame.place(x=0,y=0,width=w,height=plotFrameh)
		#plotFrame.grid(row = 0, column = 0, sticky = tk.N + tk.S + tk.W + tk.E)
		# plotFrame.rowconfigure(1, weight = 1)
		# plotFrame.rowconfigure(0, weight = 1)
		
		# plotFrame.columnconfigure(0, weight = 1)
		# plotFrame.columnconfigure(1, weight = 1)
		# plotFrame.columnconfigure(2, weight = 1)
		# plotFrame.columnconfigure(3, weight = 1)
		# plotFrame.columnconfigure(4, weight = 1)
		# plotFrame.columnconfigure(5, weight = 1)
			
		
		stat_velocityBoxFrame = tk.Frame(statisticsFrame)
		#stat_velocityBoxFrame.grid(row = 1, column = 0, sticky = tk.N + tk.S + tk.W + tk.E)
		stat_accelerationBoxFrame = tk.Frame(statisticsFrame)
		#stat_accelerationBoxFrame.grid(row = 1, column = 1, sticky = tk.N + tk.S + tk.W + tk.E)
		stat_positionBoxFrame = tk.Frame(statisticsFrame)
		#stat_positionBoxFrame.grid(row = 1, column = 2, sticky = tk.N + tk.S + tk.W + tk.E)
		stat_rollBoxFrame = tk.Frame(statisticsFrame)
		#stat_rollBoxFrame.grid(row = 1, column = 3, sticky = tk.N + tk.S + tk.W + tk.E)
		stat_pitchBoxFrame = tk.Frame(statisticsFrame)
		#stat_pitchBoxFrame.grid(row = 1, column = 4, sticky = tk.N + tk.S + tk.W + tk.E)
		stat_yawBoxFrame = tk.Frame(statisticsFrame)
		#stat_yawBoxFrame.grid(row = 1, column = 5, sticky = tk.N + tk.S + tk.W + tk.E)

		rem_h=int(int(0.66*vidH)-plotFrameh)
		frame_wid=int(w/6)
		stat_velocityBoxFrame.place(x=0,y=plotFrameh,width=frame_wid,height=rem_h)
		stat_accelerationBoxFrame.place(x=frame_wid,y=plotFrameh,width=frame_wid,height=rem_h)
		stat_positionBoxFrame.place(x=2*frame_wid,y=plotFrameh,width=frame_wid,height=rem_h)
		stat_rollBoxFrame.place(x=3*frame_wid,y=plotFrameh,width=frame_wid,height=rem_h)
		stat_pitchBoxFrame.place(x=4*frame_wid,y=plotFrameh,width=frame_wid,height=rem_h)
		stat_yawBoxFrame.place(x=5*frame_wid,y=plotFrameh,width=w-5*frame_wid,height=rem_h)

		stat_ivelocity = tk.IntVar()
		stat_iacceleration = tk.IntVar()
		stat_iposition = tk.IntVar()
		stat_iroll = tk.IntVar()
		stat_ipitch = tk.IntVar()
		stat_iyaw = tk.IntVar()

		#quad = statVariables()


		# x = range(100)
		# y = range(100)
		# f = Figure(figsize = (3,3), dpi = 50)
		# a = f.add_subplot(111)
		self.fig = plt.figure(figsize = (5,5), dpi = 75)
		#self.ax = self.fig.add_axes( (0.05, .05, .50, .50), axisbg=(.75,.75,.75), frameon=False)
		self.ax = self.fig.add_subplot(111)
		plt.title('Live Plot')
		plt.xlabel('Time(s)')
		plt.ylabel('Variable Name')
		# plt.show()

		canvas = FigureCanvasTkAgg(self.fig, plotFrame)
		canvas.get_tk_widget().grid(row = 0, column = 0, sticky = tk.N + tk.S + tk.W + tk.E)
		#canvas.get_tk_widget().place(x=0,y=0,width=w,height=plotFrameh)
		canvas.get_tk_widget().rowconfigure(0, weight = 1)
		canvas.get_tk_widget().columnconfigure(0, weight=1)

		canvas.show()


		self.velocity_line = plt.plot([],[])[0]
		self.acceleration_line = plt.plot([],[])[0]
		self.position_line = plt.plot([],[])[0]
		self.roll_line = plt.plot([],[])[0]
		self.pitch_line = plt.plot([],[])[0]
		self.yaw_line = plt.plot([],[])[0]

		self.velocity_line.set_data([],[])
		self.acceleration_line.set_data([],[])
		self.position_line.set_data([],[])
		self.roll_line.set_data([],[])
		self.pitch_line.set_data([],[])
		self.yaw_line.set_data([],[])

		self.PlotPacket = PlotPacket

		# velocity_line = canvas.create_line(0,0,0,0, fill = 'red')
		# acceleration_line = canvas.create_line(0,0,0,0, fill = 'blue')'
		# position_line = canvas,create_line(0,0,0,0, fill = 'green')
		# roll_line = canvas.create_line(0,0,0,0, fill = 'black')
		# pitch_line = canvas.create_line(0,0,0,0, fill = ')		

		stat_velocityCheckButton = tk.Checkbutton(stat_velocityBoxFrame, text = 'Velocity', variable = stat_ivelocity, command = lambda : self.Plot('Velocity', stat_ivelocity.get(), canvas))
		stat_accelerationCheckButton = tk.Checkbutton(stat_accelerationBoxFrame, text = 'Acceleration', variable = stat_iacceleration, command = lambda : self.Plot('Acceleration', stat_iacceleration.get(), canvas))
		stat_positionCheckButton = tk.Checkbutton(stat_positionBoxFrame, text = 'Position', variable = stat_iposition, command = lambda : self.Plot('Position', stat_iposition.get(), canvas))
		stat_rollCheckButton = tk.Checkbutton(stat_rollBoxFrame, text = 'Roll', variable = stat_iroll, command = lambda : self.Plot('Roll', stat_iroll.get(), canvas))
		stat_pitchCheckButton = tk.Checkbutton(stat_pitchBoxFrame, text = 'Pitch', variable = stat_ipitch, command = lambda : self.Plot('Pitch', stat_ipitch.get(), canvas))
		stat_yawCheckButton = tk.Checkbutton(stat_yawBoxFrame, text = 'Yaw', variable = stat_iyaw, command = lambda : self.Plot('Yaw', stat_iyaw.get(), canvas))

		stat_velocityCheckButton.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
		stat_accelerationCheckButton.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
		stat_positionCheckButton.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
		stat_rollCheckButton.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
		stat_pitchCheckButton.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
		stat_yawCheckButton.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)

		plt.close(self.fig)			
			
		# def AnimatePlot():
		# pullData = open('').read()
		# dataList = pullData.split('\n')
		# xList = []
		# yList = []
		# zList =  []

		# for eachLine in dataList
			# if len(eachLine) > 1:
				# x, y = eachLine.split(',')
				# xList.append(int(x))
				# yList.append(int(y))
				# zList.append(int(z))

		# a.clear()
		# a.plot(xList,yList)

		# updated_data, = plt.plot([], [])

		#Whenever new data is received run this function to update the data array
		# def update_line(new_data,ax, data):
		# updated_data_x = data.set_xdata(np.append(data.get_xdata(), new_data))
		# updated_data_y = data.set_ydata(np.append(data.get_ydata(), new_data))
		# return updated_data_x, updated_data_y
		# ax.relim()
		# ax.autoscale_view()
		# plt.draw

		# def animate():		
		# anim = animation.FuncAnimation(fig, animate, init_func = init, frames = 360, interval = 5, blit = True)
		
	def Plot(self,var_name, var_state, canvas):
		
		if var_state == 1:
			
			if var_name is "Velocity":
				t = np.arange(0.0, 3.0, 0.01)
				velocity = np.sin(np.pi*t)
				self.velocity_line.set_data(t, velocity)
				
			elif var_name is "Acceleration":
				t = np.arange(0.0, 3.0, 0.01)
				acceleration = np.sin(3*np.pi*t)
				self.acceleration_line.set_data(t, acceleration)
				
			elif var_name is "Position":
				t = np.arange(0.0, 3.0, 0.01)
				position = np.sin(5*np.pi*t)
				self.position_line.set_data(t, position)
				
			elif var_name is "Roll":
				t = np.arange(0.0, 3.0, 0.01)
				roll = np.sin(7*np.pi*t)
				self.roll_line.set_data(t, roll)
				
			elif var_name is "Pitch":
				t = np.arange(0.0, 3.0, 0.01)
				pitch = np.sin(9*np.pi*t)
				self.pitch_line.set_data(t, pitch)
				
			elif var_name is "Yaw":
				t = np.arange(0.0, 3.0, 0.01)
				yaw = np.sin(11*np.pi*t)
				self.yaw_line.set_data(t, yaw)
				
			print "Plotting " + var_name
			print 'The Packet being plotted is: ' + str(self.PlotPacket[:]) #This is the packet that would be sent to the Settings Thread for plotting
			self.ax.relim()
			self.ax.autoscale_view()
			# plt.gcf().canvas.draw()
			canvas.draw()
			plt.pause(.001)

			# self.a.plot(t, s)			
			# self.canvas = FigureCanvasTkAgg(self.f, self.plotFrame)
			# self.canvas.draw()
			
		else:
		
			if var_name is "Velocity":
				self.velocity_line.set_data([],[])
				
			elif var_name is "Acceleration":
				self.acceleration_line.set_data([],[])
				
			elif var_name is "Position":
				self.position_line.set_data([],[])
				
			elif var_name is "Roll":
				self.roll_line.set_data([],[])
				
			elif var_name is "Pitch":
				self.pitch_line.set_data([],[])
				
			elif var_name is "Yaw":
				self.yaw_line.set_data([],[])		
			
			print "Not Plotting" + var_name
			
			self.ax.relim()
			self.ax.autoscale_view()
			# plt.gcf().canvas.draw()
			canvas.draw()
			plt.pause(.001)
			
class Video(threading.Thread):
    # Manages video streaming and Video Controls
    def __init__(self,master):
        threading.Thread.__init__(self)
        self.vidFrame=tk.Frame(master,bg='green')
        #stickyelf.vidFrame.config(padx=20)
 
        self.vidFrame.place(x=w,y=h,width=vidW,height=vidH)
        self.vidLabel=tk.Label(self.vidFrame)

        # self.vidLabel.grid(row=1,
        #               column=1,
        #               rowspan=3,
        #               columnspan=2,
        #               sticky=tk.S+tk.N+tk.E+tk.W)

        self.vidLabel.pack(fill=tk.BOTH,expand=1)

        # def enforceAspectRatio(event):
        #     dw=int(0.7*event.width)
        #     dh=int(0.75*event.width)
        #     print "w,h is ",event.width, event.height,dw,dh
        #     self.vidLabel.config(width=dw,height=dh)
        #     print "frame size is", self.vidFrame.winfo_width(), self.vidFrame.winfo_height()  

        #self.vidFrame.bind("<Configure>",enforceAspectRatio)
        
        # Intialize vidControl Frame
        vidControl =tk.Frame(master)
        vidControl.place(x=w+vidW,y=h,width=screenW-vidW-w,height=int(0.33*screenH))
        self.recordButton = tk.Button(vidControl, 
                                        text="Record", 
                                        bd = 1,
                                        bg= "Red",
                                        command= self.recordVideo)
        w_dash=int(0.5*(screenW-vidW-w))
        h_dash=int(0.5*(int(0.33*vidH)))
        self.recordButton.place(x=0,y=0,width=w_dash,height=h_dash)
        toggleCameraButton = tk.Button(vidControl, 
                                            text = "Camera Toggle", 
                                            command=self.toggleCamera)
        toggleCameraButton.place(x=0,y=h_dash,width=w_dash,height=h_dash)
        screenshotButton = tk.Button(vidControl, 
                                            text = "Screen Capture",
                                            command=self.screenshot)
        screenshotButton.place(x=w_dash,y=0,width=screenW-vidW-w-w_dash,height=h_dash)
        depthToggleButton = tk.Button(vidControl,
                                        text = "Show Depth",
                                        command=self.depthToggle)
        depthToggleButton.place(x=w_dash,y=h_dash,width=screenW-vidW-w-w_dash,height=(int(0.33*vidH)-h_dash))

    def run(self):
        self.saveVideoToggle=0 # Intialize videocapture toggle to zero
        self.takeScreenShot=0 # Intialize screenshot toggle to be zerod
        self.cameraChannelOnVideo=0 # Intialize Camera Channel to default to zero
        self.vid_cap = cv2.VideoCapture(self.cameraChannelOnVideo) # Assign channel to video capture
        self.showVideo(self.vidLabel,self.vidFrame)

    def recordVideo(self):
        try:
            w=int(self.vid_cap.get(3))
            h=int(self.vid_cap.get(4))
            fourcc = cv2.cv.CV_FOURCC('D','I','V','X')
            outputFPS = 20.0
            self.vidWriter = cv2.VideoWriter('Video_'+str(self.cameraChannelOnVideo)+
                            '_'+strftime("%c")+'.avi', fourcc, outputFPS, (w, h), True)
            #self.videoWriter.open("output.avi", fourcc, outputFPS, (w, h))
            self.saveVideoToggle=1 # start capturing video frames in video loop
            self.recordButton.configure(text="Stop", 
                                        bg= "black",
                                        fg ="snow",
                                        command=self.stopVideoRecord)
        except:
            print "Something bad happened with recordVideo :("

    def stopVideoRecord(self):
        self.saveVideoToggle=0
        print "Stopped Recording Video"
        self.recordButton.configure(text="Record",
                                    bg="Red",
                                    fg ="Black",
                                    command= self.recordVideo)
        self.vidWriter.release()

    def depthToggle(self):
        print 'Depth Toggling function goes here- Read from the stereo camera manual how to do this'

    def screenshot(self):
        self.takeScreenShot=1
        print 'Took a Screenshot!'

    def toggleCamera(self):
        # works for only two cameras
        #try: # error handling is not working
        newChannel = 1-self.cameraChannelOnVideo
        self.vid_cap = cv2.VideoCapture(newChannel)
        self.cameraChannelOnVideo=newChannel

        isChannelValid,_= self.vid_cap.read(0)
        if isChannelValid:
            self.cameraChannelOnVideo=newChannel
        else:
            self.cameraChannelOnVideo=0
            self.vid_cap = cv2.VideoCapture(self.cameraChannelOnVideo) # result to default camera method
        print 'Displaying Video Feed from Camera Number = ',self.cameraChannelOnVideo 
        # except:
        #     print 'Hi'
        
    def showVideo(self,vidLabel,vidFrame):
        _, frame = self.vid_cap.read(0) 
        frame = cv2.flip(frame, 1) # flips the video feed
        cv2image = cv2.cvtColor(frame,cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
    
        # save image if screenshot toggle is on
        if self.takeScreenShot==1:
            img.save('Camera '+str(self.cameraChannelOnVideo)+'_'+strftime("%c")+'.jpg')
            self.takeScreenShot=0

        if self.saveVideoToggle==1:
           self.vidWriter.write(frame)

        # frameAspectRatio = (float(vidFrame.winfo_width())/float(vidFrame.winfo_height()))
        # if frameAspectRatio > (1.333): # Frame is wider than it needs to be
        #    new_height= int(10*(vidFrame.winfo_height()/10)) # round image size to nearest
        #    new_width=int(1.33*new_height)
        # else: # Frame is taller than it needs to be
        #     new_width= int(10*(vidFrame.winfo_width()/10))
        #     new_height =int(0.75* new_width)
        # img_resize= img.resize([new_width,new_height]) #resizing image
        imgtk = ImageTk.PhotoImage(image=img)
        vidLabel.imgarbage = imgtk # for python to exclude image from garbage collection
        vidLabel.configure(image=imgtk)
        vidLabel.after(2,self.showVideo,vidLabel,vidFrame) # calls the method after 10 ms
		
class tkinterGUI(tk.Frame):
	def __init__(self, PlotPacket, startBool, stopBool, msgIDs):
		tk.Frame.__init__(self)
		# self.grid()
		# self.grid(sticky = tk.N + tk.S + tk.E + tk.W)
		# make top level of the application stretchable and space filling
		top=self.winfo_toplevel()

		global screenH, screenW,vidH, vidW, h, w       
		screenH= top.winfo_screenheight()-25 # take 25 pixels to account for top bar
		screenW =top.winfo_screenwidth()

		# Defining gemotery of outermost Frame 
		geom_string = "%dx%d+0+0" % (screenW,screenH)
		# Assigning max height and width to outer Frame - Maximize Frame Size
		top.wm_geometry(geom_string)
		self.place(x=0, y=0,width=screenW,height=screenH)
		# Retrive scalled dimensions according to schema 
		[vidH, vidW, h, w]=self.masterWidgetSizes()

		##-------------For implementing Grid Method-------------------##
		# top.rowconfigure(0, weight=1)
		# top.columnconfigure(0, weight=1)
		# make all rows and columns grow with the widget window ; weight signifies relative rate of window growth
		# self.rowconfigure(0, weight=1)
		# self.rowconfigure(1, weight=1)
		# self.rowconfigure(2, weight=1)
		# self.rowconfigure(3, weight=1)
		# self.rowconfigure(4, weight=1)
		# self.rowconfigure(5, weight=1)
		# self.rowconfigure(6, weight=1)
		# self.rowconfigure(7, weight=1)
		# self.rowconfigure(8, weight=1)
		# self.rowconfigure(9, weight=1)
		# self.columnconfigure(0, weight=1)
		# self.columnconfigure(1, weight=1)
		# self.columnconfigure(2, weight=1)
		# self.columnconfigure(3, weight=1)

		# Set up the GUI
		# console = tk.Button(self, text='Done', command=endCommand)
		# console.grid(row = 5, column = 0, rowspan = 3, columnspan = 2)

		videoThread=Video(self)
		settingsThread = settingsThreadClass(self)
		loggingThread = loggingThreadClass(self, startBool, stopBool)
		statisticsThread = statisticsThreadClass(self, PlotPacket, msgIDs)
		myUAVThread = myUAVThreadClass(self)
		otherDrones=otherdrones(self)

		videoThread.setDaemon(True) 
		settingsThread.setDaemon(True)
		loggingThread.setDaemon(True)
		statisticsThread.setDaemon(True)
		myUAVThread.setDaemon(True)
		otherDrones.setDaemon(True)

		videoThread.start() # becomes mainthread
		settingsThread.start()
		loggingThread.start()
		statisticsThread.start()
		myUAVThread.start()
		otherDrones.start()

		print '# active threads are ',threading.enumerate()
		
	def masterWidgetSizes(self):
		# Obtain Screen Height and Width in pixel units
		screenH=self.winfo_screenheight()
		screenW=self.winfo_screenwidth()

		'''
		Get Video Dimensions from Primary Camera
		CAUTION : If primary and Secondary Cameras have different 
		dimensions then scaling happens with respect to primary camera
		'''  
		temp = cv2.VideoCapture(0) # Assign channel to video capture
		vidW=temp.get(3) # Frame Height
		vidH=temp.get(4) # Camera Frame Height
		temp.release() # Release camera object

		print vidW,vidH
		camAspectRatio= vidW/vidH

		if screenH - vidH < 100: # Not enough height for other widgets
			# Reduce video height
			vidH=screenH-100
			vidW=int(vidH*camAspectRatio)
			h= 100
			w= int(0.5*(screenW-vidW))

		if screenW - vidW < 200:# Not enough width for other widgets
			vidW=screenW-200
			vidH=int(vidW/camAspectRatio)
			h= screenH-vidH
			w= 100

		else: # Enough width and Height for all widgets
			h= (screenH-vidH)
			w= int(0.5*(screenW-vidW))

		return vidH, vidW, h, w


		'''
		h= (screenH-vidH)
		w= 0.5*(screenW-vidW)
		 ___________________________________________________________
		|             |                                             |
		|   myDrone   |             otherDrones                     |        
		|     w, h    |            w+VidW, h                        |
		|_____________|_____________________________________________|
		|             |                             |               |
		|    Status   |              Video          |   vidControl  |
		|     w,      |         Native Camera       |  w, 1/3*vidH  |
		|   2/3*vidH  |            Resolution       |_______________|
		|             |           vidW*vidH         |               |
		|             |                             |     Logging   |
		|             |                             |  w, 2/3*vidH  |
		|_____________|                             |               |
		|    modes    |                             |               |
		|      w,     |                             |               |
		|  1/3*vidH   |                             |               |
		|_____________|_____________________________|_______________|
		'''
		
def udpConnection():
	IPaddress = '192.168.1.107' # IP to send the packets
	portNum = 14551 # port number of destination
	device = 'udpout:' + str(IPaddress) + ':' + str(portNum)
	baudrate = 57600
	
	parser = ArgumentParser(description=__doc__)
	#parser.add_argument("--baudrate", type=int,
	#				  help="master port baud rate", default=57600)
	#parser.add_argument("--device", default=UDPaddr,required=True, help="serial device")
	parser.add_argument("--rate", default=4, type=int, help="requested stream rate")
	parser.add_argument("--source-system", dest='SOURCE_SYSTEM', type=int,
					  default=255, help='MAVLink source system for this GCS')
	parser.add_argument("--showmessages", action='store_true',
					  help="show incoming messages", default=False)
	args = parser.parse_args()
	# create a mavlink serial instance
	master = mavutil.mavlink_connection(device, baud=baudrate)

	# wait for the heartbeat msg to find the system ID
	#wait_heartbeat(master)

	def wait_heartbeat(m):
		'''wait for a heartbeat so we know the target system IDs'''
		print("Waiting for APM heartbeat")
		m.wait_heartbeat()
		print("Heartbeat from APM (system %u component %u)" % (m.target_system, m.target_system))
	
	return master
	
def UDP(Packets, startLogging, stopLogging,UDPmaster, msgIDs):
	UDPlistenThread=listener(10, Packets, startLogging, stopLogging, UDPmaster, msgIDs) # sizeOfRingBuffer
	UDPlistenThread.setDaemon(True)
	
	#UDPlogThread=logger(Packets)
	#UDPlogThread.setDaemon(True)
	
	print('UDP process starting')
	UDPlistenThread.start()

	#UDPlogThread.start()

	print 'Pack:' + str(Packets[:]) #The Packet which will be outputted to the plotter
	UDPlistenThread.join()
	#UDPlogThread.join()
	
	# Declaring global for killUDPprocesscounter
	"""
	print "UDP process started"

	i=0
	while(killUDPprocessCounter):
		i=i+1
		sleep(0.05)
		if i%20==0:
			print "UDP counter is",killUDPprocessCounter, "i is ", i

	print "Came out of while loop"
	"""
	#UDPlistenThread.exit()
	#UDPlogThread.exit()

def closeProgram():
    global killUDPprocessCounter
    killUDPprocessCounter=0
    print "here I am ", killUDPprocessCounter
	
def startTkinter(PlotPacket,startBool,stopBool, msgIDs):
    root = tkinterGUI(PlotPacket,startBool,stopBool, msgIDs)
    root.master.title("Azog") # Name of current drone, Here it is Azog
    root.mainloop()
	
def sendSettingPacket(m,f,p,c):
	# m - Mapping modes are : SLAM (0) or VICON pos input (1)
	# f - Flight modes are : Altitude (2) vs Manual Thrust (3) vs POS hold (4)
	# p - Pilot reference mode: global (5), First Person View (6), PPV (7)
	# c - Control mode: User (8) , Auto land (9), Come back home (10), Circle Mode (11)
	print "New Settings received :",'Mapping Mode',m,'\tFlight Mode :',f,'\tPilot Reference Mode',p,'\tControl Mode',c

def saveDroneData():
	pass
	
def killDroneMethod():
    print 'this should send a specific MAVlink packet'
    
    # start tkinter stuff
	
def broadcast():
	UDPConnectionThread = udpConnection()
	UDPConnectionThread.setDaemon(True)
	
	UDPConnectionThread.start()
	
	UDPConnectionThread.join()    

    # Data content of the UDP packet as hex
    # packetData = 'f1a525da11f6'.decode('hex')
     
    # initialize a socket
    # SOCK_DGRAM specifies that this is UDP
    # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
     
    # try:
        # connect the socket
        # s.connect((IPADDR, PORTNUM))
     
        # send the packet
        # s.send(packetData)
    # except:
        # pass
     
    # close the socket
    # s.close()

    # while 1:

        # print "Sent packets"
        # sleep(15)
	
class AutoScrollbar(tk.Scrollbar):
    # a scrollbar that hides itself if it's not needed.  only
    # works if you use the grid geometry manager.
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            # grid_remove is currently missing from Tkinter!
            self.tk.call("grid", "remove", self)
        else:
            self.grid()
        tk.Scrollbar.set(self, lo, hi)
    def pack(self, **kw):
        raise TclError, "cannot use pack with this widget"
    def place(self, **kw):
        raise TclError, "cannot use place with this widget"

def main():
    #global udpProcess # try to kill updprocess using startTkinter
	lock = Lock()
	n = Array('i', [0]*10, lock = lock) #Packet Storage Array for transfer between processes
	msgIDs = Array('i', [0]*10, lock = lock) #Message ID Storage Array for transfer between processes
	startLogging = Value('i', 0, lock = lock)
	stopLogging = Value('i', 1, lock = lock)
	print 'Start Bool: ' + str(startLogging.value) + '\n'
	print 'Stop Bool: ' + str(stopLogging.value) + '\n'
	UDPmaster = udpConnection();
	#udpProcess = Process(name = 'UDP Process', target = UDP, args=(n,startLogging,stopLogging,UDPmaster,msgIDs))
	TkinterProcess = Process(name='Tkinter Process', target=startTkinter, args=(n,startLogging,stopLogging,msgIDs))
    # broadcastProcess = Process(name='Broadcasting Process', target=broadcast)
	#udpProcess.start()
	TkinterProcess.start()
	#udpProcess.join()
	TkinterProcess.join()
	
if __name__ == '__main__':
	main()