"""Define the GUI interface."""

from tkinter import Button, Entry, Radiobutton, Tk, Label, LabelFrame, StringVar, N, S, W, E, END
from tkinter.filedialog import askopenfilename
from tkinter.scrolledtext import ScrolledText
from io import BytesIO
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
        self.thread_cls = thread_cls
        self.img = None
        self.title("Emotion API")
        self.grid()
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(4, weight=1)

        self.vid = VideoCapture()

        # Create LabelFrames
        lf_request = LabelFrame(self, text="Request Result")
        lf_request.grid(row=3, column=0, columnspan=1,
                        sticky=W+E, padx=5, pady=3)
        lf_request.grid_columnconfigure(0, weight=1)
        lf_console = LabelFrame(self, text="Console")
        lf_console.grid(row=4, column=0, columnspan=1,
                        sticky=N+S+W+E, padx=5, pady=3)
        lf_console.grid_columnconfigure(0, weight=1)
        lf_console.grid_rowconfigure(0, weight=1)
        lf_img = LabelFrame(self, text="Output Image")
        lf_img.grid(row=0, column=1, rowspan=5, sticky=N+S+W+E)
        lf_img.grid_columnconfigure(0, weight=1)
        lf_img.grid_rowconfigure(0, weight=1)
        
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

        self.window.after(10, self.update)

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
        source = self.ety_url.get() if self.var_mode.get() == 'url' else self.img
        self.thread_cls(self.ety_key.get(),
                        self.var_mode.get(),
                        source,
                        self.plot,
                        self.print_console).start()

    def get_local_img(self):
        """Open the dialog let user to choose test file and get the test data."""
        max_name_len = 20
        filename = askopenfilename(filetypes=(("JPEG", "*.jpg"),
                                              ("PNG", "*.png"),
                                              ("All Files", "*.*")),
                                   title="Choose an Image")
        if filename:
            with open(filename, 'rb') as f:
                self.img = f.read()
            self.plot.imshow(img_decode(self.img))
            self.print_console("Open a local raw image file.")
            self.btn_request.config(state='normal')
            if len(filename) > max_name_len:
                self.lb_filename.config(text=".."+filename[-max_name_len:])
            else:
                self.lb_filename.config(text=filename)

    def get_url_img(self):
        """Get the image from the given URL."""
        try:
            self.plot.imshow(Image.open(
                BytesIO(requests.get(self.ety_url.get()).content)))
        except Exception as e:
            self.print_console(e.args)
        else:
            self.print_console("Open a online image from URL.")
            self.btn_request.config(state='normal')

    def get_cam_img(self):
        """Get the image from the laptop camera."""
        # cam = cv2.VideoCapture(0)   # 0 -> index of camera
        # while(True):
        #     s, self.img = cam.read()
        #     self.plot.imshow(img_decode(self.img))
            # cv2.imshow('frame', )
            # self.img = cv2.imencode('.jpg', self.img)[1].tostring()
            # if s:    # frame captured without any errors
            #     self.print_console("Camera image captured.")
            #     self.btn_request.config(state='normal')

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
