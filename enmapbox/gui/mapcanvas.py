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


class MapCanvas(QgsMapCanvas):
    sigDragEnterEvent = pyqtSignal(QDragEnterEvent)
    sigDragMoveEvent = pyqtSignal(QDragMoveEvent)
    sigDragLeaveEvent = pyqtSignal(QDragLeaveEvent)
    sigDropEvent = pyqtSignal(QDropEvent)
    sigContextMenuEvent = pyqtSignal(QContextMenuEvent)
    sigExtentsChanged = pyqtSignal(object)
    sigLayersRemoved = pyqtSignal(list)
    sigLayersAdded = pyqtSignal(list)

    _cnt = 0

    def __init__(self, parentMapDock, *args, **kwds):
        super(MapCanvas, self).__init__(*args, **kwds)

        from enmapbox.gui.docks import MapDock
        assert isinstance(parentMapDock, MapDock)

        self._id = 'MapCanvas.#{}'.format(MapCanvas._cnt)
        self.setCrsTransformEnabled(True)
        MapCanvas._cnt += 1
        self._extentInitialized = False
        self.mapdock = parentMapDock
        self.enmapbox = self.mapdock.enmapbox
        self.acceptDrops()
        self.extentsChanged.connect(self.sandbox)

    def zoomToFeatureExtent(self, spatialExtent):
        assert isinstance(spatialExtent, SpatialExtent)
        self.setSpatialExtent(spatialExtent)

    def sandbox(self):
        self.sigExtentsChanged.emit(self)

    def __repr__(self):
        return self._id

    #forward to MapDock
    def dragEnterEvent(self, event):
        self.sigDragEnterEvent.emit(event)

    # forward to MapDock
    def dragMoveEvent(self, event):
        self.sigDragMoveEvent.emit(event)

    # forward to MapDock
    def dragLeaveEvent(self, event):
        self.sigDragLeaveEvent.emit(event)

    # forward to MapDock
    def dropEvent(self, event):
        self.sigDropEvent.emit(event)

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
        raise Exception('Depricated: Not supported any more (QGIS 3)')

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
        self.refresh()

        #signal what has been added, what has been removed
        removedLayers = [l for l in lastSet if l not in newSet]
        addedLayers = [l for l in newSet if l not in lastSet]


        if len(removedLayers) > 0:
            self.sigLayersRemoved.emit(removedLayers)
        if len(addedLayers) > 0:
            self.sigLayersAdded.emit(addedLayers)

