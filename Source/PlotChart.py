from PyQt5 import QtCore, QtWidgets, QtGui, QtChart, QtSvg
import numpy as np

class PlotChart(QtWidgets.QWidget):

    chartIsPresent = False

    def __init__(self,config,coord):
        super(PlotChart,self).__init__()
        chartDefault = dict(config['chartDefault'].items())
        self.type = coord
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
        self.chartView = PlotChartView()

    def Main(self):
        self.chartView.saveText.connect(self.savePolarAsText)
        self.chartView.saveImage.connect(self.savePolarAsImage)
        self.chartView.saveSVG.connect(self.savePolarAsSVG)
        self.chartView.setRenderHint(QtGui.QPainter.Antialiasing)
        self.chartView.setContentsMargins(0,0,0,0)
        if self.type == 'Polar':
            self.profileChart = QtChart.QPolarChart()
        elif self.type == 'Normal':
            self.profileChart = QtChart.QChart()
        self.profileChart.setBackgroundRoundness(0)
        self.profileChart.setMargins(QtCore.QMargins(0,0,0,0))
        self.profileChart.setTheme(self.theme)
        self.chartView.setChart(self.profileChart)
        self.coordinate = QtWidgets.QLabel("")
        self.chartView.chartMouseMovement.connect(self.updateCoordinate)
        self.chartView.chartMouseLeave.connect(self.clearCoordinate)
        self.Grid = QtWidgets.QGridLayout()
        self.Grid.addWidget(self.chartView,0,0)
        self.Grid.addWidget(self.coordinate,1,0)
        self.setLayout(self.Grid)

    def updateCoordinate(self,pos):
        if self.type == "Polar":
            self.coordinate.setText("(r={:5.2f}, \u03C6={:5.2f})".format(pos.y(),pos.x()))
        elif self.type == "Normal":
            self.coordinate.setText("(x={:5.2f}, y={:5.2f})".format(pos.x(),pos.y()))

    def clearCoordinate(self):
        self.coordinate.setText("")

    def refresh(self,config):
        chartDefault = dict(config['chartDefault'].items())
        if int(chartDefault['theme']) == 0:
            self.theme = QtChart.QChart.ChartThemeLight
        elif int(chartDefault['theme']) == 1:
            self.theme = QtChart.QChart.ChartThemeBlueCerulean
        elif int(chartDefault['theme']) == 2:
            self.theme = QtChart.QChart.ChartThemeDark
        elif int(chartDefault['theme']) == 3:
            self.theme = QtChart.QChart.ChartThemeBrownSand
        elif int(chartDefault['theme']) == 4:
            self.theme = QtChart.QChart.ChartThemeBlueNcs
        elif int(chartDefault['theme']) == 5:
            self.theme = QtChart.QChart.ChartThemeHighContrast
        elif int(chartDefault['theme']) == 6:
            self.theme = QtChart.QChart.ChartThemeBlueIcy
        elif int(chartDefault['theme']) == 7:
            self.theme = QtChart.QChart.ChartThemeQt
        else:
            self.Raise_Error("Wrong theme")
        self.profileChart.setTheme(self.theme)

    def addChart(self,radius,profile,type,fontname,fontsize,color,kwargs):
        if self.type == 'Polar':
            Phi = np.append(profile,profile + np.full(len(profile),180))
            pen = QtGui.QPen(QtCore.Qt.SolidLine)
            pen.setWidth(3)
            if type == 'IA' or 'IK':
                Radius = np.append(radius,radius)/np.amax(radius)
            elif type == 'FA' or 'FK':
                Radius = np.append(radius,radius)
            pen.setColor(QtGui.QColor(color))
            z = kwargs['Kp']
            low = kwargs['low']
            high = kwargs['high']
            series = QtChart.QLineSeries()
            series.setPen(pen)
            self.currentRadius = []
            self.currentProfile = []
            for x,y in zip(Phi,Radius):
                series.append(x,y)
                self.currentRadius.append(x)
                self.currentProfile.append(y)
            self.profileChart = QtChart.QPolarChart()
            self.profileChart.setTheme(self.theme)
            self.profileChart.setBackgroundRoundness(0)
            self.profileChart.setMargins(QtCore.QMargins(0,0,0,0))
            self.profileChart.removeAllSeries()
            self.profileChart.addSeries(series)
            self.profileChart.setTitleFont(QtGui.QFont(fontname,fontsize,57))
            self.profileChart.legend().setVisible(False)
            self.axisR = QtChart.QValueAxis()
            self.axisR.setTickCount(10)
            self.axisR.setLabelFormat("%.1f")
            self.axisR.setRange(low,high)
            self.axisR.setLabelsFont(QtGui.QFont(fontname,fontsize,57))
            self.axisR.setTitleFont(QtGui.QFont(fontname,fontsize,57))
            self.axisP = QtChart.QValueAxis()
            self.axisP.setTickCount(13)
            self.axisP.setLabelFormat("%.1f")
            self.axisP.setRange(0,360)
            self.axisP.setLabelsFont(QtGui.QFont(fontname,fontsize,57))
            self.axisP.setTitleFont(QtGui.QFont(fontname,fontsize,57))
            if type == 'IA':
                self.profileChart.setTitle('Intensity vs Azimuth at Kperp = {:6.2f} (\u212B\u207B\u00B9)'.format(z))
                self.axisR.setTitleText('Intensity (arb. units)')
            elif type == 'FA':
                self.profileChart.setTitle('HWHM vs Azimuth at Kperp = {:6.2f} (\u212B\u207B\u00B9)'.format(z))
                self.axisR.setTitleText('HWHM (\u212B\u207B\u00B9)')
            self.profileChart.addAxis(self.axisR, QtChart.QPolarChart.PolarOrientationRadial)
            self.profileChart.addAxis(self.axisP, QtChart.QPolarChart.PolarOrientationAngular)
            series.attachAxis(self.axisR)
            series.attachAxis(self.axisP)
            self.chartView.setChart(self.profileChart)
            self.chartView.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
            self.chartIsPresent = True
        elif self.type == 'Normal':
            Az = kwargs['Az']
            pen = QtGui.QPen(QtCore.Qt.SolidLine)
            pen.setWidth(3)
            pen.setColor(QtGui.QColor(color))
            series = QtChart.QLineSeries()
            series.setPen(pen)
            self.currentRadius = []
            self.currentProfile = []
            for y,x in zip(radius,profile):
                series.append(x,y)
                self.currentRadius.append(x)
                self.currentProfile.append(y)
            self.profileChart = QtChart.QChart()
            self.profileChart.setTheme(self.theme)
            self.profileChart.setBackgroundRoundness(0)
            self.profileChart.setMargins(QtCore.QMargins(0,0,0,0))
            self.profileChart.removeAllSeries()
            self.profileChart.addSeries(series)
            self.profileChart.setTitleFont(QtGui.QFont(fontname,fontsize,57))
            self.profileChart.legend().setVisible(False)
            self.axisX = QtChart.QValueAxis()
            self.axisX.setTickCount(10)
            self.axisX.setLabelsFont(QtGui.QFont(fontname,fontsize,57))
            self.axisX.setTitleFont(QtGui.QFont(fontname,fontsize,57))
            self.axisY = QtChart.QValueAxis()
            self.axisY.setTickCount(10)
            self.axisY.setLabelsFont(QtGui.QFont(fontname,fontsize,57))
            self.axisY.setTitleFont(QtGui.QFont(fontname,fontsize,57))
            self.axisY.setTitleText("Kperp (\u212B\u207B\u00B9)")
            if type == "IK":
                self.profileChart.setTitle('Intensity vs Kperp at \u03C6 = {:5.1f} (\u00BA)'.format(Az))
                self.axisX.setTitleText("Intensity (arb. units)")
            elif type == "FK":
                self.profileChart.setTitle('HWHM vs Kperp at \u03C6 = {:5.1f} (\u00BA)'.format(Az))
                self.axisX.setTitleText("HWHM (\u212B\u207B\u00B9)")
            self.profileChart.addAxis(self.axisX, QtCore.Qt.AlignBottom)
            self.profileChart.addAxis(self.axisY, QtCore.Qt.AlignLeft)
            series.attachAxis(self.axisX)
            series.attachAxis(self.axisY)
            self.profileChart.legend().setVisible(False)
            self.chartView.setChart(self.profileChart)
            self.chartView.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
            self.chartIsPresent = True

    def adjustFonts(self,fontname,fontsize):
        try:
            self.profileChart.setTitleFont(QtGui.QFont(fontname,fontsize,57))
            if self.type == 'Polar':
                self.axisR.setLabelsFont(QtGui.QFont(fontname,fontsize,57))
                self.axisR.setTitleFont(QtGui.QFont(fontname,fontsize,57))
                self.axisP.setLabelsFont(QtGui.QFont(fontname,fontsize,57))
                self.axisP.setTitleFont(QtGui.QFont(fontname,fontsize,57))
            elif self.type == "Normal":
                self.axisX.setLabelsFont(QtGui.QFont(fontname,fontsize,57))
                self.axisX.setTitleFont(QtGui.QFont(fontname,fontsize,57))
                self.axisY.setLabelsFont(QtGui.QFont(fontname,fontsize,57))
                self.axisY.setTitleFont(QtGui.QFont(fontname,fontsize,57))
        except:
            pass

    def adjustColor(self,name,color):
        pen = QtGui.QPen(QtCore.Qt.SolidLine)
        pen.setWidth(3)
        pen.setColor(QtGui.QColor(color))
        self.profileChart.series()[-1].setPen(pen)


    def savePolarAsText(self):
        if self.chartIsPresent:
            self.filename = QtWidgets.QFileDialog.getSaveFileName(None,"choose save file name","./polar.txt","Text (*.txt)")
            if not self.filename[0] == "":
                np.savetxt(self.filename[0],np.vstack((self.currentRadius,self.currentProfile)).transpose(),fmt='%5.3f')
            else:
                return
        else:
            self.Raise_Error("No plot is available")

    def savePolarAsImage(self):
        if self.chartIsPresent:
            self.filename = QtWidgets.QFileDialog.getSaveFileName(None,"choose save file name","./plot.png","PNG (*.png);;JPEG (*.jpeg);;GIF (*.gif);;BMP (*.bmp)")
            if not self.filename[0] == "":
                output_size = QtCore.QSize(800,600)
                output_rect = QtCore.QRectF(QtCore.QPointF(0,0),QtCore.QSizeF(output_size))
                image = QtGui.QImage(output_size,QtGui.QImage.Format_ARGB32)
                image.fill(QtCore.Qt.transparent)
                original_size = self.profileChart.size()
                self.profileChart.resize(QtCore.QSizeF(output_size))
                painter = QtGui.QPainter()
                painter.begin(image)
                painter.setRenderHint(QtGui.QPainter.Antialiasing)
                self.profileChart.scene().render(painter, source=output_rect,target=output_rect,mode=QtCore.Qt.IgnoreAspectRatio)
                painter.end()
                self.profileChart.resize(original_size)
                image.save(self.filename[0])
            else:
                return
        else:
            self.Raise_Error("No plot is available")

    def savePolarAsSVG(self):
        if self.chartIsPresent:
            self.filename = QtWidgets.QFileDialog.getSaveFileName(None,"choose save file name","./plot.svg","SVG (*.svg)")
            if not self.filename[0] == "":
                output_size = QtCore.QSize(800,600)
                output_rect = QtCore.QRectF(QtCore.QPointF(0,0),QtCore.QSizeF(output_size))

                svg = QtSvg.QSvgGenerator()
                svg.setFileName(self.filename[0])
                svg.setSize(output_size)
                svg.setViewBox(output_rect)

                original_size = self.profileChart.size()
                self.profileChart.resize(QtCore.QSizeF(output_size))
                painter = QtGui.QPainter()
                painter.begin(svg)
                painter.setRenderHint(QtGui.QPainter.Antialiasing)
                self.profileChart.scene().render(painter, source=output_rect,target=output_rect,mode=QtCore.Qt.IgnoreAspectRatio)
                painter.end()
                self.profileChart.resize(original_size)
            else:
                return
        else:
            self.Raise_Error("No plot is available")

    def Raise_Error(self,message):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.setEscapeButton(QtWidgets.QMessageBox.Close)
        msg.exec()

    def Raise_Attention(self,information):
        info = QtWidgets.QMessageBox()
        info.setIcon(QtWidgets.QMessageBox.Information)
        info.setText(information)
        info.setWindowTitle("Information")
        info.setStandardButtons(QtWidgets.QMessageBox.Ok)
        info.setEscapeButton(QtWidgets.QMessageBox.Close)
        info.exec()


class PlotChartView(QtChart.QChartView):

    saveText = QtCore.pyqtSignal()
    saveImage = QtCore.pyqtSignal()
    saveSVG = QtCore.pyqtSignal()
    chartMouseMovement = QtCore.pyqtSignal(QtCore.QPointF)
    chartMouseLeave = QtCore.pyqtSignal()

    def __init__(self):
        super(PlotChartView,self).__init__()

    def contextMenuEvent(self,event):
        self.menu = QtWidgets.QMenu()
        self.saveAsText = QtWidgets.QAction('Save as text...')
        self.saveAsText.triggered.connect(self.savePolarAsText)
        self.saveAsImage = QtWidgets.QAction('Save as an image...')
        self.saveAsImage.triggered.connect(self.savePolarAsImage)
        self.saveAsSVG = QtWidgets.QAction('Export as SVG...')
        self.saveAsSVG.triggered.connect(self.savePolarAsSVG)
        self.menu.addAction(self.saveAsText)
        self.menu.addAction(self.saveAsImage)
        self.menu.addAction(self.saveAsSVG)
        self.menu.popup(event.globalPos())

    def mouseMoveEvent(self, event):
        if self.chart().plotArea().contains(event.pos()):
            self.setCursor(QtCore.Qt.CrossCursor)
            position = self.chart().mapToValue(event.pos())
            self.chartMouseMovement.emit(position)
        else:
            self.setCursor(QtCore.Qt.ArrowCursor)
            self.chartMouseLeave.emit()
        super(PlotChartView, self).mouseMoveEvent(event)

    def savePolarAsText(self):
        self.saveText.emit()

    def savePolarAsImage(self):
        self.saveImage.emit()

    def savePolarAsSVG(self):
        self.saveSVG.emit()
