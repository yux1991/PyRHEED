from my_widgets import LabelSlider
from process import Image, FitFunctions, FitBroadening
from process_monitor import Monitor
from PyQt5 import QtCore, QtWidgets, QtGui, QtChart
from sys import getsizeof
from sklearn.mixture import BayesianGaussianMixture
import configparser
import generate_report
import glob
import manual_fit
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.colors as mcolors
import numpy as np
import numbers
import os
import time
import sys
import profile_chart
import bar_chart
import pandas
from scipy.stats import rv_discrete

class Window(QtCore.QObject):

    #Public Signals
    STATUS_REQUESTED = QtCore.pyqtSignal()
    PROGRESS_ADVANCE = QtCore.pyqtSignal(int,int,int)
    PROGRESS_END = QtCore.pyqtSignal()
    CONNECT_TO_CANVAS = QtCore.pyqtSignal()
    DRAW_LINE_REQUESTED = QtCore.pyqtSignal(QtCore.QPointF,QtCore.QPointF,bool)
    DRAW_RECT_REQUESTED = QtCore.pyqtSignal(QtCore.QPointF,QtCore.QPointF,float,bool)
    COLOR = ['magenta','cyan','darkCyan','darkMagenta','darkRed','darkBlue','darkGray','green','darkGreen','darkYellow','yellow','black']
    FONTS_CHANGED = QtCore.pyqtSignal(str,int)
    STOP_WORKER = QtCore.pyqtSignal()
    FEED_BACK_TO_FIT_WORKER = QtCore.pyqtSignal(list,tuple)

    def __init__(self):
        super(Window,self).__init__()
        self.analysisRegion = [0,0,0,0,0]
        self.config = configparser.ConfigParser()
        self.config.read('./configuration.ini')
        self.image_worker = Image()
        self.fit_worker = FitFunctions()

        self.covars = np.array([[[.1, .0], [.0, .1]],
                                [[.1, .0], [.0, .1]],
                                [[.1, .0], [.0, .1]],
                                [[.1, .0], [.0, .1]]])
        self.samples = np.array([1500, 1500, 1500, 1500])
        self.means = np.array([[-1.0, -.70],
                               [.0, .0],
                               [.5, 1.30],
                               [1.0, .70]])
        self.fit_colors = list(mcolors.XKCD_COLORS.values())[20:]

    def refresh(self,config):
            self.config = config
            try:
                self.distributionChart.refresh(config)
                self.costChart.refresh(config)
            except:
                pass

    def main(self,path='./'):
        self.startIndex = "0"
        self.endIndex = "3"
        self.range = "5"
        self.nsamp = '10000'
        self.nfeature = '2'
        self.ncomp = '4'
        self.tol = '0.001'
        self.reg_covar = '1e-6'
        self.max_itr = '1500'
        self.n_init = '1'
        self.wc_prior = '1000'
        self.mean_precision_prior = '0.8'
        self.mean_prior = ''
        self.dof = ''
        self.rs = '2'
        self.vb = '0'
        self.vb_interval = '10'
        self.FTol = '1e-6'
        self.XTol = '1e-4'
        self.GTol = '1e-6'
        self.numberOfSteps = "20"
        self.defaultFileName = "GMM Fit"
        self.cost_series_X = [1]
        self.cost_series_Y = [1]
        self.file_has_been_created = False
        self.path = os.path.dirname(path)
        self.extension = os.path.splitext(path)[1]
        self.currentSource = self.path
        self.currentDestination = self.currentSource
        self.Dialog = QtWidgets.QWidget()
        self.Grid = QtWidgets.QGridLayout(self.Dialog)
        self.LeftFrame = QtWidgets.QFrame()
        self.RightFrame = QtWidgets.QFrame()
        self.LeftGrid = QtWidgets.QGridLayout(self.LeftFrame)
        self.RightGrid = QtWidgets.QGridLayout(self.RightFrame)
        self.hSplitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.hSplitter.addWidget(self.RightFrame)
        self.hSplitter.addWidget(self.LeftFrame)
        self.hSplitter.setStretchFactor(0,1)
        self.hSplitter.setStretchFactor(1,1)
        self.hSplitter.setCollapsible(0,False)
        self.hSplitter.setCollapsible(1,False)
        self.leftScroll = QtWidgets.QScrollArea(self.hSplitter)
        self.chooseSource = QtWidgets.QGroupBox("Input")
        self.chooseSource.setStyleSheet('QGroupBox::title {color:blue;}')
        self.sourceGrid = QtWidgets.QGridLayout(self.chooseSource)
        self.sourceGrid.setAlignment(QtCore.Qt.AlignTop)
        self.chooseSourceLabel = QtWidgets.QLabel("The input data directory is:\n"+self.currentSource)
        self.chooseSourceLabel.setWordWrap(True)
        self.chooseSourceButton = QtWidgets.QPushButton("Browse...")
        self.chooseSourceButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
        self.chooseSourceButton.clicked.connect(self.choose_source)
        self.loadButton = QtWidgets.QPushButton("Load")
        self.loadButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
        self.loadButton.clicked.connect(self.load_data)
        self.loadButton.setEnabled(False)
        self.sourceGrid.addWidget(self.chooseSourceLabel,0,0,2,1)
        self.sourceGrid.addWidget(self.chooseSourceButton,0,1,1,1)
        self.sourceGrid.addWidget(self.loadButton,1,1,1,1)
        self.chooseDestination = QtWidgets.QGroupBox("Output")
        self.chooseDestination.setStyleSheet('QGroupBox::title {color:blue;}')
        self.destinationGrid = QtWidgets.QGridLayout(self.chooseDestination)
        self.chooseDestinationLabel = QtWidgets.QLabel("The output directory is:\n"+self.currentSource)
        self.destinationNameLabel = QtWidgets.QLabel("The file name is:")
        self.destinationNameEdit = QtWidgets.QLineEdit(self.defaultFileName)
        self.fileTypeLabel = QtWidgets.QLabel("The file format is:")
        self.fileType = QtWidgets.QComboBox()
        self.fileType.addItem(".txt",".txt")
        self.fileType.addItem(".xlsx",".xlsx")
        self.chooseDestinationButton = QtWidgets.QPushButton("Browse...")
        self.chooseDestinationButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
        self.chooseDestinationButton.clicked.connect(self.choose_destination)
        self.saveResultLabel = QtWidgets.QLabel("Save Results?")
        self.saveResult = QtWidgets.QCheckBox()
        self.saveResult.setChecked(False)
        self.destinationGrid.addWidget(self.chooseDestinationLabel,0,0)
        self.destinationGrid.addWidget(self.chooseDestinationButton,0,1)
        self.destinationGrid.addWidget(self.destinationNameLabel,1,0)
        self.destinationGrid.addWidget(self.destinationNameEdit,1,1)
        self.destinationGrid.addWidget(self.fileTypeLabel,2,0)
        self.destinationGrid.addWidget(self.fileType,2,1)
        self.destinationGrid.addWidget(self.saveResultLabel,3,0)
        self.destinationGrid.addWidget(self.saveResult,3,1)
        self.destinationGrid.setAlignment(self.chooseDestinationButton,QtCore.Qt.AlignRight)

        self.appearance = QtWidgets.QGroupBox("Appearance")
        self.appearance.setMaximumHeight(100)
        self.appearance.setStyleSheet('QGroupBox::title {color:blue;}')
        self.appearanceGrid = QtWidgets.QGridLayout(self.appearance)
        self.fontListLabel = QtWidgets.QLabel("Change Font")
        self.fontList = QtWidgets.QFontComboBox()
        self.fontList.setCurrentFont(QtGui.QFont("Arial"))
        self.fontList.currentFontChanged.connect(self.refresh_font_name)
        self.fontSizeLabel = QtWidgets.QLabel("Adjust Font Size ({})".format(12))
        self.fontSizeLabel.setFixedWidth(160)
        self.fontSizeSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.fontSizeSlider.setMinimum(1)
        self.fontSizeSlider.setMaximum(100)
        self.fontSizeSlider.setValue(12)
        self.fontSizeSlider.valueChanged.connect(self.refresh_font_size)
        self.appearanceGrid.addWidget(self.fontListLabel,0,0)
        self.appearanceGrid.addWidget(self.fontList,0,1)
        self.appearanceGrid.addWidget(self.fontSizeLabel,1,0)
        self.appearanceGrid.addWidget(self.fontSizeSlider,1,1)

        self.sampleOptions = QtWidgets.QGroupBox("Sample")
        self.sampleOptions.setStyleSheet('QGroupBox::title {color:blue;}')
        self.sampleOptionsGrid = QtWidgets.QGridLayout(self.sampleOptions)
        self.numberOfSamplesLabel = QtWidgets.QLabel("Number of Samples")
        self.numberOfSamplesEdit = QtWidgets.QLineEdit(self.nsamp)
        self.drawSampleButton = QtWidgets.QPushButton("Draw")
        self.drawSampleButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
        self.drawSampleButton.clicked.connect(self.draw_sample)
        self.drawSampleButton.setEnabled(False)
        self.sampleOptionsGrid.addWidget(self.numberOfSamplesLabel,0,0,1,2)
        self.sampleOptionsGrid.addWidget(self.numberOfSamplesEdit,0,2,1,4)
        self.sampleOptionsGrid.addWidget(self.drawSampleButton,1,0,1,6)

        self.fitOptions = QtWidgets.QGroupBox("Parameters")
        self.fitOptions.setStyleSheet('QGroupBox::title {color:blue;}')
        self.fitOptionsGrid = QtWidgets.QGridLayout(self.fitOptions)
        self.numberOfFeaturesLabel = QtWidgets.QLabel("Number of Features")
        self.numberOfFeaturesEdit = QtWidgets.QLineEdit(self.nfeature)
        self.fitOptionsGrid.addWidget(self.numberOfFeaturesLabel,10,0,1,2)
        self.fitOptionsGrid.addWidget(self.numberOfFeaturesEdit,10,2,1,4)

        self.numberOfComponentsLabel = QtWidgets.QLabel("Number of Components")
        self.numberOfComponentsEdit = QtWidgets.QLineEdit(self.ncomp)
        self.fitOptionsGrid.addWidget(self.numberOfComponentsLabel,20,0,1,2)
        self.fitOptionsGrid.addWidget(self.numberOfComponentsEdit,20,2,1,4)

        self.tolLabel = QtWidgets.QLabel("Convergence Threshold")
        self.tolEdit = QtWidgets.QLineEdit(self.tol)
        self.fitOptionsGrid.addWidget(self.tolLabel,30,0,1,2)
        self.fitOptionsGrid.addWidget(self.tolEdit,30,2,1,4)

        self.regCovarLabel = QtWidgets.QLabel("Covariance Reg.")
        self.regCovarEdit = QtWidgets.QLineEdit(self.reg_covar)
        self.fitOptionsGrid.addWidget(self.regCovarLabel,40,0,1,2)
        self.fitOptionsGrid.addWidget(self.regCovarEdit,40,2,1,4)

        self.maxItrLabel = QtWidgets.QLabel("EM Iterations")
        self.maxItrEdit = QtWidgets.QLineEdit(self.max_itr)
        self.fitOptionsGrid.addWidget(self.maxItrLabel,50,0,1,2)
        self.fitOptionsGrid.addWidget(self.maxItrEdit,50,2,1,4)

        self.nInitLabel = QtWidgets.QLabel("Number of Initializations")
        self.nInitEdit = QtWidgets.QLineEdit(self.n_init)
        self.fitOptionsGrid.addWidget(self.nInitLabel,60,0,1,2)
        self.fitOptionsGrid.addWidget(self.nInitEdit,60,2,1,4)

        self.covarianceType = QtWidgets.QLabel("Covariance Type")
        self.covarianceType.setFixedWidth(160)
        self.covarianceTypeCombo = QtWidgets.QComboBox()
        for types in ('full','tied','diag','spherical'):
            self.covarianceTypeCombo.addItem(types,types)
        self.fitOptionsGrid.addWidget(self.covarianceType,70,0,1,2)
        self.fitOptionsGrid.addWidget(self.covarianceTypeCombo,70,2,1,4)

        self.initMethodType = QtWidgets.QLabel("Initialization Method")
        self.initMethodType.setFixedWidth(160)
        self.initMethodTypeCombo = QtWidgets.QComboBox()
        for types in ('random','kmeans'):
            self.initMethodTypeCombo.addItem(types,types)
        self.fitOptionsGrid.addWidget(self.initMethodType,75,0,1,2)
        self.fitOptionsGrid.addWidget(self.initMethodTypeCombo,75,2,1,4)

        self.wcPriorType = QtWidgets.QLabel("Weight Prior Type")
        self.wcPriorType.setFixedWidth(160)
        self.wcPriorTypeCombo = QtWidgets.QComboBox()
        for types in ('dirichlet_process','dirichlet_distribution'):
            self.wcPriorTypeCombo.addItem(types,types)
        self.fitOptionsGrid.addWidget(self.wcPriorType,80,0,1,2)
        self.fitOptionsGrid.addWidget(self.wcPriorTypeCombo,80,2,1,4)

        self.wcPriorLabel = QtWidgets.QLabel("Weight Prior")
        self.wcPriorCheck = QtWidgets.QCheckBox()
        self.wcPriorCheck.stateChanged.connect(self.wc_prior_check_changed)
        self.wcPriorEdit = QtWidgets.QLineEdit(self.wc_prior)
        if not self.wc_prior:
            self.wcPriorCheck.setChecked(False)
            self.wcPriorEdit.setEnabled(False)
        else:
            self.wcPriorCheck.setChecked(True)
        self.fitOptionsGrid.addWidget(self.wcPriorLabel,90,0,1,2)
        self.fitOptionsGrid.addWidget(self.wcPriorCheck,90,2,1,1)
        self.fitOptionsGrid.addWidget(self.wcPriorEdit,90,3,1,3)

        self.meanPrecPriorLabel = QtWidgets.QLabel("Mean Precision Prior")
        self.meanPrecPriorCheck = QtWidgets.QCheckBox()
        self.meanPrecPriorCheck.stateChanged.connect(self.mean_precision_prior_check_changed)
        self.meanPrecPriorEdit = QtWidgets.QLineEdit(self.mean_precision_prior)
        if not self.mean_precision_prior:
            self.meanPrecPriorCheck.setChecked(False)
            self.meanPrecPriorEdit.setEnabled(False)
        else:
            self.meanPrecPriorCheck.setChecked(True)
        self.fitOptionsGrid.addWidget(self.meanPrecPriorLabel,100,0,1,2)
        self.fitOptionsGrid.addWidget(self.meanPrecPriorCheck,100,2,1,1)
        self.fitOptionsGrid.addWidget(self.meanPrecPriorEdit,100,3,1,3)

        self.meanPriorLabel = QtWidgets.QLabel("Mean Prior")
        self.meanPriorCheck = QtWidgets.QCheckBox()
        self.meanPriorCheck.stateChanged.connect(self.mean_prior_check_changed)
        self.meanPriorEdit = QtWidgets.QLineEdit(self.mean_prior)
        if not self.mean_prior:
            self.meanPriorCheck.setChecked(False)
            self.meanPriorEdit.setEnabled(False)
        else:
            self.meanPriorCheck.setChecked(True)
        self.fitOptionsGrid.addWidget(self.meanPriorLabel,110,0,1,2)
        self.fitOptionsGrid.addWidget(self.meanPriorCheck,110,2,1,1)
        self.fitOptionsGrid.addWidget(self.meanPriorEdit,110,3,1,3)

        self.dofLabel = QtWidgets.QLabel("Deg. of Freedom Prior")
        self.dofCheck = QtWidgets.QCheckBox()
        self.dofCheck.stateChanged.connect(self.dof_check_changed)
        self.dofEdit = QtWidgets.QLineEdit(self.dof)
        if not self.dof:
            self.dofCheck.setChecked(False)
            self.dofEdit.setEnabled(False)
        else:
            self.dofCheck.setChecked(True)
        self.fitOptionsGrid.addWidget(self.dofLabel,120,0,1,2)
        self.fitOptionsGrid.addWidget(self.dofCheck,120,2,1,1)
        self.fitOptionsGrid.addWidget(self.dofEdit,120,3,1,3)

        self.rsLabel = QtWidgets.QLabel("Random State")
        self.rsCheck = QtWidgets.QCheckBox()
        self.rsCheck.stateChanged.connect(self.rs_check_changed)
        self.rsEdit = QtWidgets.QLineEdit(self.rs)
        if not self.rs:
            self.rsCheck.setChecked(False)
            self.rsEdit.setEnabled(False)
        else:
            self.rsCheck.setChecked(True)
        self.fitOptionsGrid.addWidget(self.rsLabel,130,0,1,2)
        self.fitOptionsGrid.addWidget(self.rsCheck,130,2,1,1)
        self.fitOptionsGrid.addWidget(self.rsEdit,130,3,1,3)

        self.vbLabel = QtWidgets.QLabel("Verbose")
        self.vbEdit = QtWidgets.QLineEdit(self.vb)
        self.fitOptionsGrid.addWidget(self.vbLabel,140,0,1,2)
        self.fitOptionsGrid.addWidget(self.vbEdit,140,2,1,4)

        self.vbIntvLabel = QtWidgets.QLabel("Verbose Interval")
        self.vbIntvEdit = QtWidgets.QLineEdit(self.vb_interval)
        self.fitOptionsGrid.addWidget(self.vbIntvLabel,150,0,1,2)
        self.fitOptionsGrid.addWidget(self.vbIntvEdit,150,2,1,4)

        self.warmStartLabel = QtWidgets.QLabel("Warm Start?")
        self.warmStartCheck = QtWidgets.QCheckBox()
        self.warmStartCheck.setChecked(False)
        self.fitOptionsGrid.addWidget(self.warmStartLabel,160,0,1,2)
        self.fitOptionsGrid.addWidget(self.warmStartCheck,160,2,1,4)

        self.covarPriorLabel = QtWidgets.QLabel("Covariance Prior")
        self.covarPriorCheck = QtWidgets.QCheckBox()
        self.covarPriorCheck.setChecked(False)
        self.covarPriorCheck.stateChanged.connect(self.covar_prior_check_changed)
        self.covarTab = QtWidgets.QTabWidget()
        self.covarTab.setContentsMargins(0,0,0,0)
        self.covarTab.setTabsClosable(False)
        for i in range(int(self.ncomp)):
            covar_prior_table = QtWidgets.QTableWidget()
            covar_prior_table.setColumnCount(int(self.nfeature))
            for j in range(int(self.nfeature)):
                covar_prior_table.setHorizontalHeaderItem(j,QtWidgets.QTableWidgetItem('C{}'.format(j)))
            covar_prior_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
            covar_prior_table.horizontalHeader().setBackgroundRole(QtGui.QPalette.Highlight)
            covar_prior_table.setMinimumHeight(200)
            covar_prior_table.setRowCount(int(self.nfeature))
            for j in range(int(self.nfeature)):
                item = QtWidgets.QTableWidgetItem('R{}'.format(j))
                covar_prior_table.setVerticalHeaderItem(j,item)
            self.covarTab.addTab(covar_prior_table,"Component {}".format(i+1))
        self.covarTab.setEnabled(self.covarPriorCheck.isChecked())
        self.fitOptionsGrid.addWidget(self.covarPriorLabel,170,0,1,2)
        self.fitOptionsGrid.addWidget(self.covarPriorCheck,170,2,1,4)
        self.fitOptionsGrid.addWidget(self.covarTab,180,0,1,6)
       
        self.statusBar = QtWidgets.QGroupBox("Log")
        self.statusBar.setStyleSheet('QGroupBox::title {color:blue;}')
        self.statusGrid = QtWidgets.QGridLayout(self.statusBar)
        self.statusBar.setFixedHeight(150)
        self.statusBar.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Fixed)
        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setFixedHeight(12)
        self.progressBar.setFixedWidth(800)
        self.progressBar.setVisible(False)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBarSizePolicy = self.progressBar.sizePolicy()
        self.progressBarSizePolicy.setRetainSizeWhenHidden(True)
        self.progressBar.setSizePolicy(self.progressBarSizePolicy)
        self.PROGRESS_ADVANCE.connect(self.progress)
        self.PROGRESS_END.connect(self.progress_reset)
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
            connect(self.start)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[1].clicked. \
            connect(self.stop)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[2].clicked.\
            connect(self.reset)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[3].clicked.\
            connect(self.reject)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[0].setEnabled(False)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[1].setEnabled(False)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[2].setEnabled(False)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[3].setEnabled(False)
        self.distributionChartTitle = QtWidgets.QLabel('Distribution')
        self.distributionChart = profile_chart.ProfileChart(self.config)
        self.distributionChart.set_fonts(self.fontList.currentFont().family(),self.fontSizeSlider.value())
        self.distributionChart.setFixedSize(1300,1300)
        self.FONTS_CHANGED.connect(self.distributionChart.adjust_fonts)
        self.costChartTitle = QtWidgets.QLabel('ELBO Change')
        self.costChart = profile_chart.ProfileChart(self.config)
        self.costChart.set_fonts(self.fontList.currentFont().family(),self.fontSizeSlider.value())
        self.FONTS_CHANGED.connect(self.costChart.adjust_fonts)
        self.weightChart = bar_chart.BarChart(self.config)
        self.weightChart.set_fonts(self.fontList.currentFont().family(),self.fontSizeSlider.value())
        self.FONTS_CHANGED.connect(self.weightChart.adjust_fonts)
        self.LeftGrid.addWidget(self.chooseSource,0,0)
        self.LeftGrid.addWidget(self.chooseDestination,1,0)
        self.LeftGrid.addWidget(self.appearance,3,0)
        self.LeftGrid.addWidget(self.sampleOptions,4,0)
        self.LeftGrid.addWidget(self.fitOptions,5,0)
        self.LeftGrid.addWidget(self.ButtonBox,6,0)
        self.RightGrid.addWidget(self.distributionChartTitle,0,0)
        self.RightGrid.addWidget(self.costChartTitle,0,1)
        self.RightGrid.addWidget(self.distributionChart,1,0)
        self.RightGrid.addWidget(self.costChart,1,1)
        self.RightGrid.addWidget(self.weightChart,2,0,1,2)
        self.RightGrid.addWidget(self.statusBar,3,0,1,2)
        self.RightGrid.addWidget(self.progressBar,4,0,1,2)
        self.Grid.addWidget(self.hSplitter,0,0)
        self.leftScroll.setWidget(self.LeftFrame)
        self.leftScroll.setWidgetResizable(True)
        self.leftScroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.Dialog.setWindowTitle("Gaussian Mixture Modeling")
        self.Dialog.setMinimumHeight(2000)
        self.Dialog.setMinimumWidth(3000)
        self.Dialog.setWindowModality(QtCore.Qt.WindowModal)
        self.Dialog.showNormal()
        desktopRect = QtWidgets.QApplication.desktop().availableGeometry(self.Dialog)
        center = desktopRect.center()
        self.Dialog.move(center.x()-self.Dialog.width()*0.5,center.y()-self.Dialog.height()*0.5)

    def wc_prior_check_changed(self,state):
        if state == 0:
            self.wcPriorEdit.setEnabled(False)
        elif state == 2:
            self.wcPriorEdit.setEnabled(True)

    def mean_precision_prior_check_changed(self,state):
        if state == 0:
            self.meanPrecPriorEdit.setEnabled(False)
        elif state == 2:
            self.meanPrecPriorEdit.setEnabled(True)

    def mean_prior_check_changed(self,state):
        if state == 0:
            self.meanPriorEdit.setEnabled(False)
        elif state == 2:
            self.meanPriorEdit.setEnabled(True)

    def dof_check_changed(self,state):
        if state == 0:
            self.dofEdit.setEnabled(False)
        elif state == 2:
            self.dofEdit.setEnabled(True)

    def rs_check_changed(self,state):
        if state == 0:
            self.rsEdit.setEnabled(False)
        elif state == 2:
            self.rsEdit.setEnabled(True)

    def covar_prior_check_changed(self,state):
        if state == 0:
            self.covarTab.setEnabled(False)
        elif state == 2:
            self.covarTab.setEnabled(True)

    def choose_source(self):
        path = QtWidgets.QFileDialog.getOpenFileName(None,"choose the input data file","c:/users/yux20/documents/05042018 MoS2/interpolated_3D_map.txt",filter="TXT (*.txt)")[0]
        self.currentSource = path
        self.chooseSourceLabel.setText("The source directory is:\n"+self.currentSource)
        self.loadButton.setEnabled(True)

    def load_data(self):
        try:
            self.grid_3d = pandas.read_csv(filepath_or_buffer=self.currentSource,sep="\t",names=["x","y","z","probability"])
            self.drawSampleButton.setEnabled(True)
        except:
            self.raise_error("Wrong Input!")

    def draw_sample(self):
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[0].setEnabled(False)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[1].setEnabled(False)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[2].setEnabled(False)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[3].setEnabled(False)
        self.update_log("Drawing Samples... ")
        QtCore.QCoreApplication.processEvents()
        draw = rv_discrete(name='custm',values=(self.grid_3d.index,self.grid_3d["probability"]))
        indices = draw.rvs(size=int(self.numberOfSamplesEdit.text()))
        selected = self.grid_3d.iloc[indices]
        x, y = selected["x"].to_numpy(),selected["y"].to_numpy()
        self.inputdata = np.vstack([x,y]).T
        self.label = np.full(len(self.inputdata),1)
        self.update_log("Drawing Completed")
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[0].setEnabled(True)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[1].setEnabled(False)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[2].setEnabled(True)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[3].setEnabled(True)

    def choose_destination(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(None,"choose save destination",self.currentDestination,QtWidgets.QFileDialog.ShowDirsOnly)
        self.currentDestination = path
        self.chooseDestinationLabel.setText("The save destination is:\n"+self.currentDestination)

    def refresh_font_size(self):
        self.fontSizeLabel.setText("Adjust Font Size ({})".format(self.fontSizeSlider.value()))
        self.FONTS_CHANGED.emit(self.fontList.currentFont().family(),self.fontSizeSlider.value())

    def refresh_font_name(self):
        self.FONTS_CHANGED.emit(self.fontList.currentFont().family(),self.fontSizeSlider.value())
        
    def prepare(self):
        # mean_precision_prior= 0.8 to minimize the influence of the prior
        self.estimator = My_GMM(
            n_components=2 * int(self.numberOfComponentsEdit.text()), 
            covariance_type=self.covarianceTypeCombo.currentText(),
            tol=float(self.tolEdit.text()),
            reg_covar=float(self.regCovarEdit.text()), 
            max_iter=int(self.maxItrEdit.text()), 
            n_init=int(self.nInitEdit.text()),
            init_params=self.initMethodTypeCombo.currentText(),
            weight_concentration_prior_type=self.wcPriorTypeCombo.currentText(),
            mean_precision_prior=float(self.meanPrecPriorEdit.text()),
            degrees_of_freedom_prior=int(self.dofEdit.text()) if self.dofEdit.text() != '' else None,
            random_state=int(self.rsEdit.text()), 
            warm_start=self.warmStartCheck.isChecked(),
            verbose=int(self.vbEdit.text()), 
            verbose_interval=int(self.vbIntvEdit.text()),
            weight_concentration_prior=float(self.wcPriorEdit.text()))

        ## Generate data
        #rng = np.random.RandomState(int(self.rsEdit.text()))
        #self.inputdata = np.vstack([
        #    rng.multivariate_normal(self.means[j], self.covars[j], self.samples[j])
        #    for j in range(int(self.numberOfComponentsEdit.text()))])
        #self.label = np.concatenate([np.full(self.samples[j], j, dtype=int)
        #                    for j in range(int(self.numberOfComponentsEdit.text()))])
        #print(self.inputdata)
        
        self.distributionChart.add_chart(self.inputdata[:,0],self.inputdata[:,1],'scatter')
        self.cost_series_X = [1]
        self.cost_series_Y = [1]

        self.estimator.load_input(self.inputdata,self.label)
        self.estimator.UPDATE_LOG.connect(self.update_log)
        self.estimator.SEND_UPDATE.connect(self.update_plots)
        self.thread = QtCore.QThread()
        self.estimator.moveToThread(self.thread)
        self.estimator.FINISHED.connect(self.thread.quit)
        self.estimator.FINISHED.connect(self.process_finished)
        self.thread.started.connect(self.estimator.run)
        self.STOP_WORKER.connect(self.estimator.stop)
        return True

    def start(self):
        ready = self.prepare()
        if ready:
            self.thread.start()
            self.ButtonBox.findChildren(QtWidgets.QPushButton)[0].setEnabled(False)
            self.ButtonBox.findChildren(QtWidgets.QPushButton)[1].setEnabled(True)
            self.ButtonBox.findChildren(QtWidgets.QPushButton)[2].setEnabled(False)
            self.ButtonBox.findChildren(QtWidgets.QPushButton)[3].setEnabled(False)
            self.fitOptions.setEnabled(False)

    def stop(self):
        self.STOP_WORKER.emit()
        if self.thread.isRunning():
            self.thread.terminate()
            self.thread.wait()
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[0].setEnabled(True)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[1].setEnabled(False)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[2].setEnabled(True)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[3].setEnabled(True)
        self.fitOptions.setEnabled(True)

    def process_finished(self):
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[0].setEnabled(True)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[1].setEnabled(False)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[2].setEnabled(True)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[3].setEnabled(True)
        self.fitOptions.setEnabled(True)
        #title = "Infinite mixture with a Dirichlet process\n prior and" r"$\gamma_0=$" + self.wcPriorEdit.text()
        #plt.figure(figsize=(4.7 * 3, 8))
        #plt.subplots_adjust(bottom=.04, top=0.90, hspace=.05, wspace=.05,
        #                    left=.03, right=.99)
        #gs = gridspec.GridSpec(3, 1)
        #self.plot_results(plt.subplot(gs[0:2, 0]), plt.subplot(gs[2, 0]), title, plot_title = True)
        #plt.show()

    def reset(self):
        pass

    def update_plots(self,n_iter,change,params):
        if n_iter>1:
            weight_concentration = params[0]
            mean_precision = params[1]
            means = params[2]
            degrees_of_freedom = params[3]
            covars = params[4]
            precisions_cholesky = params[5]
            if self.wcPriorTypeCombo.currentText() == "dirichlet_process":
                weight_dirichlet_sum = (weight_concentration[0] + weight_concentration[1])
                tmp = weight_concentration[1] / weight_dirichlet_sum
                weights = (
                    weight_concentration[0] / weight_dirichlet_sum *
                    np.hstack((1, np.cumprod(tmp[:-1]))))
                weights /= np.sum(weights)
            else:
                weights = (weight_concentration/np.sum(weight_concentration))

            a, b, angle,colors = [], [], [], []
            for i in range(means.shape[0]):
                eig_vals, eig_vecs = np.linalg.eigh(covars[i])
                unit_eig_vec = eig_vecs[0] / np.linalg.norm(eig_vecs[0])
                ang = np.arctan2(unit_eig_vec[1], unit_eig_vec[0])
                ang = 180 * ang / np.pi
                eig_vals = 2 * np.sqrt(2) * np.sqrt(eig_vals)
                a.append(eig_vals[0])
                b.append(eig_vals[1])
                angle.append(ang)
                colors.append(self.fit_colors[i])

            self.cost_series_X.append(n_iter)
            self.cost_series_Y.append(change)
            self.costChart.add_chart(self.cost_series_X, self.cost_series_Y,'ELBO change')
            self.distributionChart.append_to_chart(x=means[:,0],y=means[:,1],a=a,b=b,angle=angle,weights=weights,colors=colors,type='ellipse')
            self.weightChart.add_chart(weights=weights,colors=colors,type='bar')

    def plot_ellipses(self,ax, weights, means, covars):
        for n in range(means.shape[0]):
            eig_vals, eig_vecs = np.linalg.eigh(covars[n])
            unit_eig_vec = eig_vecs[0] / np.linalg.norm(eig_vecs[0])
            angle = np.arctan2(unit_eig_vec[1], unit_eig_vec[0])
            # Ellipse needs degrees
            angle = 180 * angle / np.pi
            # eigenvector normalization
            eig_vals = 2 * np.sqrt(2) * np.sqrt(eig_vals)
            ell = mpl.patches.Ellipse(means[n], eig_vals[0], eig_vals[1],
                                    180 + angle, edgecolor='black')
            ell.set_clip_box(ax.bbox)
            ell.set_alpha(weights[n])
            ell.set_facecolor(self.fit_colors[n])
            ax.add_artist(ell)

    def plot_results(self,ax1, ax2, title, plot_title=False):
        estimator = self.estimator
        X = self.inputdata
        y = self.label
        ax1.set_title(title)
        ax1.scatter(X[:, 0], X[:, 1], s=5, marker='o', color='lightgray', alpha=0.8)
        ax1.set_xlim(-2., 2.)
        ax1.set_ylim(-2., 2.)
        ax1.set_xticks(())
        ax1.set_yticks(())
        self.plot_ellipses(ax1, estimator.weights_, estimator.means_,estimator.covariances_)
        ax1.set_aspect(1)

        ax2.get_xaxis().set_tick_params(direction='out')
        ax2.yaxis.grid(True, alpha=0.7)
        for n in range(estimator.means_.shape[0]):
            k,w = n, estimator.weights_[n]
            ax2.bar(k, w, width=0.9, color=self.fit_colors[k], zorder=3,
                    align='center', edgecolor='black')
            ax2.text(k, w + 0.007, "%.1f%%" % (w * 100.),
                    horizontalalignment='center')
        ax2.set_xlim(-.6, 2 * int(self.numberOfComponentsEdit.text()) - .4)
        ax2.set_ylim(0., 1.1)
        ax2.tick_params(axis='y', which='both', left=False,
                        right=False, labelleft=False)
        ax2.tick_params(axis='x', which='both', top=False)

        if plot_title:
            ax1.set_ylabel('Estimated Mixtures')
            ax2.set_ylabel('Weight of each component')

    def write_results(self,results):
        self.fitting_results.append(results)

    def close_results(self):
        for result in self.fitting_results:
            self.output.write(result)
        self.output.close()

    def update_log(self,message):
        self.logBox.append(QtCore.QTime.currentTime().toString("hh:mm:ss")+"\u00A0\u00A0\u00A0\u00A0" + message)
        self.logBox.moveCursor(QtGui.QTextCursor.End)

    def reject(self):
        self.Dialog.close()

    def initial_parameters(self):
        para = []
        if self.fitFunctionCombo.currentText() == 'Gaussian':
            j_list = [3,0,6]
        elif self.fitFunctionCombo.currentText() == 'Voigt':
            j_list = [0,3,6,9]
        for j in j_list:
            for i in range(self.table.rowCount()):
                para.append(float(self.table.item(i,j).text()))
        para.append(float(self.offset.get_value()))
        return para

    def change_fit_function(self,function):
        if function == 'Gaussian':
            self.table.setColumnCount(9)
            self.table.setHorizontalHeaderItem(0,QtWidgets.QTableWidgetItem('C'))
            self.table.setHorizontalHeaderItem(1,QtWidgets.QTableWidgetItem('C_Low'))
            self.table.setHorizontalHeaderItem(2,QtWidgets.QTableWidgetItem('C_High'))
            self.table.setHorizontalHeaderItem(3,QtWidgets.QTableWidgetItem('H'))
            self.table.setHorizontalHeaderItem(4,QtWidgets.QTableWidgetItem('H_Low'))
            self.table.setHorizontalHeaderItem(5,QtWidgets.QTableWidgetItem('H_High'))
            self.table.setHorizontalHeaderItem(6,QtWidgets.QTableWidgetItem('W'))
            self.table.setHorizontalHeaderItem(7,QtWidgets.QTableWidgetItem('W_Low'))
            self.table.setHorizontalHeaderItem(8,QtWidgets.QTableWidgetItem('W_High'))
            self.fit_function = self.fit_worker.gaussian
        elif function == 'Voigt':
            self.table.setColumnCount(12)
            self.table.setHorizontalHeaderItem(0,QtWidgets.QTableWidgetItem('C'))
            self.table.setHorizontalHeaderItem(1,QtWidgets.QTableWidgetItem('C_Low'))
            self.table.setHorizontalHeaderItem(2,QtWidgets.QTableWidgetItem('C_High'))
            self.table.setHorizontalHeaderItem(3,QtWidgets.QTableWidgetItem('A'))
            self.table.setHorizontalHeaderItem(4,QtWidgets.QTableWidgetItem('A_Low'))
            self.table.setHorizontalHeaderItem(5,QtWidgets.QTableWidgetItem('A_High'))
            self.table.setHorizontalHeaderItem(6,QtWidgets.QTableWidgetItem('FL'))
            self.table.setHorizontalHeaderItem(7,QtWidgets.QTableWidgetItem('FL_Low'))
            self.table.setHorizontalHeaderItem(8,QtWidgets.QTableWidgetItem('FL_High'))
            self.table.setHorizontalHeaderItem(9,QtWidgets.QTableWidgetItem('FG'))
            self.table.setHorizontalHeaderItem(10,QtWidgets.QTableWidgetItem('FG_Low'))
            self.table.setHorizontalHeaderItem(11,QtWidgets.QTableWidgetItem('FG_High'))
            self.fit_function = self.fit_worker.voigt
        self.table_auto_initialize()

    def update_results(self,results):
        self.offset.set_value(results[-1])
        if self.fitFunctionCombo.currentText() == 'Gaussian':
            index=0
            for j in [3,0,6]:
                for i in range(self.table.rowCount()):
                    value = np.round(results[index],2)
                    item = QtWidgets.QTableWidgetItem('{}'.format(value))
                    variation = [0.5,0.5,0.5,0.5,0.5,0.5]
                    #Height
                    if j == 3:
                        item2 = QtWidgets.QTableWidgetItem('{}'.format(max(0,np.round(value-variation[0],2))))
                        item3 = QtWidgets.QTableWidgetItem('{}'.format(np.round(value+variation[1],2)))
                    #Center
                    elif j == 0:
                        item2 = QtWidgets.QTableWidgetItem('{}'.format(max(0,np.round(value-variation[2],2))))
                        item3 = QtWidgets.QTableWidgetItem('{}'.format(np.round(value+variation[3],2)))
                    #Width
                    else:
                        item2 = QtWidgets.QTableWidgetItem('{}'.format(max(0.1,np.round(value-variation[4],2))))
                        item3 = QtWidgets.QTableWidgetItem('{}'.format(np.round(value+variation[5],2)))
                    item.setForeground(QtGui.QBrush(QtGui.QColor(QtCore.Qt.red)))
                    item.setTextAlignment(QtCore.Qt.AlignCenter)
                    item2.setTextAlignment(QtCore.Qt.AlignCenter)
                    item3.setTextAlignment(QtCore.Qt.AlignCenter)
                    self.table.setItem(i,j,item)
                    self.table.setItem(i,j+1,item2)
                    self.table.setItem(i,j+2,item3)
                    index+=1
        elif self.fitFunctionCombo.currentText() == 'Voigt':
            index=0
            for j in [0,3,6,9]:
               for i in range(self.table.rowCount()):
                   value = np.round(results[index],2)
                   item = QtWidgets.QTableWidgetItem('{}'.format(value))
                   variation = [0.5,0.5,1,1,1,1,1,1]
                   #Center
                   if j == 0:
                       item2 = QtWidgets.QTableWidgetItem('{}'.format(max(0,np.round(value-variation[0],2))))
                       item3 = QtWidgets.QTableWidgetItem('{}'.format(np.round(value+variation[1],2)))
                   #Amplitude
                   elif j == 3:
                       item2 = QtWidgets.QTableWidgetItem('{}'.format(max(0,np.round(value-variation[2],2))))
                       item3 = QtWidgets.QTableWidgetItem('{}'.format(np.round(value+variation[3],2)))
                   #FL
                   elif j == 6:
                       item2 = QtWidgets.QTableWidgetItem('{}'.format(max(0.01,np.round(value-variation[4],2))))
                       item3 = QtWidgets.QTableWidgetItem('{}'.format(np.round(value+variation[5],2)))
                   #FG
                   elif j == 9:
                       item2 = QtWidgets.QTableWidgetItem('{}'.format(max(0.01,np.round(value-variation[6],2))))
                       item3 = QtWidgets.QTableWidgetItem('{}'.format(np.round(value+variation[7],2)))
                   item.setForeground(QtGui.QBrush(QtGui.QColor(QtCore.Qt.red)))
                   item.setTextAlignment(QtCore.Qt.AlignCenter)
                   item2.setTextAlignment(QtCore.Qt.AlignCenter)
                   item3.setTextAlignment(QtCore.Qt.AlignCenter)
                   self.table.setItem(i,j,item)
                   self.table.setItem(i,j+1,item2)
                   self.table.setItem(i,j+2,item3)
                   index+=1
        self.FEED_BACK_TO_FIT_WORKER.emit(self.guess, (self.bound_low,self.bound_high))

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

    def progress(self,min,max,val):
        self.progressBar.setVisible(True)
        self.progressBar.setMinimum(min)
        self.progressBar.setMaximum(max)
        self.progressBar.setValue(val)

    def progress_reset(self):
        self.progressBar.reset()
        self.progressBar.setVisible(False)

class Meta_QT_GMM(type(QtCore.QObject),type(BayesianGaussianMixture)):
    pass

class My_GMM(QtCore.QObject, BayesianGaussianMixture,metaclass=Meta_QT_GMM):
    UPDATE_LOG = QtCore.pyqtSignal(str)
    SEND_UPDATE = QtCore.pyqtSignal(int,float,tuple)
    FINISHED = QtCore.pyqtSignal()
    def __init__(self,*,n_components=1, covariance_type='full', tol=1e-3,
                 reg_covar=1e-6, max_iter=100, n_init=1, init_params='kmeans',
                 weight_concentration_prior_type='dirichlet_process',
                 weight_concentration_prior=None,
                 mean_precision_prior=None, mean_prior=None,
                 degrees_of_freedom_prior=None, covariance_prior=None,
                 random_state=None, warm_start=False, verbose=0,
                 verbose_interval=10):
        super().__init__(n_components=n_components, covariance_type=covariance_type, tol=tol,
                 reg_covar=reg_covar, max_iter=max_iter, n_init=n_init, init_params=init_params,
                 weight_concentration_prior_type=weight_concentration_prior_type,
                 weight_concentration_prior=weight_concentration_prior,
                 mean_precision_prior=mean_precision_prior, mean_prior=mean_prior,
                 degrees_of_freedom_prior=degrees_of_freedom_prior, covariance_prior=covariance_prior,
                 random_state=random_state, warm_start=warm_start, verbose=verbose,
                 verbose_interval=verbose_interval)
        

    def load_input(self,X,y):
        self.inputdata = X
        self.label = y

    def run(self):
        self.abort_ = False
        self.fit_predict(self.inputdata,self.label)

    def stop(self):
        self.abort_ = True

    def fit_predict(self,X,y=None):
        #X = _check_X(X, self.n_components, ensure_min_samples=2)
        self._check_n_features(X, reset=True)
        self._check_initial_parameters(X)

        # if we enable warm_start, we will have a unique initialisation
        do_init = not(self.warm_start and hasattr(self, 'converged_'))
        n_init = self.n_init if do_init else 1

        max_lower_bound = -np.infty
        self.converged_ = False

        if self.random_state is None or self.random_state is np.random:
            random_state = np.random.mtrand._rand
        elif isinstance(self.random_state,numbers.Integral):
            random_state = np.random.RandomState(self.random_state)
        elif isinstance(self.random_state,np.random.RandomState):
            random_state = self.random_state

        n_samples, _ = X.shape
        for init in range(n_init):

            if do_init:
                self._initialize_parameters(X, random_state)

            lower_bound = (-np.infty if do_init else self.lower_bound_)

            for n_iter in range(1, self.max_iter + 1):
                prev_lower_bound = lower_bound

                log_prob_norm, log_resp = self._e_step(X)
                self._m_step(X, log_resp)
                lower_bound = self._compute_lower_bound(log_resp, log_prob_norm)

                change = lower_bound - prev_lower_bound
                self.SEND_UPDATE.emit(n_iter, change, self._get_parameters())
                self.UPDATE_LOG.emit("[From sklearn.mixture.BayesGM] At iteration {}, change={}".format(n_iter,change))
                time.sleep(0.05)

                if abs(change) < self.tol:
                    self.converged_ = True
                    break
                if self.abort_:
                    self.UPDATE_LOG.emit("[From sklearn.mixture.BayesGM] Aborted.")
                    break

                QtCore.QCoreApplication.processEvents()
            
            self.UPDATE_LOG.emit("[From sklearn.mixture.BayesGM] Final lower bound: {}".format(lower_bound))

            if lower_bound > max_lower_bound:
                max_lower_bound = lower_bound
                best_params = self._get_parameters()
                best_n_iter = n_iter

        if not self.converged_ and not self.abort_:
            self.UPDATE_LOG.emit('Initialization %d did not converge. Try different init parameters, or increase max_iter, tol or check for degenerate data.')

        self._set_parameters(best_params)
        self.n_iter_ = best_n_iter
        self.lower_bound_ = max_lower_bound

        # Always do a final e-step to guarantee that the labels returned by
        # fit_predict(X) are always consistent with fit(X).predict(X)
        # for any value of max_iter and tol (and any random_state).
        _, log_resp = self._e_step(X)
        self.FINISHED.emit()

        return log_resp.argmax(axis=1)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.main()
    sys.exit(app.exec_())