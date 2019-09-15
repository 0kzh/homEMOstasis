"""Define the GUI interface."""

from tkinter import Button, Entry, Radiobutton, Tk, Label, LabelFrame, StringVar, N, S, W, E, END
from tkinter.filedialog import askopenfilename
from tkinter.scrolledtext import ScrolledText
from io import BytesIO
import time
import cv2
import requests
import numpy as np
from PIL import Image
from .mpl import ResultImg

class GUIRoot(Tk):
    """The tkinter GUI root class."""

    def __init__(self, thread_cls):
        super().__init__()
        self.window = self
        self.last_request = 0
        self.running = False
        self.thread_cls = thread_cls
        self.img = None
        self.title("HomEMOstasis")

        # our ms azure api key :)
        self.ety_key = "eed879d931a146d1ac9992ce47e71342"
        self.grid()
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(4, weight=1)

        self.vid = VideoCapture()

        # Create LabelFrames
        lf_request = LabelFrame(self, text="Control Panel")
        lf_request.grid(row=0, column=0, columnspan=1,
                        sticky=W+E, padx=5, pady=3)
        lf_request.grid_columnconfigure(0, weight=1)
        lf_console = LabelFrame(self, text="Console")
        lf_console.grid(row=4, column=0, columnspan=1,
                        sticky=N+S+W+E, padx=5, pady=3)
        lf_console.grid_columnconfigure(0, weight=1)
        lf_console.grid_rowconfigure(0, weight=1)
        lf_img = LabelFrame(self, text="Webcam View")
        lf_img.grid(row=0, column=1, rowspan=5, sticky=N+S+W+E)
        lf_img.grid_columnconfigure(0, weight=1)
        lf_img.grid_rowconfigure(0, weight=1)

        self.btn_start = Button(lf_request,
                                  text="Start Analysis",
                                  command=self.start_analysis,
                                  state='normal')
        self.btn_start.grid(sticky = 'nsew', row = 0, column = 0,)

        self.btn_stop = Button(lf_request,
                                  text="Stop Analysis",
                                  command=self.stop_analysis,
                                  state='disabled')
        self.btn_stop.grid(sticky = 'nsew', row = 0, column = 1)

        lf_request.grid_columnconfigure(0, weight=1, uniform="group1")
        lf_request.grid_columnconfigure(1, weight=1, uniform="group1")
        lf_request.grid_rowconfigure(0, weight=1)
        
        # Create Output Console
        self.console = ScrolledText(
            lf_console, state='disable', width=60, bg='gray20', fg='white')
        self.console.grid(sticky=N+S+W+E)

        # Create Output Image
        self.plot = ResultImg(lf_img)
        self.plot.grid(sticky=N+S+W+E)

        self.update()

    def update(self):
        s, self.img = self.vid.get_frame()
        self.img = cv2.imencode('.jpg', self.img)[1].tostring()
        self.plot.imshow(img_decode(self.img))
        elapsed_time = time.time() - self.last_request

        # ensure at least 500 ms between each request
        # let's keep this rate-limited at 2s for now, scale down to 0.5s for demo
        timeout = 0.5
        if self.running and elapsed_time >= timeout:
            self.run_request()
            self.last_request = time.time()
        
        # Run any pending tasks:
        # q.execFromMain()
        self.window.after(1, self.update)

    def change_mode(self):
        """Change the image source mode."""
        if self.var_mode.get() == 'local':
            self.lb_filename.grid(row=0, column=0, columnspan=2)
            self.btn_fileopen.grid(row=0, column=2)
            self.lb_url.grid_forget()
            self.ety_url.grid_forget()
            self.btn_url.grid_forget()
            self.btn_get_cam.grid_forget()
        elif self.var_mode.get() == 'url':
            self.lb_filename.grid_forget()
            self.btn_fileopen.grid_forget()
            self.btn_get_cam.grid_forget()
            self.lb_url.grid(row=0, column=0)
            self.ety_url.grid(row=0, column=1, sticky=W+E, padx=3)
            self.btn_url.grid(row=0, column=2)
        else:
            self.lb_filename.grid_forget()
            self.btn_fileopen.grid_forget()
            self.lb_url.grid_forget()
            self.ety_url.grid_forget()
            self.btn_url.grid_forget()
            self.btn_get_cam.grid(row=0, column=0, columnspan=3)

    def run_request(self):
        """Create the requesting thread to request the result from Emotion API."""
        self.thread_cls(self.ety_key,
                        'cam',
                        self.img,
                        self.plot,
                        self.print_console).start()

    
    def start_analysis(self):
        self.running = True
        self.btn_start['state'] = 'disabled'
        self.btn_stop['state'] = 'normal'

    def stop_analysis(self):
        self.running = False
        self.btn_start['state'] = 'normal'
        self.btn_stop['state'] = 'disabled'

    def print_console(self, input_str):
        """Print the text on the conolse."""
        self.console.config(state='normal')
        self.console.insert(END, "{}\n".format(input_str))
        self.console.config(state='disable')
        self.console.see(END)


class VideoCapture:
    def __init__(self):
        # Open the video source
        self.vid = cv2.VideoCapture(0)
 
        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
 
    def get_frame(self):
         if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                # Return a boolean success flag and the current frame converted to BGR
                return (ret, frame)
            else:
                return (ret, None)
         else:
            return (ret, None)
 
     # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

def img_decode(data):
    """Convert the image codec from OpenCV to matplotlib readable."""
    data8uint = np.fromstring(
        data, np.uint8)  # Convert string to an unsigned int array
    return cv2.cvtColor(cv2.imdecode(data8uint, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
