from PyQt5 import QtCore, QtGui, QtWidgets
from Canvas import *
import rawpy
import numpy as np

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.viewer = Canvas(self)
        self.HS,self.VS = 0,0
        self.image_crop = [1200+self.VS,2650+self.VS,500+self.HS,3100+self.HS]
        self.img_path = 'C:/RHEED/01192017 multilayer graphene on Ni/20 keV/Img0000.nef'
        # 'Load image' button
        self.btnLoad = QtWidgets.QToolButton(self)
        self.btnLoad.setText('Load image')
        self.btnLoad.clicked.connect(self.loadImage)
        # Button to change from drag/pan to getting pixel info
        self.btnPixInfo = QtWidgets.QToolButton(self)
        self.btnPixInfo.setText('Enter pixel info mode')
        self.btnPixInfo.clicked.connect(self.pixInfo)
        self.editPixInfo = QtWidgets.QLineEdit(self)
        self.editPixInfo.setReadOnly(True)
        self.viewer.photoMouseMovement.connect(self.photoMouseMovement)
        self.grid = QtWidgets.QGridLayout(self)
        self.setLayout(self.grid)
        mode = [(self.btnLoad,0,0,1,1),(self.btnPixInfo,0,1,1,1),(self.viewer,1,0,1,-1),(self.editPixInfo,2,0,1,3)]
        for widget,row,column,rspan,cspan in mode:
            self.grid.addWidget(widget,row,column,rspan,cspan)
    def loadImage(self):
        qImg = self.read_qImage(16,self.img_path, False, 20, 100)
        qPixImg = QtGui.QPixmap(qImg.size())
        QtGui.QPixmap.convertFromImage(qPixImg,qImg,QtCore.Qt.MonoOnly)
        self.viewer.setPhoto(QtGui.QPixmap(qPixImg))

    def pixInfo(self):
        self.viewer.toggleDragMode()

    def photoMouseMovement(self, pos):
        self.editPixInfo.setText('%d, %d' % (pos.x(), pos.y()))

    def read_qImage(self,bit_depth,img_path,EnableAutoWB = False, Brightness = 20, UserBlack = 100):
        img_raw = rawpy.imread(img_path)
        img_rgb = img_raw.postprocess(demosaic_algorithm=rawpy.DemosaicAlgorithm.AHD, output_bps = bit_depth, use_auto_wb = EnableAutoWB,bright=Brightness/100,user_black=UserBlack)
        img_bw = (0.21*img_rgb[:,:,0])+(0.72*img_rgb[:,:,1])+(0.07*img_rgb[:,:,2])
        img_array = img_bw[self.image_crop[0]:self.image_crop[1],self.image_crop[2]:self.image_crop[3]]
        if bit_depth == 16:
            img_array = np.uint8(img_array/256)
        if bit_depth == 8:
            img_array = np.uint8(img_array)
        qImg = QtGui.QImage(img_array,img_array.shape[1],img_array.shape[0],img_array.shape[1], QtGui.QImage.Format_Grayscale8)
        return qImg
