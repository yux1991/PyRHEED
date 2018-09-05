from PyQt5 import QtCore, QtWidgets

class Properties(QtWidgets.QWidget):

    def __init__(self,parent):
        super(Properties,self).__init__(parent)
        self.initUI()

    def initUI(self):
        tab = QtWidgets.QTabWidget()
        #Parameters page
        parametersPage = QtWidgets.QWidget()
        parametersGrid = QtWidgets.QGridLayout(parametersPage)
        sensitivityLabel = QtWidgets.QLabel('Sensitivity (pixel/sqrt[keV])')
        sensitivityEdit = QtWidgets.QLineEdit('361.13')
        energyLabel = QtWidgets.QLabel('Electron Energy (keV)')
        energyEdit = QtWidgets.QLineEdit('20')
        azimuthLabel = QtWidgets.QLabel('Azimuth(\u00B0)')
        azimuthEdit = QtWidgets.QLineEdit('0')
        scaleBarLabel = QtWidgets.QLabel('Scale Bar Length (\u212B)')
        scaleBarEdit = QtWidgets.QLineEdit('5')
        labelButton = QtWidgets.QPushButton('Label')
        calibrateButton = QtWidgets.QPushButton('Calibrate')
        clearButton = QtWidgets.QPushButton('Clear')
        labelButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
        calibrateButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
        clearButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
        buttonGrid1 = QtWidgets.QGridLayout()
        buttonGrid1.addWidget(labelButton,0,0)
        buttonGrid1.addWidget(calibrateButton,0,1)
        buttonGrid1.addWidget(clearButton,0,2)

        parametersGrid.addWidget(sensitivityLabel,0,0)
        parametersGrid.addWidget(sensitivityEdit,0,1)
        parametersGrid.addWidget(energyLabel,1,0)
        parametersGrid.addWidget(energyEdit,1,1)
        parametersGrid.addWidget(azimuthLabel,2,0)
        parametersGrid.addWidget(azimuthEdit,2,1)
        parametersGrid.addWidget(scaleBarLabel,3,0)
        parametersGrid.addWidget(scaleBarEdit,3,1)
        parametersGrid.addLayout(buttonGrid1,4,0,1,2)
        tab.addTab(parametersPage,"Parameters")

        #image adjust page
        imageAdjustPage = QtWidgets.QWidget()
        imageAdjustGrid = QtWidgets.QGridLayout(imageAdjustPage)
        brightnessLabel = QtWidgets.QLabel('Brightness ({})'.format(0.3))
        brightnessSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        blackLevelLabel = QtWidgets.QLabel('Black Level ({})'.format(50))
        blackLevelSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        autoWBLabel = QtWidgets.QLabel('Auto white balance')
        autoWBCheckBox = QtWidgets.QCheckBox()

        applyButton2 = QtWidgets.QPushButton('Apply')
        resetButton2 = QtWidgets.QPushButton('Reset')
        applyButton2.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
        resetButton2.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
        buttonGrid2 = QtWidgets.QGridLayout()
        buttonGrid2.addWidget(applyButton2,0,0)
        buttonGrid2.addWidget(resetButton2,0,1)

        imageAdjustGrid.addWidget(brightnessLabel,0,0)
        imageAdjustGrid.addWidget(brightnessSlider,0,1)
        imageAdjustGrid.addWidget(blackLevelLabel,1,0)
        imageAdjustGrid.addWidget(blackLevelSlider,1,1)
        imageAdjustGrid.addWidget(autoWBLabel,2,0)
        imageAdjustGrid.addWidget(autoWBCheckBox,2,1)
        imageAdjustGrid.addLayout(buttonGrid2,3,0,1,2)
        tab.addTab(imageAdjustPage,"Image Adjust")

        #profile options page
        profileOptionsPage = QtWidgets.QWidget()
        profileOptionsGrid = QtWidgets.QGridLayout(profileOptionsPage)
        integralHalfWidthLabel = QtWidgets.QLabel('Integral Half Width ({} \u212B\u207B\u00B9)'.format(0.12))
        integralHalfWidthSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        chiRangeLabel = QtWidgets.QLabel('Chi Range ({}\u00B0)'.format(60))
        chiRangeSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        radiusLabel = QtWidgets.QLabel('Radius ({} \u212B\u207B\u00B9)'.format(2.48))
        radiusSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        tiltAngleLabel = QtWidgets.QLabel('Tilt Angle ({}\u00B0)'.format(0))
        tiltAngleSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)


        applyButton3 = QtWidgets.QPushButton('Apply')
        resetButton3= QtWidgets.QPushButton('Reset')
        applyButton3.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
        resetButton3.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
        buttonGrid3 = QtWidgets.QGridLayout()
        buttonGrid3.addWidget(applyButton3,0,0)
        buttonGrid3.addWidget(resetButton3,0,1)

        profileOptionsGrid.addWidget(integralHalfWidthLabel,0,0)
        profileOptionsGrid.addWidget(integralHalfWidthSlider,0,1)
        profileOptionsGrid.addWidget(chiRangeLabel,1,0)
        profileOptionsGrid.addWidget(chiRangeSlider,1,1)
        profileOptionsGrid.addWidget(radiusLabel,2,0)
        profileOptionsGrid.addWidget(radiusSlider,2,1)
        profileOptionsGrid.addWidget(tiltAngleLabel,3,0)
        profileOptionsGrid.addWidget(tiltAngleSlider,3,1)
        profileOptionsGrid.addLayout(buttonGrid3,4,0,1,2)
        tab.addTab(profileOptionsPage,"Profile Options")
        tab.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Fixed)

        UIgrid = QtWidgets.QGridLayout()
        UIgrid.addWidget(tab,0,0)
        UIgrid.setContentsMargins(0,0,0,0)
        self.setLayout(UIgrid)
        self.show()



