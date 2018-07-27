#This program is used to analyze and simulate the RHEED pattern
#Last updated by Yu Xiang at 07/27/2018
#This code is written in Python 3.6.6

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Standard Libraries ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.gridspec as gridspec
import matplotlib.ticker as ticker
import matplotlib
import rawpy
import glob
import os
from time import localtime
import math
import scipy.ndimage
from scipy.optimize import least_squares
import matplotlib.backends.tkagg as tkagg
from matplotlib.backends.backend_agg import FigureCanvasAgg
from time import sleep
import sys
import matplotlib.cm as cm
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk
from array import array

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Classes ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class RHEED_GUI(ttk.Frame):
    """This class is used to generate a GUI for RHEED pattern analysis"""

    def __init__(self, mainframe):

        self.DefaultPath = 'C:/RHEED/01192017 multilayer graphene on Ni/20 keV/Img0000.nef'
        self.Ctr_X,self.Ctr_Y,self.Mouse_X,self.Mouse_Y=0,0,0,0
        self.scale = 1.0
        self.dpi = 100.
        self.xx=array('l')
        self.yy=array('l')
        self.scalehisto=array('f')
        self.LineStartX,self.LineStartY = 0,0
        self.LineEndX,self.LineEndY = 0,0
        self.SaveLineStartX = array('f')
        self.SaveLineStartY = array('f')
        self.SaveLineEndX = array('f')
        self.SaveLineEndY = array('f')
        self.mode = StringVar()
        self.mode.set("N")
        self.EntryText1 = StringVar()
        self.EntryText1.set('20')
        self.EntryText3 = StringVar()
        self.EntryText3.set('0')
        self.EntryText4 = StringVar()
        self.EntryText4.set('5')
        self.IntegralWidth = StringVar()
        self.IntegralWidth.set('20')
        self.ChiRange = StringVar()
        self.ChiRange.set('60')
        self.PFRadius = DoubleVar()
        self.PFRadius.set('5.')
        self.ScaleVar1 = DoubleVar()
        self.ScaleVar1.set(30)
        self.CurrentBrightness =0.3
        self.CheckStatus = IntVar()
        self.CheckStatus.set(0)
        self.ProfileMode = StringVar()
        self.ProfileMode.set('2D')
        self.LineScanAxesPosition = [0.2,0.2,0.75,0.7]
        self.img = self.read_image(self.DefaultPath)
        self.LineStatus = 0
        self.CalibrationStatus =1
        self.LabelStatus =1
        fontname = 'Helvetica'
        fontsize = 10
        FrameLabelFontSize = 11

        ''' Initialize the main Frame '''
        ttk.Frame.__init__(self, master=mainframe)
        self.master.title('RHEED pattern')
        # Vertical and horizontal scrollbars for canvas
        vbar = ttk.Scrollbar(self.master, orient='vertical')
        hbar = ttk.Scrollbar(self.master, orient='horizontal')
        vbar.grid(row=0, column=1, sticky='ns')
        hbar.grid(row=1, column=0, sticky='we')
        # Create canvas and put image on it
        self.canvas = tk.Canvas(self.master, cursor = 'crosshair',relief=RIDGE, highlightthickness=0,
                                xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.canvas.grid(row=0, column=0, sticky='nswe')
        self.canvas.update()  # wait till canvas is created
        vbar.configure(command=self.scroll_y)  # bind scrollbars to the canvas
        hbar.configure(command=self.scroll_x)
        # Make the canvas expandable
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        # Bind events to the Canvas
        self.canvas.bind('<Configure>', self.show_image)  # canvas is resized
        self.canvas.bind('<MouseWheel>', self.wheel)  # with Windows and MacOS, but not Linux
        self.canvas.bind('<Double-Button-1>',self.click_coords)
        self.canvas.bind('<Motion>',self.canvas_mouse_coords)
        self.bind_all("<1>",lambda event:event.widget.focus_set())

        #create an PIL.Image object
        self.image = Image.new('L',(self.img.shape[1],self.img.shape[0]))
        #convert 16 bit image to 8 bit image
        self.uint16 = np.uint8(self.img/256)
        self.outpil = self.uint16.astype(self.uint16.dtype.newbyteorder("L")).tobytes()
        self.image.frombytes(self.outpil)

        self.width, self.height = self.image.size
        self.imscale = 1.0  # scale for the canvas image
        self.delta = 1.2  # zoom magnitude
        # Put image into container rectangle and use it to set proper coordinates to the image
        self.container = self.canvas.create_rectangle(0, 0, self.width, self.height, width=0)
        self.show_image()

        #create InfoFrame to display informations
        self.InfoFrame = ttk.Frame(self.master, relief=FLAT)
        self.InfoFrame.grid(row=0,column=19+2,sticky=N+E+S+W)

        #create a treeview widget as a file browser
        self.FileBrowserLabelFrame = ttk.LabelFrame(self.InfoFrame,text="Browse File",labelanchor=NW)
        self.FileBrowserLabelFrame.grid(row=0,column=0,sticky=N+E+W+S)
        self.ChooseWorkingDirectory = ttk.Button(self.FileBrowserLabelFrame,command=self.choose_file,text='Choose File',cursor='hand2')
        self.ChooseWorkingDirectory.grid(row=0,column=0,sticky=EW)
        self.FileBrowserVSB = ttk.Scrollbar(self.FileBrowserLabelFrame,orient='vertical')
        self.FileBrowserHSB = ttk.Scrollbar(self.FileBrowserLabelFrame,orient='horizontal')
        self.FileBrowser = ttk.Treeview(self.FileBrowserLabelFrame,columns = ('fullpath','type','date','size'),displaycolumns=('date','size'),cursor='left_ptr',height=8,selectmode='browse',yscrollcommand=lambda f,l: self.autoscroll(self.FileBrowserVSB,f,l),xscrollcommand=lambda f,l:self.autoscroll(self.FileBrowserHSB,f,l))
        self.FileBrowser.grid(row=1,column=0,sticky=N+E+W+S)
        self.FileBrowserVSB.grid(row=1,column=1,sticky=NS)
        self.FileBrowserHSB.grid(row=2,column=0,sticky=EW)
        self.FileBrowserVSB['command']=self.FileBrowser.yview
        self.FileBrowserHSB['command']=self.FileBrowser.xview
        FileBrowserHeadings= [('#0','Directory Structure'),('date','Date'),('size','Size')]
        for iid,text in FileBrowserHeadings:
            self.FileBrowser.heading(iid,text=text,anchor=W)
        FileBrowserColumns= [('#0',270),('date',70),('size',70)]
        for iid,width in FileBrowserColumns:
            self.FileBrowser.column(iid,width=width,anchor=W)
        self.populate_roots(self.FileBrowser)
        self.FileBrowser.bind('<<TreeviewOpen>>',self.tree_update)
        self.FileBrowser.bind('<Double-Button-1>',self.change_dir)

        #create a LabelFrame for "Cursor Information"
        self.CIframe = ttk.LabelFrame(self.InfoFrame,text='Cursor Information',labelanchor=NW)
        self.CIframe.grid(row=1,ipadx=5,pady=5,column=0,sticky=N+E+S+W)
        self.CIlabel1 = ttk.Label(self.CIframe,text="Coordinates of the spot is:\t\nNormalized intensity of spot is:\t")
        self.CIlabel1.grid(row=0,column=0,sticky=NW)
        self.CIlabel1.config(font=(fontname,fontsize),justify=LEFT,relief=FLAT)
        self.CIlabel2 = ttk.Label(self.CIframe,text="({}, {})\n{}".format(np.int(self.Ctr_X),np.int(self.Ctr_Y),np.int(self.img[np.int(self.Ctr_Y),np.int(self.Ctr_X)])))
        self.CIlabel2.grid(row=0,column=1,ipadx=5,sticky=NW)
        self.CIlabel2.config(font=(fontname,fontsize),width = 15,justify=LEFT,relief=FLAT)
        self.CIButton = ttk.Button(self.CIframe,command=self.get_center,text='Set As Center',cursor='hand2')
        self.CIButton.grid(row=0,column=2,sticky=E)

        #create a Notebook widget
        self.nb = ttk.Notebook(self.InfoFrame,cursor = 'hand2')
        self.nb.grid(row=2,column=0,sticky=N+W+E+S)
        #create a Frame for "Parameters"
        self.Paraframe = ttk.Frame(self.nb,relief=FLAT,padding ='0.02i')
        self.Paraframe.grid(row=0,column=0,sticky=N+E+S+W)
        OkayCommand = self.Paraframe.register(self.entry_is_okay)
        self.ParaEntryFrame = ttk.Frame(self.Paraframe,relief=FLAT,padding='0.02i')
        self.ParaEntryFrame.grid(row=0,column=0)
        self.ParaLabel1 = ttk.Label(self.ParaEntryFrame,cursor='left_ptr',text='Electron Energy (keV):',padding = '0.02i',width=28)
        self.ParaLabel1.grid(row=0,column=0,sticky=W)
        self.ParaEntry1 = ttk.Entry(self.ParaEntryFrame,cursor="xterm",width=10,justify=LEFT,textvariable = self.EntryText1,validate = 'key',validatecommand=(OkayCommand,'%d'))
        self.ParaEntry1.grid(row=0,column=1,sticky=W)
        self.ParaLabel3 = ttk.Label(self.ParaEntryFrame,cursor='left_ptr',text=u'Azimuth (\u00B0):',padding = '0.02i',width=28)
        self.ParaLabel3.grid(row=1,column=0,sticky=W)
        self.ParaEntry3 = ttk.Entry(self.ParaEntryFrame,cursor="xterm",width=10,justify=LEFT,textvariable = self.EntryText3)
        self.ParaEntry3.grid(row=1,column=1,sticky=W)
        self.ParaLabel4 = ttk.Label(self.ParaEntryFrame,cursor='left_ptr',text=u'Scale Bar Length (\u00C5):',padding = '0.02i',width=28)
        self.ParaLabel4.grid(row=2,column=0,sticky=W)
        self.ParaEntry4 = ttk.Entry(self.ParaEntryFrame,cursor="xterm",width=10,justify=LEFT,textvariable = self.EntryText4)
        self.ParaEntry4.grid(row=2,column=1,sticky=W)
        self.ParaButtonFrame = ttk.Frame(self.Paraframe,cursor ='left_ptr',relief=FLAT,padding='0.2i')
        self.ParaButtonFrame.grid(row=0,column=1)
        self.InsertCalibration = ttk.Button(self.ParaButtonFrame,cursor='hand2',text='Calibrate',command=self.calibrate)
        self.InsertCalibration.grid(row=0,column=0,sticky=E)
        self.InsertLabel = ttk.Button(self.ParaButtonFrame,cursor='hand2',text='Label',command=self.label)
        self.InsertLabel.grid(row=1,column=0,sticky=E)
        self.DeleteCalibration = ttk.Button(self.ParaButtonFrame,cursor='hand2',text='Clear',command=self.delete_calibration)
        self.DeleteCalibration.grid(row=2,column=0,sticky=E)

        #create a Frame for "Image Adjust"
        self.Adjustframe = ttk.Frame(self.nb,relief=FLAT,padding='0.02i')
        self.Adjustframe.grid(row=0,column=0,sticky=N+E+S+W)
        OkayCommand = self.Paraframe.register(self.entry_is_okay)
        self.AdjustEntryFrame = ttk.Frame(self.Adjustframe,relief=FLAT)
        self.AdjustEntryFrame.grid(row=0,column=0)
        self.AdjustLabel1 = ttk.Label(self.AdjustEntryFrame,cursor='left_ptr',text='Brightness ({})'.format(self.CurrentBrightness),padding ='0.02i',width=20)
        self.AdjustLabel1.grid(row=0,column=0,sticky=W)
        self.AdjustScale1 = ttk.Scale(self.AdjustEntryFrame,command = self.scale_update,variable=self.ScaleVar1,value=0.5,cursor="hand2",length=150,orient=HORIZONTAL,from_=0,to=100)
        self.AdjustScale1.grid(row=0,column=1,sticky=W)
        self.AdjustLabel4 = ttk.Label(self.AdjustEntryFrame,cursor='left_ptr',text='Auto White Balance',padding = '0.02i',width=20)
        self.AdjustLabel4.grid(row=3,column=0,sticky=W)
        self.AdjustCheck = ttk.Checkbutton(self.AdjustEntryFrame,cursor="hand2",variable = self.CheckStatus)
        self.AdjustCheck.grid(row=3,column=1,sticky=W)
        self.AdjustButtonFrame = ttk.Frame(self.Adjustframe,cursor ='left_ptr',relief=FLAT,padding='0.2i')
        self.AdjustButtonFrame.grid(row=0,column=1)
        self.ApplyAdjust = ttk.Button(self.AdjustButtonFrame,cursor='hand2',text='Apply',command=self.adjust_update)
        self.ApplyAdjust.grid(row=0,column=0,sticky=E)
        self.ResetAdjust = ttk.Button(self.AdjustButtonFrame,cursor='hand2',text='Reset',command=self.adjust_reset)
        self.ResetAdjust.grid(row=1,column=0,sticky=E)

        #create a Frame for "Profile Type"
        self.Profileframe = ttk.Frame(self.nb,relief=FLAT,padding='0.02i')
        self.Profileframe.grid(row=0,column=0,sticky=W)
        self.choose_profile_mode()
        self.ProfileModeFrame = ttk.Frame(self.Profileframe,relief=FLAT,padding='0.1i')
        self.ProfileModeFrame.grid(row=0,column=0,columnspan = 2,sticky=W)
        MODES = [("Pole Figure",'PF'),("2D Mapping","2D"),("3D Mapping","3D")]
        RDColumn = 0
        for text,mode in MODES:
            self.RB = ttk.Radiobutton(self.ProfileModeFrame,command=self.choose_profile_mode,text=text,variable=self.ProfileMode,value=mode,cursor="hand2")
            self.RB.grid(row=0,column=RDColumn,sticky=E+W)
            RDColumn+=1
        self.ProfileLabel1 = ttk.Label(self.Profileframe,cursor='left_ptr',text='Integral Width (pixel):',padding = '0.02i',width=20)
        self.ProfileLabel1.grid(row=1,column=0,sticky=W)
        self.ProfileEntry1 = ttk.Entry(self.Profileframe,cursor="xterm",width=10,justify=LEFT,textvariable = self.IntegralWidth)
        self.ProfileEntry1.grid(row=1,column=1,sticky=W)
        self.ProfileLabel2 = ttk.Label(self.Profileframe,cursor='left_ptr',text='Chi Range',padding = '0.02i',width=15)
        self.ProfileLabel2.grid(row=2,column=0,sticky=W)
        self.ProfileEntry2 = ttk.Entry(self.Profileframe,cursor="xterm",width=10,justify=LEFT,textvariable = self.ChiRange)
        self.ProfileEntry2.grid(row=2,column=1,sticky=W)
        self.ProfileLabel3 = ttk.Label(self.Profileframe,cursor='left_ptr',text='Radius ({} \u00C5\u207B\u00B9)'.format(np.round(self.PFRadius.get(),2)),padding = '0.02i',width=28)
        self.ProfileLabel3.grid(row=3,column=0,sticky=W)
        self.ProfileEntry3 = ttk.Scale(self.Profileframe,command=self.PFRadius_update,cursor="hand2",length=150,orient=HORIZONTAL,from_=0,to=15,variable = self.PFRadius,value=5.)
        self.ProfileEntry3.grid(row=3,column=1,sticky=W)
        self.nb.add(self.Paraframe,text="Parameters")
        self.nb.add(self.Adjustframe,text="Image Adjust")
        self.nb.add(self.Profileframe,text="Profile Type")

        #create a Label for "Cursor Motion Information"
        self.CMIlabel = ttk.Label(self.master,text='x={}, y={}'.format(self.Mouse_X,self.Mouse_Y))
        self.CMIlabel.grid(row=1,column=19+2,sticky=E)
        self.CMIlabel.config(font=(fontname,fontsize),justify=RIGHT)

        #create a LabelFrame for a Radiobutton widget
        self.RDlabelframe = ttk.LabelFrame(self.InfoFrame,text="Mode",labelanchor=NW)
        self.RDlabelframe.grid(row=3,column=0,sticky=N+E+S+W)
        #self.RDlabelframe.config(font=(fontname,FrameLabelFontSize,"bold"))
        self.RDframe = ttk.Frame(self.RDlabelframe,relief=FLAT)
        self.RDframe.grid(row=0,column=0,sticky=N+W+S+E)
        self.choose_mode()
        MODES = [("Normal",'N'),("Line Scan","LS"),("Line Integral","LI")]
        RDColumn = 0
        for text,mode in MODES:
            self.RB = ttk.Radiobutton(self.RDframe,command=self.choose_mode,text=text,variable=self.mode,value=mode,cursor="hand2")
            self.RB.grid(row=2,column=RDColumn,sticky=E+W)
            RDColumn+=1

        #create a canvas for the line scan
        self.LineScanCanvas = tk.Canvas(self.InfoFrame,bd=2,cursor='crosshair',relief=RIDGE)
        self.LineScanCanvas.grid(row=4,column=0,sticky=N+W+E+S)
        self.LineScanCanvas.update()
        self.LineScanCanvas.bind('<Motion>',self.line_scan_canvas_mouse_coords)

        #create a Text widget for "Zoom Factor"
        self.ZFtext = Text(self.master)
        self.ZoomFactor = np.prod(self.scalehisto)*np.prod(self.scalehisto)
        self.ZFtext.insert(1.0,'x {}'.format(np.round(self.ZoomFactor,3)))
        self.ZFtext.grid(row=0,column=0,sticky=NW)
        self.ZFtext.config(font=(fontname,fontsize+4),bg='black',fg='red',height=1,width=6,relief=FLAT)

    def adjust_update(self):
        self.img = self.read_image(self.DefaultPath)
        self.image = Image.new('L',(self.img.shape[1],self.img.shape[0]))
        self.uint16 = np.uint8(self.img/256)
        self.outpil = self.uint16.astype(self.uint16.dtype.newbyteorder("L")).tobytes()
        self.image.frombytes(self.outpil)
        self.show_image()
        try:
            self.line_scan_update()
        except:
            pass

    def adjust_reset(self):
        self.ScaleVar1.set(30)
        self.CheckStatus.set(0)
        self.img = self.read_image(self.DefaultPath)
        self.image = Image.new('L',(self.img.shape[1],self.img.shape[0]))
        self.uint16 = np.uint8(self.img/256)
        self.outpil = self.uint16.astype(self.uint16.dtype.newbyteorder("L")).tobytes()
        self.image.frombytes(self.outpil)
        self.show_image()
        self.AdjustLabel1['text'] = 'Brightness ({})'.format(round(self.ScaleVar1.get()/100,2))
        try:
            self.line_scan_update()
        except:
            pass

    def scale_update(self,evt):
        self.CurrentBrightness = round(float(evt)/100,2)
        self.AdjustLabel1['text'] = 'Brightness ({})'.format(self.CurrentBrightness)


    def choose_profile_mode(self):
        return

    def PFRadius_update(self,evt):
        try:
            self.ProfileLabel3['text'] = 'Radius ({} \u00C5\u207B\u00B9)'.format(np.round(self.PFRadius.get(),2))
        except:
            pass
        return

    def choose_mode(self):
        if self.mode.get() == "N":
            self.canvas.bind('<ButtonPress-1>',self.move_from)
            self.canvas.bind('<B1-Motion>',self.move_to)
            self.canvas.bind('<ButtonRelease-1>',self.move_end)
            self.canvas.bind('<Button-3>',self.delete_line)
        elif self.mode.get() == "LS":
            self.canvas.bind('<ButtonPress-1>',self.scan_from)
            self.canvas.bind('<B1-Motion>',self.scan_to)
            self.canvas.bind('<ButtonRelease-1>',self.scan_end)
            self.canvas.bind('<Alt-ButtonPress-1>',self.move_from)
            self.canvas.bind('<Alt-B1-Motion>',self.move_to)
            self.canvas.bind('<Alt-ButtonRelease-1>',self.move_end)
            self.canvas.bind('<Button-3>',self.delete_line)
        else:
            self.canvas.bind('<ButtonPress-1>',self.integrate_from)
            self.canvas.bind('<B1-Motion>',self.integrate_to)
            self.canvas.bind('<ButtonRelease-1>',self.integrate_end)
            self.canvas.bind('<Alt-ButtonPress-1>',self.move_from)
            self.canvas.bind('<Alt-B1-Motion>',self.move_to)
            self.canvas.bind('<Alt-ButtonRelease-1>',self.move_end)
            self.canvas.bind('<Button-3>',self.delete_line)

    def entry_is_okay(self,action):
        return TRUE

    def calibrate(self):
        thickness = 2
        position = 0.05
        fontsize = int(40*self.ZoomFactor)
        bbox = self.canvas.bbox(self.container)
        bx0,by0 = self.convert_coords(bbox[0],bbox[1])
        bx1,by1 = self.convert_coords(bbox[2],bbox[3])
        x0,y0,y1 = bbox[0]+(bbox[2]-bbox[0])*position,bbox[3]-(bbox[3]-bbox[1])*position,bbox[3]-(bbox[3]-bbox[1])*position
        x1 = x0+float(self.EntryText4.get())*(2269.06/np.sqrt(float(self.EntryText1.get()))/2/np.pi)/(bx1-bx0)*(bbox[2]-bbox[0])
        try:
            self.canvas.delete(self.ScaleBarLine)
        except:
            pass
        try:
            self.canvas.delete(self.CanvasInformation)
        except:
            pass
        self.ScaleBarLine = self.canvas.create_line((x0,y0),(x1,y1),fill='white',width=thickness)
        self.CanvasInformation = self.canvas.create_text(((x0+x1)/2,y0-40/(bx1-bx0)*(bbox[2]-bbox[0])),font=('Helvetica',fontsize),fill='white',text=u'{} \u00C5\u207B\u00B9'.format(np.round(float(self.EntryText4.get()),1)))
        self.CalibrationStatus=1

    def label(self):
        positionx = 0.1
        positiony = 0.05
        fontsize = int(40*self.ZoomFactor)
        bbox = self.canvas.bbox(self.container)
        bx0,by0 = self.convert_coords(bbox[0],bbox[1])
        bx1,by1 = self.convert_coords(bbox[2],bbox[3])
        x0,y0 = bbox[0]+(bbox[2]-bbox[0])*positionx,bbox[1]+(bbox[3]-bbox[1])*positiony
        try:
            self.canvas.delete(self.CanvasLabel)
        except:
            pass
        self.CanvasLabel = self.canvas.create_text((x0,y0),font = ('Helvtica',fontsize),fill='white',text=u'Energy = {} keV\n\u03C6 = {}\u00B0'.format(np.round(float(self.EntryText1.get()),1),np.round(float(self.EntryText3.get()),1)))
        self.LabelStatus = 1

    def delete_calibration(self):
        self.CalibrationStatus=0
        self.LabelStatus=0
        try:
            self.canvas.delete(self.ScaleBarLine)
        except:
            pass
        try:
            self.canvas.delete(self.CanvasInformation)
        except:
            pass
        try:
            self.canvas.delete(self.CanvasLabel)
        except:
            pass

    def autoscroll(self,sbar,first,last):
        first,last = float(first),float(last)
        if first<=0 and last >=1:
            sbar.grid_remove()
        else:
            sbar.grid()
        sbar.set(first,last)

    def populate_tree(self,tree, node):
        if tree.set(node, "type") != 'directory':
            return
        path = tree.set(node, "fullpath")
        date = tree.set(node,"date")
        tree.delete(*tree.get_children(node))
        parent = tree.parent(node)
        special_dirs = [] if parent else glob.glob('.') + glob.glob('..')

        for p in special_dirs + os.listdir(path):
            ptype = None
            p = os.path.join(path, p).replace('\\', '/')
            if os.path.isdir(p): ptype = "directory"
            elif os.path.isfile(p): ptype = "file"

            fname = os.path.split(p)[1]
            iid = tree.insert(node, "end", text=fname, values=[p, ptype])
            mtime = localtime(os.path.getmtime(p))
            mdate = "{}/{}/{}".format(mtime.tm_mon,mtime.tm_mday,mtime.tm_year)
            tree.set(iid,"date",mdate)

            if ptype == 'directory':
                if fname not in ('.', '..'):
                    tree.insert(iid, 0, text="dummy")
                    tree.item(iid, text=fname)
            elif ptype == 'file':
                size = self.format_size(os.stat(p).st_size)
                tree.set(iid, "size", size)

    def populate_roots(self,tree):
        try:
            dirname,filename = os.path.split(self.CurrentFilePath)
            dir = dirname.replace('\\','/')
            mtime = localtime(os.path.getmtime(self.CurrentFilePath))
            FormatedTime = "{}/{}/{}".format(mtime.tm_mday,mtime.tm_mon,mtime.tm_year)
        except:
            dir = os.path.abspath('.').replace('\\', '/')
            mtime = localtime(os.path.getmtime(dir))
            FormatedTime = "{}/{}/{}".format(mtime.tm_mon,mtime.tm_mday,mtime.tm_year)
        node = tree.insert('', 'end',open=TRUE, text=dir, values=[dir, 'directory',FormatedTime])
        self.populate_tree(tree, node)

    def tree_update(self,event):
        tree = event.widget
        self.populate_tree(tree, tree.focus())

    def change_dir(self,event):
        tree = event.widget
        node = tree.focus()
        if tree.parent(node):
            path = os.path.abspath(tree.set(node, "fullpath"))
            if os.path.isdir(path):
                os.chdir(path)
                tree.delete(tree.get_children(''))
                self.populate_roots(tree)
            if os.path.isfile(path):
                self.DefaultPath = path
                self.img = self.read_image(self.DefaultPath)
                self.image = Image.new('L',(self.img.shape[1],self.img.shape[0]))
                self.uint16 = np.uint8(self.img/256)
                self.outpil = self.uint16.astype(self.uint16.dtype.newbyteorder("L")).tobytes()
                self.image.frombytes(self.outpil)
                self.show_image()
                self.delete_line()
                self.delete_calibration()

    def format_size(self,size):
        KB = 1024.0
        MB = KB*KB
        GB = MB*KB
        if size >= GB:
            return '{:,.1f} GB'.format(size/GB)
        if size >= MB:
            return '{:,.1f} MB'.format(size/MB)
        if size >= KB:
            return '{:,.1f} KB'.format(size/KB)
        return '{} bytes'.format(size)

    def choose_file(self):
        try:
            initialdir,filename = os.path.split(self.CurrentFilePath)
        except:
            initialdir = ''
            pass
        self.CurrentFilePath=filedialog.askopenfilename(initialdir=initialdir,title='Choose File')
        if self.CurrentFilePath =='':pass
        else:
            self.FileBrowser.delete(self.FileBrowser.get_children(''))
            self.populate_roots(self.FileBrowser)
            self.DefaultPath = self.CurrentFilePath
            self.img = self.read_image(self.DefaultPath)
            self.image = Image.new('L',(self.img.shape[1],self.img.shape[0]))
            self.uint16 = np.uint8(self.img/256)
            self.outpil = self.uint16.astype(self.uint16.dtype.newbyteorder("L")).tobytes()
            self.image.frombytes(self.outpil)
            self.show_image()
            self.delete_line()
            self.delete_calibration()
        return self.CurrentFilePath

    def get_center(self):
        #print(int(self.Ctr_X),int(self.Ctr_Y))
        return int(self.Ctr_X),int(self.Ctr_Y)

    def scroll_y(self, *args, **kwargs):
        ''' Scroll canvas vertically and redraw the image '''
        self.canvas.yview(*args, **kwargs)  # scroll vertically
        self.show_image()  # redraw the image

    def scroll_x(self, *args, **kwargs):
        ''' Scroll canvas horizontally and redraw the image '''
        self.canvas.xview(*args, **kwargs)  # scroll horizontally
        self.show_image()  # redraw the image

    def wheel(self, event):
        bbox = self.canvas.bbox(self.container)  # get image area
        if bbox[0] < self.canvas.canvasx(event.x) < bbox[2] and bbox[1] < self.canvas.canvasy(event.y) < bbox[3]:
            self.xx.append(int(self.canvas.canvasx(event.x)))
            self.yy.append(int(self.canvas.canvasy(event.y)))
        else: return  # zoom only inside image area

        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        self.scale = 1.0
        if event.num == 5 or event.delta == -120:  # scroll down
            i = min(self.width, self.height)
            if int(i * self.imscale) < 30:
                self.xx.pop()
                self.yy.pop()
                return  # image is less than 30 pixels
            self.imscale /= self.delta
            self.scale   /= self.delta
        if event.num == 4 or event.delta == 120:  # scroll up
            i = min(self.canvas.winfo_width(), self.canvas.winfo_height())
            if i < self.imscale:
                self.xx.pop()
                self.yy.pop()
                return  # image is less than 30 pixels
            self.imscale *= self.delta
            self.scale   *= self.delta
        self.scalehisto.append(self.scale)
        self.canvas.scale('all', self.xx[-1], self.yy[-1], self.scale, self.scale)  # rescale all canvas objects
        self.ZFtext.delete(1.0,END)
        self.ZoomFactor = np.prod(self.scalehisto)
        self.ZFtext.insert(1.0,'x {}'.format(np.round(self.ZoomFactor*self.ZoomFactor,3)))
        self.show_image()

    def show_image(self, event=None):

        ''' Show image on the Canvas '''
        bbox1 = self.canvas.bbox(self.container)  # get image area
        # Remove 1 pixel shift at the sides of the bbox1
        bbox1 = (bbox1[0] + 1, bbox1[1] + 1, bbox1[2] - 1, bbox1[3] - 1)
        bbox2 = (self.canvas.canvasx(0),  # get visible area of the canvas
                 self.canvas.canvasy(0),
                 self.canvas.canvasx(self.canvas.winfo_width()),
                 self.canvas.canvasy(self.canvas.winfo_height()))
        bbox = [min(bbox1[0], bbox2[0]), min(bbox1[1], bbox2[1]),  # get scroll region box
                max(bbox1[2], bbox2[2]), max(bbox1[3], bbox2[3])]
        if bbox[0] == bbox2[0] and bbox[2] == bbox2[2]:  # whole image in the visible area
            bbox[0] = bbox1[0]
            bbox[2] = bbox1[2]
        if bbox[1] == bbox2[1] and bbox[3] == bbox2[3]:  # whole image in the visible area
            bbox[1] = bbox1[1]
            bbox[3] = bbox1[3]
        self.canvas.configure(scrollregion=bbox)  # set scroll region
        x1 = max(bbox2[0] - bbox1[0], 0)  # get coordinates (x1,y1,x2,y2) of the image tile
        y1 = max(bbox2[1] - bbox1[1], 0)
        x2 = min(bbox2[2], bbox1[2]) - bbox1[0]
        y2 = min(bbox2[3], bbox1[3]) - bbox1[1]
        if int(x2 - x1) > 0 and int(y2 - y1) > 0:  # show image if it in the visible area
            x = min(int(x2 / self.imscale), self.width)   # sometimes it is larger on 1 pixel...
            y = min(int(y2 / self.imscale), self.height)  # ...and sometimes not
            image = self.image.crop((int(x1 / self.imscale), int(y1 / self.imscale), x, y))
            imagetk = ImageTk.PhotoImage(image.resize((int(x2 - x1), int(y2 - y1))))
            imageid = self.canvas.create_image(max(bbox2[0], bbox1[0]), max(bbox2[1], bbox1[1]),
                                               anchor='nw', image=imagetk)
            self.canvas.lift(imageid)  # set image into the top layer
            try:
                self.canvas.lift(self.LineOnCanvas)
            except:
                pass
            try:
                self.canvas.lift(self.RectOnCanvas)
            except:
                pass
            self.canvas.imagetk = imagetk  # keep an extra reference to prevent garbage-collection
        calibration_status,label_status = self.CalibrationStatus,self.LabelStatus
        self.delete_calibration()
        try:
            if calibration_status == 1:
                self.calibrate()
            if label_status == 1:
                self.label()
        except:
            pass

    def show_line_scan(self,LinePlot):
        """show line scan on the canvas"""
        loc=(0,0)
        figure_canvas_agg = FigureCanvasAgg(LinePlot)
        figure_canvas_agg.draw()
        figure_x, figure_y, figure_w, figure_h = LinePlot.bbox.bounds
        figure_w, figure_h = int(figure_w), int(figure_h)
        photo = tk.PhotoImage(master=self.LineScanCanvas, width=figure_w, height=figure_h)
        self.LineScanCanvas.create_image(loc[0] + figure_w/2, loc[1] + figure_h/2, image=photo,anchor=CENTER)
        tkagg.blit(photo, figure_canvas_agg.get_renderer()._renderer, colormode=2)
        self.LineStatus = 1
        return photo

    def click_coords(self,event):

        #Get the coordinates of the spot where double clicked
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        bbox = self.canvas.bbox(self.container)  # get image area
        if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]: pass  # Ok! Inside the image
        else: return  # Click effective only inside image area

        self.Ctr_X,self.Ctr_Y = self.convert_coords(x,y)
        self.CIlabel2['text']="({}, {})\n{}".format(np.int(self.Ctr_X),np.int(self.Ctr_Y),np.round(self.img[np.int(self.Ctr_Y),np.int(self.Ctr_X)]/65535,3))

    def canvas_mouse_coords(self,event):

        #Get the coordinates of the mouse on the main canvas while it moves
        x1 = self.canvas.canvasx(event.x)
        y1 = self.canvas.canvasy(event.y)
        bbox1 = self.canvas.bbox(self.container)  # get image area
        if bbox1[0] < x1 < bbox1[2] and bbox1[1] < y1 < bbox1[3]:pass
        else: return  # Show mouse motion only inside image area
        self.Mouse_X,self.Mouse_Y = self.convert_coords(x1,y1)
        self.CMIlabel['text']='x={}, y={}'.format(np.int(self.Mouse_X),np.int(self.Mouse_Y))

    def line_scan_canvas_mouse_coords(self,event):

        #Get the coordinates of the mouse on the line scan canvas while it moves
        x2 = self.LineScanCanvas.canvasx(event.x)
        y2 = self.LineScanCanvas.canvasy(event.y)
        bbox2 = self.LineScanCanvas.bbox(ALL)
        try:
            bx1,bx2,by1,by2 = bbox2[0]+(bbox2[2]-bbox2[0])*self.LineScanAxesPosition[0], bbox2[0]+(bbox2[2]-bbox2[0])*(self.LineScanAxesPosition[0]+self.LineScanAxesPosition[2]), bbox2[1]+(bbox2[3]-bbox2[1])*(1-(self.LineScanAxesPosition[1]+self.LineScanAxesPosition[3])), bbox2[1]+(bbox2[3]-bbox2[1])*(1-self.LineScanAxesPosition[1])
            if bx1 < x2 < bx2 and by1 < y2 < by2:pass
            else:
                self.LineScanCanvas['cursor']='left_ptr'
                return  # Show mouse motion only inside image area
            self.Mouse_X,self.Mouse_Y = (x2-bx1)*(self.LinePlotRangeX[1]-self.LinePlotRangeX[0])/(bx2-bx1)+self.LinePlotRangeX[0],(by2-y2)*(self.LinePlotRangeY[1]-self.LinePlotRangeY[0])/(by2-by1)+self.LinePlotRangeY[0]
            self.CMIlabel['text']='K= {}, Int.= {}'.format(np.round(self.Mouse_X,2),np.round(self.Mouse_Y,2))
            self.LineScanCanvas['cursor']='crosshair'
        except:
            self.LineScanCanvas['cursor']='left_ptr'
            pass


    def convert_coords(self,x,y):

        #This is the function that converts the coordinates back to its native coordinates on the RHEED pattern
        Xn=[]
        Yn=[]
        n1 = len(self.xx)+1
        n2 = len(self.scalehisto)+1
        for i in range(n1):
            Xn.append(0)
            Yn.append(0)
        Xn[n1-1],Yn[n1-1]=x,y
        for j in range(n1-1,0,-1):
            Xn[j-1]=(Xn[j]-self.xx[j-1])/self.scalehisto[j-1]+self.xx[j-1]
            Yn[j-1]=(Yn[j]-self.yy[j-1])/self.scalehisto[j-1]+self.yy[j-1]
        return Xn[0],Yn[0]

    def move_from(self, event):
        ''' Remember previous coordinates for scrolling with the mouse '''
        self.canvas.scan_mark(event.x, event.y)
        self.canvas['cursor'] = 'fleur'

    def move_to(self, event):
        ''' Drag (move) canvas to the new position '''
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        self.show_image()  # redraw the image

    def move_end(self,event):
        self.canvas['cursor'] = 'crosshair'

    def scan_from(self, event):
        ''' Remember previous coordinates for scrolling with the mouse '''
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.LineStartX,self.LineStartY = self.convert_coords(x,y)
        self.LineStartX0,self.LineStartY0 = x,y

    def scan_to(self, event):
        ''' Drag the cursor to the new position '''
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.LineEndX0,self.LineEndY0 = x,y
        bbox = self.canvas.bbox(self.container)  # get image area
        if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]: pass  # Ok! Inside the image
        else: return  # Show line scan only inside image area
        self.LineEndX,self.LineEndY = self.convert_coords(x,y)
        LineScanRadius,LineScanIntensities = self.get_line_scan(self.LineStartX,self.LineStartY,self.LineEndX,self.LineEndY)
        self.LinePlot = matplotlib.figure.Figure(figsize=(self.LineScanCanvas.winfo_width()/self.dpi,self.LineScanCanvas.winfo_height()/self.dpi))
        LinePlotAx = self.LinePlot.add_axes(self.LineScanAxesPosition)
        LinePlotAx.set_xlabel(r"$K (\AA^{-1})$")
        LinePlotAx.set_ylabel("Intensity (arb. units)")
        LinePlotAx.ticklabel_format(style='sci',scilimits=(0,0),axis='y',useMathText=TRUE)
        LinePlotAx.plot(LineScanRadius/(2269.06/np.sqrt(float(self.EntryText1.get()))/2/np.pi),LineScanIntensities/np.amax(np.amax(self.img)),'r-')
        self.LinePlotRangeX = LinePlotAx.get_xlim()
        self.LinePlotRangeY = LinePlotAx.get_ylim()
        self.delete_line()
        self.LineScanFigure = self.show_line_scan(self.LinePlot)
        self.CMIlabel['text']='x={}, y={}, length ={} \u00C5\u207B\u00B9'.format(np.int(self.LineEndX),np.int(self.LineEndY),np.round(LineScanRadius[-1]/(2269.06/np.sqrt(float(self.EntryText1.get()))/2/np.pi),2))
        self.LineOnCanvas = self.canvas.create_line((self.LineStartX0,self.LineStartY0),(self.LineEndX0,self.LineEndY0),fill='yellow',width=2)


    def scan_end(self,event):
        self.SaveLineStartX.append(self.LineStartX)
        self.SaveLineStartY.append(self.LineStartY)
        self.SaveLineEndX.append(self.LineEndX)
        self.SaveLineEndY.append(self.LineEndY)
        self.LineStartX,self.LineStartY = 0,0
        self.LineEndX,self.LineEndY = 0,0

    def delete_line(self,event=NONE):
        try:
            self.canvas.delete(self.LineOnCanvas)
            self.LineStatus = 0
            self.LineScanCanvas.delete('all')
        except:
            pass
        try:
            self.canvas.delete(self.RectOnCanvas)
            self.LineStatus = 0
            self.LineScanCanvas.delete('all')
        except:
            pass

    def integrate_from(self, event):
        ''' Remember previous coordinates for scrolling with the mouse '''
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.LineStartX,self.LineStartY = self.convert_coords(x,y)
        self.LineStartX0,self.LineStartY0 = x,y

    def integrate_to(self, event):
        ''' Drag the cursor to the new position '''
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.LineEndX0,self.LineEndY0 = x,y
        self.IntegralHalfWidth = int(int(self.IntegralWidth.get())*self.ZoomFactor)
        x0,y0,x1,y1,x2,y2,x3,y3 = 0,0,0,0,0,0,0,0
        bbox = self.canvas.bbox(self.container)  # get image area
        if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]: pass  # Ok! Inside the image
        else: return  # Show line integral only inside image area

        if self.LineEndY0 == self.LineStartY0:
            x0 = self.LineStartX0
            y0 = self.LineStartY0-self.IntegralHalfWidth
            x1 = self.LineStartX0
            y1 = self.LineStartY0+self.IntegralHalfWidth
            x2 = self.LineEndX0
            y2 = self.LineEndY0+self.IntegralHalfWidth
            x3 = self.LineEndX0
            y3 = self.LineEndY0-self.IntegralHalfWidth
        elif self.LineEndX0 ==self.LineStartX0:
            x0 = self.LineStartX0+self.IntegralHalfWidth
            y0 = self.LineStartY0
            x1 = self.LineStartX0-self.IntegralHalfWidth
            y1 = self.LineStartY0
            x2 = self.LineEndX0-self.IntegralHalfWidth
            y2 = self.LineEndY0
            x3 = self.LineEndX0+self.IntegralHalfWidth
            y3 = self.LineEndY0
        else:
            slope0 =(self.LineStartX0-self.LineEndX0)/(self.LineEndY0-self.LineStartY0)
            if abs(slope0) > 1:
                x0 = np.round(self.LineStartX0+1/slope0*self.IntegralHalfWidth).astype(int)
                y0 = self.LineStartY0+self.IntegralHalfWidth
                x1 = np.round(self.LineStartX0-1/slope0*self.IntegralHalfWidth).astype(int)
                y1 = self.LineStartY0-self.IntegralHalfWidth
                x2 = np.round(self.LineEndX0-1/slope0*self.IntegralHalfWidth).astype(int)
                y2 = self.LineEndY0-self.IntegralHalfWidth
                x3 = np.round(self.LineEndX0+1/slope0*self.IntegralHalfWidth).astype(int)
                y3 = self.LineEndY0+self.IntegralHalfWidth
            else:
                x0 = self.LineStartX0-self.IntegralHalfWidth
                y0 = np.round(self.LineStartY0-slope0*self.IntegralHalfWidth).astype(int)
                x1 = self.LineStartX0+self.IntegralHalfWidth
                y1 = np.round(self.LineStartY0+slope0*self.IntegralHalfWidth).astype(int)
                x2 = self.LineEndX0+self.IntegralHalfWidth
                y2 = np.round(self.LineEndY0+slope0*self.IntegralHalfWidth).astype(int)
                x3 = self.LineEndX0-self.IntegralHalfWidth
                y3 = np.round(self.LineEndY0-slope0*self.IntegralHalfWidth).astype(int)

        self.LineEndX,self.LineEndY = self.convert_coords(x,y)
        LineScanRadius,LineScanIntensities = self.get_line_integral(self.LineStartX,self.LineStartY,self.LineEndX,self.LineEndY)
        self.LinePlot = matplotlib.figure.Figure(figsize=(self.LineScanCanvas.winfo_width()/self.dpi,self.LineScanCanvas.winfo_height()/self.dpi))
        LinePlotAx = self.LinePlot.add_axes(self.LineScanAxesPosition)
        LinePlotAx.set_xlabel(r"$K (\AA^{-1})$")
        LinePlotAx.set_ylabel("Intensity (arb. units)")
        LinePlotAx.ticklabel_format(style='sci',scilimits=(0,0),axis='y',useMathText=TRUE)
        LinePlotAx.plot(LineScanRadius/(2269.06/np.sqrt(float(self.EntryText1.get()))/2/np.pi),LineScanIntensities/np.amax(np.amax(self.img)),'r-')
        self.LinePlotRangeX = LinePlotAx.get_xlim()
        self.LinePlotRangeY = LinePlotAx.get_ylim()
        self.delete_line()
        self.LineScanFigure = self.show_line_scan(self.LinePlot)
        self.CMIlabel['text']='x={}, y={}, length = {} \u00C5\u207B\u00B9'.format(np.int(self.LineEndX),np.int(self.LineEndY),np.round(LineScanRadius[-1]/(2269.06/np.sqrt(float(self.EntryText1.get()))/2/np.pi),2))
        self.RectOnCanvas = self.canvas.create_polygon(x0,y0,x1,y1,x2,y2,x3,y3,outline='yellow',fill='',width=2)


    def integrate_end(self,event):
        self.SaveLineStartX.append(self.LineStartX)
        self.SaveLineStartY.append(self.LineStartY)
        self.SaveLineEndX.append(self.LineEndX)
        self.SaveLineEndY.append(self.LineEndY)
        self.LineStartX,self.LineStartY = 0,0
        self.LineEndX,self.LineEndY = 0,0

    def line_scan_update(self):
        if self.LineStatus == 0:
            return
        if self.mode.get() == 'LS':
            LineScanRadius,LineScanIntensities = self.get_line_scan(self.SaveLineStartX[-1],self.SaveLineStartY[-1],self.SaveLineEndX[-1],self.SaveLineEndY[-1])
            self.LinePlot = matplotlib.figure.Figure(figsize=(self.LineScanCanvas.winfo_width()/self.dpi,self.LineScanCanvas.winfo_height()/self.dpi))
            LinePlotAx = self.LinePlot.add_axes(self.LineScanAxesPosition)
            LinePlotAx.set_xlabel(r"$K (\AA^{-1})$")
            LinePlotAx.set_ylabel("Intensity (arb. units)")
            LinePlotAx.ticklabel_format(style='sci',scilimits=(0,0),axis='y',useMathText=TRUE)
            LinePlotAx.plot(LineScanRadius/(2269.06/np.sqrt(float(self.EntryText1.get()))/2/np.pi),LineScanIntensities/np.amax(np.amax(self.img)),'r-')
            self.LinePlotRangeX = LinePlotAx.get_xlim()
            self.LinePlotRangeY = LinePlotAx.get_ylim()
            self.LineScanFigure = self.show_line_scan(self.LinePlot)
        elif self.mode.get()== 'LI':
            LineScanRadius,LineScanIntensities = self.get_line_integral(self.SaveLineStartX[-1],self.SaveLineStartY[-1],self.SaveLineEndX[-1],self.SaveLineEndY[-1])
            self.LinePlot = matplotlib.figure.Figure(figsize=(self.LineScanCanvas.winfo_width()/self.dpi,self.LineScanCanvas.winfo_height()/self.dpi))
            LinePlotAx = self.LinePlot.add_axes(self.LineScanAxesPosition)
            LinePlotAx.set_xlabel(r"$K (\AA^{-1})$")
            LinePlotAx.set_ylabel("Intensity (arb. units)")
            LinePlotAx.ticklabel_format(style='sci',scilimits=(0,0),axis='y',useMathText=TRUE)
            LinePlotAx.plot(LineScanRadius/(2269.06/np.sqrt(float(self.EntryText1.get()))/2/np.pi),LineScanIntensities/np.amax(np.amax(self.img)),'r-')
            self.LinePlotRangeX = LinePlotAx.get_xlim()
            self.LinePlotRangeY = LinePlotAx.get_ylim()
            self.LineScanFigure = self.show_line_scan(self.LinePlot)

    def get_line_scan(self,x0,y0,x1,y1):
        K_length = max(int(abs(x1-x0)+1),int(abs(y1-y0)+1))
        Kx = np.linspace(x0,x1,K_length)
        Ky = np.linspace(y0,y1,K_length)
        LineScanIntensities = np.zeros(len(Kx))
        for i in range(0,len(Kx)):
            LineScanIntensities[i] = self.img[int(Ky[i]),int(Kx[i])]
        LineScanRadius = np.linspace(0,math.sqrt((x1-x0)**2+(y1-y0)**2),len(Kx))
        return LineScanRadius,LineScanIntensities

    def get_line_integral(self,x0,y0,x1,y1):
        K_length = max(int(abs(x1-x0)+1),int(abs(y1-y0)+1))
        Kx = np.linspace(x0,x1,K_length)
        Ky = np.linspace(y0,y1,K_length)
        LineScanIntensities = np.zeros(len(Kx))
        for i in range(0,len(Kx)):
            for j in range(-self.IntegralHalfWidth,self.IntegralHalfWidth+1):
                if y1 == y0:
                    image_row = np.round(Ky[i]).astype(int)+j
                    image_column = np.round(Kx[i]).astype(int)
                elif x1 == x0:
                    image_row = np.round(Ky[i]).astype(int)
                    image_column = np.round(Kx[i]).astype(int)+j
                else:
                    slope =(x0-x1)/(y1-y0)
                    if abs(slope) > 1:
                        image_row = np.round(Ky[i]).astype(int)+j
                        image_column = np.round(Kx[i]+1/slope*j).astype(int)
                    else:
                        image_row = np.round(Ky[i]+slope*j).astype(int)
                        image_column = np.round(Kx[i]).astype(int)+j
                LineScanIntensities[i] += self.img[image_row,image_column]

        LineScanRadius = np.linspace(0,math.sqrt((x1-x0)**2+(y1-y0)**2),len(Kx))
        return LineScanRadius,LineScanIntensities

    def read_image(self,img_path): # Read the raw image and convert it to grayvalue images

        #---------------------- Input list ------------------------------------
        #       img_path: the path that stores the RHEED images
        #                 Default: img_path_PC
        #
        #---------------------- Output list -----------------------------------
        #       img:the matrix that stores the grayvales of the RHEED image
        #
        #----------------------------------------------------------------------

        #create an array that stores all image pathes
        img_raw = rawpy.imread(img_path)
        #Demosaicing
        img_rgb = img_raw.postprocess(demosaic_algorithm=rawpy.DemosaicAlgorithm.AHD,output_bps = 16,use_auto_wb = self.CheckStatus.get(),bright=self.ScaleVar1.get()/100)
        #Convert to grayvalue images
        img_bw = (0.21*img_rgb[:,:,0])+(0.72*img_rgb[:,:,1])+(0.07*img_rgb[:,:,2])
        #Crop the image
        img = img_bw[1200:2650,500:3100]
        return img

    def batch_read_image(img_path,nimg=0): # Read the raw image and convert it to grayvalue images

            #---------------------- Input list ------------------------------------
            #       img_path: the path that stores the RHEED images
            #                 Default: img_path_PC
            #
            #       nimg:     the RHEED image index
            #                 Default: 0
            #
            #---------------------- Output list -----------------------------------
            #       img:the matrix that stores the grayvales of the RHEED image
            #
            #----------------------------------------------------------------------

            #create an array that stores all image pathes
            image_list = []
            for filename in glob.glob(img_path_PC):
                    image_list.append(filename)
            #Read the raw *.nef images
            img_raw = rawpy.imread(image_list[nimg])
            #Demosaicing
            img_rgb = img_raw.postprocess(demosaic_algorithm=rawpy.DemosaicAlgorithm.AHD,output_bps = 16)
            #Convert to grayvalue images
            img_bw = (0.21*img_rgb[:,:,0])+(0.72*img_rgb[:,:,1])+(0.07*img_rgb[:,:,2])
            #Crop the image
            img = img_bw[1200:2650,500:3100]
            return img,image_list[nimg]

    def find_Xcenter(img):  #Find the X-center of the image

            #---------------------- Input list ------------------------------------
            #       img:the matrix that stores the grayvales of the RHEED image
            #
            #---------------------- Output list -----------------------------------
            #       Xoffset: the x-offset in order to go to the center
            #
            #----------------------------------------------------------------------

            CtrX = np.argmax(np.sum(img[center[1]-center[3]//2:center[1]+center[3]//2,center[0]-center[2]//2:center[0]+center[2]//2],axis=0,keepdims=1),axis=1)

            #Find the offset in X direction
            Xoffset = CtrX[0]+center[0]-center[2]//2

            return Xoffset

    def plot_RHEED_pattern(img,Xoffset,Yoffset,nimg=0,Kp=700):

            #---------------------- Input list ------------------------------------
            #       img: the matrix that stores the grayvales of the RHEED image
            #
            #       Xoffset: the x-offset in order to go to the center
            #
            #       Yoffset: the y-offset in order to go to the center
            #
            #       nimg: the RHEED image index
            #             Default: 0
            #
            #       Kp: ONLY USED WHEN DIRECTION IS 'HORIZONTAL', which defines
            #           the K_perp position
            #           Default: 500
            #
            #----------------------------------------------------------------------

            #Create a figure
            plt.figure()
            #plot the RHEED pattern
            im=plt.imshow(img,cmap = plt.cm.jet)
            ax1 = plt.axes()
            plt.title(r''.join(['$\phi = ',str(nimg*1.8),'^\circ$']),fontsize = 20)
            plt.axis([0,2600,1450,0])

            if direction == 'vertical':
                    #draw the line
                    plt.plot([Xoffset,Xoffset],[y1,y2],'wo-')
                    #draw the rectangle
                    p=patches.Rectangle((Xoffset-width//2,y1),width,y2-y1,fill=False,ls='--',ec='w')
            else:
                    plt.plot([Xoffset-length//2,Xoffset+length//2],[Kp,Kp],'wo-')
                    p=patches.Rectangle((Xoffset-length//2,Kp-width//2),length,width,fill=False,ls='--',ec='w')

            plt.colorbar(im,orientation = 'horizontal',format = '%4d')
            ax1.add_patch(p)
            ax1.set_xlabel(r'$K_{\||} (\AA^{-1})$',fontsize = 20)
            ax1.set_ylabel(r'$K_{\bot} (\AA^{-1})$',fontsize = 20)

            xticks = np.around((ax1.get_xticks()-Xoffset)/SF,1)
            ax1.set_xticklabels(xticks,fontsize = 20)
            yticks = np.around((ax1.get_yticks()-Yoffset)/SF,1)
            ax1.set_yticklabels(yticks,fontsize = 20)
            return im

    def get_line_profile(img, Xoffset=0,Kp=100,integral= True):

            #---------------------- Input list ------------------------------------
            #       img: the matrix that stores the grayvales of the RHEED image
            #
            #       Xoffset: the x-offset in order to go to the center
            #                Default:0
            #
            #       Kp: ONLY USED WHEN DIRECTION IS 'HORIZONTAL', which defines
            #                the K_perp position
            #                Default:100
            #
            #       integral: either TRUE or FALSE, which determine whether perform
            #                 the integral
            #                 Default: TRUE
            #
            #---------------------- Output list -----------------------------------
            #       AreaIntegral: the area integrated profile. ONLY WHEN INTEGRAL IS TRUE
            #       profile: the line profile. ONLY WHEN INTEGRAL IS FALSE
            #
            #----------------------------------------------------------------------

            if direction == 'vertical':
                    x = np.linspace(Xoffset,Xoffset,nos)
                    y = np.linspace(y1,y2,nos)

                    #extract line profile
                    profile = scipy.ndimage.map_coordinates(img,np.vstack((y,x)),order=0,cval = 100000.)
                    #print(profile.shape)

                    #extract the area integral
                    AreaIntegral = np.sum(img[y1:y2,Xoffset-width//2:Xoffset+width//2],axis=1,keepdims=1)
                    #print(AreaIntegral.shape)

            if direction == 'horizontal':
                    x = np.linspace(Xoffset-length//2,Xoffset+length//2,nos)
                    y = np.linspace(Kp,Kp,nos)

                    #extract line profile
                    profile = scipy.ndimage.map_coordinates(img,np.vstack((y,x)),order=0,cval = 100000.)
                    #print(profile.shape)

                    #extract the area integral
                    AreaIntegral = np.transpose(np.sum(img[Kp-width//2:Kp+width//2,Xoffset-length//2:Xoffset+length//2],axis=0,keepdims=1))
                    #print(AreaIntegral.shape)

            if integral:
                    return AreaIntegral
            else:
                    return profile

    def plot_line_profile(profile, nimg, Xoffset, Yoffset,Kp):

            #---------------------- Input list ------------------------------------
            #       profile: the line profile to be plotted
            #
            #       Xoffset: the x-offset in order to go to the center
            #
            #       Yoffset: ONLY USED WHEN DIRECTION IS HORIZONTAL. the y-offset in order to go to the center
            #
            #       Kp: ONLY USED WHEN DIRECTION IS HORIZONTAL. The K perpendicular
            #           position of the horizontal line scan
            #---------------------- Output list -----------------------------------
            #       Kx: the coordinates in Kx direction. ONLY WHEN DIRECTION IS HORIZONTAL.
            #       Ky: the coordinates in Ky direction. ONLY WHEN DIRECTION IS VERTICAL.
            #
            #----------------------------------------------------------------------

            profile_shape = profile.shape
            kx = np.linspace(-length//2,length//2,profile_shape[0])
            ky = np.linspace(y1-Yoffset,y2-Yoffset,profile_shape[0])


            #plot the line profile
            plt.figure()
            ax2 = plt.axes()
            if direction == 'vertical':
                    plt.plot(ky/SF,profile)
                    ax2.set_xlabel(r'$K_{\bot} (\AA^{-1})$',fontsize = 20)
            else:
                    plt.plot(kx/SF,profile)
                    plt.title(r''.join(['$\phi = ',str(nimg*1.8),'^\circ',',','K_{\perp} =',str(np.round((Kp-Yoffset)/SF,1)),' \AA^{-1}$']),fontsize = 20)
                    ax2.set_xlabel(r'$K_{\parallel} (\AA^{-1})$',fontsize = 20)

            plt.yscale('linear')
            ax2.set_ylabel('Intensity',fontsize = 20)
            ax2.ticklabel_format(style='sci',scilimits=(0,0),axis='both',format = '%2.1f')
            if direction == 'vertical':
                    return ky/SF
            else:
                    return kx/SF


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Gaussian Fit functions ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def gaussian(x,height, center,FWHM,offset):

            #---------------------- Input list ------------------------------------
            #       x: the X variable
            #
            #       height: the height of the Gaussian function
            #
            #       center: the center of the Gaussian function
            #
            #       FWHM: the full width at half maximum of the Gaussian function
            #
            #---------------------- Output list -----------------------------------
            #       gaussian: the gaussian function
            #
            #----------------------------------------------------------------------


            return height/(FWHM*math.sqrt(math.pi/(4*math.log(2))))*np.exp(-4*math.log(2)*(x - center)**2/(FWHM**2))+offset

    def five_gaussians(x,H1,H2,H3,H4,H5,C1,C2,C3,C4,C5,W1,W2,W3,W4,W5,offset):

            #---------------------- Input list ------------------------------------
            #       x: the X variable
            #
            #       H1~H5: the five-element array that stores the heights of the Gaussian function
            #
            #       C1~C5: the five-element array that stores the centers of the Gaussian function
            #
            #       W1~W5: the five-element array that stores the full width at half maximums of the Gaussian function
            #
            #---------------------- Output list -----------------------------------
            #       five_gaussians: the function that adds five Gaussian functions
            #                       together
            #
            #----------------------------------------------------------------------

            return (gaussian(x,H1,C1,W1,offset=0)+
                    gaussian(x,H2,C2,W2,offset=0)+
                    gaussian(x,H3,C3,W3,offset=0)+
                    gaussian(x,H4,C4,W5,offset=0)+
                    gaussian(x,H5,C5,W5,offset=0)+offset)

    def nine_gaussians(x,H1,H2,H3,H4,H5,H6,H7,H8,H9,C1,C2,C3,C4,C5,C6,C7,C8,C9,W1,W2,W3,W4,W5,W6,W7,W8,W9,offset):

            #---------------------- Input list ------------------------------------
            #       x: the X variable
            #
            #       H1~H9: the nine-element array that stores the heights of the Gaussian function
            #
            #       C1~C9: the nine-element array that stores the centers of the Gaussian function
            #
            #       W1~W9: the nine-element array that stores the full width at half maximums of the Gaussian function
            #
            #---------------------- Output list -----------------------------------
            #       nine_gaussians: the function that adds seven Gaussian functions
            #                       together
            #
            #----------------------------------------------------------------------

            return (gaussian(x,H1,C1,W1,offset=0)+
                    gaussian(x,H2,C2,W2,offset=0)+
                    gaussian(x,H3,C3,W3,offset=0)+
                    gaussian(x,H4,C4,W4,offset=0)+
                    gaussian(x,H5,C5,W5,offset=0)+
                    gaussian(x,H6,C6,W6,offset=0)+
                    gaussian(x,H7,C7,W7,offset=0)+
                    gaussian(x,H8,C8,W8,offset=0)+
                    gaussian(x,H9,C9,W9,offset=0)+offset)

    def nine_gaussians_bg(x,H1,H2,H3,H4,H5,H6,H7,H8,H9,Hbg,C1,C2,C3,C4,C5,C6,C7,C8,C9,Cbg,W1,W2,W3,W4,W5,W6,W7,W8,W9,Wbg,offset):

            #---------------------- Input list ------------------------------------
            #       x: the X variable
            #
            #       H1~H9: the nine-element array that stores the heights of the Gaussian function
            #
            #       C1~C9: the nine-element array that stores the centers of the Gaussian function
            #
            #       W1~W9: the nine-element array that stores the full width at half maximums of the Gaussian function
            #
            #       Hbg,Cbg,Wbg, height, center position and the full width at half maximums of the Gaussian background
            #
            #---------------------- Output list -----------------------------------
            #       nine_gaussians: the function that adds seven Gaussian functions
            #                       together
            #
            #----------------------------------------------------------------------

            return (gaussian(x,H1,C1,W1,offset=0)+
                    gaussian(x,H2,C2,W2,offset=0)+
                    gaussian(x,H3,C3,W3,offset=0)+
                    gaussian(x,H4,C4,W4,offset=0)+
                    gaussian(x,H5,C5,W5,offset=0)+
                    gaussian(x,H6,C6,W6,offset=0)+
                    gaussian(x,H7,C7,W7,offset=0)+
                    gaussian(x,H8,C8,W8,offset=0)+
                    gaussian(x,H9,C9,W9,offset=0)+
                    gaussian(x,Hbg,Cbg,Wbg,offset=0)+offset)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Main Execution Function ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def main():
        root = Tk()
        root.title('RHEED pattern')
        #root.geometry('{}x{}'.format(img.shape[1]//2,img.shape[0]//2))
        root.state("zoomed")
        RHEED = RHEED_GUI(root)
        root.mainloop()
if __name__ == '__main__':
        #execute only if run as a script
        main()
