from collections import Counter
import glob
import itertools
import math
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas
import PIL.Image as pilImage
import PIL.ImageQt as pilQtImage
import rawpy
import random
import sys
import time
from astropy.modeling.models import Voigt1D
from io import StringIO
from lxml import etree as ET
from math import pi as Pi
from matplotlib.patches import Polygon as matPolygon
from matplotlib.collections import PatchCollection
from process_monitor import Monitor
try:
    import pycuda.compiler as comp
    import pycuda.driver as drv
    CUDA_EXIST = True
except:
    CUDA_EXIST = False
from pymatgen.io.cif import CifParser
from pymatgen.core import sites as pgSites
from pymatgen.core import structure as pgStructure
from pymatgen.core import periodic_table
from PyQt6 import QtGui,QtCore, QtWidgets
from scipy.optimize import least_squares
from scipy.spatial import ConvexHull
from scipy.spatial import Voronoi
from scipy.spatial import voronoi_plot_2d
from scipy.spatial import cKDTree
from scipy.stats import rv_discrete
from scipy.interpolate import LinearNDInterpolator
from scipy.interpolate import NearestNDInterpolator
from shapely.geometry import LineString
from shapely.geometry import MultiPoint 
from shapely.geometry import Point
from shapely.geometry import Polygon
from shapely.ops import unary_union
from sys import getsizeof

class Image(object):

    def __init__(self):
        super(Image,self).__init__()
        self.supportedRawFormats = {'.3fr','.ari','.arw','.srf','.sr2','.bay','.cri','.crw','.cr2','.cr3','.cap','.iiq','.eip', \
                            '.dcs','.dcr','.drf','.k25','.kdc','.dng','.erf','.fff','.mef','.mdc','.mos','.mrw','.nef', \
                            '.nrw','.orf','.pef','.ptx','.pxn','.r3d','.raf','.raw','.rw2','.rwl','.rwz','.srw','.x3f', \
                            '.3FR','.ARI','.ARW','.SRF','.SR2','.BAY','.CRI','.CRW','.CR2','.CR3','.CAP','.IIQ','.EIP', \
                            '.DCS','.DCR','.DRF','.K25','.KDC','.DNG','.ERF','.FFF','.MEF','.MDC','.MOS','.MRW','.NEF', \
                            '.NRW','.ORF','.PEF','.PTX','.PXN','.R3D','.RAF','.RAW','.RW2','.RWL','.RWZ','.SRW','.X3F'}
        self.supportedImageFormats = {'.bmp','.eps','.gif','.icns','.ico','.im','.jpg','.jpeg','.jpeg2000','.msp','.pcx',\
                                      '.png','.ppm','.sgi','.tiff','.tif','.xbm','.BMP','.EPS','.GIF','.ICNS','.ICO','.IM','.JPG','.JPEG','.JPEG2000','.MSP','.PCX',\
                                      '.PNG','.PPM','.SGI','.TIFF','.TIF','.XBM'}

    def get_image(self,bit_depth,img_path,EnableAutoWB, Brightness, UserBlack, image_crop,flipud=False,fliplr=False):
        pathExtension = os.path.splitext(img_path)[1]
        if pathExtension in self.supportedRawFormats:
            img_raw = rawpy.imread(img_path)
            img_rgb = img_raw.postprocess(demosaic_algorithm=rawpy.DemosaicAlgorithm.AHD, output_bps = bit_depth, use_auto_wb = EnableAutoWB,bright=Brightness/100,user_black=UserBlack)
            img_bw = (0.21*img_rgb[:,:,0])+(0.72*img_rgb[:,:,1])+(0.07*img_rgb[:,:,2])
            crop0 = max(0,image_crop[0])
            crop1 = min(len(img_bw)-1,image_crop[1])
            crop2 = max(0,image_crop[2])
            crop3 = min(len(img_bw[0])-1,image_crop[3])
            img_array = img_bw[crop0:crop1,crop2:crop3]
            if flipud:
                img_array = np.flipud(img_array)
            if fliplr:
                img_array = np.fliplr(img_array)
            if bit_depth == 16:
                img_array = np.uint8(img_array/256)
            if bit_depth == 8:
                img_array = np.uint8(img_array)
            qImg = QtGui.QImage(img_array,img_array.shape[1],img_array.shape[0],img_array.shape[1], QtGui.QImage.Format.Format_Grayscale8)
            return qImg, img_array
        elif pathExtension in self.supportedImageFormats:
            img = pilImage.open(img_path)
            if flipud:
                img = img.transpose(pilImage.FLIP_TOP_BOTTOM)
            if fliplr:
                img = img.transpose(pilImage.FLIP_LEFT_RIGHT)
            if img.mode == 'RGB':
                img_rgb = np.fromstring(img.tobytes(),dtype=np.uint8)
                img_rgb = img_rgb.reshape((img.size[1],img.size[0],3))
                img_array = (0.21*img_rgb[:,:,0])+(0.72*img_rgb[:,:,1])+(0.07*img_rgb[:,:,2])
                qImg = QtGui.QImage(np.uint8(img_array),img_array.shape[1],img_array.shape[0],img_array.shape[1], QtGui.QImage.Format.Format_Grayscale8)
            elif img.mode == 'RGBA':
                img_rgba = np.fromstring(img.tobytes(),dtype=np.uint8)
                img_rgb = img_rgba.reshape((img.size[1], img.size[0], 4))[:, :, :3]
                img_rgb = img_rgb.reshape((img.size[1],img.size[0],3))
                img_array = (0.21*img_rgb[:,:,0])+(0.72*img_rgb[:,:,1])+(0.07*img_rgb[:,:,2])
                qImg = QtGui.QImage(np.uint8(img_array),img_array.shape[1],img_array.shape[0],img_array.shape[1], QtGui.QImage.Format.Format_Grayscale8)
            elif img.mode == 'L':
                img_array = np.array(img)
                qImg = pilQtImage.ImageQt(img)
            elif img.mode == 'P':
                img_array = np.array(img.convert(mode='L'))
                qImg = pilQtImage.ImageQt(img)
            else:
                self.raise_error("Wrong format!")
                return None, None
            return qImg, img_array

    def get_line_scan(self,start,end,img,scale_factor,normalize_to_img_max=True):
        x0,y0,x1,y1 = start.x(),start.y(),end.x(),end.y()
        K_length = max(int(abs(x1-x0)+1),int(abs(y1-y0)+1))
        Kx = np.linspace(x0,min(x1,len(img[0])-1),K_length)
        Ky = np.linspace(y0,min(y1,len(img)-1),K_length)
        LineScanIntensities = np.zeros(len(Kx))
        for i in range(0,len(Kx)):
            try:
                LineScanIntensities[i] = img[int(Ky[i]),int(Kx[i])]
            except:
                pass
        LineScanRadius = np.linspace(0,math.sqrt((x1-x0)**2+(y1-y0)**2),len(Kx))
        normalization_factor = np.amax(np.amax(img)) if normalize_to_img_max else 1
        return LineScanRadius/scale_factor,LineScanIntensities/normalization_factor

    def get_integral(self,start,end,width,img,scale_factor,normalize_to_img_max=True):
        x0,y0,x1,y1 = start.x(),start.y(),end.x(),end.y()
        K_length = max(int(abs(x1-x0)+1),int(abs(y1-y0)+1))
        int_width = int(width)
        Kx = np.linspace(x0,min(x1,len(img[0])-int_width-1),K_length)
        Ky = np.linspace(y0,min(y1,len(img)-int_width-1),K_length)
        LineScanIntensities = np.zeros(len(Kx))
        LineScanRadius = np.linspace(0,math.sqrt((x1-x0)**2+(y1-y0)**2),len(Kx))
        if y1 == y0:
            for i in range (0,len(Kx)): 
                try:
                    LineScanIntensities[i] = np.sum(img[int(Ky[i])-int_width:int(Ky[i])+\
                                        int_width,int(Kx[i])])
                except:
                    pass
        elif x1 == x0:
            for i in range (0,len(Kx)): 
                try:
                    LineScanIntensities[i] = np.sum(img[int(Ky[i]),int(Kx[i])-int_width:\
                                        int(Kx[i])+int_width])
                except:
                    pass
        else:
            slope =(x0-x1)/(y1-y0)
            if abs(slope) > 1:
                try:
                    index = np.asarray([[np.linspace(Ky[i]-int_width,Ky[i]+int_width+1,2*int_width+1),\
                                     np.linspace(Kx[i]-int_width/slope,Kx[i]+(int_width+1)/slope,2*int_width+1)] for i in range(len(Kx))],dtype=int)
                except:
                    pass
            else:
                try:
                    index = np.asarray([[np.linspace(Ky[i]-int_width*slope,Ky[i]+(int_width+1)*slope,2*int_width+1),\
                                     np.linspace(Kx[i]-int_width,Kx[i]+int_width+1,2*int_width+1)] for i in range(len(Kx))],dtype=int)
                except:
                    pass
            try:
                LineScanIntensities = np.sum([img[index[i,0,:],index[i,1,:]] for i in range(len(Kx))],axis=1)
            except:
                pass
        normalization_factor = np.amax(np.amax(img)) if normalize_to_img_max else 1
        return LineScanRadius/scale_factor,LineScanIntensities/2/width/normalization_factor

    def get_chi_scan(self,center,radius,width,chiRange,tilt,img,chiStep=1,normalize_to_img_max=True):
        x0,y0 = center.x(),center.y()
        if int(chiRange/chiStep)>2:
            ChiTotalSteps = int(chiRange/chiStep)
        else:
            ChiTotalSteps = 2
        ChiAngle = np.linspace(-chiRange/2-tilt+90,chiRange/2-tilt+90,ChiTotalSteps+1)
        ChiAngle2 = np.linspace(-chiRange/2,chiRange/2,ChiTotalSteps+1)
        x1 = x0 + (radius+width)*np.cos(ChiAngle[1]*np.pi/180)
        y1 = y0 + (radius+width)*np.sin(ChiAngle[1]*np.pi/180)
        x2 = x0 + (radius-width)*np.cos(ChiAngle[1]*np.pi/180)
        y2 = y0 + (radius-width)*np.sin(ChiAngle[1]*np.pi/180)
        x3 = x0 + (radius-width)*np.cos(ChiAngle[0]*np.pi/180)
        y3 = y0 + (radius-width)*np.sin(ChiAngle[0]*np.pi/180)
        x4 = x0 + (radius+width)*np.cos(ChiAngle[0]*np.pi/180)
        y4 = y0 + (radius+width)*np.sin(ChiAngle[0]*np.pi/180)
        indices = np.array([[0,0]])
        cit = 0
        if ChiAngle[0] <= 90. and ChiAngle[0+1] > 90.:
            y5 = y0 + radius + width
        else:
            y5 = 0
        for i in range(int(np.amin([y1,y2,y3,y4])),int(np.amax([y1,y2,y3,y4,y5]))+1):
            for j in range(int(np.amin([x1,x2,x3,x4])),int(np.amax([x1,x2,x3,x4]))+1):
                if (j-x0)**2+(i-y0)**2 > (radius-width)**2 and\
                   (j-x0)**2+(i-y0)**2 < (radius+width)**2 and\
                   (j-x0)/np.sqrt((i-y0)**2+(j-x0)**2) < np.cos(ChiAngle[0]*np.pi/180) and\
                   (j-x0)/np.sqrt((i-y0)**2+(j-x0)**2) > np.cos(ChiAngle[1]*np.pi/180):
                       indices = np.append(indices,[[i,j]],axis=0)
                       cit+=1
        RotationTensor = np.array([[[-np.sin((theta-ChiAngle[0])*np.pi/180),np.cos((theta-ChiAngle[0])*np.pi/180)],\
                                    [np.cos((theta-ChiAngle[0])*np.pi/180), np.sin((theta-ChiAngle[0])*np.pi/180)]] for theta in ChiAngle])
        ImageIndices =np.tensordot(RotationTensor,(indices[1:-1]-[y0,x0]).T,axes=1).astype(int)
        try:
            ChiProfile = np.sum([img[ImageIndices[i,1,:]+int(y0),ImageIndices[i,0,:]+int(x0)] for i in range(ChiTotalSteps+1)], axis=1)/cit
        except IndexError:
            ChiProfile = []
        normalization_factor = np.amax(np.amax(img)) if normalize_to_img_max else 1
        return np.flip(ChiAngle2,axis=0),ChiProfile/normalization_factor

    def raise_error(self,message):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        msg.setEscapeButton(QtWidgets.QMessageBox.StandardButton.Close)
        msg.exec()

    def raise_attention(self,information):
        info = QtWidgets.QMessageBox()
        info.setIcon(QtWidgets.QMessageBox.Icon.Information)
        info.setText(information)
        info.setWindowTitle("Information")
        info.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        info.setEscapeButton(QtWidgets.QMessageBox.StandardButton.Close)
        info.exec()

class FitFunctions(object):

    def __init__(self):
        super(FitFunctions,self).__init__()

    def translational_antiphase_domain_model_intensity_using_h(self,h,gamma):
        result =  (1-np.multiply(self.boundary_structure_factor_using_h(h,gamma), self.boundary_structure_factor_using_h(h,gamma)))/\
               (1+np.multiply(self.boundary_structure_factor_using_h(h,gamma), self.boundary_structure_factor_using_h(h,gamma))\
               -2*np.multiply(self.boundary_structure_factor_using_h(h,gamma),np.cos(2*np.pi*h)))
        return np.where(np.isnan(result),100,result)

    def translational_antiphase_domain_model_intensity_using_S(self,S,a,gamma,height=1,offset=0):
        result =  (1-np.multiply(self.boundary_structure_factor_using_S(S,a,gamma), self.boundary_structure_factor_using_S(S,a,gamma)))/ \
                  (1+np.multiply(self.boundary_structure_factor_using_S(S,a,gamma), self.boundary_structure_factor_using_S(S,a,gamma)) \
                   -2*np.multiply(self.boundary_structure_factor_using_S(S,a,gamma),np.cos(S*a*np.cos(np.pi/6))))
        return result*height+offset

    def translational_antiphase_domain_model_intensity_2D(self,h,k,gamma_a,gamma_b):
        return np.multiply(self.translational_antiphase_domain_model_intensity_using_h(h,gamma_a),\
                           self.translational_antiphase_domain_model_intensity_using_h(k,gamma_b))

    def translational_antiphase_domain_model_intensity_2D_four_indices(self,h,k,i,gamma_a,gamma_b,gamma_c):
        return np.multiply(np.multiply(self.translational_antiphase_domain_model_intensity_using_h(h,gamma_a),\
                           self.translational_antiphase_domain_model_intensity_using_h(k,gamma_b)),\
                           self.translational_antiphase_domain_model_intensity_using_h(i,gamma_c))

    def translational_antiphase_domain_model_intensity_2D_without_approximation(self,h,k,gamma_a,gamma_b,m1,m2):
        result = np.full(h.shape,0).astype('complex128')
        for it1 in range(-m1,m1+1):
            for it2 in range(-m2,m2+1):
                result += (np.multiply(np.multiply(np.power(self.boundary_structure_factor_using_h(h,gamma_a),m1),\
                                    np.power(self.boundary_structure_factor_using_h(k,gamma_b),m2)),\
                        np.exp(1j*(it1*2*np.pi*h+it2*2*np.pi*k))))
        return np.absolute(result)

    def HWHM_of_translational_antiphase_domain_model(self,h,gamma,a):
        alpha = (4*self.boundary_structure_factor_using_h(h,gamma) - np.multiply(self.boundary_structure_factor_using_h(h,gamma),\
                    self.boundary_structure_factor_using_h(h,gamma))-1)/(2*self.boundary_structure_factor_using_h(h,gamma))
        return 1/2/a*np.arccos(alpha)

    def boundary_structure_factor_using_h(self,h,gamma):
        sum = h*0
        for n in range(0,45):
            sum += np.cos(2*np.pi*(1+n/45)*h)*self.probability(n,45)
        result = 1-gamma+gamma*sum
        return result

    def boundary_structure_factor_using_S(self,S,a,gamma):
        sum = S*0
        prob = 0
        for n in range(0,45):
            sum += np.cos((1+n/45)*S*a*np.cos(np.pi/6))*self.probability(n,45)
            prob += self.probability(n,45)
        result = 1-gamma+gamma*sum
        return result

    def probability(self,n,A):
        total = 0
        for i in range(A, 2*A):
            total+=1/i**2
        return 1/(n+A)**2/total

    def gaussian(self,x,height, center,FWHM,offset=0):
        if FWHM == 0:
            FWHM = 0.001
        return height/(FWHM*math.sqrt(math.pi/(4*math.log(2))))*np.exp(-4*math.log(2)*(x - center)**2/(FWHM**2))+offset

    def voigt(self,x,center,amplitude,fwhm_L,fwhm_G,offset=0):
        v1 = Voigt1D(center,amplitude,fwhm_L,fwhm_G)
        return v1(x)+offset
    
    def get_multiple_gaussians(self,n):
        def gaussian(x,height, center,FWHM):
            if FWHM == 0:
                FWHM = 0.001
            return height/(FWHM*math.sqrt(math.pi/(4*math.log(2))))*np.exp(-4*math.log(2)*(x - center)**2/(FWHM**2))

        def multi_gaussians(x,*args):
            nonlocal n
            offset = args[3*n]
            for i in range(n):
                offset+=gaussian(x,args[i],args[i+n],args[i+2*n])
            return offset
        return multi_gaussians

    def get_multiple_voigts(self,n):
        def voigt(x,center,amplitude,fwhm_L,fwhm_G):
            v1 = Voigt1D(center,amplitude,fwhm_L,fwhm_G)
            return v1(x)
        def multiple_voigts(x,*args):
            nonlocal n
            offset = args[4*n]
            for i in range(n):
                offset+=voigt(x,args[i],args[i+n],args[i+2*n],args[i+3*n])
            return offset
        return multiple_voigts

    def errfunc(self,p,x0,y0):
        cost = self.fitFunction(x0,*p)-y0
        self.cost_values.append(sum(map(lambda x:np.abs(x),cost)))
        return cost

    def get_fit(self,x,y,numberOfPeaks,includeBackground,function,guess,bounds,FTol,XTol,GTol,method,loss):
        if includeBackground == 2:
            numberOfPeaks+=1
        if function == 'Gaussian':
            self.fitFunction = self.get_multiple_gaussians(numberOfPeaks)
        elif function == 'Voigt':
            self.fitFunction = self.get_multiple_voigts(numberOfPeaks)
        self.cost_values=[]
        with Capture() as output:
            optim = least_squares(fun=self.errfunc,x0=guess,\
                    bounds=bounds,method=method,loss=loss, ftol=FTol,xtol=XTol,gtol=GTol,args=(x,y),verbose=2)
        return optim, self.cost_values, str(output)

    def test(self):
        raw_3d = pandas.read_csv(filepath_or_buffer="c:/users/yux20/documents/05042018 MoS2/3D_Map_04162019.txt",sep=" ",names=["x","y","z","intensity"],na_values="NaN")
        length = raw_3d.index[-1]+1
        x_min,x_max = raw_3d["x"].min(), raw_3d["x"].max()
        y_min,y_max = raw_3d["y"].min(), raw_3d["y"].max()
        z_min,z_max = raw_3d["z"].min(), raw_3d["z"].max()

        nx,ny = 1000,1000
        nz = int((z_max-z_min)/(x_max-x_min)*nx)

        x_range = np.linspace(x_min,x_max,nx)
        y_range = np.linspace(x_min,x_max,ny)
        z_range = np.linspace(z_min,z_max,nz)

        x,y,z=np.meshgrid(x_range,y_range,z_range)
        subset = range(0,length)
        print("finished meshgrid")

        rawx = raw_3d.iloc[subset,[0]].T.to_numpy()*np.cos(raw_3d.iloc[subset,[1]].T.to_numpy()/np.pi)
        rawy = raw_3d.iloc[subset,[0]].T.to_numpy()*np.sin(raw_3d.iloc[subset,[1]].T.to_numpy()/np.pi)
        rawz = raw_3d.iloc[subset,[2]].T.to_numpy()
        intensity = raw_3d.iloc[subset,[3]].T.to_numpy()
        print("finished converting")

        interp = LinearNDInterpolator(list(zip(rawx[0],rawy[0],rawz[0])),intensity[0])
        print("finished generating interpolation model")
        interp_3d = np.nan_to_num(interp(x,y,z),False)
        print("finished interpolation")
        intensity_sum = np.sum(np.concatenate(interp_3d))
        output = open("c:/users/yux20/documents/05042018 MoS2/interpolated_3D_map.txt",mode='w')
        for i in range(nx):
            for j in range(ny):
                for k in range(nz):
                    print("writting {}, {} ,{}".format(i,j,k))
                    row = "\t".join([str(np.around(x[j][i][k],4)),str(np.around(y[j][i][k],4)),str(np.around(z[j][i][k],4)),str(np.around(interp_3d[j][i][k]/intensity_sum,10))])+"\n"
                    output.write(row)
        output.close()

        #grid_3d = pandas.read_csv(filepath_or_buffer="c:/users/yux20/documents/05042018 MoS2/interpolated_3D_map.txt",sep="\t",names=["x","y","z","probability"])
        #draw = rv_discrete(name='custm',values=(grid_3d.index,grid_3d["probability"]))
        #indices = draw.rvs(size=10000)
        #selected = grid_3d.iloc[indices]
        #r, theta = selected["x"].to_numpy(),selected["y"].to_numpy()
        #fontsize=15
        #figure = plt.figure()
        #ax = figure.add_subplot(111)
        #ax.set_aspect('equal')
        #ax.scatter(r*np.cos(theta/np.pi),r*np.sin(theta/np.pi))
        #ax.set_xlabel('x (\u212B)',fontsize=fontsize)
        #ax.set_ylabel('y (\u212B)',fontsize=fontsize)
        #ax.tick_params(labelsize=fontsize)
        #plt.tight_layout()
        #plt.show()
        

class Capture(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio
        sys.stdout = self._stdout

class Convertor(object):
    def __init__(self):
        super(Convertor,self).__init__()

    def txt2vtp(self,path,type):
        raw_data = np.loadtxt(path)
        if type == "Polar":
            data = np.empty(raw_data.shape)
            data[:,2] = raw_data[:,2]
            data[:,3] = raw_data[:,3]
            data[:,0] = raw_data[:,0]*np.cos((raw_data[:,1])*math.pi/180)
            data[:,1] = raw_data[:,0]*np.sin((raw_data[:,1])*math.pi/180)
        elif type == "Cartesian":
            data = raw_data
        vtkFile = ET.Element('VTKFile')
        vtkFile.set('type', 'PolyData')
        vtkFile.set('version', '0.1')
        vtkFile.set('byte_order', 'LittleEndian')
        polyData = ET.SubElement(vtkFile, 'PolyData')
        piece = ET.SubElement(polyData, 'Piece')
        piece.set('NumberOfPoints', str(np.shape(data)[0]))
        piece.set('NumberOfVerts', str(np.shape(data)[0]))
        pointData = ET.SubElement(piece, 'PointData')
        pointData.set('Scalars', 'Intensity')
        intensity = ET.SubElement(pointData, 'DataArray')
        intensity.set('type', 'Float32')
        intensity.set('Name', 'Intensity')
        intensity.set('format', 'ascii')
        intensity.set('RangeMin', str(np.amin(data[:,3])))
        intensity.set('RangeMax', str(np.amax(data[:,3])))
        intensity.text = ' '.join(map(str, data[:,3]))
        cellData = ET.SubElement(piece, 'CellData')
        points = ET.SubElement(piece, 'Points')
        coordinates = ET.SubElement(points, 'DataArray')
        coordinates.set('type', 'Float32')
        coordinates.set('Name', 'Points')
        coordinates.set('NumberOfComponents', '3')
        coordinates.set('format', 'ascii')
        coordinates.set('RangeMin', str(np.amin(data[:, 0:3])))
        coordinates.set('RangeMax', str(np.amax(data[:, 0:3])))
        coordinates.text = ' '.join(map(str, data[:, 0:3].flatten()))
        verts = ET.SubElement(piece, 'Verts')
        connect = ET.SubElement(verts, 'DataArray')
        connect.set('type', 'Int32')
        connect.set('Name', 'connectivity')
        connect.set('format', 'ascii')
        connect.set('RangeMin', '0')
        connect.set('RangeMax', str(np.shape(data)[0]-1))
        connect.text = ' '.join(map(str, range(np.shape(data)[0])))
        offsets = ET.SubElement(verts, 'DataArray')
        offsets.set('type', 'Int32')
        offsets.set('Name', 'offsets')
        offsets.set('format', 'ascii')
        offsets.set('RangeMin', '1')
        offsets.set('RangeMax', str(np.shape(data)[0]))
        offsets.text = ' '.join(map(str, range(1, np.shape(data)[0]+1)))
        filename = os.path.dirname(path)+'/'+os.path.basename(path).split(".")[0]+".vtp"
        tree = ET.ElementTree(vtkFile)
        tree.write(open(filename, 'wb'))

    def mtx2vtp(self,dir,name,matrix,KRange,N_para,N_perp,specification,species,save_vtp = True):
        x_linear = np.linspace(KRange[0][0],KRange[0][1],N_para)
        y_linear = np.linspace(KRange[1][0],KRange[1][1],N_para)
        z_linear = np.linspace(KRange[2][0],KRange[2][1],N_perp)
        max_intensity = np.amax(np.amax(np.amax(matrix)))
        Kx,Ky,Kz = np.meshgrid(x_linear,y_linear,z_linear)
        data = np.full((N_para*N_para*N_perp,4),-1.11,dtype='float64')
        for i, j, k in itertools.product(list(range(N_para)),list(range(N_para)),list(range(N_perp))):
            data[i*N_para*N_perp+j*N_perp+k,0] = Kx[i,j,k]
            data[i*N_para*N_perp+j*N_perp+k,1] = Ky[i,j,k]
            data[i*N_para*N_perp+j*N_perp+k,2] = Kz[i,j,k]
            data[i*N_para*N_perp+j*N_perp+k,3] = matrix[i,j,k]/max_intensity
        vtkFile = ET.Element('VTKFile')
        vtkFile.set('type', 'PolyData')
        vtkFile.set('version', '0.1')
        vtkFile.set('byte_order', 'LittleEndian')
        polyData = ET.SubElement(vtkFile, 'PolyData')
        piece = ET.SubElement(polyData, 'Piece')
        piece.set('NumberOfPoints', str(np.shape(data)[0]))
        piece.set('NumberOfVerts', str(np.shape(data)[0]))
        pointData = ET.SubElement(piece, 'PointData')
        pointData.set('Scalars', 'Intensity')
        intensity = ET.SubElement(pointData, 'DataArray')
        intensity.set('type', 'Float64')
        intensity.set('Name', 'Intensity')
        intensity.set('format', 'ascii')
        intensity.set('RangeMin', str(np.amin(data[:,3])))
        intensity.set('RangeMax', str(np.amax(data[:,3])))
        intensity.text = ' '.join(map(str, data[:,3]))
        cellData = ET.SubElement(piece, 'CellData')
        points = ET.SubElement(piece, 'Points')
        coordinates = ET.SubElement(points, 'DataArray')
        coordinates.set('type', 'Float64')
        coordinates.set('Name', 'Points')
        coordinates.set('NumberOfComponents', '3')
        coordinates.set('format', 'ascii')
        coordinates.set('RangeMin', str(np.amin(data[:, 0:3])))
        coordinates.set('RangeMax', str(np.amax(data[:, 0:3])))
        coordinates.text = ' '.join(map(str, data[:, 0:3].flatten()))
        verts = ET.SubElement(piece, 'Verts')
        connect = ET.SubElement(verts, 'DataArray')
        connect.set('type', 'Int32')
        connect.set('Name', 'connectivity')
        connect.set('format', 'ascii')
        connect.set('RangeMin', '0')
        connect.set('RangeMax', str(np.shape(data)[0]-1))
        connect.text = ' '.join(map(str, range(np.shape(data)[0])))
        offsets = ET.SubElement(verts, 'DataArray')
        offsets.set('type', 'Int32')
        offsets.set('Name', 'offsets')
        offsets.set('format', 'ascii')
        offsets.set('RangeMin', '1')
        offsets.set('RangeMax', str(np.shape(data)[0]))
        offsets.text = ' '.join(map(str, range(1, np.shape(data)[0]+1)))
        if save_vtp:
            filename = dir+'/'+name+".vtp"
            tree = ET.ElementTree(vtkFile)
            tree.write(open(filename, 'wb'))
        information = {}
        information['Kx_min'] = KRange[0][0]
        information['Kx_max'] = KRange[0][1]
        information['Ky_min'] = KRange[1][0]
        information['Ky_max'] = KRange[1][1]
        information['Kz_min'] = KRange[2][0]
        information['Kz_max'] = KRange[2][1]
        information['N_para'] = N_para
        information['N_perp'] = N_perp
        output = open(dir+'/'+name+".txt",mode='w')
        output.write('Time: \n')
        output.write(QtCore.QDateTime.currentDateTime().toString("MMMM d, yyyy  hh:mm:ss ap")+"\n\n")
        output.write('Real space specification: \n')
        output.write(str(specification))
        output.write('\n\n')
        output.write('Reciprocal space specification: \n')
        output.write(str(information))
        output.write('\n\n')
        output.write('Atomic species: \n')
        output.write(str(species))
        output.write('\n\n')
        results = "\n".join("\t".join(str(data[i,j]) for j in range(4)) for i in range(N_para*N_para*N_perp))
        output.write(results)
        output.close()

class Diffraction(object):

    def __init__(self):
        super(Diffraction,self).__init__()

    def G_matrix(self,a,b,c,alpha,beta,gamma):
        return np.array([[a**2, a*b*np.cos(gamma/180*np.pi), a*c*np.cos(beta/180*np.pi)],
                        [a*b*np.cos(gamma/180*np.pi), b**2, b*c*np.cos(alpha/180*np.pi)],
                        [a*c*np.cos(beta/180*np.pi), b*c*np.cos(alpha/180*np.pi), c**2]])

    def G_star(self,a,b,c,alpha,beta,gamma):
        return 2*np.pi*np.linalg.inv(self.G_matrix(a,b,c,alpha,beta,gamma))

    def conversion_matrix(self,a,b,c,alpha,beta,gamma):
        c1 = c*np.cos(beta/180*np.pi)
        c2 = c*(np.cos(alpha/180*np.pi)-np.cos(gamma/180*np.pi)*np.cos(beta/180*np.pi))/np.sin(gamma/180*np.pi)
        c3 = np.sqrt(c**2-c1**2-c2**2)
        return np.array([[a, b*np.cos(gamma/180*np.pi), c1],
                         [0, b*np.sin(gamma/180*np.pi), c2],
                         [0, 0,                         c3]])

    def is_permitted(self,h,k,l,space_group_number):
        if space_group_number == 167:
            return ((-h+k+l)%3 == 0 and h!=-k) or ((h+l)%3==0 and l%2==0 and h==-k)
        elif space_group_number == 216:
            return (h+k)%2==0 and (k+l)%2==0 and (h+l)%2==0

class ReciprocalSpaceMap(QtCore.QObject):

    PROGRESS_ADVANCE = QtCore.pyqtSignal(int,int,int)
    PROGRESS_END = QtCore.pyqtSignal()
    CONNECT_TO_CANVAS = QtCore.pyqtSignal()
    UPDATE_LOG = QtCore.pyqtSignal(str)
    UPDATE_CHART = QtCore.pyqtSignal(np.ndarray,np.ndarray,str)
    FILE_SAVED = QtCore.pyqtSignal(str)
    FINISHED = QtCore.pyqtSignal()
    SET_TITLE = QtCore.pyqtSignal(str)
    DRAW_LINE_REQUESTED = QtCore.pyqtSignal(QtCore.QPointF,QtCore.QPointF,bool)
    DRAW_RECT_REQUESTED = QtCore.pyqtSignal(QtCore.QPointF,QtCore.QPointF,float,bool)
    REFRESH_CANVAS = QtCore.pyqtSignal(str,list)
    ERROR = QtCore.pyqtSignal(str)
    ATTENTION = QtCore.pyqtSignal(str)
    ABORTED = QtCore.pyqtSignal()

    def __init__(self,status,path,default,IsPoleFigure,azimuthRange,normalizationMethod,centralisationMethod,IsSaveResult,Is2D,IsCartesian,startIndex,endIndex,analysisRange,destination,saveFileName,fileType,group,enableSync=False,sleepTime=0,offsetFilePath=''):
        super(ReciprocalSpaceMap,self).__init__()
        self.path = path
        self.status = status
        self.windowDefault = default
        self.startIndex = startIndex
        self.endIndex = endIndex
        self.analysisRange = analysisRange
        self.currentDestination = destination
        self.saveFileName = saveFileName
        self.fileType = fileType
        self.IsPoleFigure = IsPoleFigure
        self.azimuthRange = azimuthRange
        self.normalizationMethod = normalizationMethod
        self.centralisationMethod = centralisationMethod
        self.IsSaveResult = IsSaveResult
        self.Is2D = Is2D
        self.IsCartesian = IsCartesian
        self.group = group
        self.image_worker = Image()
        self.convertor_worker = Convertor()
        self.enableSync = enableSync
        self.sleepTime = max(sleepTime,1)
        self._bit_depth = 16
        self._abort = False
        self.offsetFilePath = offsetFilePath

    def run(self):
        image_list = []
        autoWB = self.status["autoWB"]
        brightness = self.status["brightness"]
        blackLevel = self.status["blackLevel"]
        mode = self.status["mode"]
        use_external_offset = False
        if os.path.isfile(self.offsetFilePath):
            self.offset_df = pandas.read_excel(self.offsetFilePath, index_col=0)
            use_external_offset = True
        VS = int(self.windowDefault["vs"])
        HS = int(self.windowDefault["hs"])
        image_crop = [1200+VS,2650+VS,500+HS,3100+HS]
        scale_factor = self.status["sensitivity"]/np.sqrt(self.status["energy"])
        if (mode == "arc" and self.IsPoleFigure):
            if self.status["startX"] == "" or self.status["startY"] == "" or self.status["width"] =="":
                self.UPDATE_LOG.emit("ERROR: Please choose the region!")
                self.ERROR.emit("Please choose the region!")
                QtCore.QCoreApplication.processEvents()
            else:
                self.CONNECT_TO_CANVAS.emit()
                start = QtCore.QPointF()
                start.setX(self.status["startX"])
                start.setY(self.status["startY"])
                radius = self.status["radius"]
                chiRange = self.status["chiRange"]
                tiltAngle = self.status["tiltAngle"]
                width = self.status["width"]*scale_factor
                chiStep = 1
                for filename in glob.glob(self.path):
                    image_list.append(filename)
                self.endIndex = min(self.endIndex, len(image_list)-1)
                map_2D360=np.array([0,0,0])
                map_2D180=np.array([0,0,0])
                self.SET_TITLE.emit("Chi Scan at R = {:3.2f} \u212B\u207B\u00B9".format(radius))
                QtCore.QCoreApplication.processEvents()
                for nimg in range(self.startIndex,self.endIndex+1):
                    if use_external_offset:
                        offset_x = int(self.offset_df.at[nimg,'offset_x']*scale_factor)
                        offset_y = int(self.offset_df.at[nimg,'offset_y']*scale_factor)
                        image_crop = [1200+VS+offset_y,2650+VS+offset_y,500+HS+offset_x,3100+HS+offset_x]
                    qImg, img = self.image_worker.get_image(self._bit_depth,image_list[nimg-self.startIndex],autoWB,brightness,blackLevel,image_crop)
                    RC,I = self.image_worker.get_chi_scan(start,radius*scale_factor,width,chiRange,tiltAngle,img,chiStep,normalize_to_img_max=False)
                    if self.enableSync:
                        self.REFRESH_CANVAS.emit(image_list[nimg-self.startIndex],image_crop)
                    Phi360 = np.full(len(RC),nimg*1.8)
                    Phi180 = np.full(len(RC),nimg*1.8)
                    for iphi in range(0,int(len(RC)/2)):
                        Phi360[iphi]=nimg*1.8+180
                    if self.normalizationMethod == 0:
                        normalization_factor = 1
                    elif self.normalizationMethod == 1:
                        normalization_factor = 2**8 - 1
                    elif self.normalizationMethod == 2:
                        normalization_factor = max(I)
                    elif self.normalizationMethod == 3:
                        normalization_factor = np.amax(np.amax(img))
                    map_2D360 = np.vstack((map_2D360,np.vstack((abs(RC),Phi360,I/normalization_factor)).T))
                    map_2D180 = np.vstack((map_2D180,np.vstack((RC,Phi180,I/normalization_factor)).T))
                    if self.azimuthRange == 360:
                        self.UPDATE_CHART.emit(abs(RC),I/normalization_factor,"arc")
                    elif self.azimuthRange == 180:
                        self.UPDATE_CHART.emit(RC,I/normalization_factor,"arc")
                    self.PROGRESS_ADVANCE.emit(0,100,(nimg+1-self.startIndex)*100/(self.endIndex-self.startIndex+1))
                    self.UPDATE_LOG.emit("The file being processed right now is: "+image_list[nimg-self.startIndex])
                    QtCore.QCoreApplication.processEvents()
                    if self.enableSync:
                        time.sleep(self.sleepTime)
                    if self._abort:
                        break
                if not self._abort:
                    if self.azimuthRange == 360:
                        pole_figure = np.delete(map_2D360,0,0)
                    elif self.azimuthRange == 180:
                        pole_figure = np.delete(map_2D180,0,0)
                    self.graphTextPath = self.currentDestination+"/"+self.saveFileName+self.fileType
                    if self.IsSaveResult:
                        np.savetxt(self.graphTextPath,pole_figure,fmt='%4.3f')
                    self.PROGRESS_END.emit()
                    self.UPDATE_LOG.emit("Completed!")
                    self.ATTENTION.emit("Pole Figure Completed!")
                    if self.IsSaveResult:
                        self.FILE_SAVED.emit(self.graphTextPath)
                    QtCore.QCoreApplication.processEvents()
        elif mode == "arc":
            self.ERROR.emit("The type of mapping is not consistent with the chosen region!")
            QtCore.QCoreApplication.processEvents()
        elif self.IsPoleFigure:
            self.ERROR.emit("The type of mapping is not consistent with the chosen region!")
            QtCore.QCoreApplication.processEvents()
        else:
            if self.status["startX"] == "" or self.status["startY"] == "" or self.status["endX"] == "" or \
                    self.status["endY"] == ""\
                or self.status["width"] =="":
                self.UPDATE_LOG.emit("ERROR: Please choose the region!")
                self.ERROR.emit("Please choose the region!")
                QtCore.QCoreApplication.processEvents()
            elif self.status["choosedX"] == "" or self.status["choosedY"] == "":
                self.UPDATE_LOG.emit("ERROR: Please choose the origin!")
                self.ERROR.emit("Please choose the origin!")
                QtCore.QCoreApplication.processEvents()
            else:
                self.CONNECT_TO_CANVAS.emit()
                QtCore.QCoreApplication.processEvents()
                start = QtCore.QPointF()
                end = QtCore.QPointF()
                origin = QtCore.QPointF()
                origin.setX(self.status["choosedX"])
                origin.setY(self.status["choosedY"])
                start.setX(self.status["startX"])
                start.setY(self.status["startY"])
                end.setX(self.status["endX"])
                end.setY(self.status["endY"])
                width = self.status["width"]*scale_factor
                for filename in glob.glob(self.path):
                    image_list.append(filename)
                self.endIndex = min(self.endIndex, len(image_list)-1)
                if self.Is2D:
                    Kperp = (np.abs((end.y()-start.y())*origin.x()-(end.x()-start.x())*origin.y()+end.x()*start.y()-end.y()*start.x())/ \
                             np.sqrt((end.y()-start.y())**2+(end.x()-start.x())**2))/scale_factor
                    map_2D360=np.array([0,0,0])
                    map_2D180=np.array([0,0,0])
                    self.SET_TITLE.emit("Line Profile at Kperp = {:4.2f} (\u212B\u207B\u00B9)".format(Kperp))
                    QtCore.QCoreApplication.processEvents()
                    for nimg in range(self.startIndex,self.endIndex+1):
                        if use_external_offset:
                            offset_x = int(self.offset_df.at[nimg,'offset_x']*scale_factor)
                            offset_y = int(self.offset_df.at[nimg,'offset_y']*scale_factor)
                            image_crop = [1200+VS+offset_y,2650+VS+offset_y,500+HS+offset_x,3100+HS+offset_x]
                        qImg, img = self.image_worker.get_image(self._bit_depth,image_list[nimg-self.startIndex],autoWB,brightness,blackLevel,image_crop)
                        if self.enableSync:
                            self.REFRESH_CANVAS.emit(image_list[nimg-self.startIndex],image_crop)
                        if width==0.0:
                            RC,I = self.image_worker.get_line_scan(start,end,img,scale_factor,normalize_to_img_max=False)
                        else:
                            RC,I = self.image_worker.get_integral(start,end,width,img,scale_factor,normalize_to_img_max=False)
                        Phi360 = np.full(len(RC),nimg*1.8)
                        Phi180 = np.full(len(RC),nimg*1.8)
                        maxPos = np.argmax(I)
                        if self.normalizationMethod == 0:
                            normalization_factor = 1
                        elif self.normalizationMethod == 1:
                            normalization_factor = 2**8 - 1
                        elif self.normalizationMethod == 2:
                            normalization_factor = I[maxPos]
                        elif self.normalizationMethod == 3:
                            normalization_factor = np.amax(np.amax(img))
                        if self.centralisationMethod == 1:
                            for iphi in range(0,maxPos):
                                Phi360[iphi]=nimg*1.8+180
                            if maxPos<(len(RC)-1)/2:
                                x360,y360 = abs(RC[0:(2*maxPos+1)]-RC[maxPos]), I[0:(2*maxPos+1)]/normalization_factor
                                map_2D360 = np.vstack((map_2D360,np.vstack((x360,Phi360[0:(2*maxPos+1)],y360)).T))
                                x180,y180 = RC[0:(2*maxPos+1)]-RC[maxPos],I[0:(2*maxPos+1)]/normalization_factor
                                map_2D180 = np.vstack((map_2D180,np.vstack((x180,Phi180[0:(2*maxPos+1)],y180)).T))
                            else:
                                x360,y360 = abs(RC[(2*maxPos-len(RC)-1):-1]-RC[maxPos]), I[(2*maxPos-len(RC)-1):-1]/normalization_factor
                                map_2D360 = np.vstack((map_2D360,np.vstack((x360,Phi360[(2*maxPos-len(RC)-1):-1],y360)).T))
                                x180,y180 = RC[(2*maxPos-len(RC)-1):-1]-RC[maxPos], I[(2*maxPos-len(RC)-1):-1]/normalization_factor
                                map_2D180 = np.vstack((map_2D180,np.vstack((x180,Phi180[(2*maxPos-len(RC)-1):-1],y180)).T))
                        elif self.centralisationMethod == 0:
                            x360,y360 = RC, I/normalization_factor
                            map_2D360 = np.vstack((map_2D360,np.vstack((x360,Phi180,y360)).T))
                            x180,y180 = RC,I/normalization_factor
                            map_2D180 = np.vstack((map_2D180,np.vstack((x180,Phi180,y180)).T))
                        elif self.centralisationMethod == 2:
                            for iphi in range(0,len(RC)//2):
                                Phi360[iphi]=nimg*1.8+180
                            x360,y360 = abs(RC - RC[len(RC)//2]), I/normalization_factor
                            map_2D360 = np.vstack((map_2D360,np.vstack((x360,Phi360,y360)).T))
                            x180,y180 = RC - RC[len(RC)//2],I/normalization_factor
                            map_2D180 = np.vstack((map_2D180,np.vstack((x180,Phi180,y180)).T))
                        if self.azimuthRange == 360:
                            self.UPDATE_CHART.emit(x360,y360,"line")
                        elif self.azimuthRange == 180:
                            self.UPDATE_CHART.emit(x180,y180,"line")
                        self.PROGRESS_ADVANCE.emit(0,100,(nimg+1-self.startIndex)*100/(self.endIndex-self.startIndex+1))
                        self.UPDATE_LOG.emit("The file being processed right now is: "+image_list[nimg-self.startIndex])
                        QtCore.QCoreApplication.processEvents()
                        if self.enableSync:
                            time.sleep(self.sleepTime)
                        if self._abort:
                            break
                    if not self._abort:
                        if self.azimuthRange == 360:
                            map_2D_polar = np.delete(map_2D360,0,0)
                        elif self.azimuthRange == 180:
                            map_2D_polar = np.delete(map_2D180,0,0)
                        map_2D_cart = np.empty(map_2D_polar.shape)
                        map_2D_cart[:,2] = map_2D_polar[:,2]
                        map_2D_cart[:,0] = map_2D_polar[:,0]*np.cos((map_2D_polar[:,1])*Pi/180)
                        map_2D_cart[:,1] = map_2D_polar[:,0]*np.sin((map_2D_polar[:,1])*Pi/180)
                        self.graphTextPath = self.currentDestination+"/"+self.saveFileName+self.fileType
                        if self.IsSaveResult:
                            if self.IsCartesian:
                                np.savetxt(self.graphTextPath,map_2D_cart,fmt='%4.3f')
                            else:
                                np.savetxt(self.graphTextPath,map_2D_polar,fmt='%4.3f')
                        self.PROGRESS_END.emit()
                        self.UPDATE_LOG.emit("Completed!")
                        self.ATTENTION.emit("2D Mapping Completed!")
                        if self.IsSaveResult:
                            self.FILE_SAVED.emit(self.graphTextPath)
                        QtCore.QCoreApplication.processEvents()
                else:
                    map_3D360=np.array([0,0,0,0])
                    map_3D180=np.array([0,0,0,0])
                    for nimg in range(self.startIndex,self.endIndex+1):
                        if use_external_offset:
                            offset_x = int(self.offset_df.at[nimg,'offset_x']*scale_factor)
                            offset_y = int(self.offset_df.at[nimg,'offset_y']*scale_factor)
                            image_crop = [1200+VS+offset_y,2650+VS+offset_y,500+HS+offset_x,3100+HS+offset_x]
                        qImg, img = self.image_worker.get_image(self._bit_depth,image_list[nimg-self.startIndex],autoWB,brightness,blackLevel,image_crop)
                        x0,y0,xn,yn = start.x(),start.y(),end.x(),end.y()
                        newStart = QtCore.QPointF()
                        newEnd = QtCore.QPointF()
                        if self.enableSync:
                            self.REFRESH_CANVAS.emit(image_list[nimg-self.startIndex],image_crop)
                        if width==0.0:
                            if origin.y() < (y0 + yn) /2:
                                step = 5
                            else:
                                step = -5
                            nos = int(self.analysisRange*scale_factor/abs(step))
                        else:
                            nos = int(self.analysisRange*scale_factor/width)
                            if origin.y() < (y0 + yn) /2:
                                step = width
                            else:
                                step = -width
                        for i in range(1,nos+1):
                            if x0 == xn:
                                newStart.setX(x0+i*step)
                                newStart.setY(y0)
                                newEnd.setX(xn+i*step)
                                newEnd.setY(yn)
                            else:
                                angle = np.arctan((y0-yn)/(xn-x0))
                                newStart.setX(int(x0+i*step*np.sin(angle)))
                                newStart.setY(int(y0+i*step*np.cos(angle)))
                                newEnd.setX(int(xn+i*step*np.sin(angle)))
                                newEnd.setY(int(yn+i*step*np.cos(angle)))
                            Kperp = (np.abs((newEnd.y()-newStart.y())*origin.x()-(newEnd.x()-newStart.x())*origin.y()+newEnd.x()*newStart.y()-newEnd.y()*newStart.x())/ \
                                     np.sqrt((newEnd.y()-newStart.y())**2+(newEnd.x()-newStart.x())**2))/scale_factor
                            self.SET_TITLE.emit("Line Profile at Kperp = {:4.2f} (\u212B\u207B\u00B9)".format(Kperp))
                            QtCore.QCoreApplication.processEvents()
                            if width==0.0:
                                RC,I = self.image_worker.get_line_scan(newStart,newEnd,img,scale_factor,normalize_to_img_max=False)
                                self.DRAW_LINE_REQUESTED.emit(newStart,newEnd,False)
                            else:
                                RC,I = self.image_worker.get_integral(newStart,newEnd,width,img,scale_factor,normalize_to_img_max=False)
                                self.DRAW_RECT_REQUESTED.emit(newStart,newEnd,width,False)
                            QtCore.QCoreApplication.processEvents()
                            rem = np.remainder(len(RC),self.group)
                            if not rem == 0:
                                RC = np.pad(RC,(0,self.group-rem),'edge')
                                I = np.pad(I,(0,self.group-rem),'edge')
                            RC,I = RC.reshape(-1,self.group).mean(axis=1), I.reshape(-1,self.group).mean(axis=1)
                            Phi360 = np.full(len(RC),nimg*1.8)
                            Phi180 = np.full(len(RC),nimg*1.8)
                            maxPos = np.argmax(I)
                            if self.normalizationMethod == 0:
                                normalization_factor = 1
                            elif self.normalizationMethod == 1:
                                normalization_factor = 2**8 - 1
                            elif self.normalizationMethod == 2:
                                normalization_factor = I[maxPos]
                            elif self.normalizationMethod == 3:
                                normalization_factor = np.amax(np.amax(img))
                            if self.centralisationMethod == 1:
                                for iphi in range(0,maxPos):
                                    Phi360[iphi]=nimg*1.8+180
                                if maxPos<(len(RC)-1)/2:
                                    x360,y360 = abs(RC[0:(2*maxPos+1)]-RC[maxPos]), I[0:(2*maxPos+1)]/normalization_factor
                                    K = np.full(len(x360),Kperp)
                                    map_3D360 = np.vstack((map_3D360,np.vstack((x360,Phi360[0:(2*maxPos+1)],K,y360)).T))
                                    x180,y180 = RC[0:(2*maxPos+1)]-RC[maxPos],I[0:(2*maxPos+1)]/normalization_factor
                                    map_3D180 = np.vstack((map_3D180,np.vstack((x180,Phi180[0:(2*maxPos+1)],K,y180)).T))
                                else:
                                    x360,y360 = abs(RC[(2*maxPos-len(RC)-1):-1]-RC[maxPos]), I[(2*maxPos-len(RC)-1):-1]/normalization_factor
                                    K = np.full(len(x360),Kperp)
                                    map_3D360 = np.vstack((map_3D360,np.vstack((x360,Phi360[(2*maxPos-len(RC)-1):-1],K,y360)).T))
                                    x180,y180 = RC[(2*maxPos-len(RC)-1):-1]-RC[maxPos], I[(2*maxPos-len(RC)-1):-1]/normalization_factor
                                    map_3D180 = np.vstack((map_3D180,np.vstack((x180,Phi180[(2*maxPos-len(RC)-1):-1],K,y180)).T))
                            elif self.centralisationMethod == 0:
                                x360,y360 = RC, I/normalization_factor
                                K = np.full(len(x360),Kperp)
                                map_3D360 = np.vstack((map_3D360,np.vstack((x360,Phi180,K,y360)).T))
                                x180,y180 = RC,I/normalization_factor
                                map_3D180 = np.vstack((map_3D180,np.vstack((x180,Phi180,K,y180)).T))
                            elif self.centralisationMethod == 2:
                                for iphi in range(0,len(RC)//2):
                                    Phi360[iphi]=nimg*1.8+180
                                x360,y360 = abs(RC - RC[len(RC)//2]), I/normalization_factor
                                K = np.full(len(x360),Kperp)
                                map_3D360 = np.vstack((map_3D360,np.vstack((x360,Phi360,K,y360)).T))
                                x180,y180 = RC - RC[len(RC)//2],I/normalization_factor
                                map_3D180 = np.vstack((map_3D180,np.vstack((x180,Phi180,K,y180)).T))
                            if self.azimuthRange == 360:
                                self.UPDATE_CHART.emit(x360,y360,"line")
                            elif self.azimuthRange == 180:
                                self.UPDATE_CHART.emit(x180,y180,"line")
                            self.PROGRESS_ADVANCE.emit(0,100,(i+nos*(nimg-self.startIndex))*100/((self.endIndex-self.startIndex+1)*nos))
                            self.UPDATE_LOG.emit("The file being processed right now is: "+image_list[nimg-self.startIndex])
                            QtCore.QCoreApplication.processEvents()
                            if self.enableSync:
                                time.sleep(self.sleepTime)
                        if self._abort:
                            break
                    QtCore.QCoreApplication.processEvents()
                    if not self._abort:
                        if self.azimuthRange == 360:
                            map_3D_polar = np.delete(map_3D360,0,0)
                        elif self.azimuthRange == 180:
                            map_3D_polar = np.delete(map_3D180,0,0)
                        map_3D_cart = np.empty(map_3D_polar.shape)
                        map_3D_cart[:,2] = map_3D_polar[:,2]
                        map_3D_cart[:,3] = map_3D_polar[:,3]
                        map_3D_cart[:,0] = map_3D_polar[:,0]*np.cos((map_3D_polar[:,1])*Pi/180)
                        map_3D_cart[:,1] = map_3D_polar[:,0]*np.sin((map_3D_polar[:,1])*Pi/180)
                        self.graphTextPath = self.currentDestination+"/"+self.saveFileName+self.fileType
                        if self.IsSaveResult:
                            if self.IsCartesian:
                                np.savetxt(self.graphTextPath,map_3D_cart,fmt='%4.3f')
                                self.convertor_worker.txt2vtp(self.graphTextPath,"Cartesian")
                            else:
                                np.savetxt(self.graphTextPath,map_3D_polar,fmt='%4.3f')
                                self.convertor_worker.txt2vtp(self.graphTextPath,"Polar")
                        self.PROGRESS_END.emit()
                        self.UPDATE_LOG.emit("Completed!")
                        self.ATTENTION.emit("3D Mapping Completed!")
                        QtCore.QCoreApplication.processEvents()
        if not self._abort:
            self.FINISHED.emit()
        else:
            self.ABORTED.emit()
            self._abort = False

    def stop(self):
        self._abort = True


class DiffractionPattern(QtCore.QObject):
    PROGRESS_ADVANCE = QtCore.pyqtSignal(int,int,int)
    PROGRESS_END = QtCore.pyqtSignal()
    ERROR = QtCore.pyqtSignal(str)
    ACCOMPLISHED = QtCore.pyqtSignal(np.ndarray)
    ABORTED = QtCore.pyqtSignal()
    INSUFFICIENT_MEMORY = QtCore.pyqtSignal()
    FINISHED = QtCore.pyqtSignal()
    ELAPSED_TIME = QtCore.pyqtSignal(float)
    UPDATE_LOG = QtCore.pyqtSignal(str)

    def __init__(self,Kx,Ky,Kz,AFF,atoms, constant_atomic_structure_factor=False,useCUDA=True):
        super(DiffractionPattern,self).__init__()
        self.Psi = np.multiply(Kx,0).astype('complex128')
        self.species_dict = set(AFF.index.tolist())
        self.af_dict = {}
        self.atoms_list = atoms
        self.Kx = Kx
        self.Ky = Ky
        self.Kz = Kz
        self.coord_list = list(atoms.keys())
        self.specie_list = list(atoms.values())
        if self.Kx.shape[0] == 1 and self.Kx.shape[1]==1:
            self.XYZ = np.dstack((self.Kx.T,self.Ky.T,self.Kz.T)).reshape((self.Kx.shape[0],self.Kx.shape[1],self.Kx.shape[2],3))
        else:
            self.XYZ = np.dstack((self.Kx,self.Ky,self.Kz)).reshape((self.Kx.shape[0],self.Kx.shape[1],self.Kx.shape[2],3))
        self.AFF = AFF
        self.constant_atomic_structure_factor = constant_atomic_structure_factor
        self.useCUDA = useCUDA and CUDA_EXIST
        self._abort = False

    def atomic_form_factor(self,specie):
        if specie in self.species_dict:
            af_row = self.AFF.loc[specie]
        elif specie+'1+' in self.species_dict:
            af_row = self.AFF.loc[specie+'1+']
        elif specie+'2+' in self.species_dict:
            af_row = self.AFF.loc[specie+'2+']
        elif specie+'3+' in self.species_dict:
            af_row = self.AFF.loc[specie+'3+']
        elif specie+'4+' in self.species_dict:
            af_row = self.AFF.loc[specie+'4+']
        elif specie+'1-' in self.species_dict:
            af_row = self.AFF.loc[specie+'1-']
        elif specie+'2-' in self.species_dict:
            af_row = self.AFF.loc[specie+'2-']
        elif specie+'3-' in self.species_dict:
            af_row = self.AFF.loc[specie+'3-']
        elif specie+'4-' in self.species_dict:
            af_row = self.AFF.loc[specie+'4-']
        else:
            self.ERROR.emit("No scattering coefficient for %s"%specie)
        af = af_row.at['c']+af_row.at['a1']*np.exp(-af_row.at['b1']*(np.multiply(self.Kx,self.Kx)+np.multiply(self.Ky,self.Ky)+np.multiply(self.Kz,self.Kz))/4/np.pi)\
                           +af_row.at['a2']*np.exp(-af_row.at['b2']*(np.multiply(self.Kx,self.Kx)+np.multiply(self.Ky,self.Ky)+np.multiply(self.Kz,self.Kz))/4/np.pi)\
                           +af_row.at['a3']*np.exp(-af_row.at['b3']*(np.multiply(self.Kx,self.Kx)+np.multiply(self.Ky,self.Ky)+np.multiply(self.Kz,self.Kz))/4/np.pi)\
                           +af_row.at['a4']*np.exp(-af_row.at['b4']*(np.multiply(self.Kx,self.Kx)+np.multiply(self.Ky,self.Ky)+np.multiply(self.Kz,self.Kz))/4/np.pi)
        return af

    def run(self):
        if self.useCUDA:
            start_time = time.time()
            self.UPDATE_LOG.emit("Using CUDA...")
            drv.init()
            device = drv.Device(0)
            try:
                ctx = device.make_context()
            except drv.MemoryError:
                self.UPDATE_LOG.emit("[ERROR] Unable to make context for this device. Process will be aborted.")
                self.ABORTED.emit()
                self.INSUFFICIENT_MEMORY.emit()
                self._abort = False
                return

            max_blkx = device.get_attribute(drv.device_attribute.MAX_BLOCK_DIM_X)
            max_blky = device.get_attribute(drv.device_attribute.MAX_BLOCK_DIM_Y)
            max_blkz = device.get_attribute(drv.device_attribute.MAX_BLOCK_DIM_Z)
            max_gridx = device.get_attribute(drv.device_attribute.MAX_GRID_DIM_X)
            max_gridy = device.get_attribute(drv.device_attribute.MAX_GRID_DIM_Y)
            max_gridz = device.get_attribute(drv.device_attribute.MAX_GRID_DIM_Z)

            self.UPDATE_LOG.emit("Maximum block dimension: "+"({},{},{})".format(max_blkx,max_blky,max_blkz))
            self.UPDATE_LOG.emit("Maximum grid dimension: "+"({},{},{})".format(max_gridx,max_gridy,max_gridz))

            for specie in set(self.atoms_list.values()):
                if self.constant_atomic_structure_factor:
                    self.af_dict[specie] = 1
                else:
                    self.af_dict[specie] = self.atomic_form_factor(specie)

            nb_atoms = len(self.atoms_list)
            nkx,nky,nkz = self.Kx.shape[0],self.Kx.shape[1],self.Kx.shape[2]
            self.UPDATE_LOG.emit("Number of atoms: "+ str(nb_atoms))
            self.UPDATE_LOG.emit("Reciprocal space dimension: "+"({},{},{})".format(nkx,nky,nkz))
            
            host_K_tensor = np.array([self.Kx*coord[0]+self.Ky*coord[1]+self.Kz*coord[2] for coord in self.atoms_list.keys()]).astype(np.float32)
            host_atom_struct_fact = np.array([self.af_dict[specie] for specie in self.atoms_list.values()]).astype(np.float32)
            self.UPDATE_LOG.emit("Total GPU memory (MB): "+"{:6.2f}".format(drv.mem_get_info()[1]/1024/1024))
            self.UPDATE_LOG.emit("Available GPU memory (MB): "+"{:6.2f}".format(drv.mem_get_info()[0]/1024/1024))
            self.UPDATE_LOG.emit("Requested GPU memory (MB): "+"{:6.2f}".format(host_atom_struct_fact.nbytes*2/1024/1024))

            if host_atom_struct_fact.nbytes*2 > drv.mem_get_info()[0]*0.95:
                self.UPDATE_LOG.emit("[ERROR] Insufficient GPU memory. Process will be aborted")
                self.ABORTED.emit()
                self.INSUFFICIENT_MEMORY.emit()
                self._abort = False
                return
            else:
                start = drv.Event()
                end = drv.Event()

                device_atom_struct_fact = drv.mem_alloc(host_atom_struct_fact.nbytes)
                device_K_tensor = drv.mem_alloc(host_K_tensor.nbytes)
                #device_Psi_tensor = drv.mem_alloc(host_Psi_tensor.nbytes)

                drv.memcpy_htod(device_atom_struct_fact,host_atom_struct_fact)
                drv.memcpy_htod(device_K_tensor,host_K_tensor)
                #drv.memcpy_htod(device_Psi_tensor,host_Psi_tensor)

                mod = comp.SourceModule("""
                #include <stdio.h>
                #include <math.h>
                __global__ void kernal(float *d_a, float *d_b)
                {
                    const int blockId = blockIdx.x + blockIdx.y * gridDim.x + gridDim.x*gridDim.y*blockIdx.z;
                    const int threadId = blockId* (blockDim.x *blockDim.y*blockDim.z) + (threadIdx.z*(blockDim.z*blockDim.y)) + (threadIdx.y*blockDim.x) + threadIdx.x;
                    const float d_a_temp = d_a[threadId];
                    d_a[threadId] = d_a_temp * cos(d_b[threadId]);
                    d_b[threadId] = d_a_temp * sin(d_b[threadId]);
                }
                """)

                kernal = mod.get_function("kernal")
                start.record()
                #kernal(device_Psi_tensor, device_atom_struct_fact,device_K_tensor, block=(nkz,1,1), grid=(nb_atoms,nky,nkx))
                kernal(device_atom_struct_fact,device_K_tensor, block=(nkz,1,1), grid=(nb_atoms,nky,nkx))
                end.record()
                end.synchronize()
                secs = start.time_till(end)*1e-3
                self.UPDATE_LOG.emit("GPU processing time = %fs" % (secs))
                drv.memcpy_dtoh(host_atom_struct_fact,device_atom_struct_fact)
                drv.memcpy_dtoh(host_K_tensor,device_K_tensor)
                ctx.pop()
                self.Psi_real = np.sum(host_atom_struct_fact,axis=0)
                self.Psi_img = np.sum(host_K_tensor,axis=0)
                self.intensity = self.Psi_real**2+self.Psi_img**2
        else:
            start_time = time.time()
            itr = 0
            number_of_atoms = len(self.atoms_list)
            self.UPDATE_LOG.emit("Number of atoms: "+ str(number_of_atoms))
            for specie in set(self.atoms_list.values()):
                if self.constant_atomic_structure_factor:
                    self.af_dict[specie] = 1
                else:
                    self.af_dict[specie] = self.atomic_form_factor(specie)
            for coord,specie in self.atoms_list.items():
                QtCore.QCoreApplication.processEvents()
                if self._abort:
                    break
                else:
                    self.Psi += np.multiply(self.af_dict[specie],np.exp(1j*(self.Kx*coord[0]+self.Ky*coord[1]+self.Kz*coord[2])))
                    itr+=1
                    self.PROGRESS_ADVANCE.emit(0,100,itr/number_of_atoms*100)
                    QtCore.QCoreApplication.processEvents()
            #self.Psi = np.sum(e for e in self.exponent_gen())
            self.intensity = np.multiply(self.Psi.astype('complex64'),np.conj(self.Psi.astype('complex64')))

        elapsed_time = time.time() - start_time
        self.ELAPSED_TIME.emit(elapsed_time)
        if not self._abort:
            self.PROGRESS_END.emit()
            self.ACCOMPLISHED.emit(self.intensity)
        else:
            self.ABORTED.emit()
            self._abort = False

    #def exponent_gen(self):
    #    n = 0
    #    while n < len(self.atoms_list)-1 and (not self._abort):
    #        n+=1
    #        exponent = np.multiply(self.af_dict[list(self.atoms_list.values())[n]],np.exp(1j*(np.tensordot(self.XYZ,np.array(list(self.atoms_list.keys())[n]).T,axes=1))))
    #        yield exponent
    #        self.PROGRESS_ADVANCE.emit(0,100,n/(len(self.atoms_list)-1)*100)
    #        QtCore.QCoreApplication.processEvents()

    def stop(self):
        self._abort = True

class FitBroadening(QtCore.QObject):

    ADD_COST_FUNCTION = QtCore.pyqtSignal(np.ndarray,list,str)
    ADD_PLOT = QtCore.pyqtSignal(np.ndarray,np.ndarray,float,int)
    ATTENTION = QtCore.pyqtSignal(str)
    CLOSE_OUTPUT = QtCore.pyqtSignal()
    DRAW_LINE_REQUESTED = QtCore.pyqtSignal(QtCore.QPointF,QtCore.QPointF,bool)
    DRAW_RECT_REQUESTED = QtCore.pyqtSignal(QtCore.QPointF,QtCore.QPointF,float,bool)
    FINISHED = QtCore.pyqtSignal()
    PROGRESS_ADVANCE = QtCore.pyqtSignal(int,int,int)
    PROGRESS_END = QtCore.pyqtSignal()
    UPDATE_RESULTS = QtCore.pyqtSignal(list)
    UPDATE_LOG = QtCore.pyqtSignal(str)
    WRITE_OUTPUT = QtCore.pyqtSignal(str)

    def __init__(self,path,initialparameters,startIndex,endIndex,origin,start,end,width,analysisRange,scale_factor,autoWB,brightness,blackLevel,image_crop,\
                 numberOfPeaks,BGCheck,remove_linear_BGCheck, saveResult,function,guess,bounds,ftol,xtol,gtol,method,loss):
        super(FitBroadening,self).__init__()
        self.path = path
        self.initialparameters = initialparameters
        self.startIndex = startIndex
        self.endIndex = endIndex
        self.origin = origin
        self.start = start
        self.end = end
        self.width = width
        self.analysisRange = analysisRange
        self.scale_factor = scale_factor
        self.autoWB = autoWB
        self.brightness = brightness
        self.blackLevel = blackLevel
        self.image_crop = image_crop
        self.numberOfPeaks = numberOfPeaks
        self.BGCheck = BGCheck
        self.remove_linear_BGCheck = remove_linear_BGCheck
        self.saveResult = saveResult
        self.function = function
        self.guess=guess
        self.bound_low,self.bound_high = bounds[0],bounds[1]
        self.ftol = ftol
        self.xtol = xtol
        self.gtol = gtol
        self.method = method
        self.loss = loss
        self.image_list = []
        self.image_worker = Image()
        self.fit_worker = FitFunctions()
        self._abort = False
        self._periodic = False

    def update_fitting_parameters(self,guess,bounds):
        self.guess = guess
        self.bound_low,self.bound_high = bounds[0],bounds[1]
    
    def run(self):
        for filename in glob.glob(self.path):
            self.image_list.append(filename)
        if self.startIndex > self.endIndex:
            self.endIndex += 101
            self._periodic = True
        for nimg in range(self.startIndex,self.endIndex+1):
            if nimg < len(self.image_list):
                if self._periodic:
                    nimg = nimg%101
                self.UPDATE_RESULTS.emit(self.initialparameters)
                self.UPDATE_LOG.emit("The file being processed right now is: "+self.image_list[nimg])
                QtCore.QCoreApplication.processEvents()
                qImg, img = self.image_worker.get_image(16,self.image_list[nimg],self.autoWB,self.brightness,self.blackLevel,self.image_crop)
                x0,y0,x1,y1 = self.start.x(),self.start.y(),self.end.x(),self.end.y()
                newStart = QtCore.QPointF()
                newEnd = QtCore.QPointF()
                if self.width==0.0:
                    if self.origin.y() < (y0 + y1) /2:
                        step = 5
                    else:
                        step = -5
                    nos = int(self.analysisRange*self.scale_factor/step)
                else:
                    nos = int(self.analysisRange*self.scale_factor/self.width)
                    if self.origin.y() < (y0 + y1) /2:
                        step = self.width
                    else:
                        step = -self.width
                for i in range(1,nos+1):
                    if x0 == x1:
                        newStart.setX(x0+i*step)
                        newStart.setY(y0)
                        newEnd.setX(x1+i*step)
                        newEnd.setY(y1)
                    else:
                        angle = np.arctan((y0-y1)/(x1-x0))
                        newStart.setX(int(x0+i*step*np.sin(angle)))
                        newStart.setY(int(y0+i*step*np.cos(angle)))
                        newEnd.setX(int(x1+i*step*np.sin(angle)))
                        newEnd.setY(int(y1+i*step*np.cos(angle)))
                    if self.width == 0.0:
                        RC,I = self.image_worker.get_line_scan(newStart,newEnd,img,self.scale_factor)
                    else:
                        RC,I = self.image_worker.get_integral(newStart,newEnd,self.width,img,self.scale_factor)
                    if self.remove_linear_BGCheck:
                        BG = np.linspace(I[0],I[-1],len(I))
                        I = I - BG
                    results, cost, output = self.fit_worker.get_fit(RC,I,self.numberOfPeaks,self.BGCheck,self.function, self.guess,(self.bound_low,self.bound_high),self.ftol,\
                                                                    self.xtol,self.gtol,self.method,self.loss)
                    Kperp = (np.abs((newEnd.y()-newStart.y())*self.origin.x()-(newEnd.x()-newStart.x())*self.origin.y()+newEnd.x()*newStart.y()-newEnd.y()*newStart.x())/\
                            np.sqrt((newEnd.y()-newStart.y())**2+(newEnd.x()-newStart.x())**2))/self.scale_factor
                    iteration = np.linspace(1,len(cost)+1,len(cost))
                    jac = results.jac
                    cov = np.linalg.pinv(jac.T.dot(jac))
                    residual_variance = np.sum(results.fun**2)/(len(I)-len(self.guess))
                    var = np.sqrt(np.diagonal(cov*residual_variance))
                    value_variance = np.reshape(np.concatenate((np.array(results.x),np.array(var)),axis=0),(2,len(var)))
                    self.ADD_COST_FUNCTION.emit(iteration,cost,'cost_function')
                    self.UPDATE_RESULTS.emit(list(results.x))
                    self.UPDATE_LOG.emit(output)
                    if i == 1:
                        self.initialparameters = list(results.x)
                    if nimg<=100:
                        angle = nimg*1.8
                    else:
                        angle = nimg*1.8 - 180
                    fitresults =str(angle).ljust(12)+'\t'+str(np.round(Kperp,3)).ljust(12)+'\t'+'\t'.join(str(np.round(e[0],3)).ljust(12)+'\t'+str(np.round(e[1],3)).ljust(12) for e in value_variance.T)+'\n'
                    if self.saveResult == 2:
                        self.WRITE_OUTPUT.emit(fitresults)
                    self.UPDATE_LOG.emit("MESSAGE:"+results.message)
                    self.ADD_PLOT.emit(RC,I,Kperp,nimg)
                    time.sleep(0.1)
                    if self._periodic:
                        if nimg < self.startIndex:
                            offset = 1
                        else:
                            offset = 0
                        self.PROGRESS_ADVANCE.emit(0,100,((nimg+101*offset-self.startIndex)*nos+i)*100/nos/(self.endIndex-self.startIndex+1))
                    else:
                        self.PROGRESS_ADVANCE.emit(0,100,((nimg-self.startIndex)*nos+i)*100/nos/(self.endIndex-self.startIndex+1))
                    QtCore.QCoreApplication.processEvents()
                    if self._abort:
                        break
                if self._abort:
                    break
        if self.saveResult == 2:
            self.CLOSE_OUTPUT.emit()
        if not self._abort:
            self.PROGRESS_END.emit()
            self.UPDATE_LOG.emit("Completed!")
            self.ATTENTION.emit("Broadening Analysis Completed!")
        else:
            self.UPDATE_LOG.emit("Aborted!")
            self.ATTENTION.emit("Broadening Analysis Aborted!")
            self._abort = False
        self.FINISHED.emit()

    def stop(self):
        self._abort = True
    
class TAPD_model(object):
    def __init__(self,index=0):
        self.index = index
        self._vor = None
        self._substrate_structure = None
        self._substrate_sites = None
        self._substrate_list = None
        self._epilayer_structure = None
        self._epilayer_sites = None
        self._epilayer_list = None
        self._buffer_layer_list = None
        self._buffer_layer_sites = None
        self._epilayer_domain_area_list = None
        self._epilayer_domain_boundary_list = None
        self._epilayer_domain = None

    @property
    def vor(self):
        return self._vor

    @vor.setter
    def vor(self,vor):
        self._vor = vor
    @vor.deleter
    def vor(self):
        del self._vor

    @property
    def epilayer_structure(self):
        return self._epilayer_structure

    @epilayer_structure.setter
    def epilayer_structure(self,epilayer_structure):
        self._epilayer_structure = epilayer_structure
    @epilayer_structure.deleter
    def epilayer_structure(self):
        del self._epilayer_structure

    @property
    def epilayer_sites(self):
        return self._epilayer_sites

    @epilayer_sites.setter
    def epilayer_sites(self,epilayer_sites):
        self._epilayer_sites = epilayer_sites
    @epilayer_sites.deleter
    def epilayer_sites(self):
        del self._epilayer_sites

    @property
    def epilayer_list(self):
        return self._epilayer_list

    @epilayer_list.setter
    def epilayer_list(self,epilayer_list):
        self._epilayer_list = epilayer_list
    @epilayer_list.deleter
    def epilayer_list(self):
        del self._epilayer_list

    @property
    def buffer_layer_sites(self):
        return self._buffer_layer_sites

    @buffer_layer_sites.setter
    def buffer_layer_sites(self,buffer_layer_sites):
        self._buffer_layer_sites = buffer_layer_sites
    @buffer_layer_sites.deleter
    def buffer_layer_sites(self):
        del self._buffer_layer_sites

    @property
    def buffer_layer_list(self):
        return self._buffer_layer_list

    @buffer_layer_list.setter
    def buffer_layer_list(self,buffer_layer_list):
        self._buffer_layer_list = buffer_layer_list
    @buffer_layer_list.deleter
    def buffer_layer_list(self):
        del self._buffer_layer_list

    @property
    def epilayer_list(self):
        return self._epilayer_list

    @epilayer_list.setter
    def epilayer_list(self,epilayer_list):
        self._epilayer_list = epilayer_list
    @epilayer_list.deleter
    def epilayer_list(self):
        del self._epilayer_list


    @property
    def epilayer_domain_area_list(self):
        return self._epilayer_domain_area_list

    @epilayer_domain_area_list.setter
    def epilayer_domain_area_list(self,epilayer_domain_area_list):
        self._epilayer_domain_area_list = epilayer_domain_area_list
    @epilayer_domain_area_list.deleter
    def epilayer_domain_area_list(self):
        del self._epilayer_domain_area_list

    @property
    def epilayer_domain_boundary_list(self):
        return self._epilayer_domain_boundary_list

    @epilayer_domain_boundary_list.setter
    def epilayer_domain_boundary_list(self,epilayer_domain_boundary_list):
        self._epilayer_domain_boundary_list = epilayer_domain_boundary_list
    @epilayer_domain_boundary_list.deleter
    def epilayer_domain_boundary_list(self):
        del self._epilayer_domain_boundary_list

    @property
    def epilayer_boundary_sites(self):
        return self._epilayer_boundary_sites
    @epilayer_boundary_sites.setter
    def epilayer_boundary_sites(self,epilayer_boundary_sites):
        self._epilayer_boundary_sites = epilayer_boundary_sites
    @epilayer_boundary_sites.deleter
    def epilayer_boundary_sites(self):
        del self._epilayer_boundary_sites

    @property
    def epilayer_domain(self):
        return self._epilayer_domain

    @epilayer_domain.setter
    def epilayer_domain(self,epilayer_domain):
        self._epilayer_domain = epilayer_domain
    @epilayer_domain.deleter
    def epilayer_domain(self):
        del self._epilayer_domain


    @property
    def substrate_structure(self):
        return self._substrate_structure

    @substrate_structure.setter
    def substrate_structure(self,substrate_structure):
        self._substrate_structure = substrate_structure
    @substrate_structure.deleter
    def substrate_structure(self):
        del self._substrate_structure

    @property
    def substrate_sites(self):
        return self._substrate_sites

    @substrate_sites.setter
    def substrate_sites(self,substrate_sites):
        self._substrate_sites = substrate_sites
    @substrate_sites.deleter
    def substrate_sites(self):
        del self._substrate_sites

    @property
    def substrate_list(self):
        return self._substrate_list
    
    @substrate_list.setter
    def substrate_list(self,substrate_list):
        self._substrate_list = substrate_list
    @substrate_list.deleter
    def substrate_list(self):
        del self._substrate_list

class TAPD_Simulation(QtCore.QObject):
    PROGRESS_ADVANCE = QtCore.pyqtSignal(int,int,int)
    PROGRESS_END = QtCore.pyqtSignal()
    ERROR = QtCore.pyqtSignal(str)
    FINISHED = QtCore.pyqtSignal()
    SEND_RESULTS = QtCore.pyqtSignal(TAPD_model)
    UPDATE_LOG = QtCore.pyqtSignal(str)

    def __init__(self,X_max, Y_max, Z_min, Z_max, offset, substrate_CIF_path, epilayer_CIF_path, distribution,\
        atom='S',in_plane_distribution='completely random',out_of_plane_distribution='completely random',buffer_offset=[0,0,0],\
        sub_orientation='(001)', epi_orientation='(001)', use_atoms = True, add_buffer = False, **kwargs):
        super(TAPD_Simulation,self).__init__()
        self.X_max = X_max
        self.Y_max = Y_max
        self.Z_min = Z_min
        self.Z_max = Z_max
        self.offset = offset
        self.substrate_CIF_path = substrate_CIF_path
        self.epilayer_CIF_path = epilayer_CIF_path
        self.sub_orientation = sub_orientation
        self.epi_orientation = epi_orientation
        self.distribution = distribution
        self.use_atoms = use_atoms
        self.buffer_layer_atom = atom
        self.buffer_in_plane_distribution = in_plane_distribution
        self.buffer_out_of_plane_distribution = out_of_plane_distribution
        self.buffer_offset = buffer_offset
        self.add_buffer = add_buffer
        self.parameters = kwargs
        self._abort = False

    def run(self):
        self.UPDATE_LOG.emit('Preparing the translational antiphase domain sites ...')
        QtCore.QCoreApplication.processEvents()
        model = self.get_TAPD_sites(self.X_max,self.Y_max, self.Z_min, self.Z_max,self.offset, self.substrate_CIF_path, self.epilayer_CIF_path,\
            self.buffer_layer_atom, self.buffer_in_plane_distribution, self.buffer_out_of_plane_distribution, self.buffer_offset,\
            self.sub_orientation,self.epi_orientation, self.use_atoms, self.add_buffer)
        if model is not None:
            QtCore.QCoreApplication.processEvents()
            if not self._abort:
                self.UPDATE_LOG.emit('Translational antiphase domain sites are created!')
                self.SEND_RESULTS.emit(model)
            else:
                self.UPDATE_LOG.emit('Process aborted!')
                self._abort = False
        else:
            self.UPDATE_LOG.emit('Wrong parameters!')
        self.FINISHED.emit()

    def stop(self):
        self._abort = True

    def get_TAPD_sites(self, X_max, Y_max, Z_min, Z_max, offset, substrate_CIF_path, epilayer_CIF_path, \
        atom,in_plane_distribution,out_of_plane_distribution,buffer_offset,\
        sub_orientation='(001)', epi_orientation='(001)',use_atoms = True, add_buffer = False):
        model = TAPD_model()
        model.substrate_structure = CifParser(substrate_CIF_path).get_structures(primitive=False)[0]
        model.epilayer_structure = CifParser(epilayer_CIF_path).get_structures(primitive=False)[0]
        self.UPDATE_LOG.emit('Preparing the substrate ...')
        QtCore.QCoreApplication.processEvents()
        substrate_set, model.substrate_list, model.substrate_sites = self.get_substrate(model.substrate_structure, sub_orientation, X_max, Y_max, Z_min, Z_max, use_atoms)
        if not substrate_set is None:
            self.UPDATE_LOG.emit('Substrate created!')
            self.UPDATE_LOG.emit('Creating nucleation ...')
            QtCore.QCoreApplication.processEvents()
            generators = self.generator_2D(substrate_set, self.distribution, **self.parameters)
            if isinstance(generators,int):
                model.epilayer_list, model.epilayer_sites, model.epilayer_domain_area_list, model.epilayer_domain_boundary_list, model.epilayer_boundary_sites, model.epilayer_domain = self.get_boundaryless_epilayer(model.epilayer_structure, epi_orientation, X_max, Y_max, Z_min, Z_max, offset, use_atoms)
            elif generators.any():
                self.UPDATE_LOG.emit('Nucleation created!')
                self.UPDATE_LOG.emit('Creating Voronoi ...')
                QtCore.QCoreApplication.processEvents()
                try:
                    vor = Voronoi(generators)
                except:
                    return None
                model.vor = vor
                self.UPDATE_LOG.emit('Voronoi is created!')
                self.UPDATE_LOG.emit('Epilayer is growing ...')
                QtCore.QCoreApplication.processEvents()
                model.epilayer_list, model.epilayer_sites, model.epilayer_domain_area_list, model.epilayer_domain_boundary_list, model.epilayer_boundary_sites, model.epilayer_domain = self.get_epilayer(vor, model.epilayer_structure, epi_orientation, X_max, Y_max, Z_min, Z_max, offset, use_atoms)
                if model.epilayer_list:
                    self.UPDATE_LOG.emit('Atoms are filtered!')
                    QtCore.QCoreApplication.processEvents()
                    self.UPDATE_LOG.emit('Epilayer growth is done!')
        if add_buffer:
            self.UPDATE_LOG.emit('Adding the buffer layer ...')
            QtCore.QCoreApplication.processEvents()
            model.buffer_layer_list,model.buffer_layer_sites = self.get_buffer_layer(model.epilayer_list,max(model.epilayer_structure.lattice.a,model.epilayer_structure.lattice.b),\
                atom,in_plane_distribution,out_of_plane_distribution,buffer_offset,**self.parameters)
        return model

    def generator_2D(self, substrate_set, distribution, **kwargs):
        substrate_set_length = len(substrate_set)
        randPoints = []
        number_of_sites = len(substrate_set)
        i = 0
        if kwargs['density'] > 0:
            while substrate_set:
                x,y = random.choice(list(substrate_set))
                randPoints.append([x,y])
                if distribution == 'completely random':
                    density = kwargs['density']
                    number_of_sites = density*len(substrate_set)
                    substrate_set.remove((x,y))
                else:
                    if distribution == 'geometric':
                        radius = np.random.geometric(kwargs['gamma'])
                    elif distribution == 'delta':
                        radius = kwargs['radius']
                    elif distribution == 'uniform':
                        radius = np.random.uniform(kwargs['low'], kwargs['high'])
                    elif distribution == 'binomial':
                        radius = np.random.binomial(kwargs['n'],kwargs['p'])
                    substrate_set_temp = substrate_set.copy()
                    for (dx,dy) in substrate_set_temp:
                        if (dx-x)**2+(dy-y)**2 <= radius**2:
                            substrate_set.remove((dx,dy))
                if i <= number_of_sites:
                    i += 1
                    self.PROGRESS_ADVANCE.emit(0,100,np.round(100-len(substrate_set)/substrate_set_length*100,1))
                    QtCore.QCoreApplication.processEvents()
                else:
                    break
                if self._abort:
                    break
            self.PROGRESS_END.emit()
            QtCore.QCoreApplication.processEvents()
            if not self._abort:
                return np.array(randPoints)
            else:
                return None
        else:
            return 0

    def get_heavist_element(self, structure):
        atomic_number = 0
        name = ''
        for site in structure.sites:
            element = periodic_table.Element(site.as_dict()['species'][0]['element'])
            if element.Z > atomic_number:
                atomic_number = element.Z
                name = element.symbol
        return name

    def get_buffer_layer(self, epilayer_list, substrate_lattice_constant, atom, in_plane_distribution, out_of_plane_distribution, offset, **kwargs):
        epilayer_set = set(tuple(site) for site in epilayer_list)
        epilayer_set_length = len(epilayer_list)
        rand_atom_list = []
        rand_atom_sites = []
        number_of_sites = len(epilayer_set)
        i = 0
        while epilayer_set:
            x0,y0 = random.choice(list(epilayer_set))
            x = x0 + 0.1*(substrate_lattice_constant*np.random.random_sample()-substrate_lattice_constant/2)
            y = y0 + 0.1*(substrate_lattice_constant*np.random.random_sample()-substrate_lattice_constant/2)
            if out_of_plane_distribution == 'gaussian':
                z = np.random.normal((kwargs['z_low']+kwargs['z_high'])/2,kwargs['z_high']-kwargs['z_low'])
                if z < kwargs['z_low']:
                    z = kwargs['z_low']
                if z > kwargs['z_high']:
                    z = kwargs['z_high']
            elif out_of_plane_distribution == 'uniform':
                z = np.random.uniform(kwargs['z_low'], kwargs['z_high'])
            elif out_of_plane_distribution == 'completely random':
                z = np.random.random_sample()*(kwargs['z_high'] - kwargs['z_low']) + kwargs['z_low']
            rand_atom_list.append([x+offset[0],y+offset[1]])
            rand_atom_sites.append(pgSites.Site(atom,[x+offset[0],y+offset[1],z+offset[2]]))
            if in_plane_distribution == 'completely random':
                density = kwargs['buffer_density']
                number_of_sites = density*len(epilayer_set)
                epilayer_set.remove((x0,y0))
            else:
                if in_plane_distribution == 'geometric':
                    radius = np.random.geometric(kwargs['buffer_gamma'])
                elif in_plane_distribution == 'delta':
                    radius = kwargs['buffer_radius']
                elif in_plane_distribution == 'uniform':
                    radius = np.random.uniform(kwargs['buffer_in_plane_low'], kwargs['buffer_in_plane_high'])
                elif in_plane_distribution == 'buffer_binomial':
                    radius = np.random.binomial(kwargs['buffer_n'],kwargs['buffer_p'])
                epilayer_set_temp = epilayer_set.copy()
                for (dx,dy) in epilayer_set_temp:
                    if (dx-x0)**2+(dy-y0)**2 <= radius**2:
                        epilayer_set.remove((dx,dy))
            if i <= number_of_sites:
                i += 1
                self.PROGRESS_ADVANCE.emit(0,100,np.round(100-len(epilayer_set)/epilayer_set_length*100,1))
                QtCore.QCoreApplication.processEvents()
            else:
                break
            if self._abort:
                break
        self.PROGRESS_END.emit()
        QtCore.QCoreApplication.processEvents()
        if not self._abort:
            return np.array(rand_atom_list), rand_atom_sites
        else:
            return None, None

    def get_substrate(self,structure, orientation, X_max, Y_max, Z_min, Z_max, use_atoms):
        if use_atoms:
            unit_cell_sites_sub = [pgSites.Site({site.as_dict()['species'][0]['element']:site.as_dict()['species'][0]['occu']},[site.x,site.y,site.z]) \
                                   for site in structure.sites if (site.z>=Z_min*structure.lattice.c and site.z<Z_max*structure.lattice.c)]
        else:
            species = self.get_heavist_element(structure)
            unit_cell_sites_sub = [pgSites.Site({species:1},[0,0,0])]

        substrate_sites = []
        substrate_list = []
        substrate_set = set()
        if orientation == '(001)':
            a = structure.lattice.a
            b = structure.lattice.b
            angle = structure.lattice.gamma
        elif orientation == '(111)':
            a = structure.lattice.a/np.sqrt(2)
            b = structure.lattice.a/np.sqrt(2)
            angle = 120
        xa, yb = int(X_max/a), int(Y_max/b/np.sin(angle/180*np.pi))
        for i,j in itertools.product(range(-xa, xa+1), range(-yb, yb+1)):
            offset = int(j*b*np.cos(angle/180*np.pi)/a)
            x = (i-offset)*a+j*b*np.cos(angle/180*np.pi)
            y = j*b*np.sin(angle/180*np.pi)
            if orientation == '(001)':
                for site in unit_cell_sites_sub:
                    substrate_sites.append(pgSites.Site({site.as_dict()['species'][0]['element']:site.as_dict()['species'][0]['occu']},[site.x+x,site.y+y,site.z]))
            elif orientation == '(111)':
                site = unit_cell_sites_sub[0]
                substrate_sites.append(pgSites.Site({site.as_dict()['species'][0]['element']:site.as_dict()['species'][0]['occu']},[site.x+x,site.y+y,site.z]))
            substrate_set.add((x,y))
            substrate_list.append([x,y])
            QtCore.QCoreApplication.processEvents()
            if self._abort:
                break
            else:
                self.PROGRESS_ADVANCE.emit(0,100,((i+xa)*(2*yb)+(j+yb))/(2*xa*2*yb)*100)
                QtCore.QCoreApplication.processEvents()
        self.PROGRESS_END.emit()
        QtCore.QCoreApplication.processEvents()
        if not self._abort:
            return substrate_set, substrate_list, substrate_sites
        else:
            return None, None, None

    def get_boundaryless_epilayer(self,structure,orientation,X_max,Y_max, Z_min, Z_max, offset, use_atoms):
        if use_atoms:
            unit_cell_sites_epi = [pgSites.Site({site.as_dict()['species'][0]['element']:site.as_dict()['species'][0]['occu']},[site.x+offset[0],site.y+offset[1],site.z+offset[2]]) \
                                   for site in structure.sites if (site.z>=Z_min*structure.lattice.c and site.z<Z_max*structure.lattice.c)]
        else:
            species = self.get_heavist_element(structure)
            unit_cell_sites_epi = [pgSites.Site({species:1},[offset[0],offset[1],offset[2]])]

        if orientation == '(001)':
            a = structure.lattice.a
            b = structure.lattice.b
            angle = structure.lattice.gamma
        elif orientation == '(111)':
            a = structure.lattice.a/np.sqrt(2)
            b = structure.lattice.a/np.sqrt(2)
            angle = 120
        rectangle = Polygon([(-X_max,-Y_max),(-X_max,Y_max),(X_max,Y_max),(X_max,-Y_max)])
        epilayer_list, epilayer_sites, epilayer_domain_area, epilayer_domain_boundary, gap_add_out, gap_subtract_out, domain = self.get_boundaryless_domain(a, b, angle, rectangle, unit_cell_sites_epi)
        return epilayer_list, epilayer_sites, [epilayer_domain_area], [epilayer_domain_boundary], None, domain

    def get_epilayer(self,vor,structure,orientation,X_max,Y_max, Z_min, Z_max, offset, use_atoms):
        epilayer_list = []
        epilayer_sites = []
        epilayer_domain_area_list = []
        epilayer_domain_boundary_list = []
        epilayer_boundary_sites = []
        epilayer_domain_list = []
        gap_add = {}
        gap_subtract = {}
        rectangle = Polygon([(-X_max,-Y_max),(-X_max,Y_max),(X_max,Y_max),(X_max,-Y_max)])
        region_vertices_dict = self.get_region_vertices_dict(vor,X_max,Y_max)
        if use_atoms:
            unit_cell_sites_epi = [pgSites.Site({site.as_dict()['species'][0]['element']:site.as_dict()['species'][0]['occu']},[site.x+offset[0],site.y+offset[1],site.z+offset[2]]) \
                                   for site in structure.sites if (site.z>=Z_min*structure.lattice.c and site.z<Z_max*structure.lattice.c)]
        else:
            species = self.get_heavist_element(structure)
            unit_cell_sites_epi = [pgSites.Site({species:1},[offset[0],offset[1],offset[2]])]

        if orientation == '(001)':
            a = structure.lattice.a
            b = structure.lattice.b
            angle = structure.lattice.gamma
        elif orientation == '(111)':
            a = structure.lattice.a/np.sqrt(2)
            b = structure.lattice.a/np.sqrt(2)
            angle = 120
        for point_index, region_index in enumerate(vor.point_region):
            self.PROGRESS_ADVANCE.emit(0,100,np.round(point_index/len(vor.point_region)*100,1))
            QtCore.QCoreApplication.processEvents()
            point = vor.points[point_index]
            vertices = region_vertices_dict[tuple(point)]
            if len(vertices)>=3:
                original_polygon = Polygon(self.sortpts_clockwise(np.array(vertices)))
                if original_polygon.is_valid:
                    polygon = original_polygon.intersection(rectangle)
                    if polygon:
                        epilayer_domain, epilayer_domain_sites, epilayer_domain_area, epilayer_domain_boundary, epilayer_domain_boundary_sites, gap_add_out, gap_subtract_out, domain = self.get_domain(a, b, angle, point, polygon, gap_add, gap_subtract, unit_cell_sites_epi)
                        if epilayer_domain:
                            epilayer_list += epilayer_domain
                            epilayer_sites += epilayer_domain_sites
                            epilayer_domain_list.append(domain)
                            gap_add.update(gap_add_out)
                            gap_subtract.update(gap_subtract_out)
                            if not -1 in vor.regions[region_index]:
                                epilayer_domain_area_list.append(epilayer_domain_area)
                                epilayer_domain_boundary_list.append(epilayer_domain_boundary)
                                epilayer_boundary_sites += epilayer_domain_boundary_sites
            if self._abort:
                break
        self.PROGRESS_END.emit()
        QtCore.QCoreApplication.processEvents()
        if not self._abort:
            self.UPDATE_LOG.emit('Filtering atoms that are too close ...')
            return epilayer_list, epilayer_sites, epilayer_domain_area_list, epilayer_domain_boundary_list, epilayer_boundary_sites, epilayer_domain_list
        else:
            return None, None, None, None, None, None

    def get_region_vertices_dict(self,vor,x_max,y_max):
        region_vertices_dict = {}
        oversize_factor = 3
        rectangle = Polygon([(-oversize_factor*x_max,-oversize_factor*y_max),(-oversize_factor*x_max,oversize_factor*y_max),(oversize_factor*x_max,oversize_factor*y_max),(oversize_factor*x_max,-oversize_factor*y_max)])
        ptp_bound = vor.points.ptp(axis=0)
        center = vor.points.mean(axis=0)
        for point in vor.points:
            region_vertices_dict[tuple(point)] = []
        for pointidx, simplex in zip(vor.ridge_points, vor.ridge_vertices):
            simplex = np.asarray(simplex)
            if np.all(simplex >= 0):
                intersection = rectangle.intersection(LineString(vor.vertices[simplex]))
            if np.any(simplex < 0):
                i = simplex[simplex >= 0][0]
                t = vor.points[pointidx[1]] - vor.points[pointidx[0]]
                t /= np.linalg.norm(t)
                n = np.array([-t[1], t[0]])
                midpoint = vor.points[pointidx].mean(axis=0)
                direction = np.sign(np.dot(midpoint - center, n)) * n
                far_point = vor.vertices[i] + direction * ptp_bound.max()
                intersection = rectangle.intersection(LineString([(vor.vertices[i, 0], vor.vertices[i, 1]),(far_point[0], far_point[1])]))
            if intersection:
                region_vertices_dict[tuple(vor.points[pointidx[0]])].append(list(intersection.coords[0]))
                region_vertices_dict[tuple(vor.points[pointidx[0]])].append(list(intersection.coords[1]))
                region_vertices_dict[tuple(vor.points[pointidx[1]])].append(list(intersection.coords[0]))
                region_vertices_dict[tuple(vor.points[pointidx[1]])].append(list(intersection.coords[1]))
        return region_vertices_dict

    def point_in_triangle(self,v1,v2,v3,p,r):
        d1 = self.left_or_right(p,v1,v2)
        d2 = self.left_or_right(p,v2,v3)
        d3 = self.left_or_right(p,v3,v1)
        has_neg = (d1<0) or (d2<0) or (d3<0)
        has_pos = (d1>0) or (d2>0) or (d3>0)
        return (not (has_neg and has_pos)) or self.within_vertex(v1,p,r) or self.within_vertex(v2,p,r) or self.within_vertex(v3,p,r)

    def left_or_right(self,p1,p2,p3):
        return (p1[0]-p3[0])*(p2[1]-p3[1]) - (p2[0]-p3[0])*(p1[1]-p3[1])

    def within_vertex(self,v,p,r):
        return (v[0]-p[0])**2+(v[1]-p[1])**2 < (r/2)**2

    def get_boundaryless_domain(self, a, b, angle, rectangle, unit_cell_sites_epi):
        epilayer_domain = []
        epilayer_domain_sites = []
        bounding_box = list(rectangle.bounds)
        for i,j in itertools.product(range(int(bounding_box[0]/a)-5,int(bounding_box[2]/a)+6), \
                                    range(int(bounding_box[1]/b/np.sin(angle/180*np.pi))-5,int(bounding_box[3]/b/np.sin(angle/180*np.pi))+6)):
            offset = int(j*b*np.cos(angle/180*np.pi)/a)
            x = (i-offset)*a+j*b*np.cos(angle/180*np.pi)
            y = j*b*np.sin(angle/180*np.pi)
            if rectangle.contains(Point(x,y)):
                epilayer_domain.append([x,y])
                for site in unit_cell_sites_epi:
                    print(site)
                    epilayer_domain_sites.append(pgSites.Site({site.as_dict()['species'][0]['element']:site.as_dict()['species'][0]['occu']},[site.x+x,site.y+y,site.z]))
        return epilayer_domain, epilayer_domain_sites, rectangle.area, None,None,None,rectangle 


    def get_domain(self, a, b, angle, point, polygon, gap_add_in, gap_subtract_in, unit_cell_sites_epi):
        try:
            vertices = list(polygon.exterior.coords)
        except AttributeError:
            vertices = []
            for p in polygon:
                vertices.append(p.exterior.coords)
        extended_polygon = [polygon]
        exclusion = []
        for first, second in zip(vertices, vertices[1:]):
            add_gap = gap_add_in.get((first,second), None)
            subtract_gap = gap_subtract_in.get((first,second), None)
            if add_gap:
                extended_polygon.append(add_gap)
            if subtract_gap:
                exclusion.append(subtract_gap)
        domain_include = unary_union(extended_polygon)
        domain_exclude = unary_union(exclusion)
        if (domain_include.is_valid) or (np.all(subdomain.is_valid for subdomain in domain_include)):
            epilayer_domain = []
            epilayer_domain_sites = []
            hull_sites = []
            bounding_box = list(polygon.bounds)
            bounding_box[0] -= point[0]
            bounding_box[1] -= point[1]
            bounding_box[2] -= point[0]
            bounding_box[3] -= point[1]
        
            for i,j in itertools.product(range(int(bounding_box[0]/a)-5,int(bounding_box[2]/a)+6), \
                                        range(int(bounding_box[1]/b/np.sin(angle/180*np.pi))-5,int(bounding_box[3]/b/np.sin(angle/180*np.pi))+6)):
                offset = int(j*b*np.cos(angle/180*np.pi)/a)
                x = (i-offset)*a+j*b*np.cos(angle/180*np.pi) + point[0]
                y = j*b*np.sin(angle/180*np.pi) + point[1]
                try:
                    condition1 = domain_include.buffer(max(a,b)*0.001).intersects(Point(x,y))
                except:
                    condition1 = (np.any(subdomain.buffer(max(a,b)*0.001).intersects(Point(x,y)) for subdomain in domain_include))
                try:
                    condition2 = not domain_exclude.contains(Point(x,y))
                except:
                    condition2 = not np.any(subdomain.contains(Point(x,y)) for subdomain in domain_exclude)
                if condition1 and condition2 :
                    epilayer_domain.append([x,y])
                    for site in unit_cell_sites_epi:
                        epilayer_domain_sites.append(pgSites.Site({site.as_dict()['species'][0]['element']:site.as_dict()['species'][0]['occu']},[site.x+x,site.y+y,site.z]))
            point_cloud = MultiPoint(epilayer_domain)   
            try:
                hull = ConvexHull(epilayer_domain, qhull_options='Qc')
                x_list = []
                y_list = []
                for vertex_index in hull.vertices:
                    x_list.append(hull.points[vertex_index][0])
                    y_list.append(hull.points[vertex_index][1])
                for vertex_index in hull.coplanar:
                    if not (hull.points[vertex_index[0]][0] in x_list and hull.points[vertex_index[0]][1] in y_list):
                        x_list.append(hull.points[vertex_index[0]][0])
                        y_list.append(hull.points[vertex_index[0]][1])
                for x, y in zip(x_list, y_list):
                    for site in unit_cell_sites_epi:
                        hull_sites.append(pgSites.Site({site.as_dict()['species'][0]['element']:site.as_dict()['species'][0]['occu']},[site.x+x,site.y+y,site.z]))
            except:
                hull = epilayer_domain
                for point in hull:
                    for site in unit_cell_sites_epi:
                        hull_sites.append(pgSites.Site({site.as_dict()['species'][0]['element']:site.as_dict()['species'][0]['occu']},[site.x+point[0],site.y+point[1],site.z]))

            gap_add_out = {}
            gap_subtract_out = {}
            if point_cloud.is_valid:
                for first, second in zip(vertices, vertices[1:]):
                    gap_add = Polygon([first, second, point]).difference(point_cloud.buffer(max(a,b)*0.999,resolution=64))
                    gap_subtract = point_cloud.buffer(max(a,b)*0.999,resolution=64).difference(Polygon([first, second, point]))
                    if not gap_add.is_empty:
                        if not (first, second) in gap_add_in:
                            gap_add_out[(first,second)] = gap_add
                            gap_add_out[(second,first)] = gap_add
                    if not gap_subtract.is_empty:
                        if not (first, second) in gap_subtract_in:
                            gap_subtract_out[(first,second)] = gap_subtract
                            gap_subtract_out[(second,first)] = gap_subtract
            return epilayer_domain, epilayer_domain_sites, polygon.area, hull, hull_sites, gap_add_out, gap_subtract_out, domain_include
        else:
            return None,None,None,None,None,None, None, None

    def sortpts_clockwise(self,points):
        self.origin = np.mean(points,axis=0)
        sorted_points = sorted(points, key=self.get_clockwise_angle_and_distance)
        return sorted_points

    def get_clockwise_angle_and_distance(self,point):
        refvec=[0,1]
        vector = [point[0]-self.origin[0], point[1]-self.origin[1]]
        lenvector = math.hypot(vector[0], vector[1])
        normalized = [vector[0]/lenvector, vector[1]/lenvector]
        dotprod  = normalized[0]*refvec[0] + normalized[1]*refvec[1]
        diffprod = refvec[1]*normalized[0] - refvec[0]*normalized[1]
        angle = math.atan2(diffprod, dotprod)
        if angle < 0:
            return 2*math.pi+angle, lenvector
        return angle, lenvector

if __name__ == '__main__':
    fit = FitFunctions()
    fit.test()
