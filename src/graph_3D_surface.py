from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt6 import QtCore, QtGui, QtWidgets, QtDataVisualization
import math
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd

class Graph(QtWidgets.QWidget):

    SHOW_2D_CONTOUR_SIGNAL = QtCore.pyqtSignal(str,bool,float,float,float,float,int,str)

    def __init__(self):
        super(Graph,self).__init__()

    def run_3D_graph(self,path):
        self.graphPath = path
        self.graph = SurfaceGraph()
        self.container = QtWidgets.QWidget.createWindowContainer(self.graph)
        self.screenSize = self.graph.screen().size()
        self.container.setMinimumSize(int(self.screenSize.width()/2), int(self.screenSize.height()/2))
        self.container.setMaximumSize(self.screenSize)
        self.container.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,QtWidgets.QSizePolicy.Policy.Expanding)
        self.container.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.mainVLayout = QtWidgets.QVBoxLayout(self)
        self.hLayout = QtWidgets.QHBoxLayout()
        self.vLayout = QtWidgets.QVBoxLayout()
        self.hLayout.addWidget(self.container,1)
        self.vLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.hLayout.addLayout(self.vLayout)
        self.mainVLayout.addLayout(self.hLayout)
        self.setWindowTitle("3D Surface")
        self.setWindowModality(QtCore.Qt.WindowModality.WindowModal)

        self.chooseGraph = QtWidgets.QGroupBox("Choose Graph")
        self.chooseGraphGrid = QtWidgets.QGridLayout(self.chooseGraph)
        self.chooseSourceLabel = QtWidgets.QLabel("The path of the graph is:\n"+self.graphPath)
        self.chooseSourceLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.chooseSourceLabel.setFixedWidth(250)
        self.chooseSourceLabel.setFixedHeight(75)
        self.chooseSourceLabel.setWordWrap(True)
        self.chooseSourceButton = QtWidgets.QPushButton("Browse")
        self.chooseSourceButton.clicked.connect(self.choose_graph)
        self.chooseGraphGrid.addWidget(self.chooseSourceLabel,0,0)
        self.chooseGraphGrid.addWidget(self.chooseSourceButton,1,0)

        self.plotOptions = QtWidgets.QGroupBox("Contour Plot Options")
        self.plotOptionsVBox = QtWidgets.QVBoxLayout(self.plotOptions)
        self.plotOptionsGrid = QtWidgets.QGridLayout()
        self.colormapLabel = QtWidgets.QLabel("Colormap")
        self.colormap = QtWidgets.QComboBox()
        self.colormap.addItem("jet","jet")
        self.colormap.addItem("hsv","hsv")
        self.colormap.addItem("rainbow","rainbow")
        self.colormap.addItem("nipy_spectral","nipy_spectral")
        self.levelMinLabel = QtWidgets.QLabel("Level Min ({})".format(0.0))
        self.levelMinSlider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.levelMinSlider.setMinimum(0)
        self.levelMinSlider.setMaximum(100)
        self.levelMinSlider.setValue(0)
        self.levelMinSlider.valueChanged.connect(self.refresh_level_min)
        self.levelMaxLabel = QtWidgets.QLabel("Level Max ({})".format(1.0))
        self.levelMaxSlider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.levelMaxSlider.setMinimum(0)
        self.levelMaxSlider.setMaximum(100)
        self.levelMaxSlider.setValue(100)
        self.levelMaxSlider.valueChanged.connect(self.refresh_level_max)
        self.radiusMinLabel = QtWidgets.QLabel("Radius Min ({})".format(0.0))
        self.radiusMinSlider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.radiusMinSlider.setMinimum(0)
        self.radiusMinSlider.setMaximum(1000)
        self.radiusMinSlider.setValue(0)
        self.radiusMinSlider.valueChanged.connect(self.refresh_radius_min)
        self.radiusMaxLabel = QtWidgets.QLabel("Radius Max ({})".format(10.0))
        self.radiusMaxSlider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.radiusMaxSlider.setMinimum(0)
        self.radiusMaxSlider.setMaximum(1000)
        self.radiusMaxSlider.setValue(1000)
        self.radiusMaxSlider.valueChanged.connect(self.refresh_radius_max)
        self.numberOfContourLevelsLabel = QtWidgets.QLabel("Number of Contour Levels ({})".format(50))
        self.numberOfContourLevelsLabel.setFixedWidth(160)
        self.numberOfContourLevelsSlider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.numberOfContourLevelsSlider.setMinimum(5)
        self.numberOfContourLevelsSlider.setMaximum(100)
        self.numberOfContourLevelsSlider.setValue(50)
        self.numberOfContourLevelsSlider.valueChanged.connect(self.refresh_number_of_contour_levels)
        self.show2DContourButton = QtWidgets.QPushButton("Show 2D Contour")
        self.show2DContourButton.clicked.connect(self.show_2D_contour_button_pressed)
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

        self.grBtoY = QtGui.QLinearGradient(0,0,1,100)
        self.grBtoY.setColorAt(1.0,QtCore.Qt.GlobalColor.black)
        self.grBtoY.setColorAt(0.67,QtCore.Qt.GlobalColor.blue)
        self.grBtoY.setColorAt(0.33,QtCore.Qt.GlobalColor.red)
        self.grBtoY.setColorAt(0.0,QtCore.Qt.GlobalColor.yellow)
        self.pm = QtGui.QPixmap(50,100)
        self.pmp = QtGui.QPainter(self.pm)
        self.pmp.setBrush(QtGui.QBrush(self.grBtoY))
        self.pmp.setPen(QtCore.Qt.PenStyle.NoPen)
        self.pmp.drawRect(0,0,50,100)
        self.pmp.end()
        self.gradientBtoYPB = QtWidgets.QPushButton(self)
        self.gradientBtoYPB.setIcon(QtGui.QIcon(self.pm))
        self.gradientBtoYPB.setIconSize(QtCore.QSize(50,100))
        self.gradientBtoYPB.setEnabled(False)

        self.grGtoR = QtGui.QLinearGradient(0,0,1,100)
        self.grGtoR.setColorAt(1.0,QtCore.Qt.GlobalColor.darkGreen)
        self.grGtoR.setColorAt(0.5,QtCore.Qt.GlobalColor.yellow)
        self.grGtoR.setColorAt(0.2,QtCore.Qt.GlobalColor.red)
        self.grGtoR.setColorAt(0.0,QtCore.Qt.GlobalColor.darkRed)
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
        self.grBtoR.setColorAt(1.0, QtCore.Qt.GlobalColor.darkBlue)
        self.grBtoR.setColorAt(0.95, QtCore.Qt.GlobalColor.blue)
        self.grBtoR.setColorAt(0.9, QtCore.Qt.GlobalColor.darkCyan)
        self.grBtoR.setColorAt(0.8, QtCore.Qt.GlobalColor.cyan)
        self.grBtoR.setColorAt(0.6, QtCore.Qt.GlobalColor.green)
        self.grBtoR.setColorAt(0.2, QtCore.Qt.GlobalColor.yellow)
        self.grBtoR.setColorAt(0.0, QtCore.Qt.GlobalColor.red)
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
        self.statusGrid = QtWidgets.QGridLayout(self.statusBar)
        self.statusBar.setFixedHeight(150)
        self.statusBar.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,QtWidgets.QSizePolicy.Policy.Fixed)
        self.logBox = QtWidgets.QTextEdit(QtCore.QTime.currentTime().toString("hh:mm:ss")+ \
                                          "\u00A0\u00A0\u00A0\u00A0Initialized!")
        self.logCursor = QtGui.QTextCursor(self.logBox.document())
        self.logCursor.movePosition(QtGui.QTextCursor.MoveOperation.End)
        self.logBox.setTextCursor(self.logCursor)
        self.logBox.ensureCursorVisible()
        self.logBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.logBox.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.logBoxScroll = QtWidgets.QScrollArea()
        self.logBoxScroll.setWidget(self.logBox)
        self.logBoxScroll.setWidgetResizable(True)
        self.logBoxScroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
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
        desktopRect = self.geometry()
        center = desktopRect.center()
        self.move(int(center.x()-self.width()*0.5),int(center.y()-self.height()*0.5))

        self.themeList.currentIndexChanged.connect(self.graph.change_theme)
        self.gradientBtoYPB.pressed.connect(self.graph.set_black_to_yellow_gradient)
        self.gradientGtoRPB.pressed.connect(self.graph.set_green_to_red_gradient)
        self.gradientBtoRPB.pressed.connect(self.graph.set_blue_to_red_gradient)
        self.SHOW_2D_CONTOUR_SIGNAL.connect(self.show_2d_contour)
        self.graph.LOG_MESSAGE.connect(self.update_log)
        self.themeList.setCurrentIndex(3)

        if not path=='':
            self.graph.fill_two_dimensional_mapping_proxy(path)
            self.graph.enable_two_dimensional_mapping_model(True)
            self.show2DContourButton.setEnabled(True)
            self.gradientBtoYPB.setEnabled(True)
            self.gradientGtoRPB.setEnabled(True)
            self.gradientBtoRPB.setEnabled(True)

    def choose_graph(self):
        path = QtWidgets.QFileDialog.getOpenFileName(None,"choose the graph",self.graphPath)
        self.graphPath = path[0]
        self.graphPathExtension = os.path.splitext(self.graphPath)[1]
        if not self.graphPathExtension == ".txt":
            self.raise_error('[Error: wrong file type] Please choose a *.txt file')
            self.update_log('[Error: wrong file type] Please choose a *.txt file')
        else:
            self.chooseSourceLabel.setText("The path of the graph is:\n"+self.graphPath)
            self.update_log("Loading DataArray...")
            QtCore.QCoreApplication.processEvents()
            self.graph.fill_two_dimensional_mapping_proxy(self.graphPath)
            self.graph.enable_two_dimensional_mapping_model(True)
            self.show2DContourButton.setEnabled(True)
            self.gradientBtoYPB.setEnabled(True)
            self.gradientGtoRPB.setEnabled(True)
            self.gradientBtoRPB.setEnabled(True)

    def refresh_level_min(self):
        self.levelMinLabel.setText("Level Min ({})".format(self.levelMinSlider.value()/100))
        if self.levelMinSlider.value() > self.levelMaxSlider.value():
            self.levelMaxSlider.setValue(self.levelMinSlider.value())

    def refresh_level_max(self):
        self.levelMaxLabel.setText("Level Max ({})".format(self.levelMaxSlider.value()/100))
        if self.levelMinSlider.value() > self.levelMaxSlider.value():
            self.levelMinSlider.setValue(self.levelMaxSlider.value())

    def refresh_radius_min(self):
        self.radiusMinLabel.setText("Radius Min ({})".format(self.radiusMinSlider.value()/100))
        if self.radiusMinSlider.value() > self.radiusMaxSlider.value():
            self.radiusMaxSlider.setValue(self.radiusMinSlider.value())

    def refresh_radius_max(self):
        self.radiusMaxLabel.setText("Radius Max ({})".format(self.radiusMaxSlider.value()/100))
        if self.radiusMinSlider.value() > self.radiusMaxSlider.value():
            self.radiusMinSlider.setValue(self.radiusMaxSlider.value())

    def refresh_number_of_contour_levels(self):
        self.numberOfContourLevelsLabel.setText("Number of Contour Levels ({})".format(self.numberOfContourLevelsSlider.value()))

    def show_2D_contour_button_pressed(self):
        self.update_log("Showing contour plot...")
        QtCore.QCoreApplication.processEvents()
        self.SHOW_2D_CONTOUR_SIGNAL.emit(self.graphPath,True,self.levelMinSlider.value()/100,self.levelMaxSlider.value()/100,\
                                      self.radiusMinSlider.value()/100,self.radiusMaxSlider.value()/100,\
                                      self.numberOfContourLevelsSlider.value(),self.colormap.currentText())

    def show_2d_contour(self,path, insideGraph3D = False, min=0.0, max=1.0, radius_min=0, radius_max=10, number_of_levels=50, colormap='jet'):
        window = QtWidgets.QDialog()
        layout = QtWidgets.QVBoxLayout(window)
        figure = plt.figure()
        canvas = FigureCanvas(figure)
        toolbar = NavigationToolbar(canvas,window)
        figure.clear()
        if not path == None:
            if os.path.splitext(path)[1] == '.txt':
                radius,theta,intensity = self.convert_to_RTI(path)
                levels = np.linspace(min,max,number_of_levels)
                ax = figure.add_subplot(111,polar = True)
                ax.contourf(theta,radius,intensity,levels=levels,cmap=colormap)
                ax.set_ylim(radius_min,radius_max)
                canvas.draw()
            else:
                self.raise_error('[Error: wrong file type] Please choose a *.txt file')
        else:
            self.raise_error('[Error: no file] Please choose a valid file first')
        layout.addWidget(toolbar)
        layout.addWidget(canvas)
        window.setWindowTitle("2D Contour")
        window.show()
        if insideGraph3D:
            window.finished.connect(self.contour_plot_finished)

    def contour_plot_finished(self):
        self.update_log('Contour plot ended.')

    def update_log(self,msg):
        self.logBox.append(QtCore.QTime.currentTime().toString("hh:mm:ss")+"\u00A0\u00A0\u00A0\u00A0"+msg)

    def convert_to_RTI(self,path):
        raw_data =  np.loadtxt(path)
        if np.amin(raw_data[:,0])<0:
            data = np.empty(raw_data.shape)
            data[:,0] = np.abs(raw_data[:,0])
            data[:,1] = np.where(raw_data[:,0]>0,0,180)+raw_data[:,1]
            data[:,2] = raw_data[:,2]
        else:
            data = raw_data
        df = pd.DataFrame(data,columns = ['radius','theta','intensity'])
        table = df.pivot_table(values = 'intensity',index='radius',columns='theta')
        return table.index.tolist(),[a/180*math.pi for a in table.columns.tolist()],table

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


class SurfaceGraph(QtDataVisualization.Q3DSurface):

    LOG_MESSAGE = QtCore.pyqtSignal(str)

    def __init__(self):
        super(SurfaceGraph,self).__init__()
        self.twoDimensionalMappingProxy = QtDataVisualization.QSurfaceDataProxy()
        self.twoDimensionalMappingSeries = QtDataVisualization.QSurface3DSeries(self.twoDimensionalMappingProxy)

    def convert_to_data_array(self,path):
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

    def fill_two_dimensional_mapping_proxy(self,path):
        dataArray = self.convert_to_data_array(path)
        self.twoDimensionalMappingProxy.resetArray(dataArray)
        self.LOG_MESSAGE.emit("DataArray Loaded!")

    def enable_two_dimensional_mapping_model(self,enable):
        if enable:
            for series in self.seriesList():
                self.removeSeries(series)
            self.twoDimensionalMappingSeries.setDrawMode(QtDataVisualization.QSurface3DSeries.DrawFlag.DrawSurface)
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

    def change_theme(self, theme):
        self.activeTheme().setType(QtDataVisualization.Q3DTheme.Theme(theme))

    def set_black_to_yellow_gradient(self):
        self.gr = QtGui.QLinearGradient()
        self.gr.setColorAt(0.0, QtCore.Qt.GlobalColor.black)
        self.gr.setColorAt(0.33, QtCore.Qt.GlobalColor.blue)
        self.gr.setColorAt(0.67, QtCore.Qt.GlobalColor.red)
        self.gr.setColorAt(1.0, QtCore.Qt.GlobalColor.yellow)
        self.seriesList()[0].setBaseGradient(self.gr)
        self.seriesList()[0].setColorStyle(QtDataVisualization.Q3DTheme.ColorStyle.ColorStyleRangeGradient)

    def set_green_to_red_gradient(self):
        self.gr = QtGui.QLinearGradient()
        self.gr.setColorAt(0.0, QtCore.Qt.GlobalColor.darkGreen)
        self.gr.setColorAt(0.5, QtCore.Qt.GlobalColor.yellow)
        self.gr.setColorAt(0.8, QtCore.Qt.GlobalColor.red)
        self.gr.setColorAt(1.0, QtCore.Qt.GlobalColor.darkRed)
        self.seriesList()[0].setBaseGradient(self.gr)
        self.seriesList()[0].setColorStyle(QtDataVisualization.Q3DTheme.ColorStyle.ColorStyleRangeGradient)

    def set_blue_to_red_gradient(self):
        self.gr = QtGui.QLinearGradient()
        self.gr.setColorAt(0.0, QtCore.Qt.GlobalColor.darkBlue)
        self.gr.setColorAt(0.05, QtCore.Qt.GlobalColor.blue)
        self.gr.setColorAt(0.1, QtCore.Qt.GlobalColor.darkCyan)
        self.gr.setColorAt(0.2, QtCore.Qt.GlobalColor.cyan)
        self.gr.setColorAt(0.4, QtCore.Qt.GlobalColor.green)
        self.gr.setColorAt(0.8, QtCore.Qt.GlobalColor.yellow)
        self.gr.setColorAt(1.0, QtCore.Qt.GlobalColor.red)
        self.seriesList()[0].setBaseGradient(self.gr)
        self.seriesList()[0].setColorStyle(QtDataVisualization.Q3DTheme.ColorStyle.ColorStyleRangeGradient)

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

