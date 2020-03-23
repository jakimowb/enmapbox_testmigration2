import unittest, pathlib, site
from enmapbox.testing import EnMAPBoxTestCase
from enmapbox import EnMAPBox, EnMAPBoxApplication
from enmapbox.gui.utils import *
from enmapbox import DIR_ENMAPBOX
from qgis.PyQt.QtWidgets import QWidget


site.addsitedir(pathlib.Path(DIR_ENMAPBOX) / 'coreapps')
from reclassifyapp.reclassify import *

class TestEnMAPBoxApplications(EnMAPBoxTestCase):

    def test_createtestdata(self):
        EB = EnMAPBox()
        EB.initEnMAPBoxApplications()
        all_ids = [a.id() for a in QgsApplication.processingRegistry().algorithms()]

        test_algs = [a for a in all_ids if a.startswith('enmapbox:CreateTest')]

        from processing.gui.AlgorithmDialog import AlgorithmDialog
        import time
        for a in test_algs:
            n_before = len(EB.dataSources())
            d = EB.showProcessingAlgorithmDialog(a)
            self.assertIsInstance(d, AlgorithmDialog)
            d.buttonBox().button(QDialogButtonBox.Ok).click()
            time.sleep(2)
            while QgsApplication.taskManager().countActiveTasks() > 0:
                QgsApplication.processEvents()
            QgsApplication.processEvents()
            time.sleep(2)

            n_produced = len(EB.dataSources()) - n_before
            d.buttonBox().button(QDialogButtonBox.Close).click()
            self.assertTrue(n_produced > 0, msg='Algorithm "{}" did not create any data source'.format(a.id()))

        self.showGui(EB.ui)


    def test_UiLibrary(self):
        # Addresses https://bitbucket.org/hu-geomatics/enmap-box/issues/310/attributeerror-function-object-has-no

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


        self.assertTrue(len(speclibDataSources) == speclibCB.count() - 1)




if __name__ == "__main__":
    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'), buffer=False)
