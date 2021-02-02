from unittest import TestCase

from qgis._core import QgsVectorLayer

from enmapboxprocessing.utils import Utils
from enmapboxtestdata import landcover_polygons


class TestUtils(TestCase):

    def test_(self):
        vector = QgsVectorLayer(landcover_polygons)
        categories = Utils.categoriesFromCategorizedSymbolRenderer(renderer=vector.renderer())
        print(categories)

    def test_nPixelFittingInRam(self, ):
        print(Utils.nPixelFromMegaByteAndDataType(10))