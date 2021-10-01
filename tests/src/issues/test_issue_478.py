

import unittest
import xmlrunner
from qgis.core import QgsProject, QgsMapLayer, QgsRasterLayer, QgsVectorLayer, \
    QgsLayerTree, QgsProcessingAlgorithm, QgsProcessingParameterRasterLayer, QgsProcessingParameterDefinition
from qgis.gui import QgisInterface
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsApplication
from qgis.PyQt.QtCore import QResource
from enmapbox.testing import TestObjects, EnMAPBoxTestCase
from enmapbox.gui.enmapboxgui import EnMAPBox, EnMAPBoxSplashScreen
from enmapbox.gui.docks import *
from enmapbox.gui.mapcanvas import *
from enmapbox.gui import *


class TestIssue(EnMAPBoxTestCase):

    def tearDown(self):

        emb = EnMAPBox.instance()
        if isinstance(emb, EnMAPBox):
            emb.close()

        assert EnMAPBox.instance() is None

        QgsProject.instance().removeAllMapLayers()

        super().tearDown()

    def test_issue478(self):
        # https://bitbucket.org/hu-geomatics/enmap-box/issues/478/visualization-of-single-band-fails
        # test if sources can be opened in a new map
        EB = EnMAPBox(load_core_apps=False, load_other_apps=False)
        from enmapbox.exampledata import enmap

        from enmapbox.testing import TestObjects
        from enmapbox.gui.datasourcemanager import DataSourceTreeView
        EB.addSource(enmap)
        wms = TestObjects.uriWMS()
        EB.addSource(wms)
        tv = EB.dataSourceTreeView()
        self.assertIsInstance(tv, DataSourceTreeView)
        for src in EB.dataSourceManager().sources('RASTER'):
            tv.openInMap(src, rgb=[0])
            self.assertIsInstance(tv, QTreeView)

        self.showGui(EB.ui)


if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'), buffer=False)