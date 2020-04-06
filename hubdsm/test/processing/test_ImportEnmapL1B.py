import numpy as np
from qgis._core import QgsRasterLayer

from hubdsm.core.gdalrasterdriver import ENVI_DRIVER
from hubdsm.processing.importenmapl1b import ImportEnmapL1B
from hubdsm.test.processing.testcase import TestCase


class TestClassificationStatistics(TestCase):

    def test_onLayerWithoutCategoricalRenderer(self):
        alg = ImportEnmapL1B()
        io = {
            alg.P_FILE: r'C:\Users\janzandr\Downloads\ENMAP01-____L1B-DT000000987_20130205T105307Z_001_V000101_20190426T143700Z__rows100-199\ENMAP01-____L1B-DT000000987_20130205T105307Z_001_V000101_20190426T143700Z-METADATA.XML',
            alg.P_OUTRASTER_VNIR: '/vsimem/vnir.vrt',
            alg.P_OUTRASTER_SWIR: '/vsimem/swir.vrt'
        }
        result = self.runalg(alg=alg, io=io)