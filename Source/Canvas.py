from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np

class Canvas(QtWidgets.QGraphicsView):

    #public signals
    photoMouseMovement = QtCore.pyqtSignal(QtCore.QPoint)
    photoMousePress = QtCore.pyqtSignal(QtCore.QPoint)
    photoMouseRelease = QtCore.pyqtSignal(QtCore.QPoint)
    photoMouseDoubleClick = QtCore.pyqtSignal(QtCore.QPoint)
    plotLineScan = QtCore.pyqtSignal(QtCore.QPointF,QtCore.QPointF)
    plotIntegral = QtCore.pyqtSignal(QtCore.QPointF,QtCore.QPointF,float)
    plotChiScan = QtCore.pyqtSignal(QtCore.QPointF,float,float,float,float)
    KeyPress = QtCore.pyqtSignal(QtCore.QPointF,QtCore.QPointF)
    KeyPressWhileArc = QtCore.pyqtSignal(QtCore.QPointF,float)

    def __init__(self, parent,config):
        super(Canvas, self).__init__(parent)
        self._mode = "pan"
        self.canvasObject = "none"
        self._drawingLine = False
        self._drawingRect = False
        self._drawingArc = False
        self._mouseIsPressed = False
        self._mouseIsMoved = False
        self._zoom = 0
        self._scaleFactor = 1
        self._empty = True

        #Defaults
        canvasDefault = dict(config['canvasDefault'].items())
        self.widthInAngstrom = float(canvasDefault['widthinangstrom'])
        self.radiusMaximum = int(canvasDefault['radiusmaximum'])
        self.span = int(canvasDefault['span'])
        self.tilt = int(canvasDefault['tilt'])
        self.max_zoom_factor = int(canvasDefault['max_zoom_factor'])

        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self._labelText = self._scene.addText("")
        self._labelText.setDefaultTextColor(QtGui.QColor("white"))
        self._scaleBarText = self._scene.addText("")
        self._scaleBarText.setDefaultTextColor(QtGui.QColor("white"))
        self._scaleBarLine = self._scene.addLine(QtCore.QLineF(1,2,1,2),QtGui.QPen(QtCore.Qt.white,10))
        self._scaleBarLine.hide()
        self.setScene(self._scene)

        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor('darkGray')))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)

    def refresh(self,config):
        canvasDefault = dict(config['canvasDefault'].items())
        self.widthInAngstrom = float(canvasDefault['widthinangstrom'])
        self.radiusMaximum = int(canvasDefault['radiusmaximum'])
        self.span = int(canvasDefault['span'])
        self.tilt = int(canvasDefault['tilt'])
        self.max_zoom_factor = int(canvasDefault['max_zoom_factor'])
        self.clearAnnotations()
        self.clearCanvas()
        self.fitCanvas()

    def setScaleFactor(self,s):
        self._scaleFactor = s
        self.width = self.widthInAngstrom*self._scaleFactor

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

    def label(self,energy,azimuth):
        if self.hasPhoto():
            self._labelText.setPlainText("Energy = {} keV\n\u03C6 = {}\u00B0".format(energy,azimuth))
            self._labelText.setFont(QtGui.QFont("Helvetica[Cronyx]",40))
            self._labelText.setPos(40,40)
            self._labelText.show()

    def calibrate(self,scaleFactor,scaleBarLength):
        if self.hasPhoto():
            photorect = self._photo.boundingRect()
            self._scaleBarText.setPlainText("{} \u212B\u207B\u00B9".format(scaleBarLength))
            self._scaleBarText.setFont(QtGui.QFont("Helvetica[Cronyx]",40))
            self._scaleBarText.setPos(180,photorect.height()-160)
            self._scaleBarText.show()
            length = scaleBarLength*scaleFactor
            x1,y1,x2,y2 =180+self._scaleBarText.boundingRect().width()/2-length/2,\
                         photorect.height()-80,\
                         180+self._scaleBarText.boundingRect().width()/2+length/2,\
                         photorect.height()-80
            if x1 < 30:
                self._scaleBarText.setPos(180+30-x1,photorect.height()-160)
                x2 += 30-x1
                x1 = 30
            self._scaleBarLine.setLine(QtCore.QLineF(x1,y1,x2,y2))
            self._scaleBarLine.show()

    def clearAnnotations(self):
        self._labelText.hide()
        self._scaleBarText.hide()
        self._scaleBarLine.hide()

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
                self.end = QtCore.QPointF(self.mapToScene(event.pos()))
                if self._photo.isUnderMouse():
                    if self._drawingLine:
                        self.drawLine(self.start,self.end)
                    elif self._drawingRect:
                        self.drawRect(self.start,self.end,self.width)
                    elif self._drawingArc:
                        self.PFRadius = np.sqrt((self.start.x()-self.end.x())**2+(self.start.y()-self.end.y())**2)
                        self.drawArc(self.start,self.PFRadius,self.width,self.span,self.tilt)
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

    def mouseDoubleClickEvent(self, event):
        if self._photo.isUnderMouse():
            if event.button() == QtCore.Qt.LeftButton:
                if not self._mode == "pan":
                    position = self.mapToScene(event.pos())
                    self.photoMouseDoubleClick.emit(position.toPoint())
        super(Canvas, self).mouseDoubleClickEvent(event)


    def mousePressEvent(self, event):
        if self._photo.isUnderMouse():
            if event.button() == QtCore.Qt.LeftButton:
                if not self._mode == "pan":
                    self.start = QtCore.QPointF(self.mapToScene(event.pos()))
                if self._mode == "line":
                    self._drawingLine = True
                if self._mode == "rectangle":
                    self._drawingRect = True
                if self._mode == "arc":
                    self._drawingArc = True
                if not self._mode =="pan":
                    position = self.mapToScene(event.pos())
                    self.photoMousePress.emit(position.toPoint())
                    self._mouseIsPressed = True
        super(Canvas, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._photo.isUnderMouse():
            if self._drawingLine or self._drawingArc or self._drawingRect:
                self.end = QtCore.QPointF(self.mapToScene(event.pos()))
            if self._drawingLine:
                self.drawLine(self.start,self.end)
            elif self._drawingRect:
                self.drawRect(self.start,self.end,self.width)
            elif self._drawingArc:
                self.PFRadius = np.sqrt((self.start.x()-self.end.x())**2+(self.start.y()-self.end.y())**2)
                if not self.PFRadius > self.radiusMaximum*self._scaleFactor:
                    self.drawArc(self.start,self.PFRadius,self.width,self.span,self.tilt)
            if not self._mode == "pan":
                if self._mouseIsPressed:
                    self._mouseIsMoved = True
            position = self.mapToScene(event.pos())
            self.photoMouseMovement.emit(position.toPoint())
        super(Canvas, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._photo.isUnderMouse():
            if event.button() == QtCore.Qt.LeftButton:
                if self._mouseIsPressed and self._mouseIsMoved:
                    self.end = QtCore.QPointF(self.mapToScene(event.pos()))
                    if self._drawingLine:
                        self.drawLine(self.start,self.end)
                    elif self._drawingRect:
                        self.drawRect(self.start,self.end,self.width)
                    elif self._drawingArc:
                        if not self.PFRadius > self.radiusMaximum*self._scaleFactor:
                            self.PFRadius = np.sqrt((self.start.x()-self.end.x())**2+(self.start.y()-self.end.y())**2)
                            self.drawArc(self.start,self.PFRadius,self.width,self.span,self.tilt)
                    position = self.mapToScene(event.pos())
                    self.photoMouseRelease.emit(position.toPoint())
        self._drawingLine = False
        self._drawingRect = False
        self._drawingArc = False
        self._mouseIsPressed = False
        self._mouseIsMoved = False
        super(Canvas, self).mouseReleaseEvent(event)

    def keyPressEvent(self,event):
        XStep = QtCore.QPointF(10.0,0.0)
        YStep = QtCore.QPointF(0.0,10.0)
        XFineStep = QtCore.QPointF(1.0,0.0)
        YFineStep = QtCore.QPointF(0.0,1.0)
        if event.key() == QtCore.Qt.Key_Up:
            if QtGui.QGuiApplication.queryKeyboardModifiers().__eq__(QtCore.Qt.ControlModifier):
                self.saveStart-=YFineStep
                if not self.canvasObject == "arc":
                    self.saveEnd-=YFineStep
            else:
                self.saveStart-=YStep
                if not self.canvasObject == "arc":
                    self.saveEnd-=YStep
            if self.canvasObject == "line":
                self.plotLineScan.emit(self.saveStart,self.saveEnd)
                self.drawLine(self.saveStart,self.saveEnd)
                self.KeyPress.emit(self.saveStart,self.saveEnd)
            elif self.canvasObject == "rectangle":
                self.plotIntegral.emit(self.saveStart,self.saveEnd,self.saveWidth)
                self.drawRect(self.saveStart,self.saveEnd,self.saveWidth)
                self.KeyPress.emit(self.saveStart,self.saveEnd)
            elif self.canvasObject == "arc":
                self.plotChiScan.emit(self.saveStart,self.saveRadius,self.saveWidth,self.saveSpan,self.saveTilt)
                self.drawArc(self.saveStart,self.saveRadius,self.saveWidth,self.saveSpan,self.saveTilt)
                self.KeyPressWhileArc.emit(self.saveStart,self.saveRadius)
        elif event.key() == QtCore.Qt.Key_Down:
            if QtGui.QGuiApplication.queryKeyboardModifiers().__eq__(QtCore.Qt.ControlModifier):
                self.saveStart+=YFineStep
                if not self.canvasObject == "arc":
                    self.saveEnd+=YFineStep
            else:
                self.saveStart+=YStep
                if not self.canvasObject == "arc":
                    self.saveEnd+=YStep
            if self.canvasObject == "line":
                self.plotLineScan.emit(self.saveStart,self.saveEnd)
                self.drawLine(self.saveStart,self.saveEnd)
                self.KeyPress.emit(self.saveStart,self.saveEnd)
            elif self.canvasObject == "rectangle":
                self.plotIntegral.emit(self.saveStart,self.saveEnd,self.saveWidth)
                self.drawRect(self.saveStart,self.saveEnd,self.saveWidth)
                self.KeyPress.emit(self.saveStart,self.saveEnd)
            elif self.canvasObject == "arc":
                self.plotChiScan.emit(self.saveStart,self.saveRadius,self.saveWidth,self.saveSpan,self.saveTilt)
                self.drawArc(self.saveStart,self.saveRadius,self.saveWidth,self.saveSpan,self.saveTilt)
                self.KeyPressWhileArc.emit(self.saveStart,self.saveRadius)
        elif event.key() == QtCore.Qt.Key_Left:
            if QtGui.QGuiApplication.queryKeyboardModifiers().__eq__(QtCore.Qt.ControlModifier):
                self.saveStart-=XFineStep
                if not self.canvasObject == "arc":
                    self.saveEnd-=XFineStep
            else:
                self.saveStart-=XStep
                if not self.canvasObject == "arc":
                    self.saveEnd-=XStep
            if self.canvasObject == "line":
                self.plotLineScan.emit(self.saveStart,self.saveEnd)
                self.drawLine(self.saveStart,self.saveEnd)
                self.KeyPress.emit(self.saveStart,self.saveEnd)
            elif self.canvasObject == "rectangle":
                self.plotIntegral.emit(self.saveStart,self.saveEnd,self.saveWidth)
                self.drawRect(self.saveStart,self.saveEnd,self.saveWidth)
                self.KeyPress.emit(self.saveStart,self.saveEnd)
            elif self.canvasObject == "arc":
                self.plotChiScan.emit(self.saveStart,self.saveRadius,self.saveWidth,self.saveSpan,self.saveTilt)
                self.drawArc(self.saveStart,self.saveRadius,self.saveWidth,self.saveSpan,self.saveTilt)
                self.KeyPressWhileArc.emit(self.saveStart,self.saveRadius)
        elif event.key() == QtCore.Qt.Key_Right:
            if QtGui.QGuiApplication.queryKeyboardModifiers().__eq__(QtCore.Qt.ControlModifier):
                self.saveStart+=XFineStep
                if not self.canvasObject == "arc":
                    self.saveEnd+=XFineStep
            else:
                self.saveStart+=XStep
                if not self.canvasObject == "arc":
                    self.saveEnd+=XStep
            if self.canvasObject == "line":
                self.plotLineScan.emit(self.saveStart,self.saveEnd)
                self.drawLine(self.saveStart,self.saveEnd)
                self.KeyPress.emit(self.saveStart,self.saveEnd)
            elif self.canvasObject == "rectangle":
                self.plotIntegral.emit(self.saveStart,self.saveEnd,self.saveWidth)
                self.drawRect(self.saveStart,self.saveEnd,self.saveWidth)
                self.KeyPress.emit(self.saveStart,self.saveEnd)
            elif self.canvasObject == "arc":
                self.plotChiScan.emit(self.saveStart,self.saveRadius,self.saveWidth,self.saveSpan,self.saveTilt)
                self.drawArc(self.saveStart,self.saveRadius,self.saveWidth,self.saveSpan,self.saveTilt)
                self.KeyPressWhileArc.emit(self.saveStart,self.saveRadius)

    def clearCanvas(self):
        try:
            self._lineItem.hide()
        except:
            pass
        try:
            self._rectItem.hide()
        except:
            pass
        try:
            self._arcItem1.hide()
            self._arcItem2.hide()
            self._arcItem3.hide()
        except:
            pass
        self.canvasObject = "none"

    def drawLine(self,start,end):
        self.clearCanvas()
        if QtGui.QGuiApplication.queryKeyboardModifiers().__eq__(QtCore.Qt.ShiftModifier):
            if end.x() == start.x():
                slope = 10
            else:
                slope = (end.y()-start.y())/(end.x()-start.x())
            if slope > np.tan(np.pi/3):
                end.setX(start.x())
            elif slope < np.tan(np.pi/6):
                end.setY(start.y())
            else:
                end.setY(end.x()-start.x()+start.y())
        self._lineItem = self._scene.addLine(QtCore.QLineF(start,end),QtGui.QPen(QtCore.Qt.yellow,1))
        self._lineItem.show()
        self.canvasObject = "line"
        self.saveStart,self.saveEnd = start,end
        self.plotLineScan.emit(start,end)

    def drawRect(self,start,end,width):
        self.clearCanvas()
        rect = QtGui.QPolygonF()
        if QtGui.QGuiApplication.queryKeyboardModifiers().__eq__(QtCore.Qt.ShiftModifier):
            if end.x() == start.x():
                slope = 10
            else:
                slope = (end.y()-start.y())/(end.x()-start.x())
            if slope > np.tan(np.pi/3):
                end.setX(start.x())
            elif slope < np.tan(np.pi/6):
                end.setY(start.y())
            else:
                end.setY(end.x()-start.x()+start.y())
        p1,p2,p3,p4 = self.getRectanglePosition(start,end,width)
        rect.append(p1)
        rect.append(p2)
        rect.append(p3)
        rect.append(p4)
        self._rectItem = self._scene.addPolygon(rect,QtGui.QPen(QtCore.Qt.yellow,1))
        self._rectItem.show()
        self.canvasObject = "rectangle"
        self.saveStart,self.saveEnd,self.saveWidth = start,end,width
        self.plotIntegral.emit(self.saveStart,self.saveEnd,self.saveWidth)

    def drawArc(self,start,radius,width,span,tilt):
        self.clearCanvas()
        arc1x0,arc1y0,arc1x1,arc1y1 = start.x()-(radius+width),start.y()-(radius+width),\
                                      start.x()+(radius+width),start.y()+(radius+width)
        arc2x0,arc2y0,arc2x1,arc2y1 = start.x()-(radius-width),start.y()-(radius-width),\
                                      start.x()+(radius-width),start.y()+(radius-width)
        arc3x0,arc3y0,arc3x1,arc3y1 = start.x()-(radius),start.y()-radius,start.x()+(radius),\
                                      start.y()+(radius)
        rect1 = QtCore.QRectF(arc1x0,arc1y0,arc1x1-arc1x0,arc1y1-arc1y0)
        rect2 = QtCore.QRectF(arc2x0,arc2y0,arc2x1-arc2x0,arc2y1-arc2y0)
        rect3 = QtCore.QRectF(arc3x0,arc3y0,arc3x1-arc3x0,arc3y1-arc3y0)
        self._arcItem3=self._scene.addEllipse(rect3,QtGui.QPen(QtCore.Qt.yellow,1))
        self._arcItem3.setStartAngle((270-span/2+tilt)*16)
        self._arcItem3.setSpanAngle((span)*16)
        self._arcItem3.show()
        self._arcItem1=self._scene.addEllipse(rect1,QtGui.QPen(QtCore.Qt.yellow,1))
        self._arcItem1.setStartAngle((270-span/2+tilt)*16)
        self._arcItem1.setSpanAngle(span*16)
        self._arcItem1.show()
        self._arcItem2=self._scene.addEllipse(rect2,QtGui.QPen(QtCore.Qt.yellow,1))
        self._arcItem2.setStartAngle((270-span/2+tilt)*16)
        self._arcItem2.setSpanAngle(span*16)
        self._arcItem2.show()
        self.canvasObject = "arc"
        self.saveStart,self.saveRadius,self.saveWidth,self.saveSpan,self.saveTilt = start,radius,width,span,tilt
        self.plotChiScan.emit(self.saveStart,self.saveRadius,self.saveWidth,self.saveSpan,self.saveTilt)

    def lineScanSignalEmit(self):
        self.plotLineScan.emit(self.saveStart,self.saveEnd)

    def integralSignalEmit(self):
        self.plotIntegral.emit(self.saveStart,self.saveEnd,self.saveWidth)

    def chiScanSignalEmit(self):
        self.plotChiScan.emit(self.saveStart,self.saveRadius,self.saveWidth,self.saveSpan,self.saveTilt)

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

    def contextMenuEvent(self,event):
        self.menu = QtWidgets.QMenu()
        self.clear = QtWidgets.QAction('Clear')
        self.clear.triggered.connect(self.clearCanvas)
        self.save = QtWidgets.QAction('Save as...')
        self.save.triggered.connect(self.saveScene)
        self.menu.addAction(self.clear)
        self.menu.addAction(self.save)
        self.menu.popup(event.globalPos())

    def saveScene(self):
        imageFileName = QtWidgets.QFileDialog.getSaveFileName(None,"choose save file name","./pattern.jpeg",\
                                                                   "Image (*.jpeg)")
        rect = self._scene.sceneRect()
        capture = QtGui.QImage(rect.size().toSize(),QtGui.QImage.Format_ARGB32_Premultiplied)
        painter = QtGui.QPainter(capture)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        self._scene.render(painter,QtCore.QRectF(capture.rect()),QtCore.QRectF(rect))
        painter.end()
        capture.save(imageFileName[0])

