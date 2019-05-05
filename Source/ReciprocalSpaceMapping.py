from PyQt5 import QtCore, QtWidgets, QtGui
import os
import configparser
from Process import Image, Convertor, ReciprocalSpaceMap
import ProfileChart

class Window(QtCore.QObject):
    #Public Signals
    StatusRequested = QtCore.pyqtSignal()
    progressAdvance = QtCore.pyqtSignal(int,int,int)
    progressEnd = QtCore.pyqtSignal()
    Show3DGraph = QtCore.pyqtSignal(str)
    Show2DContour = QtCore.pyqtSignal(str,bool,float,float,float,float,int,str)
    fontsChanged = QtCore.pyqtSignal(str,int)
    drawLineRequested = QtCore.pyqtSignal(QtCore.QPointF,QtCore.QPointF,bool)
    drawRectRequested = QtCore.pyqtSignal(QtCore.QPointF,QtCore.QPointF,float,bool)
    connectToCanvas = QtCore.pyqtSignal()
    stopWorker = QtCore.pyqtSignal()

    def __init__(self):
        super(Window,self).__init__()
        self.twoDimensionalMappingRegion = [0,0,0,0,0]
        self.config = configparser.ConfigParser()
        self.config.read('./configuration.ini')
        self.image_worker = Image()
        self.convertor_worker = Convertor()

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
        self.range = "5"
        self.startIndex = "0"
        self.endIndex = "100"
        self.defaultFileName = "2D_Map"
        self.path = os.path.dirname(path)
        self.currentSource = self.path
        self.currentDestination = self.currentSource
        self.Dialog = QtWidgets.QWidget()
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
        self.centeredCheck.setChecked(True)
        self.saveResultsLabel = QtWidgets.QLabel("Save Results?")
        self.saveResults = QtWidgets.QCheckBox()
        self.saveResults.setChecked(False)
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
        self.destinationGrid.addWidget(self.saveResultsLabel,5,0)
        self.destinationGrid.addWidget(self.saveResults,5,1)
        self.destinationGrid.setAlignment(self.chooseDestinationButton,QtCore.Qt.AlignRight)
        self.parametersBox = QtWidgets.QGroupBox("Choose Image")
        self.parametersBox.setStyleSheet('QGroupBox::title {color:blue;}')
        self.parametersGrid = QtWidgets.QGridLayout(self.parametersBox)
        self.startImageIndexLabel = QtWidgets.QLabel("Start Image Index")
        self.startImageIndexEdit = QtWidgets.QLineEdit(self.startIndex)
        self.endImageIndexLabel = QtWidgets.QLabel("End Image Index")
        self.endImageIndexEdit = QtWidgets.QLineEdit(self.endIndex)

        self.dimensionLabel = QtWidgets.QLabel("Choose Type:")
        self.dimension = QtWidgets.QButtonGroup()
        self.dimension.setExclusive(True)
        self.dimensionFrame = QtWidgets.QFrame()
        self.coordnateGrid = QtWidgets.QGridLayout(self.dimensionFrame)
        self.twoD = QtWidgets.QCheckBox("2D")
        self.threeD = QtWidgets.QCheckBox("3D")
        self.poleFigure = QtWidgets.QCheckBox("Pole Figure")
        self.twoD.setChecked(True)
        self.threeD.stateChanged.connect(self.dimensionChanged)
        self.poleFigure.stateChanged.connect(self.poleFigureCheckChanged)
        self.coordnateGrid.addWidget(self.twoD,0,0)
        self.coordnateGrid.addWidget(self.threeD,0,1)
        self.coordnateGrid.addWidget(self.poleFigure,0,2)
        self.dimension.addButton(self.twoD)
        self.dimension.addButton(self.threeD)
        self.dimension.addButton(self.poleFigure)
        self.rangeLabel = QtWidgets.QLabel("Range (\u212B\u207B\u00B9)")
        self.rangeEdit = QtWidgets.QLineEdit(self.range)
        self.rangeEdit.setEnabled(False)
        self.groupingLabel = QtWidgets.QLabel("Bin Width:")
        self.grouping = QtWidgets.QSpinBox()
        self.grouping.setMinimum(1)
        self.grouping.setMaximum(50)
        self.grouping.setSingleStep(1)
        self.grouping.setValue(5)
        self.grouping.setEnabled(False)
        self.parametersGrid.addWidget(self.dimensionLabel,0,0)
        self.parametersGrid.addWidget(self.dimensionFrame,0,1)
        self.parametersGrid.addWidget(self.startImageIndexLabel,1,0)
        self.parametersGrid.addWidget(self.startImageIndexEdit,1,1)
        self.parametersGrid.addWidget(self.endImageIndexLabel,2,0)
        self.parametersGrid.addWidget(self.endImageIndexEdit,2,1)
        self.parametersGrid.addWidget(self.rangeLabel,3,0)
        self.parametersGrid.addWidget(self.rangeEdit,3,1)
        self.parametersGrid.addWidget(self.groupingLabel,4,0)
        self.parametersGrid.addWidget(self.grouping,4,1)

        self.appearance = QtWidgets.QGroupBox("Appearance")
        self.appearance.setMaximumHeight(100)
        self.appearance.setStyleSheet('QGroupBox::title {color:blue;}')
        self.appearanceGrid = QtWidgets.QGridLayout(self.appearance)
        self.fontListLabel = QtWidgets.QLabel("Change Font")
        self.fontList = QtWidgets.QFontComboBox()
        self.fontList.setCurrentFont(QtGui.QFont("Arial"))
        self.fontList.currentFontChanged.connect(self.RefreshFontName)
        self.fontSizeLabel = QtWidgets.QLabel("Adjust Font Size ({})".format(12))
        self.fontSizeLabel.setFixedWidth(160)
        self.fontSizeSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.fontSizeSlider.setMinimum(1)
        self.fontSizeSlider.setMaximum(100)
        self.fontSizeSlider.setValue(12)
        self.fontSizeSlider.valueChanged.connect(self.RefreshFontSize)
        self.appearanceGrid.addWidget(self.fontListLabel,0,0)
        self.appearanceGrid.addWidget(self.fontList,0,1)
        self.appearanceGrid.addWidget(self.fontSizeLabel,1,0)
        self.appearanceGrid.addWidget(self.fontSizeSlider,1,1)

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
        self.Show3DGraphButton = QtWidgets.QPushButton("Show 3D Surface")
        self.Show3DGraphButton.setEnabled(False)
        self.Show3DGraphButton.clicked.connect(self.Show3DGraphButtonClicked)
        self.Show2DContourButton = QtWidgets.QPushButton("Show 2D Contour")
        self.Show2DContourButton.setEnabled(False)
        self.Show2DContourButton.clicked.connect(self.Show2DContourButtonClicked)
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
        self.plotOptionsGrid.addWidget(self.Show2DContourButton,6,0)
        self.plotOptionsGrid.addWidget(self.Show3DGraphButton,6,1)
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
        self.ButtonBox.addButton("Start",QtWidgets.QDialogButtonBox.ActionRole)
        self.ButtonBox.addButton("Stop",QtWidgets.QDialogButtonBox.ActionRole)
        self.ButtonBox.addButton("Reset",QtWidgets.QDialogButtonBox.ResetRole)
        self.ButtonBox.addButton("Quit",QtWidgets.QDialogButtonBox.DestructiveRole)
        self.ButtonBox.setCenterButtons(True)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[0].clicked.\
            connect(self.Start)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[1].clicked. \
            connect(self.Stop)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[1].setEnabled(False)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[2].clicked.\
            connect(self.Reset)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[3].clicked.\
            connect(self.Reject)
        self.chart = ProfileChart.ProfileChart(self.config)
        self.fontsChanged.connect(self.chart.adjustFonts)
        self.chart.setFonts(self.fontList.currentFont().family(),self.fontSizeSlider.value())
        self.kperpLabel = QtWidgets.QLabel("")
        self.LeftGrid.addWidget(self.chooseSource,0,0)
        self.LeftGrid.addWidget(self.chooseDestination,1,0)
        self.LeftGrid.addWidget(self.parametersBox,2,0)
        self.LeftGrid.addWidget(self.appearance,3,0)
        self.LeftGrid.addWidget(self.plotOptions,4,0)
        self.LeftGrid.addWidget(self.ButtonBox,5,0)
        self.RightGrid.addWidget(self.kperpLabel,0,0)
        self.RightGrid.addWidget(self.chart,1,0)
        self.RightGrid.addWidget(self.statusBar,2,0)
        self.RightGrid.addWidget(self.progressBar,3,0)
        self.Grid.addWidget(self.LeftFrame,0,0)
        self.Grid.addWidget(self.RightFrame,0,1)
        self.Dialog.setWindowTitle("Reciprocal Space Mapping")
        self.Dialog.setWindowModality(QtCore.Qt.WindowModal)
        self.Dialog.showNormal()
        desktopRect = QtWidgets.QApplication.desktop().availableGeometry(self.Dialog)
        center = desktopRect.center()
        self.Dialog.move(center.x()-self.Dialog.width()*0.5,center.y()-self.Dialog.height()*0.5)

    def Show3DGraphButtonClicked(self):
        self.Show3DGraph.emit(self.graphTextPath)

    def Show2DContourButtonClicked(self):
        self.Show2DContour.emit(self.graphTextPath, False, self.levelMinSlider.value()/100,self.levelMaxSlider.value()/100,\
                                self.radiusMinSlider.value()/100,self.radiusMaxSlider.value()/100,self.numberOfContourLevelsSlider.value(),\
                                self.colormap.currentText())

    def dimensionChanged(self,state):
        if state == 0:
            self.rangeEdit.setEnabled(False)
            self.grouping.setEnabled(False)
            self.plotOptions.setEnabled(True)
        elif state ==2:
            self.rangeEdit.setEnabled(True)
            self.grouping.setEnabled(True)
            self.plotOptions.setEnabled(False)

    def poleFigureCheckChanged(self,state):
        if state == 0:
            self.coordinateFrame.setEnabled(True)
        elif state == 2:
            self.coordinateFrame.setEnabled(False)

    def updateLog(self,message):
        self.logBox.append(QtCore.QTime.currentTime().toString("hh:mm:ss")+"\u00A0\u00A0\u00A0\u00A0"+message)

    def updateChart(self,RC,I,type="arc"):
        self.chart.addChart(RC,I,type=type)

    def FileSaved(self,path):
        self.Show3DGraphButton.setEnabled(True)
        self.Show2DContourButton.setEnabled(True)
        self.graphTextPath = path
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[0].setEnabled(True)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[1].setEnabled(False)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[2].setEnabled(True)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[3].setEnabled(True)

    def ProcessFinished(self):
        self.Show3DGraphButton.setEnabled(True)
        self.Show2DContourButton.setEnabled(True)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[0].setEnabled(True)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[1].setEnabled(False)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[2].setEnabled(True)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[3].setEnabled(True)

    def setChartTitle(self,text):
        self.kperpLabel.setText(text)

    def prepare(self):
        self.StatusRequested.emit()
        self.windowDefault = dict(self.config['windowDefault'].items())
        self.logBox.clear()
        self.Show3DGraphButton.setEnabled(False)
        self.Show2DContourButton.setEnabled(False)
        if self.status["startX"] == "" or self.status["startY"] == "" or self.status["endX"] == "" or \
                self.status["endY"] == "" \
                or self.status["width"] =="": pass
        else:
            self.logBox.append(QtCore.QTime.currentTime().toString("hh:mm:ss")+"\u00A0\u00A0\u00A0\u00A0Ready to Start!")
        path = os.path.join(self.currentSource,'*.nef')
        startIndex = int(self.startImageIndexEdit.text())
        endIndex = int(self.endImageIndexEdit.text())
        analysisRange = float(self.rangeEdit.text())
        saveFileName = self.destinationNameEdit.text()
        fileType = self.fileType.currentData()
        self.reciprocal_space_worker = ReciprocalSpaceMap(self.status,path,self.windowDefault,self.poleFigure.isChecked(),self.centeredCheck.isChecked(),\
                                                          self.saveResults.isChecked(),self.twoD.isChecked(),self.cartesian.isChecked(),\
                                                          startIndex,endIndex,analysisRange,self.currentDestination,saveFileName,fileType,self.grouping.value())
        self.reciprocal_space_worker.progressAdvance.connect(self.progress)
        self.reciprocal_space_worker.progressEnd.connect(self.progressReset)
        self.reciprocal_space_worker.connectToCanvas.connect(self.connectToCanvas)
        self.reciprocal_space_worker.updateLog.connect(self.updateLog)
        self.reciprocal_space_worker.updateChart.connect(self.updateChart)
        self.reciprocal_space_worker.fileSaved.connect(self.FileSaved)
        self.reciprocal_space_worker.setTitle.connect(self.setChartTitle)
        self.reciprocal_space_worker.drawLineRequested.connect(self.drawLineRequested)
        self.reciprocal_space_worker.drawRectRequested.connect(self.drawRectRequested)
        self.reciprocal_space_worker.error.connect(self.Raise_Error)
        self.reciprocal_space_worker.attention.connect(self.Raise_Attention)
        self.reciprocal_space_worker.aborted.connect(self.workerAborted)
        self.reciprocal_space_worker.finished.connect(self.ProcessFinished)

        self.thread = QtCore.QThread()
        self.reciprocal_space_worker.moveToThread(self.thread)
        self.reciprocal_space_worker.finished.connect(self.thread.quit)
        self.thread.started.connect(self.reciprocal_space_worker.run)
        self.stopWorker.connect(self.reciprocal_space_worker.stop)


    def Start(self):
        self.prepare()
        self.thread.start()
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[0].setEnabled(False)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[1].setEnabled(True)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[2].setEnabled(False)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[3].setEnabled(False)

    def Stop(self):
        self.stopWorker.emit()
        if self.thread.isRunning():
            self.thread.terminate()
            self.thread.wait()

    def workerAborted(self):
        self.updateLog("Process aborted!")
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[0].setEnabled(True)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[1].setEnabled(False)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[2].setEnabled(True)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[3].setEnabled(True)
        self.progressReset()

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

    def Reject(self):
        self.Dialog.close()

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

    def RefreshFontSize(self):
        self.fontSizeLabel.setText("Adjust Font Size ({})".format(self.fontSizeSlider.value()))
        self.fontsChanged.emit(self.fontList.currentFont().family(),self.fontSizeSlider.value())

    def RefreshFontName(self):
        self.fontsChanged.emit(self.fontList.currentFont().family(),self.fontSizeSlider.value())

