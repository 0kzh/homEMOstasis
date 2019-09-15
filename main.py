"""The simple GUI application for Microsoft Emotion API as
   an example for final project in NCU CSIE Neural Network, Taiwan (2017).
   Author: Sean Wu (104502551)
"""

from core.gui import GUIRoot
from core.request_emotion import RequestEmotion
from tkinter import Tk

def main():
    """The main function."""
    gui_root = GUIRoot(RequestEmotion)
    gui_root.mainloop()

if __name__ == '__main__':
    main()
