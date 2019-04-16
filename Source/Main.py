#This sets up the entire application, which reads the default configuration and initialize the UI
#Last updated on 04/15/2019 by Y. Xiang
#This code is written in Python 3.6.3
from Window import *
import sys
from Configuration import *
import Menu
import Graph3DSurface
import StatisticalFactor

class Main():
    """The main class"""
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('./configuration.ini')
        app = QtWidgets.QApplication(sys.argv)
        icon = QtGui.QIcon('./icons/icon.png')
        app.setWindowIcon(icon)
        self.window = Window(config)
        self.window.showMaximized()
        self.window.show()
        self.menuPreferences = Menu.Preference()
        self.menuReciprocalSpaceMapping = Menu.ReciprocalSpaceMapping()
        self.menuBroadening = Menu.Broadening()
        self.menuManualFit = Menu.ManualFit()
        self.menuGenerateReport = Menu.GenerateReport()
        self.StatisticalFactor = StatisticalFactor.Window()
        self.window.menu_DefaultPropertiesRestRequested.connect(self.menuPreferences.Main)
        self.window.menu_ReciprocalSpaceMappingRequested.connect(self.menuReciprocalSpaceMapping.Main)
        self.window.menu_BroadeningRequested.connect(self.menuBroadening.Main)
        self.window.menu_ManualFitRequested.connect(self.menuManualFit.Main)
        self.window.menu_GenerateReportRequested.connect(self.menuGenerateReport.Main)
        self.window.menu_StatisticalFactorRequested.connect(self.StatisticalFactor.Main)
        self.window.menu_ThreeDimensionalGraphRequested.connect(self.run3DGraph)
        self.menuPreferences.DefaultSettingsChanged.connect(self.window.refresh)
        self.menuPreferences.DefaultSettingsChanged.connect(self.menuReciprocalSpaceMapping.refresh)
        self.menuReciprocalSpaceMapping.StatusRequested.connect(self.window.status)
        self.window.returnStatus.connect(self.menuReciprocalSpaceMapping.Set_Status)
        self.window.returnStatus.connect(self.menuBroadening.Set_Status)
        self.window.returnStatus.connect(self.menuManualFit.Set_Status)
        self.window.returnStatus.connect(self.menuGenerateReport.Set_Status)
        self.menuBroadening.StatusRequested.connect(self.window.status)
        self.menuBroadening.connectToCanvas.connect(self.connect_broadening_to_canvas)
        self.menuManualFit.StatusRequested.connect(self.window.status)
        self.menuGenerateReport.StatusRequested.connect(self.window.status)
        self.menuReciprocalSpaceMapping.Show3DGraph.connect(self.run3DGraph)
        self.menuReciprocalSpaceMapping.Show2DContour.connect(self.run2DContour)
        self.menuReciprocalSpaceMapping.connectToCanvas.connect(self.connect_mapping_to_canvas)
        sys.exit(app.exec_())

    def run3DGraph(self,path=''):
        """The window to show a 3D surface

        Args:
            path: str, optional
                The path of the text file that contains the 2D reciprocal space mapping data. Default is ''.
        """
        self.graph = Graph3DSurface.Graph()
        self.graph.run3DGraph(path)

    def run2DContour(self, path=None, insideGraph3D = False, min=0.0, max=1.0, radius_min=0, radius_max=10, number_of_levels=50, colormap='jet'):
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
        self.graph = Graph3DSurface.Graph()
        self.graph.Show_2D_Contour(path,insideGraph3D = insideGraph3D, min=min, max=max, radius_min=radius_min, radius_max=radius_max,\
                                   number_of_levels=number_of_levels, colormap=colormap)

    def connect_broadening_to_canvas(self):
        """Signal Connection"""
        self.menuBroadening.drawLineRequested.connect(self.window.mainTab.currentWidget().drawLine)
        self.menuBroadening.drawRectRequested.connect(self.window.mainTab.currentWidget().drawRect)

    def connect_mapping_to_canvas(self):
        """Signal Connection"""
        self.menuReciprocalSpaceMapping.drawLineRequested.connect(self.window.mainTab.currentWidget().drawLine)
        self.menuReciprocalSpaceMapping.drawRectRequested.connect(self.window.mainTab.currentWidget().drawRect)

if __name__ == '__main__':
    Main()

