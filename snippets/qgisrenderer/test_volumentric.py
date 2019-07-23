
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
        from enmapboxtestdata import hires as pathHyMap
        from enmapbox.testing import TestObjects
        pathTS = r'R:\temp\temp_bj\Cerrado\cerrado_evi.vrt'

        data = np.fromfunction()

        layers = []
        for p in [pathEnMAP, pathHyMap, pathTS]:
            if os.path.isfile(p):
                layers.append(QgsRasterLayer(p, os.path.basename(p)))

        QgsProject.instance().addMapLayers(layers)

        if True:
            lyr = layers[0]
            self.assertIsInstance(lyr, QgsRasterLayer)
            W.setRasterLayer(lyr)
            self.assertEqual(lyr, W.rasterLayer())

            x = int(lyr.width() * 0.5)
            y = int(lyr.height() * 0.5)
            z = int(lyr.bandCount() * 0.5)
            W.setX(x)
            W.setY(y)
            W.setZ(z)

            self.assertEqual(W.zScale(), 1)
            #W.setZSCale(2)
            #self.assertEqual(W.zScale(), 2)
            #W.setZSCale(2)
            self.assertEqual(W.x(), x)
            self.assertEqual(W.y(), y)
            self.assertEqual(W.z(), z)

            self.assertIsInstance(W.sliceRenderer(), QgsRasterRenderer)
            self.assertIsInstance(W.topPlaneRenderer(), QgsRasterRenderer)

            W.onLoadData()

        if SHOW_GUI:
            QGIS_APP.exec_()