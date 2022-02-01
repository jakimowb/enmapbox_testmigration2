from math import ceil, sqrt
from typing import Optional, Tuple

import numpy as np
from PyQt5.QtCore import QSize, QRectF, QPointF
from PyQt5.QtGui import QMouseEvent, QColor
from PyQt5.QtWidgets import QToolButton, QMainWindow, QComboBox, QCheckBox, QDoubleSpinBox
from PyQt5.uic import loadUi
from qgis._core import QgsMapLayerProxyModel, QgsRasterLayer, QgsMapSettings, QgsStyle, QgsColorRamp
from qgis._gui import QgsMapLayerComboBox, QgsMapCanvas, QgsRasterBandComboBox, QgsColorButton, QgsColorRampButton, \
    QgsFilterLineEdit
from scipy.stats import binned_statistic_2d

from enmapbox.qgispluginsupport.qps.pyqtgraph.pyqtgraph import PlotWidget, ImageItem
from enmapbox.qgispluginsupport.qps.utils import SpatialExtent
from enmapboxprocessing.rasterreader import RasterReader
from typeguard import typechecked


@typechecked
class ScatterPlotWidget(PlotWidget):

    def __init__(self, *args, **kwargs):
        PlotWidget.__init__(self, *args, **kwargs, background='#000')

    def mousePressEvent(self, ev):
        self.autoRange()

    def mouseMoveEvent(self, ev):
        self.autoRange()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.autoRange()

    def wheelEvent(self, ev):
        self.autoRange()


@typechecked
class ScatterPlotDialog(QMainWindow):
    mLayer: QgsMapLayerComboBox
    mBandX: QgsRasterBandComboBox
    mBandY: QgsRasterBandComboBox
    mScatterPlot: ScatterPlotWidget

    mMinimumX: QgsFilterLineEdit
    mMaximumX: QgsFilterLineEdit
    mMinimumY: QgsFilterLineEdit
    mMaximumY: QgsFilterLineEdit
    mDensityRamp: QgsColorRampButton
    mDensityP1: QDoubleSpinBox
    mDensityP2: QDoubleSpinBox

    mExtent: QComboBox
    mAccuracy: QComboBox

    mLiveUpdate: QCheckBox
    mApply: QToolButton

    EstimatedAccuracy, ActualAccuracy = 0, 1
    WholeRasterExtent, CurrentCanvasExtent = 0, 1

    def __init__(self, *args, **kwds):
        QMainWindow.__init__(self, *args, **kwds)
        loadUi(__file__.replace('.py', '.ui'), self)

        from enmapbox import EnMAPBox
        self.enmapBox = EnMAPBox.instance()

        self.mMapCanvas: Optional[QgsMapCanvas] = None
        self.mLayer.setFilters(QgsMapLayerProxyModel.RasterLayer)
        self.mMinimumX.clearValue()
        self.mMaximumX.clearValue()
        self.mMinimumY.clearValue()
        self.mMaximumY.clearValue()

        colorRamp: QgsColorRamp = QgsStyle().defaultStyle().colorRamp('Spectral')
        colorRamp.invert()
        self.mDensityRamp.setColorRamp(colorRamp)

        self.mLayer.layerChanged.connect(self.onLayerChanged)
        self.mBandX.bandChanged.connect(self.onLiveUpdate)
        self.mBandY.bandChanged.connect(self.onLiveUpdate)
        self.mScatterPlot.sigDeviceRangeChanged.connect(self.onLiveUpdate)
        self.mMinimumX.textChanged.connect(self.onLiveUpdate)
        self.mMaximumX.textChanged.connect(self.onLiveUpdate)
        self.mMinimumY.textChanged.connect(self.onLiveUpdate)
        self.mMaximumY.textChanged.connect(self.onLiveUpdate)
        self.mDensityRamp.colorRampChanged.connect(self.onLiveUpdate)
        self.mDensityP1.valueChanged.connect(self.onLiveUpdate)
        self.mDensityP2.valueChanged.connect(self.onLiveUpdate)

        self.mExtent.currentIndexChanged.connect(self.onLiveUpdate)
        self.mAccuracy.currentIndexChanged.connect(self.onLiveUpdate)

        self.mApply.clicked.connect(self.onApplyClicked)

    def currentLayer(self) -> Optional[QgsRasterLayer]:
        return self.mLayer.currentLayer()

    def currentBands(self) -> Tuple[Optional[int], Optional[int]]:
        layer = self.mLayer.currentLayer()
        if layer is None:
            return None, None

        bandNoX = self.mBandX.currentBand()
        bandNoY = self.mBandY.currentBand()

        if bandNoX == -1:
            bandNoX = None
        if bandNoY == -1:
            bandNoY = None

        return bandNoX, bandNoY

    def currentExtent(self) -> Optional[SpatialExtent]:
        layer = self.currentLayer()
        if layer is None:
            return None

        if self.mExtent.currentIndex() == self.WholeRasterExtent:
            return SpatialExtent(layer.crs(), layer.extent())
        elif self.mExtent.currentIndex() == self.CurrentCanvasExtent:
            mapSettings: QgsMapSettings = self.mMapCanvas.mapSettings()
            return SpatialExtent(mapSettings.destinationCrs(), self.mMapCanvas.extent()).toCrs(layer.crs())
        else:
            raise ValueError()

    def parseRange(self, textLower: str, textUpper: str, array: np.ndarray) -> Tuple[float, float]:

        def tofloat(text: str) -> Optional[float]:
            print(text)
            try:
                return float(text)
            except:
                return None

        lower = tofloat(textLower)
        upper = tofloat(textUpper)

        if lower is None:
            lower = np.min(array)
        if upper is None:
            upper = np.max(array)

        return float(lower), float(upper)

    def currentSampleSize(self) -> int:
        if self.mAccuracy.currentIndex() == self.EstimatedAccuracy:
            return int(QgsRasterLayer.SAMPLE_SIZE)
        elif self.mAccuracy.currentIndex() == self.ActualAccuracy:
            return 0  # use all pixel
        else:
            raise ValueError()

    def onLayerChanged(self):

        # disconnect old map canvas
        if self.mMapCanvas is not None:
            try:
                self.mMapCanvas.extentsChanged.disconnect(self.onMapCanvasExtentsChanged)
            except:
                pass

        # connect new map canvas
        self.mMapCanvas = None
        layer = self.currentLayer()
        for mapDock in self.enmapBox.dockManager().mapDocks():
            if layer in mapDock.mapCanvas().layers():
                self.mMapCanvas = mapDock.mapCanvas()
                break
        if self.mMapCanvas is not None:
            self.mMapCanvas.extentsChanged.connect(self.onMapCanvasExtentsChanged)

    def onMapCanvasExtentsChanged(self):
        if self.mExtent.currentIndex() == self.WholeRasterExtent:
            return
        self.onLiveUpdate()

    def onApplyClicked(self):

        if self.isHidden():
            return

        layer = self.currentLayer()
        if layer is None:
            return

        bandNoX, bandNoY = self.currentBands()
        if bandNoX is None or bandNoY is None:
            return

        # derive sampling extent
        reader = RasterReader(layer)
        extent = self.currentExtent()
        extent = extent.intersect(reader.extent())

        # derive sampling size
        width = extent.width() / reader.rasterUnitsPerPixelX()
        height = extent.height() / reader.rasterUnitsPerPixelY()
        width = max(min(int(round(width)), reader.width()), 1)  # 1 <= width <= layerWidth
        height = max(min(int(round(height)), reader.height()), 1)  # 1 <= height <= layerHeight

        sampleSize = self.currentSampleSize()
        if sampleSize != 0:
            sampleFraction = sqrt(min(sampleSize / (width * height), 1))
            width = ceil(width * sampleFraction)
            height = ceil(height * sampleFraction)

        # read data
        arrayX, arrayY = reader.arrayFromBoundingBoxAndSize(extent, width, height, [bandNoX, bandNoY])
        valid = np.all(reader.maskArray([arrayX, arrayY], [bandNoX, bandNoY]), axis=0)

        # calculate 2d histogram
        x = arrayX[valid]
        y = arrayY[valid]
        bins: QSize = self.mScatterPlot.size()
        bins = bins.width(), bins.height()
        range = [self.parseRange(self.mMinimumX.value(), self.mMaximumX.value(), x),
                 self.parseRange(self.mMinimumY.value(), self.mMaximumY.value(), y)]
        counts, x_edge, y_edge, binnumber = binned_statistic_2d(x, y, x, 'count', bins, range, True)
        background = counts == 0

        # stretch counts
        lower, upper = np.percentile(counts[counts != 0], [self.mDensityP1.value(), self.mDensityP2.value()])
        counts = np.round((counts - lower) * (254 / (upper - lower)))
        counts = np.clip(counts, 0, 254).astype(np.uint8) + 1
        counts[background] = 0

        # update plot
        self.mScatterPlot.clear()
        xmin, xmax = range[0]
        ymin, ymax = range[1]
        topLeft = QPointF(xmin, ymin)
        bottomRight = QPointF(xmax, ymax)
        rect = QRectF(topLeft, bottomRight)
        imageItem = ImageItem(counts)
        imageItem.setRect(rect)
        lookupTable = utilsQgsColorRampToPyQtGraphLookupTable(self.mDensityRamp.colorRamp())
        lookupTable[0] = 0
        imageItem.setLookupTable(lookupTable)
        self.mScatterPlot.addItem(imageItem)
        self.mScatterPlot.autoRange()

    def onLiveUpdate(self):
        if not self.mLiveUpdate.isChecked():
            return

        self.onApplyClicked()


@typechecked
def utilsQgsColorRampToPyQtGraphLookupTable(colorRamp: QgsColorRamp) -> np.ndarray:
    array = np.empty(shape=(256, 4), dtype=np.uint8)
    for i in range(256):
        color = colorRamp.color(i / 255)
        assert isinstance(color, QColor)
        array[i, 0] = color.red()
        array[i, 1] = color.green()
        array[i, 2] = color.blue()
        array[i, 3] = 255
    return array
