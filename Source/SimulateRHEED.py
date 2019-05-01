from PyQt5 import QtCore, QtGui, QtWidgets, QtDataVisualization
import pandas as pd
import itertools
import Process
import numpy as np
import sys
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from pymatgen.io.cif import CifParser
from pymatgen.core import structure as pgStructure
from pymatgen.core.operations import SymmOp
from pymatgen.core.lattice import Lattice

class Window(QtWidgets.QWidget,Process.Convertor):

    fontsChanged = QtCore.pyqtSignal(str,int)
    viewDirectionChanged = QtCore.pyqtSignal(int)
    progressAdvance = QtCore.pyqtSignal(int,int,int)
    progressHold = QtCore.pyqtSignal()
    progressEnd = QtCore.pyqtSignal()
    refreshPlotFonts = QtCore.pyqtSignal(str,int)
    refreshPlotFWHM = QtCore.pyqtSignal(bool)

    def __init__(self):
        super(Window,self).__init__()

    def Main(self):
        self.graph = ScatterGraph()
        self.AFF = pd.read_excel(open('AtomicFormFactors.xlsx','rb'),sheet_name="Atomic Form Factors",index_col=0)
        self.AR = pd.read_excel(open('AtomicRadii.xlsx','rb'),sheet_name="Atomic Radius",index_col=0)
        self.colors = ['magenta','cyan','green','yellow','red','black','darkGreen','darkYellow','darkCyan','darkMagenta','darkRed','darkBlue','darkGray']
        self.structure_index = 0
        self.real_space_specification_dict = {}
        self.colorSheet = {}
        self.molecule_dict = {}
        self.structure_dict = {}
        self.box = {}
        self.element_species = {}
        self.z_shift_history = {}
        self.currentDestination = ''
        self.container = QtWidgets.QWidget.createWindowContainer(self.graph)
        self.screenSize = self.graph.screen().size()
        self.container.setMinimumSize(self.screenSize.width()/2, self.screenSize.height()/2)
        self.container.setMaximumSize(self.screenSize)
        self.container.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        self.container.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.mainVLayout = QtWidgets.QVBoxLayout(self)
        self.hSplitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.controlPanel = QtWidgets.QFrame()
        self.displayPanel = QtWidgets.QFrame()
        self.vLayout = QtWidgets.QVBoxLayout(self.controlPanel)
        self.vLayout.setAlignment(QtCore.Qt.AlignTop)
        self.vLayout.setContentsMargins(0,0,0,0)
        self.vLayout_left = QtWidgets.QVBoxLayout(self.displayPanel)
        self.vLayout_left.setAlignment(QtCore.Qt.AlignTop)
        self.vLayout_left.addWidget(self.container)
        self.hSplitter.addWidget(self.displayPanel)
        self.controlPanelScroll = QtWidgets.QScrollArea(self.hSplitter)
        self.hSplitter.setStretchFactor(0,1)
        self.hSplitter.setStretchFactor(1,1)
        self.hSplitter.setCollapsible(0,False)
        self.hSplitter.setCollapsible(1,False)
        self.mainVLayout.addWidget(self.hSplitter)
        self.setWindowTitle("RHEED Simulation")
        self.setWindowModality(QtCore.Qt.WindowModal)

        self.chooseCif = QtWidgets.QGroupBox("Choose CIF")
        self.chooseCif.setStyleSheet('QGroupBox::title {color:blue;}')
        self.chooseCifGrid = QtWidgets.QGridLayout(self.chooseCif)
        self.chooseCifLabel = QtWidgets.QLabel("The path of the CIF file is:\n")
        self.chooseCifLabel.setAlignment(QtCore.Qt.AlignTop)
        self.chooseCifLabel.setWordWrap(True)
        self.chooseCifButton = QtWidgets.QPushButton("Add CIF")
        self.chooseCifButton.clicked.connect(self.getCifPath)
        self.chooseCifGrid.addWidget(self.chooseCifLabel,0,0)
        self.chooseCifGrid.addWidget(self.chooseCifButton,1,0)

        self.chooseDestination = QtWidgets.QGroupBox("Save Destination")
        self.chooseDestination.setStyleSheet('QGroupBox::title {color:blue;}')
        self.destinationGrid = QtWidgets.QGridLayout(self.chooseDestination)
        self.chooseDestinationLabel = QtWidgets.QLabel("The save destination is:\n")
        self.destinationNameLabel = QtWidgets.QLabel("The file name is:")
        self.destinationNameEdit = QtWidgets.QLineEdit('3D_data')
        self.chooseDestinationButton = QtWidgets.QPushButton("Browse...")
        self.chooseDestinationButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
        self.chooseDestinationButton.clicked.connect(self.Choose_Destination)
        self.destinationGrid.addWidget(self.chooseDestinationLabel,0,0)
        self.destinationGrid.addWidget(self.chooseDestinationButton,0,1)
        self.destinationGrid.addWidget(self.destinationNameLabel,1,0)
        self.destinationGrid.addWidget(self.destinationNameEdit,1,1)

        self.lattice_constants_box = QtWidgets.QGroupBox("Information")
        self.lattice_constants_box.setStyleSheet('QGroupBox::title {color:blue;}')
        self.lattice_constants_grid = QtWidgets.QGridLayout(self.lattice_constants_box)
        self.lattice_constants_grid.setContentsMargins(10,5,5,10)
        self.lattice_constants_label = QtWidgets.QLabel("")
        self.lattice_constants_grid.addWidget(self.lattice_constants_label,0,0)

        self.tab = QtWidgets.QTabWidget()

        self.reciprocal_range_box = QtWidgets.QWidget()
        self.reciprocal_range_grid = QtWidgets.QGridLayout(self.reciprocal_range_box)
        self.reciprocal_range_grid.setContentsMargins(5,5,5,5)
        self.reciprocal_range_grid.setAlignment(QtCore.Qt.AlignTop)
        self.number_of_steps_para_label = QtWidgets.QLabel("Number of K_para Steps:")
        self.number_of_steps_para = QtWidgets.QSpinBox()
        self.number_of_steps_para.setMinimum(1)
        self.number_of_steps_para.setMaximum(1000)
        self.number_of_steps_para.setSingleStep(1)
        self.number_of_steps_para.setValue(5)
        self.number_of_steps_para.valueChanged.connect(self.updateNumberOfStepsPara)
        self.number_of_steps_perp_label = QtWidgets.QLabel("Number of K_perp Steps:")
        self.number_of_steps_perp = QtWidgets.QSpinBox()
        self.number_of_steps_perp.setMinimum(1)
        self.number_of_steps_perp.setMaximum(1000)
        self.number_of_steps_perp.setSingleStep(1)
        self.number_of_steps_perp.setValue(5)
        self.number_of_steps_perp.valueChanged.connect(self.updateNumberOfStepsPerp)
        self.Kx_range = DoubleSlider(-1000,1000,10,-10,10,"Kx range","\u212B\u207B\u00B9",True)
        self.Ky_range = DoubleSlider(-1000,1000,10,-10,10,"Ky range","\u212B\u207B\u00B9",True)
        self.Kz_range = DoubleSlider(-1000,1000,10,0,10,"Kz range","\u212B\u207B\u00B9",False)
        self.apply_reciprocal_range = QtWidgets.QPushButton("Calculate Diffraction Pattern")
        self.apply_reciprocal_range.clicked.connect(self.updateReciprocalRange)
        self.apply_reciprocal_range.setEnabled(False)

        self.reciprocal_range_grid.addWidget(self.number_of_steps_para_label,0,0,1,1)
        self.reciprocal_range_grid.addWidget(self.number_of_steps_para,0,1,1,1)
        self.reciprocal_range_grid.addWidget(self.number_of_steps_perp_label,1,0,1,1)
        self.reciprocal_range_grid.addWidget(self.number_of_steps_perp,1,1,1,1)
        self.reciprocal_range_grid.addWidget(self.Kx_range,2,0,1,2)
        self.reciprocal_range_grid.addWidget(self.Ky_range,3,0,1,2)
        self.reciprocal_range_grid.addWidget(self.Kz_range,4,0,1,2)
        self.reciprocal_range_grid.addWidget(self.apply_reciprocal_range,7,0,1,2)
        self.KRange = [self.Kx_range.values(),self.Ky_range.values(),self.Kz_range.values()]
        self.x_linear = np.linspace(self.KRange[0][0],self.KRange[0][1],self.number_of_steps_para.value())
        self.y_linear = np.linspace(self.KRange[1][0],self.KRange[1][1],self.number_of_steps_para.value())
        self.z_linear = np.linspace(self.KRange[2][0],self.KRange[2][1],self.number_of_steps_perp.value())
        self.Kx,self.Ky,self.Kz = np.meshgrid(self.x_linear,self.y_linear,self.z_linear)
        self.tab.addTab(self.reciprocal_range_box,"Detector")

        self.plotOptions = QtWidgets.QGroupBox("Plot Options")
        self.plotOptions.setStyleSheet('QGroupBox::title {color:blue;}')
        self.plotOptionsGrid = QtWidgets.QGridLayout(self.plotOptions)
        self.load_data_button = QtWidgets.QPushButton("Load data")
        self.load_data_button.clicked.connect(self.loadData)
        self.KzIndex = DoubleSlider(0,self.number_of_steps_perp.value()-1,1,0,0,"Kz Index range")
        self.KxyIndex = DoubleSlider(0,self.number_of_steps_para.value()-1,1,0,0,"Kxy Index range")
        self.showFWHMCheckLabel = QtWidgets.QLabel("Show FWHM Contour?")
        self.showFWHMCheck = QtWidgets.QCheckBox()
        self.showFWHMCheck.setChecked(False)
        self.showFWHMCheck.stateChanged.connect(self.updateFWHMCheck)
        self.reciprocalMapfontListLabel = QtWidgets.QLabel("Font Name")
        self.reciprocalMapfontList = QtWidgets.QFontComboBox()
        self.reciprocalMapfontList.setCurrentFont(QtGui.QFont("Arial"))
        self.reciprocalMapfontList.currentFontChanged.connect(self.updatePlotFont)
        self.reciprocalMapfontSizeLabel = QtWidgets.QLabel("Font Size ({})".format(30))
        self.reciprocalMapfontSizeLabel.setFixedWidth(160)
        self.reciprocalMapfontSizeSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.reciprocalMapfontSizeSlider.setMinimum(1)
        self.reciprocalMapfontSizeSlider.setMaximum(100)
        self.reciprocalMapfontSizeSlider.setValue(30)
        self.reciprocalMapfontSizeSlider.valueChanged.connect(self.updateReciprocalMapFontSize)
        self.reciprocalMapColormapLabel = QtWidgets.QLabel("Colormap")
        self.reciprocalMapColormapCombo = QtWidgets.QComboBox()
        for colormap in plt.colormaps():
            self.reciprocalMapColormapCombo.addItem(colormap)
        self.reciprocalMapColormapCombo.setCurrentText("jet")
        self.show_XY_plot_button = QtWidgets.QPushButton("Show XY Slices")
        self.show_XY_plot_button.clicked.connect(self.showXYPlot)
        self.show_XY_plot_button.setEnabled(False)
        self.show_XZ_plot_button = QtWidgets.QPushButton("Show XZ Slices")
        self.show_XZ_plot_button.clicked.connect(self.showXZPlot)
        self.show_XZ_plot_button.setEnabled(False)
        self.show_YZ_plot_button = QtWidgets.QPushButton("Show YZ Slices")
        self.show_YZ_plot_button.clicked.connect(self.showYZPlot)
        self.show_YZ_plot_button.setEnabled(False)
        self.save_Results_button = QtWidgets.QPushButton("Save the 3D data")
        self.save_Results_button.clicked.connect(self.saveResults)
        self.save_Results_button.setEnabled(False)
        self.plotOptionsGrid.addWidget(self.load_data_button,0,0,1,3)
        self.plotOptionsGrid.addWidget(self.KxyIndex,1,0,1,3)
        self.plotOptionsGrid.addWidget(self.KzIndex,2,0,1,3)
        self.plotOptionsGrid.addWidget(self.showFWHMCheckLabel,3,0,1,1)
        self.plotOptionsGrid.addWidget(self.showFWHMCheck,3,1,1,2)
        self.plotOptionsGrid.addWidget(self.reciprocalMapfontListLabel,4,0,1,1)
        self.plotOptionsGrid.addWidget(self.reciprocalMapfontList,4,1,1,2)
        self.plotOptionsGrid.addWidget(self.reciprocalMapfontSizeLabel,5,0,1,1)
        self.plotOptionsGrid.addWidget(self.reciprocalMapfontSizeSlider,5,1,1,2)
        self.plotOptionsGrid.addWidget(self.reciprocalMapColormapLabel,6,0,1,1)
        self.plotOptionsGrid.addWidget(self.reciprocalMapColormapCombo,6,1,1,2)
        self.plotOptionsGrid.addWidget(self.show_XY_plot_button,7,0,1,1)
        self.plotOptionsGrid.addWidget(self.show_XZ_plot_button,7,1,1,1)
        self.plotOptionsGrid.addWidget(self.show_YZ_plot_button,7,2,1,1)
        self.plotOptionsGrid.addWidget(self.save_Results_button,8,0,1,3)

        self.appearance = QtWidgets.QWidget()
        self.appearanceGrid = QtWidgets.QVBoxLayout(self.appearance)
        self.appearanceGrid.setContentsMargins(5,5,5,5)
        self.appearanceGrid.setAlignment(QtCore.Qt.AlignTop)

        self.showCoordinatesWidget = QtWidgets.QWidget()
        self.showCoordinatesGrid = QtWidgets.QGridLayout(self.showCoordinatesWidget)
        self.showCoordinatesLabel = QtWidgets.QLabel('Show Coordinate System?')
        self.showCoordinates = QtWidgets.QCheckBox()
        self.showCoordinates.setChecked(True)
        self.showCoordinates.stateChanged.connect(self.updateCoordinates)
        self.showCoordinatesGrid.addWidget(self.showCoordinatesLabel,0,0)
        self.showCoordinatesGrid.addWidget(self.showCoordinates,0,1)

        self.themeList = QtWidgets.QComboBox(self)
        self.themeList.addItem("white")
        self.themeList.addItem("lightGray")
        self.themeList.addItem("darkGray")
        self.themeList.addItem("gray")
        self.themeList.addItem("black")

        self.fontListLabel = QtWidgets.QLabel("Change Font")
        self.fontListLabel.setStyleSheet('QLabel {color:blue;}')
        self.fontList = QtWidgets.QFontComboBox()
        self.fontList.setCurrentFont(QtGui.QFont("Arial"))
        self.fontList.currentFontChanged.connect(self.RefreshFontName)
        self.fontSizeLabel = QtWidgets.QLabel("Adjust Font Size ({})".format(50))
        self.fontSizeLabel.setFixedWidth(160)
        self.fontSizeSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.fontSizeSlider.setMinimum(1)
        self.fontSizeSlider.setMaximum(100)
        self.fontSizeSlider.setValue(50)
        self.fontSizeSlider.valueChanged.connect(self.RefreshFontSize)
        self.fontsChanged.connect(self.graph.changeFonts)

        self.shadowQualityLabel = QtWidgets.QLabel("Shadow Quality")
        self.shadowQualityLabel.setStyleSheet('QLabel {color:blue;}')
        self.shadowQuality = QtWidgets.QComboBox(self)
        self.shadowQuality.addItem("None")
        self.shadowQuality.addItem("Low")
        self.shadowQuality.addItem("Medium")
        self.shadowQuality.addItem("High")
        self.shadowQuality.addItem("Low Soft")
        self.shadowQuality.addItem("Medium Soft")
        self.shadowQuality.addItem("High Soft")
        self.shadowQuality.setCurrentText("None")
        self.shadowQuality.currentIndexChanged.connect(self.graph.changeShadowQuality)

        self.statusBar = QtWidgets.QGroupBox("Log")
        self.statusBar.setStyleSheet('QGroupBox::title {color:blue;}')
        self.statusGrid = QtWidgets.QGridLayout(self.statusBar)
        self.statusBar.setFixedHeight(150)
        self.statusBar.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Fixed)
        self.logBox = QtWidgets.QTextEdit(QtCore.QTime.currentTime().toString("hh:mm:ss")+ \
                                          "\u00A0\u00A0\u00A0\u00A0Initialized!")
        self.logBox.ensureCursorVisible()
        self.logBox.setAlignment(QtCore.Qt.AlignTop)
        self.logBox.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.logBoxScroll = QtWidgets.QScrollArea()
        self.logBoxScroll.setWidget(self.logBox)
        self.logBoxScroll.setWidgetResizable(True)
        self.logBoxScroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setVisible(False)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBarSizePolicy = self.progressBar.sizePolicy()
        self.progressBarSizePolicy.setRetainSizeWhenHidden(True)
        self.progressBarSizePolicy.setHorizontalPolicy(QtWidgets.QSizePolicy.Expanding)
        self.progressBar.setSizePolicy(self.progressBarSizePolicy)
        self.progressAdvance.connect(self.progress)
        self.progressHold.connect(self.progressOn)
        self.progressEnd.connect(self.progressReset)
        self.statusGrid.addWidget(self.logBoxScroll,0,0)
        self.statusGrid.addWidget(self.progressBar,1,0)
        self.vLayout_left.addWidget(self.statusBar)

        themeLabel = QtWidgets.QLabel("Background Color")
        themeLabel.setStyleSheet("QLabel {color:blue;}")

        self.viewDirection = QtWidgets.QWidget()
        self.viewDirectionGrid = QtWidgets.QGridLayout(self.viewDirection)
        self.viewDirectionButtonGroup = QtWidgets.QButtonGroup()
        cameraModes = (("Front",1,0,0),("Behind",10,1,0),\
                       ("Left",4,0,1),("Right",7,1,1),\
                       ("Front High",2,0,2),("Directly Above",16,1,2))
        for text,preset,i,j in cameraModes:
            self.viewDirectionGrid.addWidget(QtWidgets.QPushButton(text),i,j)
            count = self.viewDirectionGrid.count()
            self.viewDirectionButtonGroup.addButton(self.viewDirectionGrid.itemAt(count-1).widget(),id=preset)
        self.viewDirectionButtonGroup.buttonClicked.connect(self.viewDirectionChangedEmit)
        self.appearanceGrid.addWidget(self.showCoordinatesWidget)
        self.appearanceGrid.addWidget(themeLabel)
        self.appearanceGrid.addWidget(self.themeList)
        self.appearanceGrid.addWidget(self.fontListLabel)
        self.appearanceGrid.addWidget(self.fontList)
        self.appearanceGrid.addWidget(self.fontSizeLabel)
        self.appearanceGrid.addWidget(self.fontSizeSlider)
        self.appearanceGrid.addWidget(self.shadowQualityLabel)
        self.appearanceGrid.addWidget(self.shadowQuality)
        self.appearanceGrid.addWidget(self.viewDirection)
        self.tab.addTab(self.appearance,"View")
        self.tab.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Fixed)

        self.vLayout.addWidget(self.chooseCif)
        self.vLayout.addWidget(self.chooseDestination)
        self.vLayout.addWidget(self.lattice_constants_box)
        self.vLayout.addWidget(self.tab)
        self.vLayout.addWidget(self.plotOptions)
        self.controlPanelScroll.setWidget(self.controlPanel)
        self.controlPanelScroll.setWidgetResizable(True)
        self.controlPanelScroll.setFrameShape(QtWidgets.QFrame.NoFrame)

        self.themeList.currentTextChanged.connect(self.graph.changeTheme)
        self.themeList.setCurrentIndex(3)
        self.graph.logMessage.connect(self.updateLog)
        self.graph.progressAdvance.connect(self.progress)
        self.graph.progressEnd.connect(self.progressReset)
        self.viewDirectionChanged.connect(self.graph.updateViewDirection)
        self.showMaximized()

    def progress(self,min,max,val):
        self.progressBar.setVisible(True)
        self.progressBar.setMinimum(min)
        self.progressBar.setMaximum(max)
        self.progressBar.setValue(val)

    def progressOn(self):
        self.progressBar.setVisible(True)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(0)
        self.progressBar.setValue(0)

    def progressReset(self):
        self.progressBar.reset()
        self.progressBar.setVisible(False)

    def Choose_Destination(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(None,"choose save destination",'./',QtWidgets.QFileDialog.ShowDirsOnly)
        self.currentDestination = path
        self.chooseDestinationLabel.setText("The save destination is:\n"+self.currentDestination)

    def viewDirectionChangedEmit(self,button):
        p = self.viewDirectionButtonGroup.id(button)
        self.viewDirectionChanged.emit(p)

    def updateNumberOfStepsPerp(self,value):
        self.KzIndex.setHead(0)
        self.KzIndex.setTail(0)
        self.KzIndex.setMaximum(value-1)

    def updateNumberOfStepsPara(self,value):
        self.KxyIndex.setHead(0)
        self.KxyIndex.setTail(0)
        self.KxyIndex.setMaximum(value-1)

    def updateCoordinates(self,status):
        self.graph.updateCoordinates(status)

    def updateLattice(self,index,formula,a,b,c,alpha,beta,gamma):
        self.lattice_constants_label.setText("Sample "+str(index)+ "\n"+"\tFormula: "+formula+"\n\ta = {:5.3f}, b = {:5.3f}, c = {:5.3f}\n\talpha = {:5.3f}(\u00B0), beta = {:5.3f}(\u00B0), gamma = {:5.3f}(\u00B0)". \
                                            format(a,b,c,alpha,beta,gamma))

    def updateColors(self,name,color,index):
        self.colorSheet[index][name] = color
        self.graph.updateColors(self.colorSheet,index)

    def updateSize(self,name,size,index):
        self.graph.updateSize(name,size,index)

    def updateLog(self,msg):
        self.logBox.append(QtCore.QTime.currentTime().toString("hh:mm:ss")+"\u00A0\u00A0\u00A0\u00A0"+msg)

    def updateRange(self,index):
        self.updateLog("Constructing sample " + str(index+1))
        QtCore.QCoreApplication.processEvents()
        self.graph.clearStructure(index)
        self.box[index] = self.get_extended_structure(self.molecule_dict[index], self.structure_dict[index].lattice.a, \
                                                      self.structure_dict[index].lattice.b, \
                                            self.structure_dict[index].lattice.c, self.structure_dict[index].lattice.alpha,\
                                                      self.structure_dict[index].lattice.beta, \
                                            self.structure_dict[index].lattice.gamma, \
                                            images=(int(self.real_space_specification_dict[index]['h_range']),\
                                          int(self.real_space_specification_dict[index]['k_range']),\
                                          int(self.real_space_specification_dict[index]['k_range'])),\
                                            rotation=self.real_space_specification_dict[index]['rotation'],\
          offset=np.array([self.real_space_specification_dict[index]['x_shift'],self.real_space_specification_dict[index]['y_shift'],self.real_space_specification_dict[index]['z_shift']]))
        self.updateLog("Finished construction of sample " + str(index+1))
        self.updateLog("Applying changes in the real space range for sample " + str(index+1))
        QtCore.QCoreApplication.processEvents()

        self.graph.addData(index,self.box[index].sites,self.colorSheet, \
                            self.real_space_specification_dict[index]['lateral_size']*10, \
                            self.real_space_specification_dict[index]['z_range'],\
                            self.real_space_specification_dict[index]['shape'],\
                           np.array([self.real_space_specification_dict[index]['x_shift'],self.real_space_specification_dict[index]['y_shift'],0]),\
                           self.real_space_specification_dict[index]['rotation'],self.AR)
        self.updateLog("New real space range for sample" + str(index+1) +" applied!")

    def updateReciprocalRange(self):
        self.updateLog("Calculating diffraction pattern ......")
        QtCore.QCoreApplication.processEvents()
        self.KRange = [self.Kx_range.values(),self.Ky_range.values(),self.Kz_range.values()]
        self.x_linear = np.linspace(self.KRange[0][0],self.KRange[0][1],self.number_of_steps_para.value())
        self.y_linear = np.linspace(self.KRange[1][0],self.KRange[1][1],self.number_of_steps_para.value())
        self.z_linear = np.linspace(self.KRange[2][0],self.KRange[2][1],self.number_of_steps_perp.value())
        self.Kx,self.Ky,self.Kz = np.meshgrid(self.x_linear,self.y_linear,self.z_linear)
        self.diffraction_intensity = self.graph.getDiffraction(self.Kx,self.Ky,self.Kz,self.AFF)
        self.updateLog("Finished Calculation!")
        self.show_XY_plot_button.setEnabled(True)
        self.show_XZ_plot_button.setEnabled(True)
        self.show_YZ_plot_button.setEnabled(True)
        self.save_Results_button.setEnabled(True)

    def update_h_range(self,value,index):
        self.real_space_specification_dict[index]['h_range'] = value

    def update_k_range(self,value,index):
        self.real_space_specification_dict[index]['k_range'] = value

    def update_l_range(self,value,index):
        self.real_space_specification_dict[index]['l_range'] = value

    def update_shape(self,text,index):
        self.real_space_specification_dict[index]['shape'] = text

    def update_lateral_size(self,value,index):
        self.real_space_specification_dict[index]['lateral_size'] = value

    def update_x_shift(self,value,index):
        self.real_space_specification_dict[index]['x_shift'] = value

    def update_y_shift(self,value,index):
        self.real_space_specification_dict[index]['y_shift'] = value

    def update_z_shift(self,value,index):
        self.real_space_specification_dict[index]['z_shift'] = value
        self.z_shift_history[index].append(value)
        min = self.tab.widget(index).layout().itemAt(10).widget().currentMin + value - self.z_shift_history[index][-2]
        max = self.tab.widget(index).layout().itemAt(10).widget().currentMax + value - self.z_shift_history[index][-2]
        self.tab.widget(index).layout().itemAt(10).widget().setHead(min)
        self.tab.widget(index).layout().itemAt(10).widget().setTail(max)

    def update_rotation(self,value,index):
        self.real_space_specification_dict[index]['rotation'] = value

    def update_z_range(self,min,max,index):
        self.real_space_specification_dict[index]['z_range'] = min,max

    def addStructureControlPanel(self,index=0):
        range_structure = QtWidgets.QWidget()
        range_grid = QtWidgets.QGridLayout(range_structure)
        range_grid.setContentsMargins(5,5,5,5)
        range_grid.setAlignment(QtCore.Qt.AlignTop)
        h_range = LabelSlider(1,100,3,1,"h",index=index)
        h_range.valueChanged.connect(self.update_h_range)
        k_range = LabelSlider(1,100,3,1,"k",index=index)
        k_range.valueChanged.connect(self.update_k_range)
        l_range = LabelSlider(1,100,1,1,"l",index=index)
        l_range.valueChanged.connect(self.update_l_range)
        shape_label = QtWidgets.QLabel("Shape")
        shape_label.setStyleSheet('QLabel {color:blue;}')
        shape = IndexedComboBox(index)
        shape.addItem("Triangle")
        shape.addItem("Square")
        shape.addItem("Hexagon")
        shape.addItem("Circle")
        shape.textChanged.connect(self.update_shape)
        lateral_size = LabelSlider(1,100,1,1,"Lateral Size",'nm',index=index)
        lateral_size.valueChanged.connect(self.update_lateral_size)
        x_shift = LabelSlider(-1000,1000,0,100,"X Shift",'\u212B',index=index)
        x_shift.valueChanged.connect(self.update_x_shift)
        y_shift = LabelSlider(-1000,1000,0,100,"Y Shift",'\u212B',index=index)
        y_shift.valueChanged.connect(self.update_y_shift)
        z_shift = LabelSlider(-5000,5000,0,100,"Z Shift",'\u212B',index=index)
        z_shift.valueChanged.connect(self.update_z_shift)
        rotation = LabelSlider(-1800,1800,0,10,"rotation",'\u00B0',index=index)
        rotation.valueChanged.connect(self.update_rotation)
        z_range_slider = DoubleSlider(-8000,8000,100,-10,10,"Z range","\u212B",False,index=index)
        z_range_slider.valueChanged.connect(self.update_z_range)

        self.real_space_specification_dict[index] = {'h_range':h_range.getValue(),'k_range':k_range.getValue(),'l_range':l_range.getValue(),\
                                      'shape':shape.currentText(),'lateral_size':lateral_size.getValue(),\
                                      'x_shift':x_shift.getValue(),'y_shift':y_shift.getValue(),'z_shift':z_shift.getValue(),\
                                      'rotation':rotation.getValue(), 'z_range':z_range_slider.values()}

        apply_range = IndexedPushButton("Apply",index)
        apply_range.buttonClicked.connect(self.updateRange)
        apply_range.setEnabled(False)
        replace_structure = IndexedPushButton("Replace",index)
        replace_structure.buttonClicked.connect(self.replaceStructure)
        replace_structure.setEnabled(False)
        reset_structure = IndexedPushButton("Reset",index)
        reset_structure.buttonClicked.connect(self.resetStructure)
        reset_structure.setEnabled(False)
        range_grid.addWidget(h_range,0,0)
        range_grid.addWidget(k_range,1,0)
        range_grid.addWidget(l_range,2,0)
        range_grid.addWidget(shape_label,3,0)
        range_grid.addWidget(shape,4,0)
        range_grid.addWidget(lateral_size,5,0)
        range_grid.addWidget(x_shift,6,0)
        range_grid.addWidget(y_shift,7,0)
        range_grid.addWidget(z_shift,8,0)
        range_grid.addWidget(rotation,9,0)
        range_grid.addWidget(z_range_slider,10,0)
        range_grid.addWidget(apply_range,11,0)
        range_grid.addWidget(replace_structure,12,0)
        range_grid.addWidget(reset_structure,13,0)
        self.structure_index+=1
        self.tab.insertTab(index,range_structure,"Sample "+str(index+1))
        self.tab.setCurrentIndex(index)

    def showXYPlot(self):
        for i in range(int(self.KzIndex.values()[0]),int(self.KzIndex.values()[1]+1)):
            TwoDimPlot = TwoDimensionalMapping('XY',self.x_linear,self.y_linear,self.z_linear,self.diffraction_intensity,i,\
                         self.reciprocalMapfontList.currentFont().family(),self.reciprocalMapfontSizeSlider.value(), \
                         self.reciprocalMapColormapCombo.currentText(),self.showFWHMCheck.isChecked())
            self.refreshPlotFonts.connect(TwoDimPlot.refreshFonts)
            self.refreshPlotFWHM.connect(TwoDimPlot.refreshFWHM)
            TwoDimPlot.showPlot()
        self.updateLog("Simulated diffraction patterns obtained!")

    def showXZPlot(self):
        for i in range(int(self.KxyIndex.values()[0]),int(self.KxyIndex.values()[1]+1)):
            TwoDimPlot = TwoDimensionalMapping('XZ',self.x_linear,self.y_linear,self.z_linear,self.diffraction_intensity,i, \
                                                    self.reciprocalMapfontList.currentFont().family(),self.reciprocalMapfontSizeSlider.value(), \
                                                    self.reciprocalMapColormapCombo.currentText(),self.showFWHMCheck.isChecked())
            self.refreshPlotFonts.connect(TwoDimPlot.refreshFonts)
            self.refreshPlotFWHM.connect(TwoDimPlot.refreshFWHM)
            TwoDimPlot.showPlot()
        self.updateLog("Simulated diffraction patterns obtained!")

    def showYZPlot(self):
        for i in range(int(self.KxyIndex.values()[0]),int(self.KxyIndex.values()[1]+1)):
            TwoDimPlot = TwoDimensionalMapping('YZ',self.x_linear,self.y_linear,self.z_linear,self.diffraction_intensity,i, \
                                                    self.reciprocalMapfontList.currentFont().family(),self.reciprocalMapfontSizeSlider.value(), \
                                                    self.reciprocalMapColormapCombo.currentText(),self.showFWHMCheck.isChecked())
            self.refreshPlotFonts.connect(TwoDimPlot.refreshFonts)
            self.refreshPlotFWHM.connect(TwoDimPlot.refreshFWHM)
            TwoDimPlot.showPlot()
        self.updateLog("Simulated diffraction patterns obtained!")

    def loadData(self):
        path = QtWidgets.QFileDialog.getOpenFileName(None,"Choose The 3D Data",'./',filter="TXT (*.txt);;All Files (*.*)")[0]
        if not path == "":
            self.updateLog("Loading data ......")
            self.progressHold.emit()
            QtCore.QCoreApplication.processEvents()
            with open(path,'r') as file:
                for i, line in enumerate(file):
                    if i == 4:
                        realSpaceInformation = eval(line)
                    elif i == 7:
                        information = eval(line)
                    else:
                        pass
            self.real_space_specification_dict = realSpaceInformation
            self.x_linear = np.linspace(information['Kx_min'],information['Kx_max'],information['N_para'])
            self.y_linear = np.linspace(information['Ky_min'],information['Ky_max'],information['N_para'])
            self.z_linear = np.linspace(information['Kz_min'],information['Kz_max'],information['N_perp'])
            self.updateNumberOfStepsPara(information['N_para'])
            self.updateNumberOfStepsPerp(information['N_perp'])
            intensity = np.loadtxt(path,skiprows=12, usecols=3)
            self.diffraction_intensity = intensity.reshape(information['N_para'],information['N_para'],information['N_perp'])
            self.updateLog("Finished loading data!")
            self.progressEnd.emit()
            self.show_XY_plot_button.setEnabled(True)
            self.show_XZ_plot_button.setEnabled(True)
            self.show_YZ_plot_button.setEnabled(True)


    def getCifPath(self):
        path = QtWidgets.QFileDialog.getOpenFileName(None,"Choose The CIF File",'./',filter="CIF (*.cif);;All Files (*.*)")[0]
        if not path == "":
            self.updateLog("CIF opened!")
            self.cifPath = path
            self.chooseCifLabel.setText("The path of the CIF file is:\n"+self.cifPath)
            self.z_shift_history[self.structure_index] = [0]
            self.addStructureControlPanel(self.structure_index)
            self.addStructure(self.structure_index-1)

    def addStructure(self,index):
        self.updateLog("Adding sample" + str(index+1))
        QtCore.QCoreApplication.processEvents()
        h = int(self.real_space_specification_dict[index]['h_range'])
        k = int(self.real_space_specification_dict[index]['k_range'])
        l = int(self.real_space_specification_dict[index]['k_range'])
        self.structure_dict[index] = CifParser(self.cifPath).get_structures(primitive=False)[0]
        self.updateLattice(index+1,self.structure_dict[index].composition.reduced_formula,self.structure_dict[index].lattice.a,self.structure_dict[index].lattice.b,self.structure_dict[index].lattice.c,\
                           self.structure_dict[index].lattice.alpha,self.structure_dict[index].lattice.beta,self.structure_dict[index].lattice.gamma)
        self.molecule_dict[index] = pgStructure.Molecule.from_sites(self.structure_dict[index].sites)
        self.updateLog("Sample "+str(index+1)+" loaded!")
        self.updateLog("Constructing sample " + str(index+1))
        QtCore.QCoreApplication.processEvents()
        self.box[index] = self.get_extended_structure(self.molecule_dict[index], self.structure_dict[index].lattice.a, self.structure_dict[index].lattice.b, \
                                            self.structure_dict[index].lattice.c, self.structure_dict[index].lattice.alpha,self.structure_dict[index].lattice.beta,\
                                            self.structure_dict[index].lattice.gamma, images=(h,k,l), \
                                          rotation=self.real_space_specification_dict[index]['rotation'],\
        offset=np.array([self.real_space_specification_dict[index]['x_shift'],self.real_space_specification_dict[index]['y_shift'],self.real_space_specification_dict[index]['z_shift']]))
        self.updateLog("Finished construction of sample " + str(index+1))
        QtCore.QCoreApplication.processEvents()
        self.element_species[index] = set(site.specie for site in self.box[index].sites)
        colorPalette = QtWidgets.QWidget()
        grid = QtWidgets.QVBoxLayout(colorPalette)
        self.colorSheet[index]={}
        for i,name in enumerate(self.element_species[index]):
            colorPicker = ColorPicker(str(name),self.colors[i],self.AR.loc[str(name)].at['Normalized Radius'],index)
            colorPicker.colorChanged.connect(self.updateColors)
            colorPicker.sizeChanged.connect(self.updateSize)
            self.colorSheet[index][str(name)] = self.colors[i]
            grid.addWidget(colorPicker)
        if index == 0:
            self.colorTab = QtWidgets.QTabWidget()
            self.vLayout.insertWidget(4,self.colorTab)
        self.colorTab.addTab(colorPalette,"Atom Design "+str(index+1))
        self.colorTab.setCurrentIndex(index)
        self.updateLog("Adding data for sample " + str(index+1))
        QtCore.QCoreApplication.processEvents()
        self.graph.addData(index,self.box[index].sites,\
                            self.colorSheet, \
                            self.real_space_specification_dict[index]['lateral_size']*10, \
                            self.real_space_specification_dict[index]['z_range'],\
                            self.real_space_specification_dict[index]['shape'], \
                           np.array([self.real_space_specification_dict[index]['x_shift'],self.real_space_specification_dict[index]['y_shift'],0]),\
                           self.real_space_specification_dict[index]['rotation'],\
                            self.AR)
        self.graph.changeFonts(self.fontList.currentFont().family(),self.fontSizeSlider.value())
        self.graph.changeShadowQuality(self.shadowQuality.currentIndex())
        self.tab.widget(index).layout().itemAt(11).widget().setEnabled(True)
        self.tab.widget(index).layout().itemAt(12).widget().setEnabled(True)
        self.tab.widget(index).layout().itemAt(13).widget().setEnabled(True)
        self.updateLog("Finished adding data for sample " + str(index+1))
        QtCore.QCoreApplication.processEvents()
        self.apply_reciprocal_range.setEnabled(True)

    def replaceStructure(self,index):
        self.updateLog("Replacing sample" + str(index+1))
        QtCore.QCoreApplication.processEvents()
        path = QtWidgets.QFileDialog.getOpenFileName(None,"Choose The CIF File",'./',filter="CIF (*.cif);;All Files (*.*)")[0]
        if not path == "":
            self.updateLog("CIF opened!")
            self.cifPath = path
            self.chooseCifLabel.setText("The path of the CIF file is:\n"+self.cifPath)
            h = int(self.real_space_specification_dict[index]['h_range'])
            k = int(self.real_space_specification_dict[index]['k_range'])
            l = int(self.real_space_specification_dict[index]['k_range'])
            self.graph.clearStructure(index)
            self.structure_dict[index] = CifParser(self.cifPath).get_structures(primitive=False)[0]
            self.updateLattice(index+1,self.structure_dict[index].composition.reduced_formula,self.structure_dict[index].lattice.a,self.structure_dict[index].lattice.b,self.structure_dict[index].lattice.c,\
                               self.structure_dict[index].lattice.alpha,self.structure_dict[index].lattice.beta,self.structure_dict[index].lattice.gamma)
            self.molecule_dict[index] = pgStructure.Molecule.from_sites(self.structure_dict[index].sites)
            self.updateLog("Constructing sample " + str(index+1))
            QtCore.QCoreApplication.processEvents()
            self.box[index] = self.get_extended_structure(self.molecule_dict[index], self.structure_dict[index].lattice.a, self.structure_dict[index].lattice.b, \
                                                self.structure_dict[index].lattice.c, self.structure_dict[index].lattice.alpha,self.structure_dict[index].lattice.beta,\
                                                self.structure_dict[index].lattice.gamma, images=(h,k,l), \
                                              rotation=self.real_space_specification_dict[index]['rotation'],\
        offset=np.array([self.real_space_specification_dict[index]['x_shift'],self.real_space_specification_dict[index]['y_shift'],self.real_space_specification_dict[index]['z_shift']]))
            self.updateLog("Finished construction for sample " + str(index+1))
            QtCore.QCoreApplication.processEvents()

            self.element_species[index] = set(site.specie for site in self.box[index].sites)
            colorPalette = QtWidgets.QWidget()
            grid = QtWidgets.QVBoxLayout(colorPalette)
            self.colorSheet[index] = {}
            for i,name in enumerate(self.element_species[index]):
                colorPicker = ColorPicker(str(name),self.colors[i],self.AR.loc[str(name)].at['Normalized Radius'],index)
                colorPicker.colorChanged.connect(self.updateColors)
                colorPicker.sizeChanged.connect(self.updateSize)
                self.colorSheet[index][str(name)] = self.colors[i]
                grid.addWidget(colorPicker)
            self.colorTab.removeTab(index)
            self.colorTab.insertTab(index,colorPalette,"Atom Design "+str(index+1))
            self.graph.addData(index,self.box[index].sites,\
                                self.colorSheet,\
                                self.real_space_specification_dict[index]['lateral_size']*10, \
                                self.real_space_specification_dict[index]['z_range'],\
                                self.real_space_specification_dict[index]['shape'], \
                               np.array([self.real_space_specification_dict[index]['x_shift'],self.real_space_specification_dict[index]['y_shift'],0]),\
                               self.real_space_specification_dict[index]['rotation'],\
                                self.AR)
            self.graph.changeFonts(self.fontList.currentFont().family(),self.fontSizeSlider.value())
            self.graph.changeShadowQuality(self.shadowQuality.currentIndex())
            self.updateLog("Sample "+str(index+1)+" replaced!")

    def resetStructure(self,index):
        self.updateLog("Resetting sample" + str(index+1))
        QtCore.QCoreApplication.processEvents()
        self.tab.widget(index).layout().itemAt(0).widget().reset()
        self.tab.widget(index).layout().itemAt(1).widget().reset()
        self.tab.widget(index).layout().itemAt(2).widget().reset()
        self.tab.widget(index).layout().itemAt(4).widget().setCurrentText("Triangle")
        self.tab.widget(index).layout().itemAt(5).widget().reset()
        self.tab.widget(index).layout().itemAt(6).widget().reset()
        self.tab.widget(index).layout().itemAt(7).widget().reset()
        self.tab.widget(index).layout().itemAt(8).widget().reset()
        self.tab.widget(index).layout().itemAt(9).widget().reset()
        self.tab.widget(index).layout().itemAt(10).widget().reset()
        h = int(self.real_space_specification_dict[index]['h_range'])
        k = int(self.real_space_specification_dict[index]['k_range'])
        l = int(self.real_space_specification_dict[index]['k_range'])
        self.graph.clearStructure(index)
        self.structure_dict[index] = CifParser(self.cifPath).get_structures(primitive=False)[0]
        self.updateLattice(index+1,self.structure_dict[index].composition.reduced_formula,self.structure_dict[index].lattice.a,self.structure_dict[index].lattice.b,self.structure_dict[index].lattice.c,\
                           self.structure_dict[index].lattice.alpha,self.structure_dict[index].lattice.beta,self.structure_dict[index].lattice.gamma)
        self.molecule_dict[index] = pgStructure.Molecule.from_sites(self.structure_dict[index].sites)
        self.updateLog("Constructing sample " + str(index+1))
        QtCore.QCoreApplication.processEvents()
        self.box[index] = self.get_extended_structure(self.molecule_dict[index], self.structure_dict[index].lattice.a, self.structure_dict[index].lattice.b, \
                                            self.structure_dict[index].lattice.c, self.structure_dict[index].lattice.alpha,self.structure_dict[index].lattice.beta,\
                                            self.structure_dict[index].lattice.gamma, images=(h,k,l), \
                                          rotation=self.real_space_specification_dict[index]['rotation'],\
    offset=np.array([self.real_space_specification_dict[index]['x_shift'],self.real_space_specification_dict[index]['y_shift'],self.real_space_specification_dict[index]['z_shift']]))
        self.updateLog("Finished construction for sample " + str(index+1))
        QtCore.QCoreApplication.processEvents()

        self.element_species[index] = set(site.specie for site in self.box[index].sites)
        colorPalette = QtWidgets.QWidget()
        grid = QtWidgets.QVBoxLayout(colorPalette)
        self.colorSheet[index] = {}
        for i,name in enumerate(self.element_species[index]):
            colorPicker = ColorPicker(str(name),self.colors[i],self.AR.loc[str(name)].at['Normalized Radius'],index)
            colorPicker.colorChanged.connect(self.updateColors)
            colorPicker.sizeChanged.connect(self.updateSize)
            self.colorSheet[index][str(name)] = self.colors[i]
            grid.addWidget(colorPicker)
        self.colorTab.removeTab(index)
        self.colorTab.insertTab(index,colorPalette,"Atom Design "+str(index+1))
        self.graph.addData(index,self.box[index].sites,\
                            self.colorSheet,\
                            self.real_space_specification_dict[index]['lateral_size']*10, \
                            self.real_space_specification_dict[index]['z_range'],\
                            self.real_space_specification_dict[index]['shape'], \
                           np.array([self.real_space_specification_dict[index]['x_shift'],self.real_space_specification_dict[index]['y_shift'],0]),\
                           self.real_space_specification_dict[index]['rotation'],\
                            self.AR)
        self.graph.changeFonts(self.fontList.currentFont().family(),self.fontSizeSlider.value())
        self.graph.changeShadowQuality(self.shadowQuality.currentIndex())
        self.updateLog("Sample "+str(index+1)+" successfully reset!")

    def saveResults(self):
        if not self.currentDestination == '':
            self.progressHold.emit()
            QtCore.QCoreApplication.processEvents()
            self.mtx2vtp(self.currentDestination,self.destinationNameEdit.text(),self.diffraction_intensity,self.KRange,\
                         self.number_of_steps_para.value(),self.number_of_steps_perp.value(),\
                         self.real_space_specification_dict,self.element_species)
            self.progressEnd.emit()
        else:
            self.Raise_Error("Save destination is empty!")

    def show_2D(self,type,intensity,nkz,fontname,fontsize,colormap,showFWHM=False):
        figure = MplCanvas()
        if type == 'XY':
            matrix = intensity[:,:,nkz]
            max_intensity = np.amax(np.amax(matrix))
            cs = figure.axes.contourf(self.x_linear,self.y_linear,matrix.T/max_intensity,100,cmap=colormap)
            if showFWHM:
                min_x = np.amin(self.x_linear)
                max_y = np.amax(self.y_linear)
                csHM = figure.axes.contour(self.x_linear,self.y_linear,matrix.T/max_intensity,levels=[0.5],colors=['black'],linestyles='dashed',linewidths=2)
                FWHM = 1.0
                ratio = 1.0
                for collection in csHM.collections:
                    path = collection.get_paths()
                    for item in path:
                        x = item.vertices[:,0]
                        y = item.vertices[:,1]
                        w = np.sqrt(x**2+y**2)
                        ratio = np.amax(w)/np.amin(w)
                        FWHM = np.amax(w)+np.amin(w)
                figure.axes.text(min_x*0.96,max_y*0.8,"Average FWHM = {:5.4f} \u212B\u207B\u00B9\nFWHM Asymmetric Ratio = {:5.3f}". \
                        format(FWHM,ratio),color='white',fontsize=fontsize-5,bbox={'facecolor':'black','alpha':0.2,'pad':5})
            figure.axes.set_aspect(1)
            figure.axes.set_title('Simulated 2D reciprocal space map\nKz = {:5.2f} (\u212B\u207B\u00B9)'.\
                       format(self.z_linear[nkz]),fontsize=fontsize,pad=30)
            figure.axes.set_xlabel(r'$K_{x}$ $(\AA^{-1})$',fontname=fontname,fontsize=fontsize)
            figure.axes.set_ylabel(r'$K_{y}$ $(\AA^{-1})$',fontname=fontname,fontsize=fontsize)
            figure.axes.tick_params(which='both', labelsize=fontsize)
            cbar = figure.fig.colorbar(cs,format='%.2f')
            cbar.ax.set_ylabel("Normalized Intensity",fontname=fontname,fontsize=fontsize)
            cbar.ax.tick_params(labelsize=fontsize)
        elif type == 'XZ':
            matrix = intensity[:,nkz,:]
            max_intensity = np.amax(np.amax(matrix))
            cs = figure.axes.contourf(self.x_linear,self.z_linear,matrix.T/max_intensity,100,cmap=colormap)
            figure.axes.set_aspect(1)
            figure.axes.set_title('Simulated 2D reciprocal space map\nKy = {:5.2f} (\u212B\u207B\u00B9)'. \
                                  format(self.y_linear[nkz]),fontsize=fontsize,pad=30)
            figure.axes.set_xlabel(r'$K_{x}$ $(\AA^{-1})$',fontname=fontname,fontsize=fontsize)
            figure.axes.set_ylabel(r'$K_{z}$ $(\AA^{-1})$',fontname=fontname,fontsize=fontsize)
            figure.axes.tick_params(which='both', labelsize=fontsize)
            cbar = figure.fig.colorbar(cs,format='%.2f')
            cbar.ax.set_ylabel("Normalized Intensity",fontname=fontname,fontsize=fontsize)
            cbar.ax.tick_params(labelsize=fontsize)
        elif type == 'YZ':
            matrix = intensity[nkz,:,:]
            max_intensity = np.amax(np.amax(matrix))
            cs = figure.axes.contourf(self.y_linear,self.z_linear,matrix.T/max_intensity,100,cmap=colormap)
            figure.axes.set_aspect(1)
            figure.axes.set_title('Simulated 2D reciprocal space map\nKx = {:5.2f} (\u212B\u207B\u00B9)'. \
                                  format(self.x_linear[nkz]),fontsize=fontsize,pad=30)
            figure.axes.set_xlabel(r'$K_{y}$ $(\AA^{-1})$',fontname=fontname,fontsize=fontsize)
            figure.axes.set_ylabel(r'$K_{z}$ $(\AA^{-1})$',fontname=fontname,fontsize=fontsize)
            figure.axes.tick_params(which='both', labelsize=fontsize)
            cbar = figure.fig.colorbar(cs,format='%.2f')
            cbar.ax.set_ylabel("Normalized Intensity",fontname=fontname,fontsize=fontsize)
            cbar.ax.tick_params(labelsize=fontsize)
        self.TwoDimMappingWindow = QtWidgets.QWidget()
        self.TwoDimMappingWindow.setWindowTitle('Summary of Broadening Analysis')
        self.TwoDimMappingWindowLayout = QtWidgets.QGridLayout(self.TwoDimMappingWindow)
        toolbar = NavigationToolbar(figure,self.TwoDimMappingWindow)
        self.TwoDimMappingWindowLayout.addWidget(figure,0,0)
        self.TwoDimMappingWindowLayout.addWidget(toolbar,1,0)
        self.TwoDimMappingWindow.setWindowModality(QtCore.Qt.WindowModal)
        self.TwoDimMappingWindow.setMinimumSize(1000,800)
        self.TwoDimMappingWindow.show()


    def get_extended_structure(self,molecule,a,b,c,alpha,beta,gamma,images=(1,1,1), rotation=0,cls=None,offset=None):

        if offset is None:
            offset = np.array([0, 0, 0])

        unit_lattice = Lattice.from_parameters(a, b, c, alpha, beta, gamma)
        lattice = Lattice.from_parameters(a * (2*images[0]+1), b * (2*images[1]+1),
                                          c * (2*images[2]+1),
                                          alpha, beta, gamma)
        nimages = (2*images[0]+1) * (2*images[1]+1) * (2*images[2]+1)
        coords = []

        centered_coords = molecule.cart_coords + offset

        for i, j, k in itertools.product(list(range(-images[0],images[0]+1)),
                                         list(range(-images[1],images[1]+1)),
                                         list(range(-images[2],images[2]+1))):
            box_center = np.dot(unit_lattice.matrix.T, [i,j,k]).T
            op = SymmOp.from_origin_axis_angle(
                (0, 0, 0), axis=[0,0,1],
                angle=rotation)
            m = op.rotation_matrix
            new_coords = np.dot(m, (centered_coords+box_center).T).T
            coords.extend(new_coords)
            self.progressAdvance.emit(0,100,(i*(2*images[1]+1) * (2*images[2]+1)+j*(2*images[2]+1)+k)/nimages)
            QtCore.QCoreApplication.processEvents()
        self.progressEnd.emit()
        sprops = {k: v * nimages for k, v in molecule.site_properties.items()}

        if cls is None:
            cls = pgStructure.Structure

        return cls(lattice, molecule.species * nimages, coords,coords_are_cartesian=True,site_properties=sprops).get_sorted_structure()

    def RefreshFontSize(self):
        self.fontSizeLabel.setText("Adjust Font Size ({})".format(self.fontSizeSlider.value()))
        self.fontsChanged.emit(self.fontList.currentFont().family(),self.fontSizeSlider.value())

    def RefreshFontName(self):
        self.fontsChanged.emit(self.fontList.currentFont().family(),self.fontSizeSlider.value())

    def updateFWHMCheck(self,state):
        check = False
        if state == 2:
            check = True
        self.refreshPlotFWHM.emit(check)

    def updatePlotFont(self,font):
        self.refreshPlotFonts.emit(font.family(),self.reciprocalMapfontSizeSlider.value())

    def updateReciprocalMapFontSize(self,value):
        self.reciprocalMapfontSizeLabel.setText("Font Size ({})".format(value))
        self.refreshPlotFonts.emit(self.reciprocalMapfontList.currentFont().family(),value)

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

class ScatterGraph(QtDataVisualization.Q3DScatter):

    logMessage = QtCore.pyqtSignal(str)
    progressAdvance = QtCore.pyqtSignal(int,int,int)
    progressEnd = QtCore.pyqtSignal()

    def __init__(self):
        super(ScatterGraph,self).__init__()
        self.series_dict = {}
        self.atoms_dict = {}
        self.elements_dict = {}
        self.colors_dict = {}

    def addData(self,index,data,colorSheet,range,z_range,shape,offset,rotation,AR):
        self.colors_dict = colorSheet
        element_species = list(str(site.specie) for site in data)
        self.elements_dict[index] = element_species
        self.coords = (site.coords for site in data)
        self.coordinateStatus = 2
        self.atoms_dict[index] = {}
        self.axisX().setTitle("X (\u212B)")
        self.axisY().setTitle("Z (\u212B)")
        self.axisZ().setTitle("Y (\u212B)")
        self.axisX().setTitleVisible(True)
        self.axisY().setTitleVisible(True)
        self.axisZ().setTitleVisible(True)
        atomSeries = {}
        op = SymmOp.from_origin_axis_angle(
            (0, 0, 0), axis=[0,0,1],
            angle=-rotation)
        m = op.rotation_matrix
        number_of_coords = len(element_species)
        for i,coord in enumerate(self.coords):
            old_coords = np.dot(m, (coord-offset).T).T
            if shape == "Triangle":
                condition = (old_coords[1]>(-range/2/np.sqrt(3))) and \
                            (old_coords[1]<(-np.sqrt(3)*old_coords[0]+range/np.sqrt(3))) and \
                            (old_coords[1]<(np.sqrt(3)*old_coords[0]+range/np.sqrt(3)))
            elif shape == "Square":
                condition = (old_coords[0]> -range/2) and \
                            (old_coords[0]< range/2) and \
                            (old_coords[1]> -range/2) and \
                            (old_coords[1]< range/2)
            elif shape == "Hexagon":
                condition = (old_coords[1] < range*np.sqrt(3)/2) and \
                            (old_coords[1] > -range*np.sqrt(3)/2) and \
                            (old_coords[1] < (-np.sqrt(3)*old_coords[0]+np.sqrt(3)*range)) and \
                            (old_coords[1] < (np.sqrt(3)*old_coords[0]+np.sqrt(3)*range)) and \
                            (old_coords[1] > (-np.sqrt(3)*old_coords[0]-np.sqrt(3)*range)) and \
                            (old_coords[1] > (np.sqrt(3)*old_coords[0]-np.sqrt(3)*range))
            elif shape == "Circle":
                condition = (np.sqrt(coord[0]*coord[0]+coord[1]*coord[1]) < range)
            if condition and (coord[2]<z_range[1] and coord[2]>z_range[0]):
                self.atoms_dict[index][','.join(str(x) for x in coord)] = self.elements_dict[index][i]
                dataArray = []
                radii = AR.loc[self.elements_dict[index][i]].at['Normalized Radius']
                ScatterProxy = QtDataVisualization.QScatterDataProxy()
                ScatterSeries = QtDataVisualization.QScatter3DSeries(ScatterProxy)
                item = QtDataVisualization.QScatterDataItem()
                vector = QtGui.QVector3D(coord[0],coord[2],coord[1])
                item.setPosition(vector)
                dataArray.append(item)
                ScatterProxy.resetArray(dataArray)
                ScatterSeries.setMeshSmooth(True)
                ScatterSeries.setColorStyle(QtDataVisualization.Q3DTheme.ColorStyleUniform)
                ScatterSeries.setBaseColor(QtGui.QColor(self.colors_dict[index][self.elements_dict[index][i]]))
                ScatterSeries.setItemSize(radii/100)
                ScatterSeries.setSingleHighlightColor(QtGui.QColor('white'))
                ScatterSeries.setItemLabelFormat(self.elements_dict[index][i]+' (@xLabel, @zLabel, @yLabel)')
                atomSeries[i] = ScatterSeries
                self.addSeries(ScatterSeries)
                self.progressAdvance.emit(0,100,i/number_of_coords*100)
        self.progressEnd.emit()
        self.series_dict[index] = atomSeries

    def flatten(self,parent):
        result = {}
        for key,value in parent.items():
            if isinstance(value,dict):
                value = [value]
            if isinstance(value,list):
                for child in value:
                    deeper = self.flatten(child).items()
                    result.update({key2: value2 for key2, value2 in deeper})
            else:
                result[key] = value
        return result

    def getDiffraction(self,Kx,Ky,Kz,AFF):
        Psi = np.multiply(Kx,0).astype('complex128')
        species_dict = set(AFF.index.tolist())
        self.atoms_list = self.flatten(self.atoms_dict)
        number_of_atoms = len(self.atoms_list)
        i = 0
        for key,specie in self.atoms_list.items():
            coord = list(float(x) for x in list(key.split(',')))
            if specie in species_dict:
                af_row = AFF.loc[specie]
            elif specie+'1+' in species_dict:
                af_row = AFF.loc[specie+'1+']
            elif specie+'2+' in species_dict:
                af_row = AFF.loc[specie+'2+']
            elif specie+'3+' in species_dict:
                af_row = AFF.loc[specie+'3+']
            elif specie+'4+' in species_dict:
                af_row = AFF.loc[specie+'4+']
            elif specie+'1-' in species_dict:
                af_row = AFF.loc[specie+'1-']
            elif specie+'2-' in species_dict:
                af_row = AFF.loc[specie+'2-']
            elif specie+'3-' in species_dict:
                af_row = AFF.loc[specie+'3-']
            elif specie+'4-' in species_dict:
                af_row = AFF.loc[specie+'4-']
            else:
                self.Raise_Error("No scattering coefficient for %s"%specie)
                break
            af = af_row.at['c']+af_row.at['a1']*np.exp(-af_row.at['b1']*(np.multiply(Kx,Kx)+np.multiply(Ky,Ky)+np.multiply(Kz,Kz))/4/np.pi)\
                               +af_row.at['a2']*np.exp(-af_row.at['b2']*(np.multiply(Kx,Kx)+np.multiply(Ky,Ky)+np.multiply(Kz,Kz))/4/np.pi)\
                               +af_row.at['a3']*np.exp(-af_row.at['b3']*(np.multiply(Kx,Kx)+np.multiply(Ky,Ky)+np.multiply(Kz,Kz))/4/np.pi)\
                               +af_row.at['a4']*np.exp(-af_row.at['b4']*(np.multiply(Kx,Kx)+np.multiply(Ky,Ky)+np.multiply(Kz,Kz))/4/np.pi)
            Psi += np.multiply(af,np.exp(1j*(Kx*coord[0]+Ky*coord[1]+Kz*coord[2])))
            i+=1
            self.progressAdvance.emit(0,100,i/number_of_atoms*100)
            QtCore.QCoreApplication.processEvents()
        intensity = np.multiply(Psi.astype('complex64'),np.conj(Psi.astype('complex64')))
        self.progressEnd.emit()
        return intensity

    def clear(self):
        for series in self.seriesList():
            self.removeSeries(series)

    def clearStructure(self,index):
        for series in list(self.series_dict[index].values()):
            self.removeSeries(series)

    def updateCoordinates(self,status):
        self.coordinateStatus = status
        if status == 2:
            self.axisX().setTitleVisible(True)
            self.axisY().setTitleVisible(True)
            self.axisZ().setTitleVisible(True)
            self.activeTheme().setBackgroundEnabled(True)
            self.activeTheme().setGridEnabled(True)
            if self.activeTheme().backgroundColor() == QtGui.QColor("black"):
                self.activeTheme().setLabelTextColor(QtGui.QColor("white"))
            else:
                self.activeTheme().setLabelTextColor(QtGui.QColor("black"))

        elif status == 0:
            self.axisX().setTitleVisible(False)
            self.axisY().setTitleVisible(False)
            self.axisZ().setTitleVisible(False)
            self.activeTheme().setBackgroundEnabled(False)
            self.activeTheme().setGridEnabled(False)
            self.activeTheme().setLabelBackgroundEnabled(False)
            self.activeTheme().setLabelBorderEnabled(False)
            self.activeTheme().setLabelTextColor(QtCore.Qt.transparent)

    def updateViewDirection(self,preset):
        self.scene().activeCamera().setCameraPreset(preset)

    def updateColors(self,colorSheet,index):
        self.colors_dict = colorSheet
        for i,series in self.series_dict[index].items():
            series.setBaseColor(QtGui.QColor(colorSheet[index][self.elements_dict[index][i]]))

    def updateAllColors(self):
        for i,colorSheet in self.colors_dict.items():
            for j,series in self.series_dict[i].items():
                series.setBaseColor(QtGui.QColor(colorSheet[self.elements_dict[i][j]]))

    def updateSize(self,name,size,index):
        for i,series in self.series_dict[index].items():
            if name == self.elements_dict[index][i]:
                series.setItemSize(size)

    def changeFonts(self,fontname,fontsize):
        self.activeTheme().setFont(QtGui.QFont(fontname,fontsize))

    def changeTheme(self, color):
        self.activeTheme().setBackgroundColor(QtGui.QColor(color))
        self.activeTheme().setWindowColor(QtGui.QColor(color))
        self.activeTheme().setLabelBackgroundEnabled(False)
        self.activeTheme().setLabelBorderEnabled(False)
        try:
            self.updateCoordinates(self.coordinateStatus)
        except:
            pass
        try:
            self.updateAllColors()
        except:
            pass

    def changeShadowQuality(self,quality):
        self.setShadowQuality(quality)

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

class LabelSlider(QtWidgets.QWidget):

    valueChanged = QtCore.pyqtSignal(float,int)

    def __init__(self,min,max,initial,scale,text,unit='',orientation = QtCore.Qt.Horizontal,index=-1):
        super(LabelSlider, self).__init__()
        self.scale = scale
        self.label_text = text
        self.min = min
        self.max = max
        self.initial = initial
        self.unit = unit
        self.index = index
        if 1/self.scale >= 0.1:
            self.label = QtWidgets.QLabel(self.label_text+" = {:6.1f} ".format(initial)+self.unit)
        elif 1/self.scale >= 0.01:
            self.label = QtWidgets.QLabel(self.label_text+" = {:6.2f} ".format(initial)+self.unit)
        elif 1/self.scale >= 0.001:
            self.label = QtWidgets.QLabel(self.label_text+" = {:6.3f} ".format(initial)+self.unit)
        else:
            self.label = QtWidgets.QLabel(self.label_text+" = {:6.4f} ".format(initial)+self.unit)
        self.valueSlider = QtWidgets.QSlider(orientation)
        self.valueSlider.setMinimum(min)
        self.valueSlider.setMaximum(max)
        self.valueSlider.setValue(initial*scale)
        self.valueSlider.setTickInterval(1)
        self.valueSlider.valueChanged.connect(self.value_changed)
        self.grid = QtWidgets.QGridLayout()
        self.grid.addWidget(self.label,0,0)
        self.grid.addWidget(self.valueSlider,0,1)
        self.grid.setContentsMargins(0,0,0,0)
        self.setLayout(self.grid)

    def set(self,min,max,initial,scale):
        self.scale = scale
        self.min = min
        self.max = max
        self.valueSlider.setMinimum(min)
        self.valueSlider.setMaximum(max)
        self.valueSlider.setValue(initial*scale)
        self.value_changed(initial*scale)

    def reset(self):
        self.valueSlider.setMinimum(self.min)
        self.valueSlider.setMaximum(self.max)
        self.valueSlider.setValue(self.initial*self.scale)
        self.value_changed(self.initial*self.scale)

    def value_changed(self,value):
        if 1/self.scale >= 0.1:
            self.label.setText(self.label_text+" = {:6.1f} ".format(value/self.scale)+self.unit)
        elif 1/self.scale >= 0.01:
            self.label.setText(self.label_text+" = {:6.2f} ".format(value/self.scale)+self.unit)
        elif 1/self.scale >= 0.001:
            self.label.setText(self.label_text+" = {:6.3f} ".format(value/self.scale)+self.unit)
        elif 1/self.scale >= 0.0001:
            self.label.setText(self.label_text+" = {:6.4f} ".format(value/self.scale)+self.unit)
        else:
            self.label.setText(self.label_text+" = {:7.5f} ".format(value/self.scale)+self.unit)
        self.valueChanged.emit(value/self.scale,self.index)

    def getValue(self):
        return self.valueSlider.value()/self.scale

    def getIndex(self):
        return self.index

class DoubleSlider(QtWidgets.QWidget):
    valueChanged = QtCore.pyqtSignal(float,float,int)

    def __init__(self,minimum,maximum,scale,head,tail,text,unit='',lock = False,direction='horizontal',index=-1):
        super(DoubleSlider,self).__init__()
        self.currentMin, self.currentMax = int(head),int(tail)
        self.head = head
        self.tail = tail
        self.text = text
        self.scale = scale
        self.unit = unit
        self.lock = lock
        self.index = index
        if self.unit == '':
            if 1/self.scale >=1:
                self.minLabel = QtWidgets.QLabel(self.text+"_min = {:2.0f} ".format(self.currentMin))
            elif 1/self.scale >=0.1:
                self.minLabel = QtWidgets.QLabel(self.text+"_min = {:3.1f} ".format(self.currentMin))
            elif 1/self.scale >=0.01:
                self.minLabel = QtWidgets.QLabel(self.text+"_min = {:4.2f} ".format(self.currentMin))
            elif 1/self.scale >=0.001:
                self.minLabel = QtWidgets.QLabel(self.text+"_min = {:5.3f} ".format(self.currentMin))
            elif 1/self.scale >=0.0001:
                self.minLabel = QtWidgets.QLabel(self.text+"_min = {:6.4f} ".format(self.currentMin))
        else:
            if 1/self.scale >=1:
                self.minLabel = QtWidgets.QLabel(self.text+"_min = {:2.0f} ".format(self.currentMin)+"("+unit+")")
            elif 1/self.scale >=0.1:
                self.minLabel = QtWidgets.QLabel(self.text+"_min = {:3.1f} ".format(self.currentMin)+"("+unit+")")
            elif 1/self.scale >=0.01:
                self.minLabel = QtWidgets.QLabel(self.text+"_min = {:4.2f} ".format(self.currentMin)+"("+unit+")")
            elif 1/self.scale >=0.001:
                self.minLabel = QtWidgets.QLabel(self.text+"_min = {:5.3f} ".format(self.currentMin)+"("+unit+")")
            elif 1/self.scale >=0.0001:
                self.minLabel = QtWidgets.QLabel(self.text+"_min = {:6.4f} ".format(self.currentMin)+"("+unit+")")
        self.minLabel.setFixedWidth(180)
        self.minSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.minSlider.setMinimum(minimum)
        if self.lock:
            self.minSlider.setMaximum(0)
        else:
            self.minSlider.setMaximum(maximum)
        self.minSlider.setValue(self.currentMin*self.scale)
        self.minSlider.valueChanged.connect(self.minChanged)

        if self.unit == '':
            if 1/self.scale >=1:
                self.maxLabel = QtWidgets.QLabel(self.text+"_max = {:2.0f} ".format(self.currentMax))
            elif 1/self.scale >=0.1:
                self.maxLabel = QtWidgets.QLabel(self.text+"_max = {:3.1f} ".format(self.currentMax))
            elif 1/self.scale >=0.01:
                self.maxLabel = QtWidgets.QLabel(self.text+"_max = {:4.2f} ".format(self.currentMax))
            elif 1/self.scale >=0.001:
                self.maxLabel = QtWidgets.QLabel(self.text+"_max = {:5.3f} ".format(self.currentMax))
            elif 1/self.scale >=0.0001:
                self.maxLabel = QtWidgets.QLabel(self.text+"_max = {:6.4f} ".format(self.currentMax))
        else:
            if 1/self.scale >=1:
                self.maxLabel = QtWidgets.QLabel(self.text+"_max = {:2.0f} ".format(self.currentMax)+"("+unit+")")
            elif 1/self.scale >=0.1:
                self.maxLabel = QtWidgets.QLabel(self.text+"_max = {:3.1f} ".format(self.currentMax)+"("+unit+")")
            elif 1/self.scale >=0.01:
                self.maxLabel = QtWidgets.QLabel(self.text+"_max = {:4.2f} ".format(self.currentMax)+"("+unit+")")
            elif 1/self.scale >=0.001:
                self.maxLabel = QtWidgets.QLabel(self.text+"_max = {:5.3f} ".format(self.currentMax)+"("+unit+")")
            elif 1/self.scale >=0.0001:
                self.maxLabel = QtWidgets.QLabel(self.text+"_max = {:6.4f} ".format(self.currentMax)+"("+unit+")")
        self.maxLabel.setFixedWidth(180)
        self.maxSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        if self.lock:
            self.maxSlider.setMinimum(0)
        else:
            self.maxSlider.setMinimum(minimum)
        self.maxSlider.setMaximum(maximum)
        self.maxSlider.setValue(self.currentMax*self.scale)
        self.maxSlider.valueChanged.connect(self.maxChanged)

        self.UIgrid = QtWidgets.QGridLayout()
        self.UIgrid.addWidget(self.minLabel,0,0)
        self.UIgrid.addWidget(self.minSlider,0,1)
        self.UIgrid.addWidget(self.maxLabel,1,0)
        self.UIgrid.addWidget(self.maxSlider,1,1)
        self.UIgrid.setContentsMargins(0,0,0,0)
        self.setLayout(self.UIgrid)

    def reset(self):
        self.minSlider.setValue(self.head*self.scale)
        self.maxSlider.setValue(self.tail*self.scale)

    def setMaximum(self,value):
        if self.lock:
            self.minSlider.setMaximum(0)
        else:
            self.minSlider.setMaximum(value)
        self.maxSlider.setMaximum(value)

    def setHead(self,value):
        if not self.lock:
            self.minSlider.setValue(np.round(value*self.scale,0))

    def setTail(self,value):
        if not self.lock:
            self.maxSlider.setValue(np.round(value*self.scale,0))

    def values(self):
        return self.currentMin, self.currentMax

    def minChanged(self):
        self.currentMin = self.minSlider.value()/self.scale
        if self.lock:
            if self.currentMin > self.currentMax:
                self.maxSlider.setValue(0)
            else:
                self.maxSlider.setValue(-self.currentMin*self.scale)
        elif self.currentMin > self.currentMax:
            self.maxSlider.setValue(self.currentMin*self.scale)

        if self.unit == '':
            if 1/self.scale >=1:
                self.minLabel.setText(self.text+"_min = {:2.0f} ".format(self.currentMin))
            elif 1/self.scale >=0.1:
                self.minLabel.setText(self.text+"_min = {:3.1f} ".format(self.currentMin))
            elif 1/self.scale >=0.01:
                self.minLabel.setText(self.text+"_min = {:4.2f} ".format(self.currentMin))
            elif 1/self.scale >=0.001:
                self.minLabel.setText(self.text+"_min = {:5.3f} ".format(self.currentMin))
            elif 1/self.scale >=0.0001:
                self.minLabel.setText(self.text+"_min = {:6.4f} ".format(self.currentMin))
        else:
            if 1/self.scale >=1:
                self.minLabel.setText(self.text+"_min = {:2.0f} ".format(self.currentMin)+"("+self.unit+")")
            elif 1/self.scale >=0.1:
                self.minLabel.setText(self.text+"_min = {:3.1f} ".format(self.currentMin)+"("+self.unit+")")
            elif 1/self.scale >=0.01:
                self.minLabel.setText(self.text+"_min = {:4.2f} ".format(self.currentMin)+"("+self.unit+")")
            elif 1/self.scale >=0.001:
                self.minLabel.setText(self.text+"_min = {:5.3f} ".format(self.currentMin)+"("+self.unit+")")
            elif 1/self.scale >=0.0001:
                self.minLabel.setText(self.text+"_min = {:6.4f} ".format(self.currentMin)+"("+self.unit+")")
        self.valueChanged.emit(np.round(self.currentMin,2),np.round(self.currentMax,2),self.index)

    def maxChanged(self):
        self.currentMax = self.maxSlider.value()/self.scale
        if self.lock:
            if self.currentMin > self.currentMax:
                self.minSlider.setValue(0)
            else:
                self.minSlider.setValue(-self.currentMax*self.scale)
        elif self.currentMin > self.currentMax:
            self.minSlider.setValue(self.currentMax*self.scale)
        if self.unit == '':
            if 1/self.scale >=1:
                self.maxLabel.setText(self.text+"_max = {:2.0f} ".format(self.currentMax))
            elif 1/self.scale >=0.1:
                self.maxLabel.setText(self.text+"_max = {:3.1f} ".format(self.currentMax))
            elif 1/self.scale >=0.01:
                self.maxLabel.setText(self.text+"_max = {:4.2f} ".format(self.currentMax))
            elif 1/self.scale >=0.001:
                self.maxLabel.setText(self.text+"_max = {:5.3f} ".format(self.currentMax))
            elif 1/self.scale >=0.0001:
                self.maxLabel.setText(self.text+"_max = {:6.4f} ".format(self.currentMax))
        else:
            if 1/self.scale >=1:
                self.maxLabel.setText(self.text+"_max = {:2.0f} ".format(self.currentMax)+"("+self.unit+")")
            elif 1/self.scale >=0.1:
                self.maxLabel.setText(self.text+"_max = {:3.1f} ".format(self.currentMax)+"("+self.unit+")")
            elif 1/self.scale >=0.01:
                self.maxLabel.setText(self.text+"_max = {:4.2f} ".format(self.currentMax)+"("+self.unit+")")
            elif 1/self.scale >=0.001:
                self.maxLabel.setText(self.text+"_max = {:5.3f} ".format(self.currentMax)+"("+self.unit+")")
            elif 1/self.scale >=0.0001:
                self.maxLabel.setText(self.text+"_max = {:6.4f} ".format(self.currentMax)+"("+self.unit+")")
        self.valueChanged.emit(np.round(self.currentMin,2),np.round(self.currentMax,2),self.index)

    def setEnabled(self,enable):
        self.minSlider.setEnabled(enable)
        self.maxSlider.setEnabled(enable)

class ColorPicker(QtWidgets.QWidget):

    colorChanged = QtCore.pyqtSignal(str,str,int)
    sizeChanged = QtCore.pyqtSignal(str,float,int)

    def __init__(self,name,color,size=20,index=-1):
        super(ColorPicker,self).__init__()
        self.color = color
        self.name = name
        self.size = size
        self.index = index
        self.label = QtWidgets.QLabel(self.name)
        self.label.setFixedWidth(20)
        self.PB = QtWidgets.QPushButton()
        self.PB.clicked.connect(self.changeColor)
        self.SB = QtWidgets.QSpinBox()
        self.SB.setMinimum(0)
        self.SB.setMaximum(100)
        self.SB.setSingleStep(1)
        self.SB.setValue(self.size)
        self.SB.valueChanged.connect(self.changeSize)
        self.setColor(self.color)
        self.grid = QtWidgets.QGridLayout(self)
        self.grid.addWidget(self.label,0,0)
        self.grid.addWidget(self.PB,0,1)
        self.grid.addWidget(self.SB,0,2)

    def changeColor(self):
        new_color = QtWidgets.QColorDialog.getColor(QtGui.QColor(self.color))
        self.color = new_color.name()
        self.setColor(self.color)
        self.colorChanged.emit(self.name,self.color,self.index)

    def changeSize(self,text):
        self.size = int(text)
        self.sizeChanged.emit(self.name, self.size/100,self.index)

    def getSize(self):
        return self.size

    def setColor(self,color):
        self.PB.setStyleSheet("background-color:"+color)
        self.color = color

    def getColor(self):
        return self.color

class IndexedComboBox(QtWidgets.QComboBox):
    textChanged = QtCore.pyqtSignal(str,int)

    def __init__(self,index):
        super(IndexedComboBox,self).__init__()
        self.index = index
        self.currentTextChanged.connect(self.changeText)

    def changeText(self,text):
        self.textChanged.emit(text,self.index)

class IndexedPushButton(QtWidgets.QPushButton):
    buttonClicked = QtCore.pyqtSignal(int)

    def __init__(self,text,index):
        super(IndexedPushButton,self).__init__(text)
        self.index = index
        self.clicked.connect(self.emitSignal)

    def emitSignal(self):
        self.buttonClicked.emit(self.index)

class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def clear(self):
        self.fig.clear()
        self.axes = self.fig.add_subplot(111)

class TwoDimensionalMapping(QtWidgets.QWidget):
    def __init__(self,type,x,y,z,intensity,nkz,fontname,fontsize,colormap,showFWHM=False):
        super(TwoDimensionalMapping,self).__init__()
        self.figure = MplCanvas()
        self.x_linear = x
        self.y_linear = y
        self.z_linear = z
        self.intensity = intensity
        self.nkz = nkz
        self.showFWHM = showFWHM
        self.type = type
        self.fontname = fontname
        self.fontsize = fontsize
        self.colormap = colormap
        self.TwoDimMappingWindow = QtWidgets.QWidget()
        self.TwoDimMappingWindow.setWindowTitle('Summary of Broadening Analysis')
        self.TwoDimMappingWindowLayout = QtWidgets.QGridLayout(self.TwoDimMappingWindow)
        self.toolbar = NavigationToolbar(self.figure,self.TwoDimMappingWindow)
        self.TwoDimMappingWindowLayout.addWidget(self.figure,0,0)
        self.TwoDimMappingWindowLayout.addWidget(self.toolbar,1,0)
        self.TwoDimMappingWindow.setWindowModality(QtCore.Qt.WindowModal)
        self.TwoDimMappingWindow.setMinimumSize(1000,800)
        self.TwoDimMappingWindow.show()

    def showPlot(self):
        self.replot(self.type,self.x_linear,self.y_linear,self.z_linear,self.colormap,self.intensity,self.nkz)

    def refreshFonts(self,fontname,fontsize):
        self.fontname = fontname
        self.fontsize = fontsize
        if self.type == 'XY':
            self.figure.axes.set_title('Simulated 2D reciprocal space map\nKz = {:5.2f} (\u212B\u207B\u00B9)'.\
               format(self.z_linear[self.nkz]),fontsize=self.fontsize,pad=30)
            self.figure.axes.set_xlabel(r'$K_{x}$ $(\AA^{-1})$',fontname=self.fontname,fontsize=self.fontsize)
            self.figure.axes.set_ylabel(r'$K_{y}$ $(\AA^{-1})$',fontname=self.fontname,fontsize=self.fontsize)
        elif self.type == 'XZ':
            self.figure.axes.set_title('Simulated 2D reciprocal space map\nKy = {:5.2f} (\u212B\u207B\u00B9)'. \
                                       format(self.y_linear[self.nkz]),fontsize=self.fontsize,pad=30)
            self.figure.axes.set_xlabel(r'$K_{x}$ $(\AA^{-1})$',fontname=self.fontname,fontsize=self.fontsize)
            self.figure.axes.set_ylabel(r'$K_{z}$ $(\AA^{-1})$',fontname=self.fontname,fontsize=self.fontsize)
        elif self.type == 'YZ':
            self.figure.axes.set_title('Simulated 2D reciprocal space map\nKx = {:5.2f} (\u212B\u207B\u00B9)'. \
                                       format(self.x_linear[self.nkz]),fontsize=self.fontsize,pad=30)
            self.figure.axes.set_xlabel(r'$K_{y}$ $(\AA^{-1})$',fontname=self.fontname,fontsize=self.fontsize)
            self.figure.axes.set_ylabel(r'$K_{z}$ $(\AA^{-1})$',fontname=self.fontname,fontsize=self.fontsize)
        self.figure.axes.set_aspect(1)
        self.figure.axes.tick_params(which='both', labelsize=self.fontsize)
        self.cbar.ax.set_ylabel("Normalized Intensity",fontname=self.fontname,fontsize=self.fontsize)
        self.cbar.ax.tick_params(labelsize=self.fontsize)

    def refreshFWHM(self,showFWHM):
        if showFWHM == self.showFWHM:
            pass
        else:
            self.showFWHM = showFWHM
        if self.type == 'XY':
            if self.showFWHM:
                self.figure.axes.text(self.min_x*0.96,self.max_y*0.8,"Average FWHM = {:5.4f} \u212B\u207B\u00B9\nFWHM Asymmetric Ratio = {:5.3f}". \
                                      format(self.FWHM,self.ratio),color='white',fontsize=self.fontsize-5,bbox={'facecolor':'black','alpha':0.2,'pad':5})

    def replot(self,type,x,y,z,colormap,intensity,nkz):
        self.x_linear = x
        self.y_linear = y
        self.z_linear = z
        self.colormap = colormap
        self.intensity = intensity
        self.nkz = nkz
        self.type = type
        self.figure.clear()
        if self.type == 'XY':
            matrix = self.intensity[:,:,self.nkz]
            max_intensity = np.amax(np.amax(matrix))
            self.cs = self.figure.axes.contourf(self.x_linear,self.y_linear,matrix.T/max_intensity,100,cmap=self.colormap)
            if self.showFWHM:
                self.min_x = np.amin(self.x_linear)
                self.max_y = np.amax(self.y_linear)
                csHM = self.figure.axes.contour(self.x_linear,self.y_linear,matrix.T/max_intensity,levels=[0.5],colors=['black'],linestyles='dashed',linewidths=2)
                self.FWHM = 1.0
                self.ratio = 1.0
                self.ratio = 1.0
                for collection in csHM.collections:
                    path = collection.get_paths()
                    for item in path:
                        x0 = item.vertices[:,0]
                        y0 = item.vertices[:,1]
                        w = np.sqrt(x0**2+y0**2)
                        self.ratio = np.amax(w)/np.amin(w)
                        self.FWHM = np.amax(w)+np.amin(w)
        elif self.type == 'XZ':
            matrix = self.intensity[:,self.nkz,:]
            max_intensity = np.amax(np.amax(matrix))
            self.cs = self.figure.axes.contourf(self.x_linear,self.z_linear,matrix.T/max_intensity,100,cmap=self.colormap)
        elif self.type == 'YZ':
            matrix = self.intensity[self.nkz,:,:]
            max_intensity = np.amax(np.amax(matrix))
            self.cs = self.figure.axes.contourf(self.y_linear,self.z_linear,matrix.T/max_intensity,100,cmap=self.colormap)
        self.cbar = self.figure.fig.colorbar(self.cs,format='%.2f')
        self.refreshFonts(self.fontname,self.fontsize)
        self.refreshFWHM(self.showFWHM)

def Test():
    app = QtWidgets.QApplication(sys.argv)
    simulation = Window()
    simulation.Main()
    sys.exit(app.exec_())

if __name__ == '__main__':
    Test()
