from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple, Sequence, Union
from uuid import uuid4

import numpy as np
from osgeo import gdal

from hubdsm.core.gdalband import GdalBand
from hubdsm.core.grid import Grid


@dataclass(frozen=True)
class Band(object):
    """Raster band."""
    name: str
    filename: str
    number: int
    noDataValue: Optional[Union[float, int]]
    gra: Union[int, str]
    gdt: int

    def __post_init__(self):
        assert isinstance(self.name, str)
        assert isinstance(self.filename, str)
        assert isinstance(self.number, int) and self.number >= 1
        assert isinstance(self.noDataValue, (float, int, type(None)))
        assert isinstance(self.gra, (int, str))
        assert isinstance(self.gdt, int)

    @property
    def gdalBand(self) -> GdalBand:
        return GdalBand.open(filename=self.filename, number=self.number)

    def rename(self, name) -> Band:
        return Band(
            name=name, filename=self.filename, number=self.number, noDataValue=self.noDataValue, gra=self.gra,
            gdt=self.gdt
        )

    def withMask(self, mask: Band) -> Band:
        return Band(
            name=self.name, filename=self.filename, number=self.number, noDataValue=self.noDataValue, gra=self.gra,
            gdt=self.gdt
        )

    def readAsArray(self, grid: Grid = None):
        return self.gdalBand.readAsArray(grid=grid, gra=self.gra)

    def warp(self, filename: str = None, grid: Grid = None):
        key128bit = uuid4().hex
        filename = f'/vsimem/hubdsm.core.band.Band.warp/{key128bit}.vrt'
        gdal.Translate(destName=filename, srcDS=)
        return Band(name=self.name, filename=filename, number=1, noDataValue=self.noDataValue, gra=gra, gdt=self.gdt)