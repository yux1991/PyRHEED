from PyQt5 import QtWidgets

class Cursor(QtWidgets.QWidget):

    def __init__(self,parent):
        super(Cursor,self).__init__(parent)
        self.initUI()


    def initUI(self):
        #the Cursor Information group box
        self.cursorInfoBox = QtWidgets.QGroupBox('Cursor Information')
        self.cursorInfoBoxGrid = QtWidgets.QGridLayout()
        self.choosedXYLabel = QtWidgets.QLabel('Chosen (X,Y)')
        self.choosedXYEdit = QtWidgets.QLineEdit()
        self.intensityLabel = QtWidgets.QLabel('Intensity')
        self.intensityEdit = QtWidgets.QLineEdit()
        self.intensityEdit.setReadOnly(True)
        self.startXYLabel = QtWidgets.QLabel('Start (X,Y)')
        self.startXYEdit = QtWidgets.QLineEdit()
        self.endXYLabel = QtWidgets.QLabel('End (X,Y)')
        self.endXYEdit = QtWidgets.QLineEdit()
        self.widthLabel = QtWidgets.QLabel('Width')
        self.widthEdit = QtWidgets.QLineEdit()

        self.setAsCenterButton = QtWidgets.QPushButton('Set As Center')
        self.chooseButton = QtWidgets.QPushButton('Choose Region')
        self.setAsCenterButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
        self.chooseButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
        self.buttonGrid = QtWidgets.QGridLayout()
        self.buttonGrid.addWidget(self.setAsCenterButton,0,0)
        self.buttonGrid.addWidget(self.chooseButton,0,1)

        self.cursorInfoBoxGrid.addWidget(self.choosedXYLabel,0,0)
        self.cursorInfoBoxGrid.addWidget(self.choosedXYEdit,0,1)
        self.cursorInfoBoxGrid.addWidget(self.intensityLabel,1,0)
        self.cursorInfoBoxGrid.addWidget(self.intensityEdit,1,1)
        self.cursorInfoBoxGrid.addWidget(self.startXYLabel,2,0)
        self.cursorInfoBoxGrid.addWidget(self.startXYEdit,2,1)
        self.cursorInfoBoxGrid.addWidget(self.endXYLabel,3,0)
        self.cursorInfoBoxGrid.addWidget(self.endXYEdit,3,1)
        self.cursorInfoBoxGrid.addWidget(self.widthLabel,4,0)
        self.cursorInfoBoxGrid.addWidget(self.widthEdit,4,1)
        self.cursorInfoBoxGrid.addLayout(self.buttonGrid,5,0,1,2)
        self.cursorInfoBox.setLayout(self.cursorInfoBoxGrid)

        self.UIgrid = QtWidgets.QGridLayout()
        self.UIgrid.addWidget(self.cursorInfoBox,0,0)
        self.UIgrid.setContentsMargins(0,0,0,0)
        self.setLayout(self.UIgrid)
        self.show()



