import threading
import tkMessageBox # for messageboxes 
import Tkinter as tk
from PIL import ImageTk , Image
import cv2 # OpenCV for video handling
import tkFont # for fonts
from time import strftime,sleep


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
        while i<10:
            print 'i is =',i
            # print '# active threads in MyUAV loop are',threading.enumerate()
            sleep(2)
            i+= 1



class Video(threading.Thread):
    def __init__(self,master):
        threading.Thread.__init__(self)
        self.vidFrame=tk.Frame(master)
        self.vidFrame.grid(row=1,
                      column=1,
                      rowspan=3,
                      columnspan=2,
                      sticky=tk.S+tk.N+tk.E+tk.W)
        self.vidFrame.config(width=640,height=480)
        self.vidLabel=tk.Label(master)
        self.vidLabel.grid(row=1,
                      column=1,
                      rowspan=3,
                      columnspan=2,
                      sticky=tk.S+tk.N+tk.E+tk.W)

        #self.vidLabel.pack(fill=tk.BOTH,
        #                            expand=1)

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
                      column=3,
                      rowspan=1,
                      columnspan=1,
                      sticky=tk.N+tk.S+tk.E+tk.W)
        recordButton = tk.Button(vidControl, 
                                        text="Record", 
                                        bd = 1,
                                        bg= "Red",
                                        command=self.recordVideo)
        recordButton.pack(fill=tk.BOTH,
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
        self.takeScreenShot=0 # Intialize screenshot toggle to be zero
        self.cameraChannelOnVideo=0 # Intialize Camera Channel to default to zero
        self.vid_cap = cv2.VideoCapture(self.cameraChannelOnVideo) # Assign channel to video capture
        self.showVideo(self.vidLabel,self.vidFrame)

    def recordVideo(self):
        try:
            w=int(self.vid_cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH ))
            h=int(self.vid_cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT ))
            fourcc = cv2.cv.CV_FOURCC('M','P','4','A')
            outputFPS = 20
            self.videoWriter = cv2.VideoWriter("output.avi", fourcc, outputFPS, (w, h))
            print "I was here"
            if self.videoWriter.isOpened():
                self.videoWriter.write(frame)
                print ('Saving Video Frames')

        except expection as e:
            print e

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
    def __init__(self): #,master= None):
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
        Team=tk.Frame(self)
        Team.grid()
        Settings=tk.Frame(self)
        Settings.grid()
#        Vid_Cntrl=tk.Frame(self)
#        Vid_Cntrl.grid()
        Log=tk.Frame(self)
        Log.grid()
        Video_Button=tk.Frame(self)
        Video_Button.grid()


        myUAVThread=MyUAV(self,0,0,1,2)
        videoThread=Video(self)
        myUAVThread.setDaemon(True)
        self.createWidgets(Team,'Team UAVs',0,2,1,2)
        self.createWidgets(Status,'Stats',1,0,2,1)
        self.createWidgets(Settings,'Settings',3,0,1,1)
        self.createWidgets(Log,'Logging',2,3,2,1)


        print '# active threads are ',threading.enumerate()
        videoThread.start() # becomes mainthread
        myUAVThread.start() # becomes secondard thread
        print '# active threads are ',threading.enumerate()

    


    def createWidgets(self,frame,txt,r,c,rspan,cspan):
        # for testing

        self.qt = tk.Button(self, text=txt,command=self.quit)
        self.qt.grid(row=r, column=c,rowspan=rspan,columnspan=cspan,
        sticky=tk.N+tk.S+tk.W+tk.E) #stretch the widget both horizontally and 

    def OnButton(self):
        # for testing only
        result=tkMessageBox.askokcancel(title="File already exists", message="File already exists. Overwrite?")
        if result is True:
            print "User clicked Ok"
        else:
            print "User clicked Cancel"

def main():
    root = Application()
    root.master.title("Base Station")
    root.mainloop()
            
if __name__ == '__main__':
    main()
    