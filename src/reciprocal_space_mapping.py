from process import Image, Convertor, ReciprocalSpaceMap
from PyQt6 import QtCore, QtWidgets, QtGui
import configparser
import os
import profile_chart

class Window(QtCore.QObject):
    #Public Signals
    STATUS_REQUESTED = QtCore.pyqtSignal()
    PROGRESS_ADVANCE = QtCore.pyqtSignal(int,int,int)
    PROGRESS_END = QtCore.pyqtSignal()
    SHOW_3D_GRAPH = QtCore.pyqtSignal(str)
    SHOW_2D_CONTOUR = QtCore.pyqtSignal(str,bool,float,float,float,float,int,str)
    FONTS_CHANGED = QtCore.pyqtSignal(str,int)
    DRAW_LINE_REQUESTED = QtCore.pyqtSignal(QtCore.QPointF,QtCore.QPointF,bool)
    DRAW_RECT_REQUESTED = QtCore.pyqtSignal(QtCore.QPointF,QtCore.QPointF,float,bool)
    REFRESH_CANVAS = QtCore.pyqtSignal(str,list)
    CONNECT_TO_CANVAS = QtCore.pyqtSignal()
    STOP_WORKER = QtCore.pyqtSignal()

    def __init__(self):
        super(Window,self).__init__()
        self.twoDimensionalMappingRegion = [0,0,0,0,0]
        self.config = configparser.ConfigParser()
        dirname = os.path.dirname(__file__)
        self.config.read(os.path.join(dirname,'configuration.ini'))
        self.image_worker = Image()
        self.convertor_worker = Convertor()

    def refresh(self,config):
        self.config = config
        try:
            self.chart.refresh(config)
        except:
            pass

    def main(self,path):
        self.levelMin = 0
        self.levelMax = 100
        self.numberOfContourLevels = 5
        self.range = "5"
        self.startIndex = "0"
        self.endIndex = "100"
        self.defaultFileName = "2D_map"
        self.normalization_factor = 1
        self.path = os.path.dirname(path)
        self.extension = os.path.splitext(path)[1]
        self.currentSource = self.path
        self.currentOffset = self.path
        self.currentDestination = self.currentSource
        self.Dialog = QtWidgets.QWidget()
        self.Grid = QtWidgets.QGridLayout(self.Dialog)
        self.LeftFrame = QtWidgets.QFrame()
        self.RightFrame = QtWidgets.QFrame()
        self.LeftGrid = QtWidgets.QGridLayout(self.LeftFrame)
        self.RightGrid = QtWidgets.QGridLayout(self.RightFrame)
        self.hSplitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        self.hSplitter.addWidget(self.LeftFrame)
        self.hSplitter.addWidget(self.RightFrame)
        self.hSplitter.setStretchFactor(0,1)
        self.hSplitter.setStretchFactor(1,1)
        self.hSplitter.setCollapsible(0,False)
        self.hSplitter.setCollapsible(1,False)
        self.leftScroll = QtWidgets.QScrollArea(self.hSplitter)
        self.chooseSource = QtWidgets.QGroupBox("Source Directory")
        self.sourceGrid = QtWidgets.QGridLayout(self.chooseSource)
        self.sourceGrid.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.chooseSourceLabel = QtWidgets.QLabel("The source directory is:\n"+self.currentSource)
        self.chooseSourceButton = QtWidgets.QPushButton("Browse...")
        self.chooseSourceButton.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed,QtWidgets.QSizePolicy.Policy.Fixed)
        self.chooseSourceButton.clicked.connect(self.choose_source)
        self.sourceGrid.addWidget(self.chooseSourceLabel,0,0)
        self.sourceGrid.addWidget(self.chooseSourceButton,0,1)
        self.chooseDestination = QtWidgets.QGroupBox("Save Options")
        self.destinationGrid = QtWidgets.QGridLayout(self.chooseDestination)
        self.chooseDestinationLabel = QtWidgets.QLabel("The save destination is:\n"+self.currentSource)
        self.destinationNameLabel = QtWidgets.QLabel("The file name is:")
        self.destinationNameEdit = QtWidgets.QLineEdit(self.defaultFileName)
        self.fileTypeLabel = QtWidgets.QLabel("The file format is:")
        self.fileType = QtWidgets.QComboBox()
        self.fileType.addItem(".txt",".txt")
        self.fileType.addItem(".xlsx",".xlsx")
        self.azimuthRange = QtWidgets.QLabel("Azimuth range:")
        self.azimuthRangeCombo = QtWidgets.QComboBox()
        self.azimuthRangeCombo.addItem("0~180",180)
        self.azimuthRangeCombo.addItem("0~360",360)
        self.normalizationMethod = QtWidgets.QLabel("Normalization method:")
        self.normalizationMethodCombo = QtWidgets.QComboBox()
        self.normalizationMethodCombo.addItem("line profile peak",2)
        self.normalizationMethodCombo.addItem("none",0)
        self.normalizationMethodCombo.addItem("global maximum",1)
        self.normalizationMethodCombo.addItem("image maximum",3)
        self.normalizationMethodCombo.currentTextChanged.connect(self.normalization_method_changed)
        self.centralisationMethod = QtWidgets.QLabel("Centralisation method:")
        self.centralisationMethodCombo = QtWidgets.QComboBox()
        self.centralisationMethodCombo.addItem("shift center to profile peak",1)
        self.centralisationMethodCombo.addItem("none",0)
        self.centralisationMethodCombo.addItem("shift center to region center",2)
        self.centralisationMethodCombo.currentTextChanged.connect(self.centralisation_method_changed)
        self.saveResultsLabel = QtWidgets.QLabel("Save Results?")
        self.saveResults = QtWidgets.QCheckBox()
        self.saveResults.setChecked(False)
        self.synchronizeLabel = QtWidgets.QLabel("Synchronize View?")
        self.synchronize = QtWidgets.QCheckBox()
        self.synchronize.setChecked(False)
        self.synchronize.stateChanged.connect(self.sync_state_changed)
        self.sleepTimeLabel = QtWidgets.QLabel("Sleep Time (s)")
        self.sleepTimeEdit = QtWidgets.QLineEdit("1")
        self.sleepTimeEdit.setEnabled(False)
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
        self.chooseDestinationButton.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed,QtWidgets.QSizePolicy.Policy.Fixed)
        self.chooseDestinationButton.clicked.connect(self.choose_destination)
        self.destinationGrid.addWidget(self.chooseDestinationLabel,0,0)
        self.destinationGrid.addWidget(self.chooseDestinationButton,0,1)
        self.destinationGrid.addWidget(self.destinationNameLabel,1,0)
        self.destinationGrid.addWidget(self.destinationNameEdit,1,1)
        self.destinationGrid.addWidget(self.fileTypeLabel,2,0)
        self.destinationGrid.addWidget(self.fileType,2,1)
        self.destinationGrid.addWidget(self.coordinateLabel,3,0)
        self.destinationGrid.addWidget(self.coordinateFrame,3,1)
        self.destinationGrid.addWidget(self.azimuthRange,4,0)
        self.destinationGrid.addWidget(self.azimuthRangeCombo,4,1)
        self.destinationGrid.addWidget(self.normalizationMethod,5,0)
        self.destinationGrid.addWidget(self.normalizationMethodCombo,5,1)
        self.destinationGrid.addWidget(self.centralisationMethod,6,0)
        self.destinationGrid.addWidget(self.centralisationMethodCombo,6,1)
        self.destinationGrid.addWidget(self.saveResultsLabel,7,0)
        self.destinationGrid.addWidget(self.saveResults,7,1)
        self.destinationGrid.addWidget(self.synchronizeLabel,8,0)
        self.destinationGrid.addWidget(self.synchronize,8,1)
        self.destinationGrid.addWidget(self.sleepTimeLabel,9,0)
        self.destinationGrid.addWidget(self.sleepTimeEdit,9,1)
        self.destinationGrid.setAlignment(self.chooseDestinationButton,QtCore.Qt.AlignmentFlag.AlignRight)
        self.parametersBox = QtWidgets.QGroupBox("Image Options")
        self.parametersGrid = QtWidgets.QGridLayout(self.parametersBox)
        self.startImageIndexLabel = QtWidgets.QLabel("Start Image Index")
        self.startImageIndexEdit = QtWidgets.QLineEdit(self.startIndex)
        self.endImageIndexLabel = QtWidgets.QLabel("End Image Index")
        self.endImageIndexEdit = QtWidgets.QLineEdit(self.endIndex)

        self.chooseOffset = QtWidgets.QGroupBox("Offset File Directory")
        self.offsetGrid = QtWidgets.QGridLayout(self.chooseOffset)
        self.offsetGrid.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.chooseOffsetLabel = QtWidgets.QLabel("The offset file directory is:\n"+self.currentOffset)
        self.chooseOffsetButton = QtWidgets.QPushButton("Browse...")
        self.chooseOffsetButton.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed,QtWidgets.QSizePolicy.Policy.Fixed)
        self.chooseOffsetButton.clicked.connect(self.choose_offset)
        self.offsetGrid.addWidget(self.chooseOffsetLabel,0,0)
        self.offsetGrid.addWidget(self.chooseOffsetButton,0,1)

        self.dimensionLabel = QtWidgets.QLabel("Choose Type:")
        self.dimension = QtWidgets.QButtonGroup()
        self.dimension.setExclusive(True)
        self.dimensionFrame = QtWidgets.QFrame()
        self.coordnateGrid = QtWidgets.QGridLayout(self.dimensionFrame)
        self.twoD = QtWidgets.QCheckBox("2D")
        self.threeD = QtWidgets.QCheckBox("3D")
        self.poleFigure = QtWidgets.QCheckBox("Pole Figure")
        self.twoD.setChecked(True)
        self.twoD.stateChanged.connect(self.two_dimension_changed)
        self.threeD.stateChanged.connect(self.three_dimension_changed)
        self.poleFigure.stateChanged.connect(self.pole_figure_check_changed)
        self.coordnateGrid.addWidget(self.twoD,0,0)
        self.coordnateGrid.addWidget(self.threeD,0,1)
        self.coordnateGrid.addWidget(self.poleFigure,0,2)
        self.dimension.addButton(self.twoD)
        self.dimension.addButton(self.threeD)
        self.dimension.addButton(self.poleFigure)
        self.rangeLabel = QtWidgets.QLabel("Range (\u212B\u207B\u00B9)")
        self.rangeEdit = QtWidgets.QLineEdit(self.range)
        self.rangeEdit.setEnabled(False)
        self.groupingLabel = QtWidgets.QLabel("Bin Width (px):")
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
        #self.appearance.setMaximumHeight(100)
        self.appearanceGrid = QtWidgets.QGridLayout(self.appearance)
        self.fontListLabel = QtWidgets.QLabel("Change Font")
        self.fontList = QtWidgets.QFontComboBox()
        self.fontList.setCurrentFont(QtGui.QFont("Arial"))
        self.fontList.currentFontChanged.connect(self.refresh_font_name)
        self.fontSizeLabel = QtWidgets.QLabel("Adjust Font Size ({})".format(12))
        self.fontSizeSlider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.fontSizeSlider.setMinimum(1)
        self.fontSizeSlider.setMaximum(100)
        self.fontSizeSlider.setValue(12)
        self.fontSizeSlider.valueChanged.connect(self.refresh_font_size)
        self.appearanceGrid.addWidget(self.fontListLabel,0,0)
        self.appearanceGrid.addWidget(self.fontList,0,1)
        self.appearanceGrid.addWidget(self.fontSizeLabel,1,0)
        self.appearanceGrid.addWidget(self.fontSizeSlider,1,1)

        self.plotOptions = QtWidgets.QGroupBox("Contour Plot Options")
        self.plotOptionsGrid = QtWidgets.QGridLayout(self.plotOptions)
        self.colormapLabel = QtWidgets.QLabel("Colormap")
        self.colormap = QtWidgets.QComboBox()
        self.colormap.addItem("jet","jet")
        self.colormap.addItem("hsv","hsv")
        self.colormap.addItem("rainbow","rainbow")
        self.colormap.addItem("nipy_spectral","nipy_spectral")
        self.levelMinLabel = QtWidgets.QLabel("Level Min ({})".format(self.levelMin/100))
        self.levelMinSlider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.levelMinSlider.setMinimum(0)
        self.levelMinSlider.setMaximum(100)
        self.levelMinSlider.setValue(self.levelMin)
        self.levelMinSlider.valueChanged.connect(self.refresh_level_min)
        self.levelMaxLabel = QtWidgets.QLabel("Level Max ({})".format(self.levelMax/100))
        self.levelMaxSlider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.levelMaxSlider.setMinimum(0)
        self.levelMaxSlider.setMaximum(100)
        self.levelMaxSlider.setValue(self.levelMax)
        self.levelMaxSlider.valueChanged.connect(self.refresh_level_max)
        self.radiusMinLabel = QtWidgets.QLabel("Radius Min ({})".format(0.0))
        self.radiusMinSlider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.radiusMinSlider.setMinimum(0)
        self.radiusMinSlider.setMaximum(1000)
        self.radiusMinSlider.setValue(0)
        self.radiusMinSlider.valueChanged.connect(self.refresh_radius_min)
        self.radiusMaxLabel = QtWidgets.QLabel("Radius Max ({})".format(10.0))
        self.radiusMaxSlider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.radiusMaxSlider.setMinimum(0)
        self.radiusMaxSlider.setMaximum(1000)
        self.radiusMaxSlider.setValue(1000)
        self.radiusMaxSlider.valueChanged.connect(self.refresh_radius_max)
        self.numberOfContourLevelsLabel = QtWidgets.QLabel("Number of Levels ({})".format(self.numberOfContourLevels))
        self.numberOfContourLevelsSlider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.numberOfContourLevelsSlider.setMinimum(5)
        self.numberOfContourLevelsSlider.setMaximum(100)
        self.numberOfContourLevelsSlider.setValue(self.numberOfContourLevels)
        self.numberOfContourLevelsSlider.valueChanged.connect(self.refresh_number_of_contour_levels)
        self.Show3DGraphButton = QtWidgets.QPushButton("Show 3D Surface")
        self.Show3DGraphButton.setEnabled(False)
        self.Show3DGraphButton.clicked.connect(self.show_3D_graph_button_clicked)
        self.Show2DContourButton = QtWidgets.QPushButton("Show 2D Contour")
        self.Show2DContourButton.setEnabled(False)
        self.Show2DContourButton.clicked.connect(self.show_2D_contour_button_clicked)
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
        self.statusGrid = QtWidgets.QGridLayout(self.statusBar)
        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setVisible(False)
        self.progressBar.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.progressBarSizePolicy = self.progressBar.sizePolicy()
        self.progressBarSizePolicy.setRetainSizeWhenHidden(True)
        self.progressBarSizePolicy.setHorizontalPolicy(QtWidgets.QSizePolicy.Policy.Expanding)
        self.progressBar.setSizePolicy(self.progressBarSizePolicy)
        self.PROGRESS_ADVANCE.connect(self.progress)
        self.PROGRESS_END.connect(self.progress_reset)
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
        self.statusGrid.setAlignment(self.progressBar,QtCore.Qt.AlignmentFlag.AlignRight)
        self.ButtonBox = QtWidgets.QDialogButtonBox()
        self.ButtonBox.addButton("Start",QtWidgets.QDialogButtonBox.ButtonRole.ActionRole)
        self.ButtonBox.addButton("Stop",QtWidgets.QDialogButtonBox.ButtonRole.ActionRole)
        self.ButtonBox.addButton("Reset",QtWidgets.QDialogButtonBox.ButtonRole.ResetRole)
        self.ButtonBox.addButton("Quit",QtWidgets.QDialogButtonBox.ButtonRole.DestructiveRole)
        self.ButtonBox.setCenterButtons(True)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[0].clicked.\
            connect(self.start)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[1].clicked. \
            connect(self.stop)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[1].setEnabled(False)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[2].clicked.\
            connect(self.reset)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[3].clicked.\
            connect(self.reject)
        self.chart = profile_chart.ProfileChart(self.config)
        self.FONTS_CHANGED.connect(self.chart.adjust_fonts)
        self.chart.set_fonts(self.fontList.currentFont().family(),self.fontSizeSlider.value())
        self.kperpLabel = QtWidgets.QLabel("")
        self.LeftGrid.addWidget(self.chooseSource,0,0)
        self.LeftGrid.addWidget(self.chooseDestination,1,0)
        self.LeftGrid.addWidget(self.chooseOffset,2,0)
        self.LeftGrid.addWidget(self.parametersBox,3,0)
        self.LeftGrid.addWidget(self.appearance,4,0)
        self.LeftGrid.addWidget(self.plotOptions,5,0)
        self.LeftGrid.addWidget(self.ButtonBox,6,0)
        self.RightGrid.addWidget(self.kperpLabel,0,0)
        self.vSplitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        self.vSplitter.addWidget(self.chart)
        self.vSplitter.addWidget(self.statusBar)
        self.vSplitter.setStretchFactor(0,1)
        self.vSplitter.setStretchFactor(1,1)
        self.vSplitter.setCollapsible(0,False)
        self.vSplitter.setCollapsible(1,False)
        self.RightGrid.addWidget(self.vSplitter,2,0)
        self.RightGrid.addWidget(self.progressBar,3,0)
        self.Grid.addWidget(self.hSplitter,0,0)
        self.leftScroll.setWidget(self.LeftFrame)
        self.leftScroll.setWidgetResizable(True)
        self.leftScroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.Dialog.setWindowTitle("Reciprocal Space Mapping")
        self.Dialog.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        self.Dialog.showMaximized()

    def show_3D_graph_button_clicked(self):
        self.SHOW_3D_GRAPH.emit(self.graphTextPath)

    def show_2D_contour_button_clicked(self):
        self.SHOW_2D_CONTOUR.emit(self.graphTextPath, False, self.levelMinSlider.value()/100,self.levelMaxSlider.value()/100*self.normalization_factor,\
                                self.radiusMinSlider.value()/100,self.radiusMaxSlider.value()/100,self.numberOfContourLevelsSlider.value(),\
                                self.colormap.currentText())

    def three_dimension_changed(self,state):
        if state == 0:
            self.rangeEdit.setEnabled(False)
            self.grouping.setEnabled(False)
        elif state ==2:
            self.rangeEdit.setEnabled(True)
            self.grouping.setEnabled(True)
            self.destinationNameEdit.setText("3D_map")

    def two_dimension_changed(self,state):
        if state == 0:
            self.plotOptions.setEnabled(False)
        elif state ==2:
            self.plotOptions.setEnabled(True)
            self.destinationNameEdit.setText("2D_map")

    def centralisation_method_changed(self, text):
        if text == "none":
            self.azimuthRangeCombo.setCurrentText("0~180")
            self.polar.setChecked(True)
            self.cartesian.setEnabled(False)
        else:
            self.coordinateFrame.setEnabled(True)
            self.cartesian.setEnabled(True)

    def normalization_method_changed(self,text):
        if text == "none":
            self.normalization_factor = 255
        else:
            self.normalization_factor = 1
    
    def sync_state_changed(self,state):
        if state == 0:
            self.sleepTimeEdit.setEnabled(False)
        elif state ==2:
            self.sleepTimeEdit.setEnabled(True)

    def pole_figure_check_changed(self,state):
        if state == 0:
            self.plotOptions.setEnabled(False)
            self.centralisationMethodCombo.setEnabled(True)
            self.cartesian.setEnabled(True)
        elif state == 2:
            self.polar.setChecked(True)
            self.cartesian.setEnabled(False)
            self.plotOptions.setEnabled(True)
            self.centralisationMethodCombo.setEnabled(False)
            self.destinationNameEdit.setText("pole_figure")

    def update_log(self,message):
        self.logBox.append(QtCore.QTime.currentTime().toString("hh:mm:ss")+"\u00A0\u00A0\u00A0\u00A0"+message)

    def update_chart(self,RC,I,type="arc"):
        self.chart.add_chart(RC,I,type=type)

    def file_saved(self,path):
        self.Show3DGraphButton.setEnabled(True)
        self.Show2DContourButton.setEnabled(True)
        self.graphTextPath = path
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[0].setEnabled(True)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[1].setEnabled(False)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[2].setEnabled(True)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[3].setEnabled(True)
        self.chooseDestination.setEnabled(True)
        self.chooseSource.setEnabled(True)
        self.chooseOffset.setEnabled(True)
        self.parametersBox.setEnabled(True)

    def process_finished(self):
        self.thread.quit()
        if self.thread.isRunning():
            self.thread.terminate()
            self.thread.wait()
        if self.saveResults.isChecked():
            self.Show3DGraphButton.setEnabled(True)
            self.Show2DContourButton.setEnabled(True)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[0].setEnabled(True)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[1].setEnabled(False)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[2].setEnabled(True)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[3].setEnabled(True)
        self.chooseDestination.setEnabled(True)
        self.chooseSource.setEnabled(True)
        self.chooseOffset.setEnabled(True)
        self.parametersBox.setEnabled(True)

    def set_chart_title(self,text):
        self.kperpLabel.setText(text)

    def prepare(self):
        self.STATUS_REQUESTED.emit()
        self.windowDefault = dict(self.config['windowDefault'].items())
        self.logBox.clear()
        self.Show3DGraphButton.setEnabled(False)
        self.Show2DContourButton.setEnabled(False)
        if self.status["startX"] == "" or self.status["startY"] == "" or self.status["endX"] == "" or \
                self.status["endY"] == "" \
                or self.status["width"] =="": pass
        else:
            self.logBox.append(QtCore.QTime.currentTime().toString("hh:mm:ss")+"\u00A0\u00A0\u00A0\u00A0Ready to Start!")
        path = os.path.join(self.currentSource,'*'+self.extension)
        startIndex = int(self.startImageIndexEdit.text())
        endIndex = int(self.endImageIndexEdit.text())
        analysisRange = float(self.rangeEdit.text())
        saveFileName = self.destinationNameEdit.text()
        fileType = self.fileType.currentData()
        self.reciprocal_space_worker = ReciprocalSpaceMap(self.status,path,self.windowDefault,self.poleFigure.isChecked(),self.azimuthRangeCombo.currentData(),\
                                                          self.normalizationMethodCombo.currentData(),self.centralisationMethodCombo.currentData(),self.saveResults.isChecked(),self.twoD.isChecked(),self.cartesian.isChecked(),\
                                                          startIndex,endIndex,analysisRange,self.currentDestination,saveFileName,fileType,self.grouping.value(),self.synchronize.isChecked(),float(self.sleepTimeEdit.text()),self.currentOffset)
        self.reciprocal_space_worker.PROGRESS_ADVANCE.connect(self.progress)
        self.reciprocal_space_worker.PROGRESS_END.connect(self.progress_reset)
        self.reciprocal_space_worker.CONNECT_TO_CANVAS.connect(self.CONNECT_TO_CANVAS)
        self.reciprocal_space_worker.UPDATE_LOG.connect(self.update_log)
        self.reciprocal_space_worker.UPDATE_CHART.connect(self.update_chart)
        self.reciprocal_space_worker.FILE_SAVED.connect(self.file_saved)
        self.reciprocal_space_worker.SET_TITLE.connect(self.set_chart_title)
        self.reciprocal_space_worker.DRAW_LINE_REQUESTED.connect(self.DRAW_LINE_REQUESTED)
        self.reciprocal_space_worker.DRAW_RECT_REQUESTED.connect(self.DRAW_RECT_REQUESTED)
        self.reciprocal_space_worker.REFRESH_CANVAS.connect(self.REFRESH_CANVAS)
        self.reciprocal_space_worker.ERROR.connect(self.raise_error)
        self.reciprocal_space_worker.ATTENTION.connect(self.raise_attention)
        self.reciprocal_space_worker.ABORTED.connect(self.worker_aborted)
        self.reciprocal_space_worker.FINISHED.connect(self.process_finished)

        self.thread = QtCore.QThread()
        self.reciprocal_space_worker.moveToThread(self.thread)
        self.thread.started.connect(self.reciprocal_space_worker.run)
        self.STOP_WORKER.connect(self.reciprocal_space_worker.stop)

    def start(self):
        self.prepare()
        self.thread.start()
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[0].setEnabled(False)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[1].setEnabled(True)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[2].setEnabled(False)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[3].setEnabled(False)
        self.chooseDestination.setEnabled(False)
        self.chooseSource.setEnabled(False)
        self.chooseOffset.setEnabled(False)
        self.parametersBox.setEnabled(False)

    def stop(self):
        self.STOP_WORKER.emit()
        if self.thread.isRunning():
            self.thread.terminate()
            self.thread.wait()
        
    def worker_aborted(self):
        self.update_log("Process aborted!")
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[0].setEnabled(True)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[1].setEnabled(False)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[2].setEnabled(True)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[3].setEnabled(True)
        self.chooseDestination.setEnabled(True)
        self.chooseSource.setEnabled(True)
        self.chooseOffset.setEnabled(True)
        self.parametersBox.setEnabled(True)
        self.progress_reset()

    def reset(self):
        self.levelMin = 0
        self.levelMax = 100
        self.numberOfContourLevels = 5
        self.currentSource = self.path
        self.currentOffset = self.path
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
        self.azimuthRangeCombo.setCurrentText("0~180")
        self.normalizationMethodCombo.setCurrentText("own peak")
        self.centralisationMethodCombo.setCurrentText("center at peak")
        self.logBox.clear()
        self.logBox.append(QtCore.QTime.currentTime().toString("hh:mm:ss")+"\u00A0\u00A0\u00A0\u00A0Reset Successful!")
        self.logBox.append(QtCore.QTime.currentTime().toString("hh:mm:ss")+"\u00A0\u00A0\u00A0\u00A0Ready to Start!")

    def reject(self):
        self.Dialog.close()

    def choose_source(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(None,"choose source directory",self.currentSource,QtWidgets.QFileDialog.ShowDirsOnly)
        self.currentSource = path
        self.chooseSourceLabel.setText("The source directory is:\n"+self.currentSource)

    def choose_offset(self):
        path = QtWidgets.QFileDialog.getOpenFileName(None,"choose the offset file",self.currentOffset,filter="Excel (*.xlsx)")[0]
        self.currentOffset = path
        self.chooseOffsetLabel.setText("The offset file directory is:\n"+self.currentOffset)

    def choose_destination(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(None,"choose save destination",self.currentDestination,QtWidgets.QFileDialog.ShowDirsOnly)
        self.currentDestination = path
        self.chooseDestinationLabel.setText("The save destination is:\n"+self.currentDestination)

    def refresh_level_min(self):
        self.levelMin = self.levelMinSlider.value()
        self.levelMinLabel.setText("Level Min ({})".format(self.levelMin/100))
        if self.levelMinSlider.value() > self.levelMaxSlider.value():
            self.levelMaxSlider.setValue(self.levelMinSlider.value())

    def refresh_level_max(self):
        self.levelMax = self.levelMaxSlider.value()
        self.levelMaxLabel.setText("Level Max ({})".format(self.levelMax/100))
        if self.levelMinSlider.value() > self.levelMaxSlider.value():
            self.levelMinSlider.setValue(self.levelMaxSlider.value())

    def refresh_radius_min(self):
        self.radiusMinLabel.setText("Radius Min ({})".format(self.radiusMinSlider.value()/100))
        if self.radiusMinSlider.value() > self.radiusMaxSlider.value():
            self.radiusMaxSlider.setValue(self.radiusMinSlider.value())

    def refresh_radius_max(self):
        self.radiusMaxLabel.setText("Radius Max ({})".format(self.radiusMaxSlider.value()/100))
        if self.radiusMinSlider.value() > self.radiusMaxSlider.value():
            self.radiusMinSlider.setValue(self.radiusMaxSlider.value())

    def refresh_number_of_contour_levels(self):
        self.numberOfContourLevels = self.numberOfContourLevelsSlider.value()
        self.numberOfContourLevelsLabel.setText("Number of Levels ({})".format(self.numberOfContourLevels))

    def set_status(self,status):
        self.status = status

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

    def progress(self,min,max,val):
        self.progressBar.setVisible(True)
        self.progressBar.setMinimum(min)
        self.progressBar.setMaximum(max)
        self.progressBar.setValue(val)

    def progress_reset(self):
        self.progressBar.reset()
        self.progressBar.setVisible(False)

    def refresh_font_size(self):
        self.fontSizeLabel.setText("Adjust Font Size ({})".format(self.fontSizeSlider.value()))
        self.FONTS_CHANGED.emit(self.fontList.currentFont().family(),self.fontSizeSlider.value())

    def refresh_font_name(self):
        self.FONTS_CHANGED.emit(self.fontList.currentFont().family(),self.fontSizeSlider.value())

