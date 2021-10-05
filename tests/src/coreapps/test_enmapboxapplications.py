import unittest
import xmlrunner
import site
from qgis.core import QgsApplication
from enmapbox.testing import EnMAPBoxTestCase
from enmapbox import EnMAPBox, EnMAPBoxApplication
from enmapbox.gui.utils import *
from enmapbox import DIR_ENMAPBOX
from qgis.PyQt.QtWidgets import QWidget

site.addsitedir(pathlib.Path(DIR_ENMAPBOX) / 'coreapps')
from reclassifyapp.reclassify import *


class TestEnMAPBoxApplications(EnMAPBoxTestCase):

    def test_UiLibrary(self):
        # Addresses https://bitbucket.org/hu-geomatics/enmap-box/issues/310/attributeerror-function-object-has-no

        enmapBox = EnMAPBox(load_core_apps=True, load_other_apps=False)
        enmapBox.loadExampleData()
        self.assertIsInstance(enmapBox, EnMAPBox)

        # how to get SPECLIBs listed in the EnMAP-Box
        # a) get the URI
        speclibUris = enmapBox.dataSources('SPECLIB')

        speclibDataSources = enmapBox.dataSourceManager().sources('SPECLIB')

        self.assertTrue(len(speclibUris) > 0)
        self.assertEqual(len(speclibUris), len(speclibDataSources))

        from enmapboxapplications.widgets.core import UiLibrary
        speclibCB = UiLibrary()

        self.assertTrue(len(speclibDataSources) == speclibCB.count() - 1)


if __name__ == "__main__":
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'), buffer=False)
