from os.path import join
from unittest import TestCase

import numpy as np
from osgeo import gdal

from enmapboxtestdata import enmap
from hubdsm.core.coordinatetransformation import CoordinateTransformation
from hubdsm.core.extent import Extent
from hubdsm.core.gdalraster import GdalRaster
from hubdsm.core.gdalrasterdriver import GdalRasterDriver, ENVI_DRIVER, MEM_DRIVER
from hubdsm.core.grid import Grid
from hubdsm.core.location import Location
from hubdsm.core.projection import Projection
from hubdsm.core.raster import Raster
from hubdsm.core.resolution import Resolution
from hubdsm.core.shape import GridShape
from hubdsm.core.size import Size
from hubdsm.error import ProjectionMismatchError

outdir = r'c:\unittests\hubdsm'


class TestRaster(TestCase):

    def test_fromGdalRaster(self):
        gdalRaster = GdalRaster.open(filename=enmap)
        raster = Raster.fromGdalRaster(gdalRaster=gdalRaster)
        print(raster)

    def test_readAll(self):
        raster = Raster.open(filename=enmap)
        array = raster.readAsArray()
        assert isinstance(array, np.ndarray)
        assert array.shape == (177, 400, 220)

    def test_readMultiResolution(self):
        array1 = np.array(range(2 ** 2), dtype=np.float32).reshape((1, 2, 2))
        array2 = np.array(range(4 ** 2), dtype=np.float32).reshape((1, 4, 4))
        grid1 = Grid(
            extent=Extent(ul=Location(x=0, y=0), size=Size(x=4, y=4)), resolution=Resolution(x=2, y=2),
            projection=Projection.fromWgs84()
        )
        grid2 = Grid(
            extent=Extent(ul=Location(x=0, y=0), size=Size(x=4, y=4)), resolution=Resolution(x=1, y=1),
            projection=Projection.fromWgs84()
        )

        MEM_DRIVER.createFromArray(array=array2, grid=grid2)
        raster1 = Raster.open(gdalRaster=MEM_DRIVER.createFromArray(array=array1, grid=grid1)).rename(bandNames=['B1'])
        raster2 = Raster.open(filename='/vsimem/r2.bsq').rename(bandNames=['B2'])
        raster = raster1.addBands(raster=raster2)
        assert raster.grid.equal(grid1)
        assert np.all(raster1.readAsArray() == array1)
        assert np.all(raster2.readAsArray() == array2)
        gold = [[[0., 1.], [2., 3.]], [[2.5, 4.5], [10.5, 12.5]]]
        lead = raster.readAsArray(gra=gdal.GRA_Average)
        assert np.all(np.equal(lead, gold))

    def test_readBlockwise(self):
        array = np.array(range(5 * 4)).reshape((1, 5, 4))
        raster = Raster.fromGdalRaster(MEM_DRIVER.createFromArray(array=array))

        leads = list()
        for subgrid in raster.grid.blocks(shape=GridShape(y=2, x=2)):
            leads.append(raster.readAsArray(grid=subgrid)[0])
        golds = [
            [[0, 1], [4, 5]],
            [[2, 3], [6, 7]],
            [[8, 9], [12, 13]],
            [[10, 11], [14, 15]],
            [[16, 17]]
        ]
        for gold, lead in zip(golds, leads):
            assert np.all(np.equal(gold, lead))

    def test_readWithInvalidProjection(self):
        raster = Raster.open(filename=enmap)
        grid = Grid(
            extent=Extent(ul=Location(x=0, y=0), size=Size(x=90, y=90)), resolution=raster.grid.resolution,
            projection=Projection.fromWgs84()
        )
        try:
            raster.readAsArray(grid=grid)
        except ProjectionMismatchError:
            pass
