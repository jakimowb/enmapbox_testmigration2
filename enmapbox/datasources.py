from __future__ import absolute_import
import six, sys, os, gc, re, collections

from PyQt4.QtCore import *
from PyQt4 import QtGui
from qgis.core import *
from qgis.gui import *
from enmapbox.utils import *

from osgeo import gdal, ogr

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
        assert not isinstance(src, list)
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
        import enmapbox.main

        """
        Returns a TreeItem to be used in TreeViews
        :param parentItem:
        :return:
        """
        return enmapbox.main.TreeItem(parentItem, self.name,
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
        import enmapbox.main

        itemTop = super(DataSourceFile, self).getTreeItem(parent)
        infos = list()
        infos.append('Path: {}'.format(self.src))
        infos.append('Size: {}'.format(os.path.getsize(self.src)))
        enmapbox.main.TreeItem(itemTop, 'File Information', infos=infos, tooltip='\n'.join(infos), asChild=True)
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
                    self.icon = QtGui.QIcon(Icons.File_RasterClassification)
                else:
                    self.icon = QtGui.QIcon(Icons.File_RasterMask)
            elif dt in [QGis.Float32, QGis.Float64, QGis.CFloat32, QGis.CFloat64]:
                self.icon = QtGui.QIcon(Icons.File_RasterRegression)
        else:
            self.icon = QtGui.QIcon(Icons.File_Raster)

    def _createMapLayer(self, *args, **kwargs):
        """
        creates and returns a QgsRasterLayer from self.src
        :return:
        """
        return QgsRasterLayer(self.src, *args, **kwargs)


    def getTreeItem(self, parent):
        import enmapbox.main
        itemTop = super(DataSourceRaster, self).getTreeItem(parent)


        dp = self._refLayer.dataProvider()
        crs = self._refLayer.crs()

        infos = list()
        infos.append('URI: {}'.format(dp.dataSourceUri()))
        infos.append('DIMS: {}x{}x{}'.format(dp.xSize(), dp.ySize(), dp.bandCount()))
        enmapbox.main.TreeItem(itemTop, 'File Information', infos=infos, tooltip='\n'.join(infos), asChild=True)

        #define actions related to top icon


        if crs is not None:
            infos = list()
            infos.append('CRS: {}'.format(crs.description()))

            infos.append('Extent: {}'.format(dp.extent().toString(True)))
            enmapbox.main.TreeItem(itemTop, 'Spatial Reference', infos=infos, asChild=True, tooltip='\n'.join(infos))


        itemBands = enmapbox.main.TreeItem(itemTop, 'Bands [{}]'.format(dp.bandCount()), asChild=True)

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
            enmapbox.main.TreeItem(itemBands, bandnames[b], tooltip = '\n'.join(infos), infos=infos, asChild=True)
        return itemTop

class DataSourceVector(DataSourceSpatial):


    def __init__(self, uri,  name=None, icon=None ):
        super(DataSourceVector, self).__init__(uri, name, icon)


        dp = self._refLayer.dataProvider()
        assert isinstance(dp, QgsVectorDataProvider)

        geomType = self._refLayer.geometryType()
        if geomType in [QGis.WKBPoint, QGis.WKBPoint25D]:
            self.icon = QtGui.QIcon(Icons.File_Vector_Point)
        elif geomType in [QGis.WKBLineString, QGis.WKBMultiLineString25D]:
            self.icon = QtGui.QIcon(Icons.File_Vector_Polygon)
        elif geomType in [QGis.WKBPolygon, QGis.WKBPoint25D]:
            self.icon = QtGui.QIcon(Icons.File_Vector_Polygon)

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
        from enmapbox.main import TreeItem
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
