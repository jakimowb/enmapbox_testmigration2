import six, sys, os, gc, re, collections

from qgis.core import *
from qgis.gui import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from enmapbox.gui.utils import PanelWidgetBase, loadUI, MimeDataHelper
from osgeo import gdal, ogr
from enmapbox.gui.treeviews import *



class DockPanelUI(PanelWidgetBase, loadUI('dockpanel.ui')):
    def __init__(self, parent=None):
        super(DockPanelUI, self).__init__(parent)
        self.dockManager = None
        assert isinstance(self.dockTreeView, TreeView)

        s =""


    def connectDockManager(self, dockManager):
        assert isinstance(dockManager, DockManager)
        self.dockManager = dockManager
        self.dockTreeView.setModel(DockManagerTreeModel(self.dockManager))
        self.dockTreeView.setMenuProvider(TreeViewMenuProvider(self.dockTreeView))

class DockManagerTreeModel(TreeModel):
    def __init__(self, dockManager, parent=None):

        super(DockManagerTreeModel, self).__init__(parent)
        assert isinstance(dockManager, DockManager)
        self.setFlag(QgsLayerTreeModel.ShowLegend, True)
        self.setFlag(QgsLayerTreeModel.ShowSymbology, True)
        #self.setFlag(QgsLayerTreeModel.ShowRasterPreviewIcon, True)
        self.setFlag(QgsLayerTreeModel.ShowLegendAsTree, True)
        self.setFlag(QgsLayerTreeModel.AllowNodeReorder, True)
        self.setFlag(QgsLayerTreeModel.AllowNodeRename, True)
        self.setFlag(QgsLayerTreeModel.AllowNodeChangeVisibility, True)
        self.setFlag(QgsLayerTreeModel.AllowLegendChangeState, True)

        self.dockManager = dockManager
        self.dockManager.sigDockAdded.connect(self.addDockNode)
        self.dockManager.sigDockAdded.connect(lambda : self.sandboxslot2())
        self.dockManager.sigDockRemoved.connect(lambda :self.sandboxslot)
        #dockManager.sigDockRemoved.connect(self.removeDock)
        self.mimeIndices = []


    def sandboxslot(self, dock):
        s  =""
    def sandboxslot2(self):
        s  =""

    def setLayerStyle(self, layer, canvas):
        import enmapbox.gui.layerproperties
        if True: #modal dialog
            enmapbox.gui.layerproperties.showLayerPropertiesDialog(layer, canvas, modal=True)
        else:
            #fix: we could use non-modal dialogs that do not block other windows
            #this requires to store dialogs
            d = enmapbox.gui.layerproperties.showLayerPropertiesDialog(layer, canvas, modal=False)
            global DIALOG
            DIALOG = d
            d.show()

            #d.raise_()
            #d.activateWindow()

    def contextMenu(self, node):
        menu = QMenu()
        parentNode = node.parent()
        if type(node) is QgsLayerTreeLayer:
            #get parent dock node -> related map canvas
            mapNode = self.parentNodesFromIndices(self.node2index(node), nodeInstanceType = MapDockTreeNode)
            mapNode = mapNode[0]
            assert isinstance(mapNode, MapDockTreeNode)
            assert isinstance(mapNode.dock, MapDock)
            canvas = mapNode.dock.canvas

            lyr = node.layer()
            action = QAction('Properties', menu)
            action.triggered.connect(lambda: self.setLayerStyle(lyr, canvas))
            menu.addAction(action)

            action = QAction('Remove', menu)
            action.triggered.connect(lambda: self.removeNode(node))
            menu.addAction(action)

        elif isinstance(node, DockTreeNode):
            # global
            action = QAction('Close', menu)
            action.triggered.connect(lambda :self.removeDockNode(node))
            menu.addAction(action)

        return menu


    def addDockNode(self, dock):
        rootNode = self.rootNode
        newNode = TreeNodeProvider.CreateNodeFromDock(dock, rootNode)
        newNode.sigRemoveMe.connect(lambda : self.removeDockNode(newNode))

    def removeNode(self, node):
        idx = self.node2index(node)
        p = self.index2node(idx.parent())
        p.removeChildNode(node)

    def removeDockNode(self, node):
        self.dockManager.removeDock(node.dock)
        self.removeNode(node)


    def flags(self, parent):
        if not parent.isValid():
            return Qt.NoItemFlags

        #specify TreeNode specific actions
        node = self.index2node(parent)
        if node is None:
            return Qt.NoItemFlags

        isL1 = node.parent() == self.rootNode
        if isinstance(node, DockTreeNode):
            flags = Qt.ItemIsEnabled | \
                    Qt.ItemIsSelectable | \
                    Qt.ItemIsUserCheckable | \
                    Qt.ItemIsEditable
            if isL1:
                flags |= Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsEditable
        elif isinstance(node, QgsLayerTreeNode):
            flags = Qt.ItemIsEnabled | \
                    Qt.ItemIsSelectable | \
                    Qt.ItemIsUserCheckable | \
                    Qt.ItemIsDragEnabled

        else:
            flags = Qt.NoItemFlags
        return flags

    def mimeTypes(self):
        #specifies the mime types handled by this model
        types = [MimeDataHelper.MIME_DOCKTREEMODELDATA,
                 MimeDataHelper.MIME_LAYERTREEMODELDATA,
                 MimeDataHelper.MIME_TEXT_HTML,
                 MimeDataHelper.MIME_TEXT_PLAIN,
                 MimeDataHelper.MIME_URILIST]
        return types

    def dropMimeData(self, mimeData, action, row, column, parent):
        assert isinstance(mimeData, QMimeData)

        MDH = MimeDataHelper(mimeData)
        node = self.index2node(parent)

        #L1 is the first level below the root tree -> to place dock trees
        isL1Node = node.parent() == self.rootNode

        #get parent DockNode
        dockNode = self.parentNodesFromIndices(parent, nodeInstanceType=DockTreeNode)
        if len(dockNode) != 1:
            return False

        dockNode = list(dockNode)[0]

        if action == Qt.MoveAction:
            s = ""

        else:

            s = ""
        if isinstance(dockNode, MapDockTreeNode):
            if MDH.hasLayerTreeModelData():
                nodes = MDH.layerTreeModelNodes()
                if len(nodes) > 0:
                    if parent.isValid() and row == -1:
                        row = 0
                    node.insertChildNodes(row, nodes)
                    return True
            if MDH.hasDataSources():
                dataSources = [ds for ds in MDH.dataSources() if isinstance(ds, DataSourceSpatial)]
                if len(dataSources) > 0:
                    for ds in dataSources:
                        dockNode.addLayer(ds.createMapLayer())

                    return True
        elif isinstance(dockNode, TextDockTreeNode):

            s = ""

        return False

    def mimeData(self, indexes):
        indexes = sorted(indexes)
        self.mimeIndexes = indexes
        if len(indexes) == 0:
            return None

        nodesFinal = self.indexes2nodes(indexes, True)

        mimeData = QMimeData()
        doc = QDomDocument()
        rootElem = doc.createElement("dock_tree_model_data")
        for node in nodesFinal:
            node.writeXML(rootElem)
        doc.appendChild(rootElem)
        mimeData.setData("application/enmapbox.docktreemodeldata", doc.toString())

        mapDockNodes = self.parentNodesFromIndices(indexes, nodeInstanceType=MapDockTreeNode)
        if len(mapDockNodes) > 0:
            doc = QDomDocument()
            rootElem = doc.createElement('layer_tree_model_data')
            for dockNode in mapDockNodes:
                dockNode.writeLayerTreeGroupXML(rootElem)
            doc.appendChild(rootElem)
            mimeData.setData('application/qgis.layertreemodeldata', doc.toString())

        #todo: support any URL

        return mimeData

    def parentNodesFromIndices(self, indices, nodeInstanceType=DockTreeNode):
        """
        Returns all DockNodes contained or parent to the given indices
        :param indices:
        :return:
        """
        results = set()
        if type(indices) is QModelIndex:
            node = self.index2node(indices)
            while node is not None and not isinstance(node, nodeInstanceType):
                node = node.parent()
            if node is not None:
                results.add(node)
        else:
            for ind in indices:
                results.update(self.parentNodesFromIndices(ind, nodeInstanceType=nodeInstanceType))

        return list(results)

    def data(self, index, role ):
        node = self.index2node(index)
        #todo: implement MapDock specific behaviour

        if isinstance(node, DockTreeNode):
            if role == Qt.CheckStateRole:
                if isinstance(node.dock, Dock) and node.dock.isVisible():
                    return Qt.Checked
                else:
                    return Qt.Unchecked
            if role == Qt.DecorationRole:
                return node.icon()

        return super(DockManagerTreeModel, self).data(index, role)

    def setData(self, index, value, role=None):
        node = self.index2node(index)
        parentNode = node.parent()
        if isinstance(node, DockTreeNode) and isinstance(node.dock, Dock):
            if role == Qt.CheckStateRole:
                if value == Qt.Unchecked:
                    node.dock.setVisible(False)
                else:
                    node.dock.setVisible(True)
                return True
            if role == Qt.EditRole:
                node.dock.setTitle(value)

        if type(node) in [QgsLayerTreeLayer, QgsLayerTreeGroup]:

            if role == Qt.CheckStateRole:
                node.setVisible(value)
                mapDockNode = node.parent()
                while mapDockNode is not None and not isinstance(mapDockNode, MapDockTreeNode):
                        mapDockNode = mapDockNode.parent()

                assert isinstance(mapDockNode, MapDockTreeNode)
                mapDockNode.updateCanvas()


        return False


class DockManager(QgsLegendInterface):
    """
    Class to handle all DOCK related events
    """

    sigDockAdded = pyqtSignal(Dock)
    sigDockRemoved = pyqtSignal(Dock)
    sigDockTitleChanged = pyqtSignal(Dock)

    def __init__(self, enmapbox):
        QObject.__init__(self)
        self.enmapbox = enmapbox
        self.dockarea = self.enmapbox.ui.dockarea
        self.DOCKS = list()

        self.connectDockArea(self.dockarea)
        self.setCursorLocationValueDock(None)

    def connectDockArea(self, dockArea):
        assert isinstance(dockArea, DockArea)
        dockArea.sigDragEnterEvent.connect(lambda event : self.dockAreaSignalHandler(dockArea, event))
        dockArea.sigDragMoveEvent.connect(lambda event : self.dockAreaSignalHandler(dockArea, event))
        dockArea.sigDragLeaveEvent.connect(lambda event : self.dockAreaSignalHandler(dockArea, event))
        dockArea.sigDropEvent.connect(lambda event : self.dockAreaSignalHandler(dockArea, event))

    def dockAreaSignalHandler(self, dockArea, event):
        assert isinstance(dockArea, DockArea)
        assert isinstance(event, QEvent)

        mimeTypes = ["application/qgis.layertreemodeldata",
                     "application/enmapbox.docktreemodeldata",
                     "application/enmapbox.datasourcetreemodeldata",
                     "text/uri-list"]

        if type(event) is QDragEnterEvent:
            # check mime types we can handle
            MH = MimeDataHelper(event.mimeData())
            if MH.hasMapLayers() or MH.hasDataSources():
                    event.setDropAction(Qt.CopyAction)
                    event.accept()
            else:
                event.ignore()

        elif type(event) is QDragMoveEvent:
            pass
        elif type(event) is QDragLeaveEvent:
            pass
        elif type(event) is QDropEvent:
            MH = MimeDataHelper(event.mimeData())
            layers = []
            textfiles = []

            if MH.hasMapLayers():
                layers = MH.mapLayers()
            elif MH.hasDataSources():
                for ds in MH.dataSources():
                    layers.append(ds.createMapLayer())

            #register datasources
            for src in layers + textfiles:
                self.enmapbox.dataSourceManager.addSource(src)

            #open map dock for new layers
            if len(layers) > 0:

                NEW_MAP_DOCK = self.createDock('MAP')
                NEW_MAP_DOCK.addLayers(layers)

                event.setDropAction(Qt.CopyAction)
                event.dropAction()




    def getDockWithUUID(self, uuid_):
        if isinstance(uuid_, str):
            uuid_ = uuid.UUID(uuid_)
        assert isinstance(uuid_, uuid.UUID)
        for dock in list(self.DOCKS):
            assert isinstance(dock, Dock)
            if dock.uuid == uuid_:
                return dock

        return None

    def showCursorLocationValues(self, *args):
        if self.cursorLocationValueDock is not None:
            self.cursorLocationValueDock.showLocationValues(*args)


    def setCursorLocationValueDock(self, dock):
        if dock is None:
            self.cursorLocationValueDock = None
        else:
            assert isinstance(dock, CursorLocationValueDock)
            self.cursorLocationValueDock = dock
            self.cursorLocationValueDock.w.connectDataSourceManager(self.enmapbox.dataSourceManager)
            dock.sigClosed.connect(lambda: self.setCursorLocationValueDock(None))

    def removeDock(self, dock):
        if dock in self.DOCKS:
            self.DOCKS.remove(dock)
            self.sigDockRemoved.emit(dock)
            return True
        return False

    def createDock(self, docktype, *args, **kwds):

        #set default kwds
        kwds['name'] = kwds.get('name', '#{}'.format(len(self.DOCKS) + 1))

        is_new_dock = True
        if docktype == 'MAP':
            dock = MapDock(self.enmapbox, *args, **kwds)
            dock.sigCursorLocationValueRequest.connect(self.showCursorLocationValues)
        elif docktype == 'TEXT':
            dock = TextDock(self.enmapbox, *args, **kwds)
        elif docktype == 'MIME':
            dock = MimeDataDock(self.enmapbox, *args, **kwds)
        elif docktype == 'CURSORLOCATIONVALUE':
            if self.cursorLocationValueDock is None:
                self.setCursorLocationValueDock(CursorLocationValueDock(self.enmapbox, *args, **kwds))
            else:
                is_new_dock = False
            dock = self.cursorLocationValueDock
        else:
            raise Exception('Unknown dock type: {}'.format(docktype))

        dockArea = kwds.get('dockArea', self.dockarea)
        state = dockArea.saveState()
        main = state['main']
        if is_new_dock:
            dock.sigClosed.connect(self.removeDock)
            self.DOCKS.append(dock)
            self.dockarea.addDock(dock, *args, **kwds)
            self.sigDockAdded.emit(dock)

            if 'initSrc' in kwds.keys():
                ds = self.enmapbox.addSource(kwds['initSrc'])
                if isinstance(ds, DataSourceSpatial):
                    dock.addLayers(ds.createMapLayer())

        return dock

    """
    QgsLegendInterface() Slots
    """
    def refreshLayerSymbology(self, mapLayer):
        pass

    def removeGroup(self, p_int):
        pass

    def removeLegendLayerAction(self, QAction):
        pass

    def moveLayer(self, QgsMapLayer, p_int):
        pass
