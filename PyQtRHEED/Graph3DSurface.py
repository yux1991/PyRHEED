from PyQt5 import QtCore, QtGui, QtWidgets, QtDataVisualization
import Process
import numpy as np
import os

class Graph(QtWidgets.QWidget):

    def __init__(self):
        super(Graph,self).__init__()

    def run3DGraph(self,path):
        self.graphPath = path
        self.graph = SurfaceGraph()
        self.container = QtWidgets.QWidget.createWindowContainer(self.graph)
        self.screenSize = self.graph.screen().size()
        self.container.setMinimumSize(self.screenSize.width()/2, self.screenSize.height()/2)
        self.container.setMaximumSize(self.screenSize)
        self.container.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        self.container.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.hLayout = QtWidgets.QHBoxLayout(self)
        self.vLayout = QtWidgets.QVBoxLayout()
        self.hLayout.addWidget(self.container,1)
        self.vLayout.setAlignment(QtCore.Qt.AlignTop)
        self.hLayout.addLayout(self.vLayout)
        self.setWindowTitle("Surface example")
        self.setWindowModality(QtCore.Qt.WindowModal)

        self.chooseGraph = QtWidgets.QGroupBox("Choose Graph")
        self.chooseGraphGrid = QtWidgets.QGridLayout(self.chooseGraph)
        self.chooseSourceLabel = QtWidgets.QLabel("The path of the graph is:\n"+self.graphPath)
        self.chooseSourceLabel.setFixedWidth(150)
        self.chooseSourceLabel.setWordWrap(True)
        self.chooseSourceButton = QtWidgets.QPushButton("Browse")
        self.chooseSourceButton.clicked.connect(self.Choose_Graph)
        self.chooseGraphGrid.addWidget(self.chooseSourceLabel,0,0)
        self.chooseGraphGrid.addWidget(self.chooseSourceButton,1,0)

        self.modelGroupBox = QtWidgets.QGroupBox("Model")
        self.sqrtSinModelRB = QtWidgets.QRadioButton(self)
        self.sqrtSinModelRB.setText("Sqrt && Sin")
        self.heightMapModelRB = QtWidgets.QRadioButton(self)
        self.heightMapModelRB.setText("Height Map")
        self.heightMapModelRB.setChecked(False)

        self.modelVBox = QtWidgets.QVBoxLayout()
        self.modelVBox.addWidget(self.sqrtSinModelRB)
        self.modelVBox.addWidget(self.heightMapModelRB)
        self.modelGroupBox.setLayout(self.modelVBox)

        self.selectionGroupBox = QtWidgets.QGroupBox("Selection Mode")
        self.modeNoneRB = QtWidgets.QRadioButton(self)
        self.modeNoneRB.setText("No Selection")
        self.modeNoneRB.setChecked(False)

        self.modeItemRB = QtWidgets.QRadioButton(self)
        self.modeItemRB.setText("Item")
        self.modeItemRB.setChecked(False)

        self.modeSliceRowRB = QtWidgets.QRadioButton(self)
        self.modeSliceRowRB.setText("Row Slice")
        self.modeSliceRowRB.setChecked(False)

        self.modeSliceColumnRB = QtWidgets.QRadioButton(self)
        self.modeSliceColumnRB.setText("Column Slice")
        self.modeSliceColumnRB.setChecked(False)

        self.selectionVBox = QtWidgets.QVBoxLayout()
        self.selectionVBox.addWidget(self.modeNoneRB)
        self.selectionVBox.addWidget(self.modeItemRB)
        self.selectionVBox.addWidget(self.modeSliceRowRB)
        self.selectionVBox.addWidget(self.modeSliceColumnRB)
        self.selectionGroupBox.setLayout(self.selectionVBox)

        self.axisMinSliderX = QtWidgets.QSlider(QtCore.Qt.Horizontal,self)
        self.axisMinSliderX.setMinimum(0)
        self.axisMinSliderX.setTickInterval(1)
        self.axisMinSliderX.setEnabled(True)
        self.axisMaxSliderX = QtWidgets.QSlider(QtCore.Qt.Horizontal,self)
        self.axisMaxSliderX.setMinimum(1)
        self.axisMaxSliderX.setTickInterval(1)
        self.axisMaxSliderX.setEnabled(True)
        self.axisMinSliderZ = QtWidgets.QSlider(QtCore.Qt.Horizontal,self)
        self.axisMinSliderZ.setMinimum(0)
        self.axisMinSliderZ.setTickInterval(1)
        self.axisMinSliderZ.setEnabled(True)
        self.axisMaxSliderZ = QtWidgets.QSlider(QtCore.Qt.Horizontal,self)
        self.axisMaxSliderZ.setMinimum(1)
        self.axisMaxSliderZ.setTickInterval(1)
        self.axisMaxSliderZ.setEnabled(True)

        self.themeList = QtWidgets.QComboBox(self)
        self.themeList.addItem("Qt")
        self.themeList.addItem("Primary Colors")
        self.themeList.addItem("Digia")
        self.themeList.addItem("Stone Moss")
        self.themeList.addItem("Army Blue")
        self.themeList.addItem("Retro")
        self.themeList.addItem("Ebony")
        self.themeList.addItem("Isabelle")

        self.colorGroupBox = QtWidgets.QGroupBox("Custom gradient")

        self.grBtoY = QtGui.QLinearGradient(0,0,1,100)
        self.grBtoY.setColorAt(1.0,QtCore.Qt.black)
        self.grBtoY.setColorAt(0.67,QtCore.Qt.blue)
        self.grBtoY.setColorAt(0.33,QtCore.Qt.red)
        self.grBtoY.setColorAt(0.0,QtCore.Qt.yellow)
        self.pm = QtGui.QPixmap(24,100)
        self.pmp = QtGui.QPainter(self.pm)
        self.pmp.setBrush(QtGui.QBrush(self.grBtoY))
        self.pmp.setPen(QtCore.Qt.NoPen)
        self.pmp.drawRect(0,0,24,100)
        self.pmp.end()
        self.gradientBtoYPB = QtWidgets.QPushButton(self)
        self.gradientBtoYPB.setIcon(QtGui.QIcon(self.pm))
        self.gradientBtoYPB.setIconSize(QtCore.QSize(24,100))

        self.grGtoR = QtGui.QLinearGradient(0,0,1,100)
        self.grGtoR.setColorAt(1.0,QtCore.Qt.darkGreen)
        self.grGtoR.setColorAt(0.5,QtCore.Qt.yellow)
        self.grGtoR.setColorAt(0.2,QtCore.Qt.red)
        self.grGtoR.setColorAt(0.0,QtCore.Qt.darkRed)
        self.pm2 = QtGui.QPixmap(24,100)
        self.pmp2 = QtGui.QPainter(self.pm2)
        self.pmp2.setBrush(QtGui.QBrush(self.grGtoR))
        self.pmp2.drawRect(0,0,24,100)
        self.pmp2.end()
        self.gradientGtoRPB = QtWidgets.QPushButton(self)
        self.gradientGtoRPB.setIcon(QtGui.QIcon(self.pm2))
        self.gradientGtoRPB.setIconSize(QtCore.QSize(24,100))

        self.colorHBox = QtWidgets.QHBoxLayout()
        self.colorHBox.addWidget(self.gradientBtoYPB)
        self.colorHBox.addWidget(self.gradientGtoRPB)
        self.colorGroupBox.setLayout(self.colorHBox)

        self.vLayout.addWidget(self.chooseGraph)
        self.vLayout.addWidget(self.modelGroupBox)
        self.vLayout.addWidget(self.selectionGroupBox)
        self.vLayout.addWidget(QtWidgets.QLabel("Column Range"))
        self.vLayout.addWidget(self.axisMinSliderX)
        self.vLayout.addWidget(self.axisMaxSliderX)
        self.vLayout.addWidget(QtWidgets.QLabel("Row Range"))
        self.vLayout.addWidget(self.axisMinSliderZ)
        self.vLayout.addWidget(self.axisMaxSliderZ)
        self.vLayout.addWidget(QtWidgets.QLabel("Theme"))
        self.vLayout.addWidget(self.themeList)
        self.vLayout.addWidget(self.colorGroupBox)

        self.show()

        self.heightMapModelRB.toggled.connect(self.graph.enableHeightMapModel)
        self.sqrtSinModelRB.toggled.connect(self.graph.enableSqrtSinModel)
        self.modeNoneRB.toggled.connect(self.graph.toggleModeNone)
        self.modeItemRB.toggled.connect(self.graph.toggleModeItem)
        self.modeSliceRowRB.toggled.connect(self.graph.toggleModeSliceRow)
        self.modeSliceColumnRB.toggled.connect(self.graph.toggleModeSliceColumn)
        self.axisMinSliderX.valueChanged.connect(self.graph.adjustXMin)
        self.axisMaxSliderX.valueChanged.connect(self.graph.adjustXMax)
        self.axisMinSliderZ.valueChanged.connect(self.graph.adjustZMin)
        self.axisMaxSliderZ.valueChanged.connect(self.graph.adjustZMax)
        self.themeList.currentIndexChanged.connect(self.graph.changeTheme)
        self.gradientBtoYPB.pressed.connect(self.graph.setBlackToYellowGradient)
        self.gradientGtoRPB.pressed.connect(self.graph.setGreenToRedGradient)

        self.graph.setAxisMinSliderX(self.axisMinSliderX)
        self.graph.setAxisMaxSliderX(self.axisMaxSliderX)
        self.graph.setAxisMinSliderZ(self.axisMinSliderZ)
        self.graph.setAxisMaxSliderZ(self.axisMaxSliderZ)

        self.sqrtSinModelRB.setChecked(False)
        self.heightMapModelRB.setChecked(False)
        self.modeItemRB.setChecked(True)
        self.themeList.setCurrentIndex(3)

    def Choose_Graph(self):
        path = QtWidgets.QFileDialog.getOpenFileName(None,"choose the graph",self.graphPath)
        self.graphPath = path[0]
        self.graphPathExtension = os.path.splitext(self.graphPath)[1]
        self.chooseSourceLabel.setText("The path of the graph is:\n"+self.graphPath)


class SurfaceGraph(QtDataVisualization.Q3DSurface,Process.Image):

    sampleCountX = 100
    sampleCountZ = 100
    heightMapGridStepX = 2
    heightMapGridStepZ = 2
    sampleMin = -8.0
    sampleMax = 8.0

    def __init__(self):
        super(SurfaceGraph,self).__init__()
        self.m_sqrtSinProxy = QtDataVisualization.QSurfaceDataProxy()
        self.m_sqrtSinSeries = QtDataVisualization.QSurface3DSeries(self.m_sqrtSinProxy)
        self.fillSqrtSinProxy()
        self.heightMapImage= self.getImage(16,"Img0000.nef", False, 20, 50, [1200,2650,500,3100])[0]
        self.m_heightMapProxy = QtDataVisualization.QHeightMapSurfaceDataProxy(self.heightMapImage)
        self.m_heightMapSeries = QtDataVisualization.QSurface3DSeries(self.m_heightMapProxy)
        self.m_heightMapSeries.setItemLabelFormat("(@xLabel,@zLabel): @yLabel")
        self.m_heightMapProxy.setValueRanges(34.0,40.0,18.0,24.0)
        self.m_heightMapWidth = self.heightMapImage.width()
        self.m_heightMapHeight = self.heightMapImage.height()
        self.setHorizontalAspectRatio(1)

    def fillSqrtSinProxy(self):
        stepX = (self.sampleMax - self.sampleMin) / float(self.sampleCountX - 1)
        stepZ = (self.sampleMax - self.sampleMin) / float(self.sampleCountZ - 1)
        dataArray = []
        for i in range(0, self.sampleCountZ):
            newRow = []
            z = min(self.sampleMax, (i * stepZ + self.sampleMin))
            for j in range(0,self.sampleCountX):
                x = min(self.sampleMax, (j * stepX + self.sampleMin))
                R = np.sqrt(z * z + x * x) + 0.01
                y = (np.sin(R) / R + 0.24) * 1.61
                data = QtDataVisualization.QSurfaceDataItem()
                data.setPosition(QtGui.QVector3D(x, y, z))
                newRow.append(data)
            dataArray.append(newRow)
        self.m_sqrtSinProxy.resetArray(dataArray)

    def fillTwoDimensionalMappingProxy(self):
        if self.graphPathExtension == '.txt':
            map = np.loadtxt(self.graphPath)
            print(map.shape)
            #dataArray = []
            #for i in range(0, self.sampleCountZ):
            #    newRow = []
            #    z = min(self.sampleMax, (i * stepZ + self.sampleMin))
            #    for j in range(0,self.sampleCountX):
            #        x = min(self.sampleMax, (j * stepX + self.sampleMin))
            #        R = np.sqrt(z * z + x * x) + 0.01
            #        y = (np.sin(R) / R + 0.24) * 1.61
            #        data = QtDataVisualization.QSurfaceDataItem()
            #        data.setPosition(QtGui.QVector3D(x, y, z))
            #        newRow.append(data)
            #    dataArray.append(newRow)
            #self.m_sqrtSinProxy.resetArray(dataArray)

    def enableSqrtSinModel(self,enable):
        if enable:
            self.m_sqrtSinSeries.setDrawMode(QtDataVisualization.QSurface3DSeries.DrawSurfaceAndWireframe)
            self.m_sqrtSinSeries.setFlatShadingEnabled(True)

            self.axisX().setLabelFormat("%.2f")
            self.axisZ().setLabelFormat("%.2f")
            self.axisX().setRange(self.sampleMin, self.sampleMax)
            self.axisY().setRange(0.0, 2.0)
            self.axisZ().setRange(self.sampleMin, self.sampleMax)
            self.axisX().setLabelAutoRotation(30)
            self.axisY().setLabelAutoRotation(90)
            self.axisZ().setLabelAutoRotation(30)

            self.removeSeries(self.m_heightMapSeries)
            self.addSeries(self.m_sqrtSinSeries)

            self.m_rangeMinX = self.sampleMin
            self.m_rangeMinZ = self.sampleMin
            self.m_stepX = (self.sampleMax - self.sampleMin) / float(self.sampleCountX - 1)
            self.m_stepZ = (self.sampleMax - self.sampleMin) / float(self.sampleCountZ - 1)
            self.m_axisMinSliderX.setMaximum(self.sampleCountX - 2)
            self.m_axisMinSliderX.setValue(0)
            self.m_axisMaxSliderX.setMaximum(self.sampleCountX - 1)
            self.m_axisMaxSliderX.setValue(self.sampleCountX - 1)
            self.m_axisMinSliderZ.setMaximum(self.sampleCountZ - 2)
            self.m_axisMinSliderZ.setValue(0)
            self.m_axisMaxSliderZ.setMaximum(self.sampleCountZ - 1)
            self.m_axisMaxSliderZ.setValue(self.sampleCountZ - 1)

    def enableHeightMapModel(self,enable):
        if enable:
            self.m_heightMapSeries.setDrawMode(QtDataVisualization.QSurface3DSeries.DrawSurface)
            self.m_heightMapSeries.setFlatShadingEnabled(False)

            self.axisX().setLabelFormat("%.1f N")
            self.axisZ().setLabelFormat("%.1f E")
            self.axisX().setRange(34.0, 40.0)
            self.axisY().setAutoAdjustRange(True)
            self.axisZ().setRange(18.0, 24.0)

            self.axisX().setTitle("Latitude")
            self.axisY().setTitle("Height")
            self.axisZ().setTitle("Longitude")

            self.removeSeries(self.m_sqrtSinSeries)
            self.addSeries(self.m_heightMapSeries)

            self.mapGridCountX = self.m_heightMapWidth / self.heightMapGridStepX
            self.mapGridCountZ = self.m_heightMapHeight / self.heightMapGridStepZ
            self.m_rangeMinX = 34.0
            self.m_rangeMinZ = 18.0
            self.m_stepX = 6.0 / float(self.mapGridCountX - 1)
            self.m_stepZ = 6.0 / float(self.mapGridCountZ - 1)
            self.m_axisMinSliderX.setMaximum(self.mapGridCountX - 2)
            self.m_axisMinSliderX.setValue(0)
            self.m_axisMaxSliderX.setMaximum(self.mapGridCountX - 1)
            self.m_axisMaxSliderX.setValue(self.mapGridCountX - 1)
            self.m_axisMinSliderZ.setMaximum(self.mapGridCountZ - 2)
            self.m_axisMinSliderZ.setValue(0)
            self.m_axisMaxSliderZ.setMaximum(self.mapGridCountZ - 1)
            self.m_axisMaxSliderZ.setValue(self.mapGridCountZ - 1)

    def adjustXMin(self,min):
        self.minX = self.m_stepX * float(min) + self.m_rangeMinX
        self.max = self.m_axisMaxSliderX.value()
        if min >= self.max:
            self.max = min + 1
            self.m_axisMaxSliderX.setValue(self.max)
        self.maxX = self.m_stepX * self.max + self.m_rangeMinX
        self.setAxisXRange(self.minX, self.maxX)

    def adjustXMax(self, max):
        self.maxX = self.m_stepX * float(max) + self.m_rangeMinX
        self.min = self.m_axisMinSliderX.value()
        if max <= self.min:
            self.min = max - 1
            self.m_axisMinSliderX.setValue(self.min)
        self.minX = self.m_stepX * self.min + self.m_rangeMinX
        self.setAxisXRange(self.minX, self.maxX)

    def adjustZMin(self,min):
        self.minZ = self.m_stepZ * float(min) + self.m_rangeMinZ
        self.max = self.m_axisMaxSliderZ.value()
        if min >= self.max:
            self.max = min + 1
            self.m_axisMaxSliderZ.setValue(self.max)
        self.maxZ = self.m_stepZ * self.max + self.m_rangeMinZ
        self.setAxisZRange(self.minZ, self.maxZ)

    def adjustZMax(self, max):
        self.maxX = self.m_stepZ * float(max) + self.m_rangeMinZ
        self.min = self.m_axisMinSliderZ.value()
        if max <= self.min:
            self.min = max - 1
            self.m_axisMinSliderZ.setValue(self.min)
        self.minX = self.m_stepZ * self.min + self.m_rangeMinZ
        self.setAxisZRange(self.minX, self.maxX)

    def setAxisXRange(self, min, max):
        self.axisX().setRange(min, max)

    def setAxisZRange(self, min, max):
        self.axisZ().setRange(min, max)

    def changeTheme(self, theme):
        self.activeTheme().setType(QtDataVisualization.Q3DTheme.Theme(theme))

    def setBlackToYellowGradient(self):
        self.gr = QtGui.QLinearGradient()
        self.gr.setColorAt(0.0, QtCore.Qt.black)
        self.gr.setColorAt(0.33, QtCore.Qt.blue)
        self.gr.setColorAt(0.67, QtCore.Qt.red)
        self.gr.setColorAt(1.0, QtCore.Qt.yellow)
        self.seriesList()[0].setBaseGradient(self.gr)
        self.seriesList()[0].setColorStyle(QtDataVisualization.Q3DTheme.ColorStyleRangeGradient)

    def setGreenToRedGradient(self):
        self.gr = QtGui.QLinearGradient()
        self.gr.setColorAt(0.0, QtCore.Qt.darkGreen)
        self.gr.setColorAt(0.5, QtCore.Qt.yellow)
        self.gr.setColorAt(0.8, QtCore.Qt.red)
        self.gr.setColorAt(1.0, QtCore.Qt.darkRed)
        self.seriesList()[0].setBaseGradient(self.gr)
        self.seriesList()[0].setColorStyle(QtDataVisualization.Q3DTheme.ColorStyleRangeGradient)

    def toggleModeNone(self):
        self.setSelectionMode(QtDataVisualization.QAbstract3DGraph.SelectionNone)

    def toggleModeItem(self):
        self.setSelectionMode(QtDataVisualization.QAbstract3DGraph.SelectionItem)

    def toggleModeSliceRow(self):
        self.setSelectionMode(QtDataVisualization.QAbstract3DGraph.SelectionItemAndRow \
                                      or QtDataVisualization.QAbstract3DGraph.SelectionSlice)

    def toggleModeSliceColumn(self):
        self.setSelectionMode(QtDataVisualization.QAbstract3DGraph.SelectionItemAndColumn \
                                      or QtDataVisualization.QAbstract3DGraph.SelectionSlice)

    def setAxisMinSliderX(self,slider):
        self.m_axisMinSliderX = slider

    def setAxisMaxSliderX(self,slider):
        self.m_axisMaxSliderX = slider

    def setAxisMinSliderZ(self,slider):
        self.m_axisMinSliderZ = slider

    def setAxisMaxSliderZ(self,slider):
        self.m_axisMaxSliderZ = slider

