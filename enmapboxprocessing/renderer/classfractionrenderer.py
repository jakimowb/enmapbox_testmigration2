import traceback
from copy import deepcopy
from random import randint
from typing import List

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QToolButton, QTreeWidget, QTreeWidgetItem, QLineEdit, QCheckBox, \
    QApplication, QMessageBox, QMainWindow
from PyQt5.uic import loadUi
from qgis._core import QgsRasterRenderer, QgsRasterInterface, QgsRectangle, QgsRasterBlockFeedback, QgsRasterBlock, \
    Qgis, QgsRasterLayer
from qgis._gui import QgsRasterBandComboBox, QgsColorButton

from enmapbox.externals.qps.layerproperties import rendererFromXml
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
            weight = Utils.qgsRasterBlockToNumpyArray(block)  # note that we assume weigt
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
        outarray = (rgba[0] << 16) + (rgba[1] << 8) + rgba[2] + (rgba[3] << 24)  # re-compose channels to int
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

    mOk: QToolButton
    mCancel: QToolButton
    mApply: QToolButton

    def __init__(self, layer: QgsRasterLayer, parent=None):
        QWidget.__init__(self, parent)
        loadUi(__file__.replace('.py', '.ui'), self)
        self.layer = layer
        self.rendererBackup = layer.renderer().clone()

        self.mAdd.clicked.connect(lambda: self.addItem())
        self.mRemove.clicked.connect(self.removeItem)
        self.mDeleteAll.clicked.connect(self.mTree.clear)
        self.mClassify.clicked.connect(self.classify)
        self.mPasteStyle.clicked.connect(self.pasteStyle)

        self.mOk.clicked.connect(self.onOkClicked)
        self.mCancel.clicked.connect(self.onCancelClicked)
        self.mApply.clicked.connect(self.onApplyClicked)

        if isinstance(self.rendererBackup, ClassFractionRenderer):
            for category in self.rendererBackup.categories:
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

    def currentCategories(self) -> Categories:
        categories = list()
        for i in range(self.mTree.topLevelItemCount()):
            item: QTreeWidgetItem = self.mTree.topLevelItem(i)
            checkWidget: QCheckBox = self.mTree.itemWidget(item, 0)
            if not checkWidget.isChecked():
                continue
            bandWidget: QgsRasterBandComboBox = self.mTree.itemWidget(item, 1)
            colorWidget: QgsColorButton = self.mTree.itemWidget(item, 2)
            labelWidget: QLineEdit = self.mTree.itemWidget(item, 3)
            categories.append(Category(bandWidget.currentBand(), labelWidget.text(), colorWidget.color().name()))
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

    def onLiveUpdate(self):
        if self.mLiveUpdate.isChecked():
            self.onApplyClicked()
