from qgis._core import QgsRasterLayer

from hubdsm.processing.changemap import ChangeMap
from hubdsm.test.processing.testcase import TestCase


class TestChangeMap(TestCase):

    def test(self):
        filename1 = r'C:\Work\data\CORINE\U2000_CLC1990_V2020_20u1_subset.tif'
        filename2 = r'C:\Work\data\CORINE\U2006_CLC2000_V2020_20u1.tif'
        filename1 = filename2 = 'C:/Users/janzandr/Downloads/classification2.bsq'

#        filename = r'C:\Users\janzandr\Downloads\roi.tif'
        alg = ChangeMap()
        io = {
            alg.P_CLASSIFICATION1: QgsRasterLayer(filename1),
            alg.P_CLASSIFICATION2: QgsRasterLayer(filename2),
            alg.P_OUTRASTER: 'c:/vsimem/changemap.bsq'
        }
        result = self.runalg(alg=alg, io=io)

