from PyQt6 import QtCore, QtGui, QtWidgets, QtDataVisualization
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib import ticker, cm, colors
from my_widgets import LabelSlider
import matplotlib.pyplot as plt
import numpy as np
import sys

class Window(QtWidgets.QWidget):
    SHOW_2D_CONTOUR_SIGNAL = QtCore.pyqtSignal(list,float,float,float,float,str,int,str)
    FONTS_CHANGED = QtCore.pyqtSignal(str,int)
    def __init__(self):
        super(Window, self).__init__()

    def main(self):
        self.mainSplitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        self.mainFrame = QtWidgets.QFrame()
        self.mainGrid = QtWidgets.QGridLayout(self.mainFrame)
        self.mainGrid.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.Options = QtWidgets.QGroupBox("Options")
        self.OptionsGrid = QtWidgets.QGridLayout(self.Options)
        self.Eta = LabelSlider(0,100,0.5,100,"\u03B7 (\u03C0)")
        self.Epsilon = LabelSlider(0,200,0.01,1000,"\u03B5")
        self.AsymmetricRatio = LabelSlider(100,500,1,100,"Step Atom Density Asymmetric Ratio")
        self.x_range = LabelSlider(0,400,10,10,"x range")
        self.z_range = LabelSlider(0,400,10,10,"z range")
        self.x_step = LabelSlider(10,400,0.1,2000,"x step")
        self.z_step = LabelSlider(10,400,0.1,2000,"z step")
        self.R_label = QtWidgets.QLabel("R =")
        self.latticeConstantLabel = QtWidgets.QLabel("Lattice Constant:")
        self.latticeConstant = QtWidgets.QLineEdit('3.15')
        self.chooseUnitLabel = QtWidgets.QLabel("Choose Unit:")
        self.chooseUnit = QtWidgets.QComboBox()
        self.chooseUnit.addItem("Brillouin Zone %")
        self.chooseUnit.addItem("\u212B\u207B\u00B9")
        self.chooseUnit.currentTextChanged.connect(self.unit_changed)
        self.graph = SurfaceGraph()
        self.graph.LOG_MESSAGE.connect(self.update_log)
        self.FONTS_CHANGED.connect(self.graph.change_fonts)
        self.statusBar = QtWidgets.QGroupBox("Log")
        self.statusGrid = QtWidgets.QGridLayout(self.statusBar)
        self.statusBar.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,QtWidgets.QSizePolicy.Policy.Fixed)
        self.logBox = QtWidgets.QTextEdit(QtCore.QTime.currentTime().toString("hh:mm:ss")+ \
                                  "\u00A0\u00A0\u00A0\u00A0Initialized!")
        self.logBox.ensureCursorVisible()
        self.logBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.logBox.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.logBoxScroll = QtWidgets.QScrollArea()
        self.logBoxScroll.setWidget(self.logBox)
        self.logBoxScroll.setWidgetResizable(True)
        self.logBoxScroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.statusGrid.addWidget(self.logBoxScroll,0,0)
        self.applyButton = QtWidgets.QPushButton("Apply")
        self.applyButton.clicked.connect(self.apply)
        self.container = QtWidgets.QWidget.createWindowContainer(self.graph)
        self.screenSize = self.graph.screen().size()
        self.container.setMinimumSize(int(self.screenSize.width()/2), int(self.screenSize.height()/2))
        self.container.setMaximumSize(self.screenSize)
        self.container.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,QtWidgets.QSizePolicy.Policy.Expanding)
        self.container.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)

        self.appearance = QtWidgets.QGroupBox("Appearance")
        self.appearanceVBox = QtWidgets.QVBoxLayout(self.appearance)
        self.appearanceGrid = QtWidgets.QGridLayout()
        self.fontListLabel = QtWidgets.QLabel("Change Font")
        self.fontList = QtWidgets.QFontComboBox()
        self.fontList.setCurrentFont(QtGui.QFont("Arial"))
        self.fontList.currentFontChanged.connect(self.refresh_font_name)
        self.fontSizeLabel = QtWidgets.QLabel("Adjust Font Size ({})".format(30))
        self.fontSizeSlider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.fontSizeSlider.setMinimum(1)
        self.fontSizeSlider.setMaximum(100)
        self.fontSizeSlider.setValue(30)
        self.fontSizeSlider.valueChanged.connect(self.refresh_font_size)
        self.show2DContourButton = QtWidgets.QPushButton("Show 2D Contour")
        self.show2DContourButton.clicked.connect(self.show_2D_contour_button_pressed)
        self.SHOW_2D_CONTOUR_SIGNAL.connect(self.show_2D_contour)
        self.show2DContourButton.setEnabled(False)
        self.appearanceGrid.addWidget(self.fontListLabel,0,0)
        self.appearanceGrid.addWidget(self.fontList,0,1)
        self.appearanceGrid.addWidget(self.fontSizeLabel,1,0)
        self.appearanceGrid.addWidget(self.fontSizeSlider,1,1)
        self.appearanceVBox.addLayout(self.appearanceGrid)
        self.appearanceVBox.addWidget(self.show2DContourButton)

        self.themeLabel = QtWidgets.QLabel("Theme")
        self.themeLabel.setStyleSheet("QLabel {color:blue;}")
        self.themeLabel.setFixedHeight(20)
        self.themeList = QtWidgets.QComboBox(self)
        self.themeList.addItem("Qt")
        self.themeList.addItem("Primary Colors")
        self.themeList.addItem("Digia")
        self.themeList.addItem("Stone Moss")
        self.themeList.addItem("Army Blue")
        self.themeList.addItem("Retro")
        self.themeList.addItem("Ebony")
        self.themeList.addItem("Isabelle")
        self.themeList.currentIndexChanged.connect(self.graph_chagne_theme)
        self.themeList.setCurrentIndex(3)

        self.OptionsGrid.addWidget(self.Eta,0,0,1,2)
        self.OptionsGrid.addWidget(self.Epsilon,1,0,1,2)
        self.OptionsGrid.addWidget(self.AsymmetricRatio,2,0,1,2)
        self.OptionsGrid.addWidget(self.x_range,3,0,1,2)
        self.OptionsGrid.addWidget(self.x_step,4,0,1,2)
        self.OptionsGrid.addWidget(self.z_range,5,0,1,2)
        self.OptionsGrid.addWidget(self.z_step,6,0,1,2)
        self.OptionsGrid.addWidget(self.R_label,7,0,1,2)
        self.OptionsGrid.addWidget(self.latticeConstantLabel,8,0,1,1)
        self.OptionsGrid.addWidget(self.latticeConstant,8,1,1,1)
        self.OptionsGrid.addWidget(self.chooseUnitLabel,9,0,1,1)
        self.OptionsGrid.addWidget(self.chooseUnit,9,1,1,1)
        self.OptionsGrid.addWidget(self.applyButton,10,0,1,2)
        self.mainGrid.addWidget(self.Options,0,0)
        self.mainGrid.addWidget(self.appearance,1,0)
        self.mainGrid.addWidget(self.themeLabel,2,0)
        self.mainGrid.addWidget(self.themeList,3,0)
        self.mainGrid.addWidget(self.statusBar,4,0)
        self.mainSplitter.addWidget(self.container)
        self.mainSplitter.addWidget(self.mainFrame)
        self.mainSplitter.setStretchFactor(0,1)
        self.mainSplitter.setStretchFactor(1,1)
        self.mainSplitter.setCollapsible(0,False)
        self.mainSplitter.setCollapsible(1,False)
        self.UIGrid = QtWidgets.QGridLayout()
        self.UIGrid.addWidget(self.mainSplitter,0,0)
        self.setLayout(self.UIGrid)
        self.showMaximized()
        self.setWindowTitle("Statistical Factor Simulation")

    def unit_changed(self,unit):
        if unit == "Brillouin Zone %":
            self.x_range.set(0,400,10,10)
            self.x_step.set(10,400,0.1,2000)
            self.z_range.set(0,400,10,10)
            self.z_step.set(10,400,0.1,2000)
        elif unit == "\u212B\u207B\u00B9":
            self.x_range.set(0,400,0.1,1000)
            self.x_step.set(10,400,0.001,200000)
            self.z_range.set(0,400,0.1,1000)
            self.z_step.set(10,400,0.001,200000)

    def graph_chagne_theme(self,theme):
        self.graph.change_theme(theme)
        self.FONTS_CHANGED.emit(self.fontList.currentFont().family(),self.fontSizeSlider.value())
        try:
            self.graph.set_black_to_yellow_gradient()
        except:
            pass

    def refresh_font_size(self):
        self.fontSizeLabel.setText("Adjust Font Size ({})".format(self.fontSizeSlider.value()))
        self.FONTS_CHANGED.emit(self.fontList.currentFont().family(),self.fontSizeSlider.value())

    def refresh_font_name(self):
        self.FONTS_CHANGED.emit(self.fontList.currentFont().family(),self.fontSizeSlider.value())

    def show_2D_contour_button_pressed(self):
        self.update_log("Generating contour plot...")
        QtCore.QCoreApplication.processEvents()
        self.SHOW_2D_CONTOUR_SIGNAL.emit(self.graph.get_data_array(),-self.x_range.get_value(),self.x_range.get_value(),\
                                      -self.z_range.get_value(),self.z_range.get_value(),self.chooseUnit.currentText(),\
                                      self.fontSizeSlider.value(),self.fontList.currentFont().family())

    def show_2D_contour(self, data, x_min=-10, x_max=10, z_min=-10, z_max=10, unit = "Brillouin Zone %", fontsize = 30, fontname = "Arial", fontcolor='black'):
        window = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(window)
        figure = plt.figure()
        canvas = FigureCanvas(figure)
        toolbar = NavigationToolbar(canvas,window)
        figure.clear()
        x,y,intensity = self.convert_to_RTI(data)
        #intensity_min = np.amin(np.amin(intensity))
        #intensity_max = np.amax(np.amax(intensity))
        #levels_fixed = [intensity_min,intensity_min+0.0005*(intensity_max-intensity_min),intensity_min+\
        #                0.001*(intensity_max-intensity_min),intensity_min+0.002*(intensity_max-intensity_min),\
        #                intensity_min+0.004*(intensity_max-intensity_min),intensity_min+0.008*(intensity_max-intensity_min),\
        #                intensity_min+0.016*(intensity_max-intensity_min),intensity_min+0.032*(intensity_max-intensity_min),\
        #                intensity_min+0.064*(intensity_max-intensity_min),intensity_min+0.128*(intensity_max-intensity_min),\
        #                intensity_min+0.256*(intensity_max-intensity_min),intensity_min+0.6*(intensity_max-intensity_min),\
        #                intensity_min+0.8*(intensity_max-intensity_min),intensity_max]
        #colors_fixed = ['xkcd:black','xkcd:navy','xkcd:deep blue','xkcd:royal blue','xkcd:blue','xkcd:sky blue','xkcd:cyan','xkcd:sea green',\
        #                'xkcd:bright green','xkcd:greenish yellow','xkcd:bright yellow','xkcd:bright orange','xkcd:red','xkcd:dark red']
        ax = figure.add_subplot(111)
        #cs = ax.contourf(x,y,intensity,colors=colors_fixed, levels=levels_fixed)

        intensity_min = np.amin(intensity)
        intensity_max = np.amax(intensity)
        lev_exp = np.linspace(np.floor(np.log10(intensity_min.min())-1),np.ceil(np.log10(intensity_max.max())+1),2000)
        levs = np.power(10, lev_exp)
        cs = ax.contourf(x,y,intensity, levs, norm = colors.LogNorm(), cmap = cm.jet)
        #csHM = ax.contour(x,y,intensity,levels=[0.5],colors=['black'],linestyles='dashed',linewidths=2)
        ratio = 1.0
        FWHM = 1.0
        font = {'fontname':fontname,'fontsize':fontsize,'color':fontcolor}
        #for collection in csHM.collections:
        #    path = collection.get_paths()
        #    for item in path:
        #        x = item.vertices[:,0]
        #        y = item.vertices[:,1]
        #        w = np.sqrt(x**2+y**2)
        #        ratio = np.amax(w)/np.amin(w)
        #        FWHM = np.amax(w)+np.amin(w)
        #ax.set_title("Statistical Factor Contour Plot\n(R = {:7.5f}, \u03B7 = {:5.3f}\u03C0, \u03B5 = {:5.3f})".\
        #             format(self.R_value,self.Eta.get_value(),self.Epsilon.get_value()),fontdict=font,pad=10)
        if unit == "Brillouin Zone %":
            #ax.text(z_min*0.96,x_max*0.7,"Average FWHM = {:5.4f} %BZ\nStep Atom Density Asymmetric Ratio = {:5.3f}\nFWHM Asymmetric Ratio = {:5.3f}". \
            #        format(FWHM,self.AsymmetricRatio.get_value(),ratio),color='white',fontsize=fontsize-5,bbox={'facecolor':'black','alpha':0.2,'pad':5})
            ax.set_ylabel(r"$BZ_{y}\ (\%)$",fontdict=font)
            ax.set_xlabel(r"$BZ_{x}\ (\%)$",fontdict=font)
        elif unit == "\u212B\u207B\u00B9":
            #ax.text(z_min*0.96,x_max*0.7,"Average FWHM = {:5.4f} \u212B\u207B\u00B9\nStep Atom Density Asymmetric Ratio = {:5.3f}\nFWHM Asymmetric Ratio = {:5.3f}". \
            #        format(FWHM,self.AsymmetricRatio.get_value(),ratio),color='white',fontsize=fontsize-5,bbox={'facecolor':'black','alpha':0.2,'pad':5})
            ax.set_ylabel(r"$K_{y} (\AA^{-1})$",fontdict=font)
            ax.set_xlabel(r"$K_{x} (\AA^{-1})$",fontdict=font)
        ax.set_ylim(x_min,x_max)
        ax.tick_params(axis='both',which='major',labelsize=fontsize)
        ax.set_xlim(z_min,z_max)
        ax.set_aspect(1)
        #plt.axis('off')
        cbar = figure.colorbar(cs,format='%.1e')
        cbar.ax.set_ylabel("Normalized Intensity",fontdict=font)
        cbar.ax.tick_params(labelsize=fontsize)
        #canvas.draw()
        layout.addWidget(toolbar)
        layout.addWidget(canvas)
        window.setWindowTitle("2D Contour")
        window.show()
        self.update_log('Contour plot created!')

    def convert_to_RTI(self,data):
        z = [i[0].x() for i in data]
        x = [data[0][j].z() for j in range(len(data[0]))]
        y = [[i[j].y() for j in range(len(data[0]))] for i in data]
        return x,z,y

    def apply(self):
        self.update_log("Loading data ......")
        QtCore.QCoreApplication.processEvents()
        self.R_value = self.graph.refresh(self.Eta.get_value(),self.Epsilon.get_value(),self.AsymmetricRatio.get_value(),\
                           float(self.latticeConstant.text()),self.x_range.get_value(),self.x_step.get_value(),\
                            self.z_range.get_value(),self.z_step.get_value(),self.chooseUnit.currentText())
        self.R_label.setText("R = {:7.5f}".format(self.R_value))
        self.graph.fill_surface_proxy()
        self.graph.enable_surface_model(True)
        self.graph.set_black_to_yellow_gradient()
        self.show2DContourButton.setEnabled(True)

    def update_log(self,msg):
        self.logBox.append(QtCore.QTime.currentTime().toString("hh:mm:ss")+"\u00A0\u00A0\u00A0\u00A0"+msg)

class SurfaceGraph(QtDataVisualization.Q3DSurface):

    LOG_MESSAGE = QtCore.pyqtSignal(str)

    def __init__(self):
        super(SurfaceGraph,self).__init__()
        self.SurfaceProxy = QtDataVisualization.QSurfaceDataProxy()
        self.SurfaceSeries = QtDataVisualization.QSurface3DSeries(self.SurfaceProxy)

    def refresh(self,eta,epsilon,ratio,lattice_constant,x_range,x_step,z_range,z_step,unit):
        self.eta = eta*np.pi
        self.epsilon = epsilon
        self.ratio = ratio
        self.lc = lattice_constant
        self.x_range = x_range
        self.x_step = x_step
        self.z_range = z_range
        self.z_step = z_step
        self.unit = unit
        return self.r_function(self.epsilon,self.eta)

    def convert_to_data_array(self):
        countX = int(self.x_range/self.x_step)
        countZ = int(self.z_range/self.z_step)
        self.dataArray = []
        for i in range(-countX,countX+1):
            row = []
            for j in range(-countZ,countZ+1):
                item = QtDataVisualization.QSurfaceDataItem()
                if not (i == 0 and j == 0):
                    x = i*self.x_step
                    z = j*self.z_step
                    u = x + z/np.sqrt(3)
                    v = z/np.sqrt(3)*2
                    if self.unit == "Brillouin Zone %":
                        y = self.statistical_factor_function(u/100*(2*np.pi/self.lc/(np.sqrt(3)/2)),\
                                                    v/100*2*np.pi/self.lc/(np.sqrt(3)/2),self.epsilon,self.eta,self.ratio)
                    elif self.unit == "\u212B\u207B\u00B9":
                        y = self.statistical_factor_function(u,v,self.epsilon,self.eta,self.ratio)
                else:
                    x = 0
                    y = 1
                    z = 0
                vector = QtGui.QVector3D(x,y,z)
                item.setPosition(vector)
                row.append(item)
            self.dataArray.append(row)
        return self.dataArray

    def get_data_array(self):
        return self.dataArray

    def statistical_factor_function(self,u,v,epsilon,eta,r):
        asymmetric_epsilon, angle = self.asymetric_epsilon(u,v,epsilon,r)
        R = self.r_function(asymmetric_epsilon,eta)
        result = ((1-R**3)**2-R**2*(1-R)**2*(3+2*(np.cos(u)+np.cos(v)+np.cos(u-v))))/((1-2*R*np.cos(u)+R**2)*(1-2*R*np.cos(v)+R**2)*(1-2*R*np.cos(u-v)+R**2))
        max = ((1-R**3)**2-R**2*(1-R)**2*(3+2*3))/((1-2*R+R**2)*(1-2*R+R**2)*(1-2*R+R**2))
        return result/max

    def r_function(self,epsilon,eta):
        return 1-epsilon*(1-np.cos(eta))

    def asymetric_epsilon(self,u,v,epsilon,r):
        h = epsilon*(r-1)/(r+1)
        x = u-v/2
        y = np.sqrt(3)/2*v
        if y == 0:
            if x>0:
                angle = 0
            else:
                angle = np.pi
        elif x == 0:
            if y>0:
                angle = np.pi/2
            else:
                angle = 3*np.pi/2
        else:
            angle = np.arctan(np.abs(y/x))
            if x>0 and y>0:
                pass
            elif x<0 and y>0:
                angle = np.pi-angle
            elif x<0 and y<0:
                angle = np.pi+angle
            elif x>0 and y<0:
                angle = 2*np.pi-angle
        return epsilon+h*np.cos(6*angle), angle


    def fill_surface_proxy(self):
        dataArray = self.convert_to_data_array()
        self.SurfaceProxy.resetArray(dataArray)

    def enable_surface_model(self,enable):
        if enable:
            for series in self.seriesList():
                self.removeSeries(series)
            self.SurfaceSeries.setDrawMode(QtDataVisualization.QSurface3DSeries.DrawFlag.DrawSurface)
            self.SurfaceSeries.setFlatShadingEnabled(True)
            self.axisX().setLabelFormat("%.2f")
            self.axisZ().setLabelFormat("%.2f")
            if self.unit == "Brillouin Zone %":
                self.axisX().setRange(-self.x_range-0.01,self.x_range+0.01)
                self.axisZ().setRange(-self.z_range-0.01,self.z_range+0.01)
            elif self.unit == "\u212B\u207B\u00B9":
                self.axisX().setRange(-self.x_range-0.0001,self.x_range+0.0001)
                self.axisZ().setRange(-self.z_range-0.0001,self.z_range+0.0001)
            self.axisY().setAutoAdjustRange(True)
            if self.unit == "Brillouin Zone %":
                self.axisX().setTitle("Kx (BZ %)")
            elif self.unit == "\u212B\u207B\u00B9":
                self.axisX().setTitle("Kx (\u212B\u207B\u00B9)")
            self.axisX().setTitleVisible(True)
            self.axisZ().setTitleVisible(True)
            if self.unit == "Brillouin Zone %":
                self.axisZ().setTitle("Ky (BZ %)")
            elif self.unit == "\u212B\u207B\u00B9":
                self.axisZ().setTitle("Ky (\u212B\u207B\u00B9)")
            self.axisY().setTitle("Normalized Statistical Factor (arb. units)")
            self.axisY().setTitleVisible(True)
            self.axisX().setLabelAutoRotation(30)
            self.axisY().setLabelAutoRotation(90)
            self.axisZ().setLabelAutoRotation(30)
            self.addSeries(self.SurfaceSeries)
            self.LOG_MESSAGE.emit("DataArray Loaded!")

    def change_fonts(self,fontname,fontsize):
        self.activeTheme().setFont(QtGui.QFont(fontname,fontsize))

    def change_theme(self, theme):
        self.activeTheme().setType(QtDataVisualization.Q3DTheme.Theme(theme))

    def set_black_to_yellow_gradient(self):
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

    def set_green_to_red_gradient(self):
        self.gr = QtGui.QLinearGradient()
        self.gr.setColorAt(0.0, QtCore.Qt.GlobalColor.darkGreen)
        self.gr.setColorAt(0.5, QtCore.Qt.GlobalColor.yellow)
        self.gr.setColorAt(0.8, QtCore.Qt.GlobalColor.red)
        self.gr.setColorAt(1.0, QtCore.Qt.GlobalColor.darkRed)
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

def test():
    app = QtWidgets.QApplication(sys.argv)
    simulation = Window()
    simulation.main()
    sys.exit(app.exec_())

if __name__ == '__main__':
    test()