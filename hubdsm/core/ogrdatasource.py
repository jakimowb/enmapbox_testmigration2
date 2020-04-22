# from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Union, Any, Dict, Iterable
from os.path import exists

import numpy as np
from osgeo import gdal, ogr

from hubdsm.core.error import ProjectionMismatchError
from hubdsm.core.extent import Extent
from hubdsm.core.gdalband import GdalBand
from hubdsm.core.geotransform import GeoTransform, GdalGeoTransform
from hubdsm.core.grid import Grid
from hubdsm.core.gdalmetadatavalueformatter import GdalMetadataValueFormatter
from hubdsm.core.location import Location
from hubdsm.core.ogrlayer import OgrLayer
from hubdsm.core.projection import Projection
from hubdsm.core.shape import RasterShape, GridShape
from hubdsm.core.size import Size


@dataclass(frozen=True)
class OgrDataSource(object):
    """OGR data source."""
    ogrDataSource: ogr.DataSource

    def __post_init__(self):
        assert isinstance(self.ogrDataSource, (ogr.DataSource, gdal.Dataset))

    @staticmethod
    def open(filename: str) -> 'OgrDataSource':
        assert isinstance(filename, str)
        ogrDataSource = gdal.OpenEx(filename, gdal.OF_VECTOR)
        assert isinstance(ogrDataSource, (ogr.DataSource, gdal.Dataset))
        return OgrDataSource(ogrDataSource=ogrDataSource)

    def layer(self, nameOrIndex: Union[int, str]=None):
        if nameOrIndex is None:
            nameOrIndex = 0
        if isinstance(nameOrIndex, int):
            return OgrLayer(ogrLayer=self.ogrDataSource.GetLayerByIndex(nameOrIndex), ogrDataSource=self.ogrDataSource)
        else:
            return OgrLayer(ogrLayer=self.ogrDataSource.GetLayerByName(nameOrIndex), ogrDataSource=self.ogrDataSource)
