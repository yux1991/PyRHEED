from Window import *

class Canvas(QtWidgets.QGraphicsView):
    photoMouseMovement = QtCore.pyqtSignal(QtCore.QPoint)

    def __init__(self, parent):
        super(Canvas, self).__init__(parent)
        self._zoom = 0
        self._empty = True
        self.max_zoom_factor = 21
        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor('darkGray')))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)

    def hasPhoto(self):
        return not self._empty

    def fitInView(self, scale=True):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.hasPhoto():
                unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)

    def fitCanvas(self):
        if self.hasPhoto():
            self.setUpdatesEnabled(False)
            self.fitInView()
            QtCore.QCoreApplication.processEvents()
            self.fitInView()
            self.setUpdatesEnabled(True)
            self._zoom = 0

    def setPhoto(self, pixmap=None):
        self._zoom = 0
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._photo.setPixmap(QtGui.QPixmap())
        self.fitInView()

    def wheelEvent(self, event):
        if self.hasPhoto():
            self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > -self.max_zoom_factor and self._zoom < self.max_zoom_factor:
                self.scale(factor, factor)
            elif self._zoom <=-self.max_zoom_factor:
                self._zoom = -self.max_zoom_factor
            else:
                self._zoom = self.max_zoom_factor

    def zoomIn(self):
        if self.hasPhoto():
            self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorViewCenter)
            factor = 1.25
            self._zoom += 1
            if self._zoom > -self.max_zoom_factor and self._zoom < self.max_zoom_factor:
                self.scale(factor, factor)
            elif self._zoom <=-self.max_zoom_factor:
                self._zoom = -self.max_zoom_factor
            else:
                self._zoom = self.max_zoom_factor

    def zoomOut(self):
        if self.hasPhoto():
            self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorViewCenter)
            factor = 0.8
            self._zoom -= 1
            if self._zoom > -self.max_zoom_factor and self._zoom < self.max_zoom_factor:
                self.scale(factor, factor)
            elif self._zoom <=-self.max_zoom_factor:
                self._zoom = -self.max_zoom_factor
            else:
                self._zoom = self.max_zoom_factor

    def toggleMode(self,cursormode):
        if not self._photo.pixmap().isNull():
            if cursormode == "line":
                self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
                self.setCursor(QtCore.Qt.CrossCursor)
            if cursormode == "rectangle":
                self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
                self.setCursor(QtCore.Qt.CrossCursor)
            if cursormode == "arc":
                self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
                self.setCursor(QtCore.Qt.CrossCursor)
            if cursormode == "pan":
                self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

    def mouseMoveEvent(self, event):
        if self._photo.isUnderMouse():
            position = self.mapToScene(event.pos())
            self.photoMouseMovement.emit(position.toPoint())
        super(Canvas, self).mouseMoveEvent(event)
