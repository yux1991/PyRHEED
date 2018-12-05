from PyQt5 import QtCore, QtWidgets, QtGui, QtChart
import Process

class ProfileChart(QtChart.QChartView,Process.Image):

    progressAdvance = QtCore.pyqtSignal(int,int,int)
    progressEnd = QtCore.pyqtSignal()
    chartMouseMovement = QtCore.pyqtSignal(QtCore.QPointF,str)
    chartIsPresent = False

    def __init__(self,config):
        super(ProfileChart,self).__init__()
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
        self.profileChart = QtChart.QChart()
        self.profileChart.setTheme(self.theme)
        self.profileChart.setBackgroundRoundness(0)
        self.profileChart.setMargins(QtCore.QMargins(0,0,0,0))
        self.setChart(self.profileChart)

    def refresh(self,config):
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
        self.profileChart.setTheme(self.theme)

    def addChart(self,radius,profile,type="line"):
        series = QtChart.QLineSeries()
        for x,y in zip(radius,profile):
            series.append(x,y)
        self.profileChart = QtChart.QChart()
        self.profileChart.setTheme(self.theme)
        self.profileChart.setBackgroundRoundness(0)
        self.profileChart.setMargins(QtCore.QMargins(0,0,0,0))
        self.profileChart.addSeries(series)
        axisX = QtChart.QValueAxis()
        axisX.setTickCount(10)
        if type == "line" or type == "rectangle":
            axisX.setTitleText("K (\u212B\u207B\u00B9)")
        elif type == "arc":
            axisX.setTitleText("\u03A7 (\u00BA)")
        axisY = QtChart.QValueAxis()
        axisY.setTickCount(10)
        axisY.setTitleText("Intensity (arb. units)")
        self.profileChart.addAxis(axisX, QtCore.Qt.AlignBottom)
        self.profileChart.addAxis(axisY, QtCore.Qt.AlignLeft)
        series.attachAxis(axisX)
        series.attachAxis(axisY)
        self.profileChart.legend().setVisible(False)
        self.setChart(self.profileChart)

    def setImg(self,img):
        self._img = img

    def setScaleFactor(self,s):
        self._scaleFactor = s

    def lineScan(self,start,end):
        x,y = self.getLineScan(start,end,self._img,self._scaleFactor)
        self.addChart(x,y,"line")
        self.chartIsPresent = True

    def integral(self,start,end,width):
        x,y = self.getIntegral(start,end,width,self._img,self._scaleFactor)
        self.addChart(x,y,"rectangle")
        self.chartIsPresent = True

    def chiScan(self,center,radius,width,chiRange,tilt,chiStep=1):
        x,y = self.getChiScan(center,radius,width,chiRange,tilt,self._img,chiStep)
        self.addChart(x,y,"arc")
        self.chartIsPresent = True

    def mouseMoveEvent(self, event):
        if self.chart().plotArea().contains(event.pos()) and self.chartIsPresent:
            self.setCursor(QtCore.Qt.CrossCursor)
            position = self.chart().mapToValue(event.pos())
            self.chartMouseMovement.emit(position,"chart")
        else:
            self.setCursor(QtCore.Qt.ArrowCursor)
        super(ProfileChart, self).mouseMoveEvent(event)
