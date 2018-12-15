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
        self.window = Window(config)
        self.window.showMaximized()
        self.window.show()
        self.menuPreferences = Menu.Preference()
        self.menuTwoDimensionalMapping = Menu.TwoDimensionalMapping()
        self.window.menu_DefaultPropertiesRestRequested.connect(self.menuPreferences.Main)
        self.window.menu_TwoDimensionalMappingRequested.connect(self.menuTwoDimensionalMapping.Main)
        self.window.menu_ThreeDimensionalGraphRequested.connect(self.run3DGraph)
        self.menuPreferences.DefaultSettingsChanged.connect(self.window.refresh)
        self.menuTwoDimensionalMapping.StatusRequested.connect(self.window.status)
        self.window.returnStatus.connect(self.menuTwoDimensionalMapping.Set_Status)
        self.menuTwoDimensionalMapping.Show3DGraph.connect(self.run3DGraph)
        sys.exit(app.exec_())

    def run3DGraph(self,path):
        self.graph = Graph3DSurface.Graph()
        self.graph.run3DGraph(path)


if __name__ == '__main__':
    Main()

