from Window import *
import numpy as np

class Canvas(QtWidgets.QGraphicsView):

    #public signals
    photoMouseMovement = QtCore.pyqtSignal(QtCore.QPoint)
    photoMousePress = QtCore.pyqtSignal(QtCore.QPoint)
    photoMouseRelease = QtCore.pyqtSignal(QtCore.QPoint)

    def __init__(self, parent):
        super(Canvas, self).__init__(parent)
        self._mode = "pan"
        self._drawingLine = False
        self._drawingRect = False
        self._drawingArc = False
        self._zoom = 0
        self._empty = True
        self._width = 20
        self._span = 60
        self._tilt = 0
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
        self.clearCanvas()
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
                end = QtCore.QPointF(self.mapToScene(event.pos()))
                if self._photo.isUnderMouse():
                    if self._drawingLine:
                        self.drawLine(self._start,end)
                    elif self._drawingRect:
                        self.drawRect(self._start,end,self._width)
                    elif self._drawingArc:
                        self.drawArc(self._start,end,self._width,self._span,self._tilt)
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
                self._mode = "line"
            if cursormode == "rectangle":
                self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
                self.setCursor(QtCore.Qt.CrossCursor)
                self._mode = "rectangle"
            if cursormode == "arc":
                self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
                self.setCursor(QtCore.Qt.CrossCursor)
                self._mode = "arc"
            if cursormode == "pan":
                self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
                self._mode = "pan"

    def mousePressEvent(self, event):
        if self._photo.isUnderMouse():
            if event.button() == QtCore.Qt.LeftButton:
                self._start = QtCore.QPointF(self.mapToScene(event.pos()))
                if self._mode == "line":
                    self._drawingLine = True
                if self._mode == "rectangle":
                    self._drawingRect = True
                if self._mode == "arc":
                    self._drawingArc = True
                position = self.mapToScene(event.pos())
                self.photoMousePress.emit(position.toPoint())
            else:
                try:
                    self.clearCanvas()
                except:
                    pass
        super(Canvas, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._photo.isUnderMouse():
            end = QtCore.QPointF(self.mapToScene(event.pos()))
            if self._drawingLine:
                self.drawLine(self._start,end)
            elif self._drawingRect:
                self.drawRect(self._start,end,self._width)
            elif self._drawingArc:
                self.drawArc(self._start,end,self._width,self._span,self._tilt)
            position = self.mapToScene(event.pos())
            self.photoMouseMovement.emit(position.toPoint())
        super(Canvas, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._photo.isUnderMouse():
            end = QtCore.QPointF(self.mapToScene(event.pos()))
            if self._drawingLine:
                self.drawLine(self._start,end)
                self._drawingLine = False
            elif self._drawingRect:
                self.drawRect(self._start,end,self._width)
                self._drawingRect = False
            elif self._drawingArc:
                self.drawArc(self._start,end,self._width, self._span,self._tilt)
                self._drawingArc = False
            position = self.mapToScene(event.pos())
            self.photoMouseRelease.emit(position.toPoint())
        else:
            self._drawingLine = False
            self._drawingRect = False
            self._drawingArc = False
        super(Canvas, self).mouseReleaseEvent(event)

    def clearCanvas(self):
        try:
            self._scene.removeItem(self._lineItem)
        except:
            pass
        try:
            self._scene.removeItem(self._rectItem)
        except:
            pass
        try:
            self._scene.removeItem(self._arcItem1)
            self._scene.removeItem(self._arcItem2)
            self._scene.removeItem(self._arcItem3)
        except:
            pass

    def drawLine(self,start,end):
        self.clearCanvas()
        self._lineItem = self._scene.addLine(QtCore.QLineF(start,end),QtGui.QPen(QtCore.Qt.yellow,2))

    def drawRect(self,start,end,width):
        self.clearCanvas()
        rect = QtGui.QPolygonF()
        p1,p2,p3,p4 = self.getRectanglePosition(start,end,width)
        rect.append(p1)
        rect.append(p2)
        rect.append(p3)
        rect.append(p4)
        self._rectItem = self._scene.addPolygon(rect,QtGui.QPen(QtCore.Qt.yellow,2))

    def drawArc(self,start,end,width,span,tilt):
        self.clearCanvas()
        PFRadius = np.sqrt((start.x()-end.x())**2+(start.y()-end.y())**2)
        arc1x0,arc1y0,arc1x1,arc1y1 = start.x()-(PFRadius+width),start.y()-(PFRadius+width),\
                                      start.x()+(PFRadius+width),start.y()+(PFRadius+width)
        arc2x0,arc2y0,arc2x1,arc2y1 = start.x()-(PFRadius-width),start.y()-(PFRadius-width),\
                                      start.x()+(PFRadius-width),start.y()+(PFRadius-width)
        arc3x0,arc3y0,arc3x1,arc3y1 = start.x()-(PFRadius),start.y()-PFRadius,start.x()+(PFRadius),\
                                      start.y()+(PFRadius)
        rect1 = QtCore.QRectF(arc1x0,arc1y0,arc1x1-arc1x0,arc1y1-arc1y0)
        rect2 = QtCore.QRectF(arc2x0,arc2y0,arc2x1-arc2x0,arc2y1-arc2y0)
        rect3 = QtCore.QRectF(arc3x0,arc3y0,arc3x1-arc3x0,arc3y1-arc3y0)
        self._arcItem3=self._scene.addEllipse(rect3,QtGui.QPen(QtCore.Qt.red,1))
        self._arcItem3.setStartAngle((270-span/2+tilt)*16)
        self._arcItem3.setSpanAngle((span)*16)
        self._arcItem1=self._scene.addEllipse(rect1,QtGui.QPen(QtCore.Qt.yellow,2))
        self._arcItem1.setStartAngle((270-span/2+tilt)*16)
        self._arcItem1.setSpanAngle(span*16)
        self._arcItem2=self._scene.addEllipse(rect2,QtGui.QPen(QtCore.Qt.yellow,2))
        self._arcItem2.setStartAngle((270-span/2+tilt)*16)
        self._arcItem2.setSpanAngle(span*16)

    def getRectanglePosition(self,start,end,width):
        if end.y() == start.y():
            x0 = start.x()
            y0 = start.y()-width
            x1 = start.x()
            y1 = start.y()+width
            x2 = end.x()
            y2 = end.y()+width
            x3 = end.x()
            y3 = end.y()-width
        elif end.x() ==start.x():
            x0 = start.x()+width
            y0 = start.y()
            x1 = start.x()-width
            y1 = start.y()
            x2 = end.x()-width
            y2 = end.y()
            x3 = end.x()+width
            y3 = end.y()
        else:
            slope0 =(start.x()-end.x())/(end.y()-start.y())
            if abs(slope0) > 1:
                x0 = np.round(start.x()+1/slope0*width).astype(int)
                y0 = start.y()+width
                x1 = np.round(start.x()-1/slope0*width).astype(int)
                y1 = start.y()-width
                x2 = np.round(end.x()-1/slope0*width).astype(int)
                y2 = end.y()-width
                x3 = np.round(end.x()+1/slope0*width).astype(int)
                y3 = end.y()+width
            else:
                x0 = start.x()-width
                y0 = np.round(start.y()-slope0*width).astype(int)
                x1 = start.x()+width
                y1 = np.round(start.y()+slope0*width).astype(int)
                x2 = end.x()+width
                y2 = np.round(end.y()+slope0*width).astype(int)
                x3 = end.x()-width
                y3 = np.round(end.y()-slope0*width).astype(int)
        return QtCore.QPointF(x0,y0),QtCore.QPointF(x1,y1),QtCore.QPointF(x2,y2),QtCore.QPointF(x3,y3)
