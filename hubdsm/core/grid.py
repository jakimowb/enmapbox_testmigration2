# from __future__ import annotations
from dataclasses import dataclass
from typing import Iterator, List

import numpy as np

from hubdsm.core.extent import Extent
from hubdsm.core.geotransform import GeoTransform
from hubdsm.core.location import Location
from hubdsm.core.pixellocation import PixelLocation
from hubdsm.core.projection import Projection
from hubdsm.core.resolution import Resolution
from hubdsm.core.shape import GridShape
from hubdsm.core.size import Size


@dataclass(frozen=True)
class Grid(object):
    """Pixel grid."""
    extent: Extent
    resolution: Resolution
    projection: Projection = Projection.fromWgs84()

    def __post_init__(self):
        assert isinstance(self.extent, Extent)
        assert isinstance(self.resolution, Resolution)
        assert isinstance(self.projection, Projection)
        remainder = np.mod(self.extent.size, self.resolution)
        tol = np.true_divide(self.resolution, 1e6)
        isCloseToZero = remainder <= tol
        isCloseToResolution = np.abs(np.subtract(remainder, np.array(self.resolution))) <= tol
        isClose = np.all(np.logical_or(isCloseToZero, isCloseToResolution))
        assert isClose, f'{self.extent.size} is not multiple of {self.resolution}'

    def withResolution(self, resolution: Resolution):
        return Grid(extent=self.extent, resolution=resolution, projection=self.projection)

    @property
    def shape(self) -> GridShape:
        x, y = np.round(np.divide(self.extent.size, self.resolution))
        return GridShape(y=int(y), x=int(x))

    @property
    def geoTransform(self) -> GeoTransform:
        return GeoTransform(ul=self.extent.ul, resolution=self.resolution)

    @classmethod
    def fromGeoTransform(cls, geoTransform: GeoTransform, shape: GridShape, projection=None) -> 'Grid':
        if projection is None:
            projection = Projection.fromWgs84()
        resolution = geoTransform.resolution
        size = Size(x=shape.x * resolution.x, y=shape.y * resolution.y)
        extent = Extent(ul=geoTransform.ul, size=size)
        return Grid(extent=extent, resolution=resolution, projection=projection)

    @classmethod
    def makePseudoGridFromShape(cls, shape: GridShape) -> 'Grid':
        arcSecond = 1. / 3600.
        resolution = Resolution(x=arcSecond, y=arcSecond)
        ul = Location(x=0, y=shape.y * resolution.y)
        size = Size(x=shape.x * resolution.x, y=shape.y * resolution.y)
        extent = Extent(ul=ul, size=size)
        return Grid(extent=extent, resolution=resolution)

    @classmethod
    def makePseudoGridFromArray(cls, array: np.ndarray) -> 'Grid':
        assert 2 <= array.ndim <= 3
        *_, y, x = array.shape
        return cls.makePseudoGridFromShape(shape=GridShape(y=y, x=x))

    def pixelLocation(self, location: Location) -> PixelLocation:
        """Return pixel location on the grid."""
        assert isinstance(location, Location)
        size = location._ - self.extent.ul._
        size[1] *= -1
        return PixelLocation.fromIterable(size / self.resolution._)

    def location(self, pixelLocation: PixelLocation) -> Location:
        """Return map location."""
        assert isinstance(pixelLocation, PixelLocation)
        offset = self.extent.ul._
        size = pixelLocation._ * self.resolution._ * np.array([+1, -1])
        return Location.fromIterable(offset + size)

    def equal(self, other: 'Grid', tol: float = 1e-6) -> bool:
        """Return whether self is equal to other."""
        if not self.resolution.equal(other=other.resolution, tol=tol):
            return False
        if not self.extent.equal(other=other.extent, tol=tol):
            return False
        return True

    def xPixelCoordinates(self, offset=0) -> List[int]:
        '''Return pixel coordinates in x dimension with optional offset.'''
        return [x + offset for x in range(self.shape.x)]

    def yPixelCoordinates(self, offset=0) -> List[int]:
        '''Return pixel coordinates in y dimension with optional offset.'''
        return [y + offset for y in range(self.shape.y)]

    def xPixelCoordinatesArray(self, offset=0):
        '''Return 2d array of pixel x coordinates with optional offset.'''
        return np.int32(np.asarray(self.xPixelCoordinates(offset=offset)).reshape(1, -1) * np.ones(shape=self.shape))

    def yPixelCoordinatesArray(self, offset=0):
        '''Return 2d array of pixel y coordinates with optional offset.'''
        return np.int32(np.asarray(self.yPixelCoordinates(offset=offset)).reshape(-1, 1) * np.ones(shape=self.shape))

    def subgrid(self, offset: PixelLocation, shape: GridShape) -> 'Grid':
        """Return shape-sized subgrid at offset."""
        assert isinstance(offset, PixelLocation)
        assert isinstance(shape, GridShape)
        offset = np.array(offset)
        resolution = np.array(self.resolution)
        shape = np.flip(shape)
        blockSize = resolution * shape
        selfUpperLeft = np.array(self.extent.ul)
        f = np.array([1, -1])
        blockUpperLeft = selfUpperLeft + offset * f * resolution
        ul = Location.fromIterable(blockUpperLeft)
        size = Size.fromIterable(blockSize)
        extent = Extent(ul=ul, size=size)
        return Grid(extent=extent, resolution=self.resolution, projection=self.projection)

    def subgrids(self, shape: GridShape) -> Iterator['Grid']:
        """Iterate in shape-sized subgrids over the grid."""
        assert isinstance(shape, GridShape)
        shape = GridShape.fromIterable(np.minimum(shape, self.shape))
        offset = PixelLocation(x=0, y=0)
        while offset.y < self.shape.y:
            offset = PixelLocation(x=0, y=offset.y)
            while offset.x < self.shape.x:
                subgrid = self.subgrid(offset=offset, shape=shape)
                subextentTrimmed = self.extent.intersection(subgrid.extent)
                subgridTrimmed = Grid(extent=subextentTrimmed, resolution=self.resolution, projection=self.projection)
                yield subgridTrimmed
                offset = PixelLocation(x=offset.x + shape.x, y=offset.y)
            offset = PixelLocation(x=offset.x, y=offset.y + shape.y)
