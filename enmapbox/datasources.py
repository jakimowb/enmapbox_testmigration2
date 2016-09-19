import six, sys, os, gc, re, collections
#from qgis.gui import *
#from qgis.core import *

from PyQt4.QtCore import *
from PyQt4 import QtGui, QtCore, uic
from qgis.core import *
from qgis.gui import *

from osgeo import gdal, ogr
from enmapbox import TreeItem, EnMAPBoxIcons

class DataSource(object):
    """Base class to describe file/stream/IO sources as used in EnMAP-GUI context"""

    @staticmethod
    def isVectorSource(src):
        """
        Returns the sourc uri if it can be handled as known vector data source.
        :param src: any type
        :return: uri (str) | None
        """
        if isinstance(src, QgsVectorLayer) and src.isValid():
            return DataSource.isVectorSource(src.dataProvider())
        if isinstance(src, QgsVectorDataProvider):
            return src.dataSourceUri()
        if isinstance(src, ogr.DataSource):
            return src.GetName()
        if isinstance(src, QUrl):
            if src.isLocalFile():
                src = str(src.toLocalFile())
            else:
                src = str(src.path())
        if isinstance(src, str):
            #todo: check different providers, not only ogr
            result = None
            try:
                result = DataSource.isVectorSource(ogr.Open(src))
            except:
                pass

            return result

        return None

    @staticmethod
    def isRasterSource(src):
        """
        Returns the sourc uri if it can be handled as known raster data source.
        :param src: any type
        :return: uri (str) | None
        """
        gdal.UseExceptions()
        if isinstance(src, QgsRasterLayer) and src.isValid():
            return DataSource.isRasterSource(src.dataProvider())
        if isinstance(src, QgsRasterDataProvider):
            return src.dataSourceUri()
        if isinstance(src, gdal.Dataset):
            return src.GetFileList()[0]
        if isinstance(src, QUrl):
            if src.isLocalFile():
                src = str(src.toLocalFile())
            else:
                src = str(src.path())
        if isinstance(src, str):
            # todo: check different providers, not only gdal
            result = None
            try:
                result = DataSource.isRasterSource(gdal.Open(src))
                s= ""
            except RuntimeError, e:
                pass

            return result

        return None

    @staticmethod
    def isEnMAPBoxModel(src):
        """
        Returns the sourc uri if it can be handled as known raster data source.
        :param src: any type
        :return: uri (str) | None
        """
        #todo: implement checks to test for model
        return None

    @staticmethod
    def Factory(src, name=None, icon=None):
        """
        Factory method / switch to return the best suited DataSource Instance to an unknown source
        :param source: anything
        :param name: name, optional
        :param icon: QIcon, optional
        :return:
        """
        if isinstance(src, DataSource): return src

        uri = DataSource.isRasterSource(src)
        if uri is not None:
            return DataSourceRaster(uri, name=name, icon=icon)
        uri = DataSource.isVectorSource(src)
        if uri is not None:
            return DataSourceVector(uri, name=name, icon=icon)

        uri = DataSource.isEnMAPBoxModel(src)
        if uri is not None:
            raise NotImplementedError()

        if isinstance(src, str) and os.path.isfile(src):
            return DataSourceFile(src, name=name, icon=icon)

        print('Can not open {}'.format(str(src)))
        return None

    def __init__(self, src, name=None, icon=None):
        """
        :param uri: uri of data source. must be a string
        :param name: name as it appears in the source file list
        """
        assert type(src) is str
        if icon is None:
            icon = QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_FileIcon)
        if name is None:
            name = os.path.basename(src)
        assert name is not None
        assert type(icon) is QtGui.QIcon

        self.src = src
        self.icon = icon
        self.name = name

    def __eq__(self, other):
        return self.src == other.src

    def getUri(self):
        """Returns the URI string that describes the data source"""
        return self.src

    def getIcon(self):
        """
        Returns the icon associated with the data source
        :return: QIcon
        """
        return self.icon


    def getTreeItem(self, parentItem):
        """
        Returns a TreeItem to be used in TreeViews
        :param parentItem:
        :return:
        """
        return TreeItem(parentItem, self.name,
                        data=self,
                        icon=self.getIcon(),
                        tooltip = str(self),
                        description=None, asChild=False)

    def __repr__(self):
        return 'DataSource: {} {}'.format(self.name, str(self.src))

class DataSourceFile(DataSource):

    def __init__(self, uri, name=None, icon=None):
        super(DataSourceFile, self).__init__(uri, name, icon)

    def getTreeItem(self, parent):
        itemTop = super(DataSourceFile, self).getTreeItem(parent)
        infos = list()
        infos.append('Path: {}'.format(self.src))
        infos.append('Size: {}'.format(os.path.getsize(self.src)))
        TreeItem(itemTop, 'File Information', infos=infos, tooltip='\n'.join(infos), asChild=True)
        return itemTop

class DataSourceSpatial(DataSource):
    """
    Abstract class to be implemented by inherited DataSource that support spatial data
    """
    def __init__(self, uri, name=None, icon=None ):
        super(DataSourceSpatial, self).__init__(uri, name, icon)

        self._refLayer = self._createMapLayer()
        assert isinstance(self._refLayer, QgsMapLayer) and self._refLayer.isValid()
        self.mapLayers = list()

    def _createMapLayer(self, *args, **kwds):
        """
        creates and returns a QgsMapLayer from self.src
        :return:
        """
        raise NotImplementedError()


    def getMapLayer(self, *args, **kwds):
        """
        Returns a new map layer of this data source
        :return:
        """
        ml = self._createMapLayer(*args, **kwds)
        #qgis.core.QgsMapLayerRegistry.instance().addMapLayer(ml, False)
        self.mapLayers.append(ml)
        return ml







class DataSourceRaster(DataSourceSpatial):

    def __init__(self, uri, name=None, icon=None ):
        super(DataSourceRaster, self).__init__(uri, name, icon)

        self._refLayer = self._createMapLayer(self.src)
        dp = self._refLayer.dataProvider()

        #change icon
        if dp.bandCount() == 1:
            dt = dp.dataType(1)
            cat_types = [QGis.CInt16, QGis.CInt32, QGis.Byte, QGis.UInt16, QGis.UInt32, QGis.Int16, QGis.Int32]
            if dt in cat_types:
                if len(dp.colorTable(1)) != 0:
                    self.icon = QtGui.QIcon(EnMAPBoxIcons.File_RasterClassification)
                else:
                    self.icon = QtGui.QIcon(EnMAPBoxIcons.File_RasterMask)
            elif dt in [QGis.Float32, QGis.Float64, QGis.CFloat32, QGis.CFloat64]:
                self.icon = QtGui.QIcon(EnMAPBoxIcons.File_RasterRegression)
        else:
            self.icon = QtGui.QIcon(EnMAPBoxIcons.File_Raster)

    def _createMapLayer(self, *args, **kwargs):
        """
        creates and returns a QgsRasterLayer from self.src
        :return:
        """
        return QgsRasterLayer(self.src, *args, **kwargs)


    def getTreeItem(self, parent):
        itemTop = super(DataSourceRaster, self).getTreeItem(parent)


        dp = self._refLayer.dataProvider()
        crs = self._refLayer.crs()

        infos = list()
        infos.append('URI: {}'.format(dp.dataSourceUri()))
        infos.append('DIMS: {}x{}x{}'.format(dp.xSize(), dp.ySize(), dp.bandCount()))
        TreeItem(itemTop, 'File Information', infos=infos, tooltip='\n'.join(infos), asChild=True)

        #define actions related to top icon


        if crs is not None:
            infos = list()
            infos.append('CRS: {}'.format(crs.description()))

            infos.append('Extent: {}'.format(dp.extent().toString(True)))
            TreeItem(itemTop, 'Spatial Reference', infos=infos, asChild=True, tooltip='\n'.join(infos))


        itemBands = TreeItem(itemTop, 'Bands [{}]'.format(dp.bandCount()), asChild=True)

        bandnames = [self._refLayer.bandName(b+1) for b in range(self._refLayer.bandCount())]
        if dp.name() == 'gdal':
            ds = gdal.Open(dp.dataSourceUri())
            for b in range(ds.RasterCount):
                bandnames[b] = '{} "{}"'.format(bandnames[b], ds.GetRasterBand(b+1).GetDescription())

        for b in range(dp.bandCount()):
            infos=list()
            nodata = None
            if dp.srcHasNoDataValue(b+1):
                nodata = dp.srcNoDataValue(b+1)
            infos.append('No data : {}'.format(nodata))
            TreeItem(itemBands, bandnames[b], tooltip = '\n'.join(infos), infos=infos, asChild=True)
        return itemTop

class DataSourceVector(DataSourceSpatial):


    def __init__(self, uri,  name=None, icon=None ):
        super(DataSourceVector, self).__init__(uri, name, icon)

        dp = self._refLayer.dataProvider()
        assert isinstance(dp, QgsVectorDataProvider)

        geomType = self._refLayer.geometryType()
        if geomType in [QGis.WKBPoint, QGis.WKBPoint25D]:
            self.icon = QtGui.QIcon(EnMAPBoxIcons.File_Vector_Point)
        elif geomType in [QGis.WKBLineString, QGis.WKBMultiLineString25D]:
            self.icon = QtGui.QIcon(EnMAPBoxIcons.File_Vector_Polygon)
        elif geomType in [QGis.WKBPolygon, QGis.WKBPoint25D]:
            self.icon = QtGui.QIcon(EnMAPBoxIcons.File_Vector_Polygon)

    def _createMapLayer(self, *args, **kwargs):
        """
        creates and returns a QgsVectorLayer from self.src
        :return:
        """
        if len(args) == 0 and len(kwargs) == 0:
            return QgsVectorLayer(self.src, None, 'ogr')
        else:
            return QgsVectorLayer(self.src, **kwargs)

    def getTreeItem(self, parent):
        itemTop = super(DataSourceVector, self).getTreeItem(parent)

        #itemTop = TreeItem(parent, self.name, icon=self.getIcon())
        assert type(self._refLayer) is QgsVectorLayer
        srs = self._refLayer.crs()
        dp = self._refLayer.dataProvider()
        assert isinstance(dp, QgsVectorDataProvider)

        infos = list()
        infos.append('Path: {}'.format(self.src))
        infos.append('Features: {}'.format(dp.featureCount()))

        TreeItem(itemTop, 'File Information', infos=infos,
                 tooltip='\n'.join(infos), asChild=True)

        if srs is not None:
            infos = list()
            infos.append('CRS: {}'.format(srs.description()))
            infos.append('Extent: {}'.format(dp.extent().toString(True)))
            TreeItem(itemTop, 'Spatial Reference', infos=infos, asChild=True,
                     tooltip='\n'.join(infos))

        fields = self._refLayer.fields()
        itemFields = TreeItem(itemTop, 'Fields [{}]'.format(len(fields)), asChild=True)
        for i, field in enumerate(fields):
            infos = list()
            infos.append('Name : {}'.format(field.name()))
            infos.append('Type : {}'.format(field.typeName()))
            TreeItem(itemFields, '{} "{}" {}'.format(i+1, field.name(), field.typeName()),
                     tooltip='\n'.join(infos), infos=infos, asChild=True)

        return itemTop

class DataSourceManager(QObject):
    """
    Keeps overview on different data sources handled by EnMAP-Box.
    Similar like QGIS data registry, but manages non-spatial data sources (text files etc.) as well
    """

    sigDataSourceAdded = pyqtSignal(object)
    sigDataSourceRemoved = pyqtSignal(object)

    def __init__(self):
        QObject.__init__(self)
        self.sources = set()
        self.qgsMapRegistry = QgsMapLayerRegistry.instance()
        self.updateFromQgsMapLayerRegistry()


    def updateFromQgsMapLayerRegistry(self):
        """
        Add data sources registered in the QgsMapLayerRegistry to the data source manager
        :return: True, if a new source was added
        """
        r = False
        existing_src = [ds.src for ds in self.sources if isinstance(ds, DataSourceSpatial)]
        for lyr in self.qgsMapRegistry.mapLayers().values():
            src = lyr.dataProvider().dataSourceUri()
            if src not in existing_src:
                r =  r or (self.addSource(ds) is not None)
        return r


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
            self.sources.add(ds)
            self.sigDataSourceAdded.emit(ds)

        return ds

    def removeSource(self, src):
        assert isinstance(src, DataSource)
        self.sources.remove(src)
        self.sigDataSourceRemoved.emit(src)


    def getSourceTypes(self):
        return sorted(list(set([type(ds) for ds in self.sources])))




class DataSourceManagerTreeModel(QAbstractItemModel):

    """
    See http://doc.qt.io/qt-5/qtwidgets-itemviews-simpletreemodel-example.html
    """
    columnames = ['Name','Description']
    columnames = ['Name']

    SourceTypes = [DataSourceRaster, DataSourceVector, DataSourceFile]
    SourceTypeNames = ['Raster', 'Vector', 'File']


    def getSourceTypeName(self, dataSource):
        assert type(dataSource) in DataSourceManagerTreeModel.SourceTypes
        return DataSourceManagerTreeModel.SourceTypeNames[DataSourceManagerTreeModel.SourceTypes.index(type(dataSource))]

    def __init__(self, dataSourceManager):
        assert isinstance(dataSourceManager, DataSourceManager)
        QAbstractItemModel.__init__(self)
        self.DSM = dataSourceManager
        self.DSM.sigDataSourceAdded.connect(self.addDataSourceItems)
        self.DSM.sigDataSourceRemoved.connect(self.removeDataSourceItems)
        self.rootItem = TreeItem(None, None)



    def addDataSourceItems(self, dataSource):
        assert isinstance(dataSource, DataSource)
        dsTypeName = self.getSourceTypeName(dataSource)
        if dsTypeName not in [c.name for c in self.rootItem.childs]:
            src_grp = TreeItem(self.rootItem,dsTypeName,
                               icon=QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_DirOpenIcon)
                               )
            self.rootItem.appendChild(src_grp)



        src_grp = [c for c in self.rootItem.childs if c.name == dsTypeName][0]
        src_grp.appendChild(dataSource.getTreeItem(src_grp))


        #print(src_grp)
    def removeDataSourceItems(self, dataSource):
        assert isinstance(dataSource, DataSource)
        dsTypeName = self.getSourceTypeName(dataSource)
        src_grp = [c for c in self.rootItem.childs if c.name == dsTypeName]
        if len(src_grp) == 1:
            src_grp = src_grp[0]
            assert isinstance(src_grp, TreeItem)

            for row in range(src_grp.childCount()):
                index = self.index(row, 1, None)
                child = src_grp.childs[row]
                if child.data == dataSource:
                    self.beginRemoveRows(index, 1, 1)
                    src_grp.childs.remove(c)
                    del c
                    self.endRemoveRows()

            if src_grp.childCount() == 0:
                #self.rootItem.childs.remove(src_grp)
                s = ""



    def supportedDragActions(self):
        return Qt.CopyAction | Qt.MoveAction

    def supportedDropActions(self):
        return Qt.CopyAction | Qt.MoveAction



    def dropMimeData(self, mimeData, Qt_DropAction, row, column, parent):

        s = ""

    def mimeData(self, list_of_QModelIndex):
        s = ""
        mimeData = QMimeData()
        #todo:
        return mimeData
    #read only access functions
    """
    Used by other components to obtain information about each item provided by the model.
    In many models, the combination of flags should include Qt::ItemIsEnabled and Qt::ItemIsSelectable.
    """
    def flags(self, index):
        default = super(DataSourceManagerTreeModel, self).flags(index)
        if index.isValid():
            return Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled | default
        else:
            return default



    """
    Used to supply item data to views and delegates. Generally, models only need to supply data for
    Qt::DisplayRole and any application-specific user roles, but it is also good practice to provide
    data for Qt::ToolTipRole, Qt::AccessibleTextRole, and Qt::AccessibleDescriptionRole.
    See the Qt::ItemDataRole enum documentation for information about the types associated with each role.
    """
    def data(self, index, role=None):

        if not index.isValid():
            return None;

        item = index.internalPointer()
        columnname = self.columnames[index.column()].lower()

        if role == Qt.DisplayRole:
            #return index.internalPointer().info(index.column())
            for attr in item.__dict__.keys():
                if attr.lower() == columnname:
                    value = item.__dict__[attr]
                    if value is not None:
                        return '{}'.format(value)
                    else:
                        return None
            return None
        if role == Qt.ToolTipRole:
            tt = item.tooltip
            if tt is None:
                tt = item.description
            return tt
        if role == Qt.DecorationRole and index.column() == 0:
            if isinstance(item.icon, QtGui.QIcon):
                return item.icon
        if role == Qt.UserRole:
            return item
        return None

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

    """
    Provides the number of rows of data exposed by the model.
    """
    def rowCount(self, parent=None, *args, **kwargs):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            #return len(set([ds.type for ds in self.DSM.sources]))

            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()
        #print((parentItem, parentItem.childCount()))
        return parentItem.childCount()


    """
    Provides the number of columns of data exposed by the model.
    """
    def columnCount(self, parent):
        return len(self.columnames)

        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.rootItem.columnCount()

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
    def setData(self, QModelIndex, QVariant, int_role=None):
        s = ""
        pass

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
        if not parent.isValid():
            return self.rootItem.childCount() > 0
        else:
            item = parent.internalPointer()

            return item.childCount() > 0
        pass



    #parents and childrens



    """
    Given a model index for a parent item, this function allows views and delegates to access children of that item.
    If no valid child item - corresponding to the specified row, column, and parent model index, can be found,
    the function must return QModelIndex(), which is an invalid model index.
    """
    def index(self, row, column, parent):

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
    Provides a model index corresponding to the parent of any given child item. If the model index specified
    corresponds to a top-level item in the model, or if there is no valid parent item in the model,
    the function must return an invalid model index, created with the empty QModelIndex() constructor.
    """
    def parent(self, index):

        if not index.isValid():
            return QModelIndex()
        else:
            childItem = index.internalPointer()
            parentItem = childItem.parent
        if parentItem == self.rootItem:
            return QModelIndex()
        return self.createIndex(parentItem.row(), 0, parentItem)

