# from __future__ import annotations
from dataclasses import dataclass, field
from os import makedirs
from os.path import splitext, isabs, abspath, exists, dirname
from typing import List, Optional, Type

import numpy as np
from osgeo import gdal, gdal_array
from osgeo.gdal_array import NumericTypeCodeToGDALTypeCode

from hubdsm.core.gdalraster import GdalRaster
from hubdsm.core.grid import Grid
from hubdsm.core.shape import RasterShape


@dataclass
class GdalRasterDriver(object):
    name: str
    options: List[str] = field(default_factory=list)

    def __post_init__(self):
        assert self.gdalDriver is not None
        assert isinstance(self.options, list)

    @classmethod
    def fromFilename(cls, filename: Optional[str]) -> 'GdalRasterDriver':

        if filename is None or filename == '':
            return MEM_DRIVER

        ext = splitext(filename)[1][1:].lower()
        if ext in ['bsq', 'sli', 'esl']:
            return ENVI_BSQ_DRIVER
        if ext == 'bil':
            return ENVI_BIL_DRIVER
        if ext == 'bip':
            return ENVI_BIP_DRIVER
        if ext in ['tif', 'tiff']:
            return GTIFF_DRIVER
        if ext == 'img':
            return ERDAS_DRIVER
        if ext == 'vrt':
            return VRT_DRIVER
        return ENVI_BSQ_DRIVER

    @property
    def gdalDriver(self) -> gdal.Driver:
        """Returns the GDAL driver object."""
        gdalDriver = gdal.GetDriverByName(self.name)
        assert gdalDriver is not None
        return gdalDriver

    def create(
            self, grid: Grid, bands=1, gdalDataType: int = gdal.GDT_Float32, filename: str = None, gco: List[str] = None
    ) -> GdalRaster:
        """Create new GDAL raster."""

        assert isinstance(grid, Grid)
        assert isinstance(bands, int) and bands >= 0
        filename = self.prepareCreation(filename)
        if gco is None:
            gco = self.options
        assert isinstance(gco, list)
        utf8_path = filename
        ysize, xsize = grid.shape
        gdalDataset = self.gdalDriver.Create(utf8_path, xsize, ysize, bands, gdalDataType, gco)
        gdalDataset.SetProjection(grid.projection.wkt)
        gdalDataset.SetGeoTransform(grid.geoTransform.gdalGeoTransform())
        return GdalRaster(gdalDataset=gdalDataset)

    def createFromArray(
            self, array: np.ndarray, grid: Optional[Grid] = None, filename: str = None,
            gco: List[str] = None
    ) -> GdalRaster:
        """Create new GDAL raster from array."""
        assert isinstance(array, np.ndarray)
        assert array.ndim == 3
        gdalDataType = NumericTypeCodeToGDALTypeCode(array.dtype)
        shape = RasterShape(*array.shape)
        gdalRaster = self.createFromShape(shape=shape, gdalDataType=gdalDataType, grid=grid, filename=filename, gco=gco)
        gdalRaster.writeArray(array=array, grid=grid)
        return gdalRaster

    def createFromShape(
            self, shape: RasterShape, gdalDataType: int = gdal.GDT_Float32, grid: Grid = None, filename: str = None,
            gco: List[str] = None
    ) -> GdalRaster:
        """Create new GDAL raster from array shape."""
        assert isinstance(shape, RasterShape)
        if grid is None:
            grid = Grid.makePseudoGridFromShape(shape=shape.gridShape)
        gdalRaster = self.create(grid=grid, bands=shape.z, gdalDataType=gdalDataType, filename=filename, gco=gco)
        return gdalRaster

    def delete(self, filename: str):
        """Delete GDAL raster file on disk or unlink on /vsimem/."""
        if filename.startswith('/vsimem/'):
            gdal.Unlink(filename)
        if exists(filename):
            self.gdalDriver.Delete(filename)

    def prepareCreation(self, filename: str) -> str:
        """Return absolute filename and create root folder/subfolders if not existing."""

        if filename is None or filename == '':
            return ''

        if self == MEM_DRIVER:
            return ''

        assert isinstance(filename, str)
        if filename.startswith('/vsimem/'):
            self.delete(filename)
            return filename

        if not isabs(filename):
            filename = abspath(filename)
        if not exists(dirname(filename)):
            makedirs(dirname(filename))
        self.delete(filename=filename)
        return filename


MEM_DRIVER = GdalRasterDriver(name='MEM')
VRT_DRIVER = GdalRasterDriver(name='VRT')
ENVI_DRIVER = GdalRasterDriver(name='ENVI')
ENVI_BSQ_DRIVER = GdalRasterDriver(name='ENVI', options=['INTERLEAVE=BSQ'])
ENVI_BIL_DRIVER = GdalRasterDriver(name='ENVI', options=['INTERLEAVE=BIL'])
ENVI_BIP_DRIVER = GdalRasterDriver(name='ENVI', options=['INTERLEAVE=BIP'])
GTIFF_DRIVER = GdalRasterDriver(name='GTiff', options=['INTERLEAVE=BAND'])
ERDAS_DRIVER = GdalRasterDriver(name='HFA')
