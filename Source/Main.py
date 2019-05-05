#This sets up the entire application, which reads the default configuration and initialize the UI
#Last updated on 04/15/2019 by Y. Xiang
#This code is written in Python 3.6.3
from Window import *
import sys
from Configuration import *
import Graph3DSurface
import StatisticalFactor
import SimulateRHEED
import ReciprocalSpaceMapping
import GenerateReport
import ManualFit
import Broadening
import Preference

class Main():
    """The main class"""
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('./configuration.ini')  #Read the configuration file
        app = QtWidgets.QApplication(sys.argv)
        icon = QtGui.QIcon('./icons/icon.png')
        app.setWindowIcon(icon)
        self.window = Window(config)    #Initialze the main window using the default values in the configuration
        self.window.showMaximized()
        self.window.show()
        #Connect the signals emitted by the window object
        self.window.DefaultPropertiesRestRequested.connect(self.runPreference)
        self.window.ReciprocalSpaceMappingRequested.connect(self.runReciprocalSpaceMapping)
        self.window.BroadeningRequested.connect(self.runBroadening)
        self.window.ManualFitRequested.connect(self.runManualFit)
        self.window.GenerateReportRequested.connect(self.runGenerateReport)
        self.window.StatisticalFactorRequested.connect(self.runStatisticalFactor)
        self.window.DiffractionPatternRequested.connect(self.runSimulateRHEED)
        self.window.ThreeDimensionalGraphRequested.connect(self.run3DGraph)
        self.Preference = Preference.Window()
        self.Preference.DefaultSettingsChanged.connect(self.window.refresh)
        sys.exit(app.exec_())

    def runPreference(self):
        self.Preference.Main()

    def runReciprocalSpaceMapping(self,path):
        self.ReciprocalSpaceMapping = ReciprocalSpaceMapping.Window()
        self.ReciprocalSpaceMapping.Main(path)
        self.ReciprocalSpaceMapping.StatusRequested.connect(self.window.status)
        self.ReciprocalSpaceMapping.Show3DGraph.connect(self.run3DGraph)
        self.ReciprocalSpaceMapping.Show2DContour.connect(self.run2DContour)
        self.ReciprocalSpaceMapping.connectToCanvas.connect(self.connect_mapping_to_canvas)
        self.window.returnStatus.connect(self.ReciprocalSpaceMapping.Set_Status)
        self.Preference.DefaultSettingsChanged.connect(self.ReciprocalSpaceMapping.refresh)

    def runGenerateReport(self,path):
        self.GenerateReport = GenerateReport.Window()
        self.GenerateReport.Main(path)
        self.GenerateReport.StatusRequested.connect(self.window.status)
        self.window.returnStatus.connect(self.GenerateReport.Set_Status)

    def runManualFit(self,path,nop):
        self.ManualFit = ManualFit.Window()
        self.ManualFit.Main(path,nop)
        self.ManualFit.StatusRequested.connect(self.window.status)
        self.window.returnStatus.connect(self.ManualFit.Set_Status)
        self.Preference.DefaultSettingsChanged.connect(self.ManualFit.refresh)

    def runBroadening(self,path):
        self.Broadening = Broadening.Window()
        self.Broadening.Main(path)
        self.Broadening.StatusRequested.connect(self.window.status)
        self.Broadening.connectToCanvas.connect(self.connect_broadening_to_canvas)
        self.window.returnStatus.connect(self.Broadening.Set_Status)
        self.Preference.DefaultSettingsChanged.connect(self.Broadening.refresh)

    def runStatisticalFactor(self):
        self.StatisticalFactor = StatisticalFactor.Window()
        self.StatisticalFactor.Main()

    def runSimulateRHEED(self):
        self.simulation = SimulateRHEED.Window()
        self.simulation.Main()

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
        self.Broadening.drawLineRequested.connect(self.window.mainTab.currentWidget().drawLine)
        self.Broadening.drawRectRequested.connect(self.window.mainTab.currentWidget().drawRect)

    def connect_mapping_to_canvas(self):
        """Signal Connection"""
        self.ReciprocalSpaceMapping.drawLineRequested.connect(self.window.mainTab.currentWidget().drawLine)
        self.ReciprocalSpaceMapping.drawRectRequested.connect(self.window.mainTab.currentWidget().drawRect)

if __name__ == '__main__':
    Main()

