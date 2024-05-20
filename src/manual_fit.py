from my_widgets import VerticalLabelSlider
from process import Image, FitFunctions
from PyQt6 import QtCore, QtWidgets, QtGui, QtCharts
import configparser
import glob
import numpy as np
import os
import profile_chart
import my_widgets

class Window(QtCore.QObject):

    STATUS_REQUESTED = QtCore.pyqtSignal()
    FIT_SATISFIED = QtCore.pyqtSignal(list)
    COLOR = ['magenta','cyan','darkCyan','darkMagenta','red','darkRed','blue','darkBlue','darkGray','green','darkGreen','darkYellow','yellow','black']

    def __init__(self,fontname='Arial',fontsize=20,function='gaussian'):
        super(Window,self).__init__()
        self.config = configparser.ConfigParser()
        dirname = os.path.dirname(__file__)
        self.config.read(os.path.join(dirname,'configuration.ini'))
        self.fontname = fontname
        self.fontsize = fontsize
        self.image_worker = Image()
        self.fit_worker = FitFunctions()
        self.function = function

    def refresh(self,config):
        self.config = config
        try:
            self.fit_chart.refresh(config)
        except:
            pass

    def set_status(self,status):
        self.status = status

    def get_input(self):
        items = []
        for number in range(12):
            items.append(str(number+1))
            items.append(str(number+1)+'+BG')
        dialog = my_widgets.MultipleInputDialog()
        return dialog.getItems({'type':'ComboBox','label':'Choose the Number of Peaks','content':items},\
                               {'type':'ComboBox','label':'Choose the Fit Function','content':['gaussian','voigt',\
                                                                            'translational_antiphase_domain_model']},\
                               {'type':'ComboBox','label':'Choose Whether to Remove a Linear Background','content':['Yes','No']})

    def main(self,path,nop=1,BG=False, remove_linear_BG=False):
        if nop == 0:
            input = self.get_input()
            if input:
                text_nop = input['Choose the Number of Peaks']
                text_rmlBG = input['Choose Whether to Remove a Linear Background']
                self.function = input['Choose the Fit Function']
            else:
                return
            if text_nop.isdigit():
                self.nop = int(text_nop)
                self.BG = False
            else:
                self.nop = int(text_nop.split('+')[0])+1
                self.BG = True
            if text_rmlBG == 'Yes':
                self.remove_linear_BG = True
            elif text_rmlBG == 'No':
                self.remove_linear_BG = False
        else:
            self.nop = nop
            self.BG = BG
            self.remove_linear_BG = remove_linear_BG
        self.STATUS_REQUESTED.emit()
        if self.function == 'gaussian':
            self.fit_function = self.fit_worker.gaussian
            self.initialGuess = ['1','0.1','1','0.5']
        elif self.function == 'voigt':
            self.fit_function = self.fit_worker.voigt
            self.initialGuess = ['1','0.1','1','1','0.5']
        elif self.function == 'translational_antiphase_domain_model':
            self.fit_function = self.fit_worker.translational_antiphase_domain_model_intensity_using_S
            self.lattice_constant = 3.15
            self.initialGuess = ['3.15','0.1','1','0']
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
        self.parametersHLayout = QtWidgets.QHBoxLayout(self.parameters)
        self.windowDefault = dict(self.config['windowDefault'].items())
        self.RC, self.I = self.profile()
        if self.remove_linear_BG:
            background = np.linspace(self.I[0],self.I[-1],len(self.I))
            self.I = self.I - background
        self.maxIntensity = np.amax(self.I)
        self.maxIntensityPosition = np.argmax(self.I)
        self.minIntensity = np.amin(self.I)
        if self.function == 'translational_antiphase_domain_model':
            self.RC = self.RC - self.RC[self.maxIntensityPosition]
        for i in range(1,self.nop+1):
            parametersVLayout = QtWidgets.QVBoxLayout()
            if self.function == 'gaussian':
                mode = [('C',i,self.RC[-1]/self.nop*i,0,self.RC[-1]),('H',i,float(self.initialGuess[1]),0.01,0.5),\
                        ('W',i,float(self.initialGuess[2]),0.01,5)]
            elif self.function == 'voigt':
                mode = [('C',i,self.RC[-1]/self.nop*i,0,self.RC[-1]),('A',i,float(self.initialGuess[1]),0.01,0.5),\
                        ('FL',i,float(self.initialGuess[2]),0.01,5),('FG',i,float(self.initialGuess[3]),0.01,5)]
            elif self.function == 'translational_antiphase_domain_model':
                mode = [('G',i,float(self.initialGuess[1]),0.0001,1),('H',i,float(self.initialGuess[2]),0,5), \
                        ('O',i,float(self.initialGuess[3]),-5,5)]
            for name,index,value,minimum,maximum in mode:
                if self.function == 'gaussian':
                    if self.BG and i==self.nop:
                        if name == 'W':
                            slider = VerticalLabelSlider(minimum,2*self.RC[-1],100,value*5,name,index,self.BG,'vertical',self.COLOR[i-1])
                        elif name == 'H':
                            slider = VerticalLabelSlider(minimum,10,100,value*2,name,index,self.BG,'vertical',self.COLOR[i-1])
                        elif name =='C':
                            slider = VerticalLabelSlider(minimum,maximum,100,self.RC[-1]/2,name,index,self.BG,'vertical',self.COLOR[i-1])
                    else:
                        slider = VerticalLabelSlider(minimum,maximum,100,value,name,index,False,'vertical',self.COLOR[i-1])
                elif self.function == 'voigt':
                    if self.BG and i==self.nop:
                        if name == 'FL':
                            slider = VerticalLabelSlider(minimum,2*self.RC[-1],100,value,name,index,self.BG,'vertical',self.COLOR[i-1])
                        elif name == 'FG':
                            slider = VerticalLabelSlider(minimum,2*self.RC[-1],100,value,name,index,self.BG,'vertical',self.COLOR[i-1])
                        elif name == 'A':
                            slider = VerticalLabelSlider(minimum,10,100,value,name,index,self.BG,'vertical',self.COLOR[i-1])
                        elif name =='C':
                            slider = VerticalLabelSlider(minimum,maximum,100,self.RC[-1]/2,name,index,self.BG,'vertical',self.COLOR[i-1])
                    else:
                        slider = VerticalLabelSlider(minimum,maximum,100,value,name,index,False,'vertical',self.COLOR[i-1])

                elif self.function == 'translational_antiphase_domain_model':
                    if self.BG and i==self.nop:
                        if name == 'G':
                            name = 'C'
                            slider = VerticalLabelSlider(self.RC[0],self.RC[-1],100,0,name,index,self.BG,'vertical',self.COLOR[i-1])
                        elif name == 'H':
                            slider = VerticalLabelSlider(0,10,100,5,name,index,self.BG,'vertical',self.COLOR[i-1])
                        elif name =='O':
                            name = 'W'
                            slider = VerticalLabelSlider(0,self.RC[-1]-self.RC[0],100,(self.RC[-1]-self.RC[0])/2,name,index,self.BG,'vertical',self.COLOR[i-1])
                    else:
                        slider = VerticalLabelSlider(minimum,maximum,100,value,name,index,False,'vertical',self.COLOR[i-1])
                slider.VALUE_CHANGED.connect(self.update_guess)
                parametersVLayout.addWidget(slider)
            self.parametersHLayout.addLayout(parametersVLayout)
        if self.function == 'gaussian' or self.function == 'voigt':
            self.OffsetSlider = VerticalLabelSlider(-1,1,100,(self.I[0]+self.I[-1])/2,'O',0)
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
        desktopRect = self.Dialog.geometry()
        center = desktopRect.center()
        self.Dialog.move(int(center.x()-self.Dialog.width()*0.5),int(center.y()-self.Dialog.height()*0.5))

    def accept(self):
        self.reject()
        results = self.flatten(self.guess)
        if self.function == 'gaussian' or self.function == 'voigt':
            results.append(float(self.OffsetSlider.value()))
        self.FIT_SATISFIED.emit(results)

    def reject(self):
        self.Dialog.close()

    def flatten(self,input):
        new_list=[]
        if self.function == 'gaussian':
            i_list = [1,0,2]
        elif self.function == 'voigt':
            i_list = [0,1,2,3]
        for i in i_list:
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
        if self.function == 'gaussian' or self.function == 'voigt':
            total = np.full(len(x0),float(self.OffsetSlider.value()))
        elif self.function == 'translational_antiphase_domain_model':
            total = np.full(len(x0),float(0))
        total_min = 100
        for i in range(len(guess)):
            if self.function == 'gaussian':
                center = float(guess[i][0])
                height = float(guess[i][1])
                width = float(guess[i][2])
                offset = float(self.OffsetSlider.value())
                fit = self.fit_function(x0,height,center,width,offset)
                fit0 = self.fit_function(x0,height,center,width,0)
                total = np.add(total,fit0)
                maxH = self.fit_function(center,height,center,width,offset)
                minH1 = self.fit_function(x0[0],height,center,width,offset)
                minH2 = self.fit_function(x0[-1],height,center,width,offset)
            elif self.function == 'voigt':
                center = float(guess[i][0])
                amplitude = float(guess[i][1])
                width_L = float(guess[i][2])
                width_G = float(guess[i][3])
                offset = float(self.OffsetSlider.value())
                fit = self.fit_function(x0,center,amplitude,width_L,width_G,offset)
                fit0 = self.fit_function(x0,center,amplitude,width_L,width_G,0)
                total = np.add(total,fit0)
                maxH  = self.fit_function(center,center,amplitude,width_L, width_G,offset)
                minH1 = self.fit_function(x0[0], center,amplitude,width_L, width_G,offset)
                minH2 = self.fit_function(x0[-1],center,amplitude,width_L, width_G,offset)
            elif self.function == 'translational_antiphase_domain_model':
                if i == len(guess)-1:
                    center = float(guess[i][0])
                    height = float(guess[i][1])
                    width = float(guess[i][2])
                    offset = 0
                    fit = self.fit_worker.gaussian(x0,height,center,width,offset)
                    fit0 = self.fit_worker.gaussian(x0,height,center,width,0)
                    total = np.add(total,fit0)
                    maxH = self.fit_worker.gaussian(center,height,center,width,offset)
                    minH1 = self.fit_worker.gaussian(x0[0],height,center,width,offset)
                    minH2 = self.fit_worker.gaussian(x0[-1],height,center,width,offset)
                else:
                    center = float(guess[len(guess)-1][0])
                    height = float(guess[len(guess)-1][1])
                    width = float(guess[len(guess)-1][2])
                    fit0 = self.fit_worker.gaussian(x0,height,center,width,0)
                    fit0_normalized = fit0/np.amax(fit0)

                    gamma = float(guess[i][0])
                    height = float(guess[i][1])
                    offset = float(guess[i][2])
                    fit = self.fit_function(x0,self.lattice_constant,gamma,height,offset)*fit0_normalized
                    total = np.add(total,fit)
                    maxH = 1
                    minH1 = self.fit_function(x0[0],self.lattice_constant,gamma,height,offset)
                    minH2 = self.fit_function(x0[-1],self.lattice_constant,gamma,height,offset)
            if min(minH1,minH2) < total_min:
                total_min = min(minH1,minH2)
            pen = QtGui.QPen(QtCore.Qt.PenStyle.DotLine)
            pen.setColor(QtGui.QColor(self.COLOR[i]))
            pen.setWidth(2)
            self.series_fit = QtCharts.QLineSeries()
            self.series_fit.setPen(pen)
            for x,y in zip(x0,fit):
                self.series_fit.append(x,y)
            self.fit_chart.profileChart.addSeries(self.series_fit)
            for ax in self.fit_chart.profileChart.axes():
                self.series_fit.attachAxis(ax)
            self.fit_chart.profileChart.axes(QtCore.Qt.Orientation.Vertical)[0].setRange(min(minH1,minH2,self.minIntensity),max(maxH,self.maxIntensity))
        pen = QtGui.QPen(QtCore.Qt.PenStyle.DotLine)
        pen.setColor(QtGui.QColor('red'))
        pen.setWidth(2)
        series_total = QtCharts.QLineSeries()
        series_total.setPen(pen)
        for x,y in zip(x0,total):
            series_total.append(x,y)
        self.fit_chart.profileChart.addSeries(series_total)
        for ax in self.fit_chart.profileChart.axes():
            series_total.attachAxis(ax)
        self.fit_chart.profileChart.axes(QtCore.Qt.Orientation.Vertical)[0].setRange(min(total[0],total[-1],self.minIntensity,total_min),max(np.amax(total),self.maxIntensity))

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
