from PyQt6 import QtCore, QtWidgets, QtGui, QtCharts, QtSvg
import numpy as np
import os

class PlotChart(QtWidgets.QWidget):

    CHART_IS_PRESENT = False

    def __init__(self,theme,coord):
        super(PlotChart,self).__init__()
        self.dirname = os.path.dirname(__file__)
        self.type = coord
        if theme == 0:
            self.theme = QtCharts.QChart.ChartTheme.ChartThemeLight
        if theme == 1:
            self.theme = QtCharts.QChart.ChartTheme.ChartThemeBlueCerulean
        if theme == 2:
            self.theme = QtCharts.QChart.ChartTheme.ChartThemeDark
        if theme == 3:
            self.theme = QtCharts.QChart.ChartTheme.ChartThemeBrownSand
        if theme == 4:
            self.theme = QtCharts.QChart.ChartTheme.ChartThemeBlueNcs
        if theme == 5:
            self.theme = QtCharts.QChart.ChartTheme.ChartThemeHighContrast
        if theme == 6:
            self.theme = QtCharts.QChart.ChartTheme.ChartThemeBlueIcy
        if theme == 7:
            self.theme = QtCharts.QChart.ChartTheme.ChartThemeQt
        self.chartView = PlotChartView()

    def main(self):
        self.chartView.SAVE_TEXT.connect(self.save_polar_as_text)
        self.chartView.SAVE_IMAGE.connect(self.save_polar_as_image)
        self.chartView.SAVE_SVG.connect(self.save_polar_as_SVG)
        self.chartView.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        self.chartView.setContentsMargins(0,0,0,0)
        if self.type == 'Polar':
            self.profileChart = QtCharts.QPolarChart()
        elif self.type == 'Normal':
            self.profileChart = QtCharts.QChart()
        self.profileChart.setBackgroundRoundness(0)
        self.profileChart.setMargins(QtCore.QMargins(0,0,0,0))
        self.profileChart.setTheme(self.theme)
        self.chartView.setChart(self.profileChart)
        self.coordinate = QtWidgets.QLabel("")
        self.chartView.CHART_MOUSE_MOVEMENT.connect(self.update_coordinate)
        self.chartView.CHART_MOUSE_LEAVE.connect(self.clear_coordinate)
        self.Grid = QtWidgets.QGridLayout()
        self.Grid.addWidget(self.chartView,0,0)
        self.Grid.addWidget(self.coordinate,1,0)
        self.setLayout(self.Grid)

    def toggle_dark_mode(self, mode):
        if mode == 'light':
            self.theme = QtCharts.QChart.ChartTheme.ChartThemeLight
        elif mode == 'dark':
            self.theme = QtCharts.QChart.ChartTheme.ChartThemeDark
        self.profileChart.setTheme(self.theme)
        self.adjust_color('toggle dark mode',self.current_color)

    def update_coordinate(self,pos):
        if self.type == "Polar":
            self.coordinate.setText("(r={:5.2f}, \u03C6={:5.2f})".format(pos.y(),pos.x()))
        elif self.type == "Normal":
            self.coordinate.setText("(x={:5.2f}, y={:5.2f})".format(pos.x(),pos.y()))

    def clear_coordinate(self):
        self.coordinate.setText("")

    def refresh(self,theme):
        if theme == 0:
            self.theme = QtCharts.QChart.ChartTheme.ChartThemeLight
        elif theme == 1:
            self.theme = QtCharts.QChart.ChartTheme.ChartThemeBlueCerulean
        elif theme == 2:
            self.theme = QtCharts.QChart.ChartTheme.ChartThemeDark
        elif theme == 3:
            self.theme = QtCharts.QChart.ChartTheme.ChartThemeBrownSand
        elif theme == 4:
            self.theme = QtCharts.QChart.ChartTheme.ChartThemeBlueNcs
        elif theme == 5:
            self.theme = QtCharts.QChart.ChartTheme.ChartThemeHighContrast
        elif theme == 6:
            self.theme = QtCharts.QChart.ChartTheme.ChartThemeBlueIcy
        elif theme == 7:
            self.theme = QtCharts.QChart.ChartTheme.ChartThemeQt
        else:
            self.raise_error("Wrong theme")
        self.profileChart.setTheme(self.theme)

    def add_chart(self,radius,profile,preset,fontname,fontsize,color,switchXY,kwargs):
        self.current_color = color
        if self.type == 'Polar':
            pen1 = QtGui.QPen(QtCore.Qt.PenStyle.SolidLine)
            pen1.setWidth(3)
            pen1.setColor(QtGui.QColor(color))
            pen2 = QtGui.QPen(QtCore.Qt.PenStyle.DotLine)
            pen2.setWidth(3)
            pen2.setColor(QtGui.QColor(color))
            if preset == 'IA':
                Phi1 = profile
                Phi2 = profile + np.full(len(profile),180)
                Radius = radius/np.amax(radius)
            elif preset == 'FA':
                Phi1 = profile
                Phi2 = profile + np.full(len(profile),180)
                Radius = radius
            elif preset == 'general':
                Phi = profile
                Radius = radius
            series1 = QtCharts.QLineSeries()
            series1.setPen(pen1)
            series2 = QtCharts.QLineSeries()
            series2.setPen(pen2)
            self.currentRadius = []
            self.currentProfile = []
            if not switchXY:
                for x,y in zip(Phi1,Radius):
                    series1.append(x,y)
                    self.currentRadius.append(x)
                    self.currentProfile.append(y)
                for x,y in zip(Phi2,Radius):
                    series2.append(x,y)
                    self.currentRadius.append(x)
                    self.currentProfile.append(y)
            else:
                for y,x in zip(Phi1,Radius):
                    series1.append(x,y)
                    self.currentRadius.append(x)
                    self.currentProfile.append(y)
                for y,x in zip(Phi2,Radius):
                    series2.append(x,y)
                    self.currentRadius.append(x)
                    self.currentProfile.append(y)
            self.profileChart = QtCharts.QPolarChart()
            self.profileChart.setTheme(self.theme)
            self.profileChart.setBackgroundRoundness(0)
            self.profileChart.setMargins(QtCore.QMargins(0,0,0,0))
            self.profileChart.removeAllSeries()
            self.profileChart.addSeries(series1)
            self.profileChart.addSeries(series2)
            self.profileChart.setTitleFont(QtGui.QFont(fontname,fontsize,57))
            self.profileChart.legend().setVisible(False)
            self.axisR = QtCharts.QValueAxis()
            self.axisR.setTickCount(10)
            self.axisR.setLabelFormat("%.1f")
            self.axisR.setLabelsFont(QtGui.QFont(fontname,fontsize,57))
            self.axisR.setTitleFont(QtGui.QFont(fontname,fontsize,57))
            self.axisP = QtCharts.QValueAxis()
            self.axisP.setTickCount(13)
            self.axisP.setLabelFormat("%.1f")
            self.axisP.setRange(0,360)
            self.axisP.setLabelsFont(QtGui.QFont(fontname,fontsize,57))
            self.axisP.setTitleFont(QtGui.QFont(fontname,fontsize,57))
            if preset == 'IA':
                z = kwargs['Kp']
                low = kwargs['low']
                high = kwargs['high']
                self.profileChart.setTitle('Intensity vs Azimuth at Kperp = {:6.2f} (\u212B\u207B\u00B9)'.format(z))
                self.axisR.setTitleText('Intensity (arb. units)')
                self.axisR.setRange(low,high)
            elif preset == 'FA':
                z = kwargs['Kp']
                low = kwargs['low']
                high = kwargs['high']
                self.profileChart.setTitle('HWHM vs Azimuth at Kperp = {:6.2f} (\u212B\u207B\u00B9)'.format(z))
                self.axisR.setTitleText('HWHM (\u212B\u207B\u00B9)')
                self.axisR.setRange(low,high)
            elif preset == 'general':
                title = kwargs['title']
                r_label = kwargs['r_label']
                r_unit = kwargs['r_unit']
                low = kwargs['low']
                high = kwargs['high']
                self.profileChart.setTitle(title)
                self.axisR.setTitleText(r_label+" ("+r_unit+")")
                self.axisR.setRange(low,high)
            self.profileChart.addAxis(self.axisR, QtCharts.QPolarChart.PolarOrientationRadial)
            self.profileChart.addAxis(self.axisP, QtCharts.QPolarChart.PolarOrientationAngular)
            series1.attachAxis(self.axisR)
            series1.attachAxis(self.axisP)
            series2.attachAxis(self.axisR)
            series2.attachAxis(self.axisP)
            self.chartView.setChart(self.profileChart)
            self.chartView.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.DefaultContextMenu)
            self.CHART_IS_PRESENT = True
        elif self.type == 'Normal':
            pen = QtGui.QPen(QtCore.Qt.PenStyle.SolidLine)
            pen.setWidth(3)
            pen.setColor(QtGui.QColor(color))
            series = QtCharts.QLineSeries()
            series.setPen(pen)
            self.currentRadius = []
            self.currentProfile = []
            if not switchXY:
                for x,y in zip(radius,profile):
                    series.append(x,y)
                    self.currentRadius.append(x)
                    self.currentProfile.append(y)
            else:
                for y,x in zip(radius,profile):
                    series.append(x,y)
                    self.currentRadius.append(x)
                    self.currentProfile.append(y)
            self.profileChart = QtCharts.QChart()
            self.profileChart.setTheme(self.theme)
            self.profileChart.setBackgroundRoundness(0)
            self.profileChart.setMargins(QtCore.QMargins(0,0,0,0))
            self.profileChart.removeAllSeries()
            self.profileChart.addSeries(series)
            self.profileChart.setTitleFont(QtGui.QFont(fontname,fontsize,57))
            self.profileChart.legend().setVisible(False)
            self.axisX = QtCharts.QValueAxis()
            self.axisX.setTickCount(10)
            self.axisX.setLabelsFont(QtGui.QFont(fontname,fontsize,57))
            self.axisX.setTitleFont(QtGui.QFont(fontname,fontsize,57))
            self.axisY = QtCharts.QValueAxis()
            self.axisY.setTickCount(10)
            self.axisY.setLabelsFont(QtGui.QFont(fontname,fontsize,57))
            self.axisY.setTitleFont(QtGui.QFont(fontname,fontsize,57))
            if preset == "IK":
                Az = kwargs['Az']
                self.profileChart.setTitle('Intensity vs Kperp at \u03C6 = {:5.1f} (\u00BA)'.format(Az))
                self.axisX.setTitleText("Intensity (arb. units)")
                self.axisY.setTitleText("Kperp (\u212B\u207B\u00B9)")
            elif preset == "FK":
                Az = kwargs['Az']
                self.profileChart.setTitle('HWHM vs Kperp at \u03C6 = {:5.1f} (\u00BA)'.format(Az))
                self.axisX.setTitleText("HWHM (\u212B\u207B\u00B9)")
                self.axisY.setTitleText("Kperp (\u212B\u207B\u00B9)")
            elif preset == "general":
                title = kwargs['title']
                x_label = kwargs['x_label']
                x_unit = kwargs['x_unit']
                y_label = kwargs['y_label']
                y_unit = kwargs['y_unit']
                self.profileChart.setTitle(title)
                self.axisX.setTitleText(x_label+" ("+x_unit+")")
                self.axisY.setTitleText(y_label+" ("+y_unit+")")
            self.profileChart.addAxis(self.axisX, QtCore.Qt.AlignmentFlag.AlignBottom)
            self.profileChart.addAxis(self.axisY, QtCore.Qt.AlignmentFlag.AlignLeft)
            series.attachAxis(self.axisX)
            series.attachAxis(self.axisY)
            self.profileChart.legend().setVisible(False)
            self.chartView.setChart(self.profileChart)
            self.chartView.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.DefaultContextMenu)
            self.CHART_IS_PRESENT = True

    def adjust_fonts(self,fontname,fontsize):
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

    def adjust_color(self,name,color):
        self.current_color = color
        if self.CHART_IS_PRESENT:
            if self.type == "Polar":
                pen1 = QtGui.QPen(QtCore.Qt.PenStyle.SolidLine)
                pen1.setWidth(3)
                pen1.setColor(QtGui.QColor(self.current_color))
                pen2 = QtGui.QPen(QtCore.Qt.PenStyle.DotLine)
                pen2.setWidth(3)
                pen2.setColor(QtGui.QColor(self.current_color))
                self.profileChart.series()[-2].setPen(pen1)
                self.profileChart.series()[-1].setPen(pen2)
            elif self.type == "Normal":
                pen = QtGui.QPen(QtCore.Qt.PenStyle.SolidLine)
                pen.setWidth(3)
                pen.setColor(QtGui.QColor(self.current_color))
                self.profileChart.series()[-1].setPen(pen)

    def save_polar_as_text(self):
        if self.CHART_IS_PRESENT:
            self.filename = QtWidgets.QFileDialog.getSaveFileName(None,"choose save file name",os.join(self.dirname,"polar.txt"),"Text (*.txt)")
            if not self.filename[0] == "":
                np.savetxt(self.filename[0],np.vstack((self.currentRadius,self.currentProfile)).transpose(),fmt='%5.3f')
            else:
                return
        else:
            self.raise_error("No plot is available")

    def save_polar_as_image(self):
        if self.CHART_IS_PRESENT:
            self.filename = QtWidgets.QFileDialog.getSaveFileName(None,"choose save file name",os.join(self.dirname,"plot.png"),"PNG (*.png);;JPEG (*.jpeg);;GIF (*.gif);;BMP (*.bmp)")
            if not self.filename[0] == "":
                output_size = QtCore.QSize(int(self.profileChart.size().width()),int(self.profileChart.size().height()))
                output_rect = QtCore.QRectF(QtCore.QPointF(0,0),QtCore.QSizeF(output_size))
                image = QtGui.QImage(output_size,QtGui.QImage.Format.Format_ARGB32)
                image.fill(QtCore.Qt.GlobalColor.transparent)
                painter = QtGui.QPainter()
                painter.begin(image)
                painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
                self.profileChart.scene().render(painter, source=output_rect,target=output_rect,mode=QtCore.Qt.AspectRatioMode.IgnoreAspectRatio)
                painter.end()
                image.save(self.filename[0])
            else:
                return
        else:
            self.raise_error("No plot is available")

    def save_polar_as_SVG(self):
        if self.CHART_IS_PRESENT:
            self.filename = QtWidgets.QFileDialog.getSaveFileName(None,"choose save file name",os.join(self.dirname,"plot.svg"),"SVG (*.svg)")
            if not self.filename[0] == "":
                output_size = QtCore.QSize(int(self.profileChart.size().width()),int(self.profileChart.size().height()))
                output_rect = QtCore.QRectF(QtCore.QPointF(0,0),QtCore.QSizeF(output_size))
                svg = QtSvg.QSvgGenerator()
                svg.setFileName(self.filename[0])
                svg.setSize(output_size)
                svg.setViewBox(output_rect)
                painter = QtGui.QPainter()
                painter.begin(svg)
                painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
                self.profileChart.scene().render(painter, source=output_rect,target=output_rect,mode=QtCore.Qt.AspectRatioMode.IgnoreAspectRatio)
                painter.end()
            else:
                return
        else:
            self.raise_error("No plot is available")

    def raise_error(self,message):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        msg.setEscapeButton(QtWidgets.QMessageBox.StandardButton.Close)
        msg.exec()

    def raise_attention(self,information):
        info = QtWidgets.QMessageBox()
        info.setIcon(QtWidgets.QMessageBox.Icon.Information)
        info.setText(information)
        info.setWindowTitle("Information")
        info.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        info.setEscapeButton(QtWidgets.QMessageBox.StandardButton.Close)
        info.exec()


class PlotChartView(QtCharts.QChartView):

    SAVE_TEXT = QtCore.pyqtSignal()
    SAVE_IMAGE = QtCore.pyqtSignal()
    SAVE_SVG = QtCore.pyqtSignal()
    CHART_MOUSE_MOVEMENT = QtCore.pyqtSignal(QtCore.QPointF)
    CHART_MOUSE_LEAVE = QtCore.pyqtSignal()

    def __init__(self):
        super(PlotChartView,self).__init__()

    def contextMenuEvent(self,event):
        """This is an overload function"""
        self.menu = QtWidgets.QMenu()
        self.saveAsText = QtGui.QAction('Save as text...')
        self.saveAsText.triggered.connect(self.save_polar_as_text)
        self.saveAsImage = QtGui.QAction('Save as an image...')
        self.saveAsImage.triggered.connect(self.save_polar_as_image)
        self.saveAsSVG = QtGui.QAction('Export as SVG...')
        self.saveAsSVG.triggered.connect(self.save_polar_as_SVG)
        self.menu.addAction(self.saveAsText)
        self.menu.addAction(self.saveAsImage)
        self.menu.addAction(self.saveAsSVG)
        self.menu.popup(event.globalPos())

    def mouseMoveEvent(self, event):
        """This is an overload function"""
        if self.chart().plotArea().contains(event.position().toPoint()):
            self.setCursor(QtCore.Qt.CursorShape.CrossCursor)
            position = self.chart().mapToValue(event.position().toPoint())
            self.CHART_MOUSE_MOVEMENT.emit(position)
        else:
            self.setCursor(QtCore.Qt.CursorShape.ArrowCursor)
            self.CHART_MOUSE_LEAVE.emit()
        super(PlotChartView, self).mouseMoveEvent(event)

    def save_polar_as_text(self):
        self.SAVE_TEXT.emit()

    def save_polar_as_image(self):
        self.SAVE_IMAGE.emit()

    def save_polar_as_SVG(self):
        self.SAVE_SVG.emit()
