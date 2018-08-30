from PyQt5 import QtCore, QtWidgets

class Browser(QtWidgets.QWidget):

    def __init__(self,parent):
        super(Browser,self).__init__(parent)
        self.initUI()


    def initUI(self):
        model = QtWidgets.QFileSystemModel()
        model.setRootPath(QtCore.QDir.currentPath())
        tree = QtWidgets.QTreeView()
        tree.setModel(model)
        tree.setAnimated(False)
        tree.setIndentation(20)
        tree.setSortingEnabled(True)
        tree.setWindowTitle("Dir View")
        UIgrid = QtWidgets.QGridLayout()
        UIgrid.addWidget(tree,0,0)
        self.setLayout(UIgrid)
        self.show()

