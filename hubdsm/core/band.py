from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple, Sequence, Union

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
    mask: Optional[Band]

    def __post_init__(self):
        assert isinstance(self.name, str)
        assert isinstance(self.filename, str)
        assert isinstance(self.number, int) and self.number >= 1
        assert isinstance(self.noDataValue, (float, int, type(None)))
        assert isinstance(self.gra, (int, str))
        assert isinstance(self.gdt, int)
        assert isinstance(self.mask, (Band, type(None)))

    @property
    def gdalBand(self) -> GdalBand:
        return GdalBand.open(filename=self.filename, number=self.number)

    def rename(self, name) -> Band:
        return Band(
            name=name, filename=self.filename, number=self.number, noDataValue=self.noDataValue, gra=self.gra,
            gdt=self.gdt, mask=self.mask
        )

    def withMask(self, mask: Band) -> Band:
        return Band(
            name=self.name, filename=self.filename, number=self.number, noDataValue=self.noDataValue, gra=self.gra,
            gdt=self.gdt, mask=mask
        )

    def readAsArray(self, grid: Grid = None):
        return self.gdalBand.readAsArray(grid=grid, gra=self.gra)