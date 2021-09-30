import unittest
import xmlrunner

from enmapbox.externals.qps.speclib.core.spectrallibrary import SpectralLibraryUtils
from enmapbox.gui.datasourcemanager import DataSourceTreeView, DataSourceManagerTreeModel, DataSourceManager, \
    HubFlowPyObjectTreeNode
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

    def test_issue_724(self):

        from enmapbox import registerEditorWidgets
        registerEditorWidgets()

        path = pathlib.Path('~').expanduser() / 'Downloads' / 'library.gpkg'
        self.assertTrue(path.is_file())

        from enmapbox.externals.qps.speclib.core import EDITOR_WIDGET_REGISTRY_KEY
        filename = path.as_posix()
        reg: QgsEditorWidgetRegistry = QgsGui.editorWidgetRegistry()

        vl = QgsVectorLayer(filename)
        sl1 = SpectralLibraryUtils.readFromSource(filename)
        sl2 = SpectralLibrary(filename)
        slRef = TestObjects.createSpectralLibrary()
        for lyr in [vl, sl1, sl2, slRef]:
            self.assertIsInstance(lyr, QgsVectorLayer)
            self.assertTrue(lyr.featureCount() > 0)
            print(f'{lyr.id()}:{lyr.source()}')
            print(f'type: {lyr.fields().field("profiles").typeName()}')
            print(f'editor: {lyr.fields().field("profiles").editorWidgetSetup().type()}')

        # self.assertTrue(vl.fields().field('profiles').editorWidgetSetup().type() == '')
        self.assertEqual(sl1.fields().field('profiles').editorWidgetSetup().type(), EDITOR_WIDGET_REGISTRY_KEY)
        self.assertEqual(sl2.fields().field('profiles').editorWidgetSetup().type(), EDITOR_WIDGET_REGISTRY_KEY)


if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'), buffer=False)
