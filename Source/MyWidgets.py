from PyQt5 import QtCore, QtWidgets, QtGui
from matplotlib.figure import Figure
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

class DoubleSlider(QtWidgets.QWidget):
    valueChanged = QtCore.pyqtSignal()

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
        self.minSlider.valueChanged.connect(self.minChanged)

        self.maxLabel = QtWidgets.QLabel(self.text+"_max = {:5.2f} ".format(self.currentMax*self.scale)+"("+unit+")")
        self.maxLabel.setFixedWidth(180)
        self.maxSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.maxSlider.setFixedWidth(300)
        self.maxSlider.setMinimum(minimum)
        self.maxSlider.setMaximum(maximum)
        self.maxSlider.setValue(self.currentMax)
        self.maxSlider.valueChanged.connect(self.maxChanged)

        self.UIgrid = QtWidgets.QGridLayout()
        self.UIgrid.addWidget(self.minLabel,0,0)
        self.UIgrid.addWidget(self.minSlider,0,1)
        self.UIgrid.addWidget(self.maxLabel,1,0)
        self.UIgrid.addWidget(self.maxSlider,1,1)
        self.UIgrid.setContentsMargins(0,0,0,0)
        self.setLayout(self.UIgrid)

    def setHead(self,value):
        self.minSlider.setValue(int(value/self.scale))

    def setTail(self,value):
        self.maxSlider.setValue(int(value/self.scale))

    def values(self):
        return self.currentMin*self.scale, self.currentMax*self.scale

    def minChanged(self):
        self.currentMin = self.minSlider.value()
        if self.currentMin > self.currentMax:
            self.maxSlider.setValue(self.currentMin)
        self.minLabel.setText(self.text+"_min = {:5.2f} ".format(self.currentMin*self.scale)+"("+self.unit+")")
        self.valueChanged.emit()

    def maxChanged(self):
        self.currentMax = self.maxSlider.value()
        if self.currentMin > self.currentMax:
            self.minSlider.setValue(self.currentMax)
        self.maxLabel.setText(self.text+"_max = {:5.2f} ".format(self.currentMax*self.scale)+"("+self.unit+")")
        self.valueChanged.emit()

    def setEnabled(self,enable):
        self.minSlider.setEnabled(enable)
        self.maxSlider.setEnabled(enable)

class VerticalLabelSlider(QtWidgets.QWidget):
    valueChanged = QtCore.pyqtSignal()
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
        self.slider.valueChanged.connect(self.updateLabel)

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

    def setValue(self,value):
        self.slider.setValue(value*self.scale)

    def updateLabel(self,value):
        self.currentValue = value/self.scale
        if self.direction == 'vertical':
            if self.BG:
                self.label.setText('\u00A0\u00A0'+self.name+'\u00A0BG\n({:3.2f})'.format(self.currentValue))
            else:
                self.label.setText('\u00A0\u00A0'+self.name+'{}\n({:3.2f})'.format(self.index,self.currentValue))
        elif self.direction == 'horizontal':
            self.label.setText(self.name+'\u00A0({:3.2f})'.format(self.currentValue))
        self.valueChanged.emit()

class ColorPicker(QtWidgets.QWidget):

    colorChanged = QtCore.pyqtSignal(str,str)

    def __init__(self,name,color,enableLabel=True):
        super(ColorPicker,self).__init__()
        self.color = color
        self.name = name
        self.label = QtWidgets.QLabel(self.name)
        self.PB = QtWidgets.QPushButton()
        self.PB.clicked.connect(self.changeColor)
        self.setColor(self.color)
        self.grid = QtWidgets.QGridLayout(self)
        self.grid.setContentsMargins(0,0,0,0)
        if enableLabel:
            self.grid.addWidget(self.label,0,0,1,1)
        self.grid.addWidget(self.PB,0,1,1,1)

    def changeColor(self):
        new_color = QtWidgets.QColorDialog.getColor(QtGui.QColor(self.color))
        self.color = new_color.name()
        self.setColor(self.color)
        self.colorChanged.emit(self.name,self.color)

    def setColor(self,color):
        self.PB.setStyleSheet("background-color:"+color)
        self.color = color

    def getColor(self):
        return self.color

class LabelSlider(QtWidgets.QWidget):

    valueChanged = QtCore.pyqtSignal(float,int)

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
        self.valueChanged.emit(value/self.scale,self.index)

    def getValue(self):
        return self.valueSlider.value()/self.scale

    def setValue(self,value):
        self.valueSlider.setValue(value*self.scale)

    def getIndex(self):
        return self.index

class LockableDoubleSlider(QtWidgets.QWidget):
    valueChanged = QtCore.pyqtSignal(float,float,int)

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
        self.minSlider.valueChanged.connect(self.minChanged)

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
        self.maxSlider.valueChanged.connect(self.maxChanged)

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

    def setMaximum(self,value):
        if self.lock:
            self.minSlider.setMaximum(0)
        else:
            self.minSlider.setMaximum(value)
        self.maxSlider.setMaximum(value)

    def setHead(self,value):
        if not self.lock:
            self.minSlider.setValue(np.round(value*self.scale,0))

    def setTail(self,value):
        if not self.lock:
            self.maxSlider.setValue(np.round(value*self.scale,0))

    def values(self):
        return self.currentMin, self.currentMax

    def minChanged(self):
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
        self.valueChanged.emit(np.round(self.currentMin,2),np.round(self.currentMax,2),self.index)

    def maxChanged(self):
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
        self.valueChanged.emit(np.round(self.currentMin,2),np.round(self.currentMax,2),self.index)

    def setEnabled(self,enable):
        self.minSlider.setEnabled(enable)
        self.maxSlider.setEnabled(enable)

class IndexedColorPicker(QtWidgets.QWidget):

    colorChanged = QtCore.pyqtSignal(str,str,int)
    sizeChanged = QtCore.pyqtSignal(str,float,int)

    def __init__(self,name,color,size=20,index=-1):
        super(IndexedColorPicker,self).__init__()
        self.color = color
        self.name = name
        self.size = size
        self.index = index
        self.label = QtWidgets.QLabel(self.name)
        self.label.setFixedWidth(20)
        self.PB = QtWidgets.QPushButton()
        self.PB.clicked.connect(self.changeColor)
        self.SB = QtWidgets.QSpinBox()
        self.SB.setMinimum(0)
        self.SB.setMaximum(100)
        self.SB.setSingleStep(1)
        self.SB.setValue(self.size)
        self.SB.valueChanged.connect(self.changeSize)
        self.setColor(self.color)
        self.grid = QtWidgets.QGridLayout(self)
        self.grid.addWidget(self.label,0,0)
        self.grid.addWidget(self.PB,0,1)
        self.grid.addWidget(self.SB,0,2)

    def changeColor(self):
        new_color = QtWidgets.QColorDialog.getColor(QtGui.QColor(self.color))
        self.color = new_color.name()
        self.setColor(self.color)
        self.colorChanged.emit(self.name,self.color,self.index)

    def changeSize(self,text):
        self.size = int(text)
        self.sizeChanged.emit(self.name, self.size/100,self.index)

    def getSize(self):
        return self.size

    def setColor(self,color):
        self.PB.setStyleSheet("background-color:"+color)
        self.color = color

    def getColor(self):
        return self.color

class IndexedComboBox(QtWidgets.QComboBox):
    textChanged = QtCore.pyqtSignal(str,int)

    def __init__(self,index):
        super(IndexedComboBox,self).__init__()
        self.index = index
        self.currentTextChanged.connect(self.changeText)

    def changeText(self,text):
        self.textChanged.emit(text,self.index)

class IndexedPushButton(QtWidgets.QPushButton):
    buttonClicked = QtCore.pyqtSignal(int)

    def __init__(self,text,index):
        super(IndexedPushButton,self).__init__(text)
        self.index = index
        self.clicked.connect(self.emitSignal)

    def emitSignal(self):
        self.buttonClicked.emit(self.index)

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
    def __init__(self,parent,type,x,y,z,intensity,nkz,fontname,fontsize,colormap,showFWHM=False):
        super(DynamicalColorMap,self).__init__(parent)
        self.figure = MplCanvas(self)
        self.x_linear = x
        self.y_linear = y
        self.z_linear = z
        self.intensity = intensity
        self.nkz = nkz
        self.showFWHM = showFWHM
        self.type = type
        self.fontname = fontname
        self.fontsize = fontsize
        self.colormap = colormap
        self.TwoDimMappingWindow = QtWidgets.QWidget()
        self.TwoDimMappingWindow.setWindowTitle('Summary of Broadening Analysis')
        self.TwoDimMappingWindowLayout = QtWidgets.QGridLayout(self.TwoDimMappingWindow)
        self.toolbar = NavigationToolbar(self.figure,self.TwoDimMappingWindow)
        self.TwoDimMappingWindowLayout.addWidget(self.figure,0,0)
        self.TwoDimMappingWindowLayout.addWidget(self.toolbar,1,0)
        self.TwoDimMappingWindow.setWindowModality(QtCore.Qt.WindowModal)
        self.TwoDimMappingWindow.setMinimumSize(1000,800)
        self.TwoDimMappingWindow.show()

    def showPlot(self):
        self.replot(self.type,self.x_linear,self.y_linear,self.z_linear,self.colormap,self.intensity,self.nkz)

    def refreshFonts(self,fontname,fontsize):
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
        self.cbar.ax.set_ylabel("Normalized Intensity",fontname=self.fontname,fontsize=self.fontsize)
        self.cbar.ax.tick_params(labelsize=self.fontsize)
        self.figure.draw()

    def refreshFWHM(self,showFWHM):
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
            self.cs = self.figure.axes.contourf(self.x_linear,self.y_linear,matrix.T/max_intensity,100,cmap=self.colormap)
        elif self.type == 'XZ':
            matrix = self.intensity[:,self.nkz,:]
            max_intensity = np.amax(np.amax(matrix))
            self.cs = self.figure.axes.contourf(self.x_linear,self.z_linear,matrix.T/max_intensity,100,cmap=self.colormap)
        elif self.type == 'YZ':
            matrix = self.intensity[self.nkz,:,:]
            max_intensity = np.amax(np.amax(matrix))
            self.cs = self.figure.axes.contourf(self.y_linear,self.z_linear,matrix.T/max_intensity,100,cmap=self.colormap)
        self.cbar = self.figure.fig.colorbar(self.cs,format='%.2f')
        self.refreshFWHM(self.showFWHM)
        self.refreshFonts(self.fontname,self.fontsize)

    def refreshColormap(self,colormap):
        self.colormap = colormap
        self.replot(self.type,self.x_linear,self.y_linear,self.z_linear,self.colormap,self.intensity,self.nkz)
