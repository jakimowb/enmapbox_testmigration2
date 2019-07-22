
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
        lyr = QgsRasterLayer(pathEnMAP, 'EnMAP Example')

        W.setRasterLayer(lyr)

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