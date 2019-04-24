from PyQt5 import QtCore, QtGui, QtWidgets, QtDataVisualization
import pandas as pd
import itertools
import random
import Process
import numpy as np
import matplotlib.pyplot as plt
from pymatgen.io.cif import CifParser
from pymatgen.core import structure as pgStructure
from pymatgen.core.operations import SymmOp
from pymatgen.core.lattice import Lattice

class Window(QtWidgets.QWidget,Process.Convertor):

    fontsChanged = QtCore.pyqtSignal(str,int)
    viewDirectionChanged = QtCore.pyqtSignal(int)

    def __init__(self):
        super(Window,self).__init__()

    def Main(self):
        self.graph = ScatterGraph()
        self.AFF = pd.read_excel(open('AtomicFormFactors.xlsx','rb'),sheet_name="Atomic Form Factors",index_col=0)
        self.AR = pd.read_excel(open('AtomicRadii.xlsx','rb'),sheet_name="Atomic Radius",index_col=0)
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
        self.hSplitter.addWidget(self.controlPanel)
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
        self.chooseCifButton = QtWidgets.QPushButton("Browse")
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

        self.lattice_constants_box = QtWidgets.QGroupBox("Lattice Constants")
        self.lattice_constants_box.setStyleSheet('QGroupBox::title {color:blue;}')
        self.lattice_constants_grid = QtWidgets.QGridLayout(self.lattice_constants_box)
        self.lattice_constants_label = QtWidgets.QLabel("")
        self.lattice_constants_grid.addWidget(self.lattice_constants_label,0,0)

        self.tab = QtWidgets.QTabWidget()

        self.range_box = QtWidgets.QWidget()
        self.range_grid = QtWidgets.QGridLayout(self.range_box)
        self.range_grid.setContentsMargins(5,5,5,5)
        self.range_grid.setAlignment(QtCore.Qt.AlignTop)
        self.h_range = LabelSlider(1,100,1,1,"h")
        self.k_range = LabelSlider(1,100,1,1,"k")
        self.l_range = LabelSlider(1,100,1,1,"l")
        self.shape_label = QtWidgets.QLabel("Shape")
        self.shape_label.setStyleSheet('QLabel {color:blue;}')
        self.shape = QtWidgets.QComboBox()
        self.shape.addItem("Triangle")
        self.shape.addItem("Square")
        self.shape.addItem("Hexagon")
        self.shape.addItem("Circle")
        self.lateral_size = LabelSlider(1,100,1,1,"Lateral Size",'nm')
        self.z_range_slider = DoubleSlider(-100,100,1,-10,10,"Z range","\u212B",False)
        self.apply_range = QtWidgets.QPushButton("Apply")
        self.apply_range.clicked.connect(self.updateRange)
        self.apply_range.setEnabled(False)
        self.range_grid.addWidget(self.h_range,0,0)
        self.range_grid.addWidget(self.k_range,1,0)
        self.range_grid.addWidget(self.l_range,2,0)
        self.range_grid.addWidget(self.shape_label,3,0)
        self.range_grid.addWidget(self.shape,4,0)
        self.range_grid.addWidget(self.lateral_size,5,0)
        self.range_grid.addWidget(self.z_range_slider,6,0)
        self.range_grid.addWidget(self.apply_range,7,0)
        self.tab.addTab(self.range_box,"Real space range")

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
        self.apply_reciprocal_range = QtWidgets.QPushButton("Apply")
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
        self.tab.addTab(self.reciprocal_range_box,"Reciprocal space range")

        self.plotOptions = QtWidgets.QGroupBox("Plot Options")
        self.plotOptions.setStyleSheet('QGroupBox::title {color:blue;}')
        self.plotOptionsGrid = QtWidgets.QGridLayout(self.plotOptions)
        self.KzIndex = DoubleSlider(0,self.number_of_steps_perp.value()-1,1,0,0,"Kz Index range")
        self.KxyIndex = DoubleSlider(0,self.number_of_steps_para.value()-1,1,0,0,"Kxy Index range")
        self.reciprocalMapfontListLabel = QtWidgets.QLabel("Font Name")
        self.reciprocalMapfontList = QtWidgets.QFontComboBox()
        self.reciprocalMapfontList.setCurrentFont(QtGui.QFont("Arial"))
        self.reciprocalMapfontSizeLabel = QtWidgets.QLabel("Font Size ({})".format(20))
        self.reciprocalMapfontSizeLabel.setFixedWidth(160)
        self.reciprocalMapfontSizeSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.reciprocalMapfontSizeSlider.setMinimum(1)
        self.reciprocalMapfontSizeSlider.setMaximum(100)
        self.reciprocalMapfontSizeSlider.setValue(20)
        self.reciprocalMapfontSizeSlider.valueChanged.connect(self.RefreshReciprocalMapFontSize)
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
        self.plotOptionsGrid.addWidget(self.KxyIndex,0,0,1,3)
        self.plotOptionsGrid.addWidget(self.KzIndex,1,0,1,3)
        self.plotOptionsGrid.addWidget(self.reciprocalMapfontListLabel,2,0,1,1)
        self.plotOptionsGrid.addWidget(self.reciprocalMapfontList,2,1,1,2)
        self.plotOptionsGrid.addWidget(self.reciprocalMapfontSizeLabel,3,0,1,1)
        self.plotOptionsGrid.addWidget(self.reciprocalMapfontSizeSlider,3,1,1,2)
        self.plotOptionsGrid.addWidget(self.show_XY_plot_button,4,0,1,1)
        self.plotOptionsGrid.addWidget(self.show_XZ_plot_button,4,1,1,1)
        self.plotOptionsGrid.addWidget(self.show_YZ_plot_button,4,2,1,1)
        self.plotOptionsGrid.addWidget(self.save_Results_button,5,0,1,3)

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
        self.themeList.addItem("Qt")
        self.themeList.addItem("Primary Colors")
        self.themeList.addItem("Digia")
        self.themeList.addItem("Stone Moss")
        self.themeList.addItem("Army Blue")
        self.themeList.addItem("Retro")
        self.themeList.addItem("Ebony")
        self.themeList.addItem("Isabelle")

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
        self.statusGrid.addWidget(self.logBoxScroll,0,0)
        self.vLayout_left.addWidget(self.statusBar)

        themeLabel = QtWidgets.QLabel("Theme")
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
        self.tab.addTab(self.appearance,"Appearance")
        self.tab.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Fixed)

        self.vLayout.addWidget(self.chooseCif)
        self.vLayout.addWidget(self.chooseDestination)
        self.vLayout.addWidget(self.lattice_constants_box)
        self.vLayout.addWidget(self.tab)
        self.vLayout.addWidget(self.plotOptions)

        self.themeList.currentIndexChanged.connect(self.graph.changeTheme)
        self.themeList.setCurrentIndex(3)
        self.graph.logMessage.connect(self.updateLog)
        self.viewDirectionChanged.connect(self.graph.updateViewDirection)
        self.showMaximized()


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

    def updateLattice(self,a,b,c,alpha,beta,gamma):
        self.lattice_constants_label.setText("a = {:5.3f}, b = {:5.3f}, c = {:5.3f}\nalpha = {:5.3f}(\u00B0), beta = {:5.3f}(\u00B0), gamma = {:5.3f}(\u00B0)". \
                                            format(a,b,c,alpha,beta,gamma))

    def updateColors(self,name,color):
        self.colorSheet[name] = color
        self.graph.updateColors(self.colorSheet)

    def updateSize(self,name,size):
        self.graph.updateSize(name,size)

    def updateLog(self,msg):
        self.logBox.append(QtCore.QTime.currentTime().toString("hh:mm:ss")+"\u00A0\u00A0\u00A0\u00A0"+msg)

    def updateRange(self):
        self.updateLog("Applying changes in the real space range ......")
        QtCore.QCoreApplication.processEvents()
        self.graph.clear()
        self.box = self.get_boxed_structure(self.molecule, self.structure.lattice.a, self.structure.lattice.b, \
                                            self.structure.lattice.c, self.structure.lattice.alpha,self.structure.lattice.beta, \
                                            self.structure.lattice.gamma, images=(int(self.h_range.getValue()),int(self.k_range.getValue()),int(self.l_range.getValue())))
        self.lateralSize = self.lateral_size.getValue()*10
        self.z_range = self.z_range_slider.values()
        self.diffraction_intensity = self.graph.addData(self.box.sites,self.colorSheet,self.lateralSize,self.z_range,\
                                                        self.shape.currentText(),self.Kx,self.Ky,self.Kz,self.AFF,self.AR)
        self.updateLog("New real space range applied!")

    def updateReciprocalRange(self):
        self.updateLog("Applying changes in the reciprocal space range ......")
        QtCore.QCoreApplication.processEvents()
        self.graph.clear()
        self.KRange = [self.Kx_range.values(),self.Ky_range.values(),self.Kz_range.values()]
        self.x_linear = np.linspace(self.KRange[0][0],self.KRange[0][1],self.number_of_steps_para.value())
        self.y_linear = np.linspace(self.KRange[1][0],self.KRange[1][1],self.number_of_steps_para.value())
        self.z_linear = np.linspace(self.KRange[2][0],self.KRange[2][1],self.number_of_steps_perp.value())
        self.Kx,self.Ky,self.Kz = np.meshgrid(self.x_linear,self.y_linear,self.z_linear)
        self.diffraction_intensity = self.graph.addData(self.box.sites,self.colorSheet,self.lateralSize,self.z_range,\
                                                        self.shape.currentText(),self.Kx,self.Ky,self.Kz,self.AFF,self.AR)
        self.updateLog("New K range applied!")

    def showXYPlot(self):
        for i in range(int(self.KzIndex.values()[0]),int(self.KzIndex.values()[1]+1)):
            self.show_2D('XY',self.diffraction_intensity,i,self.lateralSize/10,\
                         self.reciprocalMapfontList.currentFont().family(),self.reciprocalMapfontSizeSlider.value())
        self.updateLog("Simulated diffraction patterns obtained!")
        plt.show()

    def showXZPlot(self):
        for i in range(int(self.KxyIndex.values()[0]),int(self.KxyIndex.values()[1]+1)):
            self.show_2D('XZ',self.diffraction_intensity,i,self.lateralSize/10, \
                         self.reciprocalMapfontList.currentFont().family(),self.reciprocalMapfontSizeSlider.value())
        self.updateLog("Simulated diffraction patterns obtained!")
        plt.show()

    def showYZPlot(self):
        for i in range(int(self.KxyIndex.values()[0]),int(self.KxyIndex.values()[1]+1)):
            self.show_2D('YZ',self.diffraction_intensity,i,self.lateralSize/10, \
                         self.reciprocalMapfontList.currentFont().family(),self.reciprocalMapfontSizeSlider.value())
        self.updateLog("Simulated diffraction patterns obtained!")
        plt.show()

    def getCifPath(self):
        path = QtWidgets.QFileDialog.getOpenFileName(None,"Choose The CIF File",'./',filter="CIF (*.cif);;All Files (*.*)")[0]
        if not path == "":
            self.updateLog("CIF opened!")
            self.cifPath = path
            self.chooseCifLabel.setText("The path of the CIF file is:\n"+self.cifPath)
            self.loadStructure(int(self.h_range.getValue()),int(self.k_range.getValue()),int(self.l_range.getValue()))

    def loadStructure(self,h,k,l):
        self.graph.clear()
        self.structure = CifParser(self.cifPath).get_structures(primitive=False)[0]
        self.updateLattice(self.structure.lattice.a,self.structure.lattice.b,self.structure.lattice.c,\
                           self.structure.lattice.alpha,self.structure.lattice.beta,self.structure.lattice.gamma)
        self.molecule = pgStructure.Molecule.from_sites(self.structure.sites)
        self.box = self.get_boxed_structure(self.molecule, self.structure.lattice.a, self.structure.lattice.b, \
                                            self.structure.lattice.c, self.structure.lattice.alpha,self.structure.lattice.beta,\
                                            self.structure.lattice.gamma, images=(h,k,l))
        self.colorSheet = {}
        self.colors = ['magenta','cyan','green','yellow','red','black','darkGreen','darkYellow','darkCyan','darkMagenta','darkRed','darkBlue','darkGray']
        self.element_species = set(site.specie for site in self.box.sites)
        colorPalette = QtWidgets.QGroupBox("Color Palette")
        colorPalette.setStyleSheet('QGroupBox::title {color:blue;}')
        grid = QtWidgets.QVBoxLayout(colorPalette)
        for i,name in enumerate(self.element_species):
            colorPicker = ColorPicker(str(name),self.colors[i],self.AR.loc[str(name)].at['Normalized Radius'])
            colorPicker.colorChanged.connect(self.updateColors)
            colorPicker.sizeChanged.connect(self.updateSize)
            self.colorSheet[str(name)] = self.colors[i]
            grid.addWidget(colorPicker)
        if self.vLayout.count()>5:
            item = self.vLayout.takeAt(self.vLayout.count()-1)
            widget = item.widget()
            widget.deleteLater()
            del item
        self.vLayout.addWidget(colorPalette)
        self.lateralSize = self.lateral_size.getValue()*10
        self.z_range = self.z_range_slider.values()
        self.diffraction_intensity = self.graph.addData(self.box.sites,self.colorSheet,self.lateralSize,self.z_range,\
                                                        self.shape.currentText(), self.Kx,self.Ky,self.Kz,self.AFF,self.AR)
        self.graph.changeFonts(self.fontList.currentFont().family(),self.fontSizeSlider.value())
        self.graph.changeShadowQuality(self.shadowQuality.currentIndex())
        self.updateLog("Structure loaded!")
        self.apply_range.setEnabled(True)
        self.apply_reciprocal_range.setEnabled(True)
        self.show_XY_plot_button.setEnabled(True)
        self.show_XZ_plot_button.setEnabled(True)
        self.show_YZ_plot_button.setEnabled(True)
        self.save_Results_button.setEnabled(True)

    def saveResults(self):
        self.mtx2vtp(self.currentDestination,self.destinationNameEdit.text(),self.diffraction_intensity,self.KRange,\
                     self.number_of_steps_para.value(),self.number_of_steps_perp.value())

    def show_2D(self,type,intensity,nkz,size,fontname,fontsize):
        figure = plt.figure()
        ax = figure.add_subplot(111)
        if type == 'XY':
            matrix = intensity[:,:,nkz]
            max_intensity = np.amax(np.amax(matrix))
            cs = ax.contourf(self.x_linear,self.y_linear,matrix/max_intensity,100,cmap='jet')
            min_x = np.amin(self.x_linear)
            max_y = np.amax(self.y_linear)
            csHM = ax.contour(self.x_linear,self.y_linear,matrix/max_intensity,levels=[0.5],colors=['black'],linestyles='dashed',linewidths=2)
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
            ax.set_aspect(1)
            ax.set_title('Simulated 2D reciprocal space map\nKz = {:5.2f} (\u212B\u207B\u00B9), lateral size = {:5.2f} (nm)'.\
                         format(self.z_linear[nkz],size),fontsize=fontsize,pad=30)
            ax.text(min_x*0.96,max_y*0.8,"Average FWHM = {:5.4f} \u212B\u207B\u00B9\nFWHM Asymmetric Ratio = {:5.3f}". \
                    format(FWHM,ratio),color='white',fontsize=fontsize-5,bbox={'facecolor':'black','alpha':0.2,'pad':5})
            ax.set_xlabel(r'$K_{x}$ $(\AA^{-1})$',fontname=fontname,fontsize=fontsize)
            ax.set_ylabel(r'$K_{y}$ $(\AA^{-1})$',fontname=fontname,fontsize=fontsize)
            ax.tick_params(which='both', labelsize=fontsize)
            cbar = figure.colorbar(cs,format='%.2f')
            cbar.ax.set_ylabel("Normalized Intensity",fontname=fontname,fontsize=fontsize)
            cbar.ax.tick_params(labelsize=fontsize)
        elif type == 'XZ':
            matrix = intensity[:,nkz,:]
            max_intensity = np.amax(np.amax(matrix))
            cs = ax.contourf(self.x_linear,self.z_linear,matrix/max_intensity,100,cmap='jet')
            ax.set_aspect(1)
            ax.set_title('Simulated 2D reciprocal space map\nKy = {:5.2f} (\u212B\u207B\u00B9), lateral size = {:5.2f} (nm)'. \
                         format(self.y_linear[nkz],size),fontsize=fontsize,pad=30)
            ax.set_xlabel(r'$K_{x}$ $(\AA^{-1})$',fontname=fontname,fontsize=fontsize)
            ax.set_ylabel(r'$K_{z}$ $(\AA^{-1})$',fontname=fontname,fontsize=fontsize)
            ax.tick_params(which='both', labelsize=fontsize)
            cbar = figure.colorbar(cs,format='%.2f')
            cbar.ax.set_ylabel("Normalized Intensity",fontname=fontname,fontsize=fontsize)
            cbar.ax.tick_params(labelsize=fontsize)
        elif type == 'YZ':
            matrix = intensity[nkz,:,:]
            max_intensity = np.amax(np.amax(matrix))
            cs = ax.contourf(self.y_linear,self.z_linear,matrix/max_intensity,100,cmap='jet')
            ax.set_aspect(1)
            ax.set_title('Simulated 2D reciprocal space map\nKx = {:5.2f} (\u212B\u207B\u00B9), lateral size = {:5.2f} (nm)'. \
                         format(self.x_linear[nkz],size),fontsize=fontsize,pad=30)
            ax.set_xlabel(r'$K_{y}$ $(\AA^{-1})$',fontname=fontname,fontsize=fontsize)
            ax.set_ylabel(r'$K_{z}$ $(\AA^{-1})$',fontname=fontname,fontsize=fontsize)
            ax.tick_params(which='both', labelsize=fontsize)
            cbar = figure.colorbar(cs,format='%.2f')
            cbar.ax.set_ylabel("Normalized Intensity",fontname=fontname,fontsize=fontsize)
            cbar.ax.tick_params(labelsize=fontsize)


    def get_boxed_structure(self,molecule,a,b,c,alpha,beta,gamma,images=(1,1,1),random_rotation = False,min_dist=1,cls=None,offset=None):

        if offset is None:
            offset = np.array([0, 0, 0])

        unit_lattice = Lattice.from_parameters(a, b, c, alpha, beta, gamma)
        lattice = Lattice.from_parameters(a * (2*images[0]+1), b * (2*images[1]+1),
                                          c * (2*images[2]+1),
                                          alpha, beta, gamma)
        nimages = (2*images[0]+1) * (2*images[1]+1) * (2*images[2]+1)
        coords = []

        centered_coords = molecule.cart_coords# - molecule.center_of_mass + offset

        for i, j, k in itertools.product(list(range(-images[0],images[0]+1)),
                                         list(range(-images[1],images[1]+1)),
                                         list(range(-images[2],images[2]+1))):
            box_center = np.dot(unit_lattice.matrix.T, [i,j,k]).T
            if random_rotation:
                while True:
                    op = SymmOp.from_origin_axis_angle(
                        (0, 0, 0), axis=np.random.rand(3),
                        angle=random.uniform(-180, 180))
                    m = op.rotation_matrix
                    new_coords = np.dot(m, centered_coords.T).T + box_center
                    if len(coords) == 0:
                        break
                    distances = lattice.get_all_distances(
                        lattice.get_fractional_coords(new_coords),
                        lattice.get_fractional_coords(coords))
                    if np.amin(distances) > min_dist:
                        break
            else:
                new_coords = centered_coords + box_center
            coords.extend(new_coords)
        sprops = {k: v * nimages for k, v in molecule.site_properties.items()}

        if cls is None:
            cls = pgStructure.Structure

        return cls(lattice, molecule.species * nimages, coords,coords_are_cartesian=True,site_properties=sprops).get_sorted_structure()

    def RefreshFontSize(self):
        self.fontSizeLabel.setText("Adjust Font Size ({})".format(self.fontSizeSlider.value()))
        self.fontsChanged.emit(self.fontList.currentFont().family(),self.fontSizeSlider.value())

    def RefreshFontName(self):
        self.fontsChanged.emit(self.fontList.currentFont().family(),self.fontSizeSlider.value())

    def RefreshReciprocalMapFontSize(self):
        self.reciprocalMapfontSizeLabel.setText("Font Size ({})".format(self.reciprocalMapfontSizeSlider.value()))

class ScatterGraph(QtDataVisualization.Q3DScatter):

    logMessage = QtCore.pyqtSignal(str)

    def __init__(self):
        super(ScatterGraph,self).__init__()

    def addData(self,data,colorSheet,range,z_range,shape,Kx,Ky,Kz,AFF,AR):
        self.colorSheet = colorSheet
        self.element_species = list(str(site.specie) for site in data)
        self.coords = (site.coords for site in data)
        self.coordinateStatus = 2
        self.axisX().setTitle("X (\u212B)")
        self.axisY().setTitle("Z (\u212B)")
        self.axisZ().setTitle("Y (\u212B)")
        self.axisX().setTitleVisible(True)
        self.axisY().setTitleVisible(True)
        self.axisZ().setTitleVisible(True)
        self.atomSeries = {}
        Psi = np.multiply(Kx,0).astype('complex128')
        species_dict = set(AFF.index.tolist())
        for i,coord in enumerate(self.coords):
            if shape == "Triangle":
                condition = (coord[1]>(-range/2/np.sqrt(3))) and \
                            (coord[1]<(-np.sqrt(3)*coord[0]+range/np.sqrt(3))) and \
                            (coord[1]<(np.sqrt(3)*coord[0]+range/np.sqrt(3)))
            elif shape == "Square":
                condition = (coord[0]> -range/2) and \
                            (coord[0]< range/2) and \
                            (coord[1]> -range/2) and \
                            (coord[1]< range/2)
            elif shape == "Hexagon":
                condition = (coord[1] < range*np.sqrt(3)/2) and \
                            (coord[1] > -range*np.sqrt(3)/2) and \
                            (coord[1] < (-np.sqrt(3)*coord[0]+np.sqrt(3)*range)) and \
                            (coord[1] < (np.sqrt(3)*coord[0]+np.sqrt(3)*range)) and \
                            (coord[1] > (-np.sqrt(3)*coord[0]-np.sqrt(3)*range)) and \
                            (coord[1] > (np.sqrt(3)*coord[0]-np.sqrt(3)*range))
            elif shape == "Circle":
                condition = (np.sqrt(coord[0]*coord[0]+coord[1]*coord[1]) < range)
            if condition and (coord[2]<z_range[1] and coord[2]>z_range[0]):
                dataArray = []
                radii = AR.loc[self.element_species[i]].at['Normalized Radius']
                ScatterProxy = QtDataVisualization.QScatterDataProxy()
                ScatterSeries = QtDataVisualization.QScatter3DSeries(ScatterProxy)
                item = QtDataVisualization.QScatterDataItem()
                vector = QtGui.QVector3D(coord[0],coord[2],coord[1])
                if self.element_species[i] in species_dict:
                    af_row = AFF.loc[self.element_species[i]]
                elif self.element_species[i]+'1+' in species_dict:
                    af_row = AFF.loc[self.element_species[i]+'1+']
                elif self.element_species[i]+'2+' in species_dict:
                    af_row = AFF.loc[self.element_species[i]+'2+']
                elif self.element_species[i]+'3+' in species_dict:
                    af_row = AFF.loc[self.element_species[i]+'3+']
                elif self.element_species[i]+'4+' in species_dict:
                    af_row = AFF.loc[self.element_species[i]+'4+']
                elif self.element_species[i]+'1-' in species_dict:
                    af_row = AFF.loc[self.element_species[i]+'1-']
                elif self.element_species[i]+'2-' in species_dict:
                    af_row = AFF.loc[self.element_species[i]+'2-']
                elif self.element_species[i]+'3-' in species_dict:
                    af_row = AFF.loc[self.element_species[i]+'3-']
                elif self.element_species[i]+'4-' in species_dict:
                    af_row = AFF.loc[self.element_species[i]+'4-']
                else:
                    self.Raise_Error("No scattering coefficient for %s"%self.element_species[i])
                    break
                af = af_row.at['c']+af_row.at['a1']*np.exp(-af_row.at['b1']*(np.multiply(Kx,Kx)+np.multiply(Ky,Ky)+np.multiply(Kz,Kz))/4/np.pi)\
                                   +af_row.at['a2']*np.exp(-af_row.at['b2']*(np.multiply(Kx,Kx)+np.multiply(Ky,Ky)+np.multiply(Kz,Kz))/4/np.pi)\
                                   +af_row.at['a3']*np.exp(-af_row.at['b3']*(np.multiply(Kx,Kx)+np.multiply(Ky,Ky)+np.multiply(Kz,Kz))/4/np.pi)\
                                   +af_row.at['a4']*np.exp(-af_row.at['b4']*(np.multiply(Kx,Kx)+np.multiply(Ky,Ky)+np.multiply(Kz,Kz))/4/np.pi)
                Psi += np.multiply(af,np.exp(1j*(Kx*coord[0]+Ky*coord[1]+Kz*coord[2])))
                item.setPosition(vector)
                dataArray.append(item)
                ScatterProxy.resetArray(dataArray)
                ScatterSeries.setMeshSmooth(True)
                ScatterSeries.setColorStyle(QtDataVisualization.Q3DTheme.ColorStyleUniform)
                ScatterSeries.setBaseColor(QtGui.QColor(self.colorSheet[self.element_species[i]]))
                ScatterSeries.setItemSize(radii/100)
                ScatterSeries.setSingleHighlightColor(QtGui.QColor('white'))
                ScatterSeries.setItemLabelFormat(self.element_species[i]+' (@xLabel, @zLabel, @yLabel)')
                self.atomSeries[i] = ScatterSeries
                self.addSeries(ScatterSeries)
        self.scene().activeCamera().setCameraPreset(QtDataVisualization.Q3DCamera.CameraPresetDirectlyAbove)
        intensity = np.multiply(Psi.astype('float64'),np.conj(Psi.astype('float64')))
        return intensity

    def clear(self):
        for series in self.seriesList():
            self.removeSeries(series)

    def updateCoordinates(self,status):
        self.coordinateStatus = status
        if status == 2:
            self.axisX().setTitleVisible(True)
            self.axisY().setTitleVisible(True)
            self.axisZ().setTitleVisible(True)
            self.activeTheme().setBackgroundEnabled(True)
            self.activeTheme().setGridEnabled(True)
            self.activeTheme().setLabelTextColor(self.original_label_text_color)
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

    def updateColors(self,colorSheet):
        self.colorSheet = colorSheet
        for i,series in self.atomSeries.items():
            series.setBaseColor(QtGui.QColor(self.colorSheet[self.element_species[i]]))

    def updateSize(self,name,size):
        for i,series in self.atomSeries.items():
            if name == self.element_species[i]:
                series.setItemSize(size)

    def changeFonts(self,fontname,fontsize):
        self.activeTheme().setFont(QtGui.QFont(fontname,fontsize))

    def changeTheme(self, theme):
        self.activeTheme().setType(QtDataVisualization.Q3DTheme.Theme(theme))
        self.original_label_text_color = self.activeTheme().labelTextColor()
        self.activeTheme().setLabelBackgroundEnabled(False)
        self.activeTheme().setLabelBorderEnabled(False)
        try:
            self.updateColors(self.colorSheet)
            self.updateCoordinates(self.coordinateStatus)
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

    valueChanged = QtCore.pyqtSignal(float)

    def __init__(self,min,max,initial,scale,text,unit='',orientation = QtCore.Qt.Horizontal):
        super(LabelSlider, self).__init__()
        self.scale = scale
        self.label_text = text
        self.min = min
        self.max = max
        self.unit = unit
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

    def reset(self,min,max,initial,scale):
        self.scale = scale
        self.min = min
        self.max = max
        self.valueSlider.setMinimum(min)
        self.valueSlider.setMaximum(max)
        self.valueSlider.setValue(initial*scale)
        self.value_changed(initial*scale)

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
        self.valueChanged.emit(value/self.scale)

    def getValue(self):
        return self.valueSlider.value()/self.scale

class DoubleSlider(QtWidgets.QWidget):
    valueChanged = QtCore.pyqtSignal()

    def __init__(self,minimum,maximum,scale,head,tail,text,unit='',lock = False,direction='horizontal'):
        super(DoubleSlider,self).__init__()
        self.currentMin, self.currentMax = int(head),int(tail)
        self.text = text
        self.scale = scale
        self.unit = unit
        self.lock = lock
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

    def setMaximum(self,value):
        if self.lock:
            self.minSlider.setMaximum(0)
        else:
            self.minSlider.setMaximum(value)
        self.maxSlider.setMaximum(value)

    def setHead(self,value):
        self.minSlider.setValue(int(value*self.scale))

    def setTail(self,value):
        self.maxSlider.setValue(int(value*self.scale))

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
        self.valueChanged.emit()

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
        self.valueChanged.emit()

    def setEnabled(self,enable):
        self.minSlider.setEnabled(enable)
        self.maxSlider.setEnabled(enable)

class ColorPicker(QtWidgets.QWidget):

    colorChanged = QtCore.pyqtSignal(str,str)
    sizeChanged = QtCore.pyqtSignal(str,float)

    def __init__(self,name,color,size=20):
        super(ColorPicker,self).__init__()
        self.color = color
        self.name = name
        self.size = size
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
        self.colorChanged.emit(self.name,self.color)

    def changeSize(self,text):
        self.size = int(text)
        self.sizeChanged.emit(self.name, self.size/100)

    def getSize(self):
        return self.size

    def setColor(self,color):
        self.PB.setStyleSheet("background-color:"+color)
        self.color = color

    def getColor(self):
        return self.color

#def Test():
#    app = QtWidgets.QApplication(sys.argv)
#    simulation = Simulate2DPattern()
#    sys.exit(app.exec_())
#
#if __name__ == '__main__':
#    Test()
