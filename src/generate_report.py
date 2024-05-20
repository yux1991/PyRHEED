from my_widgets import ColorPicker, DoubleSlider
from PyQt6 import QtCore, QtWidgets, QtGui, QtCharts
import configparser
import matplotlib.pyplot as plt
import numpy as np
import os
import plot_chart
from scipy.stats import linregress as lrg

class Window(QtCore.QObject):

    STATUS_REQUESTED = QtCore.pyqtSignal()
    POLAR_I_REQUESTED = QtCore.pyqtSignal()
    POLAR_F_REQUESTED = QtCore.pyqtSignal()
    REFRESH_POLAR_I = QtCore.pyqtSignal(np.ndarray,np.ndarray,str,str,int,str,bool,dict)
    REFRESH_POLAR_F = QtCore.pyqtSignal(np.ndarray,np.ndarray,str,str,int,str,bool,dict)
    NORMAL_I_REQUESTED = QtCore.pyqtSignal()
    NORMAL_F_REQUESTED = QtCore.pyqtSignal()
    REFRESH_NORMAL_I = QtCore.pyqtSignal(np.ndarray,np.ndarray,str,str,int,str,bool,dict)
    REFRESH_NORMAL_F = QtCore.pyqtSignal(np.ndarray,np.ndarray,str,str,int,str,bool,dict)
    FONTS_CHANGED = QtCore.pyqtSignal(str,int)
    TOGGLE_DARK_MODE_REQUEST = QtCore.pyqtSignal(str)

    def __init__(self):
        super(Window,self).__init__()
        self.config = configparser.ConfigParser()
        self.dirname = os.path.dirname(__file__)
        self.config.read(os.path.join(self.dirname,'configuration.ini'))

    def set_status(self,status):
        self.status = status

    def main(self,path,preload=False):
        self.STATUS_REQUESTED.emit()
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
        self.chooseSource.setMinimumWidth(300)
        self.sourceGrid = QtWidgets.QGridLayout(self.chooseSource)
        self.sourceGrid.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.chooseSourceLabel = QtWidgets.QLabel("The path of the report file is:\n"+self.path)
        self.chooseSourceButton = QtWidgets.QPushButton("Browse...")
        self.chooseSourceButton.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed,QtWidgets.QSizePolicy.Policy.Fixed)
        self.chooseSourceButton.clicked.connect(self.choose_source)
        self.sourceGrid.addWidget(self.chooseSourceLabel,0,0)
        self.sourceGrid.addWidget(self.chooseSourceButton,0,1)

        self.ReportInformationBox = QtWidgets.QGroupBox("Information")
        self.ReportInformationGrid = QtWidgets.QGridLayout(self.ReportInformationBox)
        self.ReportInformationGrid.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.ReportInformation = QtWidgets.QLabel("Fit function:\nNumber of peaks:\nDate of the report:\nStart image index:\nEnd image index:\nStart Kperp position:\nEnd Kperp position:\nKperp step size:")
        self.ReportInformationGrid.addWidget(self.ReportInformation)

        self.typeOfReportBox = QtWidgets.QGroupBox("Type of the Report to Be Generated")
        self.typeOfReportGrid = QtWidgets.QGridLayout(self.typeOfReportBox)
        self.typeOfReportGrid.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.type = QtWidgets.QButtonGroup()
        self.type.setExclusive(False)
        self.typeFrame = QtWidgets.QFrame()
        self.typeGrid = QtWidgets.QGridLayout(self.typeFrame)
        self.IA = QtWidgets.QCheckBox("Intensity vs Azimuth")
        self.IAColor = ColorPicker("IA",'tomato',False)
        self.FA = QtWidgets.QCheckBox("HWHM vs Azimuth")
        self.FAColor = ColorPicker("FA",'dodgerblue',False)
        self.IK = QtWidgets.QCheckBox("Intensity vs Kperp")
        self.IKColor = ColorPicker("IK",'sandybrown',False)
        self.FK = QtWidgets.QCheckBox("HWHM vs Kperp")
        self.FKColor = ColorPicker("FK",'limegreen',False)
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
        self.optionGrid = QtWidgets.QGridLayout(self.optionBox)
        self.optionGrid.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.peakLabel = QtWidgets.QLabel("Choose the peak to be analyzed:")
        self.peak = QtWidgets.QComboBox()
        self.peak.addItem('Center','0')
        self.figureGeneratorLabel = QtWidgets.QLabel("Choose the type of figure generator:")
        self.figureGenerator = QtWidgets.QComboBox()
        self.figureGenerator.addItem('Qt','Qt')
        self.figureGenerator.addItem('Matplotlib','Matplotlib')
        self.figureGenerator.currentTextChanged.connect(self.connect_OK_button)
        self.KperpLabel = QtWidgets.QLabel("Kperp = {:6.2f} (\u212B\u207B\u00B9)".format(self.currentKP/self.KperpSliderScale+self.RangeStart))
        self.KperpSlider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.KperpSlider.setMinimum(self.KPmin)
        self.KperpSlider.setMaximum(self.KPmax)
        self.KperpSlider.setValue(self.currentKP)
        self.KperpSlider.valueChanged.connect(self.kp_changed)
        self.KperpSlider.setEnabled(False)
        self.AzimuthLabel = QtWidgets.QLabel("Azimuth Angle = {:5.1f} (\u00B0)".format(self.currentAzimuth))
        self.AzimuthSlider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.AzimuthSlider.setMinimum(self.AZmin)
        self.AzimuthSlider.setMaximum(self.AZmax)
        self.AzimuthSlider.setValue(0)
        self.AzimuthSlider.valueChanged.connect(self.azimuth_changed)
        self.AzimuthSlider.setEnabled(False)

        self.intensityRangeSlider = DoubleSlider(minimum=0,maximum=200,scale=0.01,head=0,tail=1,text="Intensity",unit='arb. units')
        self.intensityRangeSlider.setEnabled(False)
        self.intensityRangeSlider.VALUE_CHANGED.connect(self.refresh_plots)
        self.HWHMRangeSlider = DoubleSlider(minimum=0,maximum=200,scale=0.01,head=0,tail=1,text="HWHM",unit='\u212B\u207B\u00B9')
        self.HWHMRangeSlider.setEnabled(False)
        self.HWHMRangeSlider.VALUE_CHANGED.connect(self.refresh_plots)

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
        self.appearanceGrid = QtWidgets.QGridLayout(self.appearance)
        self.appearanceGrid.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.fontListLabel = QtWidgets.QLabel("Change Font")
        self.fontList = QtWidgets.QFontComboBox()
        self.fontList.setCurrentFont(QtGui.QFont("Arial"))
        self.fontList.currentFontChanged.connect(self.refresh_font_name)
        self.fontSizeLabel = QtWidgets.QLabel("Adjust Font Size ({})".format(15))
        self.fontSizeSlider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.fontSizeSlider.setMinimum(1)
        self.fontSizeSlider.setMaximum(100)
        self.fontSizeSlider.setValue(15)
        self.fontSizeSlider.valueChanged.connect(self.refresh_font_size)
        self.appearanceGrid.addWidget(self.fontListLabel,0,0)
        self.appearanceGrid.addWidget(self.fontList,0,1)
        self.appearanceGrid.addWidget(self.fontSizeLabel,1,0)
        self.appearanceGrid.addWidget(self.fontSizeSlider,1,1)

        self.statusBar = QtWidgets.QGroupBox("Log")
        self.statusGrid = QtWidgets.QGridLayout(self.statusBar)
        self.statusBar.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,QtWidgets.QSizePolicy.Policy.Fixed)
        self.logBox = QtWidgets.QTextEdit(QtCore.QTime.currentTime().toString("hh:mm:ss")+\
                                    "\u00A0\u00A0\u00A0\u00A0Initialized!")
        self.logCursor = QtGui.QTextCursor(self.logBox.document())
        self.logCursor.movePosition(QtGui.QTextCursor.MoveOperation.End)
        self.logBox.setTextCursor(self.logCursor)
        self.logBox.ensureCursorVisible()
        self.logBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.logBox.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.logBoxScroll = QtWidgets.QScrollArea()
        self.logBoxScroll.setWidget(self.logBox)
        self.logBoxScroll.setWidgetResizable(True)
        self.logBoxScroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.statusGrid.addWidget(self.logBoxScroll,0,0)

        self.ButtonBox = QtWidgets.QDialogButtonBox()
        self.ButtonBox.addButton("OK",QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole)
        self.ButtonBox.addButton("Fit",QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole)
        self.ButtonBox.addButton("Quit",QtWidgets.QDialogButtonBox.ButtonRole.DestructiveRole)
        self.ButtonBox.setCenterButtons(True)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[1].clicked.\
            connect(self.linear_fit)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[2].clicked.\
            connect(self.reject)

        self.LeftGrid.addWidget(self.chooseSource,0,0,1,2)
        self.LeftGrid.addWidget(self.ReportInformationBox,1,0)
        self.LeftGrid.addWidget(self.typeOfReportBox,1,1)
        self.LeftGrid.addWidget(self.optionBox,3,0,1,2)
        self.LeftGrid.addWidget(self.appearance,4,0,1,2)
        self.LeftGrid.addWidget(self.statusBar,5,0,1,2)
        self.LeftGrid.addWidget(self.ButtonBox,6,0,1,2)
        self.Grid.addWidget(self.LeftFrame,0,0)

        self.IA.stateChanged.connect(self.IA_check_changed)
        self.FA.stateChanged.connect(self.FA_check_changed)
        self.IK.stateChanged.connect(self.IK_check_changed)
        self.FK.stateChanged.connect(self.FK_check_changed)
        self.IA.setChecked(True)

        self.connect_OK_button(self.figureGenerator.currentText())
        if preload:
            self.load_report(self.path)

        self.Dialog.setWindowTitle("Generate Report")
        self.Dialog.show()
        desktopRect = self.Dialog.geometry()
        center = desktopRect.center()
        self.Dialog.move(int(center.x()-self.Dialog.width()*0.5),int(center.y()-self.Dialog.height()*0.5))

    def refresh_font_size(self):
        self.fontSizeLabel.setText("Adjust Font Size ({})".format(self.fontSizeSlider.value()))
        self.FONTS_CHANGED.emit(self.fontList.currentFont().family(),self.fontSizeSlider.value())

    def refresh_font_name(self):
        self.FONTS_CHANGED.emit(self.fontList.currentFont().family(),self.fontSizeSlider.value())

    def connect_OK_button(self,text):
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[0].disconnect()
        if text == 'Qt':
            self.ButtonBox.findChildren(QtWidgets.QPushButton)[0].clicked. \
                connect(self.polar_start)
        elif text == 'Matplotlib':
            self.ButtonBox.findChildren(QtWidgets.QPushButton)[0].clicked. \
                connect(self.start)

    def update_log(self,msg):
        self.logBox.append(QtCore.QTime.currentTime().toString("hh:mm:ss")+"\u00A0\u00A0\u00A0\u00A0"+msg)

    def reject(self):
        self.Dialog.close()

    def choose_source(self):
        path = QtWidgets.QFileDialog.getOpenFileName(None,"Choose The Report File",self.path)
        self.path = path[0]
        self.pathExtension = os.path.splitext(self.path)[1]
        if not self.path=="":
            if not self.pathExtension == ".txt":
                self.raise_error('[Error: wrong file type] Please choose a *.txt file')
                self.update_log('[Error: wrong file type] Please choose a *.txt file')
            else:
                self.chooseSourceLabel.setText("The path of the report is:\n"+self.path)
                self.load_report(self.path)
        else:
            self.raise_error('[Error: No file] Please choose a *.txt file')
            self.update_log('[Error: No file] Please choose a *.txt file')


    def start(self):
        Kp = self.currentKP/self.KperpSliderScale+self.RangeStart
        Az = self.currentAzimuth*1.8+self.AzimuthStart
        if self.IK.checkState() == 2 and self.FK.checkState() == 2:
            I, K1, Ierror = self.get_IK()
            F, K2, Ferror = self.get_FK()
            self.plot_IFK(I,F,K1,Az)
        elif self.IK.checkState() == 2:
            I, K, Ierror = self.get_IK()
            self.plot_IK(I,K,Az)
        elif self.FK.checkState() == 2:
            F, K, Ferror = self.get_FK()
            self.plot_FK(F,K,Az)
        if self.IA.checkState() == 2:
            I, A, Ierror = self.get_IA()
            self.plot_IA(I,A,Kp,self.intensityRangeSlider.values()[0],self.intensityRangeSlider.values()[1])
        if self.FA.checkState() == 2:
            F, A, Ferror = self.get_FA()
            self.plot_FA(F,A,Kp,self.HWHMRangeSlider.values()[0],self.HWHMRangeSlider.values()[1])
        plt.show()

    def toggle_dark_mode(self, mode):
        self.TOGGLE_DARK_MODE_REQUEST.emit(mode)
        self.REFRESH_NORMAL_I = QtCore.pyqtSignal(np.ndarray,np.ndarray,str,str,int,str,bool,dict)
        self.REFRESH_NORMAL_F = QtCore.pyqtSignal(np.ndarray,np.ndarray,str,str,int,str,bool,dict)

    def polar_start(self):
        Kp = self.currentKP/self.KperpSliderScale+self.RangeStart
        Az = self.currentAzimuth*1.8+self.AzimuthStart
        theme = int(dict(self.config['chartDefault'].items())['theme'])
        self.IAPlot = plot_chart.PlotChart(theme,'Polar')
        self.FAPlot = plot_chart.PlotChart(theme,'Polar')
        self.IKPlot = plot_chart.PlotChart(theme,'Normal')
        self.FKPlot = plot_chart.PlotChart(theme,'Normal')
        self.TOGGLE_DARK_MODE_REQUEST.connect(self.IAPlot.toggle_dark_mode)
        self.TOGGLE_DARK_MODE_REQUEST.connect(self.FAPlot.toggle_dark_mode)
        self.TOGGLE_DARK_MODE_REQUEST.connect(self.IKPlot.toggle_dark_mode)
        self.TOGGLE_DARK_MODE_REQUEST.connect(self.FKPlot.toggle_dark_mode)
        self.POLAR_I_REQUESTED.connect(self.IAPlot.main)
        self.POLAR_F_REQUESTED.connect(self.FAPlot.main)
        self.NORMAL_I_REQUESTED.connect(self.IKPlot.main)
        self.NORMAL_F_REQUESTED.connect(self.FKPlot.main)
        self.REFRESH_POLAR_I.connect(self.IAPlot.add_chart)
        self.REFRESH_POLAR_F.connect(self.FAPlot.add_chart)
        self.REFRESH_NORMAL_I.connect(self.IKPlot.add_chart)
        self.REFRESH_NORMAL_F.connect(self.FKPlot.add_chart)
        self.FONTS_CHANGED.connect(self.IAPlot.adjust_fonts)
        self.FONTS_CHANGED.connect(self.FAPlot.adjust_fonts)
        self.FONTS_CHANGED.connect(self.FKPlot.adjust_fonts)
        self.FONTS_CHANGED.connect(self.IKPlot.adjust_fonts)
        self.IAColor.COLOR_CHANGED.connect(self.IAPlot.adjust_color)
        self.FAColor.COLOR_CHANGED.connect(self.FAPlot.adjust_color)
        self.IKColor.COLOR_CHANGED.connect(self.IKPlot.adjust_color)
        self.FKColor.COLOR_CHANGED.connect(self.FKPlot.adjust_color)
        self.Window = QtWidgets.QWidget()
        self.Window.setWindowTitle('Summary of Broadening Analysis')
        self.WindowLayout = QtWidgets.QGridLayout(self.Window)
        self.WindowLayout.addWidget(self.IAPlot,0,1)
        self.WindowLayout.addWidget(self.FAPlot,0,0)
        self.WindowLayout.addWidget(self.IKPlot,1,1)
        self.WindowLayout.addWidget(self.FKPlot,1,0)
        self.Window.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        self.Window.showMaximized()
        if self.IA.checkState() == 2:
            I, A, Ierror = self.get_IA()
            self.POLAR_I_REQUESTED.emit()
            self.IAIsPresent = True
            self.REFRESH_POLAR_I.emit(I,A,'IA',self.fontList.currentFont().family(),self.fontSizeSlider.value(),\
                                    self.IAColor.get_color(),False,\
                                    {'Kp':Kp,'low':self.intensityRangeSlider.values()[0],\
                                     'high':self.intensityRangeSlider.values()[1]})
        if self.IK.checkState() == 2:
            I,K,Ierror = self.get_IK()
            self.NORMAL_I_REQUESTED.emit()
            self.IKIsPresent = True
            self.REFRESH_NORMAL_I.emit(K,I,'IK',self.fontList.currentFont().family(),self.fontSizeSlider.value(), \
                                     self.IKColor.get_color(),True,\
                                     {'Az':Az})
        if self.FA.checkState() == 2:
            F, A, Ferror = self.get_FA()
            self.POLAR_F_REQUESTED.emit()
            self.FAIsPresent = True
            self.REFRESH_POLAR_F.emit(F,A,'FA',self.fontList.currentFont().family(),self.fontSizeSlider.value(), \
                                    self.FAColor.get_color(),False,\
                                    {'Kp':Kp,'low':self.HWHMRangeSlider.values()[0],\
                                                'high':self.HWHMRangeSlider.values()[1]})
        if self.FK.checkState() == 2:
            F,K,Ferror = self.get_FK()
            self.NORMAL_F_REQUESTED.emit()
            self.FKIsPresent = True
            self.REFRESH_NORMAL_F.emit(K,F,'FK',self.fontList.currentFont().family(),self.fontSizeSlider.value(), \
                                     self.FKColor.get_color(),True,\
                                     {'Az':Az})

    def plot_IA(self,I,A,Kp,imin,imax):
        A2 = A + np.full(len(A),180)
        Phi = np.append(A,A2)
        Heights = np.append(I,I)/np.amax(I)
        fig = plt.figure()
        ax = plt.subplot(projection='polar')
        ax.set_title('Intensity vs Azimuth at Kperp = {:5.2f} (\u212B\u207B\u00B9)'.format(Kp),fontsize=self.fontSizeSlider.value())
        ax.plot(Phi*np.pi/180,Heights,color=self.IAColor.get_color())
        ax.set_rmin(imin)
        ax.set_rmax(imax)
        ax.set_rlabel_position(0)
        ax.set_theta_direction(-1)
        ax.set_theta_zero_location('N')
        ax.set_thetagrids((0,30,60,90,120,150,180,210,240,270,300,330))
        ax.set_rticks(np.around(np.linspace(imin,imax,5),1))
        ax.tick_params(which='both', labelsize=self.fontSizeSlider.value())

    def plot_IK(self,I,K,Az):
        fig = plt.figure()
        ax = plt.subplot()
        ax.set_title('Intensity vs Kperp at Phi = {:5.2f}\u00B0'.format(Az),fontsize=self.fontSizeSlider.value())
        ax.plot(I,K,c=self.IKColor.get_color())
        ax.set_xlabel('Intensity (arb. units)',fontsize = self.fontSizeSlider.value())
        ax.set_ylabel(r'$K_{perp}$ $(\AA^{-1})$',fontsize = self.fontSizeSlider.value())
        ax.tick_params(which='both', labelsize=self.fontSizeSlider.value())

    def plot_FA(self,F,A,Kp,fmin,fmax):
        A2 = A + np.full(len(A),180)
        Phi = np.append(A,A2)
        HWHMs = np.append(F,F)
        fig = plt.figure()
        ax = plt.subplot(projection='polar')
        ax.set_title('HWHM vs Azimuth at Kperp = {:5.2f} (\u212B\u207B\u00B9)'.format(Kp),fontsize=self.fontSizeSlider.value())
        ax.plot(Phi*np.pi/180,HWHMs,color=self.FAColor.get_color())
        ax.set_rmin(fmin)
        ax.set_rmax(fmax)
        ax.set_rlabel_position(0)
        ax.set_theta_direction(-1)
        ax.set_theta_zero_location('N')
        ax.set_thetagrids((0,30,60,90,120,150,180,210,240,270,300,330))
        ax.set_rticks(np.around(np.linspace(fmin,fmax,5),1))
        ax.tick_params(which='both', labelsize=self.fontSizeSlider.value())

    def plot_FK(self,F,K,Az):
        fig = plt.figure()
        ax = plt.subplot()
        ax.set_title('HWHM vs Kperp at Phi = {:5.2f}\u00B0'.format(Az),fontsize=self.fontSizeSlider.value())
        ax.plot(F,K,c=self.FKColor.get_color())
        ax.set_xlabel(r'HWHM $(\AA^{-1})$',fontsize = self.fontSizeSlider.value())
        ax.set_ylabel(r'$K_{perp}$ $(\AA^{-1})$',fontsize = self.fontSizeSlider.value())
        ax.tick_params(which='both', labelsize=self.fontSizeSlider.value())

    def plot_IFK(self,I,F,K,Az):
        fig, ax1 = plt.subplots()
        fig.suptitle('Intensity and HWHM vs Kperp at Phi = {:5.2f}\u00B0'.format(Az),fontsize=self.fontSizeSlider.value())
        ax1.set_xlabel('Intensity (arb. units)',fontsize = self.fontSizeSlider.value(),color=self.IKColor.get_color())
        ax1.set_ylabel(r'$K_{perp}$ $(\AA^{-1})$',fontsize = self.fontSizeSlider.value())
        ax1.plot(I,K,c=self.IKColor.get_color())
        ax1.tick_params(axis='x',labelcolor='b')
        ax1.tick_params(axis='both',labelsize=self.fontSizeSlider.value())
        ax2 = ax1.twiny()
        ax2.set_xlabel(r'HWHM $(\AA^{-1})$',fontsize = self.fontSizeSlider.value(),color=self.FKColor.get_color())
        ax2.plot(F,K,c=self.FKColor.get_color())
        ax2.tick_params(axis='x',labelcolor='r')
        ax2.tick_params(axis='both',labelsize=self.fontSizeSlider.value())
        fig.tight_layout()

    def refresh_plots(self):
        Kp = self.currentKP/self.KperpSliderScale+self.RangeStart
        Az = self.currentAzimuth*1.8+self.AzimuthStart
        if self.IAIsPresent:
            I, A, Ierror = self.get_IA()
            self.REFRESH_POLAR_I.emit(I,A,'IA',self.fontList.currentFont().family(),self.fontSizeSlider.value(),\
                                    self.IAColor.get_color(),False,\
                                    {'Kp':Kp,'low':self.intensityRangeSlider.values()[0], \
                                                     'high':self.intensityRangeSlider.values()[1]})
        if self.FAIsPresent:
            F, A, Ferror = self.get_FA()
            self.REFRESH_POLAR_F.emit(F,A,'FA',self.fontList.currentFont().family(),self.fontSizeSlider.value(), \
                                    self.FAColor.get_color(),False,\
                                    {'Kp':Kp,'low':self.HWHMRangeSlider.values()[0], \
                                                'high':self.HWHMRangeSlider.values()[1]})
        if self.IKIsPresent:
            I,K,Ierror = self.get_IK()
            self.REFRESH_NORMAL_I.emit(K,I,'IK',self.fontList.currentFont().family(),self.fontSizeSlider.value(), \
                                     self.IKColor.get_color(),True,\
                                     {'Az':Az})
        if self.FKIsPresent:
            F,K,Ferror = self.get_FK()
            self.REFRESH_NORMAL_F.emit(K,F,'FK',self.fontList.currentFont().family(),self.fontSizeSlider.value(), \
                                     self.FKColor.get_color(),True,\
                                     {'Az':Az})

    def get_IA(self):
        if self.BGCheck:
            nop = self.NumberOfPeaks+1
        else:
            nop = self.NumberOfPeaks
        peakIndex = np.round(float(self.peak.currentData()),0)
        if self.fit_function == 'Gaussian':
            columnI = int(1+peakIndex*2+1)
            columnIerror = int(1+peakIndex*2+2)
        elif self.fit_function == 'Voigt':
            columnI = int(1+nop*2+peakIndex*2+1)
            columnIerror = int(1+nop*2+peakIndex*2+2)
        rows = np.full(self.AZmax+1, self.currentKP).astype(int) + np.linspace(0,self.AZmax,self.AZmax+1).astype(int)*(self.KPmax+1)
        A = self.Angles
        I = np.fromiter((self.report[i,columnI] for i in rows.tolist()),float)
        Ierror = np.fromiter((self.report[i,columnIerror] for i in rows.tolist()),float)
        return I,A,Ierror

    def get_FA(self):
        if self.BGCheck:
            nop = self.NumberOfPeaks+1
        else:
            nop = self.NumberOfPeaks
        peakIndex = np.round(float(self.peak.currentData()),0)
        if self.fit_function == 'Gaussian':
            columnF = int(1+nop*4+peakIndex*2+1)
            columnFerror = int(1+nop*4+peakIndex*2+2)
        elif self.fit_function == 'Voigt':
            columnFL = int(1+nop*4+peakIndex*2+1)
            columnFLerror = int(1+nop*4+peakIndex*2+2)
            columnFG = int(1+nop*6+peakIndex*2+1)
            columnFGerror = int(1+nop*6+peakIndex*2+2)
        rows = np.full(self.AZmax+1, self.currentKP).astype(int) + np.linspace(0,self.AZmax,self.AZmax+1).astype(int)*(self.KPmax+1)
        A = self.Angles
        if self.fit_function == 'Gaussian':
            F = np.fromiter((self.report[i,columnF]/2 for i in rows.tolist()),float)
            Ferror = np.fromiter((self.report[i,columnFerror]/2 for i in rows.tolist()),float)
        elif self.fit_function == 'Voigt':
            F = np.fromiter(((0.5346*self.report[i,columnFL]+np.sqrt(0.2166*self.report[i,columnFL]**2+self.report[i,columnFG]**2))/2 for i in rows.tolist()),float)
            Ferror = np.fromiter(((0.5346*self.report[i,columnFLerror]+(0.4332*self.report[i,columnFLerror]+2*self.report[i,columnFGerror])/np.sqrt(0.2166*self.report[i,columnFL]**2+self.report[i,columnFG]**2))/2 for i in rows.tolist()),float)
        return F,A,Ferror

    def get_IK(self):
        if self.BGCheck:
            nop = self.NumberOfPeaks+1
        else:
            nop = self.NumberOfPeaks
        peakIndex = np.round(float(self.peak.currentData()),0)
        if self.fit_function == 'Gaussian':
            columnI = int(1+peakIndex*2+1)
            columnIerror = int(1+peakIndex*2+2)
        elif self.fit_function == 'Voigt':
            columnI = int(1+nop*2+peakIndex*2+1)
            columnIerror = int(1+nop*2+peakIndex*2+2)
        rows = np.full(self.KPmax+1, self.currentAzimuth*(self.KPmax+1)).astype(int) + np.linspace(0,self.KPmax,self.KPmax+1).astype(int)
        K = self.Kperps
        I = np.fromiter((self.report[i,columnI] for i in rows.tolist()),float)
        Ierror = np.fromiter((self.report[i,columnIerror] for i in rows.tolist()),float)
        return I,K,Ierror

    def get_FK(self):
        if self.BGCheck:
            nop = self.NumberOfPeaks+1
        else:
            nop = self.NumberOfPeaks
        peakIndex = np.round(float(self.peak.currentData()),0)
        if self.fit_function == 'Gaussian':
            columnF = int(1+nop*4+peakIndex*2+1)
            columnFerror = int(1+nop*4+peakIndex*2+2)
        elif self.fit_function == 'Voigt':
            columnFL = int(1+nop*4+peakIndex*2+1)
            columnFLerror = int(1+nop*4+peakIndex*2+2)
            columnFG = int(1+nop*6+peakIndex*2+1)
            columnFGerror = int(1+nop*6+peakIndex*2+2)
        rows = np.full(self.KPmax+1, self.currentAzimuth*(self.KPmax+1)).astype(int) + np.linspace(0,self.KPmax,self.KPmax+1).astype(int)
        K = self.Kperps
        if self.fit_function == 'Gaussian':
            F = np.fromiter((self.report[i,columnF]/2 for i in rows.tolist()),float)
            Ferror = np.fromiter((self.report[i,columnFerror]/2 for i in rows.tolist()),float)
        elif self.fit_function == 'Voigt':
            F = np.fromiter(((0.5346*self.report[i,columnFL]+np.sqrt(0.2166*self.report[i,columnFL]**2+self.report[i,columnFG]**2))/2 for i in rows.tolist()),float)
            Ferror = np.fromiter(((0.5346*self.report[i,columnFLerror]+(0.4332*self.report[i,columnFLerror]+2*self.report[i,columnFGerror])/np.sqrt(0.2166*self.report[i,columnFL]**2+self.report[i,columnFG]**2))/2 for i in rows.tolist()),float)
        return F,K,Ferror

    def linear_fit(self):
        file_name = QtWidgets.QFileDialog.getSaveFileName(None,"choose save file name",os.path.join(self.dirname,"linear_fit_results.txt"),"TXT (*.txt)")
        if file_name:
            output = open(file_name[0],mode='w')
            for i in range(self.AZmin,self.AZmax+1):
                self.currentAzimuth = i
                Az = self.currentAzimuth*1.8+self.AzimuthStart
                F,K,Ferror = self.get_FK()
                F_part = F[10:len(F)-30]
                K_part = K[10:len(K)-30]
                slope, intercept, r, p, stderr = lrg(K_part*K_part,F_part*F_part)
                output.write('{:9.6f}\t{:9.6f}\t{:9.6f}\t{:9.6f}\n'.format(Az,slope,intercept,stderr))
                fig = plt.figure()
                ax = plt.subplot()
                ax.set_title(r'$h^{2} vs k^{2}$')
                ax.scatter(K_part*K_part,F_part*F_part)
                ax.plot(K_part*K_part,slope*K_part*K_part+intercept)
                ax.set_xlabel(r'$k^{2}$')
                ax.set_ylabel(r'$h^{2}$')
            output.close
            plt.show()
        self.update_log("The fitting is done!")

    def load_report(self,path):
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
        self.fit_function = self.header.get('fit_function','Gaussian')
        self.report = np.loadtxt(path,delimiter='\t',skiprows=5)
        self.Angles = np.unique(self.report[:,0])
        self.Kperps = np.unique(self.report[:,1])
        self.KPmax = self.Kperps.shape[0]-1
        self.AZmax = self.Angles.shape[0]-1
        self.AzimuthStart = self.Angles[0]
        self.AzimuthEnd = self.Angles[-1]
        self.startIndex = self.header.get('StartImageIndex',int(self.AzimuthStart/1.8))
        self.endIndex = self.header.get('EndImageIndex',int(self.AzimuthEnd/1.8))
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
            if len(self.Kperps) > 1:
                self.ReportInformation.setText("Date of the report: "+self.date+\
                'Fit function: '+self.fit_function+'\n'+'Number of peaks: {}\nStart image index: {}\nEnd image index: {}\nStart Kperp position: {:5.2f} (\u212B\u207B\u00B9)\nEnd Kperp position: {:5.2f} (\u212B\u207B\u00B9)\nKperp step size: {:5.2f} (\u212B\u207B\u00B9)'\
                .format(self.NumberOfPeaks+1,self.startIndex, self.endIndex,self.RangeStart,self.RangeEnd,(self.Kperps[1]-self.Kperps[0])))
            else:
                self.ReportInformation.setText("Date of the report: "+self.date+ \
                'Fit function: '+self.fit_function+'\n'+'Number of peaks: {}\nStart image index: {}\nEnd image index: {}\nStart Kperp position: {:5.2f} (\u212B\u207B\u00B9)\nEnd Kperp position: {:5.2f} (\u212B\u207B\u00B9)\nKperp step size: {:5.2f} (\u212B\u207B\u00B9)' \
                .format(self.NumberOfPeaks+1,self.startIndex, self.endIndex,self.RangeStart,self.RangeEnd,0))
        else:
            if len(self.Kperps) > 1:
                self.ReportInformation.setText("Date of the report: "+self.date+ \
                'Fit function: '+self.fit_function+'\n'+'Number of peaks: {}\nStart image index: {}\nEnd image index: {}\nStart Kperp position: {:5.2f} (\u212B\u207B\u00B9)\nEnd Kperp position: {:5.2f} (\u212B\u207B\u00B9)\nKperp step size: {:5.2f} (\u212B\u207B\u00B9)'\
                 .format(self.NumberOfPeaks,self.startIndex, self.endIndex,self.RangeStart,self.RangeEnd,(self.Kperps[1]-self.Kperps[0])))
            else:
                self.ReportInformation.setText("Date of the report: "+self.date+ \
                'Fit function: '+self.fit_function+'\n'+'Number of peaks: {}\nStart image index: {}\nEnd image index: {}\nStart Kperp position: {:5.2f} (\u212B\u207B\u00B9)\nEnd Kperp position: {:5.2f} (\u212B\u207B\u00B9)\nKperp step size: {:5.2f} (\u212B\u207B\u00B9)' \
                .format(self.NumberOfPeaks,self.startIndex, self.endIndex,self.RangeStart,self.RangeEnd,0))
        self.peak.clear()
        peaks = ['L5','L4','L3','L2','L1','Center','R1','R2','R3','R4','R5','BG']
        if self.BGCheck:
            for i in range(5-int((self.NumberOfPeaks-1)/2),5+int((self.NumberOfPeaks-1)/2)):
                self.peak.addItem(peaks[i],str(i-(5-(self.NumberOfPeaks-1)/2)))
        else:
            for i in range(5-int((self.NumberOfPeaks-1)/2),5+int((self.NumberOfPeaks-1)/2)+1):
                self.peak.addItem(peaks[i],str(i-int((5-(self.NumberOfPeaks-1)/2))))
        self.peak.setCurrentText('Center')
        self.update_log("The report file is loaded")



    def azimuth_changed(self):
        self.currentAzimuth = self.AzimuthSlider.value()
        self.AzimuthLabel.setText("Azimuth Angle = {:5.1f} (\u00B0)".format(self.currentAzimuth*1.8+self.AzimuthStart))
        self.refresh_plots()

    def kp_changed(self):
        self.currentKP = self.KperpSlider.value()
        self.KperpLabel.setText("Kperp = {:6.2f} (\u212B\u207B\u00B9)".format(self.currentKP/self.KperpSliderScale+self.RangeStart))
        self.refresh_plots()

    def IA_check_changed(self,status):
        if status == 0:
            self.intensityRangeSlider.setEnabled(False)
            if self.FA.checkState() == 0:
                self.KperpSlider.setEnabled(False)
        else:
            self.KperpSlider.setEnabled(True)
            self.intensityRangeSlider.setEnabled(True)
        self.check_start_OK()

    def FA_check_changed(self,status):
        if status == 0:
            self.HWHMRangeSlider.setEnabled(False)
            if self.IA.checkState() == 0:
                self.KperpSlider.setEnabled(False)
        else:
            self.KperpSlider.setEnabled(True)
            self.HWHMRangeSlider.setEnabled(True)
        self.check_start_OK()

    def IK_check_changed(self,status):
        if status == 0 and self.FK.checkState() == 0:
            self.AzimuthSlider.setEnabled(False)
        else:
            self.AzimuthSlider.setEnabled(True)
        self.check_start_OK()

    def FK_check_changed(self,status):
        if status == 0 and self.IK.checkState() == 0:
            self.AzimuthSlider.setEnabled(False)
        else:
            self.AzimuthSlider.setEnabled(True)
        self.check_start_OK()

    def check_start_OK(self):
        if self.IA.checkState() == 0 and self.IK.checkState() == 0 and self.FA.checkState() == 0 and self.FK.checkState() == 0:
            self.ButtonBox.findChildren(QtWidgets.QPushButton)[0].setEnabled(False)
        else:
            self.ButtonBox.findChildren(QtWidgets.QPushButton)[0].setEnabled(True)

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
