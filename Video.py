#!/usr/bin/env python     
import Tkinter as tk
import cv2

class Application(tk.Frame):              
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.grid(sticky=tk.N+tk.S+tk.E+tk.W) #The argument sticky=tk.N+tk.S+tk.E+tk.aW to self.grid() is necessary so that the Application widget will expand to fill its cell of the top-level window's grid
        

        top=self.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)


        Vid_frame=tk.Frame(self, bg='red')
        Vid_frame.grid(sticky=tk.N+tk.S+tk.E+tk.W)

        # for camera feed vid = cv2.VideoCapture(0)
        vid=cv2.VideoCapture('/home/kishan/Desktop/Python/Minion.webm') # read the video from the file
        nFrames = int(vid.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)) # get no of frames in the video 
        fps = vid.get(cv2.cv.CV_CAP_PROP_FPS) 
        waitPerFrameMillisec = int (1000/fps) # cv2 needs to wait this much before advancing to next frame 

        print 'Num. Frames = ', nFrames
        print 'Frame Rate = ', fps, ' frames per sec'

        while(True):
            frameImg = vid.read()[1] # extracting image from frame
            #colorBGR= cv2.cvtColor(frameImg,cv2.COLOR_BGR2BGR)
            cv2.imshow('image',frameImg) # display image
            if cv2.waitKey(waitPerFrameMillisec) & 0xFF == ord('q'):
                break
            # wait some milliseconds before advancing to next frame
        

        vid.release() # freeing up mmemory 
        fps1 = vid.get(cv2.cv.CV_CAP_PROP_FPS) 
        cv2.destroyAllWindows() # kill all windows





app = Application()                       
app.master.title('Sample application')
app.mainloop()