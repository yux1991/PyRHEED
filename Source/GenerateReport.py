from PyQt5 import QtCore, QtWidgets, QtGui, QtChart
import numpy as np
import os
import configparser
import matplotlib.pyplot as plt
import PlotChart
from MyWidgets import *

class Window(QtCore.QObject):

    StatusRequested = QtCore.pyqtSignal()
    PolarIRequested = QtCore.pyqtSignal()
    PolarFRequested = QtCore.pyqtSignal()
    RefreshPolarI = QtCore.pyqtSignal(np.ndarray,np.ndarray,str,str,int,str,bool,dict)
    RefreshPolarF = QtCore.pyqtSignal(np.ndarray,np.ndarray,str,str,int,str,bool,dict)
    NormalIRequested = QtCore.pyqtSignal()
    NormalFRequested = QtCore.pyqtSignal()
    RefreshNormalI = QtCore.pyqtSignal(np.ndarray,np.ndarray,str,str,int,str,bool,dict)
    RefreshNormalF = QtCore.pyqtSignal(np.ndarray,np.ndarray,str,str,int,str,bool,dict)
    fontsChanged = QtCore.pyqtSignal(str,int)

    def __init__(self):
        super(Window,self).__init__()
        self.config = configparser.ConfigParser()
        self.config.read('./configuration.ini')

    def Set_Status(self,status):
        self.status = status

    def Main(self,path,preload=False):
        self.StatusRequested.emit()
        self.path = path
        self.KPmin = 0
        self.KPmax = 100
        self.currentKP = 0
        self.RangeStart = 0
        self.AzimuthStart = 0
        self.KperpSliderScale = 1
        self.AZmin = 0
        self.AZmax = 100
        self.currentAzimuth = 0
        self.Imin = 0
        self.Imax = 2
        self.currentImin = 0
        self.currentImax = 1
        self.Fmin = 0
        self.Fmax = 2
        self.currentFmin = 0
        self.currentFmax = 1
        self.IAIsPresent = False
        self.FAIsPresent = False
        self.IKIsPresent = True
        self.FKIsPresent = True
        self.Dialog = QtWidgets.QWidget()
        self.Grid = QtWidgets.QGridLayout(self.Dialog)
        self.LeftFrame = QtWidgets.QFrame()
        self.LeftGrid = QtWidgets.QGridLayout(self.LeftFrame)

        self.chooseSource = QtWidgets.QGroupBox("Choose the Report File")
        self.chooseSource.setStyleSheet('QGroupBox::title {color:blue;}')
        self.chooseSource.setMinimumWidth(300)
        self.sourceGrid = QtWidgets.QGridLayout(self.chooseSource)
        self.sourceGrid.setAlignment(QtCore.Qt.AlignTop)
        self.chooseSourceLabel = QtWidgets.QLabel("The path of the report file is:\n"+self.path)
        self.chooseSourceLabel.setWordWrap(True)
        self.chooseSourceButton = QtWidgets.QPushButton("Browse...")
        self.chooseSourceButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
        self.chooseSourceButton.clicked.connect(self.Choose_Source)
        self.sourceGrid.addWidget(self.chooseSourceLabel,0,0)
        self.sourceGrid.addWidget(self.chooseSourceButton,0,1)

        self.ReportInformationBox = QtWidgets.QGroupBox("Information")
        self.ReportInformationBox.setStyleSheet('QGroupBox::title {color:blue;}')
        self.ReportInformationGrid = QtWidgets.QGridLayout(self.ReportInformationBox)
        self.ReportInformationGrid.setAlignment(QtCore.Qt.AlignTop)
        self.ReportInformation = QtWidgets.QLabel("Number of peaks:\nDate of the report:\nStart image index:\nEnd image index:\nStart Kperp position:\nEnd Kperp position:\nKperp step size:")
        self.ReportInformationGrid.addWidget(self.ReportInformation)

        self.typeOfReportBox = QtWidgets.QGroupBox("Type of the Report to Be Generated")
        self.typeOfReportBox.setStyleSheet('QGroupBox::title {color:blue;}')
        self.typeOfReportGrid = QtWidgets.QGridLayout(self.typeOfReportBox)
        self.typeOfReportGrid.setAlignment(QtCore.Qt.AlignTop)
        self.type = QtWidgets.QButtonGroup()
        self.type.setExclusive(False)
        self.typeFrame = QtWidgets.QFrame()
        self.typeGrid = QtWidgets.QGridLayout(self.typeFrame)
        self.IA = QtWidgets.QCheckBox("Intensity vs Azimuth")
        self.IAColor = ColorPicker("IA",'red',False)
        self.FA = QtWidgets.QCheckBox("HWHM vs Azimuth")
        self.FAColor = ColorPicker("FA",'red',False)
        self.IK = QtWidgets.QCheckBox("Intensity vs Kperp")
        self.IKColor = ColorPicker("IK",'red',False)
        self.FK = QtWidgets.QCheckBox("HWHM vs Kperp")
        self.FKColor = ColorPicker("FK",'red',False)
        self.typeGrid.addWidget(self.FA,0,0)
        self.typeGrid.addWidget(self.FAColor,0,1)
        self.typeGrid.addWidget(self.IA,1,0)
        self.typeGrid.addWidget(self.IAColor,1,1)
        self.typeGrid.addWidget(self.FK,2,0)
        self.typeGrid.addWidget(self.FKColor,2,1)
        self.typeGrid.addWidget(self.IK,3,0)
        self.typeGrid.addWidget(self.IKColor,3,1)
        self.type.addButton(self.IA)
        self.type.addButton(self.FA)
        self.type.addButton(self.IK)
        self.type.addButton(self.FK)
        self.typeOfReportGrid.addWidget(self.typeFrame,0,0)

        self.optionBox = QtWidgets.QGroupBox("Plot Options")
        self.optionBox.setStyleSheet('QGroupBox::title {color:blue;}')
        self.optionGrid = QtWidgets.QGridLayout(self.optionBox)
        self.optionGrid.setAlignment(QtCore.Qt.AlignTop)
        self.peakLabel = QtWidgets.QLabel("Choose the peak to be analyzed:")
        self.peak = QtWidgets.QComboBox()
        self.peak.addItem('Center','0')
        self.figureGeneratorLabel = QtWidgets.QLabel("Choose the type of figure generator:")
        self.figureGenerator = QtWidgets.QComboBox()
        self.figureGenerator.addItem('Qt','Qt')
        self.figureGenerator.addItem('Matplotlib','Matplotlib')
        self.figureGenerator.currentTextChanged.connect(self.connectOKButton)
        self.KperpLabel = QtWidgets.QLabel("Kperp = {:6.2f} (\u212B\u207B\u00B9)".format(self.currentKP/self.KperpSliderScale+self.RangeStart))
        self.KperpSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.KperpSlider.setMinimum(self.KPmin)
        self.KperpSlider.setMaximum(self.KPmax)
        self.KperpSlider.setValue(self.currentKP)
        self.KperpSlider.valueChanged.connect(self.KPChanged)
        self.KperpSlider.setEnabled(False)
        self.AzimuthLabel = QtWidgets.QLabel("Azimuth Angle = {:5.1f} (\u00B0)".format(self.currentAzimuth))
        self.AzimuthSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.AzimuthSlider.setMinimum(self.AZmin)
        self.AzimuthSlider.setMaximum(self.AZmax)
        self.AzimuthSlider.setValue(0)
        self.AzimuthSlider.valueChanged.connect(self.AzimuthChanged)
        self.AzimuthSlider.setEnabled(False)

        self.intensityRangeSlider = DoubleSlider(minimum=0,maximum=200,scale=0.01,head=0,tail=1,text="Intensity",unit='arb. units')
        self.intensityRangeSlider.setEnabled(False)
        self.intensityRangeSlider.valueChanged.connect(self.RefreshPlots)
        self.HWHMRangeSlider = DoubleSlider(minimum=0,maximum=200,scale=0.01,head=0,tail=1,text="HWHM",unit='\u212B\u207B\u00B9')
        self.HWHMRangeSlider.setEnabled(False)
        self.HWHMRangeSlider.valueChanged.connect(self.RefreshPlots)

        self.optionGrid.addWidget(self.peakLabel,0,0)
        self.optionGrid.addWidget(self.peak,0,1)
        self.optionGrid.addWidget(self.figureGeneratorLabel,1,0)
        self.optionGrid.addWidget(self.figureGenerator,1,1)
        self.optionGrid.addWidget(self.KperpLabel,2,0,1,2)
        self.optionGrid.addWidget(self.KperpSlider,3,0,1,2)
        self.optionGrid.addWidget(self.AzimuthLabel,4,0,1,2)
        self.optionGrid.addWidget(self.AzimuthSlider,5,0,1,2)
        self.optionGrid.addWidget(self.intensityRangeSlider,6,0,1,2)
        self.optionGrid.addWidget(self.HWHMRangeSlider,7,0,1,2)

        self.appearance = QtWidgets.QGroupBox("Appearance")
        self.appearance.setMaximumHeight(100)
        self.appearance.setStyleSheet('QGroupBox::title {color:blue;}')
        self.appearanceGrid = QtWidgets.QGridLayout(self.appearance)
        self.appearanceGrid.setAlignment(QtCore.Qt.AlignTop)
        self.fontListLabel = QtWidgets.QLabel("Change Font")
        self.fontList = QtWidgets.QFontComboBox()
        self.fontList.setCurrentFont(QtGui.QFont("Arial"))
        self.fontList.currentFontChanged.connect(self.RefreshFontName)
        self.fontSizeLabel = QtWidgets.QLabel("Adjust Font Size ({})".format(15))
        self.fontSizeLabel.setFixedWidth(160)
        self.fontSizeSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.fontSizeSlider.setMinimum(1)
        self.fontSizeSlider.setMaximum(100)
        self.fontSizeSlider.setValue(15)
        self.fontSizeSlider.valueChanged.connect(self.RefreshFontSize)
        self.appearanceGrid.addWidget(self.fontListLabel,0,0)
        self.appearanceGrid.addWidget(self.fontList,0,1)
        self.appearanceGrid.addWidget(self.fontSizeLabel,1,0)
        self.appearanceGrid.addWidget(self.fontSizeSlider,1,1)

        self.statusBar = QtWidgets.QGroupBox("Log")
        self.statusBar.setStyleSheet('QGroupBox::title {color:blue;}')
        self.statusGrid = QtWidgets.QGridLayout(self.statusBar)
        self.statusBar.setMaximumHeight(120)
        self.statusBar.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Fixed)
        self.logBox = QtWidgets.QTextEdit(QtCore.QTime.currentTime().toString("hh:mm:ss")+\
                                    "\u00A0\u00A0\u00A0\u00A0Initialized!")
        self.logBox.ensureCursorVisible()
        self.logBox.setAlignment(QtCore.Qt.AlignTop)
        self.logBox.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.logBoxScroll = QtWidgets.QScrollArea()
        self.logBoxScroll.setWidget(self.logBox)
        self.logBoxScroll.setWidgetResizable(True)
        self.logBoxScroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.statusGrid.addWidget(self.logBoxScroll,0,0)

        self.ButtonBox = QtWidgets.QDialogButtonBox()
        self.ButtonBox.addButton("OK",QtWidgets.QDialogButtonBox.AcceptRole)
        self.ButtonBox.addButton("Cancel",QtWidgets.QDialogButtonBox.DestructiveRole)
        self.ButtonBox.setCenterButtons(True)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[1].clicked.\
            connect(self.Reject)

        self.LeftGrid.addWidget(self.chooseSource,0,0,1,2)
        self.LeftGrid.addWidget(self.ReportInformationBox,1,0)
        self.LeftGrid.addWidget(self.typeOfReportBox,1,1)
        self.LeftGrid.addWidget(self.optionBox,3,0,1,2)
        self.LeftGrid.addWidget(self.appearance,4,0,1,2)
        self.LeftGrid.addWidget(self.statusBar,5,0,1,2)
        self.LeftGrid.addWidget(self.ButtonBox,6,0,1,2)
        self.Grid.addWidget(self.LeftFrame,0,0)

        self.IA.stateChanged.connect(self.IACheckChanged)
        self.FA.stateChanged.connect(self.FACheckChanged)
        self.IK.stateChanged.connect(self.IKCheckChanged)
        self.FK.stateChanged.connect(self.FKCheckChanged)
        self.IA.setChecked(True)

        self.connectOKButton(self.figureGenerator.currentText())
        if preload:
            self.loadReport(self.path)

        self.Dialog.setWindowTitle("Generate Report")
        self.Dialog.show()
        desktopRect = QtWidgets.QApplication.desktop().availableGeometry(self.Dialog)
        center = desktopRect.center()
        self.Dialog.move(center.x()-self.Dialog.width()*0.5,center.y()-self.Dialog.height()*0.5)

    def RefreshFontSize(self):
        self.fontSizeLabel.setText("Adjust Font Size ({})".format(self.fontSizeSlider.value()))
        self.fontsChanged.emit(self.fontList.currentFont().family(),self.fontSizeSlider.value())

    def RefreshFontName(self):
        self.fontsChanged.emit(self.fontList.currentFont().family(),self.fontSizeSlider.value())

    def connectOKButton(self,text):
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[0].disconnect()
        if text == 'Qt':
            self.ButtonBox.findChildren(QtWidgets.QPushButton)[0].clicked. \
                connect(self.PolarStart)
        elif text == 'Matplotlib':
            self.ButtonBox.findChildren(QtWidgets.QPushButton)[0].clicked. \
                connect(self.Start)

    def updateLog(self,msg):
        self.logBox.append(QtCore.QTime.currentTime().toString("hh:mm:ss")+"\u00A0\u00A0\u00A0\u00A0"+msg)

    def Reject(self):
        self.Dialog.close()

    def Choose_Source(self):
        path = QtWidgets.QFileDialog.getOpenFileName(None,"Choose The Report File",self.path)
        self.path = path[0]
        self.pathExtension = os.path.splitext(self.path)[1]
        if not self.path=="":
            if not self.pathExtension == ".txt":
                self.Raise_Error('[Error: wrong file type] Please choose a *.txt file')
                self.updateLog('[Error: wrong file type] Please choose a *.txt file')
            else:
                self.chooseSourceLabel.setText("The path of the report is:\n"+self.path)
                self.loadReport(self.path)
        else:
            self.Raise_Error('[Error: No file] Please choose a *.txt file')
            self.updateLog('[Error: No file] Please choose a *.txt file')


    def Start(self):
        Kp = self.currentKP/self.KperpSliderScale+self.RangeStart
        Az = self.currentAzimuth*1.8+self.AzimuthStart
        if self.IK.checkState() == 2 and self.FK.checkState() == 2:
            I, K1, Ierror = self.getIK()
            F, K2, Ferror = self.getFK()
            self.PlotIFK(I,F,K1,Az)
        elif self.IK.checkState() == 2:
            I, K, Ierror = self.getIK()
            self.PlotIK(I,K,Az)
        elif self.FK.checkState() == 2:
            F, K, Ferror = self.getFK()
            self.PlotFK(F,K,Az)
        if self.IA.checkState() == 2:
            I, A, Ierror = self.getIA()
            self.PlotIA(I,A,Kp,self.intensityRangeSlider.values()[0],self.intensityRangeSlider.values()[1])
        if self.FA.checkState() == 2:
            F, A, Ferror = self.getFA()
            self.PlotFA(F,A,Kp,self.HWHMRangeSlider.values()[0],self.HWHMRangeSlider.values()[1])
        plt.show()

    def PolarStart(self):
        Kp = self.currentKP/self.KperpSliderScale+self.RangeStart
        Az = self.currentAzimuth*1.8+self.AzimuthStart
        theme = int(dict(self.config['chartDefault'].items())['theme'])
        self.IAPlot = PlotChart.PlotChart(theme,'Polar')
        self.FAPlot = PlotChart.PlotChart(theme,'Polar')
        self.IKPlot = PlotChart.PlotChart(theme,'Normal')
        self.FKPlot = PlotChart.PlotChart(theme,'Normal')
        self.PolarIRequested.connect(self.IAPlot.Main)
        self.PolarFRequested.connect(self.FAPlot.Main)
        self.NormalIRequested.connect(self.IKPlot.Main)
        self.NormalFRequested.connect(self.FKPlot.Main)
        self.RefreshPolarI.connect(self.IAPlot.addChart)
        self.RefreshPolarF.connect(self.FAPlot.addChart)
        self.RefreshNormalI.connect(self.IKPlot.addChart)
        self.RefreshNormalF.connect(self.FKPlot.addChart)
        self.fontsChanged.connect(self.IAPlot.adjustFonts)
        self.fontsChanged.connect(self.FAPlot.adjustFonts)
        self.fontsChanged.connect(self.FKPlot.adjustFonts)
        self.fontsChanged.connect(self.IKPlot.adjustFonts)
        self.IAColor.colorChanged.connect(self.IAPlot.adjustColor)
        self.FAColor.colorChanged.connect(self.FAPlot.adjustColor)
        self.IKColor.colorChanged.connect(self.IKPlot.adjustColor)
        self.FKColor.colorChanged.connect(self.FKPlot.adjustColor)
        self.Window = QtWidgets.QWidget()
        self.Window.setWindowTitle('Summary of Broadening Analysis')
        self.WindowLayout = QtWidgets.QGridLayout(self.Window)
        self.WindowLayout.addWidget(self.IAPlot,0,1)
        self.WindowLayout.addWidget(self.FAPlot,0,0)
        self.WindowLayout.addWidget(self.IKPlot,1,1)
        self.WindowLayout.addWidget(self.FKPlot,1,0)
        self.Window.setWindowModality(QtCore.Qt.WindowModal)
        self.Window.setMinimumSize(1000,800)
        self.Window.show()
        if self.IA.checkState() == 2:
            I, A, Ierror = self.getIA()
            self.PolarIRequested.emit()
            self.IAIsPresent = True
            self.RefreshPolarI.emit(I,A,'IA',self.fontList.currentFont().family(),self.fontSizeSlider.value(),\
                                    self.IAColor.getColor(),False,\
                                    {'Kp':Kp,'low':self.intensityRangeSlider.values()[0],\
                                     'high':self.intensityRangeSlider.values()[1]})
        if self.IK.checkState() == 2:
            I,K,Ierror = self.getIK()
            self.NormalIRequested.emit()
            self.IKIsPresent = True
            self.RefreshNormalI.emit(K,I,'IK',self.fontList.currentFont().family(),self.fontSizeSlider.value(), \
                                     self.IKColor.getColor(),True,\
                                     {'Az':Az})
        if self.FA.checkState() == 2:
            F, A, Ferror = self.getFA()
            self.PolarFRequested.emit()
            self.FAIsPresent = True
            self.RefreshPolarF.emit(F,A,'FA',self.fontList.currentFont().family(),self.fontSizeSlider.value(), \
                                    self.FAColor.getColor(),False,\
                                    {'Kp':Kp,'low':self.HWHMRangeSlider.values()[0],\
                                                'high':self.HWHMRangeSlider.values()[1]})
        if self.FK.checkState() == 2:
            F,K,Ferror = self.getFK()
            self.NormalFRequested.emit()
            self.FKIsPresent = True
            self.RefreshNormalF.emit(K,F,'FK',self.fontList.currentFont().family(),self.fontSizeSlider.value(), \
                                     self.FKColor.getColor(),True,\
                                     {'Az':Az})

    def PlotIA(self,I,A,Kp,imin,imax):
        A2 = A + np.full(len(A),180)
        Phi = np.append(A,A2)
        Heights = np.append(I,I)/np.amax(I)
        fig = plt.figure()
        ax = plt.subplot(projection='polar')
        ax.set_title('Intensity vs Azimuth at Kperp = {:5.2f} (\u212B\u207B\u00B9)'.format(Kp),fontsize=self.fontSizeSlider.value())
        ax.plot(Phi*np.pi/180,Heights,color=self.IAColor.getColor())
        ax.set_rmin(imin)
        ax.set_rmax(imax)
        ax.set_rlabel_position(0)
        ax.set_theta_direction(-1)
        ax.set_theta_zero_location('N')
        ax.set_thetagrids((0,30,60,90,120,150,180,210,240,270,300,330))
        ax.set_rticks(np.around(np.linspace(imin,imax,5),1))
        ax.tick_params(which='both', labelsize=self.fontSizeSlider.value())

    def PlotIK(self,I,K,Az):
        fig = plt.figure()
        ax = plt.subplot()
        ax.set_title('Intensity vs Kperp at Phi = {:5.2f}\u00B0'.format(Az),fontsize=self.fontSizeSlider.value())
        ax.plot(I,K,c=self.IKColor.getColor())
        ax.set_xlabel('Intensity (arb. units)',fontsize = self.fontSizeSlider.value())
        ax.set_ylabel(r'$K_{perp}$ $(\AA^{-1})$',fontsize = self.fontSizeSlider.value())
        ax.tick_params(which='both', labelsize=self.fontSizeSlider.value())

    def PlotFA(self,F,A,Kp,fmin,fmax):
        A2 = A + np.full(len(A),180)
        Phi = np.append(A,A2)
        HWHMs = np.append(F,F)
        fig = plt.figure()
        ax = plt.subplot(projection='polar')
        ax.set_title('HWHM vs Azimuth at Kperp = {:5.2f} (\u212B\u207B\u00B9)'.format(Kp),fontsize=self.fontSizeSlider.value())
        ax.plot(Phi*np.pi/180,HWHMs,color=self.FAColor.getColor())
        ax.set_rmin(fmin)
        ax.set_rmax(fmax)
        ax.set_rlabel_position(0)
        ax.set_theta_direction(-1)
        ax.set_theta_zero_location('N')
        ax.set_thetagrids((0,30,60,90,120,150,180,210,240,270,300,330))
        ax.set_rticks(np.around(np.linspace(fmin,fmax,5),1))
        ax.tick_params(which='both', labelsize=self.fontSizeSlider.value())

    def PlotFK(self,F,K,Az):
        fig = plt.figure()
        ax = plt.subplot()
        ax.set_title('HWHM vs Kperp at Phi = {:5.2f}\u00B0'.format(Az),fontsize=self.fontSizeSlider.value())
        ax.plot(F,K,c=self.FKColor.getColor())
        ax.set_xlabel(r'HWHM $(\AA^{-1})$',fontsize = self.fontSizeSlider.value())
        ax.set_ylabel(r'$K_{perp}$ $(\AA^{-1})$',fontsize = self.fontSizeSlider.value())
        ax.tick_params(which='both', labelsize=self.fontSizeSlider.value())

    def PlotIFK(self,I,F,K,Az):
        fig, ax1 = plt.subplots()
        fig.suptitle('Intensity and HWHM vs Kperp at Phi = {:5.2f}\u00B0'.format(Az),fontsize=self.fontSizeSlider.value())
        ax1.set_xlabel('Intensity (arb. units)',fontsize = self.fontSizeSlider.value(),color=self.IKColor.getColor())
        ax1.set_ylabel(r'$K_{perp}$ $(\AA^{-1})$',fontsize = self.fontSizeSlider.value())
        ax1.plot(I,K,c=self.IKColor.getColor())
        ax1.tick_params(axis='x',labelcolor='b')
        ax1.tick_params(axis='both',labelsize=self.fontSizeSlider.value())
        ax2 = ax1.twiny()
        ax2.set_xlabel(r'HWHM $(\AA^{-1})$',fontsize = self.fontSizeSlider.value(),color=self.FKColor.getColor())
        ax2.plot(F,K,c=self.FKColor.getColor())
        ax2.tick_params(axis='x',labelcolor='r')
        ax2.tick_params(axis='both',labelsize=self.fontSizeSlider.value())
        fig.tight_layout()

    def RefreshPlots(self):
        Kp = self.currentKP/self.KperpSliderScale+self.RangeStart
        Az = self.currentAzimuth*1.8+self.AzimuthStart
        if self.IAIsPresent:
            I, A, Ierror = self.getIA()
            self.RefreshPolarI.emit(I,A,'IA',self.fontList.currentFont().family(),self.fontSizeSlider.value(),\
                                    self.IAColor.getColor(),False,\
                                    {'Kp':Kp,'low':self.intensityRangeSlider.values()[0], \
                                                     'high':self.intensityRangeSlider.values()[1]})
        if self.FAIsPresent:
            F, A, Ferror = self.getFA()
            self.RefreshPolarF.emit(F,A,'FA',self.fontList.currentFont().family(),self.fontSizeSlider.value(), \
                                    self.FAColor.getColor(),False,\
                                    {'Kp':Kp,'low':self.HWHMRangeSlider.values()[0], \
                                                'high':self.HWHMRangeSlider.values()[1]})
        if self.IKIsPresent:
            I,K,Ierror = self.getIK()
            self.RefreshNormalI.emit(K,I,'IK',self.fontList.currentFont().family(),self.fontSizeSlider.value(), \
                                     self.IKColor.getColor(),True,\
                                     {'Az':Az})
        if self.FKIsPresent:
            F,K,Ferror = self.getFK()
            self.RefreshNormalF.emit(K,F,'FK',self.fontList.currentFont().family(),self.fontSizeSlider.value(), \
                                     self.FKColor.getColor(),True,\
                                     {'Az':Az})

    def getIA(self):
        peakIndex = np.round(float(self.peak.currentData()),0)
        columnI = int(1+peakIndex*2+1)
        columnIerror = int(1+peakIndex*2+2)
        rows = np.full(self.AZmax+1, self.currentKP).astype(int) + np.linspace(0,self.AZmax,self.AZmax+1).astype(int)*(self.KPmax+1)
        A = self.Angles
        I = np.fromiter((self.report[i,columnI] for i in rows.tolist()),float)
        Ierror = np.fromiter((self.report[i,columnIerror] for i in rows.tolist()),float)
        return I,A,Ierror

    def getFA(self):
        if self.BGCheck:
            nop = self.NumberOfPeaks+1
        else:
            nop = self.NumberOfPeaks
        peakIndex = np.round(float(self.peak.currentData()),0)
        columnF = int(1+nop*4+peakIndex*2+1)
        columnFerror = int(1+nop*4+peakIndex*2+2)
        rows = np.full(self.AZmax+1, self.currentKP).astype(int) + np.linspace(0,self.AZmax,self.AZmax+1).astype(int)*(self.KPmax+1)
        A = self.Angles
        F = np.fromiter((self.report[i,columnF]/2 for i in rows.tolist()),float)
        Ferror = np.fromiter((self.report[i,columnFerror]/2 for i in rows.tolist()),float)
        return F,A,Ferror

    def getIK(self):
        if self.BGCheck:
            nop = self.NumberOfPeaks+1
        else:
            nop = self.NumberOfPeaks
        peakIndex = np.round(float(self.peak.currentData()),0)
        columnI = int(1+peakIndex*2+1)
        columnIerror = int(1+peakIndex*2+2)
        rows = np.full(self.KPmax+1, self.currentAzimuth*(self.KPmax+1)).astype(int) + np.linspace(0,self.KPmax,self.KPmax+1).astype(int)
        K = self.Kperps
        I = np.fromiter((self.report[i,columnI] for i in rows.tolist()),float)
        Ierror = np.fromiter((self.report[i,columnIerror] for i in rows.tolist()),float)
        return I,K,Ierror

    def getFK(self):
        if self.BGCheck:
            nop = self.NumberOfPeaks+1
        else:
            nop = self.NumberOfPeaks
        peakIndex = np.round(float(self.peak.currentData()),0)
        columnF = int(1+nop*4+peakIndex*2+1)
        columnFerror = int(1+nop*4+peakIndex*2+2)
        rows = np.full(self.KPmax+1, self.currentAzimuth*(self.KPmax+1)).astype(int) + np.linspace(0,self.KPmax,self.KPmax+1).astype(int)
        K = self.Kperps
        F = np.fromiter((self.report[i,columnF]/2 for i in rows.tolist()),float)
        Ferror = np.fromiter((self.report[i,columnFerror]/2 for i in rows.tolist()),float)
        return F,K,Ferror

    def loadReport(self,path):
        with open(path,'r') as file:
            for i, line in enumerate(file):
                if i == 0:
                    self.date = line
                elif i == 2:
                    self.header = eval(line)
                else:
                    pass
        self.NumberOfPeaks = self.header['NumberOfPeaks']
        self.BGCheck = self.header['BGCheck']
        self.report = np.loadtxt(path,delimiter='\t',skiprows=5)
        self.Angles = np.unique(self.report[:,0])
        self.Kperps = np.unique(self.report[:,1])
        self.KPmax = self.Kperps.shape[0]-1
        self.AZmax = self.Angles.shape[0]-1
        self.AzimuthStart = self.Angles[0]
        self.AzimuthEnd = self.Angles[-1]
        self.RangeStart = self.Kperps[0]
        self.RangeEnd = self.Kperps[-1]
        self.KperpSliderScale = self.KPmax/(self.RangeEnd-self.RangeStart)
        self.KperpSlider.setMaximum(self.KPmax)
        self.KperpSlider.setValue(0)
        self.AzimuthLabel.setText("Azimuth Angle = {:5.1f} (\u00B0)".format(self.currentAzimuth*1.8+self.AzimuthStart))
        self.AzimuthSlider.setMaximum(self.AZmax)
        self.AzimuthSlider.setValue(0)
        self.KperpLabel.setText("Kperp = {:6.2f} (\u212B\u207B\u00B9)".format(self.currentKP/self.KperpSliderScale+self.RangeStart))
        if self.BGCheck:
            self.ReportInformation.setText("Date of the report: "+self.date+\
            'Number of peaks: {}\nStart image index: {}\nEnd image index: {}\nStart Kperp position: {:5.2f} (\u212B\u207B\u00B9)\nEnd Kperp position: {:5.2f} (\u212B\u207B\u00B9)\nKperp step size: {:5.2f} (\u212B\u207B\u00B9)'\
            .format(self.NumberOfPeaks,int(self.AzimuthStart/1.8),int(self.AzimuthEnd/1.8),self.RangeStart,self.RangeEnd,(self.Kperps[1]-self.Kperps[0])))
        else:
            self.ReportInformation.setText("Date of the report: "+self.date+ \
            'Number of peaks: {}\nStart image index: {}\nEnd image index: {}\nStart Kperp position: {:5.2f} (\u212B\u207B\u00B9)\nEnd Kperp position: {:5.2f} (\u212B\u207B\u00B9)\nKperp step size: {:5.2f} (\u212B\u207B\u00B9)'\
             .format(self.NumberOfPeaks+1,int(self.AzimuthStart/1.8),int(self.AzimuthEnd/1.8),self.RangeStart,self.RangeEnd,(self.Kperps[1]-self.Kperps[0])))
        self.peak.clear()
        peaks = ['L5','L4','L3','L2','L1','Center','R1','R2','R3','R4','R5','BG']
        if self.BGCheck:
            for i in range(5-int((self.NumberOfPeaks-1)/2),5+int((self.NumberOfPeaks-1)/2)+1):
                self.peak.addItem(peaks[i],str(i-(5-(self.NumberOfPeaks-1)/2)))
        else:
            for i in range(5-int((self.NumberOfPeaks-1)/2),5+int((self.NumberOfPeaks-1)/2)):
                self.peak.addItem(peaks[i],str(i-int((5-(self.NumberOfPeaks-1)/2))))
        self.peak.setCurrentText('Center')
        self.updateLog("The report file is loaded")



    def AzimuthChanged(self):
        self.currentAzimuth = self.AzimuthSlider.value()
        self.AzimuthLabel.setText("Azimuth Angle = {:5.1f} (\u00B0)".format(self.currentAzimuth*1.8+self.AzimuthStart))
        self.RefreshPlots()

    def KPChanged(self):
        self.currentKP = self.KperpSlider.value()
        self.KperpLabel.setText("Kperp = {:6.2f} (\u212B\u207B\u00B9)".format(self.currentKP/self.KperpSliderScale+self.RangeStart))
        self.RefreshPlots()

    def IACheckChanged(self,status):
        if status == 0:
            self.intensityRangeSlider.setEnabled(False)
            if self.FA.checkState() == 0:
                self.KperpSlider.setEnabled(False)
        else:
            self.KperpSlider.setEnabled(True)
            self.intensityRangeSlider.setEnabled(True)
        self.checkStartOK()

    def FACheckChanged(self,status):
        if status == 0:
            self.HWHMRangeSlider.setEnabled(False)
            if self.IA.checkState() == 0:
                self.KperpSlider.setEnabled(False)
        else:
            self.KperpSlider.setEnabled(True)
            self.HWHMRangeSlider.setEnabled(True)
        self.checkStartOK()

    def IKCheckChanged(self,status):
        if status == 0 and self.FK.checkState() == 0:
            self.AzimuthSlider.setEnabled(False)
        else:
            self.AzimuthSlider.setEnabled(True)
        self.checkStartOK()

    def FKCheckChanged(self,status):
        if status == 0 and self.IK.checkState() == 0:
            self.AzimuthSlider.setEnabled(False)
        else:
            self.AzimuthSlider.setEnabled(True)
        self.checkStartOK()

    def checkStartOK(self):
        if self.IA.checkState() == 0 and self.IK.checkState() == 0 and self.FA.checkState() == 0 and self.FK.checkState() == 0:
            self.ButtonBox.findChildren(QtWidgets.QPushButton)[0].setEnabled(False)
        else:
            self.ButtonBox.findChildren(QtWidgets.QPushButton)[0].setEnabled(True)

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
