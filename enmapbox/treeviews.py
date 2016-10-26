import os, sys
import six
import importlib
from PyQt4.QtCore import *
from PyQt4.QtXml import *
from PyQt4.QtGui import *
from qgis.gui import *
from qgis.core import *
import enmapbox
dprint = enmapbox.dprint

from enmapbox.docks import *
from enmapbox.utils import *


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
        classes = [MapDock, TextDock, MimeDataDock, Dock]
        nodes   = [MapDockTreeNode, TextDockTreeNode, TextDockTreeNode, DockTreeNode]
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
        for nodeClass in [TreeNode, DockTreeNode, MapDockTreeNode, TextDockTreeNode]:
            if nodeClass.TAG_NAME == tagName:
                node = nodeClass.readXml(elem)
                break
        if node is None and tagName in ['layer-tree-group','layer-tree-layer']:
            node = QgsLayerTreeNode.readXml(elem)

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
        self.setCustomProperty('tooltip', '')

        if tooltip: self.setTooltip(tooltip)
        self.setIcon(icon)
        if parent is not None:
            parent.addChildNode(self)


    def removeChildren(self, i0, cnt):
        self.removeChildrenPrivate(i0, cnt)
        self.updateVisibilityFromChildren()

    def setTooltip(self, tooltip):
        self.customProperty('tooltip', str(tooltip))
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


    def writeXML(self, parentElement, tagName='tree-node'):
        assert isinstance(parentElement, QDomElement)
        doc = parentElement.ownerDocument()
        elem = doc.createElement(tagName)
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
            print('READ {}/{}'.format(element.tagName(),childElem.tagName()))
            node = TreeNodeProvider.CreateNodeFromXml(childElem)

            if node:
                nodes.append(node)
            childElem = childElem.nextSibling()
        if len(nodes) > 0:
            self.insertChildNodes(-1, nodes)

    def dropMimeData(self):
        raise NotImplementedError()



class TreeModel(QgsLayerTreeModel):

    def __init__(self, parent, enmapboxInstance):
        import enmapbox.main
        self.rootNode = TreeNode(None, None)
        assert isinstance(enmapboxInstance, enmapbox.main.EnMAPBox)
        self.enmapbox = enmapboxInstance
        super(TreeModel, self).__init__(self.rootNode, parent)

    def data(self, index, role ):
        node = self.index2node(index)
        if isinstance(node, TreeNode):
            if role == Qt.DecorationRole:
                return node.icon()

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

    def removeDockNode(self, node):
        idx = self.node2index(node)
        p = self.index2node(idx.parent())
        p.removeChildNode(node)


class DataSourceGroupTreeNode(TreeNode):

    def __init__(self, parent, groupName, classDef):
        assert inspect.isclass(classDef)
        icon = QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_DirOpenIcon)
        super(DataSourceGroupTreeNode, self).__init__(parent, groupName, icon=icon)
        self.childClass = classDef

    def addChildNode(self, node):
        """Ensure child types"""
        assert isinstance(node, DataSourceTreeNode)
        assert isinstance(node.dataSource, self.childClass)
        super(DataSourceGroupTreeNode, self).addChildNode(node)

    def writeXML(self, parentElement):
        return super(DataSourceGroupTreeNode, self).writeXML(parentElement, 'data_source_group_tree_node')


class DataSourceTreeNode(TreeNode):

    def __init__(self, parent, dataSource):
        super(DataSourceTreeNode, self).__init__(parent, dataSource.name)
        self.dataSource = dataSource
        self._icon = dataSource.getIcon()
        self.setCustomProperty('uuid', str(self.dataSource.uuid))
        self.setCustomProperty('uri', self.dataSource.uri)

    def writeXML(self, parentElement):
        return super(DataSourceTreeNode, self).writeXML(parentElement, 'data_source_tree_node')


class DockTreeNode(TreeNode):

    @staticmethod
    def readXml(element):
        if not DockTreeNode.inherited_xml_tag(element):
            return None

        tagName = element.tagName()
        dock = None
        node = DockTreeNode(None, dock)
        dockName = element.attribute('name')
        node.setName(dockName)
        node.setExpanded(element.attribute('expanded') == '1')
        node.setVisible(QgsLayerTreeUtils.checkStateFromXml(element.attribute("checked")))
        node.readCommonXML(element)
        #node.readChildrenFromXml(element)

        #try to find the dock by its uuid in dockmanager
        from enmapbox.main import EnMAPBox

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
        self._icon = QIcon(IconProvider.Dock)
        if isinstance(dock, Dock):
            self.connectDock(dock)


    def writeXML(self, parentElement):
        return super(DockTreeNode, self).writeXML(parentElement, 'dock-tree-node')


    def connectDock(self, dock):
        if isinstance(dock, Dock):
            self.dock = dock
            self.setName(dock.title())
            self.dock.sigTitleChanged.connect(self.setName)
            self.setCustomProperty('uuid', str(dock.uuid))
            self.dock.sigClosed.connect(self.disconnectDock)


    def disconnectDock(self):
        self.dock = None
        self.removeCustomProperty('uuid')
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
        assert isinstance(dock, MapDock)
        super(MapDockTreeNode, self).__init__(parent, dock)

        self.setIcon(QIcon(IconProvider.MapDock))
        #self.bridge = QgsLayerTreeMapCanvasBridge(self, self.dock.canvas, parent)
        #self.bridge.setAutoEnableCrsTransform(True)
        #self.bridge.setAutoSetupOnFirstLayer(True)
        self.dock.sigLayersChanged.connect(self.refreshLayerOrder)
        self.refreshLayerOrder()

    def refreshLayerOrder(self):
        self.removeAllChildren()
        for i, l in enumerate(self.dock.canvas.layers()):
            self.insertLayer(i, l)

    def insertLayer(self, idx, layer):
        assert isinstance(layer ,QgsMapLayer)
        if layer is None or QgsMapLayerRegistry.instance().mapLayer(layer.id()) != layer:
            return None

        ll = QgsLayerTreeLayer(layer)
        self.insertChildNode(idx, ll)
        return ll

    def writeXML(self, parentElement):
        return super(MapDockTreeNode, self).writeXML(parentElement, 'map-dock-tree-node')



class TreeView(QgsLayerTreeView):

    def __init__(self, parent):
        super(TreeView, self).__init__(parent)



class DockManagerTreeModel(TreeModel):
    def __init__(self, parent, enmapboxInstance):

        super(DockManagerTreeModel, self).__init__(parent, enmapboxInstance)

        self.setFlag(QgsLayerTreeModel.ShowLegend, True)
        self.setFlag(QgsLayerTreeModel.ShowSymbology, True)
        #self.setFlag(QgsLayerTreeModel.ShowRasterPreviewIcon, True)
        self.setFlag(QgsLayerTreeModel.ShowLegendAsTree, True)
        self.setFlag(QgsLayerTreeModel.AllowNodeReorder, True)
        self.setFlag(QgsLayerTreeModel.AllowNodeRename, True)
        self.setFlag(QgsLayerTreeModel.AllowNodeChangeVisibility, True)
        self.setFlag(QgsLayerTreeModel.AllowLegendChangeState, True)

        self.dockManager = self.enmapbox.dockManager
        self.dockManager.sigDockAdded.connect(self.addDockNode)
        self.dockManager.sigDockAdded.connect(lambda : self.sandboxslot2())
        #dockManager.sigDockRemoved.connect(self.removeDock)


    def sandboxslot(self, dock):
        s  =""
    def sandboxslot2(self):
        s  =""


    def addDockNode(self, dock):
        rootNode = self.rootNode
        newNode = TreeNodeProvider.CreateNodeFromDock(dock, rootNode)
        newNode.sigRemoveMe.connect(lambda : self.removeDockNode(newNode))




    def flags(self, parent):
        if not parent.isValid():
            return Qt.NoItemFlags

        #specify TreeNode specific actions
        parentNode = self.index2node(parent)
        if parentNode is None:
            return Qt.NoItemFlags

        isL1 = parentNode.parent() == self.rootNode
        if isinstance(parentNode, DockTreeNode):
            flags = Qt.ItemIsEnabled | \
                    Qt.ItemIsSelectable | \
                    Qt.ItemIsUserCheckable
            if isL1:
                flags |= Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsEditable


        else:
            flags = Qt.NoItemFlags
        return flags


    def mimeTypes(self):
        #specifies the mime types handled by this model
        types = []
        types.append("application/qgis.layertreemodeldata")
        types.append("application/enmapbox.docktreemodeldata")
        return types

    def dropMimeData(self, data, action, row, column, parent):
        assert isinstance(data, QMimeData)
        parentNode = self.index2node(parent)
        #L1 is the first level below the root tree -> to place dock trees
        isL1Node = parentNode.parent() == self.rootNode

        result = False
        if action == Qt.MoveAction:
            #collect nodes
            nodes = []
            if data.hasFormat("application/qgis.layertreemodeldata"):

                result = QgsLayerTreeModel.dropMimeData(self, data, action, row, column, parent)
                s = ""

            elif data.hasFormat("application/enmapbox.docktreemodeldata"):
                doc = QDomDocument()
                if doc.setContent(data.data("application/enmapbox.docktreemodeldata")):
                    print(str(doc.toString()))
                    root = doc.documentElement()
                    child = root.firstChildElement()
                    while not child.isNull():
                        if 'dock-tree-node' in str(child.tagName()):
                            nodes.append(TreeNodeProvider.CreateNodeFromXml(child))
                        child = child.nextSibling()

            nodes = [n for n in nodes if n is not None]

            #insert nodes, if possible
            if len(nodes) > 0:
                if row==-1 and column == -1:
                    parentNode = parentNode.parent()
                parentNode.insertChildNodes(-1, nodes)
                result = True

        return result

    def mimeData(self, indexes):
        indexes = sorted(indexes)
        if len(indexes) == 0:
            return None

        nodesFinal = self.indexes2nodes(indexes, True)
        mimeData = QMimeData()

        doc = QDomDocument()
        rootElem = doc.createElement("dock_tree_model_data");
        for node in nodesFinal:
            node.writeXML(rootElem)
        doc.appendChild(rootElem)
        txt = doc.toString()
        mimeData.setData("application/enmapbox.docktreemodeldata", txt)
        # mimeData.setData("application/x-vnd.qgis.qgis.uri", QgsMimeDataUtils.layerTreeNodesToUriList(nodesFinal) );

        return mimeData



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
        if isinstance(node, DockTreeNode) and isinstance(node.dock, Dock):
            if role == Qt.CheckStateRole:
                if value == Qt.Unchecked:
                    node.dock.setVisible(False)
                else:
                    node.dock.setVisible(True)
                return True

        return False


class DataSourceManagerTreeModel(TreeModel):

    def __init__(self,parent, enmapboxInstance):

        assert isinstance(enmapboxInstance, enmapbox.main.EnMAPBox)
        super(DataSourceManagerTreeModel, self).__init__(parent, enmapboxInstance)

        self.DSM = self.enmapbox.dataSourceManager
        self.DSM.sigDataSourceAdded.connect(self.addDataSource)
        self.DSM.sigDataSourceRemoved.connect(self.removeDataSource)

        for ds in self.DSM.sources:
            self.addDataSource(ds)

    def mimeTypes(self):
        #specifies the mime types handled by this model
        types = []
        types.append("text/uri-list")
        types.append("application/qgis.layertreemodeldata")
        types.append("application/enmapbox.datasourcetreemodeldata")
        return types

    def dropMimeData(self, data, action, row, column, parent):
        parentNode = self.index2node(parent)
        assert isinstance(data, QMimeData)

        isL1Node = parentNode.parent() == self.rootNode

        result = False
        if action == Qt.MoveAction:
            # collect nodes
            nodes = []

            if data.hasFormat("application/enmapbox.datasourcetreemodeldata"):
                return False #do not allow moving within DataSourceTree

            # add new data from external
            elif data.hasFormat('text/uri-list'):
                for url in data.urls():
                    self.DSM.addSource(url)

            # add new from QGIS
            elif data.hasFormat("application/qgis.layertreemodeldata"):
                result = QgsLayerTreeModel.dropMimeData(self, data, action, row, column, parent)
                s = ""


            nodes = [n for n in nodes if n is not None]

            # insert nodes, if possible
            if len(nodes) > 0:
                if row == -1 and column == -1:
                    parentNode = parentNode.parent()
                parentNode.insertChildNodes(-1, nodes)
                result = True

        return result

    def mimeData(self, indexes):
        indexes = sorted(indexes)
        if len(indexes) == 0:
            return None

        nodesFinal = self.indexes2nodes(indexes, True)
        mimeData = QMimeData()
        #define application/enmapbox.datasourcetreemodeldata
        doc = QDomDocument()
        uriList = list()
        rootElem = doc.createElement("datasource_tree_model_data");
        exportedNodes = []
        for node in nodesFinal:
            if isinstance(node, DataSourceTreeNode):
                exportedNodes.append(node)
            elif isinstance(node, DataSourceGroupTreeNode):
                for n in node.children():
                    exportedNodes.append(n)

        for node in exportedNodes:
            node.writeXML(rootElem)
            uriList.append(QUrl(node.dataSource.uri))

        doc.appendChild(rootElem)
        txt = doc.toString()
        mimeData.setData("application/enmapbox.datasourcetreemodeldata", txt)
        mimeData.setUrls(uriList)

        # mimeData.setData("application/x-vnd.qgis.qgis.uri", QgsMimeDataUtils.layerTreeNodesToUriList(nodesFinal) );

        return mimeData

    def getSourceGroup(self, dataSource):
        """Returns the source group relate to a data source"""
        assert isinstance(dataSource, DataSource)

        groups = [(DataSourceRaster, 'Raster Data'),
                  (DataSourceVector, 'Vector Data'),
                  (DataSourceModel, 'Models'),
                  (DataSourceFile, 'Files'),
                  (DataSource, 'Other sources')]

        srcGrp = None
        for groupType, groupName in groups:
            if isinstance(dataSource, groupType):
                srcGrp = [c for c in self.rootNode.children() if c.name() == groupName]
                if len(srcGrp) == 0:
                    #create new group node and add it to the model
                    srcGrp = DataSourceGroupTreeNode(self.rootNode, groupName, groupType)
                elif len(srcGrp) == 1:
                    srcGrp = srcGrp[0]
                else:
                    raise Exception()
                break
        if srcGrp is None:
            s = ""
        return srcGrp


    def addDataSource(self, dataSource):
        assert isinstance(dataSource, DataSource)
        dataSourceNode = TreeNodeProvider.CreateNodeFromDataSource(dataSource, None)
        sourceGroup = self.getSourceGroup(dataSource)
        sourceGroup.addChildNode(dataSourceNode)


    def removeDataSource(self, dataSource):
        assert isinstance(dataSource, DataSource)
        sourceGroup = self.getSourceGroup(dataSource)
        to_remove = [c for c in sourceGroup.children() if c.source == dataSource]
        if len(to_remove) > 0:
            sourceGroup.removeChildNodes(to_remove)


    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        #specify TreeNode specific actions
        node = self.index2node(index)
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable

        if isinstance(node, DataSourceGroupTreeNode):
            flags |= Qt.ItemIsDropEnabled
        elif isinstance(node, DataSourceTreeNode):
            flags |= Qt.ItemIsDragEnabled
        else:
            flags = Qt.NoItemFlags
        return flags

