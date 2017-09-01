import six, sys, os, gc, re, collections

from qgis.core import *
from qgis.gui import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from enmapbox.gui.utils import PanelWidgetBase, loadUI, MimeDataHelper
from osgeo import gdal, ogr
from enmapbox.gui.treeviews import *
from enmapbox.gui.mapcanvas import MapCanvas, CanvasLink, MapDock
from enmapbox.gui.utils import *

class DockTreeNode(TreeNode):
    @staticmethod
    def readXml(element):
        if element.tagName() != 'dock-tree-node':
            return None

        node = DockTreeNode(None, None)
        dockName = element.attribute('name')
        node.setName(dockName)
        node.setExpanded(element.attribute('expanded') == '1')
        node.setVisible(QgsLayerTreeUtils.checkStateFromXml(element.attribute("checked")))
        node.readCommonXML(element)
        # node.readChildrenFromXml(element)

        # try to find the dock by its uuid in dockmanager
        from enmapbox.gui.enmapboxgui import EnMAPBox

        dockManager = EnMAPBox.instance().dockManager
        uuid = node.customProperty('uuid', None)
        if uuid:
            dock = dockManager.getDockWithUUID(str(uuid))

        if dock is None:
            dock = dockManager.createDock('MAP', name=dockName)
        node.connectDock(dock)

        return node

    """
    Base TreeNode to symbolise a Dock
    """
    sigDockUpdated = pyqtSignal()
    def __init__(self, parent, dock):
        self.dock = dock
        super(DockTreeNode, self).__init__(parent, '<dockname not available>')

        self.mIcon = QIcon(':/enmapbox/icons/viewlist_dock.png')
        if isinstance(dock, Dock):
            self.connectDock(dock)

    def writeXML(self, parentElement):
        elem = super(DockTreeNode, self).writeXML(parentElement)
        elem.setTagName('dock-tree-node')
        return elem

    def writeLayerTreeGroupXML(self, parentElement):
        QgsLayerTreeGroup.writeXML(self, parentElement)

        # return super(QgsLayerTreeNode,self).writeXml(parentElement)

    def connectDock(self, dock):
        if isinstance(dock, Dock):
            self.dock = dock
            self.setName(dock.title())
            self.dock.sigTitleChanged.connect(self.setName)
            #self.dock.sigVisibilityChanged.connec(self.)
            self.setCustomProperty('uuid', str(dock.uuid))
            # self.dock.sigClosed.connect(self.removedisconnectDock)


class TextDockTreeNode(DockTreeNode):
    def __init__(self, parent, dock):
        assert isinstance(dock, TextDock)
        super(TextDockTreeNode, self).__init__(parent, dock)
        self.setIcon(QIcon(IconProvider.Dock))

    def writeXML(self, parentElement):
        return super(MapDockTreeNode, self).writeXML(parentElement, 'text-dock-tree-node')

class CanvasLinkTreeNode(TreeNode):
    def __init__(self, parent, canvasLink, name, **kwds):
        assert isinstance(canvasLink, CanvasLink)
        kwds['icon'] = canvasLink.icon()
        super(CanvasLinkTreeNode, self).__init__(parent, name, **kwds)
        self.canvasLink = canvasLink

    def contextMenu(self):
        m = QMenu()
        a = m.addAction('Remove')
        a.setToolTip('Removes this link.')
        a.triggered.connect(self.canvasLink.removeMe)
        return m



class CanvasLinkTreeNodeGroup(TreeNode):
    """
    A node to show links between difference canvases
    """
    def __init__(self, parent, canvas):
        assert isinstance(canvas, MapCanvas)
        super(CanvasLinkTreeNodeGroup, self).__init__(parent, 'Spatial Links',
                                                      icon=QIcon(":/enmapbox/icons/link_basic.png"))

        self.canvas = canvas
        self.canvas.sigCanvasLinkAdded.connect(self.addCanvasLink)
        self.canvas.sigCanvasLinkRemoved.connect(self.removeCanvasLink)


    def addCanvasLink(self, canvasLink):
        assert isinstance(canvasLink, CanvasLink)
        from enmapbox.gui.utils import findParent
        theOtherCanvas = canvasLink.theOtherCanvas(self.canvas)
        theOtherDock = findParent(theOtherCanvas, Dock, checkInstance=True)
        linkNode = CanvasLinkTreeNode(self, canvasLink, '<no name>', icon=canvasLink.icon())
        if isinstance(theOtherDock, Dock):
            name = theOtherDock.title()
            theOtherDock.sigTitleChanged.connect(linkNode.setName)
        else:
            name = str(theOtherCanvas)
        linkNode.setName(name)

    def removeCanvasLink(self, canvasLink):
        assert isinstance(canvasLink, CanvasLink)
        theOtherCanvas = canvasLink.theOtherCanvas(self.canvas)
        toRemove = [c for c in self.children() if isinstance(c, CanvasLinkTreeNode) and c.canvasLink == canvasLink]
        for node in toRemove:
            if node.canvasLink in node.canvasLink.canvases:
                #need to be deleted from other listeners first
                node.canvasLink.removeMe()
            else:
                self.removeChildNode(node)

class SpeclibDockTreeNode(DockTreeNode):
    def __init__(self, parent, dock):

        super(SpeclibDockTreeNode, self).__init__(parent, dock)
        self.setIcon(QIcon(':/enmapbox/icons/viewlist_spectrumdock.png'))



    def connectDock(self, dock):
        assert isinstance(dock, SpectralLibraryDock)
        super(SpeclibDockTreeNode, self).connectDock(dock)
        from enmapbox.gui.spectrallibraries import SpectralLibraryWidget
        self.SLW = dock.SLV
        assert isinstance(self.SLW, SpectralLibraryWidget)

        self.profilesNode = TreeNode(self, 'Profiles', value=0)
        self.SLW.mSpeclib.sigProfilesAdded.connect(self.updateNodes)
        self.SLW.mSpeclib.sigProfilesRemoved.connect(self.updateNodes)


    def updateNodes(self):
        from enmapbox.gui.spectrallibraries import SpectralLibraryWidget
        assert isinstance(self.SLW, SpectralLibraryWidget)
        self.profilesNode.setValue(len(self.SLW.mSpeclib))




class MapDockTreeNode(DockTreeNode):
    """
    A TreeNode linked to a MapDock
    Acts like the QgsLayerTreeMapCanvasBridge
    """

    def __init__(self, parent, dock):

        super(MapDockTreeNode, self).__init__(parent, dock)
        #KeepRefs.__init__(self)
        self.setIcon(QIcon(':/enmapbox/icons/viewlist_mapdock.png'))
        self.addedChildren.connect(lambda: self.updateCanvas())
        self.removedChildren.connect(lambda: self.updateCanvas())

    def connectDock(self, dock):
        assert isinstance(dock, MapDock)
        super(MapDockTreeNode, self).connectDock(dock)
        #TreeNode(self, 'Layers')
        self.layerNode = QgsLayerTreeGroup('Layers')
        self.addChildNode(self.layerNode)
        #self.layerNode = TreeNode(self, 'Layers')

        self.crsNode = CRSTreeNode(self, dock.canvas.mapSettings().destinationCrs())
        self.crsNode.setExpanded(False)

        self.linkNode = CanvasLinkTreeNodeGroup(self, dock.canvas)
        self.linkNode.setExpanded(False)

        self.dock.sigLayersAdded.connect(self.updateChildNodes)
        self.dock.sigLayersRemoved.connect(self.updateChildNodes)
        self.dock.sigCrsChanged.connect(self.crsNode.setCrs)
        self.updateChildNodes()

    def onAddedChildren(self, node, idxFrom, idxTo):
        self.updateCanvas()

    def onRemovedChildren(self, node, idxFrom, idxTo):
        self.updateCanvas()

    def updateChildNodes(self):
        """
        Compares the linked map canvas with layers in the tree node tree
        If required, missing layers will be added to the tree node
        :return:
        """
        if self.dock:
            canvasLayers = self.dock.layers()
            treeNodeLayerNodes = self.layerNode.findLayers()
            treeNodeLayers = [n.layer() for n in treeNodeLayerNodes]

            # new layers to add?
            newChildLayers = [l for l in canvasLayers if l not in treeNodeLayers]

            # layers to set visible?
            for layer in canvasLayers:
                if layer not in treeNodeLayers:
                    # insert layer on top of layer tree
                    self.layerNode.insertLayer(0, layer)

                # set canvas on visible
                lNode = self.layerNode.findLayer(layer.id())
                lNode.setVisible(Qt.Checked)

        return self

    def updateCanvas(self):
        # reads the nodes and sets the map canvas accordingly
        if self.dock:
            # update canvas only in case of different layerset
            visible = self.dock.layers()
            layers = MapDockTreeNode.visibleLayers(self)
            if len(visible) != len(layers) or \
                    any(l1 != l2 for l1, l2 in zip(visible, layers)):
                self.dock.setLayers(layers)
        return self

    @staticmethod
    def visibleLayers(node):
        """
        Returns the QgsMapLayers from all sub-nodes the are set as 'visible'
        :param node:
        :return:
        """
        lyrs = []
        if isinstance(node, list):
            for child in node:
                lyrs.extend(MapDockTreeNode.visibleLayers(child))

        elif isinstance(node, QgsLayerTreeGroup):
            for child in node.children():
                lyrs.extend(MapDockTreeNode.visibleLayers(child))

        elif isinstance(node, QgsLayerTreeLayer):
            if node.isVisible() == Qt.Checked:
                lyr = node.layer()
                if isinstance(lyr, QgsMapLayer):
                    lyrs.append(lyr)
                else:
                    logger.warning('QgsLayerTreeLayer.layer() is none')
        else:
            raise NotImplementedError()

        for l in lyrs:
            assert isinstance(l, QgsMapLayer), l

        return lyrs

    def removeLayerNodesByURI(self, uri):

        toRemove = []
        for lyrNode in self.findLayers():
            uriLyr = str(lyrNode.layer().dataProvider().dataSourceUri())
            if uriLyr == uri:
                toRemove.append(lyrNode)

        for node in toRemove:
            node.parent().removeChildNode(node)


    def insertLayer(self, idx, layer):
        """
        Inserts a new QgsMapLayer on position idx by creating a new QgsMayTreeLayer node
        :param idx:
        :param layer:
        :return:
        """
        assert isinstance(layer, QgsMapLayer)
        QgsMapLayerRegistry.instance().addMapLayer(layer)
        ll = QgsLayerTreeLayer(layer)
        self.layerNode.insertChildNode(idx, ll)
        return ll

    def writeXML(self, parentElement):
        elem = super(MapDockTreeNode, self).writeXML(parentElement)
        elem.setTagName('map-dock-tree-node')

    @staticmethod
    def readXml(element):
        if element.tagName() != 'map-dock-tree-node':
            return None

        from enmapbox.gui.enmapboxgui import EnMAPBox
        DSM = EnMAPBox.instance().dataSourceManager

        node = MapDockTreeNode(None, None)
        node.setName(element.attribute('name'))
        node.setExpanded(element.attribute('expanded') == '1')
        node.setVisible(QgsLayerTreeUtils.checkStateFromXml(element.attribute("checked")))
        node.readCommonXML(element)
        # node.readChildrenFromXml(element)

        # try to find the dock by its uuid in dockmanager
        dockManager = EnMAPBox.instance().dockManager
        uuid = node.customProperty('uuid', None)
        if uuid:
            dock = dockManager.getDockWithUUID(str(uuid))
        if dock is None:
            dock = dockManager.createDock('MAP', name=node.name())
        node.connectDock(dock)
        return node


class DockPanelUI(PanelWidgetBase, loadUI('dockpanel.ui')):
    def __init__(self, parent=None):
        super(DockPanelUI, self).__init__(parent)
        self.dockManager = None
        assert isinstance(self.dockTreeView, TreeView)

        s =""


    def connectDockManager(self, dockManager):
        assert isinstance(dockManager, DockManager)
        self.dockManager = dockManager
        self.model = DockManagerTreeModel(self.dockManager)
        self.dockTreeView.setModel(self.model)
        assert self.model == self.dockTreeView.model()
        self.menuProvider = DockManagerTreeModelMenuProvider(self.dockTreeView)
        self.dockTreeView.setMenuProvider(self.menuProvider)
        s = ""

class DockManagerTreeModel(TreeModel):
    def __init__(self, dockManager, parent=None):

        super(DockManagerTreeModel, self).__init__(parent)
        assert isinstance(dockManager, DockManager)
        self.columnNames = ['Dock/Property','Value']
        if True:
            """
             // display flags
              ShowLegend                 = 0x0001,  //!< Add legend nodes for layer nodes
              ShowRasterPreviewIcon      = 0x0002,  //!< Will use real preview of raster layer as icon (may be slow)
              ShowLegendAsTree           = 0x0004,  //!< For legends that support it, will show them in a tree instead of a list (needs also ShowLegend). Added in 2.8
              DeferredLegendInvalidation = 0x0008,  //!< Defer legend model invalidation
              UseEmbeddedWidgets         = 0x0010,  //!< Layer nodes may optionally include extra embedded widgets (if used in QgsLayerTreeView). Added in 2.16

              // behavioral flags
              AllowNodeReorder           = 0x1000,  //!< Allow reordering with drag'n'drop
              AllowNodeRename            = 0x2000,  //!< Allow renaming of groups and layers
              AllowNodeChangeVisibility  = 0x4000,  //!< Allow user to set node visibility with a check box
              AllowLegendChangeState     = 0x80
            """
            self.setFlag(QgsLayerTreeModel.ShowLegend, True)
            self.setFlag(QgsLayerTreeModel.ShowRasterPreviewIcon, False)
            self.setFlag(QgsLayerTreeModel.ShowLegendAsTree, True)
            self.setFlag(QgsLayerTreeModel.DeferredLegendInvalidation, True)
            #self.setFlag(QgsLayerTreeModel.UseEmbeddedWidget, True)

            #behavioral
            self.setFlag(QgsLayerTreeModel.AllowNodeReorder, True)
            self.setFlag(QgsLayerTreeModel.AllowNodeRename, True)
            self.setFlag(QgsLayerTreeModel.AllowNodeChangeVisibility, True)
            self.setFlag(QgsLayerTreeModel.AllowLegendChangeState, True)
            #self.setFlag(QgsLayerTreeModel.ActionHierarchical, False)

        self.dockManager = dockManager
        self.dockManager.sigDockAdded.connect(self.addDock)
        self.dockManager.sigDockRemoved.connect(self.removeDock)
        self.dockManager.sigDataSourceRemoved.connect(self.removeDataSource)
        self.mimeIndices = []

    def columnCount(self, index):
        node = self.index2node(index)
        if type(node) in [DockTreeNode, QgsLayerTreeGroup, QgsLayerTreeLayer]:
            return 1
        elif isinstance(node, TreeNode):
            return 2
        else:
            return 1

    def removeDataSource(self, dataSource):
        for node in self.rootNode.children():
            if isinstance(node, MapDockTreeNode):
                node.removeLayerNodesByURI(dataSource.uri())
                s = ""
        s = ""


    def supportedDragActions(self):
        return Qt.CopyAction | Qt.MoveAction

    def supportedDropActions(self):
        return Qt.CopyAction | Qt.MoveAction

    def addDock(self, dock):
        newNode = TreeNodeProvider.CreateNodeFromDock(dock, self.rootNode)
        s = ""

    def removeDock(self, dock):
        rootNode = self.rootNode
        to_remove = [n for n in rootNode.children() if n.dock == dock]
        for node in to_remove:
            self.removeDockNode(node)

    def removeNode(self, node):
        idx = self.node2index(node)
        p = self.index2node(idx.parent())
        p.removeChildNode(node)

    def removeDockNode(self, node):
        self.dockManager.removeDock(node.dock)
        self.removeNode(node)


    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags



        node = self.index2node(index)
        dockNode = self.parentNodesFromIndices(index, nodeInstanceType=DockTreeNode)
        if len(dockNode) == 0:
            return Qt.NoItemFlags

        if node is None:
            return Qt.NoItemFlags

        column = index.column()
        isL1 = node.parent() == self.rootNode
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable

        #normal tree nodes
        if isinstance(node, TreeNode):
            if column == 0:
                if isinstance(node, DockTreeNode):
                    flags |= Qt.ItemIsUserCheckable | \
                             Qt.ItemIsEditable | \
                             Qt.ItemIsDropEnabled
                    if isL1:
                        flags |= Qt.ItemIsDropEnabled
                if isinstance(node.parent(), MapDockTreeNode) and node.name() == 'Layers':
                    flags |= Qt.ItemIsUserCheckable
        #mapCanvas Layer Tree Nodes
        elif type(node) in [QgsLayerTreeLayer, QgsLayerTreeGroup]:
            if column == 0:
                flags |= Qt.ItemIsUserCheckable | Qt.ItemIsEditable | Qt.ItemIsDropEnabled

                if not (isinstance(dockNode, MapDockTreeNode) and node == dockNode.layerNode):
                    flags |= Qt.ItemIsDragEnabled


        return flags

    def mimeTypes(self):
        #specifies the mime types handled by this model
        types = [MimeDataHelper.MDF_DOCKTREEMODELDATA,
                 MimeDataHelper.MDF_LAYERTREEMODELDATA,
                 MimeDataHelper.MDF_TEXT_HTML,
                 MimeDataHelper.MDF_TEXT_PLAIN,
                 MimeDataHelper.MDF_URILIST,
                 MimeDataHelper.MDF_PYTHON_OBJECTS]
        return types

    def dropMimeData(self, mimeData, action, row, column, parentIndex):
        assert isinstance(mimeData, QMimeData)

        MDH = MimeDataHelper(mimeData)


        if not parentIndex.isValid():
            return False

        parentNode = self.index2node(parentIndex)
        # L1 is the first level below the root tree -> to place dock trees
        isL1Node = parentNode.parent() == self.rootNode

        #get parent DockNode
        dockNode = self.parentNodesFromIndices(parentIndex, nodeInstanceType=DockTreeNode)

        if len(dockNode) != 1:
            return False
        else:
            dockNode = dockNode[0]


        if isinstance(dockNode, MapDockTreeNode):
            if MDH.hasLayerTreeModelData():
                nodes = MDH.layerTreeModelNodes()
                if len(nodes) > 0:
                    if type(parentNode) != QgsLayerTreeGroup:
                        layerNode = dockNode.layerNode
                    else:
                        layerNode = parentNode

                    #insert layertree-nodes to parentNode
                    if row == -1:
                        row = 0
                    layerNode.insertChildNodes(row, nodes)
                    return True

            if MDH.hasDataSources():
                dataSources = [ds for ds in MDH.dataSources() if isinstance(ds, DataSourceSpatial)]
                if len(dataSources) > 0:
                    layers = reversed([ds.createUnregisteredMapLayer() for ds in dataSources])
                    for l in layers:
                        dockNode.insertLayer(0,l)
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



        #docktree to mime data
        from enmapbox.gui.utils import EnMAPBoxMimeData
        mimeData = QMimeData()
        #MimeDataHelper.storeObjectReferences(mimeData, nodesFinal)

        doc = QDomDocument()
        rootElem = doc.createElement("dock_tree_model_data")
        for node in nodesFinal:
            node.writeXML(rootElem)
        doc.appendChild(rootElem)
        mimeData.setData("application/enmapbox.docktreemodeldata", doc.toString())

        # layertree to mime data
        mapDockNodes = self.parentNodesFromIndices(indexes, nodeInstanceType=MapDockTreeNode)
        if len(mapDockNodes) > 0:
            doc = QDomDocument()
            rootElem = doc.createElement('layer_tree_model_data')
            for dockNode in mapDockNodes:
                dockNode.writeLayerTreeGroupXML(rootElem)
            doc.appendChild(rootElem)
            mimeData.setData('application/qgis.layertreemodeldata', doc.toString())


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
        if not index.isValid():
            return None

        node = self.index2node(index)

        column = index.column()

        if not isinstance(node, TreeNode):
            if type(node) in [QgsLayerTreeLayer, QgsLayerTreeGroup]:
                if column == 1:
                    if role in [Qt.DisplayRole, Qt.EditRole]:
                        return node.name()
                    else:
                        return super(DockManagerTreeModel, self).data(index, role)
                else:
                    return super(DockManagerTreeModel, self).data(index, role)
            else:
                return super(DockManagerTreeModel, self).data(index, role)

        else:

            if column == 0:

                if role in [Qt.DisplayRole, Qt.EditRole]:
                    return node.name()
                if role == Qt.DecorationRole:
                    return node.icon()
                if role == Qt.ToolTipRole:
                    return node.tooltip()
                if role == Qt.CheckStateRole:
                    if isinstance(node, DockTreeNode):
                        if isinstance(node.dock, Dock):
                            return Qt.Checked if node.dock.isVisible() else Qt.Unchecked
            else:
                if role == Qt.DisplayRole:
                    return node.value()

        return None
            #return super(DockManagerTreeModel, self).data(index, role)

    def setData(self, index, value, role=None):
        node = self.index2node(index)
        parentNode = node.parent()

        result = False
        if isinstance(node, DockTreeNode) and isinstance(node.dock, Dock):
            if role == Qt.CheckStateRole:
                if value == Qt.Unchecked:
                    node.dock.setVisible(False)
                else:
                    node.dock.setVisible(True)
                result = True
            if role == Qt.EditRole and len(value) > 0:
                node.dock.setTitle(value)
                result = True

        if type(node) in [QgsLayerTreeLayer, QgsLayerTreeGroup]:

            if role == Qt.CheckStateRole:
                node.setVisible(value)
                mapDockNode = node.parent()
                while mapDockNode is not None and not isinstance(mapDockNode, MapDockTreeNode):
                        mapDockNode = mapDockNode.parent()

                assert isinstance(mapDockNode, MapDockTreeNode)
                mapDockNode.updateCanvas()
                result = True
            if role == Qt.EditRole:
                if isinstance(node, QgsLayerTreeLayer):
                    node.setName(value)
                    node.setLayerName(value)
                    result = True
                if isinstance(node, QgsLayerTreeGroup):
                    node.setName(value)
                    result = True

        if result:
            self.dataChanged.emit(index, index)
        return result


class DockManagerTreeModelMenuProvider(TreeViewMenuProvider):

    def __init__(self, treeView):
        super(DockManagerTreeModelMenuProvider, self).__init__(treeView)
        assert isinstance(self.treeView.model(), DockManagerTreeModel)

    def createContextMenu(self):
        col = self.currentIndex().column()
        node = self.currentNode()
        parentNode = node.parent()
        parentDockNode = findParent(node, DockTreeNode, checkInstance=True)
        menu = QMenu()
        if type(node) is QgsLayerTreeLayer:
            # get parent dock node -> related map canvas
            mapNode = findParent(node, MapDockTreeNode)
            assert isinstance(mapNode, MapDockTreeNode)
            assert isinstance(mapNode.dock, MapDock)
            canvas = mapNode.dock.canvas

            lyr = node.layer()
            action = menu.addAction('Layer properties')
            action.setToolTip('Set layer properties')
            action.triggered.connect(lambda: self.setLayerStyle(lyr, canvas))

            action = menu.addAction('Remove layer')
            action.setToolTip('Removes layer from map canvas')
            action.triggered.connect(lambda: parentNode.removeChildNode(node))

            action = menu.addAction('Set layer CRS to map canvas')
            action.triggered.connect(lambda: canvas.setDestinationCrs(lyr.crs()))

            action = menu.addAction('Copy layer path')
            action.triggered.connect(lambda: QApplication.clipboard().setText(lyr.source()))

        elif isinstance(node, DockTreeNode):
            assert isinstance(node.dock, Dock)
            from enmapbox.gui.utils import appendItemsToMenu
            return node.dock.contextMenu()

        elif isinstance(node, TreeNode):
            if col == 0:
                menu = node.contextMenu()
            elif col == 1:
                menu = QMenu()
                a = menu.addAction('Copy')
                a.triggered.connect(lambda : QApplication.clipboard().setText(str(node.value())))




        return menu

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


class DockManager(QgsLegendInterface):
    """
    Class to handle all DOCK related events
    """

    sigDockAdded = pyqtSignal(Dock)
    sigDockRemoved = pyqtSignal(Dock)
    sigDockTitleChanged = pyqtSignal(Dock)
    sigDataSourceRemoved = pyqtSignal(DataSource)

    def __init__(self):
        QObject.__init__(self)
        self.mConnectedDockAreas = []
        self.mCurrentDockArea = None
        self.mDocks = list()
        self.dataSourceManager = None

    def activateMapTool(self, key):

        for dock in self.mDocks:
            if isinstance(dock, MapDock):
                dock.activateMapTool(key)


    def connectDataSourceManager(self, dataSourceManager):
        from enmapbox.gui.datasourcemanager import DataSourceManager
        assert isinstance(dataSourceManager, DataSourceManager)
        self.dataSourceManager = dataSourceManager
        pass


    def removeDataSource(self, dataSource):
        """
        Remove dependencies to removed data sources
        :param dataSource:
        :return:
        """
        if isinstance(dataSource, DataSourceSpatial):
            for mapDock in [d for d in self.mDocks if isinstance(d, MapDock)]:
                mapDock.removeLayersByURI(dataSource.uri())


        self.sigDataSourceRemoved.emit(dataSource)

    def connectDockArea(self, dockArea):
        assert isinstance(dockArea, DockArea)

        dockArea.sigDragEnterEvent.connect(lambda event : self.onDockAreaDragDropEvent(dockArea, event))
        dockArea.sigDragMoveEvent.connect(lambda event : self.onDockAreaDragDropEvent(dockArea, event))
        dockArea.sigDragLeaveEvent.connect(lambda event : self.onDockAreaDragDropEvent(dockArea, event))
        dockArea.sigDropEvent.connect(lambda event : self.onDockAreaDragDropEvent(dockArea, event))
        self.mConnectedDockAreas.append(dockArea)

    def currentDockArea(self):
        if self.mCurrentDockArea not in self.mConnectedDockAreas and len(self.mConnectedDockAreas) > 0:
            self.mCurrentDockArea = self.mConnectedDockAreas[0]
        return self.mCurrentDockArea

    def onDockAreaDragDropEvent(self, dockArea, event):

        assert isinstance(dockArea, DockArea)

        assert isinstance(event, QEvent)


        if isinstance(event, QDragEnterEvent):
            # check mime types we can handle
            MH = MimeDataHelper(event.mimeData())

            if MH.hasMapLayers() or MH.hasDataSources():
                event.setDropAction(Qt.CopyAction)
                event.accept()
            return


        elif isinstance(event, QDragMoveEvent):
            event.accept()
            return
        elif isinstance(event, QDragLeaveEvent):
            event.accept()
            return

        elif isinstance(event, QDropEvent):
            MH = MimeDataHelper(event.mimeData())
            layers = []
            textfiles = []
            if MH.hasMapLayers():
                layers = MH.mapLayers()
            elif MH.hasDataSources():
                for ds in MH.dataSources():
                    if isinstance(ds, DataSourceSpatial):
                        layers.append(ds.createUnregisteredMapLayer())
                    elif isinstance(ds, DataSourceTextFile):
                        textfiles.append(ds)

            #register datasources
            for src in layers + textfiles:
                self.dataSourceManager.addSource(src)

            #open map dock for new layers
            if len(layers) > 0:
                NEW_MAP_DOCK = self.createDock('MAP')
                NEW_MAP_DOCK.addLayers(layers)

            #open test dock for new text files
            for textSource in textfiles:
                if re.search('(xml|html)$', os.path.basename(textSource.uri)):
                    dock = self.createDock('WEBVIEW')
                    dock.load(textSource.uri)
                else:
                    self.createDock('TEXT', plainTxt=open(textSource.uri).read())
            event.accept()


    def __len__(self):
        return len(self.mDocks)

    def __iter__(self):
        return iter(self.mDocks)

    def docks(self, dockType=None):
        """
        Returns the managed docks.
        :param dockType: type of Dock to be returned. Default = None to return all Docks
        :return: [list-of-Docks controlled by this DockManager]
        """
        if dockType is None:
            return self.mDocks[:]
        else:
            return [d for d in self.mDocks if type(d) is dockType]

    def getDockWithUUID(self, uuid_):
        if isinstance(uuid_, str):
            uuid_ = uuid.UUID(uuid_)
        assert isinstance(uuid_, uuid.UUID)
        for dock in list(self.mDocks):
            assert isinstance(dock, Dock)
            if dock.uuid == uuid_:
                return dock

        return None


    def removeDock(self, dock):
        if dock in self.mDocks:
            self.mDocks.remove(dock)
            self.sigDockRemoved.emit(dock)

            if dock.container():
                dock.close()
            return True
        return False

    def createDock(self, dockType, *args, **kwds):

        n = len(self.mDocks) + 1

        is_new_dock = True
        if dockType == 'MAP':
            kwds['name'] = kwds.get('name', 'Map #{}'.format(n))
            dock = MapDock(*args, **kwds)
        elif dockType == 'TEXT':
            kwds['name'] = kwds.get('name', 'Text #{}'.format(n))
            dock = TextDock(*args, **kwds)

        elif dockType == 'MIME':
            kwds['name'] = kwds.get('name', 'MimeData #{}'.format(n))
            dock = MimeDataDock(*args, **kwds)

        elif dockType == 'WEBVIEW':
            kwds['name'] = kwds.get('name', 'HTML Viewer #{}'.format(n))
            dock = WebViewDock(*args, **kwds)
        elif dockType == 'SPECLIB':
            kwds['name'] = kwds.get('name', 'Spectral Library #{}'.format(n))
            dock = SpectralLibraryDock(*args, **kwds)
        else:
            raise Exception('Unknown dock type: {}'.format(dockType))

        dockArea = kwds.get('dockArea', self.currentDockArea())
        assert isinstance(dockArea, DockArea), \
            'DockManager not connected to any DockArea yet. \nAdd DockAreas with connectDockArea(self, dockArea)'
        if dock not in self.mDocks:
            dock.sigClosed.connect(self.removeDock)
            self.mDocks.append(dock)
            dockArea.addDock(dock, *args, **kwds)
            self.sigDockAdded.emit(dock)


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


