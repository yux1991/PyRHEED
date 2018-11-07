from PyQt5 import QtCore, QtWidgets, QtGui, QtChart
import numpy as np
import math
import time

class ProfileChart(QtChart.QChartView):

    progressAdvance = QtCore.pyqtSignal(int,int,int)
    progressEnd = QtCore.pyqtSignal()
    chartMouseMovement = QtCore.pyqtSignal(QtCore.QPointF,str)
    chartIsPresent = False

    def __init__(self,parent,config):
        super(ProfileChart,self).__init__(parent)
        chartDefault = dict(config['chartDefault'].items())
        if int(chartDefault['theme']) == 0:
            self.theme = QtChart.QChart.ChartThemeLight
        if int(chartDefault['theme']) == 1:
            self.theme = QtChart.QChart.ChartThemeBlueCerulean
        if int(chartDefault['theme']) == 2:
            self.theme = QtChart.QChart.ChartThemeDark
        if int(chartDefault['theme']) == 3:
            self.theme = QtChart.QChart.ChartThemeBrownSand
        if int(chartDefault['theme']) == 4:
            self.theme = QtChart.QChart.ChartThemeBlueNcs
        if int(chartDefault['theme']) == 5:
            self.theme = QtChart.QChart.ChartThemeHighContrast
        if int(chartDefault['theme']) == 6:
            self.theme = QtChart.QChart.ChartThemeBlueIcy
        if int(chartDefault['theme']) == 7:
            self.theme = QtChart.QChart.ChartThemeQt

        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self._scaleFactor = 1
        self.setContentsMargins(0,0,0,0)
        chart = QtChart.QChart()
        chart.setTheme(self.theme)
        chart.setBackgroundRoundness(0)
        chart.setMargins(QtCore.QMargins(0,0,0,0))
        self.setChart(chart)

    def addChart(self,radius,profile,type="line"):
        series = QtChart.QLineSeries()
        for x,y in zip(radius,profile):
            series.append(x,y)
        chart = QtChart.QChart()
        chart.setTheme(self.theme)
        chart.setBackgroundRoundness(0)
        chart.setMargins(QtCore.QMargins(0,0,0,0))
        chart.addSeries(series)
        axisX = QtChart.QValueAxis()
        axisX.setTickCount(10)
        if type == "line" or type == "rectangle":
            axisX.setTitleText("K (\u212B\u207B\u00B9)")
        elif type == "arc":
            axisX.setTitleText("\u03A7 (\u00BA)")
        axisY = QtChart.QValueAxis()
        axisY.setTickCount(10)
        axisY.setTitleText("Intensity (arb. units)")
        chart.addAxis(axisX, QtCore.Qt.AlignBottom)
        chart.addAxis(axisY, QtCore.Qt.AlignLeft)
        series.attachAxis(axisX)
        series.attachAxis(axisY)
        chart.legend().setVisible(False)
        self.setChart(chart)

    def setImg(self,img):
        self._img = img

    def setScaleFactor(self,s):
        self._scaleFactor = s

    def lineScan(self,start,end):
        #start_time = time.time()
        x0,y0,x1,y1 = start.x(),start.y(),end.x(),end.y()
        K_length = max(int(abs(x1-x0)+1),int(abs(y1-y0)+1))
        Kx = np.linspace(x0,x1,K_length)
        Ky = np.linspace(y0,y1,K_length)
        LineScanIntensities = np.zeros(len(Kx))
        for i in range(0,len(Kx)):
            LineScanIntensities[i] = self._img[int(Ky[i]),int(Kx[i])]
        LineScanRadius = np.linspace(0,math.sqrt((x1-x0)**2+(y1-y0)**2),len(Kx))
        self.addChart(LineScanRadius/self._scaleFactor,LineScanIntensities/np.amax(np.amax(self._img)),"line")
        self.chartIsPresent = True
        #print("Line Scan run time is: {} s\nThe size is: {}\n".format(np.round(time.time()-start_time,5),int(len(Kx))))

    def integral(self,start,end,width):
        #start_time = time.time()
        x0,y0,x1,y1 = start.x(),start.y(),end.x(),end.y()
        K_length = max(int(abs(x1-x0)+1),int(abs(y1-y0)+1))
        int_width = int(width)
        Kx = np.linspace(x0,x1,K_length)
        Ky = np.linspace(y0,y1,K_length)
        LineScanIntensities = np.zeros(len(Kx))
        LineScanRadius = np.linspace(0,math.sqrt((x1-x0)**2+(y1-y0)**2),len(Kx))
        if y1 == y0:
            for i in range (0,len(Kx)): LineScanIntensities[i] = np.sum(self._img[int(Ky[i])-int_width:int(Ky[i])+\
                                        int_width,int(Kx[i])])
        elif x1 == x0:
            for i in range (0,len(Kx)): LineScanIntensities[i] = np.sum(self._img[int(Ky[i]),int(Kx[i])-int_width:\
                                        int(Kx[i])+int_width])
        else:
            slope =(x0-x1)/(y1-y0)
            if abs(slope) > 1:
                index = np.asarray([[np.linspace(Ky[i]-int_width,Ky[i]+int_width+1,2*int_width+1),\
                                     np.linspace(Kx[i]-int_width/slope,Kx[i]+(int_width+1)/slope,2*int_width+1)] for i in range(len(Kx))],dtype=int)
            else:
                index = np.asarray([[np.linspace(Ky[i]-int_width*slope,Ky[i]+(int_width+1)*slope,2*int_width+1),\
                                     np.linspace(Kx[i]-int_width,Kx[i]+int_width+1,2*int_width+1)] for i in range(len(Kx))],dtype=int)
            LineScanIntensities = np.sum([self._img[index[i,0,:],index[i,1,:]] for i in range(len(Kx))],axis=1)
        self.addChart(LineScanRadius/self._scaleFactor,LineScanIntensities/2/width/np.amax(np.amax(self._img)),"rectangle")
        self.chartIsPresent = True
        #print("Line Integral run time is: {} s\nThe size is: {}\n".format(np.round(time.time()-start_time,5),int(len(Kx)*(2*width+1))))

    def chiScan(self,center,radius,width,chiRange,tilt,chiStep=1):
        x0,y0 = center.x(),center.y()
        if int(chiRange/chiStep)>2:
            ChiTotalSteps = int(chiRange/chiStep)
        else:
            ChiTotalSteps = 2
        ChiAngle = np.linspace(-chiRange/2-tilt+90,chiRange/2-tilt+90,ChiTotalSteps+1)
        ChiAngle2 = np.linspace(-chiRange/2,chiRange/2,ChiTotalSteps+1)
        x1 = x0 + (radius+width)*np.cos(ChiAngle[1]*np.pi/180)
        y1 = y0 + (radius+width)*np.sin(ChiAngle[1]*np.pi/180)
        x2 = x0 + (radius-width)*np.cos(ChiAngle[1]*np.pi/180)
        y2 = y0 + (radius-width)*np.sin(ChiAngle[1]*np.pi/180)
        x3 = x0 + (radius-width)*np.cos(ChiAngle[0]*np.pi/180)
        y3 = y0 + (radius-width)*np.sin(ChiAngle[0]*np.pi/180)
        x4 = x0 + (radius+width)*np.cos(ChiAngle[0]*np.pi/180)
        y4 = y0 + (radius+width)*np.sin(ChiAngle[0]*np.pi/180)
        indices = np.array([[0,0]])
        cit = 0
        if ChiAngle[0] <= 90. and ChiAngle[0+1] > 90.:
            y5 = y0 + radius + width
        else:
            y5 = 0
        for i in range(int(np.amin([y1,y2,y3,y4])),int(np.amax([y1,y2,y3,y4,y5]))+1):
            for j in range(int(np.amin([x1,x2,x3,x4])),int(np.amax([x1,x2,x3,x4]))+1):
                if (j-x0)**2+(i-y0)**2 > (radius-width)**2 and\
                   (j-x0)**2+(i-y0)**2 < (radius+width)**2 and\
                   (j-x0)/np.sqrt((i-y0)**2+(j-x0)**2) < np.cos(ChiAngle[0]*np.pi/180) and\
                   (j-x0)/np.sqrt((i-y0)**2+(j-x0)**2) > np.cos(ChiAngle[1]*np.pi/180):
                       indices = np.append(indices,[[i,j]],axis=0)
                       cit+=1
        RotationTensor = np.array([[[-np.sin((theta-ChiAngle[0])*np.pi/180),np.cos((theta-ChiAngle[0])*np.pi/180)],\
                                    [np.cos((theta-ChiAngle[0])*np.pi/180), np.sin((theta-ChiAngle[0])*np.pi/180)]] for theta in ChiAngle])
        ImageIndices =np.tensordot(RotationTensor,(indices[1:-1]-[y0,x0]).T,axes=1).astype(int)
        ChiProfile = np.sum([self._img[ImageIndices[i,1,:]+int(y0),ImageIndices[i,0,:]+int(x0)] for i in range(ChiTotalSteps+1)], axis=1)/cit
        self.addChart(np.flip(ChiAngle2,axis=0),ChiProfile/np.amax(np.amax(self._img)),"arc")
        self.chartIsPresent = True
        #print("Chi Scan run time is: {} s\nThe size is: {}\n".format(np.round(time.time()-start_time,5),(ChiTotalSteps+1)*cit))

    def mouseMoveEvent(self, event):
        if self.chart().plotArea().contains(event.pos()) and self.chartIsPresent:
            self.setCursor(QtCore.Qt.CrossCursor)
            position = self.chart().mapToValue(event.pos())
            self.chartMouseMovement.emit(position,"chart")
        else:
            self.setCursor(QtCore.Qt.ArrowCursor)
        super(ProfileChart, self).mouseMoveEvent(event)
