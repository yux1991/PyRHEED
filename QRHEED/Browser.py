from PyQt5 import QtCore, QtWidgets
import os

class Browser(QtWidgets.QWidget):

    def __init__(self,parent):
        super(Browser,self).__init__(parent)
        self.initUI()

    #Public Signals
    fileDoubleClicked = QtCore.pyqtSignal(str)


    def initUI(self,path=QtCore.QDir.currentPath()):
        self.model = QtWidgets.QFileSystemModel()
        self.model.setRootPath(path)
        self.tree = QtWidgets.QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(path))
        self.tree.setAnimated(False)
        self.tree.setIndentation(20)
        self.tree.setSortingEnabled(True)
        self.tree.doubleClicked.connect(self.open_file)
        self.UIgrid = QtWidgets.QGridLayout()
        self.UIgrid.addWidget(self.tree,0,0)
        self.UIgrid.setContentsMargins(0,0,2,0)
        self.setLayout(self.UIgrid)
        self.show()

    def open_file(self,index):
        item = self.tree.selectedIndexes()[0]
        path = item.model().filePath(index)
        if os.path.isfile(path):
            self.fileDoubleClicked.emit(path)

    def treeUpdate(self,path):
        dir = os.path.dirname(path)
        self.model.setRootPath(dir)
        self.tree.setRootIndex(self.model.index(dir))
