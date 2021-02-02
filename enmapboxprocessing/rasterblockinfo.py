from typing import NamedTuple

from qgis._core import QgsRectangle


class RasterBlockInfo(NamedTuple):
    extent: QgsRectangle
    xOffset: int
    yOffset: int
    width: int
    height: int