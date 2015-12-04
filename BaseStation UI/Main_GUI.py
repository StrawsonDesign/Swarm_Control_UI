import Tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
# matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
import tkFont, threading, Queue, multiprocessing, tkMessageBox
from time import strftime, sleep
from collections import deque

# class VideoControlWidget(Frame):
	
	# button_names = ['Record', 'Snapshot', 'Show Depth', 'Camera 1', 'Camera 2']
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
			
class loggingThreadClass(threading.Thread):
	
	def __init__(self, master):
		threading.Thread.__init__(self)
		loggingFrame = tk.Frame(master)
		loggingFrame.grid(row = 7, 
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
		log_recordButtonFrame.grid(row = 5, column = 0, sticky = tk.N + tk.S + tk.W + tk.E)
		log_stopButtonFrame = tk.Frame(loggingFrame)
		log_stopButtonFrame.grid(row = 6, column = 0, sticky = tk.N + tk.S + tk.W + tk.E)
		
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
		
class settingsThreadClass(threading.Thread):
	
	def __init__(self, master):
		threading.Thread.__init__(self)		
		self.settingsFrame = tk.Frame(master)
	def run(self):		
		self.settingsFrame.grid(row = 7, 
								column = 0, 
								rowspan = 1,
								columnspan = 2,
								sticky = tk.S + tk.N + tk.W + tk.E)
		self.settingsFrame.rowconfigure(5, weight = 1)
		self.settingsFrame.rowconfigure(6, weight = 1)
		self.settingsFrame.columnconfigure(0, weight = 1)
		
		set_positionBoxFrame = tk.Frame(self.settingsFrame)
		set_positionBoxFrame.grid(row = 5, sticky = tk.N + tk.S + tk.W + tk.E)
		set_attitudeBoxFrame = tk.Frame(self.settingsFrame)
		set_attitudeBoxFrame.grid(row = 6, sticky = tk.N + tk.S + tk.W + tk.E)
		
		set_iattitude = tk.IntVar()
		set_iposition = tk.IntVar()
		
		set_attitudeCheckButton = tk.Checkbutton(set_attitudeBoxFrame, text = 'Attitude', variable = set_iattitude.get)
		set_positionCheckButton = tk.Checkbutton(set_positionBoxFrame, text = 'Position', variable = set_iposition.get)
		
		set_attitudeCheckButton.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)
		set_positionCheckButton.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)
		
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
		return set_iattitude.get(), set_iposition.get()
# class VideoWidget(Frame):
# class PlotWindow(tk.Frame):
	# def __init__(self, master)
		# tk.Frame.__init__(self,master)
		# plotFrame.grid

class statisticsThreadClass(threading.Thread):
	
	def __init__(self, master):
		threading.Thread.__init__(self)
		statisticsFrame = tk.Frame(master)
		statisticsFrame.grid(row = 1,
								column = 1,
								rowspan = 3,
								columnspan = 1)
		statisticsFrame.rowconfigure(1, weight = 1)
		statisticsFrame.rowconfigure(2, weight = 1)
		statisticsFrame.rowconfigure(3, weight = 1)
		statisticsFrame.rowconfigure(4, weight = 1)
		statisticsFrame.rowconfigure(5, weight = 1)
		statisticsFrame.rowconfigure(6, weight = 1)
		statisticsFrame.columnconfigure(1, weight = 1)
		
		plotFrame = tk.Frame(master)
		plotFrame.grid(row = 2,
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
		fig = plt.figure(figsize = (4,4), dpi = 100)
		self.ax = fig.add_subplot(111)
		# plt.ion()
		plt.xlabel('Time(s)')
		plt.ylabel('Variable Name')
		# plt.show()
		
		canvas = FigureCanvasTkAgg(fig, plotFrame)
		canvas.show()
		canvas.get_tk_widget().pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
		
		velocity_line = plt.plot([],[])[0]
		acceleration_line = plt.plot([],[])[0]
		position_line = plt.plot([],[])[0]
		roll_line = plt.plot([],[])[0]
		pitch_line = plt.plot([],[])[0]
		yaw_line = plt.plot([],[])[0]
		
		velocity_line.set_data([],[])
		acceleration_line.set_data([],[])
		position_line.set_data([],[])
		roll_line.set_data([],[])
		pitch_line.set_data([],[])
		yaw_line.set_data([],[])
		
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
		
		settingsThread = settingsThreadClass(self)
		loggingThread = loggingThreadClass(self)
		statisticsThread = statisticsThreadClass(self)
		
		settingsThread.setDaemon(True)
		loggingThread.setDaemon(True)
		statisticsThread.setDaemon(True)
		
		settingsThread.start()
		loggingThread.start()
		statisticsThread.start()
		
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

def broadcast():
	# while 1:
		# print "Sent packets"
		# sleep (5)
	pass
	
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