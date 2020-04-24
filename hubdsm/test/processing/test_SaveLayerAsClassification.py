import numpy as np
from qgis._core import QgsRasterLayer

from hubdsm.core.category import Category
from hubdsm.core.color import Color
from hubdsm.core.gdalrasterdriver import ENVI_DRIVER, MEM_DRIVER
from hubdsm.core.raster import Raster
from hubdsm.processing.importenmapl1b import ImportEnmapL1B
from hubdsm.processing.savelayerasclassification import SaveLayerAsClassification, saveLayerAsClassification
from hubdsm.test.processing.testcase import TestCase


class TestSaveLayerAsClassification(TestCase):

    def test(self):

        filename = 'c:/vsimem/raster.bsq'
        raster = Raster.createFromArray(array=np.array([[[0,10,20]]]), filename=filename)
        categories = [
            Category(id=10, name='a', color=Color(255, 0, 0)),
            Category(id=20, name='b', color=Color(0, 0, 255))
        ]
        raster.setCategories(categories=categories)
        del raster

        alg = SaveLayerAsClassification()
        io = {
            alg.P_RASTER: QgsRasterLayer(filename),
            alg.P_OUTRASTER: 'c:/vsimem/classification.vrt'
        }
        result = self.runalg(alg=alg, io=io)

        classification = Raster.open(result[alg.P_OUTRASTER])
        self.assertSequenceEqual(classification.categories, categories)
