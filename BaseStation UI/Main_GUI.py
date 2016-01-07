import Tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
# matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from PIL import ImageTk , Image # for image conversion
import cv2 # OpenCV for video handling
import tkFont, threading, Queue, multiprocessing, tkMessageBox
from time import strftime, sleep
from collections import deque
import socket # for sending across UDP packets 

allDronesList=['Othrod','The Great Goblin','Boldog','Ugluk','Bolg','Orcobal','More Orcs','Orc1','Orc2','Orc3','Orc4']
activeDronesList=['Othrod','Ugluk','Bolg','Orcobal'] 

class listener(threading.Thread):
    def __init__(self,sizeOfBuffer):
        threading.Thread.__init__(self)
        self.receviedPacketBuffer = deque([], sizeOfBuffer)
        print "Initialized Ring Buffer as size of", sizeOfBuffer

    def run(self):
        for i in xrange(12): # replace by reading head
            self.receviedPacketBuffer.append(i)
            print "Buffer is : ", self.receviedPacketBuffer
            #print "Last element is ", self.receviedPacketBuffer[len(self.receviedPacketBuffer)-1] # show last element - required for other operations
            sleep(0.1)

class logger(threading.Thread):

	def __init__(self,listeningThread):
		threading.Thread.__init__(self)
		# self.recordData = False
		self.listenerobject = listeningThread
		
	# def record_data(self):
		# self.recordData = True
		
		# file='testfile.txt'		
		# self.logfile = open(file,"w",1) # use a = append mode, buffering set to true
		# print "file", file, "is opened"
		
		# return self.recordData
		
		file = 'testfile.txt'
		self.listenerobject = listeningThread
		self.logfile = open(file, 'w',1)
		print "The file", file, "has been opened"
		
		try:
			while 1:
				sleep(0.1)				
				if len(self.listenerobject.receviedPacketBuffer)>0:
					data=strftime("%c")+"\t"+str(self.listenerobject.receviedPacketBuffer.popleft())+"\n"
					self.logfile.write(data)
					
		except IndexError:
			print "No elements in the Buffer"
			
		return self.logfile
		
	# def stop_recording(self):
		# self.recordData = False
		# print "closing the file"
		# self.logfile.close()
		# print file + "is not open"
	
	def Print():
		print 'Log hi!'
	
	def run(self): 
		try :
			sleep(0.5)
			tempData=""
			m=0
			while m<50: # change this
				if len(self.listenerobject.receviedPacketBuffer)>0: #& self.listenerobject.isBufferBusy==0:
					# self.listenerobject.isBufferBusy=1
					val=self.listenerobject.receviedPacketBuffer.popleft()
					data=strftime("%c")+"\t"+str(val)+"\n"
					tempData=tempData+data
					m=m+1
					# self.listenerobject.isBufferBusy=0

				# if m%20==0:
			if self.recordData in True:
				self.logfile.write(tempData)
				print "wrote to disk"                
				tempData="" 

		except IndexError:
			print "No elements in the Buffer"
			self.logfile.close()
			
class myUAVThreadClass(threading.Thread):

	def __init__(self,master):
		threading.Thread.__init__(self)
		myUAVFrame = tk.Frame(master)
		myUAVFrame.grid(row = 0, 
						column = 0,
						rowspan = 1,
						columnspan = 1,
						sticky = tk.S + tk.N + tk.W + tk.E)
		myUAVFrame.rowconfigure(0, weight = 1)
		myUAVFrame.columnconfigure(0, weight = 1)
		myUAVFrame.columnconfigure(1, weight = 1)
		myUAVFrame.columnconfigure(2, weight = 1)
		myUAVFrame.columnconfigure(3, weight = 1)
		
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
        otherDroneCanvas.grid(row=0,
                        column=2,
                        rowspan=1,
                        columnspan=3,
                        sticky=tk.N+tk.S+tk.W+tk.E)
        otherDroneCanvas.rowconfigure(0,weight=1)
        #self.updateActiveDrones(droneFrame)
        # Intialize places for
        i=0 # counter for referencing objects in the list
        self.allDroneDict=dict() # initalizing empty dictionary 
        for orc in allDronesList:
            otherDroneCanvas.columnconfigure(i,weight=1)
            self.allDroneDict[orc]=tk.Button(otherDroneCanvas,text=orc, bg = "gray14", fg="snow")
            self.allDroneDict[orc].grid(row=0,column=i,sticky=tk.N+tk.S+tk.E+tk.W)
            i=i+1

        scrollBarOtherDrones = AutoScrollbar(otherDroneCanvas,orient=tk.HORIZONTAL)
        scrollBarOtherDrones.grid(row=1,columnspan=i,sticky=tk.E+tk.W)

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
            self.allDroneDict[orc].configure(bg='medium spring green', fg='black')
			
class loggingThreadClass(threading.Thread):
	
	def __init__(self, master):
		threading.Thread.__init__(self)
		loggingFrame = tk.Frame(master)
		loggingFrame.grid(row = 3, 
						column = 3,
						rowspan = 1,
						columnspan = 1,
						sticky = tk.S + tk.N + tk.W + tk.E)
		loggingFrame.rowconfigure(0, weight = 1)
		loggingFrame.rowconfigure(1, weight = 1)
		loggingFrame.rowconfigure(2, weight = 1)
		loggingFrame.rowconfigure(3, weight = 1)
		loggingFrame.rowconfigure(4, weight = 1)
		loggingFrame.rowconfigure(5, weight = 1)
		loggingFrame.rowconfigure(6, weight = 1)
		loggingFrame.columnconfigure(0, weight = 1)
		loggingFrame.columnconfigure(3, weight = 1)
		
		log_attitudeBoxFrame = tk.Frame(loggingFrame)
		log_attitudeBoxFrame.grid(row = 0, sticky = tk.N + tk.S + tk.W + tk.E)
		log_positionBoxFrame = tk.Frame(loggingFrame)
		log_positionBoxFrame.grid(row = 1, sticky = tk.N + tk.S + tk.W + tk.E)
		log_velocityBoxFrame = tk.Frame(loggingFrame)
		log_velocityBoxFrame.grid(row = 2, sticky = tk.N + tk.S + tk.W + tk.E)
		log_batteryBoxFrame = tk.Frame(loggingFrame)
		log_batteryBoxFrame.grid(row = 3, sticky = tk.N + tk.S + tk.W + tk.E)
		
		log_recordButtonFrame = tk.Frame(loggingFrame)
		log_recordButtonFrame.grid(row = 4, column = 0, sticky = tk.N + tk.S + tk.W + tk.E)
		log_stopButtonFrame = tk.Frame(loggingFrame)
		log_stopButtonFrame.grid(row = 5, column = 0, sticky = tk.N + tk.S + tk.W + tk.E)
		
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
		
		log_recordButton = tk.Button(log_recordButtonFrame, text = 'Record', command = logger.Print)
		log_stopButton = tk.Button(log_stopButtonFrame, text = 'Stop', command = master.destroy)
		
		log_recordButton.pack(side = tk.BOTTOM, fill = tk.BOTH, expand = 1)
		log_stopButton.pack(side = tk.BOTTOM, fill = tk.BOTH, expand = 1)
		
		# self.checkbox_names = ['Attitude', 'Position', 'Velocity', 'Battery']
		# self.button_names = ['Record', 'Stop']
		# self.vars = []
		self.loggingVariables = []
		# counter = 0
		
	
		# for self.checkbox_name in self.checkbox_names:
			# var = tk.IntVar()
			# CheckButtonFrame = tk.Frame(loggingFrame)
			# CheckButtonFrame.grid(row = 1 + counter, sticky = tk.N + tk.S + tk.E + tk.W)
			# loggingCheckbutton = tk.Checkbutton(CheckButtonFrame, text = self.checkbox_name, variable = var)
			# loggingCheckbutton.grid(row = row + counter, column = col, rowspan = row_span, columnspan = col_span, sticky=tk.N+tk.S+tk.E+tk.W)
			# loggingCheckbutton.rowconfigure(counter, weight = 1)
			# loggingCheckbutton.columnconfigure(3, weight = 1)
			# loggingCheckbutton.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
			# counter += 1
			
		# self.vars = []
		# counter = 0
		
		# for self.button_name in self.button_names:
			# var = tk.IntVar()
			# ButtonFrame = tk.Frame(loggingFrame)
			# ButtonFrame.grid(row = 4 + counter, sticky = tk.N + tk.S + tk.W + tk.E)
			
			# if self.button_name in ('Record'):
				# loggingButton = tk.Button(ButtonFrame, text = self.button_name, command = lambda: logger.record_data)
				
			# elif self.button_name in ('Stop'):
				# loggingButton = tk.Button(ButtonFrame, text = self.button_name, command = lambda: logger.stop_recording(loggingButton))
			
			# loggingButton.columnconfigure(0 + counter, weight = 1)
			# loggingButton.rowconfigure(4 + counter, weight = 1)
			# loggingButton.pack(side = tk.BOTTOM, fill = tk.BOTH, expand = 1)
			# loggingButton.grid(row = row + counter, column = col + counter, rowspan = row_span, columnspan = col_span, sticky=tk.N+tk.S+tk.E+tk.W)
			# counter += 1
	
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
		
	def Stop(self, master):
		master.quit()     # stops mainloop
		master.destroy()  # this is necessary on Windows to prevent
							# Fatal Python Error: PyEval_RestoreThread: NULL tstate
							
	def logVariables(self, var_Name, var_State):
	
		if var_State == 1:
			self.loggingVariables.append(var_Name)
			print self.loggingVariables
			
		elif var_State == 0:
			ivar_Name = self.loggingVariables.index(var_Name)
			self.loggingVariables.pop(ivar_Name)
			print self.loggingVariables
			
	def run(self):
		pass
	
	# self.rowconfigure(row, weight = 1)
	# self.columnconfigure(col, weight = 1)
class statVariables(object):

	def getVelocity(self):
		return random.randint(0,50)
		
	def getAcceleration(self):
		return random.randint(50,100)
		
	def getPosition(self):
		return random.randint(0,25)
		
	def getRoll(self):
		return random.randint(25,50)
		
	def getPitch(self):
		return random.randint(50,75)
		
	def getYaw(self):
		return random.randint(75,100)
		
# class settingsThreadClass(threading.Thread):
	
	# def __init__(self, master):
		# threading.Thread.__init__(self)		
		# self.settingsFrame = tk.Frame(master)
	# def run(self):		
		# self.settingsFrame.grid(row = 7, 
								# column = 0, 
								# rowspan = 1,
								# columnspan = 2,
								# sticky = tk.S + tk.N + tk.W + tk.E)
		# self.settingsFrame.rowconfigure(5, weight = 1)
		# self.settingsFrame.rowconfigure(6, weight = 1)
		# self.settingsFrame.columnconfigure(0, weight = 1)
		
		# set_positionBoxFrame = tk.Frame(self.settingsFrame)
		# set_positionBoxFrame.grid(row = 5, sticky = tk.N + tk.S + tk.W + tk.E)
		# set_attitudeBoxFrame = tk.Frame(self.settingsFrame)
		# set_attitudeBoxFrame.grid(row = 6, sticky = tk.N + tk.S + tk.W + tk.E)
		
		# set_iattitude = tk.IntVar()
		# set_iposition = tk.IntVar()
		
		# set_attitudeCheckButton = tk.Checkbutton(set_attitudeBoxFrame, text = 'Attitude', variable = set_iattitude.get)
		# set_positionCheckButton = tk.Checkbutton(set_positionBoxFrame, text = 'Position', variable = set_iposition.get)
		
		# set_attitudeCheckButton.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)
		# set_positionCheckButton.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)
		
		# self.names = ['Position', 'Attitude']
		# self.vars = []
		# counter = 0
		
		# for self.name in self.names:
			# var = tk.IntVar()			
			# CheckBoxFrame = tk.Frame(settingsFrame)
			# CheckBoxFrame.grid(row = 0 + counter, sticky = tk.N + tk.S + tk.W + tk.E)
			# settingsCheckButtons = tk.Checkbutton(CheckBoxFrame, text = self.name, variable = var)
			# settingsCheckButtons.rowconfigure(0 + counter, weight = 1)
			# settingsCheckButtons.columnconfigure(0, weight = 1)
			# settingsCheckButtons.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)
			# counter += 1
			# settings.grid(row = row + counter, column = col, rowspan = row_span, columnspan = col_span, sticky=tk.N+tk.S+tk.E+tk.W)
		# return set_iattitude.get(), set_iposition.get()
# class VideoWidget(Frame):
# class PlotWindow(tk.Frame):
	# def __init__(self, master)
		# tk.Frame.__init__(self,master)
		# plotFrame.grid
		
class settingsThreadClass(threading.Thread):
    def __init__(self,master):
        threading.Thread.__init__(self)
        settingsFrame=tk.Frame(master)
        settingsFrame.grid(row=3,
            column=0,
            sticky=tk.N+tk.S+tk.E+tk.W)
        settingsFrame.rowconfigure(0, weight=1)
        settingsFrame.rowconfigure(1, weight=1)
        settingsFrame.rowconfigure(2, weight=1)
        settingsFrame.rowconfigure(3, weight=1)
        settingsFrame.rowconfigure(4, weight=1)
        settingsFrame.columnconfigure(0, weight=1)
        # Mapping modes are : SLAM (0) or VICON pos input (1)
        # Flight modes are : Altitude (2) vs Manual Thrust (3) vs POS hold (4)
        # Pilot reference mode: global (5), First Person View (6), PPV (7)
        # Control mode: User (8) , Auto land (9), Come back home (10), Circle Mode (11) 

        killButton=tk.Button(settingsFrame, text="Kill Drone", command = killDroneMethod, bg ="red")
        killButton.grid(row=0,sticky=tk.N+tk.S+tk.E+tk.W)
        mappingModeFrame=tk.Frame(settingsFrame)
        mappingModeFrame.grid(row=1,sticky=tk.N+tk.S+tk.E+tk.W)
        flightModeFrame=tk.Frame(settingsFrame)
        flightModeFrame.grid(row=2,sticky=tk.N+tk.S+tk.E+tk.W)
        pilotReferenceModeFrame=tk.Frame(settingsFrame)
        pilotReferenceModeFrame.grid(row=3,sticky=tk.N+tk.S+tk.E+tk.W)
        controlModeFrame=tk.Frame(settingsFrame)
        controlModeFrame.grid(row=4,sticky=tk.N+tk.S+tk.E+tk.W)

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
	
	def __init__(self, master):
		threading.Thread.__init__(self)
		statisticsFrame = tk.Frame(master)
		statisticsFrame.grid(row = 1,
								column = 1,
								rowspan = 5,
								columnspan = 2)
		statisticsFrame.rowconfigure(1, weight = 1)
		statisticsFrame.rowconfigure(2, weight = 1)
		statisticsFrame.rowconfigure(3, weight = 1)
		statisticsFrame.rowconfigure(4, weight = 1)
		statisticsFrame.rowconfigure(5, weight = 1)
		statisticsFrame.rowconfigure(6, weight = 1)
		statisticsFrame.columnconfigure(1, weight = 1)
		
		plotFrame = tk.Frame(master)
		plotFrame.grid(row = 1,
						column = 0,
						rowspan = 1,
						columnspan = 1,
						sticky = tk.N + tk.S + tk.W + tk.E)
		plotFrame.rowconfigure(2, weight = 1)
		plotFrame.columnconfigure(0, weight = 1)
		
		stat_velocityBoxFrame = tk.Frame(statisticsFrame)
		stat_velocityBoxFrame.grid(row = 1, column = 1, sticky = tk.N + tk.S + tk.W + tk.E)
		stat_accelerationBoxFrame = tk.Frame(statisticsFrame)
		stat_accelerationBoxFrame.grid(row = 2, column = 1, sticky = tk.N + tk.S + tk.W + tk.E)
		stat_positionBoxFrame = tk.Frame(statisticsFrame)
		stat_positionBoxFrame.grid(row = 3, column = 1, sticky = tk.N + tk.S + tk.W + tk.E)
		stat_rollBoxFrame = tk.Frame(statisticsFrame)
		stat_rollBoxFrame.grid(row = 4, column = 1, sticky = tk.N + tk.S + tk.W + tk.E)
		stat_pitchBoxFrame = tk.Frame(statisticsFrame)
		stat_pitchBoxFrame.grid(row = 5, column = 1, sticky = tk.N + tk.S + tk.W + tk.E)
		stat_yawBoxFrame = tk.Frame(statisticsFrame)
		stat_yawBoxFrame.grid(row = 6, column = 1, sticky = tk.N + tk.S + tk.W + tk.E)
		
		stat_ivelocity = tk.IntVar()
		stat_iacceleration = tk.IntVar()
		stat_iposition = tk.IntVar()
		stat_iroll = tk.IntVar()
		stat_ipitch = tk.IntVar()
		stat_iyaw = tk.IntVar()
		
		quad = statVariables()
		
		
		# x = range(100)
		# y = range(100)
		# f = Figure(figsize = (3,3), dpi = 50)
		# a = f.add_subplot(111)
		fig = plt.figure(figsize = (5,5), dpi = 100)
		self.ax = fig.add_subplot(111)
		# plt.ion()
		plt.xlabel('Time(s)')
		plt.ylabel('Variable Name')
		# plt.show()
		
		canvas = FigureCanvasTkAgg(fig, plotFrame)
		canvas.show()
		canvas.get_tk_widget().pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
		
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
		
		
		# self.names = ['Velocity', 'Acceleration', 'Position', 'Roll', 'Pitch', 'Yaw']
		# self.vars = []
		# counter = 0
		
		# for i in range(len(self.names)):
			# var = tk.IntVar()
			# CheckBoxFrame = tk.Frame(statisticsFrame)
			# CheckBoxFrame.grid(row = 0 + counter, sticky = tk.N + tk.S + tk.W + tk.E)
			# if self.name[i] in ('Velocity'):
				# statisticsCheckButton = tk.Checkbutton(CheckBoxFrame, text = self.name[i], variable = var, command = lambda i=i: self.Plot(self.name[i]))
			# elif self.name[i] in ('Acceleration'):
				# statisticsCheckButton = tk.Checkbutton(CheckBoxFrame, text = self.name[i], variable = var, command = lambda i=i: self.Plot(self.name[i]))
			# elif self.name[i] in ('Position'):
				# statisticsCheckButton = tk.Checkbutton(CheckBoxFrame, text = self.name[i], variable = var, command = lambda i=i: self.Plot(self.name[i]))
			# elif self.name[i] in ('Roll'):
				# statisticsCheckButton = tk.Checkbutton(CheckBoxFrame, text = self.name[i], variable = var, command = lambda i=i: self.Plot(self.name[i]))
			# elif self.name[i] in ('Pitch'):
				# statisticsCheckButton = tk.Checkbutton(CheckBoxFrame, text = self.name[i], variable = var, command = lambda i=i: self.Plot(self.name[i]))				
			# elif self.name[i] in ('Yaw'):
				# statisticsCheckButton = tk.Checkbutton(CheckBoxFrame, text = self.name[i], variable = var, command = lambda i=i: self.Plot(self.name[i]))	
			# print 'Name: ' + self.name[i]
			# statisticsCheckButton.rowconfigure(0+counter, weight = 1)
			# statisticsCheckButton.columnconfigure(0, weight = 1)
			# statisticsCheckButton.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
			# statistics.grid(row = row + counter, column = col, rowspan = row_span, columnspan = col_span, sticky=tk.N+tk.S+tk.E+tk.W)
			# counter += 1
			
			
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
    def __init__(self,master):
        threading.Thread.__init__(self)
        self.vidFrame=tk.Frame(master)
        #stickyelf.vidFrame.config(padx=20)
 
        self.vidFrame.grid(row=1,
                      column=1,
                      rowspan=3,
                      columnspan=3,
                      sticky=tk.S+tk.N+tk.E+tk.W)
        self.vidLabel=tk.Label(self.vidFrame)

        # self.vidLabel.grid(row=1,
        #               column=1,
        #               rowspan=3,
        #               columnspan=2,
        #               sticky=tk.S+tk.N+tk.E+tk.W)

        self.vidLabel.pack(fill=tk.BOTH,expand=1)

        def enforceAspectRatio(event):
            dw=int(0.7*event.width)
            dh=int(0.75*event.width)
            print "w,h is ",event.width, event.height,dw,dh
            self.vidLabel.config(width=dw,height=dh)
            print "frame size is", self.vidFrame.winfo_width(), self.vidFrame.winfo_height()  

        #self.vidFrame.bind("<Configure>",enforceAspectRatio)
        

        # Intialize vidControl Frame
        vidControl =tk.Frame(master)
        vidControl.grid(row=1,
                      column=4,
                      rowspan=1,
                      columnspan=1,
                      sticky=tk.N+tk.S+tk.E+tk.W)
        self.recordButton = tk.Button(vidControl, 
                                        text="Record", 
                                        bd = 1,
                                        bg= "Red",
                                        command= self.recordVideo)
        self.recordButton.pack(fill=tk.BOTH,
                                expand=1)
        toggleCameraButton = tk.Button(vidControl, 
                                            text = "Camera Toggle", 
                                            command=self.toggleCamera)
        toggleCameraButton.pack(fill=tk.BOTH,
                                    expand=1)
        screenshotButton = tk.Button(vidControl, 
                                            text = "Screen Capture",
                                            command=self.screenshot)
        screenshotButton.pack(fill=tk.BOTH,
                                   expand=1)
        depthToggleButton = tk.Button(vidControl,
                                        text = "Show Depth",
                                        command=self.depthToggle)
        depthToggleButton.pack(fill=tk.BOTH,
                                    expand=1)

    def run(self):
        self.saveVideoToggle=0 # Intialize videocapture toggle to zero
        self.takeScreenShot=0 # Intialize screenshot toggle to be zerod
        self.cameraChannelOnVideo=0 # Intialize Camera Channel to default to zero
        self.vid_cap = cv2.VideoCapture(self.cameraChannelOnVideo) # Assign channel to video capture
        self.showVideo(self.vidLabel,self.vidFrame)

    def recordVideo(self):
        try:
            w=int(self.vid_cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH ))
            h=int(self.vid_cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT ))
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
            print "Something bad happened with recordVideo"

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

        frameAspectRatio = (float(vidFrame.winfo_width())/float(vidFrame.winfo_height()))
        if frameAspectRatio > (1.333): # Frame is wider than it needs to be
           new_height= int(10*(vidFrame.winfo_height()/10)) # round image size to nearest
           new_width=int(1.33*new_height)
        else: # Frame is taller than it needs to be
            new_width= int(10*(vidFrame.winfo_width()/10))
            new_height =int(0.75* new_width)
        img_resize= img.resize([new_width,new_height]) #resizing image
        imgtk = ImageTk.PhotoImage(image=img_resize)
        vidLabel.imgarbage = imgtk # for python to exclude image from garbage collection
        vidLabel.configure(image=imgtk)
        vidLabel.after(2,self.showVideo,vidLabel,vidFrame) # calls the method after 10 ms
		
class Application(tk.Frame):
    def __init__(self):
		tk.Frame.__init__(self)
		self.grid()
		self.grid(sticky = tk.N + tk.S + tk.E + tk.W)
		# make top level of the application stretchable and space filling
		top=self.winfo_toplevel()
		top.rowconfigure(0, weight=1)
		top.columnconfigure(0, weight=1)
		# make all rows and columns grow with the widget window ; weight signifies relative rate of window growth
		self.rowconfigure(0, weight=1)
		self.rowconfigure(1, weight=1)
		self.rowconfigure(2, weight=1)
		self.rowconfigure(3, weight=1)
		self.rowconfigure(4, weight=1)
		self.rowconfigure(5, weight=1)
		self.rowconfigure(6, weight=1)
		self.rowconfigure(7, weight=1)
		self.rowconfigure(8, weight=1)
		self.rowconfigure(9, weight=1)
		self.columnconfigure(0, weight=1)
		self.columnconfigure(1, weight=1)
		self.columnconfigure(2, weight=1)
		self.columnconfigure(3, weight=1)
		
        # Set up the GUI
		# console = tk.Button(self, text='Done', command=endCommand)
		# console.grid(row = 5, column = 0, rowspan = 3, columnspan = 2)
		
		videoThread=Video(self)
		settingsThread = settingsThreadClass(self)
		loggingThread = loggingThreadClass(self)
		statisticsThread = statisticsThreadClass(self)
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
		
def UDP():
	UDPlistenThread = listener(6) # sizeOfRingBuffer
	UDPlistenThread.setDaemon(False) # exit UI even if some listening is going on
	
	UDPloggingThread = logger(UDPlistenThread)
	UDPloggingThread.setDaemon(False)
	
	UDPlistenThread.start()
	UDPloggingThread.start()
	
	UDPlistenThread.join()
	UDPloggingThread.join()
	
def startTkinter():
	root = Application()
	root.master.title("GUI")
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
	# while 1:
		# print "Sent packets"
		# sleep (5)
	pass
	
class AutoScrollbar(tk.Scrollbar):
    # a scrollbar that hides itself if it's not needed.  only
    # works if you use the grid geometry manager.
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            # grid_remove is currently missing from Tkinter!
            self.tk.call("grid", "remove", self)
        else:
            self.grid()
        Scrollbar.set(self, lo, hi)
    def pack(self, **kw):
        raise TclError, "cannot use pack with this widget"
    def place(self, **kw):
        raise TclError, "cannot use place with this widget"
        raise tk.TclError, "cannot use place with this widget"	
		
def main():
	#global udpProcess # try to kill updprocess using startTkinter	
	udpProcess = multiprocessing.Process(name = 'UDP Process', target = UDP)
	TkinterProcess = multiprocessing.Process(name = 'Tkinter Process', target = startTkinter)
	broadcastProcess = multiprocessing.Process(name = 'Broadcasting Process', target = broadcast)
	
	udpProcess.start()
	TkinterProcess.start()
	broadcastProcess.start()
	
if __name__ == '__main__':
	main()