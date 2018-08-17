#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Standard Libraries ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import numpy as np
import os
import math
import matplotlib.backends.tkagg as tkagg
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib.cm as cm
from tkinter import *
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk,ImageOps,ImageDraw,ImageFont
from array import array
from io import BytesIO
from matplotlib.mathtext import math_to_image
from matplotlib.font_manager import FontProperties
from configuration import *
from io import *
import TkInfoPanel
import TkMenu

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Classes ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class canvas(object):
    """This class creates the main widget, the menu and the tool bars"""

    #class variables
    """the initialization method for this class"""
    def __init__(self,master,Defaults):

        #instance variables
        self.VS,self.HS=int(Defaults['vertical_shift']),int(Defaults['horizontal_shift'])
        self.ActionMode = StringVar()
        self.ActionMode.set("N")
        self.image_crop=[1200+self.VS,2650+self.VS,500+self.HS,3100+self.HS]
        self.Ctr_X,self.Ctr_Y=0,0
        self.Mouse_X,self.Mouse_Y=0,0
        self.scalehisto = array('f')
        self.scalehisto.append(1)
        self.master = ttk.Frame(master,relief=FLAT)

        '''Initialize the canvas widget with two scrollbars'''
        # Vertical and horizontal scrollbars for canvas
        vbar = ttk.Scrollbar(self.master, orient='vertical')
        hbar = ttk.Scrollbar(self.master, orient='horizontal')
        vbar.grid(row=0, column=1, sticky='ns')
        hbar.grid(row=1, column=0, sticky='we')
        # Create canvas and put image on it
        self.MainCanvas = tk.Canvas(self.master, cursor = 'crosshair',relief=RIDGE, highlightthickness=0,xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.MainCanvas.grid(row=0, column=0, sticky='nswe')
        self.MainCanvas.update()  # wait till canvas is created
        vbar.configure(command=self.__scroll_y__)  # bind scrollbars to the canvas
        hbar.configure(command=self.__scroll_x__)
        # Make the canvas expandable
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        # Bind events to the Canvas
        self.MainCanvas.bind('<Configure>', self.__canvas_configure_show_image__)  # canvas is resized
        self.MainCanvas.bind('<MouseWheel>', self.__wheel__)  # with Windows and MacOS, but not Linux
        self.MainCanvas.bind('<Double-Button-1>',self.__click_coords__)
        self.MainCanvas.bind('<Motion>',self.__canvas_mouse_coords__)
        master.bind('<Up>',self.__press_up__)
        master.bind('<Down>',self.__press_down__)
        master.bind('<Left>',self.__press_left__)
        master.bind('<Right>',self.__press_right__)
        # Put image into container rectangle and use it to set proper coordinates to the image
        ImageContainer = self.MainCanvas.create_rectangle(0, 0,self.image_crop[3]-self.image_crop[2], self.image_crop[1]-self.image_crop[0], width=0)

        ZFtext = Text(self.master,takefocus=0)
        self.ZoomFactor = np.prod(self.scalehisto)
        ZFtext.insert(1.0,'x {}'.format(np.round(self.ZoomFactor*self.ZoomFactor,3)))
        ZFtext.grid(row=0,column=0,sticky=NW)
        ZFtext.config(bg='black',fg='red',height=1,width=6,relief=FLAT)
        master.add(self.master,weight=500)


    """the private methods in this class"""

    def __scroll_x__(self,*args,**kwargs):
        return

    def __scroll_y__(self,*args,**kwargs):
        return

    def __canvas_configure_show_image__(self,event=NONE):
        return

    def __wheel__(self,event):
        return

    def __click_coords__(self,event):
        return

    def __canvas_mouse_coords__(self,event):
        return

    def __press_up__(self,event):
        return

    def __press_down__(self,event):
        return

    def __press_left__(self,event):
        return

    def __press_right__(self,event):
        return

    def __zoom_in__(self,event):
        return

    def __zoom_out__(self,event):
        return

    """the public methods in this class"""
