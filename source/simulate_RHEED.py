from PyQt5 import QtCore, QtGui, QtWidgets, QtDataVisualization
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.collections import LineCollection
from my_widgets import LabelLineEdit, IndexedComboBox, LockableDoubleSlider, LabelSlider, InfoBoard, IndexedPushButton, DynamicalColorMap, IndexedColorPicker
from process import Convertor, DiffractionPattern, TAPD_Simulation
from pymatgen.io.cif import CifParser
from pymatgen.core import structure as pgStructure
from pymatgen.core.operations import SymmOp
from pymatgen.core.lattice import Lattice
import browser
import itertools
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re
import sys

class Window(QtWidgets.QWidget):

    FONTS_CHANGED = QtCore.pyqtSignal(str,int)
    VIEW_DIRECTION_CHANGED = QtCore.pyqtSignal(int)
    PROGRESS_ADVANCE = QtCore.pyqtSignal(int,int,int)
    PROGRESS_HOLD = QtCore.pyqtSignal()
    PROGRESS_END = QtCore.pyqtSignal()
    REFRESH_PLOT_FONTS = QtCore.pyqtSignal(str,int)
    REFRESH_PLOT_FWHM = QtCore.pyqtSignal(bool)
    REFRESH_PLOT_COLORMAP = QtCore.pyqtSignal(str)
    DELETE_SAMPLE = QtCore.pyqtSignal(int)
    UPDATE_INOFRMATION_BOARD = QtCore.pyqtSignal(int,str,float,float,float,float,float,float)
    UPDATE_CAMERA_POSITION = QtCore.pyqtSignal(float,float,float)
    STOP_CALCULATION = QtCore.pyqtSignal()
    STOP_TAPD_WORKER = QtCore.pyqtSignal()

    def __init__(self):
        super(Window,self).__init__()
        self.convertor_worker = Convertor()

    def main(self):
        self.graph = ScatterGraph()
        self.AFF = pd.read_excel(open('../doc/AtomicFormFactors.xlsx','rb'),sheet_name="Atomic Form Factors",index_col=0)
        self.AR = pd.read_excel(open('../doc/AtomicRadii.xlsx','rb'),sheet_name="Atomic Radius",index_col=0)
        self.colors = ['magenta','cyan','green','yellow','red','black','darkGreen','darkYellow','darkCyan','darkMagenta','darkRed','darkBlue','darkGray']
        self.structure_index = 0
        self.data_index_set = set()
        self.sample_index_set = set()
        self.sample_tab_index = []
        self.deleted_tab_index = []
        self.real_space_specification_dict = {}
        self.colorSheet = {}
        self.molecule_dict = {}
        self.structure_dict = {}
        self.box = {}
        self.TAPD = {}
        self.element_species = {}
        self.z_shift_history = {}
        self.substrate_path = None
        self.epilayer_path = None
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

        self.chooseCif = QtWidgets.QWidget()
        self.chooseCifGrid = QtWidgets.QGridLayout(self.chooseCif)
        self.chooseCifBrowser = browser.Browser(self.chooseCif, {"*.cif","*.CIF"})
        self.chooseCifLabel = QtWidgets.QLabel("The path of the CIF file is:\n")
        self.chooseCifLabel.setAlignment(QtCore.Qt.AlignTop)
        self.chooseCifLabel.setWordWrap(True)
        self.chooseCifButton = QtWidgets.QPushButton("Add CIF")
        self.chooseCifButton.clicked.connect(self.get_cif_path)
        self.chooseCifGrid.addWidget(self.chooseCifBrowser,0,0)
        self.chooseCifGrid.addWidget(self.chooseCifLabel,1,0)
        self.chooseCifGrid.addWidget(self.chooseCifButton,2,0)
        self.chooseCifBrowser.FILE_DOUBLE_CLICKED.connect(self.set_cif_path)

        self.TAPD_model = QtWidgets.QWidget()
        self.TAPD_model_grid = QtWidgets.QGridLayout(self.TAPD_model)
        self.TAPD_substrate_label = QtWidgets.QLabel("The path of the substrate CIF is:\n")
        self.TAPD_substrate_label.setAlignment(QtCore.Qt.AlignTop)
        self.TAPD_substrate_label.setWordWrap(True)
        self.TAPD_add_substrate_button = QtWidgets.QPushButton("Add Substrate")
        self.TAPD_add_substrate_button.clicked.connect(lambda text: self.load_cif(text='Choose Substrate'))
        self.TAPD_epilayer_label = QtWidgets.QLabel("The path of the epilayer CIF is:\n")
        self.TAPD_epilayer_label.setAlignment(QtCore.Qt.AlignTop)
        self.TAPD_epilayer_label.setWordWrap(True)
        self.TAPD_add_epilayer_button = QtWidgets.QPushButton("Add Epilayer")
        self.TAPD_add_epilayer_button.clicked.connect(lambda text: self.load_cif(text='Choose Epilayer'))
        self.TAPD_X_max_label = QtWidgets.QLabel('Maximum length in a direction (\u212B\u207B\u00B9)')
        self.TAPD_X_max = QtWidgets.QLineEdit('50')
        self.TAPD_Y_max_label = QtWidgets.QLabel('Maximum length in b direction (\u212B\u207B\u00B9)')
        self.TAPD_Y_max = QtWidgets.QLineEdit('50')
        self.TAPD_Z_min_label = QtWidgets.QLabel('Z minimum units in c direction')
        self.TAPD_Z_min = QtWidgets.QLineEdit('0')
        self.TAPD_Z_max_label = QtWidgets.QLabel('Z maximum units in c direction')
        self.TAPD_Z_max = QtWidgets.QLineEdit('0.5')
        self.TAPD_Shift_X_label = QtWidgets.QLabel('X shift (\u212B\u207B\u00B9)')
        self.TAPD_Shift_X = QtWidgets.QLineEdit('0')
        self.TAPD_Shift_Y_label = QtWidgets.QLabel('Y shift (\u212B\u207B\u00B9)')
        self.TAPD_Shift_Y = QtWidgets.QLineEdit('0')
        self.TAPD_Shift_Z_label = QtWidgets.QLabel('Z shift (\u212B\u207B\u00B9)')
        self.TAPD_Shift_Z = QtWidgets.QLineEdit('3')
        self.TAPD_substrate_orientation_label = QtWidgets.QLabel('Substrate orientation')
        self.TAPD_substrate_orientation = QtWidgets.QComboBox()
        self.TAPD_substrate_orientation.addItem('(001)')
        self.TAPD_substrate_orientation.addItem('(010)')
        self.TAPD_substrate_orientation.addItem('(100)')
        self.TAPD_substrate_orientation.addItem('(111)')
        self.TAPD_epilayer_orientation_label = QtWidgets.QLabel('Epilayer orientation')
        self.TAPD_epilayer_orientation = QtWidgets.QComboBox()
        self.TAPD_epilayer_orientation.addItem('(001)')
        self.TAPD_epilayer_orientation.addItem('(010)')
        self.TAPD_epilayer_orientation.addItem('(100)')
        self.TAPD_epilayer_orientation.addItem('(111)')
        self.TAPD_plot_Voronoi_label = QtWidgets.QLabel('Plot Voronoi diagram?')
        self.TAPD_plot_Voronoi = QtWidgets.QCheckBox()
        self.TAPD_plot_Voronoi.setChecked(False)
        self.TAPD_add_atoms_label = QtWidgets.QLabel('Add atoms to the canvas?')
        self.TAPD_add_atoms = QtWidgets.QCheckBox()
        self.TAPD_add_atoms.setChecked(True)
        self.TAPD_add_substrate_label = QtWidgets.QLabel('Add substrate?')
        self.TAPD_add_substrate = QtWidgets.QCheckBox()
        self.TAPD_add_substrate.setChecked(False)
        self.TAPD_add_epilayer_label = QtWidgets.QLabel('Add epilayer?')
        self.TAPD_add_epilayer = QtWidgets.QCheckBox()
        self.TAPD_add_epilayer.setChecked(True)
        self.TAPD_lattice_or_atoms_label = QtWidgets.QLabel('Use lattice or atoms?')
        self.TAPD_lattice = QtWidgets.QCheckBox("Lattice")
        self.TAPD_atoms = QtWidgets.QCheckBox("Atoms")
        self.TAPD_latticeOrAtoms = QtWidgets.QButtonGroup()
        self.TAPD_latticeOrAtoms.setExclusive(True)
        self.TAPD_latticeOrAtoms.addButton(self.TAPD_lattice)
        self.TAPD_latticeOrAtoms.addButton(self.TAPD_atoms)
        self.TAPD_atoms.setChecked(True)

        self.TAPD_distribution_function_label = QtWidgets.QLabel('Choose the distribution function')
        self.TAPD_distribution_function = QtWidgets.QComboBox()
        self.TAPD_distribution_function.addItem('geometric')
        self.TAPD_distribution_function.addItem('completely random')
        self.TAPD_distribution_function.addItem('delta')
        self.TAPD_distribution_function.addItem('binomial')
        self.TAPD_distribution_function.addItem('uniform')
        self.TAPD_distribution_function.currentTextChanged.connect(self.change_distribution_function)

        self.distribution_parameters = QtWidgets.QGroupBox('Parameters of the distribution')
        self.distribution_parameters.setStyleSheet('QGroupBox::title {color:blue;}')
        self.distribution_parameters_grid = QtWidgets.QGridLayout(self.distribution_parameters)
        self.TAPD_geometric_gamma_label = QtWidgets.QLabel('Gamma')
        self.TAPD_geometric_gamma = QtWidgets.QLineEdit('0.1')
        self.distribution_parameters_grid.addWidget(self.TAPD_geometric_gamma_label)
        self.distribution_parameters_grid.addWidget(self.TAPD_geometric_gamma)

        self.load_TAPD_structure_button = QtWidgets.QPushButton("Load Structure")
        self.stop_TAPD_structure_button = QtWidgets.QPushButton("Stop")
        self.reset_TAPD_structure_button = QtWidgets.QPushButton("Reset Structure")
        self.load_TAPD_structure_button.clicked.connect(self.load_TAPD)
        self.stop_TAPD_structure_button.clicked.connect(self.stop_TAPD)
        self.reset_TAPD_structure_button.clicked.connect(self.reset_TAPD)

        self.TAPD_model_grid.addWidget(self.TAPD_substrate_label,0,0,1,3)
        self.TAPD_model_grid.addWidget(self.TAPD_add_substrate_button,0,3,1,1)
        self.TAPD_model_grid.addWidget(self.TAPD_substrate_orientation_label,1,0,1,4)
        self.TAPD_model_grid.addWidget(self.TAPD_substrate_orientation,2,0,1,4)
        self.TAPD_model_grid.addWidget(self.TAPD_epilayer_label,3,0,1,3)
        self.TAPD_model_grid.addWidget(self.TAPD_add_epilayer_button,3,3,1,1)
        self.TAPD_model_grid.addWidget(self.TAPD_epilayer_orientation_label,4,0,1,4)
        self.TAPD_model_grid.addWidget(self.TAPD_epilayer_orientation,5,0,1,4)
        self.TAPD_model_grid.addWidget(self.TAPD_X_max_label,6,0,1,4)
        self.TAPD_model_grid.addWidget(self.TAPD_X_max,7,0,1,4)
        self.TAPD_model_grid.addWidget(self.TAPD_Y_max_label,8,0,1,4)
        self.TAPD_model_grid.addWidget(self.TAPD_Y_max,9,0,1,4)
        self.TAPD_model_grid.addWidget(self.TAPD_Z_min_label,10,0,1,4)
        self.TAPD_model_grid.addWidget(self.TAPD_Z_min,11,0,1,4)
        self.TAPD_model_grid.addWidget(self.TAPD_Z_max_label,12,0,1,4)
        self.TAPD_model_grid.addWidget(self.TAPD_Z_max,13,0,1,4)
        self.TAPD_model_grid.addWidget(self.TAPD_Shift_X_label,14,0,1,4)
        self.TAPD_model_grid.addWidget(self.TAPD_Shift_X,15,0,1,4)
        self.TAPD_model_grid.addWidget(self.TAPD_Shift_Y_label,16,0,1,4)
        self.TAPD_model_grid.addWidget(self.TAPD_Shift_Y,17,0,1,4)
        self.TAPD_model_grid.addWidget(self.TAPD_Shift_Z_label,18,0,1,4)
        self.TAPD_model_grid.addWidget(self.TAPD_Shift_Z,19,0,1,4)
        self.TAPD_model_grid.addWidget(self.TAPD_plot_Voronoi_label,20,0,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_plot_Voronoi,20,2,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_add_atoms_label,21,0,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_add_atoms,21,2,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_add_substrate_label,22,0,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_add_substrate,22,2,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_add_epilayer_label,23,0,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_add_epilayer,23,2,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_lattice_or_atoms_label,24,0,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_lattice,24,2,1,1)
        self.TAPD_model_grid.addWidget(self.TAPD_atoms,24,3,1,1)
        self.TAPD_model_grid.addWidget(self.TAPD_distribution_function_label,25,0,1,4)
        self.TAPD_model_grid.addWidget(self.TAPD_distribution_function,26,0,1,4)
        self.TAPD_model_grid.addWidget(self.distribution_parameters,27,0,1,4)
        self.TAPD_model_grid.addWidget(self.load_TAPD_structure_button,28,0,1,1)
        self.TAPD_model_grid.addWidget(self.stop_TAPD_structure_button,28,1,1,1)
        self.TAPD_model_grid.addWidget(self.reset_TAPD_structure_button,28,2,1,1)

        self.CIF_tab = QtWidgets.QTabWidget()
        self.CIF_tab.addTab(self.chooseCif,'CIF')
        self.CIF_tab.addTab(self.TAPD_model,'TAPD')

        self.chooseDestination = QtWidgets.QGroupBox("Save Destination")
        self.chooseDestination.setStyleSheet('QGroupBox::title {color:blue;}')
        self.destinationGrid = QtWidgets.QGridLayout(self.chooseDestination)
        self.chooseDestinationLabel = QtWidgets.QLabel("The save destination is:\n")
        self.destinationNameLabel = QtWidgets.QLabel("The file name is:")
        self.destinationNameEdit = QtWidgets.QLineEdit('3D_data')
        self.chooseDestinationButton = QtWidgets.QPushButton("Browse...")
        self.chooseDestinationButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
        self.chooseDestinationButton.clicked.connect(self.choose_destination)
        self.destinationGrid.addWidget(self.chooseDestinationLabel,0,0)
        self.destinationGrid.addWidget(self.chooseDestinationButton,0,1)
        self.destinationGrid.addWidget(self.destinationNameLabel,1,0)
        self.destinationGrid.addWidget(self.destinationNameEdit,1,1)


        self.sample_tab = QtWidgets.QTabWidget()
        self.sample_tab.setTabsClosable(True)
        self.sample_tab.tabCloseRequested.connect(self.delete_structure)
        self.sample_tab.setVisible(False)

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
        self.number_of_steps_para.valueChanged.connect(self.update_number_of_steps_para)
        self.number_of_steps_perp_label = QtWidgets.QLabel("Number of K_perp Steps:")
        self.number_of_steps_perp = QtWidgets.QSpinBox()
        self.number_of_steps_perp.setMinimum(1)
        self.number_of_steps_perp.setMaximum(1000)
        self.number_of_steps_perp.setSingleStep(1)
        self.number_of_steps_perp.setValue(5)
        self.number_of_steps_perp.valueChanged.connect(self.update_number_of_steps_perp)
        self.Kx_range = LockableDoubleSlider(-1000,1000,10,-10,10,"Kx range","\u212B\u207B\u00B9",True)
        self.Ky_range = LockableDoubleSlider(-1000,1000,10,-10,10,"Ky range","\u212B\u207B\u00B9",True)
        self.Kz_range = LockableDoubleSlider(-1000,1000,10,0,10,"Kz range","\u212B\u207B\u00B9",False)
        self.apply_reciprocal_range = QtWidgets.QPushButton("Start Calculation")
        self.apply_reciprocal_range.clicked.connect(self.update_reciprocal_range)
        self.apply_reciprocal_range.setEnabled(False)
        self.stop_calculation = QtWidgets.QPushButton("Abort Calculation")
        self.stop_calculation.clicked.connect(self.stop_diffraction_calculation)
        self.stop_calculation.setEnabled(False)

        self.reciprocal_range_grid.addWidget(self.number_of_steps_para_label,0,0,1,1)
        self.reciprocal_range_grid.addWidget(self.number_of_steps_para,0,1,1,1)
        self.reciprocal_range_grid.addWidget(self.number_of_steps_perp_label,1,0,1,1)
        self.reciprocal_range_grid.addWidget(self.number_of_steps_perp,1,1,1,1)
        self.reciprocal_range_grid.addWidget(self.Kx_range,2,0,1,2)
        self.reciprocal_range_grid.addWidget(self.Ky_range,3,0,1,2)
        self.reciprocal_range_grid.addWidget(self.Kz_range,4,0,1,2)
        self.reciprocal_range_grid.addWidget(self.apply_reciprocal_range,7,0,1,2)
        self.reciprocal_range_grid.addWidget(self.stop_calculation,8,0,1,2)
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
        self.load_data_button.clicked.connect(self.load_data)
        self.KzIndex = LockableDoubleSlider(0,self.number_of_steps_perp.value()-1,1,0,0,"Kz Index range")
        self.KxyIndex = LockableDoubleSlider(0,self.number_of_steps_para.value()-1,1,0,0,"Kxy Index range")
        self.showFWHMCheckLabel = QtWidgets.QLabel("Show FWHM Contour?")
        self.showFWHMCheck = QtWidgets.QCheckBox()
        self.showFWHMCheck.setChecked(False)
        self.showFWHMCheck.stateChanged.connect(self.update_FWHM_check)
        self.plot_log_scale_label = QtWidgets.QLabel("Plot in logarithmic scale?")
        self.plot_log_scale = QtWidgets.QCheckBox()
        self.plot_log_scale.setChecked(False)
        self.reciprocalMapfontListLabel = QtWidgets.QLabel("Font Name")
        self.reciprocalMapfontList = QtWidgets.QFontComboBox()
        self.reciprocalMapfontList.setCurrentFont(QtGui.QFont("Arial"))
        self.reciprocalMapfontList.currentFontChanged.connect(self.update_plot_font)
        self.reciprocalMapfontSizeLabel = QtWidgets.QLabel("Font Size ({})".format(30))
        self.reciprocalMapfontSizeLabel.setFixedWidth(160)
        self.reciprocalMapfontSizeSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.reciprocalMapfontSizeSlider.setMinimum(1)
        self.reciprocalMapfontSizeSlider.setMaximum(100)
        self.reciprocalMapfontSizeSlider.setValue(30)
        self.reciprocalMapfontSizeSlider.valueChanged.connect(self.update_reciprocal_map_font_size)
        self.reciprocalMapColormapLabel = QtWidgets.QLabel("Colormap")
        self.reciprocalMapColormapCombo = QtWidgets.QComboBox()
        for colormap in plt.colormaps():
            self.reciprocalMapColormapCombo.addItem(colormap)
        self.reciprocalMapColormapCombo.setCurrentText("jet")
        self.reciprocalMapColormapCombo.currentTextChanged.connect(self.update_plot_colormap)
        self.show_XY_plot_button = QtWidgets.QPushButton("Show XY Slices")
        self.show_XY_plot_button.clicked.connect(self.show_XY_plot)
        self.show_XY_plot_button.setEnabled(False)
        self.show_XZ_plot_button = QtWidgets.QPushButton("Show XZ Slices")
        self.show_XZ_plot_button.clicked.connect(self.show_XZ_plot)
        self.show_XZ_plot_button.setEnabled(False)
        self.show_YZ_plot_button = QtWidgets.QPushButton("Show YZ Slices")
        self.show_YZ_plot_button.clicked.connect(self.show_YZ_plot)
        self.show_YZ_plot_button.setEnabled(False)
        self.save_Results_button = QtWidgets.QPushButton("Save the 3D data")
        self.save_Results_button.clicked.connect(self.save_results)
        self.save_Results_button.setEnabled(False)
        self.plotOptionsGrid.addWidget(self.load_data_button,0,0,1,3)
        self.plotOptionsGrid.addWidget(self.KxyIndex,1,0,1,3)
        self.plotOptionsGrid.addWidget(self.KzIndex,2,0,1,3)
        self.plotOptionsGrid.addWidget(self.showFWHMCheckLabel,3,0,1,1)
        self.plotOptionsGrid.addWidget(self.showFWHMCheck,3,1,1,2)
        self.plotOptionsGrid.addWidget(self.plot_log_scale_label,4,0,1,1)
        self.plotOptionsGrid.addWidget(self.plot_log_scale,4,1,1,2)
        self.plotOptionsGrid.addWidget(self.reciprocalMapfontListLabel,5,0,1,1)
        self.plotOptionsGrid.addWidget(self.reciprocalMapfontList,5,1,1,2)
        self.plotOptionsGrid.addWidget(self.reciprocalMapfontSizeLabel,6,0,1,1)
        self.plotOptionsGrid.addWidget(self.reciprocalMapfontSizeSlider,6,1,1,2)
        self.plotOptionsGrid.addWidget(self.reciprocalMapColormapLabel,7,0,1,1)
        self.plotOptionsGrid.addWidget(self.reciprocalMapColormapCombo,7,1,1,2)
        self.plotOptionsGrid.addWidget(self.show_XY_plot_button,8,0,1,1)
        self.plotOptionsGrid.addWidget(self.show_XZ_plot_button,8,1,1,1)
        self.plotOptionsGrid.addWidget(self.show_YZ_plot_button,8,2,1,1)
        self.plotOptionsGrid.addWidget(self.save_Results_button,9,0,1,3)

        self.appearance = QtWidgets.QWidget()
        self.appearanceGrid = QtWidgets.QVBoxLayout(self.appearance)
        self.appearanceGrid.setContentsMargins(5,5,5,5)
        self.appearanceGrid.setAlignment(QtCore.Qt.AlignTop)

        self.showCoordinatesWidget = QtWidgets.QWidget()
        self.showCoordinatesGrid = QtWidgets.QGridLayout(self.showCoordinatesWidget)
        self.showCoordinatesLabel = QtWidgets.QLabel('Show Coordinate System?')
        self.showCoordinates = QtWidgets.QCheckBox()
        self.showCoordinates.setChecked(True)
        self.showCoordinates.stateChanged.connect(self.update_coordinates)
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
        self.fontList.currentFontChanged.connect(self.refresh_font_name)
        self.fontSizeLabel = QtWidgets.QLabel("Adjust Font Size ({})".format(5))
        self.fontSizeLabel.setFixedWidth(160)
        self.fontSizeSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.fontSizeSlider.setMinimum(1)
        self.fontSizeSlider.setMaximum(100)
        self.fontSizeSlider.setValue(5)
        self.fontSizeSlider.valueChanged.connect(self.refresh_font_size)
        self.FONTS_CHANGED.connect(self.graph.change_fonts)

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
        self.shadowQuality.currentIndexChanged.connect(self.graph.change_shadow_quality)

        self.statusBar = QtWidgets.QGroupBox("Log")
        self.statusBar.setStyleSheet('QGroupBox::title {color:blue;}')
        self.statusGrid = QtWidgets.QGridLayout(self.statusBar)
        self.statusBar.setFixedHeight(150)
        self.statusBar.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Fixed)
        self.logBox = QtWidgets.QTextEdit(QtCore.QTime.currentTime().toString("hh:mm:ss")+ \
                                          "\u00A0\u00A0\u00A0\u00A0Initialized!")
        self.logCursor = QtGui.QTextCursor(self.logBox.document())
        self.logCursor.movePosition(QtGui.QTextCursor.End)
        self.logBox.setTextCursor(self.logCursor)
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
        self.PROGRESS_ADVANCE.connect(self.progress)
        self.PROGRESS_HOLD.connect(self.progress_on)
        self.PROGRESS_END.connect(self.progress_reset)
        self.statusGrid.addWidget(self.logBoxScroll,0,0)
        self.vLayout_left.addWidget(self.statusBar)
        self.vLayout_left.addWidget(self.progressBar)

        themeLabel = QtWidgets.QLabel("Background Color")
        themeLabel.setStyleSheet("QLabel {color:blue;}")
        self.appearanceGrid.addWidget(self.showCoordinatesWidget)
        self.appearanceGrid.addWidget(themeLabel)
        self.appearanceGrid.addWidget(self.themeList)
        self.appearanceGrid.addWidget(self.fontListLabel)
        self.appearanceGrid.addWidget(self.fontList)
        self.appearanceGrid.addWidget(self.fontSizeLabel)
        self.appearanceGrid.addWidget(self.fontSizeSlider)
        self.appearanceGrid.addWidget(self.shadowQualityLabel)
        self.appearanceGrid.addWidget(self.shadowQuality)
        self.tab.addTab(self.appearance,"Appearance")
        self.tab.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Fixed)

        self.view = QtWidgets.QWidget()
        self.viewGrid = QtWidgets.QVBoxLayout(self.view)
        self.viewGrid.setContentsMargins(5,5,5,5)
        self.viewGrid.setAlignment(QtCore.Qt.AlignTop)
        viewLabel = QtWidgets.QLabel("Set View Direction")
        viewLabel.setStyleSheet("QLabel {color:blue;}")
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
        self.viewDirectionButtonGroup.buttonClicked.connect(self.view_direction_changed_emit)

        cameraPositionLabel = QtWidgets.QLabel("Set Camera Position")
        cameraPositionLabel.setStyleSheet("QLabel {color:blue;}")
        self.horizontalRotation = LabelLineEdit('Horizontal Rotation',150,'0.0',1,'\u00B0')
        self.verticalRotation = LabelLineEdit('Vertical Rotation',150,'0.0',1,'\u00B0')
        self.zoom = LabelLineEdit('Zoom Level',150,'100.0')
        self.horizontalRotation.VALUE_CHANGED.connect(self.set_camera_position)
        self.verticalRotation.VALUE_CHANGED.connect(self.set_camera_position)
        self.zoom.VALUE_CHANGED.connect(self.set_camera_position)

        self.viewGrid.addWidget(viewLabel)
        self.viewGrid.addWidget(self.viewDirection)
        self.viewGrid.addWidget(cameraPositionLabel)
        self.viewGrid.addWidget(self.horizontalRotation)
        self.viewGrid.addWidget(self.verticalRotation)
        self.viewGrid.addWidget(self.zoom)
        self.tab.addTab(self.view,"View")
        self.tab.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Fixed)

        self.colorTab = QtWidgets.QTabWidget()
        self.colorTab.setVisible(False)
        self.vLayout.addWidget(self.CIF_tab)
        self.vLayout.addWidget(self.chooseDestination)
        self.vLayout.addWidget(self.sample_tab)
        self.vLayout.addWidget(self.tab)
        self.vLayout.addWidget(self.colorTab)
        self.vLayout.addWidget(self.plotOptions)
        self.controlPanelScroll.setWidget(self.controlPanel)
        self.controlPanelScroll.setWidgetResizable(True)
        self.controlPanelScroll.setFrameShape(QtWidgets.QFrame.NoFrame)

        self.themeList.currentTextChanged.connect(self.graph.change_theme)
        self.themeList.setCurrentIndex(3)
        self.graph.LOG_MESSAGE.connect(self.update_log)
        self.graph.PROGRESS_ADVANCE.connect(self.progress)
        self.graph.PROGRESS_END.connect(self.progress_reset)
        self.graph.CALCULATION_FINISHED.connect(self.finish_calculation)
        self.graph.CALCULATION_ABORTED.connect(self.abort_calculation)
        self.graph.CAMERA_CHANGED.connect(self.change_camera_position_values)
        self.DELETE_SAMPLE.connect(self.graph.delete_data)
        self.VIEW_DIRECTION_CHANGED.connect(self.graph.update_view_direction)
        self.UPDATE_CAMERA_POSITION.connect(self.graph.update_camera_position)
        self.STOP_CALCULATION.connect(self.graph.stop)
        self.showMaximized()

    def set_camera_position(self,label,value):
        if label == 'Horizontal Rotation':
            self.UPDATE_CAMERA_POSITION.emit(value,self.verticalRotation.value(),self.zoom.value())
        elif label == 'Vertical Rotation':
            self.UPDATE_CAMERA_POSITION.emit(self.horizontalRotation.value(),value,self.zoom.value())
        elif label == 'Zoom Level':
            self.UPDATE_CAMERA_POSITION.emit(self.horizontalRotation.value(),self.verticalRotation.value(),value)

    def change_camera_position_values(self,h,v,zoom):
        self.horizontalRotation.set_value(h)
        self.verticalRotation.set_value(v)
        self.zoom.set_value(zoom)

    def delete_structure(self,index):
        self.update_log('Tab '+str(index+1)+ ' is being deleted ...')
        QtCore.QCoreApplication.processEvents()
        self.sample_tab.widget(index).destroy()
        self.sample_tab.removeTab(index)
        if len(self.sample_index_set) == 1:
            self.sample_tab.setVisible(False)
        self.colorTab.widget(index).destroy()
        self.colorTab.removeTab(index)
        self.deleted_tab_index.append(index)
        del self.real_space_specification_dict[self.sample_tab_index[index]]
        del self.colorSheet[self.sample_tab_index[index]]
        try:
            del self.molecule_dict[self.sample_tab_index[index]]
        except:
            pass
        del self.structure_dict[self.sample_tab_index[index]]
        try:
            del self.box[self.sample_tab_index[index]]
        except:
            del self.TAPD[self.sample_tab_index[index]]
        del self.element_species[self.sample_tab_index[index]]
        if self.sample_tab_index[index] in self.data_index_set:
            self.DELETE_SAMPLE.emit(self.sample_tab_index[index])
        if self.sample_tab_index[index] in self.sample_index_set:
            self.sample_index_set.remove(self.sample_tab_index[index])
        next_available_index = 0
        while (next_available_index in self.sample_index_set):
            next_available_index+=1
        self.structure_index=next_available_index
        del self.sample_tab_index[index]
        if len(self.sample_tab_index) == 0:
            self.colorTab.setVisible(False)
        self.update_log('Tab '+str(index+1)+ ' has been deleted!')

    def progress(self,min,max,val):
        self.progressBar.setVisible(True)
        self.progressBar.setMinimum(min)
        self.progressBar.setMaximum(max)
        self.progressBar.setValue(val)

    def progress_on(self):
        self.progressBar.setVisible(True)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(0)
        self.progressBar.setValue(0)

    def progress_reset(self):
        self.progressBar.reset()
        self.progressBar.setVisible(False)

    def choose_destination(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(None,"choose save destination",'./',QtWidgets.QFileDialog.ShowDirsOnly)
        self.currentDestination = path
        self.chooseDestinationLabel.setText("The save destination is:\n"+self.currentDestination)

    def view_direction_changed_emit(self,button):
        p = self.viewDirectionButtonGroup.id(button)
        self.VIEW_DIRECTION_CHANGED.emit(p)

    def update_number_of_steps_perp(self,value):
        self.KzIndex.set_head(0)
        self.KzIndex.set_tail(0)
        self.KzIndex.set_maximum(value-1)

    def update_number_of_steps_para(self,value):
        self.KxyIndex.set_head(0)
        self.KxyIndex.set_tail(0)
        self.KxyIndex.set_maximum(value-1)

    def update_coordinates(self,status):
        self.graph.update_coordinates(status)

    def update_colors(self,name,color,index):
        self.colorSheet[index][name] = color
        self.graph.update_colors(self.colorSheet,index)

    def update_size(self,name,size,index):
        self.graph.update_size(name,size,index)

    def update_log(self,msg):
        self.logBox.append(QtCore.QTime.currentTime().toString("hh:mm:ss")+"\u00A0\u00A0\u00A0\u00A0"+msg)

    def update_range(self,index):
        self.update_log("Constructing sample " + str(index+1))
        QtCore.QCoreApplication.processEvents()
        self.graph.clear_structure(index)
        self.box[index] = self.get_extended_structure(
            self.molecule_dict[index], \
            self.structure_dict[index].lattice.a, \
            self.structure_dict[index].lattice.b, \
            self.structure_dict[index].lattice.c, \
            self.structure_dict[index].lattice.alpha,\
            self.structure_dict[index].lattice.beta, \
            self.structure_dict[index].lattice.gamma, \
            images=(int(self.real_space_specification_dict[index]['h_range']),\
                    int(self.real_space_specification_dict[index]['k_range']),\
                    int(self.real_space_specification_dict[index]['k_range'])),\
            rotation=self.real_space_specification_dict[index]['rotation'],\
            offset=np.array([self.real_space_specification_dict[index]['x_shift'],self.real_space_specification_dict[index]['y_shift'],self.real_space_specification_dict[index]['z_shift']]))

        self.update_log("Finished construction of sample " + str(index+1))
        self.update_log("Applying changes in the real space range for sample " + str(index+1))
        QtCore.QCoreApplication.processEvents()

        self.graph.add_data(index,self.box[index].sites,self.colorSheet, \
                            self.real_space_specification_dict[index]['lateral_size']*10, \
                            self.real_space_specification_dict[index]['z_range'],\
                            self.real_space_specification_dict[index]['shape'],\
                           np.array([self.real_space_specification_dict[index]['x_shift'],self.real_space_specification_dict[index]['y_shift'],0]),\
                           self.real_space_specification_dict[index]['rotation'],self.AR, self.TAPD_add_atoms.isChecked())
        self.data_index_set.add(index)
        self.update_log("New real space range for sample" + str(index+1) +" applied!")

    def update_reciprocal_range(self):
        self.update_log("Calculating diffraction pattern ......")
        self.apply_reciprocal_range.setEnabled(False)
        self.stop_calculation.setEnabled(True)
        self.show_XY_plot_button.setEnabled(False)
        self.show_XZ_plot_button.setEnabled(False)
        self.show_YZ_plot_button.setEnabled(False)
        self.save_Results_button.setEnabled(False)
        QtCore.QCoreApplication.processEvents()
        self.KRange = [self.Kx_range.values(),self.Ky_range.values(),self.Kz_range.values()]
        self.x_linear = np.linspace(self.KRange[0][0],self.KRange[0][1],self.number_of_steps_para.value())
        self.y_linear = np.linspace(self.KRange[1][0],self.KRange[1][1],self.number_of_steps_para.value())
        self.z_linear = np.linspace(self.KRange[2][0],self.KRange[2][1],self.number_of_steps_perp.value())
        self.Kx,self.Ky,self.Kz = np.meshgrid(self.x_linear,self.y_linear,self.z_linear)
        self.graph.calculate(self.Kx,self.Ky,self.Kz,self.AFF)

    def finish_calculation(self,intensity):
        self.diffraction_intensity = intensity
        self.update_log("Finished Calculation!")
        self.show_XY_plot_button.setEnabled(True)
        self.show_XZ_plot_button.setEnabled(True)
        self.show_YZ_plot_button.setEnabled(True)
        self.save_Results_button.setEnabled(True)
        self.apply_reciprocal_range.setEnabled(True)
        self.stop_calculation.setEnabled(False)

    def abort_calculation(self):
        self.apply_reciprocal_range.setEnabled(True)
        self.stop_calculation.setEnabled(False)
        self.update_log("Aborted Calculation!")
        self.show_XY_plot_button.setEnabled(False)
        self.show_XZ_plot_button.setEnabled(False)
        self.show_YZ_plot_button.setEnabled(False)
        self.save_Results_button.setEnabled(False)
        self.progress_reset()

    def stop_diffraction_calculation(self):
        self.STOP_CALCULATION.emit()

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
        tab_index = index - len([x for x in self.deleted_tab_index if x < index])
        min = self.sample_tab.widget(tab_index).layout().itemAt(11).widget().currentMin + value - self.z_shift_history[index][-2]
        max = self.sample_tab.widget(tab_index).layout().itemAt(11).widget().currentMax + value - self.z_shift_history[index][-2]
        self.sample_tab.widget(tab_index).layout().itemAt(11).widget().set_head(min)
        self.sample_tab.widget(tab_index).layout().itemAt(11).widget().set_tail(max)

    def update_rotation(self,value,index):
        self.real_space_specification_dict[index]['rotation'] = value

    def update_z_range(self,min,max,index):
        self.real_space_specification_dict[index]['z_range'] = min,max


    def show_XY_plot(self):
        for i in range(int(self.KzIndex.values()[0]),int(self.KzIndex.values()[1]+1)):
            TwoDimPlot = DynamicalColorMap(self,'XY',self.x_linear,self.y_linear,self.z_linear,self.diffraction_intensity,i,\
                         self.reciprocalMapfontList.currentFont().family(),self.reciprocalMapfontSizeSlider.value(), \
                         self.reciprocalMapColormapCombo.currentText(),self.showFWHMCheck.isChecked(),self.plot_log_scale.isChecked())
            TwoDimPlot.show_plot()
            TwoDimPlot.UPDATE_LOG.connect(self.update_log)
            self.REFRESH_PLOT_FONTS.connect(TwoDimPlot.refresh_fonts)
            self.REFRESH_PLOT_FWHM.connect(TwoDimPlot.refresh_FWHM)
            self.REFRESH_PLOT_COLORMAP.connect(TwoDimPlot.refresh_colormap)
        self.update_log("Simulated diffraction patterns obtained!")

    def show_XZ_plot(self):
        for i in range(int(self.KxyIndex.values()[0]),int(self.KxyIndex.values()[1]+1)):
            TwoDimPlot = DynamicalColorMap(self,'XZ',self.x_linear,self.y_linear,self.z_linear,self.diffraction_intensity,i, \
                                                    self.reciprocalMapfontList.currentFont().family(),self.reciprocalMapfontSizeSlider.value(), \
                                                    self.reciprocalMapColormapCombo.currentText(),self.showFWHMCheck.isChecked(),self.plot_log_scale.isChecked())
            TwoDimPlot.show_plot()
            TwoDimPlot.UPDATE_LOG.connect(self.update_log)
            self.REFRESH_PLOT_FONTS.connect(TwoDimPlot.refresh_fonts)
            self.REFRESH_PLOT_FWHM.connect(TwoDimPlot.refresh_FWHM)
            self.REFRESH_PLOT_COLORMAP.connect(TwoDimPlot.refresh_colormap)
        self.update_log("Simulated diffraction patterns obtained!")

    def show_YZ_plot(self):
        for i in range(int(self.KxyIndex.values()[0]),int(self.KxyIndex.values()[1]+1)):
            TwoDimPlot = DynamicalColorMap(self,'YZ',self.x_linear,self.y_linear,self.z_linear,self.diffraction_intensity,i, \
                                                    self.reciprocalMapfontList.currentFont().family(),self.reciprocalMapfontSizeSlider.value(), \
                                                    self.reciprocalMapColormapCombo.currentText(),self.showFWHMCheck.isChecked(),self.plot_log_scale.isChecked())
            TwoDimPlot.UPDATE_LOG.connect(self.update_log)
            self.REFRESH_PLOT_FONTS.connect(TwoDimPlot.refresh_fonts)
            self.REFRESH_PLOT_FWHM.connect(TwoDimPlot.refresh_FWHM)
            self.REFRESH_PLOT_COLORMAP.connect(TwoDimPlot.refresh_colormap)
            TwoDimPlot.show_plot()
        self.update_log("Simulated diffraction patterns obtained!")

    def load_data(self):
        path = QtWidgets.QFileDialog.getOpenFileName(None,"Choose The 3D Data",'./',filter="TXT (*.txt);;All Files (*.*)")[0]
        if not path == "":
            self.update_log("Loading data ......")
            self.PROGRESS_HOLD.emit()
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
            self.update_number_of_steps_para(information['N_para'])
            self.update_number_of_steps_perp(information['N_perp'])
            intensity = np.loadtxt(path,skiprows=12, usecols=3)
            self.diffraction_intensity = intensity.reshape(information['N_para'],information['N_para'],information['N_perp'])
            self.update_log("Finished loading data!")
            self.PROGRESS_END.emit()
            self.show_XY_plot_button.setEnabled(True)
            self.show_XZ_plot_button.setEnabled(True)
            self.show_YZ_plot_button.setEnabled(True)


    def get_cif_path(self):
        path = QtWidgets.QFileDialog.getOpenFileName(None,"Choose The CIF File",'./',filter="CIF (*.cif);;All Files (*.*)")[0]
        if not path == "":
            self.update_log("CIF opened!")
            self.cifPath = path
            self.chooseCifLabel.setText("The path of the CIF file is:\n"+self.cifPath)
            next_available_index = 0
            while (next_available_index in self.sample_index_set):
                next_available_index+=1
            self.structure_index = next_available_index
            self.z_shift_history[self.structure_index] = [0]
            self.add_sample_structure(self.structure_index)
            self.add_sample_data(self.structure_index)
            self.chooseCifBrowser.tree_update(self.cifPath)

    def set_cif_path(self,path):
        self.update_log("CIF opened!")
        self.cifPath = path
        self.chooseCifLabel.setText("The path of the CIF file is:\n"+self.cifPath)
        next_available_index = 0
        while (next_available_index in self.sample_index_set):
            next_available_index+=1
        self.structure_index = next_available_index
        self.z_shift_history[self.structure_index] = [0]
        self.add_sample_structure(self.structure_index)
        self.add_sample_data(self.structure_index)

    def load_cif(self,text):
        path = QtWidgets.QFileDialog.getOpenFileName(None,text,'./',filter="CIF (*.cif);;All Files (*.*)")[0]
        if text == 'Choose Substrate':
            self.TAPD_substrate_label.setText("The path of the substrate CIF is :\n"+path)
            self.substrate_path = path
        elif text == 'Choose Epilayer':
            self.TAPD_epilayer_label.setText("The path of the epilayer CIF is :\n"+path)
            self.epilayer_path = path

    def add_sample_structure(self,index=0):
        range_structure = QtWidgets.QWidget()
        range_grid = QtWidgets.QGridLayout(range_structure)
        range_grid.setContentsMargins(5,5,5,5)
        range_grid.setAlignment(QtCore.Qt.AlignTop)
        lattice_constants_box = InfoBoard("Information",index)
        self.UPDATE_INOFRMATION_BOARD.connect(lattice_constants_box.update)
        h_range = LabelSlider(1,100,3,1,"h",index=index)
        h_range.VALUE_CHANGED.connect(self.update_h_range)
        k_range = LabelSlider(1,100,3,1,"k",index=index)
        k_range.VALUE_CHANGED.connect(self.update_k_range)
        l_range = LabelSlider(1,100,1,1,"l",index=index)
        l_range.VALUE_CHANGED.connect(self.update_l_range)
        shape_label = QtWidgets.QLabel("Shape")
        shape_label.setStyleSheet('QLabel {color:blue;}')
        shape = IndexedComboBox(index)
        shape.addItem("Triangle")
        shape.addItem("Square")
        shape.addItem("Hexagon")
        shape.addItem("Circle")
        shape.TEXT_CHANGED.connect(self.update_shape)
        lateral_size = LabelSlider(1,100,1,1,"Lateral Size",'nm',index=index)
        lateral_size.VALUE_CHANGED.connect(self.update_lateral_size)
        x_shift = LabelSlider(-1000,1000,0,100,"X Shift",'\u212B',index=index)
        x_shift.VALUE_CHANGED.connect(self.update_x_shift)
        y_shift = LabelSlider(-1000,1000,0,100,"Y Shift",'\u212B',index=index)
        y_shift.VALUE_CHANGED.connect(self.update_y_shift)
        z_shift = LabelSlider(-5000,5000,0,100,"Z Shift",'\u212B',index=index)
        z_shift.VALUE_CHANGED.connect(self.update_z_shift)
        rotation = LabelSlider(-1800,1800,0,10,"rotation",'\u00B0',index=index)
        rotation.VALUE_CHANGED.connect(self.update_rotation)
        z_range_slider = LockableDoubleSlider(-8000,8000,100,-10,10,"Z range","\u212B",False,index=index)
        z_range_slider.VALUE_CHANGED.connect(self.update_z_range)

        self.real_space_specification_dict[index] = {'h_range':h_range.get_value(),'k_range':k_range.get_value(),'l_range':l_range.get_value(),\
                                      'shape':shape.currentText(),'lateral_size':lateral_size.get_value(),\
                                      'x_shift':x_shift.get_value(),'y_shift':y_shift.get_value(),'z_shift':z_shift.get_value(),\
                                      'rotation':rotation.get_value(), 'z_range':z_range_slider.values()}

        apply_range = IndexedPushButton("Apply",index)
        apply_range.BUTTON_CLICKED.connect(self.update_range)
        apply_range.setEnabled(False)
        replace_structure = IndexedPushButton("Replace",index)
        replace_structure.BUTTON_CLICKED.connect(self.replace_structure)
        replace_structure.setEnabled(False)
        reset_structure = IndexedPushButton("Reset",index)
        reset_structure.BUTTON_CLICKED.connect(self.reset_structure)
        reset_structure.setEnabled(False)
        range_grid.addWidget(lattice_constants_box,0,0)
        range_grid.addWidget(h_range,1,0)
        range_grid.addWidget(k_range,2,0)
        range_grid.addWidget(l_range,3,0)
        range_grid.addWidget(shape_label,4,0)
        range_grid.addWidget(shape,5,0)
        range_grid.addWidget(lateral_size,6,0)
        range_grid.addWidget(x_shift,7,0)
        range_grid.addWidget(y_shift,8,0)
        range_grid.addWidget(z_shift,9,0)
        range_grid.addWidget(rotation,10,0)
        range_grid.addWidget(z_range_slider,11,0)
        range_grid.addWidget(apply_range,12,0)
        range_grid.addWidget(replace_structure,13,0)
        range_grid.addWidget(reset_structure,14,0)
        self.sample_tab.insertTab(index,range_structure,"Sample "+str(index+1))
        self.sample_tab.setCurrentIndex(index)
        self.sample_tab.setVisible(True)
        self.sample_index_set.add(index)
        self.sample_tab_index.append(index)
        self.sample_tab_index.sort()

    def add_sample_data(self,index):
        self.update_log("Adding sample" + str(index+1))
        QtCore.QCoreApplication.processEvents()
        h = int(self.real_space_specification_dict[index]['h_range'])
        k = int(self.real_space_specification_dict[index]['k_range'])
        l = int(self.real_space_specification_dict[index]['l_range'])
        self.structure_dict[index] = CifParser(self.cifPath).get_structures(primitive=False)[0]
        self.UPDATE_INOFRMATION_BOARD.emit(index,self.structure_dict[index].composition.reduced_formula,self.structure_dict[index].lattice.a,self.structure_dict[index].lattice.b,self.structure_dict[index].lattice.c,\
                           self.structure_dict[index].lattice.alpha,self.structure_dict[index].lattice.beta,self.structure_dict[index].lattice.gamma)
        self.molecule_dict[index] = pgStructure.Molecule.from_sites(self.structure_dict[index].sites)
        self.update_log("Sample "+str(index+1)+" loaded!")
        self.update_log("Constructing sample " + str(index+1))
        QtCore.QCoreApplication.processEvents()
        self.box[index] = self.get_extended_structure(self.molecule_dict[index], self.structure_dict[index].lattice.a, self.structure_dict[index].lattice.b, \
                                            self.structure_dict[index].lattice.c, self.structure_dict[index].lattice.alpha,self.structure_dict[index].lattice.beta,\
                                            self.structure_dict[index].lattice.gamma, images=(h,k,l), \
                                          rotation=self.real_space_specification_dict[index]['rotation'],\
        offset=np.array([self.real_space_specification_dict[index]['x_shift'],self.real_space_specification_dict[index]['y_shift'],self.real_space_specification_dict[index]['z_shift']]))
        self.update_log("Finished construction of sample " + str(index+1))
        QtCore.QCoreApplication.processEvents()
        self.element_species[index] = set(re.compile('[a-zA-Z]{1,2}').match(str(site.specie)).group() for site in self.box[index].sites)
        colorPalette = QtWidgets.QWidget()
        grid = QtWidgets.QVBoxLayout(colorPalette)
        self.colorSheet[index]={}
        for i,name in enumerate(self.element_species[index]):
            colorPicker = IndexedColorPicker(name,self.colors[i],self.AR.loc[name].at['Normalized Radius'],index)
            colorPicker.COLOR_CHANGED.connect(self.update_colors)
            colorPicker.SIZE_CHANGED.connect(self.update_size)
            self.colorSheet[index][name] = self.colors[i]
            grid.addWidget(colorPicker)
        self.colorTab.setVisible(True)
        self.colorTab.insertTab(index,colorPalette,"Atom Design "+str(index+1))
        self.colorTab.setCurrentIndex(index)
        self.update_log("Adding data for sample " + str(index+1))
        QtCore.QCoreApplication.processEvents()
        self.graph.add_data(index,self.box[index].sites,\
                            self.colorSheet, \
                            self.real_space_specification_dict[index]['lateral_size']*10, \
                            self.real_space_specification_dict[index]['z_range'],\
                            self.real_space_specification_dict[index]['shape'], \
                           np.array([self.real_space_specification_dict[index]['x_shift'],self.real_space_specification_dict[index]['y_shift'],0]),\
                           self.real_space_specification_dict[index]['rotation'],\
                            self.AR, self.TAPD_add_atoms.isChecked())
        self.data_index_set.add(index)
        self.graph.change_fonts(self.fontList.currentFont().family(),self.fontSizeSlider.value())
        self.graph.change_shadow_quality(self.shadowQuality.currentIndex())
        self.sample_tab.widget(index).layout().itemAt(12).widget().setEnabled(True)
        self.sample_tab.widget(index).layout().itemAt(13).widget().setEnabled(True)
        self.sample_tab.widget(index).layout().itemAt(14).widget().setEnabled(True)
        self.update_log("Finished adding data for sample " + str(index+1))
        QtCore.QCoreApplication.processEvents()
        self.apply_reciprocal_range.setEnabled(True)

    def replace_structure(self,index):
        self.update_log("Replacing sample" + str(index+1))
        QtCore.QCoreApplication.processEvents()
        path = QtWidgets.QFileDialog.getOpenFileName(None,"Choose The CIF File",'./',filter="CIF (*.cif);;All Files (*.*)")[0]
        if not path == "":
            self.update_log("CIF opened!")
            self.cifPath = path
            self.chooseCifLabel.setText("The path of the CIF file is:\n"+self.cifPath)
            h = int(self.real_space_specification_dict[index]['h_range'])
            k = int(self.real_space_specification_dict[index]['k_range'])
            l = int(self.real_space_specification_dict[index]['k_range'])
            self.graph.clear_structure(index)
            self.structure_dict[index] = CifParser(self.cifPath).get_structures(primitive=False)[0]
            self.UPDATE_INOFRMATION_BOARD.emit(index,self.structure_dict[index].composition.reduced_formula,self.structure_dict[index].lattice.a,self.structure_dict[index].lattice.b,self.structure_dict[index].lattice.c, \
                               self.structure_dict[index].lattice.alpha,self.structure_dict[index].lattice.beta,self.structure_dict[index].lattice.gamma)
            self.molecule_dict[index] = pgStructure.Molecule.from_sites(self.structure_dict[index].sites)
            self.update_log("Constructing sample " + str(index+1))
            QtCore.QCoreApplication.processEvents()
            self.box[index] = self.get_extended_structure(self.molecule_dict[index], self.structure_dict[index].lattice.a, self.structure_dict[index].lattice.b, \
                                                self.structure_dict[index].lattice.c, self.structure_dict[index].lattice.alpha,self.structure_dict[index].lattice.beta,\
                                                self.structure_dict[index].lattice.gamma, images=(h,k,l), \
                                              rotation=self.real_space_specification_dict[index]['rotation'],\
        offset=np.array([self.real_space_specification_dict[index]['x_shift'],self.real_space_specification_dict[index]['y_shift'],self.real_space_specification_dict[index]['z_shift']]))
            self.update_log("Finished construction for sample " + str(index+1))
            QtCore.QCoreApplication.processEvents()

            self.element_species[index] = set(re.compile('[a-zA-Z]{1,2}').match(str(site.specie)).group() for site in self.box[index].sites)
            colorPalette = QtWidgets.QWidget()
            grid = QtWidgets.QVBoxLayout(colorPalette)
            self.colorSheet[index] = {}
            for i,name in enumerate(self.element_species[index]):
                colorPicker = IndexedColorPicker(name,self.colors[i],self.AR.loc[name].at['Normalized Radius'],index)
                colorPicker.COLOR_CHANGED.connect(self.update_colors)
                colorPicker.SIZE_CHANGED.connect(self.update_size)
                self.colorSheet[index][name] = self.colors[i]
                grid.addWidget(colorPicker)
            self.colorTab.widget(index).destroy()
            self.colorTab.removeTab(index)
            self.colorTab.insertTab(index,colorPalette,"Atom Design "+str(index+1))
            self.graph.add_data(index,self.box[index].sites,\
                                self.colorSheet,\
                                self.real_space_specification_dict[index]['lateral_size']*10, \
                                self.real_space_specification_dict[index]['z_range'],\
                                self.real_space_specification_dict[index]['shape'], \
                               np.array([self.real_space_specification_dict[index]['x_shift'],self.real_space_specification_dict[index]['y_shift'],0]),\
                               self.real_space_specification_dict[index]['rotation'],\
                                self.AR, self.TAPD_add_atoms.isChecked())
            self.data_index_set.add(index)
            self.graph.change_fonts(self.fontList.currentFont().family(),self.fontSizeSlider.value())
            self.graph.change_shadow_quality(self.shadowQuality.currentIndex())
            self.update_log("Sample "+str(index+1)+" replaced!")

    def reset_structure(self,index):
        tab_index = index - len([x for x in self.deleted_tab_index if x < index])
        self.update_log("Resetting sample" + str(index+1))
        QtCore.QCoreApplication.processEvents()
        self.sample_tab.widget(tab_index).layout().itemAt(1).widget().reset()
        self.sample_tab.widget(tab_index).layout().itemAt(2).widget().reset()
        self.sample_tab.widget(tab_index).layout().itemAt(3).widget().reset()
        self.sample_tab.widget(tab_index).layout().itemAt(5).widget().setCurrentText("Triangle")
        self.sample_tab.widget(tab_index).layout().itemAt(6).widget().reset()
        self.sample_tab.widget(tab_index).layout().itemAt(7).widget().reset()
        self.sample_tab.widget(tab_index).layout().itemAt(8).widget().reset()
        self.sample_tab.widget(tab_index).layout().itemAt(9).widget().reset()
        self.sample_tab.widget(tab_index).layout().itemAt(10).widget().reset()
        self.sample_tab.widget(tab_index).layout().itemAt(11).widget().reset()
        h = int(self.real_space_specification_dict[index]['h_range'])
        k = int(self.real_space_specification_dict[index]['k_range'])
        l = int(self.real_space_specification_dict[index]['k_range'])
        self.graph.clear_structure(index)
        self.structure_dict[index] = CifParser(self.cifPath).get_structures(primitive=False)[0]
        self.UPDATE_INOFRMATION_BOARD.emit(index,self.structure_dict[index].composition.reduced_formula,self.structure_dict[index].lattice.a,self.structure_dict[index].lattice.b,self.structure_dict[index].lattice.c, \
                           self.structure_dict[index].lattice.alpha,self.structure_dict[index].lattice.beta,self.structure_dict[index].lattice.gamma)
        self.molecule_dict[index] = pgStructure.Molecule.from_sites(self.structure_dict[index].sites)
        self.update_log("Constructing sample " + str(index+1))
        QtCore.QCoreApplication.processEvents()
        self.box[index] = self.get_extended_structure(self.molecule_dict[index], self.structure_dict[index].lattice.a, self.structure_dict[index].lattice.b, \
                                            self.structure_dict[index].lattice.c, self.structure_dict[index].lattice.alpha,self.structure_dict[index].lattice.beta,\
                                            self.structure_dict[index].lattice.gamma, images=(h,k,l), \
                                          rotation=self.real_space_specification_dict[index]['rotation'],\
    offset=np.array([self.real_space_specification_dict[index]['x_shift'],self.real_space_specification_dict[index]['y_shift'],self.real_space_specification_dict[index]['z_shift']]))
        self.update_log("Finished construction for sample " + str(index+1))
        QtCore.QCoreApplication.processEvents()

        self.element_species[index] = set(re.compile('[a-zA-Z]{1,2}').match(str(site.specie)).group() for site in self.box[index].sites)
        colorPalette = QtWidgets.QWidget()
        grid = QtWidgets.QVBoxLayout(colorPalette)
        self.colorSheet[index] = {}
        for i,name in enumerate(self.element_species[index]):
            colorPicker = IndexedColorPicker(name,self.colors[i],self.AR.loc[name].at['Normalized Radius'],index)
            colorPicker.COLOR_CHANGED.connect(self.update_colors)
            colorPicker.SIZE_CHANGED.connect(self.update_size)
            self.colorSheet[index][name] = self.colors[i]
            grid.addWidget(colorPicker)
        self.colorTab.widget(tab_index).destroy()
        self.colorTab.removeTab(tab_index)
        self.colorTab.insertTab(tab_index,colorPalette,"Atom Design "+str(index+1))
        self.graph.add_data(index,self.box[index].sites,\
                            self.colorSheet,\
                            self.real_space_specification_dict[index]['lateral_size']*10, \
                            self.real_space_specification_dict[index]['z_range'],\
                            self.real_space_specification_dict[index]['shape'], \
                           np.array([self.real_space_specification_dict[index]['x_shift'],self.real_space_specification_dict[index]['y_shift'],0]),\
                           self.real_space_specification_dict[index]['rotation'],\
                           self.AR, self.TAPD_add_atoms.isChecked())
        self.data_index_set.add(index)
        self.graph.change_fonts(self.fontList.currentFont().family(),self.fontSizeSlider.value())
        self.graph.change_shadow_quality(self.shadowQuality.currentIndex())
        self.update_log("Sample "+str(index+1)+" successfully reset!")

    def save_results(self):
        if not self.currentDestination == '':
            self.PROGRESS_HOLD.emit()
            QtCore.QCoreApplication.processEvents()
            self.convertor_worker.mtx2vtp(self.currentDestination,self.destinationNameEdit.text(),self.diffraction_intensity,self.KRange,\
                         self.number_of_steps_para.value(),self.number_of_steps_perp.value(),\
                         self.real_space_specification_dict,self.element_species)
            self.PROGRESS_END.emit()
        else:
            self.raise_error("Save destination is empty!")

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
            op = SymmOp.from_origin_axis_angle((0, 0, 0), axis=[0,0,1], angle=rotation)
            m = op.rotation_matrix
            new_coords = np.dot(m, (centered_coords+box_center).T).T
            coords.extend(new_coords)
            self.PROGRESS_ADVANCE.emit(0,100,(i*(2*images[1]+1) * (2*images[2]+1)+j*(2*images[2]+1)+k)/nimages)
            QtCore.QCoreApplication.processEvents()
        self.PROGRESS_END.emit()
        sprops = {k: v * nimages for k, v in molecule.site_properties.items()}
        if cls is None:
            cls = pgStructure.Structure
        return cls(lattice, molecule.species * nimages, coords,coords_are_cartesian=True,site_properties=sprops).get_sorted_structure()

    def get_random_domain_size(self, **kwargs):
        if kwargs['type'] == 'geometrical':
            return np.random.geometric(kwargs['gamma'])

    def get_random_antiphase_boundary(self, number_of_boundaries, **kwargs):
        if kwargs['type'] == 'uniform':
            return np.random.random_integers(0,number_of_boundaries)

    def generate_1D_lattice(self,a, length, number_of_boundaries, size_distribution='geometrical',boundary_distribution='uniform',**kwargs):
        position = 0
        lattice = [0]
        while position <= length:
            if size_distribution == 'geometrical':
                domain_size = self.get_random_domain_size(type=size_distribution,gamma=kwargs['gamma'])
            if boundary_distribution == 'uniform':
                boundary = self.get_random_antiphase_boundary(number_of_boundaries,type=boundary_distribution)
            for j in range(domain_size):
                lattice.append(lattice[-1]+a)
            lattice.append(lattice[-1]+boundary/number_of_boundaries*a)
            position+=(domain_size+1)
        return lattice[0:length]

    def test_random_1D(self):
        figure,ax = plt.subplots()
        ax.set_aspect('equal')
        for i in range(100):
            x = self.generate_1D_lattice(2,100,5,gamma=0.2)
            y = np.full(len(x),i)
            ax.scatter(x,y,1)
        plt.show()

    def prepare_TAPD(self):
        parameters = {}
        if self.TAPD_distribution_function.currentText() == 'completely random':
            parameters['density'] = float(self.TAPD_completely_random.text())
        elif self.TAPD_distribution_function.currentText() == 'geometric':
            parameters['gamma'] = float(self.TAPD_geometric_gamma.text())
        elif self.TAPD_distribution_function.currentText() == 'delta':
            parameters['radius'] = float(self.TAPD_delta_radius.text())
        elif self.TAPD_distribution_function.currentText() == 'uniform':
            parameters['low'] = float(self.TAPD_uniform_low.text())
            parameters['high'] = float(self.TAPD_uniform_high.text())
        elif self.TAPD_distribution_function.currentText() == 'binomial':
            parameters['n'] = float(self.TAPD_binomial_n.text())
            parameters['p'] = float(self.TAPD_binomial_p.text())

        self.TAPD_worker = TAPD_Simulation(int(self.TAPD_X_max.text()),\
                                          int(self.TAPD_Y_max.text()), \
                                          float(self.TAPD_Z_min.text()), \
                                          float(self.TAPD_Z_max.text()),\
                                          [float(self.TAPD_Shift_X.text()), float(self.TAPD_Shift_Y.text()), float(self.TAPD_Shift_Z.text())],\
                                          self.substrate_path, self.epilayer_path, \
                                           self.TAPD_distribution_function.currentText(),\
                                           self.TAPD_plot_Voronoi.isChecked(),\
                                          self.TAPD_substrate_orientation.currentText(),\
                                          self.TAPD_epilayer_orientation.currentText(),\
                                           self.TAPD_atoms.isChecked(), **parameters)
        self.thread = QtCore.QThread()
        self.TAPD_worker.moveToThread(self.thread)
        self.TAPD_worker.PROGRESS_ADVANCE.connect(self.progress)
        self.TAPD_worker.PROGRESS_END.connect(self.progress_reset)
        self.TAPD_worker.FINISHED.connect(self.thread.quit)
        self.TAPD_worker.UPDATE_LOG.connect(self.update_log)
        self.TAPD_worker.SEND_RESULTS.connect(self.get_TAPD_results)
        self.TAPD_worker.VORONOI_PLOT.connect(self.plot_voronoi)
        self.thread.started.connect(self.TAPD_worker.run)
        self.STOP_TAPD_WORKER.connect(self.TAPD_worker.stop)

    def get_TAPD_results(self, structure_sub, structure_epi, substrate_sites, epilayer_sites):
        self.structure_sub = structure_sub
        self.structure_epi = structure_epi
        self.substrate_sites = substrate_sites
        self.epilayer_sites = epilayer_sites
        if self.TAPD_add_substrate.isChecked():
            self.add_TAPD('substrate')
        if self.TAPD_add_epilayer.isChecked():
            self.add_TAPD('epilayer')

    def add_TAPD(self,label='substrate'):
        next_available_index = 0
        while (next_available_index in self.sample_index_set):
            next_available_index+=1
        self.structure_index = next_available_index
        self.z_shift_history[self.structure_index] = [0]
        self.add_TAPD_structure(label,self.structure_index)
        self.add_TAPD_data(self.structure_index,label)

    def add_TAPD_structure(self,label,index=0):
        range_structure = QtWidgets.QWidget()
        range_grid = QtWidgets.QGridLayout(range_structure)
        range_grid.setContentsMargins(5,5,5,5)
        range_grid.setAlignment(QtCore.Qt.AlignTop)
        lattice_constants_box = InfoBoard("Information",index)
        self.UPDATE_INOFRMATION_BOARD.connect(lattice_constants_box.update)
        shape_label = QtWidgets.QLabel("Shape")
        shape_label.setStyleSheet('QLabel {color:blue;}')
        shape = IndexedComboBox(index)
        shape.addItem("Triangle")
        shape.addItem("Square")
        shape.addItem("Hexagon")
        shape.addItem("Circle")
        shape.setCurrentText("Circle")
        shape.TEXT_CHANGED.connect(self.update_shape)
        lateral_size = LabelSlider(1,100,float(self.TAPD_X_max.text())/5,1,"Lateral Size",'nm',index=index)
        lateral_size.VALUE_CHANGED.connect(self.update_lateral_size)

        self.real_space_specification_dict[index] = {\
                                      'shape':shape.currentText(),'lateral_size':lateral_size.get_value(),\
                                      'x_shift':0,'y_shift':0,'z_shift':0,\
                                      'rotation':0, 'z_range':(-100,100)}

        apply_range = IndexedPushButton("Apply",index)
        apply_range.BUTTON_CLICKED.connect(self.update_TAPD_range)
        apply_range.setEnabled(False)
        reset_structure = IndexedPushButton("Reset",index)
        reset_structure.BUTTON_CLICKED.connect(self.reset_TAPD_structure)
        reset_structure.setEnabled(False)
        range_grid.addWidget(lattice_constants_box,0,0)
        range_grid.addWidget(shape_label,1,0)
        range_grid.addWidget(shape,2,0)
        range_grid.addWidget(lateral_size,3,0)
        range_grid.addWidget(apply_range,4,0)
        range_grid.addWidget(reset_structure,5,0)
        self.sample_tab.insertTab(index,range_structure,label+" "+str(index+1))
        self.sample_tab.setCurrentIndex(index)
        self.sample_tab.setVisible(True)
        self.sample_index_set.add(index)
        self.sample_tab_index.append(index)
        self.sample_tab_index.sort()

    def update_TAPD_range(self,index):
        self.update_log("Constructing TAPD " + str(index+1))
        QtCore.QCoreApplication.processEvents()
        self.graph.clear_structure(index)
        self.graph.add_data(index,self.TAPD[index],self.colorSheet, \
                            self.real_space_specification_dict[index]['lateral_size']*10, \
                            self.real_space_specification_dict[index]['z_range'],\
                            self.real_space_specification_dict[index]['shape'],\
                           np.array([self.real_space_specification_dict[index]['x_shift'],self.real_space_specification_dict[index]['y_shift'],0]),\
                           self.real_space_specification_dict[index]['rotation'],self.AR, self.TAPD_add_atoms.isChecked())
        self.data_index_set.add(index)
        self.update_log("New real space range for TAPD" + str(index+1) +" applied!")

    def reset_TAPD_structure(self,index):
        self.update_log("Resetting TAPD" + str(index+1))
        QtCore.QCoreApplication.processEvents()
        tab_index = index - len([x for x in self.deleted_tab_index if x < index])
        self.sample_tab.widget(tab_index).layout().itemAt(2).widget().setCurrentText('Squrare')
        self.sample_tab.widget(tab_index).layout().itemAt(3).widget().reset()
        self.graph.clear_structure(index)
        colorPalette = QtWidgets.QWidget()
        grid = QtWidgets.QVBoxLayout(colorPalette)
        self.colorSheet[index] = {}
        for i,name in enumerate(self.element_species[index]):
            colorPicker = IndexedColorPicker(name,self.colors[i],self.AR.loc[name].at['Normalized Radius'],index)
            colorPicker.COLOR_CHANGED.connect(self.update_colors)
            colorPicker.SIZE_CHANGED.connect(self.update_size)
            self.colorSheet[index][name] = self.colors[i]
            grid.addWidget(colorPicker)
        self.colorTab.widget(tab_index).destroy()
        self.colorTab.removeTab(tab_index)
        self.colorTab.insertTab(tab_index,colorPalette,"Atom Design "+str(index+1))
        self.graph.add_data(index,self.TAPD[index],\
                            self.colorSheet,\
                            self.real_space_specification_dict[index]['lateral_size']*10, \
                            self.real_space_specification_dict[index]['z_range'],\
                            self.real_space_specification_dict[index]['shape'], \
                           np.array([self.real_space_specification_dict[index]['x_shift'],self.real_space_specification_dict[index]['y_shift'],0]),\
                           self.real_space_specification_dict[index]['rotation'],\
                            self.AR, self.TAPD_add_atoms.isChecked())
        self.data_index_set.add(index)
        self.graph.change_fonts(self.fontList.currentFont().family(),self.fontSizeSlider.value())
        self.graph.change_shadow_quality(self.shadowQuality.currentIndex())
        self.update_log("TAPD "+str(index+1)+" successfully reset!")

    def add_TAPD_data(self,index, label):
        self.update_log("Adding TAPD "+ label + str(index+1))
        QtCore.QCoreApplication.processEvents()
        if label=='substrate':
            self.structure_dict[index] = self.structure_sub
            self.TAPD[index] = self.substrate_sites
        elif label=='epilayer':
            self.structure_dict[index] = self.structure_epi
            self.TAPD[index] = self.epilayer_sites
        self.UPDATE_INOFRMATION_BOARD.emit(index,self.structure_dict[index].composition.reduced_formula,self.structure_dict[index].lattice.a,self.structure_dict[index].lattice.b,self.structure_dict[index].lattice.c,\
                           self.structure_dict[index].lattice.alpha,self.structure_dict[index].lattice.beta,self.structure_dict[index].lattice.gamma)
        self.update_log("TAPD "+label+str(index+1)+" loaded!")
        if label=='substrate':
            self.element_species[index] = set(re.compile('[a-zA-Z]{1,2}').match(str(site.specie)).group() for site in self.substrate_sites)
        elif label=='epilayer':
            self.element_species[index] = set(re.compile('[a-zA-Z]{1,2}').match(str(site.specie)).group() for site in self.epilayer_sites)

        colorPalette = QtWidgets.QWidget()
        grid = QtWidgets.QVBoxLayout(colorPalette)
        self.colorSheet[index]={}
        for i,name in enumerate(self.element_species[index]):
            colorPicker = IndexedColorPicker(name,self.colors[i],self.AR.loc[name].at['Normalized Radius'],index)
            colorPicker.COLOR_CHANGED.connect(self.update_colors)
            colorPicker.SIZE_CHANGED.connect(self.update_size)
            self.colorSheet[index][name] = self.colors[i]
            grid.addWidget(colorPicker)
        self.colorTab.setVisible(True)
        self.colorTab.insertTab(index,colorPalette,"Atom Design "+str(index+1))
        self.colorTab.setCurrentIndex(index)

        self.update_log("Adding data for TAPD "+label + str(index+1))
        QtCore.QCoreApplication.processEvents()
        self.graph.add_data(index,self.TAPD[index],\
                            self.colorSheet, \
                            self.real_space_specification_dict[index]['lateral_size']*10, \
                            self.real_space_specification_dict[index]['z_range'],\
                            self.real_space_specification_dict[index]['shape'], \
                           np.array([self.real_space_specification_dict[index]['x_shift'],self.real_space_specification_dict[index]['y_shift'],0]),\
                           self.real_space_specification_dict[index]['rotation'],\
                            self.AR, self.TAPD_add_atoms.isChecked())
        self.data_index_set.add(index)
        self.graph.change_fonts(self.fontList.currentFont().family(),self.fontSizeSlider.value())
        self.graph.change_shadow_quality(self.shadowQuality.currentIndex())
        self.sample_tab.widget(index).layout().itemAt(4).widget().setEnabled(True)
        self.sample_tab.widget(index).layout().itemAt(5).widget().setEnabled(True)
        self.update_log("Finished adding data for sample " + str(index+1))
        QtCore.QCoreApplication.processEvents()
        self.apply_reciprocal_range.setEnabled(True)

    def load_TAPD(self):
        if self.substrate_path:
            if self.epilayer_path:
                self.prepare_TAPD()
                self.thread.start()
            else:
                self.raise_error('Please specify the epilayer!')
        else:
            self.raise_error('Please specify the substrate!')

    def stop_TAPD(self):
        self.STOP_TAPD_WORKER.emit()
        if self.thread.isRunning():
            self.thread.terminate()
            self.thread.wait()

    def reset_TAPD(self):
        self.substrate_path = None
        self.epilayer_path = None
        self.TAPD_substrate_label.setText("The path of the substrate CIF is:\n")
        self.TAPD_epilayer_label.setText("The path of the substrate CIF is:\n")
        self.TAPD_substrate_orientation.setCurrentText('(001)')
        self.TAPD_epilayer_orientation.setCurrentText('(001)')
        self.TAPD_plot_Voronoi.setChecked(False)
        self.TAPD_X_max.setText('50')
        self.TAPD_Y_max.setText('50')
        self.TAPD_Z_min.setText('0')
        self.TAPD_Z_max.setText('1')
        self.TAPD_Shift_X.setText('0')
        self.TAPD_Shift_Y.setText('0')
        self.TAPD_Shift_Z.setText('3')
        self.TAPD_distribution_function.setCurrentText('geometric')

    def change_distribution_function(self,text):
        while self.distribution_parameters_grid.itemAt(0):
            self.distribution_parameters_grid.itemAt(0).widget().deleteLater()
            self.distribution_parameters_grid.removeItem(self.distribution_parameters_grid.itemAt(0))
        if text == 'completely random':
            self.TAPD_completely_random_label = QtWidgets.QLabel('Density')
            self.TAPD_completely_random = QtWidgets.QLineEdit('0.1')
            self.distribution_parameters_grid.addWidget(self.TAPD_completely_random_label)
            self.distribution_parameters_grid.addWidget(self.TAPD_completely_random)
        elif text == 'geometric':
            self.TAPD_geometric_gamma_label = QtWidgets.QLabel('Gamma')
            self.TAPD_geometric_gamma = QtWidgets.QLineEdit('0.1')
            self.distribution_parameters_grid.addWidget(self.TAPD_geometric_gamma_label)
            self.distribution_parameters_grid.addWidget(self.TAPD_geometric_gamma)
        elif text == 'binomial':
            self.TAPD_binomial_n_label = QtWidgets.QLabel('n')
            self.TAPD_binomial_n = QtWidgets.QLineEdit('20')
            self.TAPD_binomial_p_label = QtWidgets.QLabel('p')
            self.TAPD_binomial_p = QtWidgets.QLineEdit('0.5')
            self.distribution_parameters_grid.addWidget(self.TAPD_binomial_n_label)
            self.distribution_parameters_grid.addWidget(self.TAPD_binomial_n)
            self.distribution_parameters_grid.addWidget(self.TAPD_binomial_p_label)
            self.distribution_parameters_grid.addWidget(self.TAPD_binomial_p)
        elif text == 'uniform':
            self.TAPD_uniform_low_label = QtWidgets.QLabel('low')
            self.TAPD_uniform_low = QtWidgets.QLineEdit('5')
            self.TAPD_uniform_high_label = QtWidgets.QLabel('high')
            self.TAPD_uniform_high = QtWidgets.QLineEdit('15')
            self.distribution_parameters_grid.addWidget(self.TAPD_uniform_low_label)
            self.distribution_parameters_grid.addWidget(self.TAPD_uniform_low)
            self.distribution_parameters_grid.addWidget(self.TAPD_uniform_high_label)
            self.distribution_parameters_grid.addWidget(self.TAPD_uniform_high)
        elif text == 'delta':
            self.TAPD_delta_radius_label = QtWidgets.QLabel('radius')
            self.TAPD_delta_radius = QtWidgets.QLineEdit('10')
            self.distribution_parameters_grid.addWidget(self.TAPD_delta_radius_label)
            self.distribution_parameters_grid.addWidget(self.TAPD_delta_radius)

    def plot_voronoi(self, vor, substrate, epilayer, kw):
        window = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(window)
        figure = plt.figure()
        figure.clear()
        ax = figure.add_subplot(111)
        ax.set_aspect('equal')
        ax.scatter(np.array(substrate)[:,0],np.array(substrate)[:,1],5,'black')
        ax.scatter(np.array(epilayer)[:,0],np.array(epilayer)[:,1],5,'red')
        ax.set_xlabel('x (\u212B)' ,fontsize=20)
        ax.set_ylabel('y (\u212B)',fontsize=20)
        ax.set_title('2D translational antiphase boundary model\nMoS2/sapphire',fontsize=20)
        ax.tick_params(labelsize=20)
        point_color = kw.get('point_color', 'green')
        point_size = kw.get('point_size', 1.0)
        vertex_color = kw.get('vertex_color', 'green')
        vertex_size  = kw.get('vertex_size', 1.0)

        if kw.get('show_points', True):
            ax.plot(vor.points[:,0], vor.points[:,1], '.', markersize=point_size, markerfacecolor=point_color)
        if kw.get('show_vertices', True):
            ax.plot(vor.vertices[:,0], vor.vertices[:,1], 'o', markersize=vertex_size, markerfacecolor=vertex_color)

        line_colors = kw.get('line_colors', 'k')
        line_width = kw.get('line_width', 1.0)
        line_alpha = kw.get('line_alpha', 1.0)

        line_segments = []
        for simplex in vor.ridge_vertices:
            simplex = np.asarray(simplex)
            if np.all(simplex >= 0):
                line_segments.append([(x, y) for x, y in vor.vertices[simplex]])

        lc = LineCollection(line_segments,colors=line_colors,lw=line_width,linestyle='solid')
        lc.set_alpha(line_alpha)
        ax.add_collection(lc)
        ptp_bound = vor.points.ptp(axis=0)

        line_segments = []
        center = vor.points.mean(axis=0)
        for pointidx, simplex in zip(vor.ridge_points, vor.ridge_vertices):
            simplex = np.asarray(simplex)
            if np.any(simplex < 0):
                i = simplex[simplex >= 0][0]
                t = vor.points[pointidx[1]] - vor.points[pointidx[0]]
                t /= np.linalg.norm(t)
                n = np.array([-t[1], t[0]])
                midpoint = vor.points[pointidx].mean(axis=0)
                direction = np.sign(np.dot(midpoint - center, n)) * n
                far_point = vor.vertices[i] + direction * ptp_bound.max()

                line_segments.append([(vor.vertices[i, 0], vor.vertices[i, 1]),
                                      (far_point[0], far_point[1])])

        lc = LineCollection(line_segments,colors=line_colors,lw=line_width,linestyle='dashed')
        lc.set_alpha(line_alpha)
        ax.add_collection(lc)
        ptp_bound = vor.points.ptp(axis=0)
        ax.set_xlim(vor.points[:,0].min() - 0.1*ptp_bound[0],
                    vor.points[:,0].max() + 0.1*ptp_bound[0])
        ax.set_ylim(vor.points[:,1].min() - 0.1*ptp_bound[1],
                    vor.points[:,1].max() + 0.1*ptp_bound[1])
        canvas = FigureCanvas(figure)
        toolbar = NavigationToolbar(canvas,window)
        canvas.draw()
        layout.addWidget(toolbar)
        layout.addWidget(canvas)
        window.setWindowTitle("2D Contour")
        window.show()

    def refresh_font_size(self):
        self.fontSizeLabel.setText("Adjust Font Size ({})".format(self.fontSizeSlider.value()))
        self.FONTS_CHANGED.emit(self.fontList.currentFont().family(),self.fontSizeSlider.value())

    def refresh_font_name(self):
        self.FONTS_CHANGED.emit(self.fontList.currentFont().family(),self.fontSizeSlider.value())

    def update_FWHM_check(self,state):
        check = False
        if state == 2:
            check = True
        self.REFRESH_PLOT_FWHM.emit(check)

    def update_plot_font(self,font):
        self.REFRESH_PLOT_FONTS.emit(font.family(),self.reciprocalMapfontSizeSlider.value())

    def update_plot_colormap(self,colormap):
        self.REFRESH_PLOT_COLORMAP.emit(colormap)

    def update_reciprocal_map_font_size(self,value):
        self.reciprocalMapfontSizeLabel.setText("Font Size ({})".format(value))
        self.REFRESH_PLOT_FONTS.emit(self.reciprocalMapfontList.currentFont().family(),value)

    def raise_error(self,message):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.setEscapeButton(QtWidgets.QMessageBox.Close)
        msg.exec()

    def raise_attention(self,information):
        info = QtWidgets.QMessageBox()
        info.setIcon(QtWidgets.QMessageBox.Information)
        info.setText(information)
        info.setWindowTitle("Information")
        info.setStandardButtons(QtWidgets.QMessageBox.Ok)
        info.setEscapeButton(QtWidgets.QMessageBox.Close)
        info.exec()

class ScatterGraph(QtDataVisualization.Q3DScatter):

    LOG_MESSAGE = QtCore.pyqtSignal(str)
    PROGRESS_ADVANCE = QtCore.pyqtSignal(int,int,int)
    PROGRESS_END = QtCore.pyqtSignal()
    STOP_WORKER = QtCore.pyqtSignal()
    CALCULATION_FINISHED = QtCore.pyqtSignal(np.ndarray)
    CALCULATION_ABORTED = QtCore.pyqtSignal()
    CAMERA_CHANGED = QtCore.pyqtSignal(float,float,float)

    def __init__(self):
        super(ScatterGraph,self).__init__()
        self.series_dict = {}
        self.atoms_dict = {}
        self.elements_dict = {}
        self.ion_dict = {}
        self.colors_dict = {}
        self.coordinateStatus = 2
        self.range = 10
        self.x_max = {}
        self.x_min = {}
        self.y_max = {}
        self.y_min = {}
        self.z_max = {}
        self.z_min = {}
        self.scene().activeCamera().xRotationChanged.connect(self.camera_position_changed)
        self.scene().activeCamera().yRotationChanged.connect(self.camera_position_changed)
        self.scene().activeCamera().zoomLevelChanged.connect(self.camera_position_changed)

    def add_data(self,index,data,colorSheet,range,z_range,shape,offset,rotation,AR,add_series=True):
        self.colors_dict = colorSheet
        element_species = list(re.compile('[a-zA-Z]{1,2}').match(str(site.specie)).group() for site in data)
        self.elements_dict[index] = element_species
        self.coords = (site.coords for site in data)
        self.atoms_dict[index] = {}
        if range > self.range:
            self.range = range
        z_max = -1000
        z_min = 1000
        x_max = -1000
        x_min = 1000
        y_max = -1000
        y_min = 1000
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
                condition = (np.sqrt(coord[0]*coord[0]+coord[1]*coord[1]) < range/2)
            if condition and (coord[2]<z_range[1] and coord[2]>z_range[0]):
                self.atoms_dict[index][','.join(str(x) for x in coord)] = self.elements_dict[index][i]
                dataArray = []
                ScatterProxy = QtDataVisualization.QScatterDataProxy()
                ScatterSeries = QtDataVisualization.QScatter3DSeries(ScatterProxy)
                item = QtDataVisualization.QScatterDataItem()
                if coord[2] > z_max:
                    z_max = coord[2]
                if coord[2] < z_min:
                    z_min = coord[2]
                if coord[1] > y_max:
                    y_max = coord[1]
                if coord[1] < y_min:
                    y_min = coord[1]
                if coord[0] > x_max:
                    x_max = coord[0]
                if coord[0] < x_min:
                    x_min = coord[0]
                vector = QtGui.QVector3D(coord[0],coord[2],coord[1])
                item.setPosition(vector)
                dataArray.append(item)
                ScatterProxy.resetArray(dataArray)
                radii = AR.loc[self.elements_dict[index][i]].at['Normalized Radius']
                ScatterSeries.setMeshSmooth(True)
                ScatterSeries.setColorStyle(QtDataVisualization.Q3DTheme.ColorStyleUniform)
                ScatterSeries.setBaseColor(QtGui.QColor(self.colors_dict[index][self.elements_dict[index][i]]))
                ScatterSeries.setItemSize(radii/5/self.range)
                ScatterSeries.setSingleHighlightColor(QtGui.QColor('white'))
                ScatterSeries.setItemLabelFormat(self.elements_dict[index][i]+' (@xLabel, @zLabel, @yLabel)')
                atomSeries[i] = ScatterSeries
                self.PROGRESS_ADVANCE.emit(0,100,i/number_of_coords*100)
        self.series_dict[index] = atomSeries
        self.PROGRESS_END.emit()
        self.LOG_MESSAGE.emit('Atom series generated!')
        self.x_max[index] = x_max
        self.x_min[index] = x_min
        self.y_max[index] = y_max
        self.y_min[index] = y_min
        self.z_max[index] = z_max
        self.z_min[index] = z_min
        self.setAspectRatio((max(self.x_max.values())-min(self.x_min.values()))/(max(self.z_max.values())-min(self.z_min.values())))
        self.setHorizontalAspectRatio((max(self.x_max.values())-min(self.x_min.values()))/(max(self.y_max.values())-min(self.y_min.values())))
        if add_series:
            self.LOG_MESSAGE.emit('Adding series ...')
            for i,series in atomSeries.items():
                self.addSeries(series)
                self.PROGRESS_ADVANCE.emit(0,100,i/len(atomSeries)*100)
            self.PROGRESS_END.emit()
            self.LOG_MESSAGE.emit('All series are added!')

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

    def prepare(self,Kx,Ky,Kz,AFF):
        atoms_list = self.flatten(self.atoms_dict)
        self.diffraction_worker = DiffractionPattern(Kx,Ky,Kz,AFF,atoms_list)
        self.diffraction_worker.ERROR.connect(self.raise_error)
        self.diffraction_worker.PROGRESS_ADVANCE.connect(self.PROGRESS_ADVANCE)
        self.diffraction_worker.PROGRESS_END.connect(self.PROGRESS_END)
        self.diffraction_worker.ACCOMPLISHED.connect(self.CALCULATION_FINISHED)
        self.diffraction_worker.ABORTED.connect(self.process_aborted)

        self.thread = QtCore.QThread()
        self.diffraction_worker.moveToThread(self.thread)
        self.diffraction_worker.PROGRESS_END.connect(self.thread.quit)
        self.thread.started.connect(self.diffraction_worker.run)
        self.STOP_WORKER.connect(self.diffraction_worker.stop)

    def calculate(self,Kx,Ky,Kz,AFF):
        self.prepare(Kx,Ky,Kz,AFF)
        self.thread.start()

    def stop(self):
        self.STOP_WORKER.emit()
        if self.thread.isRunning():
            self.thread.terminate()
            self.thread.wait()

    def process_aborted(self):
        self.LOG_MESSAGE.emit("Process aborted!")
        self.CALCULATION_ABORTED.emit()

    def clear(self):
        for series in self.seriesList():
            self.removeSeries(series)

    def clear_structure(self,index):
        for series in list(self.series_dict[index].values()):
            self.removeSeries(series)

    def delete_data(self,index):
        self.clear_structure(index)
        del self.series_dict[index]
        del self.atoms_dict[index]
        del self.elements_dict[index]
        del self.x_max[index]
        del self.x_min[index]
        del self.y_max[index]
        del self.y_min[index]
        del self.z_max[index]
        del self.z_min[index]
        try:
            self.setAspectRatio((max(self.x_max.values())-min(self.x_min.values()))/(max(self.z_max.values())-min(self.z_min.values())))
            self.setHorizontalAspectRatio((max(self.x_max.values())-min(self.x_min.values()))/(max(self.y_max.values())-min(self.y_min.values())))
        except:
            self.setAspectRatio(1)
            self.setHorizontalAspectRatio(1)

    def update_coordinates(self,status):
        self.coordinateStatus = status
        if status == 2:
            self.axisX().setTitleVisible(True)
            self.axisY().setTitleVisible(True)
            self.axisZ().setTitleVisible(True)
            self.activeTheme().setBackgroundEnabled(True)
            self.activeTheme().setGridEnabled(True)
            if self.activeTheme().backgroundColor() == QtGui.QColor("black"):
                self.activeTheme().setLabelTextColor(QtGui.QColor("white"))
            elif self.activeTheme().backgroundColor() == QtGui.QColor("gray"):
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

    def update_view_direction(self,preset):
        self.scene().activeCamera().setCameraPreset(preset)

    def update_camera_position(self,h,v,zoom):
        self.scene().activeCamera().setCameraPosition(h,v,zoom)

    def camera_position_changed(self,value):
        self.CAMERA_CHANGED.emit(self.scene().activeCamera().xRotation(),self.scene().activeCamera().yRotation(),self.scene().activeCamera().zoomLevel())

    def update_colors(self,colorSheet,index):
        self.colors_dict = colorSheet
        for i,series in self.series_dict[index].items():
            series.setBaseColor(QtGui.QColor(colorSheet[index][self.elements_dict[index][i]]))

    def update_all_colors(self):
        for i,colorSheet in self.colors_dict.items():
            for j,series in self.series_dict[i].items():
                series.setBaseColor(QtGui.QColor(colorSheet[self.elements_dict[i][j]]))

    def update_size(self,name,size,index):
        for i,series in self.series_dict[index].items():
            if name == self.elements_dict[index][i]:
                series.setItemSize(size*20/self.range)

    def change_fonts(self,fontname,fontsize):
        self.activeTheme().setFont(QtGui.QFont(fontname,fontsize))

    def change_theme(self, color):
        self.activeTheme().setBackgroundColor(QtGui.QColor(color))
        self.activeTheme().setWindowColor(QtGui.QColor(color))
        self.activeTheme().setLabelBackgroundEnabled(False)
        self.activeTheme().setLabelBorderEnabled(False)
        try:
            self.update_coordinates(self.coordinateStatus)
        except:
            pass
        try:
            self.update_all_colors()
        except:
            pass

    def change_shadow_quality(self,quality):
        self.setShadowQuality(quality)

    def raise_error(self,message):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.setEscapeButton(QtWidgets.QMessageBox.Close)
        msg.exec()

    def raise_attention(self,information):
        info = QtWidgets.QMessageBox()
        info.setIcon(QtWidgets.QMessageBox.Information)
        info.setText(information)
        info.setWindowTitle("Information")
        info.setStandardButtons(QtWidgets.QMessageBox.Ok)
        info.setEscapeButton(QtWidgets.QMessageBox.Close)
        info.exec()

def test():
    app = QtWidgets.QApplication(sys.argv)
    simulation = Window()
    simulation.main()
    sys.exit(app.exec_())

if __name__ == '__main__':
    test()
