from PyQt5 import QtCore, QtGui, QtWidgets
from Canvas import *
from Browser import *
from Properties import *
#from Profile import *
from ProfileChart import *
from Cursor import *
import rawpy
import numpy as np

class Window(QtWidgets.QMainWindow):

    #Public Signals
    fileOpened = QtCore.pyqtSignal(str)
    imgCreated = QtCore.pyqtSignal(np.ndarray)
    scaleFactorChanged = QtCore.pyqtSignal(float)

    def __init__(self):

        super(Window, self).__init__()
        self.currentPath = ''
        self._mode = "pan"

        #Menu bar
        self.menu = QtWidgets.QMenuBar()
        self.menuFile = self.menu.addMenu("File")
        self.menuPreference = self.menu.addMenu("Preference")
        self.menu2DMap = self.menu.addMenu("2D Map")
        self.menuFit = self.menu.addMenu("Fit")
        self.menuHelp = self.menu.addMenu("Help")
        self.setMenuBar(self.menu)

        #Center Widget
        self.HS,self.VS = 0,0
        self.image_crop = [1200+self.VS,2650+self.VS,500+self.HS,3100+self.HS]
        self.img_path = 'C:/RHEED/01192017 multilayer graphene on Ni/20 keV/Img0000.nef'

        self.mainSplitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.canvas = Canvas(self)
        self.controlPanelFrame = QtWidgets.QWidget(self)
        self.controlPanelGrid = QtWidgets.QGridLayout(self.controlPanelFrame)
        self.controlPanelGrid.setContentsMargins(0,0,0,0)
        self.controlPanelSplitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.browser = Browser(self)
        self.controlPanelBottomWidget = QtWidgets.QWidget()
        self.controlPanelBottomGrid = QtWidgets.QGridLayout(self.controlPanelBottomWidget)
        self.controlPanelBottomGrid.setContentsMargins(0,0,2,0)
        self.properties = Properties(self)
        self.cursorInfo = Cursor(self)
        self.profile = ProfileChart(self)
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

        self.mainSplitter.addWidget(self.canvas)
        self.mainSplitter.addWidget(self.controlPanelFrame)
        self.mainSplitter.setSizes([800,400])
        self.mainSplitter.setStretchFactor(0,1)
        self.mainSplitter.setStretchFactor(1,1)
        self.mainSplitter.setCollapsible(0,False)
        self.mainSplitter.setCollapsible(1,False)

        self.getScaleFactor()

        #Tool bar
        self.toolBar = QtWidgets.QToolBar(self)
        self.toolBar.setFloatable(False)
        self.toolBar.setMovable(False)
        self.open = QtWidgets.QAction(QtGui.QIcon("./icons/open.gif"), "open", self)
        self.saveAs = QtWidgets.QAction(QtGui.QIcon("./icons/save as.gif"), "save as", self)
        self.zoomIn = QtWidgets.QAction(QtGui.QIcon("./icons/zoom in.gif"), "zoom in (Ctrl + Plus)", self)
        self.zoomIn.setShortcut(QtGui.QKeySequence.ZoomIn)
        self.zoomOut = QtWidgets.QAction(QtGui.QIcon("./icons/zoom out.gif"), "zoom out (Ctrl + Minus)", self)
        self.zoomOut.setShortcut(QtGui.QKeySequence.ZoomOut)
        self.fitCanvas = QtWidgets.QAction(QtGui.QIcon("./icons/fit.png"), "fit in view",self)
        self.line = QtWidgets.QAction(QtGui.QIcon("./icons/line.png"), "line", self)
        self.line.setCheckable(True)
        self.rectangle = QtWidgets.QAction(QtGui.QIcon("./icons/rectangle.png"), "rectangle", self)
        self.rectangle.setCheckable(True)
        self.arc = QtWidgets.QAction(QtGui.QIcon("./icons/arc.png"), "arc", self)
        self.arc.setCheckable(True)
        self.pan = QtWidgets.QAction(QtGui.QIcon("./icons/move.png"), "pan", self)
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
        self.editPixInfo = QtWidgets.QLabel(self)
        self.editPixInfo.setAlignment(QtCore.Qt.AlignRight)
        self.statusBar.addPermanentWidget(self.editPixInfo)
        self.setStatusBar(self.statusBar)
        self.setCentralWidget(self.mainSplitter)
        self.mainSplitter.setContentsMargins(2,2,0,0)
        self.setWindowTitle("QtRHEED")

        #Toolbar Connections
        self.open.triggered.connect(lambda path: self.openImage(path=self.getImgPath()))
        self.zoomIn.triggered.connect(self.canvas.zoomIn)
        self.zoomOut.triggered.connect(self.canvas.zoomOut)
        self.fitCanvas.triggered.connect(self.canvas.fitCanvas)
        self.line.triggered.connect(lambda cursormode: self.toggleCanvasMode(cursormode="line"))
        self.rectangle.triggered.connect(lambda cursormode: self.toggleCanvasMode(cursormode="rectangle"))
        self.arc.triggered.connect(lambda cursormode: self.toggleCanvasMode(cursormode="arc"))
        self.pan.triggered.connect(lambda cursormode: self.toggleCanvasMode(cursormode="pan"))

        #Canvas Connections
        self.canvas.photoMouseMovement.connect(self.photoMouseMovement)
        self.canvas.photoMousePress.connect(self.photoMousePress)
        self.canvas.photoMouseRelease.connect(self.photoMouseRelease)
        self.canvas.photoMouseDoubleClick.connect(self.photoMouseDoubleClick)

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
        self.properties.clearButton.clicked.connect(self.clearAnnotations)

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
        self.cursorInfo.setAsCenterButton.clicked.connect(self.setAsCenter)
        self.cursorInfo.chooseButton.clicked.connect(self.chooseThisRegion)

        #Profile Canvas Connections
        self.scaleFactorChanged.connect(self.profile.setScaleFactor)
        self.canvas.plotLineScan.connect(self.profile.lineScan)
        self.canvas.plotIntegral.connect(self.profile.integral)
        self.canvas.plotChiScan.connect(self.profile.chiScan)

    def getScaleFactor(self):
        self.scaleFactor = float(self.properties.sensitivityEdit.text())/np.sqrt(float(self.properties.energyEdit.text()))
        self.scaleFactorChanged.emit(self.scaleFactor)

    def changeSensitivity(self,sensitivity):
        self.scaleFactor = float(sensitivity)/np.sqrt(float(self.properties.energyEdit.text()))
        self.scaleFactorChanged.emit(self.scaleFactor)

    def changeEnergy(self,energy):
        self.scaleFactor = float(self.properties.sensitivityEdit.text())/np.sqrt(float(energy))
        self.scaleFactorChanged.emit(self.scaleFactor)

    def changeAzimuth(self,azimuth):
        return

    def changeScaleBar(self,scaleBar):
        return

    def labelImage(self):
        return

    def calibrateImage(self):
        return

    def clearAnnotations(self):
        return

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
        self.properties.brightnessSlider.setValue(20)
        self.properties.blackLevelSlider.setValue(50)
        self.updateImage(self.currentPath,bitDepth = 16, enableAutoWB = self.properties.autoWBCheckBox.isChecked(), \
                       brightness = self.properties.brightnessSlider.value(),blackLevel=self.properties.blackLevelSlider.value())

    def changeWidth(self,width):
        self.properties.integralHalfWidthLabel.setText('Integral Half Width ({:3.2f} \u212B\u207B\u00B9)'.format(width/100*1))
        if not self.cursorInfo.widthEdit.text() == "":
            if self._mode == "rectangle" or self._mode == "arc":
                self.cursorInfo.widthEdit.setText('{:3.2f}'.format(width/100*1))
        self.updateDrawing()
        self.canvas.width = width/100*1 * self.scaleFactor

    def changeChiRange(self,chi):
        self.properties.chiRangeLabel.setText('Chi Range ({}\u00B0)'.format(chi))
        self.updateDrawing()
        self.canvas.span = chi

    def changeRadius(self,radius):
        self.properties.radiusLabel.setText('Radius ({:3.2f} \u212B\u207B\u00B9)'.format(radius/100*20))
        if not self.canvas._drawingArc:
            self.updateDrawing()

    def changeTiltAngle(self,tilt):
        self.properties.tiltAngleLabel.setText('Tilt Angle ({:2.1f}\u00B0)'.format(tilt/150*15))
        self.updateDrawing()
        self.canvas.tilt = tilt/10

    def applyProfileOptions(self):
        if self.canvas.canvasObject == "line":
            self.canvas.lineScanSignalEmit()
        if self.canvas.canvasObject == "rectangle":
            self.canvas.integralSignalEmit()
        if self.canvas.canvasObject == "arc":
            self.canvas.chiScanSignalEmit()

    def resetProfileOptions(self):
        self.properties.integralHalfWidthSlider.setValue(40)
        self.properties.chiRangeSlider.setValue(60)
        self.properties.radiusSlider.setValue(25)
        self.properties.tiltAngleSlider.setValue(0)
        self.applyProfileOptions()

    def editChoosedXY(self):
        return

    def editStartXY(self):
        return

    def editEndXY(self):
        return

    def editWidth(self,width):
        self.properties.integralHalfWidthSlider.setValue(int(width)*100/1)

    def setAsCenter(self):
        return

    def chooseThisRegion(self):
        return

    def getImgPath(self):
        fileDlg = QtWidgets.QFileDialog(self)
        fileDlg.setDirectory('C:/RHEED/')
        path = fileDlg.getOpenFileName()[0]
        return path

    def openImage(self,path,bitDepth = 16, enableAutoWB=False,brightness=20,blackLevel=50):
        if not path == '':
            self.restoreDefaults()
            qImg,img_array = self.read_qImage(bitDepth,path, enableAutoWB, brightness, blackLevel)
            qPixImg = QtGui.QPixmap(qImg.size())
            QtGui.QPixmap.convertFromImage(qPixImg,qImg,QtCore.Qt.MonoOnly)
            self.canvas.setPhoto(QtGui.QPixmap(qPixImg))
            self.canvas.fitCanvas()
            self.currentPath = path
            self._img = img_array
            self.imgCreated.emit(self._img)
            self.fileOpened.emit(path)
            self.toggleCanvasMode("pan")

    def updateImage(self,path,bitDepth = 16, enableAutoWB=False,brightness=20,blackLevel=50):
        qImg,img_array = self.read_qImage(bitDepth,path, enableAutoWB, brightness, blackLevel)
        qPixImg = QtGui.QPixmap(qImg.size())
        QtGui.QPixmap.convertFromImage(qPixImg,qImg,QtCore.Qt.MonoOnly)
        self.canvas.setPhoto(QtGui.QPixmap(qPixImg))
        self.clearCursorInfo()
        self._img = img_array
        self.imgCreated.emit(self._img)
        self.applyProfileOptions()

    def updateDrawing(self):
        if self.canvas.canvasObject == "rectangle":
            self.canvas.drawRect(self.canvas.start,self.canvas.end,self.properties.integralHalfWidthSlider.value()/100*1*self.scaleFactor)
        if self.canvas.canvasObject == "arc":
            self.canvas.drawArc(self.canvas.start,20/100*self.properties.radiusSlider.value()*self.scaleFactor,\
                                self.properties.integralHalfWidthSlider.value()/100*1*self.scaleFactor,self.properties.chiRangeSlider.value(),\
                                self.properties.tiltAngleSlider.value()/10)

    def restoreDefaults(self):
        self.canvas.clearCanvas()
        self.cursorInfo.choosedXYEdit.clear()
        self.cursorInfo.startXYEdit.clear()
        self.cursorInfo.endXYEdit.clear()
        self.cursorInfo.widthEdit.clear()
        self.pan.setChecked(True)
        self.properties.autoWBCheckBox.setChecked(False)
        self.properties.brightnessSlider.setValue(20)
        self.properties.blackLevelSlider.setValue(50)


    def toggleCanvasMode(self,cursormode):
        self.canvas.toggleMode(cursormode)
        if cursormode == "arc":
            self.cursorInfo.endXYLabel.setText('Length')
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
        self.cursorInfo.startXYEdit.setText('{},{}'.format(pos.x(), pos.y()))
        self.cursorInfo.endXYEdit.clear()
        if self._mode == "rectangle" or self._mode == "arc":
            self.cursorInfo.widthEdit.setText('{:3.2f}'.format(self.properties.integralHalfWidthSlider.value()/100*1))
        elif self._mode == "line":
            self.cursorInfo.widthEdit.setText('{:3.2f}'.format(0.00))

    def photoMouseRelease(self, pos):
        if self._mode == "arc":
            self.cursorInfo.endXYEdit.setText('{}'.format(int(self.canvas.PFRadius)))
        else:
            self.cursorInfo.endXYEdit.setText('{},{}'.format(pos.x(), pos.y()))
        if self.canvas._drawingArc:
            self.properties.radiusSlider.setValue(100/20*self.canvas.PFRadius/self.scaleFactor)

    def photoMouseMovement(self, pos):
        self.editPixInfo.setText('x = %d, y = %d' % (pos.x(), pos.y()))
        if self.canvas._drawingArc:
            self.properties.radiusSlider.setValue(100/20*self.canvas.PFRadius/self.scaleFactor)

    def photoMouseDoubleClick(self, pos):
        self.cursorInfo.choosedXYEdit.setText('{},{}'.format(pos.x(), pos.y()))
        self.cursorInfo.intensityEdit.setText('{:3.2f}'.format(self._img[pos.y(), pos.x()]/np.amax(np.amax(self._img))))

    def read_qImage(self,bit_depth,img_path,EnableAutoWB, Brightness, UserBlack):
        img_raw = rawpy.imread(img_path)
        img_rgb = img_raw.postprocess(demosaic_algorithm=rawpy.DemosaicAlgorithm.AHD, output_bps = bit_depth, use_auto_wb = EnableAutoWB,bright=Brightness/100,user_black=UserBlack)
        img_bw = (0.21*img_rgb[:,:,0])+(0.72*img_rgb[:,:,1])+(0.07*img_rgb[:,:,2])
        img_array = img_bw[self.image_crop[0]:self.image_crop[1],self.image_crop[2]:self.image_crop[3]]
        if bit_depth == 16:
            img_array = np.uint8(img_array/256)
        if bit_depth == 8:
            img_array = np.uint8(img_array)
        qImg = QtGui.QImage(img_array,img_array.shape[1],img_array.shape[0],img_array.shape[1], QtGui.QImage.Format_Grayscale8)
        return qImg, img_array
