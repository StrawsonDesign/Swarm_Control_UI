import Tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
# matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg #, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style, ticker

import csv
import traceback

from PIL import ImageTk , Image # for image conversion
#import cv2 # OpenCV for video handling
import tkFont, threading, Queue, tkMessageBox
from time import strftime, sleep, time
from collections import deque, OrderedDict
import socket # for sending across UDP packets 
from multiprocessing.sharedctypes import Value, Array
from ctypes import Structure, c_double, c_short, c_long
from multiprocessing import Process, Lock, Manager #multiprocessing

from argparse import ArgumentParser

from pymavlink import mavutil

allDronesList=['Othrod','The Great Goblin','Boldog','Ugluk','Bolg','Orcobal','More Orcs','Orc1','Orc2','Orc3','Orc4']
activeDronesList=['Othrod','Ugluk','Bolg','Orcobal']

style.use("ggplot")

class listener(threading.Thread):
    def __init__(self, sizeOfBuffer, messages, startLogging, Log_msgIDs, new_data):
		threading.Thread.__init__(self)
		#global receivedPacketBuffer # Must declare gloabl varibale prior to assigning values
		#global receivedPacketBufferLock
		self.receivedPacketBuffer_1= deque([], sizeOfBuffer)
		self.receivedPacketBuffer_2= deque([], sizeOfBuffer)
		self.receivedPacketBufferLock = threading.Lock()
		print "Initialized Ring Buffer as size of", sizeOfBuffer
		#self.isBufferBusy=0
		self.messages = messages
		self.sizeOfBuffer = sizeOfBuffer
		self.startLogging = startLogging
		
		################################
		self.UDPmaster = udpConnection() #Setup the UDP Connection!!
		self.UDPmaster.mav.heartbeat_send(1,  2, 3, 4, 5, 6)
		################################
		
		#print self.UDPmaster
		self.Log_msgIDs = Log_msgIDs
		
		self.message_Attitude_Boot_Time = []
		self.message_Roll = []
		self.message_Pitch = []
		self.message_Yaw = []
		
		self.message_Battery_Boot_Time = []
		self.message_Battery_Voltage =[]
		
		self.message_Position_Boot_Time = []
		self.message_X_Position = []
		self.message_Y_Position = []
		self.message_Z_Position = []
		
		self.Use_First_Buffer = True
		self.Use_Second_Buffer = False
		self.outfile='data.csv'
		self.new_data = new_data
		# print self.Log_msgIDs[:]
    # def logger(self, csv_writer):
	
		# try:
			# csv_writer.writerow([self.packet])
			
		# except(KeyboardInterrupt, SystemExit):
			# raise
			
		# except:
			# traceback.print_exc()
			
		#self.log_dummy=open(outfile,"w",1) # use a = append mode, buffering set to true
		# print "file", outfile, "is opened"
		# print "The packet delivered is: " + str(self.Packets[:])
		# tempData=""
		# m=0
		#while m<20: # change this
		#sleep(1)
		#if self.receviedPacketBufferLock.acquire(0):
			#try:
		# i = 0
		# for i in xrange(self.sizeOfBuffer): # empty the entire list
		#self.listenerobject.isBufferBusy=1
			# data=strftime("%c") + "\t" + str(self.Packets[i]) + "\n"
			# tempData=tempData+data
			# print "Packet: " + str(self.Packets[i])
			# i += 1
	#except IndexError:
		#print "Index Error occured, couldn't pop left on an empty deque"

	#finally:
		#receviedPacketBufferLock.release()
		# print "Released Packet:" + str(self.Packets[:]) #This is the packet that should be released to the plotter
		# m += 1
		#print "M is", m
		# if m%self.sizeOfBuffer==0:
			# self.log_dummy.write(tempData)
			# print "WROTE TO DISK"
			# tempData=""
			
    def run(self):
		i = 0
		with open(self.outfile, 'w') as csv_handle:
			# for i in xrange(100): # replace by reading head
			while 1:
				#self.UDPmaster.mav.sys_status_send(1, 2, 3, 4, 5, 6, 7, 8, 9 ,10, 11, 12,13)
				#self.UDPmaster.mav.gps_raw_send(1, 2, 3, 4, 5, 6, 7, 8, 9)
				#self.UDPmaster.mav.attitude_send(1, 2, 3, 4, 5, 6, 7)
				#self.UDPmaster.mav.vfr_hud_send(1, 2, 3, 4, 5, 6)
				i = i + 1
				sleep(.1)
				self.new_data.value = 0
				try:
					if self.receivedPacketBufferLock.acquire(1):
						#self.receviedPacketBuffer.append(i)
						#print self.UDPmaster
						data = self.UDPmaster.recv() #This should recv the data from the socket
						
						if self.startLogging.value == 1:
						
							if self.Use_First_Buffer == True:
								self.receivedPacketBuffer_1.append(data)
							
							elif self.Use_Second_Buffer == True:
								self.receivedPacketBuffer_2.append(data)
							
						else:
							self.receivedPacketBuffer_1.append(data)
						
					else:
						print "Lock was not ON"
					
				finally:
					self.receivedPacketBufferLock.release()
					# self.Log_msgIDs.release()
					# print "Released Buffer are: ", self.receviedPacketBuffer, "\n"
					# print "Released Buffer msg IDs are: ", self.receviedPacketBufferMsgId, "\n"
					if i == 1:
						BootTime = time()
						
					if i%self.sizeOfBuffer==0:
					
						for x in xrange(self.sizeOfBuffer):
							if self.startLogging.value == 1:
								if self.Use_First_Buffer == True:
									self.packet = self.UDPmaster.mav.parse_char(self.receivedPacketBuffer_1.popleft())
									
								elif self.Use_Second_Buffer == True:
									self.packet = self.UDPmaster.mav.parse_char(self.receivedPacketBuffer_2.popleft())
									
							else:
								self.packet = self.UDPmaster.mav.parse_char(self.receivedPacketBuffer_1.popleft())
							
							if self.packet is not None:
								self.UDPmaster.post_message(self.packet)
								# print 'Call Logger'
								
								if self.packet.get_msgId() == 30: #Attitude Packet (Contains Roll, Pitch, Yaw)
									self.message_Attitude_Boot_Time.append(time() - BootTime)
									self.message_Roll.append(self.packet.roll)			#roll  : Roll angle (rad, -pi..+pi) (float)
									self.message_Pitch.append(self.packet.pitch)		#pitch : Pitch angle (rad, -pi..+pi) (float)
									self.message_Yaw.append(self.packet.yaw)				#yaw   : Yaw angle (rad, -pi..+pi) (float)
									
								elif self.packet.get_msgId() == 1:
									self.message_Battery_Boot_Time.append(time() - BootTime)
									self.message_Battery_Voltage.append(self.packet.voltages)
									
								elif self.packet.get_msgId() == 104:
									self.message_Position_Boot_Time.append(time() - BootTime)
									self.message_X_Position.append(self.packet.x)
									self.message_Y_Position.append(self.packet.y)
									self.message_Z_Position.append(self.packet.z)
									
								# print self.packet.get_msgId()
								
								# print self.Log_msgIDs[:]
								# print self.packet.get_msgId() in self.Log_msgIDs[:]
								if self.startLogging.value == True and self.packet.get_msgId() in self.Log_msgIDs[:]: # Check if the GUI should be Logging data
										print 'Logging Data'
										csv_writer = csv.writer(csv_handle, delimiter =',')
										# self.logger(csv_writer)
										UDPlogThread = logger(csv_writer, self.packet)
										UDPlogThread.setDaemon(True)
										UDPlogThread.start()
										UDPlogThread.join()
								
								else:
									# print "Don't need to record data yet"
									pass
							else:
								# print 'No Packet!''
								pass
								
							if x == self.sizeOfBuffer-1:
								self.messages['ATTITUDE'] = {'BootTime':self.message_Attitude_Boot_Time, 'Roll': self.message_Roll, 'Pitch': self.message_Pitch, 'Yaw': self.message_Yaw}
								self.messages['SYS_STATUS'] = {'BootTime':self.message_Battery_Boot_Time, 'Battery_Voltage': self.message_Battery_Voltage}
								self.messages['VICON_POSITION_ESTIMATE'] = {'BootTime': self.message_Position_Boot_Time, 'X': self.message_X_Position, 'Y': self.message_Y_Position, 'Z': self.message_Z_Position}
								self.new_data.value = 1
								# print self.messages['ATTITUDE']['BootTime']
								self.message_Attitude_Boot_Time = []
								self.message_Roll = []
								self.message_Pitch = []
								self.message_Yaw = []
								
								self.message_Battery_Boot_Time = []
								self.message_Battery_Voltage = []
								
								self.message_Position_Boot_Time = []
								self.message_X_Position = []
								self.message_Y_Position = []
								self.message_Z_Position = []
								
								# print self.messages
								
						if self.startLogging.value == 1:
							if self.Use_First_Buffer == True:
								self.Use_First_Buffer = False
								self.Use_Second_Buffer = True
								
							elif self.Use_Second_Buffer == True:
								self.Use_First_Buffer = True
								self.Use_Second_Buffer = False
								
						else:
							self.Use_First_Buffer = True
								
							#val = self.receviedPacketBuffer.popleft()
							#self.Packets[x] = val
							#self.msgIDs[x] = self.receviedPacketBufferMsgId.popleft()
							#print "Just popped " + str(val) + '\n'
						#print 'Packet Buffer: ' + str(self.Packets[:]) + '\n'
						#print 'MSGIds: ' + str(self.msgIDs[:]) +'\n'
				
class logger(threading.Thread):
	def __init__(self,csv_writer, packet):
		threading.Thread.__init__(self)
		self.csv_writer = csv_writer
		self.packet = packet
		
	def run(self):
		try:
			self.csv_writer.writerow([self.packet])
			
		except(KeyboardInterrupt, SystemExit):
			raise
			
		except:
			traceback.print_exc()

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
	
	def __init__(self, master, startBool, Log_msgIDs):
		threading.Thread.__init__(self)
		loggingFrame = tk.Frame(master)
		h_dash=int((screenH-h-int(0.25*vidH))/5)-5# height of each setting box
		loggingFrame.place(x=w+vidW,y=h+int(0.25*vidH),width=screenW-vidW-w,height=screenH-h-int(0.25*vidH)-25)
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
		
		log_startButtonFrame.place(x=0, y=4*h_dash, width=w/2, height=h_dash)
		log_stopButtonFrame.place(x=w/2, y=4*h_dash, width=w/2, height=h_dash)
		
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
		
		self.Log_msgIDs = Log_msgIDs
		self.loggingVariables = []
		self.msgIDs = []
		self.startLogging = startBool
		
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
		print 'Start Recording Data'
		#print 'Start Bool: ' + str(self.startLogging.value) + '\n'
		#print 'Stop Bool: ' + str(self.stopLogging.value) + '\n'
		
	def stopRecording(self):
		self.startLogging.value = 0
		print 'Stop Recording Data'
		#print 'Start Bool: ' + str(self.startLogging.value) + '\n'
		#print 'Stop Bool: ' + str(self.stopLogging.value) + '\n'
		
	def logVariables(self, var_Name, var_State):
	
		if var_State == 1:
			self.loggingVariables.append(var_Name)
			
			print self.loggingVariables
			
			if 'Attitude' is var_Name:
				self.Log_msgIDs.append(30)
				
			elif 'Position' is var_Name:
				self.Log_msgIDs.append(104)
				
			elif 'Velocity' is var_Name:
				self.Log_msgIDs.append(123890122)
				
			elif 'Battery' is var_Name:
				self.Log_msgIDs.append(1)
				
			print self.Log_msgIDs	
			
		elif var_State == 0:			
			
			if 'Attitude' is var_Name:
				ivar_Name = self.Log_msgIDs.index(30)
				print ivar_Name
				self.Log_msgIDs.pop(ivar_Name)

				
			elif 'Position' is var_Name:
				ivar_Name = self.Log_msgIDs.index(104)
				self.Log_msgIDs.pop(ivar_Name)
				
			elif 'Velocity' is var_Name:
				ivar_Name = self.Log_msgIDs.index(123890122)
				self.Log_msgIDs.pop(ivar_Name)
				
			elif 'Battery' is var_Name:
				ivar_Name = self.Log_msgIDs.index(1)
				self.Log_msgIDs.pop(ivar_Name)		
			
			ivar_Name = self.loggingVariables.index(var_Name)
			self.loggingVariables.pop(ivar_Name)
			
			print self.loggingVariables
			# print self.msgIDs
			print self.Log_msgIDs
			
		self.Log_names = self.loggingVariables
		# self.Log_msgIDs = self.msgIDs
			
		
		
		#self.msgIDs = {'Attitude': 30, 'Position': 104, 'Velocity': ?????????, 'Battery': 1}
		
	def run(self):
		print "Log names: " + str(self.loggingVariables)
		print "Log message IDs: " + str(self.Log_msgIDs)
		
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
	def __init__(self, master, messages, new_data):
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
		plotFrameh = int(0.5*vidH)+20
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
		
		
		# stat_velocityBoxFrame = tk.Frame(statisticsFrame)
		#stat_velocityBoxFrame.grid(row = 1, column = 0, sticky = tk.N + tk.S + tk.W + tk.E)
		# stat_accelerationBoxFrame = tk.Frame(statisticsFrame)
		#stat_accelerationBoxFrame.grid(row = 1, column = 1, sticky = tk.N + tk.S + tk.W + tk.E)
		stat_xPositionBoxFrame = tk.Frame(statisticsFrame)
		stat_yPositionBoxFrame = tk.Frame(statisticsFrame)
		stat_zPositionBoxFrame = tk.Frame(statisticsFrame)
		#stat_positionBoxFrame.grid(row = 1, column = 2, sticky = tk.N + tk.S + tk.W + tk.E)
		stat_rollBoxFrame = tk.Frame(statisticsFrame)
		#stat_rollBoxFrame.grid(row = 1, column = 3, sticky = tk.N + tk.S + tk.W + tk.E)
		stat_pitchBoxFrame = tk.Frame(statisticsFrame)
		#stat_pitchBoxFrame.grid(row = 1, column = 4, sticky = tk.N + tk.S + tk.W + tk.E)
		stat_yawBoxFrame = tk.Frame(statisticsFrame)
		#stat_yawBoxFrame.grid(row = 1, column = 5, sticky = tk.N + tk.S + tk.W + tk.E)

		rem_h=int(int(0.66*vidH)-plotFrameh)
		frame_wid=int(w/6)
		# stat_velocityBoxFrame.place(x=0,y=plotFrameh,width=frame_wid,height=rem_h)
		# stat_accelerationBoxFrame.place(x=frame_wid,y=plotFrameh,width=frame_wid,height=rem_h)
		stat_xPositionBoxFrame.place(x=0,y=plotFrameh,width=frame_wid,height=rem_h)
		stat_yPositionBoxFrame.place(x=frame_wid,y=plotFrameh,width=frame_wid,height=rem_h)
		stat_zPositionBoxFrame.place(x=2*frame_wid,y=plotFrameh,width=frame_wid,height=rem_h)
		stat_rollBoxFrame.place(x=3*frame_wid,y=plotFrameh,width=frame_wid,height=rem_h)
		stat_pitchBoxFrame.place(x=4*frame_wid,y=plotFrameh,width=frame_wid,height=rem_h)
		stat_yawBoxFrame.place(x=5*frame_wid,y=plotFrameh,width=w-5*frame_wid,height=rem_h)
		
		
		# stat_ivelocity = tk.IntVar()
		# stat_iacceleration = tk.IntVar()
		self.stat_iXposition = tk.IntVar()
		self.stat_iYposition = tk.IntVar()
		self.stat_iZposition = tk.IntVar()
		self.stat_iroll = tk.IntVar()
		self.stat_ipitch = tk.IntVar()
		self.stat_iyaw = tk.IntVar()

		#quad = statVariables()		
		
		# x = range(100)
		# y = range(100)
		# f = Figure(figsize = (3,3), dpi = 50)
		# a = f.add_subplot(111)
		self.fig = plt.figure(figsize = (5,5), dpi = 75)
		#self.ax = self.fig.add_axes( (0.05, .05, .50, .50), axisbg=(.75,.75,.75), frameon=False)
		self.ax = self.fig.add_subplot(111)		
		# self.ax.relim()
		# self.ax.autoscale_view()
		# plt.title('Live Plot')
		# plt.xlabel('Time(s)')
		# plt.ylabel('Variable Name')
		# plt.show()

		self.canvas = FigureCanvasTkAgg(self.fig, plotFrame)
		self.canvas.get_tk_widget().grid(row = 0, column = 0, sticky = tk.N + tk.S + tk.W + tk.E)
		self.canvas.get_tk_widget().place(x=0,y=0,width=w,height=plotFrameh)
		self.canvas.get_tk_widget().rowconfigure(0, weight = 1)
		self.canvas.get_tk_widget().columnconfigure(0, weight=1)		
		self.canvas.show()

		# self.velocity_line = plt.plot([],[])[0]
		# self.acceleration_line = plt.plot([],[])[0]
		
		# self.xPosition_line = plt.plot([],[])[0]
		# self.yPosition_line = plt.plot([],[])[0]
		# self.zPosition_line = plt.plot([],[])[0]
		# self.roll_line = plt.plot([],[])[0]
		# self.pitch_line = plt.plot([],[])[0]
		# self.yaw_line = plt.plot([],[])[0]
		
		self.ax.set_ylabel('Position (m)')
		
		# self.xPosition_line = self.ax.plot([], [], 'b', label='X Position')[0]
		# self.yPosition_line = self.ax.plot([], [], 'g',label='Y Position')[0]
		# self.zPosition_line = self.ax.plot([], [], 'r',label='Z Position')[0]
		self.xPosition_line = self.ax.plot([], [])[0]
		self.yPosition_line = self.ax.plot([], [])[0]
		self.zPosition_line = self.ax.plot([], [])[0]
		
		self.ax2 = self.ax.twinx()
		self.ax2.set_ylabel('Rotation Angle (radians)')
		
		# self.roll_line 		= self.ax2.plot([], [], 'c',label='Roll')[0]
		# self.pitch_line 	= self.ax2.plot([], [], 'm',label='Pitch')[0]
		# self.yaw_line 		= self.ax2.plot([], [], 'k',label='Yaw')[0]
		self.roll_line 		= self.ax2.plot([], [])[0]
		self.pitch_line 	= self.ax2.plot([], [])[0]
		self.yaw_line 		= self.ax2.plot([], [])[0]
		
		# lines1, labels1 = self.ax.get_legend_handles_labels()
		# lines2, labels2 = self.ax2.get_legend_handles_labels()
		# L = self.ax2.legend(lines1+lines2, labels1+labels2, bbox_to_anchor = (0., 1.02, 1., .102), loc=3,
					# ncol=6, mode="expand", borderaxespad=0.)
		
		# plt.legend(bbox_to_anchor = (0., 1.02, 1., .102), loc=3,
					# ncol=6, mode="expand", borderaxespad=0.)
		# ax2.legend(bbox_to_anchor = (0., 1.02, 1., .102), loc=3,
		# ncol=2, mode="expand", borderaxespad=0.)
		# self.velocity_line.set_data([],[])
		# self.acceleration_line.set_data([],[])
		
		self.new_data = new_data
		self.messages = messages
		
		#if ('30' or '')in self.msgIds
		# velocity_line = canvas.create_line(0,0,0,0, fill = 'red')
		# acceleration_line = canvas.create_line(0,0,0,0, fill = 'blue')'
		# position_line = canvas,create_line(0,0,0,0, fill = 'green')
		# roll_line = canvas.create_line(0,0,0,0, fill = 'black')
		# pitch_line = canvas.create_line(0,0,0,0, fill = ')

		# stat_velocityCheckButton = tk.Checkbutton(stat_velocityBoxFrame, text = 'Velocity', variable = stat_ivelocity, command = lambda : self.Plot('Velocity', stat_ivelocity.get(), canvas))
		# stat_accelerationCheckButton = tk.Checkbutton(stat_accelerationBoxFrame, text = 'Acceleration', variable = stat_iacceleration, command = lambda : self.Plot('Acceleration', stat_iacceleration.get(), canvas))
		stat_xPositionCheckButton = tk.Checkbutton(stat_xPositionBoxFrame, text = 'X Position', variable = self.stat_iXposition, command = lambda : self.Plot('X_Position', self.stat_iXposition.get(), self.canvas))
		stat_yPositionCheckButton = tk.Checkbutton(stat_yPositionBoxFrame, text = 'Y Position', variable = self.stat_iYposition, command = lambda : self.Plot('Y_Position', self.stat_iYposition.get(), self.canvas))
		stat_zPositionCheckButton = tk.Checkbutton(stat_zPositionBoxFrame, text = 'Z Position', variable = self.stat_iZposition, command = lambda : self.Plot('Z_Position', self.stat_iZposition.get(), self.canvas))
		stat_rollCheckButton = tk.Checkbutton(stat_rollBoxFrame, text = 'Roll', variable = self.stat_iroll, command = lambda : self.Plot('Roll', self.stat_iroll.get(), self.canvas))
		stat_pitchCheckButton = tk.Checkbutton(stat_pitchBoxFrame, text = 'Pitch', variable = self.stat_ipitch, command = lambda : self.Plot('Pitch', self.stat_ipitch.get(), self.canvas))
		stat_yawCheckButton = tk.Checkbutton(stat_yawBoxFrame, text = 'Yaw', variable = self.stat_iyaw, command = lambda : self.Plot('Yaw', self.stat_iyaw.get(), self.canvas))

		# stat_velocityCheckButton.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
		# stat_accelerationCheckButton.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
		stat_xPositionCheckButton.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
		stat_yPositionCheckButton.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
		stat_zPositionCheckButton.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
		stat_rollCheckButton.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
		stat_pitchCheckButton.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
		stat_yawCheckButton.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)

		# plt.close(self.fig)
			
		#def AnimatePlot():
		# xList = []
		# yList = []
		# zList = []

		# for eachLine in dataList
			# if len(eachLine) > 1:
				# x, y = eachLine.split(',')
				# xList.append(int(x))
				# yList.append(int(y))
				# zList.append(int(z))

		# a.clear()
		# a.plot(xList,yList)

		# stuff, = plt.plot([], [])

		#Whenever new data is received run this function to update the data array
		# def update_line(new_data,ax, data):
		# updated_data_x = stuff.set_xdata(np.append(stuff.get_xdata(), new_data))
		# updated_data_y = stuff.set_ydata(np.append(stuff.get_ydata(), new_data))
		# return updated_data_x, updated_data_y
		# ax.relim()
		# ax.autoscale_view()
		# plt.draw
		self.Roll_Changed = False
		self.Pitch_Changed = False
		self.Yaw_Changed = False
				
		self.xPosition_line.set_data([],[])
		self.yPosition_line.set_data([],[])
		self.zPosition_line.set_data([],[])
		self.roll_line.set_data([],[])
		self.pitch_line.set_data([],[])
		self.yaw_line.set_data([],[])
		self.legend_changed = False
		
		
	def run(self):		
		while 1:
			# print 'New Data: ' + str(self.new_data.value)
			if self.new_data.value == 1:
				# print "\nPlot!" + '\n'
				self.AnimatePlot(self.canvas,self.legend_changed)
			sleep(.12)
			
		# master.after(250,self.AnimatePlot(self.canvas))
		# anim = animation.FuncAnimation(self.fig, self.AnimatePlot, frames = 100, init_func = self.init_draw, interval = 500) #init_func = init, frames = 360, interval = 5, blit = True)
		# plt.show()
		# self.canvas.draw()
	def Plot(self,var_name, var_state, canvas):

		# tseconds = (np.array(self.messages['ATTITUDE']['BootTime']) - timezone) / (60)
		#tdays += 719163 # pylab wants it since 0001-01-01
		# tseconds += 1035594720 # pylab wants it since 0001-01-01
		# self.time = tseconds
		"""
		if var_state == 1:
			
			# if var_name is "Velocity":
				# t = np.arange(0.0, 3.0, 0.01)
				# velocity = np.sin(np.pi*t)
				# self.velocity_line.set_data(t, velocity)
				
			# elif var_name is "Acceleration":
				# t = np.arange(0.0, 3.0, 0.01)
				# acceleration = np.sin(3*np.pi*t)
				# self.acceleration_line.set_data(t, acceleration)
				
			if var_name is "X_Position":
				t = np.arange(0.0, 3.0, 0.01)
				position = np.sin(5*np.pi*t)
				self.xPosition_line.set_data(t, position)
				
			elif var_name is "Y_Position":
				t = np.arange(0.0, 3.0, 0.01)
				position = np.sin(5*np.pi*t)
				self.yPosition_line.set_data(t, position)
				
			elif var_name is "Z_Position":
				t = np.arange(0.0, 3.0, 0.01)
				position = np.sin(5*np.pi*t)
				self.zPosition_line.set_data(t, position)
				
			elif var_name is "Roll":
				# anim = animation.FuncAnimation(self.fig, AnimatePlot, fargs=(self.time,self.messages['ATTITUDE']['Roll'],interval = 1000) #init_func = init, frames = 360, interval = 5, blit = True)
				t = np.arange(0.0, 3.0, 0.01)
				roll = np.sin(7*np.pi*t)
				self.roll_line.set_data(t, roll)
				
			elif var_name is "Pitch":
				# anim = animation.FuncAnimation(self.fig, AnimatePlot, fargs=(self.time,self.messages['ATTITUDE']['Pitch'],interval = 1000) #init_func = init, frames = 360, interval = 5, blit = True)
				t = np.arange(0.0, 3.0, 0.01)
				pitch = np.sin(9*np.pi*t)
				self.pitch_line.set_data(t, pitch)
				
			elif var_name is "Yaw":
				# anim = animation.FuncAnimation(self.fig, AnimatePlot, fargs=(self.time,self.messages['ATTITUDE']['Yaw'],interval = 1000) #init_func = init, frames = 360, interval = 5, blit = True)
				t = np.arange(0.0, 3.0, 0.01)
				yaw = np.sin(11*np.pi*t)
				self.yaw_line.set_data(t, yaw)				
			
			print "Plotting " + var_name
			# print 'The Packet being plotted is: ' + str(self.PlotMessages[:]) #This is the packet that would be sent to the Settings Thread for plotting
			self.ax.relim()
			self.ax.autoscale_view()
			# plt.gcf().self.canvas.draw()
			self.canvas.draw()
			plt.pause(.001)

			# self.a.plot(t, s)			
			# self.canvas = Figureself.canvasTkAgg(self.f, self.plotFrame)
			# self.canvas.draw()
			"""
		# else:
		if var_state == 0:
			# if var_name is "Velocity":
				# self.velocity_line.set_data([],[])
				
			# elif var_name is "Acceleration":
				# self.acceleration_line.set_data([],[])
				
			if var_name is "X_Position":
				self.xPosition_line.set_data([],[])
				
			elif var_name is "Y_Position":
				self.yPosition_line.set_data([],[])
				
			elif var_name is "Z_Position":
				self.zPosition_line.set_data([],[])
				
			elif var_name is "Roll":
				print 'Stop Plotting Roll'
				self.roll_line.set_data([],[])
				
			elif var_name is "Pitch":
				print 'Stop Plotting Pitch'
				self.pitch_line.set_data([],[])
					
			elif var_name is "Yaw":
				print 'Stop Plotting Yaw'
				self.yaw_line.set_data([],[])
				
			# print "Not Plotting" + var_name
			
			# self.ax.relim()
			# self.ax.autoscale_view()
			# plt.gcf().self.canvas.draw()
			# self.canvas.draw()
			# plt.pause(.001)			
			
	def AnimatePlot(self,canvas,legend_changed):
		# print self.messages['ATTITUDE']['BootTime'][0]
		Prev_Rotation_Scaling_Factor = 0
		Rotation_Scaling_Factor = 0
		Prev_Position_Scaling_Factor = 0
		Position_Scaling_Factor = 0
		Scale = 2
		
		NumDataPlots = self.stat_iyaw.get() + self.stat_ipitch.get() + self.stat_iroll.get() + self.stat_iZposition.get() + self.stat_iYposition.get() + self.stat_iXposition.get()
		
		if NumDataPlots is 0:
			Position_Lines, _ = self.ax.get_legend_handles_labels()
			Rotation_Lines, _ = self.ax2.get_legend_handles_labels()
			Position_Lables = None
			Rotation_Lables = None
			L = self.ax2.legend(Position_Lines+Rotation_Lines, 'None', bbox_to_anchor = (0., 1.02, 1., .102), loc=3,
						ncol= 1, mode="expand", borderaxespad=0.)
			L.remove()
			
		else:
			Position_Lines, Position_Lables = self.ax.get_legend_handles_labels()
			Rotation_Lines, Rotation_Lables = self.ax2.get_legend_handles_labels()
			# print Rotation_Lines
			if self.stat_iXposition.get() == 0:
				if 'X' in Position_Lables:
					Position_Lines.pop(Position_Lables.index('X'))
					Position_Lables.pop(Position_Lables.index('X'))
					print 'Remove X'
					
			if self.stat_iYposition.get() == 0:
				if 'Y' in Position_Lables:
					Position_Lines.pop(Position_Lables.index('Y'))
					Position_Lables.pop(Position_Lables.index('Y'))
					print 'Remove Y'
					
			if self.stat_iZposition.get() == 0:
				if 'Z' in Position_Lables:
					Position_Lines.pop(Position_Lables.index('Z'))
					Position_Lables.pop(Position_Lables.index('Z'))
					print "Remove Z"
					
			if self.stat_iroll.get() == 0:
				if 'Roll' in Rotation_Lables:
					Rotation_Lines.pop(Rotation_Lables.index("Roll"))
					Rotation_Lables.pop(Rotation_Lables.index("Roll"))					
					print "Remove Roll"
					
				# if ('(1/' + str(Rotation_Scaling_Factor) + ')*Roll') in Rotation_Lables:
					# Rotation_Lines.pop(Rotation_Lables.index('(1/' + str(Rotation_Scaling_Factor) + ')*Roll'))
					# Rotation_Lables.pop(Rotation_Lables.index('(1/' + str(Rotation_Scaling_Factor) + ')*Roll'))					
					
				# if ('(1/' + str(Prev_Rotation_Scaling_Factor) + ')*Roll') in Rotation_Lables:
					# Rotation_Lines.pop(Rotation_Lables.index('(1/' + str(Prev_Rotation_Scaling_Factor) + ')*Roll'))
					# Rotation_Lables.pop(Rotation_Lables.index('(1/' + str(Prev_Rotation_Scaling_Factor) + ')*Roll'))					
					
			if self.stat_ipitch.get() == 0:
				if 'Pitch' in Rotation_Lables:
					Rotation_Lines.pop(Rotation_Lables.index("Pitch"))
					Rotation_Lables.pop(Rotation_Lables.index("Pitch"))					
					print "Remove Pitch"
					
				# if '(1/' + str(Rotation_Scaling_Factor) + ')*Pitch' in Rotation_Lables:
					# Rotation_Lines.pop(Rotation_Lables.index('(1/' + str(Rotation_Scaling_Factor) + ')*Pitch'))
					# Rotation_Lables.pop(Rotation_Lables.index('(1/' + str(Rotation_Scaling_Factor) + ')*Pitch'))					
					
				# elif '(1/' + str(Prev_Rotation_Scaling_Factor) + ')*Pitch' in Rotation_Lables:
					# Rotation_Lines.pop(Rotation_Lables.index('(1/' + str(Prev_Rotation_Scaling_Factor) + ')*Pitch'))
					# Rotation_Lables.pop(Rotation_Lables.index('(1/' + str(Prev_Rotation_Scaling_Factor) + ')*Pitch'))					
					
			if self.stat_iyaw.get() == 0:
				if 'Yaw' in Rotation_Lables:
					Rotation_Lines.pop(Rotation_Lables.index('Yaw'))
					Rotation_Lables.pop(Rotation_Lables.index('Yaw'))					
					print "Remove Yaw"
					print Rotation_Lables.index('Yaw')
					
				# if ('(1/' + str(Rotation_Scaling_Factor) + ')*Yaw') in Rotation_Lables:
					# Rotation_Lines.pop(Rotation_Lables.index('(1/' + str(Rotation_Scaling_Factor) + ')*Yaw'))
					# Rotation_Lables.pop(Rotation_Lables.index('(1/' + str(Rotation_Scaling_Factor) + ')*Yaw'))					
					# print "Remove Rotation_Scaling_Factor"
					
				# if ('(1/' + str(Prev_Rotation_Scaling_Factor) + ')*Yaw') in Rotation_Lables:
					# Rotation_Lines.pop(Rotation_Lables.index('(1/' + str(Prev_Rotation_Scaling_Factor) + ')*Yaw'))
					# Rotation_Lables.pop(Rotation_Lables.index('(1/' + str(Prev_Rotation_Scaling_Factor) + ')*Yaw'))					
					# print "Remove Previous Rotation_Scaling_Factor"
			
			if Rotation_Scaling_Factor == 0:
				if ('(1/' + str(Rotation_Scaling_Factor) + ')*Roll') in Rotation_Lables:
					Rotation_Lines.pop(Rotation_Lables.index('(1/' + str(Rotation_Scaling_Factor) + ')*Roll'))
					Rotation_Lables.pop(Rotation_Lables.index('(1/' + str(Rotation_Scaling_Factor) + ')*Roll'))					
					
				elif ('(1/' + str(Prev_Rotation_Scaling_Factor) + ')*Roll') in Rotation_Lables:
					Rotation_Lines.pop(Rotation_Lables.index('(1/' + str(Prev_Rotation_Scaling_Factor) + ')*Roll'))
					Rotation_Lables.pop(Rotation_Lables.index('(1/' + str(Prev_Rotation_Scaling_Factor) + ')*Roll'))					
					
				if '(1/' + str(Rotation_Scaling_Factor) + ')*Pitch' in Rotation_Lables:
					Rotation_Lines.pop(Rotation_Lables.index('(1/' + str(Rotation_Scaling_Factor) + ')*Pitch'))
					Rotation_Lables.pop(Rotation_Lables.index('(1/' + str(Rotation_Scaling_Factor) + ')*Pitch'))					
					
				elif '(1/' + str(Prev_Rotation_Scaling_Factor) + ')*Pitch' in Rotation_Lables:
					Rotation_Lines.pop(Rotation_Lables.index('(1/' + str(Prev_Rotation_Scaling_Factor) + ')*Pitch'))
					Rotation_Lables.pop(Rotation_Lables.index('(1/' + str(Prev_Rotation_Scaling_Factor) + ')*Pitch'))					
					
				if ('(1/' + str(Rotation_Scaling_Factor) + ')*Yaw') in Rotation_Lables:
					Rotation_Lines.pop(Rotation_Lables.index('(1/' + str(Rotation_Scaling_Factor) + ')*Yaw'))
					Rotation_Lables.pop(Rotation_Lables.index('(1/' + str(Rotation_Scaling_Factor) + ')*Yaw'))					
					print "Remove Rotation_Scaling_Factor"
					
				elif ('(1/' + str(Prev_Rotation_Scaling_Factor) + ')*Yaw') in Rotation_Lables:
					Rotation_Lines.pop(Rotation_Lables.index('(1/' + str(Prev_Rotation_Scaling_Factor) + ')*Yaw'))
					Rotation_Lables.pop(Rotation_Lables.index('(1/' + str(Prev_Rotation_Scaling_Factor) + ')*Yaw'))					
					print "Remove Previous Rotation_Scaling_Factor"
					
			if Position_Scaling_Factor == 0:
				if ('(1/' + str(Position_Scaling_Factor) + ')*X') in Position_Lables:
					Position_Lines.pop(Position_Lables.index('(1/' + str(Position_Scaling_Factor) + ')*X'))
					Position_Lables.pop(Position_Lables.index('(1/' + str(Position_Scaling_Factor) + ')*X'))
				
				elif ('(1/' + str(Prev_Position_Scaling_Factor) + ')*X') in Position_Lables:
					Position_Lines.pop(Position_Lables.index('(1/' + str(Prev_Position_Scaling_Factor) + ')*X'))
					Position_Lables.pop(Position_Lables.index('(1/' + str(Prev_Position_Scaling_Factor) + ')*X'))
				
				if ('(1/' + str(Position_Scaling_Factor) + ')*Y') in Position_Lables:
					Position_Lines.pop(Position_Lables.index('(1/' + str(Position_Scaling_Factor) + ')*Y'))
					Position_Lables.pop(Position_Lables.index('(1/' + str(Position_Scaling_Factor) + ')*Y'))
				
				elif ('(1/' + str(Prev_Position_Scaling_Factor) + ')*Y') in Position_Lables:
					Position_Lines.pop(Position_Lables.index('(1/' + str(Prev_Position_Scaling_Factor) + ')*Y'))
					Position_Lables.pop(Position_Lables.index('(1/' + str(Prev_Position_Scaling_Factor) + ')*Y'))
				
				if ('(1/' + str(Position_Scaling_Factor) + ')*Z') in Position_Lables:
					Position_Lines.pop(Position_Lables.index('(1/' + str(Position_Scaling_Factor) + ')*Z'))
					Position_Lables.pop(Position_Lables.index('(1/' + str(Position_Scaling_Factor) + ')*Z'))
				
				elif ('(1/' + str(Prev_Position_Scaling_Factor) + ')*Z') in Position_Lables:
					Position_Lines.pop(Position_Lables.index('(1/' + str(Prev_Position_Scaling_Factor) + ')*Z'))
					Position_Lables.pop(Position_Lables.index('(1/' + str(Prev_Position_Scaling_Factor) + ')*Z'))
					
			print Rotation_Lines
			L = self.ax2.legend(Position_Lines + Rotation_Lines, Position_Lables + Rotation_Lables, bbox_to_anchor = (0., 1.02, 1., .102), loc=3,
						ncol= NumDataPlots, mode="expand", borderaxespad=0.)
						
###########################################################################################################################################
######################################################## Position! ########################################################################
###########################################################################################################################################
		
		New_xPosition_y_data = self.messages['VICON_POSITION_ESTIMATE']['X']
		New_yPosition_y_data = self.messages['VICON_POSITION_ESTIMATE']['Y']
		New_zPosition_y_data = self.messages['VICON_POSITION_ESTIMATE']['Z']
		xPosition_y_data = np.append(self.xPosition_line.get_ydata(), New_xPosition_y_data)
		yPosition_y_data = np.append(self.yPosition_line.get_ydata(), New_yPosition_y_data)
		zPosition_y_data = np.append(self.zPosition_line.get_ydata(), New_zPosition_y_data)
		
		if (self.stat_iXposition.get() and self.stat_iYposition.get() and self.stat_iZposition.get()) == 1:
			yMax_X_Position = abs(max(New_xPosition_y_data))
			yMax_Y_Position = abs(max(New_yPosition_y_data))
			yMax_Z_Position = abs(max(New_zPosition_y_data))
			
			Max_Position = max(yMax_X_Position, yMax_Y_Position, yMax_Z_Position)
			Min_Max_Position = min(yMax_X_Position, yMax_Y_Position, yMax_Z_Position)
			Position_Scaling_Factor = int(Min_Max_Position/Max_Position)
			
			if Position_Scaling_Factor >= Scale:
				if yMax_X_Position > (yMax_Y_Position and yMax_Z_Position):
					Scale_X_Position = 1
					Scale_Y_Position = 0
					Scale_Z_Position = 0
					
				elif yMax_Y_Position > (yMax_X_Position and yMax_Z_Position):
					Scale_X_Position = 0
					Scale_Y_Position = 1
					Scale_Z_Position = 0
					
				elif yMax_Z_Position > (yMax_X_Position and yMax_Y_Position):
					Scale_X_Position = 0
					Scale_Y_Position = 0
					Scale_Z_Position = 1
			
			else:
				Scale_X_Position = 0
				Scale_Y_Position = 0
				Scale_Z_Position = 0
			
		elif (self.stat_iXposition.get() and self.stat_iYposition.get()) == 1:
			yMax_X_Position = abs(max(New_xPosition_y_data))
			yMax_Y_Position = abs(max(New_yPosition_y_data))
			
			Max_Position = max(yMax_X_Position, yMax_Y_Position)
			Min_Max_Position = min(yMax_X_Position, yMax_Y_Position)
			Position_Scaling_Factor = int(Min_Max_Position/Max_Position)
			
			if Position_Scaling_Factor >= Scale:
				if yMax_X_Position > yMax_Y_Position:
					Scale_X_Position = 1
					Scale_Y_Position = 0
					Scale_Z_Position = 0
					
				elif yMax_Y_Position > yMax_X_Position:
					Scale_X_Position = 0
					Scale_Y_Position = 1
					Scale_Z_Position = 0
					
			else:
				Scale_X_Position = 0
				Scale_Y_Position = 0
				Scale_Z_Position = 0
				
		elif (self.stat_iYposition.get() and self.stat_iZposition.get()) == 1:
			yMax_Y_Position = abs(max(New_yPosition_y_data))
			yMax_Z_Position = abs(max(New_zPosition_y_data))
			
			Max_Position = max(yMax_Y_Position, yMax_Z_Position)
			Min_Max_Position = min(yMax_Y_Position, yMax_Z_Position)
			Position_Scaling_Factor = int(Min_Max_Position/Max_Position)
			
			if Position_Scaling_Factor >= Scale:
				if yMax_Y_Position > yMax_Z_Position:
					Scale_X_Position = 0
					Scale_Y_Position = 1
					Scale_Z_Position = 0
					
				elif yMax_Z_Position > yMax_Y_Position:
					Scale_X_Position = 0
					Scale_Y_Position = 0
					Scale_Z_Position = 1
			
			else:
				Scale_X_Position = 0
				Scale_Y_Position = 0
				Scale_Z_Position = 0
					
		elif (self.stat_iXposition.get() and self.stat_iZposition.get()) == 1:
			yMax_X_Position = abs(max(New_xPosition_y_data))
			yMax_Z_Position = abs(max(New_zPosition_y_data))
			
			Max_Position = max(yMax_X_Position, yMax_Z_Position)
			Min_Max_Position = min(yMax_X_Position, yMax_Z_Position)
			Position_Scaling_Factor = int(Min_Max_Position/Max_Position)
			
			if Position_Scaling_Factor >= Scale:
				if yMax_X_Position > yMax_Z_Position:
					Scale_X_Position = 1
					Scale_Y_Position = 0
					Scale_Z_Position = 0
					
				elif yMax_Z_Position > yMax_X_Position:
					Scale_X_Position = 0
					Scale_Y_Position = 0
					Scale_Z_Position = 1
					
		else:
			Scale_X_Position = 0
			Scale_Y_Position = 0
			Scale_Z_Position = 0
					
		if self.stat_iXposition.get() == 1:
			X_Position_x = np.append(self.xPosition_line.get_xdata(), self.messages['VICON_POSITION_ESTIMATE']['BootTime'])			
		
			if Scale_X_Position == 1:
				X_Position_y =np.append(self.xPosition_line.get_ydata(), New_xPosition_y_data*(1/Position_Scaling_Factor))
				
			else:
				X_Position_y = xPosition_y_data
				
			if len(X_Position_x) == len(X_Position_y):	
				self.xPosition_line.set_xdata(X_Position_x)
				self.xPosition_line.set_ydata(X_Position_y)
				
			else:
				self.xPosition_line.set_xdata(X_Position_x[:len(X_Position_y)])
				self.xPosition_line.set_ydata(X_Position_y)
				
			if len(X_Position_y) > 0:
				BufferSize = len(self.messages['VICON_POSITION_ESTIMATE']['BootTime'])
				
				xMax_X_Position = self.messages['VICON_POSITION_ESTIMATE']['BootTime'][BufferSize-1]
				yMin_X_Position = min(X_Position_y)
				yMax_X_Position = max(X_Position_y)
				
				xMax_Position = max(xMax_X_Position)
				yMin_Position = min(yMin_X_Position)
				yMax_Position = max(yMax_X_Position)
			
			if Scale_X_Position == 1 and self.X_Position_Changed is False and '(1/' + str(Position_Scaling_Factor) + ')*X' not in Position_Lables:
				self.xPosition_line = self.ax.plot(self.xPosition_line.get_xdata(), self.xPosition_line.get_ydata(), 'b', label='(1/' + str(Position_Scaling_Factor) + 'X Position')[0]
				self.X_Position_Changed = True
				
			elif 'X Position' not in Position_Lables and Scale_X_Position == 0:
				self.xPosition_line = self.ax.plot(self.xPosition_line.get_xdata(), self.xPosition_line.get_ydata(), 'b', label='X Position')[0]
				self.X_Position_Changed = False
			
		if self.stat_iYposition.get() == 1:
			print 'Plot Y Position!'
			Y_Position_x = np.append(self.yPosition_line.get_xdata(), self.messages['VICON_POSITION_ESTIMATE']['BootTime'])
			
			if Scale_Y_Position == 1:
				Y_Position_y = np.append(self.yPosition_line.get_ydata(), New_yPosition_y_data*(1/Position_Scaling_Factor))
			
			else:
				Y_Position_y = yPosition_y_data
			
			if len(Y_Position_x) == len(Y_Position_y):
				self.yPosition_line.set_xdata(Y_Position_x)
				self.yPosition_line.set_ydata(Y_Position_y)
				
			else:
				self.yPosition_line.set_xdata(Y_Position_x[:len(Y_Position_y)])
				self.yPosition_line.set_ydata(Y_Position_y)
			
			if len(Y_Position_y) > 0:
				BufferSize = len(self.messages['VICON_POSITION_ESTIMATE']['BootTime'])
				
				xMax_Y_Position = self.messages['VICON_POSITION_ESTIMATE']['BootTime'][BufferSize-1]
				yMin_Y_Position = min(Y_Position_y)
				yMax_Y_Position = max(Y_Position_y)
			
				if self.stat_iXposition.get() == 1:
					xMax_Position = xMax_Y_Position
					yMin_Position = min(yMin_Position, yMin_Y_Position)
					yMax_Position = max(yMax_Position, yMax_Y_Position)
					
				else:
					xMax_Position = xMax_yPosition
					yMin_Position = yMin_yPosition
					yMax_Position = yMax_yPosition
					
			if Scale_Y_Position == 1 and self.Y_Position_Changed is False and '(1/' + str(Position_Scaling_Factor) + ')*Y Position' not in Position_Lables:
				self.yPosition_line = self.ax.plot(self.yPosition_line.get_ydata(), self.yPosition_line.get_ydata(), 'g',label='(1/' + str(Position_Scaling_Factor) + ')*Y Position')[0]
				self.Y_Position_Changed = True
				
			elif 'Y Position' not in Position_Lables and Scale_Y_Position == 0:
				self.yPosition_line = self.ax.plot(self.yPosition_line.get_ydata(), self.yPosition_line.get_ydata(), 'g',label='Y Position')[0]
				self.Y_Position_Changed = False
			
		if self.stat_iZposition.get() == 1:
			Z_Position_x = np.append(self.zPosition_line.get_xdata(), self.messages['VICON_POSITION_ESTIMATE']['BootTime'])			
			
			if Scale_Z_Position == 1:
				Z_Position_y = np.append(self.zPosition_line.get_ydata(), New_zPosition_y_data*(1/Position_Scaling_Factor))
				
			else:
				Z_Position_y = zPosition_y_data
			
			if len(Z_Position_x) == len(Z_Position_y):
				self.zPosition_line.set_xdata(Z_Position_x)
				self.zPosition_line.set_ydata(Z_Position_y)
			
			else:
				self.zPosition_line.set_xdata(Z_Position_x[:len(Z_Position_y)])
				self.zPosition_line.set_ydata(Z_Position_y)
			
			if len(Z_Position_y) > 0:
			
				BufferSize = len(self.messages['VICON_POSITION_ESTIMATE']['BootTime'])
				
				xMax_Z_Position = self.messages['VICON_POSITION_ESTIMATE']['BootTime'][BufferSize-1]
				yMin_Z_Position = min(Z_Position_y)
				yMax_Z_Position = max(Z_Position_y)
			
				if (self.stat_iXposition.get() or self.stat_iYposition.get()) == 1:
					xMax_Position = xMax_Z_Position
					yMin_Position = min(yMin_Position, yMin_Z_Position)
					yMax_Position = max(yMax_Position, yMax_Z_Position)
					
				else:
					xMax_Position = xMax_zPosition
					yMin_Position = yMin_zPosition
					yMax_Position = yMax_zPosition
			
			if Scale_Z_Position == 1 and self.Z_Position_Changed is False and '(1/' + str(Position_Scaling_Factor) + ')*Z Position' not in Position_Lables:
				self.zPosition_line = self.ax.plot(self.zPosition_line.get_xdata(), self.zPosition_line.get_ydata(), 'r',label= '(1/' + str(Position_Scaling_Factor) + ')*Z Position')[0]
				self.Z_Position_Changed = True
				
			elif 'Z Position' not in Position_Lables and Scale_Z_Position == 0:
				self.zPosition_line = self.ax.plot(self.zPosition_line.get_xdata(), self.zPosition_line.get_ydata(), 'r',label='Z Position')[0]
				self.Z_Position_Changed = False
				
###########################################################################################################################################
######################################################## Rotation! ########################################################################
###########################################################################################################################################

		New_Roll_y_data = self.messages['ATTITUDE']['Roll']
		New_Pitch_y_data = self.messages['ATTITUDE']['Pitch']
		New_Yaw_y_data = self.messages['ATTITUDE']['Yaw']
		Roll_y_data = np.append(self.roll_line.get_ydata(), New_Roll_y_data)
		Pitch_y_data = np.append(self.pitch_line.get_ydata(), New_Pitch_y_data)
		Yaw_y_data = np.append(self.yaw_line.get_ydata(), New_Yaw_y_data)

		
		
		if (self.stat_iroll.get() and self.stat_ipitch.get() and self.stat_iyaw.get()) == 1:
			yMax_Roll 	= abs(max(New_Roll_y_data))
			yMax_Pitch 	= abs(max(New_Pitch_y_data))
			yMax_Yaw 	= abs(max(New_Yaw_y_data))

			Max_Angle = max(yMax_Roll, yMax_Pitch, yMax_Yaw)
			Min_Max_Angle = min(yMax_Roll, yMax_Pitch, yMax_Yaw)
			Rotation_Scaling_Factor = int(Max_Angle/Min_Max_Angle)
			print 'Roll/Pitch/Yaw Scaling Factor: ' + str(Rotation_Scaling_Factor)
			if Rotation_Scaling_Factor >= Scale:
				if yMax_Roll > (yMax_Pitch and yMax_Yaw):
					Scale_Roll 	= 1
					Scale_Pitch = 0
					Scale_Yaw 	= 0
					
				elif yMax_Pitch > (yMax_Roll and yMax_Yaw):
					Scale_Roll = 0
					Scale_Pitch = 1
					Scale_Yaw = 0
					
				elif yMax_Yaw > (yMax_Roll and yMax_Pitch):
					Scale_Roll = 0
					Scale_Pitch = 0
					Scale_Yaw = 1
			
			else:
				Scale_Roll 	= 0
				Scale_Pitch = 0
				Scale_Yaw 	= 0
				
		elif (self.stat_iroll.get() and self.stat_ipitch.get()) == 1:
			yMax_Roll 	= abs(max(New_Roll_y_data))
			yMax_Pitch 	= abs(max(New_Pitch_y_data))
			
			Max_Angle = max(yMax_Roll, yMax_Pitch)
			Min_Max_Angle = min(yMax_Roll, yMax_Pitch)
			Rotation_Scaling_Factor = abs(int(Max_Angle/Min_Max_Angle))
			print 'Roll/Pitch Scaling Factor: ' + str(Rotation_Scaling_Factor)
			if Rotation_Scaling_Factor >= Scale:
				if yMax_Roll > yMax_Pitch:
					Scale_Roll = 1
					Scale_Pitch = 0
					Scale_Yaw 	= 0
					
				elif yMax_Pitch > yMax_Roll:
					Scale_Roll = 0
					Scale_Pitch = 1
					Scale_Yaw 	= 0
					
			else:
				Scale_Roll 	= 0
				Scale_Pitch = 0
				Scale_Yaw 	= 0
				
		elif (self.stat_ipitch.get() and self.stat_iyaw.get()) == 1:
			yMax_Pitch 	= abs(max(New_Pitch_y_data))
			yMax_Yaw 	= abs(max(New_Yaw_y_data))
			
			Max_Angle = max(yMax_Pitch, yMax_Yaw)
			Min_Max_Angle = min(yMax_Pitch, yMax_Yaw)
			Rotation_Scaling_Factor = int(Max_Angle/Min_Max_Angle)
			
			if Rotation_Scaling_Factor >= Scale:
				if yMax_Pitch > yMax_Yaw:
					Scale_Roll = 0
					Scale_Pitch = 1
					Scale_Yaw 	= 0
					
				elif yMax_Yaw > yMax_Pitch:
					Scale_Roll = 0
					Scale_Pitch = 0
					Scale_Yaw 	= 1
					
			else:
				Scale_Roll 	= 0
				Scale_Pitch = 0
				Scale_Yaw 	= 0
				
		elif (self.stat_iroll.get() and self.stat_iyaw.get()) == 1:
			yMax_Roll 	= abs(max(New_Roll_y_data))
			yMax_Yaw 	= abs(max(New_Yaw_y_data))
			
			Max_Angle = max(yMax_Roll, yMax_Yaw)
			Min_Max_Angle = min(yMax_Roll, yMax_Yaw)
			Rotation_Scaling_Factor = int(Max_Angle/Min_Max_Angle)
			print Rotation_Scaling_Factor
			if Rotation_Scaling_Factor >= Scale:
				if abs(yMax_Roll) > abs(yMax_Yaw):
					Scale_Roll = 1
					Scale_Pitch = 0
					Scale_Yaw = 0
					
				elif abs(yMax_Yaw) > abs(yMax_Roll):
					Scale_Roll = 0
					Scale_Pitch = 0
					Scale_Yaw = 1
			else:
				Scale_Roll 	= 0
				Scale_Pitch = 0
				Scale_Yaw 	= 0
					
		else:
			Scale_Roll 	= 0
			Scale_Pitch = 0
			Scale_Yaw 	= 0		
		
		# print Scale_Roll
		# print Scale_Pitch
		# print Scale_Yaw
		
		if self.stat_iroll.get() == 1:
			print 'Plot Roll data!'
			# self.roll_line.set_xdata(np.append(self.roll_line.get_xdata(), self.messages['ATTITUDE']['BootTime']))
			# self.roll_line.set_ydata(np.append(self.roll_line.get_ydata(), self.messages['ATTITUDE']['Roll']))
			
			Roll_x = np.append(self.roll_line.get_xdata(), self.messages['ATTITUDE']['BootTime'])
			
			if Scale_Roll == 1:
				Roll_y = np.append(self.roll_line.get_ydata(), New_Roll_y_data*(1/Rotation_Scaling_Factor))
				
			else:
				Roll_y = Roll_y_data
			# print Roll_y
			# print len(Roll_x)
			# print len(Roll_y)
			# print Roll_x*10
			# print Roll_y*10
			if len(Roll_x) == len(Roll_y):
				self.roll_line.set_xdata(Roll_x)
				self.roll_line.set_ydata(Roll_y)
				
			else:
				self.roll_line.set_xdata(Roll_x[:len(Roll_y)])
				self.roll_line.set_ydata(Roll_y)
				# print 'New x data len: ' + str(len(self.roll_line.get_xdata()))
				
			if len(Roll_y) > 0:
			# print self.roll_line
				BufferSize = len(self.messages['ATTITUDE']['BootTime'])
				xMax_Roll = self.messages['ATTITUDE']['BootTime'][BufferSize-1]
				yMin_Roll = min(Roll_y)
				yMax_Roll = max(Roll_y)

				xMax_Angle = xMax_Roll
				yMin_Angle = yMin_Roll
				yMax_Angle = yMax_Roll
			
			# by_label = OrderedDict(zip(labels2,lines2))
			# print by_label
			# by_label = OrderedDict.popitem()
			# print by_label
			
			if Scale_Roll == 1 and self.Roll_Changed is False and '(1/' + str(Rotation_Scaling_Factor) + ')*Roll' not in Rotation_Lables:
				self.roll_line 		= self.ax2.plot(self.roll_line.get_xdata(), self.roll_line.get_ydata(), 'c',label= '(1/' + str(Rotation_Scaling_Factor) + ')*Roll')[0]
				self.Roll_Changed = True
				
			elif 'Roll' not in Rotation_Lables and Scale_Roll == 0:
				self.roll_line 		= self.ax2.plot(self.roll_line.get_xdata(), self.roll_line.get_ydata(), 'c',label='Roll')[0]
				self.Roll_Changed = False
				
			# print Rotation_Lables
		if self.stat_ipitch.get() == 1:
			print 'Plot Pitch data!'
			Pitch_x = np.append(self.pitch_line.get_xdata(), self.messages['ATTITUDE']['BootTime'])
			
			if Scale_Pitch == 1:
				Pitch_y = np.append(self.pitch_line.get_ydata(), New_Pitch_y_data*(1/Rotation_Scaling_Factor))
				
			else:
				Pitch_y = Pitch_y_data
				
			# print len(Pitch_x)
			# print len(Pitch_y)
			
			if len(Pitch_x) == len(Pitch_y):
				self.pitch_line.set_xdata(Pitch_x)
				self.pitch_line.set_ydata(Pitch_y)
				
			else:
				self.pitch_line.set_xdata(Pitch_x[:len(Pitch_y)])
				self.pitch_line.set_ydata(Pitch_y)
				# print len(self.pitch_line.get_xdata())
				
			if len(Pitch_y) > 0:
				BufferSize = len(self.messages['ATTITUDE']['BootTime'])
				
				xMax_Pitch = self.messages['ATTITUDE']['BootTime'][BufferSize-1]
				yMin_Pitch = min(Pitch_y)
				yMax_Pitch = max(Pitch_y)
			
				if self.stat_iroll.get() == 1:
					xMax_Angle = xMax_Pitch
					yMin_Angle = min(yMin_Angle, yMin_Pitch)
					yMax_Angle = max(yMax_Angle, yMax_Pitch)
					
				else:
					xMax_Angle = xMax_Pitch
					yMin_Angle = yMin_Pitch
					yMax_Angle = yMax_Pitch
			
			if Scale_Pitch == 1 and self.Pitch_Changed is False and '(1/' + str(Rotation_Scaling_Factor) + ')*Pitch' not in Rotation_Lables:
				self.pitch_line = self.ax2.plot(self.pitch_line.get_xdata(), self.pitch_line.get_ydata(), 'm',label= '(1/' + str(Rotation_Scaling_Factor) + ')*Pitch')[0]
				self.Pitch_Changed = True
			
			elif 'Pitch' not in Rotation_Lables and Scale_Pitch == 0:
				self.pitch_line = self.ax2.plot(self.pitch_line.get_xdata(), self.pitch_line.get_ydata(), 'm',label='Pitch' )[0]
				self.Pitch_Changed = False
			# print Rotation_Lables
			
		if self.stat_iyaw.get() == 1:
			print 'Plot Yaw data!'
			Yaw_x = np.append(self.yaw_line.get_xdata(), self.messages['ATTITUDE']['BootTime'])
			# print self.messages['ATTITUDE']['Yaw']
			# print type(self.messages['ATTITUDE']['Yaw'])

			if Scale_Yaw == 1:
				# print self.messages['ATTITUDE']['Yaw']
				Yaw_Scaled_data = [x*(1/float(Rotation_Scaling_Factor)) for x in New_Yaw_y_data]
				# print Yaw_Scaled_data
				Yaw_y = np.append(self.yaw_line.get_ydata(), Yaw_Scaled_data)
				# print 'Scale'				
			else:
				Yaw_y = Yaw_y_data
				# print "normal"
			# print len(Yaw_x)
			# print len(Yaw_y)
			
			if len(Yaw_x) == len(Yaw_y):
				self.yaw_line.set_xdata(Yaw_x)
				self.yaw_line.set_ydata(Yaw_y)
			else:
				self.yaw_line.set_xdata(Yaw_x[:len(Yaw_y)])
				self.yaw_line.set_ydata(Yaw_y)
				# print 'new x length: ' + str(len(self.yaw_line.get_xdata()))
								
			if len(Yaw_y) > 0:
				BufferSize = len(self.messages['ATTITUDE']['BootTime'])
				
				xMax_Yaw = self.messages['ATTITUDE']['BootTime'][BufferSize-1]
				yMin_Yaw = min(Yaw_y)
				yMax_Yaw = max(Yaw_y)
				# print yMin_Yaw
				# print yMax_Yaw
				
				if (self.stat_iroll.get() or self.stat_ipitch.get()) == 1:
					xMax_Angle = xMax_Yaw
					yMin_Angle = min(yMin_Angle, yMin_Yaw)
					yMax_Angle = max(yMax_Angle, yMax_Yaw)
					
				else:
					xMax_Angle = xMax_Yaw
					yMin_Angle = yMin_Yaw
					yMax_Angle = yMax_Yaw
				
			if Scale_Yaw == 1 and self.Yaw_Changed is False and '(1/' + str(Rotation_Scaling_Factor) + ')*Yaw' not in Rotation_Lables:
				self.yaw_line 		= self.ax2.plot(self.yaw_line.get_xdata(), self.yaw_line.get_ydata(), 'k',label= '(1/' + str(Rotation_Scaling_Factor) + ')*Yaw')[0]
				self.Yaw_Changed = True
				
			elif 'Yaw' not in Rotation_Lables and Scale_Yaw == 0:
				self.yaw_line 		= self.ax2.plot(self.yaw_line.get_xdata(), self.yaw_line.get_ydata(), 'k',label='Yaw')[0]
				self.Yaw_Changed = False
			# print Rotation_Lables
		# print 'Scaling Factor: ' + str(Rotation_Scaling_Factor)
		
		# if Rotation_Scaling_Factor >= Scale and Previous_Rotation_Scaling_Factor is not Rotation_Scaling_Factor:
			# if Scale_Roll == 1:
				# self.roll_line 		= self.ax2.plot(self.roll_line.get_xdata(), self.roll_line.get_ydata(), 'c',label= '(1/' + str(Rotation_Scaling_Factor) + ')*Roll')[0]
				
			# elif Scale_Pitch == 1:
				# self.pitch_line 	= self.ax2.plot(self.pitch_line.get_xdata(), self.pitch_line.get_ydata(), 'm',label= '(1/' + str(Rotation_Scaling_Factor) + ')*Pitch')[0]
				
			# elif Scale_Yaw == 1:
				# self.yaw_line 		= self.ax2.plot(self.yaw_line.get_xdata(), self.yaw_line.get_ydata(), 'k',label= '(1/' + str(Rotation_Scaling_Factor) + ')*Yaw')[0]
			# lines2, labels2 = self.ax2.get_legend_handles_labels()
			# L = self.ax2.legend(lines2, labels2, bbox_to_anchor = (0., 1.02, 1., .102), loc=3,
						# ncol=6, mode="expand", borderaxespad=0.)
			# Previous_Rotation_Scaling_Factor = Rotation_Scaling_Factor
			# legend_changed = True
			
		# elif legend_changed:
			# self.roll_line 		= self.ax2.plot(self.roll_line.get_xdata(), self.roll_line.get_ydata(), 'c',label= 'Roll')[0]
			# self.pitch_line 	= self.ax2.plot(self.pitch_line.get_xdata(), self.pitch_line.get_ydata(), 'm',label= 'Pitch')[0]
			# self.yaw_line 		= self.ax2.plot(self.yaw_line.get_xdata(), self.yaw_line.get_ydata(), 'k',label= 'Yaw')[0]
			# lines2, labels2 = self.ax2.get_legend_handles_labels()
			# L = self.ax2.legend(lines2, labels2, bbox_to_anchor = (0., 1.02, 1., .102), loc=3,
							# ncol=6, mode="expand", borderaxespad=0.)
			# legend_changed = False
		# xMax = max(xMax_xPosition, xMax_yPosition, xMax_zPosition, xMax_Roll, xMax_Yaw, xMax_Pitch)
		# yMin = min(yMin_xPosition, yMin_yPosition, yMin_zPosition, yMin_Roll, yMin_Yaw, yMin_Pitch)
		# yMax = max(yMax_xPosition, yMax_yPosition, yMax_zPosition, yMax_Roll, yMax_Yaw, yMax_Pitch)
		
		

		Prev_Rotation_Scaling_Factor  = Rotation_Scaling_Factor
		
		if self.stat_iXposition.get() == 1 or self.stat_iYposition.get() == 1 or self.stat_iZposition.get() == 1:
			if xMax_Position-30 <= 0:
				self.ax.set_xlim([0,xMax_Position])
				
			else:
				self.ax.set_xlim([xMax_Position-30,xMax_Position])
				
			self.ax.set_ylim([yMin_Position - abs(yMin_Position/10), yMax_Position + abs(yMax_Position/10)])
			self.ax.get_yaxis().set_major_formatter(ticker.FuncFormatter(lambda y, p: format(float(y), ',')))
			
		if self.stat_iroll.get() == 1 or self.stat_ipitch.get() == 1 or self.stat_iyaw.get() == 1:
			self.ax2.set_ylim([yMin_Angle - abs(yMin_Angle/10) ,yMax_Angle + abs(yMax_Angle/10)])
			self.ax2.get_yaxis().set_major_formatter(ticker.FuncFormatter(lambda y, p: format(float(y), ',')))
			
			if xMax_Angle-30 <= 0:
				self.ax.set_xlim([0,xMax_Angle])
				
			else:
				self.ax.set_xlim([xMax_Angle-30,xMax_Angle])
			
		self.ax.get_xaxis().set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',')))			
		canvas.draw()
		# master.after(1000,self.AnimatePlot(self.canvas))
		
class Video(threading.Thread):
    # Manages video streaming and Video Controls
    def __init__(self,master):
        threading.Thread.__init__(self)
        self.vidFrame=tk.Frame(master,bg='cyan')
        #stickyelf.vidFrame.config(padx=20)
 
        self.vidFrame.place(x=w,y=h,width=vidW,height=vidH)

        # def enforceAspectRatio(event):
        #     dw=int(0.7*event.width)
        #     dh=int(0.75*event.width)
        #     print "w,h is ",event.width, event.height,dw,dh
        #     self.vidLabel.config(width=dw,height=dh)
        #     print "frame size is", self.vidFrame.winfo_width(), self.vidFrame.winfo_height()  

        #self.vidFrame.bind("<Configure>",enforceAspectRatio)
        
        # Intialize vidControl Frame
        vidControl =tk.Frame(master)
        vidControl.place(x=w+vidW,y=h,width=screenW-vidW-w,height=int(0.25*screenH))
        self.recordButton = tk.Button(vidControl, 
                                        text="Record", 
                                        bd = 1,
                                        bg= "Red",
                                        command= self.recordVideo)
        w_dash=int(0.5*(screenW-vidW-w))
        h_dash=int(0.5*(int(0.25*vidH)))
        self.recordButton.place(x=0,y=0,width=w_dash,height=h_dash)
        screenshotButton = tk.Button(vidControl, 
                                            text = "Screen Capture",
                                            command=self.screenshot)
        screenshotButton.place(x=w_dash,y=0,width=screenW-vidW-w-w_dash,height=h_dash)

    	
    	#self.vidLabel.pack()
    	#self.vidLabel.pack(fill=tk.BOTH)

    	self.takeScreenShot=0 # Intialize screenshot toggle to be zerod
    	self.cameraChannelOnVideo=0 # Intialize Camera Channel to default to zero
    	#self.vid_cap = cv2.VideoCapture(self.cameraChannelOnVideo) # Assign channel to video capture
    	self.showVideo()

    def recordVideo(self):
        try:
            #w=int(self.vid_cap.get(3))
            #h=int(self.vid_cap.get(4))
            #fourcc = cv2.cv.CV_FOURCC('D','I','V','X')
            #outputFPS = 20.0
            #self.vidWriter = cv2.VideoWriter('Video_'+str(self.cameraChannelOnVideo)+
            #                '_'+strftime("%c")+'.avi', fourcc, outputFPS, (w, h), True)
            #self.videoWriter.open("output.avi", fourcc, outputFPS, (w, h))
            ''' @jmaddocks - please add logging code here'''
            self.recordButton.configure(text="Stop", 
                                        bg= "black",
                                        fg ="snow",
                                        command=self.stopVideoRecord)
        except:
            print "Something bad happened with recordVideo :("

    def stopVideoRecord(self):
        print "Stopped Recording Video"
        self.recordButton.configure(text="Record",
                                    bg="Red",
                                    fg ="Black",
                                    command= self.recordVideo)
        #self.vidWriter.release()

    def screenshot(self):
        self.takeScreenShot=1
        print 'Took a Screenshot!'
        
    def showVideo(self):
        #_, frame = self.vid_cap.read(0) 
        #frame = cv2.flip(frame, 1) # flips the video feed
        #cv2image = cv2.cvtColor(frame,cv2.COLOR_BGR2RGBA)
        #img = Image.fromarray(cv2image)
        self.vidLabel=tk.Label(self.vidFrame)
        self.vidLabel.pack(fill=tk.BOTH)
    	imgImport=Image.open('HW.jpg', mode='r')
        photo = ImageTk.PhotoImage(image=imgImport)
        self.vidLabel.imgarbage = photo
        self.vidLabel.config(image=photo)

        # save image if screenshot toggle is on
        if self.takeScreenShot==1:
            imgImport.save('Camera '+str(self.cameraChannelOnVideo)+'_'+strftime("%c")+'.jpg')
            self.takeScreenShot=0

        self.vidLabel.after(2,self.showVideo) # calls the method after 10 ms
		
class tkinterGUI(tk.Frame):
	def __init__(self, messages, startBool, Log_msgIDs, new_data):
		root=tk.Frame.__init__(self)

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
		loggingThread = loggingThreadClass(self, startBool, Log_msgIDs)
		statisticsThread = statisticsThreadClass(self, messages, new_data)
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


		# change this later based on UDP stream
		vidW=640
		vidH=480

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
		|     w,      |         Native Camera       |  w, 1/4*vidH  |
		|   2/3*vidH  |            Resolution       |_______________|
		|             |           vidW*vidH         |               |
		|             |                             |     Logging   |
		|             |                             |  w, 3/4*vidH  |
		|_____________|                             |               |
		|    modes    |                             |               |
		|      w,     |                             |               |
		|  1/3*vidH   |                             |               |
		|_____________|_____________________________|_______________|
		'''
		
def udpConnection():
	#ClientIPaddress = '192.168.1.107' # IP to send the packets
	ClientIPaddress = '192.168.7.2' # IP to send the packets
	portNum = 14551 # port number of destination
	device = 'udpout:' + str(ClientIPaddress) + ':' + str(portNum)
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
	
	return master
	
def UDP(messages, startLogging, Log_msgIDs, new_data):
	sizeOfBuffer = 10
	UDPlistenThread=listener(sizeOfBuffer, messages, startLogging, Log_msgIDs, new_data) # sizeOfRingBuffer
	UDPlistenThread.setDaemon(True)
	
	#UDPlogThread=logger(Packets)
	#UDPlogThread.setDaemon(True)
	
	print('UDP process starting')
	UDPlistenThread.start()

	# UDPlogThread.start()

	# print 'Pack:' + str(messages[:]) #The Packet which will be outputted to the plotter
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
	
def startTkinter(PlotPacket,startBool, msgIDs, new_data):
    root = tkinterGUI(PlotPacket,startBool, msgIDs, new_data)
    root.master.title("Azog") # Name of current drone, Here it is Azog
    root.mainloop()

def sendSettingPacket(m,f,p,c):
	# m - Mapping modes are : SLAM (0) or VICON pos input (1)
	# f - Flight modes are : Altitude (2) vs Manual Thrust (3) vs POS hold (4)
	# p - Pilot reference mode: global (5), First Person View (6), PPV (7)
	# c - Control mode: User (8) , Auto land (9), Come back home (10), Circle Mode (11)
	print "New Settings received :",'Mapping Mode',m,'\tFlight Mode :',f,'\tPilot Reference Mode',p,'\tControl Mode',c
	# mav_flight_mode_ctrl        : (See MAV_CTRL_MODE) Valid options are: MAV_CTRL_MODE_MANUAL = 0, MAV_CTRL_MODE_ALTITUDE = 1, MAV_CTRL_MODE_ATTITUDE = 2, MAV_CTRL_MODE_POS_LOCAL = 3, MAV_CTRL_MODE_POS_GLOBAL = 4, MAV_CTRL_MODE_POS_RADIAL = 5, MAV_CTRL_MODE_POS_SPHERICAL = 6, MAV_CTRL_MODE_POS_FOLLOW_ME = 7 (uint8_t)
	# mav_flight_mode_auto        : (See MAV_AUTO_MODE) Valid options are: MAV_AUTO_MODE_MANUAL = 0, MAV_AUTO_MODE_EMERGENCY_LAND = 1, MAV_AUTO_MODE_RETURN_TO_HOME = 2, MAV_AUTO_MODE_WANDER = 3 (uint8_t)
	# mav_flight_mode_kill        : (See MAV_KILL) Valid options are: MAV_KILL_SWITCH_OFF = 0, MAV_KILL_NOW = 1 (uint8_t)
	#mav_flight_ctrl_and_modes_send(chan1_raw, chan2_raw, chan3_raw, chan4_raw, chan5_raw, chan6_raw, chan7_raw, chan8_raw, mav_flight_mode_ctrl, mav_flight_mode_auto, mav_flight_mode_kill)
	#mav_flight_ctrl_and_modes_send(chan1_raw, chan2_raw, chan3_raw, chan4_raw, chan5_raw, chan6_raw, chan7_raw, chan8_raw, mav_flight_mode_ctrl, mav_flight_mode_auto, mav_flight_mode_kill)
	
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
	manager = Manager()
	startLogging = Value('i', 0, lock = lock)
	new_data = Value('i', 0, lock = lock)
	messages = manager.dict()
	Log_msgIDs = manager.list()
	# Log_msgIDs = Array('i', [0]*4, lock = lock)
	# print 'Start Bool: ' + str(startLogging.value) + '\n'
	# UDPmaster = udpConnection()
	udpProcess = Process(name = 'UDP Process', target = UDP, args=(messages, startLogging, Log_msgIDs, new_data))
	TkinterProcess = Process(name='Tkinter Process', target=startTkinter, args=(messages, startLogging, Log_msgIDs, new_data))
    # broadcastProcess = Process(name='Broadcasting Process', target=broadcast)
	udpProcess.start()
	TkinterProcess.start()
	udpProcess.join()
	TkinterProcess.join()
	
if __name__ == '__main__':
	main()
