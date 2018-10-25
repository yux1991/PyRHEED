from Window import *
import sys
from Configuration import *
import os.path

if __name__ == '__main__':
    Configuration().saveDefaults()
    config = configparser.ConfigParser()
    config.read('./configuration.ini')
    app = QtWidgets.QApplication(sys.argv)
    window = Window(config)
    window.showMaximized()
    window.show()
    sys.exit(app.exec_())
