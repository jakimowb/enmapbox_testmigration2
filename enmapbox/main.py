from __future__ import absolute_import
import six, sys, os, gc, re, collections, site
import qgis.core
import qgis.gui
from osgeo import gdal, ogr

import enmapbox
from enmapbox.utils import *
dpring = enmapbox.dprint
jp = os.path.join


VERSION = '2016-0.beta'
DIR = os.path.dirname(__file__)
DIR_REPO = os.path.dirname(DIR)
DIR_SITE_PACKAGES = jp(DIR_REPO, 'site-packages')
DIR_GUI = jp(DIR,'gui')
site.addsitedir(DIR_SITE_PACKAGES)

from enmapbox.docks import *

LORE_IPSUM = r"Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet."


#todo: reduce imports to minimum
#import PyQt4
#import pyqtgraph
#import pyqtgraph.dockarea.DockArea

import qgis.core

from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from enmapbox.utils import *
from enmapbox.datasources import *

RC_SUFFIX =  '_py3' if six.PY3 else '_py2'

add_and_remove = DIR_GUI not in sys.path
if add_and_remove: sys.path.append(DIR_GUI)

ENMAPBOX_GUI_UI, qt_base_class = uic.loadUiType(os.path.normpath(jp(DIR_GUI, 'enmapbox_gui.ui')),
                                    from_imports=False, resource_suffix=RC_SUFFIX)
if add_and_remove: sys.path.remove(DIR_GUI)
del add_and_remove, RC_SUFFIX



class DataSourceManagerTreeModel(QAbstractItemModel):
    """
    View on DataSourceManager that implements QAbstractItemModel as TreeModel
    See details described under:
    http://doc.qt.io/qt-5/qtwidgets-itemviews-simpletreemodel-example.html
    http://doc.qt.io/qt-5/model-view-programming.html#model-subclassing-reference
    """
    #columnames = ['Name','Description']
    columnames = ['Name']

    SourceTypes = [DataSourceRaster, DataSourceVector, DataSourceFile, DataSourceModel]
    SourceTypeNames = ['Raster', 'Vector', 'File','Model']


    def getSourceTypeName(self, dataSource):
        assert type(dataSource) in DataSourceManagerTreeModel.SourceTypes
        return DataSourceManagerTreeModel.SourceTypeNames[DataSourceManagerTreeModel.SourceTypes.index(type(dataSource))]

    def __init__(self, dataSourceManager):
        assert isinstance(dataSourceManager, DataSourceManager)
        QAbstractItemModel.__init__(self)
        self.DSM = dataSourceManager
        self.DSM.sigDataSourceAdded.connect(self.addDataSource)
        self.DSM.sigDataSourceRemoved.connect(self.removeDataSource)
        self.rootItem = TreeItem(None, None)
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
            typeItem = TreeItem(None, dsTypeName,
                                icon=QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_DirOpenIcon))
            self.rootItem.insertChild(r1, typeItem)
            self.endInsertRows()

        #find TreeItem with dsTypeName
        dsItem = dataSource.getTreeItem(None)
        for r1 in range(self.rowCount(QModelIndex())):
            idx1 = self.index(r1, 0, QModelIndex())
            if dsTypeName == str(idx1.data()):

                dsTypeItem = self.data(idx1, 'TreeItem')
                assert isinstance(dsTypeItem, TreeItem)

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
        assert isinstance(data, TreeItem)
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






class EnMAPBox_GUI(QtGui.QMainWindow, ENMAPBOX_GUI_UI):
    def __init__(self, parent=None):
        """Constructor."""
        super(EnMAPBox_GUI, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.setWindowIcon(getQIcon())

        pass




def getQIcon(name=IconProvider.EnMAP_Logo):
    return QtGui.QIcon(name)


from enmapbox.datasources import *
class DataSourceManager(QObject):

    """
    Keeps overview on different data sources handled by EnMAP-Box.
    Similar like QGIS data registry, but manages non-spatial data sources (text files etc.) as well.
    """

    sigDataSourceAdded = pyqtSignal(DataSource)
    sigDataSourceRemoved = pyqtSignal(DataSource)

    def __init__(self):
        QObject.__init__(self)
        self.sources = set()
        self.qgsMapLayerRegistry = QgsMapLayerRegistry.instance()
        self.updateFromQgsMapLayerRegistry()


        enmapbox.processing.sigFileCreated.connect(lambda file: self.addSource(file))
        self.updateFromProcessingFramework()

    def updateFromProcessingFramework(self):
        import enmapbox.processing
        for p,n in zip(enmapbox.processing.MODEL_URIS,
                       enmapbox.processing.MODEL_NAMES):
            self.addSource(p, name=n)

    def updateFromQgsMapLayerRegistry(self):
        """
        Add data sources registered in the QgsMapLayerRegistry to the data source manager
        :return: True, if a new source was added
        """
        r = False
        existing_src = [ds.src for ds in self.sources if isinstance(ds, DataSourceSpatial)]
        for lyr in self.qgsMapLayerRegistry.mapLayers().values():
            src = lyr.dataProvider().dataSourceUri()
            if src not in existing_src:
                r =  r or (self.addSource(src) is not None)
        return r

    def getUriList(self, sourcetype='All'):
        """
        Returns URIs of registered data sources
        :param sourcetype: uri filter: 'ALL' (default),'RASTER''VECTOR' or 'MODEL' to return only uri's related to these sources
        :return: uri as string (str), e.g. a file path
        """
        sourcetype = sourcetype.upper()
        if isinstance(sourcetype, type):
            return [ds.getUri() for ds in self.sources if type(ds) is sourcetype]

        assert sourcetype in ['ALL','RASTER''VECTOR','MODEL']
        if sourcetype == 'ALL':
            return [ds.getUri() for ds in self.sources]
        elif sourcetype == 'VECTOR':
            return [ds.getUri() for ds in self.sources if isinstance(ds, DataSourceVector)]
        elif sourcetype == 'RASTER':
            return [ds.getUri() for ds in self.sources if isinstance(ds, DataSourceVector)]
        elif sourcetype == 'MODEL':
            return [ds.getUri() for ds in self.sources if isinstance(ds, DataSourceModel)]

    @pyqtSlot(str)
    @pyqtSlot('QString')
    def addSource(self, src, name=None, icon=None):
        """
        Adds a new data source.
        :param src: any object
        :param name:
        :param icon:
        :return: a DataSource instance, if sucessfully added
        """
        ds = DataSource.Factory(src, name=name, icon=icon)


        if isinstance(ds, DataSource):
            # check if source is already registered
            for src in self.sources:
                if src.uri == ds.uri:
                    return src #return object reference of already existing source

            self.sources.add(ds)
            self.sigDataSourceAdded.emit(ds)

            if isinstance(ds, DataSourceModel):
                enmapbox.processing.registerModel(ds.uri)

        return ds

    def removeSource(self, src):
        assert isinstance(src, DataSource)
        if src in self.sources:
            self.sources.remove(src)
            self.sigDataSourceRemoved.emit(src)
        else:
            print('DEBUG: can not remove {}'.format(src))



    def getSourceTypes(self):
        return sorted(list(set([type(ds) for ds in self.sources])))





class EnMAPBox:

    _instance = None

    @staticmethod
    def instance():
        return EnMAPBox._instance



    """Main class that drives the EnMAPBox_GUI and all the magic behind"""
    def __init__(self, iface):
        print(iface)
        self.iface = iface
        self.gui = EnMAPBox_GUI()
        self.gui.showMaximized()
        self.gui.setAcceptDrops(True)
        self.gui.setWindowTitle('EnMAP-Box ' + VERSION)
        self.dataSourceManager = DataSourceManager()
        model = DataSourceManagerTreeModel(self.dataSourceManager)
        self.gui.dataSourceTreeView.setModel(model)


        self.gui.dataSourceTreeView.setDragEnabled(True)
        self.gui.dataSourceTreeView.setAcceptDrops(True)
        self.gui.dataSourceTreeView.viewport().setAcceptDrops(True)
        self.gui.dataSourceTreeView.setDropIndicatorShown(True)
        self.gui.dataSourceTreeView.customContextMenuRequested.connect(self.onDataSourceTreeViewCustomContextMenu)

        self.DOCKS = set()
        self.dockarea = DockArea()
        self.dockarea.sigDragEnterEvent.connect(self.dockAreaSignalHandler)
        self.dockarea.sigDragMoveEvent.connect(self.dockAreaSignalHandler)
        self.dockarea.sigDragLeaveEvent.connect(self.dockAreaSignalHandler)
        self.dockarea.sigDropEvent.connect(self.dockAreaSignalHandler)

        self.gui.centralWidget().layout().addWidget(self.dockarea)

        #link action objects to action behaviour
        #self.gui.actionAddView.triggered.connect(lambda: self.dockarea.addDock(EnMAPBoxDock(self)))
        self.gui.actionAddMapView.triggered.connect(lambda : self.createDock('MAP'))
        self.gui.actionAddTextView.triggered.connect(lambda: self.createDock('TEXT'))
        self.gui.actionAddDataSource.triggered.connect(lambda: self.addSource(str(QFileDialog.getOpenFileName(self.gui, "Open a data source"))))
        EnMAPBox._instance = self


    def dockAreaSignalHandler(self, event):
        M = MimeDataHelper(event.mimeData())
        if type(event) is QDragEnterEvent:
            # check mime types we can handle
            if M.hasUriList() or M.hasQgsLayerTree():
                event.setDropAction(Qt.CopyAction)
                event.accept()
            else:
                event.ignore()
        elif type(event) is QDragMoveEvent:
            pass
        elif type(event) is QDragLeaveEvent:
            pass
        elif type(event) is QDropEvent:

            addedSources = set()
            if M.hasQgsLayerTree():
                for id, name in M.getQgsLayerTreeLayers():
                    ds = DataSource.Factory(id, name=name)
                    if ds is not None:
                        addedSources.add(self.addSource(ds))

            elif M.hasUriList():
                for url in M.getUriList():
                    ds = self.addSource(url)
                    if ds is not None:
                        addedSources.add(self.addSource(ds))

            NEW_MAP_DOCK = None
            for ds in addedSources:
                if isinstance(ds, DataSourceSpatial):
                    if NEW_MAP_DOCK is None:
                        NEW_MAP_DOCK = self.createDock('MAP')
                    NEW_MAP_DOCK.addLayer(ds.createMapLayer())

            event.acceptProposedAction()
                #todo: handle non-spatial datasources


    def createDock(self, docktype,  *args, **kwds):
        #todo: ensure unique mapdock names

        assert docktype in ['MAP','TEXT']
        if docktype == 'MAP':
            dock = MapDock(self, *args, **kwds)
        elif docktype == 'TEXT':
            dock = TextDock(self, *args, **kwds)

        existing = self.dockarea.findAll()
        self.dockarea.addDock(dock,*args, **kwds)

        self.DOCKS.add(dock)
        return dock
        #dock.sigClosed.connect(lambda : self.removeDock(dock))

    #def removeDock(self, dock):
        #self.DOCKS.remove(dock)

    def isLinkedWithQGIS(self):
        return self.iface is not None and isinstance(self.iface, qgis.gui.QgisInterface)

    def addSource(self, source, name=None):
        return self.dataSourceManager.addSource(source, name=name)



    def getURIList(self, *args, **kwds):
        return self.dataSourceManager.getURIList(*args, **kwds)

    @staticmethod
    def getIcon():
        return getQIcon()

    def run(self):
        self.gui.show()
        pass


    def onDataSourceTreeViewCustomContextMenu(self, point):
        tv = self.gui.dataSourceTreeView
        assert isinstance(tv, QTreeView)
        index = tv.indexAt(point)


        model = tv.model()
        if index.isValid():
            itemData = model.data(index, Qt.UserRole)

            if itemData:
                menu = QMenu()
                if isinstance(itemData, DataSource):
                    if isinstance(itemData, DataSourceSpatial):
                        mapDocks = [d for d in self.DOCKS if isinstance(d, MapDock)]
                        mapDocks = sorted(mapDocks, key=lambda d:d.name())
                        if len(mapDocks) > 0:
                            subMenu = QMenu()
                            subMenu.setTitle('Add to Map...')
                            for mapDock in mapDocks:
                                action = QAction('"{}"'.format(mapDock.name()), menu)
                                action.triggered.connect(lambda : mapDock.addLayer(itemData.getMapLayer()))
                                subMenu.addAction(action)
                            menu.addMenu(subMenu)
                        action = QAction('Add to new map', menu)
                        action.triggered.connect(lambda : self.createDock('MAP', initSrc=itemData))
                        menu.addAction(action)
                    action = QAction('Remove', menu)
                    action.triggered.connect(lambda : self.dataSourceManager.removeSource(itemData))
                else:
                    action = QAction('Copy', menu)
                    action.triggered.connect(lambda: QApplication.clipboard().setText(str(itemData)))
                menu.addAction(action)
                menu.exec_(tv.viewport().mapToGlobal(point))




        s = ""





class TestData():

    prefix = jp(os.path.normpath(DIR), *['testdata'])
    assert os.path.exists(prefix)
    RFC_Model = jp(prefix, 'rfc.model')

    prefix = jp(os.path.normpath(DIR), *['testdata', 'AlpineForeland'])
    assert os.path.exists(prefix)
    #assert os.path.isdir(prefix)

    AF_Image = jp(prefix, 'AF_Image.bip')
    AF_LAI = jp(prefix, r'AF_LAI.bsq')
    AF_LC = jp(prefix, r'AF_LC.bsq')
    AF_Mask = jp(prefix, r'AF_Mask.bsq')
    AF_MaskVegetation = jp(prefix, r'AF_MaskVegetation.bsq')




def create_qgis_instance():
    pass


if __name__ == '__main__':

    #start a QGIS instance



    from qgis.gui import *
    from qgis.core import *
    if sys.platform == 'darwin':
        PATH_QGS = r'/Applications/QGIS.app/Contents/MacOS'
        os.environ['GDAL_DATA'] = r'/usr/local/Cellar/gdal/1.11.3_1/share'

    else:
        #assume OSGeo4W startup
        PATH_QGS = os.environ['QGIS_PREFIX_PATH']
    assert os.path.exists(PATH_QGS)
    qgsApp = QgsApplication([], True)
    QApplication.addLibraryPath(r'/Applications/QGIS.app/Contents/PlugIns')
    QApplication.addLibraryPath(r'/Applications/QGIS.app/Contents/PlugIns/qgis')

    if True:
        #register new model
        path = r'C:\foo\bar.model'
        import enmapbox.processing
        enmapbox.processing.registerModel(path, 'MyModel')
        #IconProvider.test()
        #exit()

    qgsApp.setPrefixPath(PATH_QGS, True)
    qgsApp.initQgis()

    if False:
        w = QMainWindow()
        w.setWindowTitle('QgsMapCanvas Example')

        w.setLayout(QtGui.QGridLayout())
        w.layout().addWidget(CanvasLinkTargetWidget(None, None, parent=w))
        w.show()

    qgsReg = qgis.core.QgsMapLayerRegistry.instance()
    # add example images





   # EB = EnMAPBox(w)
    EB = EnMAPBox(None)
    #EB.dockarea.addDock(EnMAPBoxDock(EB, name='Dock (unspecialized)'))
    if True:
        EB.createDock('MAP', name='MapDock 1', initSrc=TestData.AF_Image)
        EB.createDock('MAP', name='MapDock 2', initSrc=TestData.AF_LAI)
        EB.createDock('MAP', name='MapDock 4', initSrc=TestData.AF_LC)
        #EB.createDock('MAP', name='MapDock 3', initSrc=TestData.Landsat_Shp)
        if False:
            EB.createDock('TEXT', name='TextDock',
                                                 html='Here we can show HTML like text:'
                                                      '<a href="http://www.enmap.org">www.enmap.org</a>'
                                                      '</br>'+LORE_IPSUM)

        if True:
            # register new model
            path = TestData.RFC_Model
            import enmapbox.processing
            enmapbox.processing.registerModel(path, 'MyModel')
            # IconProvider.test()
            # exit()

    #md1.linkWithMapDock(md2, linktype='center')
    #EB.show()
    #EB.addSource(r'C:\Users\geo_beja\Repositories\enmap-box_svn\trunk\enmapProject\enmapBox\resource\testData\image\AF_Mask')
    #EB.addSource(r'C:\Users\geo_beja\Repositories\enmap-box_svn\trunk\enmapProject\enmapBox\resource\testData\image\AF_LAI')
    #EB.addSource(
    #   r'C:\Users\geo_beja\Repositories\enmap-box_svn\trunk\enmapProject\enmapBox\resource\testData\image\AF_LC')
    EB.run()


    qgsApp.exec_()

    qgsApp.exitQgis()

    # qgsApp.exitQgis()
    # app.exec_()
    pass

    #load the plugin
    print('Done')

