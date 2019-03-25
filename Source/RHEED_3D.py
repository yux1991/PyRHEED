import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches 
import matplotlib.gridspec as gridspec
import matplotlib.ticker as ticker
import matplotlib
import rawpy
import scipy.ndimage
import glob

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

#import image
img_path_MAC = '/Users/yuxiang/Documents/RHEED/04032018_G_on_SiC/20_keV_47_uA/*.nef' 
img_path_PC = 'C:/Users/Yu Xiang/Desktop/CdTe_GaAs100_011013/*.nef'
#create an array that stores all image pathes
image_list = []
for filename in glob.glob(img_path_PC):
	image_list.append(filename)
	
#define the area that we do area integral
class Area: 	
	x1,y1 = 200,400
	x2,y2 = 2300,400
	width = 50

	def ShowImage(self,img):
		nonlocal x1,y1,x2,y2,width
		gs = gridspec.GridSpec(4,6)
		self.img = img
		#plot the image
		ax1=plt.subplot(gs[:,:-2])

		im=plt.imshow(self.img,cmap = plt.cm.jet)
		plt.axis([0,2600,1300,0])
		#draw the line
		plt.plot([x1,x2],[y1,y2],'ro-')
		#draw the rectangle
		p=patches.Rectangle((x1,y1-width/2),(x2-x1),width,fill=False,ls='--',ec='g')
		plt.colorbar(im,orientation = 'horizontal',format = '%4d')
		ax1.add_patch(p)
		ax1.set_xlabel('K_parallel')
		ax1.set_ylabel('K_perpendicular')

		#plot the line profile
		ax2=plt.subplot(gs[:-2,4:])
		plt.plot(x/SF,profile)
		plt.yscale('linear')
		ax2.set_xlabel('K_parallel')
		ax2.set_ylabel('Intensity')
		ax2.ticklabel_format(style='sci',scilimits=(0,0),axis='both',format = '%2.1f')

		#plot the area integral
		ax3=plt.subplot(gs[2:,4:])
		plt.plot(np.linspace(x1,x2,num=x2-x1),np.transpose(AreaIntegral))
		plt.yscale('linear')
		ax3.set_xlabel('K_parallel')
		ax3.set_ylabel('Intensity')
		ax3.ticklabel_format(style='sci',scilimits=(0,0),axis='both',format = '%2.1f')

		plt.tight_layout()
		plt.show()

#define a function to get line profile
def LP(n,SF):

	"""
	n: image index
	SF: scale factor, in the unit of pixel/Angstron^-1
	"""
	img_raw = rawpy.imread(image_list[n]) #read the raw image
	img_rgb = img_raw.postprocess(demosaic_algorithm=rawpy.DemosaicAlgorithm.AHD,output_bps = 16) #convert to RGB image
	img_bw = (0.21*img_rgb[:,:,0])+(0.72*img_rgb[:,:,1])+(0.07*img_rgb[:,:,2]) #convert to grayscale
	img = img_bw[1350:2650,500:3100] #the region that contains the RHEED pattern

	#x,y = np.linspace(Area.x1,Area.x2,nos),np.linspace(Area.y1,Area.y2,nos)
	#profile = scipy.ndimage.map_coordinates(img,np.vstack((y,x)),order=0,cval = 100000.)

	AreaIntegral = np.sum(img[Area.y1-Area.width/2:Area.y1+Area.width/2,Area.x1:Area.x2],axis=0,keepdims=1)
	P = Area()
	P.ShowImage(img)
	return AreaIntegral

for i in range(6):
	AreaIntegral = LP(n=i,SF=80.75)
	ax=plt.subplot(1,6,i+1)
	plt.plot(np.linspace(Area.x1,Area.x2,num=Area.x2-Area.x1),np.transpose(AreaIntegral))
	plt.yscale('linear')
	ax.set_xlabel('K_parallel')
	ax.set_ylabel('Intensity')
	ax.ticklabel_format(style='sci',scilimits=(0,0),axis='both',format = '%2.1f')

plt.show()

