from PyQt5 import QtWidgets

class Cursor(QtWidgets.QWidget):

    def __init__(self,parent):
        super(Cursor,self).__init__(parent)
        self.initUI()


    def initUI(self):
        #the Cursor Information group box
        cursorInfoBox = QtWidgets.QGroupBox('Cursor Information')
        cursorInfoBoxGrid = QtWidgets.QGridLayout()
        choosedXYLabel = QtWidgets.QLabel('Choosed (X,Y)')
        choosedXYEdit = QtWidgets.QLineEdit('{},{}'.format(0,0))
        intensityLabel = QtWidgets.QLabel('Intensity')
        intensityEdit = QtWidgets.QLineEdit('{}'.format(0))
        startXYLabel = QtWidgets.QLabel('Start (X,Y)')
        startXYEdit = QtWidgets.QLineEdit('{},{}'.format(0,0))
        endXYLabel = QtWidgets.QLabel('End (X,Y)')
        endXYEdit = QtWidgets.QLineEdit('{},{}'.format(0,0))
        widthLabel = QtWidgets.QLabel('Width')
        widthEdit = QtWidgets.QLineEdit('{}'.format(1))

        setAsCenterButton = QtWidgets.QPushButton('Set As Center')
        chooseButton = QtWidgets.QPushButton('Choose Region')
        setAsCenterButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
        chooseButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
        buttonGrid = QtWidgets.QGridLayout()
        buttonGrid.addWidget(setAsCenterButton,0,0)
        buttonGrid.addWidget(chooseButton,0,1)

        cursorInfoBoxGrid.addWidget(choosedXYLabel,0,0)
        cursorInfoBoxGrid.addWidget(choosedXYEdit,0,1)
        cursorInfoBoxGrid.addWidget(intensityLabel,1,0)
        cursorInfoBoxGrid.addWidget(intensityEdit,1,1)
        cursorInfoBoxGrid.addWidget(startXYLabel,2,0)
        cursorInfoBoxGrid.addWidget(startXYEdit,2,1)
        cursorInfoBoxGrid.addWidget(endXYLabel,3,0)
        cursorInfoBoxGrid.addWidget(endXYEdit,3,1)
        cursorInfoBoxGrid.addWidget(widthLabel,4,0)
        cursorInfoBoxGrid.addWidget(widthEdit,4,1)
        cursorInfoBoxGrid.addLayout(buttonGrid,5,0,1,2)
        cursorInfoBox.setLayout(cursorInfoBoxGrid)

        UIgrid = QtWidgets.QGridLayout()
        UIgrid.addWidget(cursorInfoBox,0,0)
        UIgrid.setContentsMargins(0,0,0,0)
        self.setLayout(UIgrid)
        self.show()



