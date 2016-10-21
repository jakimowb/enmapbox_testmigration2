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


#class DockManagerTreeModel(QgsLayerTreeModel):
class DockManagerTreeModel(TreeModel):
    def __init__(self, dockManager, parent):

        super(DockManagerTreeModel, self).__init__(parent)

        self.setFlag(QgsLayerTreeModel.ShowLegend, True)
        self.setFlag(QgsLayerTreeModel.ShowSymbology, True)
        #self.setFlag(QgsLayerTreeModel.ShowRasterPreviewIcon, True)
        self.setFlag(QgsLayerTreeModel.ShowLegendAsTree, True)
        self.setFlag(QgsLayerTreeModel.AllowNodeReorder, True)
        self.setFlag(QgsLayerTreeModel.AllowNodeRename, True)
        self.setFlag(QgsLayerTreeModel.AllowNodeChangeVisibility, True)
        self.setFlag(QgsLayerTreeModel.AllowLegendChangeState, True)

        assert isinstance(dockManager, DockManager)
        self.dockManager = dockManager
        dockManager.sigDockAdded.connect(self.addDock)
        #dockManager.sigDockAdded.connect(self.sandboxslot)
        dockManager.sigDockAdded.connect(lambda : self.sandboxslot2())
        dockManager.sigDockRemoved.connect(self.removeDock)

    def sandboxslot(self, dock):
        s  =""
    def sandboxslot2(self):
        s  =""


    @pyqtSlot(Dock)
    def addDock(self, dock):
        s = ""
        rootNode = self.rootNode
        newNode = None
        if isinstance(dock, MapDock):
            newNode = MapDockTreeNode(rootNode, dock)
        elif isinstance(dock, TextDock):
            newNode = TextDockTreeNode(rootNode, dock)

        if newNode:
            self.rootNode.addChildNode(newNode)


    @pyqtSlot(Dock)
    def removeDock(self, dock):
        s  =""

    def mimeTypes(self):
        #specifies the mime types handled by this model
        types = []
        types.append("application/qgis.layertreemodeldata")
        types.append("application/enmapbox.docktreemodeldata")
        return types

    def dropMimeData(self, data, action, row, column, parent):
        if action == Qt.IgnoreAction:
            return True
        parentNode = self.index2node(parent)

        assert isinstance(data, QMimeData)

        if data.hasFormat("application/qgis.layertreemodeldata"):
            s = ""
            return super(DockManagerTreeModel, self).dropMimeData(data, action, row, column, parent)
        elif data.hasFormat("application/enmapbox.docktreemodeldata"):
            doc = QDomDocument()
            if not doc.setContent(data.data("application/enmapbox.docktreemodeldata")):
                return False

            s = ""
        else:
            return False

    def mimeData(self, indexes):
        indexes = sorted(indexes)
        if len(indexes) == 0:
            return None

        nodesFinal = self.indexes2nodes(indexes, True)
        mimeData = QMimeData()

        doc = QDomDocument()
        rootElem = doc.createElement("emb_tree_model_data");
        for node in nodesFinal:
            node.writeXml(rootElem)
        doc.appendChild(rootElem)
        txt = doc.toString()
        mimeData.setData("application/enmapbox.docktreemodeldata", txt)
        # mimeData.setData("application/x-vnd.qgis.qgis.uri", QgsMimeDataUtils.layerTreeNodesToUriList(nodesFinal) );

        return mimeData


    def data(self, index, role ):
        node = self.index2node(index)
        #todo: implement MapDock specific behaviour

        return super(DockManagerTreeModel, self).data(index, role)



class DockTreeNode(TreeNode):




    def __init__(self, parent, dock):
        name = dock.title()
        super(DockTreeNode, self).__init__(parent, name)

        self.dock = dock
        #self.parent = parent
        #self.dock.sigTitleChanged.connect(self.setName)



class TextDockTreeNode(DockTreeNode):

    def __init__(self, parent, dock):
        assert isinstance(dock, TextDock)
        super(TextDockTreeNode, self).__init__(parent, dock)
        s  =  ""

    def icon(self):
        return QIcon(IconProvider.File_Vector_Polygon)


class MapDockTreeNode(DockTreeNode):
    """
    A TreeNode linked to a MapDock
    Acts like the QgsLayerTreeMapCanvasBridge
    """
    def __init__(self, parent, dock):
        assert isinstance(dock, MapDock)
        super(MapDockTreeNode, self).__init__(parent, dock)


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

    def icon(self):
        return QIcon(IconProvider.File_Raster)



class TreeNode(QgsLayerTreeGroup):
    TAG_NAME = 'dock-tree-node'

    @staticmethod
    def readXml(element):
        """
        Returns the TreeNode
        generalized counterpart of QgsLayerTreeNode* QgsLayerTreeNode::readXml( QDomElement& element )
        :return: TreeNode instance
        """
        assert isinstance(element, QDomElement)
        node = None
        if element.tagName() in ["layer-tree-group","layer-tree-layer"]:
            node = QgsLayerTreeNode.readXML(element)
        elif element.tagName() == TreeNode.TAG_NAME:

            raise NotImplementedError('Abstract TreeNode')
        elif element.tagName() == DockTreeNode.TAG_NAME:

            s = ""
            pass
        else:
            raise NotImplementedError()
        return node



    def __init__(self, parent, name, checked=Qt.Unchecked, tooltip=None, icon=None):
        #QObject.__init__(self)
        super(TreeNode, self).__init__(name, checked)
        self.mParent = parent
        self.setName(name)

        # set default properties using underlying customPropertySet
        self.setTooltip(tooltip)
        self.setCustomProperty('tooltip', '')

        if tooltip: self.setTooltip(tooltip)
        if icon: self.setIcon(icon)
        #if parent is not None:
        #    parent.addChildNode(self)


    def setTooltip(self, tooltip):
        self.customProperty('tooltip', str(tooltip))
    def tooltip(self, default=''):
        return self.customProperty('tooltip',default)

    def setIcon(self, icon):
        self._icon = icon
    def icon(self):
        return self._icon


    def writeXml(self, parentElement):
        assert  isinstance(parentElement, QDomElement)

        doc = parentElement.ownerDocument()
        elem = doc.createElement(TreeNode.TAG_NAME)
        elem.setAttribute('name', self.name())
        elem.setAttribute('expanded', '1' if self.isExpanded() else '0')
        elem.setAttribute('checked', QgsLayerTreeUtils.checkStateToXml(Qt.Checked))

        #self.writeCommonXML(elem)
        self.writeCommonXML(elem)
        for node in self.children():
            node.writeXml(elem)
        parentElement.appendChild(elem)



class TreeView(QgsLayerTreeView):
    """
    Re-Implementation of QgsLayerTreeGroup:
        - can have child nodes
        - intends to implement more fine-grained control
        - not map-layer specific
    """
    def __init__(self, parent, expanded=True, nodeType=3):
        super(TreeNode, self).__init__(nodeType)

        self.mName = ''
        self.mVisible = Qt.Unchecked
        self.icon = None


        if parent is not None:
            parent.addChildNode(self)

    """
    slot to set the name
    """
    def setName(self, name):
        self.mName = name
    def name(self):
        return self.mName

    def setVisible(self, state):
        self.mVisible = state
    def isVisible(self):
        return self.mVisible

    def insertChildNode(self, index, node):
        self.insertChildNodes(index, [node])

    def insertChildNodes(self, index, nodes):

        self.insertChildrenPrivate(index, nodes)
        self.updateVisibilityFromChildren()

    def updateVisibilityFromChildren(self):

        for child in self.children():

            s  = ""
            self.setVisible(Qt.Checked)
        pass

    def setVisible(self, state):
        if state is not self.isVisible():
            self.setVisible(state)
            self.updateVisibilityFromChildren()



    def removeAllChildren(self):
        del self.children()[:]

    @staticmethod
    def readXML(QDomElement):

        raise NotImplementedError()

    def writeXML(self, QDomElement):
        raise NotImplementedError()

    def __init__(self, parent):
        super(TreeView, self).__init__(parent)


class TreeModel(QgsLayerTreeModel):

    def __init__(self, parent):
        self.rootNode = TreeNode(None, None)
        super(TreeModel, self).__init__(self.rootNode, parent)




class DataSourceManagerTreeModel(TreeModel):

    def __init__(self,parent, dataSourceManager):
        super(DataSourceManagerTreeModel, self).__init__(parent)
        assert isinstance(dataSourceManager, DataSourceManager)
        self.DSM = dataSourceManager
        self.DSM.sigDataSourceAdded.connect(self.addDataSource)
        self.DSM.sigDataSourceRemoved.connect(self.removeDataSource)

        for ds in self.DSM.sources:
            self.addDataSource(ds)


    def addDataSource(self, dataSource):
        assert isinstance(dataSource, DataSource)
        dsTypeName = self.getSourceTypeName(dataSource)

        existingNames = [c.name() for c in self.children()]
        if dsTypeName not in existingNames:
            typeNode = TreeNode(self.rootNode, dsTypeName,
                                icon=QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_DirOpenIcon))
            self.rootNode.insertChildNode(0, typeNode)

        #find TreeNode realted to dsTypeName
        typeNode = [c for c in self.rootNode.children() if c.name() == dsTypeName][0]

        dsNode = dataSource.getTreeItem(typeNode)
        typeNode.insertChildNode(0, dsNode)


    def removeDataSource(self, dataSource):
        assert isinstance(dataSource, DataSource)

        dsTypeName = self.getSourceTypeName(dataSource)

        for r1 in range(self.rowCount(QModelIndex())):
            idx1 = self.index(r1, 0, QModelIndex())
            if dsTypeName == str(idx1.data()):
                for r2 in range(self.rowCount(idx1)):
                    idx2 = self.index(r2, 0, idx1)
                    ds = self.data(idx2, Qt.UserRole)
                    if ds is dataSource:
                        typeItem = self.data(idx1, 'TreeItem')
                        dsItem = self.data(idx2, 'TreeItem')
                        self.beginRemoveRows(idx1, r2, r2)
                        typeItem.removeChild(dsItem)
                        self.endRemoveRows()

                        if typeItem.childCount() == 0:
                            self.beginRemoveRows(QModelIndex(), r1, r1)
                            self.rootItem.removeChild(typeItem)
                            self.endRemoveRows()
                        return


    def getSourceTypeName(self, dataSource):

        assert isinstance(dataSource, DataSource)
        return type(dataSource).__name__



class DataSourceManagerTreeModelX(QAbstractItemModel):
    """
    View on DataSourceManager that implements QAbstractItemModel as TreeModel
    See details described under:
    http://doc.qt.io/qt-5/qtwidgets-itemviews-simpletreemodel-example.html
    http://doc.qt.io/qt-5/model-view-programming.html#model-subclassing-reference
    """
    #columnames = ['Name','Description']
    columnames = ['Name']

    SourceTypes = [DataSourceRaster, DataSourceVector, DataSourceFile,
                   DataSourceModel, DataSourceTextFile, DataSourceXMLFile]
    SourceTypeNames = ['Raster', 'Vector', 'File','Model', 'Text', 'Text']


    def getSourceTypeName(self, dataSource):
        assert type(dataSource) in DataSourceManagerTreeModel.SourceTypes
        return DataSourceManagerTreeModel.SourceTypeNames[DataSourceManagerTreeModel.SourceTypes.index(type(dataSource))]

    def __init__(self, dataSourceManager):
        assert isinstance(dataSourceManager, DataSourceManager)
        QAbstractItemModel.__init__(self)
        self.DSM = dataSourceManager
        self.DSM.sigDataSourceAdded.connect(self.addDataSource)
        self.DSM.sigDataSourceRemoved.connect(self.removeDataSource)
        self.rootItem = TreeNode(None, None)
        self.setupModelData(self.rootItem, None)

    def setupModelData(self, parent, data):

        for ds in self.DSM.sources:
            self.addDataSource(ds)
        s  =""
        pass

    """
    TreeItem *TreeModel::getItem(const QModelIndex &index) const
    """
    def getItem(self, index):
        #assert isinstance(index, QModelIndex)
        item = None
        if index.isValid():
            item = index.internalPointer()
        else:
            item = self.rootItem
        #assert isinstance(item, TreeItem)
        return item

    """
    Provides the number of rows of data exposed by the model.
    int TreeModel::rowCount(const QModelIndex &parent) const
    """
    def rowCount(self, index):
        #assert isinstance(parent, QModelIndex)
        parentItem = self.getItem(index)
        return parentItem.childCount()



    """
    Provides the number of columns of data exposed by the model.
    int TreeModel::columnCount(const QModelIndex & /* parent */) const
    """
    def columnCount(self, parent):
        #assert isinstance(parent, QModelIndex)
        return len(self.columnames)
        #maybe worth?
        #parentItem = self.getItem(parent)
        #return parentItem.columnCount()

        """
        return len(self.columnames)

        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.rootItem.columnCount()
        """

    """
    Used by other components to obtain information about each item provided by the model.
    In many models, the combination of flags should include Qt::ItemIsEnabled and Qt::ItemIsSelectable.
    Qt::ItemFlags TreeModel::flags(const QModelIndex &index) const
    """
    def flags(self, index):

        #isinstance(index, QModelIndex)
        default = super(DataSourceManagerTreeModel, self).flags(index)
        if index.isValid():
            return Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled | default
        else:
            return default
        """
        default = super(DataSourceManagerTreeModel, self).flags(index)
        if index.isValid():
            return Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled | default
        else:
            return default
        """



    """
       Given a model index for a parent item, this function allows views and delegates to access children of that item.
       If no valid child item - corresponding to the specified row, column, and parent model index, can be found,
       the function must return QModelIndex(), which is an invalid model index.
    QModelIndex TreeModel::index(int row, int column, const QModelIndex &parent) const
    """
    def index(self, row, column, parent=None):
        #assert isinstance(parent, QModelIndex)
        if parent is None:
            parent = QModelIndex()

        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        parentItem = self.getItem(parent)
        #assert isinstance(parentItem, TreeItem)
        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

        """
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()
        """



    """
    Provides a model index corresponding to the parent of any given child item. If the model index specified
    corresponds to a top-level item in the model, or if there is no valid parent item in the model,
    the function must return an invalid model index, created with the empty QModelIndex() constructor.

    QModelIndex TreeModel::parent(const QModelIndex &index) const
    """
    def parent(self, index):
        #assert isinstance(index, QModelIndex)
        if not index.isValid():
            return QModelIndex()

        childItem = self.getItem(index)
        parentItem = childItem.parent()
        if parentItem == self.rootItem or parentItem is None:
            return QModelIndex()

        return self.createIndex(parentItem.childNumber(), 0, parentItem)

        """
        if not index.isValid():
            return QModelIndex()
        else:
            childItem = index.internalPointer()
            parentItem = childItem.parent
        if parentItem == self.rootItem:
            return QModelIndex()
        return self.createIndex(parentItem.row(), 0, parentItem)
        """

    """
    Used to supply item data to views and delegates. Generally, models only need to supply data for
    Qt::DisplayRole and any application-specific user roles, but it is also good practice to provide
    data for Qt::ToolTipRole, Qt::AccessibleTextRole, and Qt::AccessibleDescriptionRole.
    See the Qt::ItemDataRole enum documentation for information about the types associated with each role.
    """
    def data(self, index, role):
        #assert isinstance(index, QModelIndex)
        if not index.isValid():
            return None;


        item = self.getItem(index)
        if role == Qt.DisplayRole:
            columnname = self.columnames[index.column()].lower()
            text = ''.join([str(item.__dict__[k]) for k in item.__dict__.keys() if k.lower() in columnname])
            return text
        if role == Qt.ToolTipRole:
            return item.tooltip
        if role == Qt.DecorationRole and index.column() == 0:
            return item.icon
        if role == Qt.UserRole:
            return item.data
        if role == 'TreeItem':
            return item
        return None


    def addDataSource(self, dataSource):
        assert isinstance(dataSource, DataSource)
        dsTypeName = self.getSourceTypeName(dataSource)

        existingNames = [c.name for c in self.rootItem.childs]
        if dsTypeName not in existingNames:
            r1 = len(existingNames)
            #todo: insert in alphabetical order
            self.beginInsertRows(QModelIndex(), r1, r1)
            typeItem = TreeNode(None, dsTypeName,
                                   icon=QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_DirOpenIcon))
            self.rootItem.insertChild(r1, typeItem)
            self.endInsertRows()

        #find TreeItem with dsTypeName
        dsItem = dataSource.getTreeItem(None)
        for r1 in range(self.rowCount(QModelIndex())):
            idx1 = self.index(r1, 0, QModelIndex())
            if dsTypeName == str(idx1.data()):

                dsTypeItem = self.data(idx1, 'TreeItem')
                assert isinstance(dsTypeItem, TreeItemOLD)

                #todo: alphabetical order?
                r2 = dsTypeItem.childCount()

                self.beginInsertRows(idx1, r2, r2)
                dsTypeItem.insertChild(r2, dsItem)
                self.endInsertRows()


    def indexOfTreeItem(self, item, idx = None):
        if idx is None:
            idx = QModelIndex()

        item_b = self.data(idx, 'TreeItem')
        if item is item_b:
            return idx
        else:
            for r in range(self.rowCount(idx)):
                idx2 = self.indexOfTreeItem(item, self.index(r, 0 , idx))
                if idx2:
                    return idx2

        return None



    def removeDataSource(self, dataSource):
        assert isinstance(dataSource, DataSource)

        dsTypeName = self.getSourceTypeName(dataSource)

        for r1 in range(self.rowCount(QModelIndex())):
            idx1 = self.index(r1, 0, QModelIndex())
            if dsTypeName == str(idx1.data()):
                for r2 in range(self.rowCount(idx1)):
                    idx2 = self.index(r2, 0 , idx1)
                    ds = self.data(idx2, Qt.UserRole)
                    if ds is dataSource:
                        typeItem = self.data(idx1, 'TreeItem')
                        dsItem = self.data(idx2, 'TreeItem')
                        self.beginRemoveRows(idx1, r2, r2)
                        typeItem.removeChild(dsItem)
                        self.endRemoveRows()

                        if typeItem.childCount() == 0:
                            self.beginRemoveRows(QModelIndex(),r1,r1)
                            self.rootItem.removeChild(typeItem)
                            self.endRemoveRows()
                        return

    def supportedDragActions(self):
        return Qt.CopyAction

    def supportedDropActions(self):
        return Qt.CopyAction



    def dropMimeData(self, mimeData, Qt_DropAction, row, column, parent):

        s = ""


    def mimeData(self, indices):
        mimeData = QMimeData()

        for index in indices:
            assert isinstance(index, QModelIndex)
            item = self.getItem(index)
            mimeData = item.mimeData()

        #todo: handle collection of mimeData
        return mimeData
    #read only access functions





    """
    Provides views with information to show in their headers. The information is only
    retrieved by views that can display header information.
    """
    def headerData(self, section, orientation, role=None):

        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.columnames[section]
        elif role == Qt.ToolTipRole:
            return None
        else:
            return None
        pass


    #editable items
    """
    Must return an appropriate combination of flags for each item. In particular, the value returned
    by this function must include Qt::ItemIsEditable in addition to the values applied to
    items in a read-only model.
    """
    #def flags(self):
    #    pass

    """
    Used to modify the item of data associated with a specified model index. To be able to accept
    user input, provided by user interface elements, this function must handle data associated
    with Qt::EditRole. The implementation may also accept data associated with many different
    kinds of roles specified by Qt::ItemDataRole. After changing the item of data, models
    must emit the dataChanged() signal to inform other components of the change.
    """


    def setData(self, index, data, role=None):
        assert isinstance(index, QModelIndex)
        assert isinstance(data, TreeItemOLD)
        #return False
        self.dataChanged.emit()

    #    pass

    """
    Used to modify horizontal and vertical header information. After changing the item of data,
    models must emit the headerDataChanged() signal to inform other components of the change.
    """
    #def setHeaderData(self, p_int, Qt_Orientation, QVariant, int_role=None):
    #    pass

    #resizable models

    """
    Used to add new rows and items of data to all types of model. Implementations must call
    beginInsertRows() before inserting new rows into any underlying data structures, and call
    endInsertRows() immediately afterwards.
    """
    #def insertRows(self, p_int, p_int_1, QModelIndex_parent=None, *args, **kwargs):
    #    pass


    """
    Used to remove rows and the items of data they contain from all types of model. Implementations must
    call beginRemoveRows() before inserting new columns into any underlying data structures, and call
    endRemoveRows() immediately afterwards.
    """
    #def removeRows(self, p_int, p_int_1, QModelIndex_parent=None, *args, **kwargs):
    #    pass

    """
    Used to add new columns and items of data to table models and hierarchical models. Implementations must
    call beginInsertColumns() before rows are removed from any underlying data structures, and call
    endInsertColumns() immediately afterwards.
    """
    #def insertColumns(self, p_int, p_int_1, QModelIndex_parent=None, *args, **kwargs):
    #    pass

    """
    Used to remove columns and the items of data they contain from table models and hierarchical models.
    Implementations must call beginRemoveColumns() before columns are removed from any underlying data
    structures, and call endRemoveColumns() immediately afterwards.
    """
    #def removeColumns(self, p_int, p_int_1, QModelIndex_parent=None, *args, **kwargs):

    #    pass

    #lazy population

    def hasChildren(self, parent):

        item = self.getItem(parent)
        return item.childCount() > 0



    #parents and childrens




