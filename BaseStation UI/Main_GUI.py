from Tkinter import *
import tkFont, threading, Queue
	
# class VideoControlWidget(Frame):
	
	# button_names = ['Record', 'Snapshot', 'Show Depth', 'Camera 1', 'Camera 2']

# class LoggingWidget(Frame):
	
	# checkbox_names = ['Attitude', 'Position', 'Velocity', 'Battery']
	# button_names = ['Record', 'Stop']
	
	# def ButtonWidget(self):
		
		
class SettingsWidget(Frame):
	
	def __init__(self, parent,frame,row,col,row_span,col_span):
		Frame.__init__(self,parent)
		self.names = ['Position', 'Attitude']
		self.vars = []
		counter = 0
		self.queque = Queue.Queue()
		ThreadedTask(self.queque).start()
		self.parent.after(100, self.process_queue)
		
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
		self.queque = Queue.Queue()
		ThreadedTask(self.queque).start()
		self.parent.after(100, self.process_queue)
		
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
			
# class YourUAVIDWidget(Frame):


# class ScrollingUAVIDWidget(Frame):

class ThreadedTask(threading.Thread):

	def __init__(self, queque)
		threading.Thread.__init__(self)
		self.queue = queque
		
	def run(self)
		self.queue.put("Task Finished")

	
def main():
	
	root = Tk()
	root.title("GUI")
	settings = SettingsWidget(root,'Settings',3,0,1,1)
	settings.grid(row = 3, column = 0, rowspan = 1, columnspan = 1)
	statistics = StatisticsWidget(root,'Statistics',1,0,1,1)
	statistics.grid(row = 1, column = 0, rowspan = 2, columnspan = 1)
	root.mainloop()
			
if __name__ == '__main__':
	main()
	
