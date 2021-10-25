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
*   the Free Software Foundation; either version 3 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
import os
import re
import uuid
import typing
import time

from PyQt5.QtWidgets import QToolButton, QAction
from qgis.core import QgsWkbTypes

from qgis.core import Qgis
from qgis.gui import QgsLayerTreeProxyModel

from enmapbox.externals.qps.speclib.core import is_spectral_library, profile_field_list
from processing import Processing
from qgis.PyQt.QtWidgets import QHeaderView, QMenu, QAbstractItemView, QApplication
from qgis.PyQt.QtCore import Qt, QMimeData, QModelIndex, QObject, QTimer, pyqtSignal, QEvent, QSortFilterProxyModel

from qgis.PyQt.QtGui import QIcon, QDragEnterEvent, QDragMoveEvent, QDropEvent, QDragLeaveEvent
from qgis.PyQt.QtXml import QDomDocument, QDomElement
from qgis.core import QgsMapLayer, QgsVectorLayer, QgsRasterLayer, QgsProject, QgsReadWriteContext, \
    QgsLayerTreeLayer, QgsLayerTreeNode, QgsLayerTreeGroup, \
    QgsLayerTreeModelLegendNode, QgsLayerTree, QgsLayerTreeModel, QgsLayerTreeUtils, \
    QgsPalettedRasterRenderer, QgsProcessingFeedback

from qgis.gui import QgsLayerTreeView, \
    QgsMapCanvas, QgsLayerTreeViewMenuProvider, QgsLayerTreeMapCanvasBridge, QgsDockWidget, QgsMessageBar

from enmapbox import debugLog
from enmapbox.gui import \
    SpectralLibrary, SpectralLibraryWidget, SpatialExtent, findParent, loadUi, showLayerPropertiesDialog

from enmapbox.gui.utils import enmapboxUiPath
from enmapbox.gui.mapcanvas import \
    MapCanvas, KEY_LAST_CLICKED
from enmapbox.gui.mimedata import \
    MDF_QGIS_LAYERTREEMODELDATA, MDF_ENMAPBOX_LAYERTREEMODELDATA, QGIS_URILIST_MIMETYPE, \
    MDF_TEXT_HTML, MDF_URILIST, MDF_TEXT_PLAIN, MDF_QGIS_LAYER_STYLE, \
    extractMapLayers, containsMapLayers, textToByteArray
from enmapbox.gui.dataviews.docks import Dock, DockArea, \
    AttributeTableDock, SpectralLibraryDock, TextDock, MimeDataDock, WebViewDock, LUT_DOCKTYPES, MapDock
from enmapbox.gui.datasources.datasources import DataSource, VectorDataSource, SpatialDataSource
from enmapbox.externals.qps.layerproperties import pasteStyleFromClipboard, pasteStyleToClipboard
from enmapbox.gui.datasources.manager import DataSourceManager
from enmapbox.gui.utils import getDOMAttributes
from enmapboxprocessing.renderer.classfractionrenderer import ClassFractionRendererWidget
from enmapboxprocessing.renderer.decorrelationstretchrenderer import DecorrelationStretchRendererWidget


class LayerTreeNode(QgsLayerTree):
    sigIconChanged = pyqtSignal()
    sigValueChanged = pyqtSignal(QObject)
    sigRemoveMe = pyqtSignal()

    def __init__(self, name: str, value=None, checked=Qt.Unchecked, tooltip=None, icon=None):
        # QObject.__init__(self)
        super(LayerTreeNode, self).__init__()
        # assert name is not None and len(str(name)) > 0

        self.mParent = None
        self.mTooltip: str = None
        self.mValue = None
        self.mIcon: QIcon = None

        self.mXmlTag = 'tree-node'

        self.setName(name)
        self.setValue(value)
        self.setExpanded(False)
        # self.setVisible(False)
        self.setTooltip(tooltip)
        self.setIcon(icon)

        # if parent is not None:
        #    parent.addChildNode(self)
        #    if isinstance(parent, LayerTreeNode):
        #        self.sigValueChanged.connect(parent.sigValueChanged)

    def dump(self, *args, **kwargs) -> str:

        d = super(LayerTreeNode, self).dump()
        d += '{}:"{}":"{}"\n'.format(self.__class__.__name__, self.name(), self.value())
        return d

    def xmlTag(self) -> str:
        return self.mXmlTag

    def _removeSubNode(self, node):
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

    def populateContextMenu(self, menu: QMenu):
        """
        Allows to add QActions and QMenues to a parent menu
        """
        pass

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

        # custom properties
        self.writeCommonXml(elem)

        for node in self.children():
            node.writeXML(elem)
        parentElement.appendChild(elem)

        # return elem

    def readChildrenFromXml(self, element):
        nodes = []
        childElem = element.firstChildElement()
        while (not childElem.isNull()):
            elem = childElem
            tagName = elem.tagName()
            node = None
            attributes = getDOMAttributes(elem)

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
    """
    Base TreeNode to symbolise a Dock
    """
    sigDockUpdated = pyqtSignal()

    def __init__(self, dock: Dock):
        assert isinstance(dock, Dock)
        self.dock = dock
        super(DockTreeNode, self).__init__('<dockname not available>')

        self.mIcon = QIcon(':/enmapbox/gui/ui/icons/viewlist_dock.svg')
        self.dock = dock
        self.setName(dock.title())
        self.dock.sigTitleChanged.connect(self.setName)
        self.mEnMAPBoxInstance = None

    def __repr__(self):
        return f'<{self.__class__.__name__} at {id(self)}>'

    def setEnMAPBoxInstance(self, enmapbox: 'EnMAPBox'):
        from enmapbox import EnMAPBox
        if isinstance(enmapbox, EnMAPBox):
            self.mEnMAPBoxInstance = enmapbox

    def enmapBoxInstance(self) -> 'EnMAPBox':
        return self.mEnMAPBoxInstance

    def writeXML(self, parentElement):
        elem = super(DockTreeNode, self).writeXML(parentElement)
        elem.setTagName('dock-tree-node')
        return elem

    def writeLayerTreeGroupXML(self, parentElement):
        QgsLayerTreeGroup.writeXML(self, parentElement)

        # return super(QgsLayerTreeNode,self).writeXml(parentElement)


class TextDockTreeNode(DockTreeNode):
    def __init__(self, dock):
        assert isinstance(dock, TextDock)
        super(TextDockTreeNode, self).__init__(dock)
        self.setIcon(QIcon(':/enmapbox/gui/ui/icons/viewlist_dock.svg'))

        assert isinstance(dock, TextDock)

        self.fileNode = LayerTreeNode('File')
        dock.mTextDockWidget.sigSourceChanged.connect(self.setLinkedFile)
        self.setLinkedFile(dock.mTextDockWidget.mFile)
        self.addChildNode(self.fileNode)

    def setLinkedFile(self, path):
        self.fileNode.setValue(path)
        self.fileNode.setTooltip(path)


class AttributeTableDockTreeNode(DockTreeNode):
    def __init__(self, dock):
        assert isinstance(dock, AttributeTableDock)
        super(AttributeTableDockTreeNode, self).__init__(dock)
        self.setIcon(QIcon(r':/enmapbox/gui/ui/icons/viewlist_attributetabledock.svg'))


class SpeclibDockTreeNode(DockTreeNode):
    def __init__(self, dock):
        super().__init__(dock)

        self.setIcon(QIcon(':/enmapbox/gui/ui/icons/viewlist_spectrumdock.svg'))
        self.mSpeclibWidget: SpectralLibraryWidget = None
        self.profilesNode: LayerTreeNode = LayerTreeNode('Profiles')
        self.profilesNode.setIcon(QIcon(':/qps/ui/icons/profile.svg'))

        self.mPROFILES: typing.Dict[str, int] = dict()

        assert isinstance(dock, SpectralLibraryDock)
        self.mSpeclibWidget = dock.mSpeclibWidget
        assert isinstance(self.mSpeclibWidget, SpectralLibraryWidget)

        self.speclibNode = QgsLayerTreeLayer(self.speclib())

        # self.addChildNode(self.profilesNode)
        self.addChildNode(self.speclibNode)
        speclib = self.speclib()
        if is_spectral_library(speclib):
            speclib: QgsVectorLayer
            speclib.editCommandEnded.connect(self.updateNodes)
            speclib.committedFeaturesAdded.connect(self.updateNodes)
            speclib.committedFeaturesRemoved.connect(self.updateNodes)
            self.updateNodes()

    def speclib(self) -> SpectralLibrary:
        return self.speclibWidget().speclib()

    def speclibWidget(self) -> SpectralLibraryWidget:
        return self.mSpeclibWidget

    def updateNodes(self):

        PROFILES = dict()
        debugLog('update speclib nodes')
        if isinstance(self.mSpeclibWidget, SpectralLibraryWidget):
            sl: SpectralLibrary = self.mSpeclibWidget.speclib()
            if is_spectral_library(sl):
                # count number of profiles
                n = 0
                for field in profile_field_list(sl):
                    for f in sl.getFeatures(f'"{field.name()}" is not NULL'):
                        # show committed only?
                        # if f.id() >= 0:
                        n += 1
                    PROFILES[field.name()] = n

        if PROFILES != self.mPROFILES:
            self.profilesNode.removeAllChildren()
            new_nodes = []
            n_total = 0
            tt = [f'{len(PROFILES)} Spectral Profiles fields with:']
            for name, cnt in PROFILES.items():
                n_total += cnt
                node = LayerTreeNode(f'{name} {cnt}')
                node.setIcon(QIcon(r':/qps/ui/icons/profile.svg'))
                # node.setValue(cnt)
                tt.append(f'{name}: {cnt} profiles')
                new_nodes.append(node)
                self.profilesNode.addChildNode(node)

            self.profilesNode.setTooltip('\n'.join(tt))
            self.profilesNode.setName(f'{n_total} Profiles')
            self.profilesNode.setValue(n_total)

            self.mPROFILES = PROFILES


class MapDockTreeNode(DockTreeNode):
    """
    A TreeNode linked to a MapDock
    Acts like the QgsLayerTreeMapCanvasBridge
    """

    sigAddedLayers = pyqtSignal(list)
    sigRemovedLayers = pyqtSignal(list)

    def __init__(self, dock):
        super(MapDockTreeNode, self).__init__(dock)
        assert isinstance(self.dock, MapDock)
        self.setIcon(QIcon(':/enmapbox/gui/ui/icons/viewlist_mapdock.svg'))
        self.addedChildren.connect(self.onAddedChildren)
        self.removedChildren.connect(self.onRemovedChildren)
        self.willRemoveChildren.connect(self.onWillRemoveChildren)
        self.mRemovedLayerCache = []

        canvas = self.dock.mapCanvas()
        assert isinstance(canvas, MapCanvas)

        existingLayers = canvas.layers()
        self.mTreeCanvasBridge = MapCanvasBridge(self, canvas)

        # re-add layers that have been visible in the canvas before
        missing = [l for l in existingLayers if l not in canvas.layers()]
        for l in missing:
            self.addLayer(l)
        self.mTreeCanvasBridge.setCanvasLayers()

    def onAddedChildren(self, node, idxFrom, idxTo):
        self.updateCanvas()
        lyrs = []
        for n in node.children()[idxFrom:idxTo + 1]:
            if type(n) == QgsLayerTreeLayer:
                lyrs.append(n.layer())
        if len(lyrs) > 0:
            self.sigAddedLayers.emit(lyrs)

    def onWillRemoveChildren(self, node, idx_from, idx_to):
        self.mRemovedLayerCache.clear()
        to_remove = []
        for n in node.children()[idx_from:idx_to + 1]:
            if type(n) == QgsLayerTreeLayer:
                to_remove.append(n.layer())
        self.mRemovedLayerCache.extend(to_remove)

    def onRemovedChildren(self, node, idxFrom, idxTo):
        self.updateCanvas()
        self.sigRemovedLayers[list].emit(self.mRemovedLayerCache[:])
        self.mRemovedLayerCache.clear()

    def mapCanvas(self) -> MapCanvas:
        """
        Returns the MapCanvas
        :return: MapCanvas
        """
        return self.dock.mapCanvas()

    def updateCanvas(self):
        # reads the nodes and sets the map canvas accordingly
        self.mTreeCanvasBridge.setCanvasLayers()

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
                    s = ""  # logger.warning('QgsLayerTreeLayer.layer() is none')
        else:
            raise NotImplementedError()

        for l in lyrs:
            assert isinstance(l, QgsMapLayer), l

        return lyrs

    def removeLayerNodesByURI(self, uri: str):
        """
        Removes each layer node that relates to a source with the given uri
        :param uri:
        :type uri:
        :return:
        :rtype:
        """

        nodesToRemove = []
        for lyrNode in self.findLayers():
            lyr = lyrNode.layer()
            if isinstance(lyr, QgsMapLayer):
                uriLyr = lyrNode.layer().source()
                if uriLyr == uri:
                    nodesToRemove.append(lyrNode)

        for node in nodesToRemove:
            node.parent().removeChildNode(node)
            s = ""

    def insertLayer(self, idx, layerSource):
        """
        Inserts a new QgsMapLayer or SpatialDataSource on position idx by creating a new QgsMayTreeLayer node
        :param idx:
        :param layerSource:
        :return:
        """
        from enmapbox.gui.enmapboxgui import EnMAPBox

        mapLayers = []
        if isinstance(layerSource, QgsMapLayer):
            mapLayers.append(layerSource)
        else:
            s = ""
        emb = self.enmapBoxInstance()
        if isinstance(emb, EnMAPBox):
            emb.addSources(mapLayers)

        for mapLayer in mapLayers:
            assert isinstance(mapLayer, QgsMapLayer)
            # QgsProject.instance().addMapLayer(mapLayer)
            l = QgsLayerTreeLayer(mapLayer)
            # self.layerNode.insertChildNode(idx, l)
            self.insertChildNode(idx, l)


class DockManagerTreeModel(QgsLayerTreeModel):
    def __init__(self, dockManager, parent=None):
        self.rootNode: LayerTreeNode = LayerTreeNode('<hidden root node>')
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
            # self.setFlag(QgsLayerTreeModel.ShowRasterPreviewIcon, False)

            self.setFlag(QgsLayerTreeModel.DeferredLegendInvalidation, True)
            # self.setFlag(QgsLayerTreeModel.UseEmbeddedWidget, True)

            # behavioral
            self.setFlag(QgsLayerTreeModel.AllowNodeReorder, True)
            self.setFlag(QgsLayerTreeModel.AllowNodeRename, True)
            self.setFlag(QgsLayerTreeModel.AllowNodeChangeVisibility, True)
            self.setFlag(QgsLayerTreeModel.AllowLegendChangeState, True)
            # self.setFlag(QgsLayerTreeModel.ActionHierarchical, False)

            self.setAutoCollapseLegendNodes(10)

        self.mDockManager = dockManager

        for dock in dockManager:
            self.addDock(dock)

        self.mDockManager.sigDockAdded.connect(self.addDock)
        self.mDockManager.sigDockWillBeRemoved.connect(self.removeDock)

    def columnCount(self, index) -> int:
        node = self.index2node(index)
        if type(node) in [DockTreeNode, QgsLayerTreeGroup, QgsLayerTreeLayer]:
            return 1
        elif isinstance(node, LayerTreeNode):
            return 2
        else:
            return 1

    def supportedDragActions(self):
        """
        """
        return Qt.CopyAction | Qt.MoveAction

    def supportedDropActions(self) -> Qt.DropActions:
        """
        """
        return Qt.CopyAction | Qt.MoveAction

    def addDock(self, dock: Dock) -> DockTreeNode:
        """
        Adds a Dock and returns the DockTreeNode
        :param dock:
        :return:
        """
        dockNode = createDockTreeNode(dock)
        dockNode.setEnMAPBoxInstance(self.mDockManager.enmapBoxInstance())

        if isinstance(dockNode, DockTreeNode):
            self.rootNode.addChildNode(dockNode)
            if self.rowCount() == 1:
                # fix for
                # https://bitbucket.org/hu-geomatics/enmap-box/issues/361/newly-created-mapview-is-not-checked-as
                QTimer.singleShot(500, self.update_docknode_visibility)
        return dock

    def update_docknode_visibility(self):

        QApplication.processEvents()

        if self.rowCount() > 0:
            idx0 = self.index(0, 0)
            idx1 = self.index(self.rowCount() - 1, 0)
            self.dataChanged.emit(idx0, idx1, [Qt.CheckStateRole])

    def canFetchMore(self, index) -> bool:
        node = self.index2node(index)
        if isinstance(node, LayerTreeNode):
            return len(node.children()) < node.fetchCount()
        return False

    def removeDock(self, dock):
        rootNode = self.rootNode
        to_remove = [n for n in rootNode.children() if n.dock == dock]
        for node in to_remove:
            for c in node.children():
                c.disconnect()
            self.removeDockNode(node)

    def removeDataSources(self, dataSources: typing.List[DataSource]):
        """
        Removes nodes that relate to a specific DataSource
        :param dataSource:
        :type dataSource:
        :return:
        :rtype:
        """
        if not isinstance(dataSources, list):
            dataSources = list(dataSources)

        docks_to_close = []
        for d in dataSources:
            assert isinstance(d, DataSource)

            for node in self.rootNode.children():
                if isinstance(node, MapDockTreeNode):
                    # remove layers from map canvas
                    node.removeLayerNodesByURI(d.source())
                else:
                    # close docks linked to this source
                    if isinstance(node, AttributeTableDockTreeNode) \
                            and isinstance(node.dock, AttributeTableDock) \
                            and isinstance(node.dock.vectorLayer(), QgsVectorLayer) \
                            and node.dock.vectorLayer().source() == d.source():
                        docks_to_close.append(node.dock)

                    elif isinstance(node, SpeclibDockTreeNode) \
                            and isinstance(node.speclib(), QgsVectorLayer) \
                            and node.speclib().source() == d.source():
                        docks_to_close.append(node.dock)

        for dock in docks_to_close:
            self.mDockManager.removeDock(dock)

    def dockTreeNodes(self) -> typing.List[DockTreeNode]:
        return [n for n in self.rootNode.children() if isinstance(n, DockTreeNode)]

    def mapDockTreeNodes(self) -> typing.List[MapDockTreeNode]:
        """
        Returns all MapDockTreeNodes
        :return: [list-of-MapDockTreeNodes]
        """
        return [n for n in self.dockTreeNodes() if isinstance(n, MapDockTreeNode)]

    def mapDockTreeNode(self, canvas: QgsMapCanvas) -> MapDockTreeNode:
        """
        Returns the MapDockTreeNode that is connected to `canvas`
        :param canvas: QgsMapCanvas
        :type canvas:
        :return: MapDockTreeNode
        :rtype:
        """
        for n in self.mapDockTreeNodes():
            if n.mapCanvas() == canvas:
                return n
        return None

    def mapCanvases(self) -> typing.List[MapCanvas]:
        """
        Returns all MapCanvases
        :return: [list-of-MapCanvases]
        """
        return [n.mapCanvas() for n in self.mapDockTreeNodes()]

    def mapLayerIds(self) -> typing.List[str]:
        ids = []
        for node in self.mapDockTreeNodes():
            if isinstance(node, MapDockTreeNode):
                ids.extend(node.findLayerIds())
        return ids

    def mapLayers(self) -> typing.List[QgsMapLayer]:
        """
        Returns all map layers, also those that are invisible and not added to a QgsMapCanvas
        :return: [list-of-QgsMapLayer]
        """
        ids = self.mapLayerIds()
        layers = []
        for id in self.mapLayerIds():
            lyr = QgsProject.instance().mapLayer(id)
            if isinstance(lyr, QgsMapLayer):
                layers.append(lyr)
        return layers

    def removeLayers(self, layerIds: typing.List[str]):
        """Removes the node linked to map layers"""
        assert isinstance(layerIds, list)

        mapDockTreeNodes = [n for n in self.rootNode.children() if isinstance(n, MapDockTreeNode)]
        to_remove = []
        for mapDockTreeNode in mapDockTreeNodes:
            assert isinstance(mapDockTreeNode, MapDockTreeNode)
            for id in layerIds:
                node = mapDockTreeNode.findLayer(id)
                if isinstance(node, QgsLayerTreeLayer):
                    to_remove.append(node)
        self.removeNodes(to_remove)

    def removeNodes(self, nodes: typing.List[QgsLayerTreeNode]):
        for n in nodes:
            try:
                n.disconnect()
            except:
                pass
            if isinstance(n, QgsLayerTreeNode) and isinstance(n.parent(), QgsLayerTreeNode):
                n.parent().removeChildNode(n)

    def removeDockNode(self, node):
        self.removeNodes([node])
        # self.mDockManager.removeDock(node.dock)

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        node = self.index2node(index)
        if node is None:
            node = self.index2legendNode(index)
            if isinstance(node, QgsLayerTreeModelLegendNode):
                return self.legendNodeFlags(node)
                # return super(QgsLayerTreeModel,self).flags(index)
                # return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
            else:
                return Qt.NoItemFlags
        else:
            # print('node: {}  {}'.format(node, type(node)))
            dockNode = self.parentNodesFromIndices(index, nodeInstanceType=DockTreeNode)
            if len(dockNode) == 0:
                return Qt.NoItemFlags
            elif len(dockNode) > 1:
                # print('DEBUG: Multiple docknodes selected')
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
                        flags = flags | Qt.ItemIsUserCheckable | \
                                Qt.ItemIsEditable | \
                                Qt.ItemIsDropEnabled

                        if isL1:
                            flags = flags | Qt.ItemIsDropEnabled

                    if node.name() == 'Layers':
                        flags = flags | Qt.ItemIsUserCheckable | Qt.ItemIsEditable

                    if isinstance(node, CheckableLayerTreeNode):
                        flags = flags | Qt.ItemIsUserCheckable

                if column == 1:
                    pass
                    # mapCanvas Layer Tree Nodes
            elif type(node) in [QgsLayerTreeLayer, QgsLayerTreeGroup]:
                if column == 0:
                    flags = flags | Qt.ItemIsUserCheckable | Qt.ItemIsEditable | Qt.ItemIsDropEnabled | Qt.ItemIsDragEnabled

                # if isinstance(dockNode, MapDockTreeNode) and node != dockNode.layerNode:
                # if isinstance(dockNode, MapDockTreeNode) and node != dockNode.layerNode:
                #    flags = flags | Qt.ItemIsDragEnabled
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
        types = [MDF_ENMAPBOX_LAYERTREEMODELDATA,
                 MDF_QGIS_LAYERTREEMODELDATA,
                 MDF_TEXT_HTML,
                 MDF_TEXT_PLAIN,
                 MDF_URILIST]
        return types

    def dropMimeData(self, mimeData, action, row, column, parentIndex):
        assert isinstance(mimeData, QMimeData)

        if not parentIndex.isValid():
            return False

        # layerRegistry = None
        # if isinstance(EnMAPBox.instance(), EnMAPBox):
        #    layerRegistry = EnMAPBox.instance().mapLayerStore()

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
            if action == Qt.CopyAction:
                mapLayers = [l.clone() for l in mapLayers]

            i = row
            if len(mapLayers) > 0:
                QgsProject.instance().addMapLayers(mapLayers, False)
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

        mimeSuper = super(DockManagerTreeModel, self).mimeData(indexes)
        mimeData = QMimeData()
        doc = QDomDocument()
        rootElem = doc.createElement("dock_tree_model_data")
        context = QgsReadWriteContext()
        for node in nodesFinal:
            node.writeXml(rootElem, context)
        doc.appendChild(rootElem)
        mimeData.setData(MDF_ENMAPBOX_LAYERTREEMODELDATA, textToByteArray(doc))

        if MDF_QGIS_LAYERTREEMODELDATA in mimeSuper.formats():
            mimeData.setData(MDF_ENMAPBOX_LAYERTREEMODELDATA, mimeSuper.data(MDF_QGIS_LAYERTREEMODELDATA))
            # mimeData.setData(MDF_LAYERTREEMODELDATA, mimeSuper.data(MDF_LAYERTREEMODELDATA))

        if QGIS_URILIST_MIMETYPE in mimeSuper.formats():
            mimeData.setData(QGIS_URILIST_MIMETYPE, mimeSuper.data(QGIS_URILIST_MIMETYPE))

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
            # print(('LEGEND', node, column, role))
            return super(DockManagerTreeModel, self).data(index, role)

        elif type(node) in [QgsLayerTreeLayer, QgsLayerTreeGroup, QgsLayerTree]:
            # print(('QGSNODE', node, column, role))
            if role == Qt.EditRole:
                s = ""

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
                # if role == Qt.DisplayRole and isinstance(node, TreeNode):
                #    return node.value()
                return super(DockManagerTreeModel, self).data(index, role)

        return None

        # return super(DockManagerTreeModel, self).data(index, role)

    def setData(self, index, value, role=None):

        node = self.index2node(index)
        if node is None:
            node = self.index2legendNode(index)
            if isinstance(node, QgsLayerTreeModelLegendNode):
                # this does not work:
                # result = super(QgsLayerTreeModel,self).setData(index, value, role=role)
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

                if isinstance(mapDockNode, MapDockTreeNode):
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


class DockManagerTreeProxyModel(QSortFilterProxyModel):

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)


class DockTreeView(QgsLayerTreeView):
    sigPopulateContextMenu = pyqtSignal(QMenu)

    def __init__(self, parent):
        super(DockTreeView, self).__init__(parent)

        self.setHeaderHidden(False)
        self.header().setStretchLastSection(True)
        self.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        # self.header().setResizeMode(1, QHeaderView.ResizeToContents)
        self.currentLayerChanged.connect(self.onCurrentLayerChanged)
        self.setEditTriggers(QAbstractItemView.EditKeyPressed)

        self.mMenuProvider = DockManagerLayerTreeModelMenuProvider(self)
        self.setMenuProvider(self.mMenuProvider)
        self.mMenuProvider.mSignals.sigPopulateContextMenu.connect(self.sigPopulateContextMenu.emit)

    def findParentMapDockTreeNode(self, node: QgsLayerTreeNode) -> MapDockTreeNode:
        while isinstance(node, QgsLayerTreeNode) and not isinstance(node, MapDockTreeNode):
            node = node.parent()
        if isinstance(node, MapDockTreeNode):
            return node
        else:
            return None

    def onCurrentLayerChanged(self, layer: QgsMapLayer):
        debugLog('DockTreeView:onCurrentLayerChanged')
        # find QgsLayerTreeNodes connects to this layer
        currentLayerNode = self.currentNode()
        if not (isinstance(currentLayerNode, QgsLayerTreeLayer) and currentLayerNode.layerId() == layer.id()):
            # find the QgsLayerTreeNode
            currentLayerNode = self.layerTreeModel().rootNode.findLayer(layer)

        map_node = self.findParentMapDockTreeNode(currentLayerNode)
        if isinstance(map_node, MapDockTreeNode):
            self.setCurrentMapCanvas(map_node.mapCanvas())

        for canvas in self.layerTreeModel().mapCanvases():
            assert isinstance(canvas, MapCanvas)
            if layer in canvas.layers():
                canvas.setCurrentLayer(layer)

        debugLog(f'DockTreeView current layer : {self.currentLayer()}')
        debugLog(f'DockTreeView current canvas: {self.currentMapCanvas()}')

    def selectedDockNodes(self) -> typing.List[DockTreeNode]:

        nodes = []
        proxymodel = isinstance(self.model(), QSortFilterProxyModel)
        for idx in self.selectedIndexes():
            if proxymodel:
                node = self.layerTreeModel().index2node(self.model().mapToSource(idx))
            else:
                node = self.index2node(idx)

            if isinstance(node, DockTreeNode) and node not in nodes:
                nodes.append(node)
        return nodes

    def setCurrentMapCanvas(self, canvas: QgsMapCanvas):

        if canvas in self.mapCanvases():
            canvas.setProperty(KEY_LAST_CLICKED, time.time())
            return True
        else:
            return False

    def currentMapCanvas(self) -> MapCanvas:
        """
        Returns the current MapCanvas, i.e. the MapCanvas that was clicked last
        :return:
        :rtype:
        """
        canvases = sorted(self.mapCanvases(), key=lambda c: c.property(KEY_LAST_CLICKED))
        if len(canvases) > 0:
            return canvases[-1]
        else:
            return None

    def mapCanvases(self) -> typing.List[MapCanvas]:
        return self.layerTreeModel().mapCanvases()

    def setModel(self, model):
        assert isinstance(model, DockManagerTreeModel)

        super(DockTreeView, self).setModel(model)
        model.rootNode.addedChildren.connect(self.onNodeAddedChildren)
        for c in model.rootNode.findChildren(LayerTreeNode):
            self.setColumnSpan(c)

    def layerTreeModel(self) -> DockManagerTreeModel:
        return super().layerTreeModel()

    def onNodeAddedChildren(self, parent, iFrom, iTo):
        for i in range(iFrom, iTo + 1):
            node = parent.children()[i]
            if isinstance(node, LayerTreeNode):
                node.sigValueChanged.connect(self.setColumnSpan)

            self.setColumnSpan(node)

    def setColumnSpan(self, node):
        parent = node.parent()
        if parent is not None:
            model = self.layerTreeModel()
            idxNode = model.node2index(node)
            idxParent = model.node2index(parent)
            span = False
            if isinstance(node, LayerTreeNode):
                span = node.value() == None or '{}'.format(node.value()).strip() == ''
            elif type(node) in [QgsLayerTreeGroup, QgsLayerTreeLayer]:
                span = True

            m = self.model()
            # account for changes model() return between 3.16 and 3.18
            if isinstance(m, QSortFilterProxyModel):
                idxNode = m.mapFromSource(idxNode)
                idxParent = m.mapFromSource(idxParent)

            self.setFirstColumnSpanned(idxNode.row(), idxParent, span)
            # for child in node.children():
            #    self.setColumnSpan(child)


class DockManagerLayerTreeModelMenuProvider(QgsLayerTreeViewMenuProvider):
    class Signals(QObject):
        sigPopulateContextMenu = pyqtSignal(QMenu)

        def __init__(self, *args, **kwds):
            super().__init__(*args, **kwds)

    def __init__(self, treeView: DockTreeView):
        super(DockManagerLayerTreeModelMenuProvider, self).__init__()
        # QObject.__init__(self)
        assert isinstance(treeView, DockTreeView)
        self.mDockTreeView: DockTreeView = treeView
        self.mSignals = DockManagerLayerTreeModelMenuProvider.Signals()

    def createContextMenu(self):

        cidx: QModelIndex = self.mDockTreeView.currentIndex()
        col = cidx.column()
        node = self.mDockTreeView.currentNode()
        if node is None:
            return
        menu = QMenu()
        menu.setToolTipsVisible(True)

        selectedLayerNodes = list(set(self.mDockTreeView.selectedLayerNodes()))
        selectedDockNodes = self.mDockTreeView.selectedDockNodes()
        if isinstance(node, (DockTreeNode, QgsLayerTreeLayer)):
            actionEdit = menu.addAction('Rename')
            actionEdit.setShortcut(Qt.Key_F2)
            actionEdit.triggered.connect(lambda *args, idx=cidx: self.mDockTreeView.edit(idx))

        if type(node) is QgsLayerTreeLayer:
            # get parent dock node -> related map canvas
            mapNode = findParent(node, MapDockTreeNode)
            if isinstance(mapNode, MapDockTreeNode):
                assert isinstance(mapNode.dock, MapDock)
                canvas = mapNode.dock.mCanvas

                lyr = node.layer()

                actionPasteStyle = menu.addAction('Paste Style')
                actionPasteStyle.triggered.connect(lambda: pasteStyleFromClipboard(lyr))
                actionPasteStyle.setEnabled(MDF_QGIS_LAYER_STYLE in QApplication.clipboard().mimeData().formats())

                actionCopyStyle = menu.addAction('Copy Style')
                actionCopyStyle.triggered.connect(lambda: pasteStyleToClipboard(lyr))

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

                action = menu.addAction('Remove layer')
                action.setToolTip('Remove layer from map canvas')
                action.triggered.connect(
                    lambda *arg, nodes=selectedLayerNodes: self.mDockTreeView.layerTreeModel().removeNodes(nodes))

                if isinstance(lyr, QgsVectorLayer):
                    action = menu.addAction('Open Attribute Table')
                    action.setToolTip('Opens the layer attribute table')
                    action.triggered.connect(lambda *args, l=lyr: self.openAttributeTable(l))

                    action = menu.addAction('Open Spectral Library Viewer')
                    action.setToolTip('Opens the vector layer in a spectral library view')
                    action.triggered.connect(lambda *args, l=lyr: self.openSpectralLibraryView(l))

                # add processing algorithm shortcuts
                menu.addSeparator()
                if isinstance(lyr, QgsRasterLayer):
                    action = menu.addAction('Image Statistics')
                    action.triggered.connect(lambda: self.runImageStatistics(lyr))

                    if isinstance(lyr.renderer(), QgsPalettedRasterRenderer):
                        action = menu.addAction('Classification Statistics')
                        action.triggered.connect(lambda: self.runClassificationStatistics(lyr))

                menu.addSeparator()
                action = menu.addAction('Layer properties')
                action.setToolTip('Set layer properties')
                action.triggered.connect(lambda: self.setLayerStyle(lyr, canvas))

                # add raster renderer here, because we can't register; QgsRendererRegistry.addRenderer only supports vector renderer :-(
                if isinstance(lyr, QgsRasterLayer):
                    action: QAction = menu.addAction('Class Fraction/Probability Rendering')
                    action.setIcon(QIcon(':/images/themes/default/propertyicons/symbology.svg'))
                    action.setToolTip('Set layer band rendering')
                    action.triggered.connect(lambda: self.setClassFractionRenderer(lyr))

                    action: QAction = menu.addAction('Decorrelation Stretch Rendering')
                    action.setIcon(QIcon(':/images/themes/default/propertyicons/symbology.svg'))
                    action.setToolTip('Set layer band rendering')
                    action.triggered.connect(lambda: self.setDecorrelationStretchRenderer(lyr, canvas))


        elif isinstance(node, DockTreeNode):
            assert isinstance(node.dock, Dock)
            node.dock.populateContextMenu(menu)

        elif isinstance(node, LayerTreeNode):
            if col == 0:
                node.populateContextMenu(menu)
            elif col == 1:
                a = menu.addAction('Copy')
                a.triggered.connect(lambda: QApplication.clipboard().setText('{}'.format(node.value())))

        # last chance to add other menu actions
        self.mSignals.sigPopulateContextMenu.emit(menu)

        return menu

    def onZoomToLayer(self, lyr: QgsMapLayer, canvas: QgsMapCanvas):

        assert isinstance(lyr, QgsMapLayer)
        assert isinstance(canvas, QgsMapCanvas)

        ext = SpatialExtent.fromLayer(lyr).toCrs(canvas.mapSettings().destinationCrs())
        if isinstance(ext, SpatialExtent):
            canvas.setExtent(ext)
        else:
            s = ""

    def openAttributeTable(self, layer: QgsVectorLayer):
        from enmapbox import EnMAPBox
        emb = EnMAPBox.instance()
        if isinstance(emb, EnMAPBox) and isinstance(layer, QgsVectorLayer):
            from enmapbox.gui.dataviews.docks import AttributeTableDock
            emb.createDock(AttributeTableDock, layer=layer)

    def openSpectralLibraryView(self, layer: QgsVectorLayer):
        from enmapbox import EnMAPBox
        emb = EnMAPBox.instance()
        if isinstance(emb, EnMAPBox) and isinstance(layer, QgsVectorLayer):
            from enmapbox.gui.dataviews.docks import SpectralLibraryDock
            emb.createDock(SpectralLibraryDock, speclib=layer)

    def setLayerStyle(self, layer: QgsMapLayer, canvas: QgsMapCanvas):
        from enmapbox import EnMAPBox
        messageBar = None
        emb = EnMAPBox.instance()
        if isinstance(emb, EnMAPBox) and isinstance(layer, QgsVectorLayer):
            messageBar = emb.messageBar()
        showLayerPropertiesDialog(layer, canvas=canvas, messageBar=messageBar, modal=True, useQGISDialog=False)

    def setClassFractionRenderer(self, layer: QgsRasterLayer):
        widget = ClassFractionRendererWidget(layer, parent=self.mDockTreeView)
        widget.setWindowTitle(widget.windowTitle().format(layerName=layer.name()))
        widget.show()

    def setDecorrelationStretchRenderer(self, layer: QgsRasterLayer, canvas: QgsMapCanvas):
        widget = DecorrelationStretchRendererWidget(layer, canvas, parent=self.mDockTreeView)
        widget.setWindowTitle(widget.windowTitle().format(layerName=layer.name()))
        widget.show()

    def runImageStatistics(self, layer):

        from enmapboxapplications import ImageStatisticsApp
        widget = ImageStatisticsApp(parent=self.mDockTreeView)
        widget.uiRaster().setLayer(layer)
        widget.show()
        widget.uiExecute().clicked.emit()

    def runClassificationStatistics(self, layer):
        from hubdsm.processing.classificationstatistics import ClassificationStatistics, ClassificationStatisticsPlot
        alg = ClassificationStatistics()
        io = {alg.P_CLASSIFICATION: layer}
        result = Processing.runAlgorithm(alg, parameters=io, feedback=QgsProcessingFeedback())
        categories = eval(result[alg.P_OUTPUT_CATEGORIES])
        counts = eval(result[alg.P_OUTPUT_COUNTS])
        widget = ClassificationStatisticsPlot(categories=categories, counts=counts, layer=layer,
                                              parent=self.mDockTreeView)
        widget.show()


class DockManager(QObject):
    """
    Class to handle all DOCK related events
    """

    sigDockAdded = pyqtSignal(Dock)
    sigDockRemoved = pyqtSignal(Dock)
    sigDockWillBeRemoved = pyqtSignal(Dock)
    sigDockTitleChanged = pyqtSignal(Dock)

    def __init__(self):
        QObject.__init__(self)
        self.mConnectedDockAreas = []
        self.mCurrentDockArea = None
        self.mDocks = list()
        self.mDataSourceManager: DataSourceManager = None
        self.mMessageBar: QgsMessageBar = None

        self.mEnMAPBoxInstance: 'EnMAPBox' = None

    def setEnMAPBoxInstance(self, enmapBox):
        self.mEnMAPBoxInstance = enmapBox

    def enmapBoxInstance(self) -> 'EnMAPBox':
        return self.mEnMAPBoxInstance

    def setMessageBar(self, messageBar: QgsMessageBar):
        self.mMessageBar = messageBar

    def connectDataSourceManager(self, dataSourceManager: DataSourceManager):
        assert isinstance(dataSourceManager, DataSourceManager)
        self.mDataSourceManager = dataSourceManager
        self.setEnMAPBoxInstance(self.mDataSourceManager.enmapBoxInstance())

    def dataSourceManager(self) -> DataSourceManager:
        return self.mDataSourceManager

    def mapDocks(self) -> typing.List[SpectralLibraryDock]:
        return [d for d in self if isinstance(d, MapDock)]

    def spectraLibraryDocks(self) -> typing.List[SpectralLibraryDock]:
        return [d for d in self if isinstance(d, SpectralLibraryDock)]

    def connectDockArea(self, dockArea: DockArea):
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

            # speclibs = extractSpectralLibraries(mimeData)
            # speclibUris = [s.source() for s in speclibs]
            layers = extractMapLayers(mimeData)
            rxSupportedFiles = re.compile(r'(xml|html|txt|csv|log|md|rst|qml)$')
            textfiles = []
            for url in mimeData.urls():
                path = url.toLocalFile()
                if os.path.isfile(path) and rxSupportedFiles.search(path):
                    textfiles.append(path)

            # register datasources

            new_sources = self.mDataSourceManager.addDataSources(layers + textfiles)

            # dropped_speclibs = [s for s in new_sources if isinstance(s, VectorDataSource) and s.isSpectralLibrary()]
            # dropped_maplayers = [s for s in new_sources if isinstance(s, SpatialDataSource) and s not in dropped_speclibs]

            dropped_speclibs = [l for l in layers if is_spectral_library(l)]
            dropped_maplayers = [l for l in layers if isinstance(l, QgsMapLayer) and l.isValid()]

            # open spectral Library dock for new speclibs

            if len(dropped_speclibs) > 0:
                # show 1st speclib
                from enmapbox.gui.dataviews.docks import SpectralLibraryDock
                NEW_DOCK = self.createDock(SpectralLibraryDock, speclib=dropped_speclibs[0])
                assert isinstance(NEW_DOCK, SpectralLibraryDock)

            # open map dock for other map layers

            # exclude vector layers without geometry
            dropped_maplayers = [l for l in dropped_maplayers \
                                 if not (isinstance(l, QgsVectorLayer) and \
                                         l.geometryType() in [QgsWkbTypes.UnknownGeometry, QgsWkbTypes.NullGeometry])]

            if len(dropped_maplayers) > 0:
                from enmapbox.gui.dataviews.docks import MapDock
                NEW_DOCK = self.createDock(MapDock)
                assert isinstance(NEW_DOCK, MapDock)
                # layers = [s.asMapLayer() for s in dropped_maplayers]
                NEW_DOCK.addLayers(dropped_maplayers)

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

    def docks(self, dockType=None) -> list:
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
            # handle wrapper types, e.g. when calling .dock(MapDock)
            return [d for d in self.mDocks if dockType.__name__ == d.__class__.__name__]

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
            self.sigDockWillBeRemoved.emit(dock)
            self.mDocks.remove(dock)

            if dock.container():
                dock.close()
            self.sigDockRemoved.emit(dock)
            return True
        return False

    def createDock(self, dockType, *args, **kwds) -> Dock:
        """
        Creates and returns a new Dock
        :param dockType: str or Dock class, e.g. 'MAP' or MapDock
        :param args:
        :param kwds:
        :return:
        """
        assert dockType in LUT_DOCKTYPES.keys(), f'Unknown dockType "{dockType}"\n' + \
                                                 'Choose from [{}]'.format(
                                                     ','.join(['"{}"'.format(k) for k in LUT_DOCKTYPES.keys()]))
        cls = LUT_DOCKTYPES[dockType]

        # create the dock name
        existingDocks = self.docks(dockType)
        existingNames = [d.title() for d in existingDocks]
        n = len(existingDocks) + 1
        dockTypes = [MapDock, TextDock, MimeDataDock, WebViewDock, SpectralLibraryDock, AttributeTableDock]
        dockBaseNames = ['Map', 'Text', 'MimeData', 'HTML Viewer', 'SpectralLibrary', 'Attribute Table']
        baseName = 'Dock'
        if cls in dockTypes:
            baseName = dockBaseNames[dockTypes.index(cls)]
        name = '{} #{}'.format(baseName, n)
        while name in existingNames:
            n += 1
            name = '{} #{}'.format(baseName, n)
        kwds['name'] = name

        dockArea = kwds.get('dockArea', self.currentDockArea())
        assert isinstance(dockArea, DockArea), 'DockManager not connected to any DockArea yet. \n' \
                                               'Add DockAreas with connectDockArea(self, dockArea)'
        kwds['area'] = dockArea
        # kwds['parent'] = dockArea
        dock = None
        if cls == MapDock:
            dock = MapDock(*args, **kwds)
            if isinstance(self.mDataSourceManager, DataSourceManager):
                dock.sigLayersAdded.connect(self.mDataSourceManager.addDataSources)

        elif cls == TextDock:
            dock = TextDock(*args, **kwds)

        elif cls == MimeDataDock:
            dock = MimeDataDock(*args, **kwds)

        elif cls == WebViewDock:
            dock = WebViewDock(*args, **kwds)

        elif cls == SpectralLibraryDock:
            speclib = kwds.get('speclib')
            if isinstance(speclib, QgsVectorLayer):
                kwds['name'] = speclib.name()
            dock = SpectralLibraryDock(*args, **kwds)
            dock.speclib().willBeDeleted.connect(lambda *args, d=dock: self.removeDock(d))
            if isinstance(self.mMessageBar, QgsMessageBar):
                dock.mSpeclibWidget.setMainMessageBar(self.mMessageBar)

        elif cls == AttributeTableDock:
            layer = kwds.pop('layer', None)
            assert isinstance(layer, QgsVectorLayer), 'QgsVectorLayer "layer" is not defined'
            dock = AttributeTableDock(layer, *args, **kwds)
            layer.willBeDeleted.connect(lambda *args, d=dock: self.removeDock(d))
            if isinstance(self.mMessageBar, QgsMessageBar):
                dock.attributeTableWidget.setMainMessageBar(self.mMessageBar)
        else:
            raise Exception('Unknown dock type: {}'.format(dockType))
        # dock.setParent(dockArea)
        dockArea.addDock(dock, *args, **kwds)
        dock.setVisible(True)

        if dock not in self.mDocks:
            dock.sigClosed.connect(self.removeDock)
            self.mDocks.append(dock)
            self.sigDockAdded.emit(dock)

        return dock

    def onSpeclibWillBeDeleted(self, lyr):
        s = ""

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


class DockPanelUI(QgsDockWidget):
    def __init__(self, parent=None):
        super(DockPanelUI, self).__init__(parent)
        loadUi(enmapboxUiPath('dockpanel.ui'), self)
        self.mDockManager: DockManager = None
        self.mDockManagerTreeModel: DockManagerTreeModel = None
        self.mMenuProvider: DockManagerLayerTreeModelMenuProvider = None

        self.dockTreeView: DockTreeView
        self.actionRemoveSelected: QAction
        self.btnRemoveSource: QToolButton

        self.btnRemoveSource.setDefaultAction(self.actionRemoveSelected)
        self.actionRemoveSelected.triggered.connect(self.onRemoveSelected)

        assert isinstance(self.dockTreeView, DockTreeView)
        # self.dockTreeView.currentLayerChanged.connect(self.onSelectionChanged)
        self.tbFilterText.textChanged.connect(self.setFilter)
        self.initActions()

    def setFilter(self, pattern: str):
        if Qgis.QGIS_VERSION < '3.18':
            return
        proxyModel = self.dockTreeView.proxyModel()
        if isinstance(proxyModel, QgsLayerTreeProxyModel):
            proxyModel.setFilterText(pattern)

    def onRemoveSelected(self):
        tv: DockTreeView = self.dockTreeView
        model = self.dockManagerTreeModel()
        if isinstance(model, DockManagerTreeModel):
            layerNodes = list(set(tv.selectedLayerNodes()))

            layerNodes = [n for n in layerNodes if isinstance(n.parent(), MapDockTreeNode)]
            self.mDockManagerTreeModel.removeNodes(layerNodes)

            for n in tv.selectedDockNodes():
                self.mDockManager.removeDock(n.dock)
            # docks = [n.dock for n in self.dockTreeView.selectedNodes() if isinstance(n, DockTreeNode)]
            # for dock in docks:
            #    self.mDockManagerTreeModel.removeDock(dock)

    def initActions(self):
        self.btnCollapse.setDefaultAction(self.actionCollapseTreeNodes)
        self.btnExpand.setDefaultAction(self.actionExpandTreeNodes)

        self.actionCollapseTreeNodes.triggered.connect(self.dockTreeView.collapseAllNodes)
        self.actionExpandTreeNodes.triggered.connect(self.dockTreeView.expandAllNodes)

    def connectDockManager(self, dockManager: DockManager):
        """
        Connects the DockPanelUI with a DockManager
        :param dockManager:
        :return:
        """
        assert isinstance(dockManager, DockManager)
        self.mDockManager = dockManager
        self.mDockManagerTreeModel = DockManagerTreeModel(self.mDockManager)
        # self.mDockManagerProxyModel.setSourceModel(self.mDockManagerTreeModel)
        self.dockTreeView.setModel(self.mDockManagerTreeModel)

        m = self.dockTreeView.layerTreeModel()
        assert self.mDockManagerTreeModel == m
        assert isinstance(m, QgsLayerTreeModel)

        self.mMenuProvider: DockManagerLayerTreeModelMenuProvider = DockManagerLayerTreeModelMenuProvider(
            self.dockTreeView)
        self.dockTreeView.setMenuProvider(self.mMenuProvider)

    def dockManagerTreeModel(self) -> DockManagerTreeModel:
        return self.dockTreeView.layerTreeModel()


class MapCanvasBridge(QgsLayerTreeMapCanvasBridge):

    def __init__(self, root, canvas, parent=None):
        super(MapCanvasBridge, self).__init__(root, canvas)
        self.setAutoSetupOnFirstLayer(False)
        assert isinstance(root, MapDockTreeNode)
        assert isinstance(canvas, MapCanvas)

        self.mRootNode = root
        self.mCanvas = canvas
        assert self.mCanvas == self.mapCanvas()

        self.mapCanvas().layersChanged.connect(self.setLayerTreeLayers)

        self.mCanvas.sigLayersCleared.connect(self.mRootNode.clear)

    def setLayerTreeLayers(self):

        canvasLayers = self.mapCanvas().layers()
        canvasLayerIds = [l.id() for l in canvasLayers]
        treeNodeLayerIds = self.rootGroup().findLayerIds()

        # new layers to add?
        # newChildLayers = [l for l in canvasLayers if l not in treeNodeLayers]

        # layers to set visible?
        to_add = [i for i in canvasLayerIds if i not in treeNodeLayerIds]

        for lid in to_add:
            layer = [l for l in canvasLayers if l.id() == lid][0]
            self.rootGroup().insertLayer(0, layer)
            # set canvas on visible
            lNode = self.rootGroup().findLayer(lid)
            if isinstance(lNode, QgsLayerTreeLayer):
                lNode.setItemVisibilityChecked(Qt.Checked)


def createDockTreeNode(dock: Dock) -> DockTreeNode:
    """
    Returns a DockTreeNode corresponding to a Dock
    :param dock:
    :param parent:
    :return:
    """
    if isinstance(dock, MapDock):
        return MapDockTreeNode(dock)
    elif isinstance(dock, TextDock):
        return TextDockTreeNode(dock)
    elif isinstance(dock, SpectralLibraryDock):
        return SpeclibDockTreeNode(dock)
    elif isinstance(dock, AttributeTableDock):
        return AttributeTableDockTreeNode(dock)
    elif isinstance(dock, Dock):
        return DockTreeNode(dock)
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
        assert isinstance(treeView.layerTreeModel(), DockManagerTreeModel)
        self.treeView = treeView
        self.model = treeView.layerTreeModel()

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
            return self.currentNode().populateContextMenu()
        else:
            return QMenu()
