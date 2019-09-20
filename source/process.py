import glob
import itertools
import math
import matplotlib.pyplot as plt
import numpy as np
import os
import PIL.Image as pilImage
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
from pymatgen.io.cif import CifParser
from pymatgen.core import sites as pgSites
from pymatgen.core import structure as pgStructure
from pymatgen.core import periodic_table
from PyQt5 import QtGui,QtCore, QtWidgets
from scipy.optimize import least_squares
from scipy.spatial import ConvexHull
from scipy.spatial import Voronoi
from scipy.spatial import voronoi_plot_2d
from scipy.spatial import cKDTree
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

    def get_image(self,bit_depth,img_path,EnableAutoWB, Brightness, UserBlack, image_crop):
        pathExtension = os.path.splitext(img_path)[1]
        if pathExtension in self.supportedRawFormats:
            img_raw = rawpy.imread(img_path)
            img_rgb = img_raw.postprocess(demosaic_algorithm=rawpy.DemosaicAlgorithm.AHD, output_bps = bit_depth, use_auto_wb = EnableAutoWB,bright=Brightness/100,user_black=UserBlack)
            img_bw = (0.21*img_rgb[:,:,0])+(0.72*img_rgb[:,:,1])+(0.07*img_rgb[:,:,2])
            img_array = img_bw[image_crop[0]:image_crop[1],image_crop[2]:image_crop[3]]
            if bit_depth == 16:
                img_array = np.uint8(img_array/256)
            if bit_depth == 8:
                img_array = np.uint8(img_array)
            qImg = QtGui.QImage(img_array,img_array.shape[1],img_array.shape[0],img_array.shape[1], QtGui.QImage.Format_Grayscale8)
            return qImg, img_array
        elif pathExtension in self.supportedImageFormats:
            img = pilImage.open(img_path)
            img_rgb = np.fromstring(img.tobytes(),dtype=np.uint8)
            img_rgb = img_rgb.reshape((img.size[1],img.size[0],3))
            img_array = (0.21*img_rgb[:,:,0])+(0.72*img_rgb[:,:,1])+(0.07*img_rgb[:,:,2])
            #img_array = img_bw[image_crop[0]:image_crop[1],image_crop[2]:image_crop[3]]
            qImg = QtGui.QImage(np.uint8(img_array),img_array.shape[1],img_array.shape[0],img_array.shape[1], QtGui.QImage.Format_Grayscale8)
            return qImg, img_array

    def get_line_scan(self,start,end,img,scale_factor):
        x0,y0,x1,y1 = start.x(),start.y(),end.x(),end.y()
        K_length = max(int(abs(x1-x0)+1),int(abs(y1-y0)+1))
        Kx = np.linspace(x0,x1,K_length)
        Ky = np.linspace(y0,y1,K_length)
        LineScanIntensities = np.zeros(len(Kx))
        for i in range(0,len(Kx)):
            LineScanIntensities[i] = img[int(Ky[i]),int(Kx[i])]
        LineScanRadius = np.linspace(0,math.sqrt((x1-x0)**2+(y1-y0)**2),len(Kx))
        return LineScanRadius/scale_factor,LineScanIntensities/np.amax(np.amax(img))

    def get_integral(self,start,end,width,img,scale_factor):
        x0,y0,x1,y1 = start.x(),start.y(),end.x(),end.y()
        K_length = max(int(abs(x1-x0)+1),int(abs(y1-y0)+1))
        int_width = int(width)
        Kx = np.linspace(x0,x1,K_length)
        Ky = np.linspace(y0,y1,K_length)
        LineScanIntensities = np.zeros(len(Kx))
        LineScanRadius = np.linspace(0,math.sqrt((x1-x0)**2+(y1-y0)**2),len(Kx))
        if y1 == y0:
            for i in range (0,len(Kx)): LineScanIntensities[i] = np.sum(img[int(Ky[i])-int_width:int(Ky[i])+\
                                        int_width,int(Kx[i])])
        elif x1 == x0:
            for i in range (0,len(Kx)): LineScanIntensities[i] = np.sum(img[int(Ky[i]),int(Kx[i])-int_width:\
                                        int(Kx[i])+int_width])
        else:
            slope =(x0-x1)/(y1-y0)
            if abs(slope) > 1:
                index = np.asarray([[np.linspace(Ky[i]-int_width,Ky[i]+int_width+1,2*int_width+1),\
                                     np.linspace(Kx[i]-int_width/slope,Kx[i]+(int_width+1)/slope,2*int_width+1)] for i in range(len(Kx))],dtype=int)
            else:
                index = np.asarray([[np.linspace(Ky[i]-int_width*slope,Ky[i]+(int_width+1)*slope,2*int_width+1),\
                                     np.linspace(Kx[i]-int_width,Kx[i]+int_width+1,2*int_width+1)] for i in range(len(Kx))],dtype=int)
            try:
                LineScanIntensities = np.sum([img[index[i,0,:],index[i,1,:]] for i in range(len(Kx))],axis=1)
            except:
                self.raise_error("index out of bounds")
        return LineScanRadius/scale_factor,LineScanIntensities/2/width/np.amax(np.amax(img))

    def get_chi_scan(self,center,radius,width,chiRange,tilt,img,chiStep=1):
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
        ChiProfile = np.sum([img[ImageIndices[i,1,:]+int(y0),ImageIndices[i,0,:]+int(x0)] for i in range(ChiTotalSteps+1)], axis=1)/cit
        return np.flip(ChiAngle2,axis=0),ChiProfile/np.amax(np.amax(img))

    def raise_error(self,message):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.setEscapeButton(QtWidgets.QMessageBox.Close)
        msg.exec()

    def raise_attention(self,information):
        info = QtWidgets.QMessageBox()
        info.setIcon(QtWidgets.QMessageBox.Information)
        info.setText(information)
        info.setWindowTitle("Information")
        info.setStandardButtons(QtWidgets.QMessageBox.Ok)
        info.setEscapeButton(QtWidgets.QMessageBox.Close)
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

    def mtx2vtp(self,dir,name,matrix,KRange,N_para,N_perp,specification,species):
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
    ERROR = QtCore.pyqtSignal(str)
    ATTENTION = QtCore.pyqtSignal(str)
    ABORTED = QtCore.pyqtSignal()

    def __init__(self,status,path,default,IsPoleFigure,IsCentered,IsSaveResult,Is2D,IsCartesian,startIndex,endIndex,analysisRange,destination,saveFileName,fileType,group):
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
        self.IsCentered = IsCentered
        self.IsSaveResult = IsSaveResult
        self.Is2D = Is2D
        self.IsCartesian = IsCartesian
        self.group = group
        self.image_worker = Image()
        self.convertor_worker = Convertor()
        self._abort = False

    def run(self):
        image_list = []
        autoWB = self.status["autoWB"]
        brightness = self.status["brightness"]
        blackLevel = self.status["blackLevel"]
        mode = self.status["mode"]
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
                map_2D1=np.array([0,0,0])
                map_2D2=np.array([0,0,0])
                self.SET_TITLE.emit("Chi Scan at R = {:3.2f} \u212B\u207B\u00B9".format(radius))
                QtCore.QCoreApplication.processEvents()
                for nimg in range(self.startIndex,self.endIndex+1):
                    qImg, img = self.image_worker.get_image(16,image_list[nimg-self.startIndex],autoWB,brightness,blackLevel,image_crop)
                    RC,I = self.image_worker.get_chi_scan(start,radius*scale_factor,width,chiRange,tiltAngle,img,chiStep)
                    Phi1 = np.full(len(RC),nimg*1.8)
                    Phi2 = np.full(len(RC),nimg*1.8)
                    for iphi in range(0,int(len(RC)/2)):
                        Phi1[iphi]=nimg*1.8+180
                    map_2D1 = np.vstack((map_2D1,np.vstack((abs(RC),Phi1,I)).T))
                    map_2D2 = np.vstack((map_2D2,np.vstack((RC,Phi2,I)).T))
                    if self.IsCentered:
                        self.UPDATE_CHART.emit(RC,I,"arc")
                    else:
                        self.UPDATE_CHART.emit(abs(RC),I,"arc")
                    self.PROGRESS_ADVANCE.emit(0,100,(nimg+1-self.startIndex)*100/(self.endIndex-self.startIndex+1))
                    self.UPDATE_LOG.emit("The file being processed right now is: "+image_list[nimg-self.startIndex])
                    QtCore.QCoreApplication.processEvents()
                    if self._abort:
                        break
                if not self._abort:
                    if self.IsCentered:
                        pole_figure = np.delete(map_2D2,0,0)
                    else:
                        pole_figure = np.delete(map_2D1,0,0)
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
                if self.Is2D:
                    Kperp = (np.abs((end.y()-start.y())*origin.x()-(end.x()-start.x())*origin.y()+end.x()*start.y()-end.y()*start.x())/ \
                             np.sqrt((end.y()-start.y())**2+(end.x()-start.x())**2))/scale_factor
                    map_2D1=np.array([0,0,0])
                    map_2D2=np.array([0,0,0])
                    self.SET_TITLE.emit("Line Profile at Kperp = {:4.2f} (\u212B\u207B\u00B9)".format(Kperp))
                    QtCore.QCoreApplication.processEvents()
                    for nimg in range(self.startIndex,self.endIndex+1):
                        qImg, img = self.image_worker.get_image(16,image_list[nimg-self.startIndex],autoWB,brightness,blackLevel,image_crop)
                        if width==0.0:
                            RC,I = self.image_worker.get_line_scan(start,end,img,scale_factor)
                        else:
                            RC,I = self.image_worker.get_integral(start,end,width,img,scale_factor)
                        Phi1 = np.full(len(RC),nimg*1.8)
                        Phi2 = np.full(len(RC),nimg*1.8)
                        maxPos = np.argmax(I)
                        for iphi in range(0,maxPos):
                            Phi1[iphi]=nimg*1.8+180
                        if maxPos<(len(RC)-1)/2:
                            x1,y1 = abs(RC[0:(2*maxPos+1)]-RC[maxPos]), I[0:(2*maxPos+1)]/I[maxPos]
                            map_2D1 = np.vstack((map_2D1,np.vstack((x1,Phi1[0:(2*maxPos+1)],y1)).T))
                            x2,y2 = RC[0:(2*maxPos+1)]-RC[maxPos],I[0:(2*maxPos+1)]/I[maxPos]
                            map_2D2 = np.vstack((map_2D2,np.vstack((x2,Phi2[0:(2*maxPos+1)],y2)).T))
                        else:
                            x1,y1 = abs(RC[(2*maxPos-len(RC)-1):-1]-RC[maxPos]), I[(2*maxPos-len(RC)-1):-1]/I[maxPos]
                            map_2D1 = np.vstack((map_2D1,np.vstack((x1,Phi1[(2*maxPos-len(RC)-1):-1],y1)).T))
                            x2,y2 = RC[(2*maxPos-len(RC)-1):-1]-RC[maxPos], I[(2*maxPos-len(RC)-1):-1]/I[maxPos]
                            map_2D2 = np.vstack((map_2D2,np.vstack((x2,Phi2[(2*maxPos-len(RC)-1):-1],y2)).T))
                        if self.IsCentered:
                            self.UPDATE_CHART.emit(x2,y2,"line")
                        else:
                            self.UPDATE_CHART.emit(x1,y1,"line")
                        self.PROGRESS_ADVANCE.emit(0,100,(nimg+1-self.startIndex)*100/(self.endIndex-self.startIndex+1))
                        self.UPDATE_LOG.emit("The file being processed right now is: "+image_list[nimg-self.startIndex])
                        QtCore.QCoreApplication.processEvents()
                        if self._abort:
                            break
                    if not self._abort:
                        if self.IsCentered:
                            map_2D_polar = np.delete(map_2D2,0,0)
                        else:
                            map_2D_polar = np.delete(map_2D1,0,0)
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
                    map_3D1=np.array([0,0,0,0])
                    map_3D2=np.array([0,0,0,0])
                    for nimg in range(self.startIndex,self.endIndex+1):
                        qImg, img = self.image_worker.get_image(16,image_list[nimg-self.startIndex],autoWB,brightness,blackLevel,image_crop)
                        x0,y0,xn,yn = start.x(),start.y(),end.x(),end.y()
                        newStart = QtCore.QPointF()
                        newEnd = QtCore.QPointF()
                        if width==0.0:
                            step = 5
                            nos = int(self.analysisRange*scale_factor/step)
                        else:
                            nos = int(self.analysisRange*scale_factor/width)
                            step = width
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
                                RC,I = self.image_worker.get_line_scan(newStart,newEnd,img,scale_factor)
                                self.DRAW_LINE_REQUESTED.emit(newStart,newEnd,False)
                            else:
                                RC,I = self.image_worker.get_integral(newStart,newEnd,width,img,scale_factor)
                                self.DRAW_RECT_REQUESTED.emit(newStart,newEnd,width,False)
                            QtCore.QCoreApplication.processEvents()
                            rem = np.remainder(len(RC),self.group)
                            if not rem == 0:
                                RC = np.pad(RC,(0,self.group-rem),'edge')
                                I = np.pad(I,(0,self.group-rem),'edge')
                            RC,I = RC.reshape(-1,self.group).mean(axis=1), I.reshape(-1,self.group).mean(axis=1)
                            Phi1 = np.full(len(RC),nimg*1.8)
                            Phi2 = np.full(len(RC),nimg*1.8)
                            maxPos = np.argmax(I)
                            for iphi in range(0,maxPos):
                                Phi1[iphi]=nimg*1.8+180
                            if maxPos<(len(RC)-1)/2:
                                x1,y1 = abs(RC[0:(2*maxPos+1)]-RC[maxPos]), I[0:(2*maxPos+1)]/I[maxPos]
                                K = np.full(len(x1),Kperp)
                                map_3D1 = np.vstack((map_3D1,np.vstack((x1,Phi1[0:(2*maxPos+1)],K,y1)).T))
                                x2,y2 = RC[0:(2*maxPos+1)]-RC[maxPos],I[0:(2*maxPos+1)]/I[maxPos]
                                map_3D2 = np.vstack((map_3D2,np.vstack((x2,Phi2[0:(2*maxPos+1)],K,y2)).T))
                            else:
                                x1,y1 = abs(RC[(2*maxPos-len(RC)-1):-1]-RC[maxPos]), I[(2*maxPos-len(RC)-1):-1]/I[maxPos]
                                K = np.full(len(x1),Kperp)
                                map_3D1 = np.vstack((map_3D1,np.vstack((x1,Phi1[(2*maxPos-len(RC)-1):-1],K,y1)).T))
                                x2,y2 = RC[(2*maxPos-len(RC)-1):-1]-RC[maxPos], I[(2*maxPos-len(RC)-1):-1]/I[maxPos]
                                map_3D2 = np.vstack((map_3D2,np.vstack((x2,Phi2[(2*maxPos-len(RC)-1):-1],K,y2)).T))
                            if self.IsCentered:
                                self.UPDATE_CHART.emit(x2,y2,"line")
                            else:
                                self.UPDATE_CHART.emit(x1,y1,"line")
                            self.PROGRESS_ADVANCE.emit(0,100,(i+nos*(nimg-self.startIndex))*100/((self.endIndex-self.startIndex+1)*nos))
                            self.UPDATE_LOG.emit("The file being processed right now is: "+image_list[nimg-self.startIndex])
                            QtCore.QCoreApplication.processEvents()
                        if self._abort:
                            break
                    QtCore.QCoreApplication.processEvents()
                    if not self._abort:
                        if self.IsCentered:
                            map_3D_polar = np.delete(map_3D2,0,0)
                        else:
                            map_3D_polar = np.delete(map_3D1,0,0)
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
    FINISHED = QtCore.pyqtSignal()
    ELAPSED_TIME = QtCore.pyqtSignal(float)

    def __init__(self,Kx,Ky,Kz,AFF,atoms, constant_atomic_structure_factor=False):
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
        self.XYZ = np.dstack((self.Kx,self.Ky,self.Kz)).reshape((self.Kx.shape[0],self.Kx.shape[1],self.Kx.shape[2],3))
        self.AFF = AFF
        self.constant_atomic_structure_factor = constant_atomic_structure_factor
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

    def exponent_gen(self):
        n = 0
        while n < len(self.atoms_list)-1 and (not self._abort):
            n+=1
            yield np.multiply(self.af_dict[list(self.atoms_list.values())[n]],np.exp(1j*(np.tensordot(self.XYZ,np.array(self.coord_list[n]).T,axes=1))))
            self.PROGRESS_ADVANCE.emit(0,100,n/(len(self.atoms_list)-1)*100)
            QtCore.QCoreApplication.processEvents()

    def run(self):
        start_time = time.time()
        itr = 0
        number_of_atoms = len(self.atoms_list)
        for specie in set(self.atoms_list.values()):
            if self.constant_atomic_structure_factor:
                self.af_dict[specie] = 1
            else:
                self.af_dict[specie] = self.atomic_form_factor(specie)
        #for coord,specie in self.atoms_list.items():
        #    QtCore.QCoreApplication.processEvents()
        #    if self._abort:
        #        break
        #    else:
        #        self.Psi += np.multiply(self.af_dict[specie],np.exp(1j*(self.Kx*coord[0]+self.Ky*coord[1]+self.Kz*coord[2])))
        #        itr+=1
        #        self.PROGRESS_ADVANCE.emit(0,100,itr/number_of_atoms*100)
        #        QtCore.QCoreApplication.processEvents()
        self.Psi = np.sum(e for e in self.exponent_gen())
        #self.Psi = np.sum(np.multiply(np.dstack(np.array(self.af_list)).reshape(self.Kx.shape[0],self.Kx.shape[1],self.Kx.shape[2],len(self.af_list)),np.exp(1j*(np.tensordot(self.XYZ,np.array(self.coord_list).T,axes=1)))),axis=3)
        elapsed_time = time.time() - start_time
        self.ELAPSED_TIME.emit(elapsed_time)
        if not self._abort:
            self.intensity = np.multiply(self.Psi.astype('complex64'),np.conj(self.Psi.astype('complex64')))
            self.PROGRESS_END.emit()
            self.ACCOMPLISHED.emit(self.intensity)
        else:
            self.ABORTED.emit()
            self._abort = False

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
                step = 5
                nos = int(self.analysisRange*self.scale_factor/step)
            else:
                nos = int(self.analysisRange*self.scale_factor/self.width)
                step = self.width
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
        QtCore.QCoreApplication.processEvents()
        if not self._abort:
            self.UPDATE_LOG.emit('Translational antiphase domain sites are created!')
            self.SEND_RESULTS.emit(model)
        else:
            self.UPDATE_LOG.emit('Process aborted!')
            self._abort = False
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
            if generators.any():
                self.UPDATE_LOG.emit('Nucleation created!')
                self.UPDATE_LOG.emit('Creating Voronoi ...')
                QtCore.QCoreApplication.processEvents()
                vor = Voronoi(generators)
                model.vor = vor
                self.UPDATE_LOG.emit('Voronoi is created!')
                self.UPDATE_LOG.emit('Epilayer is growing ...')
                QtCore.QCoreApplication.processEvents()
                model.epilayer_list, model.epilayer_sites, model.epilayer_domain_area_list, model.epilayer_domain_boundary_list, model.epilayer_domain = self.get_epilayer(vor, model.epilayer_structure, epi_orientation, X_max, Y_max, Z_min, Z_max, offset, use_atoms)
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
        while substrate_set:
            x,y = random.choice(list(substrate_set))
            randPoints.append([x,y])
            if distribution == 'completely random':
                density = kwargs['density']
                if density > 0:
                    number_of_sites = density*len(substrate_set)
                elif density == 0:
                    number_of_sites = 1
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

    def get_epilayer(self,vor,structure,orientation,X_max,Y_max, Z_min, Z_max, offset, use_atoms):
        epilayer_list = []
        epilayer_sites = []
        epilayer_domain_area_list = []
        epilayer_domain_boundary_list = []
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
                        epilayer_domain, epilayer_domain_sites, epilayer_domain_area, epilayer_domain_boundary, gap_add_out, gap_subtract_out, domain = self.get_domain(a, b, angle, point, polygon, gap_add, gap_subtract, X_max, Y_max,unit_cell_sites_epi)
                        if epilayer_domain:
                            epilayer_list += epilayer_domain
                            epilayer_sites += epilayer_domain_sites
                            epilayer_domain_list.append(domain)
                            gap_add.update(gap_add_out)
                            gap_subtract.update(gap_subtract_out)
                            if not -1 in vor.regions[region_index]:
                                epilayer_domain_area_list.append(epilayer_domain_area)
                                epilayer_domain_boundary_list.append(epilayer_domain_boundary)
            if self._abort:
                break
        self.PROGRESS_END.emit()
        QtCore.QCoreApplication.processEvents()
        if not self._abort:
            self.UPDATE_LOG.emit('Filtering atoms that are too close ...')
            return epilayer_list, epilayer_sites, epilayer_domain_area_list, epilayer_domain_boundary_list, epilayer_domain_list
        else:
            return None, None, None, None, None

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

    def get_domain(self, a, b, angle, point, polygon, gap_add_in, gap_subtract_in, X_max, Y_max, unit_cell_sites_epi):
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
            except:
                hull = epilayer_domain
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
            return epilayer_domain, epilayer_domain_sites, polygon.area, hull, gap_add_out, gap_subtract_out, domain_include
        else:
            return None,None,None,None,None,None, None

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

