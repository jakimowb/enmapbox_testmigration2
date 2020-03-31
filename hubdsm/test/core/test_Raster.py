from unittest.case import TestCase

import numpy as np
from osgeo import gdal

from enmapboxtestdata import enmap
from hubdsm.core.error import ProjectionMismatchError
from hubdsm.core.extent import Extent
from hubdsm.core.gdalraster import GdalRaster
from hubdsm.core.gdalrasterdriver import MEM_DRIVER
from hubdsm.core.grid import Grid
from hubdsm.core.location import Location
from hubdsm.core.projection import Projection
from hubdsm.core.raster import Raster
from hubdsm.core.resolution import Resolution
from hubdsm.core.shape import GridShape
from hubdsm.core.size import Size


class TestRaster(TestCase):

    def test_open(self):
        try:
            Raster.open(filenameOrGdalRaster=None)
        except ValueError:
            pass

    def test_fromGdalRaster(self):
        gdalRaster = GdalRaster.open(filename=enmap)
        raster = Raster.fromGdalRaster(gdalRaster=gdalRaster)
        for number, band in enumerate(raster.bands, 1):
            self.assertEqual(band.number, number)
            self.assertEqual(band.filename, enmap)

    def test_readAll(self):
        raster = Raster.open(enmap)
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

        raster1 = Raster.open(MEM_DRIVER.createFromArray(array=array1, grid=grid1)).rename(bandNames=['B1'])
        raster2 = Raster.open(MEM_DRIVER.createFromArray(array=array2, grid=grid2)).rename(bandNames=['B2'])
        raster = raster1.addBands(raster=raster2)
        assert raster.grid.equal(grid1)
        assert np.all(raster1.readAsArray() == array1)
        assert np.all(raster2.readAsArray() == array2)
        gold = [[[0., 1.], [2., 3.]], [[2.5, 4.5], [10.5, 12.5]]]
        lead = raster.readAsArray(gdalResamplingAlgorithm=gdal.GRA_Average)
        assert np.all(np.equal(lead, gold))

    def test_readBlockwise(self):
        array = np.array(range(5 * 4)).reshape((1, 5, 4))
        raster = Raster.fromGdalRaster(MEM_DRIVER.createFromArray(array=array))
        leads = list()
        for subgrid in raster.grid.subgrids(shape=GridShape(y=2, x=2)):
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
        raster = Raster.open(enmap)
        grid = Grid(
            extent=Extent(ul=Location(x=0, y=0), size=Size(x=90, y=90)), resolution=raster.grid.resolution,
            projection=Projection.fromWgs84()
        )
        try:
            raster.readAsArray(grid=grid)
        except ProjectionMismatchError:
            pass

    def test_select(self):
        raster = Raster.open(
            MEM_DRIVER.createFromArray(array=np.ones(shape=(3,10,10)))
        ).rename(bandNames=['B1', 'B2', 'B3'])
        self.assertEqual(raster.select(selectors=[1, 3]).bandNames, ('B1', 'B3'))
        self.assertEqual(raster.select(selectors=['B1', 'B3']).bandNames, ('B1', 'B3'))
        try:
            raster.select(selectors=[None])
        except ValueError:
            pass

    def test_band(self):
        raster = Raster.open(
            MEM_DRIVER.createFromArray(array=np.ones(shape=(3, 10, 10)))
        ).rename(bandNames=['B1', 'B2', 'B3'])
        self.assertEqual(raster.band(number=2), raster.bands[1])

    def test_rename(self):
        raster = Raster.open(
            MEM_DRIVER.createFromArray(array=np.ones(shape=(3, 10, 10)))
        ).rename(bandNames=['B1', 'B2', 'B3'], name='Raster')
        self.assertEqual(raster.rename().bandNames, ('B1', 'B2', 'B3'))
        self.assertEqual(raster.rename().name, 'Raster')
        self.assertEqual(raster.withName('NewRaster').name, 'NewRaster')

    def test_withMask(self):
        raster = Raster.open(
            MEM_DRIVER.createFromArray(array=np.ones(shape=(3, 10, 10)))
        )
        raster = raster.withMask(raster=raster)
        for band in raster.bands:
            self.assertEqual(band.mask.band.number, band.number)
        raster = raster.withMask(raster=raster.select(selectors=[1]))
        for band in raster.bands:
            self.assertEqual(band.mask.band.number, 1)
        try:
            raster.withMask(raster=raster.select(selectors=[1, 2]))
        except ValueError:
            pass

    def test_iterArrays(self):
        mask = Raster.open(MEM_DRIVER.createFromArray(array=np.array([[[1]], [[0]]])))
        raster = Raster.open(MEM_DRIVER.createFromArray(array=np.array([[[10]], [[20]]])))
        raster = raster.withMask(raster=mask)
        self.assertTrue(np.all(np.equal(raster.readAsArray(), [[[10]], [[20]]])))
        self.assertTrue(np.all(np.equal(raster.readAsMaskArray(), [[[True]], [[False]]])))

