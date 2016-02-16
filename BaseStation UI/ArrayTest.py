# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 12:43:15 2016

@author: FailingToFocus
"""

import threading # multithreading 
from multiprocessing import Process, Lock #multiprocessing
import tkMessageBox # for messageboxes 
import Tkinter as tk
from PIL import ImageTk , Image # for image conversion
import cv2 # OpenCV for video handling
import tkFont # for fonts
from time import strftime,sleep # for sleep
from collections import deque # for ring buffer
import socket # for sending across UDP packets 
from multiprocessing.sharedctypes import Value, Array
from ctypes import Structure, c_double, c_short, c_long

allDronesList=['Othrod','The Great Goblin','Boldog','Ugluk','Bolg','Orcobal','More Orcs','Orc1','Orc2','Orc3','Orc4']
activeDronesList=['Othrod','Ugluk','Bolg','Orcobal'] 
# move these lists to the respective buffer /data structures eventually 
killUDPprocessCounter=1

class MyUAV(threading.Thread):
    def __init__(self,master,r,c,rspan,cspan):
		threading.Thread.__init__(self)
		MyUAV=tk.Frame(master)
		MyUAV.grid(row=r, 
					column=c,
					rowspan=rspan,
					columnspan=cspan,
					sticky=tk.N+tk.S+tk.W+tk.E)#stretch the widget both horizontally and 
								# vertically to fill the cell

		testButton=tk.Button(master,
							text='Overwrite',
							command=master.OnButton)
		testButton.grid(row=r, 
						column=c,
						rowspan=rspan,
						columnspan=cspan,
						sticky = tk.N+tk.S+tk.W+tk.E)
		
		
    def run(self):
		i=0		
		while i<6:
			print 'i is =',i
			# print '# active threads in MyUAV loop are',threading.enumerate()
			sleep(5)
			i+= 1

class otherdrones(threading.Thread):
    def __init__(self,master, PlotPacket):
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

		self.PlotPacket = PlotPacket
		
    def run(self):
        sleep(2) # remove this eventually
        i=1
        while 1:			
			self.updateActiveDrones()
			if (i%20)==0: # print every 30 seconds - thread is alive
				print "Updated Active Drones in the vicinity" 
				print 'The Packet being plotted is: ' + str(self.PlotPacket[:]) #This is the packet that would be sent to the Settings Thread for plotting
			i=i+1
			sleep(0.5) # sleep for 500ms before updating

    def updateActiveDrones(self):
        # add missing key error exceptions here
        for orc in activeDronesList:
            self.allDroneDict[orc].configure(bg='medium spring green', fg='black')

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
        controlModeRadioButton9=tk.Radiobutton(controlModeFrame, text="Auto Emergency Land", variable=c,
                                            value=9,indicatoron=0,
                                            command=lambda : sendSettingPacket(m.get(),f.get(),p.get(),c.get()))
        controlModeRadioButton10=tk.Radiobutton(controlModeFrame, text="Auto Return Home", variable=c,
                                            value=10,indicatoron=0,
                                            command=lambda : sendSettingPacket(m.get(),f.get(),p.get(),c.get()))
        controlModeRadioButton11=tk.Radiobutton(controlModeFrame, text="Hover", variable=c,
                                            value=11,indicatoron=0,
                                            command=lambda : sendSettingPacket(m.get(),f.get(),p.get(),c.get()))
        controlModeRadioButton8.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)
        controlModeRadioButton9.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)
        controlModeRadioButton10.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)
        controlModeRadioButton11.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)

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
        
class tkinterGUI(tk.Frame):         
    def __init__(self, PlotPacket, startBool, stopBool): 
		tk.Frame.__init__(self)
		self.grid()
		self.grid(sticky=tk.N+tk.S+tk.E+tk.W) #The argument sticky=tk.N+tk.S+tk.E+tk.aW to self.grid() is necessary so that the Application widget will expand to fill its cell of the top-level window's grid
		# make top level of the application stretchable and space filling 
		top=self.winfo_toplevel() 
		top.rowconfigure(0, weight=1)
		top.columnconfigure(0, weight=1)
		# make all rows and columns grow with the widget window ; weight signifies relative rate of window growth
		self.rowconfigure(0, weight=1)
		self.rowconfigure(1, weight=1)
		self.rowconfigure(2, weight=1)
		self.rowconfigure(3, weight=1)
		self.columnconfigure(0, weight=1)
		self.columnconfigure(1, weight=1)
		self.columnconfigure(2, weight=1)
		self.columnconfigure(3, weight=1)
		
		Status=tk.Frame(self)
		Status.grid()
		#Log=tk.Frame(self)
		#Log.grid()

		#videoThread=Video(self)
		otherDrones = otherdrones(self,PlotPacket)
		myUAVThread = MyUAV(self,0,0,1,2)
		settingsThread = settingsThreadClass(self)
		loggingThread = loggingThreadClass(self, startBool, stopBool)

		# Quit even if some operations are remaining to be complete

		#videoThread.setDaemon(True)
		myUAVThread.setDaemon(True)
		otherDrones.setDaemon(True)
		settingsThread.setDaemon(True)
		loggingThread.setDaemon(True)

		self.createWidgets(Status,'Stats',1,0,2,1)
		#self.createWidgets(Settings,'Settings',3,0,1,1)
		#self.createWidgets(Log,'Logging',2,4,2,1)

		#videoThread.start() # becomes mainthread
		myUAVThread.start() # becomes secondard thread
		otherDrones.start()
		settingsThread.start()
		loggingThread.start()
		print '# active threads are ',threading.enumerate()
		
		top.protocol("WM_DELETE_WINDOW", closeProgram) # controls what happens on exit : aim to close other threads


    def createWidgets(self,frame,txt,r,c,rspan,cspan):
        # for testing

        self.qt = tk.Button(self, text=txt,command=self.quit)
        self.qt.grid(row=r, column=c,rowspan=rspan,columnspan=cspan,
        sticky=tk.N+tk.S+tk.W+tk.E) #stretch the widget both horizontally and

    def OnButton(self):
        # for testing only
        result=tkMessageBox.askokcancel(title="File already exists", message="File already exists. Overwrite?")
        killUDPprocessCounter=0
        if result is True:
            print "User clicked Ok"
        else:
            print "User clicked Cancel"

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
        
class loggingThreadClass(threading.Thread):
	
	def __init__(self, master, startBool, stopBool):
		threading.Thread.__init__(self)
		loggingFrame = tk.Frame(master)
		loggingFrame.grid(row = 2, 
						column = 3,
						rowspan = 1,
						columnspan = 1,
						sticky = tk.S + tk.N + tk.W + tk.E)
		loggingFrame.rowconfigure(2, weight = 1)
		loggingFrame.rowconfigure(3, weight = 1)
		loggingFrame.rowconfigure(4, weight = 1)
		loggingFrame.rowconfigure(5, weight = 1)
		loggingFrame.rowconfigure(6, weight = 1)
		loggingFrame.rowconfigure(7, weight = 1)
		loggingFrame.columnconfigure(4, weight = 1)
		
		log_attitudeBoxFrame = tk.Frame(loggingFrame)
		log_attitudeBoxFrame.grid(row = 2, column = 4, sticky = tk.N + tk.S + tk.W + tk.E)
		log_positionBoxFrame = tk.Frame(loggingFrame)
		log_positionBoxFrame.grid(row = 3, column = 4, sticky = tk.N + tk.S + tk.W + tk.E)
		log_velocityBoxFrame = tk.Frame(loggingFrame)
		log_velocityBoxFrame.grid(row = 4, column = 4, sticky = tk.N + tk.S + tk.W + tk.E)
		log_batteryBoxFrame = tk.Frame(loggingFrame)
		log_batteryBoxFrame.grid(row = 5, column = 4, sticky = tk.N + tk.S + tk.W + tk.E)
		
		log_startButtonFrame = tk.Frame(loggingFrame)
		log_startButtonFrame.grid(row = 6, column = 4, sticky = tk.N + tk.S + tk.W + tk.E)
		log_stopButtonFrame = tk.Frame(loggingFrame)
		log_stopButtonFrame.grid(row = 7, column = 4, sticky = tk.N + tk.S + tk.W + tk.E)
		
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

class listener(threading.Thread):
    def __init__(self,sizeOfBuffer, n, startLogging, stopLogging):
		threading.Thread.__init__(self)
		#global receviedPacketBuffer # Must declare gloabl varibale prior to assigning values
		#global receviedPacketBufferLock
		self.receviedPacketBuffer= deque([], sizeOfBuffer)
		self.receviedPacketBufferLock = threading.Lock()
		print "Initialized Ring Buffer as size of", sizeOfBuffer
		#self.isBufferBusy=0
		self.Packets = n
		self.sizeOfBuffer = sizeOfBuffer
		self.startLogging = startLogging
		self.stopLogging = stopLogging
		
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
					self.receviedPacketBuffer.append(i)
				else:
					print "Lock was not ON"
				
			finally:
				self.receviedPacketBufferLock.release()
				print "Released Buffer is : ", self.receviedPacketBuffer, "\n"
				if i%self.sizeOfBuffer==0:
					for x in xrange(self.sizeOfBuffer):
						val = self.receviedPacketBuffer.popleft()
						self.Packets[x] = val
						#print "Just popped " + str(val) + '\n'
					print 'Packet Buffer: ' + str(self.Packets[:]) + '\n'
					print 'Call Logger'					
					
					if self.startLogging.value == 1 and self.stopLogging.value == 0:
						self.logger()
					else:
						print "Don't need to record data yet"

def UDP(Packets, startLogging, stopLogging):
	UDPlistenThread=listener(10,Packets, startLogging, stopLogging) # sizeOfRingBuffer
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

def startTkinter(PlotPacket,startBool,stopBool):
    root = tkinterGUI(PlotPacket,startBool,stopBool)
    root.master.title("Azog") # Name of current drone, Here it is Azog
    root.mainloop()

def sendSettingPacket(m,f,p,c):
    # m - Mapping modes are : SLAM (0) or VICON pos input (1)
    # f - Flight modes are : Altitude (2) vs Manual Thrust (3) vs POS hold (4)
    # p - Pilot reference mode: global (5), First Person View (6), PPV (7)
    # c - Control mode: User (8) , Auto land (9), Come back home (10), Circle Mode (11) 
    print "New Settings received :",'Mapping Mode',m,'\tFlight Mode :',f,'\tPilot Reference Mode',p,'\tControl Mode',c

def broadcast():
    IPaddr = '8.4.2.1' # IP to send the packets
    portNmbr = 80 # port number of destination

    # Data content of the UDP packet as hex
    packetData = 'f1a525da11f6'.decode('hex')
     
    # initialize a socket
    # SOCK_DGRAM specifies that this is UDP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
     
    try:
        # connect the socket
        s.connect((IPADDR, PORTNUM))
     
        # send the packet
        s.send(packetData)
    except:
        pass
     
    # close the socket
    s.close()

    while 1:

        print "Sent packets"
        sleep(15)

def main():
    #global udpProcess # try to kill updprocess using startTkinter
	lock = Lock()
	n = Array('i', [0]*10, lock = lock) #Packet Storage Array for transfer between processes
	startLogging = Value('i', 0, lock = lock)
	stopLogging = Value('i', 1, lock = lock)
	print 'Start Bool: ' + str(startLogging.value) + '\n'
	print 'Stop Bool: ' + str(stopLogging.value) + '\n'
	udpProcess = Process(name = 'UDP Process', target = UDP, args=(n,startLogging,stopLogging))
	TkinterProcess = Process(name='Tkinter Process', target=startTkinter, args=(n,startLogging,stopLogging))
    # broadcastProcess = Process(name='Broadcasting Process', target=broadcast)
	udpProcess.start()
	TkinterProcess.start()
	udpProcess.join()
	TkinterProcess.join()
	print 'End Packets: ' + str(n[:]) #The final packet after both processes have ended
	
	
	# broadcastProcess.start()

def killDroneMethod():
    print 'this should send a specific MAVlink packet'
    
    # start tkinter stuff

if __name__ == '__main__':
    main()