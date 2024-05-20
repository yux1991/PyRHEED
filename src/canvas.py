from PyQt6 import QtCore, QtGui, QtWidgets
import numpy as np

class Canvas(QtWidgets.QGraphicsView):

    #public signals
    PHOTO_MOUSE_MOVEMENT = QtCore.pyqtSignal(QtCore.QPoint)
    PHOTO_MOUSE_PRESS = QtCore.pyqtSignal(QtCore.QPointF)
    PHOTO_MOUSE_RELEASE = QtCore.pyqtSignal(QtCore.QPointF,QtCore.QPointF,bool)
    PHOTO_MOUSE_DOUBLE_CLICK = QtCore.pyqtSignal(QtCore.QPoint)
    PLOT_LINE_SCAN = QtCore.pyqtSignal(QtCore.QPointF,QtCore.QPointF)
    PLOT_INTEGRAL = QtCore.pyqtSignal(QtCore.QPointF,QtCore.QPointF,float)
    PLOT_CHI_SCAN = QtCore.pyqtSignal(QtCore.QPointF,float,float,float,float)
    KEY_PRESS = QtCore.pyqtSignal(QtCore.QPointF,QtCore.QPointF)
    KEY_PRESS_WHILE_ARC = QtCore.pyqtSignal(QtCore.QPointF,float)

    def __init__(self, parent,config, isDarkMode):
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
        self._numberOfMoves = 0
        self._scaleBarIsPresent = False
        self._labelIsPresent = False
        self._image_flipud = False
        self._image_fliplr = False
        if isDarkMode:
            self.default_background = QtGui.QColor(50, 50, 50)
        else:
            self.default_background = QtGui.QColor('darkGray')

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
        self._scaleBarLine = self._scene.addLine(QtCore.QLineF(1,2,1,2),QtGui.QPen(QtCore.Qt.GlobalColor.white,10))
        self._scaleBarLine.hide()
        self.setScene(self._scene)

        self.setTransformationAnchor(QtWidgets.QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setBackgroundBrush(QtGui.QBrush(self.default_background))
        self.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)

    def get_flipud(self):
        return self._image_flipud

    def flipud(self):
        self._image_flipud = False if self._image_flipud else True

    def get_fliplr(self):
        return self._image_fliplr
    
    def fliplr(self):
        self._image_fliplr = False if self._image_fliplr else True

    def refresh(self,config):
        canvasDefault = dict(config['canvasDefault'].items())
        self.widthInAngstrom = float(canvasDefault['widthinangstrom'])
        self.radiusMaximum = int(canvasDefault['radiusmaximum'])
        self.span = int(canvasDefault['span'])
        self.tilt = int(canvasDefault['tilt'])
        self.max_zoom_factor = int(canvasDefault['max_zoom_factor'])
        self.clear_annotations()
        self.clear_canvas()
        self.fit_canvas()

    def set_scale_factor(self,s):
        self._scaleFactor = s
        self.width = self.widthInAngstrom*self._scaleFactor

    def has_photo(self):
        return not self._empty

    def fitInView(self, scale=True):
        """This is an overload function"""
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.has_photo():
                unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)

    def label(self,energy,azimuth,fontname,fontsize):
        if self.has_photo():
            self._labelText.setPlainText("Energy = {} keV\n\u03C6 = {}\u00B0".format(energy,azimuth))
            self._labelText.setFont(QtGui.QFont(fontname,fontsize))
            self._labelText.setPos(40,40)
            self._labelText.show()
            self._labelIsPresent = True

    def calibrate(self,scaleFactor,scaleBarLength,fontname,fontsize):
        if self.has_photo():
            self.photorect = self._photo.boundingRect()
            self._scaleBarText.setPlainText("{} \u212B\u207B\u00B9".format(scaleBarLength))
            self._scaleBarText.setFont(QtGui.QFont(fontname,fontsize))
            self._scaleBarText.setPos(180,self.photorect.height()-200)
            self._scaleBarText.show()
            self.scaleBarLength = scaleBarLength*scaleFactor
            x1,y1,x2,y2 =180+self._scaleBarText.boundingRect().width()/2-self.scaleBarLength/2,\
                         self.photorect.height()-160+fontsize*4/3,\
                         180+self._scaleBarText.boundingRect().width()/2+self.scaleBarLength/2,\
                         self.photorect.height()-160+fontsize*4/3
            if x1 < 30:
                self._scaleBarText.setPos(180+30-x1,self.photorect.height()-200)
                x2 += 30-x1
                x1 = 30
            self._scaleBarLine.setLine(QtCore.QLineF(x1,y1,x2,y2))
            self._scaleBarLine.show()
            self._scaleBarIsPresent = True

    def adjust_fonts(self,fontname,fontsize):
        if self.has_photo():
            if self._labelIsPresent:
                self._labelText.setFont(QtGui.QFont(fontname,fontsize))
            if self._scaleBarIsPresent:
                x1,y1,x2,y2 =180+self._scaleBarText.boundingRect().width()/2-self.scaleBarLength/2,\
                             self.photorect.height()-160+fontsize*4/3,\
                             180+self._scaleBarText.boundingRect().width()/2+self.scaleBarLength/2,\
                             self.photorect.height()-160+fontsize*4/3
                if x1 < 30:
                    self._scaleBarText.setPos(180+30-x1,self.photorect.height()-200)
                    x2 += 30-x1
                    x1 = 30
                self._scaleBarText.setFont(QtGui.QFont(fontname,fontsize))
                self._scaleBarLine.setLine(QtCore.QLineF(x1,y1,x2,y2))

    def clear_annotations(self):
        self._labelText.hide()
        self._scaleBarText.hide()
        self._scaleBarLine.hide()
        self._scaleBarIsPresent = False
        self._labelIsPresent = False

    def fit_canvas(self):
        if self.has_photo():
            self.setUpdatesEnabled(False)
            self.fitInView()
            QtCore.QCoreApplication.processEvents()
            self.fitInView()
            self.setUpdatesEnabled(True)
            self._zoom = 0

    def set_photo(self, pixmap=None):
        self._zoom = 0
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QtWidgets.QGraphicsView.DragMode.NoDrag)
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QtWidgets.QGraphicsView.DragMode.NoDrag)
            self._photo.setPixmap(QtGui.QPixmap())

    def wheelEvent(self, event):
        """This is an overload function"""
        if self.has_photo():
            self.setResizeAnchor(QtWidgets.QGraphicsView.ViewportAnchor.AnchorUnderMouse)
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > -self.max_zoom_factor and self._zoom < self.max_zoom_factor:
                self.scale(factor, factor)
                self.end = QtCore.QPointF(self.mapToScene(event.position().toPoint()))
                if self._photo.isUnderMouse():
                    if self._drawingLine:
                        self.draw_line(self.start,self.end)
                    elif self._drawingRect:
                        self.draw_rect(self.start,self.end,self.width)
                    elif self._drawingArc:
                        self.PFRadius = np.sqrt((self.start.x()-self.end.x())**2+(self.start.y()-self.end.y())**2)
                        self.draw_arc(self.start,self.PFRadius,self.width,self.span,self.tilt)
            elif self._zoom <=-self.max_zoom_factor:
                self._zoom = -self.max_zoom_factor
            else:
                self._zoom = self.max_zoom_factor

    def zoom_in(self):
        if self.has_photo():
            self.setResizeAnchor(QtWidgets.QGraphicsView.ViewportAnchor.AnchorViewCenter)
            factor = 1.25
            self._zoom += 1
            if self._zoom > -self.max_zoom_factor and self._zoom < self.max_zoom_factor:
                self.scale(factor, factor)
            elif self._zoom <=-self.max_zoom_factor:
                self._zoom = -self.max_zoom_factor
            else:
                self._zoom = self.max_zoom_factor

    def zoom_out(self):
        if self.has_photo():
            self.setResizeAnchor(QtWidgets.QGraphicsView.ViewportAnchor.AnchorViewCenter)
            factor = 0.8
            self._zoom -= 1
            if self._zoom > -self.max_zoom_factor and self._zoom < self.max_zoom_factor:
                self.scale(factor, factor)
            elif self._zoom <=-self.max_zoom_factor:
                self._zoom = -self.max_zoom_factor
            else:
                self._zoom = self.max_zoom_factor

    def toggle_mode(self,cursormode):
        if not self._photo.pixmap().isNull():
            if cursormode == "line":
                self.setDragMode(QtWidgets.QGraphicsView.DragMode.NoDrag)
                self.setCursor(QtCore.Qt.CursorShape.CrossCursor)
                self._mode = "line"
            if cursormode == "rectangle":
                self.setDragMode(QtWidgets.QGraphicsView.DragMode.NoDrag)
                self.setCursor(QtCore.Qt.CursorShape.CrossCursor)
                self._mode = "rectangle"
            if cursormode == "arc":
                self.setDragMode(QtWidgets.QGraphicsView.DragMode.NoDrag)
                self.setCursor(QtCore.Qt.CursorShape.CrossCursor)
                self._mode = "arc"
            if cursormode == "pan":
                self.setDragMode(QtWidgets.QGraphicsView.DragMode.ScrollHandDrag)
                self._mode = "pan"

    def mouseDoubleClickEvent(self, event):
        """This is an overload function"""
        if self._photo.isUnderMouse():
            if event.button() == QtCore.Qt.MouseButton.LeftButton:
                if not self._mode == "pan":
                    position = self.mapToScene(event.position().toPoint())
                    self.PHOTO_MOUSE_DOUBLE_CLICK.emit(position.toPoint())
        super(Canvas, self).mouseDoubleClickEvent(event)


    def mousePressEvent(self, event):
        """This is an overload function"""
        if self._photo.isUnderMouse():
            if event.button() == QtCore.Qt.MouseButton.LeftButton:
                if not self._mode == "pan":
                    self.start = QtCore.QPointF(self.mapToScene(event.position().toPoint()))
                if self._mode == "line":
                    self._drawingLine = True
                if self._mode == "rectangle":
                    self._drawingRect = True
                if self._mode == "arc":
                    self._drawingArc = True
                if not self._mode =="pan":
                    self._mouseIsPressed = True
        super(Canvas, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """This is an overload function"""
        if self._photo.isUnderMouse():
            if self._drawingLine or self._drawingArc or self._drawingRect:
                self.end = QtCore.QPointF(self.mapToScene(event.position().toPoint()))
            if self._drawingLine:
                self.draw_line(self.start,self.end)
            elif self._drawingRect:
                self.draw_rect(self.start,self.end,self.width)
            elif self._drawingArc:
                self.PFRadius = np.sqrt((self.start.x()-self.end.x())**2+(self.start.y()-self.end.y())**2)
                if not self.PFRadius > self.radiusMaximum*self._scaleFactor:
                    self.draw_arc(self.start,self.PFRadius,self.width,self.span,self.tilt)
            if not self._mode == "pan":
                if self._mouseIsPressed:
                    if self._numberOfMoves == 0:
                        self.PHOTO_MOUSE_PRESS.emit(self.start)
                    self._mouseIsMoved = True
                    self._numberOfMoves+=1
            position = QtCore.QPointF(self.mapToScene(event.position().toPoint()))
            self.PHOTO_MOUSE_MOVEMENT.emit(position.toPoint())
        super(Canvas, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """This is an overload function"""
        ShiftModified = False
        if self._photo.isUnderMouse():
            if event.button() == QtCore.Qt.MouseButton.LeftButton:
                if self._mouseIsPressed and self._mouseIsMoved:
                    if QtGui.QGuiApplication.queryKeyboardModifiers()==QtCore.Qt.KeyboardModifier.ShiftModifier:
                        ShiftModified = True
                    self.end = QtCore.QPointF(self.mapToScene(event.position().toPoint()))
                    if self._drawingLine:
                        self.draw_line(self.start,self.end)
                    elif self._drawingRect:
                        self.draw_rect(self.start,self.end,self.width)
                    elif self._drawingArc:
                        if not self.PFRadius > self.radiusMaximum*self._scaleFactor:
                            self.PFRadius = np.sqrt((self.start.x()-self.end.x())**2+(self.start.y()-self.end.y())**2)
                            self.draw_arc(self.start,self.PFRadius,self.width,self.span,self.tilt)
                    position = self.mapToScene(event.position().toPoint())
                    self.PHOTO_MOUSE_RELEASE.emit(self.end,self.start,ShiftModified)
        self._drawingLine = False
        self._drawingRect = False
        self._drawingArc = False
        self._mouseIsPressed = False
        self._mouseIsMoved = False
        self._numberOfMoves = 0
        super(Canvas, self).mouseReleaseEvent(event)

    def keyPressEvent(self,event):
        """This is an overload function"""
        XStep = QtCore.QPointF(10.0,0.0)
        YStep = QtCore.QPointF(0.0,10.0)
        XFineStep = QtCore.QPointF(1.0,0.0)
        YFineStep = QtCore.QPointF(0.0,1.0)
        if event.key() == QtCore.Qt.Key.Key_Up:
            if QtGui.QGuiApplication.queryKeyboardModifiers()==QtCore.Qt.KeyboardModifier.ControlModifier:
                self.saveStart-=YFineStep
                if not self.canvasObject == "arc":
                    self.saveEnd-=YFineStep
            else:
                self.saveStart-=YStep
                if not self.canvasObject == "arc":
                    self.saveEnd-=YStep
            if self.canvasObject == "line":
                self.PLOT_LINE_SCAN.emit(self.saveStart,self.saveEnd)
                self.draw_line(self.saveStart,self.saveEnd)
                self.KEY_PRESS.emit(self.saveStart,self.saveEnd)
            elif self.canvasObject == "rectangle":
                self.PLOT_INTEGRAL.emit(self.saveStart,self.saveEnd,self.saveWidth)
                self.draw_rect(self.saveStart,self.saveEnd,self.saveWidth)
                self.KEY_PRESS.emit(self.saveStart,self.saveEnd)
            elif self.canvasObject == "arc":
                self.PLOT_CHI_SCAN.emit(self.saveStart,self.saveRadius,self.saveWidth,self.saveSpan,self.saveTilt)
                self.draw_arc(self.saveStart,self.saveRadius,self.saveWidth,self.saveSpan,self.saveTilt)
                self.KEY_PRESS_WHILE_ARC.emit(self.saveStart,self.saveRadius)
        elif event.key() == QtCore.Qt.Key.Key_Down:
            if QtGui.QGuiApplication.queryKeyboardModifiers()==QtCore.Qt.KeyboardModifier.ControlModifier:
                self.saveStart+=YFineStep
                if not self.canvasObject == "arc":
                    self.saveEnd+=YFineStep
            else:
                self.saveStart+=YStep
                if not self.canvasObject == "arc":
                    self.saveEnd+=YStep
            if self.canvasObject == "line":
                self.PLOT_LINE_SCAN.emit(self.saveStart,self.saveEnd)
                self.draw_line(self.saveStart,self.saveEnd)
                self.KEY_PRESS.emit(self.saveStart,self.saveEnd)
            elif self.canvasObject == "rectangle":
                self.PLOT_INTEGRAL.emit(self.saveStart,self.saveEnd,self.saveWidth)
                self.draw_rect(self.saveStart,self.saveEnd,self.saveWidth)
                self.KEY_PRESS.emit(self.saveStart,self.saveEnd)
            elif self.canvasObject == "arc":
                self.PLOT_CHI_SCAN.emit(self.saveStart,self.saveRadius,self.saveWidth,self.saveSpan,self.saveTilt)
                self.draw_arc(self.saveStart,self.saveRadius,self.saveWidth,self.saveSpan,self.saveTilt)
                self.KEY_PRESS_WHILE_ARC.emit(self.saveStart,self.saveRadius)
        elif event.key() == QtCore.Qt.Key.Key_Left:
            if QtGui.QGuiApplication.queryKeyboardModifiers()==QtCore.Qt.KeyboardModifier.ControlModifier:
                self.saveStart-=XFineStep
                if not self.canvasObject == "arc":
                    self.saveEnd-=XFineStep
            else:
                self.saveStart-=XStep
                if not self.canvasObject == "arc":
                    self.saveEnd-=XStep
            if self.canvasObject == "line":
                self.PLOT_LINE_SCAN.emit(self.saveStart,self.saveEnd)
                self.draw_line(self.saveStart,self.saveEnd)
                self.KEY_PRESS.emit(self.saveStart,self.saveEnd)
            elif self.canvasObject == "rectangle":
                self.PLOT_INTEGRAL.emit(self.saveStart,self.saveEnd,self.saveWidth)
                self.draw_rect(self.saveStart,self.saveEnd,self.saveWidth)
                self.KEY_PRESS.emit(self.saveStart,self.saveEnd)
            elif self.canvasObject == "arc":
                self.PLOT_CHI_SCAN.emit(self.saveStart,self.saveRadius,self.saveWidth,self.saveSpan,self.saveTilt)
                self.draw_arc(self.saveStart,self.saveRadius,self.saveWidth,self.saveSpan,self.saveTilt)
                self.KEY_PRESS_WHILE_ARC.emit(self.saveStart,self.saveRadius)
        elif event.key() == QtCore.Qt.Key.Key_Right:
            if QtGui.QGuiApplication.queryKeyboardModifiers()==QtCore.Qt.KeyboardModifier.ControlModifier:
                self.saveStart+=XFineStep
                if not self.canvasObject == "arc":
                    self.saveEnd+=XFineStep
            else:
                self.saveStart+=XStep
                if not self.canvasObject == "arc":
                    self.saveEnd+=XStep
            if self.canvasObject == "line":
                self.PLOT_LINE_SCAN.emit(self.saveStart,self.saveEnd)
                self.draw_line(self.saveStart,self.saveEnd)
                self.KEY_PRESS.emit(self.saveStart,self.saveEnd)
            elif self.canvasObject == "rectangle":
                self.PLOT_INTEGRAL.emit(self.saveStart,self.saveEnd,self.saveWidth)
                self.draw_rect(self.saveStart,self.saveEnd,self.saveWidth)
                self.KEY_PRESS.emit(self.saveStart,self.saveEnd)
            elif self.canvasObject == "arc":
                self.PLOT_CHI_SCAN.emit(self.saveStart,self.saveRadius,self.saveWidth,self.saveSpan,self.saveTilt)
                self.draw_arc(self.saveStart,self.saveRadius,self.saveWidth,self.saveSpan,self.saveTilt)
                self.KEY_PRESS_WHILE_ARC.emit(self.saveStart,self.saveRadius)

    def clear_canvas(self):
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

    def draw_line(self,start,end,EnablePlot = True):
        self.clear_canvas()
        if QtGui.QGuiApplication.queryKeyboardModifiers() == QtCore.Qt.KeyboardModifier.ShiftModifier:
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
        self._lineItem = self._scene.addLine(QtCore.QLineF(start,end),QtGui.QPen(QtCore.Qt.GlobalColor.yellow,1))
        self._lineItem.show()
        self.canvasObject = "line"
        self.saveStart,self.saveEnd = start,end
        if EnablePlot:
            self.PLOT_LINE_SCAN.emit(start,end)

    def draw_rect(self,start,end,width,EnablePlot = True):
        self.clear_canvas()
        rect = QtGui.QPolygonF()
        if QtGui.QGuiApplication.queryKeyboardModifiers()==QtCore.Qt.KeyboardModifier.ShiftModifier:
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
        p1,p2,p3,p4 = self.get_rectangle_position(start,end,width)
        rect.append(p1)
        rect.append(p2)
        rect.append(p3)
        rect.append(p4)
        self._rectItem = self._scene.addPolygon(rect,QtGui.QPen(QtCore.Qt.GlobalColor.yellow,1))
        self._rectItem.show()
        self.canvasObject = "rectangle"
        self.saveStart,self.saveEnd,self.saveWidth = start,end,width
        if EnablePlot:
            self.PLOT_INTEGRAL.emit(self.saveStart,self.saveEnd,self.saveWidth)

    def draw_arc(self,start,radius,width,span,tilt):
        self.clear_canvas()
        arc1x0,arc1y0,arc1x1,arc1y1 = start.x()-(radius+width),start.y()-(radius+width),\
                                      start.x()+(radius+width),start.y()+(radius+width)
        arc2x0,arc2y0,arc2x1,arc2y1 = start.x()-(radius-width),start.y()-(radius-width),\
                                      start.x()+(radius-width),start.y()+(radius-width)
        arc3x0,arc3y0,arc3x1,arc3y1 = start.x()-(radius),start.y()-radius,start.x()+(radius),\
                                      start.y()+(radius)
        rect1 = QtCore.QRectF(arc1x0,arc1y0,arc1x1-arc1x0,arc1y1-arc1y0)
        rect2 = QtCore.QRectF(arc2x0,arc2y0,arc2x1-arc2x0,arc2y1-arc2y0)
        rect3 = QtCore.QRectF(arc3x0,arc3y0,arc3x1-arc3x0,arc3y1-arc3y0)
        self._arcItem3=self._scene.addEllipse(rect3,QtGui.QPen(QtCore.Qt.GlobalColor.yellow,1))
        self._arcItem3.setStartAngle(int((270-span/2+tilt)*16))
        self._arcItem3.setSpanAngle(int((span)*16))
        self._arcItem3.show()
        self._arcItem1=self._scene.addEllipse(rect1,QtGui.QPen(QtCore.Qt.GlobalColor.yellow,1))
        self._arcItem1.setStartAngle(int((270-span/2+tilt)*16))
        self._arcItem1.setSpanAngle(int(span*16))
        self._arcItem1.show()
        self._arcItem2=self._scene.addEllipse(rect2,QtGui.QPen(QtCore.Qt.GlobalColor.yellow,1))
        self._arcItem2.setStartAngle(int((270-span/2+tilt)*16))
        self._arcItem2.setSpanAngle(int(span*16))
        self._arcItem2.show()
        self.canvasObject = "arc"
        self.saveStart,self.saveRadius,self.saveWidth,self.saveSpan,self.saveTilt = start,radius,width,span,tilt
        self.PLOT_CHI_SCAN.emit(self.saveStart,self.saveRadius,self.saveWidth,self.saveSpan,self.saveTilt)

    def line_scan_signal_emit(self):
        self.PLOT_LINE_SCAN.emit(self.saveStart,self.saveEnd)

    def integral_signal_emit(self):
        self.PLOT_INTEGRAL.emit(self.saveStart,self.saveEnd,self.saveWidth)

    def chi_scan_signal_emit(self):
        self.PLOT_CHI_SCAN.emit(self.saveStart,self.saveRadius,self.saveWidth,self.saveSpan,self.saveTilt)

    def get_rectangle_position(self,start,end,width):
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
        """This is an overload function"""
        self.menu = QtWidgets.QMenu()
        self.clear = QtGui.QAction('Clear')
        self.clear.triggered.connect(self.clear_canvas)
        self.save = QtGui.QAction('Save as...')
        self.save.triggered.connect(self.save_scene)
        self.menu.addAction(self.clear)
        self.menu.addAction(self.save)
        self.menu.popup(event.globalPos())

    def save_scene(self):
        dirname = os.path.dirname(__file__)
        imageFileName = QtWidgets.QFileDialog.getSaveFileName(None,"choose save file name",os.path.join(dirname,"pattern.jpeg"),\
                                                                   "Image (*.jpeg)")
        rect = self._scene.sceneRect()
        capture = QtGui.QImage(rect.size().toSize(),QtGui.QImage.Format.Format_ARGB32_Premultiplied)
        painter = QtGui.QPainter(capture)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        self._scene.render(painter,QtCore.QRectF(capture.rect()),QtCore.QRectF(rect))
        painter.end()
        capture.save(imageFileName[0])

