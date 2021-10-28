from qgis._core import QgsRasterLayer

import numpy as np

from hubdsm.core.gdaldriver import ENVI_DRIVER
from hubdsm.core.raster import Raster
from hubdsm.processing.aggregatebands import AggregateBands
from hubdsm.test.processing.testcase import TestCase


class TestAggregateBands(TestCase):

    def test(self):
        filename = '/vsimem/raster.bsq'
        gdalRaster = ENVI_DRIVER.createFromArray(array=np.array([[[1]], [[2]], [[3]]]), filename=filename)
        gdalRaster.flushCache()
        alg = AggregateBands()
        io = {
            alg.P_RASTER: QgsRasterLayer(filename),
            alg.P_FUNCTION: list(alg.FUNCTIONS.values()).index(np.mean),
            alg.P_OUTPUT_RASTER: '/vsimem/raster2.bsq'
        }
        result = self.runalg(alg=alg, io=io)
        raster2 = Raster.open(result[alg.P_OUTPUT_RASTER])
        self.assertEqual(raster2.readAsArray()[0, 0, 0], 2)
