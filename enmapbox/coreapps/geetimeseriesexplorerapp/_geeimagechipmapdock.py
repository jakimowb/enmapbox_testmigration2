from math import inf
from typing import Optional

from PyQt5 import uic
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QToolButton, QWidget
from qgis._core import QgsRasterLayer, QgsPointXY, QgsProject, QgsLayerTreeLayer
from qgis._gui import QgsMapCanvas

from enmapbox.qgispluginsupport.qps.crosshair.crosshair import CrosshairMapCanvasItem
from enmapbox.qgispluginsupport.qps.utils import SpatialPoint, SpatialExtent
from enmapbox.gui.dataviews.docks import MapDock
from typeguard import typechecked


@typechecked
class GeeImageChipToolBar(QWidget):
    mStrech: QToolButton

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        uic.loadUi(__file__.replace('.py', '.ui'), self)


@typechecked
class GeeImageChipMapDock(MapDock):
    DefautTitle = 'GEE Image Chip Viewer'

    def __init__(self, *args, **kwargs):
        MapDock.__init__(self, *args, **kwargs)
        self.setTitle(self.DefautTitle)
        self.mapCanvas().setCanvasColor(QColor('#fff'))
        self.backgroundLayer = QgsRasterLayer(
            'type=xyz&url=https://mt1.google.com/vt/lyrs%3Dm%26x%3D%7Bx%7D%26y%3D%7By%7D%26z%3D%7Bz%7D&zmax=19&zmin=0',
            'Google Maps', 'wms'
        )
        self.addLayers([self.backgroundLayer])

        self.mToolBar = GeeImageChipToolBar(self.mapCanvas())

        self.layer: QgsRasterLayer = QgsRasterLayer()
        self.mCenter = SpatialPoint(self.backgroundLayer.crs(), QgsPointXY(0, 0))
        self.scale: float = inf

        self.mCenterCrosshairItem = self.mapCanvas().mCenterCrosshairItem = CrosshairMapCanvasItem(self.mapCanvas())
        self.mCenterCrosshairItem.setVisibility(True)
        self.mCenterCrosshairItem.crosshairStyle().setShowPixelBorder(True)
        style = self.mCenterCrosshairItem.crosshairStyle()
        style.setColor(QColor('#ff0'))

        self.mapCanvas().setLastClickedTrackingEnabled(False)
        self.mapCanvas().extentsChanged.connect(self.ensureMapCanvasConstraints)

    def setLayer(self, layer: QgsRasterLayer):

        # mark layer as image chip
        key = 'GEETSE/isImageChip'
        layer.setCustomProperty(key, True)

        # hide all existing image chips
        layerNode: QgsLayerTreeLayer
        for layerNode in self.treeNode().findLayers():
            if layerNode.layer().customProperty(key, False):
                layerNode.setItemVisibilityChecked(False)

        # if the new image is already opened, show or update it
        for layerNode in self.treeNode().findLayers():
            if layer.name() == layerNode.name():
                layerNode.setItemVisibilityChecked(True)
                self.mCenterCrosshairItem.setRasterGridLayer(layerNode.layer())
                self.layer = layer
                return  # we're done here, just show the existing image -> super fast image browsing!

        # insert new image
        self.layer = layer
        self.addLayers([layer])
        self.mCenterCrosshairItem.setRasterGridLayer(layer)
        self.mapCanvas().setExtent(self.extent())

        # collapse node
        layerNode = self.treeNode().findLayer(layer)
        layerNode.setExpanded(False)

    def setScale(self, scale: float):
        assert scale > 0
        self.scale = scale

    def setCenter(self, center: SpatialPoint):
        self.mCenter = center
        self.mCenterCrosshairItem.setPosition(self.center())

    def center(self) -> SpatialPoint:
        return self.mCenter.toCrs(self.crs())

    def extent(self):
        return SpatialExtent(self.layer.crs(), self.layer.extent()).toCrs(self.crs())

    def crs(self):
        """Return map canvas CRS."""
        return self.mapCanvas().mapSettings().destinationCrs()

    def ensureMapCanvasConstraints(self):
        if not self.layer.isValid():
            return

        self.mapCanvas().blockSignals(True)

        # image chips are always centered
        self.mapCanvas().setCenter(self.center())

        self.mapCanvas().blockSignals(False)
        self.mapCanvas().refresh()
