#This program is used to study the broadening of RHEED streaks
#Last updated by Yu Xiang at 06/06/2018
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
from scipy.optimize import least_squares
from time import sleep
import sys
import matplotlib.cm as cm

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Global Variables ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
img_path_MAC = '/Users/yuxiang/Documents/RHEED/04032018_G_on_SiC/20_keV_47_uA/Img0000.nef'
img_path_PC = 'C:/RHEED/03162017 WSe2/20 keV set3/*.nef'

SF = 80.75 #scale factor in the unit of pixel/Anstrong^-1
#define the position of the line
x1,y1 = 200,50
x2,y2 = 2300,1100
width = 5 #define the width of the integral
length = 1500 #define the length of the integral
direction = 'horizontal' #determine whether the profile is vertical or horizontal
nos = 1000 #define the number of steps
center = [1200,400,300,200] #define the center of the diffraction streak
Yoffset = 80 #the Y position of the straight through spot

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Operational Functions ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def read_image(img_path,nimg=0): # Read the raw image and convert it to grayvalue images

	#---------------------- Input list ------------------------------------
	#	img_path: the path that stores the RHEED images
	#		  Default: img_path_PC
	#
	#	nimg:     the RHEED image index
	#                 Default: 0
	#
	#---------------------- Output list -----------------------------------
	#       img:the matrix that stores the grayvales of the RHEED image
	#
	#----------------------------------------------------------------------

	#create an array that stores all image pathes
	image_list = []
	for filename in glob.glob(img_path_PC):
		image_list.append(filename)
	#Read the raw *.nef images
	img_raw = rawpy.imread(image_list[nimg])
	#Demosaicing
	img_rgb = img_raw.postprocess(demosaic_algorithm=rawpy.DemosaicAlgorithm.AHD,bright=0.15, user_black=100, output_bps = 16)
	#Convert to grayvalue images
	img_bw = (0.21*img_rgb[:,:,0])+(0.72*img_rgb[:,:,1])+(0.07*img_rgb[:,:,2])
	#Crop the image
	img = img_bw[1200:2650,500:3100]
	return img

def find_Xcenter(img):  #Find the X-center of the image

	#---------------------- Input list ------------------------------------
	#	img:the matrix that stores the grayvales of the RHEED image
	#
	#---------------------- Output list -----------------------------------
	#       Xoffset: the x-offset in order to go to the center
	#
	#----------------------------------------------------------------------

	CtrX = np.argmax(np.sum(img[center[1]-center[3]//2:center[1]+center[3]//2,center[0]-center[2]//2:center[0]+center[2]//2],axis=0,keepdims=1),axis=1)

	#Find the offset in X direction
	Xoffset = CtrX[0]+center[0]-center[2]//2

	return Xoffset

def plot_RHEED_pattern(img,Xoffset,Yoffset,nimg=0,Kp=700):

	#---------------------- Input list ------------------------------------
	#	img: the matrix that stores the grayvales of the RHEED image
	#
	#       Xoffset: the x-offset in order to go to the center
	#
	#       Yoffset: the y-offset in order to go to the center
	#
	#	nimg: the RHEED image index
	#	      Default: 0
	#
	#	Kp: ONLY USED WHEN DIRECTION IS 'HORIZONTAL', which defines
	#	    the K_perp position
	#	    Default: 500
	#
	#----------------------------------------------------------------------

	#Create a figure
	plt.figure()
	#plot the RHEED pattern
	im=plt.imshow(img,cmap = plt.cm.jet)
	ax1 = plt.axes()
	plt.title(r''.join(['$\phi = ',str(nimg*1.8),'^\circ$']),fontsize = 20)
	plt.axis([0,2600,1450,0])

	if direction == 'vertical':
		#draw the line
		plt.plot([Xoffset,Xoffset],[y1,y2],'wo-')
		#draw the rectangle
		p=patches.Rectangle((Xoffset-width//2,y1),width,y2-y1,fill=False,ls='--',ec='w')
	else:
		plt.plot([Xoffset-length//2,Xoffset+length//2],[Kp,Kp],'wo-')
		p=patches.Rectangle((Xoffset-length//2,Kp-width//2),length,width,fill=False,ls='--',ec='w')

	plt.colorbar(im,orientation = 'horizontal',format = '%4d')
	ax1.add_patch(p)
	ax1.set_xlabel(r'$K_{\||} (\AA^{-1})$',fontsize = 20)
	ax1.set_ylabel(r'$K_{\bot} (\AA^{-1})$',fontsize = 20)

	xticks = np.around((ax1.get_xticks()-Xoffset)/SF,1)
	ax1.set_xticklabels(xticks,fontsize = 20)
	yticks = np.around((ax1.get_yticks()-Yoffset)/SF,1)
	ax1.set_yticklabels(yticks,fontsize = 20)

def get_line_profile(img, Xoffset=0,Kp=100,integral= True):

	#---------------------- Input list ------------------------------------
	#	img: the matrix that stores the grayvales of the RHEED image
	#
	#	Xoffset: the x-offset in order to go to the center
	#		 Default:0
	#
	#	Kp: ONLY USED WHEN DIRECTION IS 'HORIZONTAL', which defines
	#		 the K_perp position
	#		 Default:100
	#
	#	integral: either TRUE or FALSE, which determine whether perform
	#                 the integral
	#		  Default: TRUE
	#
	#---------------------- Output list -----------------------------------
	#       AreaIntegral: the area integrated profile. ONLY WHEN INTEGRAL IS TRUE
	#	profile: the line profile. ONLY WHEN INTEGRAL IS FALSE
	#
	#----------------------------------------------------------------------

	if direction == 'vertical':
		x = np.linspace(Xoffset,Xoffset,nos)
		y = np.linspace(y1,y2,nos)

		#extract line profile
		profile = scipy.ndimage.map_coordinates(img,np.vstack((y,x)),order=0,cval = 100000.)
		#print(profile.shape)

		#extract the area integral
		AreaIntegral = np.sum(img[y1:y2,Xoffset-width//2:Xoffset+width//2],axis=1,keepdims=1)
		#print(AreaIntegral.shape)

	if direction == 'horizontal':
		x = np.linspace(Xoffset-length//2,Xoffset+length//2,nos)
		y = np.linspace(Kp,Kp,nos)

		#extract line profile
		profile = scipy.ndimage.map_coordinates(img,np.vstack((y,x)),order=0,cval = 100000.)
		#print(profile.shape)

		#extract the area integral
		AreaIntegral = np.transpose(np.sum(img[Kp-width//2:Kp+width//2,Xoffset-length//2:Xoffset+length//2],axis=0,keepdims=1))
		#print(AreaIntegral.shape)

	if integral:
		return AreaIntegral
	else:
		return profile

def plot_line_profile(profile, nimg, Xoffset, Yoffset,Kp):

	#---------------------- Input list ------------------------------------
	#	profile: the line profile to be plotted
	#
	#	Xoffset: the x-offset in order to go to the center
	#
	#	Yoffset: ONLY USED WHEN DIRECTION IS HORIZONTAL. the y-offset in order to go to the center
	#
	#	Kp: ONLY USED WHEN DIRECTION IS HORIZONTAL. The K perpendicular
	#	    position of the horizontal line scan
	#---------------------- Output list -----------------------------------
	#       Kx: the coordinates in Kx direction. ONLY WHEN DIRECTION IS HORIZONTAL.
	#	Ky: the coordinates in Ky direction. ONLY WHEN DIRECTION IS VERTICAL.
	#
	#----------------------------------------------------------------------

	profile_shape = profile.shape
	kx = np.linspace(-length//2,length//2,profile_shape[0])
	ky = np.linspace(y1-Yoffset,y2-Yoffset,profile_shape[0])


	#plot the line profile
	#plt.figure()
	#ax2 = plt.axes()
	#if direction == 'vertical':
	#	plt.plot(ky/SF,profile)
	#	ax2.set_xlabel(r'$K_{\bot} (\AA^{-1})$',fontsize = 20)
	#else:
	#	plt.plot(kx/SF,profile)
	#	plt.title(r''.join(['$\phi = ',str(nimg*1.8),'^\circ',',','K_{\perp} =',str(np.round((Kp-Yoffset)/SF,1)),' \AA^{-1}$']),fontsize = 20)
	#	ax2.set_xlabel(r'$K_{\parallel} (\AA^{-1})$',fontsize = 20)

	#plt.yscale('linear')
	#ax2.set_ylabel('Intensity',fontsize = 20)
	#ax2.ticklabel_format(style='sci',scilimits=(0,0),axis='both',format = '%2.1f')
	if direction == 'vertical':
		return ky/SF
	else:
		return kx/SF


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Gaussian Fit functions ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def gaussian(x,height, center,FWHM,offset):

	#---------------------- Input list ------------------------------------
	#	x: the X variable
	#
	#	height: the height of the Gaussian function
	#
	#	center: the center of the Gaussian function
	#
	#	FWHM: the full width at half maximum of the Gaussian function
	#
	#---------------------- Output list -----------------------------------
	#	gaussian: the gaussian function
	#
	#----------------------------------------------------------------------


	return height/(FWHM*math.sqrt(math.pi/(4*math.log(2))))*np.exp(-4*math.log(2)*(x - center)**2/(FWHM**2))+offset

def five_gaussians(x,H1,H2,H3,H4,H5,C1,C2,C3,C4,C5,W1,W2,W3,W4,W5,offset):

	#---------------------- Input list ------------------------------------
	#	x: the X variable
	#
	#	H1~H5: the five-element array that stores the heights of the Gaussian function
	#
	#	C1~C5: the five-element array that stores the centers of the Gaussian function
	#
	#	W1~W5: the five-element array that stores the full width at half maximums of the Gaussian function
	#
	#---------------------- Output list -----------------------------------
	#	five_gaussians: the function that adds five Gaussian functions
	#			together
	#
	#----------------------------------------------------------------------

	return (gaussian(x,H1,C1,W1,offset=0)+
	        gaussian(x,H2,C2,W2,offset=0)+
	        gaussian(x,H3,C3,W3,offset=0)+
	        gaussian(x,H4,C4,W5,offset=0)+
	        gaussian(x,H5,C5,W5,offset=0)+offset)

def nine_gaussians(x,H1,H2,H3,H4,H5,H6,H7,H8,H9,C1,C2,C3,C4,C5,C6,C7,C8,C9,W1,W2,W3,W4,W5,W6,W7,W8,W9,offset):

	#---------------------- Input list ------------------------------------
	#	x: the X variable
	#
	#	H1~H9: the nine-element array that stores the heights of the Gaussian function
	#
	#	C1~C9: the nine-element array that stores the centers of the Gaussian function
	#
	#	W1~W9: the nine-element array that stores the full width at half maximums of the Gaussian function
	#
	#---------------------- Output list -----------------------------------
	#	nine_gaussians: the function that adds seven Gaussian functions
	#			together
	#
	#----------------------------------------------------------------------

	return (gaussian(x,H1,C1,W1,offset=0)+
	        gaussian(x,H2,C2,W2,offset=0)+
	        gaussian(x,H3,C3,W3,offset=0)+
	        gaussian(x,H4,C4,W4,offset=0)+
		gaussian(x,H5,C5,W5,offset=0)+
		gaussian(x,H6,C6,W6,offset=0)+
	        gaussian(x,H7,C7,W7,offset=0)+
		gaussian(x,H8,C8,W8,offset=0)+
		gaussian(x,H9,C9,W9,offset=0)+offset)

def nine_gaussians_bg(x,H1,H2,H3,H4,H5,H6,H7,H8,H9,Hbg,C1,C2,C3,C4,C5,C6,C7,C8,C9,Cbg,W1,W2,W3,W4,W5,W6,W7,W8,W9,Wbg,offset):

	#---------------------- Input list ------------------------------------
	#	x: the X variable
	#
	#	H1~H9: the nine-element array that stores the heights of the Gaussian function
	#
	#	C1~C9: the nine-element array that stores the centers of the Gaussian function
	#
	#	W1~W9: the nine-element array that stores the full width at half maximums of the Gaussian function
	#
	#	Hbg,Cbg,Wbg, height, center position and the full width at half maximums of the Gaussian background
	#
	#---------------------- Output list -----------------------------------
	#	nine_gaussians: the function that adds seven Gaussian functions
	#			together
	#
	#----------------------------------------------------------------------

	return (gaussian(x,H1,C1,W1,offset=0)+
	        gaussian(x,H2,C2,W2,offset=0)+
	        gaussian(x,H3,C3,W3,offset=0)+
	        gaussian(x,H4,C4,W4,offset=0)+
		gaussian(x,H5,C5,W5,offset=0)+
		gaussian(x,H6,C6,W6,offset=0)+
	        gaussian(x,H7,C7,W7,offset=0)+
		gaussian(x,H8,C8,W8,offset=0)+
		gaussian(x,H9,C9,W9,offset=0)+
		gaussian(x,Hbg,Cbg,Wbg,offset=0)+offset)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Main Execution Function ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def main():

	#................................. Error Functions .......................................

	#Error function for the five-gaussian function
	errfunc5 = lambda p,x,y: (five_gaussians(x,*p)-y)**2
	#Error function for the nine-gaussian function
	errfunc9 = lambda p,x,y: (nine_gaussians(x,*p)-y)**2
	#Error function for the nine-gaussian function with a gaussain background
	errfunc9_bg = lambda p,x,y: (nine_gaussians_bg(x,*p)-y)**2*(y/1e6)

	#................................. Fitting Parameters ....................................

	width_minimum = 0.5		#the minimum FWHM of each fitted peak
	width_maximum = 3 		#the maximum FWHM of each fitted peak
	width_guess = 2			#the guessed widht of each fitted peak
	C_tol = 0.5			#the maximum deviation of the center position from the guess
	f_tol = 1e-14			#the tolerance for termination by the change of the cost function
	x_tol = 1e-10			#the tolerance for termination by the change of the independent variables
	GaussianBackground =True 	#the boolean constant that determines whether to include a Gaussian background in the fitting (when TRUE)
	integral = True			#the boolean constant that determines whether to do areal integral (when TRUE) or line scan (when FALSE)

	#................................ Create Output File ....................................
	output = open('WSe2_RHEED_Fit.txt',mode='w')
	output.write('This is a summary of the fit results:\n\n')
	output.write('Phi              Kp                 H1              H2              H3              H4             H5              H6              H7              H8		   H9              H_bg           C1              C2              C3             C4              C5              C6              C7              C8              C9             C_bg             W1              W2	         W3              W4              W5              W6              W7              W8             W9              W_bg             offset\n')
	output.write('-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n')
	ImgRange = 100
	for nimg in range(50,50+ImgRange,1):
		img = read_image(img_path_PC,nimg)
		Xoffset = find_Xcenter(img)
		#plot_RHEED_pattern(img,Xoffset,Yoffset,nimg,850)

		for Kp in range(300,500,40):
			#output2 =open('WSe2_RHEED_profile_phi={}_Kp={}.txt'.format(nimg,Kp/SF),mode='w')
			profile = get_line_profile(img,Xoffset,Kp,integral)
			K = plot_line_profile(profile,nimg,Xoffset,Yoffset,Kp)
			K2 = K.reshape(profile.shape)
			#output2.write(str(np.round(np.hstack((K2,profile)),decimals=2)))
			#output2.close()
			#np.savetxt('RHEED_profile_phi={}_Kp={}.txt'.format(nimg,np.round(Kp/SF,decimals=2)),np.hstack((K2,profile)),fmt='%.2f',newline='\n')
			max_int = np.amax(profile)
			if GaussianBackground:
				guess9 = [3e5,3e5,3e5,3e5,max_int,3e5,3e5,3e5,3e5,0.8*max_int*(7.5*math.sqrt(math.pi/(4*math.log(2)))),-8,-6.2,-4,-1.2,0,1.2,4,6.2,8,0,width_guess,width_guess,width_guess,width_guess,width_guess,width_guess,width_guess,width_guess,width_guess,7.5,0]
				optim9 = least_squares(errfunc9_bg,guess9[:],
					bounds = ([0,0,0,0.2*max_int,0.8*max_int,0.2*max_int,0,0,0,0.5*max_int*(7.5*math.sqrt(math.pi/(4*math.log(2)))),\
					guess9[10]-C_tol,guess9[11]-C_tol,guess9[12]-C_tol,guess9[13]-C_tol,guess9[14]-0.1,guess9[15]-C_tol,guess9[16]-C_tol,guess9[17]-C_tol,guess9[18]-C_tol,guess9[19]-C_tol,\
					width_minimum,width_minimum,width_minimum,width_minimum,width_minimum,width_minimum,width_minimum,width_minimum,width_minimum,5,-np.inf],\
					[np.inf,np.inf,np.inf,np.inf,np.inf,np.inf,np.inf,np.inf,np.inf,np.inf,\
					guess9[10]+C_tol,guess9[11]+C_tol,guess9[12]+C_tol,guess9[13]+C_tol,guess9[14]+0.1,guess9[15]+C_tol,guess9[16]+C_tol,guess9[17]+C_tol,guess9[18]+C_tol,guess9[19]+C_tol,\
					width_maximum,width_maximum,width_maximum,width_maximum,width_maximum,width_maximum,width_maximum,width_maximum,width_maximum,12,np.inf]),
					x_scale=[5e5,5e5,5e5,5e5,5e5,5e5,5e5,5e5,5e5,5e5,5,5,5,5,5,5,5,5,5,5,1,1,1,1,1,1,1,1,1,5,1e4],
					ftol=f_tol,
					xtol=x_tol,
					args=(K,profile[:,0]),
					verbose=0)

				#plt.figure()
				#plt.suptitle(r''.join(['The RHEED line profile of $WSe_{2}$ at $\phi$ =',str(np.round(nimg*1.8,2)),'$^\circ$, $K_{p}$ = ', str(np.round(Kp/SF,2)),' $\AA^{-1}$']),fontsize=24)
				#plt.plot(K,profile,lw=5,c='k',label='Measurement')
				#plt.plot(K,nine_gaussians_bg(K,*optim9.x),lw=3,c='r',ls='-',label='fit of 9 Gaussians')
				#colors = cm.rainbow(np.linspace(0,1,9))
				#for optimindex in range(9):
				#	parm = np.append(optim9.x[optimindex:30:10],optim9.x[30])
				#	plt.plot(K,gaussian(K,*parm),lw=3,c=colors[optimindex],ls='--',label=''.join(['individual fit',str(optimindex+1)]))
				#parm = [optim9.x[9],optim9.x[19],optim9.x[29],optim9.x[30]]
				#plt.plot(K,gaussian(K,*parm),lw=3,c='g',ls='--',label='Gaussian background')
				#ax = plt.axes()
				#ax.set_xlabel(r'$K_{\parallel}$ ($\AA^{-1}$)',fontsize=20)
				#ax.set_ylabel('Intensity (arb. units)',fontsize=20)
				#plt.legend(loc='upper right')
				#mng = plt.get_current_fig_manager()
				#mng.window.state('zoomed')
				optim9_modified = np.append([nimg*1.8,Kp/SF],optim9.x)
				fitresults ='\t'.join(str(np.round(e,decimals=2)).ljust(12) for e in optim9_modified)+'\n'
				output.write(fitresults)

			else:
				guess9 = [3e5,3e5,3e5,3e5,0.8*max_int,3e5,3e5,3e5,3e5,-8,-6.2,-4,-1.2,0,1.2,4,6.2,8,1,1,1,1,1,1,1,1,1,0]
				optim9 = least_squares(errfunc9,guess9[:],
					bounds = ([0,0,0,0,0.4*max_int,0,0,0,0,\
					guess9[9]-C_tol,guess9[10]-C_tol,guess9[11]-C_tol,guess9[12]-C_tol,guess9[13]-C_tol,guess9[14]-C_tol,guess9[15]-C_tol,guess9[16]-C_tol,guess9[17]-C_tol,\
					width_minimum,width_minimum,width_minimum,width_minimum,width_minimum,width_minimum,width_minimum,width_minimum,width_minimum,-np.inf],\
					[np.inf,np.inf,np.inf,np.inf,np.inf,np.inf,np.inf,np.inf,np.inf,\
					guess9[9]+C_tol,guess9[10]+C_tol,guess9[11]+C_tol,guess9[12]+C_tol,guess9[13]+C_tol,guess9[14]+C_tol,guess9[15]+C_tol,guess9[16]+C_tol,guess9[17]+C_tol,\
					width_maximum,width_maximum,width_maximum,width_maximum,width_maximum,width_maximum,width_maximum,width_maximum,width_maximum,np.inf]),
					x_scale=[5e5,5e5,5e5,5e5,5e5,5e5,5e5,5e5,5e5,5,5,5,5,5,5,5,5,5,1,1,1,1,1,1,1,1,1,1e4],
					ftol=f_tol,
					xtol=x_tol,
					args=(K,profile[:,0]),
					verbose=1)

				plt.plot(K,profile,lw=5,c='k',label='Measurement')
				plt.plot(K,nine_gaussians(K,*optim9.x),lw=3,c='r',ls='-',label='fit of 9 Gaussians')
				for optimindex in range(9):
					parm = np.append(optim9.x[optimindex:27:9],optim9.x[27])
					plt.plot(K,gaussian(K,*parm),lw=3,c='b',ls='--',label='individual fits')
				plt.legend(loc='upper right')

		sys.stdout.write('\r')
		sys.stdout.write("%d%%" % ((nimg+1-50)/ImgRange*100))
		sys.stdout.flush()
		sleep(0.25)

	plt.show()
	output.close()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == '__main__':
	#execute only if run as a script
	main()
