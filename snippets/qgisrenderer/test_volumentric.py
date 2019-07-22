
import unittest
from enmapbox.testing import initQgisApplication, TestObjects

QGIS_APP = initQgisApplication(loadProcessingFramework=False, loadEditorWidgets=False)

SHOW_GUI = True

from snippets.qgisrenderer.volumetric import *
class VTest(unittest.TestCase):

    def test_widget(self):

        W = VolumetricWidget()
        W.show()


        from enmapboxtestdata import enmap as pathEnMAP
        lyr1 = QgsRasterLayer(pathEnMAP, 'EnMAP Example')

        from enmapboxtestdata import hires as pathHyMap
        lyr2 = QgsRasterLayer(pathHyMap, 'HyMAP')

        pathTS = r'R:\temp\temp_bj\Cerrado\cerrado_evi.vrt'
        lyr3 = QgsRasterLayer(pathTS, 'TimeSeries')
        QgsProject.instance().addMapLayers([lyr1, lyr2, lyr3])


        if False:
            W.setX(50)
            W.setY(25)
            W.setZ(75)

            self.assertEqual(W.x(), 50)
            self.assertEqual(W.y(), 25)
            self.assertEqual(W.z(), 75)

            self.assertTrue(isSliceRenderer(W.sliceRenderer()))
            self.assertIsInstance(W.topPlaneRenderer(), QgsRasterRenderer)

            W.onLoadData()

        if SHOW_GUI:
            QGIS_APP.exec_()