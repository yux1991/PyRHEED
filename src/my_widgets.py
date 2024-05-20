import matplotlib.pyplot as plt
import matplotlib as mpl
from PyQt6 import QtCore, QtWidgets, QtGui
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
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
        self.minSlider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.minSlider.setFixedWidth(300)
        self.minSlider.setMinimum(minimum)
        self.minSlider.setMaximum(maximum)
        self.minSlider.setValue(self.currentMin)
        self.minSlider.valueChanged.connect(self.min_changed)

        self.maxLabel = QtWidgets.QLabel(self.text+"_max = {:5.2f} ".format(self.currentMax*self.scale)+"("+unit+")")
        self.maxSlider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
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

class StartEndStep(QtWidgets.QWidget):

    def __init__(self,start,end,step):
        super(StartEndStep,self).__init__()
        self._start=start
        self._end = end
        self._step = step
        self.start_entry = QtWidgets.QLineEdit(str(self._start))
        self.end_entry = QtWidgets.QLineEdit(str(self._end))
        self.step_entry = QtWidgets.QLineEdit(str(self._step))
        self.grid = QtWidgets.QGridLayout(self)
        self.grid.addWidget(self.start_entry,0,0)
        self.grid.addWidget(self.end_entry,0,1)
        self.grid.addWidget(self.step_entry,0,2)

    def start(self):
        return float(self.start_entry.text())

    def end(self):
        return float(self.end_entry.text())

    def step(self):
        return float(self.step_entry.text())

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
            self.slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Vertical)
        elif direction == 'horizontal':
            self.slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.slider.setMinimum(int(minimum*scale))
        self.slider.setMaximum(int(maximum*scale))
        self.slider.setValue(int(value*self.scale))
        self.slider.valueChanged.connect(self.update_label)

        self.UIgrid = QtWidgets.QGridLayout()
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.ColorRole.Window, QtCore.Qt.GlobalColor.transparent)
        palette.setColor(QtGui.QPalette.ColorRole.WindowText,QtGui.QColor(color))
        if direction == 'vertical':
            if self.BG:
                self.label = QtWidgets.QLabel('\u00A0\u00A0'+self.name+'\u00A0BG\n({:3.2f})'.format(value))
            else:
                self.label = QtWidgets.QLabel('\u00A0\u00A0'+self.name+'{}\n({:3.2f})'.format(self.index,value))
            #self.label.setFixedWidth(35)
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
        self.slider.setValue(int(value*self.scale))

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

class LabelSpinBox(QtWidgets.QWidget):

    VALUE_CHANGED = QtCore.pyqtSignal(float,int)

    def __init__(self,min,max,initial,scale,text,unit='',index=-1):
        super(LabelSpinBox, self).__init__()
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
        self.valueSpinBox = QtWidgets.QSpinBox()
        self.valueSpinBox.setMinimum(min)
        self.valueSpinBox.setMaximum(max)
        self.valueSpinBox.setValue(int(initial*scale))
        self.valueSpinBox.setSingleStep(1)
        self.valueSpinBox.setSuffix(" x 10"+self.to_sup(int(np.log10(1/scale))))
        self.valueSpinBox.valueChanged.connect(self.value_changed)
        self.grid = QtWidgets.QGridLayout()
        self.grid.addWidget(self.label,0,0)
        self.grid.addWidget(self.valueSpinBox,0,1)
        self.grid.setContentsMargins(0,0,0,0)
        self.setLayout(self.grid)

    def to_sup(self,number):
        s = str(number)
        return ''.join(dict(zip('-0123456789','\u207b\u2070\xb9\xb2\xb3\u2074\u2075\u2076\u2077\u2078\u2079')).get(c,c) for c in s)

    def set(self,min,max,initial,scale):
        self.scale = scale
        self.min = min
        self.max = max
        self.valueSpinBox.setMinimum(min)
        self.valueSpinBox.setMaximum(max)
        self.valueSpinBox.setValue(int(initial*scale))
        self.value_changed(initial*scale)

    def reset(self):
        self.valueSpinBox.setMinimum(self.min)
        self.valueSpinBox.setMaximum(self.max)
        self.valueSpinBox.setValue(int(self.initial*self.scale))
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
        return self.valueSpinBox.value()/self.scale

    def set_value(self,value):
        self.valueSpinBox.setValue(int(value*self.scale))

    def get_index(self):
        return self.index

class LabelSlider(QtWidgets.QWidget):

    VALUE_CHANGED = QtCore.pyqtSignal(float,int)

    def __init__(self,min,max,initial,scale,text,unit='',orientation = QtCore.Qt.Orientation.Horizontal,index=-1):
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
        self.valueSlider.setValue(int(initial*scale))
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
        self.valueSlider.setValue(int(initial*scale))
        self.value_changed(initial*scale)

    def reset(self):
        self.valueSlider.setMinimum(self.min)
        self.valueSlider.setMaximum(self.max)
        self.valueSlider.setValue(int(self.initial*self.scale))
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
        self.valueSlider.setValue(int(value*self.scale))

    def get_index(self):
        return self.index

class LockableDoubleSlider(QtWidgets.QWidget):
    VALUE_CHANGED = QtCore.pyqtSignal(float,float,int)

    def __init__(self,minimum,maximum,scale,head,tail,text,unit='',lock = False,type='slider',index=-1):
        super(LockableDoubleSlider,self).__init__()
        self.currentMin, self.currentMax = int(head),int(tail)
        self.head = head
        self.tail = tail
        self.text = text
        self.scale = scale
        self.unit = unit
        self.lock = lock
        self.index = index
        self.type = type
        self._minimum = minimum
        self._maximum = maximum
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
        if self.type == 'slider':
            self.minSlider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        elif self.type == 'spinbox':
            self.minSlider = QtWidgets.QSpinBox()
            self.minSlider.setSingleStep(1)
            self.minSlider.setSuffix(" x 10"+self.to_sup(int(np.log10(1/scale))))
        self.minSlider.setMinimum(self._minimum)
        if self.lock:
            self.minSlider.setMaximum(0)
        else:
            self.minSlider.setMaximum(self._maximum)
        self.minSlider.setValue(int(self.currentMin*self.scale))
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
        if self.type == 'slider':
            self.maxSlider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        elif self.type == 'spinbox':
            self.maxSlider = QtWidgets.QSpinBox()
            self.maxSlider.setSingleStep(1)
            self.maxSlider.setSuffix(" x 10"+self.to_sup(int(np.log10(1/scale))))
        if self.lock:
            self.maxSlider.setMinimum(0)
        else:
            self.maxSlider.setMinimum(minimum)
        self.maxSlider.setMaximum(maximum)
        self.maxSlider.setValue(int(self.currentMax*self.scale))
        self.maxSlider.valueChanged.connect(self.max_changed)

        self.UIgrid = QtWidgets.QGridLayout()
        self.UIgrid.addWidget(self.minLabel,0,0)
        self.UIgrid.addWidget(self.minSlider,0,1)
        self.UIgrid.addWidget(self.maxLabel,1,0)
        self.UIgrid.addWidget(self.maxSlider,1,1)
        self.UIgrid.setContentsMargins(0,0,0,0)
        self.setLayout(self.UIgrid)

    def to_sup(self,number):
        s = str(number)
        return ''.join(dict(zip('-0123456789','\u207b\u2070\xb9\xb2\xb3\u2074\u2075\u2076\u2077\u2078\u2079')).get(c,c) for c in s)

    def reset(self):
        self.minSlider.setValue(int(self.head*self.scale))
        self.maxSlider.setValue(int(self.tail*self.scale))

    def set_maximum(self,value):
        if self.lock:
            self.minSlider.setMaximum(0)
        else:
            self.minSlider.setMaximum(value)
        self.maxSlider.setMaximum(value)

    def set_head(self,value):
        if not self.lock:
            self.minSlider.setValue(int(value*self.scale))

    def set_tail(self,value):
        if not self.lock:
            self.maxSlider.setValue(int(value*self.scale))

    def values(self):
        return self.currentMin, self.currentMax

    def min_changed(self):
        self.currentMin = self.minSlider.value()/self.scale
        if self.lock:
            if self.currentMin > self.currentMax:
                self.maxSlider.setValue(0)
                self.minSlider.setValue(0)
            else:
                self.maxSlider.setValue(int(-self.currentMin*self.scale))
        elif self.currentMin > self.currentMax:
            self.maxSlider.setValue(int(self.currentMin*self.scale))

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
                self.maxSlider.setValue(0)
                self.minSlider.setValue(0)
            else:
                self.minSlider.setValue(int(-self.currentMax*self.scale))
        elif self.currentMin > self.currentMax:
            self.minSlider.setValue(int(self.currentMax*self.scale))
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

    def set_locked(self,state):
        if state == 2:
            self.lock = True
        elif state == 0:
            self.lock = False
        if self.lock:
            value = abs(self.currentMax) + abs(self.currentMin)
            self.maxSlider.setValue(int(value*self.scale/2))
            self.minSlider.setValue(int(-value*self.scale/2))
            self.minSlider.setMaximum(0)
            self.maxSlider.setMinimum(0)
        else:
            self.maxSlider.setMinimum(self._minimum)
            self.minSlider.setMaximum(self._maximum)

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
        self.SB.setValue(int(self.size))
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

class IndexedPushButtonWithTag(QtWidgets.QPushButton):
    BUTTON_CLICKED = QtCore.pyqtSignal(int,str)

    def __init__(self,text,index,tag):
        super(IndexedPushButtonWithTag,self).__init__(text)
        self.index = index
        self.tag = tag
        self.clicked.connect(self.emit_signal)

    def emit_signal(self):
        self.BUTTON_CLICKED.emit(self.index, self.tag)


class InfoBoard(QtWidgets.QGroupBox):
    def __init__(self,title,index):
        super(InfoBoard,self).__init__(title)
        self.index = index
        self.lattice_constants_grid = QtWidgets.QGridLayout(self)
        self.lattice_constants_grid.setContentsMargins(10,5,5,10)
        self.lattice_constants_label = QtWidgets.QLabel("")
        self.lattice_constants_grid.addWidget(self.lattice_constants_label,0,0)

    def update(self,index,formula,a,b,c,alpha,beta,gamma):
        """This is an overload function"""
        if index == self.index:
            self.lattice_constants_label.setText("  Formula: "+formula+"\n  a = {:5.3f}, b = {:5.3f}, c = {:5.3f}\n  alpha = {:5.3f}(\u00B0), beta = {:5.3f}(\u00B0), gamma = {:5.3f}(\u00B0)". \
                                                 format(a,b,c,alpha,beta,gamma))

class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=15, height=12, dpi=400, pos=111, facecolor='white'):
        self.fig = Figure(figsize=(width, height), dpi=dpi, tight_layout=True, facecolor=facecolor)
        self.pos = pos
        self.axes = self.fig.add_subplot(self.pos)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,QtWidgets.QSizePolicy.Policy.Expanding,QtWidgets.QSizePolicy.Policy.Expanding)
        FigureCanvas.updateGeometry(self)
        mpl.rcParams['axes.linewidth'] = 0.4
        self.change_background(facecolor)

    def change_background(self, facecolor):
        if facecolor == 'white':
            mpl.rcParams['axes.labelcolor'] = 'black'
            mpl.rcParams['axes.titlecolor'] = 'black'
            mpl.rcParams['axes.edgecolor'] = 'black'
            mpl.rcParams['xtick.color'] = 'black'
            mpl.rcParams['ytick.color'] = 'black'
            mpl.rcParams['xtick.labelcolor'] = 'black'
            mpl.rcParams['ytick.labelcolor'] = 'black'
        elif facecolor == 'black':
            mpl.rcParams['axes.labelcolor'] = 'white'
            mpl.rcParams['axes.titlecolor'] = 'white'
            mpl.rcParams['axes.edgecolor'] = 'white'
            mpl.rcParams['xtick.color'] = 'white'
            mpl.rcParams['ytick.color'] = 'white'
            mpl.rcParams['xtick.labelcolor'] = 'white'
            mpl.rcParams['ytick.labelcolor'] = 'white'

    def clear(self):
        self.fig.clear()
        self.axes = self.fig.add_subplot(self.pos)

    def save_as_file(self,directory, name):
        self.fig.savefig(directory+name)

class DynamicalColorMap(QtWidgets.QWidget):

    UPDATE_LOG = QtCore.pyqtSignal(str)

    def __init__(self,parent,type,x,y,z,intensity,nkz,fontname,fontsize,colormap,showFWHM=False, log_scale = True, pos=111, appTheme='light', kwargs={}):
        super(DynamicalColorMap,self).__init__(parent)
        self.pos = pos
        self.appTheme = appTheme
        if self.appTheme == 'light':
            self.figure = MplCanvas(self,pos=self.pos,facecolor='white')
        elif self.appTheme == 'dark':
            self.figure = MplCanvas(self,pos=self.pos,facecolor='black')
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
        self.plot_IV = False
        self.minimum_log_intensity = -5
        self.TwoDimMappingWindow = QtWidgets.QWidget()
        self.kwargs = kwargs
        if 1 in self.intensity.shape[0:1]:
            self.plot_IV = True
            self.TwoDimMappingWindow.setWindowTitle('Simulated IV curve')
        else:
            self.plot_IV = False
            self.TwoDimMappingWindow.setWindowTitle('Simulated 2D reciprocal space map')
        self.TwoDimMappingWindowLayout = QtWidgets.QGridLayout(self.TwoDimMappingWindow)
        self.toolbar = NavigationToolbar(self.figure,self.TwoDimMappingWindow)
        self.TwoDimMappingWindowLayout.addWidget(self.figure,0,0, QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.TwoDimMappingWindowLayout.addWidget(self.toolbar,1,0, QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.TwoDimMappingWindow.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        if not self.kwargs.get('save_as_file', False):
            self.TwoDimMappingWindow.showMaximized()
        else:
            self.fontsize = self.kwargs.get('font_size',50)

    def toggle_dark_mode(self, mode):
        self.appTheme = mode
        self.TwoDimMappingWindowLayout.removeWidget(self.figure)
        self.TwoDimMappingWindowLayout.removeWidget(self.toolbar)
        del self.figure
        del self.toolbar
        if mode == 'light':
            self.figure = MplCanvas(self,pos=self.pos,facecolor='white')
        elif mode == 'dark':
            self.figure = MplCanvas(self,pos=self.pos,facecolor='black')
        self.toolbar = NavigationToolbar(self.figure,self.TwoDimMappingWindow)
        self.TwoDimMappingWindowLayout.addWidget(self.figure,0,0, QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.TwoDimMappingWindowLayout.addWidget(self.toolbar,1,0, QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.replot(self.type,self.x_linear,self.y_linear,self.z_linear,self.colormap,self.intensity,self.nkz)

    def show_plot(self):
        self.replot(self.type,self.x_linear,self.y_linear,self.z_linear,self.colormap,self.intensity,self.nkz)
        if self.kwargs.get('save_as_file', False):
            self.figure.save_as_file(self.kwargs['directory'], self.kwargs['name'])

    def refresh_fonts(self,fontname,fontsize):
        self.fontname = fontname
        self.fontsize = fontsize
        font_dict = {'fontname':self.fontname, 'fontsize':self.fontsize}
        plt.ion()
        if not self.plot_IV:
            if self.type == 'XY':
                if self.showFWHM:
                    self.figureText.set_visible(False)
                    self.figureText = self.figure.axes.text(self.min_x*0.96,self.max_y*0.8,"Average HWHM = {:5.4f} \u212B\u207B\u00B9\nHWHM Asymmetric Ratio = {:5.3f}". \
                                                            format(self.HWHM,self.ratio),color='white',fontsize=self.fontsize-5,bbox={'facecolor':'black','alpha':0.2,'pad':5})
                    self.csHM.set_alpha(1)
                self.figure.axes.set_xlabel(r'${\bf k}_{x}$ $(\AA^{-1})$',font_dict)
                self.figure.axes.set_ylabel(r'${\bf k}_{y}$ $(\AA^{-1})$',font_dict)
            elif self.type == 'XZ':
                self.figure.axes.set_title('Simulated 2D reciprocal space map\nKy = {:5.2f} (\u212B\u207B\u00B9)'. \
                                           format(self.y_linear[self.nkz]),fontsize = self.fontsize,pad=30)
                self.figure.axes.set_xlabel(r'${\bf k}_{x}$ $(\AA^{-1})$',font_dict)
                self.figure.axes.set_ylabel(r'${\bf k}_{z}$ $(\AA^{-1})$',font_dict)
            elif self.type == 'YZ':
                self.figure.axes.set_title('Simulated 2D reciprocal space map\nKx = {:5.2f} (\u212B\u207B\u00B9)'. \
                                           format(self.x_linear[self.nkz]),fontsize=self.fontsize,pad=30)
                self.figure.axes.set_xlabel(r'${\bf k}_{y}$ $(\AA^{-1})$',font_dict)
                self.figure.axes.set_ylabel(r'${\bf k}_{z}$ $(\AA^{-1})$',font_dict)
            self.figure.axes.set_aspect(1)
            self.figure.axes.set_frame_on(False)
            self.figure.axes.tick_params(width = 0.1, length = 1, which='both', labelsize=self.fontsize)
            if self.log_scale:
                self.cbar.ax.set_ylabel("Log Intensity",font_dict)
                self.cbar.set_ticks(np.linspace(self.log_min,self.log_max,self.log_max-self.log_min+1))
                self.cbar.set_ticklabels(list('$10^{{{}}}$'.format(i) for i in range(self.log_min,self.log_max+1,1)))
            else:
                self.cbar.ax.set_ylabel("Normalized Intensity",font_dict)
            self.cbar.ax.tick_params(width = 0.1, length = 1, labelsize=self.fontsize)
            self.cbar.outline.set_linewidth(0.1)
        else:
            self.figure.axes.set_xlabel(r'$K_{\perp}$ $(\AA^{-1})$',font_dict)
            if self.log_scale:
                self.figure.axes.set_ylabel('Log Intensity\n(arb. units)',font_dict)
            else:
                self.figure.axes.set_ylabel('Intensity\n(arb. units)',font_dict)
            self.figure.axes.tick_params(width = 0.1, length = 1, which='both', labelsize=self.fontsize)
            if self.pos == 211:
                self.fft_axes.set_xlabel(r'$R_{\perp}$ $(\AA)$',font_dict)
                self.fft_axes.set_ylabel('FFT Intensity\n(arb. units)',font_dict)
                self.fft_axes.tick_params(width = 0.1, length = 1, which='both', labelsize=self.fontsize)
        self.figure.draw()

    def refresh_FWHM(self,showFWHM):
        if showFWHM == self.showFWHM:
            pass
        else:
            self.showFWHM = showFWHM
        if self.type == 'XY':
            plt.ion()
            if not self.plot_IV:
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
                            w = np.sqrt((x0-2.27)**2+y0**2)
                            self.ratio = np.amax(w)/np.amin(w)
                            #self.FWHM = np.amax(w)+np.amin(w)
                            self.HWHM = np.amax(w)
                    self.figureText = self.figure.axes.text(self.min_x*0.96,self.max_y*0.8,"Average HWHM = {:5.4f} \u212B\u207B\u00B9\nHWHM Asymmetric Ratio = {:5.3f}". \
                                          format(self.HWHM,self.ratio),color='white',fontsize=self.fontsize-5,bbox={'facecolor':'black','alpha':0.2,'pad':5})
                    self.csHM.set_alpha(1)
                else:
                    try:
                        self.figureText.set_visible(False)
                        self.csHM.set_alpha(0)
                    except: pass
        self.figure.draw()

    def replot(self,type,x,y,z,colormap,intensity,nkz):
        #self.y_linear = x[190:309]
        #self.x_linear = y[380:499]
        self.y_linear = x
        self.x_linear = y
        self.z_linear = z
        self.colormap = colormap
        #self.intensity = intensity[380:499,190:309,:]
        self.intensity = intensity
        self.nkz = nkz
        self.type = type
        self.figure.clear()
        self.IV = None
        self.IV_line_width = 1
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
                if self.plot_IV:
                    self.UPDATE_LOG.emit('Invalid data. Please use YZ plot or XZ plot!')
                    QtCore.QCoreApplication.processEvents()
                else:
                    self.cs = self.figure.axes.contourf(self.x_linear,self.y_linear,np.clip(np.log10(matrix.T/max_intensity),self.log_min,self.log_max),200,cmap=self.colormap)
                    #from mpl_toolkits.mplot3d import axes3d, Axes3D
                    #fig, ax = plt.subplots(subplot_kw=dict(projection="3d"))
                    #surf_X, surf_Y = np.meshgrid(self.x_linear,self.y_linear)
                    #surf = ax.plot_surface(surf_X, surf_Y,np.clip(np.log10(matrix.T/max_intensity),self.log_min,self.log_max),linewidth=0, antialiased=False,cmap=self.colormap,rcount=200, ccount=200)
                    #plt.show()
            else:
                if self.plot_IV:
                    self.UPDATE_LOG.emit('Invalid data. Please use YZ plot or XZ plot!')
                    QtCore.QCoreApplication.processEvents()
                else:
                    self.cs = self.figure.axes.contourf(self.x_linear,self.y_linear,matrix.T/max_intensity,100,cmap=self.colormap)
                    #from mpl_toolkits.mplot3d import axes3d, Axes3D
                    #fig, ax = plt.subplots(subplot_kw=dict(projection="3d"))
                    #surf_X, surf_Y = np.meshgrid(self.x_linear,self.y_linear)
                    #surf = ax.plot_surface(surf_X, surf_Y,matrix.T/max_intensity,linewidth=0, antialiased=False,cmap=self.colormap,rcount=200, ccount=200)
                    #plt.show()
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
                if self.plot_IV:
                    self.UPDATE_LOG.emit('Plotting IV ...')
                    QtCore.QCoreApplication.processEvents()
                    self.IV = self.figure.axes.plot(self.z_linear,np.log10(matrix[0,:]/max_intensity),'r-',linewidth=self.IV_line_width)
                    if self.pos == 211:
                        self.fft_axes = self.figure.fig.add_subplot(212)
                        length = 100000
                        self.FFT = [np.fft.rfftfreq(length,(self.z_linear[1]-self.z_linear[0])/2/np.pi)[0:1000], abs(np.fft.rfft(matrix[0,:]/max_intensity,length))[0:1000]]
                        self.fft_axes.plot(self.FFT[0],self.FFT[1],'b-',linewidth=self.IV_line_width)
                else:
                    self.cs = self.figure.axes.contourf(self.x_linear,self.z_linear,np.clip(np.log10(matrix.T/max_intensity),self.log_min,self.log_max),200,cmap=self.colormap)
            else:
                if self.plot_IV:
                    self.UPDATE_LOG.emit('Plotting IV ...')
                    QtCore.QCoreApplication.processEvents()
                    self.IV = self.figure.axes.plot(self.z_linear,matrix[0,:]/max_intensity,'r-',linewidth=self.IV_line_width)
                    if self.pos == 211:
                        self.fft_axes = self.figure.fig.add_subplot(212)
                        length = 100000
                        self.FFT = [np.fft.rfftfreq(length,(self.z_linear[1]-self.z_linear[0])/2/np.pi)[0:1000], abs(np.fft.rfft(matrix[0,:]/max_intensity,length))[0:1000]]
                        self.fft_axes.plot(self.FFT[0],self.FFT[1],'b-',linewidth=self.IV_line_width)
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
                if self.plot_IV:
                    self.UPDATE_LOG.emit('Plotting IV ...')
                    QtCore.QCoreApplication.processEvents()
                    self.IV = self.figure.axes.plot(self.z_linear,np.log10(matrix[0,:]/max_intensity),'r-',linewidth=self.IV_line_width)
                    if self.pos == 211:
                        self.fft_axes = self.figure.fig.add_subplot(212)
                        length = 100000
                        self.FFT = [np.fft.rfftfreq(length,(self.z_linear[1]-self.z_linear[0])/2/np.pi)[0:1000], abs(np.fft.rfft(matrix[0,:]/max_intensity,length))[0:1000]]
                        self.fft_axes.plot(self.FFT[0],self.FFT[1],'b-',linewidth=self.IV_line_width)
                else:
                    self.cs = self.figure.axes.contourf(self.y_linear,self.z_linear,np.clip(np.log10(matrix.T/max_intensity),self.log_min,self.log_max),200,cmap=self.colormap)
            else:
                if self.plot_IV:
                    self.UPDATE_LOG.emit('Plotting IV ...')
                    QtCore.QCoreApplication.processEvents()
                    self.IV = self.figure.axes.plot(self.z_linear,matrix[0,:]/max_intensity,'r-',linewidth=self.IV_line_width)
                    if self.pos == 211:
                        self.fft_axes = self.figure.fig.add_subplot(212)
                        length = 100000
                        self.FFT = [np.fft.rfftfreq(length,(self.z_linear[1]-self.z_linear[0])/2/np.pi)[0:1000], abs(np.fft.rfft(matrix[0,:]/max_intensity,length))[0:1000]]
                        #self.FFT = [np.linspace(0,2*np.pi/(self.z_linear[1]-self.z_linear[0]),30001)[0:1000], abs(np.fft.rfft(matrix[0,:]/max_intensity,30000))[0:1000]]
                        self.fft_axes.plot(self.FFT[0],self.FFT[1],'b-',linewidth=self.IV_line_width)
                else:
                    self.cs = self.figure.axes.contourf(self.y_linear,self.z_linear,matrix.T/max_intensity,100,cmap=self.colormap)
        if not self.plot_IV:
            self.cbar = self.figure.fig.colorbar(self.cs,format='%.2f')
            self.refresh_FWHM(self.showFWHM)
            self.refresh_fonts(self.fontname,self.fontsize)
        if self.IV:
            self.refresh_fonts(self.fontname,self.fontsize)

    def save_FFT(self,path):
        try:
            output = open(path,mode='w')
            output.write('Time: \n')
            output.write(QtCore.QDateTime.currentDateTime().toString("MMMM d, yyyy  hh:mm:ss ap")+"\n\n")
            results = "\n".join(str(self.FFT[0][i])+'\t'+str(self.FFT[1][i]) for i in range(1000))
            output.write(results)
            output.close()
        except:
            pass

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

    def get_text(self):
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

        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok|QtWidgets.QDialogButtonBox.StandardButton.Cancel,\
                                                QtCore.Qt.Orientation.Horizontal)
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
