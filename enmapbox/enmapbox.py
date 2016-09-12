
import six, sys, os, gc, re
#from qgis.gui import *
#from qgis.core import *
import qgis.core
import qgis.gui
from PyQt4 import *
from PyQt4.QtGui import *
from osgeo import gdal, ogr


VERSION = '2016-0.beta'


def add_to_sys_path(path):
    assert os.path.isdir(path)
    if path not in sys.path:
        sys.path.append(path)
        pass

jp = os.path.join

DIR = os.path.dirname(__file__)
import gui
DIR_GUI = jp(DIR,'gui')
add_to_sys_path(DIR_GUI)
#add_to_sys_path(jp(DIR, 'libs'))

LORE_IPSUM = r"Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet."

if six.PY3:
    rc_suffix = '_py3'
    #import gui.resources_py3
else:
    rc_suffix = '_py2'
    #import gui.resources_py2

#todo: reduce imports to minimum
#from PyQt4.Qt import *
import PyQt4
try:
    import pyqtgraph
    import pyqtgraph.dockarea.DockArea
    import pyqtgraph.dockarea.Dock
    from pyqtgraph.widgets.VerticalLabel import VerticalLabel
except:
    import libs.pyqtgraph as pyqtgraph

    import libs.pyqtgraph.dockarea.DockArea
    import libs.pyqtgraph.dockarea.Dock
    from libs.pyqtgraph.widgets.VerticalLabel import VerticalLabel




from PyQt4.QtCore import *
from PyQt4 import QtGui, QtCore, uic

ENMAPBOX_GUI_UI, _ = uic.loadUiType(jp(DIR_GUI, 'enmapbox_gui.ui'),
                                    from_imports=False, resource_suffix=rc_suffix)


class EnMAPBoxIcons:
    """
    Stores icons resource paths
    """
    Logo = ':/enmapbox/icons/enmapbox.png'
    Map_Link = ':/enmapbox/icons/link_basic.svg'
    Map_Link_Center = ':/enmapbox/icons/link_center.svg'
    Map_Link_Extent = ':/enmapbox/icons/link_mapextent.svg'
    Map_Link_Scale = ':/enmapbox/icons/link_mapextent.svg'
    Map_Link_Scale_Center = ':/enmapbox/icons/link_mapextent.svg'
    Map_Zoom_In = ':/enmapbox/icons/mActionZoomOut.svg'
    Map_Zoom_Out = ':/enmapbox/icons/mActionZoomIn.svg'
    Map_Pan = ''
    File_RasterMask = ':/enmapbox/icons/filelist_mask.svg'
    File_RasterRegression = ':/enmapbox/icons/filelist_regression.svg'
    File_RasterClassification = ':/enmapbox/icons/filelist_classification.svg'
    File_Raster = ':/enmapbox/icons/filelist_image.svg'
    File_Vector_Point = ''
    File_Vector_Line = ''
    File_Vector_Polygon = ''





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


class TreeItem(QObject):
    def __init__(self, parent, name, data=None, icon=None, description=None,
                 infos=None, tooltip=None, tag=None, asChild=False):
        super(TreeItem, self).__init__()
        self.parent = parent
        self.name = name
        self.childs = list()
        self.data = data
        self.icon = icon
        self.description = description
        self.tooltip = tooltip
        if infos:
            self.addInfos(infos)

        if asChild and parent is not None:
            parent.appendChild(self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for child in self.childs:
            del child

    def addInfos(self, infolist):
        if not isinstance(infolist, list):
            infolist = list(infolist)
        for line in infolist:
            item = TreeItem(self, line, tooltip=line)
            self.appendChild(item)


    def parent(self):
        return self.parent

    def child(self, row):
        if row > len(self.childs) - 1:
            return None
        return self.childs[row]

    def childNumber(self):
        if self.parent:
            return self.parent.childs.index(self)
        return 0

    def appendChild(self, child):
        assert isinstance(child, TreeItem)
        self.childs.append(child)

    def insertChildren(self, position, count, columns):
        if position < 0 or position > len(self.childs):
            return False

        for r in range(count):
            self.childs.insert(r, TreeItem(self, 'empty'))



    def row(self):
        if self.parent != None:
            return self.parent.childs.index(self)
        return 0

    def childCount(self):
        return len(self.childs)

    def columnCount(self):
        return len(self.infos)


    def data(self, column):
        return self.infos[column]


class DataSource(object):
    """Base class to describe file/stream/IO sources in EnMAP-GUI context"""

    @staticmethod
    def Factory(src, name=None, icon=None):
        """
        Factory method / switch to return the best suited DataSource Instance to an unknown source
        :param source: anything
        :param name: name, optional
        :param icon: QIcon, optional
        :return:
        """

        reg = QgsMapLayerRegistry.instance()
        for x in reg.mapLayers():
            print(x)

        ds = None
        # 1. check string types
        if isinstance(src, str):
            if os.path.exists(src):
                # 1. test mapable sources

                lyr = qgis.core.QgsRasterLayer(src, name, 'gdal')
                if lyr.isValid():
                    return DataSource.Factory(lyr, name=name, icon=icon)

                lyr = qgis.core.QgsVectorLayer(src, name, 'ogr')
                if lyr.isValid():
                    return DataSource.Factory(lyr, name=name, icon=icon)

                #check model files
                if re.search('\.model$', src):
                    s = ""
                    pass

                #Any other file
                return DataSourceFile(src, name=name, icon=icon)

        # check QGIS data sources
        if isinstance(src, qgis.core.QgsRasterLayer):
            ds = DataSourceRaster(str(src.dataProvider().dataSourceUri()), name=name, icon=icon)
        elif isinstance(src, qgis.core.QgsRasterDataProvider):
            ds = DataSourceRaster(str(src.dataSourceUri()), name=name, icon=icon)
        elif isinstance(src, qgis.core.QgsVectorLayer):
            ds = DataSourceVector(str(src.dataProvider().dataSourceUri()), name=name, icon=icon)
        elif isinstance(src, DataSource):
            ds = src
        else:
            # todo: add GDAL dataset object
            # todo: add QFileObjects
            raise NotImplementedError

        return ds

    def __init__(self, src, name, icon):
        """
        :param uri: uri of data source
        :param uri: the source itself.
        :param name: name as it appears in the source file list
        """
        assert type(src) is str
        if icon is None:
            icon = QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_FileIcon)
        if name is None:
            name = os.path.basename(src)
        assert name is not None
        assert type(icon) is QIcon

        self.src = src
        self.icon = icon
        self.name = name

    def getUri(self):
        return self.src

    def getIcon(self):
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
    def __init__(self, uri, name=None, icon=None ):
        super(DataSourceSpatial, self).__init__(uri, name, icon)
        self.lyr = None

    def getLayer(self):

        return self.lyr



class DataSourceRaster(DataSourceSpatial):

    def __init__(self, uri, name=None, icon=None ):
        super(DataSourceSpatial, self).__init__(uri, name, icon)
        lyr = QgsRasterLayer(self.src, self.name)
        assert lyr.isValid()
        self.lyr = lyr

        QgsMapLayerRegistry.instance().addMapLayer(self.lyr)

        dp = self.lyr.dataProvider()

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


    def getTreeItem(self, parent):
        itemTop = super(DataSourceRaster, self).getTreeItem(parent)


        dp = self.lyr.dataProvider()
        crs = self.lyr.crs()

        infos = list()
        infos.append('URI: {}'.format(dp.dataSourceUri()))
        infos.append('DIMS: {}x{}x{}'.format(dp.xSize(), dp.ySize(), dp.bandCount()))
        TreeItem(itemTop, 'File Information', infos=infos, tooltip='\n'.join(infos), asChild=True)

        if crs is not None:
            infos = list()
            infos.append('CRS: {}'.format(crs.description()))

            infos.append('Extent: {}'.format(dp.extent().toString(True)))
            TreeItem(itemTop, 'Spatial Reference', infos=infos, asChild=True, tooltip='\n'.join(infos))


        itemBands = TreeItem(itemTop, 'Bands [{}]'.format(dp.bandCount()), asChild=True)

        bandnames = [self.lyr.bandName(b+1) for b in range(self.lyr.bandCount())]
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


        lyr = QgsVectorLayer(uri, None, 'ogr')
        self.lyr = lyr

        dp = self.lyr.dataProvider()
        assert isinstance(dp, qgis.core.QgsVectorDataProvider)

        geomType = self.lyr.geometryType()
        if geomType in [QGis.WKBPoint, QGis.WKBPoint25D]:
            self.icon = QtGui.QIcon(EnMAPBoxIcons.File_Vector_Point)
        elif geomType in [QGis.WKBLineString, QGis.WKBMultiLineString25D]:
            self.icon = QtGui.QIcon(EnMAPBoxIcons.File_Vector_Polygon)
        elif geomType in [QGis.WKBPolygon, QGis.WKBPoint25D]:
            self.icon = QtGui.QIcon(EnMAPBoxIcons.File_Vector_Polygon)


    def getTreeItem(self, parent):
        itemTop = super(DataSourceVector, self).getTreeItem(parent)

        #itemTop = TreeItem(parent, self.name, icon=self.getIcon())
        assert type(self.lyr) is qgis.core.QgsVectorLayer
        srs = self.lyr.crs()
        dp = self.lyr.dataProvider()
        assert isinstance(dp, qgis.core.QgsVectorDataProvider)

        infos = list()
        infos.append('Path: {}'.format(self.src))
        infos.append('Features: {}'.format(dp.featureCount()))

        TreeItem(itemTop, 'File Information', infos=infos, tooltip='\n'.join(infos), asChild=True)

        if srs is not None:
            infos = list()
            infos.append('CRS: {}'.format(srs.description()))
            infos.append('Extent: {}'.format(dp.extent().toString(True)))
            TreeItem(itemTop, 'Spatial Reference', infos=infos, asChild=True,
                     tooltip='\n'.join(infos))

        fields = self.lyr.fields()
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
        self.sources = list()
        self.qgsMapRegistry = qgis.core.QgsMapLayerRegistry.instance()
        self.qgsMapRegistry.layersRemoved.connect(self.removeQgisLayers)
        self.updateQgsMapLayers()


    def updateQgsMapLayers(self):

        existing_sources = [ds.source for ds in self.sources]
        for id in self.qgsMapRegistry.mapLayers():
            lyr = self.qgsMapRegistry.mapLayer(id)
            print(id)
            if lyr not in existing_sources:
                self.addSource(lyr, lyr.name())


    def removeQgisLayers(self, args):
        s  = ""


    def addSource(self, src, name=None, icon=None):
        #switch to add different data sources
        ds = DataSource.Factory(src, name=name, icon=icon)
        if isinstance(ds, DataSource):

            if ds is not None and ds not in self.sources:
                self.sources.append(ds)
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




def getQIcon(name=EnMAPBoxIcons.Logo):
    return QtGui.QIcon(name)



class CanvasLink(QObject):
    """
    Describes a bi-directional link between two QgsMapCanvas
    """
    #global list to store all links and avoid circular links
    LINKSETS = list() #sets of canvases linked by extent

    """
    if one canvas has changed:
        set all extents of canvases linked to = in same link group in LINK_EXTENTS
        set all centers of canvases linked to = in same link group in LINK_ZOOM

        a canvas can be either in a set of LINK_EXTENTS or LINK_CENTERS
        LINK_CENTERS allows for different zoom levels
        -> canvases can be linked by center
        Example: c = linked by center, e = linked by extent
        A c B
        B e D
        = linkset(e : {B,D})
        = linkset(c : {A,B})

          A B C D
        A
        B z
        C - e
        D e - z

    """
    LINKTYPES = ['center','extent','scale','scale_center']
    class linkset(set):
        def __init__(self, linktype):
            assert linktype in CanvasLink.LINKTYPES
            self.linktype = linktype

        def __add__(self, other):
            assert isinstance(other, qgis.gui.QgsMapCanvas)


    @staticmethod
    def CreateLink(canvas1, canvas2, linktype='extent', bidirectional=True):
        assert linktype in CanvasLink.LINKTYPES
        assert isinstance(canvas1, qgis.gui.QgsMapCanvas)
        assert isinstance(canvas1, qgis.gui.QgsMapCanvas)
        if canvas1 is canvas2:
            return None

        register2 = not CanvasLink.containsCanvas(canvas2)
        register1 = not CanvasLink.containsCanvas(canvas1)
        #remove canvas1 from existing sets, since it can follow only one other canvas
        for ls in [ls for ls in CanvasLink.LINKSETS if canvas1 in ls]:
            ls.remove(canvas1)


        ls = [ls for ls in CanvasLink.LINKSETS if ls.linktype==linktype and canvas2 in ls]
        assert len(ls) <= 1
        if len(ls) == 1:
            ls[0].add(canvas1)
        else:
            ls = CanvasLink.linkset(linktype)
            ls.add(canvas1)
            ls.add(canvas2)
            CanvasLink.LINKSETS.append(ls)

        # register events
        if register2:
            canvas2.extentsChanged.connect(lambda: CanvasLink.setLinks(canvas2))
        if register1:
            canvas1.extentsChanged.connect(lambda: CanvasLink.setLinks(canvas1))

    @staticmethod
    def containsCanvas(canvas):
        for ls in CanvasLink.LINKSETS:
            if canvas in ls:
                return True
        return False

    @staticmethod
    def setLinks(canvas):
        #find linked canvases
        assert isinstance(canvas, QgsMapCanvas)
        extents = canvas.extent()
        center = canvas.center()
        scale = canvas.scale()

        already_changed = set([canvas])

        def applyLinkset(ls, blocksignals=True):
            if canvas in ls:
                for c in [c for c in list(ls) if c not in already_changed]:
                    assert isinstance(c, QgsMapCanvas)
                    c.blockSignals(blocksignals)
                    if ls.linktype == 'extent':
                        c.setExtent(extents)
                    elif ls.linktype == 'center':
                        c.setCenter(center)
                    elif ls.linktype == 'scale':
                        c.zoomScale(scale)
                    elif ls.linktype == 'scale_center':
                        c.zoomScale(scale)
                        c.setCenter(center)
                    else:
                        raise NotImplementedError()
                    c.blockSignals(False)
                    already_changed.add(c)


        for ls in [ls for ls in CanvasLink.LINKSETS if ls.linktype == 'extent']:
            applyLinkset(ls, True)

        for ls in [ls for ls in CanvasLink.LINKSETS if ls.linktype == 'center']:
            applyLinkset(ls, True)

        for ls in [ls for ls in CanvasLink.LINKSETS if ls.linktype == 'scale']:
            applyLinkset(ls, True)

        for ls in [ls for ls in CanvasLink.LINKSETS if ls.linktype == 'scale_center']:
            applyLinkset(ls, True)

        s = ""

    @staticmethod
    def link_exists(canvas1, canvas2):
        # check circular reference
        linked1 = CanvasLink.get_linked_canvases(canvas1)
        linked2 = CanvasLink.get_linked_canvases(canvas2)

        return canvas2 in linked1 or canvas1 in linked2

    @staticmethod
    def get_linked_canvases(canvas):
        linked = set()
        linked.add(canvas)
        n = len(linked)
        changed = True
        if changed == True:
            for link in CanvasLink.LINK_SETS:
                if link.canvas1 in linked:
                    linked.add(link.canvas2)
                if link.canvas2 in linked:
                    linked.add(link.canvas1)
            changed = len(linked) > n
        linked.remove(canvas)
        return linked

    def setExtent(self, c1, c2):
        pass

    def panCenter(self, c1, c2):
        pass




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
        self.dockarea = EnMAPBoxDockArea()
        self.gui.centralWidget().layout().addWidget(self.dockarea)
        #self.gui.centralWidget().addWidget(self.dockarea)



        #link action objects to action behaviour
        #self.gui.actionAddView.triggered.connect(lambda: self.dockarea.addDock(EnMAPBoxDock(self)))
        self.gui.actionAddMapView.triggered.connect(lambda : self.createDock('MAP'))
        self.gui.actionAddTextView.triggered.connect(lambda: self.createDock('TEXT'))
        self.gui.actionAddDataSource.triggered.connect(lambda: self.addSource(str(QFileDialog.getOpenFileName(self.gui, "Open a data source"))))
        EnMAPBox._instance = self

    def createDock(self, docktype,  *args, **kwds):
        #todo: ensure unique mapdock names

        assert docktype in ['MAP','TEXT']
        if docktype == 'MAP':
            dock = EnMAPBoxMapDock(self,  *args, **kwds)
        elif docktype == 'TEXT':
            dock = EnMAPBoxTextDock(self,  *args, **kwds)

        self.dockarea.addDock(dock)
        self.DOCKS.add(dock)

        dock.sigClosed.connect(lambda : self.DOCKS.remove(dock))

    def isLinkedWithQGIS(self):
        return self.iface is not None and isinstance(self.iface, qgis.gui.QgisInterface)


    def addSource(self, source, name=None):
        self.dataSourceManager.addSource(source, name=name)

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


        m = tv.model()
        if index.isValid():

            node = m.data(index, Qt.UserRole)
            if isinstance(node.data, DataSource):
                src = node.data
                menu = QMenu()
                if isinstance(node.data, DataSourceSpatial):
                    mapDocks = [d for d in self.DOCKS if isinstance(d, EnMAPBoxMapDock)]
                    for mapDock in mapDocks:
                        action = QAction('Add to "{}"'.format(mapDock.name()), menu)
                        action.triggered.connect(lambda : mapDock.addLayer(src))
                        menu.addAction(action)
                    action = QAction('Add to new map', menu)
                    action.triggered.connect(lambda : self.createDock('MAP', initSrc=src))
                    menu.addAction(action)
                    action = QAction('Remove', menu)
                    action.triggered.connect(lambda : self.dataSourceManager.removeSource(src))

                menu.addAction(action)
                menu.exec_(tv.viewport().mapToGlobal(point))




        s = ""





class TestData():


    prefix = jp(DIR, 'testdata')
    #assert os.path.isdir(prefix)
    Image = jp(prefix, 'SF_20x20.tif')
    Diagrams = jp(prefix, 'diagrams.png')
    AlpineForelandSubset = jp(prefix, 'AlpineForelandSubset.img')
    AF_Image = jp(prefix, 'AF_Image')
    Landsat_Shp = jp(prefix, 'landsat_labels.shp')
    Landsat_Image = jp(prefix, 'landsat_img.tif')
    Landsat_Fmask = jp(prefix, 'landsat_fmask.tif')





class EnMAPBoxDockArea(pyqtgraph.dockarea.DockArea):

    def __init__(self, *args, **kwds):
        super(EnMAPBoxDockArea, self).__init__(*args, **kwds)

    def addDock(self, enmapboxdock, position='bottom', relativeTo=None, **kwds):
        assert enmapboxdock is not None
        assert isinstance(enmapboxdock, EnMAPBoxDock)
        return super(EnMAPBoxDockArea,self).addDock(dock=enmapboxdock, position=position, relativeTo=relativeTo, **kwds)


class EnMAPBoxDock(pyqtgraph.dockarea.Dock):
    '''
    Handle style sheets etc., basic stuff that differs from pyqtgraph dockarea
    '''


    def __init__(self, enmapbox, name='view', closable=True, *args, **kwds):
        super(EnMAPBoxDock, self).__init__(name=name, closable=False, *args, **kwds)

        assert isinstance(enmapbox, EnMAPBox)
        self.enmapbox = enmapbox


        self.title = name
        self.setStyleSheet('background:#FFF')

        #change the enmapbox-like things
        self.topLayout.removeWidget(self.label)
        del self.label


        self.label = self._getLabel()
        self.topLayout.addWidget(self.label, 0, 1)

        if closable:
            self.label.sigCloseClicked.connect(self.close)

        self.raiseOverlay()


        self.hStyle = """
        EnMAPBoxDock > QWidget {
            border: 1px solid #000;
            border-radius: 5px;
            border-top-left-radius: 0px;
            border-top-right-radius: 0px;
            border-top-width: 0px;
        }
        """
        self.vStyle = """
        EnMAPBoxDock > QWidget {
            border: 1px solid #000;
            border-radius: 5px;
            border-top-left-radius: 0px;
            border-bottom-left-radius: 0px;
            border-left-width: 0px;
        }
        """
        self.nStyle = """
        EnMAPBoxDock > QWidget {
            border: 1px solid #000;
            border-radius: 5px;
        }"""
        self.dragStyle = """
        EnMAPBoxDock > QWidget {
            border: 4px solid #00F;
            border-radius: 5px;
        }"""

        self.widgetArea.setStyleSheet(self.hStyle)
        self.topLayout.update()


        self.sigClosed.connect(lambda: self.enmapbox.DOCKS.remove(self))
        self.enmapbox.DOCKS.add(self)


    def _getLabel(self):
        """
        This functions returns the Label that is used to style the Dock
        :return:
        """
        return EnMAPBoxDockLabel(self)

    def append_hv_style(self, stylestr):
        obj_name = type(self).__name__
        style = ' \n{} {{\n{}\n}} '.format(obj_name, stylestr)
        self.hStyle += style
        self.vStyle += style


class EnMAPBoxDockLabel(VerticalLabel):
    sigClicked = QtCore.Signal(object, object)
    sigCloseClicked = QtCore.Signal()
    sigNormalClicked = QtCore.Signal()

    def __init__(self, dock, allow_floating=True):
        assert isinstance(dock, EnMAPBoxDock)
        self.dim = False
        self.fixedWidth = False
        self.dock = dock
        VerticalLabel.__init__(self, self.dock.title, orientation='horizontal', forceWidth=False)
        self.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        self.updateStyle()
        self.setAutoFillBackground(False)
        self.startedDrag = False
        self.buttons = list() #think from right to left
        self.pressPos = QtCore.QPoint()

        closeButton = QtGui.QToolButton(self)
        closeButton.clicked.connect(self.sigCloseClicked)
        closeButton.setToolTip('Close window')
        closeButton.setIcon(QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_TitleBarCloseButton))
        self.buttons.append(closeButton)

        if allow_floating:
            floatButton = QtGui.QToolButton(self)
            #testButton.clicked.connect(self.sigNormalClicked)
            floatButton.setToolTip('Float window')
            floatButton.clicked.connect(lambda : self.dock.float())
            floatButton.setIcon(QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_TitleBarNormalButton))
            self.buttons.append(floatButton)

    def updateStyle(self):
        r = '3px'
        if self.dim:
            fg = '#aaa'
            bg = '#44a'
            border = '#339'
        else:
            fg = '#fff'
            bg = '#66c'
            border = '#55B'

        if self.orientation == 'vertical':
            self.vStyle = """EnMAPBoxDockLabel {
                background-color : %s;
                color : %s;
                border-top-right-radius: 0px;
                border-top-left-radius: %s;
                border-bottom-right-radius: 0px;
                border-bottom-left-radius: %s;
                border-width: 0px;
                border-right: 2px solid %s;
                padding-top: 3px;
                padding-bottom: 3px;
            }""" % (bg, fg, r, r, border)
            self.setStyleSheet(self.vStyle)
        else:
            self.hStyle = """EnMAPBoxDockLabel {
                background-color : %s;
                color : %s;
                border-top-right-radius: %s;
                border-top-left-radius: %s;
                border-bottom-right-radius: 0px;
                border-bottom-left-radius: 0px;
                border-width: 0px;
                border-bottom: 2px solid %s;
                padding-left: 3px;
                padding-right: 3px;
            }""" % (bg, fg, r, r, border)
            self.setStyleSheet(self.hStyle)

    def setDim(self, d):
        if self.dim != d:
            self.dim = d
            self.updateStyle()

    def setOrientation(self, o):
        VerticalLabel.setOrientation(self, o)
        self.updateStyle()

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.pressPos = ev.pos()
            self.startedDrag = False
            ev.accept()

    def mouseMoveEvent(self, ev):
        if not self.startedDrag and (
            ev.pos() - self.pressPos).manhattanLength() > QtGui.QApplication.startDragDistance():
            self.dock.startDrag()
        ev.accept()

    def mouseReleaseEvent(self, ev):
        if not self.startedDrag:
            self.sigClicked.emit(self, ev)
        ev.accept()

    def mouseDoubleClickEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.dock.float()

    def resizeEvent(self, ev):
        if self.orientation == 'vertical':
            size = ev.size().width()
        else:
            size = ev.size().height()

        for i, btn in enumerate([b for b in self.buttons if not b.isHidden()]):
            if self.orientation == 'vertical':
                pos = QtCore.QPoint(0, i * size)
            else:
                pos = QtCore.QPoint(ev.size().width() - (i+1)*size, 0)
            btn.setFixedSize(QtCore.QSize(size, size))
            btn.move(pos)

        super(EnMAPBoxDockLabel, self).resizeEvent(ev)


class CanvasLinkTargetWidget(QtGui.QFrame):

    LINK_TARGET_WIDGETS = set()

    @staticmethod
    def ShowMapLinkTargets(canvas_targed):

        assert isinstance(canvas_targed, qgis.gui.QgsMapCanvas)
        CanvasLinkTargetWidget.RemoveMapLinkTargetWidgets(True)


        target_canvases = [c for c in gc.get_referrers(qgis.gui.QgsMapCanvas)
                           if isinstance(c, qgis.gui.QgsMapCanvas) and c is not canvas_targed]

        for canvas_source in target_canvases:

            w = CanvasLinkTargetWidget(canvas_targed, canvas_source)
            w.setAutoFillBackground(True)
            w.show()
            CanvasLinkTargetWidget.LINK_TARGET_WIDGETS.add(w)
            canvas_source.freeze()
            s = ""

        s = ""

    @staticmethod
    def linkMaps(maplinkwidget, linktype):

        CanvasLink.CreateLink(maplinkwidget.canvas1, maplinkwidget.canvas2, linktype)
        CanvasLinkTargetWidget.RemoveMapLinkTargetWidgets()

    @staticmethod
    def RemoveMapLinkTargetWidgets(processEvents=True):
        for w in list(CanvasLinkTargetWidget.LINK_TARGET_WIDGETS):
            CanvasLinkTargetWidget.LINK_TARGET_WIDGETS.remove(w)
            p = w.parent()
            w.hide()
            del(w)
            p.refresh()
            p.update()

        if processEvents:
            #qApp.processEvents()
            QCoreApplication.instance().processEvents()

    def __init__(self, canvas1, canvas2):
        assert isinstance(canvas1, qgis.gui.QgsMapCanvas)
        assert isinstance(canvas2, qgis.gui.QgsMapCanvas)

        QFrame.__init__(self, parent=canvas2)
        self.canvas1 = canvas1
        self.canvas2 = canvas2
        #self.canvas1.installEventFilter(self)
        self.canvas2.installEventFilter(self)
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.setCursor(Qt.ArrowCursor)

        ly = QHBoxLayout()
        #add buttons with link functions
        self.buttons = list()
        bt = QtGui.QToolButton(self)
        bt.setToolTip('Link map center')
        bt.clicked.connect(lambda: CanvasLinkTargetWidget.linkMaps(self, 'center'))
        bt.setIcon(getQIcon(EnMAPBoxIcons.Map_Link_Center))
        self.buttons.append(bt)

        if False:
            bt = QtGui.QToolButton(self)
            bt.setToolTip('Link map extent')
            bt.clicked.connect(lambda: CanvasLinkTargetWidget.linkMaps(self, 'extent'))
            bt.setIcon(getQIcon(EnMAPBoxIcons.Map_Link_Extent))
            self.buttons.append(bt)

        bt = QtGui.QToolButton(self)
        bt.setToolTip('Link map scale ("Zoom")')
        bt.clicked.connect(lambda: CanvasLinkTargetWidget.linkMaps(self, 'scale'))
        bt.setIcon(getQIcon(EnMAPBoxIcons.Map_Link_Scale))
        self.buttons.append(bt)

        bt = QtGui.QToolButton(self)
        bt.setToolTip('Link map scale and center')
        bt.clicked.connect(lambda: CanvasLinkTargetWidget.linkMaps(self, 'scale_center'))
        bt.setIcon(getQIcon(EnMAPBoxIcons.Map_Link_Scale_Center))
        self.buttons.append(bt)



        for bt in self.buttons:
            bt.setAttribute(Qt.WA_PaintOnScreen)
            #bt.setIconSize(QSize(100, 100))
            bt.setAutoRaise(True)
            ly.addWidget(bt)

        self.layout.addLayout(ly, 0,0)

        self.setStyleSheet('background-color:rgba(200, 200, 200, 180)')
        self.setAttribute(Qt.WA_PaintOnScreen)

        self.updatePosition()

    def updatePosition(self):
        if hasattr(self.parent(), 'viewport'):
            parentRect = self.parent().viewport().rect()

        else:
            parentRect = self.parent().rect()

        if not parentRect:
            return

        #get map center
        x = int(parentRect.width() / 2 - self.width() / 2)
        y = int(parentRect.height() / 2 - self.height() / 2)

        mw = int(min([self.width(),self.height()]) * 0.9)
        for bt in self.buttons:
            bt.setIconSize(QSize(mw, mw))

        #self.setGeometry(x, y, self.width(), self.height())
        self.setGeometry(parentRect)

    def setParent(self, parent):
        self.updatePosition()
        return super(CanvasLinkTargetWidget, self).setParent(parent)

    def resizeEvent(self, event):
        super(CanvasLinkTargetWidget, self).resizeEvent(event)
        self.updatePosition()

    def showEvent(self, event):
        self.updatePosition()
        return super(CanvasLinkTargetWidget, self).showEvent(event)

    def eventFilter(self, obj, event):

        if event.type() == QEvent.Resize:
            s  = ""
            self.updatePosition()
        return False

    def mousePressEvent(self, ev):

        if ev.button() == Qt.RightButton:
            #no choice, remove Widgets
            CanvasLinkTargetWidget.RemoveMapLinkTargetWidgets(True)
            ev.accept()


class EnMAPBoxMapDockLabel(EnMAPBoxDockLabel):

    def __init__(self, *args, **kwds):

        super(EnMAPBoxMapDockLabel, self).__init__(*args, **kwds)

        self.linkMap = QtGui.QToolButton(self)
        self.linkMap.setToolTip('Link with other map')
        #linkExtent.clicked.connect(lambda: self.dock.linkWithMapDock())
        #self.linkMap.setIcon(QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_CommandLink))
        self.linkMap.setIcon(getQIcon(EnMAPBoxIcons.Map_Link))

        self.buttons.append(self.linkMap)


class EnMAPBoxMapDock(EnMAPBoxDock):
    """
    A dock to visualize geodata that can be mapped
    """
    @staticmethod
    def get_canvases():
        return [c for c in gc.get_referrers(qgis.gui.QgsMapCanvas) if isinstance(c, qgis.gui.QgsMapCanvas)]

    def __init__(self, *args, **kwds):
        initSrc = kwds.pop('initSrc', None)



        super(EnMAPBoxMapDock, self).__init__(*args, **kwds)

        #self.actionLinkExtent = QAction(QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_CommandLink), 'Link to map extent', self)
        #self.actionLinkCenter = QAction(QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_CommandLink), 'Linkt to map center', self)
        #self.label.buttons.append(self.actionLinkCenter.getButton())
        self.canvas = qgis.gui.QgsMapCanvas(self)
        settings = QSettings()
        assert isinstance(self.canvas, qgis.gui.QgsMapCanvas)
        self.canvas.setCanvasColor(Qt.black)
        self.canvas.enableAntiAliasing(settings.value('/qgis/enable_anti_aliasing', False, type=bool))
        self.canvas.useImageToRender(settings.value('/qgis/use_image_to_render', False, type=bool))
        self.layout.addWidget(self.canvas)

        #link canvas to map tools
        g = self.enmapbox.gui
        #g.actionAddView.triggered.connect(lambda: self.enmapbox.dockarea.addDock(EnMAPBoxDock(self)))
        #g.actionAddMapView.triggered.connect(lambda : self.enmapbox.dockarea.addDock(EnMAPBoxMapDock(self)))
        #g.actionAddTextView.triggered.connect(lambda: self.enmapbox.dockarea.addDock(EnMAPBoxTextDock(self)))

        # create the map tools and linke them to the toolbar actions
        self.toolPan = qgis.gui.QgsMapToolPan(self.canvas)
        self.toolPan.setAction(g.actionPan)
        self.toolPan.action().triggered.connect(lambda: self.canvas.setMapTool(self.toolPan))

        self.toolZoomIn = qgis.gui.QgsMapToolZoom(self.canvas, False)  # false = in
        self.toolZoomIn.setAction(g.actionZoomIn)
        self.toolZoomIn.action().triggered.connect(lambda: self.canvas.setMapTool(self.toolZoomIn))

        self.toolZoomOut = qgis.gui.QgsMapToolZoom(self.canvas, True)  # true = out
        self.toolZoomOut.setAction(g.actionZoomOut)
        self.toolZoomOut.action().triggered.connect(lambda: self.canvas.setMapTool(self.toolZoomOut))


        self.label.linkMap.clicked.connect(lambda:CanvasLinkTargetWidget.ShowMapLinkTargets(self.canvas))

        #set default map tool
        self.canvas.setMapTool(self.toolPan)

        #todo: context menu

        if initSrc:
            self.addLayer(initSrc)

    def test(self):
        print('START LINKING')

        w = CanvasLinkTargetWidget(self.enmapbox.gui)
        s = ""

    def _getLabel(self):
        return EnMAPBoxMapDockLabel(self)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
                s = ""
        else:
            super(EnMAPBoxMapDock, self).mousePressEvent(event)

    def linkWithMapDock(self, mapDock, linktype='extent'):
        assert isinstance(mapDock, EnMAPBoxMapDock)
        self.linkWithCanvas(mapDock.canvas, linktype=linktype)


    def linkWithCanvas(self, canvas, linktype='extent'):
        assert isinstance(canvas, qgis.gui.QgsMapCanvas)

        CanvasLink.CreateLink(canvas, self.canvas, linktype=linktype)

    def addLayer(self, mapLayer):

        ds = self.enmapbox.dataSourceManager.addSource(mapLayer)
        if isinstance(ds, DataSourceSpatial):

            canvasLayers = self.canvas.layers()
            mapLyr = QgsMapCanvasLayer(ds.lyr)
            mapLyr.setVisible(True)

            canvasLayers.append(mapLyr)

            if len(canvasLayers) == 1:
                self.canvas.setExtent(ds.lyr.extent())

            self.canvas.setLayerSet(canvasLayers)

            s  =""



class EnMAPBoxTextDock(EnMAPBoxDock):

    """
    A dock to visualize textural data
    """
    def __init__(self, *args, **kwds):
        html = kwds.pop('html', None)
        plainTxt = kwds.pop('plainTxt', None)

        super(EnMAPBoxTextDock, self).__init__(*args, **kwds)

        self.edit = QtGui.QTextEdit(self)

        if html:
            self.edit.insertHtml(html)
        elif plainTxt:
            self.edit.insertPlainText(plainTxt)
        self.layout.addWidget(self.edit)








def create_qgis_instance():
    pass


if __name__ == '__main__':

    #start a QGIS instance

    from qgis.gui import *
    from qgis.core import *
    if sys.platform == 'darwin':
        PATH_QGS = r'/Applications/QGIS.app/Contents/MacOS'
    else:
        PATH_QGS = os.environ['QGIS_PREFIX_PATH']
    assert os.path.exists(PATH_QGS)
    qgsApp = QgsApplication([], True)
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
    EB.createDock('MAP', name='MapDock 1', initSrc=TestData.Landsat_Fmask)
    EB.createDock('MAP', name='MapDock 2', initSrc=TestData.Landsat_Image)
    EB.createDock('MAP', name='MapDock 4', initSrc=TestData.AlpineForelandSubset)
    EB.createDock('MAP', name='MapDock 3', initSrc=TestData.Landsat_Shp)
    EB.createDock('TEXT', name='TextDock',
                                         html='Here we can show HTML like text:'
                                              '<a href="http://www.enmap.org">www.enmap.org</a>'
                                              '</br>'+LORE_IPSUM)


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

