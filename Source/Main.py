from Window import *
import sys
from Configuration import *
import Menu
import Graph3DSurface

class Main():
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
        self.menuTwoDimensionalMapping = Menu.TwoDimensionalMapping()
        self.menuBroadening = Menu.Broadening()
        self.menuManualFit = Menu.ManualFit()
        self.menuGenerateReport = Menu.GenerateReport()
        self.window.menu_DefaultPropertiesRestRequested.connect(self.menuPreferences.Main)
        self.window.menu_TwoDimensionalMappingRequested.connect(self.menuTwoDimensionalMapping.Main)
        self.window.menu_BroadeningRequested.connect(self.menuBroadening.Main)
        self.window.menu_ManualFitRequested.connect(self.menuManualFit.Main)
        self.window.menu_GenerateReportRequested.connect(self.menuGenerateReport.Main)
        self.window.menu_ThreeDimensionalGraphRequested.connect(self.run3DGraph)
        self.menuPreferences.DefaultSettingsChanged.connect(self.window.refresh)
        self.menuPreferences.DefaultSettingsChanged.connect(self.menuTwoDimensionalMapping.refresh)
        self.menuTwoDimensionalMapping.StatusRequested.connect(self.window.status)
        self.window.returnStatus.connect(self.menuTwoDimensionalMapping.Set_Status)
        self.window.returnStatus.connect(self.menuBroadening.Set_Status)
        self.window.returnStatus.connect(self.menuManualFit.Set_Status)
        self.window.returnStatus.connect(self.menuGenerateReport.Set_Status)
        self.menuBroadening.StatusRequested.connect(self.window.status)
        self.menuBroadening.connectToCanvas.connect(self.connect_broadening_to_canvas)
        self.menuManualFit.StatusRequested.connect(self.window.status)
        self.menuGenerateReport.StatusRequested.connect(self.window.status)
        self.menuTwoDimensionalMapping.Show3DGraph.connect(self.run3DGraph)
        self.menuTwoDimensionalMapping.Show2DContour.connect(self.run2DContour)
        sys.exit(app.exec_())

    def run3DGraph(self,path=''):
        self.graph = Graph3DSurface.Graph()
        self.graph.run3DGraph(path)

    def run2DContour(self, path=None, insideGraph3D = False, min=0.0, max=1.0, radius_min=0, radius_max=10, number_of_levels=50, colormap='jet'):
        self.graph = Graph3DSurface.Graph()
        self.graph.Show_2D_Contour(path,insideGraph3D = insideGraph3D, min=min, max=max, radius_min=radius_min, radius_max=radius_max,\
                                   number_of_levels=number_of_levels, colormap=colormap)

    def connect_broadening_to_canvas(self):
        self.menuBroadening.drawLineRequested.connect(self.window.mainTab.currentWidget().drawLine)
        self.menuBroadening.drawRectRequested.connect(self.window.mainTab.currentWidget().drawRect)

if __name__ == '__main__':
    Main()

