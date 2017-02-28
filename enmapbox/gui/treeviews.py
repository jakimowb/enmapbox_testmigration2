from PyQt4.QtXml import *

import enmapbox
from qgis.core import *



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
        node = DataSourceTreeNode(parent, dataSource)
        node.setIcon(dataSource.icon)
        return node


    @staticmethod
    def CreateNodeFromDock(dock, parent):
        t = type(dock)
        classes = [MapDock, TextDock, MimeDataDock, Dock, CursorLocationValueDock]
        nodes   = [MapDockTreeNode, TextDockTreeNode, TextDockTreeNode, DockTreeNode, DockTreeNode]
        assert t in classes
        for i, cls in enumerate(classes):
            if t is cls:
                return nodes[i](parent, dock)
        return None

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
        return Qt.MoveAction | Qt.CopyAction

    def supportedDropActions(self):
        return Qt.MoveAction | Qt.CopyAction

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

class DataSourceGroupTreeNode(TreeNode):

    def __init__(self, parent, groupName, classDef):
        assert inspect.isclass(classDef)
        icon = QApplication.style().standardIcon(QStyle.SP_DirOpenIcon)
        super(DataSourceGroupTreeNode, self).__init__(parent, groupName, icon=icon)
        self.childClass = classDef

    def addChildNode(self, node):
        """Ensure child types"""
        assert isinstance(node, DataSourceTreeNode)
        assert isinstance(node.dataSource, self.childClass)
        super(DataSourceGroupTreeNode, self).addChildNode(node)

    def writeXML(self, parentElement):
        elem = super(DataSourceGroupTreeNode, self).writeXML(parentElement)
        elem.setTagName('data_source_group_tree_node')
        elem.setAttribute('datasourcetype', str(self.childClass))
        return elem

    @staticmethod
    def readXml(element):

        if element.tagName() != 'data_source_group_tree_node':
            return None


        name = None
        classDef = None
        node = DataSourceGroupTreeNode(None, name, classDef)

        TreeNode.attachCommonPropertiesFromXML(node, element)

        return node

class DataSourceTreeNode(TreeNode):

    def __init__(self, parent, dataSource):
        super(DataSourceTreeNode, self).__init__(parent, '<empty>')
        self.disconnectDataSource()
        if dataSource:
            self.connectDataSource(dataSource)

    def connectDataSource(self, dataSource):
        from enmapbox.gui.datasources import DataSource
        assert isinstance(dataSource, DataSource)
        self.setName(dataSource.name)
        self.dataSource = dataSource
        self.setTooltip(dataSource.uri)
        self._icon = dataSource.getIcon()
        self.setCustomProperty('uuid', str(self.dataSource.uuid))
        self.setCustomProperty('uri', self.dataSource.uri)

    def disconnectDataSource(self):
        self.dataSource = None
        self.setName('<empty>')
        self._icon = None
        for k in self.customProperties():
            self.removeCustomProperty(k)

    @staticmethod
    def readXml(element):
        if element.tagName() != 'datasource-tree-node':
            return None

        cp = QgsObjectCustomProperties()
        cp.readXml(element)

        from enmapbox.gui.datasources import DataSourceFactory
        dataSource = DataSourceFactory.Factory(cp.value('uri'), name=element.attribute('name'))
        node = DataSourceTreeNode(None, dataSource)
        TreeNode.attachCommonPropertiesFromXML(node, element)

        return node

    def writeXML(self, parentElement):
        elem = super(DataSourceTreeNode, self).writeXML(parentElement)
        elem.setTagName('datasource-tree-node')
        #elem.setAttribute('uuid', str(self.dataSource.uuid))
        return elem


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
        #node.readChildrenFromXml(element)

        #try to find the dock by its uuid in dockmanager
        from enmapbox.gui.main import EnMAPBox

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

    def writeLayerTreeGroupXML(self,parentElement):
        QgsLayerTreeGroup.writeXML(self, parentElement)

        #return super(QgsLayerTreeNode,self).writeXml(parentElement)


    def connectDock(self, dock):
        if isinstance(dock, Dock):
            self.dock = dock
            self.setName(dock.title())
            self.dock.sigTitleChanged.connect(self.setName)
            self.setCustomProperty('uuid', str(dock.uuid))
            self.dock.sigClosed.connect(self.disconnectDock)



    def disconnectDock(self):
        self.dock = None
        #self.removeCustomProperty('uuid')
        self.sigRemoveMe.emit()


class TextDockTreeNode(DockTreeNode):


    def __init__(self, parent, dock):
        assert isinstance(dock, TextDock)
        super(TextDockTreeNode, self).__init__(parent, dock)
        self.setIcon(QIcon(IconProvider.Dock))

    def writeXML(self, parentElement):
        return super(MapDockTreeNode, self).writeXML(parentElement, 'text-dock-tree-node')

class MapDockTreeNode(DockTreeNode):
    """
    A TreeNode linked to a MapDock
    Acts like the QgsLayerTreeMapCanvasBridge
    """
    def __init__(self, parent, dock):

        super(MapDockTreeNode, self).__init__(parent, dock)
        self.setIcon(QIcon(':/enmapbox/icons/viewlist_mapdock.png'))
        self.blockSignals = False
        #if dock:
        #    self.connectDock(dock)

        self.addedChildren.connect(lambda : self.updateCanvas())
        self.removedChildren.connect(lambda: self.updateCanvas())


    def connectDock(self, dock):
        assert isinstance(dock, MapDock)
        super(MapDockTreeNode,self).connectDock(dock)
        self.updateChildNodes()
        self.dock.sigLayersChanged.connect(self.updateChildNodes)


    def updateChildNodes(self):
        if self.dock:
            self.blockSignals = True
            self.removeAllChildren()
            self.blockSignals = False
            for i, l in enumerate(self.dock.canvas.layers()):
                self.insertLayer(i, l)

    def updateCanvas(self):
        if self.dock and not self.blockSignals:
            self.dock.canvas.blockSignals(True)
            layers = self.visibleLayers(self)
            self.dock.setLayerSet(layers)
            self.dock.canvas.blockSignals(False)

    @staticmethod
    def visibleLayers(node):
        if isinstance(node, list):
            lyrs = []
            for child in node:
                lyrs.extend(MapDockTreeNode.visibleLayers(child))
            return lyrs
        elif isinstance(node, QgsLayerTreeGroup):
            lyrs = []
            for child in node.children():
                lyrs.extend(MapDockTreeNode.visibleLayers(child))
            return lyrs
        elif QgsLayerTree.isLayer(node):
            if node.isVisible():
                return [node.layer()]
            else:
                return []
        else:
            raise NotImplementedError()



    def insertLayer(self, idx, layer):
        assert isinstance(layer ,QgsMapLayer)
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

        from enmapbox.gui.main import EnMAPBox
        DSM = EnMAPBox.instance().dataSourceManager


        node = MapDockTreeNode(None, None)
        node.setName(element.attribute('name'))
        node.setExpanded(element.attribute('expanded') == '1')
        node.setVisible(QgsLayerTreeUtils.checkStateFromXml(element.attribute("checked")))
        node.readCommonXML(element)
        # node.readChildrenFromXml(element)

        # try to find the dock by its uuid in dockmanager
        from enmapbox.gui.main import EnMAPBox

        dockManager = EnMAPBox.instance().dockManager
        uuid = node.customProperty('uuid', None)
        if uuid:
            dock = dockManager.getDockWithUUID(str(uuid))
        if dock is None:
            dock = dockManager.createDock('MAP', name=dockName)
        node.connectDock(dock)

        return node



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

