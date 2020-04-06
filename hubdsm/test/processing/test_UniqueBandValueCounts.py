import numpy as np
from qgis._core import QgsRasterLayer

from hubdsm.core.gdalrasterdriver import ENVI_DRIVER
from hubdsm.processing.uniquebandvaluecounts import UniqueBandValueCounts
from hubdsm.test.processing.testcase import TestCase


class TestUniqueBandValueCounts(TestCase):

    def test_onLayerWithoutCategoricalRenderer(self):
        filename = '/vsimem/r.bsq'
        rasterDataset = ENVI_DRIVER.createFromArray(array=np.atleast_3d([-1, 0, 2, 50, 50]), filename=filename)
        rasterDataset.flushCache()
        qgsRasterLayer = QgsRasterLayer(filename)
        assert qgsRasterLayer.isValid()
        alg = UniqueBandValueCounts()
        io = {alg.P_RASTER: qgsRasterLayer, alg.P_BAND: 1}
        result = self.runalg(alg=alg, io=io)
        self.assertEqual('-1: 1\n0: 1\n2: 1\n50: 2\ntotal: 5', result[alg.P_OUTSTRING])