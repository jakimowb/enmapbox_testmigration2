from __future__ import annotations
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
    def fromFilename(cls, filename: Optional[str]) -> GdalRasterDriver:

        if filename is None or filename == '':
            return MEM_DRIVER

        ext = splitext(filename)[1][1:].lower()
        if ext in ['bsq', 'sli', 'esl']:
            return ENVI_BSQ__DRIVER
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
        return ENVI_BSQ__DRIVER

    @property
    def gdalDriver(self) -> gdal.Driver:
        """Returns the GDAL driver object."""
        gdalDriver = gdal.GetDriverByName(self.name)
        assert gdalDriver is not None
        return gdalDriver

    def create(
            self, grid: Grid, bands=1, gdalDataType: int = gdal.GDT_Float32, filename: str = None, options: List[str] = None
    ) -> GdalRaster:
        """Create new GDAL raster."""

        assert isinstance(grid, Grid)
        assert isinstance(bands, int) and bands >= 0
        filename = self.prepareCreation(filename)
        if options is None:
            options = self.options
        assert isinstance(options, list)
        utf8_path = filename
        ysize, xsize = grid.shape
        gdalDataset = self.gdalDriver.Create(utf8_path, xsize, ysize, bands, gdalDataType, options)
        gdalDataset.SetProjection(grid.projection.wkt)
        gdalDataset.SetGeoTransform(grid.geoTransform.gdalGeoTransform())
        return GdalRaster(gdalDataset=gdalDataset)

    def createFromArray(
            self, array: np.ndarray, grid: Optional[Grid] = None, filename: str = None,
            options: List[str] = None
    ) -> GdalRaster:
        """Create new GDAL raster from array."""
        assert isinstance(array, np.ndarray)
        assert array.ndim == 3
        if grid is None:
            grid = Grid.makePseudoGridFromArray(array=array)
        bands = len(array)
        gdalDataType = NumericTypeCodeToGDALTypeCode(array.dtype)
        gdalRaster = self.create(grid=grid, bands=bands, gdalDataType=gdalDataType, filename=filename, options=options)
        gdalRaster.writeArray(array=array, grid=grid)
        return gdalRaster

    def createFromShape(
            self, shape: RasterShape, gdalDataType: int = gdal.GDT_Float32, grid: Grid = None, filename: str = None,
            options: List[str] = None
    ) -> GdalRaster:
        """Create new GDAL raster from array shape."""
        assert isinstance(shape, RasterShape)
        if grid is None:
            grid = Grid.makePseudoGridFromShape(shape=shape.gridShape)
        gdalRaster = self.create(grid=grid, bands=shape.z, gdalDataType=gdalDataType, filename=filename, options=options)
        return gdalRaster

    def delete(self, filename: str, raiseError=False):
        """Delete GDAL raster file on disk or unlink on /vsimem/."""
        if filename.startswith('/vsimem/'):
            gdal.Unlink(filename)
        if exists(filename):
            errorCode = self.gdalDriver.Delete(filename)
            if raiseError:
                assert errorCode == 0, f'gdal.Driver.Delete error code: {errorCode}'

    def prepareCreation(self, filename: str) -> str:
        """Returns absolute filename and creates root folders if not existing."""

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


class GeoTiffCreationOption(object):
    class INTERLEAVE(object):
        BAND = 'INTERLEAVE=BAND'
        PIXEL = 'INTERLEAVE=PIXEL'

    class TILED(object):
        YES = 'TILED=YES'
        NO = 'TILED=NO'

    @staticmethod
    def BLOCKXSIZE(n=256):
        return 'BLOCKXSIZE={}'.format(n)

    @staticmethod
    def BLOCKYSIZE(n=256):
        return 'BLOCKYSIZE={}'.format(n)

    @staticmethod
    def NBITS(n):
        return 'NBITS={}'.format(n)

    class PREDICTOR(object):
        NONE = 'PREDICTOR=1'
        HorizontalDifferencing = 'PREDICTOR=2'
        FloatingPoint = 'PREDICTOR=3'

    class SPARSE_OK(object):
        TRUE = 'SPARSE_OK=TRUE'
        FALSE = 'SPARSE_OK=FALSE'

    @staticmethod
    def JPEG_QUALITY(n=75):
        assert 1 <= n <= 100
        return 'JPEG_QUALITY={}'.format(n)

    @staticmethod
    def ZLEVEL(n=6):
        assert 1 <= n <= 9
        return 'ZLEVEL={}'.format(n)

    @staticmethod
    def ZSTD_LEVEL(n=9):
        assert 1 <= n <= 22
        return 'ZSTD_LEVEL={}'.format(n)

    @staticmethod
    def MAX_Z_ERROR(threshold=0):
        assert threshold >= 0
        return 'MAX_Z_ERROR={}'.format(threshold)

    @staticmethod
    def WEBP_LEVEL(n=75):
        assert 1 <= n <= 100
        return 'WEBP_LEVEL={}'.format(n)

    class WEBP_LOSSLESS(object):
        TRUE = 'WEBP_LOSSLESS=TRUE'
        FALSE = 'WEBP_LOSSLESS=FALSE'

    class PHOTOMETRIC(object):
        MINISBLACK = 'PHOTOMETRIC=MINISBLACK'
        MINISWHITE = 'PHOTOMETRIC=MINISWHITE'
        RGB = 'PHOTOMETRIC=RGB'
        CMYK = 'PHOTOMETRIC=CMYK'
        YCBCR = 'PHOTOMETRIC=YCBCR'
        CIELAB = 'PHOTOMETRIC=CIELAB'
        ICCLAB = 'PHOTOMETRIC=ICCLAB'
        ITULAB = 'PHOTOMETRIC=ITULAB'

    class ALPHA(object):
        YES = 'ALPHA=YES'
        NON_PREMULTIPLIED = 'ALPHA=NON-PREMULTIPLIED'
        PREMULTIPLIED = 'ALPHA=PREMULTIPLIED'
        UNSPECIFIED = 'ALPHA=UNSPECIFIED'

    class PROFILE(object):
        GDALGeoTIFF = 'PROFILE=GDALGeoTIFF'
        GeoTIFF = 'PROFILE=GeoTIFF'
        BASELINE = 'PROFILE=BASELINE'

    class BIGTIFF(object):
        YES = 'BIGTIFF=YES'
        NO = 'BIGTIFF=NO'
        IF_NEEDED = 'BIGTIFF=IF_NEEDED'
        IF_SAFER = 'BIGTIFF=IF_SAFER'

    class PIXELTYPE(object):
        DEFAULT = 'PIXELTYPE=DEFAULT'
        SIGNEDBYTE = 'PIXELTYPE=SIGNEDBYTE'

    class COPY_SRC_OVERVIEWS(object):
        YES = 'COPY_SRC_OVERVIEWS=YES'
        NO = 'COPY_SRC_OVERVIEWS=NO'

    class GEOTIFF_KEYS_FLAVOR(object):
        STANDARD = 'GEOTIFF_KEYS_FLAVOR=STANDARD'
        ESRI_PE = 'GEOTIFF_KEYS_FLAVOR=ESRI_PE'

    @staticmethod
    def NUM_THREADS(n='ALL_CPUS'):
        return 'NUM_THREADS={}'.format(n)

    class COMPRESS(object):
        JPEG = 'COMPRESS=JPEG'
        LZW = 'COMPRESS=LZW'
        PACKBITS = 'COMPRESS=JPEG'
        DEFLATE = 'COMPRESS=PACKBITS'
        CCITTRLE = 'COMPRESS=CCITTRLE'
        CCITTFAX3 = 'COMPRESS=CCITTFAX3'
        CCITTFAX4 = 'COMPRESS=CCITTFAX4'
        LZMA = 'COMPRESS=LZMA'
        ZSTD = 'COMPRESS=ZSTD'
        LERC = 'COMPRESS=LERC'
        LERC_DEFLATE = 'COMPRESS=LERC_DEFLATE'
        LERC_ZSTD = 'COMPRESS=LERC_ZSTD'
        WEBP = 'COMPRESS=WEBP'
        NONE = 'COMPRESS=NONE'


class EnviCreationOption(object):
    class INTERLEAVE(object):
        BSQ = 'INTERLEAVE=BSQ'
        BIL = 'INTERLEAVE=BIL'
        BIP = 'INTERLEAVE=BIP'

    class SUFFIX(object):
        REPLACE = 'SUFFIX=REPLACE'
        ADD = 'SUFFIX=ADD'


MEM_DRIVER = GdalRasterDriver(name='MEM')
VRT_DRIVER = GdalRasterDriver(name='VRT')
ENVI_DRIVER = GdalRasterDriver(name='ENVI')
ENVI_BSQ__DRIVER = GdalRasterDriver(name='ENVI', options=[EnviCreationOption.INTERLEAVE.BSQ])
ENVI_BIL_DRIVER = GdalRasterDriver(name='ENVI', options=[EnviCreationOption.INTERLEAVE.BIL])
ENVI_BIP_DRIVER = GdalRasterDriver(name='ENVI', options=[EnviCreationOption.INTERLEAVE.BIP])
GTIFF_DRIVER = GdalRasterDriver(name='GTiff', options=[GeoTiffCreationOption.INTERLEAVE.BAND])
ERDAS_DRIVER = GdalRasterDriver(name='HFA')
