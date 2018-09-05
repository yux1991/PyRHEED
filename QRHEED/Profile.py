from PyQt5 import QtCore, QtWidgets,QtGui

class Profile(QtWidgets.QGraphicsView):

    def __init__(self,parent):
        super(Profile,self).__init__(parent)
        self.initUI()

    def initUI(self):
        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor('darkGray')))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        profileImg = QtGui.QImage()
        profilePixmap = QtGui.QPixmap()
        QtGui.QPixmap.convertFromImage(profilePixmap,profileImg,QtCore.Qt.AutoColor)
        self._photo.setPixmap(profilePixmap)



