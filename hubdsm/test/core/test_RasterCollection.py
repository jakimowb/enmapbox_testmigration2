from unittest.case import TestCase

import numpy as np
from osgeo import gdal

from enmapboxtestdata import enmap
from hubdsm.core.band import Band
from hubdsm.core.error import ProjectionMismatchError
from hubdsm.core.extent import Extent
from hubdsm.core.gdalraster import GdalRaster
from hubdsm.core.gdalrasterdriver import MEM_DRIVER
from hubdsm.core.grid import Grid
from hubdsm.core.location import Location
from hubdsm.core.mask import Mask
from hubdsm.core.pixellocation import PixelLocation
from hubdsm.core.projection import Projection
from hubdsm.core.raster import Raster
from hubdsm.core.rastercollection import RasterCollection
from hubdsm.core.resolution import Resolution
from hubdsm.core.shape import GridShape
from hubdsm.core.size import Size


class TestRasterCollection(TestCase):

    def test_readAsSample(self):
        r1 = Raster.createFromArray(array=np.zeros((3, 2, 2))).withName('Raster1').rename(['B11', 'B12', 'B13'])
        r2 = Raster.createFromArray(array=np.ones((2, 2, 2))).withName('Raster2').rename(['B21', 'B22'])
        c = RasterCollection(rasters=(r1, r2))
        samples = c.readAsSample(xMap='xMap', yMap='yMap')
        for rasterName, sample in samples.items():
            print(rasterName)
            for fieldName in sample.dtype.names:
                print(f'  {fieldName}: {sample[fieldName]}')
        return

        # test field names
        sample = raster.readAsSample(fieldNames=Raster.SampleFieldNames.bandNames)
        assert isinstance(sample.B1, np.ndarray)
        assert isinstance(sample.B2, np.ndarray)
        assert isinstance(sample['B1'], np.ndarray)
        assert isinstance(sample['B2'], np.ndarray)
        sample = raster.readAsSample(fieldNames=Raster.SampleFieldNames.bandIndices)
        assert isinstance(sample['0'], np.ndarray)
        assert isinstance(sample['1'], np.ndarray)

        # sample also incomplete profiles (e.g. required for timeseries analysis)
        sample = raster.readAsSample(xPixel='x', yPixel='y', mode=Raster.SampleMode.relaxed)
        self.assertTrue(np.all(np.equal(sample.x, [1, 2, 3])))
        self.assertTrue(np.all(np.equal(sample.y, [0, 0, 0])))
        self.assertTrue(np.all(np.equal(sample.B1, [11, 12, 13])))
        self.assertTrue(np.all(np.equal(sample.B2, [21, 22, -1])))

        # sample only complete profiles (e.g. required for classification)
        sample = raster.readAsSample(xPixel='x', yPixel='y', mode=Raster.SampleMode.strict)
        self.assertTrue(np.all(np.equal(sample.x, [1, 2])))
        self.assertTrue(np.all(np.equal(sample.y, [0, 0])))
        self.assertTrue(np.all(np.equal(sample.B1, [11, 12])))
        self.assertTrue(np.all(np.equal(sample.B2, [21, 22])))

        # sample on subgrid
        subgrid = raster.grid.subgrid(offset=PixelLocation(x=2, y=0), shape=GridShape(x=2, y=1))
        sample = raster.readAsSample(grid=subgrid, xPixel='x', yPixel='y', mode=Raster.SampleMode.relaxed)
        self.assertTrue(np.all(np.equal(sample.x, [2, 3])))
        self.assertTrue(np.all(np.equal(sample.y, [0, 0])))
        self.assertTrue(np.all(np.equal(sample.B1, [12, 13])))
        self.assertTrue(np.all(np.equal(sample.B2, [22, -1])))

    def test___getitem__(self):
        raster = Raster.open(MEM_DRIVER.createFromArray(array=np.ones(shape=(3, 5, 5)))).rename(['B1', 'B2', 'B3'])
        self.assertTupleEqual(raster.bandNames, ('B1', 'B2', 'B3'))
        self.assertTupleEqual(raster[1].bandNames, ('B2',))
        self.assertTupleEqual(raster[1:].bandNames, ('B2', 'B3'))
