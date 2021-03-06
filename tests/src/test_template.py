"""
This is a template to create an EnMAP-Box test
"""
import unittest
import xmlrunner

from qgis.PyQt.QtWidgets import QApplication
from qgis.core import QgsApplication, QgsRasterLayer, QgsVectorLayer
from enmapbox.testing import EnMAPBoxTestCase, TestObjects
from enmapbox import EnMAPBox

hasTestData = False
try:
    import enmapbox.exampledata
    hasTestData = True
except ModuleNotFoundError:
    hasTestData = False

class EnMAPBoxTestCaseExample(EnMAPBoxTestCase):

    def test_testenvironemnt(self):

        # this example shows you the standard environment of an EnMAPBoxTestCase

        # QGIS is up and running
        qgsApp = QgsApplication.instance()
        self.assertIsInstance(qgsApp, QgsApplication)
        self.assertTrue(qgsApp == QApplication.instance())


        self.assertTrue(EnMAPBox.instance() == None) # EnMAPBox is not started

    def test_with_enmapbox(self):

        enmapBox = EnMAPBox()

        self.assertIsInstance(enmapBox, EnMAPBox)
        self.assertEqual(enmapBox, EnMAPBox.instance())

        if hasTestData:
            enmapBox.loadExampleData()

        # generate in-memory test layers
        rasterLayer = TestObjects.createRasterLayer()
        self.assertIsInstance(rasterLayer, QgsRasterLayer)
        self.assertTrue(rasterLayer.isValid())

        vectorLayer = TestObjects.createVectorLayer()
        self.assertIsInstance(vectorLayer, QgsVectorLayer)
        self.assertTrue(vectorLayer.isValid())


if __name__ == '__main__':

    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'), buffer=False)
