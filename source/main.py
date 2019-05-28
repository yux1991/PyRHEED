#This sets up the entire application, which reads the default configuration and initialize the UI
#Last updated on 04/15/2019 by Y. Xiang
#This code is written in Python 3.6.3
from PyQt5 import QtGui, QtWidgets
import broadening
import configparser
import generate_report
import graph_3D_surface
import manual_fit
import preference
import reciprocal_space_mapping
import simulate_RHEED
import statistical_factor
import sys
import window

class Window():
    """The main class"""
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('./configuration.ini')  #Read the configuration file
        app = QtWidgets.QApplication(sys.argv)
        icon = QtGui.QIcon('./icons/icon.png')
        app.setWindowIcon(icon)
        self.window = window.Window(config)    #Initialze the main window using the default values in the configuration
        self.window.showMaximized()
        self.window.show()
        #Connect the signals emitted by the window object
        self.window.DEFAULT_PROPERTIES_REQUESTED.connect(self.run_preference)
        self.window.RECIPROCAL_SPACE_MAPPING_REQUESTED.connect(self.run_reciprocal_space_mapping)
        self.window.BROADENING_REQUESTED.connect(self.run_broadening)
        self.window.MANUAL_FIT_REQUESTED.connect(self.run_manual_fit)
        self.window.GENERATE_REPORT_REQUESTED.connect(self.run_generate_report)
        self.window.STATISTICAL_FACTOR_REQUESTED.connect(self.run_simulate_RHEED)
        self.window.DIFFRACTION_PATTERN_REQUESTED.connect(self.run_simulate_RHEED)
        self.window.THREE_DIMENSIONAL_GRAPH_REQUESTED.connect(self.run_3D_graph)
        self.preference = preference.Window()
        self.preference.DEFAULT_SETTINGS_CHANGED.connect(self.window.refresh)
        sys.exit(app.exec_())

    def run_preference(self):
        self.preference.main()

    def run_reciprocal_space_mapping(self,path):
        self.reciprocal_space_mapping = reciprocal_space_mapping.Window()
        self.reciprocal_space_mapping.STATUS_REQUESTED.connect(self.window.status)
        self.reciprocal_space_mapping.SHOW_3D_GRAPH.connect(self.run_3D_graph)
        self.reciprocal_space_mapping.SHOW_2D_CONTOUR.connect(self.run_2D_contour)
        self.reciprocal_space_mapping.CONNECT_TO_CANVAS.connect(self.connect_mapping_to_canvas)
        self.window.RETURN_STATUS.connect(self.reciprocal_space_mapping.set_status)
        self.preference.DEFAULT_SETTINGS_CHANGED.connect(self.reciprocal_space_mapping.refresh)
        self.reciprocal_space_mapping.main(path)

    def run_generate_report(self,path):
        self.generate_report = generate_report.Window()
        self.generate_report.STATUS_REQUESTED.connect(self.window.status)
        self.window.RETURN_STATUS.connect(self.generate_report.set_status)
        self.generate_report.main(path)

    def run_manual_fit(self,path,nop):
        self.manual_fit = manual_fit.Window()
        self.manual_fit.STATUS_REQUESTED.connect(self.window.status)
        self.window.RETURN_STATUS.connect(self.manual_fit.set_status)
        self.preference.DEFAULT_SETTINGS_CHANGED.connect(self.manual_fit.refresh)
        self.manual_fit.main(path,nop)

    def run_broadening(self,path):
        self.broadening = broadening.Window()
        self.broadening.STATUS_REQUESTED.connect(self.window.status)
        self.broadening.CONNECT_TO_CANVAS.connect(self.connect_broadening_to_canvas)
        self.window.RETURN_STATUS.connect(self.broadening.set_status)
        self.preference.DEFAULT_SETTINGS_CHANGED.connect(self.broadening.refresh)
        self.broadening.main(path)

    def run_statistical_factor(self):
        self.statistical_factor = statistical_factor.Window()
        self.statistical_factor.main()

    def run_simulate_RHEED(self):
        self.simulation = simulate_RHEED.Window()
        self.simulation.main()

    def run_3D_graph(self,path=''):
        """The window to show a 3D surface

        Args:
            path: str, optional
                The path of the text file that contains the 2D reciprocal space mapping data. Default is ''.
        """
        self.graph = graph_3D_surface.Graph()
        self.graph.run_3D_graph(path)

    def run_2D_contour(self, path=None, insideGraph3D = False, min=0.0, max=1.0, radius_min=0, radius_max=10, number_of_levels=50, colormap='jet'):
        """The window to show a 2D Contour

        Args:
            path: str, optional
                The path of the text file that contains the 2D reciprocal space mapping data. Default is None.
            insideGraph3D: bool, optional
                True if the function is intended to be called from a 3D graph window. Default is False.
            min: float, optional
                Level minimum. Default is 0.0.
            max: float,optional
                Level maximum. Default is 1.0.
            radius_min: float, optional
                The start position on the radial axis. Default is 0.
            radius_max: float, optional
                The end position on the radial axis. Default is 10.
            number_of_levels: int, optional
                The number of contour levels. Default is 50.
            colormap: str, optional
                The name of the colormap. Default is 'jet'.

        """
        self.graph = graph_3D_surface.Graph()
        self.graph.show_2d_contour(path,insideGraph3D = insideGraph3D, min=min, max=max, radius_min=radius_min, radius_max=radius_max,\
                                   number_of_levels=number_of_levels, colormap=colormap)

    def connect_broadening_to_canvas(self):
        """Signal Connection"""
        self.broadening.DRAW_LINE_REQUESTED.connect(self.window.mainTab.currentWidget().draw_line)
        self.broadening.DRAW_RECT_REQUESTED.connect(self.window.mainTab.currentWidget().draw_rect)

    def connect_mapping_to_canvas(self):
        """Signal Connection"""
        self.reciprocal_space_mapping.DRAW_LINE_REQUESTED.connect(self.window.mainTab.currentWidget().draw_line)
        self.reciprocal_space_mapping.DRAW_RECT_REQUESTED.connect(self.window.mainTab.currentWidget().draw_rect)

if __name__ == '__main__':
    Window()

