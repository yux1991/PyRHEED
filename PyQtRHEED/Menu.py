from PyQt5 import QtCore, QtWidgets
import configparser

class Menu(QtCore.QObject):

    #Public Signals
    DefaultSettingsChanged = QtCore.pyqtSignal(configparser.ConfigParser)

    def __init__(self):
        super(Menu,self).__init__()
        self.config = configparser.ConfigParser()
        self.config.read('./configuration.ini')
        self.defaultLineValueList = [['0', '0', '20', '0', '5', '60', '0.4', '100', '5', '20', '10', '0', '10'], \
                                     ['361.13', '20', '0', '5', '30', '0', '100', '50', '0', '500', '0.4', '0', '1',\
                                      '100', '60', '0', '180', '5', '0', '20', '10', '0', '-15', '15', '10'], \
                                     ['0.4', '20', '60', '0', '21'], ['1']]

    def Preference_DefaultSettings(self):
        self.windowDefault = dict(self.config['windowDefault'].items())
        self.propertiesDefault = dict(self.config['propertiesDefault'].items())
        self.canvasDefault = dict(self.config['canvasDefault'].items())
        self.chartDefault = dict(self.config['chartDefault'].items())
        dlg = QtWidgets.QDialog()
        dlgGrid = QtWidgets.QGridLayout(dlg)
        tab = QtWidgets.QTabWidget()
        buttonBox = QtWidgets.QDialogButtonBox()
        self.window = QtWidgets.QWidget()
        self.properties = QtWidgets.QWidget()
        self.canvas = QtWidgets.QWidget()
        self.chart = QtWidgets.QWidget()
        windowGrid = QtWidgets.QGridLayout(self.window)
        windowMode = [('Horizontal Shift (px)',self.windowDefault['hs'],0,0,1),\
                      ('Vertical Shift (px)',self.windowDefault['vs'],1,0,1),\
                      ('Energy (keV)',self.windowDefault['energy'],2,0,1),\
                      ('Azimuth (\u00B0)',self.windowDefault['azimuth'],3,0,1),\
                      ('Scale Bar Length (\u212B\u207B\u00B9)',self.windowDefault['scalebarlength'],4,0,1),\
                      ('Chi Range (\u00B0)',self.windowDefault['chirange'],5,0,1),\
                      ('Integral Half Width (\u212B\u207B\u00B9)',self.windowDefault['width'],6,0,1),\
                      ('Integral Half Width Slider Scale',self.windowDefault['widthsliderscale'],7,0,1),\
                      ('Radius (\u212B\u207B\u00B9)',self.windowDefault['radius'],8,0,1),\
                      ('Radius Maximum (\u212B\u207B\u00B9)',self.windowDefault['radiusmaximum'],9,0,1),\
                      ('Radius Slider Scale',self.windowDefault['radiussliderscale'],10,0,1),\
                      ('Tilt Angle (\u00B0)',self.windowDefault['tiltangle'],11,0,1),\
                      ('Tilt Angle Slider Scale',self.windowDefault['tiltanglesliderscale'],12,0,1)]
        propertiesGrid = QtWidgets.QGridLayout(self.properties)
        propertiesMode = [('Sensitivity (pixel/sqrt[keV])',self.propertiesDefault['sensitivity'],0,0,3),\
                          ('Electron Energy (keV)',self.propertiesDefault['electronenergy'],1,0,3),\
                          ('Azimuth (\u00B0)',self.propertiesDefault['azimuth'],2,0,3),\
                          ('Scale Bar Length (\u212B\u207B\u00B9)',self.propertiesDefault['scalebarlength'],3,0,3),\
                          (',',self.propertiesDefault['brightness'],4,1,1),\
                          ('Brightness (Minimum,Default,Maximum)',self.propertiesDefault['brightnessminimum'],4,0,1),\
                          (',',self.propertiesDefault['brightnessmaximum'],4,2,1),\
                          (',',self.propertiesDefault['blacklevel'],5,1,1),\
                          ('Black Level (Minimum,Default,Maximum)',self.propertiesDefault['blacklevelminimum'],5,0,1),\
                          (',',self.propertiesDefault['blacklevelmaximum'],5,2,1),\
                          (',',self.propertiesDefault['integralhalfwidth'],6,1,1),\
                          ('Half Width (\u212B\u207B\u00B9) (Minimum,Default,Maximum)',self.propertiesDefault['widthminimum'],6,0,1),\
                          (',',self.propertiesDefault['widthmaximum'],6,2,1),\
                          ('Slider Scales (Half Width,Radius,Tilt Angle)',self.propertiesDefault['widthsliderscale'],10,0,1),\
                          (',',self.propertiesDefault['chirange'],7,1,1),\
                          ('Chi Range (\u00B0) (Minimum,Default,Maximum)',self.propertiesDefault['chirangeminimum'],7,0,1),\
                          (',',self.propertiesDefault['chirangemaximum'],7,2,1),\
                          (',',self.propertiesDefault['radius'],8,1,1),\
                          ('Radius (\u212B\u207B\u00B9) (Minimum,Default,Maximum)',self.propertiesDefault['radiusminimum'],8,0,1),\
                          (',',self.propertiesDefault['radiusmaximum'],8,2,1),\
                          (',',self.propertiesDefault['radiussliderscale'],10,1,1),\
                          (',',self.propertiesDefault['tiltangle'],9,1,1),\
                          ('Tilt Angle (\u00B0) (Minimum,Default,Maximum)',self.propertiesDefault['tiltangleminimum'],9,0,1),\
                          (',',self.propertiesDefault['tiltanglemaximum'],9,2,1),\
                          (',',self.propertiesDefault['tiltanglesliderscale'],10,2,1)]
        canvasGrid = QtWidgets.QGridLayout(self.canvas)
        canvasMode = [('Integral Half Width',self.canvasDefault['widthinangstrom'],0,0,1),\
                      ('Radius Maximum',self.canvasDefault['radiusmaximum'],1,0,1),\
                      ('Span',self.canvasDefault['span'],2,0,1),\
                      ('Tilt',self.canvasDefault['tilt'],3,0,1),\
                      ('Maximum Zoom Factor',self.canvasDefault['max_zoom_factor'],4,0,1)]
        chartGrid = QtWidgets.QGridLayout(self.chart)
        chartMode = [('Theme',self.chartDefault['theme'],0,0,1)]
        PageMode = [(windowGrid,windowMode),(propertiesGrid,propertiesMode),(canvasGrid,canvasMode),(chartGrid,chartMode)]
        for grid, mode in PageMode:
            for label,value,row,col,span in mode:
                grid.addWidget(QtWidgets.QLabel(label),row,2*col,1,1)
                grid.addWidget(QtWidgets.QLineEdit(value),row,2*col+1,1,2*span-1)
        tab.addTab(self.window,"Window")
        tab.addTab(self.properties,"Properties")
        tab.addTab(self.canvas,"Canvas")
        tab.addTab(self.chart,"Chart")

        buttonBox.addButton("Accept",QtWidgets.QDialogButtonBox.AcceptRole)
        buttonBox.addButton("Reset",QtWidgets.QDialogButtonBox.ResetRole)
        buttonBox.addButton("Cancel",QtWidgets.QDialogButtonBox.DestructiveRole)
        buttonBox.setCenterButtons(True)
        buttonBox.findChildren(QtWidgets.QPushButton)[0].clicked.connect(self.Accept)
        buttonBox.findChildren(QtWidgets.QPushButton)[1].clicked.connect(self.Reset)

        dlgGrid.addWidget(tab,0,0)
        dlgGrid.addWidget(buttonBox,1,0)
        dlgGrid.setContentsMargins(0,0,0,0)
        dlg.setWindowTitle("Default Settings")
        dlg.setWindowModality(QtCore.Qt.ApplicationModal)
        dlg.resize(tab.minimumSizeHint())
        dlg.showNormal()
        dlg.exec_()

    def Save_Preference_DefaultSettings(self,lineValueList):
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
        with open('./configuration.ini','w') as configfile:
            config.write(configfile)
        return Dic

    def Accept(self):
        windowValueList = [item.text() for item in self.window.findChildren(QtWidgets.QLineEdit)]
        propertiesValueList = [item.text() for item in self.properties.findChildren(QtWidgets.QLineEdit)]
        canvasValueList = [item.text() for item in self.canvas.findChildren(QtWidgets.QLineEdit)]
        chartValueList = [item.text() for item in self.chart.findChildren(QtWidgets.QLineEdit)]
        lineValueList = [windowValueList, propertiesValueList,canvasValueList,chartValueList]
        Dic = self.Save_Preference_DefaultSettings(lineValueList)
        config = configparser.ConfigParser()
        config.read_dict(Dic)
        self.DefaultSettingsChanged.emit(config)

    def Reset(self):
        Dic = self.Save_Preference_DefaultSettings(self.defaultLineValueList)
        config = configparser.ConfigParser()
        config.read_dict(Dic)
        self.DefaultSettingsChanged.emit(config)
