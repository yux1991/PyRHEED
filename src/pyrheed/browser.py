from PyQt6 import QtCore, QtWidgets, QtGui
import os

class Browser(QtWidgets.QWidget):

    #Public Signals
    FILE_DOUBLE_CLICKED = QtCore.pyqtSignal(str)

    def __init__(self,parent,filter):
        super(Browser,self).__init__(parent)
        self.filter = filter
        self.init_UI()

    def init_UI(self,path=QtCore.QDir.currentPath()):
        self.model = QtGui.QFileSystemModel()
        self.model.setRootPath(path)
        self.model.setNameFilters(self.filter)
        self.model.setNameFilterDisables(False)
        self.tree = QtWidgets.QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(path))
        self.tree.setAnimated(True)
        self.tree.setIndentation(20)
        self.tree.setSortingEnabled(True)
        self.tree.sortByColumn(0,QtCore.Qt.SortOrder.AscendingOrder)
        self.tree.setColumnWidth(0,400)
        self.tree.setColumnWidth(1,150)
        self.tree.setColumnWidth(2,150)
        self.tree.doubleClicked.connect(self.open_file)
        self.tree.expandAll()
        self.UIgrid = QtWidgets.QGridLayout()
        self.UIgrid.addWidget(self.tree,0,0)
        self.UIgrid.setContentsMargins(0,0,2,0)
        self.setLayout(self.UIgrid)
        self.show()

    def open_file(self,index):
        item = self.tree.selectedIndexes()[0]
        path = item.model().filePath(index)
        if os.path.isfile(path):
            self.FILE_DOUBLE_CLICKED.emit(path)

    def tree_update(self,path):
        dir = os.path.dirname(path)
        parent_dir = os.path.dirname(dir)
        self.model.setRootPath(parent_dir)
        self.tree.setRootIndex(self.model.index(parent_dir))
        self.tree.setExpanded(self.model.index(dir), True)
