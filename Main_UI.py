import pandas as pd
import os
from tkinter import *

root = Tk()
root.geometry('1920x1080')


class MainMenu:
    def __init__(self, master):
        FrameBtn = Frame(master, width=10, height=1080, background='red')
        FrameBtn.grid(row=0, column=1, sticky='nsew')

        self.bAddRound = Button(FrameBtn, text='Add Round', height=3, width=20, command=self.test_shot)
        self.bCourses = Button(FrameBtn, text='Course Editor', height=3, width=20, command=self.test_shot)
        self.bTestShot = Button(FrameBtn, text='Test Shot', height=3, width=20, command=self.test_shot)
        self.bStats = Button(FrameBtn, text='Stats', height=3, width=20, command=self.test_shot)

        self.bAddRound.grid(row=1, column=1, pady=5)
        self.bCourses.grid(row=2, column=1, pady=5)
        self.bTestShot.grid(row=3, column=1, pady=5)
        self.bStats.grid(row=4, column=1, pady=5)

        FrameLeft = Frame(master, width=1780, height=1080, background='yellow')
        FrameLeft.grid(row=0, column=0, sticky='nsew')

        master.grid_rowconfigure(0, minsize=200, weight=1)
        master.grid_columnconfigure(0, minsize=200, weight=1)
        master.grid_columnconfigure(1, weight=1)

    def test_shot(self):
        print('i')


MainMenu(root)

root.mainloop()