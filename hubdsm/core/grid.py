from __future__ import annotations
from dataclasses import dataclass
from typing import Iterator, Optional

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
    def fromGeoTransform(cls, geoTransform: GeoTransform, shape: GridShape, projection=None) -> Grid:
        if projection is None:
            projection = Projection.fromWgs84()
        resolution = geoTransform.resolution
        size = Size(x=shape.x * resolution.x, y=shape.y * resolution.y)
        extent = Extent(ul=geoTransform.ul, size=size)
        return Grid(extent=extent, resolution=resolution, projection=projection)

    @classmethod
    def makePseudoGridFromShape(cls, shape: GridShape) -> Grid:
        arcSecond = 1. / 3600.
        resolution = Resolution(x=arcSecond, y=arcSecond)
        ul = Location(x=0, y=shape.y * resolution.y)
        size = Size(x=shape.x * resolution.x, y=shape.y * resolution.y)
        extent = Extent(ul=ul, size=size)
        return Grid(extent=extent, resolution=resolution)

    @classmethod
    def makePseudoGridFromArray(cls, array: np.ndarray) -> Grid:
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

    # def snapExtent(self, extent: Extent) -> extent:
    #    assert self.extent.projection == extent.projection
    #    ulPixel = self.snapCoordinate(location=extent.ul())
    #    lrPixel = self.snapCoordinate(location=extent.lr())
    #    ul = self.
    #    size = np.abs(np.subtract(ul, lr))
    #    Extent.fromUpperLeftAndSize(ul=ul, size=Size.fromIterable(size), projection=extent.projection)

    def equal(self, other: Grid, tol: float = 1e-6) -> bool:
        """Return whether self is equal to other."""
        if not self.resolution.equal(other=other.resolution, tol=tol):
            return False
        if not self.extent.equal(other=other.extent, tol=tol):
            return False
        return True

    #    def withResolution(self, resolution: Resolution, snap: Callable = round) -> Grid:
    #        """Return grid with new resolution. The extent is snapped to match the new resolution."""
    #        extent = Grid.snapExtentToResolution(extent=self.extent, resolution=resolution, snap=snap)
    #        return Grid(extent=extent, resolution=resolution)

    # def xMapCoordinates(self):
    #     """Returns the list of map locations in x dimension."""
    #     return [self.extent().xmin() + (x + 0.5) * self.resolution().x() for x in range(self.size().x())]
    #
    # def yMapCoordinates(self):
    #     """Returns the list of map coordinates in y dimension."""
    #     return [self.extent().ymax() - (y + 0.5) * self.resolution().y() for y in range(self.size().y())]
    #
    # def xMapCoordinatesArray(self):
    #     """Returns the 2d array of map x coordinates."""
    #     return np.asarray(self.xMapCoordinates()).reshape(1, -1) * np.ones(shape=self.shape())
    #
    # def yMapCoordinatesArray(self):
    #     """Returns the 2d array of map y coordinates."""
    #     return np.asarray(self.yMapCoordinates()).reshape(-1, 1) * np.ones(shape=self.shape())
    #
    # def xPixelCoordinates(self, offset=0):
    #     """Returns the list of pixel coordinates in x dimension with optional ``offset``."""
    #     return [x + offset for x in range(self.size().x())]
    #
    # def yPixelCoordinates(self, offset=0):
    #     """Returns the list of pixel coordinates in y dimension with optional ``offset``."""
    #     return [y + offset for y in range(self.size().y())]
    #
    # def xPixelCoordinatesArray(self, offset=0):
    #     """Returns the 2d array of pixel x coordinates with optional ``offset``."""
    #     return np.int32(np.asarray(self.xPixelCoordinates(offset=offset))
    #              .reshape(1, -1) * np.ones(shape=self.shape()))
    #
    # def yPixelCoordinatesArray(self, offset=0):
    #     """Returns the 2d array of pixel y coordinates with optional ``offset``."""
    #     return np.int32(np.asarray(self.yPixelCoordinates(offset=offset))
    #     .reshape(-1, 1) * np.ones(shape=self.shape()))
    #
    #

    # def clip(self, extent):
    #     """Return self clipped by given extent."""
    #     assert isinstance(extent, Extent)
    #     extent = self.extent().intersection(other=extent)
    #     return Grid(extent=extent, resolution=self.resolution()).anchor(point=self.extent().upperLeft())
    #
    # def pixelBuffer(self, buffer, left=True, right=True, up=True, down=True):
    #     """Returns a new instance with a pixel buffer applied in different directions.
    #
    #     :param buffer: number of pixels to be buffered (can also be negativ)
    #     :type buffer: int
    #     :param left: whether to buffer to the left/west
    #     :type left: bool
    #     :param right: whether to buffer to the right/east
    #     :type right: bool
    #     :param up: whether to buffer upwards/north
    #     :type up: bool
    #     :param down: whether to buffer downwards/south
    #     :type down: bool
    #     :return:
    #     :rtype: hubdc.core.Grid
    #     """
    #     assert isinstance(buffer, int)
    #     extent = Extent(xmin=self.extent().xmin() - buffer * (self.resolution().x() if left else 0),
    #                     xmax=self.extent().xmax() + buffer * (self.resolution().x() if right else 0),
    #                     ymin=self.extent().ymin() - buffer * (self.resolution().y() if down else 0),
    #                     ymax=self.extent().ymax() + buffer * (self.resolution().y() if up else 0),
    #                     projection=self.projection())
    #     return Grid(extent=extent, resolution=self.resolution())
    #
    # def anchor(self, point):
    #     """Returns a new instance that is anchored to the given ``point``.
    #     Anchoring will result in a subpixel shift.
    #     See the source code for implementation details."""
    #
    #     assert isinstance(point, Point)
    #     point = point.reproject(projection=self.projection())
    #     xoff = (self.extent().xmin() - point.x()) % self.resolution().x()
    #     yoff = (self.extent().ymin() - point.y()) % self.resolution().y()
    #
    #     # round snapping offset
    #     if xoff > self.resolution().x() / 2.:
    #         xoff -= self.resolution().x()
    #     if yoff > self.resolution().y() / 2.:
    #         yoff -= self.resolution().y()
    #
    #     # return new instance
    #     extent = Extent(xmin=self.extent().xmin() - xoff,
    #                     ymin=self.extent().ymin() - yoff,
    #                     xmax=self.extent().xmax() - xoff,
    #                     ymax=self.extent().ymax() - yoff,
    #                     projection=self.projection())
    #     return Grid(extent=extent, resolution=self.resolution())
    #

    def block(self, offset: PixelLocation, shape: GridShape) -> Grid:
        """Return shape-sized block at offset."""

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

    def blocks(self, shape: GridShape) -> Iterator[Grid]:
        """Iterate in shape-sized blocks over the grid."""
        assert isinstance(shape, GridShape)
        shape = GridShape.fromIterable(np.minimum(shape, self.shape))
        offset = PixelLocation(x=0, y=0)
        while offset.y < self.shape.y:
            offset = PixelLocation(x=0, y=offset.y)
            while offset.x < self.shape.x:
                block = self.block(offset=offset, shape=shape)
                block = block.intersection(self)
                yield block
                offset = PixelLocation(x=offset.x + shape.x, y=offset.y)
            offset = PixelLocation(x=offset.x, y=offset.y + shape.y)

    def within(self, other: Grid, tol: Optional[float] = None) -> bool:
        """Return wether grid is inside other grid."""
        assert isinstance(other, Grid)
        if not self.projection == other.projection:
            return False
        if not self.isAligned(other, tol=tol):
            return False
        return self.extent.within(other.extent, tol=tol)

    def intersection(self, other: Grid, tol: Optional[float] = None) -> Grid:
        """Return the intersection of self and other grid. """
        assert isinstance(other, Grid)
        assert self.projection == other.projection
        assert self.isAligned(other, tol=tol)
        extent = self.extent.intersection(other.extent)
        return Grid(extent=extent, resolution=self.resolution, projection=self.projection)

    def union(self, other: Grid, tol: Optional[float] = None) -> Grid:
        """Return the union of self and other grid. """
        assert isinstance(other, Grid)
        assert self.projection == other.projection
        assert self.isAligned(other, tol=tol)
        extent = self.extent.union(other.extent)
        return Grid(extent=extent, resolution=self.resolution, projection=self.projection)

    def isAligned(self, other: Grid, tol: Optional[float] = None) -> bool:
        assert isinstance(other, Grid)
        if not self.resolution.equal(other.resolution, tol=tol):
            return False
        for location in [other.extent.ul, other.extent.lr]:
            pixelLocation = self.pixelLocation(location=location)
            pixelLocationSnapped = pixelLocation.round
            if not pixelLocation.equal(pixelLocationSnapped, tol=tol):
                return False
        return True
