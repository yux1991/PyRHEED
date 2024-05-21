from PyQt6 import QtCore, QtWidgets
import configparser
import os

class Window(QtCore.QObject):

    #Public Signals
    DEFAULT_SETTINGS_CHANGED = QtCore.pyqtSignal(configparser.ConfigParser)

    def __init__(self):
        super(Window,self).__init__()
        self.twoDimensionalMappingRegion = [0,0,0,0,0]
        self.config = configparser.ConfigParser()
        dirname = os.path.dirname(__file__)
        self.config.read(os.path.join(dirname,'configuration.ini'))
        self.defaultLineValueList = [['0', '0', '20', '0', '5', '60', '0.4', '100', '5', '20', '10', '0', '10'], \
                                     ['361.13', '20', '0', '5', '20', '0', '100', '50', '0', '500', '0.4', '0', '1',\
                                      '100', '60', '0', '180', '5', '0', '20', '10', '0', '-15', '15', '10'], \
                                     ['0.4', '20', '60', '0', '21'], ['1']]

#Preference_Default Settings

    def main(self):
        self.windowDefault = dict(self.config['windowDefault'].items())
        self.propertiesDefault = dict(self.config['propertiesDefault'].items())
        self.canvasDefault = dict(self.config['canvasDefault'].items())
        self.chartDefault = dict(self.config['chartDefault'].items())
        self.DefaultSettings_Dialog = QtWidgets.QDialog()
        self.DefaultSettings_DialogGrid = QtWidgets.QGridLayout(self.DefaultSettings_Dialog)
        self.tab = self.refresh_tab(self.config)
        buttonBox = QtWidgets.QDialogButtonBox()
        buttonBox.addButton("Accept",QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole)
        buttonBox.addButton("Reset",QtWidgets.QDialogButtonBox.ButtonRole.ResetRole)
        buttonBox.addButton("Quit",QtWidgets.QDialogButtonBox.ButtonRole.DestructiveRole)
        buttonBox.setCenterButtons(True)
        buttonBox.findChildren(QtWidgets.QPushButton)[0].clicked.connect(self.accept)
        buttonBox.findChildren(QtWidgets.QPushButton)[1].clicked.connect(self.reset)
        buttonBox.findChildren(QtWidgets.QPushButton)[2].clicked.connect(self.DefaultSettings_Dialog.reject)
        self.DefaultSettings_DialogGrid.addWidget(self.tab,0,0)
        self.DefaultSettings_DialogGrid.addWidget(buttonBox,1,0)
        self.DefaultSettings_DialogGrid.setContentsMargins(0,0,0,0)
        self.DefaultSettings_Dialog.setWindowTitle("Default Settings")
        self.DefaultSettings_Dialog.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        self.DefaultSettings_Dialog.resize(self.tab.minimumSizeHint())
        self.DefaultSettings_Dialog.showNormal()
        self.DefaultSettings_Dialog.exec()

    def save(self,lineValueList):
        windowKeys = ['HS','VS','energy','azimuth','scaleBarLength','chiRange','width','widthSliderScale','radius',\
                      'radiusMaximum','radiusSliderScale','tiltAngle','tiltAngleSliderScale']
        propertiesKeys = ['sensitivity','electronEnergy','azimuth','scaleBarLength','brightness','brightnessMinimum',\
                          'brightnessMaximum','blackLevel','blackLevelMinimum','blackLevelMaximum','integralHalfWidth','widthMinimum','widthMaximum','widthSliderScale',\
                          'chiRange','chiRangeMinimum','chiRangeMaximum','radius','radiusMinimum','radiusMaximum',\
                          'radiusSliderScale','tiltAngle','tiltAngleMinimum','tiltAngleMaximum','tiltAngleSliderScale']
        canvasKeys=['widthInAngstrom','radiusMaximum','span','tilt','max_zoom_factor']
        chartKeys = ['theme']
        Dic = {'windowDefault':{key:value for (key,value) in zip(windowKeys,lineValueList[0])},\
               'propertiesDefault':{key:value for (key,value) in zip(propertiesKeys,lineValueList[1])}, \
               'canvasDefault':{key:value for (key,value) in zip(canvasKeys,lineValueList[2])}, \
               'chartDefault':{key:value for (key,value) in zip(chartKeys,lineValueList[3])},\
               }
        config = configparser.ConfigParser()
        config.read_dict(Dic)
        dirname = os.path.dirname(__file__)
        with open(os.path.join(dirname,'configuration/configuration.ini'),'w') as configfile:
            config.write(configfile)
        return Dic

    def refresh_tab(self,config):
        windowDefault = dict(config['windowDefault'].items())
        propertiesDefault = dict(config['propertiesDefault'].items())
        canvasDefault = dict(config['canvasDefault'].items())
        chartDefault = dict(config['chartDefault'].items())
        tab = QtWidgets.QTabWidget()
        self.window = QtWidgets.QWidget()
        self.properties = QtWidgets.QWidget()
        self.canvas = QtWidgets.QWidget()
        self.chart = QtWidgets.QWidget()
        chartCombo = QtWidgets.QComboBox()
        chartCombo.addItem("Light","0")
        chartCombo.addItem("BlueCerulean","1")
        chartCombo.addItem("Dark","2")
        chartCombo.addItem("Brown Sand","3")
        chartCombo.addItem("Blue Ncs","4")
        chartCombo.addItem("High Contrast","5")
        chartCombo.addItem("Blue Icey","6")
        chartCombo.addItem("Qt","7")
        chartCombo.setCurrentIndex(int(chartDefault["theme"]))
        windowGrid = QtWidgets.QGridLayout(self.window)
        windowMode = [('Horizontal Shift (px)',windowDefault['hs'],0,0,1),\
                      ('Vertical Shift (px)',windowDefault['vs'],1,0,1),\
                      ('Energy (keV)',windowDefault['energy'],2,0,1),\
                      ('Azimuth (\u00B0)',windowDefault['azimuth'],3,0,1),\
                      ('Scale Bar Length (\u212B\u207B\u00B9)',windowDefault['scalebarlength'],4,0,1),\
                      ('Chi Range (\u00B0)',windowDefault['chirange'],5,0,1),\
                      ('Integral Half Width (\u212B\u207B\u00B9)',windowDefault['width'],6,0,1),\
                      ('Integral Half Width Slider Scale',windowDefault['widthsliderscale'],7,0,1),\
                      ('Radius (\u212B\u207B\u00B9)',windowDefault['radius'],8,0,1),\
                      ('Radius Maximum (\u212B\u207B\u00B9)',windowDefault['radiusmaximum'],9,0,1),\
                      ('Radius Slider Scale',windowDefault['radiussliderscale'],10,0,1),\
                      ('Tilt Angle (\u00B0)',windowDefault['tiltangle'],11,0,1),\
                      ('Tilt Angle Slider Scale',windowDefault['tiltanglesliderscale'],12,0,1)]
        propertiesGrid = QtWidgets.QGridLayout(self.properties)
        propertiesMode = [('Sensitivity (pixel/sqrt[keV])',propertiesDefault['sensitivity'],0,0,3),\
                          ('Electron Energy (keV)',propertiesDefault['electronenergy'],1,0,3),\
                          ('Azimuth (\u00B0)',propertiesDefault['azimuth'],2,0,3),\
                          ('Scale Bar Length (\u212B\u207B\u00B9)',propertiesDefault['scalebarlength'],3,0,3),\
                          (',',propertiesDefault['brightness'],4,1,1),\
                          ('Brightness (Minimum,Default,Maximum)',propertiesDefault['brightnessminimum'],4,0,1),\
                          (',',propertiesDefault['brightnessmaximum'],4,2,1),\
                          (',',propertiesDefault['blacklevel'],5,1,1),\
                          ('Black Level (Minimum,Default,Maximum)',propertiesDefault['blacklevelminimum'],5,0,1),\
                          (',',propertiesDefault['blacklevelmaximum'],5,2,1),\
                          (',',propertiesDefault['integralhalfwidth'],6,1,1),\
                          ('Half Width (\u212B\u207B\u00B9) (Minimum,Default,Maximum)',propertiesDefault['widthminimum'],6,0,1),\
                          (',',propertiesDefault['widthmaximum'],6,2,1),\
                          ('Slider Scales (Half Width,Radius,Tilt Angle)',propertiesDefault['widthsliderscale'],10,0,1),\
                          (',',propertiesDefault['chirange'],7,1,1),\
                          ('Chi Range (\u00B0) (Minimum,Default,Maximum)',propertiesDefault['chirangeminimum'],7,0,1),\
                          (',',propertiesDefault['chirangemaximum'],7,2,1),\
                          (',',propertiesDefault['radius'],8,1,1),\
                          ('Radius (\u212B\u207B\u00B9) (Minimum,Default,Maximum)',propertiesDefault['radiusminimum'],8,0,1),\
                          (',',propertiesDefault['radiusmaximum'],8,2,1),\
                          (',',propertiesDefault['radiussliderscale'],10,1,1),\
                          (',',propertiesDefault['tiltangle'],9,1,1),\
                          ('Tilt Angle (\u00B0) (Minimum,Default,Maximum)',propertiesDefault['tiltangleminimum'],9,0,1),\
                          (',',propertiesDefault['tiltanglemaximum'],9,2,1),\
                          (',',propertiesDefault['tiltanglesliderscale'],10,2,1)]
        canvasGrid = QtWidgets.QGridLayout(self.canvas)
        canvasMode = [('Integral Half Width',canvasDefault['widthinangstrom'],0,0,1),\
                      ('Radius Maximum',canvasDefault['radiusmaximum'],1,0,1),\
                      ('Span',canvasDefault['span'],2,0,1),\
                      ('Tilt',canvasDefault['tilt'],3,0,1),\
                      ('Maximum Zoom Factor',canvasDefault['max_zoom_factor'],4,0,1)]
        chartGrid = QtWidgets.QVBoxLayout(self.chart)
        chartGrid.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        PageMode = [(windowGrid,windowMode),(propertiesGrid,propertiesMode),(canvasGrid,canvasMode)]
        for grid, mode in PageMode:
            for label,value,row,col,span in mode:
                grid.addWidget(QtWidgets.QLabel(label),row,2*col,1,1)
                grid.addWidget(QtWidgets.QLineEdit(value),row,2*col+1,1,2*span-1)
                grid.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        chartGrid.addWidget(QtWidgets.QLabel("Theme:"))
        chartGrid.addWidget(chartCombo)
        tab.addTab(self.window,"Window")
        tab.addTab(self.properties,"Properties")
        tab.addTab(self.canvas,"Canvas")
        tab.addTab(self.chart,"Chart")
        return tab

    def accept(self):
        windowValueList = [item.text() for item in self.window.findChildren(QtWidgets.QLineEdit)]
        propertiesValueList = [item.text() for item in self.properties.findChildren(QtWidgets.QLineEdit)]
        canvasValueList = [item.text() for item in self.canvas.findChildren(QtWidgets.QLineEdit)]
        chartValueList = [item.currentData() for item in self.chart.findChildren(QtWidgets.QComboBox)]
        lineValueList = [windowValueList, propertiesValueList,canvasValueList,chartValueList]
        Dic = self.save(lineValueList)
        config = configparser.ConfigParser()
        config.read_dict(Dic)
        self.DEFAULT_SETTINGS_CHANGED.emit(config)

    def reset(self):
        Dic = self.save(self.defaultLineValueList)
        config = configparser.ConfigParser()
        config.read_dict(Dic)
        self.DEFAULT_SETTINGS_CHANGED.emit(config)
        tab_new = self.refresh_tab(config)
        self.DefaultSettings_DialogGrid.replaceWidget(self.tab,tab_new)
        self.tab = tab_new

    def toggle_dark_theme(self, mode):
        if mode == "dark":
            self.defaultLineValueList = [['0', '0', '20', '0', '5', '60', '0.4', '100', '5', '20', '10', '0', '10'], \
                                        ['361.13', '20', '0', '5', '20', '0', '100', '50', '0', '500', '0.4', '0', '1',\
                                        '100', '60', '0', '180', '5', '0', '20', '10', '0', '-15', '15', '10'], \
                                        ['0.4', '20', '60', '0', '21'], ['2']]
        elif mode == "light":
            self.defaultLineValueList = [['0', '0', '20', '0', '5', '60', '0.4', '100', '5', '20', '10', '0', '10'], \
                                        ['361.13', '20', '0', '5', '20', '0', '100', '50', '0', '500', '0.4', '0', '1',\
                                        '100', '60', '0', '180', '5', '0', '20', '10', '0', '-15', '15', '10'], \
                                        ['0.4', '20', '60', '0', '21'], ['0']]
        Dic = self.save(self.defaultLineValueList)
        config = configparser.ConfigParser()
        config.read_dict(Dic)
        self.DEFAULT_SETTINGS_CHANGED.emit(config)