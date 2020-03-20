from os.path import join
from unittest import TestCase

from enmapboxtestdata import enmap
from hubdsm.core.coordinatetransformation import CoordinateTransformation
from hubdsm.core.extent import Extent
from hubdsm.core.grid import Grid
from hubdsm.core.location import Location
from hubdsm.core.projection import Projection
from hubdsm.core.raster import Raster
from hubdsm.core.resolution import Resolution
from hubdsm.core.size import Size

outdir = r'c:\unittests\hubdsm'


class TestRaster(TestCase):

    def test_readAsArray(self):
        raster = Raster.open(filename=enmap)
        array = raster.readAsArray()
        print(array.shape)

    def test_readAsArrayWithInvalidExtent(self):
        raster = Raster.open(filename=enmap)
        grid = Grid(
            extent=Extent(ul=Location(x=0, y=0), size=Size(x=90, y=90)), resolution=raster.grid.resolution,
            projection=raster.grid.projection
        )
        try:
            raster.readAsArray(grid=grid)
        except AssertionError as error:
            print(repr(error))

    def test_readAsArrayWithInvalidProjection(self):
        raster = Raster.open(filename=enmap)
        grid = Grid(
            extent=Extent(ul=Location(x=0, y=0), size=Size(x=90, y=90)), resolution=raster.grid.resolution,
            projection=Projection.fromWgs84()
        )
        try:
            raster.readAsArray(grid=grid)
        except AssertionError as error:
            print(repr(error))

    def test_warp(self):
        raster = Raster.open(filename=enmap)
        grid = Grid(
            extent=Extent(ul=Location(x=13., y=53.), size=Size(x=1, y=1)), resolution=Resolution(x=0.01, y=0.01),
            projection=Projection.fromWgs84()
        )
        raster.warp(grid=grid)