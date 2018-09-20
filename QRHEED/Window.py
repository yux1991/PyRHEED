from PyQt5 import QtCore, QtGui, QtWidgets
from Canvas import *
from Browser import *
from Properties import *
from ProfileChart import *
from Cursor import *
import rawpy
import os
import numpy as np

class Window(QtWidgets.QMainWindow):

    #Public Signals
    fileOpened = QtCore.pyqtSignal(str)
    imgCreated = QtCore.pyqtSignal(np.ndarray)
    scaleFactorChanged = QtCore.pyqtSignal(float)
    labelChanged = QtCore.pyqtSignal(float,float)
    calibrationChanged = QtCore.pyqtSignal(float,float)
    progressAdvance = QtCore.pyqtSignal(int,int,int)
    progressEnd = QtCore.pyqtSignal()

    def __init__(self):

        super(Window, self).__init__()
        self.currentPath = ''
        self._mode = "pan"
        self.energy = 20
        self.azimuth = 0
        self.scaleBarLength = 5
        self.photoList = []
        self.pathList = []
        self.tabClosed = False

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
        self.setWindowTitle("QtRHEED")

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
        self.cursorInfo.setAsCenterButton.clicked.connect(self.setAsCenter)
        self.cursorInfo.chooseButton.clicked.connect(self.chooseThisRegion)

        #Profile Canvas Connections
        self.scaleFactorChanged.connect(self.profile.setScaleFactor)
        self.profile.chartMouseMovement.connect(self.photoMouseMovement)

        self.getScaleFactor()

    def progress(self,min,max,val):
        self.progressBar.setVisible(True)
        self.progressBar.setMinimum(min)
        self.progressBar.setMaximum(max)
        self.progressBar.setValue(val)

    def progressReset(self):
        self.progressBar.reset()
        self.progressBar.setVisible(False)


    def getScaleFactor(self):
        self.scaleFactor = float(self.properties.sensitivityEdit.text())/np.sqrt(float(self.properties.energyEdit.text()))
        self.scaleFactorChanged.emit(self.scaleFactor)

    def changeSensitivity(self,sensitivity):
        self.scaleFactor = float(sensitivity)/np.sqrt(float(self.properties.energyEdit.text()))
        self.scaleFactorChanged.emit(self.scaleFactor)

    def changeEnergy(self,energy):
        self.scaleFactor = float(self.properties.sensitivityEdit.text())/np.sqrt(float(energy))
        self.scaleFactorChanged.emit(self.scaleFactor)
        self.energy = float(energy)

    def changeAzimuth(self,azimuth):
        self.azimuth = float(azimuth)

    def changeScaleBar(self,scaleBar):
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
        for i in range(0,self.mainTab.count()):
            self.mainTab.widget(i).width = width/100*1 * self.scaleFactor

    def changeChiRange(self,chi):
        self.properties.chiRangeLabel.setText('Chi Range ({}\u00B0)'.format(chi))
        self.updateDrawing()
        for i in range(0,self.mainTab.count()):
            self.mainTab.widget(i).span = chi

    def changeRadius(self,radius):
        self.properties.radiusLabel.setText('Radius ({:3.2f} \u212B\u207B\u00B9)'.format(radius/100*20))
        if not self.mainTab.currentWidget()._drawingArc:
            self.updateDrawing()

    def changeTiltAngle(self,tilt):
        self.properties.tiltAngleLabel.setText('Tilt Angle ({:2.1f}\u00B0)'.format(tilt/150*15))
        self.updateDrawing()
        for i in range(0,self.mainTab.count()):
            self.mainTab.widget(i).tilt = tilt/10

    def applyProfileOptions(self):
        if self.mainTab.currentWidget().canvasObject == "line":
            self.mainTab.currentWidget().lineScanSignalEmit()
        if self.mainTab.currentWidget().canvasObject == "rectangle":
            self.mainTab.currentWidget().integralSignalEmit()
        if self.mainTab.currentWidget().canvasObject == "arc":
            self.mainTab.currentWidget().chiScanSignalEmit()

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
            canvas = Canvas(self)
            self.connectCanvas(canvas)
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
        #canvas slots
        self.zoomIn.triggered.connect(canvas.zoomIn)
        self.zoomOut.triggered.connect(canvas.zoomOut)
        self.fitCanvas.triggered.connect(canvas.fitCanvas)
        self.properties.clearButton.clicked.connect(canvas.clearAnnotations)
        self.labelChanged.connect(canvas.label)
        self.calibrationChanged.connect(canvas.calibrate)

    def disconnectCanvas(self):
        self.zoomIn.disconnect()
        self.zoomOut.disconnect()
        self.fitCanvas.disconnect()
        self.properties.clearButton.disconnect()
        self.labelChanged.disconnect()
        self.calibrationChanged.disconnect()

    def reconnectCanvas(self,canvas):
        self.zoomIn.triggered.connect(canvas.zoomIn)
        self.zoomOut.triggered.connect(canvas.zoomOut)
        self.fitCanvas.triggered.connect(canvas.fitCanvas)
        self.properties.clearButton.clicked.connect(canvas.clearAnnotations)
        self.labelChanged.connect(canvas.label)
        self.calibrationChanged.connect(canvas.calibrate)

    def updateImage(self,path,bitDepth = 16, enableAutoWB=False,brightness=20,blackLevel=50):
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
        qImg,img_array = self.read_qImage(bitDepth,path, enableAutoWB, brightness, blackLevel)
        qPixImg = QtGui.QPixmap(qImg.size())
        QtGui.QPixmap.convertFromImage(qPixImg,qImg,QtCore.Qt.MonoOnly)
        canvas.setPhoto(QtGui.QPixmap(qPixImg))
        self._img = img_array
        self.imgCreated.emit(self._img)
        self.messageLoadingImage.setText("Path of the image: "+path)
        return img_array

    def updateDrawing(self):
        if self.mainTab.currentWidget().canvasObject == "rectangle":
            self.mainTab.currentWidget().drawRect(self.mainTab.currentWidget().start,self.mainTab.currentWidget().end,self.properties.integralHalfWidthSlider.value()/100*1*self.scaleFactor)
        if self.mainTab.currentWidget().canvasObject == "arc":
            self.mainTab.currentWidget().drawArc(self.mainTab.currentWidget().start,20/100*self.properties.radiusSlider.value()*self.scaleFactor,\
                                self.properties.integralHalfWidthSlider.value()/100*1*self.scaleFactor,self.properties.chiRangeSlider.value(),\
                                self.properties.tiltAngleSlider.value()/10)

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
            self.cursorInfo.endXYEdit.setText('{}'.format(int(self.mainTab.currentWidget().PFRadius)))
        else:
            self.cursorInfo.endXYEdit.setText('{},{}'.format(pos.x(), pos.y()))
        if self.mainTab.currentWidget()._drawingArc:
            self.properties.radiusSlider.setValue(100/20*self.mainTab.currentWidget().PFRadius/self.scaleFactor)

    def photoMouseMovement(self, pos, type="canvas"):
        if type == "canvas":
            self.editPixInfo.setText('x = %d, y = %d' % (pos.x(), pos.y()))
        elif type == "chart":
            self.editPixInfo.setText('K = %3.2f, Int. = %3.2f' % (pos.x(), pos.y()))
        if self.mainTab.currentWidget()._drawingArc:
            self.properties.radiusSlider.setValue(100/20*self.mainTab.currentWidget().PFRadius/self.scaleFactor)

    def photoMouseDoubleClick(self, pos):
        self.cursorInfo.choosedXYEdit.setText('{},{}'.format(pos.x(), pos.y()))
        self.cursorInfo.intensityEdit.setText('{:3.2f}'.format(self._img[pos.y(), pos.x()]/np.amax(np.amax(self._img))))

    def keyPressEvent(self,event):
        if event.key() == QtCore.Qt.Key_Up or QtCore.Qt.Key_Down or QtCore.Qt.Key_Left or QtCore.Qt.Key_Right :
            self.mainTab.currentWidget().setFocus()
            self.mainTab.currentWidget().keyPressEvent(event)

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
