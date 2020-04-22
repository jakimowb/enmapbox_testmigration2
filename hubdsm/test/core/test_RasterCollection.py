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
        assert 0 #todo finish test

    def test___getitem__(self):
        raster = Raster.open(MEM_DRIVER.createFromArray(array=np.ones(shape=(3, 5, 5)))).rename(['B1', 'B2', 'B3'])
        self.assertTupleEqual(raster.bandNames, ('B1', 'B2', 'B3'))
        self.assertTupleEqual(raster[1].bandNames, ('B2',))
        self.assertTupleEqual(raster[1:].bandNames, ('B2', 'B3'))
