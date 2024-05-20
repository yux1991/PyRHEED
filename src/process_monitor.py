from PyQt6 import QtCore, QtWidgets, QtGui, QtCharts
from sys import getsizeof


class Monitor(QtCore.QObject):

    def __init__(self, *args, **kwargs):
        super(Monitor,self).__init__()
        self.widget = QtWidgets.QWidget()
        self.grid = QtWidgets.QGridLayout(self.widget)
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(len(args))
        self.row_dict={}
        self.row_number=1
        for obj in args:
            for att in dir(obj):
                if not att in self.row_dict:
                    self.row_dict[att] = self.row_number
                    self.row_number+=1
        self.table.setRowCount(len(self.row_dict))
        self.table.setVerticalHeaderItem(0,QtWidgets.QTableWidgetItem('Total'))
        for att in self.row_dict.keys():
            item = QtWidgets.QTableWidgetItem(att)
            self.table.setVerticalHeaderItem(self.row_dict[att],item)

        for j, obj in enumerate(args):
            self.table.setHorizontalHeaderItem(j,QtWidgets.QTableWidgetItem(obj.__class__.__name__))
            total_size=0
            for att in dir(obj):
                size = getsizeof(getattr(obj,att))
                total_size+=size
                item = QtWidgets.QTableWidgetItem('{}'.format(size))
                if size >= 1024000:
                    item.setForeground(QtGui.QBrush(QtGui.QColor(QtCore.Qt.GlobalColor.red)))
                else:
                    item.setForeground(QtGui.QBrush(QtGui.QColor(QtCore.Qt.GlobalColor.black)))
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(self.row_dict[att],j,item)
            self.table.setItem(0,j,QtWidgets.QTableWidgetItem('{}'.format(total_size)))
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setBackgroundRole(QtGui.QPalette.ColorRole.Highlight)
        self.grid.addWidget(self.table,0,0)
        self.widget.setWindowTitle("Process Monitor")
        self.widget.setMinimumHeight(800)
        self.widget.setMinimumWidth(400)
        self.widget.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        self.widget.showNormal()
        desktopRect = self.Dialog.geometry()
        center = desktopRect.center()
        self.widget.move(center.x()-self.widget.width()*0.5,center.y()-self.widget.height()*0.5)

    def update(self, *args, **kwargs):
        for j, obj in enumerate(args):
            total_size = 0
            for att in dir(obj):
                if not att in self.row_dict:
                    self.row_dict[att] = self.row_number
                    self.table.insertRow(self.row_number)
                    self.table.setVerticalHeaderItem(self.row_dict[att],QtWidgets.QTableWidgetItem(att))
                    self.row_number+=1
                size = getsizeof(getattr(obj,att))
                total_size+=size
                item = QtWidgets.QTableWidgetItem('{}'.format(size))
                if size >= 1024000:
                    item.setForeground(QtGui.QBrush(QtGui.QColor(QtCore.Qt.GlobalColor.red)))
                else:
                    item.setForeground(QtGui.QBrush(QtGui.QColor(QtCore.Qt.GlobalColor.black)))
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(self.row_dict[att],j,item)
            self.table.setItem(0,j,QtWidgets.QTableWidgetItem('{}'.format(total_size)))
