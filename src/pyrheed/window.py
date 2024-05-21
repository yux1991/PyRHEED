from process import Image
from PyQt6 import QtCore, QtGui, QtWidgets
import browser
import canvas
import configparser
import cursor
import numpy as np
import os
import profile_chart
import properties
import time

class Window(QtWidgets.QMainWindow):

    #Public Signals
    FILE_OPENED = QtCore.pyqtSignal(str)
    IMG_CREATED = QtCore.pyqtSignal(np.ndarray)
    SCALE_FACTOR_CHANGED = QtCore.pyqtSignal(float)
    CANVAS_SCALE_FACTOR_CHANGED = QtCore.pyqtSignal(float)
    LABEL_CHANGED = QtCore.pyqtSignal(float,float,str,int)
    CALIBRATION_CHANGED = QtCore.pyqtSignal(float,float,str,int)
    PROGRESS_ADVANCE = QtCore.pyqtSignal(int,int,int)
    PROGRESS_END = QtCore.pyqtSignal()
    DEFAULT_PROPERTIES_REQUESTED = QtCore.pyqtSignal()
    RECIPROCAL_SPACE_MAPPING_REQUESTED = QtCore.pyqtSignal(str)
    THREE_DIMENSIONAL_GRAPH_REQUESTED = QtCore.pyqtSignal(str)
    BROADENING_REQUESTED = QtCore.pyqtSignal(str)
    GMM_REQUESTED = QtCore.pyqtSignal(str)
    MANUAL_FIT_REQUESTED = QtCore.pyqtSignal(str,int)
    STATISTICAL_FACTOR_REQUESTED = QtCore.pyqtSignal()
    DIFFRACTION_PATTERN_REQUESTED = QtCore.pyqtSignal()
    KIKUCHI_PATTERN_REQUESTED = QtCore.pyqtSignal()
    GENERATE_REPORT_REQUESTED = QtCore.pyqtSignal(str)
    WINDOW_INITIALIZED = QtCore.pyqtSignal()
    PROPERTIES_REFRESH = QtCore.pyqtSignal(configparser.ConfigParser)
    CANVAS_REFRESH = QtCore.pyqtSignal(configparser.ConfigParser)
    CHART_REFRESH = QtCore.pyqtSignal(configparser.ConfigParser)
    RETURN_STATUS = QtCore.pyqtSignal(dict)
    SCENARIO_REQUESTED = QtCore.pyqtSignal()
    TOGGLE_DARK_MODE = QtCore.pyqtSignal(str)

    def __init__(self,config):

        super(Window, self).__init__()
        self.currentPath = ''
        self._mode = "pan"
        self.isDarkMode = False
        self.photoList = []
        self.pathList = []
        self.tabClosed = False
        self.config = config
        self.image_worker = Image()

        #Defaults
        self.windowDefault = dict(self.config['windowDefault'].items())
        self.propertiesDefault = dict(self.config['propertiesDefault'].items())
        self.canvasDefault = dict(self.config['canvasDefault'].items())
        self.chartDefault = dict(self.config['chartDefault'].items())
        self.HS = int(self.windowDefault['hs'])
        self.VS = int(self.windowDefault['vs'])
        self.energy = int(self.windowDefault['energy'])
        self.azimuth = int(self.windowDefault['azimuth'])
        self.scaleBarLength = int(self.windowDefault['scalebarlength'])
        self.chiRange = int(self.windowDefault['chirange'])
        self.width = float(self.windowDefault['width'])
        self.widthSliderScale = int(self.windowDefault['widthsliderscale'])
        self.radius = int(self.windowDefault['radius'])
        self.radiusMaximum = int(self.windowDefault['radiusmaximum'])
        self.radiusSliderScale = int(self.windowDefault['radiussliderscale'])
        self.tiltAngle = int(self.windowDefault['tiltangle'])
        self.tiltAngleSliderScale = int(self.windowDefault['tiltanglesliderscale'])

        #Menu bar
        self.menu = QtWidgets.QMenuBar()
        self.menuFile = self.menu.addMenu("File")
        self.menuPreference = self.menu.addMenu("Preference")
        self.menu2DMap = self.menu.addMenu("Mapping")
        self.menuFit = self.menu.addMenu("Fit")
        self.menuSimulation = self.menu.addMenu("Simulation")
        self.menuRun = self.menu.addMenu("Run")
        self.menuHelp = self.menu.addMenu("Help")
        self.setMenuBar(self.menu)

        #File Menu
        self.openFile = self.menuFile.addAction("Open",self.manu_actions_open)
        self.export = self.menuFile.addMenu("Export")
        self.saveCanvasAsImage = self.export.addAction("RHEED pattern as Image",self.menu_actions_save_as_image)
        self.saveProfileAsText = self.export.addAction("Line profile as text",self.menu_actions_save_as_text)
        self.saveProfileAsImage = self.export.addAction("Line profile as image",self.menu_actions_save_profile_as_image)
        self.saveProfileAsSVG = self.export.addAction("Line profile as SVG",self.menu_actions_save_as_svg)

        #Preference Menu
        self.defaultSettings = self.menuPreference.addAction("Default Settings",\
                                    self.menu_actions_preferences_default_settings)

        #2D Map Menu
        self.Two_Dimensional_Mapping = self.menu2DMap.addAction("Configuration", \
                                            self.menu_actions_two_dimensional_mapping)

        self.Three_Dimensional_Graph = self.menu2DMap.addAction("3D Surface", \
                                        self.menu_actions_three_dimensional_graph)

        #Fit Menu
        self.Fit_Broadening = self.menuFit.addAction("Broadening",self.menu_actions_broadening)
        self.Fit_ManualFit = self.menuFit.addAction("Manual Fit", self.menu_actions_show_manual_fit)
        self.Fit_Report = self.menuFit.addAction("Generate Report", self.menu_actions_generate_report)
        self.gmm = self.menuFit.addAction("Gaussian Mixture Modeling",self.menu_actions_gmm)

        #Simulation Menu
        self.Statistical_Factor = self.menuSimulation.addAction("Statistical Factor",self.menu_actions_statistical_factor)
        self.Diffraction_pattern = self.menuSimulation.addAction("Diffraction Pattern",self.menu_actions_diffraction_pattern)
        self.Kikuchi_pattern = self.menuSimulation.addAction("Kikuchi Pattern",self.menu_actions_kikuchi_pattern)

        #Run Menu
        self.run_scenario = self.menuRun.addAction("Run Scenario", self.menu_action_run_scenario)

        #Help Menu
        self.about = self.menuHelp.addAction("About",self.menu_actions_about)

        #Center Widget
        self.image_crop = [1200+self.VS,2650+self.VS,500+self.HS,3100+self.HS]

        self.mainSplitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        self.mainTab = QtWidgets.QTabWidget()
        self.mainTab.setContentsMargins(0,0,0,0)
        self.mainTab.setTabsClosable(True)
        self.controlPanelFrame = QtWidgets.QWidget(self)
        self.controlPanelGrid = QtWidgets.QGridLayout(self.controlPanelFrame)
        self.controlPanelGrid.setContentsMargins(0,0,0,0)
        self.controlPanelSplitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        supportedFormats =    {'*.3fr','*.ari','*.arw','*.srf', '*.sr2','*.bay','*.cri','*.crw', '*.cr2',     '*.cr3', '*.cap','*.iiq','*.eip',\
                               '*.dcs','*.dcr','*.drf','*.k25', '*.kdc','*.dng','*.erf','*.fff', '*.mef',     '*.mdc', '*.mos','*.mrw','*.nef',\
                               '*.nrw','*.orf','*.pef','*.ptx', '*.pxn','*.r3d','*.raf','*.raw', '*.rw2',     '*.rwl', '*.rwz','*.srw','*.x3f',\
                               '*.3FR','*.ARI','*.ARW','*.SRF', '*.SR2','*.BAY','*.CRI','*.CRW', '*.CR2',     '*.CR3', '*.CAP','*.IIQ','*.EIP',\
                               '*.DCS','*.DCR','*.DRF','*.K25', '*.KDC','*.DNG','*.ERF','*.FFF', '*.MEF',     '*.MDC', '*.MOS','*.MRW','*.NEF',\
                               '*.NRW','*.ORF','*.PEF','*.PTX', '*.PXN','*.R3D','*.RAF','*.RAW', '*.RW2',     '*.RWL', '*.RWZ','*.SRW','*.X3F',\
                               '*.bmp','*.eps','*.gif','*.icns','*.ico','*.im', '*.jpg','*.jpeg','*.jpeg2000','*.msp', '*.pcx','*.png','*.ppm',\
                               '*.sgi','*.tiff','*.tif','*.xbm','*.BMP','*.EPS','*.GIF','*.ICNS','*.ICO',     '*.IM',  '*.JPG','*.JPEG','*.JPEG2000',\
                               '*.MSP','*.PCX','*.PNG','*.PPM','*.SGI','*.TIFF','*.TIF','*.XBM'}

        self.browser_widget = browser.Browser(self,supportedFormats)
        self.controlPanelBottomWidget = QtWidgets.QWidget()
        self.controlPanelBottomGrid = QtWidgets.QGridLayout(self.controlPanelBottomWidget)
        self.controlPanelBottomGrid.setContentsMargins(0,0,2,0)
        self.properties_widget = properties.Properties(self,self.config)
        self.cursorInfo = cursor.Cursor(self)
        self.profile = profile_chart.ProfileChart(self.config)
        self.controlPanelBottomGrid.addWidget(self.properties_widget,0,0)
        self.controlPanelBottomGrid.addWidget(self.cursorInfo,1,0)
        self.controlPanelBottomGrid.addWidget(self.profile,2,0)
        self.controlPanelSplitter.addWidget(self.browser_widget)
        self.controlPanelSplitter.addWidget(self.controlPanelBottomWidget)

        self.controlPanelSplitter.setSizes([100,500])
        self.controlPanelSplitter.setStretchFactor(0,1)
        self.controlPanelSplitter.setStretchFactor(1,1)
        self.controlPanelSplitter.setCollapsible(0,False)
        self.controlPanelSplitter.setCollapsible(1,False)
        self.controlPanelGrid.addWidget(self.controlPanelSplitter,0,0)

        self.mainSplitter.addWidget(self.mainTab)
        self.mainSplitter.addWidget(self.controlPanelFrame)
        self.mainSplitter.setSizes([2000,400])
        self.mainSplitter.setStretchFactor(0,1)
        self.mainSplitter.setStretchFactor(1,1)
        self.mainSplitter.setCollapsible(0,False)
        self.mainSplitter.setCollapsible(1,False)


        #Tool bar
        self.toolBar = QtWidgets.QToolBar(self)
        self.toolBar.setFloatable(False)
        self.toolBar.setMovable(False)
        self.dirname = os.path.dirname(__file__)
        self.open = QtGui.QAction(QtGui.QIcon(os.path.join(self.dirname,"data/icons/open.svg")), "open", self)
        self.saveAs = QtGui.QAction(QtGui.QIcon(os.path.join(self.dirname,"data/icons/save as.svg")), "save as", self)
        self.zoomIn = QtGui.QAction(QtGui.QIcon(os.path.join(self.dirname,"data/icons/zoom in.svg")), "zoom in (Ctrl + Plus)", self)
        self.zoomIn.setShortcut(QtGui.QKeySequence.StandardKey.ZoomIn)
        self.zoomOut = QtGui.QAction(QtGui.QIcon(os.path.join(self.dirname,"data/icons/zoom out.svg")), "zoom out (Ctrl + Minus)", self)
        self.zoomOut.setShortcut(QtGui.QKeySequence.StandardKey.ZoomOut)
        self.fitCanvas = QtGui.QAction(QtGui.QIcon(os.path.join(self.dirname,"data/icons/fit.svg")), "fit in view",self)
        self.line = QtGui.QAction(QtGui.QIcon(os.path.join(self.dirname,"data/icons/line.svg")), "line", self)
        self.line.setCheckable(True)
        self.rectangle = QtGui.QAction(QtGui.QIcon(os.path.join(self.dirname,"data/icons/rectangle.svg")), "rectangle", self)
        self.rectangle.setCheckable(True)
        self.arc = QtGui.QAction(QtGui.QIcon(os.path.join(self.dirname,"data/icons/arc.svg")), "arc", self)
        self.arc.setCheckable(True)
        self.pan = QtGui.QAction(QtGui.QIcon(os.path.join(self.dirname,"data/icons/move.svg")), "pan", self)
        self.pan.setCheckable(True)
        self.flipud = QtGui.QAction(QtGui.QIcon(os.path.join(self.dirname,"data/icons/flipud.svg")), "flipud", self)
        self.fliplr = QtGui.QAction(QtGui.QIcon(os.path.join(self.dirname,"data/icons/fliplr.svg")), "fliplr", self)
        self.lightMode = QtGui.QAction(QtGui.QIcon(os.path.join(self.dirname,"data/icons/dark.svg")), "dark mode", self)
        self.lightMode.setCheckable(True)
        self.darkMode = QtGui.QAction(QtGui.QIcon(os.path.join(self.dirname,"data/icons/light.svg")), "light mode", self)
        self.darkMode.setCheckable(True)
        self.buttonModeGroup = QtGui.QActionGroup(self.toolBar)
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
        self.toolBar.addAction(self.flipud)
        self.toolBar.addAction(self.fliplr)
        self.toolBar.addAction(self.fitCanvas)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.darkMode)
        self.addToolBar(self.toolBar)

        #Status bar
        self.statusBar = QtWidgets.QStatusBar(self)
        self.messageLoadingImage = QtWidgets.QLabel("Processing ... ",self)
        self.messageLoadingImage.setVisible(False)
        self.progressBar = QtWidgets.QProgressBar(self)
        self.progressBar.setMaximumHeight(12)
        self.progressBar.setVisible(False)
        self.progressBar.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.progressBarSizePolicy = self.progressBar.sizePolicy()
        self.progressBarSizePolicy.setRetainSizeWhenHidden(True)
        self.progressBarSizePolicy.setHorizontalPolicy(QtWidgets.QSizePolicy.Policy.Expanding)
        self.progressBar.setSizePolicy(self.progressBarSizePolicy)
        self.editPixInfo = QtWidgets.QLabel(self)
        self.editPixInfo.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.editPixInfo.setMinimumWidth(150)
        self.statusBar.addWidget(self.messageLoadingImage)
        self.statusBar.insertPermanentWidget(1,self.progressBar)
        self.statusBar.addPermanentWidget(self.editPixInfo)
        self.setStatusBar(self.statusBar)

        #Main Window Settings
        self.setCentralWidget(self.mainSplitter)
        self.mainSplitter.setContentsMargins(2,2,0,0)
        self.setWindowTitle("PyRHEED")

        #Main Tab Connections
        self.mainTab.currentChanged.connect(self.switch_tab)
        self.mainTab.tabCloseRequested.connect(self.close_tab)

        #Toolbar Connections
        self.open.triggered.connect(lambda path: self.open_image(path=self.get_img_path()))
        self.line.triggered.connect(lambda cursormode: self.toggle_canvas_mode(cursormode="line"))
        self.rectangle.triggered.connect(lambda cursormode: self.toggle_canvas_mode(cursormode="rectangle"))
        self.arc.triggered.connect(lambda cursormode: self.toggle_canvas_mode(cursormode="arc"))
        self.pan.triggered.connect(lambda cursormode: self.toggle_canvas_mode(cursormode="pan"))
        self.flipud.triggered.connect(self.flip_image_up_down)
        self.fliplr.triggered.connect(self.flip_image_left_right)
        self.lightMode.triggered.connect(lambda mode: self.toggle_dark_mode(mode="light"))
        self.darkMode.triggered.connect(lambda mode: self.toggle_dark_mode(mode="dark"))

        #Progress Bar Connections
        self.PROGRESS_ADVANCE.connect(self.progress)
        self.PROGRESS_END.connect(self.progress_reset)

        #Browser Connections
        self.FILE_OPENED.connect(self.browser_widget.tree_update)
        self.IMG_CREATED.connect(self.profile.set_img)
        self.browser_widget.FILE_DOUBLE_CLICKED.connect(self.open_image)

        #Parameters Page Connections
        self.properties_widget.sensitivityEdit.textChanged.connect(self.check_sensitivity)
        self.properties_widget.energyEdit.textChanged.connect(self.change_energy)
        self.properties_widget.azimuthEdit.textChanged.connect(self.change_azimuth)
        self.properties_widget.scaleBarEdit.textChanged.connect(self.change_scale_bar)
        self.properties_widget.labelButton.clicked.connect(self.label_image)
        self.properties_widget.calibrateButton.clicked.connect(self.calibrate_image)

        #Image Adjust Page Connections
        self.properties_widget.brightnessSlider.valueChanged.connect(self.change_brightness)
        self.properties_widget.blackLevelSlider.valueChanged.connect(self.change_black_level)
        self.properties_widget.autoWBCheckBox.stateChanged.connect(self.change_auto_WB)
        self.properties_widget.applyButton2.clicked.connect(self.apply_image_adjusts)
        self.properties_widget.resetButton2.clicked.connect(self.reset_image_adjusts)

        #Profile Options Page Connections
        self.properties_widget.integralHalfWidthSlider.valueChanged.connect(self.change_width)
        self.properties_widget.chiRangeSlider.valueChanged.connect(self.change_chi_range)
        self.properties_widget.radiusSlider.valueChanged.connect(self.change_radius)
        self.properties_widget.tiltAngleSlider.valueChanged.connect(self.change_tilt_angle)
        self.properties_widget.applyButton3.clicked.connect(self.apply_profile_options)
        self.properties_widget.resetButton3.clicked.connect(self.reset_profile_options)

        #Appearance Page Connections
        self.profile.set_fonts(self.properties_widget.fontList.currentFont().family(),self.properties_widget.chartFontSizeSlider.value())
        self.properties_widget.CHART_FONTS_CHANGED.connect(self.profile.adjust_fonts)

        #Cursor Information Connections
        self.cursorInfo.choosedXYEdit.textChanged.connect(self.edit_choosed_XY)
        self.cursorInfo.startXYEdit.textChanged.connect(self.edit_start_XY)
        self.cursorInfo.endXYEdit.textChanged.connect(self.edit_end_XY)
        self.cursorInfo.widthEdit.textEdited.connect(self.edit_width)

        #Profile Canvas Connections
        self.SCALE_FACTOR_CHANGED.connect(self.profile.set_scale_factor)
        self.profile.CHART_MOUSE_MOVEMENT.connect(self.photo_mouse_movement)

        #Refresh Connections
        self.PROPERTIES_REFRESH.connect(self.properties_widget.refresh)
        self.CHART_REFRESH.connect(self.profile.refresh)

        self.get_scale_factor()
        self.WINDOW_INITIALIZED.emit()

    def refresh(self,config):
        self.windowDefault = dict(config['windowDefault'].items())
        self.propertiesDefault = dict(config['propertiesDefault'].items())
        self.canvasDefault = dict(config['canvasDefault'].items())
        self.chartDefault = dict(config['chartDefault'].items())
        self.HS = int(self.windowDefault['hs'])
        self.VS = int(self.windowDefault['vs'])
        self.energy = int(self.windowDefault['energy'])
        self.azimuth = int(self.windowDefault['azimuth'])
        self.scaleBarLength = int(self.windowDefault['scalebarlength'])
        self.chiRange = int(self.windowDefault['chirange'])
        self.width = float(self.windowDefault['width'])
        self.widthSliderScale = int(self.windowDefault['widthsliderscale'])
        self.radius = int(self.windowDefault['radius'])
        self.radiusMaximum = int(self.windowDefault['radiusmaximum'])
        self.radiusSliderScale = int(self.windowDefault['radiussliderscale'])
        self.tiltAngle = int(self.windowDefault['tiltangle'])
        self.tiltAngleSliderScale = int(self.windowDefault['tiltanglesliderscale'])
        self.image_crop = [1200+self.VS,2650+self.VS,500+self.HS,3100+self.HS]
        self.PROPERTIES_REFRESH.emit(config)
        self.CHART_REFRESH.emit(config)
        self.CANVAS_REFRESH.emit(config)
        self.reset_image_adjusts()
        self.get_scale_factor()

    def progress(self,min,max,val):
        self.progressBar.setVisible(True)
        self.progressBar.setMinimum(min)
        self.progressBar.setMaximum(max)
        self.progressBar.setValue(val)

    def progress_reset(self):
        self.progressBar.reset()
        self.progressBar.setVisible(False)

    def manu_actions_open(self):
        self.open_image(path=self.get_img_path())

    def menu_actions_save_as_image(self):
        canvas_widget = self.mainTab.currentWidget()
        try:
            canvas_widget.save_scene()
        except:
            self.raise_error("Please open a RHEED pattern first")

    def menu_actions_statistical_factor(self):
        self.STATISTICAL_FACTOR_REQUESTED.emit()

    def menu_actions_diffraction_pattern(self):
        self.DIFFRACTION_PATTERN_REQUESTED.emit()

    def menu_actions_kikuchi_pattern(self):
        self.KIKUCHI_PATTERN_REQUESTED.emit()

    def menu_action_run_scenario(self):
        self.SCENARIO_REQUESTED.emit()

    def menu_actions_save_as_text(self):
        self.profile.save_profile_as_text()

    def menu_actions_save_profile_as_image(self):
        self.profile.save_profile_as_image()

    def menu_actions_save_as_svg(self):
        self.profile.save_profile_as_SVG()

    def menu_actions_preferences_default_settings(self):
        self.DEFAULT_PROPERTIES_REQUESTED.emit()

    def menu_actions_two_dimensional_mapping(self):
        self.RECIPROCAL_SPACE_MAPPING_REQUESTED.emit(self.currentPath)

    def menu_actions_three_dimensional_graph(self):
        self.THREE_DIMENSIONAL_GRAPH_REQUESTED.emit('')

    def menu_actions_gmm(self):
        self.GMM_REQUESTED.emit(self.currentPath)

    def menu_actions_broadening(self):
        self.BROADENING_REQUESTED.emit(self.currentPath)

    def menu_actions_show_manual_fit(self):
        self.MANUAL_FIT_REQUESTED.emit(self.currentPath,0)

    def menu_actions_generate_report(self):
        self.GENERATE_REPORT_REQUESTED.emit(self.currentPath)

    def menu_actions_about(self):
        self.raise_attention(information="Author: Yu Xiang\nEmail: yux1991@gmail.com")

    def get_scale_factor(self):
        self.scaleFactor = float(self.properties_widget.sensitivityEdit.text())/np.sqrt(float(self.properties_widget.energyEdit.text()))
        self.SCALE_FACTOR_CHANGED.emit(self.scaleFactor)
        self.CANVAS_SCALE_FACTOR_CHANGED.emit(self.scaleFactor)

    def check_input(self,text,type="int"):
        if type == "int":
            try:
                int(text)
                return True
            except ValueError:
                self.raise_error("Please input a integer number!")
                return False
        elif type == "float":
            try:
                float(text)
                return True
            except ValueError:
                self.raise_error("Please input a float number!")
                return False

    def check_sensitivity(self,sensitivity):
        if self.check_input(sensitivity,"float"):
            self.scaleFactor = float(sensitivity)/np.sqrt(float(self.properties_widget.energyEdit.text()))
            self.SCALE_FACTOR_CHANGED.emit(self.scaleFactor)
            self.CANVAS_SCALE_FACTOR_CHANGED.emit(self.scaleFactor)

    def change_energy(self,energy):
        if self.check_input(energy,"float"):
            self.scaleFactor = float(self.properties_widget.sensitivityEdit.text())/np.sqrt(float(energy))
            self.SCALE_FACTOR_CHANGED.emit(self.scaleFactor)
            self.CANVAS_SCALE_FACTOR_CHANGED.emit(self.scaleFactor)
            self.energy = float(energy)

    def change_azimuth(self,azimuth):
        if self.check_input(azimuth,"float"):
            self.azimuth = float(azimuth)

    def change_scale_bar(self,scaleBar):
        if self.check_input(scaleBar,"float"):
            self.scaleBarLength = float(scaleBar)

    def label_image(self):
        self.LABEL_CHANGED.emit(self.energy,self.azimuth,self.properties_widget.fontList.currentFont().family(),\
                               self.properties_widget.canvasFontSizeSlider.value())

    def calibrate_image(self):
        self.CALIBRATION_CHANGED.emit(self.scaleFactor,self.scaleBarLength,self.properties_widget.fontList.currentFont().family(),\
                               self.properties_widget.canvasFontSizeSlider.value())


    def change_brightness(self,brightness):
        self.properties_widget.brightnessLabel.setText('Brightness ({})'.format(brightness))

    def change_black_level(self,blackLevel):
        self.properties_widget.blackLevelLabel.setText('Black Level ({})'.format(blackLevel))

    def change_auto_WB(self):
        return

    def apply_image_adjusts(self):
        if not self.mainTab.count() == 0:
            canvas_widget = self.mainTab.currentWidget()
            self.update_image(self.currentPath,bitDepth = 16, enableAutoWB = self.properties_widget.autoWBCheckBox.isChecked(),\
                            brightness = self.properties_widget.brightnessSlider.value(),blackLevel=self.properties_widget.blackLevelSlider.value(), flipud=canvas_widget.get_flipud(), fliplr=canvas_widget.get_fliplr())
        else:
            self.update_image(self.currentPath,bitDepth = 16, enableAutoWB = self.properties_widget.autoWBCheckBox.isChecked(),\
                            brightness = self.properties_widget.brightnessSlider.value(),blackLevel=self.properties_widget.blackLevelSlider.value())

    def reset_image_adjusts(self):
        self.properties_widget.autoWBCheckBox.setChecked(False)
        self.properties_widget.brightnessSlider.setValue(int(self.propertiesDefault['brightness']))
        self.properties_widget.blackLevelSlider.setValue(int(self.propertiesDefault['blacklevel']))
        if not self.mainTab.count() == 0:
            canvas_widget = self.mainTab.currentWidget()
            self.update_image(self.currentPath,bitDepth = 16, enableAutoWB = self.properties_widget.autoWBCheckBox.isChecked(), \
                        brightness = self.properties_widget.brightnessSlider.value(),blackLevel=self.properties_widget.blackLevelSlider.value(), flipud=canvas_widget.get_flipud(), fliplr=canvas_widget.get_fliplr())
        else:
            self.update_image(self.currentPath,bitDepth = 16, enableAutoWB = self.properties_widget.autoWBCheckBox.isChecked(), \
                        brightness = self.properties_widget.brightnessSlider.value(),blackLevel=self.properties_widget.blackLevelSlider.value())

    def change_width(self,width):
        self.properties_widget.integralHalfWidthLabel.setText('Integral Half Width ({:3.2f} \u212B\u207B\u00B9)'.format(width/self.widthSliderScale))
        if not self.cursorInfo.widthEdit.text() == "":
            if self._mode == "rectangle" or self._mode == "arc":
                self.cursorInfo.widthEdit.setText('{:3.2f}'.format(width/self.widthSliderScale))
        self.update_drawing()
        for i in range(0,self.mainTab.count()):
            self.mainTab.widget(i).width = width/self.widthSliderScale * self.scaleFactor

    def change_chi_range(self,chi):
        self.properties_widget.chiRangeLabel.setText('Chi Range ({}\u00B0)'.format(chi))
        self.update_drawing()
        for i in range(0,self.mainTab.count()):
            self.mainTab.widget(i).span = chi

    def change_radius(self,radius):
        self.properties_widget.radiusLabel.setText('Radius ({:3.2f} \u212B\u207B\u00B9)'.format(radius/self.radiusSliderScale))
        if not self.mainTab.count() == 0:
            if not self.mainTab.currentWidget()._drawingArc:
                self.update_drawing()

    def change_tilt_angle(self,tilt):
        self.properties_widget.tiltAngleLabel.setText('Tilt Angle ({:2.1f}\u00B0)'.format(tilt/self.tiltAngleSliderScale))
        self.update_drawing()
        for i in range(0,self.mainTab.count()):
            self.mainTab.widget(i).tilt = tilt/self.tiltAngleSliderScale

    def apply_profile_options(self):
        if not self.mainTab.count() == 0:
            if self.mainTab.currentWidget().canvasObject == "line":
                self.mainTab.currentWidget().line_scan_signal_emit()
            if self.mainTab.currentWidget().canvasObject == "rectangle":
                self.mainTab.currentWidget().integral_signal_emit()
            if self.mainTab.currentWidget().canvasObject == "arc":
                self.mainTab.currentWidget().chi_scan_signal_emit()

    def reset_profile_options(self):
        self.properties_widget.integralHalfWidthSlider.setValue(int(self.width*self.widthSliderScale))
        self.properties_widget.chiRangeSlider.setValue(int(self.chiRange))
        self.properties_widget.radiusSlider.setValue(int(self.radius*self.radiusSliderScale))
        self.properties_widget.tiltAngleSlider.setValue(int(self.tiltAngle))
        self.apply_profile_options()

    def edit_choosed_XY(self):
        return

    def edit_start_XY(self):
        return

    def edit_end_XY(self):
        return

    def edit_width(self,width):
        self.properties_widget.integralHalfWidthSlider.setValue(int(width*self.widthSliderScale))

    def get_img_path(self):
        supportedRawFormats = {'.3fr','.ari','.arw','.srf','.sr2','.bay','.cri','.crw','.cr2','.cr3','.cap','.iiq','.eip',\
                            '.dcs','.dcr','.drf','.k25','.kdc','.dng','.erf','.fff','.mef','.mdc','.mos','.mrw','.nef',\
                            '.nrw','.orf','.pef','.ptx','.pxn','.r3d','.raf','.raw','.rw2','.rwl','.rwz','.srw','.x3f',\
                            '.3FR','.ARI','.ARW','.SRF','.SR2','.BAY','.CRI','.CRW','.CR2','.CR3','.CAP','.IIQ','.EIP',\
                            '.DCS','.DCR','.DRF','.K25','.KDC','.DNG','.ERF','.FFF','.MEF','.MDC','.MOS','.MRW','.NEF',\
                            '.NRW','.ORF','.PEF','.PTX','.PXN','.R3D','.RAF','.RAW','.RW2','.RWL','.RWZ','.SRW','.X3F'}
        supportedImageFormats = {'.bmp','.eps','.gif','.icns','.ico','.im','.jpg','.jpeg','.jpeg2000','.msp','.pcx', \
                                      '.png','.ppm','.sgi','.tiff','.tif','.xbm','.BMP','.EPS','.GIF','.ICNS','.ICO','.IM','.JPG','.JPEG','.JPEG2000','.MSP','.PCX', \
                                      '.PNG','.PPM','.SGI','.TIFF','.TIF','.XBM'}
        fileDlg = QtWidgets.QFileDialog(self)
        fileDlg.setDirectory(os.path.dirname(__file__))
        path = fileDlg.getOpenFileName(filter="All Files (*.*);;Nikon (*.nef;*.nrw);;Sony (*.arw;*.srf;*.sr2);;Canon (*.crw;*.cr2;*.cr3);;JPEG (*.jpg;*.jpeg;*.jpeg2000);;GIF (*.gif);;PNG (*.png);;TIF (*.tif;*.tiff);;BMP (*.bmp)")[0]
        if not path == '':
            if not (os.path.splitext(path)[1] in supportedRawFormats or os.path.splitext(path)[1] in supportedImageFormats):
                self.raise_error("Not supported image type!")
                return ''
            else:
                return path
        else:
            return ''

    def refresh_image(self,path,crop, bitDepth = 16, enableAutoWB=False,brightness=20,blackLevel=50):
        if not path == '':
            canvas_widget = self.mainTab.currentWidget()
            img_array = self.load_image(canvas_widget,path,bitDepth,enableAutoWB,brightness,blackLevel,crop)
            if img_array is not None:
                self.photoList.pop()
                self.photoList.append(img_array)
                self.pathList.pop()
                self.pathList.append(path)
                self.mainTab.setTabText(self.mainTab.currentIndex(), os.path.basename(path))
                canvas_widget.fit_canvas()
                canvas_widget.toggle_mode(self._mode)
                self.currentPath = path
                self.FILE_OPENED.emit(path)

    def open_image(self,path,bitDepth = 16, enableAutoWB=False,brightness=20,blackLevel=50):
        if not path == '':
            canvas_widget = canvas.Canvas(self,self.config,self.isDarkMode)
            self.connect_canvas(canvas_widget)
            self.CANVAS_SCALE_FACTOR_CHANGED.emit(self.scaleFactor)
            img_array = self.load_image(canvas_widget,path,bitDepth,enableAutoWB,brightness,blackLevel)
            if img_array is not None:
                self.photoList.append(img_array)
                self.pathList.append(path)
                self.mainTab.addTab(canvas_widget,os.path.basename(path))
                self.mainTab.setCurrentIndex(self.mainTab.count()-1)
                canvas_widget.fit_canvas()
                canvas_widget.toggle_mode(self._mode)
                self.currentPath = path
                self.FILE_OPENED.emit(path)
    
    def flip_image_up_down(self):
        canvas_widget = self.mainTab.currentWidget()
        canvas_widget.flipud()
        self.update_image(self.currentPath,bitDepth = 16, enableAutoWB = self.properties_widget.autoWBCheckBox.isChecked(),\
                           brightness = self.properties_widget.brightnessSlider.value(),blackLevel=self.properties_widget.blackLevelSlider.value(), flipud=canvas_widget.get_flipud(), fliplr=canvas_widget.get_fliplr())

    def flip_image_left_right(self):
        canvas_widget = self.mainTab.currentWidget()
        canvas_widget.fliplr()
        self.update_image(self.currentPath,bitDepth = 16, enableAutoWB = self.properties_widget.autoWBCheckBox.isChecked(),\
                           brightness = self.properties_widget.brightnessSlider.value(),blackLevel=self.properties_widget.blackLevelSlider.value(), flipud=canvas_widget.get_flipud(), fliplr=canvas_widget.get_fliplr())

    def switch_tab(self,index):
        if self.mainTab.count() > 0:
            if not self.tabClosed:
                self._img=self.photoList[index]
            self.currentPath=self.pathList[index]
            self.messageLoadingImage.setText("Path of the image: "+self.currentPath)
            self.disconnect_canvas()
            self.reconnect_canvas(self.mainTab.currentWidget())
            self.IMG_CREATED.emit(self._img)
        elif self.mainTab.count() == 0:
            self.messageLoadingImage.clear()
            self.disconnect_canvas()
        if self.tabClosed:
            self.tabClosed = False

    def close_tab(self,index):
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

    def connect_canvas(self,canvas_widget):
        #canvas signals
        canvas_widget.PHOTO_MOUSE_MOVEMENT.connect(self.photo_mouse_movement)
        canvas_widget.PHOTO_MOUSE_PRESS.connect(self.photo_mouse_press)
        canvas_widget.PHOTO_MOUSE_RELEASE.connect(self.photo_mouse_release)
        canvas_widget.PHOTO_MOUSE_DOUBLE_CLICK.connect(self.photo_mouse_double_click)
        canvas_widget.PLOT_LINE_SCAN.connect(self.profile.line_scan)
        canvas_widget.PLOT_INTEGRAL.connect(self.profile.integral)
        canvas_widget.PLOT_CHI_SCAN.connect(self.profile.chi_scan)
        canvas_widget.KEY_PRESS.connect(self.cursorInfo.chosen_region_update)
        canvas_widget.KEY_PRESS_WHILE_ARC.connect(self.cursorInfo.chi_scan_region_update)

        #canvas slots
        self.zoomIn.triggered.connect(canvas_widget.zoom_in)
        self.zoomOut.triggered.connect(canvas_widget.zoom_out)
        self.fitCanvas.triggered.connect(canvas_widget.fit_canvas)
        self.properties_widget.clearButton.clicked.connect(canvas_widget.clear_annotations)
        self.LABEL_CHANGED.connect(canvas_widget.label)
        self.CALIBRATION_CHANGED.connect(canvas_widget.calibrate)
        self.CANVAS_SCALE_FACTOR_CHANGED.connect(canvas_widget.set_scale_factor)
        self.CANVAS_REFRESH.connect(canvas_widget.refresh)
        self.properties_widget.CANVAS_FONTS_CHANGED.connect(canvas_widget.adjust_fonts)

    def disconnect_canvas(self):
        self.zoomIn.disconnect()
        self.zoomOut.disconnect()
        self.fitCanvas.disconnect()
        self.properties_widget.clearButton.disconnect()
        self.LABEL_CHANGED.disconnect()
        self.CALIBRATION_CHANGED.disconnect()
        self.CANVAS_SCALE_FACTOR_CHANGED.disconnect()

    def reconnect_canvas(self,canvas_widget):
        self.zoomIn.triggered.connect(canvas_widget.zoom_in)
        self.zoomOut.triggered.connect(canvas_widget.zoom_out)
        self.fitCanvas.triggered.connect(canvas_widget.fit_canvas)
        self.properties_widget.clearButton.clicked.connect(canvas_widget.clear_annotations)
        self.LABEL_CHANGED.connect(canvas_widget.label)
        self.CALIBRATION_CHANGED.connect(canvas_widget.calibrate)
        self.CANVAS_SCALE_FACTOR_CHANGED.connect(canvas_widget.set_scale_factor)

    def update_image(self,path,bitDepth = 16, enableAutoWB=False,brightness=20,blackLevel=50,flipud=False, fliplr=False):
        if not self.mainTab.count() == 0:
            canvas_widget = self.mainTab.currentWidget()
            img_array=self.load_image(canvas_widget,path,bitDepth,enableAutoWB,brightness,blackLevel,flipud=flipud, fliplr=fliplr)
            if img_array is not None:
                self.photoList[self.mainTab.currentIndex()]=img_array
                self.apply_profile_options()

    def load_image(self,canvas_widget,path,bitDepth = 16, enableAutoWB=False,brightness=20,blackLevel=50, crop=[], flipud=False, fliplr=False):
        self.messageLoadingImage.setText("Processing ... ")
        self.messageLoadingImage.setVisible(True)
        QtWidgets.QApplication.sendPostedEvents()
        self.messageLoadingImage.setVisible(True)
        QtWidgets.QApplication.sendPostedEvents()
        if not crop:
            crop = self.image_crop
        qImg,img_array = self.image_worker.get_image(bitDepth,path, enableAutoWB, brightness, blackLevel,crop,flipud,fliplr)
        if qImg is not None:
            qPixImg = QtGui.QPixmap(qImg.size())
            QtGui.QPixmap.convertFromImage(qPixImg,qImg,QtCore.Qt.ImageConversionFlag.MonoOnly)
            canvas_widget.set_photo(QtGui.QPixmap(qPixImg))
            self._img = img_array
            self.IMG_CREATED.emit(self._img)
            self.messageLoadingImage.setText("Path of the image: "+path)
            return img_array
        else:
            return None

    def update_drawing(self):
        if not self.mainTab.count() == 0:
            if self.mainTab.currentWidget().canvasObject == "rectangle":
                self.mainTab.currentWidget().draw_rect(self.mainTab.currentWidget().start,self.mainTab.currentWidget().end,self.properties_widget.integralHalfWidthSlider.value()/100*1*self.scaleFactor)
            if self.mainTab.currentWidget().canvasObject == "arc":
                self.mainTab.currentWidget().draw_arc(self.mainTab.currentWidget().start,self.properties_widget.radiusSlider.value()/self.radiusSliderScale*self.scaleFactor,\
                                    self.properties_widget.integralHalfWidthSlider.value()/self.widthSliderScale*self.scaleFactor,self.properties_widget.chiRangeSlider.value(),\
                                    self.properties_widget.tiltAngleSlider.value()/self.tiltAngleSliderScale)

    def restore_defaults(self):
        self.mainTab.currentWidget().clear_canvas()
        self.mainTab.currentWidget().clear_annotations()
        self.pan.setChecked(True)
        self.properties_widget.autoWBCheckBox.setChecked(False)
        self.properties_widget.brightnessSlider.setValue(20)
        self.properties_widget.blackLevelSlider.setValue(50)
        self.clear_cursor_info()


    def toggle_canvas_mode(self,cursormode):
        for i in range(0,self.mainTab.count()):
            self.mainTab.widget(i).toggle_mode(cursormode)
        if cursormode == "arc":
            self.cursorInfo.startXYLabel.setText('Center (X,Y)')
            self.cursorInfo.endXYLabel.setText('Radius (px)')
        else:
            self.cursorInfo.startXYLabel.setText('Start (X,Y)')
            self.cursorInfo.endXYLabel.setText('End (X,Y)')
        self.clear_cursor_info()
        self._mode = cursormode
    
    def toggle_dark_mode(self, mode):
        self.TOGGLE_DARK_MODE.emit(mode)
        if mode == "light":
            self.isDarkMode = False
            self.toolBar.removeAction(self.lightMode)
            self.toolBar.addAction(self.darkMode)
            self.open.setIcon(QtGui.QIcon(os.path.join(self.dirname,"data/icons/open.svg")))
            self.saveAs.setIcon(QtGui.QIcon(os.path.join(self.dirname,"data/icons/save as.svg")))
            self.zoomIn.setIcon(QtGui.QIcon(os.path.join(self.dirname,"data/icons/zoom in.svg")))
            self.zoomOut.setIcon(QtGui.QIcon(os.path.join(self.dirname,"data/icons/zoom out.svg")))
            self.fitCanvas.setIcon(QtGui.QIcon(os.path.join(self.dirname,"data/icons/fit.svg")))
            self.line.setIcon(QtGui.QIcon(os.path.join(self.dirname,"data/icons/line.svg")))
            self.rectangle.setIcon(QtGui.QIcon(os.path.join(self.dirname,"data/icons/rectangle.svg")))
            self.arc.setIcon(QtGui.QIcon(os.path.join(self.dirname,"data/icons/arc.svg")))
            self.pan.setIcon(QtGui.QIcon(os.path.join(self.dirname,"data/icons/move.svg")))
            self.flipud.setIcon(QtGui.QIcon(os.path.join(self.dirname,"data/icons/flipud.svg")))
            self.fliplr.setIcon(QtGui.QIcon(os.path.join(self.dirname,"data/icons/fliplr.svg")))
            self.lightMode.setIcon(QtGui.QIcon(os.path.join(self.dirname,"data/icons/dark.svg")))
            self.darkMode.setIcon(QtGui.QIcon(os.path.join(self.dirname,"data/icons/light.svg")))
        elif mode == "dark":
            self.isDarkMode = True
            self.toolBar.removeAction(self.darkMode)
            self.toolBar.addAction(self.lightMode)
            self.open.setIcon(QtGui.QIcon(os.path.join(self.dirname,"data/icons/open_dark.svg")))
            self.saveAs.setIcon(QtGui.QIcon(os.path.join(self.dirname,"data/icons/save as_dark.svg")))
            self.zoomIn.setIcon(QtGui.QIcon(os.path.join(self.dirname,"data/icons/zoom in_dark.svg")))
            self.zoomOut.setIcon(QtGui.QIcon(os.path.join(self.dirname,"data/icons/zoom out_dark.svg")))
            self.fitCanvas.setIcon(QtGui.QIcon(os.path.join(self.dirname,"data/icons/fit_dark.svg")))
            self.line.setIcon(QtGui.QIcon(os.path.join(self.dirname,"data/icons/line_dark.svg")))
            self.rectangle.setIcon(QtGui.QIcon(os.path.join(self.dirname,"data/icons/rectangle_dark.svg")))
            self.arc.setIcon(QtGui.QIcon(os.path.join(self.dirname,"data/icons/arc_dark.svg")))
            self.pan.setIcon(QtGui.QIcon(os.path.join(self.dirname,"data/icons/move_dark.svg")))
            self.flipud.setIcon(QtGui.QIcon(os.path.join(self.dirname,"data/icons/flipud_dark.svg")))
            self.fliplr.setIcon(QtGui.QIcon(os.path.join(self.dirname,"data/icons/fliplr_dark.svg")))
            self.lightMode.setIcon(QtGui.QIcon(os.path.join(self.dirname,"data/icons/dark_dark.svg")))
            self.darkMode.setIcon(QtGui.QIcon(os.path.join(self.dirname,"data/icons/light_dark.svg")))

    def clear_cursor_info(self):
        self.cursorInfo.choosedXYEdit.clear()
        self.cursorInfo.intensityEdit.clear()
        self.cursorInfo.startXYEdit.clear()
        self.cursorInfo.endXYEdit.clear()
        self.cursorInfo.widthEdit.clear()

    def photo_mouse_press(self, pos):
        self.cursorInfo.startXYEdit.setText('{},{}'.format(int(pos.x()), int(pos.y())))
        self.cursorInfo.endXYEdit.clear()
        if self._mode == "rectangle" or self._mode == "arc":
            self.cursorInfo.widthEdit.setText('{:3.2f}'.format(self.properties_widget.integralHalfWidthSlider.value()/self.widthSliderScale))
        elif self._mode == "line":
            self.cursorInfo.widthEdit.setText('{:3.2f}'.format(0.00))

    def photo_mouse_release(self, pos,start,ShiftModified):
        if self._mode == "arc":
            self.cursorInfo.endXYEdit.setText('{}'.format(np.round(self.mainTab.currentWidget().PFRadius,2)))
        else:
            if ShiftModified:
                if pos.x() == start.x():
                    slope = 10
                else:
                    slope = (pos.y()-start.y())/(pos.x()-start.x())
                if slope > np.tan(np.pi/3):
                    pos.setX(start.x())
                elif slope < np.tan(np.pi/6):
                    pos.setY(start.y())
                else:
                    pos.setY(pos.x()-start.x()+start.y())
            self.cursorInfo.endXYEdit.setText('{},{}'.format(int(pos.x()), int(pos.y())))
        if self.mainTab.currentWidget()._drawingArc:
            self.properties_widget.radiusSlider.setValue(int(self.radiusSliderScale*self.mainTab.currentWidget().PFRadius/self.scaleFactor))

    def photo_mouse_movement(self, pos, type="canvas"):
        if type == "canvas":
            self.editPixInfo.setText('x = %d, y = %d' % (int(pos.x()), int(pos.y())))
            if self.mainTab.currentWidget()._drawingArc:
                self.properties_widget.radiusSlider.setValue(int(self.radiusSliderScale*self.mainTab.currentWidget().PFRadius/self.scaleFactor))
        elif type == "chart":
            self.editPixInfo.setText('K = %3.2f, Int. = %3.2f' % (pos.x(), pos.y()))

    def photo_mouse_double_click(self, pos):
        self.cursorInfo.choosedXYEdit.setText('{},{}'.format(pos.x(), pos.y()))
        self.cursorInfo.intensityEdit.setText('{:3.2f}'.format(self._img[pos.y(), pos.x()]/np.amax(np.amax(self._img))))

    def key_press_event(self,event):
        if event.key() == QtCore.Qt.Key.Key_Up or QtCore.Qt.Key.Key_Down or QtCore.Qt.Key.Key_Left or QtCore.Qt.Key.Key_Right :
            self.mainTab.currentWidget().setFocus()
            self.mainTab.currentWidget().keyPressEvent(event)

    def status(self):
        status = {"sensitivity": float(self.properties_widget.sensitivityEdit.text()),\
                "energy": float(self.properties_widget.energyEdit.text()),\
                "azimuth": float(self.properties_widget.azimuthEdit.text()),\
                "scaleBar": float(self.properties_widget.scaleBarEdit.text()),\
                "brightness": self.properties_widget.brightnessSlider.value(),\
                "blackLevel": self.properties_widget.blackLevelSlider.value(),\
                "integralWidth": self.properties_widget.integralHalfWidthSlider.value()/self.properties_widget.widthSliderScale,\
                "chiRange": self.properties_widget.chiRangeSlider.value(),\
                "radius": self.properties_widget.radiusSlider.value()/self.properties_widget.radiusSliderScale,\
                "tiltAngle": self.properties_widget.tiltAngleSlider.value()/self.properties_widget.tiltAngleSliderScale,\
                "autoWB": self.properties_widget.autoWBCheckBox.isChecked(),\
                "mode": self._mode}
        try:
            status["choosedX"] = int(self.cursorInfo.choosedXYEdit.text().split(',')[0])
            status["choosedY"] = int(self.cursorInfo.choosedXYEdit.text().split(',')[1])
        except:
            status["choosedX"] = ""
            status["choosedY"] = ""
        try:
            status["startX"] = int(self.cursorInfo.startXYEdit.text().split(',')[0])
            status["startY"] = int(self.cursorInfo.startXYEdit.text().split(',')[1])
        except:
            status["startX"] = ""
            status["startY"] = ""
        try:
            status["endX"] = int(self.cursorInfo.endXYEdit.text().split(',')[0])
            status["endY"] = int(self.cursorInfo.endXYEdit.text().split(',')[1])
        except:
            status["endX"] = ""
            status["endY"] = ""
        try:
            status["width"] = float(self.cursorInfo.widthEdit.text())
        except:
            status["width"] = ""
        self.RETURN_STATUS.emit(status)

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
