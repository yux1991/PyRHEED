import configparser
from process import Diffraction
import profile_chart
from pymatgen.io.cif import CifParser
from PyQt5 import QtCore, QtWidgets, QtGui, QtChart
from my_widgets import LabelMultipleLineEdit, LabelLineEdit, ColorPicker
import sys

class Window(QtCore.QObject):

    def __init__(self):
        super(Window,self).__init__()
        self.config = configparser.ConfigParser()
        self.config.read('./configuration.ini')

    def main(self):
        self.label_size = 120
        self.chooseCif = QtWidgets.QGroupBox("Choose CIF")
        self.chooseCif.setStyleSheet('QGroupBox::title {color:blue;}')
        self.chooseCifGrid = QtWidgets.QGridLayout(self.chooseCif)
        self.chooseCifLabel = QtWidgets.QLabel("The path of the CIF file is:\n")
        self.chooseCifLabel.setAlignment(QtCore.Qt.AlignTop)
        self.chooseCifLabel.setWordWrap(True)
        self.chooseCifButton = QtWidgets.QPushButton("Add CIF")
        self.chooseCifButton.clicked.connect(self.open_cif)
        self.chooseCifGrid.addWidget(self.chooseCifLabel,0,0)
        self.chooseCifGrid.addWidget(self.chooseCifButton,1,0)

        self.lattice_constants = QtWidgets.QGroupBox("Lattice Constants")
        self.lattice_constants.setStyleSheet('QGroupBox::title {color:blue;}')
        self.lattice_constant_a       = LabelLineEdit('a',self.label_size,'',3,'\u212B\u207B\u00B9')
        self.lattice_constant_b       = LabelLineEdit('b',self.label_size,'',3,'\u212B\u207B\u00B9')
        self.lattice_constant_c       = LabelLineEdit('c',self.label_size,'',3,'\u212B\u207B\u00B9')
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
        self.parameters.setStyleSheet('QGroupBox::title {color:blue;}')
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
        self.options.setStyleSheet('QGroupBox::title {color:blue;}')
        self.options_grid = QtWidgets.QGridLayout(self.options)
        self.index_max = LabelLineEdit('Index maximum',self.label_size,'100',1)
        self.plot_range = LabelLineEdit('Plot range',self.label_size,'12',1)
        self.enable_indices_label = QtWidgets.QLabel('Show indices?')
        self.enable_indices = QtWidgets.QCheckBox()
        self.enable_indices.setChecked(True)
        self.kikuchi_line_color = ColorPicker("Kikuchi line",'red')
        self.kikuchi_envelope_color = ColorPicker("Kikuchi envelope",'green')
        self.laue_spot_color = ColorPicker('Laue spot','blue')
        self.fontListLabel = QtWidgets.QLabel("Change Font")
        self.fontList = QtWidgets.QFontComboBox()
        self.fontList.setCurrentFont(QtGui.QFont("Arial"))
        self.fontList.currentFontChanged.connect(self.refresh_font_name)
        self.fontSizeLabel = QtWidgets.QLabel("Adjust Font Size ({})".format(15))
        self.fontSizeLabel.setFixedWidth(160)
        self.fontSizeSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.fontSizeSlider.setMinimum(1)
        self.fontSizeSlider.setMaximum(100)
        self.fontSizeSlider.setValue(15)
        self.fontSizeSlider.valueChanged.connect(self.refresh_font_size)
        self.options_grid.addWidget(self.index_max,0,0,1,2)
        self.options_grid.addWidget(self.plot_range,1,0,1,2)
        self.options_grid.addWidget(self.enable_indices_label,2,0,1,1)
        self.options_grid.addWidget(self.enable_indices,2,1,1,1)
        self.options_grid.addWidget(self.kikuchi_line_color,3,0,1,2)
        self.options_grid.addWidget(self.kikuchi_envelope_color,4,0,1,2)
        self.options_grid.addWidget(self.laue_spot_color,5,0,1,2)
        self.options_grid.addWidget(self.fontListLabel,6,0,1,1)
        self.options_grid.addWidget(self.fontList,6,1,1,1)
        self.options_grid.addWidget(self.fontSizeLabel,7,0,1,1)
        self.options_grid.addWidget(self.fontSizeSlider,7,1,1,1)

        self.statusBar = QtWidgets.QGroupBox("Log")
        self.statusBar.setStyleSheet('QGroupBox::title {color:blue;}')
        self.statusGrid = QtWidgets.QGridLayout(self.statusBar)
        self.statusBar.setFixedHeight(150)
        self.statusBar.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Fixed)
        self.logBox = QtWidgets.QTextEdit(QtCore.QTime.currentTime().toString("hh:mm:ss")+ \
                                          "\u00A0\u00A0\u00A0\u00A0Initialized!")
        self.logCursor = QtGui.QTextCursor(self.logBox.document())
        self.logCursor.movePosition(QtGui.QTextCursor.End)
        self.logBox.setTextCursor(self.logCursor)
        self.logBox.ensureCursorVisible()
        self.logBox.setAlignment(QtCore.Qt.AlignTop)
        self.logBox.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.logBoxScroll = QtWidgets.QScrollArea()
        self.logBoxScroll.setWidget(self.logBox)
        self.logBoxScroll.setWidgetResizable(True)
        self.logBoxScroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setVisible(False)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBarSizePolicy = self.progressBar.sizePolicy()
        self.progressBarSizePolicy.setRetainSizeWhenHidden(True)
        self.progressBarSizePolicy.setHorizontalPolicy(QtWidgets.QSizePolicy.Expanding)
        self.progressBar.setSizePolicy(self.progressBarSizePolicy)
        self.statusGrid.addWidget(self.logBoxScroll,0,0)

        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok|QtWidgets.QDialogButtonBox.Cancel,QtCore.Qt.Horizontal)
        self.button_box.setCenterButtons(True)
        self.button_box.accepted.connect(self.start)
        self.button_box.rejected.connect(self.cancel)

        self.control_panel = QtWidgets.QWidget()
        self.control_panel.setMinimumWidth(400)
        self.Vlayout = QtWidgets.QVBoxLayout(self.control_panel)
        self.Vlayout.addWidget(self.chooseCif)
        self.Vlayout.addWidget(self.lattice_constants)
        self.Vlayout.addWidget(self.parameters)
        self.Vlayout.addWidget(self.options)
        self.Vlayout.addWidget(self.statusBar)
        self.Vlayout.addWidget(self.button_box)

        self.plot = profile_chart.ProfileChart(self.config)

        self.main_splitter = QtWidgets.QSplitter()
        self.main_splitter.addWidget(self.control_panel)
        self.main_splitter.addWidget(self.plot)
        self.main_splitter.setContentsMargins(0,0,0,0)
        self.main_splitter.setSizes([400,800])

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.main_splitter)

        self.Dialog = QtWidgets.QWidget()
        self.Dialog.setLayout(self.main_layout)
        self.Dialog.setWindowTitle('Kikuchi Pattern Simulation')
        self.Dialog.showMaximized()

    def start(self):
        return

    def cancel(self):
        self.Dialog.close()
        return

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

    def add_line(self,x_list,y_list,type=QtCore.Qt.DotLine,color='red',width=2):
        pen = QtGui.QPen(type)
        pen.setColor(QtGui.QColor(color))
        pen.setWidth(width)
        series = QtChart.QLineSeries()
        series.setPen(pen)
        for x,y in zip(x_list,y_list):
            series.append(x,y)
        self.plot.profileChart.addSeries(series)
        for ax in self.plot.profileChart.axes():
            series.attachAxis(ax)

    def add_spot(self,x,y,shape='circle',color='red',size=15):
        series = QtChart.QScatterSeries()
        if shape == 'circle':
            series.setMarkerShape(QtChart.QScatterSeries.MarkerShapeCircle)
        elif shape == 'rectangle':
            series.setMarkerShape(QtChart.QScatterSeries.MarkerShapeRectangle)
        series.setMarkerSize(size)
        series.setColor(QtGui.QColor(color))
        series.append(x,y)
        self.plot.profileChart.addSeries(series)
        for ax in self.plot.profileChart.axes():
            series.attachAxis(ax)

    def clear_plot(self):
        if len(self.plot.profileChart.series())>1:
            for series in self.plot.profileChart.series()[1:]:
                self.plot.profileChart.removeSeries(series)

    def refresh_font_size(self):
        self.fontSizeLabel.setText("Adjust Font Size ({})".format(self.fontSizeSlider.value()))
        self.plot.adjust_fonts(self.fontList.currentFont().family(),self.fontSizeSlider.value())

    def refresh_font_name(self):
        self.plot.adjust_fonts(self.fontList.currentFont().family(),self.fontSizeSlider.value())



class Simulation(QtCore.QObject):
    ADD_LINE = QtCore.pyqtSignal(list, list, int, str)
    ADD_SPOT = QtCore.pyqtSignal(float, float, int, str)
    ADD_INDEX = QtCore.pyqtSignal(float, float, list, int, str)

    def __init__(self, index_max, plot_range, enable_indices, kikuchi_line_color, kikuchi_envelope_color, laue_spot_color):
        super(Simulation,self).__init__()





def main():
    app = QtWidgets.QApplication(sys.argv)
    kikuchi = Window()
    kikuchi.main()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()


