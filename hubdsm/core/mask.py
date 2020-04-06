from dataclasses import dataclass

import numpy as np
from osgeo import gdal

from hubdsm.core.grid import Grid


@dataclass
class Mask(object):
    band: 'Band'
    invert: bool = False

    def __post_init__(self):
        from hubdsm.core.band import Band
        assert isinstance(self.band, Band)
        assert isinstance(self.invert, bool)

    def withInvert(self, invert: bool):
        return Mask(band=self.band, invert=invert)

    def readAsArray(self, grid: Grid = None, gdalResamplingAlgorithm: int = gdal.GRA_NearestNeighbour) -> np.ndarray:
        if self.band.gdalBand.noDataValue is None:
            array = self.band.readAsArray(grid=grid, gdalResamplingAlgorithm=gdalResamplingAlgorithm) != 0
        else:
            array = self.band.readAsMaskArray(grid=grid, gdalResamplingAlgorithm=gdalResamplingAlgorithm)
        if self.invert:
            array = np.logical_not(array)
        assert array.dtype == np.bool
        return array