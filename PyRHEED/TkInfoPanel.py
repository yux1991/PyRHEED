#This program is used to analyze and simulate the RHEED pattern
#Last updated by Yu Xiang at 08/11/2018
#This code is written in Python 3.6.6 (32 bit)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Standard Libraries ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import numpy as np
import os
import math
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
from scipy.special import wofz
from TkMain import *

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Classes ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TkInfoPanel(TkMain):

    def __init__(self,main_window,Defaults):

        """instance variables"""
        self.Sensitivity = StringVar()
        self.Sensitivity.set(Defaults['sensitivity'])
        self.ElectronEnergy = StringVar()
        self.ElectronEnergy.set(Defaults['electron_energy'])
        self.Azimuth = StringVar()
        self.Azimuth.set(Defaults['azimuth'])
        self.ScaleBarLength = StringVar()
        self.ScaleBarLength.set(Defaults['scale_bar_length'])
        self.Brightness = DoubleVar()
        self.Brightness.set(float(Defaults['brightness']))
        self.CurrentBrightness=float(Defaults['brightness'])
        self.UserBlack = IntVar()
        self.UserBlack.set(int(Defaults['black_level']))
        self.CurrentBlackLevel=int(Defaults['black_level'])
        self.EnableAutoWB = IntVar()
        self.EnableAutoWB.set(int(Defaults['auto_wb']))
        self.IntegralWidth = IntVar()
        self.IntegralWidth.set(int(Defaults['integral_width']))
        self.ChiRange = IntVar()
        self.ChiRange.set(int(Defaults['chi_range']))
        self.PFRadius = DoubleVar()
        self.PFRadius.set(float(Defaults['pf_radius']))
        self.PFTilt = DoubleVar()
        self.PFTilt.set(float(Defaults['pf_tilt']))
        self.StartEntryText = StringVar()
        self.StartEntryText.set("0, 0")
        self.EndEntryText = StringVar()
        self.EndEntryText.set("0, 0")
        self.WidthEntryText = StringVar()
        self.WidthEntryText.set("1")

        '''Initialize the information panel on the right hand side of the canvas'''
        #create InfoFrame to display informations
        self.InfoFrame = ttk.Frame(main_window.master, relief=FLAT,padding="0.05i")
        self.InfoFrame.grid(row=1,column=19+2,sticky=N+E+S+W)
        FileBrowserLabelFrame = ttk.LabelFrame(self.InfoFrame,text="Browse File",labelanchor=NW)
        FileBrowserLabelFrame.grid(row=0,column=0,sticky=N+E+W+S)
        FileBrowserButtonFrame = ttk.Frame(FileBrowserLabelFrame,padding="0.05i")
        FileBrowserButtonFrame.grid(row=0,column=0,sticky=N+E+W+S)
        ChooseWorkingDirectory = ttk.Button(FileBrowserButtonFrame,command=TkMain.choose_file,text='Choose File',width=20,cursor='hand2')
        ChooseWorkingDirectory.grid(row=0,column=0,sticky=EW)
        SavePlainImage = ttk.Button(FileBrowserButtonFrame,command=TkMain.save_as_plain_image,text='Save Plain Image',width=20,cursor='hand2')
        SavePlainImage.grid(row=0,column=1,sticky=EW)
        SaveAnnotatedImage = ttk.Button(FileBrowserButtonFrame,command=TkMain.save_as_annotated_image,text='Save Annotated Image',width=20, cursor='hand2')
        SaveAnnotatedImage.grid(row=0,column=2,sticky=EW)
        FileBrowserVSB = ttk.Scrollbar(FileBrowserLabelFrame,orient='vertical')
        FileBrowserHSB = ttk.Scrollbar(FileBrowserLabelFrame,orient='horizontal')
        FileBrowser = ttk.Treeview(FileBrowserLabelFrame,columns = ('fullpath','type','date','size'),displaycolumns=('date','size'), cursor='left_ptr',height=8,selectmode='browse',yscrollcommand=lambda f,l: self.__autoscroll__(FileBrowserVSB,f,l),xscrollcommand=lambda f,l:self.__autoscroll__(FileBrowserHSB,f,l))
        FileBrowser.grid(row=1,column=0,sticky=N+E+W+S)
        FileBrowserVSB.grid(row=1,column=1,sticky=NS)
        FileBrowserHSB.grid(row=2,column=0,sticky=EW)
        FileBrowserVSB['command']=FileBrowser.yview
        FileBrowserHSB['command']=FileBrowser.xview
        FileBrowserHeadings= [('#0','Current Directory Structure'),('date','Date'),('size','Size')]
        for iid,text in FileBrowserHeadings:
            FileBrowser.heading(iid,text=text,anchor=W)
        FileBrowserColumns= [('#0',270),('date',70),('size',70)]
        for iid,width in FileBrowserColumns:
            FileBrowser.column(iid,width=width,anchor=W)
        FileBrowser.bind('<<TreeviewOpen>>',self.tree_update)
        FileBrowser.bind('<Double-Button-1>',self.change_dir)
        self.populate_roots(FileBrowser)

        #create a Notebook widget
        NoteBook = ttk.Notebook(self.InfoFrame,cursor = 'hand2')
        NoteBook.grid(row=1,column=0,sticky=N+W+E+S)

        #create a Frame for "Parameters"
        Paraframe = ttk.Frame(NoteBook,relief=FLAT,padding='0.05i')
        Paraframe.grid(row=0,column=0,sticky=N+E+S+W)
        OkayCommand = Paraframe.register(self.__entry_is_okay__)
        ParaEntryFrame = ttk.Frame(Paraframe,relief=FLAT)
        ParaEntryFrame.grid(row=0,column=0)
        self.ParaLabel1=self.latex2image('Sensitivity ($pixel/\sqrt{keV}$):')
        self.ParaLabel2=self.latex2image('Electron energy ($kev$):')
        self.ParaLabel3=self.latex2image('Azimuth ($\degree$):')
        self.ParaLabel4=self.latex2image('Scale Bar Length ($\AA$):')
        ParaModes=[(self.ParaLabel1,0,self.Sensitivity),(self.ParaLabel2,1,self.ElectronEnergy),(self.ParaLabel3,2,self.Azimuth),(self.ParaLabel4,3, self.ScaleBarLength)]
        for LatexImage,row,textvariable in ParaModes:
            ParaLabel = ttk.Label(ParaEntryFrame,cursor='left_ptr',image=LatexImage,width=35)
            ParaLabel.grid(row=row,column=0,sticky=W)
            ParaEntry = ttk.Entry(ParaEntryFrame,cursor='xterm',width=20,justify=LEFT,textvariable=textvariable)
            ParaEntry.grid(row=row,column=1,sticky=W,padx=10)

        ButtonModes=[('Label',0,self.__label__),('Calibrate',1,self.__calibrate__),('Clear',2,self.__delete_calibration__)]
        ParaButtonFrame = ttk.Frame(Paraframe,cursor ='left_ptr',relief=FLAT,)
        ParaButtonFrame.grid(row=0,column=1,padx=20)
        for text,row,command in ButtonModes:
            Button = ttk.Button(ParaButtonFrame,cursor='hand2',text=text,command=command)
            Button.grid(row=row,column=0,sticky=E)

        #create a Frame for "Image Adjust"
        Adjustframe = ttk.Frame(NoteBook,relief=FLAT,padding='0.05i')
        Adjustframe.grid(row=0,column=0,sticky=N+E+S+W)
        AdjustEntryFrame = ttk.Frame(Adjustframe,relief=FLAT)
        AdjustEntryFrame.grid(row=0,column=0)
        BrightnessLabel = ttk.Label(AdjustEntryFrame,cursor='left_ptr',text='Brightness ({})'.format(self.CurrentBrightness),width=20)
        BrightnessLabel.grid(row=0,column=0,sticky=W)
        BrightnessScale = ttk.Scale(AdjustEntryFrame,command = self.__brightness_update__,variable=self.Brightness,value=0.5,cursor="hand2",length=290,orient=HORIZONTAL,from_=0,to=100)
        BrightnessScale.grid(row=0,column=1,sticky=W)
        BlackLevelLabel = ttk.Label(AdjustEntryFrame,cursor='left_ptr',text='Black Level ({})'.format(self.CurrentBlackLevel),width=20)
        BlackLevelLabel.grid(row=1,column=0,sticky=W)
        BlackLevelScale = ttk.Scale(AdjustEntryFrame,command = self.__user_black_update__,variable=self.UserBlack,value=50,cursor="hand2",length=290,orient=HORIZONTAL,from_=0,to=655)
        BlackLevelScale.grid(row=1,column=1,sticky=W)
        AutoWBLabel = ttk.Label(AdjustEntryFrame,cursor='left_ptr',text='Auto White Balance',width=20)
        AutoWBLabel.grid(row=2,column=0,sticky=W)
        WBCheckbutton = ttk.Checkbutton(AdjustEntryFrame,cursor="hand2",variable = self.EnableAutoWB)
        WBCheckbutton.grid(row=2,column=1,sticky=W)
        AdjustButtonFrame = ttk.Frame(Adjustframe,cursor ='left_ptr',relief=FLAT)
        AdjustButtonFrame.grid(row=1,column=0)
        ApplyAdjust = ttk.Button(AdjustButtonFrame,cursor='hand2',text='Apply',command=self.adjust_update)
        ApplyAdjust.grid(row=0,column=0,sticky=E,pady=10,padx=10)
        ResetAdjust = ttk.Button(AdjustButtonFrame,cursor='hand2',text='Reset',command=self.adjust_reset)
        ResetAdjust.grid(row=0,column=1,sticky=W,pady=10,padx=10)

        #create a Frame for "Profile Type"
        ProfileTypeFrame = ttk.Frame(NoteBook,relief=FLAT,padding='0.05i')
        ProfileTypeFrame.grid(row=0,column=0,sticky=W)
        Profileframe = ttk.Frame(ProfileTypeFrame,relief=FLAT)
        Profileframe.grid(row=0,column=0,sticky=W)
        IntegralWidthLabel = ttk.Label(Profileframe,cursor='left_ptr',text='Half Width ({} \u00C5\u207B\u00B9)'.format(np.round(self.IntegralWidth.get()/(float(self.Sensitivity.get())/np.sqrt(float(self.ElectronEnergy.get()))),2)),width=20)
        IntegralWidthLabel.grid(row=1,column=0,sticky=W)
        IntegralWidthScale = ttk.Scale(Profileframe,cursor="hand2",command=self.__integral_width_update__,length=290, orient=HORIZONTAL,from_=1,to=100, variable = self.IntegralWidth,value=10)
        IntegralWidthScale.grid(row=1,column=1,sticky=W)
        ChiRangeLabel = ttk.Label(Profileframe,cursor='left_ptr',text='Chi Range ({}\u00B0)'.format(self.ChiRange.get()),width=20)
        ChiRangeLabel.grid(row=2,column=0,sticky=W)
        ChiRangeScale = ttk.Scale(Profileframe,cursor="hand2",command=self.__PFChiRange_update__,length=290, orient=HORIZONTAL,from_=1,to=180,variable = self.ChiRange,value=60)
        ChiRangeScale.grid(row=2,column=1,sticky=W)
        RadiusLabel = ttk.Label(Profileframe,cursor='left_ptr',text='Radius ({} \u00C5\u207B\u00B9)'.format(np.round(self.PFRadius.get()/(float(self.Sensitivity.get())/np.sqrt(float(self.ElectronEnergy.get()))),2)),width=20)
        RadiusLabel.grid(row=3,column=0,sticky=W)
        RadiusScale = ttk.Scale(Profileframe,command=self.__PFRadius_update__,cursor="hand2",length=290,orient=HORIZONTAL,from_=50,to=1000,variable = self.PFRadius,value=200.)
        RadiusScale.grid(row=3,column=1,sticky=W)
        TiltLabel = ttk.Label(Profileframe,cursor='left_ptr',text='Tilt Angle ({}\u00B0)'.format(np.round(self.PFTilt.get(),1)),width=20)
        TiltLabel.grid(row=4,column=0,sticky=W)
        TiltScale = ttk.Scale(Profileframe,command=self.__PFTilt_update__,cursor="hand2",length=290,orient=HORIZONTAL,from_=-15,to=15,variable =self.PFTilt,value=0.)
        TiltScale.grid(row=4,column=1,sticky=W)
        ButtonFrame = ttk.Frame(ProfileTypeFrame)
        ButtonFrame.grid(row=1,column=0)
        ApplyProfile = ttk.Button(ButtonFrame,cursor='hand2',text='Apply',command=self.profile_update)
        ApplyProfile.grid(row=0,column=0,sticky=E,padx=10)
        ResetProfile = ttk.Button(ButtonFrame,cursor='hand2',text='Reset',command=self.profile_reset)
        ResetProfile.grid(row=0,column=1,sticky=W,padx=10)

        NoteBook.add(Paraframe,text="Parameters")
        NoteBook.add(Adjustframe,text="Image Adjust")
        NoteBook.add(ProfileTypeFrame,text="Profile Options")


        #create a LabelFrame for "Cursor Information"
        CIlabelframe = ttk.LabelFrame(self.InfoFrame,text='Cursor Information',labelanchor=NW)
        CIlabelframe.grid(row=2,ipadx=5,pady=5,column=0,sticky=N+E+S+W)
        CIframe = ttk.Frame(CIlabelframe,padding='0.05i')
        CIframe.grid(row=0,column=0,sticky=W+E)
        CIButtonframe = ttk.Frame(CIlabelframe,padding='0.1i')
        CIButtonframe.grid(row=0,column=1,sticky=W+E)
        ChoosedSpotLabel = ttk.Label(CIframe,text="Choosed (X,Y):\t\nIntensity:\t\n")
        ChoosedSpotLabel.grid(row=0,column=0,sticky=NW)
        ChoosedSpotLabel.config(justify=LEFT,relief=FLAT)
        ChoosedSpotEntry = ttk.Label(CIframe,text="({}, {})\n0\n".format(np.int(main_window.Ctr_X),np.int(main_window.Ctr_Y)))
        ChoosedSpotEntry.grid(row=0,column=1,ipadx=5,sticky=NW)
        ChoosedSpotEntry.config(width = 10,justify=LEFT,relief=FLAT)
        CIButton1 = ttk.Button(CIButtonframe,command=self.__set_as_center__,text='Set As Center',cursor='hand2')
        CIButton1.grid(row=0,column=0,sticky=N+S+E+W,padx=10,pady=13)
        StartLabel = ttk.Label(CIframe,text="Start (X,Y):")
        StartLabel.grid(row=1,column=0,sticky=NW)
        StartLabel.config(justify=LEFT,relief=FLAT)
        EndLabel = ttk.Label(CIframe,text="End (X,Y):")
        EndLabel.grid(row=2,column=0,sticky=NW)
        EndLabel.config(justify=LEFT,relief=FLAT)
        WidthLabel = ttk.Label(CIframe,text="Width:")
        WidthLabel.grid(row=3,column=0,sticky=NW)
        WidthLabel.config(justify=LEFT,relief=FLAT)
        StartEntry = ttk.Entry(CIframe,textvariable=self.StartEntryText)
        StartEntry.grid(row=1,column=1,ipadx=5,sticky=NW)
        StartEntry.config(width = 20,justify=LEFT)
        EndEntry = ttk.Entry(CIframe,textvariable=self.EndEntryText)
        EndEntry.grid(row=2,column=1,ipadx=5,sticky=NW)
        EndEntry.config(width = 20,justify=LEFT)
        WidthEntry = ttk.Entry(CIframe,textvariable=self.WidthEntryText)
        WidthEntry.grid(row=3,column=1,ipadx=5,sticky=NW)
        WidthEntry.config(width = 20,justify=LEFT)
        CIButton2 = ttk.Button(CIButtonframe,command=self.choose_this_region,text='Choose This Region',cursor='hand2')
        CIButton2.grid(row=1,column=0,sticky=N+S+E+W,padx=10,pady=25)

        CMIBottomFrame = ttk.Frame(main_window.master)
        CMIBottomFrame.grid(row=2,column=19+2,sticky=E)
        CMIlabel = ttk.Label(CMIBottomFrame,text='  x={}, y={}'.format(main_window.Mouse_X,main_window.Mouse_Y))
        CMIlabel.grid(row=0,column=2,sticky=E)
        CMIlabel.config(justify=RIGHT,width=30)
        self.LineScanCanvas = tk.Canvas(self.InfoFrame,bd=2,cursor='crosshair',relief=RIDGE)
        self.LineScanCanvas.grid(row=4,column=0,sticky=N+W+E+S)
        self.LineScanCanvas.update()
        self.LineScanCanvas.bind('<Motion>',self.__line_scan_canvas_mouse_coords__)
        ZFtext = Text(main_window.master,takefocus=0)
        self.ZoomFactor = np.prod(main_window.scalehisto)
        ZFtext.insert(1.0,'x {}'.format(np.round(self.ZoomFactor*self.ZoomFactor,3)))
        ZFtext.grid(row=1,column=0,sticky=NW)
        ZFtext.config(bg='black',fg='red',height=1,width=6,relief=FLAT)

    """the private methods in this class"""

    def __autoscroll__(self,sbar,first,last):
        return

    def __entry_is_okay__():
        return

    def __calibrate__():
        return

    def __label__():
        return

    def __delete_calibration__():
        return

    def __brightness_update__():
        return

    def __user_black_update__():
        return

    def __integral_width_update__():
        return

    def __PFChiRange_update__():
        return

    def __PFRadius_update__():
        return

    def __PFTilt_update__():
        return

    def __set_as_center__():
        return

    def __line_scan_canvas_mouse_coords__():
        return


    """the public methods in this class"""
    def tree_update(self,event):
        return

    def change_dir(self,event):
        return

    def populate_roots(self,FileBrowser):
        return

    def latex2image(self,LatexExpression):
        buffer = BytesIO()
        font = FontProperties(family='Arial', style='normal',weight='roman')
        math_to_image(LatexExpression,buffer, prop=font, dpi=100,format='png')
        buffer.seek(0)
        pimg=Image.open(buffer)
        r,g,b,a=pimg.split()
        im1_rgb = Image.merge('RGB',(r,g,b))
        im2_rgb=ImageOps.invert(im1_rgb)
        im2_L= im2_rgb.convert('L')
        pimg.putalpha(im2_L)
        image = ImageTk.PhotoImage(pimg)
        buffer.close()
        return image

    def adjust_update():
        return

    def adjust_reset():
        return

    def profile_update():
        return

    def profile_reset():
        return

    def choose_this_region():
        return
