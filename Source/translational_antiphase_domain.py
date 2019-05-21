from PyQt5 import QtCore, QtWidgets, QtGui
import plot_chart
from my_widgets import LabelSlider
import matplotlib.pyplot as plt
import numpy as np
import sys

class Window(QtCore.QObject):

    REFRESH_PLOT = QtCore.pyqtSignal(np.ndarray,np.ndarray,str,str,int,str,bool,dict)

    def __init__(self):
        super(Window,self).__init__()
        self.Dialog = QtWidgets.QWidget()
        self.Grid = QtWidgets.QGridLayout(self.Dialog)
        self.plot = plot_chart.PlotChart(0,"Normal")
        self.REFRESH_PLOT.connect(self.plot.addChart)
        self.lattice_a_label = QtWidgets.QLabel("a' (\u212B)")
        self.lattice_a = QtWidgets.QLineEdit('3.15')
        self.gamma_slider = LabelSlider(0,100,0.1,200,'Gamma')
        self.gamma_slider.VALUE_CHANGED.connect(self.update_gamma)
        self.OKButton = QtWidgets.QPushButton("OK")
        self.OKButton.clicked.connect(self.plot_IS)
        self.plot_IS()
        self.plot_contour()
        self.Grid.addWidget(self.plot,0,0,1,5)
        self.Grid.addWidget(self.lattice_a_label,1,0,1,1)
        self.Grid.addWidget(self.lattice_a,1,1,1,1)
        self.Grid.addWidget(self.gamma_slider,2,0,1,5)
        self.Dialog.setWindowTitle("Translational-antiphase Domain Model")
        self.Dialog.setWindowModality(QtCore.Qt.WindowModal)
        self.Dialog.show()
        plt.show()

    def plot_IS(self):
        self.Energy = 100
        self.Lambda = np.sqrt(150.4/(self.Energy))
        self.plot.Main()
        self.S = np.linspace(-18,18,1000)/(2*np.pi/float(self.lattice_a.text()))
        self.I = self.intensity(self.S,self.gamma_slider.get_value(),float(self.lattice_a.text()))
        self.REFRESH_PLOT.emit(self.S,self.I,'general','Arial',25,'red',False,{'title':'Intensity Profile From 1D Translational-antiphase Domain Model\n(gamma={:5.3f})'.format(self.gamma_slider.get_value()),\
                                                                                  'x_label':'h', 'x_unit':'S\u2090\u22C5a/2\u03C0','y_label':'Intensity','y_unit':'arb. units'})

    def plot_contour(self):
        x = np.linspace(-16,16,1000)/(2*np.pi/float(self.lattice_a.text()))
        y = np.linspace(0.01,1,1000)
        self.sa,self.gamma = np.meshgrid(x,y)
        self.Int = self.intensity(self.sa,self.gamma,float(self.lattice_a.text()))
        self.figure, self.ax = plt.subplots()
        self.cs = self.ax.contourf(self.sa,self.gamma,np.log(self.Int),200,cmap='jet')
        self.ax.set_xlabel('h (S\u2090\u22C5a/2\u03C0)' ,fontsize=25)
        self.ax.set_ylabel(r'$\gamma$',fontsize=25)
        self.ax.set_title('Intensity contour',fontsize=25)
        self.ax.tick_params(labelsize=25)
        cbar = self.figure.colorbar(self.cs)
        cbar.set_ticks(np.linspace(-6,5,12))
        cbar.set_ticklabels(list('$10^{{{}}}$'.format(i) for i in range(-6,6,1)))
        cbar.set_label('Intensity',fontsize=25)
        cbar.ax.tick_params(labelsize=25)

    def f_a(self,S,gamma,a):
        #return 1-gamma+gamma*np.cos(S*a/2)
        return 1-gamma+1/2*gamma*np.cos(S*a/3)+1/2*gamma*np.cos(S*2*a/3)

    def intensity(self,S,gamma,a):
        fa = self.f_a(S,gamma,a)
        return (1-np.multiply(fa,fa))/(1+np.multiply(fa,fa)-2*np.multiply(fa,np.cos(S*a)))

    def update_gamma(self,value,index):
        self.I = self.intensity(self.S,self.gamma_slider.get_value(),float(self.lattice_a.text()))
        self.REFRESH_PLOT.emit(self.S,self.I,'general','Arial',25,'red',False,{'title':'Intensity Profile From 1D Translational-antiphase Domain Model\n(gamma={:5.3f})'.format(self.gamma_slider.get_value()), \
                                                                                  'x_label':'h', 'x_unit':'S\u2090\u22C5a/2\u03C0','y_label':'Intensity','y_unit':'arb. units'})

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    simulation = Window()
    sys.exit(app.exec_())
