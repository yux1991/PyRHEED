from PyQt5 import QtCore, QtWidgets,QtGui
import numpy as np
import math
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvas

class Profile(QtWidgets.QGraphicsView):

    def __init__(self,parent):
        super(Profile,self).__init__(parent)
        self.initUI()

    def initUI(self):
        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self._img = []
        self._scaleFactor = 1
        self.setScene(self._scene)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor('darkGray')))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        profileImg = QtGui.QImage()
        profilePixmap = QtGui.QPixmap(profileImg.size())
        QtGui.QPixmap.convertFromImage(profilePixmap,profileImg,QtCore.Qt.AutoColor)
        self._photo.setPixmap(profilePixmap)
        self.fitInView()


    def fitInView(self, scale=True):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
            self.scale(1 / unity.width(), 1 / unity.height())
            viewrect = self.viewport().rect()
            scenerect = self.transform().mapRect(rect)
            self.scale(viewrect.width() / scenerect.width(),
                         viewrect.height() / scenerect.height())

    def setImg(self,img):
        self._img = img

    def setScaleFactor(self,s):
        self._scaleFactor = s

    def lineScan(self,start,end):
        x0,y0,x1,y1 = start.x(),start.y(),end.x(),end.y()
        K_length = max(int(abs(x1-x0)+1),int(abs(y1-y0)+1))
        Kx = np.linspace(x0,x1,K_length)
        Ky = np.linspace(y0,y1,K_length)
        LineScanIntensities = np.zeros(len(Kx))
        for i in range(0,len(Kx)):
            LineScanIntensities[i] = self._img[int(Ky[i]),int(Kx[i])]
        LineScanRadius = np.linspace(0,math.sqrt((x1-x0)**2+(y1-y0)**2),len(Kx))
        fig = self.plotProfile(LineScanRadius,LineScanIntensities)
        self.figure = self.fig2qpixmap(fig)
        self._photo.setPixmap(self.figure)
        self.fitInView()

    def integral(self,start,end,width):
        x0,y0,x1,y1 = start.x(),start.y(),end.x(),end.y()
        K_length = max(int(abs(x1-x0)+1),int(abs(y1-y0)+1))
        Kx = np.linspace(x0,x1,K_length)
        Ky = np.linspace(y0,y1,K_length)
        LineScanIntensities = np.zeros(len(Kx))
        for i in range(0,len(Kx)):
            for j in range(-int(width),int(width)+1):
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
                LineScanIntensities[i] += self._img[image_row,image_column]
        LineScanRadius = np.linspace(0,math.sqrt((x1-x0)**2+(y1-y0)**2),len(Kx))
        fig = self.plotProfile(LineScanRadius,LineScanIntensities)
        self.figure = self.fig2qpixmap(fig)
        self._photo.setPixmap(self.figure)
        self.fitInView()

    def chiScan(self,center,radius,width,chiRange,tilt,chiStep=1):
        x0,y0 = center.x(),center.y()
        if int(chiRange/chiStep)>2:
            ChiTotalSteps = int(chiRange/chiStep)
        else:
            ChiTotalSteps = 2
        ChiAngle = np.linspace(-chiRange/2+tilt+90,chiRange/2+tilt+90,ChiTotalSteps+1)
        ChiAngle2 = np.linspace(-chiRange/2,chiRange/2,ChiTotalSteps+1)
        ChiScan = np.full(ChiTotalSteps,0)
        ChiProfile = np.full(ChiTotalSteps,0)
        for k in range(0,ChiTotalSteps):
            cit = 0
            x1 = x0 + (radius+width)*np.cos(ChiAngle[k+1]*np.pi/180)
            y1 = y0 + (radius+width)*np.sin(ChiAngle[k+1]*np.pi/180)
            x2 = x0 + (radius-width)*np.cos(ChiAngle[k+1]*np.pi/180)
            y2 = y0 + (radius-width)*np.sin(ChiAngle[k+1]*np.pi/180)
            x3 = x0 + (radius-width)*np.cos(ChiAngle[k]*np.pi/180)
            y3 = y0 + (radius-width)*np.sin(ChiAngle[k]*np.pi/180)
            x4 = x0 + (radius+width)*np.cos(ChiAngle[k]*np.pi/180)
            y4 = y0 + (radius+width)*np.sin(ChiAngle[k]*np.pi/180)
            y5 = 0
            if ChiAngle[k] <= 90. and ChiAngle[k+1] > 90.:
                y5 = y0 + radius + width
            for i in range(int(np.amin([y1,y2,y3,y4])),int(np.amax([y1,y2,y3,y4,y5]))+1):
                for j in range(int(np.amin([x1,x2,x3,x4])),int(np.amax([x1,x2,x3,x4]))+1):
                    if (j-x0)**2+(i-y0)**2 > (radius-width)**2 and\
                       (j-x0)**2+(i-y0)**2 < (radius+width)**2 and\
                       (j-x0)/np.sqrt((i-y0)**2+(j-x0)**2) < np.cos(ChiAngle[k]*np.pi/180) and\
                       (j-x0)/np.sqrt((i-y0)**2+(j-x0)**2) > np.cos(ChiAngle[k+1]*np.pi/180):
                           ChiScan[k] += self._img[i,j]
                           cit+=1
            if cit == 0 and k>0:
                ChiProfile[k] = ChiProfile[k-1]
            else:
                ChiProfile[k] = float(ChiScan[k])/float(cit)
        fig = self.plotChiScan(ChiAngle2[0:-1],ChiProfile)
        self.figure = self.fig2qpixmap(fig)
        self._photo.setPixmap(self.figure)
        self.fitInView()

    def plotProfile(self,x,y):
        LineScanRadius = x
        LineScanIntensities = y
        screen = QtGui.QGuiApplication.primaryScreen()
        LinePlot = matplotlib.figure.Figure()#figsize = (self.frameSize().width()/screen.logicalDotsPerInch(),self.frameSize().height()/screen.logicalDotsPerInch()))
        LinePlotAx = LinePlot.add_axes([0.15,0.15,0.75,0.75])
        LinePlotAx.set_xlabel(r"$K (\AA^{-1})$")
        LinePlotAx.set_ylabel("Intensity (arb. units)")
        LinePlotAx.ticklabel_format(style='sci',scilimits=(0,0),axis='y',useMathText= True)
        LinePlotAx.plot(LineScanRadius/self._scaleFactor,LineScanIntensities/np.amax(np.amax(self._img)),'r-')
        return LinePlot

    def plotChiScan(self,x,y):
        LineScanRadius = x
        LineScanIntensities = y
        screen = QtGui.QGuiApplication.primaryScreen()
        LinePlot = matplotlib.figure.Figure()#figsize = (self.frameSize().width()/screen.logicalDotsPerInch(),self.frameSize().height()/screen.logicalDotsPerInch()))
        LinePlotAx = LinePlot.add_axes([0.15,0.15,0.75,0.75])
        LinePlotAx.set_xlabel(r"$\chi (^{\circ})$")
        LinePlotAx.set_ylabel("Intensity (arb. units)")
        LinePlotAx.ticklabel_format(style='sci',scilimits=(0,0),axis='y',useMathText= True)
        LinePlotAx.plot(LineScanRadius,LineScanIntensities/np.amax(np.amax(self._img)),'r-')
        return LinePlot

    def fig2qpixmap(self,fig):
        canvas = FigureCanvas(fig)
        canvas.draw()
        size = canvas.size()
        width,height = size.width(),size.height()
        im = QtGui.QImage(canvas.buffer_rgba(),width,height,QtGui.QImage.Format_ARGB32)
        return QtGui.QPixmap(im)
