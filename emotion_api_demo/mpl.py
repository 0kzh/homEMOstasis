"""Define the matplotlib to show the result image, which is embedded in tkinter GUI."""

from tkinter import Frame, BOTH
import operator
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle


class ResultImg(Frame):
    """The class creating result image."""

    def __init__(self, master=None):
        super().__init__(master)
        fig = Figure(figsize=(6, 6))
        self.canvas = FigureCanvasTkAgg(fig, self)
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        self.ax = fig.add_subplot(1, 1, 1)  # the main axis
        self.rectangles = []

    def imshow(self, img):
        """Show the image on the main axis."""
        self.ax.clear()
        self.ax.imshow(img)
        self.canvas.draw()

    def draw_labels(self, result):
        """Draw the face rectangle and emotion label on the mpl ax."""
        for rect in self.rectangles:
            try:
                rect.remove()
            except ValueError:
                pass
        self.rectangles.clear()
        for curr_face in result:
            face_rect = curr_face['faceRectangle']
            curr_emotion = max(
                curr_face['scores'].items(), key=operator.itemgetter(1))[0]
            self.rectangles.append(self.ax.add_patch(Rectangle((face_rect['left'],
                                                                face_rect['top']),
                                                               face_rect['width'],
                                                               face_rect['height'],
                                                               fill=False,
                                                               lw=2,
                                                               color='orange')))
            self.ax.annotate(curr_emotion,
                             xy=(face_rect['left'], face_rect['top'] - 15),
                             color='black',
                             bbox=dict(boxstyle="round", fc="w", lw=0, alpha=0.6))
        self.canvas.draw()
