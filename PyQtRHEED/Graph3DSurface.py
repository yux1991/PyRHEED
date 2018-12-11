from PyQt5 import QtCore, QtGui, QtWidgets, QtDataVisualization
import Process
import numpy as np

class Graph(QtWidgets.QWidget):

    def __init__(self):
        super(Graph,self).__init__()

    def main(self):
        self.graph = SurfaceGraph()
        container = QtWidgets.QWidget.createWindowContainer(self.graph)
        screenSize = self.graph.screen().size()
        container.setMinimumSize(screenSize.width()/2, screenSize.height()/2)
        container.setMaximumSize(screenSize)
        container.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        container.setFocusPolicy(QtCore.Qt.StrongFocus)

        hLayout = QtWidgets.QHBoxLayout(self)
        vLayout = QtWidgets.QVBoxLayout()
        hLayout.addWidget(container,1)
        hLayout.addLayout(vLayout)
        vLayout.setAlignment(QtCore.Qt.AlignTop)
        self.setWindowTitle("Surface example")
        self.setWindowModality(QtCore.Qt.WindowModal)

        modelGroupBox = QtWidgets.QGroupBox("Model")
        sqrtSinModelRB = QtWidgets.QRadioButton(self)
        sqrtSinModelRB.setText("Sqrt && Sin")
        heightMapModelRB = QtWidgets.QRadioButton(self)
        heightMapModelRB.setText("Height Map")
        heightMapModelRB.setChecked(False)

        modelVBox = QtWidgets.QVBoxLayout()
        modelVBox.addWidget(sqrtSinModelRB)
        modelVBox.addWidget(heightMapModelRB)
        modelGroupBox.setLayout(modelVBox)

        selectionGroupBox = QtWidgets.QGroupBox("Selection Mode")
        modeNoneRB = QtWidgets.QRadioButton(self)
        modeNoneRB.setText("No Selection")
        modeNoneRB.setChecked(False)

        modeItemRB = QtWidgets.QRadioButton(self)
        modeItemRB.setText("Item")
        modeItemRB.setChecked(False)

        modeSliceRowRB = QtWidgets.QRadioButton(self)
        modeSliceRowRB.setText("Row Slice")
        modeSliceRowRB.setChecked(False)

        modeSliceColumnRB = QtWidgets.QRadioButton(self)
        modeSliceColumnRB.setText("Column Slice")
        modeSliceColumnRB.setChecked(False)

        selectionVBox = QtWidgets.QVBoxLayout()
        selectionVBox.addWidget(modeNoneRB)
        selectionVBox.addWidget(modeItemRB)
        selectionVBox.addWidget(modeSliceRowRB)
        selectionVBox.addWidget(modeSliceColumnRB)
        selectionGroupBox.setLayout(selectionVBox)

        axisMinSliderX = QtWidgets.QSlider(QtCore.Qt.Horizontal,self)
        axisMinSliderX.setMinimum(0)
        axisMinSliderX.setTickInterval(1)
        axisMinSliderX.setEnabled(True)
        axisMaxSliderX = QtWidgets.QSlider(QtCore.Qt.Horizontal,self)
        axisMaxSliderX.setMinimum(1)
        axisMaxSliderX.setTickInterval(1)
        axisMaxSliderX.setEnabled(True)
        axisMinSliderZ = QtWidgets.QSlider(QtCore.Qt.Horizontal,self)
        axisMinSliderZ.setMinimum(0)
        axisMinSliderZ.setTickInterval(1)
        axisMinSliderZ.setEnabled(True)
        axisMaxSliderZ = QtWidgets.QSlider(QtCore.Qt.Horizontal,self)
        axisMaxSliderZ.setMinimum(1)
        axisMaxSliderZ.setTickInterval(1)
        axisMaxSliderZ.setEnabled(True)

        themeList = QtWidgets.QComboBox(self)
        themeList.addItem("Qt")
        themeList.addItem("Primary Colors")
        themeList.addItem("Digia")
        themeList.addItem("Stone Moss")
        themeList.addItem("Army Blue")
        themeList.addItem("Retro")
        themeList.addItem("Ebony")
        themeList.addItem("Isabelle")

        colorGroupBox = QtWidgets.QGroupBox("Custom gradient")

        grBtoY = QtGui.QLinearGradient(0,0,1,100)
        grBtoY.setColorAt(1.0,QtCore.Qt.black)
        grBtoY.setColorAt(0.67,QtCore.Qt.blue)
        grBtoY.setColorAt(0.33,QtCore.Qt.red)
        grBtoY.setColorAt(0.0,QtCore.Qt.yellow)
        pm = QtGui.QPixmap(24,100)
        pmp = QtGui.QPainter(pm)
        pmp.setBrush(QtGui.QBrush(grBtoY))
        pmp.setPen(QtCore.Qt.NoPen)
        pmp.drawRect(0,0,24,100)
        pmp.end()
        gradientBtoYPB = QtWidgets.QPushButton(self)
        gradientBtoYPB.setIcon(QtGui.QIcon(pm))
        gradientBtoYPB.setIconSize(QtCore.QSize(24,100))

        grGtoR = QtGui.QLinearGradient(0,0,1,100)
        grGtoR.setColorAt(1.0,QtCore.Qt.darkGreen)
        grGtoR.setColorAt(0.5,QtCore.Qt.yellow)
        grGtoR.setColorAt(0.2,QtCore.Qt.red)
        grGtoR.setColorAt(0.0,QtCore.Qt.darkRed)
        pm2 = QtGui.QPixmap(24,100)
        pmp2 = QtGui.QPainter(pm2)
        pmp2.setBrush(QtGui.QBrush(grGtoR))
        pmp2.drawRect(0,0,24,100)
        pmp2.end()
        gradientGtoRPB = QtWidgets.QPushButton(self)
        gradientGtoRPB.setIcon(QtGui.QIcon(pm2))
        gradientGtoRPB.setIconSize(QtCore.QSize(24,100))

        colorHBox = QtWidgets.QHBoxLayout()
        colorHBox.addWidget(gradientBtoYPB)
        colorHBox.addWidget(gradientGtoRPB)
        colorGroupBox.setLayout(colorHBox)

        vLayout.addWidget(modelGroupBox)
        vLayout.addWidget(selectionGroupBox)
        vLayout.addWidget(QtWidgets.QLabel("Column Range"))
        vLayout.addWidget(axisMinSliderX)
        vLayout.addWidget(axisMaxSliderX)
        vLayout.addWidget(QtWidgets.QLabel("Row Range"))
        vLayout.addWidget(axisMinSliderZ)
        vLayout.addWidget(axisMaxSliderZ)
        vLayout.addWidget(QtWidgets.QLabel("Theme"))
        vLayout.addWidget(themeList)
        vLayout.addWidget(colorGroupBox)

        self.show()

        heightMapModelRB.toggled.connect(self.graph.enableHeightMapModel)
        sqrtSinModelRB.toggled.connect(self.graph.enableSqrtSinModel)
        modeNoneRB.toggled.connect(self.graph.toggleModeNone)
        modeItemRB.toggled.connect(self.graph.toggleModeItem)
        modeSliceRowRB.toggled.connect(self.graph.toggleModeSliceRow)
        modeSliceColumnRB.toggled.connect(self.graph.toggleModeSliceColumn)
        axisMinSliderX.valueChanged.connect(self.graph.adjustXMin)
        axisMaxSliderX.valueChanged.connect(self.graph.adjustXMax)
        axisMinSliderZ.valueChanged.connect(self.graph.adjustZMin)
        axisMaxSliderZ.valueChanged.connect(self.graph.adjustZMax)
        themeList.currentIndexChanged.connect(self.graph.changeTheme)
        gradientBtoYPB.pressed.connect(self.graph.setBlackToYellowGradient)
        gradientGtoRPB.pressed.connect(self.graph.setGreenToRedGradient)

        self.graph.setAxisMinSliderX(axisMinSliderX)
        self.graph.setAxisMaxSliderX(axisMaxSliderX)
        self.graph.setAxisMinSliderZ(axisMinSliderZ)
        self.graph.setAxisMaxSliderZ(axisMaxSliderZ)

        sqrtSinModelRB.setChecked(True)
        modeItemRB.setChecked(True)
        themeList.setCurrentIndex(3)

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

