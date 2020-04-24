# from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Union, Any, Dict, Iterable
from os.path import exists

import numpy as np
from osgeo import gdal

from hubdsm.core.error import ProjectionMismatchError
from hubdsm.core.gdalband import GdalBand
from hubdsm.core.geotransform import GeoTransform, GdalGeoTransform
from hubdsm.core.grid import Grid
from hubdsm.core.gdalmetadatavalueformatter import GdalMetadataValueFormatter
from hubdsm.core.projection import Projection
from hubdsm.core.shape import RasterShape, GridShape


@dataclass(frozen=True)
class GdalRaster(object):
    """GDAL Raster dataset."""
    gdalDataset: gdal.Dataset

    def __post_init__(self):
        assert isinstance(self.gdalDataset, gdal.Dataset), repr(self.gdalDataset)

    def __del__(self):
        self.flushCache()

    @property
    def geoTransform(self) -> GeoTransform:
        gdalGeoTransform = GdalGeoTransform(*self.gdalDataset.GetGeoTransform())
        return GeoTransform.fromGdalGeoTransform(gdalGeoTransform)

    @property
    def shape(self) -> RasterShape:
        return RasterShape(
            x=self.gdalDataset.RasterXSize, y=self.gdalDataset.RasterYSize, z=self.gdalDataset.RasterCount
        )

    @property
    def grid(self) -> Grid:
        shape = GridShape(x=self.gdalDataset.RasterXSize, y=self.gdalDataset.RasterYSize)
        projection = Projection(wkt=str(self.gdalDataset.GetProjection()))
        return Grid.fromGeoTransform(geoTransform=self.geoTransform, shape=shape, projection=projection)

    @property
    def driver(self) -> 'GdalRasterDriver':
        from hubdsm.core.gdalrasterdriver import GdalRasterDriver
        gdalDriver: gdal.Driver = self.gdalDataset.GetDriver()
        return GdalRasterDriver(name=gdalDriver.ShortName)

    @staticmethod
    def open(filenameOrGdalDataset: Union[str, gdal.Dataset], access: int = gdal.GA_ReadOnly) -> 'GdalRaster':

        if isinstance(filenameOrGdalDataset, str):
            assert exists(filenameOrGdalDataset) or filenameOrGdalDataset.startswith('/vsimem/')
            gdalDataset: gdal.Dataset = gdal.Open(filenameOrGdalDataset, access)
        elif isinstance(filenameOrGdalDataset, gdal.Dataset):
            gdalDataset = filenameOrGdalDataset
        else:
            raise ValueError(filenameOrGdalDataset)

        assert gdalDataset is not None
        assert gdalDataset.GetProjection() != ''
        return GdalRaster(gdalDataset=gdalDataset)

    @property
    def filenames(self) -> str:
        """Return filenames list."""
        filenames = self.gdalDataset.GetFileList()
        if filenames is None:
            filenames = []
        return filenames

    @property
    def filename(self) -> str:
        """Return filename."""
        return self.gdalDataset.GetDescription()

    def setGrid(self, grid: Grid):
        """Set grid."""
        assert isinstance(grid, Grid)
        self.gdalDataset.SetGeoTransform(grid.geoTransform.gdalGeoTransform())
        self.gdalDataset.SetProjection(grid.projection.wkt)

    def band(self, number) -> GdalBand:
        """Return the band dataset."""
        assert number >= 1
        return GdalBand(gdalDataset=self.gdalDataset, gdalBand=self.gdalDataset.GetRasterBand(number), number=number)

    @property
    def bands(self) -> Iterable[GdalBand]:
        """Iterate over all bands."""
        for i in range(self.shape.z):
            yield self.band(number=i + 1)

    def readAsArray(self, grid: Optional[Grid] = None, gra: int = None) -> np.ndarray:
        """Read as 3d array."""

        if gra is None:
            gra = gdal.GRA_NearestNeighbour

        if grid is None:
            array = self.gdalDataset.ReadAsArray()
        else:
            assert isinstance(grid, Grid)
            if self.grid.projection != grid.projection:
                raise ProjectionMismatchError()
            resolution = self.grid.resolution
            extent = self.grid.extent
            xoff = int(round((grid.extent.xmin - extent.xmin) / resolution.x, 0))
            yoff = int(round((extent.ymax - grid.extent.ymax) / resolution.y, 0))
            xsize = int(round((grid.extent.xmax - grid.extent.xmin) / resolution.x, 0))
            ysize = int(round((grid.extent.ymax - grid.extent.ymin) / resolution.y, 0))
            buf_ysize, buf_xsize = grid.shape
            array = self.gdalDataset.ReadAsArray(
                xoff=xoff, yoff=yoff, xsize=xsize, ysize=ysize, buf_xsize=buf_xsize, buf_ysize=buf_ysize,
                resample_alg=gra)

        if array.ndim == 2:
            array = np.expand_dims(array, 0)
        assert array.ndim == 3
        return array

    def writeArray(self, array: np.ndarray, grid: Optional[Grid] = None):
        """Write 3d array."""

        assert isinstance(array, np.ndarray)
        assert array.ndim == 3
        assert len(array) == self.shape.z
        for band, bandArray in zip(self.bands, array):
            band.writeArray(bandArray, grid=grid)

    def setNoDataValue(self, value: Union[int, float]):
        """Set no data value to all bands."""
        for band in self.bands:
            band.setNoDataValue(value=value)

    def flushCache(self):
        """Flush the cache."""
        self.gdalDataset.FlushCache()

    def metadataDomainList(self) -> List[str]:
        """Returns the list of metadata domain names."""
        domainList = self.gdalDataset.GetMetadataDomainList()
        if domainList is None:
            return list()
        return domainList

    def metadataItem(
            self, key: str, domain: str, dtype: Union[str, float, int] = None, required=False, default=None):
        """Return (type-casted) metadata value.
        If metadata item is missing, but not required, return the default value."""

        if dtype is None:
            dtype = str
        key = key.replace(' ', '_')
        gdalString = self.gdalDataset.GetMetadataItem(key, domain)
        if gdalString is None:
            assert not required, f'missing metadata item: {key} in {domain}'
            return default
        return GdalMetadataValueFormatter.stringToValue(gdalString, dtype=dtype)

    def metadataDomain(self, domain=''):
        """Returns the metadata dictionary for the given ``domain``."""
        values = dict()
        for key in self.gdalDataset.GetMetadata(domain):
            key = key.replace('_', ' ')
            values[key] = self.metadataItem(key=key, domain=domain)
        return values

    @property
    def metadataDict(self):
        """Returns the metadata dictionary for all domains."""
        values = dict()
        for domain in self.metadataDomainList():
            values[domain] = self.metadataDomain(domain=domain)
        return values

    def setMetadataItem(self, key: str, value: Union[Any, List[Any]], domain: str = ''):
        """Set metadata item."""
        if value is None:
            return
        key = key.replace(' ', '_').strip()
        gdalString = GdalMetadataValueFormatter.valueToString(value)
        self.gdalDataset.SetMetadataItem(key, gdalString, domain)

    def setMetadataDomain(self, values: Dict[str, Union[Any, List[Any]]], domain: str):
        """Set the metadata domain."""
        assert isinstance(values, dict)
        for key, value in values.items():
            self.setMetadataItem(key=key, value=value, domain=domain)

    def setMetadataDict(self, metadataDict=Dict[str, Dict[str, Union[Any, List[Any]]]]):
        """Set the metadata."""
        assert isinstance(metadataDict, dict)
        for domain, metadataDomain in metadataDict.items():
            self.setMetadataDomain(values=metadataDomain, domain=domain)

    def translate(
            self, grid: Grid = None, filename: str = None, driver: 'GdalRasterDriver' = None, gco: List[str] = None,
            gra: int = None, **kwargs
    ):
        '''Return translated raster.'''
        from hubdsm.core.gdalrasterdriver import GdalRasterDriver

        if grid is None:
            grid = self.grid

        if driver is None:
            driver = GdalRasterDriver.fromFilename(filename=filename)

        assert isinstance(grid, Grid)
        assert self.grid.projection == grid.projection
        assert isinstance(driver, GdalRasterDriver)
        if gco is None:
            gco = driver.options
        assert isinstance(gco, list)

        filename = driver.prepareCreation(filename)

        ul = grid.extent.ul
        lr = grid.extent.lr
        xRes, yRes = grid.resolution.x, grid.resolution.y

        options = gdal.TranslateOptions(
            format=driver.name, creationOptions=gco,
            resampleAlg=gra, projWin=[ul.x, ul.y, lr.x, lr.y],
            xRes=xRes, yRes=yRes, **kwargs)
        gdalDataset = gdal.Translate(destName=filename, srcDS=self.gdalDataset, options=options)

        gdalRaster = GdalRaster(gdalDataset=gdalDataset)
        gdalRaster.setGrid(grid=grid)
        return gdalRaster
