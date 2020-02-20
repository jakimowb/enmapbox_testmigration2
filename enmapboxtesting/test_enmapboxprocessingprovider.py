import unittest
from enmapbox.testing import TestCase, TestObjects
from qgis.core import *
from qgis.gui import *

class ProcessingProviderTests(TestCase):

    def test_processing_provider(self):

        from enmapbox.algorithmprovider import EnMAPBoxAlgorithmProvider
        reg = QgsApplication.instance().processingRegistry()

        pNames = [p.name() for p in reg.providers()]
        p = EnMAPBoxAlgorithmProvider()
        pNames2 = [p.name() for p in reg.providers()]
        self.assertIsInstance(p, QgsProcessingProvider)
        self.assertTrue(len(p.algorithms()) == 0)

        self.assertIsInstance(reg, QgsProcessingRegistry)
        self.assertTrue(p not in reg.providers())
        reg.addProvider(p)
        self.assertTrue(p in reg.providers())

        alg = TestObjects.processingAlgorithm()
        self.assertTrue(alg, QgsProcessingAlgorithm)
        p.addAlgorithm(alg)
        self.assertTrue(alg in p.algorithms())
        self.assertTrue(alg in reg.algorithms())

        reg.removeProvider(p)
        self.assertTrue(p not in reg.providers())
        self.assertTrue(alg not in reg.algorithms())

    def test_init(self):

        from enmapbox import initEnMAPBoxProcessingProvider
        s = ""
        initEnMAPBoxProcessingProvider()
        s = ""

if __name__ == "__main__":
    unittest.main()


