from PyQt5 import QtCore, QtWidgets, QtGui, QtChart
import numpy as np
import os
import glob
import configparser
import Process
import math
import ProfileChart
import matplotlib.pyplot as plt

class Preference(QtCore.QObject):

    #Public Signals
    DefaultSettingsChanged = QtCore.pyqtSignal(configparser.ConfigParser)

    def __init__(self):
        super(Preference,self).__init__()
        self.twoDimensionalMappingRegion = [0,0,0,0,0]
        self.config = configparser.ConfigParser()
        self.config.read('./configuration.ini')
        self.defaultLineValueList = [['0', '0', '20', '0', '5', '60', '0.4', '100', '5', '20', '10', '0', '10'], \
                                     ['361.13', '20', '0', '5', '30', '0', '100', '50', '0', '500', '0.4', '0', '1',\
                                      '100', '60', '0', '180', '5', '0', '20', '10', '0', '-15', '15', '10'], \
                                     ['0.4', '20', '60', '0', '21'], ['1']]

#Preference_Default Settings

    def Main(self):
        self.windowDefault = dict(self.config['windowDefault'].items())
        self.propertiesDefault = dict(self.config['propertiesDefault'].items())
        self.canvasDefault = dict(self.config['canvasDefault'].items())
        self.chartDefault = dict(self.config['chartDefault'].items())
        self.DefaultSettings_Dialog = QtWidgets.QDialog()
        self.DefaultSettings_DialogGrid = QtWidgets.QGridLayout(self.DefaultSettings_Dialog)
        self.tab = self.RefreshTab(self.config)
        buttonBox = QtWidgets.QDialogButtonBox()
        buttonBox.addButton("Accept",QtWidgets.QDialogButtonBox.AcceptRole)
        buttonBox.addButton("Reset",QtWidgets.QDialogButtonBox.ResetRole)
        buttonBox.addButton("Cancel",QtWidgets.QDialogButtonBox.DestructiveRole)
        buttonBox.setCenterButtons(True)
        buttonBox.findChildren(QtWidgets.QPushButton)[0].clicked.connect(self.Accept)
        buttonBox.findChildren(QtWidgets.QPushButton)[1].clicked.connect(self.Reset)
        buttonBox.findChildren(QtWidgets.QPushButton)[2].clicked.connect(self.DefaultSettings_Dialog.reject)
        self.DefaultSettings_DialogGrid.addWidget(self.tab,0,0)
        self.DefaultSettings_DialogGrid.addWidget(buttonBox,1,0)
        self.DefaultSettings_DialogGrid.setContentsMargins(0,0,0,0)
        self.DefaultSettings_Dialog.setWindowTitle("Default Settings")
        self.DefaultSettings_Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        self.DefaultSettings_Dialog.resize(self.tab.minimumSizeHint())
        self.DefaultSettings_Dialog.showNormal()
        self.DefaultSettings_Dialog.exec_()

    def Save(self,lineValueList):
        windowKeys = ['HS','VS','energy','azimuth','scaleBarLength','chiRange','width','widthSliderScale','radius',\
                      'radiusMaximum','radiusSliderScale','tiltAngle','tiltAngleSliderScale']
        propertiesKeys = ['sensitivity','electronEnergy','azimuth','scaleBarLength','brightness','brightnessMinimum',\
                          'brightnessMaximum','blackLevel','blackLevelMinimum','blackLevelMaximum','integralHalfWidth','widthMinimum','widthMaximum','widthSliderScale',\
                          'chiRange','chiRangeMinimum','chiRangeMaximum','radius','radiusMinimum','radiusMaximum',\
                          'radiusSliderScale','tiltAngle','tiltAngleMinimum','tiltAngleMaximum','tiltAngleSliderScale']
        canvasKeys=['widthInAngstrom','radiusMaximum','span','tilt','max_zoom_factor']
        chartKeys = ['theme']
        Dic = {'windowDefault':{key:value for (key,value) in zip(windowKeys,lineValueList[0])},\
               'propertiesDefault':{key:value for (key,value) in zip(propertiesKeys,lineValueList[1])}, \
               'canvasDefault':{key:value for (key,value) in zip(canvasKeys,lineValueList[2])}, \
               'chartDefault':{key:value for (key,value) in zip(chartKeys,lineValueList[3])},\
               }
        config = configparser.ConfigParser()
        config.read_dict(Dic)
        with open('./configuration.ini','w') as configfile:
            config.write(configfile)
        return Dic

    def RefreshTab(self,config):
        windowDefault = dict(config['windowDefault'].items())
        propertiesDefault = dict(config['propertiesDefault'].items())
        canvasDefault = dict(config['canvasDefault'].items())
        chartDefault = dict(config['chartDefault'].items())
        tab = QtWidgets.QTabWidget()
        self.window = QtWidgets.QWidget()
        self.properties = QtWidgets.QWidget()
        self.canvas = QtWidgets.QWidget()
        self.chart = QtWidgets.QWidget()
        chartCombo = QtWidgets.QComboBox()
        chartCombo.addItem("Light","0")
        chartCombo.addItem("BlueCerulean","1")
        chartCombo.addItem("Dark","2")
        chartCombo.addItem("Brown Sand","3")
        chartCombo.addItem("Blue Ncs","4")
        chartCombo.addItem("High Contrast","5")
        chartCombo.addItem("Blue Icey","6")
        chartCombo.addItem("Qt","7")
        chartCombo.setCurrentIndex(int(chartDefault["theme"]))
        windowGrid = QtWidgets.QGridLayout(self.window)
        windowMode = [('Horizontal Shift (px)',windowDefault['hs'],0,0,1),\
                      ('Vertical Shift (px)',windowDefault['vs'],1,0,1),\
                      ('Energy (keV)',windowDefault['energy'],2,0,1),\
                      ('Azimuth (\u00B0)',windowDefault['azimuth'],3,0,1),\
                      ('Scale Bar Length (\u212B\u207B\u00B9)',windowDefault['scalebarlength'],4,0,1),\
                      ('Chi Range (\u00B0)',windowDefault['chirange'],5,0,1),\
                      ('Integral Half Width (\u212B\u207B\u00B9)',windowDefault['width'],6,0,1),\
                      ('Integral Half Width Slider Scale',windowDefault['widthsliderscale'],7,0,1),\
                      ('Radius (\u212B\u207B\u00B9)',windowDefault['radius'],8,0,1),\
                      ('Radius Maximum (\u212B\u207B\u00B9)',windowDefault['radiusmaximum'],9,0,1),\
                      ('Radius Slider Scale',windowDefault['radiussliderscale'],10,0,1),\
                      ('Tilt Angle (\u00B0)',windowDefault['tiltangle'],11,0,1),\
                      ('Tilt Angle Slider Scale',windowDefault['tiltanglesliderscale'],12,0,1)]
        propertiesGrid = QtWidgets.QGridLayout(self.properties)
        propertiesMode = [('Sensitivity (pixel/sqrt[keV])',propertiesDefault['sensitivity'],0,0,3),\
                          ('Electron Energy (keV)',propertiesDefault['electronenergy'],1,0,3),\
                          ('Azimuth (\u00B0)',propertiesDefault['azimuth'],2,0,3),\
                          ('Scale Bar Length (\u212B\u207B\u00B9)',propertiesDefault['scalebarlength'],3,0,3),\
                          (',',propertiesDefault['brightness'],4,1,1),\
                          ('Brightness (Minimum,Default,Maximum)',propertiesDefault['brightnessminimum'],4,0,1),\
                          (',',propertiesDefault['brightnessmaximum'],4,2,1),\
                          (',',propertiesDefault['blacklevel'],5,1,1),\
                          ('Black Level (Minimum,Default,Maximum)',propertiesDefault['blacklevelminimum'],5,0,1),\
                          (',',propertiesDefault['blacklevelmaximum'],5,2,1),\
                          (',',propertiesDefault['integralhalfwidth'],6,1,1),\
                          ('Half Width (\u212B\u207B\u00B9) (Minimum,Default,Maximum)',propertiesDefault['widthminimum'],6,0,1),\
                          (',',propertiesDefault['widthmaximum'],6,2,1),\
                          ('Slider Scales (Half Width,Radius,Tilt Angle)',propertiesDefault['widthsliderscale'],10,0,1),\
                          (',',propertiesDefault['chirange'],7,1,1),\
                          ('Chi Range (\u00B0) (Minimum,Default,Maximum)',propertiesDefault['chirangeminimum'],7,0,1),\
                          (',',propertiesDefault['chirangemaximum'],7,2,1),\
                          (',',propertiesDefault['radius'],8,1,1),\
                          ('Radius (\u212B\u207B\u00B9) (Minimum,Default,Maximum)',propertiesDefault['radiusminimum'],8,0,1),\
                          (',',propertiesDefault['radiusmaximum'],8,2,1),\
                          (',',propertiesDefault['radiussliderscale'],10,1,1),\
                          (',',propertiesDefault['tiltangle'],9,1,1),\
                          ('Tilt Angle (\u00B0) (Minimum,Default,Maximum)',propertiesDefault['tiltangleminimum'],9,0,1),\
                          (',',propertiesDefault['tiltanglemaximum'],9,2,1),\
                          (',',propertiesDefault['tiltanglesliderscale'],10,2,1)]
        canvasGrid = QtWidgets.QGridLayout(self.canvas)
        canvasMode = [('Integral Half Width',canvasDefault['widthinangstrom'],0,0,1),\
                      ('Radius Maximum',canvasDefault['radiusmaximum'],1,0,1),\
                      ('Span',canvasDefault['span'],2,0,1),\
                      ('Tilt',canvasDefault['tilt'],3,0,1),\
                      ('Maximum Zoom Factor',canvasDefault['max_zoom_factor'],4,0,1)]
        chartGrid = QtWidgets.QVBoxLayout(self.chart)
        chartGrid.setAlignment(QtCore.Qt.AlignTop)
        PageMode = [(windowGrid,windowMode),(propertiesGrid,propertiesMode),(canvasGrid,canvasMode)]
        for grid, mode in PageMode:
            for label,value,row,col,span in mode:
                grid.addWidget(QtWidgets.QLabel(label),row,2*col,1,1)
                grid.addWidget(QtWidgets.QLineEdit(value),row,2*col+1,1,2*span-1)
                grid.setAlignment(QtCore.Qt.AlignTop)
        chartGrid.addWidget(QtWidgets.QLabel("Theme:"))
        chartGrid.addWidget(chartCombo)
        tab.addTab(self.window,"Window")
        tab.addTab(self.properties,"Properties")
        tab.addTab(self.canvas,"Canvas")
        tab.addTab(self.chart,"Chart")
        return tab

    def Accept(self):
        windowValueList = [item.text() for item in self.window.findChildren(QtWidgets.QLineEdit)]
        propertiesValueList = [item.text() for item in self.properties.findChildren(QtWidgets.QLineEdit)]
        canvasValueList = [item.text() for item in self.canvas.findChildren(QtWidgets.QLineEdit)]
        chartValueList = [item.currentData() for item in self.chart.findChildren(QtWidgets.QComboBox)]
        lineValueList = [windowValueList, propertiesValueList,canvasValueList,chartValueList]
        Dic = self.Save(lineValueList)
        config = configparser.ConfigParser()
        config.read_dict(Dic)
        self.DefaultSettingsChanged.emit(config)

    def Reset(self):
        Dic = self.Save(self.defaultLineValueList)
        config = configparser.ConfigParser()
        config.read_dict(Dic)
        self.DefaultSettingsChanged.emit(config)
        tab_new = self.RefreshTab(config)
        self.DefaultSettings_DialogGrid.replaceWidget(self.tab,tab_new)
        self.tab = tab_new

class TwoDimensionalMapping(QtCore.QObject,Process.Image):
    #Public Signals
    StatusRequested = QtCore.pyqtSignal()
    progressAdvance = QtCore.pyqtSignal(int,int,int)
    progressEnd = QtCore.pyqtSignal()
    Show3DGraph = QtCore.pyqtSignal(str)
    Show2DContour = QtCore.pyqtSignal(str,bool,float,float,float,float,int,str)

    def __init__(self):
        super(TwoDimensionalMapping,self).__init__()
        self.twoDimensionalMappingRegion = [0,0,0,0,0]
        self.config = configparser.ConfigParser()
        self.config.read('./configuration.ini')

    def refresh(self,config):
        self.config = config
        try:
            self.chart.refresh(config)
        except:
            pass

    def Main(self,path):
        self.levelMin = 0
        self.levelMax = 100
        self.numberOfContourLevels = 5
        self.startIndex = "0"
        self.endIndex = "100"
        self.defaultFileName = "2D_Map"
        self.path = os.path.dirname(path)
        self.currentSource = self.path
        self.currentDestination = self.currentSource
        self.Dialog = QtWidgets.QDialog()
        self.Grid = QtWidgets.QGridLayout(self.Dialog)
        self.LeftFrame = QtWidgets.QFrame()
        self.RightFrame = QtWidgets.QFrame()
        self.LeftGrid = QtWidgets.QGridLayout(self.LeftFrame)
        self.RightGrid = QtWidgets.QGridLayout(self.RightFrame)
        self.chooseSource = QtWidgets.QGroupBox("Source Directory")
        self.chooseSource.setStyleSheet('QGroupBox::title {color:blue;}')
        self.sourceGrid = QtWidgets.QGridLayout(self.chooseSource)
        self.sourceGrid.setAlignment(QtCore.Qt.AlignTop)
        self.chooseSourceLabel = QtWidgets.QLabel("The source directory is:\n"+self.currentSource)
        self.chooseSourceButton = QtWidgets.QPushButton("Browse...")
        self.chooseSourceButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
        self.chooseSourceButton.clicked.connect(self.Choose_Source)
        self.sourceGrid.addWidget(self.chooseSourceLabel,0,0)
        self.sourceGrid.addWidget(self.chooseSourceButton,0,1)
        self.chooseDestination = QtWidgets.QGroupBox("Save Destination")
        self.chooseDestination.setStyleSheet('QGroupBox::title {color:blue;}')
        self.destinationGrid = QtWidgets.QGridLayout(self.chooseDestination)
        self.chooseDestinationLabel = QtWidgets.QLabel("The save destination is:\n"+self.currentSource)
        self.destinationNameLabel = QtWidgets.QLabel("The file name is:")
        self.destinationNameEdit = QtWidgets.QLineEdit(self.defaultFileName)
        self.fileTypeLabel = QtWidgets.QLabel("Type of file is:")
        self.fileType = QtWidgets.QComboBox()
        self.fileType.addItem(".txt",".txt")
        self.fileType.addItem(".xlsx",".xlsx")
        self.profileCentered = QtWidgets.QLabel("Centered?")
        self.centeredCheck = QtWidgets.QCheckBox()
        self.centeredCheck.setChecked(False)
        self.coordinateLabel = QtWidgets.QLabel("Choose coordinate system:")
        self.coordinate = QtWidgets.QButtonGroup()
        self.coordinate.setExclusive(True)
        self.coordinateFrame = QtWidgets.QFrame()
        self.coordnateGrid = QtWidgets.QGridLayout(self.coordinateFrame)
        self.polar = QtWidgets.QCheckBox("Polar")
        self.cartesian = QtWidgets.QCheckBox("Cartesian")
        self.polar.setChecked(True)
        self.coordnateGrid.addWidget(self.polar,0,0)
        self.coordnateGrid.addWidget(self.cartesian,0,1)
        self.coordinate.addButton(self.polar)
        self.coordinate.addButton(self.cartesian)
        self.chooseDestinationButton = QtWidgets.QPushButton("Browse...")
        self.chooseDestinationButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
        self.chooseDestinationButton.clicked.connect(self.Choose_Destination)
        self.destinationGrid.addWidget(self.chooseDestinationLabel,0,0)
        self.destinationGrid.addWidget(self.chooseDestinationButton,0,1)
        self.destinationGrid.addWidget(self.destinationNameLabel,1,0)
        self.destinationGrid.addWidget(self.destinationNameEdit,1,1)
        self.destinationGrid.addWidget(self.fileTypeLabel,2,0)
        self.destinationGrid.addWidget(self.fileType,2,1)
        self.destinationGrid.addWidget(self.coordinateLabel,3,0)
        self.destinationGrid.addWidget(self.coordinateFrame,3,1)
        self.destinationGrid.addWidget(self.profileCentered,4,0)
        self.destinationGrid.addWidget(self.centeredCheck,4,1)
        self.destinationGrid.setAlignment(self.chooseDestinationButton,QtCore.Qt.AlignRight)
        self.parametersBox = QtWidgets.QGroupBox("Choose Image")
        self.parametersBox.setStyleSheet('QGroupBox::title {color:blue;}')
        self.parametersGrid = QtWidgets.QGridLayout(self.parametersBox)
        self.startImageIndexLabel = QtWidgets.QLabel("Start Image Index")
        self.startImageIndexEdit = QtWidgets.QLineEdit(self.startIndex)
        self.endImageIndexLabel = QtWidgets.QLabel("End Image Index")
        self.endImageIndexEdit = QtWidgets.QLineEdit(self.endIndex)
        self.parametersGrid.addWidget(self.startImageIndexLabel,0,0)
        self.parametersGrid.addWidget(self.startImageIndexEdit,0,1)
        self.parametersGrid.addWidget(self.endImageIndexLabel,1,0)
        self.parametersGrid.addWidget(self.endImageIndexEdit,1,1)
        self.plotOptions = QtWidgets.QGroupBox("Contour Plot Options")
        self.plotOptions.setStyleSheet('QGroupBox::title {color:blue;}')
        self.plotOptionsGrid = QtWidgets.QGridLayout(self.plotOptions)
        self.colormapLabel = QtWidgets.QLabel("Colormap")
        self.colormap = QtWidgets.QComboBox()
        self.colormap.addItem("jet","jet")
        self.colormap.addItem("hsv","hsv")
        self.colormap.addItem("rainbow","rainbow")
        self.colormap.addItem("nipy_spectral","nipy_spectral")
        self.levelMinLabel = QtWidgets.QLabel("Level Min ({})".format(self.levelMin/100))
        self.levelMinSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.levelMinSlider.setMinimum(0)
        self.levelMinSlider.setMaximum(100)
        self.levelMinSlider.setValue(self.levelMin)
        self.levelMinSlider.valueChanged.connect(self.Refresh_Level_Min)
        self.levelMaxLabel = QtWidgets.QLabel("Level Max ({})".format(self.levelMax/100))
        self.levelMaxSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.levelMaxSlider.setMinimum(0)
        self.levelMaxSlider.setMaximum(100)
        self.levelMaxSlider.setValue(self.levelMax)
        self.levelMaxSlider.valueChanged.connect(self.Refresh_Level_Max)
        self.radiusMinLabel = QtWidgets.QLabel("Radius Min ({})".format(0.0))
        self.radiusMinSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.radiusMinSlider.setMinimum(0)
        self.radiusMinSlider.setMaximum(1000)
        self.radiusMinSlider.setValue(0)
        self.radiusMinSlider.valueChanged.connect(self.Refresh_Radius_Min)
        self.radiusMaxLabel = QtWidgets.QLabel("Radius Max ({})".format(10.0))
        self.radiusMaxSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.radiusMaxSlider.setMinimum(0)
        self.radiusMaxSlider.setMaximum(1000)
        self.radiusMaxSlider.setValue(1000)
        self.radiusMaxSlider.valueChanged.connect(self.Refresh_Radius_Max)
        self.numberOfContourLevelsLabel = QtWidgets.QLabel("Number of Contour Levels ({})".format(self.numberOfContourLevels))
        self.numberOfContourLevelsLabel.setFixedWidth(160)
        self.numberOfContourLevelsSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.numberOfContourLevelsSlider.setMinimum(5)
        self.numberOfContourLevelsSlider.setMaximum(100)
        self.numberOfContourLevelsSlider.setValue(self.numberOfContourLevels)
        self.numberOfContourLevelsSlider.valueChanged.connect(self.Refresh_Number_Of_Contour_Levels)
        self.plotOptionsGrid.addWidget(self.colormapLabel,0,0)
        self.plotOptionsGrid.addWidget(self.colormap,0,1)
        self.plotOptionsGrid.addWidget(self.levelMinLabel,1,0)
        self.plotOptionsGrid.addWidget(self.levelMinSlider,1,1)
        self.plotOptionsGrid.addWidget(self.levelMaxLabel,2,0)
        self.plotOptionsGrid.addWidget(self.levelMaxSlider,2,1)
        self.plotOptionsGrid.addWidget(self.radiusMinLabel,3,0)
        self.plotOptionsGrid.addWidget(self.radiusMinSlider,3,1)
        self.plotOptionsGrid.addWidget(self.radiusMaxLabel,4,0)
        self.plotOptionsGrid.addWidget(self.radiusMaxSlider,4,1)
        self.plotOptionsGrid.addWidget(self.numberOfContourLevelsLabel,5,0)
        self.plotOptionsGrid.addWidget(self.numberOfContourLevelsSlider,5,1)
        self.statusBar = QtWidgets.QGroupBox("Log")
        self.statusBar.setStyleSheet('QGroupBox::title {color:blue;}')
        self.statusGrid = QtWidgets.QGridLayout(self.statusBar)
        self.statusBar.setFixedHeight(150)
        self.statusBar.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Fixed)
        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setFixedHeight(12)
        self.progressBar.setFixedWidth(500)
        self.progressBar.setVisible(False)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBarSizePolicy = self.progressBar.sizePolicy()
        self.progressBarSizePolicy.setRetainSizeWhenHidden(True)
        self.progressBar.setSizePolicy(self.progressBarSizePolicy)
        self.progressAdvance.connect(self.progress)
        self.progressEnd.connect(self.progressReset)
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
        self.statusGrid.setAlignment(self.progressBar,QtCore.Qt.AlignRight)
        self.ButtonBox = QtWidgets.QDialogButtonBox()
        self.ButtonBox.addButton("Start",QtWidgets.QDialogButtonBox.AcceptRole)
        self.ButtonBox.addButton("Reset",QtWidgets.QDialogButtonBox.ResetRole)
        self.ButtonBox.addButton("Cancel",QtWidgets.QDialogButtonBox.DestructiveRole)
        self.ButtonBox.setCenterButtons(True)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[0].clicked.\
            connect(self.Start)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[1].clicked.\
            connect(self.Reset)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[2].clicked.\
            connect(self.Dialog.reject)
        self.Show3DGraphButton = QtWidgets.QPushButton("Show 3D Graph")
        self.Show3DGraphButton.setEnabled(False)
        self.Show3DGraphButton.clicked.connect(self.Show3DGraphButtonClicked)
        self.Show2DContourButton = QtWidgets.QPushButton("Show 2D Contour")
        self.Show2DContourButton.setEnabled(False)
        self.Show2DContourButton.clicked.connect(self.Show2DContourButtonClicked)
        self.chart = ProfileChart.ProfileChart(self.config)
        self.LeftGrid.addWidget(self.chooseSource,0,0)
        self.LeftGrid.addWidget(self.chooseDestination,1,0)
        self.LeftGrid.addWidget(self.parametersBox,2,0)
        self.LeftGrid.addWidget(self.plotOptions,3,0)
        self.LeftGrid.addWidget(self.ButtonBox,4,0)
        self.LeftGrid.addWidget(self.Show2DContourButton,5,0)
        self.LeftGrid.addWidget(self.Show3DGraphButton,6,0)
        self.RightGrid.addWidget(self.chart,0,0)
        self.RightGrid.addWidget(self.statusBar,1,0)
        self.RightGrid.addWidget(self.progressBar,2,0)
        self.Grid.addWidget(self.LeftFrame,0,0)
        self.Grid.addWidget(self.RightFrame,0,1)
        self.Dialog.setWindowTitle("2D Map")
        self.Dialog.setWindowModality(QtCore.Qt.WindowModal)
        self.Dialog.showNormal()
        self.Dialog.exec_()

    def Show3DGraphButtonClicked(self):
        self.Show3DGraph.emit(self.graphTextPath)

    def Show2DContourButtonClicked(self):
        self.Show2DContour.emit(self.graphTextPath, False, self.levelMinSlider.value()/100,self.levelMaxSlider.value()/100,\
                                self.radiusMinSlider.value()/100,self.radiusMaxSlider.value()/100,self.numberOfContourLevelsSlider.value(),\
                                self.colormap.currentText())

    def Start(self):
        self.StatusRequested.emit()
        self.windowDefault = dict(self.config['windowDefault'].items())
        self.logBox.clear()
        self.Show3DGraphButton.setEnabled(False)
        if self.status["startX"] == "" or self.status["startY"] == "" or self.status["endX"] == "" or \
                self.status["endY"] == "" \
                or self.status["width"] =="": pass
        else:
            self.logBox.append(QtCore.QTime.currentTime().toString("hh:mm:ss")+"\u00A0\u00A0\u00A0\u00A0Ready to Start!")
        image_list = []
        map_2D1=np.array([0,0,0])
        map_2D2=np.array([0,0,0])
        path = os.path.join(self.currentSource,'*.nef')
        autoWB = self.status["autoWB"]
        brightness = self.status["brightness"]
        blackLevel = self.status["blackLevel"]
        VS = int(self.windowDefault["vs"])
        HS = int(self.windowDefault["hs"])
        image_crop = [1200+VS,2650+VS,500+HS,3100+HS]
        scale_factor = self.status["sensitivity"]/np.sqrt(self.status["energy"])
        startIndex = int(self.startImageIndexEdit.text())
        endIndex = int(self.endImageIndexEdit.text())
        saveFileName = self.destinationNameEdit.text()
        fileType = self.fileType.currentData()
        if self.status["startX"] == "" or self.status["startY"] == "" or self.status["endX"] == "" or \
                self.status["endY"] == ""\
            or self.status["width"] =="":
            self.logBox.append(QtCore.QTime.currentTime().toString("hh:mm:ss")+"\u00A0\u00A0\u00A0\u00A0ERROR: Please choose the region!")
            self.Raise_Error("Please choose the region!")
        else:
            start = QtCore.QPointF()
            end = QtCore.QPointF()
            start.setX(self.status["startX"])
            start.setY(self.status["startY"])
            end.setX(self.status["endX"])
            end.setY(self.status["endY"])
            width = self.status["width"]*scale_factor
            for filename in glob.glob(path):
                image_list.append(filename)
            for nimg in range(startIndex,endIndex+1):
                qImg, img = self.getImage(16,image_list[nimg-startIndex],autoWB,brightness,blackLevel,image_crop)
                if width==0.0:
                    RC,I = self.getLineScan(start,end,img,scale_factor)
                    Phi1 = np.full(len(RC),nimg*1.8)
                    Phi2 = np.full(len(RC),nimg*1.8)
                    maxPos = np.argmax(I)
                    for iphi in range(0,maxPos):
                        Phi1[iphi]=nimg*1.8+180
                    if maxPos<(len(RC)-1)/2:
                        x1,y1 = abs(RC[0:(2*maxPos+1)]-RC[maxPos]), I[0:(2*maxPos+1)]/I[maxPos]
                        map_2D1 = np.vstack((map_2D1,np.vstack((x1,Phi1[0:(2*maxPos+1)],y1)).T))
                        x2,y2 = RC[0:(2*maxPos+1)]-RC[maxPos], I[0:(2*maxPos+1)]/I[maxPos]
                        map_2D2 = np.vstack((map_2D2,np.vstack((x2,Phi2[0:(2*maxPos+1)],y2)).T))
                    else:
                        x1,y1 = abs(RC[(2*maxPos-len(RC)-1):-1]-RC[maxPos]), I[(2*maxPos-len(RC)-1):-1]/I[maxPos]
                        map_2D1 = np.vstack((map_2D1,np.vstack((x1,Phi1[(2*maxPos-len(RC)-1):-1],y1)).T))
                        x2,y2 = RC[(2*maxPos-len(RC)-1):-1]-RC[maxPos], I[(2*maxPos-len(RC)-1):-1]/I[maxPos]
                        map_2D2 = np.vstack((map_2D2,np.vstack((x2,Phi2[(2*maxPos-len(RC)-1):-1],y2)).T))
                else:
                    RC,I = self.getIntegral(start,end,width,img,scale_factor)
                    Phi1 = np.full(len(RC),nimg*1.8)
                    Phi2 = np.full(len(RC),nimg*1.8)
                    maxPos = np.argmax(I)
                    for iphi in range(0,maxPos):
                        Phi1[iphi]=nimg*1.8+180
                    if maxPos<(len(RC)-1)/2:
                        x1,y1 = abs(RC[0:(2*maxPos+1)]-RC[maxPos]), I[0:(2*maxPos+1)]/I[maxPos]
                        map_2D1 = np.vstack((map_2D1,np.vstack((x1,Phi1[0:(2*maxPos+1)],y1)).T))
                        x2,y2 = RC[0:(2*maxPos+1)]-RC[maxPos],I[0:(2*maxPos+1)]/I[maxPos]
                        map_2D2 = np.vstack((map_2D2,np.vstack((x2,Phi2[0:(2*maxPos+1)],y2)).T))
                    else:
                        x1,y1 = abs(RC[(2*maxPos-len(RC)-1):-1]-RC[maxPos]), I[(2*maxPos-len(RC)-1):-1]/I[maxPos]
                        map_2D1 = np.vstack((map_2D1,np.vstack((x1,Phi1[(2*maxPos-len(RC)-1):-1],y1)).T))
                        x2,y2 = RC[(2*maxPos-len(RC)-1):-1]-RC[maxPos], I[(2*maxPos-len(RC)-1):-1]/I[maxPos]
                        map_2D2 = np.vstack((map_2D2,np.vstack((x2,Phi2[(2*maxPos-len(RC)-1):-1],y2)).T))
                self.progressAdvance.emit(0,100,(nimg+1-startIndex)*100/(endIndex-startIndex+1))
                self.logBox.append(QtCore.QTime.currentTime().toString("hh:mm:ss")+"\u00A0\u00A0\u00A0\u00A0The file being processed right now is: "+image_list[nimg-startIndex])
                if self.centeredCheck.checkState():
                    self.chart.addChart(x2,y2)
                else:
                    self.chart.addChart(x1,y1)
                QtCore.QCoreApplication.processEvents()
            if self.centeredCheck.checkState():
                map_2D_polar = np.delete(map_2D2,0,0)
            else:
                map_2D_polar = np.delete(map_2D1,0,0)
            map_2D_cart = np.empty(map_2D_polar.shape)
            map_2D_cart[:,2] = map_2D_polar[:,2]
            map_2D_cart[:,0] = map_2D_polar[:,0]*np.cos((map_2D_polar[:,1])*math.pi/180)
            map_2D_cart[:,1] = map_2D_polar[:,0]*np.sin((map_2D_polar[:,1])*math.pi/180)
            self.graphTextPath = self.currentDestination+"/"+saveFileName+fileType
            if self.cartesian.checkState():
                np.savetxt(self.graphTextPath,map_2D_cart,fmt='%4.3f')
            else:
                np.savetxt(self.graphTextPath,map_2D_polar,fmt='%4.3f')
            self.progressEnd.emit()
            self.logBox.append(QtCore.QTime.currentTime().toString("hh:mm:ss")+"\u00A0\u00A0\u00A0\u00A0Completed!")
            self.Raise_Attention("2D Map Completed!")
            self.Show3DGraphButton.setEnabled(True)
            self.Show2DContourButton.setEnabled(True)

    def Reset(self):
        self.levelMin = 0
        self.levelMax = 100
        self.numberOfContourLevels = 5
        self.currentSource = self.path
        self.currentDestination = self.currentSource
        self.levelMinSlider.setValue(self.levelMin)
        self.levelMaxSlider.setValue(self.levelMax)
        self.numberOfContourLevelsSlider.setValue(self.numberOfContourLevels)
        self.colormap.setCurrentText("jet")
        self.chooseSourceLabel.setText("The source directory is:\n"+self.currentSource)
        self.chooseDestinationLabel.setText("The save destination is:\n"+self.currentDestination)
        self.destinationNameEdit.setText(self.defaultFileName)
        self.startImageIndexEdit.setText(self.startIndex)
        self.endImageIndexEdit.setText(self.endIndex)
        self.fileType.setCurrentText(".txt")
        self.polar.setChecked(True)
        self.centeredCheck.setChecked(True)
        self.logBox.clear()
        self.logBox.append(QtCore.QTime.currentTime().toString("hh:mm:ss")+"\u00A0\u00A0\u00A0\u00A0Reset Successful!")
        self.logBox.append(QtCore.QTime.currentTime().toString("hh:mm:ss")+"\u00A0\u00A0\u00A0\u00A0Ready to Start!")

    def Choose_Source(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(None,"choose source directory",self.currentSource,QtWidgets.QFileDialog.ShowDirsOnly)
        self.currentSource = path
        self.chooseSourceLabel.setText("The source directory is:\n"+self.currentSource)

    def Choose_Destination(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(None,"choose save destination",self.currentDestination,QtWidgets.QFileDialog.ShowDirsOnly)
        self.currentDestination = path
        self.chooseDestinationLabel.setText("The save destination is:\n"+self.currentDestination)

    def Refresh_Level_Min(self):
        self.levelMin = self.levelMinSlider.value()
        self.levelMinLabel.setText("Level Min ({})".format(self.levelMin/100))
        if self.levelMinSlider.value() > self.levelMaxSlider.value():
            self.levelMaxSlider.setValue(self.levelMinSlider.value())

    def Refresh_Level_Max(self):
        self.levelMax = self.levelMaxSlider.value()
        self.levelMaxLabel.setText("Level Max ({})".format(self.levelMax/100))
        if self.levelMinSlider.value() > self.levelMaxSlider.value():
            self.levelMinSlider.setValue(self.levelMaxSlider.value())

    def Refresh_Radius_Min(self):
        self.radiusMinLabel.setText("Radius Min ({})".format(self.radiusMinSlider.value()/100))
        if self.radiusMinSlider.value() > self.radiusMaxSlider.value():
            self.radiusMaxSlider.setValue(self.radiusMinSlider.value())

    def Refresh_Radius_Max(self):
        self.radiusMaxLabel.setText("Radius Max ({})".format(self.radiusMaxSlider.value()/100))
        if self.radiusMinSlider.value() > self.radiusMaxSlider.value():
            self.radiusMinSlider.setValue(self.radiusMaxSlider.value())

    def Refresh_Number_Of_Contour_Levels(self):
        self.numberOfContourLevels = self.numberOfContourLevelsSlider.value()
        self.numberOfContourLevelsLabel.setText("Number of Contour Levels ({})".format(self.numberOfContourLevels))

    def Set_Status(self,status):
        self.status = status

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

    def progress(self,min,max,val):
        self.progressBar.setVisible(True)
        self.progressBar.setMinimum(min)
        self.progressBar.setMaximum(max)
        self.progressBar.setValue(val)

    def progressReset(self):
        self.progressBar.reset()
        self.progressBar.setVisible(False)

class Broadening(QtCore.QObject,Process.Image,Process.Fit):

    #Public Signals
    StatusRequested = QtCore.pyqtSignal()
    progressAdvance = QtCore.pyqtSignal(int,int,int)
    progressEnd = QtCore.pyqtSignal()
    connectToCanvas = QtCore.pyqtSignal()
    drawLineRequested = QtCore.pyqtSignal(QtCore.QPointF,QtCore.QPointF,bool)
    drawRectRequested = QtCore.pyqtSignal(QtCore.QPointF,QtCore.QPointF,float,bool)
    color = ['magenta','cyan','darkCyan','darkMagenta','darkRed','darkBlue','darkGray','green','darkGreen','yellow','darkYellow','black']

    def __init__(self):
        super(Broadening,self).__init__()
        self.analysisRegion = [0,0,0,0,0]
        self.config = configparser.ConfigParser()
        self.config.read('./configuration.ini')

    def refresh(self,config):
            self.config = config
            try:
                self.chart.refresh(config)
            except:
                pass

    def Main(self,path):
        self.startIndex = "0"
        self.endIndex = "3"
        self.range = "5"
        self.FTol = '1e-6'
        self.XTol = '1e-4'
        self.GTol = '1e-6'
        self.numberOfSteps = "20"
        self.defaultFileName = "Broadening"
        self.path = os.path.dirname(path)
        self.currentSource = self.path
        self.currentDestination = self.currentSource
        self.Dialog = QtWidgets.QDialog()
        self.Grid = QtWidgets.QGridLayout(self.Dialog)
        self.LeftFrame = QtWidgets.QFrame()
        self.RightFrame = QtWidgets.QFrame()
        self.LeftGrid = QtWidgets.QGridLayout(self.LeftFrame)
        self.RightGrid = QtWidgets.QGridLayout(self.RightFrame)
        self.chooseSource = QtWidgets.QGroupBox("Source Directory")
        self.chooseSource.setStyleSheet('QGroupBox::title {color:blue;}')
        self.sourceGrid = QtWidgets.QGridLayout(self.chooseSource)
        self.sourceGrid.setAlignment(QtCore.Qt.AlignTop)
        self.chooseSourceLabel = QtWidgets.QLabel("The source directory is:\n"+self.currentSource)
        self.chooseSourceButton = QtWidgets.QPushButton("Browse...")
        self.chooseSourceButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
        self.chooseSourceButton.clicked.connect(self.Choose_Source)
        self.sourceGrid.addWidget(self.chooseSourceLabel,0,0)
        self.sourceGrid.addWidget(self.chooseSourceButton,0,1)
        self.chooseDestination = QtWidgets.QGroupBox("Save Destination")
        self.chooseDestination.setStyleSheet('QGroupBox::title {color:blue;}')
        self.destinationGrid = QtWidgets.QGridLayout(self.chooseDestination)
        self.chooseDestinationLabel = QtWidgets.QLabel("The save destination is:\n"+self.currentSource)
        self.destinationNameLabel = QtWidgets.QLabel("The file name is:")
        self.destinationNameEdit = QtWidgets.QLineEdit(self.defaultFileName)
        self.fileTypeLabel = QtWidgets.QLabel("Type of file is:")
        self.fileType = QtWidgets.QComboBox()
        self.fileType.addItem(".txt",".txt")
        self.fileType.addItem(".xlsx",".xlsx")
        self.chooseDestinationButton = QtWidgets.QPushButton("Browse...")
        self.chooseDestinationButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
        self.chooseDestinationButton.clicked.connect(self.Choose_Destination)
        self.destinationGrid.addWidget(self.chooseDestinationLabel,0,0)
        self.destinationGrid.addWidget(self.chooseDestinationButton,0,1)
        self.destinationGrid.addWidget(self.destinationNameLabel,1,0)
        self.destinationGrid.addWidget(self.destinationNameEdit,1,1)
        self.destinationGrid.addWidget(self.fileTypeLabel,2,0)
        self.destinationGrid.addWidget(self.fileType,2,1)
        self.destinationGrid.setAlignment(self.chooseDestinationButton,QtCore.Qt.AlignRight)
        self.parametersBox = QtWidgets.QGroupBox("Choose Image")
        self.parametersBox.setStyleSheet('QGroupBox::title {color:blue;}')
        self.parametersGrid = QtWidgets.QGridLayout(self.parametersBox)
        self.startImageIndexLabel = QtWidgets.QLabel("Start Image Index")
        self.startImageIndexEdit = QtWidgets.QLineEdit(self.startIndex)
        self.endImageIndexLabel = QtWidgets.QLabel("End Image Index")
        self.endImageIndexEdit = QtWidgets.QLineEdit(self.endIndex)
        self.rangeLabel = QtWidgets.QLabel("Range (\u212B\u207B\u00B9)")
        self.rangeEdit = QtWidgets.QLineEdit(self.range)
        self.parametersGrid.addWidget(self.startImageIndexLabel,0,0)
        self.parametersGrid.addWidget(self.startImageIndexEdit,0,1)
        self.parametersGrid.addWidget(self.endImageIndexLabel,1,0)
        self.parametersGrid.addWidget(self.endImageIndexEdit,1,1)
        self.parametersGrid.addWidget(self.rangeLabel,2,0)
        self.parametersGrid.addWidget(self.rangeEdit,2,1)
        self.fitOptions = QtWidgets.QGroupBox("Fit Options")
        self.fitOptions.setStyleSheet('QGroupBox::title {color:blue;}')
        self.fitOptionsGrid = QtWidgets.QGridLayout(self.fitOptions)
        self.numberOfPeaksLabel = QtWidgets.QLabel("Number of Gaussian Peaks")
        self.numberOfPeaksLabel.setFixedWidth(160)
        self.numberOfPeaksCombo = QtWidgets.QComboBox()
        self.numberOfPeaksCombo.addItem('1','1')
        self.numberOfPeaksCombo.addItem('3','3')
        self.numberOfPeaksCombo.addItem('5','5')
        self.numberOfPeaksCombo.addItem('7','7')
        self.numberOfPeaksCombo.addItem('9','9')
        self.numberOfPeaksCombo.addItem('11','11')
        self.numberOfPeaksCombo.currentIndexChanged.connect(self.numberOfPeaksChanged)
        self.includeBG = QtWidgets.QLabel("Include Gaussian Background?")
        self.BGCheck = QtWidgets.QCheckBox()
        self.BGCheck.setChecked(False)
        self.BGCheck.stateChanged.connect(self.BGCheckChanged)
        self.FTolLabel = QtWidgets.QLabel("Cost Function Tolerance")
        self.FTolEdit = QtWidgets.QLineEdit(self.FTol)
        self.XTolLabel = QtWidgets.QLabel("Variable Tolerance")
        self.XTolEdit = QtWidgets.QLineEdit(self.XTol)
        self.GTolLabel = QtWidgets.QLabel("Gradient Tolerance")
        self.GTolEdit = QtWidgets.QLineEdit(self.GTol)
        self.methodLabel = QtWidgets.QLabel("Algorithm")
        self.methodLabel.setFixedWidth(160)
        self.method = QtWidgets.QComboBox()
        self.method.addItem('Trust Region Reflective','trf')
        self.method.addItem('Dogleg','dogbox')
        self.lossLabel = QtWidgets.QLabel("Loss Function")
        self.lossLabel.setFixedWidth(160)
        self.loss = QtWidgets.QComboBox()
        self.loss.addItem('Linear','linear')
        self.loss.addItem('Soft l1','soft_l1')
        self.loss.addItem('Huber','huber')
        self.loss.addItem('Cauchy','cauchy')
        self.loss.addItem('Arctan','arctan')
        self.ManualFitButton = QtWidgets.QPushButton("Manual Fit")
        self.ManualFitButton.clicked.connect(self.ShowManualFit)
        self.offset = LabelSlider(0,1,100,0,'Offset',0,False,'horizontal')
        self.fitOptionsGrid.addWidget(self.numberOfPeaksLabel,0,0)
        self.fitOptionsGrid.addWidget(self.numberOfPeaksCombo,0,1)
        self.fitOptionsGrid.addWidget(self.methodLabel,1,0)
        self.fitOptionsGrid.addWidget(self.method,1,1)
        self.fitOptionsGrid.addWidget(self.lossLabel,2,0)
        self.fitOptionsGrid.addWidget(self.loss,2,1)
        self.fitOptionsGrid.addWidget(self.includeBG,3,0)
        self.fitOptionsGrid.addWidget(self.BGCheck,3,1)
        self.fitOptionsGrid.addWidget(self.offset,4,0,1,2)
        self.fitOptionsGrid.addWidget(self.FTolLabel,5,0)
        self.fitOptionsGrid.addWidget(self.FTolEdit,5,1)
        self.fitOptionsGrid.addWidget(self.XTolLabel,6,0)
        self.fitOptionsGrid.addWidget(self.XTolEdit,6,1)
        self.fitOptionsGrid.addWidget(self.GTolLabel,7,0)
        self.fitOptionsGrid.addWidget(self.GTolEdit,7,1)
        self.fitOptionsGrid.addWidget(self.ManualFitButton,8,0,1,2)
        self.statusBar = QtWidgets.QGroupBox("Log")
        self.statusBar.setStyleSheet('QGroupBox::title {color:blue;}')
        self.statusGrid = QtWidgets.QGridLayout(self.statusBar)
        self.statusBar.setFixedHeight(150)
        self.statusBar.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Fixed)
        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setFixedHeight(12)
        self.progressBar.setFixedWidth(800)
        self.progressBar.setVisible(False)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBarSizePolicy = self.progressBar.sizePolicy()
        self.progressBarSizePolicy.setRetainSizeWhenHidden(True)
        self.progressBar.setSizePolicy(self.progressBarSizePolicy)
        self.progressAdvance.connect(self.progress)
        self.progressEnd.connect(self.progressReset)
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
        self.statusGrid.setAlignment(self.progressBar,QtCore.Qt.AlignRight)
        self.ButtonBox = QtWidgets.QDialogButtonBox()
        self.ButtonBox.addButton("Start",QtWidgets.QDialogButtonBox.AcceptRole)
        self.ButtonBox.addButton("Reset",QtWidgets.QDialogButtonBox.ResetRole)
        self.ButtonBox.addButton("Cancel",QtWidgets.QDialogButtonBox.DestructiveRole)
        self.ButtonBox.setCenterButtons(True)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[0].clicked.\
            connect(self.Start)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[1].clicked.\
            connect(self.Reset)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[2].clicked.\
            connect(self.Dialog.reject)
        self.GenerateReportButton = QtWidgets.QPushButton("Generate Report")
        self.GenerateReportButton.setEnabled(False)
        self.GenerateReportButton.clicked.connect(self.GenerateBroadeningReport)
        self.chartTitle = QtWidgets.QLabel('Profile')
        self.chart = ProfileChart.ProfileChart(self.config)
        self.costChartTitle = QtWidgets.QLabel('Cost Function')
        self.costChart = ProfileChart.ProfileChart(self.config)
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderItem(0,QtWidgets.QTableWidgetItem('C'))
        self.table.setHorizontalHeaderItem(1,QtWidgets.QTableWidgetItem('C_Low'))
        self.table.setHorizontalHeaderItem(2,QtWidgets.QTableWidgetItem('C_High'))
        self.table.setHorizontalHeaderItem(3,QtWidgets.QTableWidgetItem('H'))
        self.table.setHorizontalHeaderItem(4,QtWidgets.QTableWidgetItem('H_Low'))
        self.table.setHorizontalHeaderItem(5,QtWidgets.QTableWidgetItem('H_High'))
        self.table.setHorizontalHeaderItem(6,QtWidgets.QTableWidgetItem('W'))
        self.table.setHorizontalHeaderItem(7,QtWidgets.QTableWidgetItem('W_Low'))
        self.table.setHorizontalHeaderItem(8,QtWidgets.QTableWidgetItem('W_High'))
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.horizontalHeader().setBackgroundRole(QtGui.QPalette.Highlight)
        self.table.setMinimumHeight(200)
        self.table.setRowCount(int(self.numberOfPeaksCombo.currentData()))
        self.Table_Auto_Initilize()
        for i in range(1,int(self.numberOfPeaksCombo.currentData())+1):
            item = QtWidgets.QTableWidgetItem('Peak {}'.format(i))
            item.setForeground(QtGui.QColor(self.color[i-1]))
            self.table.setVerticalHeaderItem(i-1,item)
        self.LeftGrid.addWidget(self.chooseSource,0,0)
        self.LeftGrid.addWidget(self.chooseDestination,1,0)
        self.LeftGrid.addWidget(self.parametersBox,2,0)
        self.LeftGrid.addWidget(self.fitOptions,3,0)
        self.LeftGrid.addWidget(self.ButtonBox,4,0)
        self.LeftGrid.addWidget(self.GenerateReportButton,5,0)
        self.RightGrid.addWidget(self.chartTitle,0,0)
        self.RightGrid.addWidget(self.costChartTitle,0,1)
        self.RightGrid.addWidget(self.chart,1,0)
        self.RightGrid.addWidget(self.costChart,1,1)
        self.RightGrid.addWidget(self.table,2,0,1,2)
        self.RightGrid.addWidget(self.statusBar,3,0,1,2)
        self.RightGrid.addWidget(self.progressBar,4,0,1,2)
        self.Grid.addWidget(self.LeftFrame,0,0)
        self.Grid.addWidget(self.RightFrame,0,1)
        self.Dialog.setWindowTitle("Broadening Analysis")
        self.Dialog.setMinimumHeight(800)
        self.Dialog.setWindowModality(QtCore.Qt.WindowModal)
        self.Dialog.showNormal()
        self.Dialog.exec_()

    def Choose_Source(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(None,"choose source directory",self.currentSource,QtWidgets.QFileDialog.ShowDirsOnly)
        self.currentSource = path
        self.chooseSourceLabel.setText("The source directory is:\n"+self.currentSource)

    def Choose_Destination(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(None,"choose save destination",self.currentDestination,QtWidgets.QFileDialog.ShowDirsOnly)
        self.currentDestination = path
        self.chooseDestinationLabel.setText("The save destination is:\n"+self.currentDestination)

    def Start(self):
        if self.TableIsReady():
            self.StatusRequested.emit()
            self.windowDefault = dict(self.config['windowDefault'].items())
            self.logBox.clear()
            if self.status["startX"] == "" or self.status["startY"] == "" or self.status["endX"] == "" or \
                    self.status["endY"] == "" \
                    or self.status["width"] =="": pass
            else:
                self.logBox.append(QtCore.QTime.currentTime().toString("hh:mm:ss")+"\u00A0\u00A0\u00A0\u00A0Ready to Start!")
            image_list = []
            path = os.path.join(self.currentSource,'*.nef')
            autoWB = self.status["autoWB"]
            brightness = self.status["brightness"]
            blackLevel = self.status["blackLevel"]
            VS = int(self.windowDefault["vs"])
            HS = int(self.windowDefault["hs"])
            image_crop = [1200+VS,2650+VS,500+HS,3100+HS]
            scale_factor = self.status["sensitivity"]/np.sqrt(self.status["energy"])
            startIndex = int(self.startImageIndexEdit.text())
            endIndex = int(self.endImageIndexEdit.text())
            saveFileName = self.destinationNameEdit.text()
            fileType = self.fileType.currentData()
            analysisRange = float(self.rangeEdit.text())
            self.initialparameters = self.initialParameters()
            self.reportPath = self.currentDestination+"/"+saveFileName+fileType
            output = open(self.reportPath,mode='w')
            output.write(QtCore.QDateTime.currentDateTime().toString("MMMM d, yyyy  hh:mm:ss ap")+"\n")
            output.write("The source directory is: "+self.currentSource+"\n")
            index = []
            for index_i in range(1,int(self.numberOfPeaksCombo.currentData())+1):
                index.append(str(index_i))
            if self.BGCheck.checkState():
                index.append('BG')
            information = self.status
            information['AnalysisRange'] = analysisRange
            information['NumberOfPeaks'] = int(self.numberOfPeaksCombo.currentData())
            information['BGCheck'] = self.BGCheck.checkState()
            information['FTol'] = float(self.FTolEdit.text())
            information['XTol'] = float(self.XTolEdit.text())
            information['GTol'] = float(self.GTolEdit.text())
            information['method'] = self.method.currentData()
            information['loss_function'] = self.loss.currentData()
            output.write(str(information))
            output.write('\n\n')
            results_head =str('Phi').ljust(12)+'\t'+str('Kperp').ljust(12)+'\t'+'\t'.join(str(label+i).ljust(12)+'\t'+str(label+i+'_error').ljust(12) for label in ['H','C','W'] for i in index )+'\t'+str('Offset').ljust(12)+'\t'+str('Offset_error').ljust(12)+'\n'
            output.write(results_head)
            if self.status["startX"] == "" or self.status["startY"] == "" or self.status["endX"] == "" or \
                    self.status["endY"] == ""\
                or self.status["width"] =="":
                self.logBox.append(QtCore.QTime.currentTime().toString("hh:mm:ss")+"\u00A0\u00A0\u00A0\u00A0ERROR: Please choose the region!")
                self.Raise_Error("Please choose the region!")
            elif self.status["choosedX"] == "" or self.status["choosedY"] == "":
                self.logBox.append(QtCore.QTime.currentTime().toString("hh:mm:ss")+"\u00A0\u00A0\u00A0\u00A0ERROR: Please choose the origin!")
                self.Raise_Error("Please choose the origin!")
            else:
                self.connectToCanvas.emit()
                start = QtCore.QPointF()
                end = QtCore.QPointF()
                origin = QtCore.QPointF()
                origin.setX(self.status["choosedX"])
                origin.setY(self.status["choosedY"])
                start.setX(self.status["startX"])
                start.setY(self.status["startY"])
                end.setX(self.status["endX"])
                end.setY(self.status["endY"])
                width = self.status["width"]*scale_factor
                for filename in glob.glob(path):
                    image_list.append(filename)
                for nimg in range(startIndex,endIndex+1):
                    self.updateResults(self.initialparameters)
                    self.logBox.append(QtCore.QTime.currentTime().toString("hh:mm:ss")+ \
                                       "\u00A0\u00A0\u00A0\u00A0The file being processed right now is: "+image_list[nimg])
                    qImg, img = self.getImage(16,image_list[nimg],autoWB,brightness,blackLevel,image_crop)
                    x0,y0,x1,y1 = start.x(),start.y(),end.x(),end.y()
                    newStart = QtCore.QPointF()
                    newEnd = QtCore.QPointF()
                    if width==0.0:
                        step = 5
                        nos = int(analysisRange*scale_factor/step)
                    else:
                        nos = int(analysisRange*scale_factor/width)
                        step = width
                    for i in range(1,nos+1):
                        if x0 == x1:
                            newStart.setX(x0+i*step)
                            newStart.setY(y0)
                            newEnd.setX(x1+i*step)
                            newEnd.setY(y1)
                        else:
                            angle = np.arctan((y0-y1)/(x1-x0))
                            newStart.setX(int(x0+i*step*np.sin(angle)))
                            newStart.setY(int(y0+i*step*np.cos(angle)))
                            newEnd.setX(int(x1+i*step*np.sin(angle)))
                            newEnd.setY(int(y1+i*step*np.cos(angle)))
                        if width == 0.0:
                            self.drawLineRequested.emit(newStart,newEnd,False)
                            RC,I = self.getLineScan(newStart,newEnd,img,scale_factor)
                        else:
                            self.drawRectRequested.emit(newStart,newEnd,width,False)
                            RC,I = self.getIntegral(newStart,newEnd,width,img,scale_factor)
                        results, cost = self.getGaussianFit(RC,I,\
                            int(self.numberOfPeaksCombo.currentData()),\
                            self.BGCheck.checkState(),self.guess,(self.bound_low,self.bound_high),float(self.FTolEdit.text()),\
                            float(self.XTolEdit.text()),float(self.GTolEdit.text()),self.method.currentData(),self.loss.currentData())
                        Kperp = (np.abs((newEnd.y()-newStart.y())*origin.x()-(newEnd.x()-newStart.x())*origin.y()+newEnd.x()*newStart.y()-newEnd.y()*newStart.x())/\
                                np.sqrt((newEnd.y()-newStart.y())**2+(newEnd.x()-newStart.x())**2))/scale_factor
                        iteration = np.linspace(1,len(cost)+1,len(cost))
                        jac = results.jac
                        cov = np.linalg.pinv(jac.T.dot(jac))
                        residual_variance = np.sum(results.fun**2)/(len(I)-len(self.guess))
                        var = np.sqrt(np.diagonal(cov*residual_variance))
                        value_variance = np.reshape(np.concatenate((np.array(results.x),np.array(var)),axis=0),(2,len(var)))
                        self.costChart.addChart(iteration,cost,'cost_function')
                        self.updateResults(results.x)
                        if i == 1:
                            self.initialparameters = results.x
                        fitresults =str(nimg*1.8).ljust(12)+'\t'+str(np.round(Kperp,3)).ljust(12)+'\t'+'\t'.join(str(np.round(e[0],3)).ljust(12)+'\t'+str(np.round(e[1],3)).ljust(12) for e in value_variance.T)+'\n'
                        output.write(fitresults)
                        self.logBox.append(QtCore.QTime.currentTime().toString("hh:mm:ss")+ \
                                           "\u00A0\u00A0\u00A0\u00A0MESSAGE:"+results.message)
                        self.plotResults(RC,I)
                        self.progressAdvance.emit(0,100,((nimg-startIndex)*nos+i)*100/nos/(endIndex-startIndex+1))
                self.progressEnd.emit()
                output.close()
                self.logBox.append(QtCore.QTime.currentTime().toString("hh:mm:ss")+"\u00A0\u00A0\u00A0\u00A0Completed!")
                self.Raise_Attention("Broadening Analysis Completed!")
                self.GenerateReportButton.setEnabled(True)

    def initialParameters(self):
        para = []
        for j in [3,0,6]:
            for i in range(self.table.rowCount()):
                para.append(float(self.table.item(i,j).text()))
        para.append(float(self.offset.value()))
        return para

    def updateResults(self,results):
        index=0
        for j in [3,0,6]:
            for i in range(self.table.rowCount()):
                value = np.round(results[index],2)
                item = QtWidgets.QTableWidgetItem('{}'.format(value))
                variation = [0.5,0.5,0.5,0.5,0.5,0.5]
                #Height
                if j == 3:
                    item2 = QtWidgets.QTableWidgetItem('{}'.format(max(0,np.round(value-variation[0],2))))
                    item3 = QtWidgets.QTableWidgetItem('{}'.format(np.round(value+variation[1],2)))
                #Center
                elif j == 0:
                    item2 = QtWidgets.QTableWidgetItem('{}'.format(max(0,np.round(value-variation[2],2))))
                    item3 = QtWidgets.QTableWidgetItem('{}'.format(np.round(value+variation[3],2)))
                #Width
                else:
                    item2 = QtWidgets.QTableWidgetItem('{}'.format(max(0.1,np.round(value-variation[4],2))))
                    item3 = QtWidgets.QTableWidgetItem('{}'.format(np.round(value+variation[5],2)))
                item.setForeground(QtGui.QBrush(QtGui.QColor(QtCore.Qt.red)))
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                item2.setTextAlignment(QtCore.Qt.AlignCenter)
                item3.setTextAlignment(QtCore.Qt.AlignCenter)
                self.table.setItem(i,j,item)
                self.table.setItem(i,j+1,item2)
                self.table.setItem(i,j+2,item3)
                index+=1
        self.offset.setValue(results[-1])

    def plotResults(self,x0,y0):
        self.chart.addChart(x0,y0)
        total = np.full(len(x0),float(self.offset.value()))
        total_min = 100
        for i in range(self.table.rowCount()):
            center = float(self.table.item(i,0).text())
            height = float(self.table.item(i,3).text())
            width = float(self.table.item(i,6).text())
            offset = float(self.offset.value())
            fit = self.gaussian(x0,height,center,width,offset)
            fit0 = self.gaussian(x0,height,center,width,0)
            total = np.add(total,fit0)
            maxH = self.gaussian(center,height,center,width,offset)
            minH1 = self.gaussian(x0[0],height,center,width,offset)
            minH2 = self.gaussian(x0[-1],height,center,width,offset)
            if min(minH1,minH2) < total_min:
                total_min = min(minH1,minH2)
            pen = QtGui.QPen(QtCore.Qt.DotLine)
            pen.setColor(QtGui.QColor(self.color[i]))
            pen.setWidth(2)
            series_fit = QtChart.QLineSeries()
            series_fit.setPen(pen)
            for x,y in zip(x0,fit):
                series_fit.append(x,y)
            self.chart.profileChart.addSeries(series_fit)
            for ax in self.chart.profileChart.axes():
                series_fit.attachAxis(ax)
            self.chart.profileChart.axisY().setRange(min(minH1,minH2,min(y0)),max(maxH,max(y0)))
        pen = QtGui.QPen(QtCore.Qt.DotLine)
        pen.setColor(QtGui.QColor('red'))
        pen.setWidth(2)
        series_total = QtChart.QLineSeries()
        series_total.setPen(pen)
        for x,y in zip(x0,total):
            series_total.append(x,y)
        self.chart.profileChart.addSeries(series_total)
        for ax in self.chart.profileChart.axes():
            series_total.attachAxis(ax)
        self.chart.profileChart.axisY().setRange(min(total[0],total[-1],np.amin(y0),total_min),max(np.amax(total),np.amax(y0)))
        QtCore.QCoreApplication.processEvents()

    def Reset(self):
        self.currentSource = self.path
        self.currentDestination = self.currentSource
        self.numberOfPeaksCombo.setCurrentText('1')
        self.chooseSourceLabel.setText("The source directory is:\n"+self.currentSource)
        self.chooseDestinationLabel.setText("The save destination is:\n"+self.currentDestination)
        self.destinationNameEdit.setText(self.defaultFileName)
        self.startImageIndexEdit.setText(self.startIndex)
        self.endImageIndexEdit.setText(self.endIndex)
        self.fileType.setCurrentText(".txt")
        self.logBox.clear()
        self.logBox.append(QtCore.QTime.currentTime().toString("hh:mm:ss")+"\u00A0\u00A0\u00A0\u00A0Reset Successful!")
        self.logBox.append(QtCore.QTime.currentTime().toString("hh:mm:ss")+"\u00A0\u00A0\u00A0\u00A0Ready to Start!")

    def Table_Auto_Initilize(self):
        self.table.disconnect()
        for r in range(0,self.table.rowCount()):
            valueList = ['1','0','5','1','0','5','1','0','5']
            for c in range(0,self.table.columnCount()):
                item = QtWidgets.QTableWidgetItem(valueList[c])
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                if c == 0 or c == 3 or c == 6:
                    item.setForeground(QtGui.QBrush(QtGui.QColor(QtCore.Qt.red)))
                self.table.setItem(r,c,item)
        self.SaveTableContents()
        self.table.cellChanged.connect(self.SaveTableContents)

    def TableIsReady(self):
        B = True
        for j in [3,0,6]:
            for i in range(self.table.rowCount()):
                if not (float(self.table.item(i,j).text()) >= float(self.table.item(i,j+1).text()) \
                        and float(self.table.item(i,j).text()) <= float(self.table.item(i,j+2).text())):
                    self.Raise_Error('Wrong table entry at cell ({},{})'.format(i,j))
                    B = False
        return B

    def SaveTableContents(self,row=0,column=0):
        self.guess = []
        self.bound_low = []
        self.bound_high = []
        for j in [3,0,6]:
            for i in range(self.table.rowCount()):
                self.guess.append(float(self.table.item(i,j).text()))
        for j in [4,1,7]:
            for i in range(self.table.rowCount()):
                self.bound_low.append(float(self.table.item(i,j).text()))
        for j in [5,2,8]:
            for i in range(self.table.rowCount()):
                self.bound_high.append(float(self.table.item(i,j).text()))
        self.guess.append(float(self.offset.value()))
        self.bound_low.append(0)
        self.bound_high.append(1)

    def numberOfPeaksChanged(self):
        self.table.setRowCount(int(self.numberOfPeaksCombo.currentData()))
        for i in range(1,int(self.numberOfPeaksCombo.currentData())+1):
            item = QtWidgets.QTableWidgetItem('Peak {}'.format(i))
            item.setForeground(QtGui.QColor(self.color[i-1]))
            self.table.setVerticalHeaderItem(i-1,item)
        if self.BGCheck.checkState() == 2:
            self.table.setRowCount(self.table.rowCount()+1)
            item = QtWidgets.QTableWidgetItem('BG')
            item.setForeground(QtGui.QColor(self.color[self.table.rowCount()-1]))
            self.table.setVerticalHeaderItem(self.table.rowCount()-1,item)
        self.Table_Auto_Initilize()

    def BGCheckChanged(self,state):
        if state == 2:
            self.table.setRowCount(self.table.rowCount()+1)
            item = QtWidgets.QTableWidgetItem('BG')
            item.setForeground(QtGui.QColor(self.color[self.table.rowCount()-1]))
            self.table.setVerticalHeaderItem(self.table.rowCount()-1,item)
        elif state == 0:
            self.table.removeRow(self.table.rowCount()-1)
        self.Table_Auto_Initilize()


    def GenerateBroadeningReport(self):
        report = GenerateReport()
        report.Main(self.reportPath,True)

    def ShowManualFit(self):
        self.StatusRequested.emit()
        window = ManualFit()
        window.FitSatisfied.connect(self.updateResults)
        window.Set_Status(self.status)
        path = os.path.join(self.currentSource,'*.nef')
        startIndex = int(self.startImageIndexEdit.text())
        image_list = []
        for filename in glob.glob(path):
            image_list.append(filename)
        window.Main(image_list[startIndex],self.table.rowCount(),self.BGCheck.checkState())

    def Set_Status(self,status):
        self.status = status

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

    def progress(self,min,max,val):
        self.progressBar.setVisible(True)
        self.progressBar.setMinimum(min)
        self.progressBar.setMaximum(max)
        self.progressBar.setValue(val)

    def progressReset(self):
        self.progressBar.reset()
        self.progressBar.setVisible(False)

class ManualFit(QtCore.QObject,Process.Image,Process.Fit):

    StatusRequested = QtCore.pyqtSignal()
    FitSatisfied = QtCore.pyqtSignal(list)
    color = ['magenta','cyan','darkCyan','darkMagenta','darkRed','darkBlue','darkGray','green','darkGreen','yellow','darkYellow','black']

    def __init__(self):
        super(ManualFit,self).__init__()
        self.config = configparser.ConfigParser()
        self.config.read('./configuration.ini')

    def Set_Status(self,status):
        self.status = status

    def getInput(self):
        items = ['1','1+BG','3','3+BG','5','5+BG','7','7+BG','9','9+BG','11','11+BG']
        return QtWidgets.QInputDialog.getItem(None,'Input','Choose the Number of Peaks',items,0,False)

    def Main(self,path,nop=1,BG=False):
        if nop == 0:
            text, OK = self.getInput()
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
        self.StatusRequested.emit()
        self.initialGuess = ['1','0.1','1','0.5']
        if os.path.isdir(path):
            self.path = os.path.join(path,'*.nef')
        elif os.path.isfile(path):
            self.path = path
        else:
            self.Raise_Error('Please open a pattern!')
            return
        self.Dialog = QtWidgets.QDialog()
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
                        slider = LabelSlider(minimum,self.RC[-1],100,value,name,index,self.BG,'vertical',self.color[i-1])
                    elif name == 'H':
                        slider = LabelSlider(minimum,5,100,value,name,index,self.BG,'vertical',self.color[i-1])
                    elif name =='C':
                        slider = LabelSlider(minimum,maximum,100,self.RC[-1]/2,name,index,self.BG,'vertical',self.color[i-1])
                else:
                    slider = LabelSlider(minimum,maximum,100,value,name,index,False,'vertical',self.color[i-1])
                slider.valueChanged.connect(self.updateGuess)
                parametersVLayout.addWidget(slider)
            self.parametersHLayout.addLayout(parametersVLayout)
        self.OffsetSlider = LabelSlider(0,1,100,(self.I[0]+self.I[-1])/2,'O',0)
        self.OffsetSlider.valueChanged.connect(self.updateGuess)
        self.parametersHLayout.addWidget(self.OffsetSlider)

        self.AcceptButton = QtWidgets.QPushButton("Accept")
        self.AcceptButton.clicked.connect(self.Accept)
        self.FitChartTitle = QtWidgets.QLabel('Profile')
        self.FitChart = ProfileChart.ProfileChart(self.config)
        self.FitChart.addChart(self.RC,self.I)
        self.FitChart.profileChart.setMinimumWidth(650)
        self.updateGuess()

        self.LeftGrid.addWidget(self.parameters,0,0)
        self.LeftGrid.addWidget(self.AcceptButton,1,0)
        self.RightGrid.addWidget(self.FitChartTitle,0,0)
        self.RightGrid.addWidget(self.FitChart,1,0)
        self.Grid.addWidget(self.LeftFrame,0,0)
        self.Grid.addWidget(self.RightFrame,0,1)

        self.Dialog.setWindowTitle("Manual Fit")
        self.Dialog.setMinimumHeight(600)
        self.Dialog.setWindowModality(QtCore.Qt.WindowModal)
        self.Dialog.showNormal()
        self.Dialog.exec_()

    def Accept(self):
        self.Dialog.reject()
        results = self.flatten(self.guess)
        results.append(float(self.OffsetSlider.value()))
        self.FitSatisfied.emit(results)

    def flatten(self,input):
        new_list=[]
        for i in [1,0,2]:
            for j in range(len(input)):
                new_list.append(float(input[j][i]))
        return new_list

    def updateGuess(self):
        guess = []
        for VLayout in self.parametersHLayout.children():
            row = []
            for i in range(VLayout.count()):
                row.append(VLayout.itemAt(i).widget().value())
            guess.append(row)
        self.guess = guess
        self.plotResults(self.RC,self.guess)

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
            self.Raise_Error("Please choose the region!")
        else:
            start = QtCore.QPointF()
            end = QtCore.QPointF()
            start.setX(self.status["startX"])
            start.setY(self.status["startY"])
            end.setX(self.status["endX"])
            end.setY(self.status["endY"])
            width = self.status["width"]*scale_factor
            qImg, img = self.getImage(16,image_list[0],autoWB,brightness,blackLevel,image_crop)
            if width == 0.0:
                RC,I = self.getLineScan(start,end,img,scale_factor)
            else:
                RC,I = self.getIntegral(start,end,width,img,scale_factor)
            return RC,I

    def plotResults(self,x0,guess):
        if len(self.FitChart.profileChart.series())>1:
            for series in self.FitChart.profileChart.series()[1:]:
                self.FitChart.profileChart.removeSeries(series)
        total = np.full(len(x0),float(self.OffsetSlider.value()))
        total_min = 100
        for i in range(len(guess)):
            center = float(guess[i][0])
            height = float(guess[i][1])
            width = float(guess[i][2])
            offset = float(self.OffsetSlider.value())
            fit = self.gaussian(x0,height,center,width,offset)
            fit0 = self.gaussian(x0,height,center,width,0)
            total = np.add(total,fit0)
            maxH = self.gaussian(center,height,center,width,offset)
            minH1 = self.gaussian(x0[0],height,center,width,offset)
            minH2 = self.gaussian(x0[-1],height,center,width,offset)
            if min(minH1,minH2) < total_min:
                total_min = min(minH1,minH2)
            pen = QtGui.QPen(QtCore.Qt.DotLine)
            pen.setColor(QtGui.QColor(self.color[i]))
            pen.setWidth(2)
            self.series_fit = QtChart.QLineSeries()
            self.series_fit.setPen(pen)
            for x,y in zip(x0,fit):
                self.series_fit.append(x,y)
            self.FitChart.profileChart.addSeries(self.series_fit)
            for ax in self.FitChart.profileChart.axes():
                self.series_fit.attachAxis(ax)
            self.FitChart.profileChart.axisY().setRange(min(minH1,minH2,self.minIntensity),max(maxH,self.maxIntensity))
        pen = QtGui.QPen(QtCore.Qt.DotLine)
        pen.setColor(QtGui.QColor('red'))
        pen.setWidth(2)
        series_total = QtChart.QLineSeries()
        series_total.setPen(pen)
        for x,y in zip(x0,total):
            series_total.append(x,y)
        self.FitChart.profileChart.addSeries(series_total)
        for ax in self.FitChart.profileChart.axes():
            series_total.attachAxis(ax)
        self.FitChart.profileChart.axisY().setRange(min(total[0],total[-1],self.minIntensity,total_min),max(np.amax(total),self.maxIntensity))

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

class DoubleSlider(QtWidgets.QWidget):
    valueChanged = QtCore.pyqtSignal(float,float)

    def __init__(self,minimum,maximum,scale,head,tail,text,unit,direction='horizontal'):
        super(DoubleSlider,self).__init__()
        self.currentMin, self.currentMax = int(head/scale),int(tail/scale)
        self.text = text
        self.scale = scale
        self.unit = unit
        self.minLabel = QtWidgets.QLabel(self.text+"_min = {:5.2f} ".format(self.currentMin*self.scale)+"("+unit+")")
        self.minLabel.setFixedWidth(180)
        self.minSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.minSlider.setFixedWidth(300)
        self.minSlider.setMinimum(minimum)
        self.minSlider.setMaximum(maximum)
        self.minSlider.setValue(self.currentMin)
        self.minSlider.valueChanged.connect(self.minChanged)

        self.maxLabel = QtWidgets.QLabel(self.text+"_max = {:5.2f} ".format(self.currentMax*self.scale)+"("+unit+")")
        self.maxLabel.setFixedWidth(180)
        self.maxSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.maxSlider.setFixedWidth(300)
        self.maxSlider.setMinimum(minimum)
        self.maxSlider.setMaximum(maximum)
        self.maxSlider.setValue(self.currentMax)
        self.maxSlider.valueChanged.connect(self.maxChanged)

        self.UIgrid = QtWidgets.QGridLayout()
        self.UIgrid.addWidget(self.minLabel,0,0)
        self.UIgrid.addWidget(self.minSlider,0,1)
        self.UIgrid.addWidget(self.maxLabel,1,0)
        self.UIgrid.addWidget(self.maxSlider,1,1)
        self.UIgrid.setContentsMargins(0,0,0,0)
        self.setLayout(self.UIgrid)

    def setHead(self,value):
        self.minSlider.setValue(int(value/self.scale))

    def setTail(self,value):
        self.maxSlider.setValue(int(value/self.scale))

    def values(self):
        return self.currentMin*self.scale, self.currentMax*self.scale

    def minChanged(self):
        self.currentMin = self.minSlider.value()
        if self.currentMin > self.currentMax:
            self.maxSlider.setValue(self.currentMin)
        self.minLabel.setText(self.text+"_min = {:5.2f} ".format(self.currentMin*self.scale)+"("+self.unit+")")
        self.valueChanged.emit(self.currentMin*self.scale, self.currentMax*self.scale)

    def maxChanged(self):
        self.currentMax = self.maxSlider.value()
        if self.currentMin > self.currentMax:
            self.minSlider.setValue(self.currentMax)
        self.maxLabel.setText(self.text+"_max = {:5.2f} ".format(self.currentMax*self.scale)+"("+self.unit+")")
        self.valueChanged.emit(self.currentMin*self.scale, self.currentMax*self.scale)

    def setEnabled(self,enable):
        self.minSlider.setEnabled(enable)
        self.maxSlider.setEnabled(enable)

class LabelSlider(QtWidgets.QWidget):
    valueChanged = QtCore.pyqtSignal()
    def __init__(self,minimum,maximum,scale,value,name,index,BG=False,direction='vertical',color='black'):
        super(LabelSlider,self).__init__()
        self.name = name
        self.scale = scale
        self.index = index
        self.BG = BG
        self.currentValue = value
        self.direction = direction
        if direction == 'vertical':
            self.slider = QtWidgets.QSlider(QtCore.Qt.Vertical)
        elif direction == 'horizontal':
            self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setMinimum(minimum*scale)
        self.slider.setMaximum(maximum*scale)
        self.slider.setValue(value*self.scale)
        self.slider.valueChanged.connect(self.updateLabel)

        self.UIgrid = QtWidgets.QGridLayout()
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Window, QtCore.Qt.transparent)
        palette.setColor(QtGui.QPalette.WindowText,QtGui.QColor(color))
        if direction == 'vertical':
            if self.BG:
                self.label = QtWidgets.QLabel('\u00A0\u00A0'+self.name+'\u00A0BG\n({:3.2f})'.format(value))
            else:
                self.label = QtWidgets.QLabel('\u00A0\u00A0'+self.name+'{}\n({:3.2f})'.format(self.index,value))
            self.label.setFixedWidth(35)
            self.UIgrid.addWidget(self.slider,0,0)
            self.UIgrid.addWidget(self.label,1,0)
        elif direction == 'horizontal':
            self.label = QtWidgets.QLabel(self.name+'\u00A0({:3.2f})'.format(value))
            self.UIgrid.addWidget(self.label,0,0)
            self.UIgrid.addWidget(self.slider,0,1)
        self.label.setAutoFillBackground(True)
        self.label.setPalette(palette)
        self.UIgrid.setContentsMargins(0,0,0,0)
        self.setLayout(self.UIgrid)

    def value(self):
        return str(self.currentValue)

    def setValue(self,value):
        self.slider.setValue(value*self.scale)

    def updateLabel(self,value):
        self.currentValue = value/self.scale
        if self.direction == 'vertical':
            if self.BG:
                self.label.setText('\u00A0\u00A0'+self.name+'\u00A0BG\n({:3.2f})'.format(self.currentValue))
            else:
                self.label.setText('\u00A0\u00A0'+self.name+'{}\n({:3.2f})'.format(self.index,self.currentValue))
        elif self.direction == 'horizontal':
            self.label.setText(self.name+'\u00A0({:3.2f})'.format(self.currentValue))
        self.valueChanged.emit()

class GenerateReport(QtCore.QObject):

    StatusRequested = QtCore.pyqtSignal()

    def __init__(self):
        super(GenerateReport,self).__init__()
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
        self.Dialog = QtWidgets.QDialog()
        self.Grid = QtWidgets.QGridLayout(self.Dialog)
        self.LeftFrame = QtWidgets.QFrame()
        self.LeftGrid = QtWidgets.QGridLayout(self.LeftFrame)

        self.chooseSource = QtWidgets.QGroupBox("Choose the Report File")
        self.chooseSource.setStyleSheet('QGroupBox::title {color:blue;}')
        self.chooseSource.setMinimumHeight(100)
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
        self.ReportInformation = QtWidgets.QLabel("Number of peaks:\nDate of the report:\nStart image index:\nEnd image index:\nStart Kperp position:\nEnd Kperp position:\nKperp step size:")
        self.ReportInformationGrid.addWidget(self.ReportInformation)

        self.typeOfReportBox = QtWidgets.QGroupBox("Type of the Report to Be Generated")
        self.typeOfReportBox.setStyleSheet('QGroupBox::title {color:blue;}')
        self.typeOfReportGrid = QtWidgets.QGridLayout(self.typeOfReportBox)
        self.type = QtWidgets.QButtonGroup()
        self.type.setExclusive(False)
        self.typeFrame = QtWidgets.QFrame()
        self.typeGrid = QtWidgets.QGridLayout(self.typeFrame)
        self.IA = QtWidgets.QCheckBox("Intensity vs Azimuth")
        self.FA = QtWidgets.QCheckBox("FWHM vs Azimuth")
        self.IK = QtWidgets.QCheckBox("Intensity vs Kperp")
        self.FK = QtWidgets.QCheckBox("FWHM vs Kperp")
        self.typeGrid.addWidget(self.IA,0,0)
        self.typeGrid.addWidget(self.FA,1,0)
        self.typeGrid.addWidget(self.IK,2,0)
        self.typeGrid.addWidget(self.FK,3,0)
        self.type.addButton(self.IA)
        self.type.addButton(self.FA)
        self.type.addButton(self.IK)
        self.type.addButton(self.FK)
        self.typeOfReportGrid.addWidget(self.typeFrame,0,0)

        self.optionBox = QtWidgets.QGroupBox("Plot Options")
        self.optionBox.setStyleSheet('QGroupBox::title {color:blue;}')
        self.optionGrid = QtWidgets.QGridLayout(self.optionBox)
        self.peakLabel = QtWidgets.QLabel("Choose the peak to be analyzed:")
        self.peak = QtWidgets.QComboBox()
        self.peak.addItem('Center','0')
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
        self.FWHMRangeSlider = DoubleSlider(minimum=0,maximum=200,scale=0.01,head=0,tail=1,text="FWHM",unit='\u212B\u207B\u00B9')
        self.FWHMRangeSlider.setEnabled(False)

        self.optionGrid.addWidget(self.peakLabel,0,0)
        self.optionGrid.addWidget(self.peak,0,1)
        self.optionGrid.addWidget(self.KperpLabel,1,0,1,2)
        self.optionGrid.addWidget(self.KperpSlider,2,0,1,2)
        self.optionGrid.addWidget(self.AzimuthLabel,3,0,1,2)
        self.optionGrid.addWidget(self.AzimuthSlider,4,0,1,2)
        self.optionGrid.addWidget(self.intensityRangeSlider,5,0,1,2)
        self.optionGrid.addWidget(self.FWHMRangeSlider,6,0,1,2)

        self.statusBar = QtWidgets.QGroupBox("Log")
        self.statusBar.setStyleSheet('QGroupBox::title {color:blue;}')
        self.statusGrid = QtWidgets.QGridLayout(self.statusBar)
        self.statusBar.setFixedHeight(150)
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
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[0].clicked.\
            connect(self.Start)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[1].clicked.\
            connect(self.Dialog.reject)

        self.LeftGrid.addWidget(self.chooseSource,0,0,1,2)
        self.LeftGrid.addWidget(self.ReportInformationBox,1,0)
        self.LeftGrid.addWidget(self.typeOfReportBox,1,1)
        self.LeftGrid.addWidget(self.optionBox,3,0,1,2)
        self.LeftGrid.addWidget(self.statusBar,4,0,1,2)
        self.LeftGrid.addWidget(self.ButtonBox,5,0,1,2)
        self.Grid.addWidget(self.LeftFrame,0,0)

        self.IA.stateChanged.connect(self.IACheckChanged)
        self.FA.stateChanged.connect(self.FACheckChanged)
        self.IK.stateChanged.connect(self.IKCheckChanged)
        self.FK.stateChanged.connect(self.FKCheckChanged)
        self.IA.setChecked(True)

        if preload:
            self.loadReport(self.path)

        self.Dialog.setWindowTitle("Generate Report")
        self.Dialog.setWindowModality(QtCore.Qt.WindowModal)
        self.Dialog.showNormal()
        self.Dialog.exec_()

    def updateLog(self,msg):
        self.logBox.append(QtCore.QTime.currentTime().toString("hh:mm:ss")+"\u00A0\u00A0\u00A0\u00A0"+msg)

    def Choose_Source(self):
        path = QtWidgets.QFileDialog.getOpenFileName(None,"Choose The Report File",self.path)
        self.path = path[0]
        self.pathExtension = os.path.splitext(self.path)[1]
        if not self.pathExtension == ".txt":
            self.Raise_Error('[Error: wrong file type] Please choose a *.txt file')
            self.updateLog('[Error: wrong file type] Please choose a *.txt file')
        else:
            self.chooseSourceLabel.setText("The path of the report is:\n"+self.path)
        self.loadReport(self.path)

    def Start(self):
        Kp = self.currentKP/self.KperpSliderScale+self.RangeStart
        Az = self.currentAzimuth*1.8+self.AzimuthStart
        if self.IA.checkState() == 2:
            I, A, Ierror = self.getIA()
            self.IAPlot(I,A,Kp,self.intensityRangeSlider.values()[0],self.intensityRangeSlider.values()[1])
        if self.IK.checkState() == 2:
            I, K, Ierror = self.getIK()
            self.IKPlot(I,K,Az)
        if self.FA.checkState() == 2:
            F, A, Ferror = self.getFA()
            self.FAPlot(F,A,Kp,self.FWHMRangeSlider.values()[0],self.FWHMRangeSlider.values()[1])
        if self.FK.checkState() == 2:
            F, K, Ferror = self.getFK()
            self.FKPlot(F,K,Az)
        plt.show()

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
        F = np.fromiter((self.report[i,columnF] for i in rows.tolist()),float)
        Ferror = np.fromiter((self.report[i,columnFerror] for i in rows.tolist()),float)
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
        F = np.fromiter((self.report[i,columnF] for i in rows.tolist()),float)
        Ferror = np.fromiter((self.report[i,columnFerror] for i in rows.tolist()),float)
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

    def IAPlot(self,I,A,Kp,imin,imax):
        A2 = A + np.full(len(A),180)
        Phi = np.append(A,A2)
        Heights = np.append(I,I)/np.amax(I)
        fig = plt.figure()
        ax = plt.subplot(projection='polar')
        ax.set_title('Intensity vs Azimuth at Kperp = {}'.format(Kp),fontsize=20)
        ax.scatter(Phi*np.pi/180,Heights,c='b')
        ax.set_rmin(imin)
        ax.set_rmax(imax)
        ax.set_rticks(np.around(np.linspace(imin,imax,5),1))

    def IKPlot(self,I,K,Az):
        fig = plt.figure()
        ax = plt.subplot()
        ax.set_title('Intensity vs Kperp at Phi = {}\u00B0'.format(Az),fontsize=20)
        ax.plot(K,I,c='b')
        ax.set_ylabel('Intensity (arb. units)',fontsize = 20)
        ax.set_xlabel(r'$K_{perp}$ $(\AA^{-1})$',fontsize = 20)

    def FAPlot(self,F,A,Kp,fmin,fmax):
        A2 = A + np.full(len(A),180)
        Phi = np.append(A,A2)
        FWHMs = np.append(F,F)/np.amax(F)
        fig = plt.figure()
        ax = plt.subplot(projection='polar')
        ax.set_title('FWHM vs Azimuth at Kperp = {}'.format(Kp),fontsize=20)
        ax.scatter(Phi*np.pi/180,FWHMs,c='b')
        ax.set_rmin(fmin)
        ax.set_rmax(fmax)
        ax.set_rticks(np.around(np.linspace(fmin,fmax,5),1))

    def FKPlot(self,F,K,Az):
        fig = plt.figure()
        ax = plt.subplot()
        ax.set_title('FWHM vs Kperp at Phi = {}\u00B0'.format(Az),fontsize=20)
        ax.plot(K,F,c='b')
        ax.set_ylabel(r'FWHM $(\AA^{-1})$',fontsize = 20)
        ax.set_xlabel(r'$K_{perp}$ $(\AA^{-1})$',fontsize = 20)

    def AzimuthChanged(self):
        self.currentAzimuth = self.AzimuthSlider.value()
        self.AzimuthLabel.setText("Azimuth Angle = {:5.1f} (\u00B0)".format(self.currentAzimuth*1.8+self.AzimuthStart))

    def KPChanged(self):
        self.currentKP = self.KperpSlider.value()
        self.KperpLabel.setText("Kperp = {:6.2f} (\u212B\u207B\u00B9)".format(self.currentKP/self.KperpSliderScale+self.RangeStart))

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
            self.FWHMRangeSlider.setEnabled(False)
            if self.IA.checkState() == 0:
                self.KperpSlider.setEnabled(False)
        else:
            self.KperpSlider.setEnabled(True)
            self.FWHMRangeSlider.setEnabled(True)
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
