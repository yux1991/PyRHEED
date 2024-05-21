from PyQt6 import QtCore, QtGui, QtWidgets, QtDataVisualization
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.collections import LineCollection
from my_widgets import LabelLineEdit, IndexedComboBox, LockableDoubleSlider, LabelSlider, LabelSpinBox, InfoBoard, IndexedPushButton, DynamicalColorMap, IndexedColorPicker
from process import Convertor, DiffractionPattern, TAPD_Simulation, TAPD_model
from pymatgen.io.cif import CifParser
from pymatgen.core import structure as pgStructure
from pymatgen.core.operations import SymmOp
from pymatgen.core.lattice import Lattice
import browser
import itertools
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd
import os
import re
from scipy.spatial import cKDTree
from scipy.spatial import voronoi_plot_2d
from shapely.geometry import LineString
from shapely.geometry import Point
from shapely.geometry import Polygon
import sys
try:
    import pycuda.compiler as comp
    import pycuda.driver as drv
    CUDA_EXIST = True
except:
    CUDA_EXIST = False

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
    TAPD_FINISHED = QtCore.pyqtSignal()
    TAPD_RESULTS = QtCore.pyqtSignal(TAPD_model,str)
    CLOSE = QtCore.pyqtSignal()
    RESULT_IS_READY = QtCore.pyqtSignal()
    SAVE_FFT = QtCore.pyqtSignal(str)
    TOGGLE_DARK_MODE_SIGNAL = QtCore.pyqtSignal(str)

    def __init__(self, appTheme):
        super(Window,self).__init__()
        self.dirname = os.path.dirname(__file__)
        self.convertor_worker = Convertor()
        self.appTheme = appTheme

    def main(self):
        self.graph = ScatterGraph()
        dirname = os.path.dirname(__file__)
        self.AFF = pd.read_excel(open(os.path.join(dirname,'data/files/AtomicFormFactors.xlsx'),'rb'),sheet_name="Atomic Form Factors",index_col=0)
        self.AR = pd.read_excel(open(os.path.join(dirname,'data/files/AtomicRadii.xlsx'),'rb'),sheet_name="Atomic Radius",index_col=0)
        self.structure_index = 0
        self.data_index_set = set()
        self.sample_index_set = set()
        self.sample_tab_index = []
        self.deleted_tab_index = set()
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
        self.scenario_CIF = None 
        self.currentDestination = ''
        self.container = QtWidgets.QWidget.createWindowContainer(self.graph)
        self.screenSize = self.graph.screen().size()
        self.container.setMinimumSize(int(self.screenSize.width()/2), int(self.screenSize.height()/2))
        self.container.setMaximumSize(self.screenSize)
        self.container.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,QtWidgets.QSizePolicy.Policy.Expanding)
        self.container.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.mainVLayout = QtWidgets.QVBoxLayout(self)
        self.hSplitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        self.controlPanel = QtWidgets.QFrame()
        self.displayPanel = QtWidgets.QFrame()
        self.vLayout = QtWidgets.QVBoxLayout(self.controlPanel)
        self.vLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.vLayout.setContentsMargins(0,0,0,0)
        self.vLayout_left = QtWidgets.QVBoxLayout(self.displayPanel)
        self.vLayout_left.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.vSplitter_left = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        self.vLayout_left.addWidget(self.vSplitter_left)
        self.vSplitter_left.addWidget(self.container)
        self.vSplitter_left.setStretchFactor(0,1)
        self.vSplitter_left.setStretchFactor(1,1)
        self.hSplitter.addWidget(self.displayPanel)
        self.controlPanelScroll = QtWidgets.QScrollArea(self.hSplitter)
        self.hSplitter.setStretchFactor(0,1)
        self.hSplitter.setStretchFactor(1,1)
        self.hSplitter.setCollapsible(0,False)
        self.hSplitter.setCollapsible(1,False)
        self.mainVLayout.addWidget(self.hSplitter)
        self.setWindowTitle("RHEED Simulation")
        self.setWindowModality(QtCore.Qt.WindowModality.WindowModal)

        self.chooseCif = QtWidgets.QWidget()
        self.chooseCifGrid = QtWidgets.QGridLayout(self.chooseCif)
        self.chooseCifBrowser = browser.Browser(self.chooseCif, {"*.cif","*.CIF"})
        self.chooseCifLabel = QtWidgets.QLabel("The path of the CIF file is:\n")
        self.chooseCifLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
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
        self.TAPD_substrate_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.TAPD_substrate_label.setWordWrap(True)
        self.TAPD_add_substrate_button = QtWidgets.QPushButton("Add Substrate")
        self.TAPD_add_substrate_button.clicked.connect(lambda text: self.load_cif(text='Choose Substrate'))
        self.TAPD_epilayer_label = QtWidgets.QLabel("The path of the epilayer CIF is:\n")
        self.TAPD_epilayer_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.TAPD_epilayer_label.setWordWrap(True)
        self.TAPD_add_epilayer_button = QtWidgets.QPushButton("Add Epilayer")
        self.TAPD_add_epilayer_button.clicked.connect(lambda text: self.load_cif(text='Choose Epilayer'))
        self.TAPD_X_max_label = QtWidgets.QLabel('Maximum length in a direction (\u212B)')
        self.TAPD_X_max = QtWidgets.QLineEdit('100')
        self.TAPD_Y_max_label = QtWidgets.QLabel('Maximum length in b direction (\u212B)')
        self.TAPD_Y_max = QtWidgets.QLineEdit('100')
        self.TAPD_Z_min_label = QtWidgets.QLabel('Z minimum units in c direction')
        self.TAPD_Z_min = QtWidgets.QLineEdit('0')
        self.TAPD_Z_max_label = QtWidgets.QLabel('Z maximum units in c direction')
        self.TAPD_Z_max = QtWidgets.QLineEdit('0.5')
        self.TAPD_Shift_X_label = QtWidgets.QLabel('X shift (\u212B)')
        self.TAPD_Shift_X = QtWidgets.QLineEdit('0')
        self.TAPD_Shift_Y_label = QtWidgets.QLabel('Y shift (\u212B)')
        self.TAPD_Shift_Y = QtWidgets.QLineEdit('0')
        self.TAPD_Shift_Z_label = QtWidgets.QLabel('Z shift (\u212B)')
        self.TAPD_Shift_Z = QtWidgets.QLineEdit('8')
        self.TAPD_buffer_shift_X_label = QtWidgets.QLabel('Buffer X shift (\u212B)')
        self.TAPD_buffer_shift_X = QtWidgets.QLineEdit('0')
        self.TAPD_buffer_shift_Y_label = QtWidgets.QLabel('Buffer Y shift (\u212B)')
        self.TAPD_buffer_shift_Y = QtWidgets.QLineEdit('0')
        self.TAPD_buffer_shift_Z_label = QtWidgets.QLabel('Buffer Z shift (\u212B)')
        self.TAPD_buffer_shift_Z = QtWidgets.QLineEdit('-3')
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
        self.TAPD_add_atoms_label = QtWidgets.QLabel('Add atoms to the canvas?')
        self.TAPD_add_atoms = QtWidgets.QCheckBox()
        self.TAPD_add_atoms.setChecked(True)
        self.TAPD_add_substrate_label = QtWidgets.QLabel('Add substrate?')
        self.TAPD_add_substrate = QtWidgets.QCheckBox()
        self.TAPD_add_substrate.setChecked(True)
        self.TAPD_add_epilayer_label = QtWidgets.QLabel('Add epilayer?')
        self.TAPD_add_epilayer = QtWidgets.QCheckBox()
        self.TAPD_add_epilayer.setChecked(True)
        self.TAPD_add_epilayer.stateChanged.connect(self.toggle_add_epilayer)
        self.TAPD_add_boundary_label = QtWidgets.QLabel('Add only boundary?')
        self.TAPD_add_boundary = QtWidgets.QCheckBox()
        self.TAPD_add_boundary.setChecked(False)
        self.TAPD_constant_af_label = QtWidgets.QLabel('Use constant atomic structure factor?')
        self.TAPD_constant_af = QtWidgets.QCheckBox()
        self.TAPD_constant_af.setChecked(False)
        self.TAPD_lattice_or_atoms_label = QtWidgets.QLabel('Use lattice or atoms?')
        self.TAPD_lattice = QtWidgets.QCheckBox("Lattice")
        self.TAPD_atoms = QtWidgets.QCheckBox("Atoms")
        self.TAPD_latticeOrAtoms = QtWidgets.QButtonGroup()
        self.TAPD_latticeOrAtoms.setExclusive(True)
        self.TAPD_latticeOrAtoms.addButton(self.TAPD_lattice)
        self.TAPD_latticeOrAtoms.addButton(self.TAPD_atoms)
        self.TAPD_atoms.setChecked(True)

        self.TAPD_distribution_function_label = QtWidgets.QLabel('Epilayer nucleation distribution')
        self.TAPD_distribution_function = QtWidgets.QComboBox()
        self.TAPD_distribution_function.addItem('completely random')
        self.TAPD_distribution_function.addItem('geometric')
        self.TAPD_distribution_function.addItem('delta')
        self.TAPD_distribution_function.addItem('binomial')
        self.TAPD_distribution_function.addItem('uniform')
        self.TAPD_distribution_function.currentTextChanged.connect(self.change_distribution_function)

        self.TAPD_add_buffer_label = QtWidgets.QLabel('Add buffer layer?')
        self.TAPD_add_buffer = QtWidgets.QCheckBox()
        self.TAPD_add_buffer.setChecked(False)
        self.TAPD_add_buffer.stateChanged.connect(self.toggle_add_buffer)
        self.TAPD_buffer_atom_label = QtWidgets.QLabel('Specify the buffer layer atom')
        self.TAPD_buffer_atom = QtWidgets.QLineEdit('S')
        self.TAPD_buffer_atom.textChanged.connect(self.check_TAPD_buffer_atom)

        self.TAPD_buffer_in_plane_distribution_label = QtWidgets.QLabel('Buffer layer in-plane distribution')
        self.TAPD_buffer_in_plane_distribution = QtWidgets.QComboBox()
        self.TAPD_buffer_in_plane_distribution.addItem('completely random')
        self.TAPD_buffer_in_plane_distribution.addItem('geometric')
        self.TAPD_buffer_in_plane_distribution.addItem('delta')
        self.TAPD_buffer_in_plane_distribution.addItem('binomial')
        self.TAPD_buffer_in_plane_distribution.addItem('uniform')
        self.TAPD_buffer_in_plane_distribution.currentTextChanged.connect(self.change_buffer_in_plane_distribution)

        self.TAPD_buffer_out_of_plane_distribution_label = QtWidgets.QLabel('Buffer layer out-of-plane distribution')
        self.TAPD_buffer_out_of_plane_distribution = QtWidgets.QComboBox()
        self.TAPD_buffer_out_of_plane_distribution.addItem('completely random')
        self.TAPD_buffer_out_of_plane_distribution.addItem('gaussian')
        self.TAPD_buffer_out_of_plane_distribution.addItem('uniform')
        self.TAPD_buffer_out_of_plane_distribution.setCurrentText('gaussian')

        self.distribution_parameters = QtWidgets.QGroupBox('Epilayer nucleation')
        self.distribution_parameters_grid = QtWidgets.QGridLayout(self.distribution_parameters)
        self.distribution_parameters_grid.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.TAPD_completely_random_label = QtWidgets.QLabel('Density')
        self.TAPD_completely_random = QtWidgets.QLineEdit('0.01')
        self.distribution_parameters_grid.addWidget(self.TAPD_completely_random_label)
        self.distribution_parameters_grid.addWidget(self.TAPD_completely_random)

        self.buffer_in_plane_distribution_parameters = QtWidgets.QGroupBox('Buffer layer in-plane')
        self.buffer_in_plane_distribution_parameters_grid = QtWidgets.QGridLayout(self.buffer_in_plane_distribution_parameters)
        self.buffer_in_plane_distribution_parameters_grid.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.TAPD_buffer_in_plane_completely_random_label = QtWidgets.QLabel('Density')
        self.TAPD_buffer_in_plane_completely_random = QtWidgets.QLineEdit('1')
        self.buffer_in_plane_distribution_parameters_grid.addWidget(self.TAPD_buffer_in_plane_completely_random_label)
        self.buffer_in_plane_distribution_parameters_grid.addWidget(self.TAPD_buffer_in_plane_completely_random)

        self.buffer_out_of_plane_distribution_parameters = QtWidgets.QGroupBox('Buffer layer out-of-plane')
        self.buffer_out_of_plane_distribution_parameters_grid = QtWidgets.QGridLayout(self.buffer_out_of_plane_distribution_parameters)
        self.buffer_out_of_plane_distribution_parameters_grid.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.TAPD_buffer_out_of_plane_low_label = QtWidgets.QLabel('low (\u212B)')
        self.TAPD_buffer_out_of_plane_low = QtWidgets.QLineEdit('-0.5')
        self.TAPD_buffer_out_of_plane_high_label = QtWidgets.QLabel('high (\u212B)')
        self.TAPD_buffer_out_of_plane_high = QtWidgets.QLineEdit('0.5')
        self.buffer_out_of_plane_distribution_parameters_grid.addWidget(self.TAPD_buffer_out_of_plane_low_label)
        self.buffer_out_of_plane_distribution_parameters_grid.addWidget(self.TAPD_buffer_out_of_plane_low)
        self.buffer_out_of_plane_distribution_parameters_grid.addWidget(self.TAPD_buffer_out_of_plane_high_label)
        self.buffer_out_of_plane_distribution_parameters_grid.addWidget(self.TAPD_buffer_out_of_plane_high)
        self.toggle_add_buffer(0)

        self.plot_size_distribution_button = QtWidgets.QPushButton("Plot Size Distribution")
        self.plot_boundary_statistics_button = QtWidgets.QPushButton("Plot Boundary Statistics")
        self.plot_boundary_button = QtWidgets.QPushButton("Plot Boundary")
        self.plot_voronoi_button = QtWidgets.QPushButton("Plot Voronoi Diagram")
        self.save_scene_button = QtWidgets.QPushButton("Save Scene")
        self.save_scene_button.clicked.connect(self.graph.save_scene)
        self.plot_size_distribution_button.setEnabled(False)
        self.plot_boundary_statistics_button.setEnabled(False)
        self.plot_boundary_button.setEnabled(False)
        self.plot_voronoi_button.setEnabled(False)
        self.reload_TAPD_structure_button = QtWidgets.QPushButton("Reload Structure")
        self.load_TAPD_structure_button = QtWidgets.QPushButton("Add Structure")
        self.stop_TAPD_structure_button = QtWidgets.QPushButton("Stop")
        self.reset_TAPD_structure_button = QtWidgets.QPushButton("Reset Structure")
        self.plot_size_distribution_button.clicked.connect(self.plot_distribution)
        self.plot_boundary_statistics_button.clicked.connect(self.plot_boundary_statistics)
        self.plot_boundary_button.clicked.connect(self.plot_boundary)
        self.plot_voronoi_button.clicked.connect(self.plot_voronoi)
        self.reload_TAPD_structure_button.clicked.connect(self.reload_TAPD)
        self.load_TAPD_structure_button.clicked.connect(self.load_TAPD)
        self.stop_TAPD_structure_button.clicked.connect(self.stop_TAPD)
        self.reset_TAPD_structure_button.clicked.connect(self.reset_TAPD)

        self.TAPD_model_grid.addWidget(self.TAPD_substrate_label,0,0,1,3)
        self.TAPD_model_grid.addWidget(self.TAPD_add_substrate_button,0,3,1,1)
        self.TAPD_model_grid.addWidget(self.TAPD_epilayer_label,1,0,1,3)
        self.TAPD_model_grid.addWidget(self.TAPD_add_epilayer_button,1,3,1,1)
        self.TAPD_model_grid.addWidget(self.TAPD_substrate_orientation_label,2,0,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_substrate_orientation,2,2,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_epilayer_orientation_label,3,0,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_epilayer_orientation,3,2,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_X_max_label,6,0,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_X_max,6,2,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_Y_max_label,7,0,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_Y_max,7,2,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_Z_min_label,10,0,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_Z_min,10,2,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_Z_max_label,11,0,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_Z_max,11,2,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_Shift_X_label,14,0,1,1)
        self.TAPD_model_grid.addWidget(self.TAPD_Shift_X,14,1,1,1)
        self.TAPD_model_grid.addWidget(self.TAPD_Shift_Y_label,15,0,1,1)
        self.TAPD_model_grid.addWidget(self.TAPD_Shift_Y,15,1,1,1)
        self.TAPD_model_grid.addWidget(self.TAPD_Shift_Z_label,16,0,1,1)
        self.TAPD_model_grid.addWidget(self.TAPD_Shift_Z,16,1,1,1)
        self.TAPD_model_grid.addWidget(self.TAPD_buffer_shift_X_label,14,2,1,1)
        self.TAPD_model_grid.addWidget(self.TAPD_buffer_shift_X,14,3,1,1)
        self.TAPD_model_grid.addWidget(self.TAPD_buffer_shift_Y_label,15,2,1,1)
        self.TAPD_model_grid.addWidget(self.TAPD_buffer_shift_Y,15,3,1,1)
        self.TAPD_model_grid.addWidget(self.TAPD_buffer_shift_Z_label,16,2,1,1)
        self.TAPD_model_grid.addWidget(self.TAPD_buffer_shift_Z,16,3,1,1)
        self.TAPD_model_grid.addWidget(self.TAPD_add_atoms_label,26,0,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_add_atoms,26,2,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_add_substrate_label,27,0,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_add_substrate,27,2,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_add_epilayer_label,28,0,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_add_epilayer,28,2,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_add_boundary_label,29,0,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_add_boundary,29,2,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_constant_af_label,30,0,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_constant_af,30,2,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_lattice_or_atoms_label,31,0,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_lattice,31,2,1,1)
        self.TAPD_model_grid.addWidget(self.TAPD_atoms,31,3,1,1)
        self.TAPD_model_grid.addWidget(self.TAPD_add_buffer_label,32,0,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_add_buffer,32,2,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_buffer_atom_label,33,0,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_buffer_atom,33,2,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_distribution_function_label,34,0,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_distribution_function,34,2,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_buffer_in_plane_distribution_label,35,0,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_buffer_in_plane_distribution,35,2,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_buffer_out_of_plane_distribution_label,36,0,1,2)
        self.TAPD_model_grid.addWidget(self.TAPD_buffer_out_of_plane_distribution,36,2,1,2)
        self.TAPD_distribution_parameters_layout = QtWidgets.QHBoxLayout()
        self.TAPD_distribution_parameters_layout.addWidget(self.distribution_parameters)
        self.TAPD_distribution_parameters_layout.addWidget(self.buffer_in_plane_distribution_parameters)
        self.TAPD_distribution_parameters_layout.addWidget(self.buffer_out_of_plane_distribution_parameters)
        self.TAPD_model_grid.addLayout(self.TAPD_distribution_parameters_layout,37,0,1,4)
        self.TAPD_model_grid.addWidget(self.reload_TAPD_structure_button,39,0,1,1)
        self.TAPD_model_grid.addWidget(self.load_TAPD_structure_button,39,1,1,1)
        self.TAPD_model_grid.addWidget(self.stop_TAPD_structure_button,39,2,1,1)
        self.TAPD_model_grid.addWidget(self.reset_TAPD_structure_button,39,3,1,1)
        self.TAPD_model_grid.addWidget(self.plot_size_distribution_button,40,0,1,4)
        self.TAPD_model_grid.addWidget(self.plot_boundary_statistics_button,41,0,1,4)
        self.TAPD_model_grid.addWidget(self.plot_boundary_button,42,0,1,4)
        self.TAPD_model_grid.addWidget(self.plot_voronoi_button,43,0,1,4)

        self.CIF_tab = QtWidgets.QTabWidget()
        self.CIF_tab.addTab(self.chooseCif,'CIF')
        self.CIF_tab.addTab(self.TAPD_model,'TAPD')
        self.CIF_tab.setMaximumHeight(400)
        self.CIF_tab.currentChanged.connect(self.CIF_tab_changed)

        self.chooseDestination = QtWidgets.QGroupBox("Save Destination")
        self.destinationGrid = QtWidgets.QGridLayout(self.chooseDestination)
        self.chooseDestinationLabel = QtWidgets.QLabel("The save destination is:\n")
        self.chooseDestinationLabel.setWordWrap(True)
        self.destinationNameLabel = QtWidgets.QLabel("The file name is:")
        self.destinationNameEdit = QtWidgets.QLineEdit('3D_data')
        self.chooseDestinationButton = QtWidgets.QPushButton("Browse...")
        self.chooseDestinationButton.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed,QtWidgets.QSizePolicy.Policy.Fixed)
        self.chooseDestinationButton.clicked.connect(self.choose_destination)
        self.destinationGrid.addWidget(self.chooseDestinationLabel,0,0,1,3)
        self.destinationGrid.addWidget(self.chooseDestinationButton,0,3,1,1)
        self.destinationGrid.addWidget(self.destinationNameLabel,1,0,1,1)
        self.destinationGrid.addWidget(self.destinationNameEdit,1,1,1,3)
        self.destinationGrid.addWidget(self.save_scene_button,2,0,1,4)

        self.sample_tab = QtWidgets.QTabWidget()
        self.sample_tab.setTabsClosable(True)
        self.sample_tab.tabCloseRequested.connect(self.delete_structure)
        self.sample_tab.setVisible(False)

        self.tab = QtWidgets.QTabWidget()

        self.reciprocal_range_box = QtWidgets.QWidget()
        self.reciprocal_range_grid = QtWidgets.QGridLayout(self.reciprocal_range_box)
        self.reciprocal_range_grid.setContentsMargins(5,5,5,5)
        self.reciprocal_range_grid.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
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
        self.K_range_lock_label = QtWidgets.QLabel('Symmetric')
        self.Kx_range_lock = QtWidgets.QCheckBox()
        self.Kx_range_lock.setChecked(True)
        self.Kx_range = LockableDoubleSlider(-1000,1000,10,-10,10,"Kx range","\u212B\u207B\u00B9",self.Kx_range_lock.isChecked())
        self.Kx_range_lock.stateChanged.connect(self.Kx_range.set_locked)
        self.Ky_range_lock = QtWidgets.QCheckBox()
        self.Ky_range_lock.setChecked(True)
        self.Ky_range = LockableDoubleSlider(-1000,1000,10,-10,10,"Ky range","\u212B\u207B\u00B9",self.Ky_range_lock.isChecked())
        self.Ky_range_lock.stateChanged.connect(self.Ky_range.set_locked)
        self.Kz_range_lock = QtWidgets.QCheckBox()
        self.Kz_range_lock.setChecked(False)
        self.Kz_range = LockableDoubleSlider(-1000,1000,10,0,10,"Kz range","\u212B\u207B\u00B9",self.Kz_range_lock.isChecked())
        self.Kz_range_lock.stateChanged.connect(self.Kz_range.set_locked)
        self.apply_reciprocal_range = QtWidgets.QPushButton("Start Calculation")
        self.apply_reciprocal_range.clicked.connect(self.update_reciprocal_range)
        self.apply_reciprocal_range.setEnabled(False)
        self.stop_calculation = QtWidgets.QPushButton("Abort Calculation")
        self.stop_calculation.clicked.connect(self.stop_diffraction_calculation)
        self.stop_calculation.setEnabled(False)

        self.reciprocal_range_grid.addWidget(self.number_of_steps_para_label,0,0,1,4)
        self.reciprocal_range_grid.addWidget(self.number_of_steps_para,0,4,1,4)
        self.reciprocal_range_grid.addWidget(self.number_of_steps_perp_label,1,0,1,4)
        self.reciprocal_range_grid.addWidget(self.number_of_steps_perp,1,4,1,4)
        self.reciprocal_range_grid.addWidget(self.K_range_lock_label,2,7,1,1)
        self.reciprocal_range_grid.addWidget(self.Kx_range,3,0,1,7)
        self.reciprocal_range_grid.addWidget(self.Kx_range_lock,3,7,1,1)
        self.reciprocal_range_grid.addWidget(self.Ky_range,4,0,1,7)
        self.reciprocal_range_grid.addWidget(self.Ky_range_lock,4,7,1,1)
        self.reciprocal_range_grid.addWidget(self.Kz_range,5,0,1,7)
        self.reciprocal_range_grid.addWidget(self.Kz_range_lock,5,7,1,1)
        self.reciprocal_range_grid.addWidget(self.apply_reciprocal_range,6,0,1,8)
        self.reciprocal_range_grid.addWidget(self.stop_calculation,7,0,1,8)
        self.KRange = [self.Kx_range.values(),self.Ky_range.values(),self.Kz_range.values()]
        self.x_linear = np.linspace(self.KRange[0][0],self.KRange[0][1],self.number_of_steps_para.value())
        self.y_linear = np.linspace(self.KRange[1][0],self.KRange[1][1],self.number_of_steps_para.value())
        self.z_linear = np.linspace(self.KRange[2][0],self.KRange[2][1],self.number_of_steps_perp.value())
        self.Kx,self.Ky,self.Kz = np.meshgrid(self.x_linear,self.y_linear,self.z_linear)
        self.tab.addTab(self.reciprocal_range_box,"Detector")

        self.plotOptions = QtWidgets.QGroupBox("Plot Options")
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
        self.plot_fft_label = QtWidgets.QLabel("Do FFT for the IV curve?")
        self.plot_fft = QtWidgets.QCheckBox()
        self.pos = 111
        self.plot_fft.setChecked(False)
        self.plot_fft.stateChanged.connect(self.update_plot_fft)
        self.reciprocalMapfontListLabel = QtWidgets.QLabel("Font Name")
        self.reciprocalMapfontList = QtWidgets.QFontComboBox()
        self.reciprocalMapfontList.setCurrentFont(QtGui.QFont("Arial"))
        self.reciprocalMapfontList.currentFontChanged.connect(self.update_plot_font)
        self.reciprocalMapfontSizeLabel = QtWidgets.QLabel("Font Size ({})".format(7))
        self.reciprocalMapfontSizeLabel.setFixedWidth(160)
        self.reciprocalMapfontSizeSlider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.reciprocalMapfontSizeSlider.setMinimum(1)
        self.reciprocalMapfontSizeSlider.setMaximum(100)
        self.reciprocalMapfontSizeSlider.setValue(7)
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
        self.save_Results_button = QtWidgets.QPushButton("Save the data")
        self.save_Results_button.clicked.connect(self.save_results)
        self.save_Results_button.setEnabled(False)
        self.save_FFT_button = QtWidgets.QPushButton("Save the FFT")
        self.save_FFT_button.clicked.connect(self.save_FFT)
        self.save_FFT_button.setEnabled(False)
        self.plotOptionsGrid.addWidget(self.load_data_button,0,0,1,3)
        self.plotOptionsGrid.addWidget(self.KxyIndex,1,0,1,3)
        self.plotOptionsGrid.addWidget(self.KzIndex,2,0,1,3)
        self.plotOptionsGrid.addWidget(self.showFWHMCheckLabel,3,0,1,1)
        self.plotOptionsGrid.addWidget(self.showFWHMCheck,3,1,1,2)
        self.plotOptionsGrid.addWidget(self.plot_log_scale_label,4,0,1,1)
        self.plotOptionsGrid.addWidget(self.plot_log_scale,4,1,1,2)
        self.plotOptionsGrid.addWidget(self.plot_fft_label,5,0,1,1)
        self.plotOptionsGrid.addWidget(self.plot_fft,5,1,1,2)
        self.plotOptionsGrid.addWidget(self.reciprocalMapfontListLabel,6,0,1,1)
        self.plotOptionsGrid.addWidget(self.reciprocalMapfontList,6,1,1,2)
        self.plotOptionsGrid.addWidget(self.reciprocalMapfontSizeLabel,7,0,1,1)
        self.plotOptionsGrid.addWidget(self.reciprocalMapfontSizeSlider,7,1,1,2)
        self.plotOptionsGrid.addWidget(self.reciprocalMapColormapLabel,8,0,1,1)
        self.plotOptionsGrid.addWidget(self.reciprocalMapColormapCombo,8,1,1,2)
        self.plotOptionsGrid.addWidget(self.show_XY_plot_button,9,0,1,1)
        self.plotOptionsGrid.addWidget(self.show_XZ_plot_button,9,1,1,1)
        self.plotOptionsGrid.addWidget(self.show_YZ_plot_button,9,2,1,1)
        self.plotOptionsGrid.addWidget(self.save_Results_button,10,0,1,3)
        self.plotOptionsGrid.addWidget(self.save_FFT_button,11,0,1,3)

        self.appearance = QtWidgets.QWidget()
        self.appearanceGrid = QtWidgets.QVBoxLayout(self.appearance)
        self.appearanceGrid.setContentsMargins(5,5,5,5)
        self.appearanceGrid.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.graph.update_coordinates(0)
        self.showCoordinatesWidget = QtWidgets.QWidget()
        self.showCoordinatesGrid = QtWidgets.QGridLayout(self.showCoordinatesWidget)
        self.showCoordinatesLabel = QtWidgets.QLabel('Show Coordinate System?')
        self.showCoordinates = QtWidgets.QCheckBox()
        self.showCoordinates.setChecked(False)
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
        self.fontList = QtWidgets.QFontComboBox()
        self.fontList.setCurrentFont(QtGui.QFont("Arial"))
        self.fontList.currentFontChanged.connect(self.refresh_font_name)
        self.fontSizeLabel = QtWidgets.QLabel("Adjust Font Size ({})".format(5))
        self.fontSizeSlider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.fontSizeSlider.setMinimum(1)
        self.fontSizeSlider.setMaximum(100)
        self.fontSizeSlider.setValue(5)
        self.fontSizeSlider.valueChanged.connect(self.refresh_font_size)
        self.FONTS_CHANGED.connect(self.graph.change_fonts)

        self.shadowQualityLabel = QtWidgets.QLabel("Shadow Quality")
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
        self.statusGrid = QtWidgets.QGridLayout(self.statusBar)
        #self.statusBar.setFixedHeight(150)
        self.statusBar.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,QtWidgets.QSizePolicy.Policy.Fixed)
        self.logBox = QtWidgets.QTextEdit(QtCore.QTime.currentTime().toString("hh:mm:ss")+ \
                                          "\u00A0\u00A0\u00A0\u00A0Initialized!")
        self.logCursor = QtGui.QTextCursor(self.logBox.document())
        self.logCursor.movePosition(QtGui.QTextCursor.MoveOperation.End)
        self.logBox.setTextCursor(self.logCursor)
        self.logBox.ensureCursorVisible()
        self.logBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.logBox.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        #self.logBoxScroll = QtWidgets.QScrollArea()
        #self.logBoxScroll.setWidget(self.logBox)
        #self.logBoxScroll.setWidgetResizable(True)
        #self.logBoxScroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setVisible(False)
        self.progressBar.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.progressBarSizePolicy = self.progressBar.sizePolicy()
        self.progressBarSizePolicy.setRetainSizeWhenHidden(True)
        self.progressBarSizePolicy.setHorizontalPolicy(QtWidgets.QSizePolicy.Policy.Expanding)
        self.progressBar.setSizePolicy(self.progressBarSizePolicy)
        self.PROGRESS_ADVANCE.connect(self.progress)
        self.PROGRESS_HOLD.connect(self.progress_on)
        self.PROGRESS_END.connect(self.progress_reset)
        self.statusGrid.addWidget(self.logBox,0,0)
        self.vSplitter_left.addWidget(self.statusBar)
        self.vLayout_left.addWidget(self.progressBar)

        themeLabel = QtWidgets.QLabel("Background Color")
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
        self.tab.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,QtWidgets.QSizePolicy.Policy.Fixed)

        self.view = QtWidgets.QWidget()
        self.viewGrid = QtWidgets.QVBoxLayout(self.view)
        self.viewGrid.setContentsMargins(5,5,5,5)
        self.viewGrid.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        viewLabel = QtWidgets.QLabel("Set View Direction")
        self.graph.update_view_direction(16)
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
        self.tab.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,QtWidgets.QSizePolicy.Policy.Fixed)

        self.gpu = QtWidgets.QWidget()
        self.gpuGrid = QtWidgets.QVBoxLayout(self.gpu)
        self.gpuGrid.setContentsMargins(5,5,5,5)
        self.gpuGrid.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.useCUDAWidget = QtWidgets.QWidget()
        self.useCUDAGrid = QtWidgets.QGridLayout(self.useCUDAWidget)
        self.useCUDALabel = QtWidgets.QLabel('Use CUDA?')
        self.useCUDA = QtWidgets.QCheckBox()
        if CUDA_EXIST:
            self.useCUDA.setChecked(True)
        else:
            self.useCUDA.setChecked(False)
            self.useCUDA.setEnabled(False)
        self.gstart_calculation = QtWidgets.QPushButton("Start Calculation")
        self.gstart_calculation.clicked.connect(self.update_reciprocal_range)
        self.gstart_calculation.setEnabled(False)
        self.gstop_calculation = QtWidgets.QPushButton("Abort Calculation")
        self.gstop_calculation.clicked.connect(self.stop_diffraction_calculation)
        self.gstop_calculation.setEnabled(False)
        self.useCUDA.stateChanged.connect(self.update_gpu)
        self.useCUDAGrid.addWidget(self.useCUDALabel,0,0,1,1)
        self.useCUDAGrid.addWidget(self.useCUDA,0,1,1,1)
        self.useCUDAGrid.addWidget(self.gstart_calculation,1,0,1,2)
        self.useCUDAGrid.addWidget(self.gstop_calculation,2,0,1,2)

        self.gpuGrid.addWidget(self.useCUDAWidget)
        self.tab.addTab(self.gpu,"GPU")
        self.tab.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,QtWidgets.QSizePolicy.Policy.Fixed)

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
        self.controlPanelScroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)

        self.themeList.currentTextChanged.connect(self.graph.change_theme)
        if self.appTheme == 'light':
            self.themeList.setCurrentIndex(0)
        elif self.appTheme == 'dark':
            self.themeList.setCurrentIndex(4)
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

    def toggle_dark_mode(self, mode):
        self.appTheme = mode
        if mode == 'dark':
            self.themeList.setCurrentIndex(4)
        elif mode == 'light':
            self.themeList.setCurrentIndex(0)
        self.TOGGLE_DARK_MODE_SIGNAL.emit(mode)

    def CIF_tab_changed(self,index):
        if index == 0:
            self.CIF_tab.setMaximumHeight(400)
        elif index == 1:
            self.CIF_tab.setMaximumHeight(4000)

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
        self.deleted_tab_index.add(index)
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
        path = QtWidgets.QFileDialog.getExistingDirectory(None,"choose save destination",self.dirname,QtWidgets.QFileDialog.ShowDirsOnly)
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

    def update_gpu(self,status):
        self.graph.update_gpu(status)

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
                           self.real_space_specification_dict[index]['rotation'],self.AR, self.TAPD_constant_af.isChecked(), self.TAPD_add_atoms.isChecked(),self.useCUDA.isChecked())
        self.data_index_set.add(index)
        self.update_log("New real space range for sample" + str(index+1) +" applied!")

    def update_reciprocal_range(self):
        self.update_log("Calculating diffraction pattern ......")
        self.apply_reciprocal_range.setEnabled(False)
        self.stop_calculation.setEnabled(True)
        self.gstart_calculation.setEnabled(False)
        self.gstop_calculation.setEnabled(True)
        self.show_XY_plot_button.setEnabled(False)
        self.show_XZ_plot_button.setEnabled(False)
        self.show_YZ_plot_button.setEnabled(False)
        self.save_Results_button.setEnabled(False)
        self.save_FFT_button.setEnabled(False)
        QtCore.QCoreApplication.processEvents()
        self.KRange = [self.Kx_range.values(),self.Ky_range.values(),self.Kz_range.values()]
        self.x_linear = np.linspace(self.KRange[0][0],self.KRange[0][1],self.number_of_steps_para.value())
        self.y_linear = np.linspace(self.KRange[1][0],self.KRange[1][1],self.number_of_steps_para.value())
        self.z_linear = np.linspace(self.KRange[2][0],self.KRange[2][1],self.number_of_steps_perp.value())
        self.Kx,self.Ky,self.Kz = np.meshgrid(self.x_linear,self.y_linear,self.z_linear)
        if hasattr(self,'constant_af'):
            af = self.constant_af
        else:
            af = self.TAPD_constant_af.isChecked()
        self.graph.calculate(self.Kx,self.Ky,self.Kz,self.AFF,af)

    def finish_calculation(self,intensity):
        self.diffraction_intensity = intensity
        self.update_log("Finished Calculation!")
        self.show_XY_plot_button.setEnabled(True)
        self.show_XZ_plot_button.setEnabled(True)
        self.show_YZ_plot_button.setEnabled(True)
        self.save_Results_button.setEnabled(True)
        if 1 in self.diffraction_intensity.shape:
            self.save_FFT_button.setEnabled(True)
        self.apply_reciprocal_range.setEnabled(True)
        self.stop_calculation.setEnabled(False)
        self.gstart_calculation.setEnabled(True)
        self.gstop_calculation.setEnabled(False)
        self.RESULT_IS_READY.emit()

    def abort_calculation(self):
        self.apply_reciprocal_range.setEnabled(True)
        self.stop_calculation.setEnabled(False)
        self.gstart_calculation.setEnabled(True)
        self.gstop_calculation.setEnabled(False)
        self.update_log("Aborted Calculation!")
        self.show_XY_plot_button.setEnabled(False)
        self.show_XZ_plot_button.setEnabled(False)
        self.show_YZ_plot_button.setEnabled(False)
        self.save_Results_button.setEnabled(False)
        self.save_FFT_button.setEnabled(False)
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

    def update_plot_fft(self,state):
        if state == 2:
            self.pos = 211
        elif state == 0:
            self.pos = 111

    def show_XY_plot(self, **kwargs):
        for i in range(int(self.KzIndex.values()[0]),int(self.KzIndex.values()[1]+1)):
            TwoDimPlot = DynamicalColorMap(self,'XY',self.x_linear,self.y_linear,self.z_linear,self.diffraction_intensity,i,\
                         self.reciprocalMapfontList.currentFont().family(),self.reciprocalMapfontSizeSlider.value(), \
                         self.reciprocalMapColormapCombo.currentText(),self.showFWHMCheck.isChecked(),self.plot_log_scale.isChecked(),111,self.appTheme,kwargs)
            TwoDimPlot.UPDATE_LOG.connect(self.update_log)
            self.REFRESH_PLOT_FONTS.connect(TwoDimPlot.refresh_fonts)
            self.TOGGLE_DARK_MODE_SIGNAL.connect(TwoDimPlot.toggle_dark_mode)
            if not 1 in self.diffraction_intensity.shape[0:1]:
                self.REFRESH_PLOT_FWHM.connect(TwoDimPlot.refresh_FWHM)
                self.REFRESH_PLOT_COLORMAP.connect(TwoDimPlot.refresh_colormap)
                TwoDimPlot.show_plot()
        if not 1 in self.diffraction_intensity.shape[0:1]:
            self.update_log("Simulated diffraction patterns obtained!")

    def show_XZ_plot(self, **kwargs):
        for i in range(int(self.KxyIndex.values()[0]),int(self.KxyIndex.values()[1]+1)):
            TwoDimPlot = DynamicalColorMap(self,'XZ',self.x_linear,self.y_linear,self.z_linear,self.diffraction_intensity,i, \
                                                    self.reciprocalMapfontList.currentFont().family(),self.reciprocalMapfontSizeSlider.value(), \
                                                    self.reciprocalMapColormapCombo.currentText(),self.showFWHMCheck.isChecked(),self.plot_log_scale.isChecked(),self.pos,self.appTheme,kwargs)
            TwoDimPlot.UPDATE_LOG.connect(self.update_log)
            self.REFRESH_PLOT_FONTS.connect(TwoDimPlot.refresh_fonts)
            self.TOGGLE_DARK_MODE_SIGNAL.connect(TwoDimPlot.toggle_dark_mode)
            if not 1 in self.diffraction_intensity.shape:
                self.REFRESH_PLOT_FWHM.connect(TwoDimPlot.refresh_FWHM)
                self.REFRESH_PLOT_COLORMAP.connect(TwoDimPlot.refresh_colormap)
            else:
                self.SAVE_FFT.connect(TwoDimPlot.save_FFT)
            TwoDimPlot.show_plot()
        if not 1 in self.diffraction_intensity.shape:
            self.update_log("Simulated diffraction patterns obtained!")

    def show_YZ_plot(self, **kwargs):
        for i in range(int(self.KxyIndex.values()[0]),int(self.KxyIndex.values()[1]+1)):
            TwoDimPlot = DynamicalColorMap(self,'YZ',self.x_linear,self.y_linear,self.z_linear,self.diffraction_intensity,i, \
                                                    self.reciprocalMapfontList.currentFont().family(),self.reciprocalMapfontSizeSlider.value(), \
                                                    self.reciprocalMapColormapCombo.currentText(),self.showFWHMCheck.isChecked(),self.plot_log_scale.isChecked(),\
                                                    self.pos,self.appTheme,kwargs)
            TwoDimPlot.UPDATE_LOG.connect(self.update_log)
            self.REFRESH_PLOT_FONTS.connect(TwoDimPlot.refresh_fonts)
            self.TOGGLE_DARK_MODE_SIGNAL.connect(TwoDimPlot.toggle_dark_mode)
            if not 1 in self.diffraction_intensity.shape:
                self.REFRESH_PLOT_FWHM.connect(TwoDimPlot.refresh_FWHM)
                self.REFRESH_PLOT_COLORMAP.connect(TwoDimPlot.refresh_colormap)
            else:
                self.SAVE_FFT.connect(TwoDimPlot.save_FFT)
            TwoDimPlot.show_plot()
        if not 1 in self.diffraction_intensity.shape:
            self.update_log("Simulated diffraction patterns obtained!")

    def load_data(self):
        path = QtWidgets.QFileDialog.getOpenFileName(None,"Choose The 3D Data",self.dirname,filter="TXT (*.txt);;All Files (*.*)")[0]
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


    def get_cif_path(self,path=None):
        if not path:
            path = QtWidgets.QFileDialog.getOpenFileName(None,"Choose The CIF File",self.dirname,filter="CIF (*.cif);;All Files (*.*)")[0]
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
        path = QtWidgets.QFileDialog.getOpenFileName(None,text,self.dirname,filter="CIF (*.cif);;All Files (*.*)")[0]
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
        range_grid.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        lattice_constants_box = InfoBoard("Information",index)
        self.UPDATE_INOFRMATION_BOARD.connect(lattice_constants_box.update)
        shape_label = QtWidgets.QLabel("Shape")
        shape = IndexedComboBox(index)
        shape.addItem("Triangle")
        shape.addItem("Square")
        shape.addItem("Hexagon")
        shape.addItem("Circle")
        if not self.scenario_CIF:
            h_range = LabelSlider(1,100,3,1,"h",index=index)
            k_range = LabelSlider(1,100,3,1,"k",index=index)
            l_range = LabelSlider(1,100,1,1,"l",index=index)
            lateral_size = LabelSpinBox(1,100,1,1,"Lateral Size",'nm',index=index)
            x_shift = LabelSpinBox(-1000,1000,0,100,"X Shift",'\u212B',index=index)
            y_shift = LabelSpinBox(-1000,1000,0,100,"Y Shift",'\u212B',index=index)
            z_shift = LabelSpinBox(-5000,5000,0,100,"Z Shift",'\u212B',index=index)
            rotation = LabelSpinBox(-1800,1800,0,10,"rotation",'\u00B0',index=index)
            z_range_slider = LockableDoubleSlider(-8000,8000,100,-10,10,"Z range","\u212B",False,type='spinbox', index=index)
        else:
            h_range = LabelSlider(1,100,int(self.scenario_CIF['h_range']),1,"h",index=index)
            k_range = LabelSlider(1,100,int(self.scenario_CIF['k_range']),1,"k",index=index)
            l_range = LabelSlider(1,100,int(self.scenario_CIF['l_range']),1,"l",index=index)
            shape.setCurrentText(self.scenario_CIF['shape'])
            lateral_size = LabelSpinBox(1,100,int(self.scenario_CIF['lateral_size']),1,"Lateral Size",'nm',index=index)
            x_shift = LabelSpinBox(-1000,1000,float(self.scenario_CIF['X_shift']),100,"X Shift",'\u212B',index=index)
            y_shift = LabelSpinBox(-1000,1000,float(self.scenario_CIF['Y_shift']),100,"Y Shift",'\u212B',index=index)
            z_shift = LabelSpinBox(-5000,5000,float(self.scenario_CIF['Z_shift']),100,"Z Shift",'\u212B',index=index)
            rotation = LabelSpinBox(-1800,1800,float(self.scenario_CIF['rotation']),10,"rotation",'\u00B0',index=index)
            z_range_slider = LockableDoubleSlider(-8000,8000,100,-10,self.scenario_CIF['Z_max'],"Z range","\u212B",False,type='spinbox', index=index)
        shape.TEXT_CHANGED.connect(self.update_shape)
        h_range.VALUE_CHANGED.connect(self.update_h_range)
        k_range.VALUE_CHANGED.connect(self.update_k_range)
        l_range.VALUE_CHANGED.connect(self.update_l_range)
        lateral_size.VALUE_CHANGED.connect(self.update_lateral_size)
        x_shift.VALUE_CHANGED.connect(self.update_x_shift)
        y_shift.VALUE_CHANGED.connect(self.update_y_shift)
        z_shift.VALUE_CHANGED.connect(self.update_z_shift)
        rotation.VALUE_CHANGED.connect(self.update_rotation)
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
        if index in self.deleted_tab_index:
            self.deleted_tab_index.remove(index)
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
            colorPicker = IndexedColorPicker(name,'#'+self.AR.loc[name].at['Color'],self.AR.loc[name].at['Normalized Radius'],index)
            colorPicker.COLOR_CHANGED.connect(self.update_colors)
            colorPicker.SIZE_CHANGED.connect(self.update_size)
            self.colorSheet[index][name] = '#'+self.AR.loc[name].at['Color']
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
                            self.AR, self.TAPD_constant_af.isChecked(), self.TAPD_add_atoms.isChecked(),self.useCUDA.isChecked())
        self.data_index_set.add(index)
        self.graph.change_fonts(self.fontList.currentFont().family(),self.fontSizeSlider.value())
        self.graph.change_shadow_quality(self.shadowQuality.currentIndex())
        self.sample_tab.widget(index).layout().itemAt(12).widget().setEnabled(True)
        self.sample_tab.widget(index).layout().itemAt(13).widget().setEnabled(True)
        self.sample_tab.widget(index).layout().itemAt(14).widget().setEnabled(True)
        self.update_log("Finished adding data for sample " + str(index+1))
        QtCore.QCoreApplication.processEvents()
        self.apply_reciprocal_range.setEnabled(True)
        self.gstart_calculation.setEnabled(True)

    def replace_structure(self,index):
        self.update_log("Replacing sample" + str(index+1))
        QtCore.QCoreApplication.processEvents()
        path = QtWidgets.QFileDialog.getOpenFileName(None,"Choose The CIF File",self.dirname,filter="CIF (*.cif);;All Files (*.*)")[0]
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
                colorPicker = IndexedColorPicker(name,'#'+self.AR.loc[name].at['Color'],self.AR.loc[name].at['Normalized Radius'],index)
                colorPicker.COLOR_CHANGED.connect(self.update_colors)
                colorPicker.SIZE_CHANGED.connect(self.update_size)
                self.colorSheet[index][name] = '#'+self.AR.loc[name].at['Color']
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
                                self.AR, self.TAPD_constant_af.isChecked(), self.TAPD_add_atoms.isChecked(),self.useCUDA.isChecked())
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
            colorPicker = IndexedColorPicker(name,'#'+self.AR.loc[name].at['Color'],self.AR.loc[name].at['Normalized Radius'],index)
            colorPicker.COLOR_CHANGED.connect(self.update_colors)
            colorPicker.SIZE_CHANGED.connect(self.update_size)
            self.colorSheet[index][name] = '#'+self.AR.loc[name].at['Color']
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
                           self.AR, self.TAPD_constant_af.isChecked(), self.TAPD_add_atoms.isChecked(),self.useCUDA.isChecked())
        self.data_index_set.add(index)
        self.graph.change_fonts(self.fontList.currentFont().family(),self.fontSizeSlider.value())
        self.graph.change_shadow_quality(self.shadowQuality.currentIndex())
        self.update_log("Sample "+str(index+1)+" successfully reset!")

    def save_results(self, **kwargs):
        self.PROGRESS_HOLD.emit()
        QtCore.QCoreApplication.processEvents()
        if kwargs.get('save_as_file',False):
            directory = kwargs['directory']
            name = kwargs['name']
        else:
            directory = self.currentDestination
            name = self.destinationNameEdit.text()
        if not directory == '':
            self.convertor_worker.mtx2vtp(directory,name,self.diffraction_intensity,self.KRange,\
                        self.number_of_steps_para.value(),self.number_of_steps_perp.value(),\
                        self.real_space_specification_dict,self.element_species,kwargs.get('save_vtp',False))
            self.PROGRESS_END.emit()
        else:
            self.raise_error("Save destination is empty!")
    
    def save_FFT(self,path=None):
        if not path:
            path = QtWidgets.QFileDialog.getSaveFileName(None,\
                "Choose the destination for the FFT result",os.path.join(self.dirname,'FFT.txt'),"TXT (*.txt)")
        self.update_log("Saving FFT...")
        self.SAVE_FFT.emit(path[0])
        QtCore.QCoreApplication.processEvents()
        self.update_log("FFT saved")

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

    def closeEvent(self,event):
        try:
            self.stop_TAPD()
        except:
            pass
        self.CLOSE.emit()
        QtCore.QCoreApplication.processEvents()
        event.accept()

    def resizeEvent(self,event):
        self.screenSize = self.graph.screen().size()
        self.container.setMinimumSize(int(self.screenSize.width()/2), int(self.screenSize.height()/2))
        self.container.setMaximumSize(self.screenSize)

    def toggle_add_epilayer(self,state):
        if state == 0:
            enabled = False
        elif state == 2:
            enabled = True
        self.TAPD_add_boundary.setEnabled(enabled)

    def toggle_add_buffer(self,state):
        if state == 0:
            enabled = False
        elif state == 2:
            enabled = True
        self.TAPD_buffer_shift_X.setEnabled(enabled)
        self.TAPD_buffer_shift_Y.setEnabled(enabled)
        self.TAPD_buffer_shift_Z.setEnabled(enabled)
        self.TAPD_buffer_atom.setEnabled(enabled)
        self.TAPD_buffer_in_plane_distribution.setEnabled(enabled)
        self.TAPD_buffer_out_of_plane_distribution.setEnabled(enabled)
        self.buffer_in_plane_distribution_parameters.setEnabled(enabled)
        self.buffer_out_of_plane_distribution_parameters.setEnabled(enabled)

    def check_TAPD_buffer_atom(self,text):
        if not text in self.AR.index:
            self.raise_error('Please enter a valid name of element')

    def load_CIF_scenario(self,scenario):
        self.scenario_CIF = scenario
        self.CIF_tab.setCurrentWidget(self.chooseCif)
        self.Kx_range.set_locked(False)
        self.Ky_range.set_locked(False)
        self.Kx_range.set_head(float(scenario['Kx_range_min']))
        self.Kx_range.set_tail(float(scenario['Kx_range_max']))
        self.Ky_range.set_head(float(scenario['Ky_range_min']))
        self.Ky_range.set_tail(float(scenario['Ky_range_max']))
        self.Kz_range.set_head(float(scenario['Kz_range_min']))
        self.Kz_range.set_tail(float(scenario['Kz_range_max']))
        self.number_of_steps_para.setValue(int(scenario['number_of_K_para_steps']))
        self.number_of_steps_perp.setValue(int(scenario['number_of_K_perp_steps']))
        self.currentDestination = scenario['destination'] 
        self.chooseDestinationLabel.setText("The save destination is:\n"+self.currentDestination)
        if scenario['constant_af'] == 'True':
            self.TAPD_constant_af.setChecked(True)
            self.constant_af = True
        elif scenario['constant_af'] == 'False':
            self.TAPD_constant_af.setChecked(False)
            self.constant_af = False
        if scenario['plot_log_scale'] == 'True':
            self.plot_log_scale.setChecked(True)
        elif scenario['plot_log_scale'] == 'False':
            self.plot_log_scale.setChecked(False)
        if scenario['do_FFT_for_IV'] == 'True':
            self.plot_fft.setChecked(True)
        elif scenario['plot_log_scale'] == 'False':
            self.plot_fft.setChecked(False)
        self.UPDATE_CAMERA_POSITION.emit(float(scenario['camera_horizontal_rotation']),\
            float(scenario['camera_vertical_rotation']),float(scenario['camera_zoom_level']))

    def load_TAPD_scenario(self,scenario):
        self.scenario_TAPD = scenario
        self.CIF_tab.setCurrentWidget(self.TAPD_model)
        self.TAPD_distribution_function.setCurrentText(scenario['distribution'])
        if self.TAPD_distribution_function.currentText() == 'completely random':
            self.TAPD_completely_random.setText(scenario['density'])
        elif self.TAPD_distribution_function.currentText() == 'geometric':
            self.TAPD_geometric_gamma.text().setText(scenario['gamma'])
        elif self.TAPD_distribution_function.currentText() == 'delta':
            self.TAPD_delta_radius.text().setText(scenario['radius'])
        elif self.TAPD_distribution_function.currentText() == 'uniform':
            self.TAPD_uniform_low.text().setText(scenario['low'])
            self.TAPD_uniform_high.text().setText(scenario['high'])
        elif self.TAPD_distribution_function.currentText() == 'binomial':
            self.TAPD_binomial_n.text().setText(scenario['n'])
            self.TAPD_binomial_p.text().setText(scenario['p'])
        self.TAPD_X_max.setText(scenario['x_max'])
        self.TAPD_Y_max.setText(scenario['y_max'])
        self.TAPD_Z_max.setText(scenario['z_min'])
        self.TAPD_Z_max.setText(scenario['z_max'])
        self.TAPD_Shift_X.setText(scenario['x_shift'])
        self.TAPD_Shift_Y.setText(scenario['y_shift'])
        self.TAPD_Shift_Z.setText(scenario['z_shift'])
        self.Kx_range.set_locked(False)
        self.Ky_range.set_locked(False)
        self.Kx_range.set_head(float(scenario['Kx_range_min']))
        self.Kx_range.set_tail(float(scenario['Kx_range_max']))
        self.Ky_range.set_head(float(scenario['Ky_range_min']))
        self.Ky_range.set_tail(float(scenario['Ky_range_max']))
        self.Kz_range.set_head(float(scenario['Kz_range_min']))
        self.Kz_range.set_tail(float(scenario['Kz_range_max']))
        self.number_of_steps_para.setValue(int(scenario['number_of_K_para_steps']))
        self.number_of_steps_perp.setValue(int(scenario['number_of_K_perp_steps']))
        self.substrate_path = scenario['sub_cif_path']
        self.epilayer_path = scenario['epi_cif_path']
        self.currentDestination = scenario['destination'] 
        self.chooseDestinationLabel.setText("The save destination is:\n"+self.currentDestination)
        if scenario['lattice_or_atoms'] == 'lattice':
            self.TAPD_atoms.setChecked(False)
        elif scenario['lattice_or_atoms'] == 'atoms':
            self.TAPD_atoms.setChecked(True)
        if scenario['add_substrate'] == 'True':
            self.TAPD_add_substrate.setChecked(True)
        elif scenario['add_substrate'] == 'False':
            self.TAPD_add_substrate.setChecked(False)
        if scenario['add_epilayer'] == 'True':
            self.TAPD_add_epilayer.setChecked(True)
        elif scenario['add_epilayer'] == 'False':
            self.TAPD_add_epilayer.setChecked(False)
        if scenario['constant_af'] == 'True':
            self.TAPD_constant_af.setChecked(True)
            self.constant_af=True
        elif scenario['constant_af'] == 'False':
            self.TAPD_constant_af.setChecked(False)
            self.constant_af=False
        if scenario['add_atoms'] == 'True':
            self.TAPD_add_atoms.setChecked(True)
        elif scenario['add_atoms'] == 'False':
            self.TAPD_add_atoms.setChecked(False)
        if scenario['plot_log_scale'] == 'True':
            self.plot_log_scale.setChecked(True)
        elif scenario['plot_log_scale'] == 'False':
            self.plot_log_scale.setChecked(False)

        if scenario.get('add_buffer','False') == 'True':
            self.TAPD_add_buffer.setChecked(True)
            self.TAPD_buffer_in_plane_distribution.setCurrentText(scenario['buffer_in_plane_distribution'])
            if self.TAPD_buffer_in_plane_distribution.currentText() == 'completely random':
                self.TAPD_buffer_in_plane_completely_random.setText(scenario['buffer_in_plane_density'])
            elif self.TAPD_buffer_in_plane_distribution.currentText() == 'geometric':
                self.TAPD_buffer_in_plane_geometric_gamma.text().setText(scenario['buffer_in_plane_gamma'])
            elif self.TAPD_buffer_in_plane_distribution.currentText() == 'delta':
                self.TAPD_buffer_in_plane_delta_radius.text().setText(scenario['buffer_in_plane_radius'])
            elif self.TAPD_buffer_in_plane_distribution.currentText() == 'uniform':
                self.TAPD_buffer_in_plane_uniform_low.text().setText(scenario['buffer_in_plane_low'])
                self.TAPD_buffer_in_plane_uniform_high.text().setText(scenario['buffer_in_plane_high'])
            elif self.TAPD_buffer_in_plane_distribution.currentText() == 'buffer_in_plane_binomial':
                self.TAPD_buffer_in_plane_binomial_n.text().setText(scenario['buffer_in_plane_n'])
                self.TAPD_buffer_in_plane_binomial_p.text().setText(scenario['buffer_in_plane_p'])

            self.TAPD_buffer_out_of_plane_distribution.setCurrentText(scenario['buffer_out_of_plane_distribution'])
            self.TAPD_buffer_out_of_plane_low.setText(scenario['buffer_out_of_plane_low'])
            self.TAPD_buffer_out_of_plane_high.setText(scenario['buffer_out_of_plane_high'])

            self.TAPD_buffer_shift_X.setText(scenario['buffer_x_shift'])
            self.TAPD_buffer_shift_Y.setText(scenario['buffer_y_shift'])
            self.TAPD_buffer_shift_Z.setText(scenario['buffer_z_shift'])

            self.TAPD_buffer_atom.setText(scenario['buffer_atom'])
        else:
            self.TAPD_add_buffer.setChecked(False)
        self.reciprocalMapColormapCombo.setCurrentText(scenario['colormap'])
        self.TAPD_substrate_orientation.setCurrentText(scenario['sub_orientation'])
        self.TAPD_epilayer_orientation.setCurrentText(scenario['epi_orientation'])
        self.UPDATE_CAMERA_POSITION.emit(float(scenario['camera_horizontal_rotation']),\
            float(scenario['camera_vertical_rotation']),float(scenario['camera_zoom_level']))

    def prepare_TAPD(self):
        parameters = {}
        parameters['z_low'] = float(self.TAPD_buffer_out_of_plane_low.text())
        parameters['z_high'] = float(self.TAPD_buffer_out_of_plane_high.text())
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

        if self.TAPD_buffer_in_plane_distribution.currentText() == 'completely random':
            parameters['buffer_density'] = float(self.TAPD_buffer_in_plane_completely_random.text())
        elif self.TAPD_buffer_in_plane_distribution.currentText() == 'geometric':
            parameters['buffer_gamma'] = float(self.TAPD_buffer_in_plane_geometric_gamma.text())
        elif self.TAPD_buffer_in_plane_distribution.currentText() == 'delta':
            parameters['buffer_radius'] = float(self.TAPD_buffer_in_plane_delta_radius.text())
        elif self.TAPD_buffer_in_plane_distribution.currentText() == 'uniform':
            parameters['buffer_in_plane_low'] = float(self.TAPD_buffer_in_plane_uniform_low.text())
            parameters['buffer_in_plane_high'] = float(self.TAPD_buffer_in_plane_uniform_high.text())
        elif self.TAPD_buffer_in_plane_distribution.currentText() == 'binomial':
            parameters['buffer_n'] = float(self.TAPD_buffer_in_plane_binomial_n.text())
            parameters['buffer_p'] = float(self.TAPD_in_plane_binomial_p.text())

        self.TAPD_worker = TAPD_Simulation(float(self.TAPD_X_max.text()),\
                                          float(self.TAPD_Y_max.text()), \
                                          float(self.TAPD_Z_min.text()), \
                                          float(self.TAPD_Z_max.text()),\
                                          [float(self.TAPD_Shift_X.text()), float(self.TAPD_Shift_Y.text()), float(self.TAPD_Shift_Z.text())],\
                                          self.substrate_path, self.epilayer_path, \
                                          self.TAPD_distribution_function.currentText(),\
                                          self.TAPD_buffer_atom.text(),\
                                          self.TAPD_buffer_in_plane_distribution.currentText(),\
                                          self.TAPD_buffer_out_of_plane_distribution.currentText(),\
                                          [float(self.TAPD_buffer_shift_X.text()), float(self.TAPD_buffer_shift_Y.text()),float(self.TAPD_buffer_shift_Z.text())],\
                                          self.TAPD_substrate_orientation.currentText(),\
                                          self.TAPD_epilayer_orientation.currentText(),\
                                          self.TAPD_atoms.isChecked(),\
                                          self.TAPD_add_buffer.isChecked(),**parameters)
        self.thread = QtCore.QThread()
        self.TAPD_worker.moveToThread(self.thread)
        self.TAPD_worker.PROGRESS_ADVANCE.connect(self.progress)
        self.TAPD_worker.PROGRESS_END.connect(self.progress_reset)
        self.TAPD_worker.FINISHED.connect(self.thread.quit)
        self.TAPD_worker.FINISHED.connect(self.TAPD_FINISHED)
        self.TAPD_worker.UPDATE_LOG.connect(self.update_log)
        self.TAPD_worker.SEND_RESULTS.connect(self.get_TAPD_results)
        self.thread.started.connect(self.TAPD_worker.run)
        self.STOP_TAPD_WORKER.connect(self.TAPD_worker.stop)

    def get_TAPD_results(self, model):
        self.vor = model.vor
        self.structure_sub = model.substrate_structure 
        self.structure_epi = model.epilayer_structure
        self.substrate_sites = model.substrate_sites
        self.substrate_list = model.substrate_list
        self.buffer_sites = model.buffer_layer_sites
        self.buffer_list = model.buffer_layer_list
        self.epilayer_sites = model.epilayer_sites
        self.epilayer_list = model.epilayer_list
        self.epilayer_domain_area_list = model.epilayer_domain_area_list
        self.epilayer_domain_boundary_list = model.epilayer_domain_boundary_list
        self.epilayer_boundary_sites = model.epilayer_boundary_sites
        self.epilayer_domain = model.epilayer_domain
        if self.TAPD_add_substrate.isChecked():
            self.add_TAPD('substrate')
        if self.TAPD_add_epilayer.isChecked() and self.TAPD_add_boundary.isChecked():
            self.add_TAPD('boundary')
        elif self.TAPD_add_epilayer.isChecked():
            self.add_TAPD('epilayer')
        if self.TAPD_add_buffer.isChecked():
            self.add_TAPD('buffer')
        self.plot_size_distribution_button.setEnabled(True)
        self.plot_boundary_statistics_button.setEnabled(True)
        self.plot_boundary_button.setEnabled(True)
        self.plot_voronoi_button.setEnabled(True)
        try:
            self.TAPD_RESULTS.emit(model, self.TAPD_completely_random.text())
        except AttributeError:
            pass

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
        range_grid.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        lattice_constants_box = InfoBoard("Information",index)
        self.UPDATE_INOFRMATION_BOARD.connect(lattice_constants_box.update)
        shape_label = QtWidgets.QLabel("Shape")
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
        if index in self.deleted_tab_index:
            self.deleted_tab_index.remove(index)
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
                           self.real_space_specification_dict[index]['rotation'],self.AR, self.TAPD_constant_af.isChecked(), self.TAPD_add_atoms.isChecked(),self.useCUDA.isChecked())
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
            colorPicker = IndexedColorPicker(name,'#'+self.AR.loc[name].at['Color'],self.AR.loc[name].at['Normalized Radius'],index)
            colorPicker.COLOR_CHANGED.connect(self.update_colors)
            colorPicker.SIZE_CHANGED.connect(self.update_size)
            self.colorSheet[index][name] = '#'+self.AR.loc[name].at['Color']
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
                            self.AR, self.TAPD_constant_af.isChecked(), self.TAPD_add_atoms.isChecked(),self.useCUDA.isChecked())
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
        elif label=='boundary':
            self.structure_dict[index] = self.structure_epi
            self.TAPD[index] = self.epilayer_boundary_sites
        elif label=='epilayer':
            self.structure_dict[index] = self.structure_epi
            self.TAPD[index] = self.epilayer_sites
        elif label =='buffer':
            self.structure_dict[index] = None
            self.TAPD[index] = self.buffer_sites

        if not label == 'buffer':
            self.UPDATE_INOFRMATION_BOARD.emit(index,self.structure_dict[index].composition.reduced_formula,self.structure_dict[index].lattice.a,self.structure_dict[index].lattice.b,self.structure_dict[index].lattice.c,\
                            self.structure_dict[index].lattice.alpha,self.structure_dict[index].lattice.beta,self.structure_dict[index].lattice.gamma)
        self.update_log("TAPD "+label+str(index+1)+" loaded!")
        if label=='substrate':
            self.element_species[index] = set(re.compile('[a-zA-Z]{1,2}').match(str(site.specie)).group() for site in self.substrate_sites)
        elif label=='boundary':
            self.element_species[index] = set(re.compile('[a-zA-Z]{1,2}').match(str(site.specie)).group() for site in self.epilayer_boundary_sites)
        elif label=='epilayer':
            self.element_species[index] = set(re.compile('[a-zA-Z]{1,2}').match(str(site.specie)).group() for site in self.epilayer_sites)
        elif label=='buffer':
            self.element_species[index] = set(re.compile('[a-zA-Z]{1,2}').match(str(site.specie)).group() for site in self.buffer_sites)

        colorPalette = QtWidgets.QWidget()
        grid = QtWidgets.QVBoxLayout(colorPalette)
        self.colorSheet[index]={}
        for i,name in enumerate(self.element_species[index]):
            colorPicker = IndexedColorPicker(name,'#'+self.AR.loc[name].at['Color'],self.AR.loc[name].at['Normalized Radius'],index)
            colorPicker.COLOR_CHANGED.connect(self.update_colors)
            colorPicker.SIZE_CHANGED.connect(self.update_size)
            self.colorSheet[index][name] = '#'+self.AR.loc[name].at['Color']
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
                            self.AR, self.TAPD_constant_af.isChecked(), self.TAPD_add_atoms.isChecked(),self.useCUDA.isChecked())
        self.data_index_set.add(index)
        self.graph.change_fonts(self.fontList.currentFont().family(),self.fontSizeSlider.value())
        self.graph.change_shadow_quality(self.shadowQuality.currentIndex())
        self.sample_tab.widget(index).layout().itemAt(4).widget().setEnabled(True)
        self.sample_tab.widget(index).layout().itemAt(5).widget().setEnabled(True)
        self.update_log("Finished adding data for sample " + str(index+1))
        QtCore.QCoreApplication.processEvents()
        self.apply_reciprocal_range.setEnabled(True)
        self.gstart_calculation.setEnabled(True)

    def reload_TAPD(self, **kwargs):
        try:
            self.UPDATE_CAMERA_POSITION.emit(float(self.scenario_TAPD['camera_horizontal_rotation']),\
            float(self.scenario_TAPD['camera_vertical_rotation']),float(self.scenario_TAPD['camera_zoom_level']))
        except AttributeError:
            pass
        if kwargs.get('density',False):
            self.TAPD_completely_random.setText(kwargs['density'])
        for index in sorted(list(self.sample_index_set), reverse = True):
            tab_index = index - len([x for x in self.deleted_tab_index if x < index])
            self.delete_structure(tab_index)
        if self.substrate_path:
            if self.epilayer_path:
                self.prepare_TAPD()
                self.thread.start()
            else:
                self.raise_error('Please specify the epilayer!')
        else:
            self.raise_error('Please specify the substrate!')

    def reload_CIF(self, **kwargs):
        try:
            self.UPDATE_CAMERA_POSITION.emit(float(self.scenario_TAPD['camera_horizontal_rotation']),\
            float(self.scenario_TAPD['camera_vertical_rotation']),float(self.scenario_TAPD['camera_zoom_level']))
        except AttributeError:
            pass
        if kwargs.get('Z_min',False):
            self.sample_tab.widget(0).layout().itemAt(11).widget().set_head(kwargs['Z_min'])
        self.update_range(0)
        self.update_reciprocal_range()

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
        self.TAPD_Shift_Z.setText('6')
        self.TAPD_buffer_shift_X.setText('0')
        self.TAPD_buffer_shift_Y.setText('0')
        self.TAPD_buffer_shift_Z.setText('6')
        self.TAPD_distribution_function.setCurrentText('geometric')

    def change_buffer_in_plane_distribution(self,text):
        while self.buffer_in_plane_distribution_parameters_grid.itemAt(0):
            self.buffer_in_plane_distribution_parameters_grid.itemAt(0).widget().deleteLater()
            self.buffer_in_plane_distribution_parameters_grid.removeItem(self.buffer_in_plane_distribution_parameters_grid.itemAt(0))
        if text == 'completely random':
            self.TAPD_buffer_in_plane_completely_random_label = QtWidgets.QLabel('Density')
            self.TAPD_buffer_in_plane_completely_random = QtWidgets.QLineEdit('0.1')
            self.buffer_in_plane_distribution_parameters_grid.addWidget(self.TAPD_buffer_in_plane_completely_random_label)
            self.buffer_in_plane_distribution_parameters_grid.addWidget(self.TAPD_buffer_in_plane_completely_random)
        elif text == 'geometric':
            self.TAPD_buffer_in_plane_geometric_gamma_label = QtWidgets.QLabel('Gamma')
            self.TAPD_buffer_in_plane_geometric_gamma = QtWidgets.QLineEdit('0.1')
            self.buffer_in_plane_distribution_parameters_grid.addWidget(self.TAPD_buffer_in_plane_geometric_gamma_label)
            self.buffer_in_plane_distribution_parameters_grid.addWidget(self.TAPD_buffer_in_plane_geometric_gamma)
        elif text == 'binomial':
            self.TAPD_buffer_in_plane_binomial_n_label = QtWidgets.QLabel('n')
            self.TAPD_buffer_in_plane_binomial_n = QtWidgets.QLineEdit('20')
            self.TAPD_buffer_in_plane_binomial_p_label = QtWidgets.QLabel('p')
            self.TAPD_buffer_in_plane_binomial_p = QtWidgets.QLineEdit('0.5')
            self.buffer_in_plane_distribution_parameters_grid.addWidget(self.TAPD_buffer_in_plane_binomial_n_label)
            self.buffer_in_plane_distribution_parameters_grid.addWidget(self.TAPD_buffer_in_plane_binomial_n)
            self.buffer_in_plane_distribution_parameters_grid.addWidget(self.TAPD_buffer_in_plane_binomial_p_label)
            self.buffer_in_plane_distribution_parameters_grid.addWidget(self.TAPD_buffer_in_plane_binomial_p)
        elif text == 'uniform':
            self.TAPD_buffer_in_plane_uniform_low_label = QtWidgets.QLabel('low')
            self.TAPD_buffer_in_plane_uniform_low = QtWidgets.QLineEdit('5')
            self.TAPD_buffer_in_plane_uniform_high_label = QtWidgets.QLabel('high')
            self.TAPD_buffer_in_plane_uniform_high = QtWidgets.QLineEdit('15')
            self.buffer_in_plane_distribution_parameters_grid.addWidget(self.TAPD_buffer_in_plane_uniform_low_label)
            self.buffer_in_plane_distribution_parameters_grid.addWidget(self.TAPD_buffer_in_plane_uniform_low)
            self.buffer_in_plane_distribution_parameters_grid.addWidget(self.TAPD_buffer_in_plane_uniform_high_label)
            self.buffer_in_plane_distribution_parameters_grid.addWidget(self.TAPD_buffer_in_plane_uniform_high)
        elif text == 'delta':
            self.TAPD_buffer_in_plane_delta_radius_label = QtWidgets.QLabel('radius')
            self.TAPD_buffer_in_plane_delta_radius = QtWidgets.QLineEdit('10')
            self.buffer_in_plane_distribution_parameters_grid.addWidget(self.TAPD_buffer_in_plane_delta_radius_label)
            self.buffer_in_plane_distribution_parameters_grid.addWidget(self.TAPD_buffer_in_plane_delta_radius)

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

    def plot_distribution(self,**kwargs):
        data = np.array(list(np.sqrt(x*2)/10 for x in self.epilayer_domain_area_list))
        if self.currentDestination:
            if kwargs.get('save_as_file',False):
                output = open(kwargs['destination']+'distribution'+".txt",mode='w')
            else:
                output = open(self.currentDestination+'/'+'distribution'+".txt",mode='w')
            output.write("\n".join(str(area) for area in data))
            output.close()
        figure = plt.figure()
        ax = figure.add_subplot(111)
        ax.hist(data,color = 'red', edgecolor='black', density=True, bins=100)
        ax.axvline(data.mean(), linestyle='dashed',linewidth=2,color='k')
        ax.set_xlabel('Domain diameter (nm)',fontsize=20)
        ax.set_ylabel('Probability Density',fontsize=20)
        ax.tick_params(labelsize=20)
        x_min,x_max = plt.xlim()
        y_min,y_max = plt.ylim()
        ax.set_title('Domain size distribution\n(Mean: {:.2f} nm, Std. Deviation: {:.2f} nm)'.format(data.mean(), data.std()),fontsize=20)
        plt.tight_layout()
        if kwargs.get('save_as_file',False):
            figure.savefig(kwargs['destination']+'distribution.tif')
            figure.savefig(kwargs['destination']+'distribution.svg')
        else:
            self.plot_distribution_window = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(self.plot_distribution_window)
            canvas = FigureCanvas(figure)
            toolbar = NavigationToolbar(canvas,self.plot_distribution_window)
            canvas.draw()
            layout.addWidget(toolbar)
            layout.addWidget(canvas)
            self.plot_distribution_window.setWindowTitle("Domain size distribution")
            self.plot_distribution_window.setVisible(True)
            self.plot_distribution_window.show()
    
    def plot_boundary(self,**kwargs):
        fontsize = 20
        point_color = 'red'
        point_size = 5
        x_list = []
        y_list = []
        for boundary in self.epilayer_domain_boundary_list:
            try:
                for vertex_index in boundary.vertices:
                    x_list.append(boundary.points[vertex_index][0])
                    y_list.append(boundary.points[vertex_index][1])
                for vertex_index in boundary.coplanar:
                    if not (boundary.points[vertex_index[0]][0] in x_list and boundary.points[vertex_index[0]][1] in y_list):
                        x_list.append(boundary.points[vertex_index[0]][0])
                        y_list.append(boundary.points[vertex_index[0]][1])

            except AttributeError:
                for point in boundary:
                    x_list.append(point[0])
                    y_list.append(point[1])

        figure = plt.figure()
        ax = figure.add_subplot(111)
        ax.set_aspect('equal')
        voronoi_plot_2d(self.vor,ax,show_points=False, show_vertices=False)
        ax.plot(x_list, y_list, '.', markersize=point_size, markerfacecolor=point_color, markeredgecolor=point_color)
        ax.set_xlabel('x (\u212B)',fontsize=fontsize)
        ax.set_ylabel('y (\u212B)',fontsize=fontsize)
        ax.tick_params(labelsize=fontsize)
        plt.tight_layout()
        if kwargs.get('save_as_file',False):
            figure.savefig(kwargs['destination']+'boundary.tif')
            figure.savefig(kwargs['destination']+'boundary.svg')
        else:
            self.plot_boundary_window = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(self.plot_boundary_window)
            canvas = FigureCanvas(figure)
            toolbar = NavigationToolbar(canvas,self.plot_boundary_window)
            canvas.draw()
            layout.addWidget(toolbar)
            layout.addWidget(canvas)
            self.plot_boundary_window.setWindowTitle("Domain boundary")
            self.plot_boundary_window.show()

    def plot_boundary_statistics(self, **kwargs):
        fontsize = 20
        fontname = 'Arial'
        x_list, y_list, xy_list = [], [], []

        for boundary in self.epilayer_domain_boundary_list:
            try:
                for vertex_index in boundary.vertices:
                    x_list.append(boundary.points[vertex_index][0])
                    y_list.append(boundary.points[vertex_index][1])
                    xy_list.append(boundary.points[vertex_index])
                for vertex_index in boundary.coplanar:
                    if not (boundary.points[vertex_index[0]][0] in x_list and boundary.points[vertex_index[0]][1] in y_list):
                        x_list.append(boundary.points[vertex_index[0]][0])
                        y_list.append(boundary.points[vertex_index[0]][1])
                        xy_list.append(boundary.points[vertex_index[0]])

            except AttributeError:
                for point in boundary:
                    x_list.append(point[0])
                    y_list.append(point[1])
                    xy_list.append(point)

        xy_tree= cKDTree(np.array(xy_list))
        lattice_constant = max(self.structure_epi.lattice.a,self.structure_epi.lattice.b)
        dict_xy = xy_tree.sparse_distance_matrix(xy_tree,lattice_constant*1.99999,output_type='dict')
        xy_distance = []
        r_dic = {}
        for key,value in dict_xy.items():
            if value > lattice_constant*1.00001:
                r = value/lattice_constant
                x = (xy_list[key[0]][0] - xy_list[key[1]][0])/lattice_constant
                y = (xy_list[key[0]][1] - xy_list[key[1]][1])/lattice_constant
                angle = np.arcsin(np.abs(y/r)) + np.where(x>0,np.where(y>0,0,270),np.where(y>0,90,180))
                xy_distance.append([x, y, r, angle])
                r_round = np.around(r,5)
                if r_round in r_dic:
                    r_dic[r_round] += 1
                else:
                    r_dic[r_round] = 1
        if self.currentDestination:
            if kwargs.get('save_as_file',False):
                output1 = open(kwargs['destination']+'boundary_statistics'+".txt",mode='w')
                output2 = open(kwargs['destination']+'boundary_statistics_1d'+".txt",mode='w')
            else:
                output1 = open(self.currentDestination+'/'+'boundary_statistics'+".txt",mode='w')
                output2 = open(self.currentDestination+'/'+'boundary_statistics_1d'+".txt",mode='w')
            output1.write("\n".join('\t'.join(str(d) for d in distance) for distance in np.array(xy_distance)))
            output1.close()
            output2.write("\n".join('\t'.join([str(k),str(r_dic[k])]) for k in r_dic))
            output2.close()
        figure = plt.figure()
        ax = figure.add_subplot(111)
        x_min, x_max = np.amin(np.array(xy_distance)[:,0]), np.amax(np.array(xy_distance)[:,0])
        y_min, y_max = np.amin(np.array(xy_distance)[:,1]), np.amax(np.array(xy_distance)[:,1])
        H, x_edges, y_edges = np.histogram2d(np.array(xy_distance)[:,0],np.array(xy_distance)[:,1],bins=500)
        H[H == 0] = 0.1
        ax.imshow(H,cmap='hot',aspect='equal', origin = 'lower', interpolation='gaussian',\
            norm=mcolors.LogNorm(0.1,np.amax(np.amax(H))), extent=[x_min, x_max, y_min, y_max])
        ax.set_xlabel('\u0394x/a',fontsize=fontsize, fontname=fontname)
        ax.set_ylabel('\u0394y/a',fontsize=fontsize, fontname=fontname)
        ax.set_xticks([-1.5,-1,-0.5,0,0.5,1,1.5])
        ax.set_yticks([-1.5,-1,-0.5,0,0.5,1,1.5])
        ax.set_frame_on(False)
        ax.set_xticklabels(ax.get_xticks(),fontsize=fontsize, fontname=fontname)
        ax.set_yticklabels(ax.get_yticks(),fontsize=fontsize, fontname=fontname)
        plt.tight_layout()
        if kwargs.get('save_as_file',False):
            figure.savefig(kwargs['destination']+'boundary_statistics.tif')
            figure.savefig(kwargs['destination']+'boundary_statistics.svg')
        else:
            self.plot_boundary_statistics_window = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(self.plot_boundary_statistics_window)
            canvas = FigureCanvas(figure)
            toolbar = NavigationToolbar(canvas,self.plot_boundary_statistics_window)
            canvas.draw()
            layout.addWidget(toolbar)
            layout.addWidget(canvas)
            self.plot_boundary_statistics_window.setWindowTitle("Domain boundary statistics")
            self.plot_boundary_statistics_window.show()

    def plot_voronoi(self, **kwargs):
        x_max = kwargs.get('X_max',float(self.TAPD_X_max.text()))
        y_max = kwargs.get('Y_max',float(self.TAPD_Y_max.text()))
        rectangle = Polygon([(-x_max,-y_max),(-x_max,y_max),(x_max,y_max),(x_max,-y_max)])
        figure = plt.figure()
        ax = figure.add_subplot(111)
        ax.set_aspect('equal')
        ax.scatter(np.array(self.substrate_list)[:,0],np.array(self.substrate_list)[:,1],5,'lightblue')
        ax.scatter(np.array(self.epilayer_list)[:,0],np.array(self.epilayer_list)[:,1],5,'pink')
        ax.set_xlabel('x (\u212B)' ,fontsize=20)
        ax.set_ylabel('y (\u212B)',fontsize=20)
        ax.set_title('2D translational antiphase boundary model\nMoS2/sapphire',fontsize=20)
        ax.tick_params(labelsize=20)
        point_color = kwargs.get('point_color', 'orange')
        point_size = kwargs.get('point_size', 20)
        vertex_color = kwargs.get('vertex_color', 'green')
        vertex_size  = kwargs.get('vertex_size', 3)
        plot_domains = kwargs.get('plot_domains', False)

        if kwargs.get('show_points', True):
            ax.plot(self.vor.points[:,0], self.vor.points[:,1], '.', markersize=point_size, markerfacecolor=point_color, markeredgecolor=point_color)
        if kwargs.get('show_vertices', False):
            ax.plot(self.vor.vertices[:,0], self.vor.vertices[:,1], 'o', markersize=vertex_size, markerfacecolor=vertex_color)

        line_colors = kwargs.get('line_colors', 'k')
        line_width = kwargs.get('line_width', 1.0)
        line_alpha = kwargs.get('line_alpha', 1.0)

        line_segments = []
        for simplex in self.vor.ridge_vertices:
            simplex = np.asarray(simplex)
            if np.all(simplex >= 0):
                intersection = rectangle.intersection(LineString(self.vor.vertices[simplex]))
                if intersection:
                    line_segments.append(list(intersection.coords))

        lc = LineCollection(line_segments,colors=line_colors,lw=line_width,linestyle='solid')
        lc.set_alpha(line_alpha)
        ax.add_collection(lc)
        ptp_bound = self.vor.points.ptp(axis=0)

        line_segments = []
        center = self.vor.points.mean(axis=0)
        for pointidx, simplex in zip(self.vor.ridge_points, self.vor.ridge_vertices):
            simplex = np.asarray(simplex)
            if np.any(simplex < 0):
                i = simplex[simplex >= 0][0]
                t = self.vor.points[pointidx[1]] - self.vor.points[pointidx[0]]
                t /= np.linalg.norm(t)
                n = np.array([-t[1], t[0]])
                midpoint = self.vor.points[pointidx].mean(axis=0)
                direction = np.sign(np.dot(midpoint - center, n)) * n
                far_point = self.vor.vertices[i] + direction * ptp_bound.max()
                intersection = rectangle.intersection(LineString([(self.vor.vertices[i, 0], self.vor.vertices[i, 1]),(far_point[0], far_point[1])]))
                if intersection:
                    line_segments.append(list(intersection.coords))

        lc = LineCollection(line_segments,colors=line_colors,lw=line_width,linestyle='solid')
        lc.set_alpha(line_alpha)
        ax.add_collection(lc)

        if plot_domains:
            for polygon in list(self.epilayer_domain):
                x1=[]
                y1=[]
                try:
                    for cx,cy in polygon.exterior.coords:
                        x1.append(cx)
                        y1.append(cy)
                    ax.plot(x1,y1,color=np.random.rand(3,), marker=',', linestyle='-')
                except:
                    try:
                        for subpolygon in polygon:
                            x1=[]
                            y1=[]
                            for cx,cy in subpolygon.exterior.coords:
                                x1.append(cx)
                                y1.append(cy)
                            ax.plot(x1,y1,color=np.random.rand(3,), marker=',', linestyle='-')
                    except: pass

        ptp_bound = self.vor.points.ptp(axis=0)
        ax.set_xlim(-x_max,x_max)
        ax.set_ylim(-y_max,y_max)
        plt.tight_layout()
        if kwargs.get('save_as_file',False):
            figure.set_size_inches(20,20)
            figure.savefig(kwargs['destination']+'voronoi.tif')
            figure.savefig(kwargs['destination']+'voronoi.svg')
        else:
            self.plot_voronoi_window = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(self.plot_voronoi_window)
            canvas = FigureCanvas(figure)
            toolbar = NavigationToolbar(canvas,self.plot_voronoi_window)
            canvas.draw()
            layout.addWidget(toolbar)
            layout.addWidget(canvas)
            self.plot_voronoi_window.setWindowTitle("2D Contour")
            self.plot_voronoi_window.show()

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
        self.scene().activeCamera().setMaxZoomLevel(10000)

    def add_data(self,index,data,colorSheet,range,z_range,shape,offset,rotation,AR,constant_af=False,add_series=True,useCUDA=True):
        self.colors_dict = colorSheet
        self.constant_af = constant_af
        self.useCUDA = useCUDA
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
                self.atoms_dict[index][tuple(list(coord))] = self.elements_dict[index][i]
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
                ScatterSeries.setColorStyle(QtDataVisualization.Q3DTheme.ColorStyle.ColorStyleUniform)
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

    def update_elapsed_time(self,time):
        self.LOG_MESSAGE.emit('Time elapsed is: {:10.5f} s'.format(time))

    def prepare(self,Kx,Ky,Kz,AFF,constant_af):
        atoms_list = self.flatten(self.atoms_dict)
        self.diffraction_worker = DiffractionPattern(Kx,Ky,Kz,AFF,atoms_list, constant_af,self.useCUDA)
        self.diffraction_worker.ERROR.connect(self.raise_error)
        self.diffraction_worker.PROGRESS_ADVANCE.connect(self.PROGRESS_ADVANCE)
        self.diffraction_worker.PROGRESS_END.connect(self.PROGRESS_END)
        self.diffraction_worker.ACCOMPLISHED.connect(self.CALCULATION_FINISHED)
        self.diffraction_worker.ABORTED.connect(self.process_aborted)
        self.diffraction_worker.INSUFFICIENT_MEMORY.connect(self.stop)
        self.diffraction_worker.ELAPSED_TIME.connect(self.update_elapsed_time)
        self.diffraction_worker.UPDATE_LOG.connect(self.LOG_MESSAGE)

        self.thread = QtCore.QThread()
        self.diffraction_worker.moveToThread(self.thread)
        self.diffraction_worker.PROGRESS_END.connect(self.thread.quit)
        self.thread.started.connect(self.diffraction_worker.run)
        self.STOP_WORKER.connect(self.diffraction_worker.stop)

    def calculate(self,Kx,Ky,Kz,AFF,constant_af):
        self.prepare(Kx,Ky,Kz,AFF,constant_af)
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

    def update_gpu(self,status):
        if status == 2:
            self.useCUDA = True
        elif status == 0:
            self.useCUDA = False

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
            self.activeTheme().setLabelTextColor(QtCore.Qt.GlobalColor.transparent)

    def update_view_direction(self,preset):
        if preset == 1:
            p = QtDataVisualization.Q3DCamera.CameraPreset.CameraPresetFront
        elif preset == 2:
            p = QtDataVisualization.Q3DCamera.CameraPreset.CameraPresetFrontHigh
        elif preset == 4:
            p = QtDataVisualization.Q3DCamera.CameraPreset.CameraPresetLeft
        elif preset == 7:
            p = QtDataVisualization.Q3DCamera.CameraPreset.CameraPresetRight
        elif preset == 10:
            p = QtDataVisualization.Q3DCamera.CameraPreset.CameraPresetBehind
        elif preset == 16:
            p = QtDataVisualization.Q3DCamera.CameraPreset.CameraPresetDirectlyAbove
        else:
            p = 1
        self.scene().activeCamera().setCameraPreset(p)

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
        if quality == 0:
            quality = QtDataVisualization.QAbstract3DGraph.ShadowQuality.ShadowQualityNone
        elif quality == 1:
            quality = QtDataVisualization.QAbstract3DGraph.ShadowQuality.ShadowQualityLow
        elif quality == 2:
            quality = QtDataVisualization.QAbstract3DGraph.ShadowQuality.ShadowQualityMedium
        elif quality == 3:
            quality = QtDataVisualization.QAbstract3DGraph.ShadowQuality.ShadowQualityHigh
        elif quality == 4:
            quality = QtDataVisualization.QAbstract3DGraph.ShadowQuality.ShadowQualitySoftLow
        elif quality == 5:
            quality = QtDataVisualization.QAbstract3DGraph.ShadowQuality.ShadowQualitySoftMedium
        elif quality == 6:
            quality = QtDataVisualization.QAbstract3DGraph.ShadowQuality.ShadowQualitySoftHigh
        else:
            quality = QtDataVisualization.QAbstract3DGraph.ShadowQuality.ShadowQualityNone
        self.setShadowQuality(quality)

    def save_scene(self, **kwargs):
        if kwargs.get('save_as_file',False):
            imageFileName1 = [kwargs['destination'] + 'lattice.bmp']
            imageFileName2 = [kwargs['destination'] + 'lattice_5x5_zoomed.bmp']
        else:
            imageFileName1 = QtWidgets.QFileDialog.getSaveFileName(None,"choose save file name",os.path.join(self.dirname,"lattice.bmp"),\
                                                                    "BMP (*.bmp);;JPEG (*.jpeg);;PNG(*.png)")
            imageFileName2 = QtWidgets.QFileDialog.getSaveFileName(None,"choose save file name",os.path.join(self.dirname,"lattice_5x5_zoomed.bmp"),\
                                                                    "BMP (*.bmp);;JPEG (*.jpeg);;PNG(*.png)")
        if imageFileName1[0] and imageFileName2[0]:
            capture = self.renderToImage(0,QtCore.QSize(3000,3000))
            capture.save(imageFileName1[0], quality=100)
            if kwargs.get('save_zoomed_scene',True):
                self.scene().activeCamera().setCameraPosition(self.scene().activeCamera().xRotation(),\
                    self.scene().activeCamera().yRotation(),self.scene().activeCamera().zoomLevel()*5)
                capture = self.renderToImage(0,QtCore.QSize(3000,3000))
                capture.save(imageFileName2[0], quality=100)

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

def test():
    app = QtWidgets.QApplication(sys.argv)
    simulation = Window()
    simulation.main()
    sys.exit(app.exec_())

if __name__ == '__main__':
    test()
