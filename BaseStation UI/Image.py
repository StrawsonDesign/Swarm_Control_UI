from PIL import ImageTk,Image
from Tkinter import *

class Application(Frame):              
    def __init__(self, master=None):
    	Frame.__init__(self, master)
        self.grid()
        img = ImageTk.PhotoImage(file='/home/kishan/Desktop/lena.png')
        panel = Label(self)
        panel.grid()
        panel.config(image=img, bg='red')
        panel.image=img

app = Application()                       
app.master.title('Sample application')
app.mainloop()
