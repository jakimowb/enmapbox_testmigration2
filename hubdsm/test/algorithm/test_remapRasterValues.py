from unittest import TestCase
from unittest.case import TestCase

import numpy as np
from osgeo import gdal

from hubdsm.algorithm.processingoptions import ProcessingOptions
from hubdsm.algorithm.remaprastervalues import remapRasterValues
from hubdsm.core.gdalrasterdriver import MEM_DRIVER
from hubdsm.core.raster import Raster
from hubdsm.core.shape import GridShape


class TestRemapRasterValues(TestCase):

    def test(self):
        mask = Raster.open(MEM_DRIVER.createFromArray(array=np.array([[[1, 1, 1, 1, 0, 0, 0, 0]]])))
        raster = Raster.open(MEM_DRIVER.createFromArray(array=np.array([[[-1, 0, 10, 20, -1, 0, 10, 20]]])))
        raster.band(1).gdalBand.setNoDataValue(-1)
        raster = raster.withMask(raster=mask)
        po = ProcessingOptions(shape=GridShape(x=1, y=1))
        outraster = remapRasterValues(
            raster=raster, sources=np.array((0, 10, 20)), targets=np.array((5, 15, 25), dtype=np.uint8), po=po
        )
        assert outraster.band(1).gdalBand.gdalDataType == gdal.GDT_Byte
        assert outraster.band(1).gdalBand.noDataValue == -1

        outraster = remapRasterValues(
            raster=raster, sources=np.array((-1, 0, 10, 20)), targets=np.array((-999, 5, 15, 25), dtype=np.float64),
            po=po
        )
        assert outraster.band(1).gdalBand.gdalDataType == gdal.GDT_Float64
        assert outraster.band(1).gdalBand.noDataValue == -999