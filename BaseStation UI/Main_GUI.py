import Tkinter as tk
import tkFont, threading, Queue, multiprocessing, tkMessageBox
from time import strftime, sleep

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
			
class logging(tk.Frame):
	
	def __init__(self, parent,frame,row,col,row_span,col_span):
		tk.Frame.__init__(self,parent)	
		self.checkbox_names = ['Attitude', 'Position', 'Velocity', 'Battery']
		self.button_names = ['Record', 'Stop']
		self.vars = []
		counter = 0
		
		for self.checkbox_name in self.checkbox_names:
			var = tk.IntVar()
			counter += 1
			loggingCheckbutton = tk.Checkbutton(self, text = self.checkbox_name, variable = var)
			loggingCheckbutton.grid(row = row + counter, column = col, rowspan = row_span, columnspan = col_span, sticky=tk.N+tk.S+tk.E+tk.W)
			loggingCheckbutton.rowconfigure(counter, weight = 1)
		
		self.vars = []	
		counter = 0	
		for self.button_name in self.button_names:
			var = tk.IntVar()
			counter += 1
			
			if self.button_name in ('Record'):
				loggingButton = tk.Button(self, text = self.button_name, command = self.record_data)
			elif self.button_name in ('Stop'):
				loggingButton = tk.Button(self, text = self.button_name, command = self.stop_recording)
				
			loggingButton.columnconfigure(col + counter, weight = 1)
			loggingButton.rowconfigure(row + counter, weight = 1)
			loggingButton.grid(row = row + counter, column = col + counter, rowspan = row_span, columnspan = col_span, sticky=tk.N+tk.S+tk.E+tk.W)
			loggingButton.columnconfigure(counter, weight = 1)
	
	def record_data(self):
		
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
	
	def stop_recording(self):
	
			self.logfile.close()
			# print file + "is not open"
	
	def run(self):
		pass
	
	
	# self.rowconfigure(row, weight = 1)
	# self.columnconfigure(col, weight = 1)
		
class settings(tk.Frame):
	
	def __init__(self, parent,frame,row,col,row_span,col_span):
		tk.Frame.__init__(self,parent)
		self.names = ['Position', 'Attitude']
		self.vars = []
		counter = 0
		
		for self.name in self.names:
			var = tk.IntVar()
			counter += 1
			
			settings = tk.Checkbutton(self, text = self.name, variable = var)
			settings.rowconfigure(row + counter, weight = 1)
			settings.columnconfigure(col + counter, weight = 1)			
			settings.grid(row = row + counter, column = col, rowspan = row_span, columnspan = col_span, sticky=tk.N+tk.S+tk.E+tk.W)
			
# class VideoWidget(Frame):


class statistics(tk.Frame):
	
	def __init__(self, parent,frame,row,col,row_span,col_span):
		tk.Frame.__init__(self,parent)
		self.names = ['Velocity', 'Acceleration', 'Position', 'Roll', 'Pitch', 'Yaw']
		self.vars = []
		counter = 0
		
		for self.name in self.names:
			var = tk.IntVar()
			counter += 1
			statistics = tk.Checkbutton(self, text = self.name, variable = var)
			statistics.rowconfigure(row + counter, weight = 1)
			statistics.columnconfigure(col + counter, weight = 1)
			statistics.grid(row = row + counter, column = col, rowspan = row_span, columnspan = col_span, sticky=tk.N+tk.S+tk.E+tk.W)
			
	def plot_data():
		pass
		
			
	# class YourUAVIDWidget(Frame):


	# class ScrollingUAVIDWidget(Frame):

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
		self.columnconfigure(0, weight=1)
		self.columnconfigure(1, weight=1)
		self.columnconfigure(2, weight=1)
		self.columnconfigure(3, weight=1)
		
        # Set up the GUI
		# console = tk.Button(self, text='Done', command=endCommand)
		# console.grid(row = 5, column = 0, rowspan = 3, columnspan = 2)
		
		settingsThread = settings(self,'Settings',3,0,1,1)
		settingsThread.grid(row = 3, column = 0, rowspan = 1, columnspan = 1)
		
		statisticsThread = statistics(self,'Statistics',1,0,1,1)
		statisticsThread.grid(row = 1, column = 0, rowspan = 2, columnspan = 1)
		
		loggingThread = logging(self, 'Logging',2,3,2,1)
		loggingThread.grid(row = 2, column = 3, rowspan = 2, columnspan = 1)
		
        # Add more GUI stuff here
				
class ThreadedTask:
	"""
	Launch the main part of the GUI and the worker thread. periodicCall and
	endApplication could reside in the GUI part, but putting them here
	means that you have all the thread controls in a single place.
	"""
	def __init__(self, master):
		"""
		Start the GUI and the asynchronous threads. We are in the main
		(original) thread of the application, which will later be used by
		the GUI. We spawn a new thread for the worker.
		"""
		self.master = master

		# Set up the GUI part
		self.gui = Application(master)

		# Set up the thread to do asynchronous I/O
		# More can be made if necessary
		self.running = 1
		self.thread1 = threading.Thread(target=self.workerThread1)
		self.thread1.start()

		# Start the periodic call in the GUI to check if the queue contains
		# anything
		self.periodicCall()
	
	def periodicCall(self):
		"""
		Check every 100 ms if there is something new in the queue.
		"""
		self.gui.processIncoming()

		if not self.running:
			# This is the brutal stop of the system. You may want to do
			# some cleanup before actually shutting it down.
			import sys
			sys.exit(1)
		self.master.after(100, self.periodicCall)
		
	def workerThread1(self):
		"""
		This is where we handle the asynchronous I/O. For example, it may be
		a 'select()'.
		One important thing to remember is that the thread has to yield
		control.
		"""
		while self.running:
			# To simulate asynchronous I/O, we create a random number at
			# random intervals. Replace the following 2 lines with the real
			# thing.
			time.sleep(rand.random() * 0.3)
			msg = rand.random()
			self.queue.put(msg)

	def endApplication(self):
		self.running = 0
		
	def run(self):
		self.queue.put("Task Finished")

	
def main():
	listeningThread=listener(6)
	listeningThread.setDaemon(True) # exit UI even if some listening is going on
	listeningThread.start()


	root = Application()
	root.master.title("GUI")
	# GUI = ThreadedTask(root)
	root.mainloop()
			
if __name__ == '__main__':
	main()
	
