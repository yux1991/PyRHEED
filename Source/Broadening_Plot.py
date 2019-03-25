#This is a program to plot out the results obtained with "Broadening.py"
#Last updated by Yu Xiang at 06/08/2018
#This code is written in Python 3.6.3

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Standard Libraries ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.gridspec as gridspec
import matplotlib.ticker as ticker
import matplotlib
import rawpy
import glob
import math
import scipy.ndimage
from mpl_toolkits.mplot3d import Axes3D

path = 'C:/Google Drive/Documents/RHEED/Python Code/WSe2_RHEED_Fit.txt'
FitResults = np.loadtxt(path,delimiter='\t',skiprows=4)

def HorizontalSlice(n_Peak,n_Kp):

	Phi = np.linspace(0,358.2,200)*np.pi/180
	Kp = np.unique(FitResults[:,1])
	FWHM = FitResults[n_Kp-1:100*Kp.shape[0]:Kp.shape[0],21+n_Peak]
	FWHMs = np.append(FWHM,FWHM)
	Height = FitResults[n_Kp-1:100*Kp.shape[0]:Kp.shape[0],1+n_Peak]
	Heights = np.append(Height,Height)/np.amax(Height)
	fig = plt.figure()
	ax1 = fig.add_subplot(121,projection='polar')
	plt.title(r'FWHM ($\AA^{-1}$) vs $\phi$ ($^\circ$)',fontsize=20)
	ax1.scatter(Phi,FWHMs,c='r')
	ax1.set_rmin(0.9)
	ax1.set_rmax(1.6)
	ax1.set_rticks(np.around(np.linspace(0.9,1.6,7),1))
	plt.suptitle(r''.join(['The Horizontal Slice of the (00) Reciprocal Rod of $WSe_{2}$ at $K_{p}$ = ', str(np.round(Kp[n_Kp-1],2)),' $\AA^{-1}$']),fontsize=24)
	ax2 = fig.add_subplot(122,projection='polar')
	plt.title(r'Intensity (arb. units) vs $\phi$ ($^\circ$)',fontsize=20)
	ax2.scatter(Phi,Heights,c='b')
	ax2.set_rmin(0)
	ax2.set_rmax(1.1)
	ax2.set_rticks(np.around(np.linspace(0,1.1,5),1))

def VerticalSlice(n_Peak,n_Phi):

	Phi = np.linspace(0,358.2,100)
	Kp = np.unique(FitResults[:,1])
	FWHMs = FitResults[n_Phi*Kp.shape[0]:(n_Phi+1)*Kp.shape[0],21+n_Peak]
	Heights = FitResults[n_Phi*Kp.shape[0]:(n_Phi+1)*Kp.shape[0],1+n_Peak]
	fig = plt.figure()
	ax1 = fig.add_subplot(121)
	ax1.plot(FWHMs,Kp,c='r')
	ax1.set_xlabel(r'$FWHM$ $(\AA^{-1})$',fontsize = 20)
	ax1.set_ylabel(r'$K_{perp}$ $(\AA^{-1})$',fontsize = 20)
	plt.suptitle(r''.join(['The Vertical Slice of the (00) Reciprocal Rod of $MoS_{2}$ at $\phi$ = ', str(np.round(Phi[n_Phi],1)),'$^\circ$']),fontsize=24)
	ax2 = fig.add_subplot(122)
	ax2.plot(Heights,Kp,c='b')
	ax2.set_xlabel('Intensity (arb. units)',fontsize = 20)
	ax2.set_ylabel(r'$K_{perp}$ $(\AA^{-1})$',fontsize = 20)

def Rod_3D(n_Peak):

	output = open('MoS2_3D.txt',mode='a')
	fig = plt.figure()
	ax1 = fig.add_subplot(111,projection='3d')
	plt.title(r'Shape of $MoS_{2}$ (00) reciprocal rod',fontsize=20)

	Phi = np.linspace(0,358.2,200)*np.pi/180
	Kp = np.unique(FitResults[:,1])

	for n_Kp in range(0,Kp.shape[0]):

		FWHM_Kp = FitResults[n_Kp:100*Kp.shape[0]:Kp.shape[0],21+n_Peak]
		FWHMs_Kp = np.append(FWHM_Kp,FWHM_Kp)
		X = np.multiply(FWHMs_Kp,np.cos(Phi))
		Y = np.multiply(FWHMs_Kp,np.sin(Phi))
		Z = np.full(X.shape,Kp[n_Kp])
		ax1.scatter(X,Y,Kp[n_Kp],c='r',marker='o')
		result = '\n'.join(str(np.round(e,decimals=2)).ljust(8) for e in np.transpose(np.vstack((X,Y,Z))))+'\n'
		output.write(result)

	ax1.set_xlabel(r'$K_{x}$ $(\AA^{-1})$')
	ax1.set_ylabel(r'$K_{y}$ $(\AA^{-1})$')
	ax1.set_zlabel(r'$K_{z}$ $(\AA^{-1})$')
	output.close()

def main():

	for n_Kp in range(0,4):
		HorizontalSlice(5,n_Kp+1)
		mng = plt.get_current_fig_manager()
		mng.window.state('zoomed')

	#for n_Phi in range(20):
	#	VerticalSlice(5,n_Phi)
	#	mng = plt.get_current_fig_manager()
	#	mng.window.state('zoomed')

	#Rod_3D(5)

	plt.show()

if __name__ == '__main__':
	main()
