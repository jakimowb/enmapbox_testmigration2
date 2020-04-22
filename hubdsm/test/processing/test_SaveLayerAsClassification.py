import numpy as np
from qgis._core import QgsRasterLayer

from hubdsm.core.gdalrasterdriver import ENVI_DRIVER
from hubdsm.core.raster import Raster
from hubdsm.processing.importenmapl1b import ImportEnmapL1B
from hubdsm.processing.savelayerasclassification import SaveLayerAsClassification, saveLayerAsClassification
from hubdsm.test.processing.testcase import TestCase


class TestSaveLayerAsClassification(TestCase):

    def test_coreAlgo(self):
        filename = r'C:\Users\janzandr\Desktop\raster.bsq'
        rasterLayer = QgsRasterLayer(filename)
        classification = saveLayerAsClassification(qgsRasterLayer=rasterLayer, filename=filename.replace('raster.bsq', 'classification.vrt'))
        print(classification.categories)

    def test_processingAlgo(self):
        filename = r'C:\Users\janzandr\Desktop\raster.bsq'
        alg = SaveLayerAsClassification()
        io = {
            alg.P_RASTER: QgsRasterLayer(filename),
            alg.P_OUTRASTER: filename.replace('raster.bsq', 'classification.bsq')
        }
        result = self.runalg(alg=alg, io=io)
        print(Raster.open(result[alg.P_OUTRASTER]).categories)
