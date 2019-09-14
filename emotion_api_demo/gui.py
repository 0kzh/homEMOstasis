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
        self.thread_cls = thread_cls
        self.img = None
        self.title("Emotion API")
        self.grid()
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(4, weight=1)

        # Create LabelFrames
        lf_key = LabelFrame(self, text="Emotion API Key")
        lf_key.grid(row=0, column=0, columnspan=1, sticky=W+E, padx=5, pady=3)
        lf_key.grid_columnconfigure(0, weight=1)
        lf_mode = LabelFrame(self, text="Mode")
        lf_mode.grid(row=1, column=0, columnspan=1, sticky=W+E, padx=5, pady=3)
        for i in range(3):
            lf_mode.grid_columnconfigure(i, weight=1)
        lf_source = LabelFrame(self, text="Image Source", height=50)
        lf_source.grid(row=2, column=0, columnspan=1,
                       sticky=W+E, padx=5, pady=3)
        lf_source.rowconfigure(0, weight=1)
        lf_source.grid_propagate(False)
        lf_source.columnconfigure(0, weight=1)
        lf_source.columnconfigure(1, weight=5)
        lf_source.columnconfigure(2, weight=1)
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

        # Create Input Fields
        self.ety_key = Entry(lf_key)
        self.ety_key.insert(END, "eed879d931a146d1ac9992ce47e71342")
        self.ety_key.grid(sticky=W+E, padx=3)
        self.var_mode = StringVar()
        Radiobutton(lf_mode,
                    text="Local Image",
                    variable=self.var_mode,
                    value='local',
                    command=self.change_mode).grid(row=1, column=0)
        Radiobutton(lf_mode,
                    text="URL Image",
                    variable=self.var_mode,
                    value='url',
                    command=self.change_mode).grid(row=1, column=1)
        Radiobutton(lf_mode,
                    text="Camera",
                    variable=self.var_mode,
                    value='cam',
                    command=self.change_mode).grid(row=1, column=2)
        # Local Image Source
        self.lb_filename = Label(lf_source, text="..")
        self.btn_fileopen = Button(
            lf_source, text="Open..", command=self.get_local_img)
        # URL Image Source
        self.lb_url = Label(lf_source, text="URL")
        self.ety_url = Entry(lf_source)
        self.ety_url.insert(END, "https://i.imgflip.com/qiev6.jpg")
        self.btn_url = Button(lf_source, text="Get Image",
                              command=self.get_url_img)
        # Camera Image Source
        self.btn_get_cam = Button(
            lf_source, text="Get the Camera Image", command=self.get_cam_img)
        # set default mode: local raw image
        self.var_mode.set('local')
        self.change_mode()
        # request btn
        self.btn_request = Button(lf_request,
                                  text="Request Result",
                                  command=self.run_request,
                                  state='disable')
        self.btn_request.grid(sticky=W+E)

        # Create Output Console
        self.console = ScrolledText(
            lf_console, state='disable', width=60, bg='gray20', fg='white')
        self.console.grid(sticky=N+S+W+E)

        # Create Output Image
        self.plot = ResultImg(lf_img)
        self.plot.grid(sticky=N+S+W+E)

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
        cam = cv2.VideoCapture(0)   # 0 -> index of camera
        s, self.img = cam.read()
        self.img = cv2.imencode('.jpg', self.img)[1].tostring()
        if s:    # frame captured without any errors
            self.print_console("Camera image captured.")
            self.plot.imshow(img_decode(self.img))
            self.btn_request.config(state='normal')

    def print_console(self, input_str):
        """Print the text on the conolse."""
        self.console.config(state='normal')
        self.console.insert(END, "{}\n".format(input_str))
        self.console.config(state='disable')
        self.console.see(END)


def img_decode(data):
    """Convert the image codec from OpenCV to matplotlib readable."""
    data8uint = np.fromstring(
        data, np.uint8)  # Convert string to an unsigned int array
    return cv2.cvtColor(cv2.imdecode(data8uint, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
