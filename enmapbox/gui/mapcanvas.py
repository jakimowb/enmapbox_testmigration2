from qgis.core import *
from qgis.gui import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import numpy as np

from enmapbox.gui.utils import *
from enmapbox.gui.utils import KeepRefs
from enmapbox.gui.crosshair import CrosshairMapCanvasItem, CrosshairStyle


class CursorLocationMapTool(QgsMapToolEmitPoint):

    sigLocationRequest = pyqtSignal(SpatialPoint)

    def __init__(self, canvas, showCrosshair=True):
        self.mShowCrosshair = showCrosshair
        self.canvas = canvas
        QgsMapToolEmitPoint.__init__(self, self.canvas)
        self.marker = QgsVertexMarker(self.canvas)
        self.rubberband = QgsRubberBand(self.canvas, QGis.Polygon)

        color = QColor('red')

        self.rubberband.setLineStyle(Qt.SolidLine)
        self.rubberband.setColor(color)
        self.rubberband.setWidth(2)



        self.marker.setColor(color)
        self.marker.setPenWidth(3)
        self.marker.setIconSize(5)
        self.marker.setIconType(QgsVertexMarker.ICON_CROSS)  # or ICON_CROSS, ICON_X

    def canvasPressEvent(self, e):
        geoPoint = self.toMapCoordinates(e.pos())
        self.marker.setCenter(geoPoint)
        #self.marker.show()

    def setStyle(self, color=None, brushStyle=None, fillColor=None, lineStyle=None):
        if color:
            self.rubberband.setColor(color)
        if brushStyle:
            self.rubberband.setBrushStyle(brushStyle)
        if fillColor:
            self.rubberband.setFillColor(fillColor)
        if lineStyle:
            self.rubberband.setLineStyle(lineStyle)
    def canvasReleaseEvent(self, e):


        pixelPoint = e.pixelPoint()

        crs = self.canvas.mapSettings().destinationCrs()
        self.marker.hide()
        geoPoint = self.toMapCoordinates(pixelPoint)
        if self.mShowCrosshair:
            #show a temporary crosshair
            ext = SpatialExtent.fromMapCanvas(self.canvas)
            cen = geoPoint
            geom = QgsGeometry()
            geom.addPart([QgsPoint(ext.upperLeftPt().x(),cen.y()), QgsPoint(ext.lowerRightPt().x(), cen.y())],
                          QGis.Line)
            geom.addPart([QgsPoint(cen.x(), ext.upperLeftPt().y()), QgsPoint(cen.x(), ext.lowerRightPt().y())],
                          QGis.Line)
            self.rubberband.addGeometry(geom, None)
            self.rubberband.show()
            #remove crosshair after 0.25 sec
            QTimer.singleShot(250, self.hideRubberband)

        self.sigLocationRequest.emit(SpatialPoint(crs, geoPoint))

    def hideRubberband(self):
        self.rubberband.reset()



class FullExtentMapTool(QgsMapTool):
    def __init__(self, canvas):
        super(FullExtentMapTool, self).__init__(canvas)
        self.canvas = canvas


    def canvasReleaseEvent(self, mouseEvent):
        self.canvas.zoomToFullExtent()

    def flags(self):
        return QgsMapTool.Transient

class PixelScaleExtentMapTool(QgsMapTool):
    def __init__(self, canvas):
        super(PixelScaleExtentMapTool, self).__init__(canvas)
        self.canvas = canvas

    def flags(self):
        return QgsMapTool.Transient


    def canvasReleaseEvent(self, mouseEvent):
        layers = self.canvas.layers()

        unitsPxX = []
        unitsPxY = []
        for lyr in self.canvas.layers():
            if isinstance(lyr, QgsRasterLayer):
                unitsPxX.append(lyr.rasterUnitsPerPixelX())
                unitsPxY.append(lyr.rasterUnitsPerPixelY())

        if len(unitsPxX) > 0:
            unitsPxX = np.asarray(unitsPxX)
            unitsPxY = np.asarray(unitsPxY)
            if True:
                # zoom to largest pixel size
                i = np.nanargmax(unitsPxX)
            else:
                # zoom to smallest pixel size
                i = np.nanargmin(unitsPxX)
            unitsPxX = unitsPxX[i]
            unitsPxY = unitsPxY[i]
            f = 0.2
            width = f * self.canvas.size().width() * unitsPxX #width in map units
            height = f * self.canvas.size().height() * unitsPxY #height in map units


            center = SpatialPoint.fromMapCanvasCenter(self.canvas)
            extent = SpatialExtent(center.crs(), 0, 0, width, height)
            extent.setCenter(center, center.crs())
            self.canvas.setExtent(extent)
        s = ""

LINK_ON_SCALE = 'SCALE'
LINK_ON_CENTER = 'CENTER'
LINK_ON_CENTER_SCALE = 'CENTER_SCALE'


class CanvasLinkTargetWidget(QFrame):

    LINK_TARGET_WIDGETS = set()


    @staticmethod
    def ShowMapLinkTargets(mapDockOrMapCanvas):
        if isinstance(mapDockOrMapCanvas, MapDock):
            mapDockOrMapCanvas = mapDockOrMapCanvas.canvas
        assert isinstance(mapDockOrMapCanvas, QgsMapCanvas)

        canvas1 = mapDockOrMapCanvas
        assert isinstance(canvas1, QgsMapCanvas)
        CanvasLinkTargetWidget.RemoveMapLinkTargetWidgets(True)

        for canvas_source in MapCanvas.instances():
            if canvas_source != canvas1:
                w = CanvasLinkTargetWidget(canvas1, canvas_source)
                w.setAutoFillBackground(False)
                w.show()
                CanvasLinkTargetWidget.LINK_TARGET_WIDGETS.add(w)
                #canvas_source.freeze()
            s = ""

        s = ""

    @staticmethod
    def linkMaps(maplinkwidget, linktype):
        from enmapbox.gui.mapcanvas import CanvasLink
        CanvasLink(maplinkwidget.canvas1, maplinkwidget.canvas2, linktype)
        CanvasLinkTargetWidget.RemoveMapLinkTargetWidgets()

    @staticmethod
    def RemoveMapLinkTargetWidgets(processEvents=True):
        for w in list(CanvasLinkTargetWidget.LINK_TARGET_WIDGETS):
            CanvasLinkTargetWidget.LINK_TARGET_WIDGETS.remove(w)
            p = w.parent()
            w.hide()
            del(w)
            p.refresh()
            p.update()

        if processEvents:
            #qApp.processEvents()
            QCoreApplication.instance().processEvents()

    def __init__(self, canvas1, canvas2):
        assert isinstance(canvas1, QgsMapCanvas)
        assert isinstance(canvas2, QgsMapCanvas)

        QFrame.__init__(self, parent=canvas2)
        self.canvas1 = canvas1
        self.canvas2 = canvas2
        #self.canvas1.installEventFilter(self)
        self.canvas2.installEventFilter(self)
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)
        self.setCursor(Qt.ArrowCursor)

        ly = QHBoxLayout()
        #add buttons with link functions
        from enmapbox.gui.mapcanvas import LINK_ON_CENTER_SCALE, LINK_ON_SCALE, LINK_ON_CENTER
        self.buttons = list()
        bt = QToolButton(self)
        bt.setToolTip('Link map center')
        bt.clicked.connect(lambda: CanvasLinkTargetWidget.linkMaps(self, LINK_ON_CENTER))
        icon = QIcon(':/enmapbox/icons/link_center.png')
        bt.setIcon(icon)
        bt.setIconSize(QSize(16,16))
        self.buttons.append(bt)

        bt = QToolButton(self)
        bt.setToolTip('Link map scale ("Zoom")')
        bt.clicked.connect(lambda: CanvasLinkTargetWidget.linkMaps(self, LINK_ON_SCALE))
        bt.setIcon(QIcon(':/enmapbox/icons/link_mapscale.png'))
        self.buttons.append(bt)

        bt = QToolButton(self)
        bt.setToolTip('Link map scale and center')
        bt.clicked.connect(lambda: CanvasLinkTargetWidget.linkMaps(self, LINK_ON_CENTER_SCALE))
        bt.setIcon(QIcon(':/enmapbox/icons/link_mapscale_center.png'))
        self.buttons.append(bt)


        btStyle = """
        QToolButton { /* all types of tool button */
        border: 2px solid #8f8f91;
        border-radius: 6px;
        background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #f6f7fa, stop: 1 #dadbde);
        }

        QToolButton[popupMode="1"] { /* only for MenuButtonPopup */
            padding-right: 20px; /* make way for the popup button */
        }

        QToolButton:pressed {
            background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                              stop: 0 #dadbde, stop: 1 #f6f7fa);
        }"""

        for bt in self.buttons:
            bt.setAttribute(Qt.WA_PaintOnScreen)
            bt.setStyleSheet(btStyle)
            bt.setIconSize(QSize(100, 100))
            bt.setAutoRaise(True)
            ly.addWidget(bt)

        self.layout.addLayout(ly, 0,0)
        self.setStyleSheet('background-color:rgba(125, 125, 125, 125);')
        self.setAttribute(Qt.WA_PaintOnScreen)

        self.updatePosition()

    def updatePosition(self):
        if hasattr(self.parent(), 'viewport'):
            parentRect = self.parent().viewport().rect()

        else:
            parentRect = self.parent().rect()

        if not parentRect:
            return

        #get map center
        x = int(parentRect.width() / 2 - self.width() / 2)
        y = int(parentRect.height() / 2 - self.height() / 2)

        mw = int(min([self.width(),self.height()]) * 0.9)
        mw = min([mw, 120])
        for bt in self.buttons:
            bt.setIconSize(QSize(mw, mw))

        #self.setGeometry(x, y, self.width(), self.height())
        self.setGeometry(parentRect)

    def setParent(self, parent):
        self.updatePosition()
        return super(CanvasLinkTargetWidget, self).setParent(parent)

    def resizeEvent(self, event):
        super(CanvasLinkTargetWidget, self).resizeEvent(event)
        self.updatePosition()

    def showEvent(self, event):
        self.updatePosition()
        return super(CanvasLinkTargetWidget, self).showEvent(event)

    def eventFilter(self, obj, event):

        if event.type() == QEvent.Resize:
            s  = ""
            self.updatePosition()
        return False

    def mousePressEvent(self, ev):

        if ev.button() == Qt.RightButton:
            #no choice, remove Widgets
            CanvasLinkTargetWidget.RemoveMapLinkTargetWidgets(True)
            ev.accept()



class CanvasLink(QObject):
    LINKTYPES = [LINK_ON_SCALE, LINK_ON_CENTER, LINK_ON_CENTER_SCALE]

    GLOBAL_LINK_LOCK = False

    @staticmethod
    def resetLinkLock():
        CanvasLink.GLOBAL_LINK_LOCK = False



    def __init__(self, canvas1, canvas2, linkType):
        super(CanvasLink, self).__init__()
        assert linkType in CanvasLink.LINKTYPES
        assert isinstance(canvas1, MapCanvas)
        assert isinstance(canvas2, MapCanvas)
        assert canvas1 != canvas2
        self.linkType = linkType
        self.canvases = [canvas1, canvas2]

        canvas1.addCanvasLink(self)
        canvas2.addCanvasLink(self)

    def removeMe(self):
        """Call this to remove this think from both canvases."""
        self.canvases[0].removeCanvasLink(self)


    @staticmethod
    def applyLinking(initialSrcCanvas):
        if CanvasLink.GLOBAL_LINK_LOCK:
            #do not disturb ongoing linking by starting a new one
            return
        else:
            CanvasLink.GLOBAL_LINK_LOCK = True
            QTimer.singleShot(500, lambda: CanvasLink.resetLinkLock())

            #G0(A) -> G1(B) -> G3(E)
            #      -> G1(C) -> G3(A)
            #               -> G3(E)
            #Gx = Generation. G1 will be set before G2,...
            #A,B,..,E = MapCanvas Instances
            #Order of linking starting from A: B,C,E
            #Note: G3(A) will be not set, as A is already handled (initial signal)
            #      G3(E) receives link from G1(B) only.
            #      change related signals in-between will be blocked by GLOBAL_LINK_LOCK


            handledCanvases = [initialSrcCanvas]

            def filterNextGenerationLinks(srcCanvas):
                linkList = []
                for link in srcCanvas.canvasLinks:
                    dstCanvas = link.theOtherCanvas(srcCanvas)
                    if dstCanvas not in handledCanvases:
                        linkList.append(link)
                return srcCanvas, linkList


            def removeEmptyEntries(nextGen):
                return [pair for pair in nextGen if len(pair[1]) > 0]

            nextGeneration = removeEmptyEntries([filterNextGenerationLinks(initialSrcCanvas)])

            while len(nextGeneration) > 0:
                #get the links that have to be set for the next generation
                _nextGeneration = []
                for item in nextGeneration:
                    srcCanvas, links = item

                    #apply links
                    srcExt = SpatialExtent.fromMapCanvas(srcCanvas)
                    for link in links:
                        dstCanvas = link.theOtherCanvas(srcCanvas)
                        if dstCanvas not in handledCanvases:
                            assert dstCanvas == link.apply(srcCanvas, dstCanvas)
                            handledCanvases.append(dstCanvas)

                    _nextGeneration.extend([filterNextGenerationLinks(srcCanvas)])
                nextGeneration = removeEmptyEntries(_nextGeneration)
            logger.debug('Linking done')

    def containsCanvas(self, canvas):
        return canvas in self.canvases

    def theOtherCanvas(self, canvas):
        assert canvas in self.canvases
        assert len(self.canvases) == 2
        return self.canvases[1] if canvas == self.canvases[0] else self.canvases[0]

    def unlink(self):
        for canvas in self.canvases:
            canvas.removeCanvasLink(self)

    def icon(self):

        if self.linkType == LINK_ON_SCALE:
            src = ":/enmapbox/icons/link_mapscale.png"
        elif self.linkType == LINK_ON_CENTER:
            src = ":/enmapbox/icons/link_center.png"
        elif self.linkType == LINK_ON_CENTER_SCALE:
            src = ":/enmapbox/icons/link_mapscale_center.png"
        else:
            raise NotImplementedError('unknown link type: {}'.format(self.linkType))

        return QIcon(src)

    def apply(self, srcCanvas, dstCanvas):
        assert isinstance(srcCanvas, QgsMapCanvas)
        assert isinstance(dstCanvas, QgsMapCanvas)

        srcExt = SpatialExtent.fromMapCanvas(srcCanvas)

        # original center and extent
        centerO = SpatialPoint.fromMapCanvasCenter(dstCanvas)
        extentO = SpatialExtent.fromMapCanvas(dstCanvas)

        # transform (T) to target CRS
        dstCrs = dstCanvas.mapSettings().destinationCrs()
        extentT = srcExt.toCrs(dstCrs)
        centerT = SpatialPoint(srcExt.crs(), srcExt.center())

        w, h = srcCanvas.width(), srcCanvas.height()
        if w == 0:
            w = max([10, dstCanvas.width()])
        if h == 0:
            h = max([10, dstCanvas.height()])

        mapUnitsPerPx_x = extentT.width() / w
        mapUnitsPerPx_y = extentT.height() / h

        scaledWidth = mapUnitsPerPx_x * dstCanvas.width()
        scaledHeight = mapUnitsPerPx_y * dstCanvas.height()
        scaledBox = SpatialExtent(dstCrs, scaledWidth, scaledHeight).setCenter(centerO)

        if self.linkType == LINK_ON_CENTER:
            dstCanvas.setCenter(centerT)

        elif self.linkType == LINK_ON_SCALE:
            dstCanvas.zoomToFeatureExtent(scaledBox)

        elif self.linkType == LINK_ON_CENTER_SCALE:
            dstCanvas.zoomToFeatureExtent(extentT)

        else:
            raise NotImplementedError()

        s = ""

        return dstCanvas

    def applyTo(self, canvasTo):
        assert isinstance(canvasTo, QgsMapCanvas)
        canvasFrom = self.theOtherCanvas(canvasTo)
        return self.apply(canvasFrom, canvasTo)



    def isSameCanvasPair(self, canvasLink):
        """
        Returns True if canvasLink contains the same canvases
        :param canvasLink:
        :return:
        """
        assert isinstance(canvasLink, CanvasLink)
        return self.canvases[0] in canvasLink.canvases and \
               self.canvases[1] in canvasLink.canvases



    def __repr__(self):
        cs = list(self.canvases)
        return 'CanvasLink "{}" {} <-> {}'.format(self.linkType, cs[0], cs[1])


class MapCanvas(QgsMapCanvas):

    from weakref import WeakSet
    _instances = WeakSet()
    @staticmethod
    def instances():
        return list(MapCanvas._instances)

    #sigContextMenuEvent = pyqtSignal(QContextMenuEvent)
    sigSpatialExtentChanged = pyqtSignal(SpatialExtent)
    sigCrsChanged  = pyqtSignal(QgsCoordinateReferenceSystem)

    sigLayersRemoved = pyqtSignal(list)
    sigLayersAdded = pyqtSignal(list)

    sigCursorLocationRequest = pyqtSignal(SpatialPoint)

    sigCanvasLinkAdded = pyqtSignal(CanvasLink)
    sigCanvasLinkRemoved = pyqtSignal(CanvasLink)
    _cnt = 0


    def __init__(self, *args, **kwds):
        super(MapCanvas, self).__init__(*args, **kwds)
        #KeepRefs.__init__(self)
        #from enmapbox.gui.docks import MapDock
        #assert isinstance(parentMapDock, MapDock)

        self._id = 'MapCanvas.#{}'.format(MapCanvas._cnt)
        self.setCrsTransformEnabled(True)

        MapCanvas._cnt += 1
        self._extentInitialized = False
        #self.mapdock = parentMapDock
        #self.enmapbox = self.mapdock.enmapbox
        self.acceptDrops()


        self.mCrosshairItem = CrosshairMapCanvasItem(self)
        self.setShowCrosshair(False)

        self.canvasLinks = []
        # register signals to react on changes
        self.scaleChanged.connect(self.onScaleChanged)
        self.extentsChanged.connect(self.onExtentsChanged)

        self.destinationCrsChanged.connect(lambda : self.sigCrsChanged.emit(self.mapSettings().destinationCrs()))

        self.mMapTools = {}
        self.registerMapTools()
        #activate default map tool
        self.activateMapTool('PAN')
        MapCanvas._instances.add(self)

    def refresh(self, force=False):

        self.setRenderFlag(True)
        if self.renderFlag() or force:
            super(MapCanvas, self).refresh()
            #super(MapCanvas, self).refreshAllLayers()

    def contextMenu(self):
        """
        Create a context menu for common MapCanvas operations
        :return: QMenu
        """
        menu = QMenu()

        action = menu.addAction('Link with other maps')
        action.setIcon(QIcon(':/enmapbox/icons/link_basic.png'))
        action.triggered.connect(lambda: CanvasLinkTargetWidget.ShowMapLinkTargets(self))
        action = menu.addAction('Remove links to other maps')
        action.setIcon(QIcon(':/enmapbox/icons/link_open.png'))
        action.triggered.connect(lambda: self.removeAllCanvasLinks())

        menu.addSeparator()

        if self.crosshairIsVisible():
            action = menu.addAction('Hide Crosshair')
            action.triggered.connect(lambda : self.setShowCrosshair(False))
        else:
            action = menu.addAction('Show Crosshair')
            action.triggered.connect(lambda: self.setShowCrosshair(True))

        from enmapbox.gui.crosshair import CrosshairDialog
        action = menu.addAction('Set Crosshair Style')
        action.triggered.connect(lambda : self.setCrosshairStyle(
            CrosshairDialog.getCrosshairStyle(
                crosshairStyle=self.crosshairStyle(), mapCanvas=self
            )
        ))

        menu.addSeparator()

        action = menu.addAction('Zoom Full')
        action.setIcon(QIcon(':/enmapbox/icons/mActionZoomFullExtent.png'))
        action.triggered.connect(lambda: self.setExtent(self.fullExtent()))

        action = menu.addAction('Zoom Native Resolution')
        action.setIcon(QIcon(':/enmapbox/icons/mActionZoomActual.png'))
        action.triggered.connect(lambda: self.setExtent(self.fullExtent()))

        menu.addSeparator()

        m = menu.addMenu('Save to...')
        action = m.addAction('PNG')
        action.triggered.connect(lambda: self.saveMapImageDialog('PNG'))
        action = m.addAction('JPEG')
        action.triggered.connect(lambda: self.saveMapImageDialog('JPG'))
        action = m.addAction('Clipboard')
        action.triggered.connect(lambda: QApplication.clipboard().setPixmap(self.pixmap()))
        action = menu.addAction('Copy layer paths')
        action.triggered.connect(lambda: QApplication.clipboard().setText('\n'.join(self.layerPaths())))

        menu.addSeparator()

        action = menu.addAction('Refresh')
        action.setIcon(QIcon(":/enmapbox/icons/mActionRefresh.png"))
        action.triggered.connect(lambda: self.refresh())


        action = menu.addAction('Refresh all layers')
        action.setIcon(QIcon(":/enmapbox/icons/mActionRefresh.png"))
        action.triggered.connect(lambda: self.refreshAllLayers())


        menu.addSeparator()

        action = menu.addAction('Clear map')
        action.triggered.connect(lambda: self.setLayers([]))

        menu.addSeparator()
        action = menu.addAction('Set CRS...')
        action.triggered.connect(self.setCRSfromDialog)

        return menu

    def layerPaths(self):
        """
        Returns the paths/URIs of presented QgsMapLayers
        :return:
        """
        return [str(l.source()) for l in self.layers()]

    def pixmap(self):
        """
        Returns the current map image as pixmap
        :return: QPixmap
        """
        #deprectated
        #return QPixmap(self.map().contentImage().copy())
        return QPixmap.grabWidget(self)

    def saveMapImageDialog(self, fileType):
        from enmapbox.gui import settings
        lastDir = settings().value('CANVAS_SAVE_IMG_DIR', os.path.expanduser('~'))
        path = jp(lastDir, '{}.{}.{}'.format(self.tsdView.TSD.date, self.mapView.title(), fileType.lower()))

        path = QFileDialog.getSaveFileName(self, 'Save map as {}'.format(fileType), path)

        if len(path) > 0:
            self.saveAsImage(path, None, fileType)
            settings().setValue('EMB_SAVE_IMG_DIR', os.path.dirname(path))

    def setCrs(self, crs):
        assert isinstance(crs, QgsCoordinateReferenceSystem)
        if self.crs() != crs:
            self.setDestinationCrs(crs)

    def crs(self):
        return self.mapSettings().destinationCrs()


    def setCRSfromDialog(self, *args):
        setMapCanvasCRSfromDialog(self)

    def setCrosshairStyle(self,crosshairStyle):
        if crosshairStyle is None:
            self.mCrosshairItem.crosshairStyle.setShow(False)
            self.mCrosshairItem.update()
        else:
            assert isinstance(crosshairStyle, CrosshairStyle)
            self.mCrosshairItem.setCrosshairStyle(crosshairStyle)

    def crosshairStyle(self):
        return self.mCrosshairItem.crosshairStyle

    def setShowCrosshair(self,b):
        self.mCrosshairItem.setShow(b)

    def crosshairIsVisible(self):
        return self.mCrosshairItem.mShow

    def registerMapTool(self, key, mapTool):
        assert isinstance(key, str)
        assert isinstance(mapTool, QgsMapTool)
        assert key not in self.mMapTools.keys()
        self.mMapTools[key] = mapTool
        return mapTool

    def registerMapTools(self):
        self.registerMapTool('PAN', QgsMapToolPan(self))
        self.registerMapTool('ZOOM_IN', QgsMapToolZoom(self, False))
        self.registerMapTool('ZOOM_OUT', QgsMapToolZoom(self, True))
        self.registerMapTool('ZOOM_FULL', FullExtentMapTool(self))
        self.registerMapTool('ZOOM_PIXEL_SCALE', PixelScaleExtentMapTool(self))

        tool = self.registerMapTool('CURSORLOCATIONVALUE', CursorLocationMapTool(self, showCrosshair=True))
        tool.sigLocationRequest.connect(self.sigCursorLocationRequest.emit)

        tool = self.registerMapTool('MOVE_CENTER', CursorLocationMapTool(self, showCrosshair=True))
        tool.sigLocationRequest.connect(self.setCenter)


    def activateMapTool(self, key):
        assert key in self.mMapTools.keys(), 'No QgsMapTool registered with key "{}"'.format(key)
        self.setMapTool(self.mMapTools[key])

    def onScaleChanged(self, scale):
        CanvasLink.applyLinking(self)
        pass



    def onExtentsChanged(self):

        CanvasLink.applyLinking(self)
        self.sigSpatialExtentChanged.emit(SpatialExtent.fromMapCanvas(self))

    def zoomToFeatureExtent(self, spatialExtent):
        assert isinstance(spatialExtent, SpatialExtent)
        self.setSpatialExtent(spatialExtent)

    def moveCenterToPoint(self, spatialPoint):
        assert isinstance(spatialPoint, SpatialPoint)


    def zoomToPixelScale(self):
        unitsPxX = []
        unitsPxY = []
        for lyr in self.layers():
            if isinstance(lyr, QgsRasterLayer):
                unitsPxX.append(lyr.rasterUnitsPerPixelX())
                unitsPxY.append(lyr.rasterUnitsPerPixelY())

        if len(unitsPxX) > 0:
            unitsPxX = np.asarray(unitsPxX)
            unitsPxY = np.asarray(unitsPxY)
            if True:
                # zoom to largest pixel size
                i = np.nanargmax(unitsPxX)
            else:
                # zoom to smallest pixel size
                i = np.nanargmin(unitsPxX)
            unitsPxX = unitsPxX[i]
            unitsPxY = unitsPxY[i]
            f = 0.2
            width = f * self.size().width() * unitsPxX  # width in map units
            height = f * self.size().height() * unitsPxY  # height in map units

            center = SpatialPoint.fromMapCanvasCenter(self.canvas)
            extent = SpatialExtent(center.crs(), 0, 0, width, height)
            extent.setCenter(center, center.crs())
            self.setExtent(extent)
        s = ""

    def __repr__(self):
        return self._id

    #forward to MapDock
    def dragEnterEvent(self, event):
        ME = MimeDataHelper(event.mimeData())
        # check mime types we can handle
        assert isinstance(event, QDragEnterEvent)
        if ME.hasMapLayers() or ME.hasUrls() or ME.hasDataSources():
            event.setDropAction(Qt.CopyAction)  # copy but do not remove
            event.accept()
        else:
            event.ignore()


    def dropEvent(self, event):
        ME = MimeDataHelper(event.mimeData())
        newLayers = None
        if ME.hasMapLayers():
            newLayers = ME.mapLayers()
        elif ME.hasDataSources():
            from enmapbox.gui.datasources import DataSourceSpatial
            from enmapbox.gui.enmapboxgui import EnMAPBox
            dataSources = [d for d in ME.dataSources() if isinstance(d, DataSourceSpatial)]
            dataSources = [EnMAPBox.instance().dataSourceManager.addSource(d) for d in dataSources]
            newLayers = [d.createRegisteredMapLayer() for d in dataSources]

        if newLayers != None:
            self.setLayers(newLayers + self.layers())
            event.accept()
            event.acceptProposedAction()

    def contextMenuEvent(self, event):

        menu = self.contextMenu()
        menu.exec_(event.globalPos())

        #self.sigContextMenuEvent.emit(event)

    def setSpatialExtent(self, spatialExtent):
        assert isinstance(spatialExtent, SpatialExtent)
        if self.spatialExtent() != spatialExtent:
            spatialExtent = spatialExtent.toCrs(self.crs())
            if spatialExtent:
                self.setExtent(spatialExtent)

    def setExtent(self, QgsRectangle):
        super(MapCanvas, self).setExtent(QgsRectangle)
        self.setRenderFlag(True)

    def spatialExtent(self):
        return SpatialExtent.fromMapCanvas(self)

    def setLayerSet(self, *arg, **kwds):
        raise Exception('Deprecated: Not supported any more (QGIS 3)')


    def createCanvasLink(self, otherCanvas, linkType):
        assert isinstance(otherCanvas, MapCanvas)
        return self.addCanvasLink(CanvasLink(self, otherCanvas, linkType))

    def addCanvasLink(self, canvasLink):
        assert isinstance(canvasLink, CanvasLink)
        toRemove = [cLink for cLink in self.canvasLinks if cLink.isSameCanvasPair(canvasLink)]
        for cLink in toRemove:
            self.removeCanvasLink(cLink)
        self.canvasLinks.append(canvasLink)
        self.sigCanvasLinkAdded.emit(canvasLink)
        return canvasLink

    def removeCanvasLink(self, canvasLink):
        if canvasLink in self.canvasLinks:
            self.canvasLinks.remove(canvasLink)
            self.sigCanvasLinkRemoved.emit(canvasLink)

    def removeAllCanvasLinks(self):
        toRemove = self.canvasLinks[:]
        for cLink in toRemove:
            for canvas in cLink.canvases:
                canvas.removeCanvasLink(cLink)

    def setLayers(self, mapLayers):
        """
        Sets the list of mapLayers to show in the map canvas
        :param mapLayers: QgsMapLayer or [list-of-QgsMapLayers]
        :return: self
        """
        if not isinstance(mapLayers, list):
            mapLayers = [mapLayers]

        lastSet = self.layers()
        newSet = mapLayers[:]

        #register not-registered layers
        reg = QgsMapLayerRegistry.instance()
        for l in newSet:
            assert isinstance(l, QgsMapLayer)
            if l not in reg.children():
                reg.addMapLayer(l, False)

        #set the new layers (QGIS 2 style)
        #todo: change with QGIS 3
        super(MapCanvas,self).setLayerSet([QgsMapCanvasLayer(l) for l in newSet])

        if not self._extentInitialized and len(newSet) > 0:
            # set canvas to first layer's CRS and full extent
            newExtent = SpatialExtent.fromLayer(newSet[0])
            self.setSpatialExtent(newExtent)
            self._extentInitialized = True
        self.setRenderFlag(True)
        self.refreshAllLayers()

        #signal what has been added, what has been removed
        removedLayers = [l for l in lastSet if l not in newSet]
        addedLayers = [l for l in newSet if l not in lastSet]

        if len(removedLayers) > 0:
            self.sigLayersRemoved.emit(removedLayers)
        if len(addedLayers) > 0:
            self.sigLayersAdded.emit(addedLayers)
        return self


from enmapbox.gui.docks import Dock, DockLabel
class MapDockLabel(DockLabel):

    def __init__(self, *args, **kwds):

        super(MapDockLabel, self).__init__(*args, **kwds)

        self.addMapLink = QToolButton(self)
        self.addMapLink.setToolTip('Link with other map(s)')
        self.addMapLink.setIcon(QIcon(':/enmapbox/icons/link_basic.png'))
        self.buttons.append(self.addMapLink)

        self.removeMapLink = QToolButton(self)
        self.removeMapLink.setToolTip('Remove links to this map')
        self.removeMapLink.setIcon(QIcon(':/enmapbox/icons/link_open.png'))
        self.buttons.append(self.removeMapLink)



def setMapCanvasCRSfromDialog(mapCanvas, crs=None):
    assert isinstance(mapCanvas, QgsMapCanvas)
    w  = QgsProjectionSelectionWidget(mapCanvas)
    if crs is None:
        crs = mapCanvas.mapSettings().destinationCrs()
    else:
        crs = QgsCoordinateReferenceSystem(crs)
    # set current CRS
    w.setCrs(crs)

    lyrs = mapCanvas.layers()
    if len(lyrs) > 0:
        w.setLayerCrs(lyrs[0].crs())

    w.crsChanged.connect(mapCanvas.setDestinationCrs)
    w.selectCrs()
    return w


class MapDock(Dock):
    """
    A dock to visualize geodata that can be mapped
    """
    #sigCursorLocationValueRequest = pyqtSignal(QgsPoint, QgsRectangle, float, QgsRectangle)
    from enmapbox.gui.utils import SpatialPoint, SpatialExtent
    sigCursorLocationRequest = pyqtSignal(SpatialPoint)
    sigLayersAdded = pyqtSignal(list)
    sigLayersRemoved = pyqtSignal(list)
    sigCrsChanged = pyqtSignal(QgsCoordinateReferenceSystem)

    def __init__(self, *args, **kwds):
        initSrc = kwds.pop('initSrc', None)
        super(MapDock, self).__init__(*args, **kwds)
        self.basename = self.title()

        #self.actionLinkExtent = QAction(QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_CommandLink), 'Link to map extent', self)
        #self.actionLinkCenter = QAction(QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_CommandLink), 'Linkt to map center', self)
        #self.label.buttons.append(self.actionLinkCenter.getButton())

        self.canvas = MapCanvas(self)

        #self.label.setText(self.basename)
        #self.canvas.setScaleLocked(True)
        #self.canvas.customContextMenuRequested.connect(self.onCanvasContextMenuEvent)
        #self.canvas.sigContextMenuEvent.connect(self.onCanvasContextMenuEvent)
        self.canvas.sigLayersAdded.connect(self.sigLayersAdded.emit)
        self.canvas.sigLayersRemoved.connect(self.sigLayersRemoved.emit)
        self.canvas.sigCrsChanged.connect(self.sigCrsChanged.emit)
        self.canvas.sigCursorLocationRequest.connect(self.sigCursorLocationRequest)
        settings = QSettings()
        assert isinstance(self.canvas, QgsMapCanvas)
        self.canvas.setCanvasColor(Qt.black)
        self.canvas.enableAntiAliasing(settings.value('/qgis/enable_anti_aliasing', False, type=bool))
        #self.canvas.useImageToRender(settings.value('/qgis/use_image_to_render', False, type=bool))
        self.layout.addWidget(self.canvas)

        """
        The problem still exists in QGis 2.0.1-3 available through OSGeo4W distribution. New style connection always return the same error:
        TypeError: connect() failed between geometryChanged(QgsFeatureId,QgsGeometry) and unislot()
        A possible workaround is to use old signal/slot code:

        QObject.connect(my_vectlayer,SIGNAL("geometryChanged(QgsFeatureId, QgsGeometry&)"),mynicehandler)
        instead of expected:

        my_vectlayer.geometryChanged.connect(mynicehandler)
        """
        #QObject.connect(self.toolIdentify,
        #                SIGNAL("changedRasterResults(QList<QgsMapToolIdentify::IdentifyResult>&)"),
        #                self.identifyChangedRasterResults)
        #self.toolIdentify.changedRasterResults.connect(self.identifyChangedRasterResults)

        from enmapbox.gui.mapcanvas import CanvasLinkTargetWidget
        self.label.addMapLink.clicked.connect(lambda:CanvasLinkTargetWidget.ShowMapLinkTargets(self))
        self.label.removeMapLink.clicked.connect(lambda: self.canvas.removeAllCanvasLinks())

        if initSrc is not None:
            from enmapbox.gui.datasources import DataSourceFactory
            ds = DataSourceFactory.Factory(initSrc)
            if ds is not None:
                self.canvas.setLayers([ds.createUnregisteredMapLayer()])

    def cursorLocationValueRequest(self,*args):
        self.sigCursorLocationRequest.emit(*args)

    def contextMenu(self):
        m = super(MapDock, self).contextMenu()
        from enmapbox.gui.utils import appendItemsToMenu

        return appendItemsToMenu(m, self.canvas.contextMenu())

    #
    #def onCanvasContextMenuEvent(self, event):
    #    menu = self.contextMenu()
    #    menu.exec_(event.globalPos())

    def sandboxSlot(self,crs):
        self.canvas.setDestinationCrs(crs)


    def activateMapTool(self, key):
        self.canvas.activateMapTool(key)

    def mimeData(self):
        return ['']

    def _createLabel(self, *args, **kwds):
        return MapDockLabel(self, *args, **kwds)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
                s = ""
        else:
            super(MapDock, self).mousePressEvent(event)

    def linkWithMapDock(self, mapDock, linkType):
        assert isinstance(mapDock, MapDock)
        self.linkWithCanvas(mapDock.canvas, linkType)


    def linkWithCanvas(self, canvas, linkType):
        assert isinstance(canvas, QgsMapCanvas)
        canvas.createCanvasLink(canvas, linkType)


    def layers(self):
        return self.canvas.layers()

    def setLayers(self, mapLayers):
        assert isinstance(mapLayers, list)
        self.canvas.setLayers(mapLayers)


    def addLayers(self, mapLayers):
        if not type(mapLayers) is list:
            mapLayers = [mapLayers]
        for l in mapLayers:
            assert isinstance(l, QgsMapLayer)
        self.setLayers(mapLayers + self.canvas.layers())

    def removeLayersByURI(self, uri):
        to_remove = []
        uri = os.path.abspath(uri)

        for lyr in self.canvas.layers():
            lyrUri = os.path.abspath(str(lyr.dataProvider().dataSourceUri()))
            if uri == lyrUri:
                to_remove.append(lyr)

        self.removeLayers(to_remove)


    def removeLayers(self, mapLayers):
        newSet = [l for l in self.canvas.layers() if l not in mapLayers]
        self.setLayers(newSet)




if __name__ == '__main__':
    import site, sys
    #add site-packages to sys.path as done by enmapboxplugin.py

    from enmapbox.gui import sandbox
    qgsApp = sandbox.initQgisEnvironment()


    qgsApp.exec_()
    qgsApp.exitQgis()
