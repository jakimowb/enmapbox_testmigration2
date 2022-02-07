import traceback
from random import randint
from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent, QColor
from PyQt5.QtWidgets import QToolButton, QMainWindow, QCheckBox, QTableWidget, QSpinBox, QComboBox, QApplication, \
    QMessageBox
from PyQt5.uic import loadUi
from qgis._core import QgsRasterLayer, QgsRasterDataProvider, QgsRasterHistogram, QgsMapLayerProxyModel, QgsMapSettings
from qgis._gui import QgsMapCanvas, QgsMapLayerComboBox, QgsColorButton

from classfractionstatisticsapp.classfractionrenderer import ClassFractionRenderer
from enmapbox.qgispluginsupport.qps.layerproperties import rendererFromXml
from enmapbox.qgispluginsupport.qps.pyqtgraph.pyqtgraph import PlotWidget
from enmapbox.qgispluginsupport.qps.utils import SpatialExtent
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.typing import Categories, Category
from enmapboxprocessing.utils import Utils
from typeguard import typechecked


@typechecked
class ClassFractionStatisticsDialog(QMainWindow):
    mLayer: QgsMapLayerComboBox
    mTable: QTableWidget

    mPasteStyle: QToolButton

    mHistogramMinimum: QSpinBox
    mHistogramMaximum: QSpinBox
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

        self.mLayer.layerChanged.connect(self.onLayerChanged)

        self.mPasteStyle.clicked.connect(self.onPasteStyleClicked)

        self.mApply.clicked.connect(self.onApplyClicked)

        self.mHistogramMinimum.valueChanged.connect(self.onLiveUpdate)
        self.mHistogramMaximum.valueChanged.connect(self.onLiveUpdate)

    def onLayerChanged(self):

        self.removeAllItems()

        # disconnect old map canvas
        if self.mMapCanvas is not None:
            try:
                self.mMapCanvas.extentsChanged.disconnect(self.onMapCanvasExtentsChanged)
            except:
                pass

        # connect new map canvas
        self.mMapCanvas = None
        layer = self.currentLayer()
        if layer is None:
            return
        for mapDock in self.enmapBox.dockManager().mapDocks():
            if layer in mapDock.mapCanvas().layers():
                self.mMapCanvas = mapDock.mapCanvas()
                break
        if self.mMapCanvas is not None:
            self.mMapCanvas.extentsChanged.connect(self.onMapCanvasExtentsChanged)

        # init table
        self.mTable.setRowCount(layer.bandCount())
        for row in range(layer.bandCount()):
            bandNo = row + 1
            color = QColor(randint(0, 255), randint(0, 255), randint(0, 255))
            bandName = RasterReader(layer).bandName(bandNo)

            w = QCheckBox(bandName)
            w.setCheckState(Qt.Checked)
            w.stateChanged.connect(self.onLiveUpdate)
            self.mTable.setCellWidget(row, 0, w)

            w = QgsColorButton()
            w.setColor(color)
            w.setShowMenu(False)
            w.setAutoRaise(True)
            w.setFixedSize(30, 30)
            w.colorChanged.connect(self.onLiveUpdate)
            self.mTable.setCellWidget(row, 1, w)

            w = HistogramPlotWidget()
            w.setFixedHeight(30)
            self.mTable.setCellWidget(row, 2, w)

        self.onLiveUpdate()

    def currentLayer(self) -> Optional[QgsRasterLayer]:
        return self.mLayer.currentLayer()

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

    def currentSampleSize(self) -> int:
        if self.mAccuracy.currentIndex() == self.EstimatedAccuracy:
            return int(QgsRasterLayer.SAMPLE_SIZE)
        elif self.mAccuracy.currentIndex() == self.ActualAccuracy:
            return 0  # use all pixel
        else:
            raise ValueError()

    def onPasteStyleClicked(self):
        try:
            mimeData = QApplication.clipboard().mimeData()
            renderer = rendererFromXml(mimeData)
            categories = Utils.categoriesFromRenderer(renderer)
        except:
            traceback.print_exc()
            QMessageBox.warning(
                self, 'Paste Style', 'Unable to derive categories from clipboard content. '
                                     'Inspect console for details.'
            )
            return

        for row, category in zip(range(self.mTable.rowCount()), categories):
            w: QgsColorButton = self.mTable.cellWidget(row, 1)
            w.setColor(QColor(category.color))
        self.onLiveUpdate()

    def removeAllItems(self):
        for i in reversed(range(self.mTable.rowCount())):
            self.mTable.removeRow(i)
        self.onLiveUpdate()

    def currentItemValues(self):
        for row in range(self.mTable.rowCount()):
            bandNo: int = row + 1
            checked: bool = self.mTable.cellWidget(row, 0).isChecked()
            name: str = self.mTable.cellWidget(row, 0).text()
            color: QColor = self.mTable.cellWidget(row, 1).color()
            plotWidget: HistogramPlotWidget = self.mTable.cellWidget(row, 2)
            yield checked, bandNo, color, name, plotWidget

    def currentCategories(self) -> Categories:
        categories = list()
        for checked, bandNo, color, name, plotItem in self.currentItemValues():
            if not checked:
                continue
            categories.append(Category(bandNo, name, color.name()))
        return categories

    def currentRenderer(self) -> ClassFractionRenderer:
        renderer = ClassFractionRenderer()
        categories = self.currentCategories()
        for category in categories:
            renderer.addCategory(category)
        return renderer

    def onApplyClicked(self):
        layer = self.currentLayer()
        if layer is None:
            return

        layer.setRenderer(self.currentRenderer())
        self.onMapCanvasExtentsChanged()
        layer.triggerRepaint()

    def onLiveUpdate(self):
        if self.mLiveUpdate.isChecked():
            self.onApplyClicked()

    def onMapCanvasExtentsChanged(self):
        layer = self.currentLayer()
        if layer is None:
            return

        if self.mMapCanvas is None:
            return

        extent = self.currentExtent()
        sampleSize = self.currentSampleSize()

        for checked, bandNo, color, name, plotWidget in self.currentItemValues():
            # clear current plot
            plotWidget.clear()
            plotWidget.getAxis('bottom').setPen('#000000')
            plotWidget.getAxis('left').setPen('#000000')

            # make new plot
            if checked:
                provider: QgsRasterDataProvider = layer.dataProvider()
                minimum = self.mHistogramMinimum.value()
                maximum = self.mHistogramMaximum.value()
                binCount = maximum - minimum
                rasterHistogram: QgsRasterHistogram = provider.histogram(
                    bandNo, binCount, minimum / 100., maximum / 100., extent, sampleSize
                )
                y = rasterHistogram.histogramVector
                x = range(binCount + 1)
                plot = plotWidget.plot(x, y, stepMode='center', fillLevel=0, brush=color)
                plot.setPen(color=color, width=1)
                plotWidget.autoRange()


@typechecked
class HistogramPlotWidget(PlotWidget):
    def __init__(self):
        PlotWidget.__init__(self, parent=None, background='#ffffff')
        self.getPlotItem().hideAxis('bottom')
        self.getPlotItem().hideAxis('left')

    def mousePressEvent(self, ev):
        self.autoRange()

    def mouseMoveEvent(self, ev):
        self.autoRange()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.autoRange()
