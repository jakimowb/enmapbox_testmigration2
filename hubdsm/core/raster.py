# from __future__ import annotations
from dataclasses import dataclass
from os.path import basename
from typing import Tuple, List, Sequence, Union, Iterator

import numpy as np
from osgeo import gdal

from hubdsm.core.band import Band
from hubdsm.core.mask import Mask
from hubdsm.core.gdalband import GdalBand
from hubdsm.core.gdalraster import GdalRaster
from hubdsm.core.grid import Grid
from hubdsm.core.gdalrasterdriver import GdalRasterDriver


@dataclass(frozen=True)
class Raster(object):
    """Raster."""
    name: str
    bands: Tuple[Band, ...]
    grid: Grid

    def __post_init__(self):
        assert isinstance(self.name, str)
        assert isinstance(self.bands, tuple)
        assert isinstance(self.grid, Grid)
        for band in self.bands:
            assert isinstance(band, Band)
        assert isinstance(self.grid, Grid)
        # assert len(self.bandNames) == len(set(self.bandNames)), 'each band name must be unique'

    @classmethod
    def open(cls, filenameOrGdalRaster: Union[str, GdalRaster]) -> 'Raster':
        if isinstance(filenameOrGdalRaster, str):
            gdalRaster = GdalRaster.open(filename=filenameOrGdalRaster)
        elif isinstance(filenameOrGdalRaster, GdalRaster):
            gdalRaster = filenameOrGdalRaster
        else:
            raise ValueError('filenameOrGdalRaster')
        return cls.fromGdalRaster(gdalRaster=gdalRaster)

    @staticmethod
    def fromGdalRaster(gdalRaster: GdalRaster) -> 'Raster':
        bands = tuple(Band.fromGdalBand(gdalBand=gdalBand) for gdalBand in gdalRaster.bands)
        return Raster(name=gdalRaster.filename, bands=bands, grid=gdalRaster.grid)

    @property
    def bandNames(self) -> Tuple[str, ...]:
        return tuple(band.name for band in self.bands)

    def band(self, number: int) -> Band:
        return self.bands[number - 1]

    def select(
            self, selectors: Sequence[Union[str, int]], newBandNames: Sequence[str] = None,
            newRasterName: str = None
    ) -> 'Raster':

        # derives band numbers and new names
        numbers = list()
        bandNames = self.bandNames
        assert isinstance(selectors, (list, tuple))
        for selector in selectors:
            if isinstance(selector, int):
                assert 1 <= selector <= len(self.bands)
                number = selector
            elif isinstance(selector, str):
                number = bandNames.index(selector) + 1
            else:
                raise ValueError(f'unexpected selector "{selector}"')
            numbers.append(number)
        if newBandNames is None:
            newBandNames = (self.bands[number - 1].name for number in numbers)
        else:
            assert len(selectors) == len(newBandNames)
        if newRasterName is None:
            newRasterName = self.name

        # subset bands
        bands = tuple(self.bands[number - 1].rename(name) for number, name in zip(numbers, newBandNames))
        raster = Raster(name=newRasterName, bands=bands, grid=self.grid)
        return raster

    def rename(self, name: str = None, bandNames: Sequence[str] = None) -> 'Raster':
        """Rename raster and raster bands."""
        if name is None:
            name = self.name
        if bandNames is None:
            bandNames = self.bandNames
        assert len(bandNames) == len(self.bands)
        selectors = list(range(1, len(self.bands) + 1))
        raster = self.select(selectors=selectors, newBandNames=bandNames, newRasterName=name)
        return raster

    def addBands(self, raster: 'Raster') -> 'Raster':
        """Return raster containing all bands copied from the first raster and bands from the second input."""
        return Raster(name=self.name, bands=self.bands + raster.bands, grid=self.grid)

    def withMask(self, raster: 'Raster', invert=False) -> 'Raster':
        """Return raster with new mask raster."""
        if len(self.bands) == len(raster.bands):
            maskBands = raster.bands
        elif len(raster.bands) == 1:
            maskBands = raster.bands * len(self.bands)
        else:
            raise ValueError(f'expected raster with 1 or {len(self.bands)} bands')

        bands = tuple(
            band.withMask(mask=Mask(band=maskBand, invert=invert)) for band, maskBand in zip(self.bands, maskBands)
        )
        return Raster(name=self.name, bands=bands, grid=self.grid)

    def withName(self, name: str) -> 'Raster':
        return Raster(name=name, bands=self.bands, grid=self.grid)

    def readAsArray(self, grid: Grid = None, gra: int = None) -> np.ndarray:
        '''Return 3d array.'''
        return np.array(list(self.iterArrays(grid=grid, gra=gra)))

    def readAsMaskArray(self, grid: Grid = None, gra: int = None) -> np.ndarray:
        '''Return 3d mask array.'''
        return np.array(list(self.iterMaskArrays(grid=grid, gra=gra)))

    def iterArrays(self, grid: Grid = None, gra: int = None) -> Iterator[np.ndarray]:
        '''Iterates over 2d band arrays.'''
        if grid is None:
            grid = self.grid
        for band in self.bands:
            yield band.readAsArray(grid=grid, gra=gra)

    def iterMaskArrays(self, grid: Grid = None, gra: int = None) -> Iterator[np.ndarray]:
        '''Iterates over 2d mask band arrays.'''
        if grid is None:
            grid = self.grid
        for band in self.bands:
            yield band.readAsMaskArray(grid=grid, gra=gra)

    # def warp(self, grid: Grid = None) -> Raster:
    #    if grid is None:
    #        grid = self.grid
    #    bands = list()
    #    for band in self.bands:
    #        bands.append(band.warp(grid=grid))
    #    bands = tuple(bands)
    #    return Raster(name=self.name, bands=bands, grid=grid)
