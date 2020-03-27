from os.path import join
from unittest import TestCase

import numpy as np

from enmapboxtestdata import enmap
from hubdsm.algorithm.convertraster import convertRaster
from hubdsm.algorithm.categorycounts import categoryCounts
from hubdsm.algorithm.processingoptions import ProcessingOptions
from hubdsm.core.coordinatetransformation import CoordinateTransformation
from hubdsm.core.extent import Extent
from hubdsm.core.gdalrasterdriver import ENVI_DRIVER, MEM_DRIVER
from hubdsm.core.grid import Grid
from hubdsm.core.location import Location
from hubdsm.core.projection import Projection
from hubdsm.core.raster import Raster
from hubdsm.core.resolution import Resolution
from hubdsm.core.size import Size


class TestCategoryCounts(TestCase):

    def test(self):
        mask = Raster.open(MEM_DRIVER.createFromArray(array=np.array([[[0, 0, 1, 1, 1, 0, 0]]])))
        raster = Raster.open(MEM_DRIVER.createFromArray(array=np.array([[[1, 2, 3, 2, 1, 0, -1]]]))).withMask(mask=mask)
        lead = categoryCounts(raster=raster)
        gold = {1: 1, 2: 1, 3: 1}
        self.assertDictEqual(gold, lead)


class TestConvertRaster(TestCase):

    def test_mask(self):
        assert 0 #weiter blockwise!!!!!!!!!!!!!
        mask = Raster.open(MEM_DRIVER.createFromArray(array=np.array([[[1, 0, 1]]])))
        raster = Raster.open(MEM_DRIVER.createFromArray(array=np.array([[[1, 2, 0]]])))
        raster = raster.withMask(mask=mask)

        processingOptions = ProcessingOptions(shape=GridShape(x=1, y=1))
        converted = convertRaster(raster=raster, noDataValues=[-9999])
        assert np.all(np.equal(converted.readAsArray(), [[[1, -9999, 0]]]))
