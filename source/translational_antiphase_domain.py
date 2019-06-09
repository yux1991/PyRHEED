from PyQt5 import QtCore, QtWidgets
from my_widgets import LabelSlider
from process import FitFunctions
import matplotlib.pyplot as plt
import numpy as np
import plot_chart
import sys

class Window(QtCore.QObject):

    REFRESH_PLOT = QtCore.pyqtSignal(np.ndarray,np.ndarray,str,str,int,str,bool,dict)

    def __init__(self):
        super(Window,self).__init__()
        #self.Dialog = QtWidgets.QWidget()
        #self.Grid = QtWidgets.QGridLayout(self.Dialog)
        #self.plot = plot_chart.PlotChart(0,"Normal")
        #self.REFRESH_PLOT.connect(self.plot.add_chart)
        #self.gamma_slider = LabelSlider(0,100,0.1,200,'Gamma')
        #self.gamma_slider.VALUE_CHANGED.connect(self.update_gamma)
        #self.Grid.addWidget(self.plot,0,0,1,5)
        #self.Grid.addWidget(self.gamma_slider,1,0,1,5)
        #self.Dialog.setWindowTitle("Translational-antiphase Domain Model")
        #self.Dialog.setWindowModality(QtCore.Qt.WindowModal)
        #self.Dialog.show()

        self.fit_worker = FitFunctions()
        #self.plot_IS()
        #self.plot_contour()
        self.plot_2D()
        plt.show()

    def plot_IS(self):
        self.Energy = 100
        self.Lambda = np.sqrt(150.4/(self.Energy))
        self.plot.main()
        self.h = np.linspace(-4,4,10000)
        self.I = self.fit_worker.translational_antiphase_domain_model_intensity(self.h,self.gamma_slider.get_value())
        self.REFRESH_PLOT.emit(self.h,self.I,'general','Arial',25,'red',False,{'title':'Intensity Profile From 1D Translational-antiphase Domain Model\n(gamma={:5.3f})'.format(self.gamma_slider.get_value()),\
                                                                                  'x_label':'h', 'x_unit':'S\u2090\u22C5a/2\u03C0','y_label':'Intensity','y_unit':'arb. units'})

    def plot_contour(self):
        x = np.linspace(-4,4,1000)
        y = np.linspace(0.001,0.25,1000)
        self.h_index,self.gamma = np.meshgrid(x,y)
        self.Int = self.fit_worker.translational_antiphase_domain_model_intensity(self.h_index,self.gamma)
        self.figure, self.ax = plt.subplots()
        self.cs = self.ax.contourf(self.h_index,self.gamma,np.log(self.Int),200,cmap='jet')
        self.ax.set_xlabel('h (S\u2090\u22C5a/2\u03C0)' ,fontsize=25)
        self.ax.set_ylabel(r'$\gamma$',fontsize=25)
        self.ax.set_title('Intensity contour',fontsize=25)
        self.ax.tick_params(labelsize=25)
        cbar = self.figure.colorbar(self.cs)
        cbar.set_ticks(np.linspace(-8,7,16))
        cbar.set_ticklabels(list('$10^{{{}}}$'.format(i) for i in range(-8,8,1)))
        cbar.set_label('Intensity',fontsize=25)
        cbar.ax.tick_params(labelsize=25)

    def plot_2D(self):
        hk_range = 4
        m_range = 1
        h = np.linspace(-hk_range,hk_range,1000)
        k = np.linspace(-hk_range,hk_range,1000)
        angle=60
        self.gamma_a = 0.1
        self.gamma_b = 0.1
        self.h_index_grid, self.k_index_grid = np.meshgrid(h,k)
        self.Int_2D = self.fit_worker.translational_antiphase_domain_model_intensity_2D_without_approximation(self.h_index_grid, self.k_index_grid,\
                                                                                        self.gamma_a,self.gamma_b,m_range,m_range)
        #self.Int_2D = self.fit_worker.translational_antiphase_domain_model_intensity_2D(self.h_index_grid, self.k_index_grid, \
        #                                                                                self.gamma_a,self.gamma_b)
        int_max = np.amax(self.Int_2D)
        log_max = int(np.log10(int_max))
        int_min = np.amin(self.Int_2D)
        if int_min == 0:
            log_min = -3
        else:
            log_min = max(int(np.log10(int_min)),-3)
        self.x_grid = self.h_index_grid+np.cos(angle/180*np.pi)*self.k_index_grid
        self.y_grid = np.sin(angle/180*np.pi)*self.k_index_grid
        self.figure_2D, self.ax_2D = plt.subplots()
        self.cs_2D = self.ax_2D.contourf(self.x_grid,self.y_grid,np.clip(np.log10(self.Int_2D),log_min,log_max),200,cmap='jet')
        self.ax_2D.set_xlabel(r'h ($S_{a}$'+'\u22C5a/2\u03C0)' ,fontsize=25)
        self.ax_2D.set_ylabel(r'k ($S_{b}$'+'\u22C5b/2\u03C0)',fontsize=25)
        self.ax_2D.set_xlim(-hk_range/2,hk_range/2)
        self.ax_2D.set_ylim(-hk_range/2,hk_range/2)
        self.ax_2D.set_title('Simulated 2D Map',fontsize=25)
        self.ax_2D.tick_params(labelsize=25)
        self.ax_2D.set_aspect(1)
        cbar = self.figure_2D.colorbar(self.cs_2D)
        cbar.set_ticks(np.linspace(log_min,log_max,log_max-log_min+1))
        cbar.set_ticklabels(list('$10^{{{}}}$'.format(i) for i in range(log_min,log_max+1,1)))
        cbar.set_label('Intensity',fontsize=25)
        cbar.ax.tick_params(labelsize=25)

    def update_gamma(self,value,index):
        self.I = self.fit_worker.translational_antiphase_domain_model_intensity(self.h,self.gamma_slider.get_value())
        self.REFRESH_PLOT.emit(self.h,self.I,'general','Arial',25,'red',False,{'title':'Intensity Profile From 1D Translational-antiphase Domain Model\n(gamma={:5.3f})'.format(self.gamma_slider.get_value()), \
                                                                                  'x_label':'h', 'x_unit':'S\u2090\u22C5a/2\u03C0','y_label':'Intensity','y_unit':'arb. units'})

def main():
    app = QtWidgets.QApplication(sys.argv)
    simulation = Window()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
