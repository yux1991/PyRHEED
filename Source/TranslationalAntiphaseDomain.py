from PyQt5 import QtCore, QtWidgets, QtGui
import PlotChart
from MyWidgets import *
import numpy as np
import sys

class Window(QtCore.QObject):

    RefreshPlot = QtCore.pyqtSignal(np.ndarray,np.ndarray,str,str,int,str,bool,dict)

    def __init__(self):
        super(Window,self).__init__()
        self.Dialog = QtWidgets.QWidget()
        self.Grid = QtWidgets.QGridLayout(self.Dialog)
        self.plot = PlotChart.PlotChart(0,"Normal")
        self.RefreshPlot.connect(self.plot.addChart)
        self.lattice_a_label = QtWidgets.QLabel("a' (\u212B)")
        self.lattice_a = QtWidgets.QLineEdit('3.15')
        self.gamma_slider = LabelSlider(0,100,0.1,200,'Gamma')
        self.gamma_slider.valueChanged.connect(self.update_gamma)
        self.OKButton = QtWidgets.QPushButton("OK")
        self.OKButton.clicked.connect(self.load)
        self.load()
        self.Grid.addWidget(self.plot,0,0,1,5)
        self.Grid.addWidget(self.lattice_a_label,1,0,1,1)
        self.Grid.addWidget(self.lattice_a,1,1,1,1)
        self.Grid.addWidget(self.gamma_slider,2,0,1,5)
        self.Dialog.setWindowTitle("Translational-antiphase Domain Model")
        self.Dialog.setWindowModality(QtCore.Qt.WindowModal)
        self.Dialog.show()

    def load(self):
        self.fixed_fa = True
        self.Energy = 100
        self.Lambda = np.sqrt(150.4/(self.Energy))
        self.plot.Main()
        if self.fixed_fa:
            self.S = np.linspace(-1,1,2000)
            self.I, self.FWHM = self.intensity(self.S,self.gamma_slider.getValue(),float(self.lattice_a.text()))
            self.RefreshPlot.emit(self.S,self.I,'general','Arial',25,'red',False,{'title':'Intensity Profile From 1D Translational-antiphase Domain Model\n(gamma={:5.3f}, HWHM={:5.3f} \u212B\u207B\u00B9)'.format(self.gamma_slider.getValue(),self.FWHM), \
                                                                                      'x_label':'S', 'x_unit':'\u212B\u207B\u00B9','y_label':'Intensity','y_unit':'arb. units'})
        else:
            self.S = np.linspace(-18,18,1000)/(2*np.pi/float(self.lattice_a.text()))
            self.I = self.intensity(self.S,self.gamma_slider.getValue(),float(self.lattice_a.text()))
            self.RefreshPlot.emit(self.S,self.I,'general','Arial',25,'red',False,{'title':'Intensity Profile From 1D Translational-antiphase Domain Model\n(gamma={:5.3f})'.format(self.gamma_slider.getValue()),\
                                                                                  'x_label':'h', 'x_unit':'S\u2090\u22C5a/2\u03C0','y_label':'Intensity','y_unit':'arb. units'})

    def f_a_fixed(self,gamma):
        return 1-2*gamma

    def f_a(self,S,gamma,a):
        return 1-gamma+gamma*np.cos(S*a/2)

    def intensity(self,S,gamma,a):
        if self.fixed_fa:
            fa = self.f_a_fixed(gamma)
            return (1-np.multiply(fa,fa))/(1+np.multiply(fa,fa)-2*np.multiply(fa,np.cos(S*a))), np.arccos((4*fa-np.multiply(fa,fa)-1)/(2*fa))/a
        else:
            fa = self.f_a(S,gamma,a)
            return (1-np.multiply(fa,fa))/(1+np.multiply(fa,fa)-2*np.multiply(fa,np.cos(S*a)))

    def update_gamma(self,value,index):
        if self.fixed_fa:
            self.I, self.FWHM = self.intensity(self.S,value,float(self.lattice_a.text()))
            self.RefreshPlot.emit(self.S,self.I,'general','Arial',25,'red',False,{'title':'Intensity Profile From 1D Translational Anti-phase Domain Model\n(gamma={:5.3f}, HWHM={:5.3f} \u212B\u207B\u00B9)'.format(self.gamma_slider.getValue(),self.FWHM), \
                                                                                  'x_label':'S', 'x_unit':'\u212B\u207B\u00B9','y_label':'Intensity','y_unit':'arb. units'})
        else:
            self.I = self.intensity(self.S,self.gamma_slider.getValue(),float(self.lattice_a.text()))
            self.RefreshPlot.emit(self.S,self.I,'general','Arial',25,'red',False,{'title':'Intensity Profile From 1D Translational-antiphase Domain Model\n(gamma={:5.3f})'.format(self.gamma_slider.getValue()), \
                                                                                  'x_label':'h', 'x_unit':'S\u2090\u22C5a/2\u03C0','y_label':'Intensity','y_unit':'arb. units'})

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    simulation = Window()
    sys.exit(app.exec_())
