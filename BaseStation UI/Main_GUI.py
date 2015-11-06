from Tkinter import *
import tkFont, threading, Queue, time
	
# class VideoControlWidget(Frame):
	
	# button_names = ['Record', 'Snapshot', 'Show Depth', 'Camera 1', 'Camera 2']

class LoggingWidget(Frame):
	
	def __init__(self, parent,frame,row,col,row_span,col_span):
		Frame.__init__(self,parent)
		self.checkbox_names = ['Attitude', 'Position', 'Velocity', 'Battery']
		self.button_names = ['Record', 'Stop']
		self.vars = []
		counter = 0
		
		for self.checkbox_name in self.checkbox_names:
			var = IntVar()
			counter += 1
			logging = Checkbutton(self, text = self.checkbox_name, variable = var)
			logging.grid(row = row + counter, column = col, rowspan = row_span, columnspan = col_span, sticky = W)
		
		for self.button_name in self.button_names:
			var = IntVar()
			counter += 1
			logging = Button(self, text = self.button_name, command = self.quit)
			logging.grid(row = row + counter, column = col + counter, rowspan = row_span, columnspan = col_span, sticky = W)
		
		self.rowconfigure(row, weight = 1)
		self.columnconfigure(col, weight = 1)
	
	def process_queue(self):
		try:
			msg = self.queue.get(0)
			print msg
			
		except Queue.Empty:
			self.parent.after(100, self.process_queue)
		
class SettingsWidget(Frame):
	
	def __init__(self, parent,frame,row,col,row_span,col_span):
		Frame.__init__(self,parent)
		self.names = ['Position', 'Attitude']
		self.vars = []
		counter = 0
		
		for self.name in self.names:
			var = IntVar()
			counter += 1
			settings = Checkbutton(self, text = self.name, variable = var)
			settings.grid(row = row + counter, column = col, rowspan = row_span, columnspan = col_span, sticky = W)
		
		self.rowconfigure(row, weight = 1)
		self.columnconfigure(col, weight = 1)
	
	def process_queue(self):
		try:
			msg = self.queue.get(0)
			print msg
			
		except Queue.Empty:
			self.parent.after(100, self.process_queue)
			
# class VideoWidget(Frame):


class StatisticsWidget(Frame):
	
	def __init__(self, parent,frame,row,col,row_span,col_span):
		Frame.__init__(self,parent)
		self.names = ['Velocity', 'Acceleration', 'Position', 'Roll', 'Pitch', 'Yaw']
		self.vars = []
		counter = 0
		
		for self.name in self.names:
			var = IntVar()
			counter += 1
			statistics = Checkbutton(self, text = self.name, variable = var)
			statistics.grid(row = row + counter, column = col, rowspan = row_span, columnspan = col_span, sticky = W)
		
		self.rowconfigure(row, weight = 1)
		self.columnconfigure(col, weight = 1)
		
	def process_queue(self):
		try:
			msg = self.queue.get(0)
			print msg
			
		except Queue.Empty:
			self.parent.after(100, self.process_queue)
			
# class YourUAVIDWidget(Frame):


# class ScrollingUAVIDWidget(Frame):

class GuiPart:
    def __init__(self, master, queue, endCommand):
		self.queue = queue
        # Set up the GUI
		console = Button(master, text='Done', command=endCommand)
		console.grid(row = 5, column = 0, rowspan = 3, columnspan = 2)
		settings = SettingsWidget(master,'Settings',3,0,1,1)
		settings.grid(row = 3, column = 0, rowspan = 1, columnspan = 1)
		statistics = StatisticsWidget(master,'Statistics',1,0,1,1)
		statistics.grid(row = 1, column = 0, rowspan = 2, columnspan = 1)
		logging = LoggingWidget(master, 'Logging',2,3,2,1)
		logging.grid(row = 2, column = 3, rowspan = 2, columnspan = 1)
        # Add more GUI stuff here

    def processIncoming(self):
		"""
		Handle all the messages currently in the queue (if any).
		"""
		while self.queue.qsize():
			try:
				msg = self.queue.get(0)
				# Check contents of message and do what it says
				# As a test, we simply print it
				print msg
			except Queue.Empty:
				pass
				
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

		# Create the queue
		self.queue = Queue.Queue()

		# Set up the GUI part
		self.gui = GuiPart(master, self.queue, self.endApplication)

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
	root = Tk()
	root.title("GUI")
	GUI = ThreadedTask(root)
	root.mainloop()
			
if __name__ == '__main__':
	main()
	
