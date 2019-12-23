# -*- coding: utf-8 -*-
# noinspection PyPep8Naming
"""
***************************************************************************
    dockmanager.py
    ---------------------
    Date                 : August 2017
    Copyright            : (C) 2017 by Benjamin Jakimow
    Email                : benjamin.jakimow@geo.hu-berlin.de
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from enmapbox.gui import *
from enmapbox.gui.mapcanvas import *
from enmapbox.gui.mimedata import *
from enmapbox.gui.docks import *
from enmapbox.externals.qps.utils import *
from enmapbox.externals.qps.layerproperties import *
from enmapbox.gui.datasourcemanager import DataSourceManager
from enmapbox.gui import SpectralLibrary

LUT_DOCKTYPES = {'MAP':MapDock,
                 'TEXT':TextDock,
                 'MIME':MimeDataDock,
                 'WEBVIEW':WebViewDock,
                 'SPECLIB':SpectralLibraryDock}

for cls in list(LUT_DOCKTYPES.values()):
    LUT_DOCKTYPES[cls] = cls


class LayerTreeNode(QgsLayerTree):
    sigIconChanged = pyqtSignal()
    sigValueChanged = pyqtSignal(QObject)
    sigRemoveMe = pyqtSignal()
    def __init__(self, parent, name, value=None, checked=Qt.Unchecked, tooltip=None, icon=None):
        #QObject.__init__(self)
        super(LayerTreeNode, self).__init__()
        #assert name is not None and len(str(name)) > 0


        self.mParent = parent
        self.mTooltip = None
        self.mValue = None
        self.mIcon = None

        self.mXmlTag = 'tree-node'

        self.setName(name)
        self.setValue(value)
        self.setExpanded(False)
       # self.setVisible(False)
        self.setTooltip(tooltip)
        self.setIcon(icon)

        if parent is not None:
            parent.addChildNode(self)
            if isinstance(parent, LayerTreeNode):
                self.sigValueChanged.connect(parent.sigValueChanged)

    def dump(self, *args, **kwargs)->str:

        d = super(LayerTreeNode, self).dump()
        d += '{}:"{}":"{}"\n'.format(self.__class__.__name__, self.name(), self.value())
        return d

    def xmlTag(self)->str:
        return self.mXmlTag

    def _removeSubNode(self,node):
        if node in self.children():
            self.removeChildNode(node)
        return None

    def fetchCount(self):
        return 0

    def fetchNext(self):
        pass

    def removeFromParent(self):
        """
        Removed this node from its parent node
        :return: this node
        """
        if self.parent() is not None:
            self.parent().removeChildNode(self)
        return self

    def setValue(self, value):
        self.mValue = value
        self.sigValueChanged.emit(self)

    def value(self):
        return self.mValue

    def removeChildren(self, i0, cnt):
        self.removeChildrenPrivate(i0, cnt)
        self.updateVisibilityFromChildren()

    def setTooltip(self, tooltip):
        self.mTooltip = tooltip

    def tooltip(self, default=''):
        return self.mTooltip

    def setIcon(self, icon):
        if icon:
            assert isinstance(icon, QIcon)
        self.mIcon = icon
        self.sigIconChanged.emit()

    def icon(self):
        return self.mIcon

    def contextMenu(self):
        """
        Returns an empty QMenu
        Overwrite with QMenu + QActions that implement logic related to the TreeNode and its data.
        :return:
        """
        return QMenu()

    @staticmethod
    def readXml(element):

        raise NotImplementedError()

        return None


    @staticmethod
    def attachCommonPropertiesFromXML(node, element):
        assert 'tree-node' in element.tagName()

        node.setName(element.attribute('name'))
        node.setExpanded(element.attribute('expanded') == '1')
        node.setVisible(QgsLayerTreeUtils.checkStateFromXml(element.attribute("checked")))
        node.readCommonXml(element)


    def writeXML(self, parentElement):

        assert isinstance(parentElement, QDomElement)
        doc = parentElement.ownerDocument()
        elem = doc.createElement('tree-node')

        elem.setAttribute('name', self.name())
        elem.setAttribute('expanded', '1' if self.isExpanded() else '0')
        elem.setAttribute('checked', QgsLayerTreeUtils.checkStateToXml(Qt.Checked))

        #custom properties
        self.writeCommonXml(elem)

        for node in self.children():
            node.writeXML(elem)
        parentElement.appendChild(elem)

        #return elem


    def readChildrenFromXml(self, element):
        nodes = []
        childElem = element.firstChildElement()
        while(not childElem.isNull()):
            elem = childElem
            tagName = elem.tagName()
            node = None
            attributes = getDOMAttributes(elem)
            # from enmapbox.gui.dockmanager import DockTreeNode, MapDockTreeNode, TextDockTreeNode
            # from enmapbox.gui.datasourcemanager import DataSourceGroupTreeNode, DataSourceTreeNode

            if tagName == 'tree-node':
                node = LayerTreeNode.readXml(elem)
            else:
                for nodeClass in LayerTreeNode.__subclasses__():
                    if True:
                        node = nodeClass.readXml(elem)
                        break

            if node:
                nodes.append(node)
            childElem = childElem.nextSibling()
        if len(nodes) > 0:
            self.insertChildNodes(-1, nodes)

    def dropMimeData(self):
        raise NotImplementedError()

    def __eq__(self, other):
        return id(self) == id(other)

    def __hash__(self):
        return hash(id(self))


class DockTreeNode(LayerTreeNode):
    @staticmethod
    def readXml(element):
        if element.tagName() != 'dock-tree-node':
            return None

        node = DockTreeNode(None, None)
        dockName = element.attribute('name')
        node.setName(dockName)
        node.setExpanded(element.attribute('expanded') == '1')
        node.setVisible(QgsLayerTreeUtils.checkStateFromXml(element.attribute("checked")))
        node.readCommonXml(element)
        # node.readChildrenFromXml(element)

        # try to find the dock by its uuid in dockmanager
        from enmapbox.gui.enmapboxgui import EnMAPBox

        dockManager = EnMAPBox.instance().dockManager
        uuid = node.customProperty('uuid', None)
        if uuid:
            dock = dockManager.getDockWithUUID('{}'.format(uuid))

        if dock is None:
            dock = dockManager.createDock('MAP', name=dockName)
        node.connectDock(dock)

        return node

    """
    Base TreeNode to symbolise a Dock
    """
    sigDockUpdated = pyqtSignal()

    def __init__(self, parent, dock:Dock):

        self.dock = dock
        super(DockTreeNode, self).__init__(parent, '<dockname not available>')

        self.mIcon = QIcon(':/enmapbox/gui/ui/icons/viewlist_dock.svg')
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
            # self.dock.sigVisibilityChanged.connec(self.)
            #self.setCustomProperty('uuid', '{}'.format(dock.uuid))
            # self.dock.sigClosed.connect(self.removedisconnectDock)


class TextDockTreeNode(DockTreeNode):
    def __init__(self, parent, dock):
        assert isinstance(dock, TextDock)
        super(TextDockTreeNode, self).__init__(parent, dock)
        self.setIcon(QIcon(':/enmapbox/gui/ui/icons/viewlist_dock.svg'))

    def connectDock(self, dock):
        assert isinstance(dock, TextDock)
        super(TextDockTreeNode, self).connectDock(dock)

        self.fileNode = LayerTreeNode(self, 'File')
        dock.mTextDockWidget.sigSourceChanged.connect(self.setLinkedFile)
        self.setLinkedFile(dock.mTextDockWidget.mFile)

    def setLinkedFile(self, path):
        self.fileNode.setValue(path)
        self.fileNode.setTooltip(path)

class CanvasLinkTreeNode(TreeNode):
    def __init__(self, parent, canvasLink, name, **kwds):
        assert isinstance(canvasLink, CanvasLink)
        kwds['icon'] = canvasLink.icon()
        super(CanvasLinkTreeNode, self).__init__(parent, name, **kwds)
        self.canvasLink = canvasLink

    def contextMenu(self):
        m = QMenu()

        #parent canvas
        canvas = self.parent().canvas
        otherCanvas = self.canvasLink.theOtherCanvas(canvas)
        a = m.addAction('Remove')
        a.setToolTip('Remove link to {}.'.format(otherCanvas.name()))
        a.triggered.connect(self.canvasLink.removeMe)
        return m


class CanvasLinkTreeNodeGroup(TreeNode):
    """
    A node to show links between difference canvases
    """

    def __init__(self, parent, canvas:MapCanvas):
        assert isinstance(canvas, MapCanvas)
        super(CanvasLinkTreeNodeGroup, self).__init__(parent, 'Spatial Links',
                                                      icon=QIcon(":/enmapbox/gui/ui/icons/link_basic.svg"))

        self.canvas = canvas
        self.canvas.sigCanvasLinkAdded.connect(self.addCanvasLink)
        self.canvas.sigCanvasLinkRemoved.connect(self.removeCanvasLink)

    def addCanvasLink(self, canvasLink:CanvasLink):
        assert isinstance(canvasLink, CanvasLink)
        from enmapbox.gui.utils import findParent
        theOtherCanvas = canvasLink.theOtherCanvas(self.canvas)
        theOtherDock = findParent(theOtherCanvas, Dock, checkInstance=True)
        linkNode = CanvasLinkTreeNode(self, canvasLink, '<no name>', icon=canvasLink.icon())
        if isinstance(theOtherDock, Dock):
            name = theOtherDock.title()
            theOtherDock.sigTitleChanged.connect(linkNode.setName)
        else:
            name = '{}'.format(theOtherCanvas)
        linkNode.setName(name)

    def removeCanvasLink(self, canvasLink):
        assert isinstance(canvasLink, CanvasLink)
        theOtherCanvas = canvasLink.theOtherCanvas(self.canvas)
        toRemove = [c for c in self.children() if isinstance(c, CanvasLinkTreeNode) and c.canvasLink == canvasLink]
        for node in toRemove:
            if node.canvasLink in node.canvasLink.canvases:
                # need to be deleted from other listeners first
                node.canvasLink.removeMe()
            else:
                self.removeChildNode(node)

    def contextMenu(self):
        m = QMenu()
        from enmapbox import EnMAPBox

        otherMaps = collections.OrderedDict()
        for mapDock in EnMAPBox.instance().dockManager().docks('MAP'):
            assert isinstance(mapDock, MapDock)
            if mapDock.mapCanvas() == self.canvas:
                continue
            otherMaps[mapDock.title()] = mapDock.mapCanvas()

        sub = m.addMenu('Link to all other maps')
        a = sub.addAction('on center + scale')
        a.triggered.connect(lambda _, c1=self.canvas, canvases=otherMaps.values():
                            [CanvasLink.linkMapCanvases(c1, c2, LINK_ON_CENTER_SCALE) for c2 in canvases])

        a = sub.addAction('on center')
        a.triggered.connect(lambda _, c1=self.canvas, canvases=otherMaps.values():
                            [CanvasLink.linkMapCanvases(c1, c2, LINK_ON_CENTER) for c2 in canvases])

        a = sub.addAction('on scale')
        a.triggered.connect(lambda _, c1=self.canvas, canvases=otherMaps.values():
                            [CanvasLink.linkMapCanvases(c1, c2, LINK_ON_SCALE) for c2 in canvases])

        a = sub.addAction('unlink')
        a.triggered.connect(lambda _, c1=self.canvas, canvases=otherMaps.values():
                            [CanvasLink.linkMapCanvases(c1, c2, UNLINK) for c2 in canvases])

        for name, targetCanvas in otherMaps.items():
            assert isinstance(targetCanvas, MapCanvas)
            sub = m.addMenu('Link to "{}"'.format(name))
            a = sub.addAction('on center + scale')
            a.triggered.connect(lambda _, c1=self.canvas, c2=targetCanvas: CanvasLink.linkMapCanvases(c1,c2, LINK_ON_CENTER_SCALE))

            a = sub.addAction('on center')
            a.triggered.connect(
                lambda _, c1=self.canvas, c2=targetCanvas: CanvasLink.linkMapCanvases(c1, c2, LINK_ON_CENTER))

            a = sub.addAction('on scale')
            a.triggered.connect(
                lambda _, c1=self.canvas, c2=targetCanvas: CanvasLink.linkMapCanvases(c1, c2, LINK_ON_SCALE))

            a = sub.addAction('unlink')
            a.triggered.connect(
                lambda _, c1=self.canvas, c2=targetCanvas: CanvasLink.linkMapCanvases(c1, c2, UNLINK))


        return m


class SpeclibDockTreeNode(DockTreeNode):
    def __init__(self, parent, dock):
        super(SpeclibDockTreeNode, self).__init__(parent, dock)
        self.setIcon(QIcon(':/enmapbox/gui/ui/icons/viewlist_spectrumdock.svg'))

    def connectDock(self, dock):
        assert isinstance(dock, SpectralLibraryDock)
        super(SpeclibDockTreeNode, self).connectDock(dock)
        self.speclibWidget = dock.mSpeclibWidget
        assert isinstance(self.speclibWidget, SpectralLibraryWidget)

        #self.showMapSpectra = CheckableLayerTreeNode(self, 'Show map profiles', checked=Qt.Checked)
        #self.showMapSpectra.setCheckState(Qt.Checked if self.speclibWidget.mapInteraction() else Qt.Unchecked)
        #self.showMapSpectra.sigCheckStateChanged.connect(
        #    lambda s: self.speclibWidget.setMapInteraction(s == Qt.Checked))
        self.profilesNode = LayerTreeNode(self, 'Profiles', value=0)
        self.speclibWidget.mSpeclib.committedFeaturesAdded.connect(self.updateNodes)
        self.speclibWidget.mSpeclib.committedFeaturesRemoved.connect(self.updateNodes)

    def updateNodes(self):
        assert isinstance(self.speclibWidget, SpectralLibraryWidget)
        self.profilesNode.setValue(len(self.speclibWidget.mSpeclib))


class MapDockTreeNode(DockTreeNode):
    """
    A TreeNode linked to a MapDock
    Acts like the QgsLayerTreeMapCanvasBridge
    """

    sigAddedLayers = pyqtSignal(list)
    sigRemovedLayers = pyqtSignal(list)

    def __init__(self, parent, dock):

        super(MapDockTreeNode, self).__init__(parent, dock)
        # KeepRefs.__init__(self)
        self.setIcon(QIcon(':/enmapbox/gui/ui/icons/viewlist_mapdock.svg'))
        self.addedChildren.connect(self.onAddedChildren)
        self.removedChildren.connect(self.onRemovedChildren)
        self.willRemoveChildren.connect(self.onWillRemoveChildren)
        self.mRemovedLayerCache = []

    def connectDock(self, dock:MapDock):
        assert isinstance(dock, MapDock)
        super(MapDockTreeNode, self).connectDock(dock)
        # TreeNode(self, 'Layers')
        assert isinstance(self.dock, MapDock)
        #self.layerNode = QgsLayerTree()
        #self.layerNode.setName('Layers')
        #self.addChildNode(self.layerNode)

        #self.mTreeCanvasBridge = QgsLayerTreeMapCanvasBridge(self.layerNode, self.dock.canvas)

        assert isinstance(dock, MapDock)
        canvas = self.dock.mapCanvas()
        assert isinstance(canvas, MapCanvas)
        self.mTreeCanvasBridge = MapCanvasBridge(self, canvas)


    def onAddedChildren(self, node, idxFrom, idxTo):
        self.updateCanvas()
        lyrs = []
        for n in node.children()[idxFrom:idxTo+1]:
            if type(n) == QgsLayerTreeLayer:
                lyrs.append(n.layer())
        if len(lyrs) > 0:
            self.sigAddedLayers.emit(lyrs)

    def onWillRemoveChildren(self, node, idxFrom, idxTo):
        self.mRemovedLayerCache.clear()
        for n in node.children()[idxFrom:idxTo + 1]:
            if type(n) == QgsLayerTreeLayer:
                self.mRemovedLayerCache.append(n.layer())

    def onRemovedChildren(self, node, idxFrom, idxTo):
        self.updateCanvas()

        lyrs = self.mRemovedLayerCache[:]
        self.mRemovedLayerCache.clear()
        self.sigRemovedLayers.emit(lyrs)

    def updateChildNodes(self):
        """
        Compares the linked map canvas with layers in the tree node tree
        If required, missing layers will be added to the tree node
        :return:
        """
        if self.dock:
            canvasLayers = self.dock.layers()
            #treeNodeLayerNodes = self.layerNode.findLayers()
            treeNodeLayerNodes = self.findLayers()
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
                lNode.setItemVisibilityChecked(Qt.Checked)

        return self

    def mapCanvas(self)->MapCanvas:
        """
        Returns the MapCanvas
        :return: MapCanvas
        """
        return self.dock.mapCanvas()

    def updateCanvas(self):
        # reads the nodes and sets the map canvas accordingly
        if self.dock:

            self.mTreeCanvasBridge.setCanvasLayers()
            return


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
                    s = "" #logger.warning('QgsLayerTreeLayer.layer() is none')
        else:
            raise NotImplementedError()

        for l in lyrs:
            assert isinstance(l, QgsMapLayer), l

        return lyrs

    def removeLayerNodesByURI(self, uri):

        toRemove = []
        for lyrNode in self.findLayers():
            lyr = lyrNode.layer()
            if isinstance(lyr, QgsMapLayer):
                uriLyr = lyrNode.layer().source()
                if uriLyr == uri:
                    toRemove.append(lyrNode)

        for node in toRemove:
            node.parent().removeChildNode(node)
        s = ""

    def insertLayer(self, idx, layerSource):
        """
        Inserts a new QgsMapLayer od DataSourceSpatial on position idx by creating a new QgsMayTreeLayer node
        :param idx:
        :param layerSource:
        :return:
        """
        from enmapbox.gui.datasourcemanager import DataSourceManager
        dsm = DataSourceManager.instance()

        mapLayers = []
        if isinstance(layerSource, QgsMapLayer):
            mapLayers.append(layerSource)
        else:
            s = ""

        if isinstance(dsm, DataSourceManager):
            dsm.addSources(mapLayers)


        for mapLayer in mapLayers:
            assert isinstance(mapLayer, QgsMapLayer)
            #QgsProject.instance().addMapLayer(mapLayer)
            l = QgsLayerTreeLayer(mapLayer)
            #self.layerNode.insertChildNode(idx, l)
            self.insertChildNode(idx, l)









class DockManagerTreeModel(QgsLayerTreeModel):
    def __init__(self, dockManager, parent=None):
        self.rootNode = LayerTreeNode(None, '<hidden root node>')
        assert isinstance(dockManager, DockManager)
        super(DockManagerTreeModel, self).__init__(self.rootNode, parent)
        self.columnNames = ['Property', 'Value']

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
            self.setFlag(QgsLayerTreeModel.ShowLegendAsTree, True)
            #self.setFlag(QgsLayerTreeModel.ShowRasterPreviewIcon, False)

            self.setFlag(QgsLayerTreeModel.DeferredLegendInvalidation, True)
            # self.setFlag(QgsLayerTreeModel.UseEmbeddedWidget, True)

            # behavioral
            self.setFlag(QgsLayerTreeModel.AllowNodeReorder, True)
            self.setFlag(QgsLayerTreeModel.AllowNodeRename, True)
            self.setFlag(QgsLayerTreeModel.AllowNodeChangeVisibility, True)
            self.setFlag(QgsLayerTreeModel.AllowLegendChangeState, True)
            # self.setFlag(QgsLayerTreeModel.ActionHierarchical, False)

        self.mDockManager = dockManager
        self.mDockManager.sigDockAdded.connect(self.addDock)
        self.mDockManager.sigDockRemoved.connect(self.removeDock)
        self.mDockManager.sigDataSourceRemoved.connect(self.removeDataSource)


    def columnCount(self, index)->int:
        node = self.index2node(index)
        if type(node) in [DockTreeNode, QgsLayerTreeGroup, QgsLayerTreeLayer]:
            return 1
        elif isinstance(node, LayerTreeNode):
            return 2
        else:
            return 1


    def removeDataSource(self, dataSource):
        assert isinstance(dataSource, DataSource)

        for node in self.rootNode.children():
            if isinstance(node, MapDockTreeNode):
                node.removeLayerNodesByURI(dataSource.uri())
                s = ""
        s = ""

    def supportedDragActions(self):
        """
        """
        return Qt.CopyAction | Qt.MoveAction

    def supportedDropActions(self)->Qt.DropActions:
        """

        :return:
        """
        return Qt.CopyAction | Qt.MoveAction

    def addDock(self, dock:Dock)->DockTreeNode:
        """
        Adds a Dock and returns the DockTreeNode
        :param dock:
        :return:
        """
        return createDockTreeNode(dock, self.rootNode)

    def canFetchMore(self, index)->bool:
        node = self.index2node(index)
        if isinstance(node, LayerTreeNode):
            from enmapbox.gui.datasourcemanager import SpeclibProfilesTreeNode
            if isinstance(node, SpeclibProfilesTreeNode):
                s = ""
            return len(node.children()) < node.fetchCount()
        return False

    def removeDock(self, dock):
        rootNode = self.rootNode
        to_remove = [n for n in rootNode.children() if n.dock == dock]
        for node in to_remove:
            self.removeDockNode(node)

    def mapDockTreeNodes(self)->typing.List[MapDockTreeNode]:
        """
        Returns all MapDockTreeNodes
        :return: [list-of-MapDockTreeNodes]
        """
        return [n for n in self.rootNode.children() if isinstance(n, MapDockTreeNode)]

    def mapCanvases(self)->typing.List[MapCanvas]:
        """
        Returns all MapCanvases
        :return: [list-of-MapCanvases]
        """
        return [n.mapCanvas() for n in self.mapDockTreeNodes()]

    def mapLayers(self)->typing.List[QgsMapLayer]:
        """
        Returns all map layers, also invisible layers that are currently not added to a QgsMapCanvas
        :return: [list-of-QgsMapLayer]
        """
        layers = []
        for node in self.mapDockTreeNodes():
            if isinstance(node, MapDockTreeNode):
                layers.extend([l.layer() for l in node.findLayers()])
        return layers

    def removeLayers(self, layers: list):
        assert isinstance(layers, list)

        mapDockTreeNodes = [n for n in self.rootNode.children() if isinstance(n, MapDockTreeNode)]
        for mapDockTreeNode in mapDockTreeNodes:
            assert isinstance(mapDockTreeNode, MapDockTreeNode)
            for lyr in layers:
                assert isinstance(lyr, QgsMapLayer)
                mapDockTreeNode.removeLayer(lyr)

    def removeNode(self, node):
        idx = self.node2index(node)
        p = self.index2node(idx.parent())
        p.removeChildNode(node)

    def removeDockNode(self, node):
        self.mDockManager.removeDock(node.dock)
        self.removeNode(node)

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        node = self.index2node(index)
        if node is None:
            node = self.index2legendNode(index)
            if isinstance(node, QgsLayerTreeModelLegendNode):
                return self.legendNodeFlags(node)
                #return super(QgsLayerTreeModel,self).flags(index)
                #return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
            else:
                return Qt.NoItemFlags
        else:
            #print('node: {}  {}'.format(node, type(node)))
            dockNode = self.parentNodesFromIndices(index, nodeInstanceType=DockTreeNode)
            if len(dockNode) == 0:
                return Qt.NoItemFlags
            elif len(dockNode) > 1:
                #print('DEBUG: Multiple docknodes selected')
                return Qt.NoItemFlags
            else:
                dockNode = dockNode[0]


            column = index.column()
            isL1 = node.parent() == self.rootNode
            flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable

            # normal tree nodes


            if isinstance(node, LayerTreeNode):
                if column == 0:

                    if isinstance(node, DockTreeNode):
                        flags |= Qt.ItemIsUserCheckable | \
                                 Qt.ItemIsEditable | \
                                 Qt.ItemIsDropEnabled

                        if isL1:
                            flags |= Qt.ItemIsDropEnabled


                    if node.name() == 'Layers':
                        flags |= Qt.ItemIsUserCheckable | Qt.ItemIsEditable

                    if isinstance(node, CheckableLayerTreeNode):
                        flags |= Qt.ItemIsUserCheckable

                if column == 1:
                    pass
                        # mapCanvas Layer Tree Nodes
            elif type(node) in [QgsLayerTreeLayer, QgsLayerTreeGroup]:
                if column == 0:
                    flags |= Qt.ItemIsUserCheckable | Qt.ItemIsEditable | Qt.ItemIsDropEnabled | Qt.ItemIsDragEnabled

                #if isinstance(dockNode, MapDockTreeNode) and node != dockNode.layerNode:
                #if isinstance(dockNode, MapDockTreeNode) and node != dockNode.layerNode:
                #    flags |= Qt.ItemIsDragEnabled
            elif not isinstance(node, QgsLayerTree):
                s = ""
            else:
                s = ""

            return flags


    def headerData(self, section, orientation, role=None):

        if role == Qt.DisplayRole:
            return self.columnNames[section]

        return None


    def mimeTypes(self):
        # specifies the mime types handled by this model
        types = [MDF_DOCKTREEMODELDATA,
                 MDF_LAYERTREEMODELDATA,
                 MDF_TEXT_HTML,
                 MDF_TEXT_PLAIN,
                 MDF_URILIST]
        return types

    def dropMimeData(self, mimeData, action, row, column, parentIndex):
        assert isinstance(mimeData, QMimeData)


        if not parentIndex.isValid():
            return False

        from enmapbox import EnMAPBox
        layerRegistry = None
        if isinstance(EnMAPBox.instance(), EnMAPBox):
            layerRegistry = EnMAPBox.instance().mapLayerStore()

        parentNode = self.index2node(parentIndex)
        # L1 is the first level below the root tree -> to place dock trees
        isL1Node = parentNode.parent() == self.rootNode

        # get parent DockNode
        dockNode = self.parentNodesFromIndices(parentIndex, nodeInstanceType=DockTreeNode)

        if len(dockNode) != 1:
            return False
        else:
            dockNode = dockNode[0]

        if isinstance(dockNode, MapDockTreeNode):

            parentLayerGroup = self.parentNodesFromIndices(parentIndex, nodeInstanceType=QgsLayerTreeGroup)
            assert len(parentLayerGroup) == 1
            parentLayerGroup = parentLayerGroup[0]

            mapLayers = extractMapLayers(mimeData)

            if isinstance(layerRegistry, QgsMapLayerStore):
                layerRegistry.addMapLayers(mapLayers)

            i = parentIndex.row()
            i = row
            if len(mapLayers) > 0:
                for l in mapLayers:
                    parentLayerGroup.insertLayer(i, l)
                    i += 1
                return True

        elif isinstance(dockNode, TextDockTreeNode):

            s = ""

        return False

    def mimeData(self, indexes):

        indexes = sorted(indexes)

        if len(indexes) == 0:
            return None

        nodesFinal = self.indexes2nodes(indexes, True)

        mimeData = QMimeData()

        doc = QDomDocument()

        rootElem = doc.createElement("dock_tree_model_data")
        context = QgsReadWriteContext()
        for node in nodesFinal:
            node.writeXml(rootElem, context)
        doc.appendChild(rootElem)
        mimeData.setData(MDF_DOCKTREEMODELDATA, textToByteArray(doc))

        mapNodes = [n for n in nodesFinal if type(n) in [QgsLayerTreeLayer, QgsLayerTreeGroup]]
        if len(mapNodes) > 0:
            doc = QDomDocument()
            context = QgsReadWriteContext()
            rootElem = doc.createElement('layer_tree_model_data')
            for node in mapNodes:
                if type(node) == QgsLayerTreeGroup:
                    node.writeLayerTreeGroupXML(rootElem)
                elif type(node) == QgsLayerTreeLayer:
                    node.writeXml(rootElem, context)
            doc.appendChild(rootElem)
            mimeData.setData(MDF_LAYERTREEMODELDATA, textToByteArray(doc))
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

    def data(self, index, role):

        if not index.isValid():
            return None

        node = self.index2node(index)
        legendNode = self.index2legendNode(index)
        column = index.column()

        if isinstance(legendNode, QgsLayerTreeModelLegendNode):
            #print(('LEGEND', node, column, role))
            return super(DockManagerTreeModel, self).data(index, role)

        elif type(node) in [QgsLayerTreeLayer, QgsLayerTreeGroup, QgsLayerTree]:
            #print(('QGSNODE', node, column, role))

            if isinstance(node, QgsLayerTree) and column > 0:
                return None

            if column == 1:
                if role in [Qt.DisplayRole, Qt.EditRole]:
                    return node.name()

            return super(DockManagerTreeModel, self).data(index, role)
        elif isinstance(node, LayerTreeNode):

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
                    if isinstance(node, CheckableLayerTreeNode):
                        return node.checkState()
            elif column == 1:
                if role == Qt.DisplayRole:
                    # print(node.value())
                    return node.value()

                if role == Qt.EditRole:
                    return node.value()

            else:
                #if role == Qt.DisplayRole and isinstance(node, TreeNode):
                #    return node.value()
                return super(DockManagerTreeModel, self).data(index, role)



        return None

        # return super(DockManagerTreeModel, self).data(index, role)

    def setData(self, index, value, role=None):

        node = self.index2node(index)
        if node is None:
            node = self.index2legendNode(index)
            if isinstance(node, QgsLayerTreeModelLegendNode):
                #this does not work:
                #result = super(QgsLayerTreeModel,self).setData(index, value, role=role)
                if role == Qt.CheckStateRole and not self.testFlag(QgsLayerTreeModel.AllowLegendChangeState):
                    return False
                result = node.setData(value, role)
                if result:
                    self.dataChanged.emit(index, index)
                return result

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

        if isinstance(node, CheckableLayerTreeNode) and role == Qt.CheckStateRole:
            node.setCheckState(Qt.Unchecked if value in [False, 0, Qt.Unchecked] else Qt.Checked)
            return True

        if type(node) in [QgsLayerTreeLayer, QgsLayerTreeGroup]:

            if role == Qt.CheckStateRole:
                node.setItemVisibilityChecked(value)
                mapDockNode = node.parent()
                while mapDockNode is not None and not isinstance(mapDockNode, MapDockTreeNode):
                    mapDockNode = mapDockNode.parent()

                assert isinstance(mapDockNode, MapDockTreeNode)
                mapDockNode.updateCanvas()
                result = True
            if role == Qt.EditRole:
                if isinstance(node, QgsLayerTreeLayer):
                    node.setName(value)
                    result = True
                if isinstance(node, QgsLayerTreeGroup):
                    node.setName(value)
                    result = True

        if result:
            self.dataChanged.emit(index, index)
        return result



#class TreeView(QTreeView):
class DockTreeView(QgsLayerTreeView):

    def __init__(self, parent):
        super(DockTreeView, self).__init__(parent)

        self.setHeaderHidden(False)
        self.header().setStretchLastSection(True)
        self.header().setResizeMode(QHeaderView.ResizeToContents)
        #self.header().setResizeMode(1, QHeaderView.ResizeToContents)
        self.currentLayerChanged.connect(self.onCurrentLayerChanged)


    def onCurrentLayerChanged(self, layer:QgsMapCanvas):
        for canvas in self.layerTreeModel().mapCanvases():
            assert isinstance(canvas, MapCanvas)
            if layer in canvas.layers():
                canvas.setCurrentLayer(layer)

        s = ""

    def layerTreeModel(self)->DockManagerTreeModel:
        return self.model()

    def setModel(self, model):
        assert isinstance(model, DockManagerTreeModel)

        super(DockTreeView, self).setModel(model)
        model.rootNode.addedChildren.connect(self.onNodeAddedChildren)
        for c in model.rootNode.findChildren(LayerTreeNode):
            self.setColumnSpan(c)

    def onNodeAddedChildren(self, parent, iFrom, iTo):
        for i in range(iFrom, iTo+1):
            node = parent.children()[i]
            if isinstance(node, LayerTreeNode):
                node.sigValueChanged.connect(self.setColumnSpan)

            self.setColumnSpan(node)

    def setColumnSpan(self, node):
        parent = node.parent()
        if parent is not None:
            model = self.model()
            idxNode = model.node2index(node)
            idxParent = model.node2index(parent)
            span = False
            if isinstance(node, LayerTreeNode):
                span = node.value() == None or '{}'.format(node.value()).strip() == ''
            elif type(node) in [QgsLayerTreeGroup, QgsLayerTreeLayer]:
                span = True
            self.setFirstColumnSpanned(idxNode.row(), idxParent, span)
            #for child in node.children():
            #    self.setColumnSpan(child)



class DockManagerLayerTreeModelMenuProvider(QgsLayerTreeViewMenuProvider):
    def __init__(self, treeView:DockTreeView):
        super(DockManagerLayerTreeModelMenuProvider, self).__init__()
        assert isinstance(treeView, DockTreeView)
        self.mDockTreeView = treeView
        assert isinstance(self.mDockTreeView.model(), DockManagerTreeModel)

    def createContextMenu(self):


        col = self.mDockTreeView.currentIndex().column()
        node = self.mDockTreeView.currentNode()
        if node is None:
            return
        parentNode = node.parent()
        parentDockNode = findParent(node, DockTreeNode, checkInstance=True)
        menu = QMenu()

        selectedLayerNodes = [n for n in self.mDockTreeView.selectedNodes() if type(n) == QgsLayerTreeLayer]
        selectedMapLayers = [n.layer() for n in self.mDockTreeView.selectedNodes() if type(n) == QgsLayerTreeLayer]
        selectedLayerIDs = [n.layer().id() for n in self.mDockTreeView.selectedNodes() if type(n) == QgsLayerTreeLayer]
        if type(node) is QgsLayerTreeLayer:
            # get parent dock node -> related map canvas
            mapNode = findParent(node, MapDockTreeNode)
            assert isinstance(mapNode, MapDockTreeNode)
            assert isinstance(mapNode.dock, MapDock)
            canvas = mapNode.dock.mCanvas

            lyr = node.layer()

            actionPasteStyle = menu.addAction('Paste Style')
            actionPasteStyle.triggered.connect(lambda : pasteStyleFromClipboard(lyr))
            actionPasteStyle.setEnabled(MDF_QGIS_LAYER_STYLE in QApplication.clipboard().mimeData().formats())


            actionCopyStyle = menu.addAction('Copy Style')
            actionCopyStyle.triggered.connect(lambda : pasteStyleToClipboard(lyr))

            menu.addSeparator()
            b = isinstance(canvas, QgsMapCanvas)
            action = menu.addAction('Zoom to layer')
            action.triggered.connect(lambda *args, l=lyr, c=canvas: self.onZoomToLayer(l, c))
            action.setEnabled(b)

            action = menu.addAction('Set layer CRS to map canvas')
            action.triggered.connect(lambda: canvas.setDestinationCrs(lyr.crs()))
            action.setEnabled(b)



            action = menu.addAction('Copy layer path')
            action.triggered.connect(lambda: QApplication.clipboard().setText(lyr.source()))


            menu.addSeparator()

            def removeLayerTreeNodes(nodes):
                for node in nodes:
                    assert isinstance(node, QgsLayerTreeLayer)
                    parentNode = node.parent()
                    parentNode.removeChildNode(node)

            action = menu.addAction('Remove layer')
            action.setToolTip('Remove layer from map canvas')
            action._refToNodes = selectedLayerNodes
            action.triggered.connect(lambda: self.mDockTreeView.model().removeLayers(selectedMapLayers))

            action = menu.addAction('Layer properties')
            action.setToolTip('Set layer properties')
            action.triggered.connect(lambda: self.setLayerStyle(lyr, canvas))



        elif isinstance(node, DockTreeNode):
            assert isinstance(node.dock, Dock)
            from enmapbox.gui.utils import appendItemsToMenu
            return node.dock.contextMenu()

        elif isinstance(node, LayerTreeNode):
            if col == 0:
                menu = node.contextMenu()
            elif col == 1:
                menu = QMenu()
                a = menu.addAction('Copy')
                a.triggered.connect(lambda: QApplication.clipboard().setText('{}'.format(node.value())))

        return menu

    def onZoomToLayer(self,lyr:QgsMapLayer, canvas:QgsMapCanvas):

        assert isinstance(lyr, QgsMapLayer)
        assert isinstance(canvas, QgsMapCanvas)

        ext = SpatialExtent.fromLayer(lyr).toCrs(canvas.mapSettings().destinationCrs())
        if isinstance(ext, SpatialExtent):
            canvas.setExtent(ext)
        else:
            s = ""



    def setLayerStyle(self, layer, canvas):


        showLayerPropertiesDialog(layer, canvas, modal=True)


class DockManager(QObject):
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
        self.mDataSourceManager = None

    def connectDataSourceManager(self, dataSourceManager:DataSourceManager):
        assert isinstance(dataSourceManager, DataSourceManager)
        self.mDataSourceManager = dataSourceManager
        pass

    def dataSourceManager(self)->DataSourceManager:
        return self.mDataSourceManager


    def mapDocks(self)->typing.List[SpectralLibraryDock]:
        return [d for d in self if isinstance(d, MapDock)]

    def spectraLibraryDocks(self)->typing.List[SpectralLibraryDock]:
        return [d for d in self if isinstance(d, SpectralLibraryDock)]



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

        dockArea.sigDragEnterEvent.connect(lambda event: self.onDockAreaDragDropEvent(dockArea, event))
        dockArea.sigDragMoveEvent.connect(lambda event: self.onDockAreaDragDropEvent(dockArea, event))
        dockArea.sigDragLeaveEvent.connect(lambda event: self.onDockAreaDragDropEvent(dockArea, event))
        dockArea.sigDropEvent.connect(lambda event: self.onDockAreaDragDropEvent(dockArea, event))
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
            mimeData = event.mimeData()
            assert isinstance(mimeData, QMimeData)
            if containsMapLayers(mimeData):
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
            mimeData = event.mimeData()
            assert isinstance(mimeData, QMimeData)

            speclibs = extractSpectralLibraries(mimeData)
            speclibUris = [s.source() for s in speclibs]
            layers = extractMapLayers(mimeData)
            layers = [l for l in layers if l.source() not in speclibUris]
            textfiles = []


            # register datasources
            for src in layers + textfiles + speclibs:
                self.mDataSourceManager.addSource(src)

            # open map dock for new layers
            if len(speclibs) > 0:
                NEW_DOCK = self.createDock('SPECLIB')
                assert isinstance(NEW_DOCK, SpectralLibraryDock)
                sl = NEW_DOCK.speclib()
                assert isinstance(sl, SpectralLibrary)
                sl.startEditing()
                for speclib in speclibs:
                    NEW_DOCK.speclib().addSpeclib(speclib, addMissingFields=True)
                sl.commitChanges()

            # open map dock for new layers
            if len(layers) > 0:
                NEW_DOCK = self.createDock('MAP')
                assert isinstance(NEW_DOCK, MapDock)
                NEW_DOCK.addLayers(layers)


            # open test dock for new text files
            for textSource in textfiles:
                if re.search('(xml|html)$', os.path.basename(textSource.uri)):
                    dock = self.createDock('WEBVIEW')
                    dock.load(textSource.uri)
                else:
                    self.createDock('TEXT', plainTxt=open(textSource.uri).read())
            event.accept()

    def __len__(self):
        """
        Returns the number of Docks.
        :return: int
        """
        return len(self.mDocks)

    def __iter__(self):
        """
        Iterator over all Docks.
        """
        return iter(self.mDocks)

    def docks(self, dockType=None)->list:
        """
        Returns the managed docks.
        :param dockType: type of Dock to be returned. Default = None to return all Docks
        :return: [list-of-Docks controlled by this DockManager]
        """
        if isinstance(dockType, str):
            dockType = LUT_DOCKTYPES[dockType]
        if dockType is None:
            return self.mDocks[:]
        else:
            return [d for d in self.mDocks if isinstance(d, dockType)]

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
        """
        Removes a Dock instances
        :param dock:
        :return:
        """
        if dock in self.mDocks:
            self.mDocks.remove(dock)

            if dock.container():
                dock.close()
            self.sigDockRemoved.emit(dock)
            return True
        return False

    def createDock(self, dockType, *args, **kwds)->Dock:
        """
        Creates and returns a new Dock
        :param dockType: str or Dock class, e.g. 'MAP' or MapDock
        :param args:
        :param kwds:
        :return:
        """
        assert dockType in LUT_DOCKTYPES.keys(), 'dockType must be from [{}]'.format(','.join(['"{}"'.format(k) for k in LUT_DOCKTYPES.keys()]))
        cls = LUT_DOCKTYPES[dockType]

        #create the dock name
        existingDocks = self.docks(dockType)
        existingNames = [d.title() for d in existingDocks]
        n = len(existingDocks) + 1
        dockTypes = [MapDock, TextDock, MimeDataDock, WebViewDock, SpectralLibraryDock]
        dockBaseNames = ['Map', 'Text', 'MimeData', 'HTML Viewer', 'SpectralLibrary']
        baseName = 'Dock'
        if cls in dockTypes:
            baseName = dockBaseNames[dockTypes.index(cls)]
        name = '{} #{}'.format(baseName, n)
        while name in existingNames:
            n += 1
            name = '{} #{}'.format(baseName, n)
        kwds['name'] = name

        dock = None
        if cls == MapDock:
            dock = MapDock(*args, **kwds)
            if isinstance(self.mDataSourceManager, DataSourceManager):
                dock.sigLayersAdded.connect(self.mDataSourceManager.addSources)

        elif cls == TextDock:
            dock = TextDock(*args, **kwds)

        elif cls == MimeDataDock:
            dock = MimeDataDock(*args, **kwds)

        elif cls == WebViewDock:
            dock = WebViewDock(*args, **kwds)

        elif cls == SpectralLibraryDock:
            dock = SpectralLibraryDock(*args, **kwds)
            dock.mSpeclibWidget.setMapInteraction(False)

        else:
            raise Exception('Unknown dock type: {}'.format(dockType))

        dockArea = kwds.get('dockArea', self.currentDockArea())
        if not isinstance(dockArea, DockArea):
            warnings.warn('DockManager not connected to any DockArea yet. \nAdd DockAreas with connectDockArea(self, dockArea)')
        else:
            dockArea.addDock(dock, *args, **kwds)
            if dock not in self.mDocks:
                dock.sigClosed.connect(self.removeDock)
                self.mDocks.append(dock)

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



class DockPanelUI(QgsDockWidget, loadUI('dockpanel.ui')):
    def __init__(self, parent=None):
        super(DockPanelUI, self).__init__(parent)
        self.setupUi(self)
        self.dockManager = None
        assert isinstance(self.dockTreeView, DockTreeView)

        self.initActions()

    def initActions(self):

        self.btnCollapse.setDefaultAction(self.actionCollapseTreeNodes)
        self.btnExpand.setDefaultAction(self.actionExpandTreeNodes)

        self.actionCollapseTreeNodes.triggered.connect(self.dockTreeView.collapseAllNodes)
        self.actionExpandTreeNodes.triggered.connect(self.dockTreeView.expandAllNodes)



    def connectDockManager(self, dockManager:DockManager):
        """
        Connects the DockPanelUI with a DockManager
        :param dockManager:
        :return:
        """
        assert isinstance(dockManager, DockManager)
        self.dockManager = dockManager
        self.model = DockManagerTreeModel(self.dockManager)
        self.dockTreeView.setModel(self.model)
        assert self.model == self.dockTreeView.model()
        self.menuProvider = DockManagerLayerTreeModelMenuProvider(self.dockTreeView)
        self.dockTreeView.setMenuProvider(self.menuProvider)


        s = ""


class MapCanvasBridge(QgsLayerTreeMapCanvasBridge):

    def __init__(self, root, canvas, parent=None):
        super(MapCanvasBridge, self).__init__(root, canvas)
        assert isinstance(root, MapDockTreeNode)
        assert isinstance(canvas, MapCanvas)
        self.mRootNode = root
        self.mCanvas = canvas
        assert self.mCanvas == self.mapCanvas()
        self.mapCanvas().layersChanged.connect(self.setLayerTreeLayers)
        self.mCanvas.sigLayersCleared.connect(self.mRootNode.clear)

    def setLayerTreeLayers(self):

        canvasLayers = self.mapCanvas().layers()
        treeNodeLayerNodes = self.rootGroup().findLayers()
        treeNodeLayers = [n.layer() for n in treeNodeLayerNodes]

        # new layers to add?
        newChildLayers = [l for l in canvasLayers if l not in treeNodeLayers]

        # layers to set visible?
        for layer in canvasLayers:
            if layer not in treeNodeLayers:
                # insert layer on top of layer tree
                self.rootGroup().insertLayer(0, layer)

            # set canvas on visible
            lNode = self.rootGroup().findLayer(layer.id())
            lNode.setItemVisibilityChecked(Qt.Checked)

        # layers to hide?
        for layer in treeNodeLayers:
            if isinstance(layer, QgsMapLayer) and layer not in canvasLayers:
                lnode = self.rootGroup().findLayer(layer.id())
                if isinstance(lnode, QgsLayerTreeLayer):
                    lnode.setItemVisibilityChecked(Qt.Unchecked)



def createDockTreeNode(dock:Dock, parent=None)->DockTreeNode:
    if isinstance(dock, Dock):
        dockType = type(dock)
        if dockType is MapDock:
            return MapDockTreeNode(parent, dock)
        elif dockType in [TextDock]:
            return TextDockTreeNode(parent, dock)
        elif dockType is SpectralLibraryDock:
            return SpeclibDockTreeNode(parent, dock)
        else:
            return DockTreeNode(parent, dock)
    return None




class CheckableLayerTreeNode(LayerTreeNode):
    def __init__(self, *args, **kwds):
        super(CheckableLayerTreeNode, self).__init__(*args, **kwds)
    sigCheckStateChanged = pyqtSignal(Qt.CheckState)
    def __init__(self, *args, **kwds):
        super(CheckableLayerTreeNode, self).__init__(*args, **kwds)
        self.mCheckState = Qt.Unchecked

    def setCheckState(self, checkState):
        if isinstance(checkState, bool):
            checkState == Qt.Checked if checkState else Qt.Unchecked
        assert isinstance(checkState, Qt.CheckState)
        old = self.mCheckState
        self.mCheckState = checkState
        if old != self.mCheckState:
            self.sigCheckStateChanged.emit(self.mCheckState)

    def checkState(self):
        return self.mCheckState

class LayerTreeViewMenuProvider(QgsLayerTreeViewMenuProvider):

    def __init__(self, treeView):
        super(LayerTreeViewMenuProvider, self).__init__()
        assert isinstance(treeView, DockTreeView)
        assert isinstance(treeView.model(), DockManagerTreeModel)
        self.treeView = treeView
        self.model = treeView.model()

    def currentNode(self):
        return self.treeView.currentNode()

    def currentIndex(self):
        return self.treeView.currentIndex()

    def currentColumnName(self):
        return self.model.columnNames[self.currentIndex().column()]

    def createContextMenu(self):
        """
        Returns the current nodes contextMenu.
        Overwrite to add TreeViewModel specific logic.
        :return:
        """
        node = self.currentNode()
        if isinstance(node, LayerTreeNode):
            return self.currentNode().contextMenu()
        else:
            return QMenu()
