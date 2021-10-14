import unittest

import xmlrunner

from enmapbox.gui.datasources.manager import DataSourceManager, DataSourceManagerPanelUI, DataSourceFactory
from enmapbox.testing import EnMAPBoxTestCase


class DataSourceV2Tests(EnMAPBoxTestCase):

    def setUp(self):
        super().setUp()

    def test_DataSourceModel(self):
        from enmapbox.exampledata import enmap, landcover_polygons, library, enmap_srf_library
        from testdata import classifier_pkl
        from testdata.asd import filenames_binary
        sources = [enmap,
                   enmap,
                   landcover_polygons,
                   landcover_polygons,
                   enmap_srf_library,
                   enmap_srf_library,
                   library,
                   library,
                   classifier_pkl,
                   classifier_pkl,
                   filenames_binary[0],
                   filenames_binary[0]]

        model = DataSourceManager()

        panel = DataSourceManagerPanelUI()
        panel.connectDataSourceManager(model)

        for source in sources:
            dataSources = DataSourceFactory.create(source)
            self.assertIsInstance(dataSources, list)
            model.addDataSources(dataSources)
        self.showGui(panel)

    def test_EnMAPBox(self):

        from enmapbox import EnMAPBox
        emb = EnMAPBox(load_core_apps=True, load_other_apps=True)
        emb.loadExampleData()
        self.showGui(emb.ui)


if __name__ == "__main__":
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'), buffer=False)
