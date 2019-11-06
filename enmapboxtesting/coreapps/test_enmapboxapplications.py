import unittest
from unittest import TestCase
from enmapbox.testing import initQgisApplication, TestObjects
import enmapboxtestdata
from reclassifyapp.reclassify import *
from enmapbox.gui import ClassificationScheme
from enmapbox.gui.utils import *
from enmapbox import EnMAPBox, EnMAPBoxApplication

SHOW_GUI = True

class TestEnMAPBoxApplications(TestCase):

    @classmethod
    def setUpClass(cls):

        cls.qgsApp = initQgisApplication()

    @classmethod
    def tearDownClass(cls):

        cls.qgsApp.quit()


    def setUp(self):

        self.emb = EnMAPBox()
        self.emb.loadExampleData()

    def tearDown(self):
        self.emb.close()
        self.emb = None


    def test_UiLibrary(self):
        # addresses https://bitbucket.org/hu-geomatics/enmap-box/issues/310/attributeerror-function-object-has-no

        enmapBox = EnMAPBox.instance()
        self.assertIsInstance(enmapBox, EnMAPBox)

        # how to get SPECLIBs listed in the EnMAP-Box
        # a) get the URI
        speclibUris = enmapBox.dataSources('SPECLIB')
        # b) get the DataSourceSpectralLibrary instances
        speclibDataSources = enmapBox.dataSourceManager().sources('SPECLIB')

        self.assertTrue(len(speclibUris) > 0)
        self.assertEqual(len(speclibUris), len(speclibDataSources))


        from enmapboxapplications.widgets.core import UiLibrary
        speclibCB = UiLibrary()


        self.assertIsInstance(speclibCB, QComboBox)
        self.assertTrue(len(speclibDataSources) == speclibCB.count() - 1)




if __name__ == "__main__":

    SHOW_GUI = False
    unittest.main()
