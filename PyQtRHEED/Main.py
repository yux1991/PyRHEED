from Window import *
import sys
from Configuration import *
import Menu

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
        self.menuPreferences.DefaultSettingsChanged.connect(self.window.refresh)
        self.menuTwoDimensionalMapping.StatusRequested.connect(self.window.status)
        self.window.returnStatus.connect(self.menuTwoDimensionalMapping.Set_Status)
        sys.exit(app.exec_())

if __name__ == '__main__':
    Main()

