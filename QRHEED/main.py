from Window import *
import sys

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.showMaximized()
    window.show()
    sys.exit(app.exec_())
