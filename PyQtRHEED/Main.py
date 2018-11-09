from Window import *
import sys
from Configuration import *
from Menu import *

class Main():
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('./configuration.ini')
        app = QtWidgets.QApplication(sys.argv)
        self.window = Window(config)
        self.window.showMaximized()
        self.window.show()
        self.menuActions = Menu()
        self.window.menu_DefaultPropertiesRestRequested.connect(self.menuActions.Preference_DefaultSettings)
        self.menuActions.DefaultSettingsChanged.connect(self.window.refresh)
        sys.exit(app.exec_())

if __name__ == '__main__':
    Main()

