import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt5 import QtCore, QtWidgets, QtGui
import numpy as np

class DoubleSlider(QtWidgets.QWidget):
    VALUE_CHANGED = QtCore.pyqtSignal()

    def __init__(self,minimum,maximum,scale,head,tail,text,unit,direction='horizontal'):
        super(DoubleSlider,self).__init__()
        self.currentMin, self.currentMax = int(head/scale),int(tail/scale)
        self.text = text
        self.scale = scale
        self.unit = unit
        self.minLabel = QtWidgets.QLabel(self.text+"_min = {:5.2f} ".format(self.currentMin*self.scale)+"("+unit+")")
        self.minLabel.setFixedWidth(180)
        self.minSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.minSlider.setFixedWidth(300)
        self.minSlider.setMinimum(minimum)
        self.minSlider.setMaximum(maximum)
        self.minSlider.setValue(self.currentMin)
        self.minSlider.valueChanged.connect(self.min_changed)

        self.maxLabel = QtWidgets.QLabel(self.text+"_max = {:5.2f} ".format(self.currentMax*self.scale)+"("+unit+")")
        self.maxLabel.setFixedWidth(180)
        self.maxSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.maxSlider.setFixedWidth(300)
        self.maxSlider.setMinimum(minimum)
        self.maxSlider.setMaximum(maximum)
        self.maxSlider.setValue(self.currentMax)
        self.maxSlider.valueChanged.connect(self.max_changed)

        self.UIgrid = QtWidgets.QGridLayout()
        self.UIgrid.addWidget(self.minLabel,0,0)
        self.UIgrid.addWidget(self.minSlider,0,1)
        self.UIgrid.addWidget(self.maxLabel,1,0)
        self.UIgrid.addWidget(self.maxSlider,1,1)
        self.UIgrid.setContentsMargins(0,0,0,0)
        self.setLayout(self.UIgrid)

    def set_head(self,value):
        self.minSlider.setValue(int(value/self.scale))

    def set_tail(self,value):
        self.maxSlider.setValue(int(value/self.scale))

    def values(self):
        return self.currentMin*self.scale, self.currentMax*self.scale

    def min_changed(self):
        self.currentMin = self.minSlider.value()
        if self.currentMin > self.currentMax:
            self.maxSlider.setValue(self.currentMin)
        self.minLabel.setText(self.text+"_min = {:5.2f} ".format(self.currentMin*self.scale)+"("+self.unit+")")
        self.VALUE_CHANGED.emit()

    def max_changed(self):
        self.currentMax = self.maxSlider.value()
        if self.currentMin > self.currentMax:
            self.minSlider.setValue(self.currentMax)
        self.maxLabel.setText(self.text+"_max = {:5.2f} ".format(self.currentMax*self.scale)+"("+self.unit+")")
        self.VALUE_CHANGED.emit()

    def setEnabled(self,enable):
        self.minSlider.setEnabled(enable)
        self.maxSlider.setEnabled(enable)

class VerticalLabelSlider(QtWidgets.QWidget):
    VALUE_CHANGED = QtCore.pyqtSignal()
    def __init__(self,minimum,maximum,scale,value,name,index,BG=False,direction='vertical',color='black'):
        super(VerticalLabelSlider,self).__init__()
        self.name = name
        self.scale = scale
        self.index = index
        self.BG = BG
        self.currentValue = value
        self.direction = direction
        if direction == 'vertical':
            self.slider = QtWidgets.QSlider(QtCore.Qt.Vertical)
        elif direction == 'horizontal':
            self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setMinimum(minimum*scale)
        self.slider.setMaximum(maximum*scale)
        self.slider.setValue(value*self.scale)
        self.slider.valueChanged.connect(self.update_label)

        self.UIgrid = QtWidgets.QGridLayout()
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Window, QtCore.Qt.transparent)
        palette.setColor(QtGui.QPalette.WindowText,QtGui.QColor(color))
        if direction == 'vertical':
            if self.BG:
                self.label = QtWidgets.QLabel('\u00A0\u00A0'+self.name+'\u00A0BG\n({:3.2f})'.format(value))
            else:
                self.label = QtWidgets.QLabel('\u00A0\u00A0'+self.name+'{}\n({:3.2f})'.format(self.index,value))
            self.label.setFixedWidth(35)
            self.UIgrid.addWidget(self.slider,0,0)
            self.UIgrid.addWidget(self.label,1,0)
        elif direction == 'horizontal':
            self.label = QtWidgets.QLabel(self.name+'\u00A0({:3.2f})'.format(value))
            self.UIgrid.addWidget(self.label,0,0)
            self.UIgrid.addWidget(self.slider,0,1)
        self.label.setAutoFillBackground(True)
        self.label.setPalette(palette)
        self.UIgrid.setContentsMargins(0,0,0,0)
        self.setLayout(self.UIgrid)

    def value(self):
        return str(self.currentValue)

    def set_value(self,value):
        self.slider.setValue(value*self.scale)

    def update_label(self,value):
        self.currentValue = value/self.scale
        if self.direction == 'vertical':
            if self.BG:
                self.label.setText('\u00A0\u00A0'+self.name+'\u00A0BG\n({:3.2f})'.format(self.currentValue))
            else:
                self.label.setText('\u00A0\u00A0'+self.name+'{}\n({:3.2f})'.format(self.index,self.currentValue))
        elif self.direction == 'horizontal':
            self.label.setText(self.name+'\u00A0({:3.2f})'.format(self.currentValue))
        self.VALUE_CHANGED.emit()

class ColorPicker(QtWidgets.QWidget):

    COLOR_CHANGED = QtCore.pyqtSignal(str,str)

    def __init__(self,name,color,enableLabel=True):
        super(ColorPicker,self).__init__()
        self.color = color
        self.name = name
        self.label = QtWidgets.QLabel(self.name)
        self.PB = QtWidgets.QPushButton()
        self.PB.clicked.connect(self.change_color)
        self.set_color(self.color)
        self.grid = QtWidgets.QGridLayout(self)
        self.grid.setContentsMargins(0,0,0,0)
        if enableLabel:
            self.grid.addWidget(self.label,0,0,1,1)
        self.grid.addWidget(self.PB,0,1,1,1)

    def change_color(self):
        new_color = QtWidgets.QColorDialog.getColor(QtGui.QColor(self.color))
        self.color = new_color.name()
        self.set_color(self.color)
        self.COLOR_CHANGED.emit(self.name,self.color)

    def set_color(self,color):
        self.PB.setStyleSheet("background-color:"+color+"; border: none")
        self.color = color

    def get_color(self):
        return self.color

class LabelSlider(QtWidgets.QWidget):

    VALUE_CHANGED = QtCore.pyqtSignal(float,int)

    def __init__(self,min,max,initial,scale,text,unit='',orientation = QtCore.Qt.Horizontal,index=-1):
        super(LabelSlider, self).__init__()
        self.scale = scale
        self.label_text = text
        self.min = min
        self.max = max
        self.initial = initial
        self.unit = unit
        self.index = index
        if 1/self.scale >= 0.1:
            self.label = QtWidgets.QLabel(self.label_text+" = {:6.1f} ".format(initial)+self.unit)
        elif 1/self.scale >= 0.01:
            self.label = QtWidgets.QLabel(self.label_text+" = {:6.2f} ".format(initial)+self.unit)
        elif 1/self.scale >= 0.001:
            self.label = QtWidgets.QLabel(self.label_text+" = {:6.3f} ".format(initial)+self.unit)
        else:
            self.label = QtWidgets.QLabel(self.label_text+" = {:6.4f} ".format(initial)+self.unit)
        self.valueSlider = QtWidgets.QSlider(orientation)
        self.valueSlider.setMinimum(min)
        self.valueSlider.setMaximum(max)
        self.valueSlider.setValue(initial*scale)
        self.valueSlider.setTickInterval(1)
        self.valueSlider.valueChanged.connect(self.value_changed)
        self.grid = QtWidgets.QGridLayout()
        self.grid.addWidget(self.label,0,0)
        self.grid.addWidget(self.valueSlider,0,1)
        self.grid.setContentsMargins(0,0,0,0)
        self.setLayout(self.grid)

    def set(self,min,max,initial,scale):
        self.scale = scale
        self.min = min
        self.max = max
        self.valueSlider.setMinimum(min)
        self.valueSlider.setMaximum(max)
        self.valueSlider.setValue(initial*scale)
        self.value_changed(initial*scale)

    def reset(self):
        self.valueSlider.setMinimum(self.min)
        self.valueSlider.setMaximum(self.max)
        self.valueSlider.setValue(self.initial*self.scale)
        self.value_changed(self.initial*self.scale)

    def value_changed(self,value):
        if 1/self.scale >= 0.1:
            self.label.setText(self.label_text+" = {:6.1f} ".format(value/self.scale)+self.unit)
        elif 1/self.scale >= 0.01:
            self.label.setText(self.label_text+" = {:6.2f} ".format(value/self.scale)+self.unit)
        elif 1/self.scale >= 0.001:
            self.label.setText(self.label_text+" = {:6.3f} ".format(value/self.scale)+self.unit)
        elif 1/self.scale >= 0.0001:
            self.label.setText(self.label_text+" = {:6.4f} ".format(value/self.scale)+self.unit)
        else:
            self.label.setText(self.label_text+" = {:7.5f} ".format(value/self.scale)+self.unit)
        self.VALUE_CHANGED.emit(value/self.scale,self.index)

    def get_value(self):
        return self.valueSlider.value()/self.scale

    def set_value(self,value):
        self.valueSlider.setValue(value*self.scale)

    def get_index(self):
        return self.index

class LockableDoubleSlider(QtWidgets.QWidget):
    VALUE_CHANGED = QtCore.pyqtSignal(float,float,int)

    def __init__(self,minimum,maximum,scale,head,tail,text,unit='',lock = False,direction='horizontal',index=-1):
        super(LockableDoubleSlider,self).__init__()
        self.currentMin, self.currentMax = int(head),int(tail)
        self.head = head
        self.tail = tail
        self.text = text
        self.scale = scale
        self.unit = unit
        self.lock = lock
        self.index = index
        if self.unit == '':
            if 1/self.scale >=1:
                self.minLabel = QtWidgets.QLabel(self.text+"_min = {:2.0f} ".format(self.currentMin))
            elif 1/self.scale >=0.1:
                self.minLabel = QtWidgets.QLabel(self.text+"_min = {:3.1f} ".format(self.currentMin))
            elif 1/self.scale >=0.01:
                self.minLabel = QtWidgets.QLabel(self.text+"_min = {:4.2f} ".format(self.currentMin))
            elif 1/self.scale >=0.001:
                self.minLabel = QtWidgets.QLabel(self.text+"_min = {:5.3f} ".format(self.currentMin))
            elif 1/self.scale >=0.0001:
                self.minLabel = QtWidgets.QLabel(self.text+"_min = {:6.4f} ".format(self.currentMin))
        else:
            if 1/self.scale >=1:
                self.minLabel = QtWidgets.QLabel(self.text+"_min = {:2.0f} ".format(self.currentMin)+"("+unit+")")
            elif 1/self.scale >=0.1:
                self.minLabel = QtWidgets.QLabel(self.text+"_min = {:3.1f} ".format(self.currentMin)+"("+unit+")")
            elif 1/self.scale >=0.01:
                self.minLabel = QtWidgets.QLabel(self.text+"_min = {:4.2f} ".format(self.currentMin)+"("+unit+")")
            elif 1/self.scale >=0.001:
                self.minLabel = QtWidgets.QLabel(self.text+"_min = {:5.3f} ".format(self.currentMin)+"("+unit+")")
            elif 1/self.scale >=0.0001:
                self.minLabel = QtWidgets.QLabel(self.text+"_min = {:6.4f} ".format(self.currentMin)+"("+unit+")")
        self.minLabel.setFixedWidth(180)
        self.minSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.minSlider.setMinimum(minimum)
        if self.lock:
            self.minSlider.setMaximum(0)
        else:
            self.minSlider.setMaximum(maximum)
        self.minSlider.setValue(self.currentMin*self.scale)
        self.minSlider.valueChanged.connect(self.min_changed)

        if self.unit == '':
            if 1/self.scale >=1:
                self.maxLabel = QtWidgets.QLabel(self.text+"_max = {:2.0f} ".format(self.currentMax))
            elif 1/self.scale >=0.1:
                self.maxLabel = QtWidgets.QLabel(self.text+"_max = {:3.1f} ".format(self.currentMax))
            elif 1/self.scale >=0.01:
                self.maxLabel = QtWidgets.QLabel(self.text+"_max = {:4.2f} ".format(self.currentMax))
            elif 1/self.scale >=0.001:
                self.maxLabel = QtWidgets.QLabel(self.text+"_max = {:5.3f} ".format(self.currentMax))
            elif 1/self.scale >=0.0001:
                self.maxLabel = QtWidgets.QLabel(self.text+"_max = {:6.4f} ".format(self.currentMax))
        else:
            if 1/self.scale >=1:
                self.maxLabel = QtWidgets.QLabel(self.text+"_max = {:2.0f} ".format(self.currentMax)+"("+unit+")")
            elif 1/self.scale >=0.1:
                self.maxLabel = QtWidgets.QLabel(self.text+"_max = {:3.1f} ".format(self.currentMax)+"("+unit+")")
            elif 1/self.scale >=0.01:
                self.maxLabel = QtWidgets.QLabel(self.text+"_max = {:4.2f} ".format(self.currentMax)+"("+unit+")")
            elif 1/self.scale >=0.001:
                self.maxLabel = QtWidgets.QLabel(self.text+"_max = {:5.3f} ".format(self.currentMax)+"("+unit+")")
            elif 1/self.scale >=0.0001:
                self.maxLabel = QtWidgets.QLabel(self.text+"_max = {:6.4f} ".format(self.currentMax)+"("+unit+")")
        self.maxLabel.setFixedWidth(180)
        self.maxSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        if self.lock:
            self.maxSlider.setMinimum(0)
        else:
            self.maxSlider.setMinimum(minimum)
        self.maxSlider.setMaximum(maximum)
        self.maxSlider.setValue(self.currentMax*self.scale)
        self.maxSlider.valueChanged.connect(self.max_changed)

        self.UIgrid = QtWidgets.QGridLayout()
        self.UIgrid.addWidget(self.minLabel,0,0)
        self.UIgrid.addWidget(self.minSlider,0,1)
        self.UIgrid.addWidget(self.maxLabel,1,0)
        self.UIgrid.addWidget(self.maxSlider,1,1)
        self.UIgrid.setContentsMargins(0,0,0,0)
        self.setLayout(self.UIgrid)

    def reset(self):
        self.minSlider.setValue(self.head*self.scale)
        self.maxSlider.setValue(self.tail*self.scale)

    def set_maximum(self,value):
        if self.lock:
            self.minSlider.setMaximum(0)
        else:
            self.minSlider.setMaximum(value)
        self.maxSlider.setMaximum(value)

    def set_head(self,value):
        if not self.lock:
            self.minSlider.setValue(np.round(value*self.scale,0))

    def set_tail(self,value):
        if not self.lock:
            self.maxSlider.setValue(np.round(value*self.scale,0))

    def values(self):
        return self.currentMin, self.currentMax

    def min_changed(self):
        self.currentMin = self.minSlider.value()/self.scale
        if self.lock:
            if self.currentMin > self.currentMax:
                self.maxSlider.setValue(0)
            else:
                self.maxSlider.setValue(-self.currentMin*self.scale)
        elif self.currentMin > self.currentMax:
            self.maxSlider.setValue(self.currentMin*self.scale)

        if self.unit == '':
            if 1/self.scale >=1:
                self.minLabel.setText(self.text+"_min = {:2.0f} ".format(self.currentMin))
            elif 1/self.scale >=0.1:
                self.minLabel.setText(self.text+"_min = {:3.1f} ".format(self.currentMin))
            elif 1/self.scale >=0.01:
                self.minLabel.setText(self.text+"_min = {:4.2f} ".format(self.currentMin))
            elif 1/self.scale >=0.001:
                self.minLabel.setText(self.text+"_min = {:5.3f} ".format(self.currentMin))
            elif 1/self.scale >=0.0001:
                self.minLabel.setText(self.text+"_min = {:6.4f} ".format(self.currentMin))
        else:
            if 1/self.scale >=1:
                self.minLabel.setText(self.text+"_min = {:2.0f} ".format(self.currentMin)+"("+self.unit+")")
            elif 1/self.scale >=0.1:
                self.minLabel.setText(self.text+"_min = {:3.1f} ".format(self.currentMin)+"("+self.unit+")")
            elif 1/self.scale >=0.01:
                self.minLabel.setText(self.text+"_min = {:4.2f} ".format(self.currentMin)+"("+self.unit+")")
            elif 1/self.scale >=0.001:
                self.minLabel.setText(self.text+"_min = {:5.3f} ".format(self.currentMin)+"("+self.unit+")")
            elif 1/self.scale >=0.0001:
                self.minLabel.setText(self.text+"_min = {:6.4f} ".format(self.currentMin)+"("+self.unit+")")
        self.VALUE_CHANGED.emit(np.round(self.currentMin,2),np.round(self.currentMax,2),self.index)

    def max_changed(self):
        self.currentMax = self.maxSlider.value()/self.scale
        if self.lock:
            if self.currentMin > self.currentMax:
                self.minSlider.setValue(0)
            else:
                self.minSlider.setValue(-self.currentMax*self.scale)
        elif self.currentMin > self.currentMax:
            self.minSlider.setValue(self.currentMax*self.scale)
        if self.unit == '':
            if 1/self.scale >=1:
                self.maxLabel.setText(self.text+"_max = {:2.0f} ".format(self.currentMax))
            elif 1/self.scale >=0.1:
                self.maxLabel.setText(self.text+"_max = {:3.1f} ".format(self.currentMax))
            elif 1/self.scale >=0.01:
                self.maxLabel.setText(self.text+"_max = {:4.2f} ".format(self.currentMax))
            elif 1/self.scale >=0.001:
                self.maxLabel.setText(self.text+"_max = {:5.3f} ".format(self.currentMax))
            elif 1/self.scale >=0.0001:
                self.maxLabel.setText(self.text+"_max = {:6.4f} ".format(self.currentMax))
        else:
            if 1/self.scale >=1:
                self.maxLabel.setText(self.text+"_max = {:2.0f} ".format(self.currentMax)+"("+self.unit+")")
            elif 1/self.scale >=0.1:
                self.maxLabel.setText(self.text+"_max = {:3.1f} ".format(self.currentMax)+"("+self.unit+")")
            elif 1/self.scale >=0.01:
                self.maxLabel.setText(self.text+"_max = {:4.2f} ".format(self.currentMax)+"("+self.unit+")")
            elif 1/self.scale >=0.001:
                self.maxLabel.setText(self.text+"_max = {:5.3f} ".format(self.currentMax)+"("+self.unit+")")
            elif 1/self.scale >=0.0001:
                self.maxLabel.setText(self.text+"_max = {:6.4f} ".format(self.currentMax)+"("+self.unit+")")
        self.VALUE_CHANGED.emit(np.round(self.currentMin,2),np.round(self.currentMax,2),self.index)

    def setEnabled(self,enable):
        """This is an overload function"""
        self.minSlider.setEnabled(enable)
        self.maxSlider.setEnabled(enable)

class IndexedColorPicker(QtWidgets.QWidget):

    COLOR_CHANGED = QtCore.pyqtSignal(str,str,int)
    SIZE_CHANGED = QtCore.pyqtSignal(str,float,int)

    def __init__(self,name,color,size=20,index=-1):
        super(IndexedColorPicker,self).__init__()
        self.color = color
        self.name = name
        self.size = size
        self.index = index
        self.label = QtWidgets.QLabel(self.name)
        self.label.setFixedWidth(20)
        self.PB = QtWidgets.QPushButton()
        self.PB.clicked.connect(self.change_color)
        self.SB = QtWidgets.QSpinBox()
        self.SB.setMinimum(0)
        self.SB.setMaximum(100)
        self.SB.setSingleStep(1)
        self.SB.setValue(self.size)
        self.SB.valueChanged.connect(self.change_size)
        self.set_color(self.color)
        self.grid = QtWidgets.QGridLayout(self)
        self.grid.addWidget(self.label,0,0)
        self.grid.addWidget(self.PB,0,1)
        self.grid.addWidget(self.SB,0,2)

    def change_color(self):
        new_color = QtWidgets.QColorDialog.getColor(QtGui.QColor(self.color))
        self.color = new_color.name()
        self.set_color(self.color)
        self.COLOR_CHANGED.emit(self.name,self.color,self.index)

    def change_size(self,text):
        self.size = int(text)
        self.SIZE_CHANGED.emit(self.name, self.size/100,self.index)

    def get_size(self):
        return self.size

    def set_color(self,color):
        self.PB.setStyleSheet("background-color:"+color)
        self.color = color

    def get_color(self):
        return self.color

class IndexedComboBox(QtWidgets.QComboBox):
    TEXT_CHANGED = QtCore.pyqtSignal(str,int)

    def __init__(self,index):
        super(IndexedComboBox,self).__init__()
        self.index = index
        self.currentTextChanged.connect(self.change_text)

    def change_text(self,text):
        self.TEXT_CHANGED.emit(text,self.index)

class IndexedPushButton(QtWidgets.QPushButton):
    BUTTON_CLICKED = QtCore.pyqtSignal(int)

    def __init__(self,text,index):
        super(IndexedPushButton,self).__init__(text)
        self.index = index
        self.clicked.connect(self.emit_signal)

    def emit_signal(self):
        self.BUTTON_CLICKED.emit(self.index)

class InfoBoard(QtWidgets.QGroupBox):
    def __init__(self,title,index):
        super(InfoBoard,self).__init__(title)
        self.index = index
        self.lattice_constants_grid = QtWidgets.QGridLayout(self)
        self.lattice_constants_grid.setContentsMargins(10,5,5,10)
        self.lattice_constants_label = QtWidgets.QLabel("")
        self.lattice_constants_grid.addWidget(self.lattice_constants_label,0,0)
        self.setStyleSheet('QGroupBox::title {color:blue;}')

    def update(self,index,formula,a,b,c,alpha,beta,gamma):
        """This is an overload function"""
        if index == self.index:
            self.lattice_constants_label.setText("  Formula: "+formula+"\n  a = {:5.3f}, b = {:5.3f}, c = {:5.3f}\n  alpha = {:5.3f}(\u00B0), beta = {:5.3f}(\u00B0), gamma = {:5.3f}(\u00B0)". \
                                                 format(a,b,c,alpha,beta,gamma))

class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def clear(self):
        self.fig.clear()
        self.axes = self.fig.add_subplot(111)

class DynamicalColorMap(QtWidgets.QWidget):
    def __init__(self,parent,type,x,y,z,intensity,nkz,fontname,fontsize,colormap,showFWHM=False, log_scale = True):
        super(DynamicalColorMap,self).__init__(parent)
        self.figure = MplCanvas(self)
        self.x_linear = x
        self.y_linear = y
        self.z_linear = z
        self.intensity = intensity
        self.nkz = nkz
        self.showFWHM = showFWHM
        self.log_scale = log_scale
        self.type = type
        self.fontname = fontname
        self.fontsize = fontsize
        self.colormap = colormap
        self.minimum_log_intensity = -6
        self.TwoDimMappingWindow = QtWidgets.QWidget()
        self.TwoDimMappingWindow.setWindowTitle('Summary of Broadening Analysis')
        self.TwoDimMappingWindowLayout = QtWidgets.QGridLayout(self.TwoDimMappingWindow)
        self.toolbar = NavigationToolbar(self.figure,self.TwoDimMappingWindow)
        self.TwoDimMappingWindowLayout.addWidget(self.figure,0,0)
        self.TwoDimMappingWindowLayout.addWidget(self.toolbar,1,0)
        self.TwoDimMappingWindow.setWindowModality(QtCore.Qt.WindowModal)
        self.TwoDimMappingWindow.setMinimumSize(1000,800)
        self.TwoDimMappingWindow.show()

    def show_plot(self):
        self.replot(self.type,self.x_linear,self.y_linear,self.z_linear,self.colormap,self.intensity,self.nkz)

    def refresh_fonts(self,fontname,fontsize):
        self.fontname = fontname
        self.fontsize = fontsize
        plt.ion()
        if self.type == 'XY':
            if self.showFWHM:
                self.figureText.set_visible(False)
                self.figureText = self.figure.axes.text(self.min_x*0.96,self.max_y*0.8,"Average FWHM = {:5.4f} \u212B\u207B\u00B9\nFWHM Asymmetric Ratio = {:5.3f}". \
                                                        format(self.FWHM,self.ratio),color='white',fontsize=self.fontsize-5,bbox={'facecolor':'black','alpha':0.2,'pad':5})
                self.csHM.set_alpha(1)
            self.figure.axes.set_title('Simulated 2D reciprocal space map\nKz = {:5.2f} (\u212B\u207B\u00B9)'.\
               format(self.z_linear[self.nkz]),fontsize=self.fontsize,pad=30)
            self.figure.axes.set_xlabel(r'$K_{x}$ $(\AA^{-1})$',fontname=self.fontname,fontsize=self.fontsize)
            self.figure.axes.set_ylabel(r'$K_{y}$ $(\AA^{-1})$',fontname=self.fontname,fontsize=self.fontsize)
        elif self.type == 'XZ':
            self.figure.axes.set_title('Simulated 2D reciprocal space map\nKy = {:5.2f} (\u212B\u207B\u00B9)'. \
                                       format(self.y_linear[self.nkz]),fontsize=self.fontsize,pad=30)
            self.figure.axes.set_xlabel(r'$K_{x}$ $(\AA^{-1})$',fontname=self.fontname,fontsize=self.fontsize)
            self.figure.axes.set_ylabel(r'$K_{z}$ $(\AA^{-1})$',fontname=self.fontname,fontsize=self.fontsize)
        elif self.type == 'YZ':
            self.figure.axes.set_title('Simulated 2D reciprocal space map\nKx = {:5.2f} (\u212B\u207B\u00B9)'. \
                                       format(self.x_linear[self.nkz]),fontsize=self.fontsize,pad=30)
            self.figure.axes.set_xlabel(r'$K_{y}$ $(\AA^{-1})$',fontname=self.fontname,fontsize=self.fontsize)
            self.figure.axes.set_ylabel(r'$K_{z}$ $(\AA^{-1})$',fontname=self.fontname,fontsize=self.fontsize)
        self.figure.axes.set_aspect(1)
        self.figure.axes.tick_params(which='both', labelsize=self.fontsize)
        if self.log_scale:
            self.cbar.ax.set_ylabel("Log Intensity",fontname=self.fontname,fontsize=self.fontsize)
            self.cbar.set_ticks(np.linspace(self.log_min,self.log_max,self.log_max-self.log_min+1))
            self.cbar.set_ticklabels(list('$10^{{{}}}$'.format(i) for i in range(self.log_min,self.log_max+1,1)))
        else:
            self.cbar.ax.set_ylabel("Normalized Intensity",fontname=self.fontname,fontsize=self.fontsize)
        self.cbar.ax.tick_params(labelsize=self.fontsize)
        self.figure.draw()

    def refresh_FWHM(self,showFWHM):
        if showFWHM == self.showFWHM:
            pass
        else:
            self.showFWHM = showFWHM
        if self.type == 'XY':
            plt.ion()
            if self.showFWHM:
                matrix = self.intensity[:,:,self.nkz]
                max_intensity = np.amax(np.amax(matrix))
                self.min_x = np.amin(self.x_linear)
                self.max_y = np.amax(self.y_linear)
                self.csHM = self.figure.axes.contour(self.x_linear,self.y_linear,matrix.T/max_intensity,levels=[0.5],colors=['black'],linestyles='dashed',linewidths=2)
                self.FWHM = 1.0
                self.ratio = 1.0
                for collection in self.csHM.collections:
                    path = collection.get_paths()
                    for item in path:
                        x0 = item.vertices[:,0]
                        y0 = item.vertices[:,1]
                        w = np.sqrt(x0**2+y0**2)
                        self.ratio = np.amax(w)/np.amin(w)
                        self.FWHM = np.amax(w)+np.amin(w)
                self.figureText = self.figure.axes.text(self.min_x*0.96,self.max_y*0.8,"Average FWHM = {:5.4f} \u212B\u207B\u00B9\nFWHM Asymmetric Ratio = {:5.3f}". \
                                      format(self.FWHM,self.ratio),color='white',fontsize=self.fontsize-5,bbox={'facecolor':'black','alpha':0.2,'pad':5})
                self.csHM.set_alpha(1)
            else:
                try:
                    self.figureText.set_visible(False)
                    self.csHM.set_alpha(0)
                except: pass
        self.figure.draw()

    def replot(self,type,x,y,z,colormap,intensity,nkz):
        self.x_linear = x
        self.y_linear = y
        self.z_linear = z
        self.colormap = colormap
        self.intensity = intensity
        self.nkz = nkz
        self.type = type
        self.figure.clear()
        if self.type == 'XY':
            matrix = self.intensity[:,:,self.nkz]
            max_intensity = np.amax(np.amax(matrix))
            if self.log_scale:
                self.log_max = 1
                int_min = np.amin(np.amin(matrix/max_intensity))
                if int_min == 0:
                    self.log_min = self.minimum_log_intensity
                else:
                    self.log_min = max(int(np.log10(int_min)),self.minimum_log_intensity)
                self.cs = self.figure.axes.contourf(self.x_linear,self.y_linear,np.clip(np.log10(matrix.T/max_intensity),self.log_min,self.log_max),200,cmap=self.colormap)
            else:
                self.cs = self.figure.axes.contourf(self.x_linear,self.y_linear,matrix.T/max_intensity,100,cmap=self.colormap)
        elif self.type == 'XZ':
            matrix = self.intensity[:,self.nkz,:]
            max_intensity = np.amax(np.amax(matrix))
            if self.log_scale:
                self.log_max = 1
                int_min = np.amin(np.amin(matrix/max_intensity))
                if int_min == 0:
                    self.log_min = self.minimum_log_intensity
                else:
                    self.log_min = max(int(np.log10(int_min)),self.minimum_log_intensity)
                self.cs = self.figure.axes.contourf(self.x_linear,self.z_linear,np.clip(np.log10(matrix.T/max_intensity),self.log_min,self.log_max),200,cmap=self.colormap)
            else:
                self.cs = self.figure.axes.contourf(self.x_linear,self.z_linear,matrix.T/max_intensity,100,cmap=self.colormap)
        elif self.type == 'YZ':
            matrix = self.intensity[self.nkz,:,:]
            max_intensity = np.amax(np.amax(matrix))
            if self.log_scale:
                self.log_max = 1
                int_min = np.amin(np.amin(matrix/max_intensity))
                if int_min == 0:
                    self.log_min = self.minimum_log_intensity
                else:
                    self.log_min = max(int(np.log10(int_min)),self.minimum_log_intensity)
                self.cs = self.figure.axes.contourf(self.y_linear,self.z_linear,np.clip(np.log10(matrix.T/max_intensity),self.log_min,self.log_max),200,cmap=self.colormap)
            else:
                self.cs = self.figure.axes.contourf(self.y_linear,self.z_linear,matrix.T/max_intensity,100,cmap=self.colormap)
        self.cbar = self.figure.fig.colorbar(self.cs,format='%.2f')
        self.refresh_FWHM(self.showFWHM)
        self.refresh_fonts(self.fontname,self.fontsize)

    def refresh_colormap(self,colormap):
        self.colormap = colormap
        self.replot(self.type,self.x_linear,self.y_linear,self.z_linear,self.colormap,self.intensity,self.nkz)


class LabelLineEdit(QtWidgets.QWidget):

    ERROR = QtCore.pyqtSignal(str)
    VALUE_CHANGED = QtCore.pyqtSignal(str,float)

    def __init__(self,label,width,text,digit=1,unit=''):
        super(LabelLineEdit, self).__init__()
        self.label_text = label
        self.label_width = width
        self.text = text
        self.unit = unit
        self.digit = digit
        if not self.unit == '':
            self.label = QtWidgets.QLabel(self.label_text+' ('+self.unit+')')
        else:
            self.label = QtWidgets.QLabel(self.label_text)
        self.label.setFixedWidth(self.label_width)
        self.line = QtWidgets.QLineEdit()
        self.line.textEdited.connect(self.update_text)
        self.line.setText(self.text)
        self.grid = QtWidgets.QGridLayout()
        self.grid.addWidget(self.label,0,0)
        self.grid.addWidget(self.line,0,1)
        self.grid.setContentsMargins(0,0,0,0)
        self.setLayout(self.grid)

    def update_text(self,text):
        try:
            self.VALUE_CHANGED.emit(self.label_text,float(text))
        except:
            self.ERROR.emit("Wrong input!")

    def set_value(self,value):
        self.line.setText(str(np.round(value,self.digit)))

    def value(self):
        return float(self.line.text())

    def text(self):
        return self.line.text()

class LabelMultipleLineEdit(QtWidgets.QWidget):

    ERROR = QtCore.pyqtSignal(str)
    VALUE_CHANGED = QtCore.pyqtSignal(str,list)

    def __init__(self,number,label,width,text,unit=''):
        super(LabelMultipleLineEdit, self).__init__()
        self.number = number
        self.label_text = label
        self.label_width = width
        self.text = text
        self.unit = unit
        if not self.unit == '':
            self.label = QtWidgets.QLabel(self.label_text+' ('+self.unit+')')
        else:
            self.label = QtWidgets.QLabel(self.label_text)
        self.label.setFixedWidth(self.label_width)
        self.grid = QtWidgets.QGridLayout()
        self.grid.addWidget(self.label,0,0)
        self.grid.setContentsMargins(0,0,0,0)
        self.setLayout(self.grid)
        self.line_list = []
        for i in range(self.number):
            line = QtWidgets.QLineEdit()
            line.textEdited.connect(self.update_text)
            line.setText(self.text[i])
            self.line_list.append(line)
            self.grid.addWidget(line,0,i+1)

    def update_text(self,text):
        try:
            text_list = []
            for i,line in enumerate(self.line_list):
                text_list.append(float(line.text()))
            self.VALUE_CHANGED.emit(self.label_text,text_list)
        except:
            self.ERROR.emit("Wrong input!")

    def set_values(self,values):
        for i,line in enumerate(self.line_list):
            line.setText(str(np.round(values[i],1)))

    def values(self):
        text_list = []
        for i,line in enumerate(self.line_list):
            text_list.append(float(line.text()))
        return text_list

class MultipleInputDialog(QtWidgets.QDialog):

    def __init__(self):
        super(MultipleInputDialog,self).__init__()

    def getItems(self,*args):
        self.form = QtWidgets.QFormLayout()
        self.number_of_inputs = len(args)
        self.widget_list = []
        self.label_list = []
        self.type_list = []
        for count, dict in enumerate(args):
            self.type_list.append(dict['type'])
            self.label_list.append(dict['label'])
            if dict['type'] == 'LineEdit':
                self.widget_list.append(QtWidgets.QLineEdit(dict['content']))
            elif dict['type'] == 'SpinBox':
                self.widget_list.append(QtWidgets.QSpinBox())
                self.widget_list[-1].setMinimum(dict['content']['minimum'])
                self.widget_list[-1].setMaximum(dict['content']['maximum'])
                self.widget_list[-1].setSingleStep(dict['content']['step'])
                self.widget_list[-1].setValue(dict['content']['value'])
            elif dict['type'] == 'ComboBox':
                self.widget_list.append(QtWidgets.QComboBox())
                self.widget_list[-1].addItems(dict['content'])
            self.form.addRow(self.label_list[-1],self.widget_list[-1])

        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok|QtWidgets.QDialogButtonBox.Cancel,\
                                                QtCore.Qt.Horizontal)
        self.form.addRow(button_box)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        self.setLayout(self.form)
        return self.exec()

    def exec(self):
        code = super(MultipleInputDialog,self).exec()
        if code == 1:
            return_dict = {}
            for i in range(self.number_of_inputs):
                if self.type_list[i] == 'LineEdit':
                    return_dict[self.label_list[i]] = self.widget_list[i].text()
                elif self.type_list[i] == 'SpinBox':
                    return_dict[self.label_list[i]] = str(self.widget_list[i].value())
                elif self.type_list[i] == 'ComboBox':
                    return_dict[self.label_list[i]] = self.widget_list[i].currentText()
            return return_dict
        elif code == 0:
            return {}
