from tkinter import *
import tkinter as tk

class B(object):
    def __init__(self,master):
        self.Label = tk.Label(master,text='B')
        self.Label.grid(row=0,column=1)
        self.ButtonB = tk.Button(master,text='B',command=self.__ButtonB,width=10)
        self.ButtonB.grid(row=1,column=1)

    def buttonB_press(self):
        print('Bob')
        self.ButtonB['text']='D'

    def __ButtonB(self):


