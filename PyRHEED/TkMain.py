#This module is used to construct the GUI
#Last updated by Yu Xiang at 08/12/2018
#This code is written in Python 3.6.6 (32 bit)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Standard Libraries ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import numpy as np
import os
import math
import matplotlib.backends.tkagg as tkagg
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib.cm as cm
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk,ImageOps,ImageDraw,ImageFont
from array import array
from io import BytesIO
from matplotlib.mathtext import math_to_image
from matplotlib.font_manager import FontProperties
from configuration import *

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Classes ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TkMain(ttk.Frame):
    """This class creates the main widget, the menu and the tool bars"""

    #class variables

    """the initialization method for this class"""
    def __init__(self,mainframe,Defaults):

        #instance variables
        self.DefaultPath=Defaults['image_path']
        self.IconPath=Defaults['icon_path']
        self.VS,self.HS=int(Defaults['vertical_shift']),int(Defaults['horizontal_shift'])
        self.DefaultFileName = os.path.basename(self.DefaultPath)
        self.ActionMode = StringVar()
        self.ActionMode.set("N")
        self.image_crop=[1200+self.VS,2650+self.VS,500+self.HS,3100+self.HS]
        self.Ctr_X,self.Ctr_Y=0,0
        self.Mouse_X,self.Mouse_Y=0,0
        self.scalehisto = array('f')
        self.scalehisto.append(1)

        """initialization of the menu"""
        ttk.Frame.__init__(self,master=mainframe)
        self.master.title('PyRHEED: ~/'+self.DefaultFileName)
        top=self.master.winfo_toplevel()
        MenuBar=tk.Menu(top)
        top['menu']=MenuBar

        FileMenu=tk.Menu(MenuBar,tearoff=0)
        MenuBar.add_cascade(label='File',menu=FileMenu)
        FileModes = [('New',self.__menu_file_new__),('Open',self.__menu_file_open__),('Save As...',self.__menu_file_save_as__),('Close',self.__menu_file_close__)]
        for label,command in FileModes:
            FileMenu.add_command(label=label,command=command)

        PreferenceMenu=tk.Menu(MenuBar,tearoff=0)
        MenuBar.add_cascade(label='Preferences',menu=PreferenceMenu)
        PreferenceModes = [('Default Settings',self.__menu_preference_default__)]
        for label,command in PreferenceModes:
            PreferenceMenu.add_command(label=label,command=command)

        TwoDimMenu=tk.Menu(MenuBar,tearoff=0)
        MenuBar.add_cascade(label='2D Map',menu=TwoDimMenu)
        TwoDimModes = [('Settings',self.two_dim_mapping)]
        for label,command in TwoDimModes:
            TwoDimMenu.add_command(label=label,command=command)

        FitMenu=tk.Menu(MenuBar,tearoff=0)
        MenuBar.add_cascade(label='Fit',menu=FitMenu)
        FitModes = [('Settings',self.fit)]
        for label,command in FitModes:
            FitMenu.add_command(label=label,command=command)

        HelpMenu=tk.Menu(MenuBar,tearoff=0)
        MenuBar.add_cascade(label='Help',menu=HelpMenu)
        HelpModes = [('About',self.__menu_help_about__)]
        for label,command in HelpModes:
            HelpMenu.add_command(label=label,command=command)

        """initialization of the toolbar"""

        ToolBarFrame = ttk.Frame(self.master)
        ToolBarFrame.grid(row=0,column=0,sticky=NW)
        self.OpenIcon = ImageTk.PhotoImage(file=os.path.join(self.IconPath,'open.gif'))
        self.SaveIcon = ImageTk.PhotoImage(file=os.path.join(self.IconPath,'save.gif'))
        self.SaveAsIcon = ImageTk.PhotoImage(file=os.path.join(self.IconPath,'save as.gif'))
        self.FitIcon = ImageTk.PhotoImage(file=os.path.join(self.IconPath,'curve.png'))
        self.ZoomInIcon = ImageTk.PhotoImage(file=os.path.join(self.IconPath,'zoom in.gif'))
        self.ZoomOutIcon = ImageTk.PhotoImage(file=os.path.join(self.IconPath,'zoom out.gif'))

        LineIconImage = Image.open(os.path.join(self.IconPath,'line.png'))
        ResizedLineIconImage = LineIconImage.resize(size=(24,24))
        self.LineIcon = ImageTk.PhotoImage(ResizedLineIconImage)
        RectangleIconImage = Image.open(os.path.join(self.IconPath,'rectangle.png'))
        ResizedRectangleIconImage = RectangleIconImage.resize(size=(24,24))
        self.RectangleIcon = ImageTk.PhotoImage(ResizedRectangleIconImage)
        ArcIconImage = Image.open(os.path.join(self.IconPath,'arc.png'))
        ResizedArcIconImage = ArcIconImage.resize(size=(24,24))
        self.ArcIcon = ImageTk.PhotoImage(ResizedArcIconImage)
        MoveIconImage = Image.open(os.path.join(self.IconPath,'move.png'))
        ResizedMoveIconImage = MoveIconImage.resize(size=(24,24))
        self.MoveIcon = ImageTk.PhotoImage(ResizedMoveIconImage)

        ToolBarModes1 = [(self.OpenIcon,self.choose_file,0),(self.SaveIcon,self.save_as_plain_image,1),(self.SaveAsIcon,self.save_as_annotated_image,2),(self.ZoomInIcon,self.__zoom_in__,6),(self.ZoomOutIcon,self.__zoom_out__,7),(self.FitIcon,self.fit,3)]
        for icon,command,col in ToolBarModes1:
            ToolButton = ttk.Button(ToolBarFrame,image=icon,command=command,cursor='hand2')
            ToolButton.grid(row=0,column=col,sticky=NW)

        ToolButton2D = ttk.Button(ToolBarFrame,text='2D',command=self.two_dim_mapping,cursor='hand2',width=4)
        ToolButton2D.grid(row=0,column=4,sticky=N+S+W+E)
        ToolButton3D = ttk.Button(ToolBarFrame,text='3D',command=self.three_dim_mapping,cursor='hand2',width=4)
        ToolButton3D.grid(row=0,column=5,sticky=N+S+W+E)
        ToolBarModes2 = [(self.LineIcon,'LS',8),(self.RectangleIcon,'LI',9),(self.ArcIcon,'PF',10),(self.MoveIcon,'N',11)]

        for icon,mode,col in ToolBarModes2:
            ToolButton = tk.Radiobutton(ToolBarFrame,command=self.__choose_mode__,image=icon,indicatoron=0,variable=self.ActionMode,value=mode, cursor="hand2")
            ToolButton.grid(row=0,column=col,sticky=NW)

        '''Initialize the canvas widget with two scrollbars'''
        # Vertical and horizontal scrollbars for canvas
        vbar = ttk.Scrollbar(self.master, orient='vertical')
        hbar = ttk.Scrollbar(self.master, orient='horizontal')
        vbar.grid(row=1, column=1, sticky='ns')
        hbar.grid(row=2, column=0, sticky='we')
        # Create canvas and put image on it
        self.MainCanvas = tk.Canvas(self.master, cursor = 'crosshair',relief=RIDGE, highlightthickness=0,xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.MainCanvas.grid(row=1, column=0, sticky='nswe')
        self.MainCanvas.update()  # wait till canvas is created
        vbar.configure(command=self.__scroll_y__)  # bind scrollbars to the canvas
        hbar.configure(command=self.__scroll_x__)
        # Make the canvas expandable
        self.master.rowconfigure(1, weight=1)
        self.master.columnconfigure(0, weight=1)
        # Bind events to the Canvas
        self.MainCanvas.bind('<Configure>', self.__canvas_configure_show_image__)  # canvas is resized
        self.MainCanvas.bind('<MouseWheel>', self.__wheel__)  # with Windows and MacOS, but not Linux
        self.MainCanvas.bind('<Double-Button-1>',self.__click_coords__)
        self.MainCanvas.bind('<Motion>',self.__canvas_mouse_coords__)
        mainframe.bind('<Up>',self.__press_up__)
        mainframe.bind('<Down>',self.__press_down__)
        mainframe.bind('<Left>',self.__press_left__)
        mainframe.bind('<Right>',self.__press_right__)
        # Put image into container rectangle and use it to set proper coordinates to the image
        ImageContainer = self.MainCanvas.create_rectangle(0, 0,self.image_crop[3]-self.image_crop[2], self.image_crop[1]-self.image_crop[0], width=0)


    """the private methods in this class"""
    def __menu_file_new__():
        return

    def __menu_file_open__():
        return

    def __menu_file_save_as__():
        return

    def __menu_file_close__():
        return

    def __menu_preference_default__():
        return

    def __menu_help_about__():
        return

    def __choose_mode__():
        return

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
    def two_dim_mapping():
        return

    def three_dim_mapping():
        return

    def fit():
        return

    def save_as_plain_image():
        return

    def save_as_annotated_image():
        return

    def choose_file():
        return
