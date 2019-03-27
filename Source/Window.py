from Canvas import *
from Browser import *
from Properties import *
from Cursor import *
from Menu import *
import rawpy
import ProfileChart
import os
import numpy as np
import Process

class Window(QtWidgets.QMainWindow,Process.Image):

    #Public Signals
    fileOpened = QtCore.pyqtSignal(str)
    imgCreated = QtCore.pyqtSignal(np.ndarray)
    scaleFactorChanged = QtCore.pyqtSignal(float)
    canvasScaleFactorChanged = QtCore.pyqtSignal(float)
    labelChanged = QtCore.pyqtSignal(float,float)
    calibrationChanged = QtCore.pyqtSignal(float,float)
    progressAdvance = QtCore.pyqtSignal(int,int,int)
    progressEnd = QtCore.pyqtSignal()
    menu_DefaultPropertiesRestRequested = QtCore.pyqtSignal()
    menu_TwoDimensionalMappingRequested = QtCore.pyqtSignal(str)
    menu_ThreeDimensionalGraphRequested = QtCore.pyqtSignal(str)
    menu_BroadeningRequested = QtCore.pyqtSignal(str)
    menu_ManualFitRequested = QtCore.pyqtSignal(str,int)
    menu_GenerateReportRequested = QtCore.pyqtSignal(str)
    window_initialized = QtCore.pyqtSignal()
    propertiesRefresh = QtCore.pyqtSignal(configparser.ConfigParser)
    canvasRefresh = QtCore.pyqtSignal(configparser.ConfigParser)
    chartRefresh = QtCore.pyqtSignal(configparser.ConfigParser)
    returnStatus = QtCore.pyqtSignal(dict)

    def __init__(self,config):

        super(Window, self).__init__()
        self.currentPath = ''
        self._mode = "pan"
        self.photoList = []
        self.pathList = []
        self.tabClosed = False
        self.config = config

        #Defaults
        self.windowDefault = dict(self.config['windowDefault'].items())
        self.propertiesDefault = dict(self.config['propertiesDefault'].items())
        self.canvasDefault = dict(self.config['canvasDefault'].items())
        self.chartDefault = dict(self.config['chartDefault'].items())
        self.HS = int(self.windowDefault['hs'])
        self.VS = int(self.windowDefault['vs'])
        self.energy = int(self.windowDefault['energy'])
        self.azimuth = int(self.windowDefault['azimuth'])
        self.scaleBarLength = int(self.windowDefault['scalebarlength'])
        self.chiRange = int(self.windowDefault['chirange'])
        self.width = float(self.windowDefault['width'])
        self.widthSliderScale = int(self.windowDefault['widthsliderscale'])
        self.radius = int(self.windowDefault['radius'])
        self.radiusMaximum = int(self.windowDefault['radiusmaximum'])
        self.radiusSliderScale = int(self.windowDefault['radiussliderscale'])
        self.tiltAngle = int(self.windowDefault['tiltangle'])
        self.tiltAngleSliderScale = int(self.windowDefault['tiltanglesliderscale'])

        #Menu bar
        self.menu = QtWidgets.QMenuBar()
        self.menuFile = self.menu.addMenu("File")
        self.menuPreference = self.menu.addMenu("Preference")
        self.menu2DMap = self.menu.addMenu("2D Map")
        self.menuFit = self.menu.addMenu("Fit")
        self.menuHelp = self.menu.addMenu("Help")
        self.setMenuBar(self.menu)

        #File Menu
        self.openFile = self.menuFile.addAction("Open",self.MenuActions_Open)
        self.export = self.menuFile.addMenu("Export")
        self.saveCanvasAsImage = self.export.addAction("RHEED pattern as Image",self.MenuActions_Save_As_Image)
        self.saveProfileAsText = self.export.addAction("Line profile as text",self.MenuActions_Save_As_Text)
        self.saveProfileAsText = self.export.addAction("Line profile as image",self.MenuActions_Save_Profile_As_Image)
        self.saveProfileAsText = self.export.addAction("Line profile as SVG",self.MenuActions_Save_As_SVG)

        #Preference Menu
        self.defaultSettings = self.menuPreference.addAction("Default Settings",\
                                    self.MenuActions_Preference_DefaultSettings)

        #2D Map Menu
        self.Two_Dimensional_Mapping = self.menu2DMap.addAction("Configuration", \
                                            self.MenuActions_Two_Dimensional_Mapping)

        self.Three_Dimensional_Graph = self.menu2DMap.addAction("3D Graph", \
                                        self.MenuActions_Three_Dimensional_Graph)

        #Fit Menu
        self.Fit_Broadening = self.menuFit.addAction("Broadening",self.MenuActions_Broadening)
        self.Fit_ManualFit = self.menuFit.addAction("Manual Fit", self.MenuActions_ShowManualFit)
        self.Fit_Report = self.menuFit.addAction("Generate Report", self.MenuActions_GenerateReport)

        #Help Menu
        self.about = self.menuHelp.addAction("About",self.MenuActions_About)

        #Center Widget
        self.image_crop = [1200+self.VS,2650+self.VS,500+self.HS,3100+self.HS]

        self.mainSplitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.mainTab = QtWidgets.QTabWidget()
        self.mainTab.setContentsMargins(0,0,0,0)
        self.mainTab.setTabsClosable(True)
        self.controlPanelFrame = QtWidgets.QWidget(self)
        self.controlPanelGrid = QtWidgets.QGridLayout(self.controlPanelFrame)
        self.controlPanelGrid.setContentsMargins(0,0,0,0)
        self.controlPanelSplitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.browser = Browser(self)
        self.controlPanelBottomWidget = QtWidgets.QWidget()
        self.controlPanelBottomGrid = QtWidgets.QGridLayout(self.controlPanelBottomWidget)
        self.controlPanelBottomGrid.setContentsMargins(0,0,2,0)
        self.properties = Properties(self,self.config)
        self.cursorInfo = Cursor(self)
        self.profile = ProfileChart.ProfileChart(self.config)
        self.controlPanelBottomGrid.addWidget(self.properties,0,0)
        self.controlPanelBottomGrid.addWidget(self.cursorInfo,1,0)
        self.controlPanelBottomGrid.addWidget(self.profile,2,0)
        self.controlPanelSplitter.addWidget(self.browser)
        self.controlPanelSplitter.addWidget(self.controlPanelBottomWidget)

        self.controlPanelSplitter.setSizes([100,500])
        self.controlPanelSplitter.setStretchFactor(0,1)
        self.controlPanelSplitter.setStretchFactor(1,1)
        self.controlPanelSplitter.setCollapsible(0,False)
        self.controlPanelSplitter.setCollapsible(1,False)
        self.controlPanelGrid.addWidget(self.controlPanelSplitter,0,0)

        self.mainSplitter.addWidget(self.mainTab)
        self.mainSplitter.addWidget(self.controlPanelFrame)
        self.mainSplitter.setSizes([800,400])
        self.mainSplitter.setStretchFactor(0,1)
        self.mainSplitter.setStretchFactor(1,1)
        self.mainSplitter.setCollapsible(0,False)
        self.mainSplitter.setCollapsible(1,False)


        #Tool bar
        self.toolBar = QtWidgets.QToolBar(self)
        self.toolBar.setFloatable(False)
        self.toolBar.setMovable(False)
        self.open = QtWidgets.QAction(QtGui.QIcon("./icons/open.svg"), "open", self)
        self.saveAs = QtWidgets.QAction(QtGui.QIcon("./icons/save as.svg"), "save as", self)
        self.zoomIn = QtWidgets.QAction(QtGui.QIcon("./icons/zoom in.svg"), "zoom in (Ctrl + Plus)", self)
        self.zoomIn.setShortcut(QtGui.QKeySequence.ZoomIn)
        self.zoomOut = QtWidgets.QAction(QtGui.QIcon("./icons/zoom out.svg"), "zoom out (Ctrl + Minus)", self)
        self.zoomOut.setShortcut(QtGui.QKeySequence.ZoomOut)
        self.fitCanvas = QtWidgets.QAction(QtGui.QIcon("./icons/fit.svg"), "fit in view",self)
        self.line = QtWidgets.QAction(QtGui.QIcon("./icons/line.svg"), "line", self)
        self.line.setCheckable(True)
        self.rectangle = QtWidgets.QAction(QtGui.QIcon("./icons/rectangle.svg"), "rectangle", self)
        self.rectangle.setCheckable(True)
        self.arc = QtWidgets.QAction(QtGui.QIcon("./icons/arc.svg"), "arc", self)
        self.arc.setCheckable(True)
        self.pan = QtWidgets.QAction(QtGui.QIcon("./icons/move.svg"), "pan", self)
        self.pan.setCheckable(True)
        self.buttonModeGroup = QtWidgets.QActionGroup(self.toolBar)
        self.buttonModeGroup.addAction(self.line)
        self.buttonModeGroup.addAction(self.rectangle)
        self.buttonModeGroup.addAction(self.arc)
        self.buttonModeGroup.addAction(self.pan)
        self.toolBar.addAction(self.open)
        self.toolBar.addAction(self.saveAs)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.line)
        self.toolBar.addAction(self.rectangle)
        self.toolBar.addAction(self.arc)
        self.toolBar.addAction(self.pan)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.zoomIn)
        self.toolBar.addAction(self.zoomOut)
        self.toolBar.addAction(self.fitCanvas)
        self.addToolBar(self.toolBar)

        #Status bar
        self.statusBar = QtWidgets.QStatusBar(self)
        self.messageLoadingImage = QtWidgets.QLabel("Processing ... ",self)
        self.messageLoadingImage.setVisible(False)
        self.progressBar = QtWidgets.QProgressBar(self)
        self.progressBar.setMaximumHeight(12)
        self.progressBar.setMaximumWidth(200)
        self.progressBar.setVisible(False)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.editPixInfo = QtWidgets.QLabel(self)
        self.editPixInfo.setAlignment(QtCore.Qt.AlignRight)
        self.editPixInfo.setMinimumWidth(150)
        self.statusBar.addWidget(self.messageLoadingImage)
        self.statusBar.insertPermanentWidget(1,self.progressBar)
        self.statusBar.addPermanentWidget(self.editPixInfo)
        self.setStatusBar(self.statusBar)

        #Main Window Settings
        self.setCentralWidget(self.mainSplitter)
        self.mainSplitter.setContentsMargins(2,2,0,0)
        self.setWindowTitle("PyRHEED")

        #Main Tab Connections
        self.mainTab.currentChanged.connect(self.switchTab)
        self.mainTab.tabCloseRequested.connect(self.closeTab)

        #Toolbar Connections
        self.open.triggered.connect(lambda path: self.openImage(path=self.getImgPath()))
        self.line.triggered.connect(lambda cursormode: self.toggleCanvasMode(cursormode="line"))
        self.rectangle.triggered.connect(lambda cursormode: self.toggleCanvasMode(cursormode="rectangle"))
        self.arc.triggered.connect(lambda cursormode: self.toggleCanvasMode(cursormode="arc"))
        self.pan.triggered.connect(lambda cursormode: self.toggleCanvasMode(cursormode="pan"))

        #Progress Bar Connections
        self.progressAdvance.connect(self.progress)
        self.progressEnd.connect(self.progressReset)
        self.profile.progressAdvance.connect(self.progress)
        self.profile.progressEnd.connect(self.progressReset)

        #Browser Connections
        self.fileOpened.connect(self.browser.treeUpdate)
        self.imgCreated.connect(self.profile.setImg)
        self.browser.fileDoubleClicked.connect(self.openImage)

        #Parameters Page Connections
        self.properties.sensitivityEdit.textChanged.connect(self.changeSensitivity)
        self.properties.energyEdit.textChanged.connect(self.changeEnergy)
        self.properties.azimuthEdit.textChanged.connect(self.changeAzimuth)
        self.properties.scaleBarEdit.textChanged.connect(self.changeScaleBar)
        self.properties.labelButton.clicked.connect(self.labelImage)
        self.properties.calibrateButton.clicked.connect(self.calibrateImage)

        #Image Adjust Page Connections
        self.properties.brightnessSlider.valueChanged.connect(self.changeBrightness)
        self.properties.blackLevelSlider.valueChanged.connect(self.changeBlackLevel)
        self.properties.autoWBCheckBox.stateChanged.connect(self.changeAutoWB)
        self.properties.applyButton2.clicked.connect(self.applyImageAdjusts)
        self.properties.resetButton2.clicked.connect(self.resetImageAdjusts)

        #Profile Options Page Connections
        self.properties.integralHalfWidthSlider.valueChanged.connect(self.changeWidth)
        self.properties.chiRangeSlider.valueChanged.connect(self.changeChiRange)
        self.properties.radiusSlider.valueChanged.connect(self.changeRadius)
        self.properties.tiltAngleSlider.valueChanged.connect(self.changeTiltAngle)
        self.properties.applyButton3.clicked.connect(self.applyProfileOptions)
        self.properties.resetButton3.clicked.connect(self.resetProfileOptions)

        #Cursor Information Connections
        self.cursorInfo.choosedXYEdit.textChanged.connect(self.editChoosedXY)
        self.cursorInfo.startXYEdit.textChanged.connect(self.editStartXY)
        self.cursorInfo.endXYEdit.textChanged.connect(self.editEndXY)
        self.cursorInfo.widthEdit.textEdited.connect(self.editWidth)

        #Profile Canvas Connections
        self.scaleFactorChanged.connect(self.profile.setScaleFactor)
        self.profile.chartMouseMovement.connect(self.photoMouseMovement)

        #Refresh Connections
        self.propertiesRefresh.connect(self.properties.refresh)
        self.chartRefresh.connect(self.profile.refresh)

        self.getScaleFactor()
        self.window_initialized.emit()

    def refresh(self,config):
        self.windowDefault = dict(config['windowDefault'].items())
        self.propertiesDefault = dict(config['propertiesDefault'].items())
        self.canvasDefault = dict(config['canvasDefault'].items())
        self.chartDefault = dict(config['chartDefault'].items())
        self.HS = int(self.windowDefault['hs'])
        self.VS = int(self.windowDefault['vs'])
        self.energy = int(self.windowDefault['energy'])
        self.azimuth = int(self.windowDefault['azimuth'])
        self.scaleBarLength = int(self.windowDefault['scalebarlength'])
        self.chiRange = int(self.windowDefault['chirange'])
        self.width = float(self.windowDefault['width'])
        self.widthSliderScale = int(self.windowDefault['widthsliderscale'])
        self.radius = int(self.windowDefault['radius'])
        self.radiusMaximum = int(self.windowDefault['radiusmaximum'])
        self.radiusSliderScale = int(self.windowDefault['radiussliderscale'])
        self.tiltAngle = int(self.windowDefault['tiltangle'])
        self.tiltAngleSliderScale = int(self.windowDefault['tiltanglesliderscale'])
        self.image_crop = [1200+self.VS,2650+self.VS,500+self.HS,3100+self.HS]
        self.propertiesRefresh.emit(config)
        self.chartRefresh.emit(config)
        self.canvasRefresh.emit(config)
        self.resetImageAdjusts()
        self.getScaleFactor()

    def progress(self,min,max,val):
        self.progressBar.setVisible(True)
        self.progressBar.setMinimum(min)
        self.progressBar.setMaximum(max)
        self.progressBar.setValue(val)

    def progressReset(self):
        self.progressBar.reset()
        self.progressBar.setVisible(False)

    def MenuActions_Open(self):
        self.openImage(path=self.getImgPath())

    def MenuActions_Save_As_Image(self):
        canvas = self.mainTab.currentWidget()
        try:
            canvas.saveScene()
        except:
            self.Raise_Error("Please open a RHEED pattern first")

    def MenuActions_Save_As_Text(self):
        self.profile.saveProfileAsText()

    def MenuActions_Save_Profile_As_Image(self):
        self.profile.saveProfileAsImage()

    def MenuActions_Save_As_SVG(self):
        self.profile.saveProfileAsSVG()

    def MenuActions_Preference_DefaultSettings(self):
        self.menu_DefaultPropertiesRestRequested.emit()

    def MenuActions_Two_Dimensional_Mapping(self):
        self.menu_TwoDimensionalMappingRequested.emit(self.currentPath)

    def MenuActions_Three_Dimensional_Graph(self):
        self.menu_ThreeDimensionalGraphRequested.emit(self.currentPath)

    def MenuActions_Broadening(self):
        self.menu_BroadeningRequested.emit(self.currentPath)

    def MenuActions_ShowManualFit(self):
        self.menu_ManualFitRequested.emit(self.currentPath,0)

    def MenuActions_GenerateReport(self):
        self.menu_GenerateReportRequested.emit(self.currentPath)

    def MenuActions_About(self):
        self.Raise_Attention(information="Author: Yu Xiang\nEmail: yux1991@gmail.com")

    def getScaleFactor(self):
        self.scaleFactor = float(self.properties.sensitivityEdit.text())/np.sqrt(float(self.properties.energyEdit.text()))
        self.scaleFactorChanged.emit(self.scaleFactor)
        self.canvasScaleFactorChanged.emit(self.scaleFactor)

    def changeSensitivity(self,sensitivity):
        if not sensitivity == "":
            self.scaleFactor = float(sensitivity)/np.sqrt(float(self.properties.energyEdit.text()))
        self.scaleFactorChanged.emit(self.scaleFactor)
        self.canvasScaleFactorChanged.emit(self.scaleFactor)

    def changeEnergy(self,energy):
        if not energy == "":
            self.scaleFactor = float(self.properties.sensitivityEdit.text())/np.sqrt(float(energy))
        self.scaleFactorChanged.emit(self.scaleFactor)
        self.canvasScaleFactorChanged.emit(self.scaleFactor)
        self.energy = float(energy)

    def changeAzimuth(self,azimuth):
        if not azimuth == "":
            self.azimuth = float(azimuth)

    def changeScaleBar(self,scaleBar):
        if not scaleBar == "":
            self.scaleBarLength = float(scaleBar)

    def labelImage(self):
        self.labelChanged.emit(self.energy,self.azimuth)

    def calibrateImage(self):
        self.calibrationChanged.emit(self.scaleFactor,self.scaleBarLength)

    def changeBrightness(self,brightness):
        self.properties.brightnessLabel.setText('Brightness ({})'.format(brightness))

    def changeBlackLevel(self,blackLevel):
        self.properties.blackLevelLabel.setText('Black Level ({})'.format(blackLevel))

    def changeAutoWB(self):
        return

    def applyImageAdjusts(self):
        self.updateImage(self.currentPath,bitDepth = 16, enableAutoWB = self.properties.autoWBCheckBox.isChecked(),\
                           brightness = self.properties.brightnessSlider.value(),blackLevel=self.properties.blackLevelSlider.value())

    def resetImageAdjusts(self):
        self.properties.autoWBCheckBox.setChecked(False)
        self.properties.brightnessSlider.setValue(int(self.propertiesDefault['brightness']))
        self.properties.blackLevelSlider.setValue(int(self.propertiesDefault['blacklevel']))
        self.updateImage(self.currentPath,bitDepth = 16, enableAutoWB = self.properties.autoWBCheckBox.isChecked(), \
                       brightness = self.properties.brightnessSlider.value(),blackLevel=self.properties.blackLevelSlider.value())

    def changeWidth(self,width):
        self.properties.integralHalfWidthLabel.setText('Integral Half Width ({:3.2f} \u212B\u207B\u00B9)'.format(width/self.widthSliderScale))
        if not self.cursorInfo.widthEdit.text() == "":
            if self._mode == "rectangle" or self._mode == "arc":
                self.cursorInfo.widthEdit.setText('{:3.2f}'.format(width/self.widthSliderScale))
        self.updateDrawing()
        for i in range(0,self.mainTab.count()):
            self.mainTab.widget(i).width = width/self.widthSliderScale * self.scaleFactor

    def changeChiRange(self,chi):
        self.properties.chiRangeLabel.setText('Chi Range ({}\u00B0)'.format(chi))
        self.updateDrawing()
        for i in range(0,self.mainTab.count()):
            self.mainTab.widget(i).span = chi

    def changeRadius(self,radius):
        self.properties.radiusLabel.setText('Radius ({:3.2f} \u212B\u207B\u00B9)'.format(radius/self.radiusSliderScale))
        if not self.mainTab.count() == 0:
            if not self.mainTab.currentWidget()._drawingArc:
                self.updateDrawing()

    def changeTiltAngle(self,tilt):
        self.properties.tiltAngleLabel.setText('Tilt Angle ({:2.1f}\u00B0)'.format(tilt/self.tiltAngleSliderScale))
        self.updateDrawing()
        for i in range(0,self.mainTab.count()):
            self.mainTab.widget(i).tilt = tilt/self.tiltAngleSliderScale

    def applyProfileOptions(self):
        if not self.mainTab.count() == 0:
            if self.mainTab.currentWidget().canvasObject == "line":
                self.mainTab.currentWidget().lineScanSignalEmit()
            if self.mainTab.currentWidget().canvasObject == "rectangle":
                self.mainTab.currentWidget().integralSignalEmit()
            if self.mainTab.currentWidget().canvasObject == "arc":
                self.mainTab.currentWidget().chiScanSignalEmit()

    def resetProfileOptions(self):
        self.properties.integralHalfWidthSlider.setValue(self.width*self.widthSliderScale)
        self.properties.chiRangeSlider.setValue(self.chiRange)
        self.properties.radiusSlider.setValue(self.radius*self.radiusSliderScale)
        self.properties.tiltAngleSlider.setValue(self.tiltAngle)
        self.applyProfileOptions()

    def editChoosedXY(self):
        return

    def editStartXY(self):
        return

    def editEndXY(self):
        return

    def editWidth(self,width):
        self.properties.integralHalfWidthSlider.setValue(int(width)*self.widthSliderScale)

    def getImgPath(self):
        fileDlg = QtWidgets.QFileDialog(self)
        fileDlg.setDirectory('C:/RHEED/')
        path = fileDlg.getOpenFileName(filter="NEF (*.nef);;All Files (*.*)")[0]
        return path

    def openImage(self,path,bitDepth = 16, enableAutoWB=False,brightness=20,blackLevel=50):
        if not path == '':
            canvas = Canvas(self,self.config)
            self.connectCanvas(canvas)
            self.canvasScaleFactorChanged.emit(self.scaleFactor)
            img_array = self.loadImage(canvas,path,bitDepth,enableAutoWB,brightness,blackLevel)
            self.photoList.append(img_array)
            self.pathList.append(path)
            self.mainTab.addTab(canvas,os.path.basename(path))
            self.mainTab.setCurrentIndex(self.mainTab.count()-1)
            canvas.fitCanvas()
            canvas.toggleMode(self._mode)
            self.currentPath = path
            self.fileOpened.emit(path)

    def switchTab(self,index):
        if self.mainTab.count() > 0:
            if not self.tabClosed:
                self._img=self.photoList[index]
            self.currentPath=self.pathList[index]
            self.messageLoadingImage.setText("Path of the image: "+self.currentPath)
            self.disconnectCanvas()
            self.reconnectCanvas(self.mainTab.currentWidget())
            self.imgCreated.emit(self._img)
        elif self.mainTab.count() == 0:
            self.messageLoadingImage.clear()
            self.disconnectCanvas()
        if self.tabClosed:
            self.tabClosed = False

    def closeTab(self,index):
        if index == self.mainTab.currentIndex() and not self.mainTab.count()== 1:
            if index == self.mainTab.count()-1:
                self._img=self.photoList[index-1]
                self.currentPath=self.pathList[index-1]
                self.tabClosed = True
                self.mainTab.setCurrentIndex(index-1)
            else:
                self._img=self.photoList[index+1]
                self.currentPath=self.pathList[index+1]
                self.tabClosed = True
                self.mainTab.setCurrentIndex(index+1)
            self.mainTab.widget(index).destroy()
            self.mainTab.removeTab(index)
        elif self.mainTab.count()==1:
            self.mainTab.clear()
            self.tabClosed = True
        else:
            self.tabClosed = True
            self.mainTab.widget(index).destroy()
            self.mainTab.removeTab(index)
        self.photoList.pop(index)
        self.pathList.pop(index)

    def connectCanvas(self,canvas):
        #canvas signals
        canvas.photoMouseMovement.connect(self.photoMouseMovement)
        canvas.photoMousePress.connect(self.photoMousePress)
        canvas.photoMouseRelease.connect(self.photoMouseRelease)
        canvas.photoMouseDoubleClick.connect(self.photoMouseDoubleClick)
        canvas.plotLineScan.connect(self.profile.lineScan)
        canvas.plotIntegral.connect(self.profile.integral)
        canvas.plotChiScan.connect(self.profile.chiScan)
        canvas.KeyPress.connect(self.cursorInfo.chosenRegionUpdate)
        canvas.KeyPressWhileArc.connect(self.cursorInfo.chiScanRegionUpdate)

        #canvas slots
        self.zoomIn.triggered.connect(canvas.zoomIn)
        self.zoomOut.triggered.connect(canvas.zoomOut)
        self.fitCanvas.triggered.connect(canvas.fitCanvas)
        self.properties.clearButton.clicked.connect(canvas.clearAnnotations)
        self.labelChanged.connect(canvas.label)
        self.calibrationChanged.connect(canvas.calibrate)
        self.canvasScaleFactorChanged.connect(canvas.setScaleFactor)
        self.canvasRefresh.connect(canvas.refresh)

    def disconnectCanvas(self):
        self.zoomIn.disconnect()
        self.zoomOut.disconnect()
        self.fitCanvas.disconnect()
        self.properties.clearButton.disconnect()
        self.labelChanged.disconnect()
        self.calibrationChanged.disconnect()
        self.canvasScaleFactorChanged.disconnect()

    def reconnectCanvas(self,canvas):
        self.zoomIn.triggered.connect(canvas.zoomIn)
        self.zoomOut.triggered.connect(canvas.zoomOut)
        self.fitCanvas.triggered.connect(canvas.fitCanvas)
        self.properties.clearButton.clicked.connect(canvas.clearAnnotations)
        self.labelChanged.connect(canvas.label)
        self.calibrationChanged.connect(canvas.calibrate)
        self.canvasScaleFactorChanged.connect(canvas.setScaleFactor)

    def updateImage(self,path,bitDepth = 16, enableAutoWB=False,brightness=20,blackLevel=50):
        if not self.mainTab.count() == 0:
            canvas = self.mainTab.currentWidget()
            img_array=self.loadImage(canvas,path,bitDepth,enableAutoWB,brightness,blackLevel)
            self.photoList[self.mainTab.currentIndex()]=img_array
            self.applyProfileOptions()

    def loadImage(self,canvas,path,bitDepth = 16, enableAutoWB=False,brightness=20,blackLevel=50):
        self.messageLoadingImage.setText("Processing ... ")
        self.messageLoadingImage.setVisible(True)
        QtWidgets.QApplication.sendPostedEvents()
        self.messageLoadingImage.setVisible(True)
        QtWidgets.QApplication.sendPostedEvents()
        qImg,img_array = self.getImage(bitDepth,path, enableAutoWB, brightness, blackLevel,self.image_crop)
        qPixImg = QtGui.QPixmap(qImg.size())
        QtGui.QPixmap.convertFromImage(qPixImg,qImg,QtCore.Qt.MonoOnly)
        canvas.setPhoto(QtGui.QPixmap(qPixImg))
        self._img = img_array
        self.imgCreated.emit(self._img)
        self.messageLoadingImage.setText("Path of the image: "+path)
        return img_array

    def updateDrawing(self):
        if not self.mainTab.count() == 0:
            if self.mainTab.currentWidget().canvasObject == "rectangle":
                self.mainTab.currentWidget().drawRect(self.mainTab.currentWidget().start,self.mainTab.currentWidget().end,self.properties.integralHalfWidthSlider.value()/100*1*self.scaleFactor)
            if self.mainTab.currentWidget().canvasObject == "arc":
                self.mainTab.currentWidget().drawArc(self.mainTab.currentWidget().start,self.properties.radiusSlider.value()/self.radiusSliderScale*self.scaleFactor,\
                                    self.properties.integralHalfWidthSlider.value()/self.widthSliderScale*self.scaleFactor,self.properties.chiRangeSlider.value(),\
                                    self.properties.tiltAngleSlider.value()/self.tiltAngleSliderScale)

    def restoreDefaults(self):
        self.mainTab.currentWidget().clearCanvas()
        self.mainTab.currentWidget().clearAnnotations()
        self.pan.setChecked(True)
        self.properties.autoWBCheckBox.setChecked(False)
        self.properties.brightnessSlider.setValue(20)
        self.properties.blackLevelSlider.setValue(50)
        self.clearCursorInfo()


    def toggleCanvasMode(self,cursormode):
        for i in range(0,self.mainTab.count()):
            self.mainTab.widget(i).toggleMode(cursormode)
        if cursormode == "arc":
            self.cursorInfo.startXYEdit.setText('Center (X,Y)')
            self.cursorInfo.endXYLabel.setText('Radius')
        else:
            self.cursorInfo.endXYLabel.setText('End (X,Y)')
        self.clearCursorInfo()
        self._mode = cursormode

    def clearCursorInfo(self):
        self.cursorInfo.choosedXYEdit.clear()
        self.cursorInfo.intensityEdit.clear()
        self.cursorInfo.startXYEdit.clear()
        self.cursorInfo.endXYEdit.clear()
        self.cursorInfo.widthEdit.clear()

    def photoMousePress(self, pos):
        self.cursorInfo.startXYEdit.setText('{},{}'.format(int(pos.x()), int(pos.y())))
        self.cursorInfo.endXYEdit.clear()
        if self._mode == "rectangle" or self._mode == "arc":
            self.cursorInfo.widthEdit.setText('{:3.2f}'.format(self.properties.integralHalfWidthSlider.value()/self.widthSliderScale))
        elif self._mode == "line":
            self.cursorInfo.widthEdit.setText('{:3.2f}'.format(0.00))

    def photoMouseRelease(self, pos,start,ShiftModified):
        if self._mode == "arc":
            self.cursorInfo.endXYEdit.setText('{}'.format(np.round(self.mainTab.currentWidget().PFRadius,2)))
        else:
            if ShiftModified:
                if pos.x() == start.x():
                    slope = 10
                else:
                    slope = (pos.y()-start.y())/(pos.x()-start.x())
                if slope > np.tan(np.pi/3):
                    pos.setX(start.x())
                elif slope < np.tan(np.pi/6):
                    pos.setY(start.y())
                else:
                    pos.setY(pos.x()-start.x()+start.y())
            self.cursorInfo.endXYEdit.setText('{},{}'.format(int(pos.x()), int(pos.y())))
        if self.mainTab.currentWidget()._drawingArc:
            self.properties.radiusSlider.setValue(self.radiusSliderScale*self.mainTab.currentWidget().PFRadius/self.scaleFactor)

    def photoMouseMovement(self, pos, type="canvas"):
        if type == "canvas":
            self.editPixInfo.setText('x = %d, y = %d' % (int(pos.x()), int(pos.y())))
        elif type == "chart":
            self.editPixInfo.setText('K = %3.2f, Int. = %3.2f' % (pos.x(), pos.y()))
        if self.mainTab.currentWidget()._drawingArc:
            self.properties.radiusSlider.setValue(self.radiusSliderScale*self.mainTab.currentWidget().PFRadius/self.scaleFactor)

    def photoMouseDoubleClick(self, pos):
        self.cursorInfo.choosedXYEdit.setText('{},{}'.format(pos.x(), pos.y()))
        self.cursorInfo.intensityEdit.setText('{:3.2f}'.format(self._img[pos.y(), pos.x()]/np.amax(np.amax(self._img))))

    def keyPressEvent(self,event):
        if event.key() == QtCore.Qt.Key_Up or QtCore.Qt.Key_Down or QtCore.Qt.Key_Left or QtCore.Qt.Key_Right :
            self.mainTab.currentWidget().setFocus()
            self.mainTab.currentWidget().keyPressEvent(event)

    def status(self):
        status = {"sensitivity": float(self.properties.sensitivityEdit.text()),\
                "energy": float(self.properties.energyEdit.text()),\
                "azimuth": float(self.properties.azimuthEdit.text()),\
                "scaleBar": float(self.properties.scaleBarEdit.text()),\
                "brightness": self.properties.brightnessSlider.value(),\
                "blackLevel": self.properties.blackLevelSlider.value(),\
                "integralWidth": self.properties.integralHalfWidthSlider.value()/self.properties.widthSliderScale,\
                "chiRange": self.properties.chiRangeSlider.value(),\
                "radius": self.properties.radiusSlider.value()/self.properties.radiusSliderScale,\
                "tiltAngle": self.properties.tiltAngleSlider.value()/self.properties.tiltAngleSliderScale,\
                "autoWB": self.properties.autoWBCheckBox.isChecked()}
        try:
            status["choosedX"] = int(self.cursorInfo.choosedXYEdit.text().split(',')[0])
            status["choosedY"] = int(self.cursorInfo.choosedXYEdit.text().split(',')[1])
        except:
            status["choosedX"] = ""
            status["choosedY"] = ""
        try:
            status["startX"] = int(self.cursorInfo.startXYEdit.text().split(',')[0])
            status["startY"] = int(self.cursorInfo.startXYEdit.text().split(',')[1])
        except:
            status["startX"] = ""
            status["startY"] = ""
        try:
            status["endX"] = int(self.cursorInfo.endXYEdit.text().split(',')[0])
            status["endY"] = int(self.cursorInfo.endXYEdit.text().split(',')[1])
        except:
            status["endX"] = ""
            status["endY"] = ""
        try:
            status["width"] = float(self.cursorInfo.widthEdit.text())
        except:
            status["width"] = ""
        self.returnStatus.emit(status)

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
