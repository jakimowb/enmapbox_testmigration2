from __future__ import absolute_import
import six, sys, os, gc, re, collections

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from enmapbox.utils import *

from osgeo import gdal, ogr

import enmapbox
dprint = enmapbox.dprint

class DataSource(object):
    """Base class to describe file/stream/IO sources as used in EnMAP-GUI context"""



    @staticmethod
    def isVectorSource(src):
        """
        Returns the sourc uri if it can be handled as known vector data source.
        :param src: any type
        :return: uri (str) | None
        """
        uri = None
        if isinstance(src, QgsVectorLayer) and src.isValid():
            uri = DataSource.isVectorSource(src.dataProvider())
        if isinstance(src, QgsVectorDataProvider):
            uri = src.dataSourceUri()
        if isinstance(src, ogr.DataSource):
            uri = src.GetName()
        if isinstance(src, QUrl):
            if src.isLocalFile():
                uri = str(src.toLocalFile())
            else:
                uri = str(src.path())
        if isinstance(src, str):
            #todo: check different providers, not only ogr
            result = None
            try:
                result = DataSource.isVectorSource(ogr.Open(src))
            except:
                pass

            uri = result

        assert uri is None or isinstance(uri, str)
        return uri

    @staticmethod
    def isRasterSource(src):
        """
        Returns the source uri string if it can be handled as known raster data source.
        :param src: any type
        :return: uri (str) | None
        """

        gdal.UseExceptions()
        uri = None
        if isinstance(src, QgsRasterLayer) and src.isValid():
            uri = DataSource.isRasterSource(src.dataProvider())
        if isinstance(src, QgsRasterDataProvider):
            uri = str(src.dataSourceUri())
        if isinstance(src, gdal.Dataset):
            uri = src.GetFileList()[0]
        if isinstance(src, QUrl):
            if src.isLocalFile():
                uri = str(src.toLocalFile())
            else:
                uri = str(src.path())

        if isinstance(src, unicode):
            src = str(src)

        if isinstance(src, str):
            # todo: check different providers, not only gdal
            try:
                uri = DataSource.isRasterSource(gdal.Open(src))
            except RuntimeError, e:
                pass

        assert uri is None or isinstance(uri, str)
        return uri

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
        assert not isinstance(src, list)
        """
        Factory method / switch to return the best suited DataSource Instance to an unknown source
        :param source: anything
        :param name: name, optional
        :param icon: QIcon, optional
        :return:
        """

        if isinstance(src, DataSource): return src

        dprint('DataSourceFactory input: {} {}'.format(type(src), src))

        uri = DataSource.isRasterSource(src)
        if uri is not None:
            return DataSourceRaster(uri, name=name, icon=icon)
        uri = DataSource.isVectorSource(src)
        if uri is not None:
            return DataSourceVector(uri, name=name, icon=icon)

        uri = DataSource.isEnMAPBoxModel(src)
        if uri is not None:
            raise NotImplementedError()

        if isinstance(src, str):
            if os.path.isfile(src):
                return DataSourceFile(src, name=name, icon=icon)

            reg = QgsMapLayerRegistry.instance()
            ids = [str(l.id()) for l in reg.mapLayers().values()]
            if src in ids:
                mapLyr = reg.mapLayer(src)
                dprint('MAP LAYER: {}'.format(mapLyr))
                return DataSource.Factory(reg.mapLayer(src), name)
            dprint('EXISTING REGISTRY IDS: {}'.format(','.join(ids)))
        dprint('Can not open {}'.format(str(src)))
        return None

    def __init__(self, uri, name=None, icon=None):
        """
        :param uri: uri of data source. must be a string
        :param name: name as it appears in the source file list
        """
        assert type(uri) is str
        if icon is None:
            icon = IconProvider.icon(uri)
        if name is None:
            name = os.path.basename(uri)
        assert name is not None
        assert type(icon) is QIcon

        self.uri = uri
        self.icon = icon
        self.name = name

    def __eq__(self, other):
        return self.uri == other.uri

    def getUri(self):
        """Returns the URI string that describes the data source"""
        return self.uri

    def getIcon(self):
        """
        Returns the icon associated with the data source
        :return: QIcon
        """
        return self.icon


    def getTreeItem(self, parentItem):
        import enmapbox.main

        """
        Returns a TreeItem to be used in TreeViews
        :param parentItem:
        :return:
        """
        return TreeItem(parentItem, self.name,
                        data=self,
                        icon=self.getIcon(),
                        tooltip = str(self))

    def __repr__(self):
        return 'DataSource: {} {}'.format(self.name, str(self.uri))

class DataSourceFile(DataSource):

    def __init__(self, uri, name=None, icon=None):
        super(DataSourceFile, self).__init__(uri, name, icon)

    def getTreeItem(self, parent):
        import enmapbox.main

        itemTop = super(DataSourceFile, self).getTreeItem(parent)
        infos = list()
        infos.append('Path: {}'.format(self.uri))
        infos.append('Size: {}'.format(os.path.getsize(self.uri)))
        TreeItem(itemTop, 'File Information', infos=infos, tooltip='\n'.join(infos), asChild=True)
        return itemTop

class DataSourceTextFile(DataSourceFile):

    def __init__(self, uri, name=None, icon=None):
        if icon is None:
            icon = QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_FileIcon)
        super(DataSourceTextFile, self).__init__(uri, name, icon)



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
        the QgsMapLayer should be not registered in the QgsMapLayerRegistry
        to be implemented by inherited classes
        :return:
        """
        raise NotImplementedError()


    def createMapLayer(self, *args, **kwds):
        """
        Returns a new registered map layer from this data source
        :return:
        """
        ml = self._createMapLayer(*args, **kwds)
        QgsMapLayerRegistry.instance().addMapLayer(ml, False)
        self.mapLayers.append(ml)
        return ml


class DataSourceRaster(DataSourceSpatial):

    def __init__(self, uri, name=None, icon=None ):
        super(DataSourceRaster, self).__init__(uri, name, icon)

        self._refLayer = self._createMapLayer(self.uri)
        dp = self._refLayer.dataProvider()

        #change icon
        if dp.bandCount() == 1:
            dt = dp.dataType(1)
            cat_types = [QGis.CInt16, QGis.CInt32, QGis.Byte, QGis.UInt16, QGis.UInt32, QGis.Int16, QGis.Int32]
            if dt in cat_types:
                if len(dp.colorTable(1)) != 0:
                    self.icon = QIcon(IconProvider.File_RasterClassification)
                else:
                    self.icon = QIcon(IconProvider.File_RasterMask)
            elif dt in [QGis.Float32, QGis.Float64, QGis.CFloat32, QGis.CFloat64]:
                self.icon = QIcon(IconProvider.File_RasterRegression)
        else:
            self.icon = QIcon(IconProvider.File_Raster)

    def _createMapLayer(self, *args, **kwargs):
        """
        creates and returns a QgsRasterLayer from self.src
        :return:
        """
        return QgsRasterLayer(self.uri, *args, **kwargs)


    def getTreeItem(self, parent):
        import enmapbox.main
        itemTop = super(DataSourceRaster, self).getTreeItem(parent)


        dp = self._refLayer.dataProvider()
        crs = self._refLayer.crs()

        infos = list()
        infos.append('URI: {}'.format(dp.dataSourceUri()))
        infos.append('DIMS: {}x{}x{}'.format(dp.xSize(), dp.ySize(), dp.bandCount()))
        item = TreeItem(itemTop, 'File Information')
        item.tooltip = '\n'.join(infos)
        item.addTextChilds(infos)
        #define actions related to top icon

        if crs is not None:
            infos = list()
            infos.append('CRS: {}'.format(crs.description()))
            infos.append('Extent: {}'.format(dp.extent().toString(True)))
            item = TreeItem(itemTop, 'Spatial Reference')
            item.tooltip = '\n'.join(infos)
            item.addTextChilds(infos)

        item = TreeItem(itemTop, 'Bands [{}]'.format(dp.bandCount()))

        bandnames = [self._refLayer.bandName(b+1) for b in range(self._refLayer.bandCount())]

        if dp.name() == 'gdal':
            ds = gdal.Open(dp.dataSourceUri())
            for b in range(ds.RasterCount):
                bandnames[b] = '{} "{}"'.format(bandnames[b], ds.GetRasterBand(b+1).GetDescription())

        for b in range(dp.bandCount()):
            infos=list()
            if dp.srcHasNoDataValue(b+1):
                infos.append('No data : {}'.format(dp.srcNoDataValue(b+1)))
            itemBand = TreeItem(item, bandnames[b])
            itemBand.tooltip = '\n'.join(infos)
            itemBand.addTextChilds(infos)
        return itemTop

class DataSourceVector(DataSourceSpatial):
    def __init__(self, uri,  name=None, icon=None ):
        super(DataSourceVector, self).__init__(uri, name, icon)


        dp = self._refLayer.dataProvider()
        assert isinstance(dp, QgsVectorDataProvider)

        geomType = self._refLayer.geometryType()
        if geomType in [QGis.WKBPoint, QGis.WKBPoint25D]:
            self.icon = QIcon(IconProvider.File_Vector_Point)
        elif geomType in [QGis.WKBLineString, QGis.WKBMultiLineString25D]:
            self.icon = QIcon(IconProvider.File_Vector_Polygon)
        elif geomType in [QGis.WKBPolygon, QGis.WKBPoint25D]:
            self.icon = QIcon(IconProvider.File_Vector_Polygon)

    def _createMapLayer(self, *args, **kwargs):
        """
        creates and returns a QgsVectorLayer from self.src
        :return:
        """
        if len(args) == 0 and len(kwargs) == 0:
            return QgsVectorLayer(self.uri, None, 'ogr')
        else:
            return QgsVectorLayer(self.uri, **kwargs)

    def getTreeItem(self, parent):
        from enmapbox.main import TreeItem
        itemTop = super(DataSourceVector, self).getTreeItem(parent)

        #itemTop = TreeItem(parent, self.name, icon=self.getIcon())
        assert type(self._refLayer) is QgsVectorLayer
        srs = self._refLayer.crs()
        dp = self._refLayer.dataProvider()
        assert isinstance(dp, QgsVectorDataProvider)

        infos = list()
        infos.append('Path: {}'.format(self.uri))
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
