from PyQt5.QtCore import QSize, QSizeF, Qt
from qgis._core import QgsRasterLayer, QgsRasterDataProvider, QgsRectangle

from typeguard import typechecked

from enmapboxprocessing.extentwalker import ExtentWalker


@typechecked
class GridWalker(ExtentWalker):

    def __init__(self, extent: QgsRectangle, blockSizeX: int, blockSizeY: int, pixelSizeX: float, pixelSizeY: float):
        blockSizeX = float(blockSizeX * pixelSizeX)
        blockSizeY = float(blockSizeY * pixelSizeY)
        super().__init__(extent=extent, blockSizeX=blockSizeX, blockSizeY=blockSizeY)
