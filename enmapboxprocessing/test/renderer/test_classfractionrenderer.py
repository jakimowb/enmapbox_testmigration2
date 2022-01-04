from PyQt5.QtGui import QColor
from qgis._core import QgsRasterLayer, Qgis
import numpy as np

from enmapboxprocessing.renderer.classfractionrenderer import ClassFractionRenderer
from enmapboxprocessing.test.testcase import TestCase
from enmapboxprocessing.utils import Utils
from enmapboxtestdata import landcover_map_l3

from tests.testdata import fraction_map_l3_tif


class TestClassFractionRenderer(TestCase):

    def test_fractionL3(self):
        renderer = ClassFractionRenderer()
        classification = QgsRasterLayer(landcover_map_l3)
        categories = Utils.categoriesFromPalettedRasterRenderer(classification.renderer())
        for category in categories:
            renderer.addCategory(category)
        raster = QgsRasterLayer(fraction_map_l3_tif)
        raster.setRenderer(renderer)
        block = renderer.block(1, raster.extent(), raster.width(), raster.height())
        self.assertEqual(Qgis.ARGB32_Premultiplied, block.dataType())
        self.assertEqual(305025900183086, np.sum(Utils.qgsRasterBlockToNumpyArray(block), dtype=float))

    def test_roofOnly(self):
        renderer = ClassFractionRenderer()
        classification = QgsRasterLayer(landcover_map_l3)
        categories = Utils.categoriesFromPalettedRasterRenderer(classification.renderer())
        renderer.addCategory(categories[0])
        raster = QgsRasterLayer(fraction_map_l3_tif)
        raster.setRenderer(renderer)
        block = renderer.block(1, raster.extent(), raster.width(), raster.height())
        self.assertEqual(Qgis.ARGB32_Premultiplied, block.dataType())
        self.assertEqual(242419437535232, np.sum(Utils.qgsRasterBlockToNumpyArray(block), dtype=float))
