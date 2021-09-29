
import unittest
import xmlrunner

from enmapbox.gui.datasourcemanager import DataSourceTreeView
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

    def test_issue_672(self):

        tv = DataSourceTreeView()
        tv.setDa
        self.assertIsInstance(tv, DataSourceTreeView)
        for src in EB.dataSourceManager().sources('RASTER'):
            tv.openInMap(src, rgb=[0])
            self.assertIsInstance(tv, QTreeView)

        self.showGui(EB.ui)


if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'), buffer=False)
