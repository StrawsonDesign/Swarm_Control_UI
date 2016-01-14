# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 12:43:15 2016

@author: FailingToFocus
"""

import threading # multithreading 
import multiprocessing #multiprocessing
import tkMessageBox # for messageboxes 
import Tkinter as tk
from PIL import ImageTk , Image # for image conversion
import cv2 # OpenCV for video handling
import tkFont # for fonts
from time import strftime,sleep # for sleep
from collections import deque # for ring buffer
import socket # for sending across UDP packets 

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
    def __init__(self,master):
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

    def run(self):
        sleep(2) # remove this eventually
        i=1
        while 1:
            self.updateActiveDrones()
            if (i%60)==0: # print every 30 seconds - thread is alive
                print "Updated Active Drones in the vicinity" 
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
        controlModeRadioButton9=tk.Radiobutton(controlModeFrame, text="Auto Land", variable=c,
                                            value=9,indicatoron=0,
                                            command=lambda : sendSettingPacket(m.get(),f.get(),p.get(),c.get()))
        controlModeRadioButton10=tk.Radiobutton(controlModeFrame, text="Return Home", variable=c,
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
    def __init__(self): 
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
        Log=tk.Frame(self)
        Log.grid()


        videoThread=Video(self)
        otherDrones=otherdrones(self)
        myUAVThread=MyUAV(self,0,0,1,2)
        settingsThread=settingsThreadClass(self)


        # Quit even if some operations are remaining to be complete

        videoThread.setDaemon(True) 
        myUAVThread.setDaemon(True)
        otherDrones.setDaemon(True)
        settingsThread.setDaemon(True)  

        self.createWidgets(Status,'Stats',1,0,2,1)
        #self.createWidgets(Settings,'Settings',3,0,1,1)
        self.createWidgets(Log,'Logging',2,4,2,1)


       
        videoThread.start() # becomes mainthread
        myUAVThread.start() # becomes secondard thread
        otherDrones.start()
        settingsThread.start()
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
        

class listener(threading.Thread):
    def __init__(self,sizeOfBuffer, conn):
        threading.Thread.__init__(self)
        self.conn = conn
        self.conn.send = ([42, None, 'listen'])
        self.conn.close()
        global receviedPacketBuffer # Must declare gloabl varibale prior to assigning values
        global receviedPacketBufferLock
        receviedPacketBuffer= deque([], sizeOfBuffer)
        receviedPacketBufferLock = threading.Lock()
        print "Initialized Ring Buffer as size of", sizeOfBuffer
        #self.isBufferBusy=0  
        
    
    def run(self):
        for i in xrange(500): # replace by reading head
            #sleep(1)
            try:
                if receviedPacketBufferLock.acquire(1):
                    #print "Buffer is : ", receviedPacketBuffer, "\n"
                    receviedPacketBuffer.append(i)                    
                #else:
                    #print "Lock was not ON"
            finally:
                    receviedPacketBufferLock.release()
                    

class logger(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        outfile='testfile.txt'
        self.log_dummy=open(outfile,"w",1) # use a = append mode, buffering set to true
        print "file", outfile, "is opened"
        #child_conn.send(['log'])
        #child_conn.close()
        
    def run(self): 
        tempData=""
        m=0
        while m<100: # change this
            #sleep(0.01)
            if receviedPacketBufferLock.acquire(0):
                try:
                    while(1): # empty the entire list
                    #self.listenerobject.isBufferBusy=1
                        val=receviedPacketBuffer.popleft()
                        data=strftime("%c") + "\t" + str(val) + "\n"
                        tempData=tempData+data
                        # print "Just popped ",val
                except:
                    pass
                finally:
                    receviedPacketBufferLock.release()
                    self.Packet_Received = True

            m += 1   
            #print "M is", m     
            if m%50==0:
                self.log_dummy.write(tempData)
                print "wrote to disk"
                tempData=""
    def Packets(self):
        print 'Checking Packet'
        if self.Packet_Received:
            print 'Returning Data'
            return data

def UDP(Logging_child_conn, Listen_child_conn):
    UDPlistenThread=listener(10, Listen_child_conn) # sizeOfRingBuffer
    UDPlistenThread.setDaemon(True)

    UDPlogThread=logger()
    UDPlogThread.setDaemon(True)
    print('UDP')
    
    UDPlistenThread.start()
    #Listen_child_conn.send([84, None, 'Listen', receviedPacketBuffer])
    #Listen_child_conn.close()
    UDPlogThread.start()
    print(UDPlogThread)
    print(UDPlistenThread)
    
    #Logging_child_conn.send([42, None, 'Logging',receviedPacketBuffer])
    #Logging_child_conn.close()
    
    UDPlistenThread.join()
    UDPlogThread.join()

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

def startTkinter():
    root = tkinterGUI()
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
    Logging_parent_conn, Logging_child_conn = multiprocessing.Pipe()
    Listen_parent_conn, Listen_child_conn = multiprocessing.Pipe()
    udpProcess = multiprocessing.Process(name='UDP Process', target=UDP, args = (Logging_child_conn, Listen_child_conn,))
    #TkinterProcess = multiprocessing.Process(name='Tkinter Process', target=startTkinter)
    # broadcastProcess=multiprocessing.Process(name='Broadcasting Process', target=broadcast)
    udpProcess.start()
    #TkinterProcess.start()
    # broadcastProcess.start()
    print(Logging_parent_conn.recv())
    print(Listen_parent_conn.recv())

def killDroneMethod():
    print 'this should send a specific MAVlink packet'
    
    # start tkinter stuff

if __name__ == '__main__':
    main()