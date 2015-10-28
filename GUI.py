import Tkinter as tk
from PIL import ImageTk , Image
import cv2 # OpenCV for video handling
import tkFont # for fonts


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

        self.createWidgets(MyUAV,'My UAV',0,0,1,2)
        self.createWidgets(Team,'Team UAVs',0,2,1,2)
        self.createWidgets(Status,'Stats',1,0,2,1)
        self.createWidgets(Settings,'Settings',3,0,1,1)
        self.createWidgets(Vid_Cntrl,'Video Control',1,3,1,1)
        self.createWidgets(Log,'Logging',2,3,2,1) 
        self.createVideo()

    def createVideo(self):
        #define new frame
        Vid_frame=tk.Frame(self, bg='red')
        Vid_frame.grid(row=1,column=1,rowspan=3,columnspan=2, sticky=tk.N+tk.S+tk.E+tk.W)
        # for camera feed vid = cv2.VideoCapture(0)
        
        vid=cv2.VideoCapture('/home/kishan/Desktop/Python/Timer.mp4') # read the video from the file
        nFrames = int(vid.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)) # get no of frames in the video 
        fps = vid.get(cv2.cv.CV_CAP_PROP_FPS) 
        waitPerFrameMillisec = int (1000/fps) # cv2 needs to wait this much before advancing to next frame 

        print 'Frame Rate = ', fps, ' frames per sec'
        
''' Convert to Label here to display images '''


        while(True):
            frameImg = vid.read()[1] # extracting image from frame
            cv2image= cv2.cvtColor(frameImg,cv2.COLOR_BGR2RGBA)
            # cv2.imshow('image',frameImg) # display image using openCV
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            Vid_frame.imgtk = imgtk
            Vid_frame.configure(image=imgtk)
            Vid_frame.after(10, show_frame)
            if cv2.waitKey(waitPerFrameMillisec) & 0xFF == ord('q'):
                break
            # wait some milliseconds before advancing to next frame

        vid.release() # freeing up mmemory 
        #cv2.destroyAllWindows() # kill all windows
        

    def createWidgets(self,frame,txt,r,c,rspan,cspan):

        self.rowconfigure(r, weight=1)           
        self.columnconfigure(c, weight=1)
        self.qt = tk.Button(self, text=txt,command=frame.quit)
        self.qt.grid(row=r, column=c,rowspan=rspan,columnspan=cspan,
        sticky=tk.N+tk.S+tk.W+tk.E) #stretch the widget both horizontally and 
                                # vertically to fill the cell


app = Application()                       
app.master.title('Sample application')
app.mainloop()