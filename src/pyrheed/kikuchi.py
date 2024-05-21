import configparser
import numpy as np
from numpy.lib import scimath
from process import Diffraction
import profile_chart
from pymatgen.io.cif import CifParser
from PyQt6 import QtCore, QtWidgets, QtGui, QtCharts
from my_widgets import LabelMultipleLineEdit, LabelLineEdit, ColorPicker
import sys
import os
import itertools

class Window(QtCore.QObject):
    STOP_KIKUCHI_WORKER = QtCore.pyqtSignal()
    FONTS_CHANGED = QtCore.pyqtSignal(str,int)

    def __init__(self):
        super(Window,self).__init__()
        dirname = os.path.dirname(__file__)
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(dirname,'configuration.ini'))
        self.kikuchi_line_series = {}
        self.kikuchi_envelope_series = {}
        self.reciprocal_spot_series = {}
        self.laue_spot_series = {}

    def main(self):
        self.label_size = 120
        self.chooseCif = QtWidgets.QGroupBox("Choose CIF")
        self.chooseCifGrid = QtWidgets.QGridLayout(self.chooseCif)
        self.chooseCifLabel = QtWidgets.QLabel("The path of the CIF file is:\n")
        self.chooseCifLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.chooseCifLabel.setWordWrap(True)
        self.chooseCifButton = QtWidgets.QPushButton("Add CIF")
        self.chooseCifButton.clicked.connect(self.open_cif)
        self.chooseCifGrid.addWidget(self.chooseCifLabel,0,0)
        self.chooseCifGrid.addWidget(self.chooseCifButton,1,0)

        self.lattice_constants = QtWidgets.QGroupBox("Lattice Constants")
        self.lattice_constant_a       = LabelLineEdit('a',self.label_size,'',3,'\u212B')
        self.lattice_constant_b       = LabelLineEdit('b',self.label_size,'',3,'\u212B')
        self.lattice_constant_c       = LabelLineEdit('c',self.label_size,'',3,'\u212B')
        self.lattice_constant_alpha   = LabelLineEdit('alpha',self.label_size,'',2,'\u00B0')
        self.lattice_constant_beta    = LabelLineEdit('beta',self.label_size,'',2,'\u00B0')
        self.lattice_constant_gamma   = LabelLineEdit('gamma',self.label_size,'',2,'\u00B0')
        self.lattice_constants_grid = QtWidgets.QVBoxLayout(self.lattice_constants)
        self.lattice_constants_grid.addWidget(self.lattice_constant_a)
        self.lattice_constants_grid.addWidget(self.lattice_constant_b)
        self.lattice_constants_grid.addWidget(self.lattice_constant_c)
        self.lattice_constants_grid.addWidget(self.lattice_constant_alpha)
        self.lattice_constants_grid.addWidget(self.lattice_constant_beta)
        self.lattice_constants_grid.addWidget(self.lattice_constant_gamma)

        self.parameters = QtWidgets.QGroupBox("Experimental Parameters")
        self.parameters_grid = QtWidgets.QVBoxLayout(self.parameters)
        self.zone_axis                = LabelMultipleLineEdit(3,'Zone axis (h k l)',self.label_size,['2','1','0'])
        self.out_of_plane_orientation = LabelMultipleLineEdit(3,'Out-of-plane axis (h k l)',self.label_size,['0','0','1'])
        self.electron_energy          = LabelLineEdit('Electron energy',self.label_size,'20',1,'keV')
        self.incident_angle           = LabelLineEdit('Incident angle',self.label_size,'3',1,'\u00B0')
        self.inner_potential          = LabelLineEdit('Inner potential',self.label_size,'15',1,'eV')
        self.parameters_grid.addWidget(self.zone_axis)
        self.parameters_grid.addWidget(self.out_of_plane_orientation)
        self.parameters_grid.addWidget(self.electron_energy)
        self.parameters_grid.addWidget(self.incident_angle)
        self.parameters_grid.addWidget(self.inner_potential)


        self.options = QtWidgets.QGroupBox("Simulation Options")
        self.options_grid = QtWidgets.QGridLayout(self.options)
        self.index_max = LabelLineEdit('Index maximum',self.label_size,'10',1)
        self.plot_range = LabelLineEdit('Plot range',self.label_size,'12',1)
        self.reciprocal_spot_color = ColorPicker("Reciprocal spot",'black')
        self.reciprocal_spot_color.COLOR_CHANGED.connect(self.change_color)
        self.kikuchi_line_color = ColorPicker("Kikuchi line",'#00ff00')
        self.kikuchi_line_color.COLOR_CHANGED.connect(self.change_color)
        self.kikuchi_envelope_color = ColorPicker("Kikuchi envelope",'red')
        self.kikuchi_envelope_color.COLOR_CHANGED.connect(self.change_color)
        self.laue_spot_color = ColorPicker('Laue spot','blue')
        self.laue_spot_color.COLOR_CHANGED.connect(self.change_color)
        self.fontListLabel = QtWidgets.QLabel("Change Font")
        self.fontList = QtWidgets.QFontComboBox()
        self.fontList.setCurrentFont(QtGui.QFont("Arial"))
        self.fontList.currentFontChanged.connect(self.refresh_font_name)
        self.fontSizeLabel = QtWidgets.QLabel("Adjust Font Size ({})".format(15))
        self.fontSizeLabel.setFixedWidth(160)
        self.fontSizeSlider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.fontSizeSlider.setMinimum(1)
        self.fontSizeSlider.setMaximum(100)
        self.fontSizeSlider.setValue(15)
        self.show_axes_label = QtWidgets.QLabel("Show axes?")
        self.show_axes = QtWidgets.QCheckBox()
        self.show_axes.setChecked(False)
        self.show_grid_label = QtWidgets.QLabel("Show grid?")
        self.show_grid = QtWidgets.QCheckBox()
        self.show_grid.setChecked(False)
        self.fontSizeSlider.valueChanged.connect(self.refresh_font_size)
        self.options_grid.addWidget(self.index_max,0,0,1,4)
        self.options_grid.addWidget(self.plot_range,1,0,1,4)
        self.options_grid.addWidget(self.reciprocal_spot_color,2,0,1,4)
        self.options_grid.addWidget(self.kikuchi_line_color,3,0,1,4)
        self.options_grid.addWidget(self.kikuchi_envelope_color,4,0,1,4)
        self.options_grid.addWidget(self.laue_spot_color,5,0,1,4)
        self.options_grid.addWidget(self.fontListLabel,6,0,1,2)
        self.options_grid.addWidget(self.fontList,6,2,1,2)
        self.options_grid.addWidget(self.fontSizeLabel,7,0,1,2)
        self.options_grid.addWidget(self.fontSizeSlider,7,2,1,2)
        self.options_grid.addWidget(self.show_axes_label,8,0,1,1)
        self.options_grid.addWidget(self.show_axes,8,1,1,1)
        self.options_grid.addWidget(self.show_grid_label,8,2,1,1)
        self.options_grid.addWidget(self.show_grid,8,3,1,1)

        self.statusBar = QtWidgets.QGroupBox("Log")
        self.statusGrid = QtWidgets.QGridLayout(self.statusBar)
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
        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setVisible(False)
        self.progressBar.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.progressBarSizePolicy = self.progressBar.sizePolicy()
        self.progressBarSizePolicy.setRetainSizeWhenHidden(True)
        self.progressBarSizePolicy.setHorizontalPolicy(QtWidgets.QSizePolicy.Policy.Expanding)
        self.progressBar.setSizePolicy(self.progressBarSizePolicy)
        self.statusGrid.addWidget(self.logBoxScroll,0,0)

        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok|QtWidgets.QDialogButtonBox.StandardButton.Abort|QtWidgets.QDialogButtonBox.StandardButton.Discard,QtCore.Qt.Orientation.Horizontal)
        self.button_box.setCenterButtons(True)
        self.button_box.accepted.connect(self.start)
        self.button_box.rejected.connect(self.stop)
        self.button_box.buttons()[2].clicked.connect(self.discard)

        self.control_panel = QtWidgets.QWidget()
        self.control_panel.setMinimumWidth(400)
        self.Vlayout = QtWidgets.QVBoxLayout(self.control_panel)
        self.Vlayout.addWidget(self.chooseCif)
        self.Vlayout.addWidget(self.lattice_constants)
        self.Vlayout.addWidget(self.parameters)
        self.vSplitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        self.vSplitter.addWidget(self.options)
        self.vSplitter.addWidget(self.statusBar)
        self.vSplitter.setStretchFactor(0,1)
        self.vSplitter.setStretchFactor(1,1)
        self.vSplitter.setCollapsible(0,False)
        self.vSplitter.setCollapsible(1,False)
        self.Vlayout.addWidget(self.vSplitter)
        self.Vlayout.addWidget(self.progressBar)
        self.Vlayout.addWidget(self.button_box)

        self.plot_widget = QtWidgets.QWidget()
        self.plot_widget_grid = QtWidgets.QVBoxLayout(self.plot_widget)
        self.plot = profile_chart.ProfileChart(self.config)
        self.plot.set_fonts(self.fontList.currentFont().family(),self.fontSizeSlider.value())
        self.plot.add_chart([],[],'kikuchi line')
        self.plot.profileChart.axes(QtCore.Qt.Orientation.Horizontal)[0].setRange(-self.plot_range.value(),self.plot_range.value())
        self.plot.set_axes_visible(False)
        self.plot.set_grids_visible(False)
        self.show_grid.stateChanged.connect(self.plot.set_grids_visible)
        self.show_axes.stateChanged.connect(self.plot.set_axes_visible)
        self.FONTS_CHANGED.connect(self.plot.adjust_fonts)
        self.coordinate = QtWidgets.QLabel("")
        self.plot.CHART_MOUSE_MOVEMENT.connect(self.update_coordinate)
        self.plot.CHART_MOUSE_LEAVE.connect(self.clear_coordinate)
        self.plot_widget_grid.addWidget(self.plot)
        self.plot_widget_grid.addWidget(self.coordinate)

        self.main_splitter = QtWidgets.QSplitter()
        self.main_splitter.addWidget(self.control_panel)
        self.main_splitter.addWidget(self.plot_widget)
        self.main_splitter.setContentsMargins(0,0,0,0)
        self.main_splitter.setSizes([400,2000])
        self.leftScroll = QtWidgets.QScrollArea(self.main_splitter)
        self.leftScroll.setWidget(self.control_panel)
        self.leftScroll.setWidgetResizable(True)
        self.leftScroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.main_splitter)

        self.Dialog = QtWidgets.QWidget()
        self.Dialog.setLayout(self.main_layout)
        self.Dialog.setWindowTitle('Kikuchi Pattern Simulation')
        self.Dialog.showMaximized()

    def update_coordinate(self,pos):
        self.coordinate.setText("(x={:5.2f} \u212B\u207B\u00B9, y={:5.2f} \u212B\u207B\u00B9)".format(pos.x(),pos.y()))

    def clear_coordinate(self):
        self.coordinate.setText("")

    def prepare(self):
        self.clear_plot()
        self.diffraction_worker = Diffraction()
        self.G_star = self.diffraction_worker.G_star(self.lattice_constant_a.value(),self.lattice_constant_b.value(),self.lattice_constant_c.value(), \
                                         self.lattice_constant_alpha.value(),self.lattice_constant_beta.value(),self.lattice_constant_gamma.value())
        self.conversion_matrix = self.diffraction_worker.conversion_matrix(self.lattice_constant_a.value(),self.lattice_constant_b.value(),self.lattice_constant_c.value(), \
                                                               self.lattice_constant_alpha.value(),self.lattice_constant_beta.value(),self.lattice_constant_gamma.value())
        self.star = [np.matmul(self.G_star,[1,0,0]),np.matmul(self.G_star,[0,1,0]),np.matmul(self.G_star,[0,0,1])]
        self.kikuchi_worker = Simulation(self.zone_axis.values(), self.out_of_plane_orientation.values(), \
                                         self.structure, self.star,\
                                         self.conversion_matrix, self.electron_energy.value(), self.incident_angle.value(),\
                                         self.inner_potential.value(), int(self.index_max.value()), self.plot_range.value(),\
                                         self.reciprocal_spot_color.get_color(),\
                                         self.kikuchi_line_color.get_color(), self.kikuchi_envelope_color.get_color(),\
                                         self.laue_spot_color.get_color())
        self.thread = QtCore.QThread()
        self.kikuchi_worker.moveToThread(self.thread)
        self.kikuchi_worker.ADD_CURVE.connect(self.add_curve)
        self.kikuchi_worker.ADD_LINE.connect(self.add_line)
        self.kikuchi_worker.ADD_SPOT.connect(self.add_spot)
        self.kikuchi_worker.PROGRESS_ADVANCE.connect(self.progress)
        self.kikuchi_worker.PROGRESS_END.connect(self.progress_reset)
        self.kikuchi_worker.UPDATE_LOG.connect(self.update_log)
        self.kikuchi_worker.FINISHED.connect(self.thread.quit)
        self.thread.started.connect(self.kikuchi_worker.run)
        self.STOP_KIKUCHI_WORKER.connect(self.kikuchi_worker.stop)

    def start(self):
        try:
            self.prepare()
            self.thread.start()
        except ValueError:
            self.raise_error('Please make sure the inputs are correct!')

    def stop(self):
        self.STOP_KIKUCHI_WORKER.emit()
        if self.thread.isRunning():
            self.thread.terminate()
            self.thread.wait()

    def discard(self):
        self.Dialog.close()

    def open_cif(self):
        path = QtWidgets.QFileDialog.getOpenFileName(None,"Choose The CIF File",'./',filter="CIF (*.cif);;All Files (*.*)")[0]
        if not path == "":
            self.update_log("CIF opened!")
            self.cifPath = path
            self.chooseCifLabel.setText("The path of the CIF file is:\n"+self.cifPath)
            self.structure = CifParser(self.cifPath).get_structures(primitive=False)[0]
            self.lattice_constant_a.set_value(self.structure.lattice.a)
            self.lattice_constant_b.set_value(self.structure.lattice.b)
            self.lattice_constant_c.set_value(self.structure.lattice.c)
            self.lattice_constant_alpha.set_value(self.structure.lattice.alpha)
            self.lattice_constant_beta.set_value(self.structure.lattice.beta)
            self.lattice_constant_gamma.set_value(self.structure.lattice.gamma)

    def update_log(self,msg):
        self.logBox.append(QtCore.QTime.currentTime().toString("hh:mm:ss")+"\u00A0\u00A0\u00A0\u00A0"+msg)

    def change_color(self,name,color):
        if name == 'Kikuchi line':
            for series in self.kikuchi_line_series.values():
                series.setColor(QtGui.QColor(color))
        elif name == 'Kikuchi envelope':
            for series in self.kikuchi_envelope_series.values():
                series.setColor(QtGui.QColor(color))
        elif name == 'Reciprocal spot':
            for series in self.reciprocal_spot_series.values():
                series.setColor(QtGui.QColor(color))
        elif name == 'Laue spot':
            for series in self.laue_spot_series.values():
                series.setColor(QtGui.QColor(color))

    def add_line(self,list,x1,x2,y1,y2,color='red',width=2,number_of_steps=200, label='kikuchi_line'):
        pen = QtGui.QPen(QtCore.Qt.PenStyle.SolidLine)
        pen.setColor(QtGui.QColor(color))
        pen.setWidth(width)
        series = QtCharts.QLineSeries()
        series.setPen(pen)
        for x,y in zip(np.linspace(x1,x2,number_of_steps),np.linspace(y1,y2,number_of_steps)):
            series.append(x,y)
        self.plot.profileChart.addSeries(series)
        for ax in self.plot.profileChart.axes():
            series.attachAxis(ax)
        if label == 'kikuchi_line':
            self.kikuchi_line_series[list] = series
        self.plot.profileChart.axes(QtCore.Qt.Orientation.Vertical)[0].setRange(-0.5,self.plot_range.value())

    def add_curve(self,list,list_x,list_y,color='red',width=2,label='kikuchi_line'):
        pen = QtGui.QPen(QtCore.Qt.PenStyle.SolidLine)
        pen.setColor(QtGui.QColor(color))
        pen.setWidth(width)
        series = QtCharts.QLineSeries()
        series.setPen(pen)
        for x,y in zip(list_x,list_y):
            series.append(x,y)
        self.plot.profileChart.addSeries(series)
        for ax in self.plot.profileChart.axes():
            series.attachAxis(ax)
        if label == 'kikuchi_line':
            self.kikuchi_line_series[list] = series
        elif label == 'kikuchi_envelope':
            self.kikuchi_envelope_series[list] = series
        self.plot.profileChart.axes(QtCore.Qt.Orientation.Vertical)[0].setRange(-0.5,self.plot_range.value())

    def add_spot(self,list,x,y,shape='circle',color='red',size=15,label='reciprocal_spot'):
        series = QtCharts.QScatterSeries()
        if shape == 'circle':
            series.setMarkerShape(QtCharts.QScatterSeries.MarkerShape.MarkerShapeCircle)
        elif shape == 'rectangle':
            series.setMarkerShape(QtCharts.QScatterSeries.MarkerShape.MarkerShapeRectangle)
        series.setMarkerSize(size)
        series.setColor(QtGui.QColor(color))
        series.append(x,y)
        self.plot.profileChart.addSeries(series)
        for ax in self.plot.profileChart.axes():
            series.attachAxis(ax)
        if label == 'reciprocal_spot':
            self.reciprocal_spot_series[list] = series
        elif label == 'laue_spot':
            self.laue_spot_series[list] = series
        self.plot.profileChart.axes(QtCore.Qt.Orientation.Vertical)[0].setRange(-0.5,self.plot_range.value())

    def clear_plot(self):
        if len(self.plot.profileChart.series())>1:
            for series in self.plot.profileChart.series()[1:]:
                self.plot.profileChart.removeSeries(series)

    def refresh(self,config):
        self.plot.refresh(config)

    def refresh_font_size(self):
        self.fontSizeLabel.setText("Adjust Font Size ({})".format(self.fontSizeSlider.value()))
        self.FONTS_CHANGED.emit(self.fontList.currentFont().family(),self.fontSizeSlider.value())

    def refresh_font_name(self):
        self.FONTS_CHANGED.emit(self.fontList.currentFont().family(),self.fontSizeSlider.value())

    def progress(self,min,max,val):
        self.progressBar.setVisible(True)
        self.progressBar.setMinimum(min)
        self.progressBar.setMaximum(max)
        self.progressBar.setValue(val)

    def progress_reset(self):
        self.progressBar.reset()
        self.progressBar.setVisible(False)

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

class Simulation(QtCore.QObject):
    ADD_LINE = QtCore.pyqtSignal(tuple, float, float, float, float, str, int, int,str)
    ADD_CURVE = QtCore.pyqtSignal(tuple, list, list, str, int,str)
    ADD_SPOT = QtCore.pyqtSignal(tuple, float, float, str, str, int,str)
    PROGRESS_ADVANCE = QtCore.pyqtSignal(int,int,int)
    PROGRESS_END = QtCore.pyqtSignal()
    UPDATE_LOG = QtCore.pyqtSignal(str)
    FINISHED = QtCore.pyqtSignal()

    def __init__(self, ZA, OPA, structure, star, conversion, energy, theta_in, inner_potential, index_max, plot_range,\
                 reciprocal_spot_color, kikuchi_line_color, kikuchi_envelope_color, laue_spot_color):
        super(Simulation,self).__init__()
        self.ZA, self.OPA, self.structure, self.star, self.conversion, self.energy, self.theta_in, self.inner_potential, \
        self.index_max, self.plot_range, self.reciprocal_spot_color, self.kikuchi_line_color,\
        self.kikuchi_envelope_color,self.laue_spot_color =\
            ZA, OPA,structure,  star, conversion, energy, theta_in, inner_potential, \
            index_max, plot_range, reciprocal_spot_color, kikuchi_line_color, kikuchi_envelope_color, \
            laue_spot_color
        self.diffraction_worker = Diffraction()
        self.K_in = 0.512*scimath.sqrt(self.energy*1000)
        self.HA = np.cross(np.matmul(self.conversion,self.ZA), np.matmul(self.conversion,self.OPA))
        self._abort = False
        self.space_group_number = structure.get_space_group_info()[1]

    def run(self):
        Bin, width = self.plot_range,self.plot_range
        R0 = self.K_in*np.sin(self.theta_in/180*np.pi)
        theta_f1 = np.arccos((self.K_in*np.cos(self.theta_in/180*np.pi)-Bin)/self.K_in)
        R1 = self.K_in*np.cos(self.theta_in/180*np.pi)*np.tan(theta_f1)
        theta_f2 = np.arccos((self.K_in*np.cos(self.theta_in/180*np.pi)-2*Bin)/self.K_in)
        R2 = self.K_in*np.cos(self.theta_in/180*np.pi)*np.tan(theta_f2)
        self.UPDATE_LOG.emit("Calculating Kikuchi lines ...")
        QtCore.QCoreApplication.processEvents()
        for h,k,l in itertools.product(range(-self.index_max,self.index_max+1),repeat=3):
            if self.diffraction_worker.is_permitted(h,k,l,self.space_group_number):
                ccc = np.transpose(np.linalg.multi_dot([self.conversion,self.star,[[h],[k],[l]]]))
                kb = np.linalg.multi_dot([ccc,self.conversion,self.ZA])/np.linalg.norm(np.matmul(self.conversion,self.ZA))
                if abs(kb) < Bin and kb > 0.01:
                    Bin = abs(kb)
                if np.matmul(self.ZA,[[h],[k],[l]]) == 0:
                    kh = np.matmul(ccc,self.HA)/np.linalg.norm(self.HA)
                    kp = np.linalg.multi_dot([ccc,self.conversion,self.OPA])/np.linalg.norm(np.matmul(self.conversion,self.OPA))

                    if abs(kh) < width and abs(kh)>0.01:
                        width = abs(kh)

                    if scimath.sqrt(kh**2+kp**2)<R1 or (scimath.sqrt(kh**2+kp**2)<2*R2 and scimath.sqrt(kh**2+kp**2)>2*R1-1):
                        if kh > -self.plot_range and kh < self.plot_range and kp>-1e-3 and kp < self.plot_range:
                            self.ADD_SPOT.emit((h,k,l), kh,kp,'circle',self.reciprocal_spot_color,5,'reciprocal_spot')
                        if kp**2 < 0.0001 and kh!=0:
                            self.ADD_LINE.emit((h,k,l), kh/2,kh/2,0,self.plot_range,self.kikuchi_line_color,1,200,'kikuchi_line')
                        elif kp !=0:
                            if kh/kp > 1e-6:
                                x = np.linspace(-self.plot_range, kp/kh*(kp/2-np.real(scimath.sqrt(0.265*self.inner_potential))) + kh/2,200)
                            elif kh/kp < -1e-6:
                                x = np.linspace(kp/kh*(kp/2-np.real(scimath.sqrt(0.265*self.inner_potential))) + kh/2, self.plot_range, 200)
                            else:
                                x = np.linspace(-self.plot_range, self.plot_range,200)
                            if kp/2 > scimath.sqrt(0.265*self.inner_potential) or kh!=0:
                                y = np.real(scimath.sqrt((-kh/kp*(x-kh/2)+kp/2)**2 - 0.265*self.inner_potential))
                                self.ADD_CURVE.emit((h,k,l), list(x),list(y),self.kikuchi_line_color,1,'kikuchi_line')
            self.PROGRESS_ADVANCE.emit(0,100,((h+self.index_max)*(2*self.index_max)**2+(k+self.index_max)*(2*self.index_max)+l+self.index_max)/(2*self.index_max)**3*100)
            QtCore.QCoreApplication.processEvents()
            if self._abort:
                break
        self.PROGRESS_END.emit()
        self.UPDATE_LOG.emit("Kikuchi lines added!")
        if not self._abort:
            self.UPDATE_LOG.emit("Calculating Laue spots ...")
            QtCore.QCoreApplication.processEvents()
            for i in range(-self.index_max,self.index_max+1):
                xr0 = i*width
                xr1 = (i+1/2)*width*np.cos(self.theta_in/180*np.pi)/np.cos(theta_f1)
                xr2 = i*width*np.cos(self.theta_in/180*np.pi)/np.cos(theta_f2)
                if R0**2 > xr0**2:
                    self.ADD_SPOT.emit((i,0), xr0, scimath.sqrt(R0**2-xr0**2),'circle',self.laue_spot_color,15,'laue_spot')
                if R1**2 > xr1**2:
                    self.ADD_SPOT.emit((i,1), xr1, scimath.sqrt(R1**2-xr1**2),'circle',self.laue_spot_color,15,'laue_spot')
                if R2**2 > xr2**2:
                    self.ADD_SPOT.emit((i,2),xr2, scimath.sqrt(R2**2-xr2**2),'circle',self.laue_spot_color,15,'laue_spot')
                self.PROGRESS_ADVANCE.emit(0,100,(i+self.index_max)/(2*self.index_max)*100)
                QtCore.QCoreApplication.processEvents()
                if self._abort:
                    break
            self.PROGRESS_END.emit()
            self.UPDATE_LOG.emit("Laue spots added!")
            if not self._abort:
                self.UPDATE_LOG.emit("Calculating Kikuchi envelope ...")
                QtCore.QCoreApplication.processEvents()
                for m in range(-3,4):
                    if not m==0:
                        Bm = width*m
                        U = 0.265*self.inner_potential
                        if m>0:
                            x_ke1 = np.linspace((U-Bm**2)/2/Bm,self.plot_range,200)
                            x_ke2 = np.linspace(-Bm/2,self.plot_range,200)
                        else:
                            x_ke1 = np.linspace(-self.plot_range, (U-Bm**2)/2/Bm,200)
                            x_ke2 = np.linspace(-self.plot_range,-Bm/2,200)
                        y_ke1 = np.real(scimath.sqrt(2*x_ke1*Bm + Bm**2 - U))
                        y_ke2 = np.real(scimath.sqrt(2*x_ke2*Bm + Bm**2))
                        self.ADD_CURVE.emit((m,1), list(x_ke1),list(y_ke1),self.kikuchi_envelope_color,3,'kikuchi_envelope')
                        self.ADD_CURVE.emit((m,2), list(x_ke2),list(y_ke2),self.kikuchi_envelope_color,3,'kikuchi_envelope')
                self.UPDATE_LOG.emit("Kikuchi envelope added!")
                QtCore.QCoreApplication.processEvents()

        if not self._abort:
            self.UPDATE_LOG.emit("Kikuchi calculation finished!")
        else:
            self.UPDATE_LOG.emit("Kikuchi calculation aborted!")
            self._abort = False
        self.FINISHED.emit()

    def stop(self):
        self._abort = True

def main():
    app = QtWidgets.QApplication(sys.argv)
    kikuchi = Window()
    kikuchi.main()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()


