import Tkinter as tk
import cv2
#import cv
from PIL import ImageTk , Image

width, height = 800, 600
cap = cv2.VideoCapture(0)

root = tk.Tk()
root.bind('<Escape>', lambda e: root.quit())
lmain = tk.Label(root)
lmain.pack()

def show_frame():
    _, frame = cap.read()
    #frame = cv2.flip(frame, 1)
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    lmain.after(10, show_frame)	

show_frame()
root.mainloop()