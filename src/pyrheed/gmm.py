from my_widgets import LabelSlider
from process import Image, FitFunctions, FitBroadening
from process_monitor import Monitor
from PyQt6 import QtCore, QtWidgets, QtGui, QtCharts
from sys import getsizeof
from sklearn.mixture import BayesianGaussianMixture
from sklearn.mixture._gaussian_mixture import _estimate_gaussian_parameters
from sklearn.mixture._gaussian_mixture import _compute_precision_cholesky
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
        dirname = os.path.dirname(__file__)
        self.config.read(os.path.join(dirname,'configuration.ini'))
        self.image_worker = Image()
        self.fit_worker = FitFunctions()
        self.stopped = False

        primary_colors = ['salmon','bright green','bright pink','robin egg blue','bright lavender','deep sky blue','irish green','golden','greenish teal','light blue','butter yellow',\
                                                                            'turquoise green','iris','off blue','plum','mauve','burgundy','coral','clay','emerald green','cadet blue','avocado','rose pink','aqua green','scarlet']
        self.fit_colors = [mcolors.XKCD_COLORS['xkcd:'+name] for name in primary_colors]
        for color in mcolors.XKCD_COLORS.keys():
            if not color in primary_colors:
                self.fit_colors.append(mcolors.XKCD_COLORS[color])
        self.default_means = [[0,0],[2.3,0],[1.15,2],[-1.15,2],[-2.3,0],[-1.15,-2],[1.15,-2],[4.6,0],[2.3,4],[-2.3,4],[-4.6,0],[-2.3,-4],[2.3,-4],[3.45,2],[0,4],[-3.45,2],[-3.45,-2],[0,-4],[3.45,-2]]

    def refresh(self,config):
            self.config = config
            try:
                self.distributionChart.refresh(config)
                self.costChart.refresh(config)
                self.weightChart.refresh(config)
            except:
                pass

    def set_status(self,status):
        self.status = status

    def main(self,path="c:/users/yux20/documents/05042018 MoS2/interpolated_2D_stack_large.csv"):
        self.startIndex = "0"
        self.endIndex = "3"
        self.range = "5"
        self.nsamp = '10'
        self.ndraw = '2'
        self.nzslices = '10'
        self.nfeature = '2'
        self.ncomp = '19'
        self.tol = '0.001'
        self.reg_covar = '1e-6'
        self.max_itr = '1500'
        self.n_init = '1'
        self.wc_prior = '1000'
        self.mean_precision_prior = '0.8'
        self.dof = ''
        self.rs = '2'
        self.vb = '0'
        self.vb_interval = '10'
        self.defaultFileName = "GMM Fit"
        self.cost_series_X = [1]
        self.cost_series_Y = [1]
        self.thread = QtCore.QThread(parent=self)
        self.file_has_been_created = False
        self.scatter_exist = False
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
        self.hSplitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        self.hSplitter.addWidget(self.RightFrame)
        self.hSplitter.addWidget(self.LeftFrame)
        self.hSplitter.setStretchFactor(0,1)
        self.hSplitter.setStretchFactor(1,1)
        self.hSplitter.setCollapsible(0,False)
        self.hSplitter.setCollapsible(1,False)
        self.leftScroll = QtWidgets.QScrollArea(self.hSplitter)

        self.chooseSource = QtWidgets.QGroupBox("Input")
        self.sourceGrid = QtWidgets.QGridLayout(self.chooseSource)
        self.sourceGrid.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.chooseSourceLabel = QtWidgets.QLabel("The input data directory is:\n"+self.currentSource)
        self.chooseSourceLabel.setWordWrap(True)
        self.chooseSourceButton = QtWidgets.QPushButton("Browse...")
        self.chooseSourceButton.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed,QtWidgets.QSizePolicy.Policy.Fixed)
        self.chooseSourceButton.clicked.connect(self.choose_source)
        self.loadButton = QtWidgets.QPushButton("Load")
        self.loadButton.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed,QtWidgets.QSizePolicy.Policy.Fixed)
        self.loadButton.clicked.connect(self.load_data)
        self.loadButton.setEnabled(False)
        self.sourceGrid.addWidget(self.chooseSourceLabel,0,0,2,1)
        self.sourceGrid.addWidget(self.chooseSourceButton,0,1,1,1)
        self.sourceGrid.addWidget(self.loadButton,1,1,1,1)

        self.information = QtWidgets.QGroupBox("Information")
        self.informationGrid = QtWidgets.QGridLayout(self.information)
        self.informationGrid.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.informationLabel = QtWidgets.QLabel("")
        self.informationLabel.setWordWrap(True)
        self.informationGrid.addWidget(self.informationLabel,0,0)

        self.chooseDestination = QtWidgets.QGroupBox("Output")
        self.destinationGrid = QtWidgets.QGridLayout(self.chooseDestination)
        self.chooseDestinationLabel = QtWidgets.QLabel("The output directory is:\n"+self.currentSource)
        self.destinationNameLabel = QtWidgets.QLabel("The file name is:")
        self.destinationNameEdit = QtWidgets.QLineEdit(self.defaultFileName)
        self.fileTypeLabel = QtWidgets.QLabel("The file format is:")
        self.fileType = QtWidgets.QComboBox()
        self.fileType.addItem(".txt",".txt")
        self.fileType.addItem(".xlsx",".xlsx")
        self.chooseDestinationButton = QtWidgets.QPushButton("Browse...")
        self.chooseDestinationButton.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed,QtWidgets.QSizePolicy.Policy.Fixed)
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
        self.destinationGrid.setAlignment(self.chooseDestinationButton,QtCore.Qt.AlignmentFlag.AlignRight)

        self.appearance = QtWidgets.QGroupBox("Appearance")
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

        self.sampleOptions = QtWidgets.QGroupBox("Sample")
        self.sampleOptionsGrid = QtWidgets.QGridLayout(self.sampleOptions)
        self.numberOfSamplesLabel = QtWidgets.QLabel("Number of Samples")
        self.numberOfSamplesEdit = QtWidgets.QLineEdit(self.nsamp)
        self.numberOfDrawsLabel = QtWidgets.QLabel("Number of Draws")
        self.numberOfDrawsEdit = QtWidgets.QLineEdit(self.ndraw)
        self.numberOfZsLabel = QtWidgets.QLabel("Number of Z Slices")
        self.numberOfZsEdit = QtWidgets.QLineEdit(self.nzslices)
        self.drawSampleButton = QtWidgets.QPushButton("Draw Z=0")
        self.drawSampleButton.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed,QtWidgets.QSizePolicy.Policy.Fixed)
        self.drawSampleButton.clicked.connect(self.draw_sample)
        self.drawSampleButton.setEnabled(False)
        self.plotSampleButton = QtWidgets.QPushButton("Plot Z=0")
        self.plotSampleButton.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed,QtWidgets.QSizePolicy.Policy.Fixed)
        self.plotSampleButton.clicked.connect(self.plot_sample)
        self.plotSampleButton.setEnabled(False)
        self.sampleOptionsGrid.addWidget(self.numberOfSamplesLabel,0,0,1,2)
        self.sampleOptionsGrid.addWidget(self.numberOfSamplesEdit,0,2,1,4)
        self.sampleOptionsGrid.addWidget(self.numberOfDrawsLabel,1,0,1,2)
        self.sampleOptionsGrid.addWidget(self.numberOfDrawsEdit,1,2,1,4)
        self.sampleOptionsGrid.addWidget(self.numberOfZsLabel,2,0,1,2)
        self.sampleOptionsGrid.addWidget(self.numberOfZsEdit,2,2,1,4)
        self.sampleOptionsGrid.addWidget(self.drawSampleButton,3,0,1,3)
        self.sampleOptionsGrid.addWidget(self.plotSampleButton,3,3,1,3)

        self.fitOptions = QtWidgets.QGroupBox("Parameters")
        self.fitOptionsGrid = QtWidgets.QGridLayout(self.fitOptions)
        self.numberOfFeaturesLabel = QtWidgets.QLabel("Number of Features")
        self.numberOfFeaturesEdit = QtWidgets.QLineEdit(self.nfeature)
        self.fitOptionsGrid.addWidget(self.numberOfFeaturesLabel,10,0,1,2)
        self.fitOptionsGrid.addWidget(self.numberOfFeaturesEdit,10,2,1,4)
        self.numberOfFeaturesEdit.textChanged.connect(self.covar_prior_table_change_features)
        self.numberOfFeaturesEdit.textChanged.connect(self.mean_prior_table_change_features)

        self.numberOfComponentsLabel = QtWidgets.QLabel("Number of Components")
        self.numberOfComponentsEdit = QtWidgets.QLineEdit(self.ncomp)
        self.fitOptionsGrid.addWidget(self.numberOfComponentsLabel,20,0,1,2)
        self.fitOptionsGrid.addWidget(self.numberOfComponentsEdit,20,2,1,4)
        self.numberOfComponentsEdit.textChanged.connect(self.mean_prior_table_initialize)
        self.numberOfComponentsEdit.textChanged.connect(self.covar_prior_table_initialize)

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
        self.covarianceTypeCombo = QtWidgets.QComboBox()
        for types in ('full','tied','diag','spherical'):
            self.covarianceTypeCombo.addItem(types,types)
        self.fitOptionsGrid.addWidget(self.covarianceType,70,0,1,2)
        self.fitOptionsGrid.addWidget(self.covarianceTypeCombo,70,2,1,4)

        self.initMethodType = QtWidgets.QLabel("Initialization Method")
        self.initMethodTypeCombo = QtWidgets.QComboBox()
        for types in ('random','kmeans'):
            self.initMethodTypeCombo.addItem(types,types)
        self.fitOptionsGrid.addWidget(self.initMethodType,75,0,1,2)
        self.fitOptionsGrid.addWidget(self.initMethodTypeCombo,75,2,1,4)

        self.wcPriorType = QtWidgets.QLabel("Weight Prior Type")
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

        self.meanPriorTable = QtWidgets.QGroupBox("Mean Prior")
        self.meanPriorTableGrid = QtWidgets.QGridLayout(self.meanPriorTable)
        self.meanPriorLabel = QtWidgets.QLabel("Use Mean Prior?")
        self.meanPriorCheck = QtWidgets.QCheckBox()
        self.meanPriorCheck.setChecked(False)
        self.meanPriorCheck.stateChanged.connect(self.mean_prior_table_check_changed)
        self.resetMeanPriorButton = QtWidgets.QPushButton("Reset")
        self.resetMeanPriorButton.clicked.connect(self.set_default_mean_priors)
        self.mean_prior_table = QtWidgets.QTableWidget()
        self.mean_prior_table.setMinimumHeight(200)
        self.mean_prior_table_initialize(int(self.ncomp))
        self.meanPriorTableGrid.addWidget(self.meanPriorLabel,0,0,1,2)
        self.meanPriorTableGrid.addWidget(self.meanPriorCheck,0,2,1,2)
        self.meanPriorTableGrid.addWidget(self.resetMeanPriorButton,0,4,1,2)
        self.meanPriorTableGrid.addWidget(self.mean_prior_table,1,0,1,6)

        self.covarPriorTable = QtWidgets.QGroupBox("Covariance Prior")
        self.covarPriorTableGrid = QtWidgets.QGridLayout(self.covarPriorTable)
        self.covarPriorLabel = QtWidgets.QLabel("Use Covariance Prior?")
        self.covarPriorCheck = QtWidgets.QCheckBox()
        self.covarPriorCheck.setChecked(False)
        self.covarPriorCheck.stateChanged.connect(self.covar_prior_check_changed)
        self.covarTab = QtWidgets.QTabWidget()
        self.covarTab.setContentsMargins(0,0,0,0)
        self.covarTab.setTabsClosable(False)
        self.covar_prior_table_initialize(int(self.ncomp))
        self.covarTab.widget(0).setEnabled(self.covarPriorCheck.isChecked())
        self.covarPriorTableGrid.addWidget(self.covarPriorLabel,0,0,1,2)
        self.covarPriorTableGrid.addWidget(self.covarPriorCheck,0,2,1,4)
        self.covarPriorTableGrid.addWidget(self.covarTab,1,0,1,6)
       
        self.statusBar = QtWidgets.QGroupBox("Log")
        self.statusGrid = QtWidgets.QGridLayout(self.statusBar)
        self.statusBar.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,QtWidgets.QSizePolicy.Policy.Fixed)
        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setVisible(False)
        self.progressBar.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.progressBarSizePolicy = self.progressBar.sizePolicy()
        self.progressBarSizePolicy.setRetainSizeWhenHidden(True)
        self.progressBar.setSizePolicy(self.progressBarSizePolicy)
        self.PROGRESS_ADVANCE.connect(self.progress)
        self.PROGRESS_END.connect(self.progress_reset)
        self.logBox = QtWidgets.QTextEdit(QtCore.QTime.currentTime().toString("hh:mm:ss")+\
                                    "\u00A0\u00A0\u00A0\u00A0Initialized!")
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
        self.FONTS_CHANGED.connect(self.distributionChart.adjust_fonts)
        self.costChartTitle = QtWidgets.QLabel('ELBO Change')
        self.costChart = profile_chart.ProfileChart(self.config)
        self.costChart.set_fonts(self.fontList.currentFont().family(),self.fontSizeSlider.value())
        self.FONTS_CHANGED.connect(self.costChart.adjust_fonts)
        self.weightChart = bar_chart.BarChart(self.config)
        self.weightChart.set_fonts(self.fontList.currentFont().family(),self.fontSizeSlider.value())
        self.weightChart.setFixedHeight(500)
        self.FONTS_CHANGED.connect(self.weightChart.adjust_fonts)
        self.LeftGrid.addWidget(self.chooseSource,0,0)
        self.LeftGrid.addWidget(self.information,1,0)
        self.LeftGrid.addWidget(self.chooseDestination,2,0)
        self.LeftGrid.addWidget(self.appearance,3,0)
        self.LeftGrid.addWidget(self.sampleOptions,4,0)
        self.LeftGrid.addWidget(self.fitOptions,5,0)
        self.LeftGrid.addWidget(self.meanPriorTable,6,0)
        self.LeftGrid.addWidget(self.covarPriorTable,7,0)
        self.LeftGrid.addWidget(self.ButtonBox,8,0)
        self.RightGrid.addWidget(self.distributionChartTitle,0,0)
        self.RightGrid.addWidget(self.costChartTitle,0,1)
        self.RightGrid.addWidget(self.distributionChart,1,0)
        self.RightGrid.addWidget(self.costChart,1,1)
        self.RightGrid.addWidget(self.weightChart,2,0,1,2)
        self.RightGrid.addWidget(self.statusBar,3,0,1,2)
        self.RightGrid.addWidget(self.progressBar,4,0,1,2)
        self.Grid.addWidget(self.hSplitter,0,0)
        self.leftScroll.setWidget(self.LeftFrame)
        self.leftScroll.setMinimumWidth(800)
        self.leftScroll.setWidgetResizable(True)
        self.leftScroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.Dialog.setWindowTitle("Gaussian Mixture Modeling")
        self.Dialog.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        self.Dialog.showMaximized()
        self.set_default_mean_priors()

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

    def mean_prior_table_check_changed(self,state):
        if state == 0:
            for c in range(self.mean_prior_table.columnCount()):
                if self.mean_prior_table.item(0,2*c):
                    self.mean_prior_table.item(0,2*c).setBackground(QtCore.Qt.GlobalColor.lightGray)
        elif state == 2:
            for c in range(self.mean_prior_table.columnCount()):
                if self.mean_prior_table.item(0,2*c):
                    self.mean_prior_table.item(0,2*c).setBackground(QtCore.Qt.GlobalColor.transparent)

    def covar_prior_check_changed(self,state):
        if state == 0:
            self.covarTab.widget(0).setEnabled(False)
        elif state == 2:
            self.covarTab.widget(0).setEnabled(True)

    def mean_prior_table_change_features(self,text):
        ncomp = int(self.numberOfComponentsEdit.text())
        nfeatures = int(text)
        if nfeatures > 3:
            self.mean_prior_table.clear()
            self.raise_error('Dimension > 3 not supported')
        else:
            self.mean_prior_table.clear()
            self.mean_prior_table.setColumnCount(2*nfeatures)
            coords = ['Prior X', 'Posterior X', 'Prior Y', 'Posterior Y', 'Prior Z', 'Posterior Z']
            for n in range(2*nfeatures):
                header_item = QtWidgets.QTableWidgetItem(coords[n])
                self.mean_prior_table.setHorizontalHeaderItem(n,header_item)
            self.mean_prior_table.setRowCount(ncomp)
            self.mean_prior_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
            self.mean_prior_table.horizontalHeader().setBackgroundRole(QtGui.QPalette.ColorRole.Highlight)
            for i in range(ncomp):
                icon_pm = QtGui.QPixmap(50,50)
                icon_pm.fill(QtGui.QColor(self.fit_colors[i]))
                icon = QtGui.QIcon(icon_pm)
                item = QtWidgets.QTableWidgetItem(icon,'{}'.format(i+1))
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.mean_prior_table.setVerticalHeaderItem(i,item)

    def mean_prior_table_initialize(self,text):
        ncomp = int(text)
        nfeatures = int(self.numberOfFeaturesEdit.text())
        if nfeatures > 3:
            self.mean_prior_table.clear()
            self.raise_error('Dimension > 3 not supported')
        else:
            self.mean_prior_table.clear()
            self.mean_prior_table.setColumnCount(2*nfeatures)
            coords = ['Prior X', 'Posterior X', 'Prior Y', 'Posterior Y', 'Prior Z', 'Posterior Z']
            for n in range(2*nfeatures):
                header_item = QtWidgets.QTableWidgetItem(coords[n])
                self.mean_prior_table.setHorizontalHeaderItem(n,header_item)
            self.mean_prior_table.setRowCount(ncomp)
            self.mean_prior_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
            self.mean_prior_table.horizontalHeader().setBackgroundRole(QtGui.QPalette.ColorRole.Highlight)
            for i in range(ncomp):
                icon_pm = QtGui.QPixmap(50,50)
                icon_pm.fill(QtGui.QColor(self.fit_colors[i]))
                icon = QtGui.QIcon(icon_pm)
                item = QtWidgets.QTableWidgetItem(icon,'{}'.format(i+1))
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.mean_prior_table.setVerticalHeaderItem(i,item)

    def get_mean_posteriors(self):
        means = []
        for i in range(self.mean_prior_table.rowCount()):
            row = []
            for j in range(int(self.numberOfFeaturesEdit.text())):
                if not self.mean_prior_table.item(i,j*2+1):
                    row.append(0)
                else:
                    row.append(float(self.mean_prior_table.item(i,j*2+1).text()))
            means.append(row)
        return means

    def get_mean_priors(self):
        means = []
        for i in range(self.mean_prior_table.rowCount()):
            row = []
            for j in range(int(self.numberOfFeaturesEdit.text())):
                if not self.mean_prior_table.item(i,j*2):
                    row.append(0)
                else:
                    row.append(float(self.mean_prior_table.item(i,j*2).text()))
            means.append(row)
        return means

    def set_default_mean_priors(self):
        self.numberOfComponentsEdit.setText(str(len(self.default_means)))
        for i in range(len(self.default_means)):
            for j in range(int(self.numberOfFeaturesEdit.text())):
                if not self.mean_prior_table.item(i,j*2):
                    item = QtWidgets.QTableWidgetItem('{:.2f}'.format(self.default_means[i][j]))
                    item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                    self.mean_prior_table.setItem(i,2*j,item)
                else:
                    self.mean_prior_table.item(i,2*j).setText('{:.2f}'.format(self.default_means[i][j]))

    def update_mean_posteriors(self,means):
        for i in range(int(self.numberOfComponentsEdit.text())):
            for j in range(int(self.numberOfFeaturesEdit.text())):
                if not self.mean_prior_table.item(i,2*j+1):
                    item = QtWidgets.QTableWidgetItem('{:.2f}'.format(means[i,j]))
                    item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                    self.mean_prior_table.setItem(i,2*j+1,item)
                else:
                    self.mean_prior_table.item(i,2*j+1).setText('{:.2f}'.format(means[i,j]))

    def update_mean_priors(self):
        for i in range(int(self.numberOfComponentsEdit.text())):
            for j in range(int(self.numberOfFeaturesEdit.text())):
                value = float(self.mean_prior_table.item(i,j*2+1).text())
                if not self.mean_prior_table.item(i,2*j):
                    item = QtWidgets.QTableWidgetItem('{:.2f}'.format(value))
                    item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                    self.mean_prior_table.setItem(i,2*j,item)
                else:
                    self.mean_prior_table.item(i,2*j).setText('{:.2f}'.format(value))

    def covar_prior_table_initialize(self,text):
        ncomp = int(text)
        nfeatures = int(self.numberOfFeaturesEdit.text())
        self.covarTab.clear()
        if nfeatures > 3:
            self.mean_prior_table.clear()
            self.raise_error('Dimension > 3 not supported')
        else:
            for i in range(int(ncomp)+1):
                covar_prior_table = QtWidgets.QTableWidget()
                covar_prior_table.setColumnCount(nfeatures)
                for j in range(nfeatures):
                    header_item = QtWidgets.QTableWidgetItem('C{}'.format(j))
                    covar_prior_table.setHorizontalHeaderItem(j,header_item)
                covar_prior_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
                covar_prior_table.horizontalHeader().setBackgroundRole(QtGui.QPalette.ColorRole.Highlight)
                covar_prior_table.setMinimumHeight(200)
                covar_prior_table.setRowCount(nfeatures)
                for j in range(nfeatures):
                    item = QtWidgets.QTableWidgetItem('R{}'.format(j))
                    item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                    covar_prior_table.setVerticalHeaderItem(j,item)
                if i == 0:
                    self.covarTab.addTab(covar_prior_table,"Prior")
                else:
                    icon_pm = QtGui.QPixmap(50,50)
                    icon_pm.fill(QtGui.QColor(self.fit_colors[i-1]))
                    icon = QtGui.QIcon(icon_pm)
                    self.covarTab.addTab(covar_prior_table,icon,"{}".format(i))

    def covar_prior_table_change_features(self,text):
        nfeatures = int(text)
        self.covarTab.clear()
        if nfeatures > 3:
            self.mean_prior_table.clear()
            self.raise_error('Dimension > 3 not supported')
        else:
            for i in range(int(self.numberOfComponentsEdit.text())+1):
                covar_prior_table = QtWidgets.QTableWidget()
                covar_prior_table.setColumnCount(nfeatures)
                for j in range(nfeatures):
                    header_item = QtWidgets.QTableWidgetItem('C{}'.format(j))
                    covar_prior_table.setHorizontalHeaderItem(j,header_item)
                covar_prior_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
                covar_prior_table.horizontalHeader().setBackgroundRole(QtGui.QPalette.ColorRole.Highlight)
                covar_prior_table.setMinimumHeight(200)
                covar_prior_table.setRowCount(nfeatures)
                for j in range(nfeatures):
                    item = QtWidgets.QTableWidgetItem('R{}'.format(j))
                    item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                    covar_prior_table.setVerticalHeaderItem(j,item)
                if i == 0:
                    self.covarTab.addTab(covar_prior_table,"Prior")
                else:
                    icon_pm = QtGui.QPixmap(50,50)
                    icon_pm.fill(QtGui.QColor(self.fit_colors[i-1]))
                    icon = QtGui.QIcon(icon_pm)
                    self.covarTab.addTab(covar_prior_table,icon,"{}".format(i+1))

    def get_covar_posteriors(self):
        covars = []
        for i in range(int(self.numberOfComponentsEdit.text())+1):
            component = []
            for j in range(int(self.numberOfFeaturesEdit.text())):
                row = []
                for k in range(int(self.numberOfFeaturesEdit.text())):
                    if not self.covarTab.widget(i).item(j,k):
                        row.append(0)
                    else:
                        row.append(float(self.covarTab.widget(i).item(j,k).text()))
                component.append(row)
            covars.append(component)
        return covars

    def update_covar_posteriors(self,covars):
        for i in range(1,int(self.numberOfComponentsEdit.text())+1):
            for j in range(int(self.numberOfFeaturesEdit.text())):
                for k in range(int(self.numberOfFeaturesEdit.text())):
                    if not self.covarTab.widget(i).item(j,k):
                        item = QtWidgets.QTableWidgetItem('{:.2f}'.format(covars[i-1,j,k]))
                        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                        self.covarTab.widget(i).setItem(j,k,item)
                    else:
                        self.covarTab.widget(i).item(j,k).setText('{:.2f}'.format(covars[i-1,j,k]))

    def update_covar_priors(self):
        for j in range(int(self.numberOfFeaturesEdit.text())):
            for k in range(int(self.numberOfFeaturesEdit.text())):
                value = 0
                for i in range(1,int(self.numberOfComponentsEdit.text())+1):
                    value += float(self.covarTab.widget(i).item(j,k).text())
                value /= int(self.numberOfComponentsEdit.text())
                if not self.covarTab.widget(0).item(j,k):
                    item = QtWidgets.QTableWidgetItem('{:.2f}'.format(value))
                    item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                    self.covarTab.widget(0).setItem(j,k,item)
                else:
                    self.covarTab.widget(0).item(j,k).setText('{:.2f}'.format(value))

    def get_covar_priors(self):
        covars = []
        for j in range(int(self.numberOfFeaturesEdit.text())):
            row = []
            for k in range(int(self.numberOfFeaturesEdit.text())):
                if not self.covarTab.widget(0).item(j,k):
                    row.append(0)
                else:
                    row.append(float(self.covarTab.widget(0).item(j,k).text()))
            covars.append(row)
        return covars

    def choose_source(self):
        path = QtWidgets.QFileDialog.getOpenFileName(None,"choose the input data file","c:/users/yux20/documents/05042018 MoS2/interpolated_2D_stack_large.csv",filter="CSV (*.csv)")[0]
        self.currentSource = path
        self.chooseSourceLabel.setText("The source directory is:\n"+self.currentSource)
        self.loadButton.setEnabled(True)

    def load_data(self):
        self.update_log("Loading Data ... ")
        self.loadButton.setEnabled(False)
        QtCore.QCoreApplication.processEvents()
        try:
            self.grid_3d = pandas.read_csv(filepath_or_buffer=self.currentSource)
            self.nz = 0
            self.z_levels = np.unique(self.grid_3d["z"].to_numpy())
            if int(self.numberOfZsEdit.text()) > len(self.z_levels):
                self.numberOfZsEdit.setText(str(len(self.z_levels)))
                self.update_log("Number of Z levels truncated")
            self.informationLabel.setText(self.grid_3d.describe(include='all').applymap(lambda x: np.around(x,3)).to_string())
            self.drawSampleButton.setEnabled(True)
            self.loadButton.setEnabled(True)
            self.update_log("Loading Complete")
            self.ButtonBox.findChildren(QtWidgets.QPushButton)[0].setEnabled(True)
            self.ButtonBox.findChildren(QtWidgets.QPushButton)[1].setEnabled(False)
            self.ButtonBox.findChildren(QtWidgets.QPushButton)[2].setEnabled(True)
            self.ButtonBox.findChildren(QtWidgets.QPushButton)[3].setEnabled(True)
        except:
            self.raise_error("Wrong Input!")

    def draw_sample(self,level=0,change_buttons = True):
        if change_buttons:
            self.ButtonBox.findChildren(QtWidgets.QPushButton)[0].setEnabled(False)
            self.ButtonBox.findChildren(QtWidgets.QPushButton)[1].setEnabled(False)
            self.ButtonBox.findChildren(QtWidgets.QPushButton)[2].setEnabled(False)
            self.ButtonBox.findChildren(QtWidgets.QPushButton)[3].setEnabled(False)
            self.plotSampleButton.setEnabled(False)
            self.drawSampleButton.setEnabled(False)
        self.update_log("Drawing Samples for level {}".format(level))
        QtCore.QCoreApplication.processEvents()
        indices = []
        mask = self.grid_3d["z"]==list(self.z_levels)[level]
        for _ in range(int(self.numberOfDrawsEdit.text())):
            if self.stopped:
                break
            else:
                draw = rv_discrete(name='custm',values=(self.grid_3d[mask].index,self.grid_3d[mask]["intensity"]))
                indices.append(draw.rvs(size=int(self.numberOfSamplesEdit.text())))
                self.update_log("Draw {} finished".format(_+1))
                QtCore.QCoreApplication.processEvents()
        indices = np.concatenate(indices)
        selected = self.grid_3d.iloc[indices]
        x, y = selected["x"].to_numpy(),selected["y"].to_numpy()
        self.inputdata = np.vstack([x,y]).T
        self.update_log("Drawing for level {} Completed".format(level))
        if change_buttons:
            self.ButtonBox.findChildren(QtWidgets.QPushButton)[0].setEnabled(True)
            self.ButtonBox.findChildren(QtWidgets.QPushButton)[1].setEnabled(False)
            self.ButtonBox.findChildren(QtWidgets.QPushButton)[2].setEnabled(True)
            self.ButtonBox.findChildren(QtWidgets.QPushButton)[3].setEnabled(True)
            self.plotSampleButton.setEnabled(True)
            self.drawSampleButton.setEnabled(True)

    def plot_sample(self,level=0):
        self.update_log("Plotting Samples... ")
        QtCore.QCoreApplication.processEvents()
        self.distributionChart.add_chart(self.inputdata[:,0],self.inputdata[:,1],'scatter')
        self.update_log("Plotting Complete")
        self.scatter_exist = True

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
        if self.meanPriorCheck.isChecked():
            mean_priors = self.get_mean_priors()
        else:
            mean_priors = None
        if self.covarPriorCheck.isChecked():
            covar_priors = self.get_covar_priors()
        else:
            covar_priors = None
        self.estimator = My_GMM(
            n_components= int(self.numberOfComponentsEdit.text()), 
            covariance_type=self.covarianceTypeCombo.currentText(),
            tol=float(self.tolEdit.text()),
            reg_covar=float(self.regCovarEdit.text()), 
            max_iter=int(self.maxItrEdit.text()), 
            n_init=int(self.nInitEdit.text()),
            init_params=self.initMethodTypeCombo.currentText(),
            weight_concentration_prior_type=self.wcPriorTypeCombo.currentText(),
            mean_precision_prior=float(self.meanPrecPriorEdit.text()),
            mean_prior=None,
            mean_priors=mean_priors,
            degrees_of_freedom_prior=int(self.dofEdit.text()) if self.dofEdit.text() != '' else None,
            covariance_prior=covar_priors,
            random_state=int(self.rsEdit.text()), 
            warm_start=self.warmStartCheck.isChecked(),
            verbose=int(self.vbEdit.text()), 
            verbose_interval=int(self.vbIntvEdit.text()),
            weight_concentration_prior=float(self.wcPriorEdit.text()))

        self.cost_series_X = [1]
        self.cost_series_Y = [1]
        if not self.scatter_exist:
            self.distributionChart.add_chart(self.inputdata[:,0],self.inputdata[:,1],'scatter')
        self.estimator.load_input(self.inputdata)
        self.estimator.UPDATE_LOG.connect(self.update_log)
        self.estimator.SEND_UPDATE.connect(self.update_plots)
        self.estimator.moveToThread(self.thread)
        self.estimator.FINISHED.connect(self.thread.quit)
        self.estimator.FINISHED.connect(self.process_finished)
        self.thread.started.connect(self.estimator.run)
        self.STOP_WORKER.connect(self.estimator.stop)
        return True

    def start(self):
        if self.stopped:
            self.stopped = False
            self.nz  = 0
        if self.nz == int(self.numberOfZsEdit.text()):
            self.nz = 0
        self.update_log("Z level {} started".format(self.nz))
        if not hasattr(self,'inputdata'):
            self.draw_sample(0)
        ready = self.prepare()
        if ready:
            self.thread.start()
            self.ButtonBox.findChildren(QtWidgets.QPushButton)[0].setEnabled(False)
            self.ButtonBox.findChildren(QtWidgets.QPushButton)[1].setEnabled(True)
            self.ButtonBox.findChildren(QtWidgets.QPushButton)[2].setEnabled(False)
            self.ButtonBox.findChildren(QtWidgets.QPushButton)[3].setEnabled(False)
            self.fitOptions.setEnabled(False)

    def stop(self):
        self.stopped = True
        self.nz = int(self.numberOfZsEdit.text()) + 1
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
        if not self.stopped:
            self.update_log("Z level {} finished".format(self.nz))
            self.nz += 1
            if self.thread.isRunning():
                self.thread.terminate()
                self.thread.wait()
            self.ButtonBox.findChildren(QtWidgets.QPushButton)[1].setEnabled(False)
            QtCore.QCoreApplication.processEvents()
            time.sleep(0.5)
            self.ButtonBox.findChildren(QtWidgets.QPushButton)[1].setEnabled(True)
            if self.nz < int(self.numberOfZsEdit.text()):
                self.draw_sample(self.nz,False)
                #self.update_mean_priors()
                #self.update_covar_priors()
                self.start()
        if self.stopped or self.nz == int(self.numberOfZsEdit.text()):
            self.ButtonBox.findChildren(QtWidgets.QPushButton)[0].setEnabled(True)
            self.ButtonBox.findChildren(QtWidgets.QPushButton)[1].setEnabled(False)
            self.ButtonBox.findChildren(QtWidgets.QPushButton)[2].setEnabled(True)
            self.ButtonBox.findChildren(QtWidgets.QPushButton)[3].setEnabled(True)
            self.fitOptions.setEnabled(True)

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
            self.cost_series_Y.append(np.abs(change))
            self.costChart.add_chart(self.cost_series_X, self.cost_series_Y,'ELBO change')
            self.distributionChart.append_to_chart(x=means[:,0],y=means[:,1],a=a,b=b,angle=angle,weights=weights,colors=colors,type='ellipse')
            self.weightChart.add_chart(weights=weights,colors=colors,type='bar')
            self.update_covar_posteriors(covars)
            self.update_mean_posteriors(means)

    def write_results(self,results):
        self.fitting_results.append(results)

    def close_results(self):
        for result in self.fitting_results:
            self.output.write(result)
        self.output.close()

    def update_log(self,message):
        self.logBox.append(QtCore.QTime.currentTime().toString("hh:mm:ss")+"\u00A0\u00A0\u00A0\u00A0" + message)
        self.logBox.moveCursor(QtGui.QTextCursor.MoveOperation.End)

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
                    item.setForeground(QtGui.QBrush(QtGui.QColor(QtCore.Qt.GlobalColor.red)))
                    item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                    item2.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                    item3.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
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
                   item.setForeground(QtGui.QBrush(QtGui.QColor(QtCore.Qt.GlobalColor.red)))
                   item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                   item2.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                   item3.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                   self.table.setItem(i,j,item)
                   self.table.setItem(i,j+1,item2)
                   self.table.setItem(i,j+2,item3)
                   index+=1
        self.FEED_BACK_TO_FIT_WORKER.emit(self.guess, (self.bound_low,self.bound_high))

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
                 mean_precision_prior=None, mean_prior=None,mean_priors=None,
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
        self.mean_priors = mean_priors

    def _initialize(self, X, resp):
        """Initialization of the mixture parameters.
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
        resp : array-like of shape (n_samples, n_components)
        """
        nk, xk, sk = _estimate_gaussian_parameters(X, resp, self.reg_covar,
                                                   self.covariance_type)

        self._estimate_weights(nk)
        self._estimate_means(nk, xk,True)
        self._estimate_precisions(nk, xk, sk,True)

    def _estimate_precisions(self, nk, xk, sk,initialize=False):
        """Estimate the precisions parameters of the precision distribution.
        Parameters
        ----------
        nk : array-like of shape (n_components,)
        xk : array-like of shape (n_components, n_features)
        sk : array-like
            The shape depends of `covariance_type`:
            'full' : (n_components, n_features, n_features)
            'tied' : (n_features, n_features)
            'diag' : (n_components, n_features)
            'spherical' : (n_components,)
        """
        {"full": self._estimate_wishart_full,
         "tied": self._estimate_wishart_tied,
         "diag": self._estimate_wishart_diag,
         "spherical": self._estimate_wishart_spherical
         }[self.covariance_type](nk, xk, sk,initialize)

        self.precisions_cholesky_ = _compute_precision_cholesky(
            self.covariances_, self.covariance_type)

    def _estimate_means(self, nk, xk,initial=False):
        """Estimate the parameters of the Gaussian distribution.
        Parameters
        ----------
        nk : array-like of shape (n_components,)
        xk : array-like of shape (n_components, n_features)
        """
        if self.mean_priors and initial:
            self.mean_precision_ = self.mean_precision_prior_ + nk
            self.means_=np.array(self.mean_priors)
        else:
            self.mean_precision_ = self.mean_precision_prior_ + nk
            self.means_ = ((self.mean_precision_prior_ * self.mean_prior_ +
                            nk[:, np.newaxis] * xk) /
                        self.mean_precision_[:, np.newaxis])

    def _estimate_wishart_full(self, nk, xk, sk,initialize=False):
        """Estimate the full Wishart distribution parameters.
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
        nk : array-like of shape (n_components,)
        xk : array-like of shape (n_components, n_features)
        sk : array-like of shape (n_components, n_features, n_features)
        """
        _, n_features = xk.shape

        # Warning : in some Bishop book, there is a typo on the formula 10.63
        # `degrees_of_freedom_k = degrees_of_freedom_0 + Nk` is
        # the correct formula
        self.degrees_of_freedom_ = self.degrees_of_freedom_prior_ + nk

        self.covariances_ = np.empty((self.n_components, n_features,
                                      n_features))

        if not initialize:
            for k in range(self.n_components):
                diff = xk[k] - self.mean_prior_
                self.covariances_[k] = (self.covariance_prior_ + nk[k] * sk[k] +
                                        nk[k] * self.mean_precision_prior_ /
                                        self.mean_precision_[k] * np.outer(diff,
                                                                        diff))
            # Contrary to the original bishop book, we normalize the covariances
            self.covariances_ /= (
                self.degrees_of_freedom_[:, np.newaxis, np.newaxis])
        else:
            for k in range(self.n_components):
                self.covariances_[k] = self.covariance_prior_

    def _estimate_wishart_tied(self, nk, xk, sk,initialize=False):
        """Estimate the tied Wishart distribution parameters.
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
        nk : array-like of shape (n_components,)
        xk : array-like of shape (n_components, n_features)
        sk : array-like of shape (n_features, n_features)
        """
        _, n_features = xk.shape

        # Warning : in some Bishop book, there is a typo on the formula 10.63
        # `degrees_of_freedom_k = degrees_of_freedom_0 + Nk`
        # is the correct formula
        self.degrees_of_freedom_ = (
            self.degrees_of_freedom_prior_ + nk.sum() / self.n_components)

        diff = xk - self.mean_prior_
        if not initialize:
            self.covariances_ = (
                self.covariance_prior_ + sk * nk.sum() / self.n_components +
                self.mean_precision_prior_ / self.n_components * np.dot(
                    (nk / self.mean_precision_) * diff.T, diff))
            # Contrary to the original bishop book, we normalize the covariances
            self.covariances_ /= self.degrees_of_freedom_
        else:
            self.covariances_ = self.covariance_prior_

    def _estimate_wishart_diag(self, nk, xk, sk,initialize=False):
        """Estimate the diag Wishart distribution parameters.
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
        nk : array-like of shape (n_components,)
        xk : array-like of shape (n_components, n_features)
        sk : array-like of shape (n_components, n_features)
        """
        _, n_features = xk.shape

        # Warning : in some Bishop book, there is a typo on the formula 10.63
        # `degrees_of_freedom_k = degrees_of_freedom_0 + Nk`
        # is the correct formula
        self.degrees_of_freedom_ = self.degrees_of_freedom_prior_ + nk

        diff = xk - self.mean_prior_
        if not initialize:
            self.covariances_ = (
                self.covariance_prior_ + nk[:, np.newaxis] * (
                    sk + (self.mean_precision_prior_ /
                        self.mean_precision_)[:, np.newaxis] * np.square(diff)))
            # Contrary to the original bishop book, we normalize the covariances
            self.covariances_ /= self.degrees_of_freedom_[:, np.newaxis]
        else:
            self.covariances_ = self.covariance_prior_

    def _estimate_wishart_spherical(self, nk, xk, sk,initialize=False):
        """Estimate the spherical Wishart distribution parameters.
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
        nk : array-like of shape (n_components,)
        xk : array-like of shape (n_components, n_features)
        sk : array-like of shape (n_components,)
        """
        _, n_features = xk.shape

        # Warning : in some Bishop book, there is a typo on the formula 10.63
        # `degrees_of_freedom_k = degrees_of_freedom_0 + Nk`
        # is the correct formula
        self.degrees_of_freedom_ = self.degrees_of_freedom_prior_ + nk

        diff = xk - self.mean_prior_
        if not initialize:
            self.covariances_ = (
                self.covariance_prior_ + nk * (
                    sk + self.mean_precision_prior_ / self.mean_precision_ *
                    np.mean(np.square(diff), 1)))
            # Contrary to the original bishop book, we normalize the covariances
            self.covariances_ /= self.degrees_of_freedom_
        else:
            self.covariances_ = self.covariance_prior_


    def load_input(self,X,y=None):
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
