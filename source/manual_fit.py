from my_widgets import VerticalLabelSlider
from process import Image, Fit
from PyQt5 import QtCore, QtWidgets, QtGui, QtChart
import configparser
import glob
import numpy as np
import os
import profile_chart

class Window(QtCore.QObject):

    STATUS_REQUESTED = QtCore.pyqtSignal()
    FIT_SATISFIED = QtCore.pyqtSignal(list)
    COLOR = ['magenta','cyan','darkCyan','darkMagenta','darkRed','darkBlue','darkGray','green','darkGreen','darkYellow','yellow','black']

    def __init__(self,fontname='Arial',fontsize=10):
        super(Window,self).__init__()
        self.config = configparser.ConfigParser()
        self.config.read('./configuration.ini')
        self.fontname = fontname
        self.fontsize = fontsize
        self.image_worker = Image()
        self.fit_worker = Fit()

    def refresh(self,config):
        self.config = config
        try:
            self.fit_chart.refresh(config)
        except:
            pass

    def set_status(self,status):
        self.status = status

    def get_input(self):
        items = ['1','1+BG','3','3+BG','5','5+BG','7','7+BG','9','9+BG','11','11+BG']
        return QtWidgets.QInputDialog.getItem(None,'Input','Choose the Number of Peaks',items,0,False)

    def main(self,path,nop=1,BG=False):
        if nop == 0:
            text, OK = self.get_input()
            if OK:
                if text.isdigit():
                    self.nop = int(text)
                    self.BG = False
                else:
                    self.nop = int(text.split('+')[0])+1
                    self.BG = True
            else:
                return
        else:
            self.nop = nop
            self.BG = BG
        self.STATUS_REQUESTED.emit()
        self.initialGuess = ['1','0.1','1','0.5']
        if os.path.isdir(path):
            self.path = os.path.join(path,'*.nef')
        elif os.path.isfile(path):
            self.path = path
        else:
            self.raise_error('Please open a pattern!')
            return
        self.Dialog = QtWidgets.QWidget()
        self.Grid = QtWidgets.QGridLayout(self.Dialog)
        self.LeftFrame = QtWidgets.QFrame()
        self.RightFrame = QtWidgets.QFrame()
        self.LeftGrid = QtWidgets.QGridLayout(self.LeftFrame)
        self.RightGrid = QtWidgets.QGridLayout(self.RightFrame)
        self.parameters = QtWidgets.QGroupBox("Fitting Parameters")
        self.parameters.setStyleSheet('QGroupBox::title {color:blue;}')
        self.parametersHLayout = QtWidgets.QHBoxLayout(self.parameters)
        self.windowDefault = dict(self.config['windowDefault'].items())
        self.RC, self.I = self.profile()
        self.maxIntensity = np.amax(self.I)
        self.minIntensity = np.amin(self.I)
        for i in range(1,self.nop+1):
            parametersVLayout = QtWidgets.QVBoxLayout()
            mode = [('C',i,self.RC[-1]/self.nop*i,0,self.RC[-1]),('H',i,float(self.initialGuess[1]),0.01,0.5),\
                    ('W',i,float(self.initialGuess[2]),0.01,5)]
            for name,index,value,minimum,maximum in mode:
                if self.BG and i==self.nop:
                    if name == 'W':
                        slider = VerticalLabelSlider(minimum,self.RC[-1],100,value,name,index,self.BG,'vertical',self.COLOR[i-1])
                    elif name == 'H':
                        slider = VerticalLabelSlider(minimum,5,100,value,name,index,self.BG,'vertical',self.COLOR[i-1])
                    elif name =='C':
                        slider = VerticalLabelSlider(minimum,maximum,100,self.RC[-1]/2,name,index,self.BG,'vertical',self.COLOR[i-1])
                else:
                    slider = VerticalLabelSlider(minimum,maximum,100,value,name,index,False,'vertical',self.COLOR[i-1])
                slider.VALUE_CHANGED.connect(self.update_guess)
                parametersVLayout.addWidget(slider)
            self.parametersHLayout.addLayout(parametersVLayout)
        self.OffsetSlider = VerticalLabelSlider(0,1,100,(self.I[0]+self.I[-1])/2,'O',0)
        self.OffsetSlider.VALUE_CHANGED.connect(self.update_guess)
        self.parametersHLayout.addWidget(self.OffsetSlider)

        self.AcceptButton = QtWidgets.QPushButton("Accept")
        self.AcceptButton.clicked.connect(self.accept)
        self.FitChartTitle = QtWidgets.QLabel('Profile')
        self.fit_chart = profile_chart.ProfileChart(self.config)
        self.fit_chart.set_fonts(self.fontname,self.fontsize)
        self.fit_chart.add_chart(self.RC,self.I)
        self.fit_chart.profileChart.setMinimumWidth(650)
        self.update_guess()

        self.LeftGrid.addWidget(self.parameters,0,0)
        self.LeftGrid.addWidget(self.AcceptButton,1,0)
        self.RightGrid.addWidget(self.FitChartTitle,0,0)
        self.RightGrid.addWidget(self.fit_chart,1,0)
        self.Grid.addWidget(self.LeftFrame,0,0)
        self.Grid.addWidget(self.RightFrame,0,1)

        self.Dialog.setWindowTitle("Manual Fit")
        self.Dialog.setMinimumHeight(600)
        self.Dialog.showNormal()
        desktopRect = QtWidgets.QApplication.desktop().availableGeometry(self.Dialog)
        center = desktopRect.center()
        self.Dialog.move(center.x()-self.Dialog.width()*0.5,center.y()-self.Dialog.height()*0.5)

    def accept(self):
        self.reject()
        results = self.flatten(self.guess)
        results.append(float(self.OffsetSlider.value()))
        self.FIT_SATISFIED.emit(results)

    def reject(self):
        self.Dialog.close()

    def flatten(self,input):
        new_list=[]
        for i in [1,0,2]:
            for j in range(len(input)):
                new_list.append(float(input[j][i]))
        return new_list

    def update_guess(self):
        guess = []
        for VLayout in self.parametersHLayout.children():
            row = []
            for i in range(VLayout.count()):
                row.append(VLayout.itemAt(i).widget().value())
            guess.append(row)
        self.guess = guess
        self.plot_results(self.RC,self.guess)

    def profile(self):
        image_list = []
        autoWB = self.status["autoWB"]
        brightness = self.status["brightness"]
        blackLevel = self.status["blackLevel"]
        VS = int(self.windowDefault["vs"])
        HS = int(self.windowDefault["hs"])
        image_crop = [1200+VS,2650+VS,500+HS,3100+HS]
        scale_factor = self.status["sensitivity"]/np.sqrt(self.status["energy"])
        for filename in glob.glob(self.path):
            image_list.append(filename)
        if self.status["startX"] == "" or self.status["startY"] == "" or self.status["endX"] == "" or \
                self.status["endY"] == ""\
            or self.status["width"] =="":
            self.raise_error("Please choose the region!")
        else:
            start = QtCore.QPointF()
            end = QtCore.QPointF()
            start.setX(self.status["startX"])
            start.setY(self.status["startY"])
            end.setX(self.status["endX"])
            end.setY(self.status["endY"])
            width = self.status["width"]*scale_factor
            qImg, img = self.image_worker.get_image(16,image_list[0],autoWB,brightness,blackLevel,image_crop)
            if width == 0.0:
                RC,I = self.image_worker.get_line_scan(start,end,img,scale_factor)
            else:
                RC,I = self.image_worker.get_integral(start,end,width,img,scale_factor)
            return RC,I

    def plot_results(self,x0,guess):
        if len(self.fit_chart.profileChart.series())>1:
            for series in self.fit_chart.profileChart.series()[1:]:
                self.fit_chart.profileChart.removeSeries(series)
        total = np.full(len(x0),float(self.OffsetSlider.value()))
        total_min = 100
        for i in range(len(guess)):
            center = float(guess[i][0])
            height = float(guess[i][1])
            width = float(guess[i][2])
            offset = float(self.OffsetSlider.value())
            fit = self.fit_worker.gaussian(x0,height,center,width,offset)
            fit0 = self.fit_worker.gaussian(x0,height,center,width,0)
            total = np.add(total,fit0)
            maxH = self.fit_worker.gaussian(center,height,center,width,offset)
            minH1 = self.fit_worker.gaussian(x0[0],height,center,width,offset)
            minH2 = self.fit_worker.gaussian(x0[-1],height,center,width,offset)
            if min(minH1,minH2) < total_min:
                total_min = min(minH1,minH2)
            pen = QtGui.QPen(QtCore.Qt.DotLine)
            pen.setColor(QtGui.QColor(self.COLOR[i]))
            pen.setWidth(2)
            self.series_fit = QtChart.QLineSeries()
            self.series_fit.setPen(pen)
            for x,y in zip(x0,fit):
                self.series_fit.append(x,y)
            self.fit_chart.profileChart.addSeries(self.series_fit)
            for ax in self.fit_chart.profileChart.axes():
                self.series_fit.attachAxis(ax)
            self.fit_chart.profileChart.axisY().setRange(min(minH1,minH2,self.minIntensity),max(maxH,self.maxIntensity))
        pen = QtGui.QPen(QtCore.Qt.DotLine)
        pen.setColor(QtGui.QColor('red'))
        pen.setWidth(2)
        series_total = QtChart.QLineSeries()
        series_total.setPen(pen)
        for x,y in zip(x0,total):
            series_total.append(x,y)
        self.fit_chart.profileChart.addSeries(series_total)
        for ax in self.fit_chart.profileChart.axes():
            series_total.attachAxis(ax)
        self.fit_chart.profileChart.axisY().setRange(min(total[0],total[-1],self.minIntensity,total_min),max(np.amax(total),self.maxIntensity))

    def raise_error(self,message):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.setEscapeButton(QtWidgets.QMessageBox.Close)
        msg.exec()

    def raise_attention(self,information):
        info = QtWidgets.QMessageBox()
        info.setIcon(QtWidgets.QMessageBox.Information)
        info.setText(information)
        info.setWindowTitle("Information")
        info.setStandardButtons(QtWidgets.QMessageBox.Ok)
        info.setEscapeButton(QtWidgets.QMessageBox.Close)
        info.exec()
