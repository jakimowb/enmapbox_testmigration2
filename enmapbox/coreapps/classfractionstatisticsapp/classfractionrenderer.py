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
