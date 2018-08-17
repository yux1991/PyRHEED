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
from tkinter import messagebox
from PIL import Image, ImageTk,ImageOps,ImageDraw,ImageFont
from array import array
from io import BytesIO
from matplotlib.mathtext import math_to_image
from matplotlib.font_manager import FontProperties
from scipy.special import wofz

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Classes ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class io():
    """this class is used to realize basic input and output operations"""

    def choose_file(self,FileBrowser,DefaultPath,CurrentFilePath):
        try:
            initialdir,filename = os.path.split(CurrentFilePath)
        except:
            initialdir = ''
            pass
        CurrentFilePath=filedialog.askopenfilename(initialdir=initialdir,filetypes=(("Raw File (*.nef)","*.nef"),("All Files (*.*)","*.*")),title='Choose File')
        if CurrentFilePath =='':pass
        else:
            FileBrowser.delete(FileBrowser.get_children(''))
            self.populate_roots(FileBrowser)
            DefaultPath = CurrentFilePath
            DefaultFileName = os.path.basename(self.DefaultPath)
            main_window.master.title('PyRHEED /'+self.DefaultFileName)
            self.img = self.read_image(self.DefaultPath)
            self.convert_image()
            self.show_image()
            self.delete_line()
            self.delete_calibration()
        return self.CurrentFilePath


    def choose_2D_mapping_save_dir(self):
        self.save_2D_mapping_path = filedialog.asksaveasfilename(title="Save As",initialfile='2D Mapping.txt',filetypes=(("TXT (*.txt)","*.txt"),("All Files (*.*)","*.*")))
        self.ShowDir['text']='The destination is:\n'+self.save_2D_mapping_path

    def make_image(self):
        self.img = self.read_image(self.DefaultPath)
        self.convert_image()
        self.AnnotatedImage = self.image.copy()

    def adjust_update(self):
        self.img = self.read_image(self.DefaultPath)
        self.convert_image()
        self.show_image()
        try:
            self.line_scan_update()
        except:
            pass

    def adjust_reset(self):
        self.Brightness.set(30)
        self.UserBlack.set(50)
        self.EnableAutoWB.set(0)
        self.img = self.read_image(self.DefaultPath)
        self.convert_image()
        self.show_image()
        self.AdjustLabel1['text'] = 'Brightness ({})'.format(round(self.Brightness.get()/100,2))
        self.AdjustLabel2['text'] = 'Black Level ({})'.format(self.UserBlack.get())
        try:
            self.line_scan_update()
        except:
            pass

    def calibrate(self):
        thickness = 2
        position = 0.05
        fontsize = int(40*self.ZoomFactor)
        bbox = self.canvas.bbox(self.container)
        bx0,by0 = self.convert_coords(bbox[0],bbox[1])
        bx1,by1 = self.convert_coords(bbox[2],bbox[3])
        x0,y0,y1 = bbox[0]+(bbox[2]-bbox[0])*position,bbox[3]-(bbox[3]-bbox[1])*position,bbox[3]-(bbox[3]-bbox[1])*position
        positionx = 0.1
        positiony = 0.05
        x1 = x0+float(self.ScaleBarLength.get())*(float(self.Sensitivity.get())/np.sqrt(float(self.ElectronEnergy.get())))/(bx1-bx0)*(bbox[2]-bbox[0])
        self.AnnotatedImage = self.image.copy()
        try:
            self.canvas.delete(self.ScaleBarLine)
        except:
            pass
        try:
            self.canvas.delete(self.ScaleBarText)
        except:
            pass
        self.ScaleBarLine = self.canvas.create_line((x0,y0),(x1,y1),fill='white',width=thickness)
        self.ScaleBarText = self.canvas.create_text(((x0+x1)/2,y0-40/(bx1-bx0)*(bbox[2]-bbox[0])),font=('Helvetica',fontsize),fill='white',text=u'{} \u00C5\u207B\u00B9'.format(np.round(float(self.ScaleBarLength.get()),1)))
        self.EnableCalibration=1
        ibox = self.AnnotatedImage.getbbox()
        ix0,iy0,iy1 = ibox[0]+(ibox[2]-ibox[0])*position,ibox[3]-(ibox[3]-ibox[1])*position,ibox[3]-(ibox[3]-ibox[1])*position
        ix1 = ix0+float(self.ScaleBarLength.get())*(float(self.Sensitivity.get())/np.sqrt(float(self.ElectronEnergy.get())))
        draw = ImageDraw.Draw(self.AnnotatedImage)
        draw.line([(ix0,iy0),(ix1,iy1)],fill='white',width=thickness*2)
        draw.text(((ix0+ix1)/2-80,iy0-60),font=ImageFont.truetype(self.TrueTypeFont,40),fill='white',text=u'{} \u00C5\u207B\u00B9'.format(np.round(float(self.ScaleBarLength.get()),1)))
        if self.EnableCanvasLabel ==1:
            x0_2,y0_2 = ibox[0]+(ibox[2]-ibox[0])*positionx,ibox[1]+(ibox[3]-ibox[1])*positiony
            draw.text((x0_2-100,y0_2),font = ImageFont.truetype(self.TrueTypeFont,40),fill='white',text=u'Energy = {} keV\n\u03C6 = {}\u00B0'.format(np.round(float(self.ElectronEnergy.get()),1),np.round(float(self.Azimuth.get()),1)))

    def label(self):
        thickness = 2
        position = 0.05
        fontsize = int(40*self.ZoomFactor)
        bbox = self.canvas.bbox(self.container)
        bx0,by0 = self.convert_coords(bbox[0],bbox[1])
        bx1,by1 = self.convert_coords(bbox[2],bbox[3])
        x0,y0,y1 = bbox[0]+(bbox[2]-bbox[0])*position,bbox[3]-(bbox[3]-bbox[1])*position,bbox[3]-(bbox[3]-bbox[1])*position
        positionx = 0.1
        positiony = 0.05
        x0_2,y0_2 = bbox[0]+(bbox[2]-bbox[0])*positionx,bbox[1]+(bbox[3]-bbox[1])*positiony
        x1 = x0+float(self.ScaleBarLength.get())*(float(self.Sensitivity.get())/np.sqrt(float(self.ElectronEnergy.get())))/(bx1-bx0)*(bbox[2]-bbox[0])
        self.AnnotatedImage = self.image.copy()
        try:
            self.canvas.delete(self.CanvasLabel)
        except:
            pass
        self.CanvasLabel = self.canvas.create_text((x0_2,y0_2),font = ('Helvtica',fontsize),fill='white',text=u'Energy = {} keV\n\u03C6 = {}\u00B0'.format(np.round(float(self.ElectronEnergy.get()),1),np.round(float(self.Azimuth.get()),1)))
        self.EnableCanvasLabel = 1
        ibox = self.AnnotatedImage.getbbox()
        ix0,iy0,iy1 = ibox[0]+(ibox[2]-ibox[0])*position,ibox[3]-(ibox[3]-ibox[1])*position,ibox[3]-(ibox[3]-ibox[1])*position
        ix0_2,iy0_2 = ibox[0]+(ibox[2]-ibox[0])*positionx,ibox[1]+(ibox[3]-ibox[1])*positiony
        ix1 = ix0+float(self.ScaleBarLength.get())*(float(self.Sensitivity.get())/np.sqrt(float(self.ElectronEnergy.get())))
        draw = ImageDraw.Draw(self.AnnotatedImage)
        draw.text((ix0_2-100,iy0_2),font = ImageFont.truetype(self.TrueTypeFont,40),fill='white',text=u'Energy = {} keV\n\u03C6 = {}\u00B0'.format(np.round(float(self.ElectronEnergy.get()),1),np.round(float(self.Azimuth.get()),1)))
        if self.EnableCalibration ==1:
            draw.line([(ix0,iy0),(ix1,iy1)],fill='white',width=thickness*2)
            draw.text(((ix0+ix1)/2-80,iy0-60),font=ImageFont.truetype(self.TrueTypeFont,40),fill='white',text=u'{} \u00C5\u207B\u00B9'.format(np.round(float(self.ScaleBarLength.get()),1)))

    def delete_calibration(self):
        self.EnableCalibration=0
        self.EnableCanvasLabel=0
        try:
            self.canvas.delete(self.ScaleBarLine)
        except:
            pass
        try:
            self.canvas.delete(self.ScaleBarText)
        except:
            pass
        try:
            self.canvas.delete(self.CanvasLabel)
        except:
            pass
        self.AnnotatedImage = self.image.copy()

    def brightness_update(self,evt):
        self.CurrentBrightness = round(float(evt)/100,2)
        self.AdjustLabel1['text'] = 'Brightness ({})'.format(self.CurrentBrightness)

    def user_black_update(self,evt):
        self.CurrentBlackLevel = int(float(evt))
        self.AdjustLabel2['text'] = 'Black Level ({})'.format(self.CurrentBlackLevel)

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
                self.DefaultFileName = os.path.basename(self.DefaultPath)
                self.master.title('PyRHEED /'+self.DefaultFileName)
                self.img = self.read_image(self.DefaultPath)
                self.convert_image()
                self.show_image()
                self.delete_line()
                self.delete_calibration()


    def save_as_plain_image(self):
        self.save_image_path = filedialog.asksaveasfilename(title="Save As",filetypes=(("JPEG (*.jpeg)","*.jpeg"),("TIFF (*.tif)","*.tif"),("PNG (*.png)","*.png"),("GIF (*.gif)","*.gif"),("All Files (*.*)","*.*")))
        if self.save_image_path == '':pass
        else:
            self.image.save(self.save_image_path)

    def save_as_annotated_image(self):
        self.save_image_path = filedialog.asksaveasfilename(title="Save As",filetypes=(("JPEG (*.jpeg)","*.jpeg"),("TIFF (*.tif)","*.tif"),("PNG (*.png)","*.png"),("GIF (*.gif)","*.gif"),("All Files (*.*)","*.*")))
        if self.save_image_path == '':pass
        else:
            self.AnnotatedImage.save(self.save_image_path)

    def show_image(self, event=None):

        ''' Show image on the Canvas '''
        bbox,bbox1,bbox2 = self.canvas_configure()
        x1 = max(bbox2[0] - bbox1[0], 0)  # get coordinates (x1,y1,x2,y2) of the image tile
        y1 = max(bbox2[1] - bbox1[1], 0)
        x2 = min(bbox2[2], bbox1[2]) - bbox1[0]
        y2 = min(bbox2[3], bbox1[3]) - bbox1[1]
        if int(x2 - x1) > 0 and int(y2 - y1) > 0:  # show image if it in the visible area
            x = min(int(x2 / self.imscale), self.image_crop[3]-self.image_crop[2])   # sometimes it is larger on 1 pixel...
            y = min(int(y2 / self.imscale), self.image_crop[1]-self.image_crop[0])  # ...and sometimes not
            self.CroppedImage = self.image.crop((int(x1 / self.imscale), int(y1 / self.imscale), x, y))
            imagetk = ImageTk.PhotoImage(self.CroppedImage.resize((int(x2 - x1), int(y2 - y1))))
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
            try:
                self.canvas.lift(self.ArcOnCanvas1)
                self.canvas.lift(self.ArcOnCanvas2)
                self.canvas.lift(self.ArcOnCanvas3)
            except:
                pass
            self.canvas.imagetk = imagetk  # keep an extra reference to prevent garbage-collection
        self.AnnotatedImage = self.image.copy()
        calibration_status,label_status = self.EnableCalibration,self.EnableCanvasLabel
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
        if self.mode.get() == 'PF':pass
        else:
            self.EnableCanvasLines = 1

    def click_coords(self,event):

        #Get the coordinates of the spot where double clicked
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        bbox = self.canvas.bbox(self.container)  # get image area
        if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]: pass  # Ok! Inside the image
        else: return  # Click effective only inside image area

        self.Ctr_X,self.Ctr_Y = self.convert_coords(x,y)
        self.CanvasCtr_X,self.CanvasCtr_Y = x,y
        self.ChoosedSpotEntry['text']="({}, {})\n{}".format(np.int(self.Ctr_X),np.int(self.Ctr_Y),np.round(self.img[np.int(self.Ctr_Y),np.int(self.Ctr_X)]/65535,3))

        if self.mode.get() == 'PF':
            self.plot_arc()
        self.CenterChosen = 1

    def delete_line(self,event=NONE):
        try:
            self.canvas.delete(self.LineOnCanvas)
            self.EnableCanvasLines = 0
            self.LineOrRect.set('None')
            self.LineScanCanvas.delete('all')
        except:
            pass
        try:
            self.canvas.delete(self.RectOnCanvas)
            self.EnableCanvasLines = 0
            self.LineOrRect.set('None')
            self.LineScanCanvas.delete('all')
        except:
            pass
        try:
            self.canvas.delete(self.ArcOnCanvas1)
            self.canvas.delete(self.ArcOnCanvas2)
            self.canvas.delete(self.ArcOnCanvas3)
            self.EnableCanvasLines = 0
            self.LineOrRect.set('None')
            self.LineScanCanvas.delete('all')
        except:
            pass

    def PFRadius_update(self,evt):
        try:
            self.RadiusLabel['text'] ='Radius ({} \u00C5\u207B\u00B9)'.format(np.round(self.PFRadius.get()/(float(self.Sensitivity.get())/np.sqrt(float(self.ElectronEnergy.get()))),2))
        except:
            pass
        if self.mode.get()=='PF':
            self.plot_arc()

    def integral_width_update(self,evt):
        self.WidthEntryText.set('{}'.format(self.IntegralWidth.get()))
        try:
            self.IntegralWidthLabel['text']='Integral Half Width ({} \u00C5\u207B\u00B9)'.format(np.round(self.IntegralWidth.get()/(float(self.Sensitivity.get())/np.sqrt(float(self.ElectronEnergy.get()))),2))
        except:
            pass
        if self.LineOrRect.get() =='Arc':
            self.plot_arc()
        elif self.LineOrRect.get() =='Rect':
            self.plot_rectangle()

    def PFChiRange_update(self,evt):
        try:
            self.ChiRangeLabel['text'] = 'Chi Range ({}\u00B0)'.format(self.ChiRange.get())
        except:
            pass
        if self.mode.get()=='PF':
            self.plot_arc()

    def PFTilt_update(self,evt):
        try:
            self.TiltLabel['text'] = 'Tilt Angle ({}\u00B0)'.format(np.round(self.PFTilt.get(),1))
        except:
            pass
        if self.mode.get()=='PF':
            self.plot_arc()

    def profile_update(self):
        if self.EnableCanvasLines==1:
            self.mode.set('LI')
            self.choose_mode()
            try:
                self.plot_rectangle()
            except:
                pass
            self.line_scan_update()
        elif self.mode.get() == 'PF':
            try:
                self.canvas.delete(self.ArcOnCanvas1)
                self.canvas.delete(self.ArcOnCanvas2)
                self.canvas.delete(self.ArcOnCanvas3)
            except:
                pass
            self.plot_arc()
            self.plot_chi_scan()

    def plot_rectangle(self):
        if int(int(self.IntegralWidth.get())*self.ZoomFactor) == 0:
            self.IntegralHalfWidth = 1
        else:
            self.IntegralHalfWidth = int(int(self.IntegralWidth.get())*self.ZoomFactor)
        self.SaveRegionWidth.append(self.IntegralWidth.get())
        x0,y0,x1,y1,x2,y2,x3,y3 = self.get_rectangle_position()
        try:
            self.canvas.delete(self.LineOnCanvas)
        except:
            pass
        try:
            self.canvas.delete(self.RectOnCanvas)
        except:
            pass
        self.RectOnCanvas = self.canvas.create_polygon(x0,y0,x1,y1,x2,y2,x3,y3,outline='yellow',fill='',width=2)
        self.LineOrRect.set('Rect')

    def press_up(self,event):
        if self.EnableCanvasLines==1:
            if int(int(self.IntegralWidth.get())*self.ZoomFactor) == 0:
                self.IntegralHalfWidth = 1
            else:
                self.IntegralHalfWidth = int(int(self.IntegralWidth.get())*self.ZoomFactor)
            try:
                self.SaveLineStartX.append(self.SaveLineStartX[-1])
                self.SaveLineStartY.append(self.SaveLineStartY[-1]-1*self.MoveStep.get())
                self.SaveLineEndX.append(self.SaveLineEndX[-1])
                self.SaveLineEndY.append(self.SaveLineEndY[-1]-1*self.MoveStep.get())
                self.SaveLineStartX0.append(self.SaveLineStartX0[-1])
                self.SaveLineStartY0.append(self.SaveLineStartY0[-1]-self.ZoomFactor*self.MoveStep.get())
                self.SaveLineEndX0.append(self.SaveLineEndX0[-1])
                self.SaveLineEndY0.append(self.SaveLineEndY0[-1]-self.ZoomFactor*self.MoveStep.get())
                self.LineStartX0 = self.SaveLineStartX0[-1]
                self.LineStartY0 = self.SaveLineStartY0[-1]
                self.LineEndX0 = self.SaveLineEndX0[-1]
                self.LineEndY0 = self.SaveLineEndY0[-1]
                self.line_scan_update()
                if self.LineOrRect.get() == 'Line':
                    self.canvas.delete(self.LineOnCanvas)
                    self.LineOnCanvas = self.canvas.create_line((self.SaveLineStartX0[-1],self.SaveLineStartY0[-1]),(self.SaveLineEndX0[-1],self.SaveLineEndY0[-1]),fill='yellow',width=2)
                elif self.LineOrRect.get() == 'Rect':
                    x0,y0,x1,y1,x2,y2,x3,y3 = self.get_rectangle_position()
                    self.canvas.delete(self.RectOnCanvas)
                    self.RectOnCanvas = self.canvas.create_polygon(x0,y0,x1,y1,x2,y2,x3,y3,outline='yellow',fill='',width=2)
                else:
                    pass
                self.canvas.update_idletasks()
                self.StartEntryText.set("{}, {}".format(np.int(self.SaveLineStartX[-1]),np.int(self.SaveLineStartY[-1])))
                self.EndEntryText.set("{}, {}".format(np.int(self.SaveLineEndX[-1]),np.int(self.SaveLineEndY[-1])))
                self.WidthEntryText.set("{}".format(np.int(self.SaveRegionWidth[-1])))
            except:
                pass
        elif self.LineOrRect.get() == 'Arc':
                self.CanvasCtr_Y -=1*self.MoveStep.get()*self.ZoomFactor
                self.canvas.delete(self.ArcOnCanvas1)
                self.canvas.delete(self.ArcOnCanvas2)
                self.canvas.delete(self.ArcOnCanvas3)
                self.plot_arc()
                self.Ctr_Y -= self.MoveStep.get()

    def press_down(self,event):
        if self.EnableCanvasLines==1:
            if int(int(self.IntegralWidth.get())*self.ZoomFactor) == 0:
                self.IntegralHalfWidth = 1
            else:
                self.IntegralHalfWidth = int(int(self.IntegralWidth.get())*self.ZoomFactor)
            try:
                self.SaveLineStartX.append(self.SaveLineStartX[-1])
                self.SaveLineStartY.append(self.SaveLineStartY[-1]+1*self.MoveStep.get())
                self.SaveLineEndX.append(self.SaveLineEndX[-1])
                self.SaveLineEndY.append(self.SaveLineEndY[-1]+1*self.MoveStep.get())
                self.SaveLineStartX0.append(self.SaveLineStartX0[-1])
                self.SaveLineStartY0.append(self.SaveLineStartY0[-1]+self.ZoomFactor*self.MoveStep.get())
                self.SaveLineEndX0.append(self.SaveLineEndX0[-1])
                self.SaveLineEndY0.append(self.SaveLineEndY0[-1]+self.ZoomFactor*self.MoveStep.get())
                self.LineStartX0 = self.SaveLineStartX0[-1]
                self.LineStartY0 = self.SaveLineStartY0[-1]
                self.LineEndX0 = self.SaveLineEndX0[-1]
                self.LineEndY0 = self.SaveLineEndY0[-1]
                self.line_scan_update()
                if self.LineOrRect.get() == 'Line':
                    self.canvas.delete(self.LineOnCanvas)
                    self.LineOnCanvas = self.canvas.create_line((self.SaveLineStartX0[-1],self.SaveLineStartY0[-1]),(self.SaveLineEndX0[-1],self.SaveLineEndY0[-1]),fill='yellow',width=2)
                elif self.LineOrRect.get() == 'Rect':
                    x0,y0,x1,y1,x2,y2,x3,y3 = self.get_rectangle_position()
                    self.canvas.delete(self.RectOnCanvas)
                    self.RectOnCanvas = self.canvas.create_polygon(x0,y0,x1,y1,x2,y2,x3,y3,outline='yellow',fill='',width=2)
                else:
                    pass
                self.canvas.update_idletasks()
                self.StartEntryText.set("{}, {}".format(np.int(self.SaveLineStartX[-1]),np.int(self.SaveLineStartY[-1])))
                self.EndEntryText.set("{}, {}".format(np.int(self.SaveLineEndX[-1]),np.int(self.SaveLineEndY[-1])))
                self.WidthEntryText.set("{}".format(np.int(self.SaveRegionWidth[-1])))
            except:
                pass
        elif self.LineOrRect.get() == 'Arc':
                self.CanvasCtr_Y +=1*self.MoveStep.get()*self.ZoomFactor
                self.canvas.delete(self.ArcOnCanvas1)
                self.canvas.delete(self.ArcOnCanvas2)
                self.canvas.delete(self.ArcOnCanvas3)
                self.plot_arc()
                self.Ctr_Y += self.MoveStep.get()

    def press_left(self,event):
        if self.EnableCanvasLines==1:
            if int(int(self.IntegralWidth.get())*self.ZoomFactor) == 0:
                self.IntegralHalfWidth = 1
            else:
                self.IntegralHalfWidth = int(int(self.IntegralWidth.get())*self.ZoomFactor)
            try:
                self.SaveLineStartX.append(self.SaveLineStartX[-1]-1*self.MoveStep.get())
                self.SaveLineStartY.append(self.SaveLineStartY[-1])
                self.SaveLineEndX.append(self.SaveLineEndX[-1]-1*self.MoveStep.get())
                self.SaveLineEndY.append(self.SaveLineEndY[-1])
                self.SaveLineStartX0.append(self.SaveLineStartX0[-1]-self.ZoomFactor*self.MoveStep.get())
                self.SaveLineStartY0.append(self.SaveLineStartY0[-1])
                self.SaveLineEndX0.append(self.SaveLineEndX0[-1]-self.ZoomFactor*self.MoveStep.get())
                self.SaveLineEndY0.append(self.SaveLineEndY0[-1])
                self.LineStartX0 = self.SaveLineStartX0[-1]
                self.LineStartY0 = self.SaveLineStartY0[-1]
                self.LineEndX0 = self.SaveLineEndX0[-1]
                self.LineEndY0 = self.SaveLineEndY0[-1]
                self.line_scan_update()
                if self.LineOrRect.get() == 'Line':
                    self.canvas.delete(self.LineOnCanvas)
                    self.LineOnCanvas = self.canvas.create_line((self.SaveLineStartX0[-1],self.SaveLineStartY0[-1]),(self.SaveLineEndX0[-1],self.SaveLineEndY0[-1]),fill='yellow',width=2)
                elif self.LineOrRect.get() == 'Rect':
                    x0,y0,x1,y1,x2,y2,x3,y3 = self.get_rectangle_position()
                    self.canvas.delete(self.RectOnCanvas)
                    self.RectOnCanvas = self.canvas.create_polygon(x0,y0,x1,y1,x2,y2,x3,y3,outline='yellow',fill='',width=2)
                else:
                    pass
                self.canvas.update_idletasks()
                self.StartEntryText.set("{}, {}".format(np.int(self.SaveLineStartX[-1]),np.int(self.SaveLineStartY[-1])))
                self.EndEntryText.set("{}, {}".format(np.int(self.SaveLineEndX[-1]),np.int(self.SaveLineEndY[-1])))
                self.WidthEntryText.set("{}".format(np.int(self.SaveRegionWidth[-1])))
            except:
                pass
        elif self.LineOrRect.get() == 'Arc':
                self.CanvasCtr_X -=1*self.MoveStep.get()*self.ZoomFactor
                self.canvas.delete(self.ArcOnCanvas1)
                self.canvas.delete(self.ArcOnCanvas2)
                self.canvas.delete(self.ArcOnCanvas3)
                self.plot_arc()
                self.Ctr_X -= self.MoveStep.get()

    def press_right(self,event):
        if self.EnableCanvasLines==1:
            if int(int(self.IntegralWidth.get())*self.ZoomFactor) == 0:
                self.IntegralHalfWidth = 1
            else:
                self.IntegralHalfWidth = int(int(self.IntegralWidth.get())*self.ZoomFactor)
            try:
                self.SaveLineStartX.append(self.SaveLineStartX[-1]+1*self.MoveStep.get())
                self.SaveLineStartY.append(self.SaveLineStartY[-1])
                self.SaveLineEndX.append(self.SaveLineEndX[-1]+1*self.MoveStep.get())
                self.SaveLineEndY.append(self.SaveLineEndY[-1])
                self.SaveLineStartX0.append(self.SaveLineStartX0[-1]+self.ZoomFactor*self.MoveStep.get())
                self.SaveLineStartY0.append(self.SaveLineStartY0[-1])
                self.SaveLineEndX0.append(self.SaveLineEndX0[-1]+self.ZoomFactor*self.MoveStep.get())
                self.SaveLineEndY0.append(self.SaveLineEndY0[-1])
                self.LineStartX0 = self.SaveLineStartX0[-1]
                self.LineStartY0 = self.SaveLineStartY0[-1]
                self.LineEndX0 = self.SaveLineEndX0[-1]
                self.LineEndY0 = self.SaveLineEndY0[-1]
                self.line_scan_update()
                if self.LineOrRect.get() == 'Line':
                    self.canvas.delete(self.LineOnCanvas)
                    self.LineOnCanvas = self.canvas.create_line((self.SaveLineStartX0[-1],self.SaveLineStartY0[-1]),(self.SaveLineEndX0[-1],self.SaveLineEndY0[-1]),fill='yellow',width=2)
                elif self.LineOrRect.get() == 'Rect':
                    x0,y0,x1,y1,x2,y2,x3,y3 = self.get_rectangle_position()
                    self.canvas.delete(self.RectOnCanvas)
                    self.RectOnCanvas = self.canvas.create_polygon(x0,y0,x1,y1,x2,y2,x3,y3,outline='yellow',fill='',width=2)
                else:
                    pass
                self.canvas.update_idletasks()
                self.StartEntryText.set("{}, {}".format(np.int(self.SaveLineStartX[-1]),np.int(self.SaveLineStartY[-1])))
                self.EndEntryText.set("{}, {}".format(np.int(self.SaveLineEndX[-1]),np.int(self.SaveLineEndY[-1])))
                self.WidthEntryText.set("{}".format(np.int(self.SaveRegionWidth[-1])))
            except:
                pass
        elif self.LineOrRect.get() == 'Arc':
                self.CanvasCtr_X +=1*self.MoveStep.get()*self.ZoomFactor
                self.canvas.delete(self.ArcOnCanvas1)
                self.canvas.delete(self.ArcOnCanvas2)
                self.canvas.delete(self.ArcOnCanvas3)
                self.plot_arc()
                self.Ctr_X += self.MoveStep.get()

    def profile_reset(self):
        self.IntegralWidth.set(10)
        self.SaveRegionWidth.append(self.IntegralWidth.get())
        try:
            self.StartEntryText.set("{}, {}".format(np.int(self.SaveLineStartX[-1]),np.int(self.SaveLineStartY[-1])))
            self.EndEntryText.set("{}, {}".format(np.int(self.SaveLineEndX[-1]),np.int(self.SaveLineEndY[-1])))
            self.WidthEntryText.set("{}".format(np.int(self.SaveRegionWidth[-1])))
        except:
            pass
        self.PFRadius.set(200.)
        self.ChiRange.set(60)
        self.PFTilt.set(0.)
        self.RadiusLabel['text'] ='Radius ({} \u00C5\u207B\u00B9)'.format(np.round(self.PFRadius.get()/(float(self.Sensitivity.get())/np.sqrt(float(self.ElectronEnergy.get()))),2))
        self.ChiRangeLabel['text'] = 'Chi Range ({}\u00B0)'.format(self.ChiRange.get())
        self.TiltLabel['text'] = 'Tilt Angle ({}\u00B0)'.format(np.round(self.PFTilt.get(),1))
        self.IntegralWidthLabel['text']='Integral Half Width ({} \u00C5\u207B\u00B9)'.format(np.round(self.IntegralWidth.get()/(float(self.Sensitivity.get())/np.sqrt(float(self.ElectronEnergy.get()))),2))
        if self.EnableCanvasLines==1:
            try:
                if int(int(self.IntegralWidth.get())*self.ZoomFactor) == 0:
                    self.IntegralHalfWidth = 1
                else:
                    self.IntegralHalfWidth = int(int(self.IntegralWidth.get())*self.ZoomFactor)
                x0,y0,x1,y1,x2,y2,x3,y3 = self.get_rectangle_position()
                try:
                    self.canvas.delete(self.LineOnCanvas)
                except:
                    pass
                try:
                    self.canvas.delete(self.RectOnCanvas)
                except:
                    pass
                self.RectOnCanvas = self.canvas.create_polygon(x0,y0,x1,y1,x2,y2,x3,y3,outline='yellow',fill='',width=2)
            except:
                pass
            self.line_scan_update()

        elif self.mode.get() == 'PF':
                self.canvas.delete(self.ArcOnCanvas1)
                self.canvas.delete(self.ArcOnCanvas2)
                self.canvas.delete(self.ArcOnCanvas3)
                self.plot_arc()

    '''Secondary Action Functions'''

    def menu_file_new(self):
        return

    def menu_file_open(self):
        self.choose_file()

    def menu_file_save_as(self):
        self.save_as_plain_image()
        return

    def menu_file_close(self):
        return

    def menu_preference_default(self):
        self.menu_default_win=tk.Toplevel()
        self.menu_default_win.wm_title('Default Settings')
        DefaultFrame = ttk.Frame(self.menu_default_win)
        DefaultFrame.grid(row=0,column=0)

        SettingFrame=ttk.LabelFrame(DefaultFrame,text='Parameters')
        SettingFrame.grid(row=0,column=0)

        MODE1 = [('Image Shift X:',1,self.HorizontalShift),('Image Shift Y:',2,self.VerticalShift),('Move Step (pixel):',3,self.MoveStep)]
        for text,row,textvariable in MODE1:
            DefaultLabel = ttk.Label(SettingFrame,cursor='left_ptr',text=text,padding = '0.02i',width=20)
            DefaultLabel.grid(row=row,column=0,sticky=W)
            DefaultEntry = ttk.Entry(SettingFrame,cursor="xterm",width=20,justify=LEFT,textvariable = textvariable)
            DefaultEntry.grid(row=row,column=1,sticky=W)

        MODE2 = [('Image Bit Depth',0,self.image_bit,(8,16))]
        for text,row,textvariable,values in MODE2:
            DefaultLabel = ttk.Label(SettingFrame,cursor='left_ptr',text=text,padding = '0.02i',width=20)
            DefaultLabel.grid(row=row,column=0,sticky=W)
            DefaultEntry = ttk.Combobox(SettingFrame,cursor="xterm",width=20,justify=LEFT,textvariable = textvariable,values=values)
            DefaultEntry.grid(row=row,column=1,sticky=W)

        ButtonFrame = ttk.Frame(DefaultFrame,cursor ='left_ptr',relief=FLAT,padding='0.1i')
        ButtonFrame.grid(row=1,column=0)
        SaveButton = ttk.Button(ButtonFrame,text='Save',command=self.save_default_settings)
        SaveButton.grid(row=0,column=0)
        CancelButton = ttk.Button(ButtonFrame,text='Quit',command=self.menu_default_win.destroy)
        CancelButton.grid(row=0,column=1)

        self.menu_default_win.focus_force()
        self.menu_default_win.grab_set()

    def save_default_settings(self):
        self.HS,self.VS = self.HorizontalShift.get(),self.VerticalShift.get()
        self.image_crop = [1200+self.VS,2650+self.VS,500+self.HS,3100+self.HS]
        self.img = self.read_image(self.DefaultPath)
        self.convert_image()
        self.show_image()
        self.delete_line()
        self.delete_calibration()


    def menu_help_about(self):
        messagebox.showinfo(title="About", default="ok",message="PyRHEED 1.0.0   By Yu Xiang\n\nContact: yux1991@gmail.com")

    def choose_profile_mode(self):
        if self.mode.get() == 'PF':
            self.delete_line()
            bbox = self.canvas.bbox(self.container)
            if self.CenterChosen ==0:
                self.CanvasCtr_X,self.CanvasCtr_Y = (bbox[2]+bbox[0])/2,bbox[1]*0.8+bbox[3]*0.2
            else:
                pass
            self.plot_arc()
        else:
            self.delete_line()

    def plot_arc(self):
        try:
            self.canvas.delete(self.ArcOnCanvas1)
            self.canvas.delete(self.ArcOnCanvas2)
            self.canvas.delete(self.ArcOnCanvas3)
            self.EnableCanvasLines = 0
            self.LineOrRect.set('None')
        except:
            pass

        arc1x0,arc1y0,arc1x1,arc1y1 = self.CanvasCtr_X-self.ZoomFactor*(self.PFRadius.get()+self.IntegralWidth.get()),self.CanvasCtr_Y-self.ZoomFactor*(self.PFRadius.get()+self.IntegralWidth.get()),self.CanvasCtr_X+self.ZoomFactor*(self.PFRadius.get()+self.IntegralWidth.get()),self.CanvasCtr_Y+self.ZoomFactor*(self.PFRadius.get()+self.IntegralWidth.get())
        arc2x0,arc2y0,arc2x1,arc2y1 = self.CanvasCtr_X-self.ZoomFactor*(self.PFRadius.get()-self.IntegralWidth.get()),self.CanvasCtr_Y-self.ZoomFactor*(self.PFRadius.get()-self.IntegralWidth.get()),self.CanvasCtr_X+self.ZoomFactor*(self.PFRadius.get()-self.IntegralWidth.get()),self.CanvasCtr_Y+self.ZoomFactor*(self.PFRadius.get()-self.IntegralWidth.get())
        arc3x0,arc3y0,arc3x1,arc3y1 = self.CanvasCtr_X-self.ZoomFactor*(self.PFRadius.get()),self.CanvasCtr_Y-self.ZoomFactor*(self.PFRadius.get()),self.CanvasCtr_X+self.ZoomFactor*(self.PFRadius.get()),self.CanvasCtr_Y+self.ZoomFactor*(self.PFRadius.get())
        arcstart = 270-self.ChiRange.get()/2
        arcextent = self.ChiRange.get()
        self.ArcOnCanvas1 = self.canvas.create_arc(arc1x0,arc1y0,arc1x1,arc1y1,start=arcstart+self.PFTilt.get(),extent = arcextent,style=PIESLICE,outline='yellow')
        self.ArcOnCanvas2 = self.canvas.create_arc(arc2x0,arc2y0,arc2x1,arc2y1,start=arcstart+self.PFTilt.get(),extent = arcextent,style=ARC,outline='yellow')
        self.ArcOnCanvas3 = self.canvas.create_arc(arc3x0,arc3y0,arc3x1,arc3y1,start=arcstart+self.PFTilt.get(),extent = arcextent,style=ARC,outline='red')
        self.LineOrRect.set('Arc')

    def get_chi_scan(self):
        self.ChiStep.set(50/self.PFRadius.get())
        if int(self.ChiRange.get()/self.ChiStep.get())>2:
            ChiTotalSteps = int(self.ChiRange.get()/self.ChiStep.get())
        else:
            ChiTotalSteps = 2
        ChiAngle = np.linspace(-self.ChiRange.get()/2+self.PFTilt.get()+90,self.ChiRange.get()/2+self.PFTilt.get()+90,ChiTotalSteps+1)
        ChiAngle2 = np.linspace(self.ChiRange.get()/2,-self.ChiRange.get()/2,ChiTotalSteps+1)
        ChiScan = np.full(ChiTotalSteps,0)
        ChiProfile = np.full(ChiTotalSteps,0)
        self.CMIProgressBar = ttk.Progressbar(self.CMIBottomFrame,length=180,variable = self.Progress,value='0',mode='determinate',orient=HORIZONTAL)
        self.CMIProgressBar.grid(row=0,column=0,sticky=W)

        for k in range(0,ChiTotalSteps):
            cit = 0
            x1 = self.Ctr_X + (self.PFRadius.get()+self.IntegralWidth.get())*np.cos(ChiAngle[k+1]*np.pi/180)
            y1 = self.Ctr_Y + (self.PFRadius.get()+self.IntegralWidth.get())*np.sin(ChiAngle[k+1]*np.pi/180)
            x2 = self.Ctr_X + (self.PFRadius.get()-self.IntegralWidth.get())*np.cos(ChiAngle[k+1]*np.pi/180)
            y2 = self.Ctr_Y + (self.PFRadius.get()-self.IntegralWidth.get())*np.sin(ChiAngle[k+1]*np.pi/180)
            x3 = self.Ctr_X + (self.PFRadius.get()-self.IntegralWidth.get())*np.cos(ChiAngle[k]*np.pi/180)
            y3 = self.Ctr_Y + (self.PFRadius.get()-self.IntegralWidth.get())*np.sin(ChiAngle[k]*np.pi/180)
            x4 = self.Ctr_X + (self.PFRadius.get()+self.IntegralWidth.get())*np.cos(ChiAngle[k]*np.pi/180)
            y4 = self.Ctr_Y + (self.PFRadius.get()+self.IntegralWidth.get())*np.sin(ChiAngle[k]*np.pi/180)
            y5 = 0
            if ChiAngle[k] <= 90. and ChiAngle[k+1] > 90.:
                y5 = self.Ctr_Y + self.PFRadius.get() + self.IntegralWidth.get()

            for i in range(int(np.amin([y1,y2,y3,y4])),int(np.amax([y1,y2,y3,y4,y5]))+1):
                for j in range(int(np.amin([x1,x2,x3,x4])),int(np.amax([x1,x2,x3,x4]))+1):
                    if (j-self.Ctr_X)**2+(i-self.Ctr_Y)**2 > (self.PFRadius.get()-self.IntegralWidth.get())**2 and\
                       (j-self.Ctr_X)**2+(i-self.Ctr_Y)**2 < (self.PFRadius.get()+self.IntegralWidth.get())**2 and\
                       (j-self.Ctr_X)/np.sqrt((i-self.Ctr_Y)**2+(j-self.Ctr_X)**2) < np.cos(ChiAngle[k]*np.pi/180) and\
                       (j-self.Ctr_X)/np.sqrt((i-self.Ctr_Y)**2+(j-self.Ctr_X)**2) > np.cos(ChiAngle[k+1]*np.pi/180):
                           ChiScan[k] += self.img[i,j]
                           cit+=1
            if cit == 0 and k>0:
                ChiProfile[k] = ChiProfile[k-1]
            else:
                ChiProfile[k] = float(ChiScan[k])/float(cit)

            self.Progress.set(k/(ChiTotalSteps-1)*100)
            self.CMIProgressBar.update_idletasks()

        self.CMIProgressBar.destroy()

        return ChiAngle2[0:-1], ChiProfile


    def choose_mode(self):
        if self.mode.get() == "N":
            self.canvas.bind('<ButtonPress-1>',self.move_from)
            self.canvas.bind('<B1-Motion>',self.move_to)
            self.canvas.bind('<ButtonRelease-1>',self.move_end)
            self.canvas.bind('<Button-3>',self.delete_line)
            self.StartEntry.state(['!disabled','selected'])
            self.EndEntry.state(['!disabled','selected'])
            self.WidthEntry.state(['!disabled','selected'])
            self.IntegralWidthScale.state(['disabled'])
            self.ChiRangeScale.state(['disabled'])
            self.RadiusScale.state(['disabled'])
            self.TiltScale.state(['disabled'])
        elif self.mode.get() == "LS":
            self.canvas.bind('<ButtonPress-1>',self.scan_from)
            self.canvas.bind('<B1-Motion>',self.scan_to)
            self.canvas.bind('<ButtonRelease-1>',self.scan_end)
            self.canvas.bind('<Alt-ButtonPress-1>',self.move_from)
            self.canvas.bind('<Alt-B1-Motion>',self.move_to)
            self.canvas.bind('<Alt-ButtonRelease-1>',self.move_end)
            self.canvas.bind('<Button-3>',self.delete_line)
            self.StartEntry.state(['!disabled','selected'])
            self.EndEntry.state(['!disabled','selected'])
            self.WidthEntry.state(['!disabled','selected'])
            self.IntegralWidthScale.state(['!disabled','selected'])
            self.ChiRangeScale.state(['disabled'])
            self.RadiusScale.state(['disabled'])
            self.TiltScale.state(['disabled'])
            self.IntegralWidthScale['to'] = 200
        elif self.mode.get() =='LI':
            self.canvas.bind('<ButtonPress-1>',self.integrate_from)
            self.canvas.bind('<B1-Motion>',self.integrate_to)
            self.canvas.bind('<ButtonRelease-1>',self.integrate_end)
            self.canvas.bind('<Alt-ButtonPress-1>',self.move_from)
            self.canvas.bind('<Alt-B1-Motion>',self.move_to)
            self.canvas.bind('<Alt-ButtonRelease-1>',self.move_end)
            self.canvas.bind('<Button-3>',self.delete_line)
            self.StartEntry.state(['!disabled','selected'])
            self.EndEntry.state(['!disabled','selected'])
            self.WidthEntry.state(['!disabled','selected'])
            self.IntegralWidthScale.state(['!disabled','selected'])
            self.ChiRangeScale.state(['disabled'])
            self.RadiusScale.state(['disabled'])
            self.TiltScale.state(['disabled'])
            self.IntegralWidthScale['to'] = 200
        else:
            self.canvas.bind('<ButtonPress-1>',self.move_from)
            self.canvas.bind('<B1-Motion>',self.move_to)
            self.canvas.bind('<ButtonRelease-1>',self.move_end)
            self.canvas.bind('<Button-3>',self.delete_line)
            self.StartEntry.state(['disabled'])
            self.EndEntry.state(['disabled'])
            self.WidthEntry.state(['disabled'])
            self.IntegralWidthScale.state(['!disabled','selected'])
            self.ChiRangeScale.state(['!disabled','selected'])
            self.RadiusScale.state(['!disabled','selected'])
            self.TiltScale.state(['!disabled','selected'])
            self.delete_line()
            self.IntegralWidthScale['to'] = 50
            bbox = self.canvas.bbox(self.container)
            if self.CenterChosen ==0:
                self.CanvasCtr_X,self.CanvasCtr_Y = (bbox[2]+bbox[0])/2,bbox[1]*0.8+bbox[3]*0.2
            else:
                pass
            self.plot_arc()

    def entry_is_okay(self,action):
        return TRUE

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

    def get_center(self):
        return int(self.Ctr_X),int(self.Ctr_Y)

    def set_as_center(self):
        self.XOffset,self.YOffset = self.Ctr_X,self.Ctr_Y

    def choose_this_region(self):
        self.SaveLineStartX.append(int(self.StartEntryText.get().split(',')[0]))
        self.SaveLineStartY.append(int(self.StartEntryText.get().split(',')[1]))
        self.SaveLineEndX.append(int(self.EndEntryText.get().split(',')[0]))
        self.SaveLineEndY.append(int(self.EndEntryText.get().split(',')[1]))
        self.IntegralWidth.set(int(self.WidthEntryText.get()))
        #print(self.SaveLineStartX[-1],self.SaveLineStartY[-1],self.SaveLineEndX[-1],self.SaveLineEndY[-1])
        Startx0,Starty0 = self.inverse_convert_coords(self.SaveLineStartX[-1],self.SaveLineStartY[-1])
        Endx0,Endy0 = self.inverse_convert_coords(self.SaveLineEndX[-1],self.SaveLineEndY[-1])
        #print(Startx0,Starty0,Endx0,Endy0)
        self.SaveLineStartX0.append(Startx0)
        self.SaveLineStartY0.append(Starty0)
        self.SaveLineEndX0.append(Endx0)
        self.SaveLineEndY0.append(Endy0)
        self.LineStartX0 = self.SaveLineStartX0[-1]
        self.LineStartY0 = self.SaveLineStartY0[-1]
        self.LineEndX0 = self.SaveLineEndX0[-1]
        self.LineEndY0 = self.SaveLineEndY0[-1]
        try:
            self.RegionStartX,self.RegionStartY,self.RegionEndX,self.RegionEndY = self.SaveLineStartX[-1],self.SaveLineStartY[-1],self.SaveLineEndX[-1],self.SaveLineEndY[-1]
            self.RegionWidth = self.SaveRegionWidth[-1]
        except:
            pass
        self.EnableCanvasLines == 1
        self.plot_rectangle()
        self.line_scan_update()

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
            i = min(self.image_crop[3]-self.image_crop[2], self.image_crop[1]-self.image_crop[0])
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
        self.CanvasCtr_X = (self.CanvasCtr_X-self.xx[-1])*self.scale+self.xx[-1]
        self.CanvasCtr_Y = (self.CanvasCtr_Y-self.yy[-1])*self.scale+self.yy[-1]
        try:
            self.LineStartX0 = (self.LineStartX0-self.xx[-1])*self.scale+self.xx[-1]
            self.LineStartY0 = (self.LineStartY0-self.yy[-1])*self.scale+self.yy[-1]
            self.SaveLineStartX0.append(self.LineStartX0)
            self.SaveLineStartY0.append(self.LineStartY0)
            self.LineEndX0 = (self.LineEndX0-self.xx[-1])*self.scale+self.xx[-1]
            self.LineEndY0 = (self.LineEndY0-self.yy[-1])*self.scale+self.yy[-1]
            self.SaveLineEndX0.append(self.LineEndX0)
            self.SaveLineEndY0.append(self.LineEndY0)
        except:
            pass
        self.ZFtext.delete(1.0,END)
        self.ZoomFactor = np.prod(self.scalehisto)
        self.ZFtext.insert(1.0,'x {}'.format(np.round(self.ZoomFactor*self.ZoomFactor,3)))
        self.show_image()

    def zoom_in(self):
        bbox = self.canvas.bbox(self.container)  # get image area
        xx = int((bbox[2]+bbox[0])/2)
        yy = int((bbox[3]+bbox[1])/2)
        self.xx.append(xx)
        self.yy.append(yy)
        self.scale = 1.0
        i = min(self.image_crop[3]-self.image_crop[2], self.image_crop[1]-self.image_crop[0])
        if int(i * self.imscale) < 30:
            self.xx.pop()
            self.yy.pop()
            return  # image is less than 30 pixels
        self.imscale /= self.delta
        self.scale   /= self.delta

        self.scalehisto.append(self.scale)
        self.canvas.scale('all', self.xx[-1], self.yy[-1], self.scale, self.scale)  # rescale all canvas objects
        self.CanvasCtr_X = (self.CanvasCtr_X-self.xx[-1])*self.scale+self.xx[-1]
        self.CanvasCtr_Y = (self.CanvasCtr_Y-self.yy[-1])*self.scale+self.yy[-1]
        try:
            self.LineStartX0 = (self.LineStartX0-self.xx[-1])*self.scale+self.xx[-1]
            self.LineStartY0 = (self.LineStartY0-self.yy[-1])*self.scale+self.yy[-1]
            self.SaveLineStartX0.append(self.LineStartX0)
            self.SaveLineStartY0.append(self.LineStartY0)
            self.LineEndX0 = (self.LineEndX0-self.xx[-1])*self.scale+self.xx[-1]
            self.LineEndY0 = (self.LineEndY0-self.yy[-1])*self.scale+self.yy[-1]
            self.SaveLineEndX0.append(self.LineEndX0)
            self.SaveLineEndY0.append(self.LineEndY0)
        except:
            pass
        self.ZFtext.delete(1.0,END)
        self.ZoomFactor = np.prod(self.scalehisto)
        self.ZFtext.insert(1.0,'x {}'.format(np.round(self.ZoomFactor*self.ZoomFactor,3)))
        self.show_image()

    def zoom_out(self):
        bbox = self.canvas.bbox(self.container)  # get image area
        xx = int((bbox[2]+bbox[0])/2)
        yy = int((bbox[3]+bbox[1])/2)
        self.xx.append(xx)
        self.yy.append(yy)
        self.scale = 1.0
        i = min(self.canvas.winfo_width(), self.canvas.winfo_height())
        if i < self.imscale:
            self.xx.pop()
            self.yy.pop()
            return  # image is less than 30 pixels
        self.imscale *= self.delta
        self.scale   *= self.delta
        self.scalehisto.append(self.scale)
        self.canvas.scale('all', self.xx[-1], self.yy[-1], self.scale, self.scale)  # rescale all canvas objects
        self.CanvasCtr_X = (self.CanvasCtr_X-self.xx[-1])*self.scale+self.xx[-1]
        self.CanvasCtr_Y = (self.CanvasCtr_Y-self.yy[-1])*self.scale+self.yy[-1]
        try:
            self.LineStartX0 = (self.LineStartX0-self.xx[-1])*self.scale+self.xx[-1]
            self.LineStartY0 = (self.LineStartY0-self.yy[-1])*self.scale+self.yy[-1]
            self.SaveLineStartX0.append(self.LineStartX0)
            self.SaveLineStartY0.append(self.LineStartY0)
            self.LineEndX0 = (self.LineEndX0-self.xx[-1])*self.scale+self.xx[-1]
            self.LineEndY0 = (self.LineEndY0-self.yy[-1])*self.scale+self.yy[-1]
            self.SaveLineEndX0.append(self.LineEndX0)
            self.SaveLineEndY0.append(self.LineEndY0)
        except:
            pass
        self.ZFtext.delete(1.0,END)
        self.ZoomFactor = np.prod(self.scalehisto)
        self.ZFtext.insert(1.0,'x {}'.format(np.round(self.ZoomFactor*self.ZoomFactor,3)))
        self.show_image()

    def canvas_configure(self,event=NONE):
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
        return bbox,bbox1,bbox2

    def canvas_configure_show_image(self,event=NONE):
        try:
            self.show_image()
        except:
            pass

    def canvas_mouse_coords(self,event):

        #Get the coordinates of the mouse on the main canvas while it moves
        x1 = self.canvas.canvasx(event.x)
        y1 = self.canvas.canvasy(event.y)
        bbox1 = self.canvas.bbox(self.container)  # get image area
        if bbox1[0] < x1 < bbox1[2] and bbox1[1] < y1 < bbox1[3]:pass
        else: return  # Show mouse motion only inside image area
        self.Mouse_X,self.Mouse_Y = self.convert_coords(x1,y1)
        self.CMIlabel['text']='  x={}, y={}'.format(np.int(self.Mouse_X),np.int(self.Mouse_Y))

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
            if self.LineOrRect.get() == 'Arc':
                self.CMIlabel['text']='  Chi= {}, Int.= {}'.format(np.round(self.Mouse_X,2),np.round(self.Mouse_Y,2))
            else:
                self.CMIlabel['text']='  K= {}, Int.= {}'.format(np.round(self.Mouse_X,2),np.round(self.Mouse_Y,2))
            self.LineScanCanvas['cursor']='crosshair'
        except:
            self.LineScanCanvas['cursor']='left_ptr'
            pass

    def convert_coords(self,x,y):

        #This is the function that converts the coordinates back to its native coordinates on the RHEED pattern
        Xn=[]
        Yn=[]
        n = len(self.xx)
        for i in range(n+1):
            Xn.append(0)
            Yn.append(0)
        Xn[n],Yn[n]=x,y
        for j in range(n,0,-1):
            Xn[j-1]=(Xn[j]-self.xx[j-1])/self.scalehisto[j-1]+self.xx[j-1]
            Yn[j-1]=(Yn[j]-self.yy[j-1])/self.scalehisto[j-1]+self.yy[j-1]
        return Xn[0],Yn[0]

    def inverse_convert_coords(self,x,y):

        #This is the function that converts the coordinates back to its native coordinates on the RHEED pattern
        Xn=[]
        Yn=[]
        n = len(self.xx)
        for i in range(n+1):
            Xn.append(0)
            Yn.append(0)
        Xn[0],Yn[0]=x,y
        for j in range(0,n,1):
            Xn[j+1]=(Xn[j]-self.xx[j])*self.scalehisto[j]+self.xx[j]
            Yn[j+1]=(Yn[j]-self.yy[j])*self.scalehisto[j]+self.yy[j]
        return Xn[n],Yn[n]

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
        self.SaveLineStartX0.append(x)
        self.SaveLineStartY0.append(y)
        self.ScanStatus = 0

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
        LinePlotAx.plot(LineScanRadius/(float(self.Sensitivity.get())/np.sqrt(float(self.ElectronEnergy.get()))),LineScanIntensities/np.amax(np.amax(self.img)),'r-')
        self.LinePlotRangeX = LinePlotAx.get_xlim()
        self.LinePlotRangeY = LinePlotAx.get_ylim()
        self.delete_line()
        self.LineScanFigure = self.show_line_scan(self.LinePlot)
        self.CMIlabel['text']='  x={}, y={}, length ={} \u00C5\u207B\u00B9'.format(np.int(self.LineEndX),np.int(self.LineEndY),np.round(LineScanRadius[-1]/(float(self.Sensitivity.get())/np.sqrt(float(self.ElectronEnergy.get()))),2))
        self.LineOnCanvas = self.canvas.create_line((self.LineStartX0,self.LineStartY0),(self.LineEndX0,self.LineEndY0),fill='yellow',width=2)
        self.ScanStatus = 1
        self.LineOrRect.set('Line')


    def scan_end(self,event):
        if self.ScanStatus == 0:
            try:
                self.SaveLineStartX0.pop()
                self.SaveLineStartY0.pop()
                self.LineStartX0 = self.SaveLineStartX0[-1]
                self.LineStartY0 = self.SaveLineStartY0[-1]
            except:
                pass
        else:
            self.SaveLineStartX.append(self.LineStartX)
            self.SaveLineStartY.append(self.LineStartY)
            self.SaveLineEndX.append(self.LineEndX)
            self.SaveLineEndY.append(self.LineEndY)
            self.SaveLineEndX0.append(self.LineEndX0)
            self.SaveLineEndY0.append(self.LineEndY0)
            self.SaveRegionWidth.append(1)
            self.StartEntryText.set("{}, {}".format(np.int(self.SaveLineStartX[-1]),np.int(self.SaveLineStartY[-1])))
            self.EndEntryText.set("{}, {}".format(np.int(self.SaveLineEndX[-1]),np.int(self.SaveLineEndY[-1])))
            self.WidthEntryText.set("{}".format(np.int(self.SaveRegionWidth[-1])))
            self.LineStartX,self.LineStartY = 0,0
            self.LineEndX,self.LineEndY = 0,0

    def integrate_from(self, event):
        ''' Remember previous coordinates for scrolling with the mouse '''
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.LineStartX,self.LineStartY = self.convert_coords(x,y)
        self.LineStartX0,self.LineStartY0 = x,y
        self.SaveLineStartX0.append(x)
        self.SaveLineStartY0.append(y)
        self.ScanStatus=0

    def integrate_to(self, event):
        ''' Drag the cursor to the new position '''
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.LineEndX0,self.LineEndY0 = x,y
        if int(int(self.IntegralWidth.get())*self.ZoomFactor) == 0:
            self.IntegralHalfWidth = 1
        else:
            self.IntegralHalfWidth = int(int(self.IntegralWidth.get())*self.ZoomFactor)
        bbox = self.canvas.bbox(self.container)  # get image area
        if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]: pass  # Ok! Inside the image
        else: return  # Show line integral only inside image area
        x0,y0,x1,y1,x2,y2,x3,y3 = self.get_rectangle_position()
        self.LineEndX,self.LineEndY = self.convert_coords(x,y)
        LineScanRadius,LineScanIntensities = self.get_line_integral(self.LineStartX,self.LineStartY,self.LineEndX,self.LineEndY)
        self.LinePlot = matplotlib.figure.Figure(figsize=(self.LineScanCanvas.winfo_width()/self.dpi,self.LineScanCanvas.winfo_height()/self.dpi))
        LinePlotAx = self.LinePlot.add_axes(self.LineScanAxesPosition)
        LinePlotAx.set_xlabel(r"$K (\AA^{-1})$")
        LinePlotAx.set_ylabel("Intensity (arb. units)")
        LinePlotAx.ticklabel_format(style='sci',scilimits=(0,0),axis='y',useMathText=TRUE)
        LinePlotAx.plot(LineScanRadius/(float(self.Sensitivity.get())/np.sqrt(float(self.ElectronEnergy.get()))),LineScanIntensities/np.amax(np.amax(self.img)),'r-')
        self.LinePlotRangeX = LinePlotAx.get_xlim()
        self.LinePlotRangeY = LinePlotAx.get_ylim()
        self.delete_line()
        self.LineScanFigure = self.show_line_scan(self.LinePlot)
        self.CMIlabel['text']='  x={}, y={}, length = {} \u00C5\u207B\u00B9'.format(np.int(self.LineEndX),np.int(self.LineEndY),np.round(LineScanRadius[-1]/(float(self.Sensitivity.get())/np.sqrt(float(self.ElectronEnergy.get()))),2))
        self.RectOnCanvas = self.canvas.create_polygon(x0,y0,x1,y1,x2,y2,x3,y3,outline='yellow',fill='',width=2)
        self.LineOrRect.set('Rect')
        self.ScanStatus = 1

    def integrate_end(self,event):
        if self.ScanStatus == 0:
            try:
                self.SaveLineStartX0.pop()
                self.SaveLineStartY0.pop()
                self.LineStartX0 = self.SaveLineStartX0[-1]
                self.LineStartY0 = self.SaveLineStartY0[-1]
            except:
                pass
        else:
            self.SaveLineStartX.append(self.LineStartX)
            self.SaveLineStartY.append(self.LineStartY)
            self.SaveLineEndX.append(self.LineEndX)
            self.SaveLineEndY.append(self.LineEndY)
            self.SaveLineEndX0.append(self.LineEndX0)
            self.SaveLineEndY0.append(self.LineEndY0)
            self.SaveRegionWidth.append(self.IntegralWidth.get())
            self.StartEntryText.set("{}, {}".format(np.int(self.SaveLineStartX[-1]),np.int(self.SaveLineStartY[-1])))
            self.EndEntryText.set("{}, {}".format(np.int(self.SaveLineEndX[-1]),np.int(self.SaveLineEndY[-1])))
            self.WidthEntryText.set("{}".format(np.int(self.SaveRegionWidth[-1])))
            self.LineStartX,self.LineStartY = 0,0
            self.LineEndX,self.LineEndY = 0,0

    def line_scan_update(self):
        if self.EnableCanvasLines == 1:
            if self.LineOrRect.get() == 'Line':
                LineScanRadius,LineScanIntensities = self.get_line_scan(self.SaveLineStartX[-1],self.SaveLineStartY[-1],self.SaveLineEndX[-1],self.SaveLineEndY[-1])
                self.LinePlot = matplotlib.figure.Figure(figsize=(self.LineScanCanvas.winfo_width()/self.dpi,self.LineScanCanvas.winfo_height()/self.dpi))
                LinePlotAx = self.LinePlot.add_axes(self.LineScanAxesPosition)
                LinePlotAx.set_xlabel(r"$K (\AA^{-1})$")
                LinePlotAx.set_ylabel("Intensity (arb. units)")
                LinePlotAx.ticklabel_format(style='sci',scilimits=(0,0),axis='y',useMathText=TRUE)
                LinePlotAx.plot(LineScanRadius/(float(self.Sensitivity.get())/np.sqrt(float(self.ElectronEnergy.get()))),LineScanIntensities/np.amax(np.amax(self.img)),'r-')
                self.LinePlotRangeX = LinePlotAx.get_xlim()
                self.LinePlotRangeY = LinePlotAx.get_ylim()
                self.LineScanFigure = self.show_line_scan(self.LinePlot)
                self.LineOrRect.set('Line')
            elif self.LineOrRect.get()== 'Rect':
                LineScanRadius,LineScanIntensities = self.get_line_integral(self.SaveLineStartX[-1],self.SaveLineStartY[-1],self.SaveLineEndX[-1],self.SaveLineEndY[-1])
                self.LinePlot = matplotlib.figure.Figure(figsize=(self.LineScanCanvas.winfo_width()/self.dpi,self.LineScanCanvas.winfo_height()/self.dpi))
                LinePlotAx = self.LinePlot.add_axes(self.LineScanAxesPosition)
                LinePlotAx.set_xlabel(r"$K (\AA^{-1})$")
                LinePlotAx.set_ylabel("Intensity (arb. units)")
                LinePlotAx.ticklabel_format(style='sci',scilimits=(0,0),axis='y',useMathText=TRUE)
                LinePlotAx.plot(LineScanRadius/(float(self.Sensitivity.get())/np.sqrt(float(self.ElectronEnergy.get()))),LineScanIntensities/np.amax(np.amax(self.img)),'r-')
                self.LinePlotRangeX = LinePlotAx.get_xlim()
                self.LinePlotRangeY = LinePlotAx.get_ylim()
                self.LineScanFigure = self.show_line_scan(self.LinePlot)
                self.LineOrRect.set('Rect')

    def plot_chi_scan(self):
        LineScanRadius,LineScanIntensities = self.get_chi_scan()
        self.LinePlot = matplotlib.figure.Figure(figsize=(self.LineScanCanvas.winfo_width()/self.dpi,self.LineScanCanvas.winfo_height()/self.dpi))
        LinePlotAx = self.LinePlot.add_axes(self.LineScanAxesPosition)
        LinePlotAx.set_xlabel(r"$\chi (^{\circ})$")
        LinePlotAx.set_ylabel("Intensity (arb. units)")
        LinePlotAx.ticklabel_format(style='sci',scilimits=(0,0),axis='y',useMathText=TRUE)
        LinePlotAx.plot(LineScanRadius,LineScanIntensities/np.amax(np.amax(self.img)),'r-')
        self.LinePlotRangeX = LinePlotAx.get_xlim()
        self.LinePlotRangeY = LinePlotAx.get_ylim()
        self.LineScanFigure = self.show_line_scan(self.LinePlot)

    def get_rectangle_position(self):
        x0,y0,x1,y1,x2,y2,x3,y3 = 0,0,0,0,0,0,0,0
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
        return x0,y0,x1,y1,x2,y2,x3,y3

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
        if self.IntegralWidth.get()>20:
            self.CMIProgressBar = ttk.Progressbar(self.CMIBottomFrame,length=180,variable = self.Progress,value='0',mode='determinate',orient=HORIZONTAL)
            self.CMIProgressBar.grid(row=0,column=0,sticky=W)
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

            if self.IntegralWidth.get()>20:
                self.Progress.set(i/(len(Kx)-1)*100)
                self.CMIProgressBar.update_idletasks()
        LineScanRadius = np.linspace(0,math.sqrt((x1-x0)**2+(y1-y0)**2),len(Kx))
        if self.IntegralWidth.get()>20:
            self.CMIProgressBar.destroy()

        return LineScanRadius,LineScanIntensities/(2*self.IntegralHalfWidth)

    def latex2image(self,LatexExpression):
        buffer = BytesIO()
        font = FontProperties(family='arial', style='normal',weight='roman')
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
        img_rgb = img_raw.postprocess(demosaic_algorithm=rawpy.DemosaicAlgorithm.AHD,output_bps = self.image_bit.get(),use_auto_wb = self.EnableAutoWB.get(),bright=self.Brightness.get()/100,user_black=self.UserBlack.get())
        #Convert to grayvalue images
        img_bw = (0.21*img_rgb[:,:,0])+(0.72*img_rgb[:,:,1])+(0.07*img_rgb[:,:,2])
        #Crop the image
        img = img_bw[self.image_crop[0]:self.image_crop[1],self.image_crop[2]:self.image_crop[3]]
        #img = (img/255).astype(int)*255
        return img

    def convert_image(self):
        self.image = Image.new('L',(self.img.shape[1],self.img.shape[0]))
        if self.image_bit.get() == 16:
            self.uint8 = np.uint8(self.img/256)
        if self.image_bit.get() == 8:
            self.uint8 = np.uint8(self.img)
        self.outpil = self.uint8.astype(self.uint8.dtype.newbyteorder("L")).tobytes()
        self.image.frombytes(self.outpil)

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

