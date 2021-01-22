import math

from PyQt5.QtCore import QSizeF, QRectF
from qgis._core import QgsRectangle, QgsPointXY

from typeguard import typechecked


@typechecked
class ExtentWalker(object):

    def __init__(self, extent: QgsRectangle, blockSizeX: float, blockSizeY: float):
        self.extent = extent
        self.blockSizeX = blockSizeX
        self.blockSizeY = blockSizeY

    def __iter__(self):
        for y in range(self.nBlocksY()):
            for x in range(self.nBlocksX()):
                left = self.extent.xMinimum() + x * self.blockSizeX
                top = self.extent.yMaximum() - y * self.blockSizeY
                right = left + self.blockSizeX
                bottom = top - self.blockSizeY
                blockExtent = QgsRectangle(left, bottom, right, top).intersect(self.extent)
                yield blockExtent

    def nBlocksX(self) -> int:
        return math.ceil(self.extent.width() / self.blockSizeX)

    def nBlocksY(self) -> int:
        return math.ceil(self.extent.height() / self.blockSizeY)
