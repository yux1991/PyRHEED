from PyQt5 import QtCore, QtGui, QtWidgets, QtDataVisualization
import Process
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import pandas as pd
import os
import math

class Graph(QtWidgets.QWidget):

    show2DContourSignal = QtCore.pyqtSignal(str,bool,float,float,float,float,int,str)

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
        self.mainVLayout = QtWidgets.QVBoxLayout(self)
        self.hLayout = QtWidgets.QHBoxLayout()
        self.vLayout = QtWidgets.QVBoxLayout()
        self.hLayout.addWidget(self.container,1)
        self.vLayout.setAlignment(QtCore.Qt.AlignTop)
        self.hLayout.addLayout(self.vLayout)
        self.mainVLayout.addLayout(self.hLayout)
        self.setWindowTitle("3D Surface")
        self.setWindowModality(QtCore.Qt.WindowModal)

        self.chooseGraph = QtWidgets.QGroupBox("Choose Graph")
        self.chooseGraph.setStyleSheet('QGroupBox::title {color:blue;}')
        self.chooseGraphGrid = QtWidgets.QGridLayout(self.chooseGraph)
        self.chooseSourceLabel = QtWidgets.QLabel("The path of the graph is:\n"+self.graphPath)
        self.chooseSourceLabel.setAlignment(QtCore.Qt.AlignTop)
        self.chooseSourceLabel.setFixedWidth(250)
        self.chooseSourceLabel.setFixedHeight(75)
        self.chooseSourceLabel.setWordWrap(True)
        self.chooseSourceButton = QtWidgets.QPushButton("Browse")
        self.chooseSourceButton.clicked.connect(self.Choose_Graph)
        self.chooseGraphGrid.addWidget(self.chooseSourceLabel,0,0)
        self.chooseGraphGrid.addWidget(self.chooseSourceButton,1,0)

        self.plotOptions = QtWidgets.QGroupBox("Contour Plot Options")
        self.plotOptions.setStyleSheet('QGroupBox::title {color:blue;}')
        self.plotOptionsVBox = QtWidgets.QVBoxLayout(self.plotOptions)
        self.plotOptionsGrid = QtWidgets.QGridLayout()
        self.colormapLabel = QtWidgets.QLabel("Colormap")
        self.colormap = QtWidgets.QComboBox()
        self.colormap.addItem("jet","jet")
        self.colormap.addItem("hsv","hsv")
        self.colormap.addItem("rainbow","rainbow")
        self.colormap.addItem("nipy_spectral","nipy_spectral")
        self.levelMinLabel = QtWidgets.QLabel("Level Min ({})".format(0.0))
        self.levelMinSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.levelMinSlider.setMinimum(0)
        self.levelMinSlider.setMaximum(100)
        self.levelMinSlider.setValue(0)
        self.levelMinSlider.valueChanged.connect(self.Refresh_Level_Min)
        self.levelMaxLabel = QtWidgets.QLabel("Level Max ({})".format(1.0))
        self.levelMaxSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.levelMaxSlider.setMinimum(0)
        self.levelMaxSlider.setMaximum(100)
        self.levelMaxSlider.setValue(100)
        self.levelMaxSlider.valueChanged.connect(self.Refresh_Level_Max)
        self.radiusMinLabel = QtWidgets.QLabel("Radius Min ({})".format(0.0))
        self.radiusMinSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.radiusMinSlider.setMinimum(0)
        self.radiusMinSlider.setMaximum(1000)
        self.radiusMinSlider.setValue(0)
        self.radiusMinSlider.valueChanged.connect(self.Refresh_Radius_Min)
        self.radiusMaxLabel = QtWidgets.QLabel("Radius Max ({})".format(10.0))
        self.radiusMaxSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.radiusMaxSlider.setMinimum(0)
        self.radiusMaxSlider.setMaximum(1000)
        self.radiusMaxSlider.setValue(1000)
        self.radiusMaxSlider.valueChanged.connect(self.Refresh_Radius_Max)
        self.numberOfContourLevelsLabel = QtWidgets.QLabel("Number of Contour Levels ({})".format(50))
        self.numberOfContourLevelsLabel.setFixedWidth(160)
        self.numberOfContourLevelsSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.numberOfContourLevelsSlider.setMinimum(5)
        self.numberOfContourLevelsSlider.setMaximum(100)
        self.numberOfContourLevelsSlider.setValue(50)
        self.numberOfContourLevelsSlider.valueChanged.connect(self.Refresh_Number_Of_Contour_Levels)
        self.show2DContourButton = QtWidgets.QPushButton("Show 2D Contour")
        self.show2DContourButton.clicked.connect(self.show2DContourButtonPressed)
        self.show2DContourButton.setEnabled(False)
        self.plotOptionsGrid.addWidget(self.colormapLabel,0,0)
        self.plotOptionsGrid.addWidget(self.colormap,0,1)
        self.plotOptionsGrid.addWidget(self.levelMinLabel,1,0)
        self.plotOptionsGrid.addWidget(self.levelMinSlider,1,1)
        self.plotOptionsGrid.addWidget(self.levelMaxLabel,2,0)
        self.plotOptionsGrid.addWidget(self.levelMaxSlider,2,1)
        self.plotOptionsGrid.addWidget(self.radiusMinLabel,3,0)
        self.plotOptionsGrid.addWidget(self.radiusMinSlider,3,1)
        self.plotOptionsGrid.addWidget(self.radiusMaxLabel,4,0)
        self.plotOptionsGrid.addWidget(self.radiusMaxSlider,4,1)
        self.plotOptionsGrid.addWidget(self.numberOfContourLevelsLabel,5,0)
        self.plotOptionsGrid.addWidget(self.numberOfContourLevelsSlider,5,1)
        self.plotOptionsVBox.addLayout(self.plotOptionsGrid)
        self.plotOptionsVBox.addWidget(self.show2DContourButton)

        self.themeList = QtWidgets.QComboBox(self)
        self.themeList.addItem("Qt")
        self.themeList.addItem("Primary Colors")
        self.themeList.addItem("Digia")
        self.themeList.addItem("Stone Moss")
        self.themeList.addItem("Army Blue")
        self.themeList.addItem("Retro")
        self.themeList.addItem("Ebony")
        self.themeList.addItem("Isabelle")

        self.colorGroupBox = QtWidgets.QGroupBox("3D Surface Colormap")
        self.colorGroupBox.setStyleSheet('QGroupBox::title {color:blue;}')

        self.grBtoY = QtGui.QLinearGradient(0,0,1,100)
        self.grBtoY.setColorAt(1.0,QtCore.Qt.black)
        self.grBtoY.setColorAt(0.67,QtCore.Qt.blue)
        self.grBtoY.setColorAt(0.33,QtCore.Qt.red)
        self.grBtoY.setColorAt(0.0,QtCore.Qt.yellow)
        self.pm = QtGui.QPixmap(50,100)
        self.pmp = QtGui.QPainter(self.pm)
        self.pmp.setBrush(QtGui.QBrush(self.grBtoY))
        self.pmp.setPen(QtCore.Qt.NoPen)
        self.pmp.drawRect(0,0,50,100)
        self.pmp.end()
        self.gradientBtoYPB = QtWidgets.QPushButton(self)
        self.gradientBtoYPB.setIcon(QtGui.QIcon(self.pm))
        self.gradientBtoYPB.setIconSize(QtCore.QSize(50,100))
        self.gradientBtoYPB.setEnabled(False)

        self.grGtoR = QtGui.QLinearGradient(0,0,1,100)
        self.grGtoR.setColorAt(1.0,QtCore.Qt.darkGreen)
        self.grGtoR.setColorAt(0.5,QtCore.Qt.yellow)
        self.grGtoR.setColorAt(0.2,QtCore.Qt.red)
        self.grGtoR.setColorAt(0.0,QtCore.Qt.darkRed)
        self.pm2 = QtGui.QPixmap(50,100)
        self.pmp2 = QtGui.QPainter(self.pm2)
        self.pmp2.setBrush(QtGui.QBrush(self.grGtoR))
        self.pmp2.drawRect(0,0,50,100)
        self.pmp2.end()
        self.gradientGtoRPB = QtWidgets.QPushButton(self)
        self.gradientGtoRPB.setIcon(QtGui.QIcon(self.pm2))
        self.gradientGtoRPB.setIconSize(QtCore.QSize(50,100))
        self.gradientGtoRPB.setEnabled(False)

        self.grBtoR = QtGui.QLinearGradient(0,0,1,100)
        self.grBtoR.setColorAt(1.0, QtCore.Qt.darkBlue)
        self.grBtoR.setColorAt(0.95, QtCore.Qt.blue)
        self.grBtoR.setColorAt(0.9, QtCore.Qt.darkCyan)
        self.grBtoR.setColorAt(0.8, QtCore.Qt.cyan)
        self.grBtoR.setColorAt(0.6, QtCore.Qt.green)
        self.grBtoR.setColorAt(0.2, QtCore.Qt.yellow)
        self.grBtoR.setColorAt(0.0, QtCore.Qt.red)
        self.pm3 = QtGui.QPixmap(50,100)
        self.pmp3 = QtGui.QPainter(self.pm3)
        self.pmp3.setBrush(QtGui.QBrush(self.grBtoR))
        self.pmp3.drawRect(0,0,50,100)
        self.pmp3.end()
        self.gradientBtoRPB = QtWidgets.QPushButton(self)
        self.gradientBtoRPB.setIcon(QtGui.QIcon(self.pm3))
        self.gradientBtoRPB.setIconSize(QtCore.QSize(50,100))
        self.gradientBtoRPB.setEnabled(False)

        self.colorHBox = QtWidgets.QHBoxLayout()
        self.colorHBox.addWidget(self.gradientBtoYPB)
        self.colorHBox.addWidget(self.gradientGtoRPB)
        self.colorHBox.addWidget(self.gradientBtoRPB)
        self.colorGroupBox.setLayout(self.colorHBox)

        self.statusBar = QtWidgets.QGroupBox("Log")
        self.statusBar.setStyleSheet('QGroupBox::title {color:blue;}')
        self.statusGrid = QtWidgets.QGridLayout(self.statusBar)
        self.statusBar.setFixedHeight(150)
        self.statusBar.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Fixed)
        self.logBox = QtWidgets.QTextEdit(QtCore.QTime.currentTime().toString("hh:mm:ss")+ \
                                          "\u00A0\u00A0\u00A0\u00A0Initialized!")
        self.logBox.ensureCursorVisible()
        self.logBox.setAlignment(QtCore.Qt.AlignTop)
        self.logBox.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.logBoxScroll = QtWidgets.QScrollArea()
        self.logBoxScroll.setWidget(self.logBox)
        self.logBoxScroll.setWidgetResizable(True)
        self.logBoxScroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.statusGrid.addWidget(self.logBoxScroll,0,0)

        self.vLayout.addWidget(self.chooseGraph)
        self.vLayout.addWidget(self.plotOptions)
        themeLabel = QtWidgets.QLabel("Theme")
        themeLabel.setStyleSheet("QLabel {color:blue;}")
        self.vLayout.addWidget(themeLabel)
        self.vLayout.addWidget(self.themeList)
        self.vLayout.addWidget(self.colorGroupBox)
        self.mainVLayout.addWidget(self.statusBar)

        self.show()

        self.themeList.currentIndexChanged.connect(self.graph.changeTheme)
        self.gradientBtoYPB.pressed.connect(self.graph.setBlackToYellowGradient)
        self.gradientGtoRPB.pressed.connect(self.graph.setGreenToRedGradient)
        self.gradientBtoRPB.pressed.connect(self.graph.setBlueToRedGradient)
        self.show2DContourSignal.connect(self.Show_2D_Contour)
        self.graph.logMessage.connect(self.updateLog)
        self.themeList.setCurrentIndex(3)

        if not path=='':
            self.graph.fillTwoDimensionalMappingProxy(path)
            self.graph.enableTwoDimensionalMappingModel(True)
            self.show2DContourButton.setEnabled(True)

    def Choose_Graph(self):
        path = QtWidgets.QFileDialog.getOpenFileName(None,"choose the graph",self.graphPath)
        self.graphPath = path[0]
        self.graphPathExtension = os.path.splitext(self.graphPath)[1]
        if not self.graphPathExtension == ".txt":
            self.Raise_Error('[Error: wrong file type] Please choose a *.txt file')
            self.updateLog('[Error: wrong file type] Please choose a *.txt file')
        else:
            self.chooseSourceLabel.setText("The path of the graph is:\n"+self.graphPath)
            self.updateLog("Loading DataArray...")
            QtCore.QCoreApplication.processEvents()
            self.graph.fillTwoDimensionalMappingProxy(self.graphPath)
            self.graph.enableTwoDimensionalMappingModel(True)
            self.show2DContourButton.setEnabled(True)
            self.gradientBtoYPB.setEnabled(True)
            self.gradientGtoRPB.setEnabled(True)
            self.gradientBtoRPB.setEnabled(True)

    def Refresh_Level_Min(self):
        self.levelMinLabel.setText("Level Min ({})".format(self.levelMinSlider.value()/100))
        if self.levelMinSlider.value() > self.levelMaxSlider.value():
            self.levelMaxSlider.setValue(self.levelMinSlider.value())

    def Refresh_Level_Max(self):
        self.levelMaxLabel.setText("Level Max ({})".format(self.levelMaxSlider.value()/100))
        if self.levelMinSlider.value() > self.levelMaxSlider.value():
            self.levelMinSlider.setValue(self.levelMaxSlider.value())

    def Refresh_Radius_Min(self):
        self.radiusMinLabel.setText("Radius Min ({})".format(self.radiusMinSlider.value()/100))
        if self.radiusMinSlider.value() > self.radiusMaxSlider.value():
            self.radiusMaxSlider.setValue(self.radiusMinSlider.value())

    def Refresh_Radius_Max(self):
        self.radiusMaxLabel.setText("Radius Max ({})".format(self.radiusMaxSlider.value()/100))
        if self.radiusMinSlider.value() > self.radiusMaxSlider.value():
            self.radiusMinSlider.setValue(self.radiusMaxSlider.value())

    def Refresh_Number_Of_Contour_Levels(self):
        self.numberOfContourLevelsLabel.setText("Number of Contour Levels ({})".format(self.numberOfContourLevelsSlider.value()))

    def show2DContourButtonPressed(self):
        self.updateLog("Showing contour plot...")
        QtCore.QCoreApplication.processEvents()
        self.show2DContourSignal.emit(self.graphPath,True,self.levelMinSlider.value()/100,self.levelMaxSlider.value()/100,\
                                      self.radiusMinSlider.value()/100,self.radiusMaxSlider.value()/100,\
                                      self.numberOfContourLevelsSlider.value(),self.colormap.currentText())

    def Show_2D_Contour(self,path, insideGraph3D = False, min=0.0, max=1.0, radius_min=0, radius_max=10, number_of_levels=50, colormap='jet'):
        window = QtWidgets.QDialog()
        layout = QtWidgets.QVBoxLayout(window)
        figure = plt.figure()
        canvas = FigureCanvas(figure)
        toolbar = NavigationToolbar(canvas,window)
        figure.clear()
        if not path == None:
            if os.path.splitext(path)[1] == '.txt':
                radius,theta,intensity = self.convertToRTI(path)
                levels = np.linspace(min,max,number_of_levels)
                ax = figure.add_subplot(111,polar = True)
                ax.contourf(theta,radius,intensity,levels=levels,cmap=colormap)
                ax.set_ylim(radius_min,radius_max)
                canvas.draw()
            else:
                self.Raise_Error('[Error: wrong file type] Please choose a *.txt file')
        else:
            self.Raise_Error('[Error: no file] Please choose a valid file first')
        layout.addWidget(toolbar)
        layout.addWidget(canvas)
        window.setWindowTitle("2D Contour")
        window.show()
        if insideGraph3D:
            window.finished.connect(self.contourPlotFinished)

    def contourPlotFinished(self):
        self.updateLog('Contour plot ended.')

    def updateLog(self,msg):
        self.logBox.append(QtCore.QTime.currentTime().toString("hh:mm:ss")+"\u00A0\u00A0\u00A0\u00A0"+msg)

    def convertToRTI(self,path):
        data =  np.loadtxt(path)
        df = pd.DataFrame(data,columns = ['radius','theta','intensity'])
        table = df.pivot_table(values = 'intensity',index='radius',columns='theta')
        return table.index.tolist(),[a/180*math.pi for a in table.columns.tolist()],table

    def Raise_Error(self,message):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.setEscapeButton(QtWidgets.QMessageBox.Close)
        msg.exec()

    def Raise_Attention(self,information):
        info = QtWidgets.QMessageBox()
        info.setIcon(QtWidgets.QMessageBox.Information)
        info.setText(information)
        info.setWindowTitle("Information")
        info.setStandardButtons(QtWidgets.QMessageBox.Ok)
        info.setEscapeButton(QtWidgets.QMessageBox.Close)
        info.exec()


class SurfaceGraph(QtDataVisualization.Q3DSurface,Process.Image):

    logMessage = QtCore.pyqtSignal(str)

    def __init__(self):
        super(SurfaceGraph,self).__init__()
        self.twoDimensionalMappingProxy = QtDataVisualization.QSurfaceDataProxy()
        self.twoDimensionalMappingSeries = QtDataVisualization.QSurface3DSeries(self.twoDimensionalMappingProxy)

    def convertToDataArray(self,path):
        data =  np.loadtxt(path)
        df = pd.DataFrame(data,columns = ['radius','theta','intensity'])
        table = df.pivot_table(values = 'intensity',index='radius',columns='theta')
        radius = table.index.tolist()
        theta = table.columns.tolist()
        self.sampleMin,self.sampleMax = -max(radius),max(radius)
        dataArray = []
        for i in range(table.shape[0]):
            newRow=[]
            for j in range(table.shape[1]):
                item = QtDataVisualization.QSurfaceDataItem()
                X,Y,Z = radius[i]*np.cos(theta[j]/180*math.pi),\
                        radius[i]*np.sin(theta[j]/180*math.pi),\
                        table.loc[radius[i],theta[j]]
                item.setPosition(QtGui.QVector3D(X,Z,Y))
                newRow.append(item)
            dataArray.append(newRow)
        return dataArray

    def fillTwoDimensionalMappingProxy(self,path):
        dataArray = self.convertToDataArray(path)
        self.twoDimensionalMappingProxy.resetArray(dataArray)
        self.logMessage.emit("DataArray Loaded!")

    def enableTwoDimensionalMappingModel(self,enable):
        if enable:
            for series in self.seriesList():
                self.removeSeries(series)
            self.twoDimensionalMappingSeries.setDrawMode(QtDataVisualization.QSurface3DSeries.DrawSurface)
            self.twoDimensionalMappingSeries.setFlatShadingEnabled(True)
            self.axisX().setLabelFormat("%.2f")
            self.axisZ().setLabelFormat("%.2f")
            self.axisX().setRange(self.sampleMin,self.sampleMax)
            self.axisY().setRange(0,1)
            self.axisZ().setRange(self.sampleMin,self.sampleMax)
            self.axisX().setTitle("Kx (\u212B\u207B\u00B9)")
            self.axisX().setTitleVisible(True)
            self.axisZ().setTitle("Ky (\u212B\u207B\u00B9)")
            self.axisZ().setTitleVisible(True)
            self.axisY().setTitle("Normalized Intensity (arb. units)")
            self.axisY().setTitleVisible(True)
            self.axisX().setLabelAutoRotation(30)
            self.axisY().setLabelAutoRotation(90)
            self.axisZ().setLabelAutoRotation(30)
            self.addSeries(self.twoDimensionalMappingSeries)

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

    def setBlueToRedGradient(self):
        self.gr = QtGui.QLinearGradient()
        self.gr.setColorAt(0.0, QtCore.Qt.darkBlue)
        self.gr.setColorAt(0.05, QtCore.Qt.blue)
        self.gr.setColorAt(0.1, QtCore.Qt.darkCyan)
        self.gr.setColorAt(0.2, QtCore.Qt.cyan)
        self.gr.setColorAt(0.4, QtCore.Qt.green)
        self.gr.setColorAt(0.8, QtCore.Qt.yellow)
        self.gr.setColorAt(1.0, QtCore.Qt.red)
        self.seriesList()[0].setBaseGradient(self.gr)
        self.seriesList()[0].setColorStyle(QtDataVisualization.Q3DTheme.ColorStyleRangeGradient)

    def Raise_Error(self,message):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.setEscapeButton(QtWidgets.QMessageBox.Close)
        msg.exec()

    def Raise_Attention(self,information):
        info = QtWidgets.QMessageBox()
        info.setIcon(QtWidgets.QMessageBox.Information)
        info.setText(information)
        info.setWindowTitle("Information")
        info.setStandardButtons(QtWidgets.QMessageBox.Ok)
        info.setEscapeButton(QtWidgets.QMessageBox.Close)
        info.exec()

