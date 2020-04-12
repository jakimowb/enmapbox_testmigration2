# from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Union, Any, List, Dict

import numpy as np
from osgeo import gdal

from hubdsm.core.category import Category
from hubdsm.core.color import Color
from hubdsm.core.grid import Grid
from hubdsm.core.gdalmetadatavalueformatter import GdalMetadataValueFormatter
from hubdsm.core.error import ProjectionMismatchError


@dataclass(frozen=True)
class GdalBand(object):
    """Raster band dataset."""
    gdalDataset: gdal.Dataset
    gdalBand: gdal.Band
    number: int

    def __post_init__(self):
        assert isinstance(self.gdalDataset, gdal.Dataset)
        assert isinstance(self.gdalBand, gdal.Band)
        assert isinstance(self.number, int)

    @staticmethod
    def open(filenameOrGdalRaster: Union[str, 'GdalRaster'], number: int, access: int = gdal.GA_ReadOnly) -> 'GdalBand':
        from hubdsm.core.gdalraster import GdalRaster
        if isinstance(filenameOrGdalRaster, str):
            gdalRaster = GdalRaster.open(filename=filenameOrGdalRaster, access=access)
        else:
            gdalRaster = filenameOrGdalRaster
        assert isinstance(gdalRaster, GdalRaster)
        return gdalRaster.band(number=number)

    @property
    def index(self):
        """Return band index."""
        return self.number - 1

    @property
    def raster(self) -> 'GdalRaster':
        """Return raster dataset."""
        from hubdsm.core.gdalraster import GdalRaster
        return GdalRaster(gdalDataset=self.gdalDataset)

    @property
    def gdalDataType(self) -> int:
        """Return GDAL data type."""
        return self.gdalBand.DataType

    @property
    def grid(self) -> Grid:
        """Return grid."""
        return self.raster.grid

    def flushCache(self):
        """Flush the cache."""
        self.gdalBand.FlushCache()

    def readAsArray(self, grid: Grid = None, gra: int=None) -> np.ndarray:
        """Return 2d array."""

        if gra is None:
            gra = gdal.GRA_NearestNeighbour

        if grid is None:
            array = self.gdalBand.ReadAsArray(resample_alg=gra)
        else:
            assert isinstance(grid, Grid)
            if grid.projection != self.grid.projection:
                raise ProjectionMismatchError()
            assert grid.extent.within(self.grid.extent)
            resolution = self.grid.resolution
            extent = self.grid.extent
            buf_ysize, buf_xsize = grid.shape
            xoff = round((grid.extent.xmin - extent.xmin) / resolution.x, 0)
            yoff = round((extent.ymax - grid.extent.ymax) / resolution.y, 0)
            xsize = round((grid.extent.xmax - grid.extent.xmin) / resolution.x, 0)
            ysize = round((grid.extent.ymax - grid.extent.ymin) / resolution.y, 0)
            array = self.gdalBand.ReadAsArray(
                xoff=xoff, yoff=yoff, win_xsize=xsize, win_ysize=ysize,
                buf_xsize=buf_xsize, buf_ysize=buf_ysize,
                resample_alg=gra
            )
        assert isinstance(array, np.ndarray)
        assert array.ndim == 2
        return array

    def writeArray(self, array: np.ndarray, grid: Optional[Grid] = None):
        """Write raster data."""

        assert isinstance(array, np.ndarray), array
        assert array.ndim == 2, array.ndim
        if grid is None:
            grid = self.grid
        assert isinstance(grid, Grid), grid
        assert array.shape == tuple(grid.shape), (array.shape, grid.shape)
        assert self.raster.grid.projection == grid.projection

        xoff = int(round((grid.extent.xmin - self.grid.extent.xmin) / self.grid.resolution.x, 0))
        yoff = int(round((self.grid.extent.ymax - grid.extent.ymax) / self.grid.resolution.y, 0))

        self.gdalBand.WriteArray(array, xoff=xoff, yoff=yoff)

    def fill(self, value):
        """Write constant ``value`` to the whole raster band."""
        self.gdalBand.Fill(value)

    def setMetadataItem(self, key, value: Union[Any, List[Any]], domain=''):
        """Set metadata item."""
        if value is None:
            return
        key = key.replace(' ', '_')
        gdalString = GdalMetadataValueFormatter.valueToString(value)
        self.gdalBand.SetMetadataItem(key, gdalString, domain)

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

    def metadataItem(self, key, domain='', default=None, dtype=str):
        """Return the metadata item."""
        key = key.replace(' ', '_')
        gdalString = self.gdalBand.GetMetadataItem(key, domain)
        if gdalString is not None:
            value = GdalMetadataValueFormatter.stringToValue(gdalString, dtype=dtype)
        else:
            value = None
        return value

    def metadataDomain(self, domain=''):
        """Return the metadata dictionary for the given ``domain``."""
        metadataDomain = dict()
        for key in self.gdalBand.GetMetadata(domain):
            key = key.replace('_', ' ')
            metadataDomain[key] = self.metadataItem(key=key, domain=domain)
        return metadataDomain

    @property
    def metadataDict(self):
        """Return the metadata dictionary for all domains."""
        metadataDict = dict()
        for domain in self.metadataDomainList:
            metadataDict[domain] = self.metadataDomain(domain=domain)
        return metadataDict

    def setNoDataValue(self, value):
        """Set no data value."""
        if value is not None:
            self.gdalBand.SetNoDataValue(float(value))

    @property
    def noDataValue(self) -> Optional[float]:
        """Return no data value."""
        return self.gdalBand.GetNoDataValue()

    def setDescription(self, value):
        """Set description."""
        self.gdalBand.SetDescription(value)

    @property
    def description(self) -> str:
        """Return description."""
        return self.gdalBand.GetDescription()

    def setCategories(self, categories: List[Category]):
        """Set categories."""
        ids = [c.id for c in categories]
        maxId = max(ids)
        names = ['n/a'] * (maxId + 1)
        colors = [Color(red=0, green=0, blue=0)] * (maxId +1)
        for c in categories:
            names[c.id] = c.name
            colors[c.id] = c.color
        self._setCategoryNames(names=names)
        self._setCategoryColors(colors)

    def _setCategoryNames(self, names: List[str]):
        """Set category names."""
        self.gdalBand.SetCategoryNames(names)

    def _setCategoryColors(self, colors: List[Color]):
        """Set category colors."""
        colorTable = gdal.ColorTable()
        for i, color in enumerate(colors):
            assert isinstance(color, Color)
            colorTable.SetColorEntry(i, tuple(color))
        self.gdalBand.SetColorTable(colorTable)

    @property
    def categories(self) -> List[Category]:
        """Return categories."""
        categories = list()
        for id, (name, color) in enumerate(zip(self._categoryNames(), self._categoryColors())):
            if name == 'n/a' and color == Color():
                continue
            categories.append(Category(id=id, name=name, color=color))
        return categories

    def _categoryNames(self) -> List[str]:
        """Return category names."""
        names = self.gdalBand.GetCategoryNames()
        if names is None:
            return list()
        return names

    def _categoryColors(self) -> List[Color]:
        """Return category colors."""
        colorTable = self.gdalBand.GetColorTable()
        colors = list()
        if colorTable is not None:
            for i in range(colorTable.GetCount()):
                rgba = colorTable.GetColorEntry(i)
                colors.append(Color(*rgba))
        return colors

    @property
    def metadataDomainList(self):
        """Returns the list of metadata domain names."""
        domains = self.gdalBand.GetMetadataDomainList()
        return domains if domains is not None else []
