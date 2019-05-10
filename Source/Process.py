import numpy as np
from PyQt5 import QtGui,QtCore, QtWidgets
from scipy.optimize import least_squares
import rawpy
import math
import os
import glob
import itertools
import PIL.Image as pilImage
from math import pi as Pi
from lxml import etree as ET

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

    def getImage(self,bit_depth,img_path,EnableAutoWB, Brightness, UserBlack, image_crop):
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

    def getLineScan(self,start,end,img,scale_factor):
        x0,y0,x1,y1 = start.x(),start.y(),end.x(),end.y()
        K_length = max(int(abs(x1-x0)+1),int(abs(y1-y0)+1))
        Kx = np.linspace(x0,x1,K_length)
        Ky = np.linspace(y0,y1,K_length)
        LineScanIntensities = np.zeros(len(Kx))
        for i in range(0,len(Kx)):
            LineScanIntensities[i] = img[int(Ky[i]),int(Kx[i])]
        LineScanRadius = np.linspace(0,math.sqrt((x1-x0)**2+(y1-y0)**2),len(Kx))
        return LineScanRadius/scale_factor,LineScanIntensities/np.amax(np.amax(img))

    def getIntegral(self,start,end,width,img,scale_factor):
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
                self.Raise_Error("index out of bounds")
        return LineScanRadius/scale_factor,LineScanIntensities/2/width/np.amax(np.amax(img))

    def getChiScan(self,center,radius,width,chiRange,tilt,img,chiStep=1):
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

    def Raise_Error(self,message):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.setEscapeButton(QtWidgets.QMessageBox.Close)
        msg.exec()

    def Raise_Attention(self,information):
        info = QtWidgets.QMessageBox()
        info.setIcon(QtWidgets.QMessageBox.Information)
        info.setText(information)
        info.setWindowTitle("Information")
        info.setStandardButtons(QtWidgets.QMessageBox.Ok)
        info.setEscapeButton(QtWidgets.QMessageBox.Close)
        info.exec()

class Fit(object):

    def __init__(self):
        super(Fit,self).__init__()

    def gaussian(self,x,height, center,FWHM,offset=0):
        if FWHM == 0:
            FWHM = 0.001
        return height/(FWHM*math.sqrt(math.pi/(4*math.log(2))))*np.exp(-4*math.log(2)*(x - center)**2/(FWHM**2))+offset

    def gaussian_bg(self,x,H1,Hbg,C1,Cbg,W1,Wbg,offset=0):
        return (self.gaussian(x,H1,C1,W1,offset=0)+
                self.gaussian(x,Hbg,Cbg,Wbg,offset=0)+offset)

    def three_gaussians(self,x,H1,H2,H3,C1,C2,C3,W1,W2,W3,offset=0):
        return (self.gaussian(x,H1,C1,W1,offset=0)+
                self.gaussian(x,H2,C2,W2,offset=0)+
                self.gaussian(x,H3,C3,W3,offset=0)+offset)

    def three_gaussians_bg(self,x,H1,H2,H3,Hbg,C1,C2,C3,Cbg,W1,W2,W3,Wbg,offset=0):
        return (self.gaussian(x,H1,C1,W1,offset=0)+
                self.gaussian(x,H2,C2,W2,offset=0)+
                self.gaussian(x,H3,C3,W3,offset=0)+
                self.gaussian(x,Hbg,Cbg,Wbg,offset=0)+offset)

    def five_gaussians(self,x,H1,H2,H3,H4,H5,C1,C2,C3,C4,C5,W1,W2,W3,W4,W5,offset=0):
        return (self.gaussian(x,H1,C1,W1,offset=0)+
                self.gaussian(x,H2,C2,W2,offset=0)+
                self.gaussian(x,H3,C3,W3,offset=0)+
                self.gaussian(x,H4,C4,W4,offset=0)+
                self.gaussian(x,H5,C5,W5,offset=0)+offset)

    def five_gaussians_bg(self,x,H1,H2,H3,H4,H5,Hbg,C1,C2,C3,C4,C5,Cbg,\
                          W1,W2,W3,W4,W5,Wbg,offset=0):
        return (self.gaussian(x,H1,C1,W1,offset=0)+
                self.gaussian(x,H2,C2,W2,offset=0)+
                self.gaussian(x,H3,C3,W3,offset=0)+
                self.gaussian(x,H4,C4,W4,offset=0)+
                self.gaussian(x,H5,C5,W5,offset=0)+
                self.gaussian(x,Hbg,Cbg,Wbg,offset=0)+offset)

    def seven_gaussians(self,x,H1,H2,H3,H4,H5,H6,H7,C1,C2,C3,C4,C5,C6,C7,\
                        W1,W2,W3,W4,W5,W6,W7,offset=0):
        return (self.gaussian(x,H1,C1,W1,offset=0)+
                self.gaussian(x,H2,C2,W2,offset=0)+
                self.gaussian(x,H3,C3,W3,offset=0)+
                self.gaussian(x,H4,C4,W4,offset=0)+
                self.gaussian(x,H5,C5,W5,offset=0)+
                self.gaussian(x,H6,C6,W6,offset=0)+
                self.gaussian(x,H7,C7,W7,offset=0)+offset)

    def seven_gaussians_bg(self,x,H1,H2,H3,H4,H5,H6,H7,Hbg,C1,C2,C3,C4,C5,C6,C7,Cbg, \
                        W1,W2,W3,W4,W5,W6,W7,Wbg,offset=0):
        return (self.gaussian(x,H1,C1,W1,offset=0)+
                self.gaussian(x,H2,C2,W2,offset=0)+
                self.gaussian(x,H3,C3,W3,offset=0)+
                self.gaussian(x,H4,C4,W4,offset=0)+
                self.gaussian(x,H5,C5,W5,offset=0)+
                self.gaussian(x,H6,C6,W6,offset=0)+
                self.gaussian(x,H7,C7,W7,offset=0)+
                self.gaussian(x,Hbg,Cbg,Wbg,offset=0)+offset)

    def nine_gaussians(self,x,H1,H2,H3,H4,H5,H6,H7,H8,H9,C1,C2,C3,C4,C5,C6,C7,\
                       C8,C9,W1,W2,W3,W4,W5,W6,W7,W8,W9,offset=0):

        return (self.gaussian(x,H1,C1,W1,offset=0)+
                self.gaussian(x,H2,C2,W2,offset=0)+
                self.gaussian(x,H3,C3,W3,offset=0)+
                self.gaussian(x,H4,C4,W4,offset=0)+
                self.gaussian(x,H5,C5,W5,offset=0)+
                self.gaussian(x,H6,C6,W6,offset=0)+
                self.gaussian(x,H7,C7,W7,offset=0)+
                self.gaussian(x,H8,C8,W8,offset=0)+
                self.gaussian(x,H9,C9,W9,offset=0)+offset)

    def nine_gaussians_bg(self,x,H1,H2,H3,H4,H5,H6,H7,H8,H9,Hbg,C1,C2,C3,C4,C5,C6,C7,\
                          C8,C9,Cbg,W1,W2,W3,W4,W5,W6,W7,W8,W9,Wbg,offset=0):
        return (self.gaussian(x,H1,C1,W1,offset=0)+
                self.gaussian(x,H2,C2,W2,offset=0)+
                self.gaussian(x,H3,C3,W3,offset=0)+
                self.gaussian(x,H4,C4,W4,offset=0)+
                self.gaussian(x,H5,C5,W5,offset=0)+
                self.gaussian(x,H6,C6,W6,offset=0)+
                self.gaussian(x,H7,C7,W7,offset=0)+
                self.gaussian(x,H8,C8,W8,offset=0)+
                self.gaussian(x,H9,C9,W9,offset=0)+
                self.gaussian(x,Hbg,Cbg,Wbg,offset=0)+offset)

    def eleven_gaussians(self,x,H1,H2,H3,H4,H5,H6,H7,H8,H9,H10,H11,C1,C2,\
        C3,C4,C5,C6,C7,C8,C9,C10,C11,W1,W2,W3,W4,W5,W6,W7,W8,W9,W10, W11,offset=0):
        return (self.gaussian(x,H1,C1,W1,offset=0)+
                self.gaussian(x,H2,C2,W2,offset=0)+
                self.gaussian(x,H3,C3,W3,offset=0)+
                self.gaussian(x,H4,C4,W4,offset=0)+
                self.gaussian(x,H5,C5,W5,offset=0)+
                self.gaussian(x,H6,C6,W6,offset=0)+
                self.gaussian(x,H7,C7,W7,offset=0)+
                self.gaussian(x,H8,C8,W8,offset=0)+
                self.gaussian(x,H9,C9,W9,offset=0)+
                self.gaussian(x,H10,C10,W10,offset=0)+
                self.gaussian(x,H11,C11,W11,offset=0)+offset)

    def eleven_gaussians_bg(self,x,H1,H2,H3,H4,H5,H6,H7,H8,H9,H10,H11,Hbg,C1,C2, \
        C3,C4,C5,C6,C7,C8,C9,C10,C11,Cbg,W1,W2,W3,W4,W5,W6,W7,W8,W9,W10,W11,Wbg,offset=0):
        return (self.gaussian(x,H1,C1,W1,offset=0)+
                self.gaussian(x,H2,C2,W2,offset=0)+
                self.gaussian(x,H3,C3,W3,offset=0)+
                self.gaussian(x,H4,C4,W4,offset=0)+
                self.gaussian(x,H5,C5,W5,offset=0)+
                self.gaussian(x,H6,C6,W6,offset=0)+
                self.gaussian(x,H7,C7,W7,offset=0)+
                self.gaussian(x,H8,C8,W8,offset=0)+
                self.gaussian(x,H9,C9,W9,offset=0)+
                self.gaussian(x,H10,C10,W10,offset=0)+
                self.gaussian(x,H11,C11,W11,offset=0)+
                self.gaussian(x,Hbg,Cbg,Wbg,offset=0)+offset)

    def errfunc(self,p,x0,y0):
        cost = self.fitFunction(x0,*p)-y0
        self.cost_values.append(sum(map(lambda x:np.abs(x),cost)))
        return cost

    def getGaussianFit(self,x,y,numberOfPeaks,includeBackground,guess,bounds,FTol,XTol,GTol,method,loss):
        if includeBackground == 0:
            if numberOfPeaks == 1:
                self.fitFunction = self.gaussian
            elif numberOfPeaks == 3:
                self.fitFunction = self.three_gaussians
            elif numberOfPeaks == 5:
                self.fitFunction = self.five_gaussians
            elif numberOfPeaks == 7:
                self.fitFunction = self.seven_gaussians
            elif numberOfPeaks == 9:
                self.fitFunction = self.nine_gaussians
            elif numberOfPeaks == 11:
                self.fitFunction = self.eleven_gaussians
        elif includeBackground == 2:
            if numberOfPeaks == 1:
                self.fitFunction = self.gaussian_bg
            elif numberOfPeaks == 3:
                self.fitFunction = self.three_gaussians_bg
            elif numberOfPeaks == 5:
                self.fitFunction = self.five_gaussians_bg
            elif numberOfPeaks == 7:
                self.fitFunction = self.seven_gaussians_bg
            elif numberOfPeaks == 9:
                self.fitFunction = self.nine_gaussians_bg
            elif numberOfPeaks == 11:
                self.fitFunction = self.eleven_gaussians_bg
        self.cost_values=[]
        optim = least_squares(fun=self.errfunc,x0=guess,\
                bounds=bounds,method=method,loss=loss, ftol=FTol,xtol=XTol,gtol=GTol,args=(x,y),verbose=0)
        return optim, self.cost_values

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

class ReciprocalSpaceMap(QtCore.QObject):

    progressAdvance = QtCore.pyqtSignal(int,int,int)
    progressEnd = QtCore.pyqtSignal()
    connectToCanvas = QtCore.pyqtSignal()
    updateLog = QtCore.pyqtSignal(str)
    updateChart = QtCore.pyqtSignal(np.ndarray,np.ndarray,str)
    fileSaved = QtCore.pyqtSignal(str)
    finished = QtCore.pyqtSignal()
    setTitle = QtCore.pyqtSignal(str)
    drawLineRequested = QtCore.pyqtSignal(QtCore.QPointF,QtCore.QPointF,bool)
    drawRectRequested = QtCore.pyqtSignal(QtCore.QPointF,QtCore.QPointF,float,bool)
    error = QtCore.pyqtSignal(str)
    attention = QtCore.pyqtSignal(str)
    aborted = QtCore.pyqtSignal()

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
                self.updateLog.emit("ERROR: Please choose the region!")
                self.error.emit("Please choose the region!")
                QtCore.QCoreApplication.processEvents()
            else:
                self.connectToCanvas.emit()
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
                self.setTitle.emit("Chi Scan at R = {:3.2f} \u212B\u207B\u00B9".format(radius))
                QtCore.QCoreApplication.processEvents()
                for nimg in range(self.startIndex,self.endIndex+1):
                    qImg, img = self.image_worker.getImage(16,image_list[nimg-self.startIndex],autoWB,brightness,blackLevel,image_crop)
                    RC,I = self.image_worker.getChiScan(start,radius*scale_factor,width,chiRange,tiltAngle,img,chiStep)
                    Phi1 = np.full(len(RC),nimg*1.8)
                    Phi2 = np.full(len(RC),nimg*1.8)
                    for iphi in range(0,int(len(RC)/2)):
                        Phi1[iphi]=nimg*1.8+180
                    map_2D1 = np.vstack((map_2D1,np.vstack((abs(RC),Phi1,I)).T))
                    map_2D2 = np.vstack((map_2D2,np.vstack((RC,Phi2,I)).T))
                    if self.IsCentered:
                        self.updateChart.emit(RC,I,"arc")
                    else:
                        self.updateChart.emit(abs(RC),I,"arc")
                    self.progressAdvance.emit(0,100,(nimg+1-self.startIndex)*100/(self.endIndex-self.startIndex+1))
                    self.updateLog.emit("The file being processed right now is: "+image_list[nimg-self.startIndex])
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
                    self.progressEnd.emit()
                    self.updateLog.emit("Completed!")
                    self.attention.emit("Pole Figure Completed!")
                    if self.IsSaveResult:
                        self.fileSaved.emit(self.graphTextPath)
                    QtCore.QCoreApplication.processEvents()
        elif mode == "arc":
            self.error.emit("The type of mapping is not consistent with the chosen region!")
            QtCore.QCoreApplication.processEvents()
        elif self.IsPoleFigure:
            self.error.emit("The type of mapping is not consistent with the chosen region!")
            QtCore.QCoreApplication.processEvents()
        else:
            if self.status["startX"] == "" or self.status["startY"] == "" or self.status["endX"] == "" or \
                    self.status["endY"] == ""\
                or self.status["width"] =="":
                self.updateLog.emit("ERROR: Please choose the region!")
                self.error.emit("Please choose the region!")
                QtCore.QCoreApplication.processEvents()
            elif self.status["choosedX"] == "" or self.status["choosedY"] == "":
                self.updateLog.emit("ERROR: Please choose the origin!")
                self.error.emit("Please choose the origin!")
                QtCore.QCoreApplication.processEvents()
            else:
                self.connectToCanvas.emit()
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
                    self.setTitle.emit("Line Profile at Kperp = {:4.2f} (\u212B\u207B\u00B9)".format(Kperp))
                    QtCore.QCoreApplication.processEvents()
                    for nimg in range(self.startIndex,self.endIndex+1):
                        qImg, img = self.image_worker.getImage(16,image_list[nimg-self.startIndex],autoWB,brightness,blackLevel,image_crop)
                        if width==0.0:
                            RC,I = self.image_worker.getLineScan(start,end,img,scale_factor)
                            Phi1 = np.full(len(RC),nimg*1.8)
                            Phi2 = np.full(len(RC),nimg*1.8)
                            maxPos = np.argmax(I)
                            for iphi in range(0,maxPos):
                                Phi1[iphi]=nimg*1.8+180
                            if maxPos<(len(RC)-1)/2:
                                x1,y1 = abs(RC[0:(2*maxPos+1)]-RC[maxPos]), I[0:(2*maxPos+1)]/I[maxPos]
                                map_2D1 = np.vstack((map_2D1,np.vstack((x1,Phi1[0:(2*maxPos+1)],y1)).T))
                                x2,y2 = RC[0:(2*maxPos+1)]-RC[maxPos], I[0:(2*maxPos+1)]/I[maxPos]
                                map_2D2 = np.vstack((map_2D2,np.vstack((x2,Phi2[0:(2*maxPos+1)],y2)).T))
                            else:
                                x1,y1 = abs(RC[(2*maxPos-len(RC)-1):-1]-RC[maxPos]), I[(2*maxPos-len(RC)-1):-1]/I[maxPos]
                                map_2D1 = np.vstack((map_2D1,np.vstack((x1,Phi1[(2*maxPos-len(RC)-1):-1],y1)).T))
                                x2,y2 = RC[(2*maxPos-len(RC)-1):-1]-RC[maxPos], I[(2*maxPos-len(RC)-1):-1]/I[maxPos]
                                map_2D2 = np.vstack((map_2D2,np.vstack((x2,Phi2[(2*maxPos-len(RC)-1):-1],y2)).T))
                        else:
                            RC,I = self.image_worker.getIntegral(start,end,width,img,scale_factor)
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
                            self.updateChart.emit(x2,y2,"line")
                        else:
                            self.updateChart.emit(x1,y1,"line")
                        self.progressAdvance.emit(0,100,(nimg+1-self.startIndex)*100/(self.endIndex-self.startIndex+1))
                        self.updateLog.emit("The file being processed right now is: "+image_list[nimg-self.startIndex])
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
                        self.progressEnd.emit()
                        self.updateLog.emit("Completed!")
                        self.attention.emit("2D Mapping Completed!")
                        if self.IsSaveResult:
                            self.fileSaved.emit(self.graphTextPath)
                        QtCore.QCoreApplication.processEvents()
                else:
                    map_3D1=np.array([0,0,0,0])
                    map_3D2=np.array([0,0,0,0])
                    for nimg in range(self.startIndex,self.endIndex+1):
                        qImg, img = self.image_worker.getImage(16,image_list[nimg-self.startIndex],autoWB,brightness,blackLevel,image_crop)
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
                            self.setTitle.emit("Line Profile at Kperp = {:4.2f} (\u212B\u207B\u00B9)".format(Kperp))
                            QtCore.QCoreApplication.processEvents()
                            if width==0.0:
                                RC,I = self.image_worker.getLineScan(newStart,newEnd,img,scale_factor)
                                rem = np.remainder(len(RC),self.group)
                                if not rem == 0:
                                    RC = np.pad(RC,(0,self.group-rem),'edge')
                                    I = np.pad(I,(0,self.group-rem),'edge')
                                RC,I = RC.reshape(-1,self.group).mean(axis=1), I.reshape(-1,self.group).mean(axis=1)
                                self.drawLineRequested.emit(newStart,newEnd,False)
                                QtCore.QCoreApplication.processEvents()
                                Phi1 = np.full(len(RC),nimg*1.8)
                                Phi2 = np.full(len(RC),nimg*1.8)
                                maxPos = np.argmax(I)
                                for iphi in range(0,maxPos):
                                    Phi1[iphi]=nimg*1.8+180
                                if maxPos<(len(RC)-1)/2:
                                    x1,y1 = abs(RC[0:(2*maxPos+1)]-RC[maxPos]), I[0:(2*maxPos+1)]/I[maxPos]
                                    K = np.full(len(x1),Kperp)
                                    map_3D1 = np.vstack((map_3D1,np.vstack((x1,Phi1[0:(2*maxPos+1)],K,y1)).T))
                                    x2,y2 = RC[0:(2*maxPos+1)]-RC[maxPos], I[0:(2*maxPos+1)]/I[maxPos]
                                    map_3D2 = np.vstack((map_3D2,np.vstack((x2,Phi2[0:(2*maxPos+1)],K,y2)).T))
                                else:
                                    x1,y1 = abs(RC[(2*maxPos-len(RC)-1):-1]-RC[maxPos]), I[(2*maxPos-len(RC)-1):-1]/I[maxPos]
                                    K = np.full(len(x1),Kperp)
                                    map_3D1 = np.vstack((map_3D1,np.vstack((x1,Phi1[(2*maxPos-len(RC)-1):-1],K,y1)).T))
                                    x2,y2 = RC[(2*maxPos-len(RC)-1):-1]-RC[maxPos], I[(2*maxPos-len(RC)-1):-1]/I[maxPos]
                                    map_3D2 = np.vstack((map_3D2,np.vstack((x2,Phi2[(2*maxPos-len(RC)-1):-1],K,y2)).T))
                            else:
                                RC,I = self.image_worker.getIntegral(newStart,newEnd,width,img,scale_factor)
                                rem = np.remainder(len(RC),self.group)
                                if not rem == 0:
                                    RC = np.pad(RC,(0,self.group-rem),'edge')
                                    I = np.pad(I,(0,self.group-rem),'edge')
                                RC,I = RC.reshape(-1,self.group).mean(axis=1), I.reshape(-1,self.group).mean(axis=1)
                                self.drawRectRequested.emit(newStart,newEnd,width,False)
                                QtCore.QCoreApplication.processEvents()
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
                                self.updateChart.emit(x2,y2,"line")
                            else:
                                self.updateChart.emit(x1,y1,"line")
                            self.progressAdvance.emit(0,100,(i+nos*(nimg-self.startIndex))*100/((self.endIndex-self.startIndex+1)*nos))
                            self.updateLog.emit("The file being processed right now is: "+image_list[nimg-self.startIndex])
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
                        self.progressEnd.emit()
                        self.updateLog.emit("Completed!")
                        self.attention.emit("3D Mapping Completed!")
                        QtCore.QCoreApplication.processEvents()
        if not self._abort:
            self.finished.emit()
        else:
            self.aborted.emit()
            self._abort = False

    def stop(self):
        self._abort = True


class DiffractionPattern(QtCore.QObject):
    progressAdvance = QtCore.pyqtSignal(int,int,int)
    progressEnd = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(str)
    accomplished = QtCore.pyqtSignal(np.ndarray)
    aborted = QtCore.pyqtSignal()
    finished = QtCore.pyqtSignal()

    def __init__(self,Kx,Ky,Kz,AFF,atoms):
        super(DiffractionPattern,self).__init__()
        self.Psi = np.multiply(Kx,0).astype('complex128')
        self.species_dict = set(AFF.index.tolist())
        self.atoms_list = atoms
        self.Kx = Kx
        self.Ky = Ky
        self.Kz = Kz
        self.AFF = AFF
        self._abort = False

    def run(self):
        itr = 0
        number_of_atoms = len(self.atoms_list)
        for key,specie in self.atoms_list.items():
            coord = list(float(x) for x in list(key.split(',')))
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
                self.error.emit("No scattering coefficient for %s"%specie)
                break
            QtCore.QCoreApplication.processEvents()
            if self._abort:
                break
            else:
                af = af_row.at['c']+af_row.at['a1']*np.exp(-af_row.at['b1']*(np.multiply(self.Kx,self.Kx)+np.multiply(self.Ky,self.Ky)+np.multiply(self.Kz,self.Kz))/4/np.pi)\
                                   +af_row.at['a2']*np.exp(-af_row.at['b2']*(np.multiply(self.Kx,self.Kx)+np.multiply(self.Ky,self.Ky)+np.multiply(self.Kz,self.Kz))/4/np.pi)\
                                   +af_row.at['a3']*np.exp(-af_row.at['b3']*(np.multiply(self.Kx,self.Kx)+np.multiply(self.Ky,self.Ky)+np.multiply(self.Kz,self.Kz))/4/np.pi)\
                                   +af_row.at['a4']*np.exp(-af_row.at['b4']*(np.multiply(self.Kx,self.Kx)+np.multiply(self.Ky,self.Ky)+np.multiply(self.Kz,self.Kz))/4/np.pi)
                self.Psi += np.multiply(af,np.exp(1j*(self.Kx*coord[0]+self.Ky*coord[1]+self.Kz*coord[2])))
                itr+=1
                self.progressAdvance.emit(0,100,itr/number_of_atoms*100)
                QtCore.QCoreApplication.processEvents()
        if not self._abort:
            self.intensity = np.multiply(self.Psi.astype('complex64'),np.conj(self.Psi.astype('complex64')))
            self.progressEnd.emit()
            self.accomplished.emit(self.intensity)
        else:
            self.aborted.emit()
            self._abort = False

    def stop(self):
        self._abort = True

class FitBroadening(QtCore.QObject):

    drawLineRequested = QtCore.pyqtSignal(QtCore.QPointF,QtCore.QPointF,bool)
    drawRectRequested = QtCore.pyqtSignal(QtCore.QPointF,QtCore.QPointF,float,bool)
    progressAdvance = QtCore.pyqtSignal(int,int,int)
    progressEnd = QtCore.pyqtSignal()
    updateResults = QtCore.pyqtSignal(list)
    updateLog = QtCore.pyqtSignal(str)
    writeOutput = QtCore.pyqtSignal(str)
    closeOutput = QtCore.pyqtSignal()
    attention = QtCore.pyqtSignal(str)
    finished = QtCore.pyqtSignal()
    addCostFunction = QtCore.pyqtSignal(np.ndarray,list,str)
    addPlot = QtCore.pyqtSignal(np.ndarray,np.ndarray)

    def __init__(self,path,initialparameters,startIndex,endIndex,origin,start,end,width,analysisRange,scale_factor,autoWB,brightness,blackLevel,image_crop,\
                 numberOfPeaks,BGCheck,saveResult,guess,bounds,ftol,xtol,gtol,method,loss):
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
        self.saveResult = saveResult
        self.guess=guess
        self.bound_low,self.bound_high = bounds[0],bounds[1]
        self.ftol = ftol
        self.xtol = xtol
        self.gtol = gtol
        self.method = method
        self.loss = loss
        self.image_list = []
        self.image_worker = Image()
        self.fit_worker = Fit()
        self._abort = False

    def run(self):
        for filename in glob.glob(self.path):
            self.image_list.append(filename)
        for nimg in range(self.startIndex,self.endIndex+1):
            self.updateResults.emit(self.initialparameters)
            self.updateLog.emit("The file being processed right now is: "+self.image_list[nimg])
            qImg, img = self.image_worker.getImage(16,self.image_list[nimg],self.autoWB,self.brightness,self.blackLevel,self.image_crop)
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
                    self.drawLineRequested.emit(newStart,newEnd,False)
                    RC,I = self.image_worker.getLineScan(newStart,newEnd,img,self.scale_factor)
                else:
                    self.drawRectRequested.emit(newStart,newEnd,self.width,False)
                    RC,I = self.image_worker.getIntegral(newStart,newEnd,self.width,img,self.scale_factor)
                results, cost = self.fit_worker.getGaussianFit(RC,I,self.numberOfPeaks,self.BGCheck,self.guess,(self.bound_low,self.bound_high),self.ftol,\
                                                                self.xtol,self.gtol,self.method,self.loss)
                Kperp = (np.abs((newEnd.y()-newStart.y())*self.origin.x()-(newEnd.x()-newStart.x())*self.origin.y()+newEnd.x()*newStart.y()-newEnd.y()*newStart.x())/\
                        np.sqrt((newEnd.y()-newStart.y())**2+(newEnd.x()-newStart.x())**2))/self.scale_factor
                iteration = np.linspace(1,len(cost)+1,len(cost))
                jac = results.jac
                cov = np.linalg.pinv(jac.T.dot(jac))
                residual_variance = np.sum(results.fun**2)/(len(I)-len(self.guess))
                var = np.sqrt(np.diagonal(cov*residual_variance))
                value_variance = np.reshape(np.concatenate((np.array(results.x),np.array(var)),axis=0),(2,len(var)))
                self.addCostFunction.emit(iteration,cost,'cost_function')
                self.updateResults.emit(list(results.x))
                if i == 1:
                    self.initialparameters = list(results.x)
                fitresults =str(nimg*1.8).ljust(12)+'\t'+str(np.round(Kperp,3)).ljust(12)+'\t'+'\t'.join(str(np.round(e[0],3)).ljust(12)+'\t'+str(np.round(e[1],3)).ljust(12) for e in value_variance.T)+'\n'
                if self.saveResult == 2:
                    self.writeOutput.emit(fitresults)
                self.updateLog.emit("MESSAGE:"+results.message)
                self.addPlot.emit(RC,I)
                self.progressAdvance.emit(0,100,((nimg-self.startIndex)*nos+i)*100/nos/(self.endIndex-self.startIndex+1))
                QtCore.QCoreApplication.processEvents()
                if self._abort:
                    break
            if self._abort:
                break
        if self.saveResult == 2:
            self.closeOutput.emit()
        if not self._abort:
            self.progressEnd.emit()
            self.updateLog.emit("Completed!")
            self.attention.emit("Broadening Analysis Completed!")
        else:
            self.updateLog.emit("Aborted!")
            self.attention.emit("Broadening Analysis Aborted!")
            self._abort = False
        self.finished.emit()

    def stop(self):
        self._abort = True
