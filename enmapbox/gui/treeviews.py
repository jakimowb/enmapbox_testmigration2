from PyQt4.QtXml import *

import enmapbox
from qgis.core import *
from PyQt4.QtGui import QApplication
from PyQt4.QtCore import QMimeData
import numpy as np


from enmapbox.gui.docks import *
from enmapbox.gui.datasources import *

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
        FileDataSourceTreeNode, RasterDataSourceTreeNode, VectorDataSourceTreeNode, DataSourceTreeNode
        assert isinstance(dataSource, DataSource)

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
    def __init__(self, parent, name, value=None, checked=Qt.Unchecked, tooltip=None, icon=None):
        #QObject.__init__(self)
        super(TreeNode, self).__init__(name, checked)
        #assert name is not None and len(str(name)) > 0
        self.mParent = parent
        self.mTooltip = None
        self.mValue = None
        self.setName(name)
        self.setValue(value)
        self.setExpanded(False)
        self.setVisible(False)
        self.setTooltip(tooltip)

        self.setIcon(icon)
        if parent is not None:
            parent.addChildNode(self)

    def setValue(self, value):
        self.mValue = value

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

class FileSizesTreeNode(TreeNode):
    """
    A node to show the different apsects of spatial extents
    Sub-Nodes:
        spatial extent in map unit
        pixel sizes (if raster source)
        pixel extent (if raster source)
    """
    def __init__(self, parent, spatialDataSource):
        assert isinstance(spatialDataSource, DataSourceSpatial)
        super(FileSizesTreeNode, self).__init__(parent, 'Extent')
        ext = spatialDataSource.spatialExtent
        mu = QgsUnitTypes.encodeUnit(ext.crs().mapUnits())

        n = TreeNode(self, 'Spatial', value='{}X{} {}'.format(ext.width(),ext.height(), mu))

        if isinstance(spatialDataSource, DataSourceRaster):
            n = TreeNode(self, 'Pixel', value)

        fstr = fileSize(spatialDataSource.uri)
        n = TreeNode(self, 'Data', value='{}'.format(fstr))


class CRSTreeNode(TreeNode):
    def __init__(self, parent, crs):
        assert isinstance(crs, QgsCoordinateReferenceSystem)

        super(CRSTreeNode, self).__init__(parent, crs.description())

        self.setIcon(QIcon(':/enmapbox/icons/crs.png'))
        self.setTooltip('Coordinate Reference System')
        self.mCrs = None
        self.nodeDescription = TreeNode(self, 'Name', tooltip='Description')
        self.nodeAuthID = TreeNode(self, 'AuthID', tooltip='Authority ID')
        self.nodeAcronym = TreeNode(self, 'Acronym', tooltip='Projection Acronym')
        self.setCrs(crs)


    def setCrs(self, crs):
        assert isinstance(crs, QgsCoordinateReferenceSystem)
        self.mCrs = crs
        self.nodeDescription.setValue(crs.description())
        self.nodeAuthID.setValue(crs.authid())
        self.nodeAcronym.setValue(crs.projectionAcronym())

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
        self.header().setResizeMode(0, QHeaderView.ResizeToContents)

    def layerTreeModel(self):
        model = self.model()
        return model

    def setModel(self, model):
        assert isinstance(model, TreeModel)
        model.rootNode.addedChildren.connect(self.onNodeAddedChildren)
        super(TreeView, self).setModel(model)

        s = ""

    def onNodeAddedChildren(self, parent, iFrom, iTo):
        model = self.model()
        for i in range(iFrom, iTo+1):
            node = parent.children()[i]
            nameOnly = True
            if isinstance(node, TreeNode):
                nameOnly = node.value() is None
            self.setFirstColumnSpanned(i, model.node2index(parent), nameOnly)

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


