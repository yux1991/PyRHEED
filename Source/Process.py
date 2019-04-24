import numpy as np
from PyQt5 import QtGui
from scipy.optimize import least_squares
import rawpy
import math
import os
import itertools
from lxml import etree as ET

class Image(object):

    def __init__(self):
        super(Image,self).__init__()

    def getImage(self,bit_depth,img_path,EnableAutoWB, Brightness, UserBlack, image_crop):
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

    def mtx2vtp(self,dir,name,matrix,KRange,N_para,N_perp):
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
            #print("({},{},{}): {} {} {} {}".format(i,j,k,data[i+j+k,0],data[i+j+k,1],data[i+j+k,2],data[i+j+k,3]))
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
        np.savetxt(dir+'/'+name+".txt",data,delimiter='\t')
