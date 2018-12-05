from PyQt5 import QtCore, QtWidgets
import numpy as np
import os
import glob
import configparser
import Process
import math
import ProfileChart

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
        DefaultSettings_DialogGrid = QtWidgets.QGridLayout(self.DefaultSettings_Dialog)
        tab = QtWidgets.QTabWidget()
        buttonBox = QtWidgets.QDialogButtonBox()
        self.window = QtWidgets.QWidget()
        self.properties = QtWidgets.QWidget()
        self.canvas = QtWidgets.QWidget()
        self.chart = QtWidgets.QWidget()
        windowGrid = QtWidgets.QGridLayout(self.window)
        windowMode = [('Horizontal Shift (px)',self.windowDefault['hs'],0,0,1),\
                      ('Vertical Shift (px)',self.windowDefault['vs'],1,0,1),\
                      ('Energy (keV)',self.windowDefault['energy'],2,0,1),\
                      ('Azimuth (\u00B0)',self.windowDefault['azimuth'],3,0,1),\
                      ('Scale Bar Length (\u212B\u207B\u00B9)',self.windowDefault['scalebarlength'],4,0,1),\
                      ('Chi Range (\u00B0)',self.windowDefault['chirange'],5,0,1),\
                      ('Integral Half Width (\u212B\u207B\u00B9)',self.windowDefault['width'],6,0,1),\
                      ('Integral Half Width Slider Scale',self.windowDefault['widthsliderscale'],7,0,1),\
                      ('Radius (\u212B\u207B\u00B9)',self.windowDefault['radius'],8,0,1),\
                      ('Radius Maximum (\u212B\u207B\u00B9)',self.windowDefault['radiusmaximum'],9,0,1),\
                      ('Radius Slider Scale',self.windowDefault['radiussliderscale'],10,0,1),\
                      ('Tilt Angle (\u00B0)',self.windowDefault['tiltangle'],11,0,1),\
                      ('Tilt Angle Slider Scale',self.windowDefault['tiltanglesliderscale'],12,0,1)]
        propertiesGrid = QtWidgets.QGridLayout(self.properties)
        propertiesMode = [('Sensitivity (pixel/sqrt[keV])',self.propertiesDefault['sensitivity'],0,0,3),\
                          ('Electron Energy (keV)',self.propertiesDefault['electronenergy'],1,0,3),\
                          ('Azimuth (\u00B0)',self.propertiesDefault['azimuth'],2,0,3),\
                          ('Scale Bar Length (\u212B\u207B\u00B9)',self.propertiesDefault['scalebarlength'],3,0,3),\
                          (',',self.propertiesDefault['brightness'],4,1,1),\
                          ('Brightness (Minimum,Default,Maximum)',self.propertiesDefault['brightnessminimum'],4,0,1),\
                          (',',self.propertiesDefault['brightnessmaximum'],4,2,1),\
                          (',',self.propertiesDefault['blacklevel'],5,1,1),\
                          ('Black Level (Minimum,Default,Maximum)',self.propertiesDefault['blacklevelminimum'],5,0,1),\
                          (',',self.propertiesDefault['blacklevelmaximum'],5,2,1),\
                          (',',self.propertiesDefault['integralhalfwidth'],6,1,1),\
                          ('Half Width (\u212B\u207B\u00B9) (Minimum,Default,Maximum)',self.propertiesDefault['widthminimum'],6,0,1),\
                          (',',self.propertiesDefault['widthmaximum'],6,2,1),\
                          ('Slider Scales (Half Width,Radius,Tilt Angle)',self.propertiesDefault['widthsliderscale'],10,0,1),\
                          (',',self.propertiesDefault['chirange'],7,1,1),\
                          ('Chi Range (\u00B0) (Minimum,Default,Maximum)',self.propertiesDefault['chirangeminimum'],7,0,1),\
                          (',',self.propertiesDefault['chirangemaximum'],7,2,1),\
                          (',',self.propertiesDefault['radius'],8,1,1),\
                          ('Radius (\u212B\u207B\u00B9) (Minimum,Default,Maximum)',self.propertiesDefault['radiusminimum'],8,0,1),\
                          (',',self.propertiesDefault['radiusmaximum'],8,2,1),\
                          (',',self.propertiesDefault['radiussliderscale'],10,1,1),\
                          (',',self.propertiesDefault['tiltangle'],9,1,1),\
                          ('Tilt Angle (\u00B0) (Minimum,Default,Maximum)',self.propertiesDefault['tiltangleminimum'],9,0,1),\
                          (',',self.propertiesDefault['tiltanglemaximum'],9,2,1),\
                          (',',self.propertiesDefault['tiltanglesliderscale'],10,2,1)]
        canvasGrid = QtWidgets.QGridLayout(self.canvas)
        canvasMode = [('Integral Half Width',self.canvasDefault['widthinangstrom'],0,0,1),\
                      ('Radius Maximum',self.canvasDefault['radiusmaximum'],1,0,1),\
                      ('Span',self.canvasDefault['span'],2,0,1),\
                      ('Tilt',self.canvasDefault['tilt'],3,0,1),\
                      ('Maximum Zoom Factor',self.canvasDefault['max_zoom_factor'],4,0,1)]
        chartGrid = QtWidgets.QGridLayout(self.chart)
        chartMode = [('Theme',self.chartDefault['theme'],0,0,1)]
        PageMode = [(windowGrid,windowMode),(propertiesGrid,propertiesMode),(canvasGrid,canvasMode),(chartGrid,chartMode)]
        for grid, mode in PageMode:
            for label,value,row,col,span in mode:
                grid.addWidget(QtWidgets.QLabel(label),row,2*col,1,1)
                grid.addWidget(QtWidgets.QLineEdit(value),row,2*col+1,1,2*span-1)
        tab.addTab(self.window,"Window")
        tab.addTab(self.properties,"Properties")
        tab.addTab(self.canvas,"Canvas")
        tab.addTab(self.chart,"Chart")

        buttonBox.addButton("Accept",QtWidgets.QDialogButtonBox.AcceptRole)
        buttonBox.addButton("Reset",QtWidgets.QDialogButtonBox.ResetRole)
        buttonBox.addButton("Cancel",QtWidgets.QDialogButtonBox.DestructiveRole)
        buttonBox.setCenterButtons(True)
        buttonBox.findChildren(QtWidgets.QPushButton)[0].clicked.connect(self.Accept)
        buttonBox.findChildren(QtWidgets.QPushButton)[1].clicked.connect(self.Reset)
        buttonBox.findChildren(QtWidgets.QPushButton)[2].clicked.connect(self.DefaultSettings_Dialog.reject)

        DefaultSettings_DialogGrid.addWidget(tab,0,0)
        DefaultSettings_DialogGrid.addWidget(buttonBox,1,0)
        DefaultSettings_DialogGrid.setContentsMargins(0,0,0,0)
        self.DefaultSettings_Dialog.setWindowTitle("Default Settings")
        self.DefaultSettings_Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        self.DefaultSettings_Dialog.resize(tab.minimumSizeHint())
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

    def Accept(self):
        windowValueList = [item.text() for item in self.window.findChildren(QtWidgets.QLineEdit)]
        propertiesValueList = [item.text() for item in self.properties.findChildren(QtWidgets.QLineEdit)]
        canvasValueList = [item.text() for item in self.canvas.findChildren(QtWidgets.QLineEdit)]
        chartValueList = [item.text() for item in self.chart.findChildren(QtWidgets.QLineEdit)]
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

class TwoDimensionalMapping(QtCore.QObject,Process.Image):
    #Public Signals
    StatusRequested = QtCore.pyqtSignal()
    progressAdvance = QtCore.pyqtSignal(int,int,int)
    progressEnd = QtCore.pyqtSignal()

    def __init__(self):
        super(TwoDimensionalMapping,self).__init__()
        self.twoDimensionalMappingRegion = [0,0,0,0,0]
        self.config = configparser.ConfigParser()
        self.config.read('./configuration.ini')

    def Main(self,path):
        self.backgroundLevel = 0
        self.cutoffLevel = 100
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
        self.sourceGrid = QtWidgets.QGridLayout(self.chooseSource)
        self.chooseSourceLabel = QtWidgets.QLabel("The source directory is:\n"+self.currentSource)
        self.chooseSourceButton = QtWidgets.QPushButton("Choose")
        self.chooseSourceButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
        self.chooseSourceButton.clicked.connect(self.Choose_Source)
        self.sourceGrid.addWidget(self.chooseSourceLabel,0,0)
        self.sourceGrid.addWidget(self.chooseSourceButton,0,1)
        self.sourceGrid.setAlignment(self.chooseSourceLabel,QtCore.Qt.AlignTop)
        self.chooseDestination = QtWidgets.QGroupBox("Save Destination")
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
        self.centeredCheck.setChecked(True)
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
        self.chooseDestinationButton = QtWidgets.QPushButton("Choose")
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
        self.parametersBox = QtWidgets.QGroupBox("Parameters")
        self.parametersGrid = QtWidgets.QGridLayout(self.parametersBox)
        self.startImageIndexLabel = QtWidgets.QLabel("Start Image Index")
        self.startImageIndexEdit = QtWidgets.QLineEdit(self.startIndex)
        self.endImageIndexLabel = QtWidgets.QLabel("End Image Index")
        self.endImageIndexEdit = QtWidgets.QLineEdit(self.endIndex)
        self.parametersGrid.addWidget(self.startImageIndexLabel,0,0)
        self.parametersGrid.addWidget(self.startImageIndexEdit,0,1)
        self.parametersGrid.addWidget(self.endImageIndexLabel,1,0)
        self.parametersGrid.addWidget(self.endImageIndexEdit,1,1)
        self.plotOptions = QtWidgets.QGroupBox("Plot Options")
        self.plotOptionsGrid = QtWidgets.QGridLayout(self.plotOptions)
        self.colormapLabel = QtWidgets.QLabel("Colormap")
        self.colormap = QtWidgets.QComboBox()
        self.colormap.addItem("jet","jet")
        self.colormap.addItem("hsv","hsv")
        self.colormap.addItem("rainbow","rainbow")
        self.colormap.addItem("nipy_spectral","nipy_spectral")
        self.backgroundLevelLabel = QtWidgets.QLabel("Background Level ({})".format(self.backgroundLevel))
        self.backgroundLevelSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.backgroundLevelSlider.setMinimum(0)
        self.backgroundLevelSlider.setMaximum(100)
        self.backgroundLevelSlider.setValue(self.backgroundLevel)
        self.backgroundLevelSlider.valueChanged.connect(self.Refresh_Background_Level)
        self.cutoffLevelLabel = QtWidgets.QLabel("Cutoff Level ({})".format(self.cutoffLevel))
        self.cutoffLevelSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.cutoffLevelSlider.setMinimum(0)
        self.cutoffLevelSlider.setMaximum(100)
        self.cutoffLevelSlider.setValue(self.cutoffLevel)
        self.cutoffLevelSlider.valueChanged.connect(self.Refresh_Cutoff_Level)
        self.numberOfContourLevelsLabel = QtWidgets.QLabel("Number of Contour Levels ({})".format(self.numberOfContourLevels))
        self.numberOfContourLevelsLabel.setFixedWidth(150)
        self.numberOfContourLevelsSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.numberOfContourLevelsSlider.setMinimum(5)
        self.numberOfContourLevelsSlider.setMaximum(50)
        self.numberOfContourLevelsSlider.setValue(self.numberOfContourLevels)
        self.numberOfContourLevelsSlider.valueChanged.connect(self.Refresh_Number_Of_Contour_Levels)
        self.plotOptionsGrid.addWidget(self.colormapLabel,0,0)
        self.plotOptionsGrid.addWidget(self.colormap,0,1)
        self.plotOptionsGrid.addWidget(self.backgroundLevelLabel,1,0)
        self.plotOptionsGrid.addWidget(self.backgroundLevelSlider,1,1)
        self.plotOptionsGrid.addWidget(self.cutoffLevelLabel,2,0)
        self.plotOptionsGrid.addWidget(self.cutoffLevelSlider,2,1)
        self.plotOptionsGrid.addWidget(self.numberOfContourLevelsLabel,3,0)
        self.plotOptionsGrid.addWidget(self.numberOfContourLevelsSlider,3,1)
        self.statusBar = QtWidgets.QGroupBox("Log")
        self.statusGrid = QtWidgets.QGridLayout(self.statusBar)
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
                                    "\u00A0\u00A0\u00A0\u00A0PyRHEED developed by Y. Xiang (yux1991@gmail.com)")
        self.logBox.ensureCursorVisible()
        self.logBox.setAlignment(QtCore.Qt.AlignTop)
        self.logBox.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.messageScroll = QtWidgets.QScrollArea()
        self.messageScroll.setWidget(self.logBox)
        self.messageScroll.setWidgetResizable(True)
        self.messageScroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.statusGrid.addWidget(self.messageScroll,0,0)
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
        self.chart = ProfileChart.ProfileChart(self.config)
        self.LeftGrid.addWidget(self.chooseSource,0,0)
        self.LeftGrid.addWidget(self.chooseDestination,1,0)
        self.LeftGrid.addWidget(self.parametersBox,2,0)
        self.LeftGrid.addWidget(self.ButtonBox,4,0)
        self.RightGrid.addWidget(self.chart,0,0)
        self.RightGrid.addWidget(self.plotOptions,1,0)
        self.RightGrid.addWidget(self.statusBar,2,0)
        self.RightGrid.addWidget(self.progressBar,3,0)
        self.Grid.addWidget(self.LeftFrame,0,0)
        self.Grid.addWidget(self.RightFrame,0,1)
        self.Dialog.setWindowTitle("2D Map")
        self.Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        self.Dialog.showNormal()
        self.Dialog.exec_()


    def Start(self):
        self.StatusRequested.emit()
        self.windowDefault = dict(self.config['windowDefault'].items())
        self.logBox.clear()
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
                    for iphi in range(0,np.argmax(I)):
                        Phi1[iphi]=nimg*1.8+180
                    if np.argmax(I)<(len(RC)-1)/2:
                        x1,y1 = abs(RC[0:(2*np.argmax(I)+1)]), I[0:(2*np.argmax(I)+1)]/I[np.argmax(I)]
                        map_2D1 = np.vstack((map_2D1,np.vstack((x1,Phi1[0:(2*np.argmax(I)+1)],y1)).T))
                        x2,y2 = RC[0:(2*np.argmax(I)+1)], I[0:(2*np.argmax(I)+1)]/I[np.argmax(I)]
                        map_2D2 = np.vstack((map_2D2,np.vstack((x2,Phi2[0:(2*np.argmax(I)+1)],y2)).T))
                    else:
                        x1,y1 = abs(RC[(2*np.argmax(I)-len(RC)-1):-1]), I[(2*np.argmax(I)-len(RC)-1):-1]/I[np.argmax(I)]
                        map_2D1 = np.vstack((map_2D1,np.vstack((x1,Phi1[(2*np.argmax(I)-len(RC)-1):-1],y1)).T))
                        x2,y2 = RC[(2*np.argmax(I)-len(RC)-1):-1], I[(2*np.argmax(I)-len(RC)-1):-1]/I[np.argmax(I)]
                        map_2D2 = np.vstack((map_2D2,np.vstack((x2,Phi2[(2*np.argmax(I)-len(RC)-1):-1],y2)).T))
                else:
                    RC,I = self.getIntegral(start,end,width,img,scale_factor)
                    Phi1 = np.full(len(RC),nimg*1.8)
                    Phi2 = np.full(len(RC),nimg*1.8)
                    for iphi in range(0,np.argmax(I)):
                        Phi1[iphi]=nimg*1.8+180
                    if np.argmax(I)<(len(RC)-1)/2:
                        x1,y1 = abs(RC[0:(2*np.argmax(I)+1)]),I[0:(2*np.argmax(I)+1)]/I[np.argmax(I)]
                        map_2D1 = np.vstack((map_2D1,np.vstack((x1,Phi1[0:(2*np.argmax(I)+1)],y1)).T))
                        x2,y2 = RC[0:(2*np.argmax(I)+1)],I[0:(2*np.argmax(I)+1)]/I[np.argmax(I)]
                        map_2D2 = np.vstack((map_2D2,np.vstack((x2,Phi2[0:(2*np.argmax(I)+1)],y2)).T))
                    else:
                        x1,y1 = abs(RC[(2*np.argmax(I)-len(RC)-1):-1]), I[(2*np.argmax(I)-len(RC)-1):-1]/I[np.argmax(I)]
                        map_2D1 = np.vstack((map_2D1,np.vstack((x1,Phi1[(2*np.argmax(I)-len(RC)-1):-1],y1)).T))
                        x2,y2 = RC[(2*np.argmax(I)-len(RC)-1):-1], I[(2*np.argmax(I)-len(RC)-1):-1]/I[np.argmax(I)]
                        map_2D2 = np.vstack((map_2D2,np.vstack((x2,Phi2[(2*np.argmax(I)-len(RC)-1):-1],y2)).T))
                self.progressAdvance.emit(0,100,(nimg+1-startIndex)*100/(endIndex-startIndex+1))
                self.logBox.append(QtCore.QTime.currentTime().toString("hh:mm:ss")+"\u00A0\u00A0\u00A0\u00A0The file being processed right now is: "+image_list[nimg-startIndex])
                if self.centeredCheck.checkState():
                    self.chart.addChart(x1,y1)
                else:
                    self.chart.addChart(x2,y2)
                QtCore.QCoreApplication.processEvents()
            if self.centeredCheck.checkState():
                map_2D_polar = np.delete(map_2D2,0,0)
            else:
                map_2D_polar = np.delete(map_2D1,0,0)
            map_2D_cart = np.empty(map_2D_polar.shape)
            map_2D_cart[:,2] = map_2D_polar[:,2]
            map_2D_cart[:,0] = map_2D_polar[:,0]*np.cos((map_2D_polar[:,1])*math.pi/180)
            map_2D_cart[:,1] = map_2D_polar[:,0]*np.sin((map_2D_polar[:,1])*math.pi/180)
            if self.cartesian.checkState():
                np.savetxt(self.currentDestination+"/"+saveFileName+fileType,map_2D_cart,fmt='%4.3f')
            else:
                np.savetxt(self.currentDestination+"/"+saveFileName+fileType,map_2D_polar,fmt='%4.3f')
            self.progressEnd.emit()
            self.logBox.append(QtCore.QTime.currentTime().toString("hh:mm:ss")+"\u00A0\u00A0\u00A0\u00A0Completed!")
            self.Raise_Attention("2D Map Completed!")

    def Reset(self):
        self.backgroundLevel = 0
        self.cutoffLevel = 100
        self.numberOfContourLevels = 5
        self.currentSource = self.path
        self.currentDestination = self.currentSource
        self.backgroundLevelSlider.setValue(self.backgroundLevel)
        self.cutoffLevelSlider.setValue(self.cutoffLevel)
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

    def Refresh_Background_Level(self):
        self.backgroundLevel = self.backgroundLevelSlider.value()
        self.backgroundLevelLabel.setText("Background Level ({})".format(self.backgroundLevel))

    def Refresh_Cutoff_Level(self):
        self.cutoffLevel = self.cutoffLevelSlider.value()
        self.cutoffLevelLabel.setText("Cutoff Level ({})".format(self.cutoffLevel))

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
