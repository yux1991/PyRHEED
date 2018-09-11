from PyQt5 import QtCore, QtGui, QtChart
import numpy as np
import math

class ProfileChart(QtChart.QChartView):

    def __init__(self,parent):
        super(ProfileChart,self).__init__(parent)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self._img = []
        self._scaleFactor = 1

    def addChart(self,radius,profile,type="line"):
        series = QtChart.QLineSeries()
        for x,y in zip(radius,profile):
            series.append(x,y)
        chart = QtChart.QChart()
        chart.setTheme(QtChart.QChart.ChartThemeLight)
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
        x0,y0,x1,y1 = start.x(),start.y(),end.x(),end.y()
        K_length = max(int(abs(x1-x0)+1),int(abs(y1-y0)+1))
        Kx = np.linspace(x0,x1,K_length)
        Ky = np.linspace(y0,y1,K_length)
        LineScanIntensities = np.zeros(len(Kx))
        for i in range(0,len(Kx)):
            LineScanIntensities[i] = self._img[int(Ky[i]),int(Kx[i])]
        LineScanRadius = np.linspace(0,math.sqrt((x1-x0)**2+(y1-y0)**2),len(Kx))
        self.addChart(LineScanRadius/self._scaleFactor,LineScanIntensities/np.amax(np.amax(self._img)),"line")

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
        self.addChart(LineScanRadius/self._scaleFactor,LineScanIntensities/2/width/np.amax(np.amax(self._img)),"rectangle")

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
        self.addChart(ChiAngle2[0:-1],ChiProfile/np.amax(np.amax(self._img)),"arc")
