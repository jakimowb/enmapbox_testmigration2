from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple, Sequence, Union
from uuid import uuid4

import numpy as np
from osgeo import gdal

from hubdsm.core.gdalband import GdalBand
from hubdsm.core.grid import Grid


@dataclass
class Band(object):
    """Raster band."""
    name: str
    filename: str
    number: int
    mask: Optional[Mask]
    _gdalBand: Optional[GdalBand]

    def __post_init__(self):
        assert isinstance(self.name, str)
        assert isinstance(self.filename, str)
        assert isinstance(self.number, int) and self.number >= 1
        assert isinstance(self.mask, (Mask, type(None)))
        assert isinstance(self._gdalBand, (GdalBand, type(None)))

    @staticmethod
    def fromGdalBand(gdalBand: GdalBand):
        band = Band(
            name=gdalBand.description, filename=gdalBand.gdalDataset.GetDescription(), number=gdalBand.number,
            mask=None, _gdalBand=gdalBand
        )
        return band

    @property
    def gdalBand(self) -> GdalBand:
        '''Return GdalBand instance.'''
        if self._gdalBand is None:
            self._gdalBand = GdalBand.open(filename=self.filename, number=self.number)
        return self._gdalBand

    def rename(self, name) -> Band:
        '''Return band with new name.'''
        return Band(name=name, filename=self.filename, number=self.number, mask=self.mask, _gdalBand=self._gdalBand)

    def withMask(self, mask: Mask) -> Band:
        '''Return band with mask.'''
        return Band(
            name=self.name, filename=self.filename, number=self.number, mask=mask,
            _gdalBand=self._gdalBand
        )

    def readAsArray(self, grid: Grid = None, gdalResamplingAlgorithm: int = gdal.GRA_NearestNeighbour) -> np.ndarray:
        '''Return 2d array.'''
        return self.gdalBand.readAsArray(grid=grid, gra=gdalResamplingAlgorithm)

    def readAsMaskArray(
            self, grid: Grid = None, noDataValue: Union[int, float] = None,
            gdalResamplingAlgorithm=gdal.GRA_NearestNeighbour
    ) -> np.ndarray:
        '''Return 2d mask array.'''
        if grid is None:
            grid = self.gdalBand.grid
        if noDataValue is None:
            noDataValue = self.gdalBand.noDataValue
        array = self.readAsArray(grid=grid, gdalResamplingAlgorithm=gdalResamplingAlgorithm)
        if noDataValue is np.nan:
            maskArray1 = np.logical_not(np.isnan(array))
        elif noDataValue is None:
            maskArray1 = np.full_like(array, fill_value=True, dtype=np.bool)
        else:
            maskArray1 = array != noDataValue
        if self.mask is not None:
            maskArray2 = self.mask.readAsArray(grid=grid, gdalResamplingAlgorithm=gdalResamplingAlgorithm)
            maskArray = np.logical_and(maskArray1, maskArray2)
        else:
            maskArray = maskArray1
        return maskArray


#    def warp(self, filename: str = None, grid: Grid = None):
#        key128bit = uuid4().hex
#        filename = f'/vsimem/hubdsm.core.band.Band.warp/{key128bit}.vrt'
#        gdal.Translate(destName=filename, srcDS=)
#        return Band(name=self.name, filename=filename, number=1, noDataValue=self.noDataValue, gra=gra, gdt=self.gdt)

@dataclass
class Mask(object):
    band: Band
    noDataValue: Union[int, float] = None
    invert: bool = False

    def __post_init__(self):
        assert isinstance(self.band, Band)
        assert isinstance(self.invert, bool)
        assert isinstance(self.noDataValue, (int, float, type(None)))

    def readAsArray(self, grid: Grid = None, gdalResamplingAlgorithm: int = gdal.GRA_NearestNeighbour) -> np.ndarray:
        noDataValue = self.noDataValue
        if noDataValue is None:
            noDataValue = self.band.gdalBand.noDataValue
            if noDataValue is None:
                noDataValue = 0
        array = self.band.readAsMaskArray(grid=grid, noDataValue=noDataValue,
            gdalResamplingAlgorithm=gdalResamplingAlgorithm
        )
        if self.invert:
            array = np.logical_not(array)
        return array
