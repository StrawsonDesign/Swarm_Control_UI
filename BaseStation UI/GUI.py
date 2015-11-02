import Tkinter as tk
from PIL import ImageTk , Image
import cv2 # OpenCV for video handling
import tkFont # for fonts
from time import sleep


class Application(tk.Frame):              
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.grid(sticky=tk.N+tk.S+tk.E+tk.W) #The argument sticky=tk.N+tk.S+tk.E+tk.aW to self.grid() is necessary so that the Application widget will expand to fill its cell of the top-level window's grid
        # make top level of the application strectchable and space filling 
        top=self.winfo_toplevel() 
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)
        Status=tk.Frame(self)
        Status.grid()
        MyUAV=tk.Frame(self)
        MyUAV.grid()
        Team=tk.Frame(self)
        Team.grid()
        Settings=tk.Frame(self)
        Settings.grid()
        Vid_Cntrl=tk.Frame(self)
        Vid_Cntrl.grid()
        Log=tk.Frame(self)
        Log.grid()
        Video_Button=tk.Frame(self)
        Video_Button.grid()

        self.createWidgets(MyUAV,'My UAV',0,0,1,2)
        self.createWidgets(Team,'Team UAVs',0,2,1,2)
        self.createWidgets(Status,'Stats',1,0,2,1)
        self.createWidgets(Settings,'Settings',3,0,1,1)
        self.createWidgets(Vid_Cntrl,'Video Control',1,3,1,1)
        self.createWidgets(Log,'Logging',2,3,2,1)
        self.createWidgets(Video_Button,'Video',2,3,2,1) 
        


        vidLabel=tk.Label(self)
        vidLabel.grid(row=1,column=1,rowspan=3,columnspan=2, sticky=tk.N+tk.S+tk.E+tk.W)
        vid_cap = cv2.VideoCapture(0)
        self.showVideo(vid_cap,vidLabel)

    
    def showVideo(self,vid_cap,vidLabel):
        _, frame = vid_cap.read()
        frame = cv2.flip(frame, 1) # flips the video feed
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        vidLabel.imgtk = imgtk
        vidLabel.configure(image=imgtk)
        vidLabel.after(10, self.showVideo(vid_cap,vidLabel)) # calls the method after 


    def createWidgets(self,frame,txt,r,c,rspan,cspan):

        self.rowconfigure(r, weight=1)           
        self.columnconfigure(c, weight=1)
        self.qt = tk.Button(self, text=txt,command=self.quit)
        self.qt.grid(row=r, column=c,rowspan=rspan,columnspan=cspan,
        sticky=tk.N+tk.S+tk.W+tk.E) #stretch the widget both horizontally and 
                                # vertically to fill the cell


app = Application()                       
app.master.title('Sample application')
app.mainloop()