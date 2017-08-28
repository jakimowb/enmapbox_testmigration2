from PyQt4.QtXml import *

import enmapbox
from qgis.core import *
from PyQt4.QtGui import QApplication
from PyQt4.QtCore import QMimeData
import numpy as np


from enmapbox.gui.docks import *
from enmapbox.gui.datasources import *
from enmapbox.gui.mapcanvas import MapDock
class TreeNodeProvider():

    @staticmethod
    def CreateNodeFromInstance(o, parent):
        node = None
        if isinstance(o, DataSource):
            node = TreeNodeProvider.CreateNodeFromDataSource(o, parent)
        elif isinstance(o, Dock):
            node = TreeNodeProvider.CreateNodeFromDock(o, parent)
        elif isinstance(o, QMimeData):
            s = ""
        return node

    @staticmethod
    def CreateNodeFromDataSource(dataSource, parent):

        from enmapbox.gui.datasourcemanager import DataSource, ProcessingTypeTreeNode, \
        FileDataSourceTreeNode, RasterDataSourceTreeNode, VectorDataSourceTreeNode, DataSourceTreeNode, \
        SpeclibDataSourceTreeNode
        assert isinstance(dataSource, DataSource)

        #hint: take care of class inheritance order
        if isinstance(dataSource, HubFlowDataSource):
            node = ProcessingTypeTreeNode(parent, dataSource)
        elif isinstance(dataSource, DataSourceRaster):
            node = RasterDataSourceTreeNode(parent, dataSource)
        elif isinstance(dataSource, DataSourceVector):
            node = VectorDataSourceTreeNode(parent, dataSource)
        elif isinstance(dataSource, DataSourceSpectralLibrary):
            node = SpeclibDataSourceTreeNode(parent, dataSource)
        elif isinstance(dataSource, DataSourceFile):
            node = FileDataSourceTreeNode(parent, dataSource)
        else:
            node = DataSourceTreeNode(parent, dataSource)

        return node


    @staticmethod
    def CreateNodeFromDock(dock, parent):
        assert isinstance(dock, Dock)
        dockType = type(dock)
        from enmapbox.gui.dockmanager import DockTreeNode, MapDockTreeNode, TextDockTreeNode
        if dockType is MapDock:
            return MapDockTreeNode(parent, dock)
        elif dockType in [TextDock, MimeDataDock]:
            return TextDockTreeNode(parent, dock)
        elif dockType is CursorLocationValueDock:
            return DockTreeNode(parent, dock)
        else:
            return DockTreeNode(parent, dock)


    @staticmethod
    def CreateNodeFromXml(elem):
        assert isinstance(elem, QDomElement), str(elem)
        tagName = str(elem.tagName())
        node = None
        attributes = getDOMAttributes(elem)
        tagMap = [('tree-node', TreeNode),
                  ('dock-tree-node', DockTreeNode),
                  ('map-dock-tree-node', MapDockTreeNode),
                  ('test-dock-tree-node', TextDockTreeNode),
                  ('layer-tree-group', QgsLayerTreeGroup),
                  ('layer-tree-layer', QgsLayerTreeLayer),
                  ('datasource-tree-node', DataSourceTreeNode),
                  ('datasource-tree-group', DataSourceGroupTreeNode)
                  ]
        for xmlTag, nodeClass in tagMap:
            if xmlTag == tagName:
                node = nodeClass.readXml(elem)
                break
        return node


class TreeNode(QgsLayerTreeGroup):
    sigIconChanged = pyqtSignal()
    sigValueChanged = pyqtSignal(QObject)
    sigRemoveMe = pyqtSignal()
    def __init__(self, parent, name, value=None, checked=Qt.Unchecked, tooltip=None, icon=None):
        #QObject.__init__(self)
        super(TreeNode, self).__init__(name, checked)
        #assert name is not None and len(str(name)) > 0

        self.mParent = parent
        self.mTooltip = None
        self.mValue = None
        self.mIcon = None

        self.setName(name)
        self.setValue(value)
        self.setExpanded(False)
        self.setVisible(False)
        self.setTooltip(tooltip)
        self.setIcon(icon)

        if parent is not None:
            parent.addChildNode(self)

    def _removeSubNode(self,node):
        if node in self.children():
            self.removeChildNode(node)
        return None

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
            assert isinstance(icon, QIcon), str(icon)
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
        node.readCommonXML(element)


    def writeXML(self, parentElement):

        assert isinstance(parentElement, QDomElement)
        doc = parentElement.ownerDocument()
        elem = doc.createElement('tree-node')

        elem.setAttribute('name', self.name())
        elem.setAttribute('expanded', '1' if self.isExpanded() else '0')
        elem.setAttribute('checked', QgsLayerTreeUtils.checkStateToXml(Qt.Checked))

        #custom properties
        self.writeCommonXML(elem)

        for node in self.children():
            node.writeXML(elem)
        parentElement.appendChild(elem)

        #return elem

    def readChildrenFromXml(self, element):
        nodes = []
        childElem = element.firstChildElement()
        while(not childElem.isNull()):
            node = TreeNodeProvider.CreateNodeFromXml(childElem)

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


class TreeModel(QgsLayerTreeModel):
    def __init__(self, parent=None):
        self.rootNode = TreeNode(None, '<hidden root node>')
        super(TreeModel, self).__init__(self.rootNode, parent)
        self.columnNames = ['Property','Value']

    def headerData(self, section, orientation, role=None):

        if role == Qt.DisplayRole:
            return self.columnNames[section]

        return None



    def columnCount(self, index):
        node = self.index2node(index)
        if isinstance(node, TreeNode):
            return 2
        else:
            return 1


    def data(self, index, role ):
        """

        :param index:
        :param role:
        :return:
        """
        node = self.index2node(index)
        col = index.column()
        if isinstance(node, TreeNode):

            if col == 0:
                if role == Qt.DisplayRole:
                    return node.name()
                if role == Qt.DecorationRole:
                    return node.icon()
                if role == Qt.ToolTipRole:
                    return node.tooltip()
            if col == 1:
                if role == Qt.DisplayRole:
                    return node.value()
        else:
            if col == 0:
                return super(TreeModel, self).data(index, role)



        return None
    def supportedDragActions(self):
        return Qt.IgnoreAction

    def supportedDropActions(self):
        return Qt.IgnoreAction

    def flags(self, index):
        raise NotImplementedError()

    def mimeTypes(self):
        raise NotImplementedError()

    def mimeData(self, indexes):
        raise NotImplementedError()

    def dropMimeData(self, data, action, row, column, parent):
        raise NotImplementedError()


class CRSTreeNode(TreeNode):
    def __init__(self, parent, crs):
        assert isinstance(crs, QgsCoordinateReferenceSystem)
        super(CRSTreeNode, self).__init__(parent, crs.description())
        self.setName('CRS')
        self.setIcon(QIcon(':/enmapbox/icons/crs.png'))
        self.setTooltip('Coordinate Reference System')
        self.mCrs = None
        self.nodeDescription = TreeNode(self, 'Name', tooltip='Description')
        self.nodeAuthID = TreeNode(self, 'AuthID', tooltip='Authority ID')
        self.nodeAcronym = TreeNode(self, 'Acronym', tooltip='Projection Acronym')
        self.nodeMapUnits = TreeNode(self, 'Map Units')
        self.setCrs(crs)


    def setCrs(self, crs):
        assert isinstance(crs, QgsCoordinateReferenceSystem)
        self.mCrs = crs
        if self.mCrs.isValid():
            self.setValue(crs.description())
            self.nodeDescription.setValue(crs.description())
            self.nodeAuthID.setValue(crs.authid())
            self.nodeAcronym.setValue(crs.projectionAcronym())
            self.nodeDescription.setVisible(Qt.Checked)
            self.nodeMapUnits.setValue(QgsUnitTypes.toString(self.mCrs.mapUnits()))
        else:
            self.setValue(None)
            self.nodeDescription.setValue('N/A')
            self.nodeAuthID.setValue('N/A')
            self.nodeAcronym.setValue('N/A')
            self.nodeMapUnits.setValue('N/A')

    def contextMenu(self):
        menu = QMenu()
        a = menu.addAction('Copy EPSG Code')
        a.setToolTip('Copy the authority id ("{}") of this CRS.'.format(self.mCrs.authid()))
        a.triggered.connect(lambda: QApplication.clipboard().setText(self.mCrs.authid()))

        a = menu.addAction('Copy WKT')
        a.setToolTip('Copy the well-known-type representation of this CRS.')
        a.triggered.connect(lambda: QApplication.clipboard().setText(self.mCrs.toWkt()))

        a = menu.addAction('Copy Proj4')
        a.setToolTip('Copy the Proj4 representation of this CRS.')
        a.triggered.connect(lambda: QApplication.clipboard().setText(self.mCrs.toProj4()))
        return menu

#class TreeView(QTreeView):
class TreeView(QgsLayerTreeView):

    def __init__(self, parent):
        super(TreeView, self).__init__(parent)

        self.setHeaderHidden(False)
        self.header().setStretchLastSection(True)
        self.header().setResizeMode(QHeaderView.ResizeToContents)
        #self.header().setResizeMode(1, QHeaderView.ResizeToContents)

    def layerTreeModel(self):
        model = self.model()
        return model

    def setModel(self, model):
        assert isinstance(model, TreeModel)

        super(TreeView, self).setModel(model)
        model.rootNode.addedChildren.connect(self.onNodeAddedChildren)
        for c in model.rootNode.findChildren(TreeNode):
            self.setColumnSpan(c)

    def onNodeAddedChildren(self, parent, iFrom, iTo):
        for i in range(iFrom, iTo+1):
            node = parent.children()[i]
            if isinstance(node, TreeNode):
                node.sigValueChanged.connect(self.setColumnSpan)

            self.setColumnSpan(node)
        #self.resizeColumnToContents(0)
        #self.resizeColumnToContents(1)

    def setColumnSpan(self, node):
        parent = node.parent()
        if parent is not None:
            model = self.model()
            idxNode = model.node2index(node)
            idxParent = model.node2index(parent)
            span = True
            if isinstance(node, TreeNode):
                span = node.value() == None or len(node.value()) == 0
            elif type(node) in [QgsLayerTreeGroup, QgsLayerTreeLayer]:
                span = True
            self.setFirstColumnSpanned(idxNode.row(), idxParent, span)

class TreeViewMenuProvider(QgsLayerTreeViewMenuProvider):

    def __init__(self, treeView):
        super(TreeViewMenuProvider,self).__init__()
        assert isinstance(treeView, TreeView)
        assert isinstance(treeView.model(), TreeModel)
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
        if isinstance(node, TreeNode):
            return self.currentNode().contextMenu()
        else:
            return QMenu()


