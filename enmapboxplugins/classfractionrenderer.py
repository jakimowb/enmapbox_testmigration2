import traceback
from copy import deepcopy
from os.path import splitext
from random import randint
from typing import List

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QMouseEvent
from PyQt5.QtWidgets import QWidget, QToolButton, QTreeWidget, QTreeWidgetItem, QLineEdit, QCheckBox, \
    QApplication, QMessageBox, QMainWindow, QSpinBox
from PyQt5.uic import loadUi
from qgis._core import QgsRasterRenderer, QgsRasterInterface, QgsRectangle, QgsRasterBlockFeedback, QgsRasterBlock, \
    Qgis, QgsRasterLayer, QgsRasterDataProvider, QgsRasterHistogram
from qgis._gui import QgsRasterBandComboBox, QgsColorButton, QgsMapCanvas

from enmapbox.qgispluginsupport.qps.layerproperties import rendererFromXml
from enmapbox.qgispluginsupport.qps.pyqtgraph.pyqtgraph.widgets.PlotWidget import PlotWidget
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.typing import Categories, Category
from enmapboxprocessing.utils import Utils
from typeguard import typechecked


@typechecked
class ClassFractionRenderer(QgsRasterRenderer):

    def __init__(self, input: QgsRasterInterface = None, type: str = ''):
        super().__init__(input, type)
        self.categories: List[Category] = list()

    def addCategory(self, category: Category):
        self.categories.append(category)

    def usesBands(self) -> List[int]:
        return [c.value for c in self.categories]

    def block(self, band_nr: int, extent: QgsRectangle, width: int, height: int,
              feedback: QgsRasterBlockFeedback = None):

        # Sum up weighted category RGBs.
        # We assume weights to be between 0 and 1.
        # We assume that the sum of all weights for a single pixel is <=1.

        r = np.zeros((height, width), dtype=np.float32)
        g = np.zeros((height, width), dtype=np.float32)
        b = np.zeros((height, width), dtype=np.float32)
        a = np.zeros((height, width), dtype=np.float32)
        for category in self.categories:
            bandNo = category.value
            color = QColor(category.color)
            if bandNo < 1 or bandNo > self.input().bandCount():
                continue
            block: QgsRasterBlock = self.input().block(bandNo, extent, width, height)
            weight = Utils.qgsRasterBlockToNumpyArray(block)
            r += color.red() * weight
            g += color.green() * weight
            b += color.blue() * weight
            a[weight > 0] = 255  # every used pixel gets full opacity

        # clip RGBs to 0-255, in case the assumptions where violated
        np.clip(r, 0, 255, r)
        np.clip(g, 0, 255, g)
        np.clip(b, 0, 255, b)

        # convert back to QGIS raster block
        rgba = np.array([r, g, b, a], dtype=np.uint32)
        outarray = (rgba[0] << 16) + (rgba[1] << 8) + rgba[2] + (rgba[3] << 24)
        return Utils.numpyArrayToQgsRasterBlock(outarray, Qgis.ARGB32_Premultiplied)

    def clone(self) -> QgsRasterRenderer:
        renderer = ClassFractionRenderer()
        renderer.categories = deepcopy(self.categories)
        return renderer


@typechecked
class ClassFractionRendererWidget(QMainWindow):
    mTree: QTreeWidget
    mClassify: QToolButton
    mAdd: QToolButton
    mRemove: QToolButton
    mDeleteAll: QToolButton
    mPasteStyle: QToolButton
    mLiveUpdate: QCheckBox
    mMin: QSpinBox
    mMax: QSpinBox

    mOk: QToolButton
    mCancel: QToolButton
    mApply: QToolButton
    mSaveStyle: QToolButton
    mLoadStyle: QToolButton

    def __init__(self, layer: QgsRasterLayer, mapCanvas: QgsMapCanvas, parent=None):
        QWidget.__init__(self, parent)
        loadUi(__file__.replace('.py', '.ui'), self)
        self.layer = layer
        self.mapCanvas = mapCanvas
        self.rendererBackup = layer.renderer().clone()

        self.mAdd.clicked.connect(lambda: self.addItem())
        self.mRemove.clicked.connect(self.removeItem)
        self.mDeleteAll.clicked.connect(self.removeAllItems)
        self.mClassify.clicked.connect(self.classify)
        self.mPasteStyle.clicked.connect(self.pasteStyle)

        self.mOk.clicked.connect(self.onOkClicked)
        self.mCancel.clicked.connect(self.onCancelClicked)
        self.mApply.clicked.connect(self.onApplyClicked)
        self.mSaveStyle.clicked.connect(self.onSaveStyleClicked)
        self.mLoadStyle.clicked.connect(self.onLoadStyleClicked)

        self.mMin.valueChanged.connect(self.onMapCanvasExtentsChanged)
        self.mMax.valueChanged.connect(self.onMapCanvasExtentsChanged)

        self.mapCanvas.extentsChanged.connect(self.onMapCanvasExtentsChanged)

        self.restoreRenderer(self.rendererBackup)

    def restoreRenderer(self, renderer: QgsRasterRenderer):
        self.mTree.clear()
        if isinstance(self.rendererBackup, ClassFractionRenderer):
            for category in renderer.categories:
                self.addItem(category.value, QColor(category.color), label=category.name)

    def pasteStyle(self):
        try:
            mimeData = QApplication.clipboard().mimeData()
            renderer = rendererFromXml(mimeData)
            categories = Utils.categoriesFromRenderer(renderer)
        except:
            traceback.print_exc()
            QMessageBox.warning(self, 'Paste Style', 'Unable to derive categories from clipboard content. '
                                                     'Inspect console for details.')
            return

        self.mTree.clear()
        for bandNo, category in enumerate(categories, 1):
            self.addItem(bandNo, QColor(category.color), label=category.name, liveUpdate=False)
        self.onLiveUpdate()

    def classify(self):
        self.mTree.clear()
        for bandNo in range(1, self.layer.bandCount() + 1):
            self.addItem(bandNo, liveUpdate=False)
        self.onLiveUpdate()

    def addItem(self, bandNo: int = None, color: QColor = None, label: str = None, liveUpdate=True):
        if bandNo is None:
            bandNo = -1
        if color is None:
            color = QColor(randint(0, 255), randint(0, 255), randint(0, 255))
        if label is None:
            if bandNo != -1:
                label = RasterReader(self.layer).bandName(bandNo)

        item = QTreeWidgetItem()
        self.mTree.addTopLevelItem(item)

        checkWidget = QCheckBox()
        checkWidget.setCheckState(Qt.Checked)
        checkWidget.setMinimumHeight(40)
        self.mTree.setItemWidget(item, 0, checkWidget)
        self.mTree.setColumnWidth(0, 10)

        bandWidget = QgsRasterBandComboBox()
        bandWidget.setLayer(self.layer)
        bandWidget.setBand(bandNo)
        bandWidget.setMinimumHeight(40)
        self.mTree.setItemWidget(item, 1, bandWidget)
        self.mTree.resizeColumnToContents(1)

        colorWidget = QgsColorButton()
        colorWidget.setColor(color)
        colorWidget.setShowMenu(False)
        colorWidget.setFixedSize(40, 40)
        colorWidget.setAutoRaise(True)
        self.mTree.setItemWidget(item, 2, colorWidget)

        labelWidget = QLineEdit(label)
        labelWidget.setFrame(False)
        self.mTree.setItemWidget(item, 3, labelWidget)

        plotWidget = HistogramPlotWidget()
        plotWidget.setFixedHeight(40)
        self.mTree.setItemWidget(item, 4, plotWidget)

        if liveUpdate:
            self.onLiveUpdate()

        # connect signals
        bandWidget.bandChanged.connect(lambda bandNo: labelWidget.setText(RasterReader(self.layer).bandName(bandNo)))
        checkWidget.stateChanged.connect(self.onLiveUpdate)
        bandWidget.bandChanged.connect(self.onLiveUpdate)
        colorWidget.colorChanged.connect(self.onLiveUpdate)

    def removeItem(self):
        for item in self.mTree.selectedItems():
            for index in range(self.mTree.topLevelItemCount()):
                if self.mTree.topLevelItem(index) == item:
                    self.mTree.takeTopLevelItem(index)
                    self.onLiveUpdate()
                    return

    def removeAllItems(self):
        self.mTree.clear()
        self.onLiveUpdate()

    def currentItemValues(self):
        for i in range(self.mTree.topLevelItemCount()):
            item: QTreeWidgetItem = self.mTree.topLevelItem(i)
            checked: bool = self.mTree.itemWidget(item, 0).isChecked()
            bandNo: int = self.mTree.itemWidget(item, 1).currentBand()
            color: QColor = self.mTree.itemWidget(item, 2).color()
            name: str = self.mTree.itemWidget(item, 3).text()
            plotWidget: HistogramPlotWidget = self.mTree.itemWidget(item, 4)
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

    def onOkClicked(self):
        self.onApplyClicked()
        self.close()

    def onCancelClicked(self):
        self.layer.setRenderer(self.rendererBackup)
        self.layer.triggerRepaint()
        self.close()

    def onApplyClicked(self):
        self.layer.setRenderer(self.currentRenderer())
        self.layer.triggerRepaint()

    def styleFilename(self):
        return splitext(self.layer.source())[0] + '.qml.pkl'

    def onSaveStyleClicked(self):
        renderer = self.currentRenderer()
        Utils.pickleDump(renderer.categories, self.styleFilename())

    def onLoadStyleClicked(self):
        self.removeAllItems()
        categories: Categories = Utils.pickleLoad(self.styleFilename())
        for category in categories:
            self.addItem(category.value, QColor(category.color), category.name, False)
        self.onLiveUpdate()

    def onLiveUpdate(self):
        if self.mLiveUpdate.isChecked():
            self.onApplyClicked()

    def onMapCanvasExtentsChanged(self):
        extent = Utils.layerExtentInMapCanvas(self.layer, self.mapCanvas)
        for checked, bandNo, color, name, plotWidget in self.currentItemValues():
            # clear current plot
            plotWidget.clear()
            plotWidget.getAxis('bottom').setPen('#000000')
            plotWidget.getAxis('left').setPen('#000000')

            # make new plot
            if checked:
                provider: QgsRasterDataProvider = self.layer.dataProvider()
                minimum = self.mMin.value()
                maximum = self.mMax.value()
                binCount = maximum - minimum
                rasterHistogram: QgsRasterHistogram = provider.histogram(
                    bandNo, binCount, minimum / 100., maximum / 100., extent
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
        # QGraphicsView.setMaximumHeight(10)
        self.getPlotItem().hideAxis('bottom')
        self.getPlotItem().hideAxis('left')
        #self.getPlotItem().setXRange(0, 100, padding=0)
        #self.getPlotItem().autoRange()

    def mousePressEvent(self, ev):
        self.autoRange()

    def mouseMoveEvent(self, ev):
        self.autoRange()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.autoRange()
        print(event.x(), event.y())
