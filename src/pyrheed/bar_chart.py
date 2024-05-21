from process import Image
from PyQt6 import QtCore, QtWidgets, QtGui, QtCharts, QtSvg
import numpy as np

class BarChart(QtCharts.QChartView):
    CHART_IS_PRESENT = False
    FONTS_CHANGED = QtCore.pyqtSignal(str,int)

    def __init__(self,config):
        super(BarChart,self).__init__()
        chartDefault = dict(config['chartDefault'].items())
        if int(chartDefault['theme']) == 0:
            self.theme = QtCharts.QChart.ChartTheme.ChartThemeLight
        if int(chartDefault['theme']) == 1:
            self.theme = QtCharts.QChart.ChartTheme.ChartThemeBlueCerulean
        if int(chartDefault['theme']) == 2:
            self.theme = QtCharts.QChart.ChartTheme.ChartThemeDark
        if int(chartDefault['theme']) == 3:
            self.theme = QtCharts.QChart.ChartTheme.ChartThemeBrownSand
        if int(chartDefault['theme']) == 4:
            self.theme = QtCharts.QChart.ChartTheme.ChartThemeBlueNcs
        if int(chartDefault['theme']) == 5:
            self.theme = QtCharts.QChart.ChartTheme.ChartThemeHighContrast
        if int(chartDefault['theme']) == 6:
            self.theme = QtCharts.QChart.ChartTheme.ChartThemeBlueIcy
        if int(chartDefault['theme']) == 7:
            self.theme = QtCharts.QChart.ChartTheme.ChartThemeQt

        self.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        self.setContentsMargins(0,0,0,0)
        self.barChart = QtCharts.QChart()
        self.barChart.setBackgroundRoundness(0)
        self.barChart.setMargins(QtCore.QMargins(0,0,0,0))
        self.barChart.setTheme(self.theme)
        self.barChart.legend().setVisible(False)
        self.ncomp = 0
        self.setChart(self.barChart)

    def add_chart(self,weights,colors,type="bar"):
        if not hasattr(self,'axisX'):
            self.axisX = QtCharts.QBarCategoryAxis()
            for n in range(len(weights)):
                self.axisX.append("<span style=\"color: "+colors[n]+";\">{}</span>".format(n+1))
            self.axisY = QtCharts.QValueAxis()
            self.axisX.setTitleText("Components")
            self.axisY.setTitleText("Weight (%)")
            self.axisY.setRange(0,100)
            self.axisX.setLabelsFont(QtGui.QFont(self.fontname,self.fontsize,57))
            self.axisX.setTitleFont(QtGui.QFont(self.fontname,self.fontsize,57))
            self.axisY.setLabelsFont(QtGui.QFont(self.fontname,self.fontsize,57))
            self.axisY.setTitleFont(QtGui.QFont(self.fontname,self.fontsize,57))
            self.barChart.addAxis(self.axisX, QtCore.Qt.AlignmentFlag.AlignBottom)
            self.barChart.addAxis(self.axisY, QtCore.Qt.AlignmentFlag.AlignLeft)
        elif len(weights)!=self.ncomp:
            self.axisX.clear()
            for n in range(len(weights)):
                self.axisX.append("<span style=\"color: "+colors[n]+";\">{}</span>".format(n+1))
        self.ncomp = len(weights)
        self.barChart.removeAllSeries()
        series = QtCharts.QBarSeries()
        barset = QtCharts.QBarSet("Weight")
        for n in range(self.ncomp):
            barset.append(weights[n]*100)
        series.append(barset)
        self.barChart.addSeries(series)
        series.attachAxis(self.axisX)
        series.attachAxis(self.axisY)
        self.CHART_IS_PRESENT = True

    def refresh(self, config):
        chartDefault = dict(config['chartDefault'].items())
        if int(chartDefault['theme']) == 0:
            self.theme = QtCharts.QChart.ChartTheme.ChartThemeLight
        elif int(chartDefault['theme']) == 1:
            self.theme = QtCharts.QChart.ChartTheme.ChartThemeBlueCerulean
        elif int(chartDefault['theme']) == 2:
            self.theme = QtCharts.QChart.ChartTheme.ChartThemeDark
        elif int(chartDefault['theme']) == 3:
            self.theme = QtCharts.QChart.ChartTheme.ChartThemeBrownSand
        elif int(chartDefault['theme']) == 4:
            self.theme = QtCharts.QChart.ChartTheme.ChartThemeBlueNcs
        elif int(chartDefault['theme']) == 5:
            self.theme = QtCharts.QChart.ChartTheme.ChartThemeHighContrast
        elif int(chartDefault['theme']) == 6:
            self.theme = QtCharts.QChart.ChartTheme.ChartThemeBlueIcy
        elif int(chartDefault['theme']) == 7:
            self.theme = QtCharts.QChart.ChartTheme.ChartThemeQt
        else:
            self.raise_error("Wrong theme")
        self.barChart.setTheme(self.theme)

    def adjust_fonts(self,fontname,fontsize):
        self.set_fonts(fontname,fontsize)
        try:
            self.axisX.setLabelsFont(QtGui.QFont(fontname,fontsize,57))
            self.axisX.setTitleFont(QtGui.QFont(fontname,fontsize,57))
            self.axisY.setLabelsFont(QtGui.QFont(fontname,fontsize,57))
            self.axisY.setTitleFont(QtGui.QFont(fontname,fontsize,57))
        except:
            pass

    def set_fonts(self,fontname,fontsize):
        self.fontname = fontname
        self.fontsize = fontsize

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

