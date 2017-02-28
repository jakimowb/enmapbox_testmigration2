import six, sys, os, gc, re, collections, uuid, logging
logger = logging.getLogger(__name__)
from qgis.core import *
from qgis.gui import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from enmapbox.gui.utils import PanelWidgetBase, loadUI
from osgeo import gdal, ogr
from enmapbox.gui.treeviews import *
from enmapbox.gui.datasources import *

class ProcessingAlgorithmGroup(TreeNode):

    def __init__(self, parent, alg):

        super(ProcessingAlgorithmGroup, self).__init__(parent, '<empty>')


class ProcessingAlgorithm(TreeNode):
    def __init__(self, parent, alg):
        super(ProcessingAlgorithmGroup, self).__init__(parent, '<empty>')


class ProcessingAlgorithmsPanelUI(PanelWidgetBase, loadUI('processingpanel.ui')):

    def __init__(self, parent=None):
        super(ProcessingAlgorithmsPanelUI, self).__init__(parent)

        assert isinstance(self.processingAlgTreeView, TreeView)

    def connectProcessingAlgManager(self, manager):
        if isinstance(manager, ProcessingAlgorithmsManager):
            self.manager = manager
            self.model = ProcessingAlgorithmsTreeModel(self.manager)
            self.processingAlgTreeView.setModel(self.model)
            self.processingAlgTreeView.setMenuProvider(TreeViewMenuProvider(self.processingAlgTreeView))
        else:
            self.manager = None
            self.processingAlgTreeView.setModel(None)


class ProcessingAlgorithmsTreeModel(TreeModel):

    def __init__(self, processingAlgorithmsManager, parent=None):

        super(ProcessingAlgorithmsTreeModel, self).__init__(parent)
        assert isinstance(processingAlgorithmsManager, ProcessingAlgorithmsManager)
        self.processingAlgManager = processingAlgorithmsManager

    def mimeTypes(self):
        # specifies the mime types handled by this model
        types = []
        return types

    def dropMimeData(self, data, action, row, column, parent):
        parentNode = self.index2node(parent)
        assert isinstance(data, QMimeData)

        isL1Node = parentNode.parent() == self.rootNode

        result = False

        return result

    def mimeData(self, indexes):
        indexes = sorted(indexes)
        if len(indexes) == 0:
            return None

        nodesFinal = self.indexes2nodes(indexes, True)
        mimeData = QMimeData()
        #todo: handle processing algorithms related MimeData
        return mimeData


    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        # specify TreeNode specific actions
        node = self.index2node(index)
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable

        if isinstance(node, DataSourceGroupTreeNode):
            flags |= Qt.ItemIsDropEnabled
        elif isinstance(node, DataSourceTreeNode):
            flags |= Qt.ItemIsDragEnabled
        else:
            flags = Qt.NoItemFlags
        return flags

    def contextMenu(self, node):
        menu = QMenu()
        #todo: add node specific menu actions
        return menu

class ProcessingAlgorithmsManager(QObject):

    """
    Keeps overview on QGIS Processing Framework algorithms.
    """


    def __init__(self, enmapBoxInstance):
        super(ProcessingAlgorithmsManager, self).__init__()
        from enmapbox.gui.enmapboxgui import EnMAPBox
        assert isinstance(enmapBoxInstance, EnMAPBox)

        self.enmapbox = enmapBoxInstance

        if isinstance(self.enmapbox.iface, QgisInterface):
            from processing.core.Processing import Processing
            self.algList = Processing.algList








