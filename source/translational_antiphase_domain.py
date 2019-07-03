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
        self.Dialog = QtWidgets.QWidget()
        self.Grid = QtWidgets.QGridLayout(self.Dialog)
        self.plot = plot_chart.PlotChart(0,"Normal")
        self.REFRESH_PLOT.connect(self.plot.add_chart)
        self.gamma_slider = LabelSlider(0,1000,0.1,1000,'Gamma')
        self.gamma_slider.VALUE_CHANGED.connect(self.update_gamma)
        self.Grid.addWidget(self.plot,0,0,1,5)
        self.Grid.addWidget(self.gamma_slider,1,0,1,5)
        self.Dialog.setWindowTitle("Translational-antiphase Domain Model")
        self.Dialog.setWindowModality(QtCore.Qt.WindowModal)
        self.Dialog.setMinimumSize(1000,800)
        #self.Dialog.show()
        desktopRect = QtWidgets.QApplication.desktop().availableGeometry(self.Dialog)
        center = desktopRect.center()
        self.Dialog.move(center.x()-self.Dialog.width()*0.5,center.y()-self.Dialog.height()*0.5)


        self.Energy = 100
        self.Lambda = np.sqrt(150.4/(self.Energy))
        self.lattice_constant = 3.15
        self.unit = 'S'

        self.fit_worker = FitFunctions()
        #self.plot_IS()
        #self.plot_contour()
        self.plot_2D()
        #self.plot_FWHM()
        plt.show()

    def plot_IS(self):
        self.plot.main()
        if self.unit == 'h':
            self.h = np.linspace(1.5,2.5,1001)
            self.I = self.fit_worker.translational_antiphase_domain_model_intensity_using_h(self.h,self.gamma_slider.get_value())
            self.REFRESH_PLOT.emit(self.h,self.I,'general','Arial',25,'red',False,{'title':'Intensity Profile From 1D Translational-antiphase Domain Model\n(gamma={:5.3f})'.format(self.gamma_slider.get_value()),\
                                                                                      'x_label':'h', 'x_unit':'S\u2090\u22C5a/2\u03C0','y_label':'Intensity','y_unit':'arb. units'})
        elif self.unit == 'S':
            self.S = np.linspace(1.8,2.8,1001)
            self.I = self.fit_worker.translational_antiphase_domain_model_intensity_using_S(self.S,self.lattice_constant,self.gamma_slider.get_value())
            self.REFRESH_PLOT.emit(self.S,self.I,'general','Arial',25,'red',False,{'title':'Intensity Profile From 1D Translational-antiphase Domain Model\n(gamma={:5.3f})'.format(self.gamma_slider.get_value()), \
                                                                                   'x_label':'S', 'x_unit':'\u212B\u207B\u00B9','y_label':'Intensity','y_unit':'arb. units'})

    def plot_FWHM(self):
        self.gamma = np.linspace(0.001,1,400)
        self.width = self.fit_worker.FWHM_of_translational_antiphase_domain_model(1,self.gamma,self.lattice_constant)
        self.figure_FWHM, self.ax_FWHM = plt.subplots()
        self.ax_FWHM.plot(self.gamma,self.width,'ro')
        self.ax_FWHM.set_xlabel(r'$\gamma$',fontsize=30)
        self.ax_FWHM.set_ylabel('HWHM (\u212B\u207B\u00B9)',fontsize=30)
        self.ax_FWHM.tick_params(labelsize=30)

    def plot_contour(self):
        x = np.linspace(-4,4,1001)
        y = np.linspace(0.001,0.25,1000)
        self.h_index,self.gamma = np.meshgrid(x,y)
        self.Int = self.fit_worker.translational_antiphase_domain_model_intensity(self.h_index,self.gamma)
        self.figure, self.ax = plt.subplots()
        self.cs = self.ax.contourf(self.h_index,self.gamma,np.log(self.Int),200,cmap='jet')
        self.ax.set_xlabel('h' ,fontsize=30)
        self.ax.set_ylabel(r'$\gamma$',fontsize=30)
        #self.ax.set_title('Intensity contour',fontsize=30)
        self.ax.tick_params(labelsize=30)
        cbar = self.figure.colorbar(self.cs)
        cbar.set_ticks(np.linspace(-8,7,16))
        cbar.set_ticklabels(list('$10^{{{}}}$'.format(i) for i in range(-8,8,1)))
        cbar.set_label('Intensity',fontsize=30)
        cbar.ax.tick_params(labelsize=30)

    def plot_2D(self):
        hk_range = 3
        h = np.linspace(-hk_range,hk_range,1001)
        k = np.linspace(-hk_range,hk_range,1001)
        angle=60
        self.gamma_a = 0.1
        self.gamma_b = 0.1
        self.gamma_c = 0.1
        self.h_index_grid, self.k_index_grid = np.meshgrid(h,k)
        self.i_index_grid = -(self.h_index_grid+self.k_index_grid)
        #self.Int_2D = self.fit_worker.translational_antiphase_domain_model_intensity_2D_four_indices\
        #    (self.h_index_grid, self.k_index_grid, self.i_index_grid, self.gamma_a, self.gamma_b, self.gamma_c)
        self.Int_2D = self.fit_worker.translational_antiphase_domain_model_intensity_2D\
            (self.h_index_grid, self.k_index_grid, self.gamma_a, self.gamma_b)
        int_max = np.amax(self.Int_2D)
        log_max = int(np.log10(int_max)+1)
        int_min = np.amin(self.Int_2D)
        if int_min == 0:
            log_min = -3
        else:
            log_min = max(int(np.log10(int_min)),-3)
        self.x_grid = self.h_index_grid+np.cos(angle/180*np.pi)*self.k_index_grid
        self.y_grid = np.sin(angle/180*np.pi)*self.k_index_grid
        self.figure_2D, self.ax_2D = plt.subplots()
        self.cs_2D = self.ax_2D.contourf(self.x_grid,self.y_grid,np.clip(np.log10(self.Int_2D),log_min,log_max),200,cmap='jet')
        self.ax_2D.set_xlabel('h' ,fontsize=25)
        self.ax_2D.set_ylabel('2k - h',fontsize=25)
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
        if self.unit == 'h':
            self.I = self.fit_worker.translational_antiphase_domain_model_intensity_using_h(self.h,self.gamma_slider.get_value())
            self.REFRESH_PLOT.emit(self.h,self.I,'general','Arial',25,'red',False,{'title':'Intensity Profile From 1D Translational-antiphase Domain Model\n(gamma={:5.3f})'.format(self.gamma_slider.get_value()),\
                                                                                      'x_label':'h', 'x_unit':'S\u2090\u22C5a/2\u03C0','y_label':'Intensity','y_unit':'arb. units'})
        elif self.unit == 'S':
            self.I = self.fit_worker.translational_antiphase_domain_model_intensity_using_S(self.S,self.lattice_constant,self.gamma_slider.get_value())
            self.REFRESH_PLOT.emit(self.S,self.I,'general','Arial',25,'red',False,{'title':'Intensity Profile From 1D Translational-antiphase Domain Model\n(gamma={:5.3f})'.format(self.gamma_slider.get_value()), \
                                                                                   'x_label':'S', 'x_unit':'\u212B\u207B\u00B9','y_label':'Intensity','y_unit':'arb. units'})

def main():
    app = QtWidgets.QApplication(sys.argv)
    simulation = Window()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
