import six, sys, os, gc, re, collections

from qgis.core import *
from qgis.gui import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from enmapbox.gui.utils import PanelWidgetBase, loadUI, MimeDataHelper
from osgeo import gdal, ogr
from enmapbox.gui.treeviews import *
from enmapbox.gui.mapcanvas import MapCanvas, CanvasLink

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

    def __init__(self, parent, dock):

        super(DockTreeNode, self).__init__(parent, '<dockname not available>')
        self.dock = None
        self._icon = QIcon(':/enmapbox/icons/viewlist_dock.png')
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
    """
    A node to show linkin between difference canvases
    """
    def __init__(self, parent, canvas):
        assert isinstance(canvas, MapCanvas)
        super(CanvasLinkTreeNode, self).__init__(parent, 'Spatial Links',
                                                    icon=QIcon(":/enmapbox/icons/link_basic.png"))


        self.lookup = dict()
        self.canvas = canvas
        self.canvas.sigCanvasLinkAdded.connect(self.addCanvasLink)
        self.canvas.sigCanvasLinkRemoved.connect(self.removeCanvasLink)


    def addCanvasLink(self, canvasLink):
        assert isinstance(canvasLink, CanvasLink)
        from enmapbox.gui.utils import findParent
        theOtherCanvas = canvasLink.theOtherCanvas(self.canvas)
        theOtherDock = findParent(theOtherCanvas, Dock, checkInstance=True)
        node = TreeNode(self, '', icon=canvasLink.icon())
        if isinstance(theOtherDock, Dock):
            name = theOtherDock.title()
            theOtherDock.sigTitleChanged.connect(node.setName)
        else:
            name = str(theOtherCanvas)
        node.setName(name)
        self.lookup[theOtherCanvas] = node

    def removeCanvasLink(self, canvasLink):
        assert isinstance(canvasLink, CanvasLink)
        theOtherCanvas = canvasLink.theOtherCanvas(self.canvas)
        node = self.lookup[theOtherCanvas]
        self.removeChildNode(node)

class MapDockTreeNode(DockTreeNode):
    """
    A TreeNode linked to a MapDock
    Acts like the QgsLayerTreeMapCanvasBridge
    """

    def __init__(self, parent, dock):

        super(MapDockTreeNode, self).__init__(parent, dock)
        self.setIcon(QIcon(':/enmapbox/icons/viewlist_mapdock.png'))


        self.addedChildren.connect(lambda: self.updateCanvas())
        self.removedChildren.connect(lambda: self.updateCanvas())

    def connectDock(self, dock):
        assert isinstance(dock, MapDock)
        super(MapDockTreeNode, self).connectDock(dock)

        self.crsNode = CRSTreeNode(self, dock.canvas.mapSettings().destinationCrs())
        self.linkNode = CanvasLinkTreeNode(self, dock.canvas)
        self.dock.sigLayersAdded.connect(self.updateChildNodes)
        self.dock.sigLayersRemoved.connect(self.updateChildNodes)
        self.dock.sigCrsChanged.connect(self.crsNode.setCrs)
        self.updateChildNodes()

    def onAddedChildren(self, node, idxFrom, idxTo):
        self.updateCanvas()

    def onRemovedChildren(self, node, idxFrom, idxTo):
        self.updateCanvas()

    def updateChildNodes(self):
        if self.dock:
            # state = self.blockSignals
            # self.blockSignals = True
            # self.removeAllChildren()
            canvasLayers = self.dock.layers()
            treeNodeLayerNodes = self.findLayers()
            treeNodeLayers = [n.layer() for n in treeNodeLayerNodes]
            visibleLayers = self.visibleLayers(self)

            # new layers to add?
            newChildLayers = [l for l in canvasLayers if l not in treeNodeLayers]

            # layers to set visible?
            for layer in canvasLayers:
                if layer not in treeNodeLayers:
                    # insert layer to layer tree
                    self.insertLayer(0, layer)

                # set canvas on visible
                lNode = self.findLayer(layer.id())
                lNode.setVisible(Qt.Checked)
                s = ""

        return self

    def updateCanvas(self):
        # reads the nodes and sets the mapcanvas accordingly
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

    def insertLayer(self, idx, layer):
        assert isinstance(layer, QgsMapLayer)
        if layer is None or QgsMapLayerRegistry.instance().mapLayer(layer.id()) != layer:
            return None

        ll = QgsLayerTreeLayer(layer)
        self.insertChildNode(idx, ll)
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
        self.dockManager.sigDockAdded.connect(self.addDock)
        self.dockManager.sigDockRemoved.connect(self.removeDock)
        self.dockManager.sigDockAdded.connect(lambda : self.sandboxslot2())

        #dockManager.sigDockRemoved.connect(self.removeDock)
        self.mimeIndices = []


    def sandboxslot(self, dock):
        s  =""
    def sandboxslot2(self):
        s  =""

    def supportedDragActions(self):
        return Qt.CopyAction | Qt.MoveAction

    def supportedDropActions(self):
        return Qt.CopyAction | Qt.MoveAction

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
            action.setToolTip('Shows the layer properties')
            action.triggered.connect(lambda: self.setLayerStyle(lyr, canvas))
            menu.addAction(action)

            action = QAction('Remove', menu)
            action.setToolTip('Removes this layer from the map canvas')
            action.triggered.connect(lambda: parentNode.removeChildNode(node))
            menu.addAction(action)

        elif isinstance(node, DockTreeNode):
            # global
            action = QAction('Close', menu)
            action.setToolTip('Closes this map dock')
            action.triggered.connect(lambda: self.dockManager.removeDock(node.dock))
            menu.addAction(action)

            action = QAction('Clear', menu)
            action.triggered.connect(lambda: node.removeAllChildren())
            action.setToolTip('Removes all layers from this map dock')
            menu.addAction(action)

        return menu


    def addDock(self, dock):
        rootNode = self.rootNode
        newNode = TreeNodeProvider.CreateNodeFromDock(dock, rootNode)
        #newNode.sigRemoveMe.connect(lambda : self.removeDockNode(newNode))

    def removeDock(self, dock):
        rootNode = self.rootNode
        to_remove = [n for n in rootNode.children() if n.dock == dock]
        for node in to_remove:
            self.removeDockNode(node)
        s = ""

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
                flags |= Qt.ItemIsDropEnabled

        elif type(node) in [QgsLayerTreeLayer, QgsLayerTreeGroup]:
            flags = Qt.ItemIsEnabled | \
                    Qt.ItemIsSelectable | \
                    Qt.ItemIsUserCheckable | \
                    Qt.ItemIsDragEnabled

        else:
            flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
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

        if isinstance(dockNode, MapDockTreeNode):
            if MDH.hasLayerTreeModelData():
                nodes = MDH.layerTreeModelNodes()
                if len(nodes) > 0:
                    if parent.isValid() and row == -1:
                        row = 0
                    #node.insertChildNodes(row, nodes)
                    node.insertChildNodes(row, nodes)
                    return True

            if MDH.hasDataSources():
                dataSources = [ds for ds in MDH.dataSources() if isinstance(ds, DataSourceSpatial)]
                if len(dataSources) > 0:
                    layers = [ds.createRegisteredMapLayer() for ds in dataSources]

                    #layers for nodes have to be registered
                    reg = QgsMapLayerRegistry.instance()
                    reg = QgsMapLayerRegistry.instance().addMapLayers(layers, False)
                    nodes = [QgsLayerTreeLayer(l) for l in layers]

                    if len(nodes) > 0:
                        if parent.isValid() and row == -1:
                            row = 0
                        node.insertChildNodes(row, nodes)
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
        mimeData = QMimeData()
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

        if type(node) in [QgsLayerTreeGroup, QgsLayerTreeLayer]:
            return super(DockManagerTreeModel, self).data(index, role)

        elif isinstance(node, TreeNode):
            if role == Qt.DisplayRole:
                return node.name()
            if role == Qt.DecorationRole:
                return node.icon()
            if role == Qt.ToolTipRole:
                return node.tooltip()
            if role == Qt.CheckStateRole:
                if isinstance(node, DockTreeNode):
                    if isinstance(node.dock, Dock) and node.dock.isVisible():
                        return Qt.Checked
                    else:
                        return Qt.Unchecked
                else:
                    return QVariant.Invalid
                return QVariant.Invalid
        else:
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
        self.enmapBox = enmapbox

        self.dockArea = self.enmapBox.ui.dockArea
        self.DOCKS = list()
        self.enmapBox.dataSourceManager.sigDataSourceRemoved.connect(self.onDataSourceRemoved)
        self.connectDockArea(self.dockArea)
        self.setCursorLocationValueDock(None)

    def onDataSourceRemoved(self, dataSource):
        """
        Remove dependencies to removed data sources
        :param dataSource:
        :return:
        """
        if isinstance(dataSource, DataSourceSpatial):
            for mapDock in [d for d in self.DOCKS if isinstance(d, MapDock)]:
                mapDock.removeLayers(dataSource.mapLayers)


    def connectDockArea(self, dockArea):
        assert isinstance(dockArea, DockArea)

        dockArea.sigDragEnterEvent.connect(lambda event : self.onDockAreaDragDropEvent(dockArea, event))
        dockArea.sigDragMoveEvent.connect(lambda event : self.onDockAreaDragDropEvent(dockArea, event))
        dockArea.sigDragLeaveEvent.connect(lambda event : self.onDockAreaDragDropEvent(dockArea, event))
        dockArea.sigDropEvent.connect(lambda event : self.onDockAreaDragDropEvent(dockArea, event))

    def onDockAreaDragDropEvent(self, dockArea, event):

        assert isinstance(dockArea, DockArea)

        assert isinstance(event, QEvent)

        if type(event) in [QDragEnterEvent, QDropEvent]:
            print((dockArea,event))

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
                        layers.append(ds.createRegisteredMapLayer())
                    elif isinstance(ds, DataSourceTextFile):
                        textfiles.append(ds)

            #register datasources
            for src in layers + textfiles:
                self.enmapBox.dataSourceManager.addSource(src)

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
            self.cursorLocationValueDock.w.connectDataSourceManager(self.enmapBox.dataSourceManager)
            dock.sigClosed.connect(lambda: self.setCursorLocationValueDock(None))

    def removeDock(self, dock):
        if dock in self.DOCKS:
            self.DOCKS.remove(dock)
            self.sigDockRemoved.emit(dock)

            if dock.container():
                dock.close()
            return True
        return False

    def createDock(self, docktype, *args, **kwds):

        #set default kwds

        n = len(self.DOCKS) + 1

        is_new_dock = True
        if docktype == 'MAP':
            kwds['name'] = kwds.get('name', 'MapDock #{}'.format(n))
            dock = MapDock(self.enmapBox, *args, **kwds)
            dock.sigCursorLocationValueRequest.connect(self.showCursorLocationValues)

        elif docktype == 'TEXT':
            kwds['name'] = kwds.get('name', 'TextDock #{}'.format(n))
            dock = TextDock(self.enmapBox, *args, **kwds)

        elif docktype == 'MIME':
            kwds['name'] = kwds.get('name', 'MimeDataDock #{}'.format(n))
            dock = MimeDataDock(self.enmapBox, *args, **kwds)

        elif docktype == 'WEBVIEW':
            kwds['name'] = kwds.get('name', 'HTML Viewer #{}'.format(n))
            dock = WebViewDock(self.enmapBox,  *args, **kwds)

        elif docktype == 'CURSORLOCATIONVALUE':
            kwds['name'] = kwds.get('name', 'Cursor Location Values')
            if self.cursorLocationValueDock is None:
                self.setCursorLocationValueDock(CursorLocationValueDock(self.enmapBox, *args, **kwds))
            else:
                is_new_dock = False
            dock = self.cursorLocationValueDock
        else:
            raise Exception('Unknown dock type: {}'.format(docktype))

        dockArea = kwds.get('dockArea', self.dockArea)
        state = dockArea.saveState()
        main = state['main']
        if dock not in self.DOCKS:
            dock.sigClosed.connect(self.removeDock)
            self.DOCKS.append(dock)
            self.dockArea.addDock(dock, *args, **kwds)
            self.sigDockAdded.emit(dock)

            if 'initSrc' in kwds.keys():
                ds = self.enmapBox.addSource(kwds['initSrc'])
                if isinstance(ds, DataSourceSpatial):
                    dock.addLayers(ds.createRegisteredMapLayer())

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


