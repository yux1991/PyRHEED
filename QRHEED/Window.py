from PyQt5 import QtCore, QtGui, QtWidgets
from Canvas import *
from Browser import *
from Properties import *
from Profile import *
from Cursor import *
import rawpy
import numpy as np

class Window(QtWidgets.QMainWindow):
    def __init__(self):

        super(Window, self).__init__()
        self.HS,self.VS = 0,0
        self.image_crop = [1200+self.VS,2650+self.VS,500+self.HS,3100+self.HS]
        self.img_path = 'C:/RHEED/01192017 multilayer graphene on Ni/20 keV/Img0000.nef'
        self.mainFrame = QtWidgets.QWidget(self)
        self.mainGrid = QtWidgets.QGridLayout(self.mainFrame)
        self.mainSplitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.canvas = Canvas(self)
        self.canvas.photoMouseMovement.connect(self.photoMouseMovement)

        self.controlPanelFrame = QtWidgets.QWidget(self)
        self.controlPanelGrid = QtWidgets.QGridLayout(self.controlPanelFrame)
        self.controlPanelSplitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.browser = Browser(self)
        self.controlPanelBottomWidget = QtWidgets.QWidget()
        self.controlPanelBottomGrid = QtWidgets.QGridLayout(self.controlPanelBottomWidget)
        self.properties = Properties(self)
        self.profile = Profile(self)
        self.cursorInfo = Cursor(self)
        self.controlPanelBottomGrid.addWidget(self.properties,0,0)
        self.controlPanelBottomGrid.addWidget(self.cursorInfo,1,0)
        self.controlPanelBottomGrid.addWidget(self.profile,2,0)
        self.controlPanelSplitter.addWidget(self.browser)
        self.controlPanelSplitter.addWidget(self.controlPanelBottomWidget)

        self.controlPanelSplitter.setSizes([100,400])
        self.controlPanelSplitter.setStretchFactor(0,1)
        self.controlPanelSplitter.setStretchFactor(1,1)
        self.controlPanelSplitter.setCollapsible(0,False)
        self.controlPanelSplitter.setCollapsible(1,False)
        self.controlPanelGrid.addWidget(self.controlPanelSplitter,0,0)

        self.mainSplitter.addWidget(self.canvas)
        self.mainSplitter.addWidget(self.controlPanelFrame)
        self.mainSplitter.setSizes([800,200])
        self.mainSplitter.setStretchFactor(0,1)
        self.mainSplitter.setStretchFactor(1,1)
        self.mainSplitter.setCollapsible(0,False)
        self.mainSplitter.setCollapsible(1,False)
        self.mainGrid.addWidget(self.mainSplitter,0,0)

        #Tool bar
        self.toolBar = QtWidgets.QToolBar(self)
        self.toolBar.setFloatable(False)
        self.toolBar.setMovable(False)
        self.open = QtWidgets.QAction(QtGui.QIcon("./icons/open.gif"), "open", self)
        self.open.triggered.connect(self.openImage)
        self.pixInfo = QtWidgets.QAction("pixel info",self)
        self.pixInfo.triggered.connect(self.showPixInfo)
        self.toolBar.addAction(self.open)
        self.toolBar.addAction(self.pixInfo)
        self.addToolBar(self.toolBar)

        #Status bar
        self.statusBar = QtWidgets.QStatusBar(self)
        self.editPixInfo = QtWidgets.QLabel(self)
        self.editPixInfo.setAlignment(QtCore.Qt.AlignRight)
        self.statusBar.addPermanentWidget(self.editPixInfo)
        self.setStatusBar(self.statusBar)

        self.setCentralWidget(self.mainFrame)
        self.setWindowTitle("QtRHEED")

    def openImage(self):
        qImg = self.read_qImage(16,self.img_path, False, 20, 100)
        qPixImg = QtGui.QPixmap(qImg.size())
        QtGui.QPixmap.convertFromImage(qPixImg,qImg,QtCore.Qt.MonoOnly)
        self.canvas.setPhoto(QtGui.QPixmap(qPixImg))

    def showPixInfo(self):
        self.canvas.toggleDragMode()

    def photoMouseMovement(self, pos):
        self.editPixInfo.setText('x = %d, y = %d' % (pos.x(), pos.y()))

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
