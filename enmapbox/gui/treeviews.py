from PyQt4.QtXml import *

import enmapbox
from qgis.core import *
from PyQt4.QtGui import QApplication
import numpy as np

from enmapbox.gui.docks import *


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
        assert isinstance(dataSource, DataSource)

        from datasourcemanager import *
        #hint: take care of derived class order
        if isinstance(dataSource, ProcessingTypeDataSource):
            node = ProcessingTypeTreeNode(parent, dataSource)
        elif isinstance(dataSource, DataSourceFile):
            node = FileDataSourceTreeNode(parent, dataSource)
        elif isinstance(dataSource, DataSourceRaster):
            node = RasterDataSourceTreeNode(parent, dataSource)
        elif isinstance(dataSource, DataSourceVector):
            node = VectorDataSourceTreeNode(parent, dataSource)
        else:
            node = DataSourceTreeNode(parent, dataSource)

        node.setIcon(dataSource.icon)
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
    sigRemoveMe = pyqtSignal()
    def __init__(self, parent, name, checked=Qt.Unchecked, tooltip=None, icon=None):
        #QObject.__init__(self)
        super(TreeNode, self).__init__(name, checked)
        self.mParent = parent
        self.setName(name)

        # set default properties using underlying customPropertySet
        self.setTooltip(tooltip)

        self.setIcon(icon)
        if parent is not None:
            parent.addChildNode(self)


    def removeChildren(self, i0, cnt):
        self.removeChildrenPrivate(i0, cnt)
        self.updateVisibilityFromChildren()

    def setTooltip(self, tooltip):
        if tooltip is None:
            self.setCustomProperty('tooltip', None)
        else:
            self.setCustomProperty('tooltip', tooltip)

    def tooltip(self, default=''):
        return self.customProperty('tooltip',default)

    def setIcon(self, icon):
        if icon:
            assert isinstance(icon, QIcon), str(icon)
        self._icon = icon
        self.sigIconChanged.emit()

    def icon(self):
        return self._icon

    def contextMenu(self):
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
        return elem

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
        from enmapbox.gui.enmapboxgui import EnMAPBox
        self.rootNode = TreeNode(None, None)
        super(TreeModel, self).__init__(self.rootNode, parent)

    def data(self, index, role ):
        node = self.index2node(index)
        if isinstance(node, TreeNode):
            if role == Qt.DecorationRole:
                return node.icon()
            if role == Qt.ToolTipRole:
                return node.tooltip()

        #the last choice: default
        return super(TreeModel, self).data(index, role)

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

    def contextMenu(self, node):
        raise NotImplementedError()



class CRSTreeNode(TreeNode):
    def __init__(self, parent, crs):
        assert isinstance(crs, QgsCoordinateReferenceSystem)

        super(CRSTreeNode, self).__init__(parent, crs.description())

        self.setIcon(QIcon(':/enmapbox/icons/crs.png'))
        self.setTooltip('Coordinate Reference System')

        self.nodeAuthID = TreeNode(self, '<authid>', tooltip='Authority ID')
        self.nodeAcronym = TreeNode(self, '<acronym>', tooltip='Projection Acronym')
        self.setCrs(crs)

    def setCrs(self, crs):
        assert isinstance(crs, QgsCoordinateReferenceSystem)
        self.nodeAuthID.setName(crs.authid())
        self.nodeAcronym.setName(crs.projectionAcronym())

    def contextMenu(self):
        menu = QMenu()
        a = menu.addAction('Copy EPSG Code')
        a.triggered.connect(lambda: QApplication.clipboard().setText(self.crs.toWkt()))

        a = menu.addAction('Copy WKT')
        a.triggered.connect(lambda: QApplication.clipboard().setText(self.crs.toauthid()))
        return menu


class TreeView(QgsLayerTreeView):

    def __init__(self, parent):
        super(TreeView, self).__init__(parent)


class TreeViewMenuProvider(QgsLayerTreeViewMenuProvider):

    def __init__(self, treeView):
        super(TreeViewMenuProvider,self).__init__()
        assert isinstance(treeView, TreeView)
        assert isinstance(treeView.model(), TreeModel)
        self.treeView = treeView
        self.model = treeView.model()

    def createContextMenu(self):
        #redirect to model
        return self.model.contextMenu(self.treeView.currentNode())

