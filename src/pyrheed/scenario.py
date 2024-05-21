import broadening, generate_report, main, process, reciprocal_space_mapping, simulate_RHEED, translational_antiphase_domain
from PyQt6 import QtCore, QtGui, QtWidgets, QtDataVisualization
from my_widgets import IndexedPushButtonWithTag, StartEndStep
import configparser
import matplotlib.pyplot as plt
import shutil
import sys
import os

class Window(QtWidgets.QWidget):


    def __init__(self):
        super(Window,self).__init__()
        self.setWindowTitle("Scenario")
        self.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        self.main_layout = QtWidgets.QGridLayout(self)
        self.path_dict = {}
        self.dir_dict = {}
        self.line_edit_dict = {}
        self.check_box_dict = {}
        self.combo_box_dict = {}
        self.label_dict = {}
        self.key_dict = {}
        self.row = {}

        self.dirname = os.path.dirname(__file__)
        self.load_scenario()
        default_destination = os.path.join(self.dirname,'RHEED scenario '+QtCore.QDateTime().currentDateTime().toString('MMddyyyy'))
        try:
            os.mkdir(default_destination)
        except FileExistsError:
            value = self.request_confirmation('The directory already exist. Do you want to overwrite it?')
            if value == 0x00004000:
                for file in os.listdir(default_destination):
                    file_path = os.path.join(default_destination,file)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path+'/'):
                            shutil.rmtree(file_path+'/')
                    except:pass
            elif value == 0x00010000:
                failed = True
                suffix = 1
                while failed:
                    default_destination = os.path.join(self.dirname,'RHEED scenario '+QtCore.QDateTime().currentDateTime().toString('MMddyyyy') + ' (' + str(suffix) + ')')
                    try:
                        os.mkdir(default_destination)
                        failed = False
                    except FileExistsError:
                        suffix+=1
        self.config.set('TAPD','destination', default_destination)
        self.config.set('CIF','destination', default_destination)

        self.tab = QtWidgets.QTabWidget()
        for section in self.config.sections():
            app = QtWidgets.QWidget()
            app_grid = QtWidgets.QGridLayout(app)
            self.path_dict[section] = {}
            self.dir_dict[section] = {}
            self.line_edit_dict[section] = {}
            self.check_box_dict[section] = {}
            self.combo_box_dict[section] = {}
            self.label_dict[section] = {}
            self.key_dict[section] = {}
            iteration = 0
            for key, value in self.config[section].items():
                if self.is_float(value) and (not key in {'density', 'gamma','radius','low','high','n','p',\
                    'buffer_in_plane_density', 'buffer_in_plane_gamma','buffer_in_plane_radius','buffer_in_plane_low','buffer_in_plane_high','buffer_in_plane_n','buffer_in_plane_p'}):
                        label = QtWidgets.QLabel(key)
                        widget = QtWidgets.QLineEdit(value)
                        widget.textChanged.connect(self.update_scenario)
                        self.line_edit_dict[section][iteration] = widget
                elif os.path.exists(value):
                    label = QtWidgets.QLabel('The ' + key + ' is:\n' + value)
                    label.setWordWrap(True)
                    widget = IndexedPushButtonWithTag('Choose', iteration, section)
                    widget.BUTTON_CLICKED.connect(self.choose_path)
                    self.path_dict[section][iteration] = value
                elif os.access(value, os.W_OK):
                    label = QtWidgets.QLabel('The ' + key + ' is:\n' + value)
                    label.setWordWrap(True)
                    widget = IndexedPushButtonWithTag('Choose', iteration, section)
                    widget.BUTTON_CLICKED.connect(self.choose_dir)
                    self.dir_dict[section][iteration] = value
                elif value == "True" or value == "False":
                    label = QtWidgets.QLabel(key)
                    widget = QtWidgets.QCheckBox()
                    if value == "True":
                        widget.setChecked(True)
                    else:
                        widget.setChecked(False)
                    widget.stateChanged.connect(self.update_scenario)
                    self.check_box_dict[section][iteration] = widget
                else:
                    if key == 'sub_orientation' or key == 'epi_orientation':
                        label = QtWidgets.QLabel(key)
                        widget = QtWidgets.QComboBox()
                        widget.addItem('(001)')
                        widget.addItem('(111)')
                        widget.addItem('(100)')
                        widget.addItem('(110)')
                        widget.setCurrentText(value)
                        widget.currentTextChanged.connect(self.update_scenario)
                        self.combo_box_dict[section][iteration] = widget
                    elif key == 'lattice_or_atoms':
                        label = QtWidgets.QLabel(key)
                        widget = QtWidgets.QComboBox()
                        widget.addItem('lattice')
                        widget.addItem('atoms')
                        widget.setCurrentText(value)
                        widget.currentTextChanged.connect(self.update_scenario)
                        self.combo_box_dict[section][iteration] = widget
                    elif key == 'shape':
                        label = QtWidgets.QLabel(key)
                        widget = QtWidgets.QComboBox()
                        widget.addItem("Triangle")
                        widget.addItem("Square")
                        widget.addItem("Hexagon")
                        widget.addItem("Circle")
                        widget.setCurrentText(value)
                        widget.currentTextChanged.connect(self.update_scenario)
                        self.combo_box_dict[section][iteration] = widget
                    elif key == 'colormap':
                        label = QtWidgets.QLabel(key)
                        widget = QtWidgets.QComboBox()
                        for colormap in plt.colormaps():
                            widget.addItem(colormap)
                        widget.setCurrentText(value)
                        widget.currentTextChanged.connect(self.update_scenario)
                        self.combo_box_dict[section][iteration] = widget
                    elif key == 'distribution' or key == 'buffer_in_plane_distribution':
                        label = QtWidgets.QLabel(key)
                        widget = QtWidgets.QComboBox()
                        widget.addItem('geometric')
                        widget.addItem('completely random')
                        widget.addItem('delta')
                        widget.addItem('binomial')
                        widget.addItem('uniform')
                        widget.setCurrentText(value)
                        widget.currentTextChanged.connect(self.update_scenario)
                        self.combo_box_dict[section][iteration] = widget
                    elif key == 'buffer_out_of_plane_distribution':
                        label = QtWidgets.QLabel(key)
                        widget = QtWidgets.QComboBox()
                        widget.addItem('completely random')
                        widget.addItem('gaussian')
                        widget.addItem('uniform')
                        widget.setCurrentText(value)
                        widget.currentTextChanged.connect(self.update_scenario)
                        self.combo_box_dict[section][iteration] = widget
                    else:
                        label = QtWidgets.QLabel(key)
                        widget = QtWidgets.QLineEdit(value)
                        widget.textChanged.connect(self.update_scenario)
                        self.line_edit_dict[section][iteration] = widget
        
                app_grid.addWidget(label,iteration,0,1,2)
                app_grid.addWidget(widget,iteration,2,1,2)
                self.label_dict[section][iteration] = label
                self.key_dict[section][iteration] = key
                iteration+=1
            self.row[section] = iteration

            scroll = QtWidgets.QScrollArea()
            scroll.setWidget(app)
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
            self.tab.addTab(scroll,section)

        self.scenario_path_label = QtWidgets.QLabel("The scenario is:\n"+os.path.join(self.dirname,'default_scenario.ini'))
        self.choose_scenario_button = QtWidgets.QPushButton("Choose Scenario")
        self.choose_scenario_button.pressed.connect(self.choose_scenario)
        self.save_scenario_button = QtWidgets.QPushButton("Save Scenario")
        self.save_as_default_scenario_button = QtWidgets.QPushButton("Save As Default")
        self.save_scenario_button.clicked.connect(self.save_scenario)
        self.save_as_default_scenario_button.clicked.connect(self.save_as_default_scenario)
        self.run_scenario_button = QtWidgets.QPushButton("Run Current Scenario")
        self.run_scenario_button.clicked.connect(self.run_scenario)
        self.stop_scenario_button = QtWidgets.QPushButton("Stop Running")
        self.stop_scenario_button.clicked.connect(self.stop_scenario)
        self.stop_scenario_button.setEnabled(False)
        self.close_scenario_button = QtWidgets.QPushButton("Close Scenario")
        self.close_scenario_button.clicked.connect(self.close_scenario)
        self.close_scenario_button.setEnabled(False)
    
        self.main_layout.addWidget(self.scenario_path_label,0,0,1,3)
        self.main_layout.addWidget(self.choose_scenario_button,1,0,1,1)
        self.main_layout.addWidget(self.save_scenario_button,1,1,1,1)
        self.main_layout.addWidget(self.save_as_default_scenario_button,1,2,1,1)
        self.main_layout.addWidget(self.tab,2,0,1,3)
        self.main_layout.addWidget(self.run_scenario_button,3,0,1,1)
        self.main_layout.addWidget(self.stop_scenario_button,3,1,1,1)
        self.main_layout.addWidget(self.close_scenario_button,3,2,1,1)
        self.setMinimumSize(600,800)
        self.showNormal()

    def choose_path(self,row,section):
        self.path_dict[section][row] = QtWidgets.QFileDialog.getOpenFileName(None,"Choose the "+self.key_dict[section][row],self.dirname,filter="CIF (*.cif);;All Files (*.*)")[0]
        self.label_dict[section][row].setText("The " + self.key_dict[section][row] +" is:\n"+self.path_dict[section][row])
        if self.path_dict[section][row]:
            self.update_scenario

    def choose_dir(self,row,section):
        self.dir_dict[section][row] = QtWidgets.QFileDialog.getOpenFileName(None,"Choose the "+self.key_dict[section][row],self.dirname,filter="CIF (*.cif);;All Files (*.*)")[0]
        self.label_dict[section][row].setText("The " + self.key_dict[section][row] +" is:\n"+self.path_dict[section][row])
        if self.dir_dict[section][row]:
            self.update_scenario

    def choose_scenario(self):
        self.scenario_path = QtWidgets.QFileDialog.getOpenFileName(None,"Choose scenario",self.dirname,filter="INI (*.ini);;All Files (*.*)")[0]
        self.scenario_path_label.setText("The scenario path is:\n"+self.scenario_path)
        self.load_scenario(self.scenario_path)
        self.apply_scenario()

    def update_scenario(self, para=None):
        for section in self.config.sections():
            for row in range(self.row[section]):
                if row in self.path_dict[section]:
                    value = self.path_dict[section][row]
                elif row in self.dir_dict[section]:
                    value = self.dir_dict[section][row]
                elif row in self.line_edit_dict[section]:
                    value = self.line_edit_dict[section][row].text()
                elif row in self.check_box_dict[section]:
                    value = str(self.check_box_dict[section][row].isChecked())
                elif row in self.combo_box_dict[section]:
                    value = self.combo_box_dict[section][row].currentText()
                self.config.set(section,self.key_dict[section][row],value)

    def save_scenario(self):
        current_date = QtCore.QDateTime().currentDateTime().toString('MMddyyyy_')
        filename = current_date + 'scenario.ini'
        path = QtWidgets.QFileDialog.getSaveFileName(None,"choose save file name",os.path.join(self.dirname,filename),"INI (*.ini)")[0]
        with open(path,'w') as configfile:
            self.config.write(configfile)

    def save_as_default_scenario(self):
        with open(os.path.join(self.dirname,'default_scenario.ini'),'w') as configfile:
            self.config.write(configfile)

    def load_scenario(self,path=None):
        self.config = configparser.ConfigParser()
        if path == None:
            self.config.read(os.path.join(self.dirname,'default_scenario.ini'))
        else:
            self.config.read(path)

    def apply_scenario(self):
        for section in self.config.sections():
            for row in range(self.row[section]):
                key = self.key_dict[section][row]
                value = self.config[section][key]
                if self.is_float(value):
                    self.line_edit_dict[section][row].setText(value)
                elif os.path.exists(value):
                    self.path_dict[section][row] = value 
                    self.label_dict[section][row].setText("The " + key +" is:\n"+value)
                elif os.access(value, os.W_OK):
                    self.dir_dict[section][row] = value 
                    self.label_dict[section][row].setText("The " + key +" is:\n"+value)
                elif value == "True":
                    self.check_box_dict[section][row].setChecked(True)
                elif value == "False":
                    self.check_box_dict[section][row].setChecked(False)
                else:
                    self.combo_box_dict[section][row].setCurrentText(value)

    def run_scenario(self):
        section = self.tab.tabText(self.tab.currentIndex())
        self.stop_scenario_button.setEnabled(True)
        self.close_scenario_button.setEnabled(False)
        if section == 'TAPD':
            self.density_length = len(self.config[section]['density'].split(","))-1
            self.density_index=0
            self.sub_TAPD_scenario(self.config[section]['density'].split(",")[self.density_index])
        elif section == 'CIF':
            self.Z_min_length = len(self.config[section]['Z_min'].split(","))-1
            self.Z_min_index=0
            self.sub_CIF_scenario(float(self.config[section]['Z_min'].split(",")[self.Z_min_index]))

    def sub_TAPD_scenario(self,density):
        section = self.tab.tabText(self.tab.currentIndex())
        self.simulation = simulate_RHEED.Window()
        self.simulation.setEnabled(False)
        self.simulation.TAPD_FINISHED.connect(self.scenario_finished)
        self.simulation.TAPD_RESULTS.connect(self.scenario_TAPD_results)
        self.simulation.CLOSE.connect(self.scenario_is_closed)
        self.simulation.RESULT_IS_READY.connect(self.save_TAPD_results)
        self.simulation.main()
        self.simulation.load_TAPD_scenario(self.config[section])
        self.simulation.reload_TAPD(density=density)

    def sub_CIF_scenario(self,Z_min):
        section = self.tab.tabText(self.tab.currentIndex())
        self.simulation = simulate_RHEED.Window()
        self.simulation.setEnabled(False)
        self.simulation.CLOSE.connect(self.scenario_is_closed)
        self.simulation.RESULT_IS_READY.connect(self.save_CIF_results)
        self.simulation.main()
        self.simulation.load_CIF_scenario(self.config[section])
        self.simulation.get_cif_path(self.config[section]['cif_path'])
        self.simulation.reload_CIF(Z_min=Z_min)

    def scenario_finished(self):
        self.stop_scenario_button.setEnabled(False)

    def scenario_TAPD_results(self,model,density):
        self.TAPD_results = model
        self.close_scenario_button.setEnabled(True)
        section = self.tab.tabText(self.tab.currentIndex())
        self.save_dir = self.config[section]['destination'] + '/' + density + '-' + \
            str(float(self.config[section]['x_max'])*2/10) + 'nm/'
        try:
            os.mkdir(self.save_dir)
        except FileExistsError:
            value = self.request_confirmation('The directory already exist. Do you want to overwrite it?')
            if value == 0x00004000:
                for file in os.listdir(self.save_dir):
                    file_path = os.path.join(self.save_dir,file)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except:pass
            elif value == 0x00010000:
                failed = True
                suffix = 1
                while failed:
                    self.save_dir = self.config[section]['destination'] + '/' + density + '-' + \
                    str(float(self.config[section]['x_max'])*2/10) + 'nm' + ' (' + str(suffix) + ')/'
                    try:
                        os.mkdir(self.save_dir)
                        failed = False
                    except FileExistsError:
                        suffix+=1

        with open(self.save_dir + 'scenario.ini','w') as configfile:
            self.config.write(configfile)
        if self.config[section]['save_size_distribution'] == 'True':
            self.simulation.plot_distribution(destination=self.save_dir, save_as_file=True)
        if self.config[section]['save_boundary'] == 'True':
            self.simulation.plot_boundary(destination=self.save_dir, save_as_file=True)
        if self.config[section]['save_boundary_statistics'] == 'True':
            self.simulation.plot_boundary_statistics(destination=self.save_dir, save_as_file=True)
        if self.config[section]['save_voronoi_diagram'] == 'True':
            self.simulation.plot_voronoi(destination=self.save_dir, save_as_file=True)
        if self.config[section]['save_scene'] == 'True':
            self.simulation.graph.save_scene(destination=self.save_dir, save_as_file=True)
        if self.config[section]['calculate_diffraction'] == 'True':
            self.simulation.update_reciprocal_range()
        else:
            if self.density_index < self.density_length:
                self.density_index+=1
                self.simulation.deleteLater()
                self.sub_TAPD_scenario(self.config[section]['density'].split(",")[self.density_index])
            else:
                self.simulation.setEnabled(True)

    def save_TAPD_results(self):
        section = self.tab.tabText(self.tab.currentIndex())
        if self.config[section]['save_2D_map_data'] == 'True':
            self.simulation.save_results(directory=self.save_dir, name='2D_map', save_as_file=True)
        if self.config[section]['save_2D_map_image'] == 'True':
            self.simulation.show_XY_plot(directory=self.save_dir, name='2D_map.tif', font_size=50, save_as_file=True)
        if self.density_index < self.density_length:
            self.density_index+=1
            self.simulation.deleteLater()
            self.sub_TAPD_scenario(self.config[section]['density'].split(",")[self.density_index])
        else:
            self.simulation.setEnabled(True)

    def save_CIF_results(self,always_say_yes = True):
        section = self.tab.tabText(self.tab.currentIndex())
        self.save_dir = self.config[section]['destination'] + self.config[section]['Z_min'].split(",")[self.Z_min_index] + '/'
        try:
            os.mkdir(self.save_dir)
        except FileExistsError:
            if not always_say_yes:
                value = self.request_confirmation('The directory already exist. Do you want to overwrite it?')
            else:
                value = 0x00004000
            if value == 0x00004000:
                for file in os.listdir(self.save_dir):
                    file_path = os.path.join(self.save_dir,file)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except:pass
            elif value == 0x00010000:
                failed = True
                suffix = 1
                while failed:
                    self.save_dir = self.config[section]['destination'] + self.config[section]['Z_min'].split(",")[self.Z_min_index] +  + ' (' + str(suffix) + ')/'
                    try:
                        os.mkdir(self.save_dir)
                        failed = False
                    except FileExistsError:
                        suffix+=1

        if self.config[section]['save_scene'] == 'True':
            if self.config[section]['save_zoomed_scene'] == 'True':
                zoom = True
            elif self.config[section]['save_zoomed_scene'] == 'False':
                zoom = False
            self.simulation.graph.save_scene(destination=self.save_dir, save_as_file=True, save_zoomed_scene = zoom)
        if self.config[section]['save_IV_data'] == 'True':
            self.simulation.save_results(directory=self.save_dir, name='IV_'+str(self.Z_min_index)+'.txt', save_as_file=True, save_vtp=False)
        if self.config[section]['save_IV_image'] == 'True':
            self.simulation.show_YZ_plot(directory=self.save_dir, name='IV_'+str(self.Z_min_index)+'.tif', font_size=50, save_as_file=True)
            self.simulation.save_FFT([self.save_dir+'FFT_'+str(self.Z_min_index)+'.txt'])
        if self.Z_min_index < self.Z_min_length:
            self.Z_min_index+=1
            self.simulation.deleteLater()
            self.sub_CIF_scenario(float(self.config[section]['Z_min'].split(",")[self.Z_min_index]))
        else:
            self.simulation.setEnabled(True)
    
    def stop_scenario(self):
        section = self.tab.tabText(self.tab.currentIndex())
        if section == 'TAPD':
            self.simulation.stop_TAPD()
            self.simulation.deleteLater()
            self.close_scenario_button.setEnabled(False)
        elif section == 'CIF':
            self.simulation.stop_diffraction_calculation()
            self.simulation.deleteLater()
            self.close_scenario_button.setEnabled(False)

    def close_scenario(self):
        self.simulation.deleteLater()
        self.close_scenario_button.setEnabled(False)

    def scenario_is_closed(self):
        self.simulation.deleteLater()
        self.close_scenario_button.setEnabled(False)
        self.stop_scenario_button.setEnabled(False)
            
    def is_float(self,value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def request_confirmation(self,message):
        info = QtWidgets.QMessageBox()
        info.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        info.setText(message)
        info.setWindowTitle("Information")
        info.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
        return info.exec()

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
    window = Window()
    sys.exit(app.exec_())

if __name__ == '__main__':
    test()
