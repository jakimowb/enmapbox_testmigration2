from unittest.case import TestCase

import numpy as np
from osgeo import gdal

from enmapboxtestdata import enmap
from hubdsm.core.band import Band
from hubdsm.core.mask import Mask
from hubdsm.core.gdalrasterdriver import MEM_DRIVER


class TestBand(TestCase):

    def test_Band(self):
        band = Band(name='enmap', filename=enmap, number=1, mask=None, _gdalBand=None)
        assert isinstance(band.gdalBand.gdalBand, gdal.Band)

    def test_readAsArray(self):
        mask = Mask(band=Band.fromGdalBand(MEM_DRIVER.createFromArray(array=np.array([[[1, 1, 1, 0, 0, 0]]])).band(1)))
        band = Band.fromGdalBand(MEM_DRIVER.createFromArray(array=np.array([[[-1, 0, 1, -1, 0, 1]]])).band(1))
        band.gdalBand.setNoDataValue(-1)
        band = band.withMask(mask=mask)
        assert np.all(np.equal(band.readAsArray(), [[-1, 0, 1, -1, 0, 1]]))
        assert np.all(np.equal(mask.readAsArray(), [[True, True, True, False, False, False]]))
        assert np.all(np.equal(band.readAsMaskArray(), [[False, True, True, False, False, False]]))

    def test_readAsMaskArray(self):
        band = Band.fromGdalBand(MEM_DRIVER.createFromArray(array=np.array([[[np.nan, 0, 1]]])).band(1))
        band.gdalBand.setNoDataValue(np.nan)
        assert np.all(np.equal(band.readAsMaskArray(), [[False, True, True]]))

    def test_readAsSample(self):
        mask = Mask(band=Band.fromGdalBand(MEM_DRIVER.createFromArray(array=np.array([[[1, 1, 1, 0, 0, 0]]])).band(1)))
        band = Band.fromGdalBand(MEM_DRIVER.createFromArray(array=np.array([[[-1, 10, 20, -1, 0, 1]]])).band(1))
        band.gdalBand.setNoDataValue(-1)
        band = band.withMask(mask=mask)
        sample = band.readAsSample()
        assert np.all(np.equal(sample.xLocations, [[1, 2]]))
        assert np.all(np.equal(sample.yLocations, [[0, 0]]))
        assert np.all(np.equal(sample.values, [[10, 20]]))
