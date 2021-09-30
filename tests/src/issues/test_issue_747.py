
import unittest
import xmlrunner

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

    def test_issue_747(self):
        """
        Collapsing parent nodes crashes TreeView
        How to reproduce
        1. Show Widget
        2. Expand nodes 'Models', 'classification_dataset.pkl', 'dict', 'X', 'array'
           (below 'classification_dataset.pkl' will be fetched on demand)
        3. unexpand 'X'

        - happens with TreeView but not QTreeView
        - seems to be related to TreeView.setColumnSpan
        - automatic column span is necessary to save space
        """
        mgr = DataSourceManager()
        model = DataSourceManagerTreeModel(None, mgr)

        tv = TreeView()
        # tv = QTreeView()
        tv.setUniformRowHeights(True)
        tv.setIndentation(12)
        tv.setAutoExpansionDepth(10)
        tv.setModel(model)

        # set False to avoid error
        tv.setAutoFirstColumnSpan(True)

        from testdata import classification_dataset_pkl
        self.assertIsInstance(tv, QTreeView)
        mgr.addSource(classification_dataset_pkl)

        node = model.rootNode().findChildNodes(HubFlowPyObjectTreeNode, recursive=True)
        self.assertTrue(len(node) == 1)
        node = node[0]
        # tv.expandRecursively(QModelIndex(), 4)
        # dict X array
        self.assertIsInstance(node, HubFlowPyObjectTreeNode)
        NODES = dict(ROOT=node)

        for name in ['dict', 'X', 'array']:

            node.fetch()
            # tv.expand(model.node2idx(node))
            node = node.findChildNodes(PyObjectTreeNode, name)[0]
            NODES[name] = node

        # tv.expand(model.node2idx(node))
        tv.resize(QSize(600, 600))
        tv.show()
        s  =""

        self.showGui(tv)


if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'), buffer=False)
