from tkinter import *
import tkinter as tk

#class MetaA(type):


class A(object):
    def __init__(self,master):
        self.Label = tk.Label(master,text='A')
        self.Label.grid(row=0,column=0)
        self.ButtonA = tk.Button(master,text='A',command=self.__ButtonA,width=10)
        self.ButtonA.grid(row=1,column=0)

    def buttonA_press(self):
        print('Apple')
        self.ButtonA['text']='C'

    def __ButtonA(self):
        print('Apple')
        self.b.buttonB_press()
