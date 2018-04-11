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

import six, sys, os, gc, re, collections

from qgis.core import *
from qgis.gui import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from osgeo import gdal, ogr
from enmapbox.gui.treeviews import *
from enmapbox.gui.mapcanvas import *
from enmapbox.gui.utils import *
from enmapbox.gui.mimedata import *



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
            # self.dock.sigVisibilityChanged.connec(self.)
            self.setCustomProperty('uuid', '{}'.format(dock.uuid))
            # self.dock.sigClosed.connect(self.removedisconnectDock)


class TextDockTreeNode(DockTreeNode):
    def __init__(self, parent, dock):
        assert isinstance(dock, TextDock)
        super(TextDockTreeNode, self).__init__(parent, dock)
        self.setIcon(QIcon(IconProvider.Dock))

    def connectDock(self, dock):
        assert isinstance(dock, TextDock)
        super(TextDockTreeNode, self).connectDock(dock)

        self.fileNode = TreeNode(self, 'File')
        dock.textDockWidget.sigSourceChanged.connect(self.setLinkedFile)
        self.setLinkedFile(dock.textDockWidget.mFile)

    def setLinkedFile(self, path):
        self.fileNode.setValue(path)
        self.fileNode.setTooltip(path)

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


class SpeclibDockTreeNode(DockTreeNode):
    def __init__(self, parent, dock):
        super(SpeclibDockTreeNode, self).__init__(parent, dock)
        self.setIcon(QIcon(':/enmapbox/icons/viewlist_spectrumdock.png'))

    def connectDock(self, dock):
        assert isinstance(dock, SpectralLibraryDock)
        super(SpeclibDockTreeNode, self).connectDock(dock)
        from enmapbox.gui.spectrallibraries import SpectralLibraryWidget
        self.speclibWidget = dock.speclibWidget
        assert isinstance(self.speclibWidget, SpectralLibraryWidget)

        self.showMapSpectra = CheckableTreeNode(self, 'Show map profiles', checked=Qt.Checked)
        self.showMapSpectra.setCheckState(Qt.Checked if self.speclibWidget.mapInteraction() else Qt.Unchecked)
        self.showMapSpectra.sigCheckStateChanged.connect(
            lambda s: self.speclibWidget.setMapInteraction(s == Qt.Checked))
        self.profilesNode = TreeNode(self, 'Profiles', value=0)
        self.speclibWidget.mSpeclib.sigProfilesAdded.connect(self.updateNodes)
        self.speclibWidget.mSpeclib.sigProfilesRemoved.connect(self.updateNodes)

    def updateNodes(self):
        from enmapbox.gui.spectrallibraries import SpectralLibraryWidget
        assert isinstance(self.speclibWidget, SpectralLibraryWidget)
        self.profilesNode.setValue(len(self.speclibWidget.mSpeclib))


class MapDockTreeNode(DockTreeNode):
    """
    A TreeNode linked to a MapDock
    Acts like the QgsLayerTreeMapCanvasBridge
    """

    def __init__(self, parent, dock):

        super(MapDockTreeNode, self).__init__(parent, dock)
        # KeepRefs.__init__(self)
        self.setIcon(QIcon(':/enmapbox/icons/viewlist_mapdock.png'))
        self.addedChildren.connect(lambda: self.updateCanvas())
        self.removedChildren.connect(lambda: self.updateCanvas())

    def connectDock(self, dock):
        assert isinstance(dock, MapDock)
        super(MapDockTreeNode, self).connectDock(dock)
        # TreeNode(self, 'Layers')

        self.layerNode = QgsLayerTree()
        self.layerNode.setName('Layers')
        self.addChildNode(self.layerNode)

        #self.mTreeCanvasBridge = QgsLayerTreeMapCanvasBridge(self.layerNode, self.dock.canvas)
        self.mTreeCanvasBridge = MapCanvasBridge(self.layerNode, self.dock.canvas)


        # self.layerNode = TreeNode(self, 'Layers')

        self.crsNode = CRSTreeNode(self, dock.canvas.mapSettings().destinationCrs())
        self.crsNode.setExpanded(False)

        self.linkNode = CanvasLinkTreeNodeGroup(self, dock.canvas)
        self.linkNode.setExpanded(False)

        self.dock.canvas.destinationCrsChanged.connect(lambda : self.crsNode.setCrs(self.dock.canvas.mapSettings().destinationCrs()))

        #self.dock.sigLayersAdded.connect(self.updateChildNodes)
        #self.dock.sigLayersRemoved.connect(self.updateChildNodes)
        #self.dock.sigCrsChanged.connect(self.crsNode.setCrs)
        #self.updateChildNodes()


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
                lNode.setItemVisibilityChecked(Qt.Checked)

        return self

    def updateCanvas(self):
        # reads the nodes and sets the map canvas accordingly
        if self.dock:

            self.mTreeCanvasBridge.setCanvasLayers()
            return

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
                    s = "" #logger.warning('QgsLayerTreeLayer.layer() is none')
        else:
            raise NotImplementedError()

        for l in lyrs:
            assert isinstance(l, QgsMapLayer), l

        return lyrs

    def removeLayerNodesByURI(self, uri):

        toRemove = []
        for lyrNode in self.findLayers():
            uriLyr = lyrNode.layer().dataProvider().dataSourceUri()
            if uriLyr == uri:
                toRemove.append(lyrNode)

        for node in toRemove:
            node.parent().removeChildNode(node)

    def insertLayer(self, idx, layerSource):
        """
        Inserts a new QgsMapLayer on position idx by creating a new QgsMayTreeLayer node
        :param idx:
        :param layerSource:
        :return:
        """
        from enmapbox.gui.datasourcemanager import DataSourceManager
        dsm = DataSourceManager.instance()

        renderer = None
        layerTreeLayers = []
        if isinstance(layerSource, QgsMapLayer):
            renderer = layerSource.renderer()

        if isinstance(dsm, DataSourceManager):

            sources = dsm.addSource(layerSource)
            newLayers = [s.createUnregisteredMapLayer() for s in sources if isinstance(s, DataSourceSpatial)]

            for l in newLayers:
                if renderer is not None:
                    l.setRenderer(renderer)
                layerTreeLayers.append(QgsLayerTreeLayer(l))
                ""
        elif isinstance(layerSource, QgsMapLayer):
            layerTreeLayers.append(QgsLayerTreeLayer(layerSource))

        for l in layerTreeLayers:
            assert isinstance(l, QgsLayerTreeLayer)
            QgsProject.instance().addMapLayer(l.layer())
            self.layerNode.insertChildNode(idx, l)


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
        node.readCommonXml(element)
        # node.readChildrenFromXml(element)

        # try to find the dock by its uuid in dockmanager
        dockManager = EnMAPBox.instance().dockManager
        uuid = node.customProperty('uuid', None)
        if uuid:
            dock = dockManager.getDockWithUUID(''.format(uuid))
        if dock is None:
            dock = dockManager.createDock('MAP', name=node.name())
        node.connectDock(dock)
        return node


class DockPanelUI(PanelWidgetBase, loadUI('dockpanel.ui')):
    def __init__(self, parent=None):
        super(DockPanelUI, self).__init__(parent)
        self.dockManager = None
        assert isinstance(self.dockTreeView, TreeView)

        s = ""

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
        self.columnNames = ['Dock/Property', 'Value']
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
        if node is None:
            node = self.index2legendNode(index)
            if isinstance(node, QgsLayerTreeModelLegendNode):
                return self.legendNodeFlags(node)
                #return super(QgsLayerTreeModel,self).flags(index)
                return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
        #print('node: {}  {}'.format(node, type(node)))
        dockNode = self.parentNodesFromIndices(index, nodeInstanceType=DockTreeNode)
        if len(dockNode) == 0:
            return Qt.NoItemFlags
        elif len(dockNode) > 1:
            print('DEBUG: Multiple docknodes selected')
            return Qt.NoItemFlags
        else:
            dockNode = dockNode[0]

        if node is None:
            return Qt.NoItemFlags


        column = index.column()
        isL1 = node.parent() == self.rootNode
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable

        # normal tree nodes


        if isinstance(node, TreeNode):
            if column == 0:
                if isinstance(node, DockTreeNode):
                    flags |= Qt.ItemIsUserCheckable | \
                             Qt.ItemIsEditable | \
                             Qt.ItemIsDropEnabled
                    if isL1:
                        flags |= Qt.ItemIsDropEnabled


                if node.name() == 'Layers':
                    flags |= Qt.ItemIsUserCheckable

                if isinstance(node, CheckableTreeNode):
                    flags |= Qt.ItemIsUserCheckable

                    # mapCanvas Layer Tree Nodes
        elif type(node) in [QgsLayerTreeLayer, QgsLayerTreeGroup]:
            if column == 0:
                flags |= Qt.ItemIsUserCheckable | Qt.ItemIsEditable | Qt.ItemIsDropEnabled

            if isinstance(dockNode, MapDockTreeNode) and node != dockNode.layerNode:
                flags |= Qt.ItemIsDragEnabled
        elif not isinstance(node, QgsLayerTree):
            s = ""

        return flags

    def mimeTypes(self):
        # specifies the mime types handled by this model
        types = [MimeDataHelper.MDF_DOCKTREEMODELDATA,
                 MimeDataHelper.MDF_LAYERTREEMODELDATA,
                 MimeDataHelper.MDF_TEXT_HTML,
                 MimeDataHelper.MDF_TEXT_PLAIN,
                 MimeDataHelper.MDF_URILIST,
                 MimeDataHelper.MDF_PYTHON_OBJECTS]
        return types

    def dropMimeData(self, mimeData, action, row, column, parentIndex):
        assert isinstance(mimeData, QMimeData)


        if not parentIndex.isValid():
            return False

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

            if mimeData.hasFormat(MDF_LAYERTREEMODELDATA):
                doc = QDomDocument()
                xml = fromByteArray(mimeData.data(MDF_LAYERTREEMODELDATA))

                sources = re.findall('(?<=source=")[^<>"]*(?=")', xml)
                doc.setContent(xml)
                root = doc.documentElement()
                context = QgsReadWriteContext()
                layerTree = QgsLayerTree.readXml(root,context)
                mapLayers = []

                regLayers = QgsProject.instance().mapLayers()
                for layerTreeLayer in layerTree.findLayers():
                    assert isinstance(layerTreeLayer, QgsLayerTreeLayer)
                    if layerTreeLayer.layerId() in regLayers.keys():
                        mapLayers.append(regLayers[layerTreeLayer.layerId()])
                if len(mapLayers) > 0:
                    for l in mapLayers:
                        dockNode.insertLayer(0, l)
                    return True
                if len(sources) > 0:
                    for s in sources:
                        dockNode.insertLayer(0, s)
                    return True

            if mimeData.hasUrls():
                for url in mimeData.urls():
                    dockNode.insertLayer(0, url)
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
        context = QgsReadWriteContext()
        for node in nodesFinal:
            node.writeXml(rootElem, context)
        doc.appendChild(rootElem)
        mimeData.setData("application/enmapbox.docktreemodeldata", toByteArray(doc))

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
            mimeData.setData(MDF_LAYERTREEMODELDATA, toByteArray(doc))
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

        if isinstance(legendNode, QgsSymbolLegendNode):
            return super(DockManagerTreeModel, self).data(index, role)
            s = ""

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
                    if isinstance(node, CheckableTreeNode):
                        return node.checkState()
            else:
                if role == Qt.DisplayRole:
                    return node.value()

        return None
        # return super(DockManagerTreeModel, self).data(index, role)

    def setData(self, index, value, role=None):
        node = self.index2node(index)
        if node is None:
            node = self.index2legendNode(index)
            if isinstance(node, QgsLayerTreeModelLegendNode):
                #this does not work:
                #result = super(QgsLayerTreeModel,self).setData(index, value, role=role)
                result = node.setData(value, role)
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

        if isinstance(node, CheckableTreeNode) and role == Qt.CheckStateRole:
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


class DockManagerTreeModelMenuProvider(TreeViewMenuProvider):
    def __init__(self, treeView):
        super(DockManagerTreeModelMenuProvider, self).__init__(treeView)
        assert isinstance(self.treeView.model(), DockManagerTreeModel)

    def createContextMenu(self):
        col = self.currentIndex().column()
        node = self.currentNode()
        if node is None:
            return
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
                a.triggered.connect(lambda: QApplication.clipboard().setText('{}'.format(node.value())))

        return menu

    def setLayerStyle(self, layer, canvas):
        from enmapbox.gui.layerproperties import showLayerPropertiesDialog
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
        self.dataSourceManager = None

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
            speclibs = []

            if MH.hasMapLayers():
                layers = MH.mapLayers()
            elif MH.hasDataSources():
                for ds in MH.dataSources():
                    if isinstance(ds, DataSourceSpatial):
                        layers.append(ds.createUnregisteredMapLayer())
                    elif isinstance(ds, DataSourceTextFile):
                        textfiles.append(ds)
                    elif isinstance(ds, DataSourceSpectralLibrary):
                        speclibs.append(ds)

            # register datasources
            for src in layers + textfiles + speclibs:
                self.dataSourceManager.addSource(src)

            # open map dock for new layers
            if len(layers) > 0:
                NEW_DOCK = self.createDock('MAP')
                assert isinstance(NEW_DOCK, MapDock)
                NEW_DOCK.addLayers(layers)

            if len(speclibs) > 0:
                NEW_DOCK = self.createDock('SPECLIB')
                assert isinstance(NEW_DOCK, SpectralLibraryDock)
                from spectrallibraries import SpectralLibrary
                for speclib in speclibs:
                    NEW_DOCK.speclibWidget.addSpeclib(SpectralLibrary.readFrom(speclib.uri()))

            # open test dock for new text files
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



class MapCanvasBridge(QgsLayerTreeMapCanvasBridge):

    def __init__(self, root, canvas, parent=None):
        super(MapCanvasBridge, self).__init__(root, canvas)

        self.mapCanvas().layersChanged.connect(self.setLayerTreeLayers)
        s = ""

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

        s = ""