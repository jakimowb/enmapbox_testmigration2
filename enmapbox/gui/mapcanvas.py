from qgis.core import *
from qgis.gui import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import numpy as np

from enmapbox.gui.utils import *

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
    def ShowMapLinkTargets(mapDock):
        from enmapbox.gui.docks import MapDock
        from enmapbox.gui.dockmanager import DockManager
        assert isinstance(mapDock, MapDock)

        canvas1 = mapDock.canvas
        assert isinstance(canvas1, QgsMapCanvas)
        CanvasLinkTargetWidget.RemoveMapLinkTargetWidgets(True)

        for canvas_source in MapCanvas.instances():
            w = CanvasLinkTargetWidget(canvas1, canvas_source)
            w.setAutoFillBackground(False)
            w.show()
            CanvasLinkTargetWidget.LINK_TARGET_WIDGETS.add(w)
            canvas_source.freeze()
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

from enmapbox.gui.utils import KeepRefs
class MapCanvas(QgsMapCanvas, KeepRefs):
    sigContextMenuEvent = pyqtSignal(QContextMenuEvent)
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
        KeepRefs.__init__(self)
        #from enmapbox.gui.docks import MapDock
        #assert isinstance(parentMapDock, MapDock)

        self._id = 'MapCanvas.#{}'.format(MapCanvas._cnt)
        self.setCrsTransformEnabled(True)
        MapCanvas._cnt += 1
        self._extentInitialized = False
        #self.mapdock = parentMapDock
        #self.enmapbox = self.mapdock.enmapbox
        self.acceptDrops()

        self.canvasLinks = []
        # register signals to react on changes
        self.scaleChanged.connect(self.onScaleChanged)
        self.extentsChanged.connect(self.onExtentsChanged)
        self.destinationCrsChanged.connect(lambda : self.sigCrsChanged.emit(self.mapSettings().destinationCrs()))

        self.mMapTools = {}
        self.registerMapTools()
        #activate default map tool
        self.activateMapTool('PAN')

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
        from enmapbox.gui.cursorlocationvalue import CursorLocationValueMapTool
        tool = self.registerMapTool('CURSORLOCATIONVALUE', CursorLocationValueMapTool(self))
        tool.sigLocationRequest.connect(self.sigCursorLocationRequest.emit)

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
        self.sigContextMenuEvent.emit(event)

    def setSpatialExtent(self, spatialExtent):
        assert isinstance(spatialExtent, SpatialExtent)
        if self.spatialExtent() != spatialExtent:
            self.blockSignals(True)
            self.setDestinationCrs(spatialExtent.crs())
            self.setExtent(spatialExtent)
            self.blockSignals(False)
            self.refresh()

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
        #self.setRenderFlag(True)
        self.refreshAllLayers()

        #signal what has been added, what has been removed
        removedLayers = [l for l in lastSet if l not in newSet]
        addedLayers = [l for l in newSet if l not in lastSet]


        if len(removedLayers) > 0:
            self.sigLayersRemoved.emit(removedLayers)
        if len(addedLayers) > 0:
            self.sigLayersAdded.emit(addedLayers)

