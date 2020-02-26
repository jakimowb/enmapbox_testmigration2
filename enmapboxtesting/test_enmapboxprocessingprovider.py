import unittest, sys
from enmapbox.testing import TestCase, TestObjects
from qgis.core import *
from qgis.gui import *

class ProcessingProviderTests(TestCase):

    def setUp(self):
        reg = QgsApplication.instance().processingRegistry()
        to_Remove = []
        from enmapbox.algorithmprovider import NAME, ID
        for p in reg.providers():
            if p.id() == ID:
                to_Remove.append(p)
        for p in to_Remove:
            reg.removeProvider(p)

    def test_processing_provider(self):

        from enmapbox.algorithmprovider import EnMAPBoxAlgorithmProvider
        reg = QgsApplication.instance().processingRegistry()

        pNames = [p.name() for p in reg.providers()]
        provider = EnMAPBoxAlgorithmProvider()
        self._p = provider
        pNames2 = [p.name() for p in reg.providers()]
        self.assertIsInstance(provider, QgsProcessingProvider)
        self.assertTrue(len(provider.algorithms()) == 0)

        self.assertIsInstance(reg, QgsProcessingRegistry)
        self.assertTrue(provider not in reg.providers())
        reg.addProvider(provider)
        if not provider in reg.providers():
            print('Provider not in registry:\n{}'.format(str(provider)), file=sys.stderr)
            for p2 in reg.providers():
                print(p2)

        self.assertTrue(provider in reg.providers())

        alg = TestObjects.processingAlgorithm()
        self.assertTrue(alg, QgsProcessingAlgorithm)
        provider.addAlgorithm(alg)
        self.assertTrue(alg in provider.algorithms())
        self.assertTrue(alg in reg.algorithms())

        reg.removeProvider(provider)
        self.assertTrue(provider not in reg.providers())
        self.assertTrue(alg not in reg.algorithms())

    def test_init(self):

        from enmapbox import initEnMAPBoxProcessingProvider
        s = ""
        initEnMAPBoxProcessingProvider()
        s = ""

if __name__ == "__main__":
    unittest.main()


