from __future__ import absolute_import
import six, sys, os, gc, re, collections, uuid

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from enmapbox.utils import *

from osgeo import gdal, ogr

import enmapbox
dprint = enmapbox.dprint


def openPlatformDefault(uri):
    if os.path.isfile(uri):
        if sys.platform == 'darwin':
            os.system('open {}'.format(uri))

        elif sys.platform.startswith('win'):
            os.system('start {}'.format(uri))
        else:
            raise NotImplementedError('Unhandled platform {}'.format(sys.platform))
    else:
        raise NotImplementedError('Unhandled uri type {}'.format(uri))

class DataSourceFactory(object):

    @staticmethod
    def srctostring(src):
        if isinstance(src, QUrl):
            if src.isLocalFile():
                src = str(src.toLocalFile())
            else:
                src = str(src.path())
        if isinstance(src, unicode):
            src = str(src)

        if isinstance(src, str):
            src = os.path.abspath(src)
        return src

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

        src = DataSourceFactory.srctostring(src)
        if isinstance(src, str):
            # todo: check different providers, not only ogr
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
            uri = DataSourceFactory.isRasterSource(src.dataProvider())
        if isinstance(src, QgsRasterDataProvider):
            uri = str(src.dataSourceUri())
        if isinstance(src, gdal.Dataset):
            uri = src.GetFileList()[0]

        src = DataSourceFactory.srctostring(src)
        if isinstance(src, str):
            # todo: check different providers, not only gdal
            try:
                uri = DataSourceFactory.isRasterSource(gdal.Open(src))
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

        uri = None
        src = DataSourceFactory.srctostring(src)
        if isinstance(src, str) and os.path.exists(src):

            try:
                from enmapbox.processing import types
                from enmapbox.processing.types import Estimator

                obj = types.unpickle(src)
                if isinstance(obj, Estimator):
                    uri = src
            except Exception, e:
                pass
        return uri

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

        uri = DataSourceFactory.isRasterSource(src)
        if uri is not None:
            return DataSourceRaster(uri, name=name, icon=icon)
        uri = DataSourceFactory.isVectorSource(src)
        if uri is not None:
            return DataSourceVector(uri, name=name, icon=icon)

        uri = DataSourceFactory.isEnMAPBoxModel(src)
        if uri is not None:
            return DataSourceModel(uri, name=name, icon=icon)

        src = DataSourceFactory.srctostring(src)
        if isinstance(src, str):
            if os.path.isfile(src):
                ext = os.path.splitext(src)[1].lower()
                if ext in ['.csv', '.txt']:
                    return DataSourceTextFile(src, name=name, icon=icon)
                if ext in ['.xml', '.html']:
                    return DataSourceXMLFile(src, name=name, icon=icon)
                return DataSourceFile(src, name=name, icon=icon)

            reg = QgsMapLayerRegistry.instance()
            ids = [str(l.id()) for l in reg.mapLayers().values()]
            if src in ids:
                mapLyr = reg.mapLayer(src)
                dprint('MAP LAYER: {}'.format(mapLyr))
                return DataSourceFactory.Factory(reg.mapLayer(src), name)

        dprint('Can not open {}'.format(str(src)))
        return None


class DataSource(object):
    """Base class to describe file/stream/IO sources as used in EnMAP-GUI context"""



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
        self.uuid = uuid.uuid4()
        self.uri = uri
        self.icon = icon
        self.name = name

    def __eq__(self, other):
        return other is not None and str(self.uri) == str(other.uri)

    def getUri(self):
        """Returns the URI string that describes the data source"""
        return self.uri

    def getIcon(self):
        """
        Returns the icon associated with the data source
        :return: QIcon
        """
        return self.icon

    def writeXml(self, element):

        s = ""

    def __repr__(self):
        return 'DataSource: {} {}'.format(self.name, str(self.uri))

class DataSourceFile(DataSource):

    def __init__(self, uri, name=None, icon=None):
        super(DataSourceFile, self).__init__(uri, name, icon)


class DataSourceTextFile(DataSourceFile):
    """
    Class to handle editable text files
    """
    def __init__(self, uri, name=None, icon=None):
        super(DataSourceTextFile, self).__init__(uri, name, icon)





class DataSourceXMLFile(DataSourceTextFile):
    """
    Class to specifically handle XML based files like XML, HTML etc.
    """
    def __init__(self, uri, name=None, icon=None):
        super(DataSourceXMLFile, self).__init__(uri, name, icon)




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
        ml.setName(self.name)
        QgsMapLayerRegistry.instance().addMapLayer(ml, False)
        self.mapLayers.append(ml)
        return ml

class DataSourceModel(DataSourceFile):
    def __init__(self, uri, name=None, icon=None):
        super(DataSourceModel, self).__init__(uri, name, icon)
        from enmapbox.processing import types
        from enmapbox.processing.types import Estimator


        self.model = types.unpickle(uri)



class DataSourceRaster(DataSourceSpatial):

    def __init__(self, uri, name=None, icon=None ):
        super(DataSourceRaster, self).__init__(uri, name, icon)

        self._refLayer = self._createMapLayer(self.uri)
        #lyr =QgsRasterLayer(self.uri, self.name, False)
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
        ds = DataSourceFactory.Factory(src, name=name, icon=icon)


        if isinstance(ds, DataSource):
            # check if source is already registered
            for src in self.sources:
                if os.path.abspath(src.uri) == os.path.abspath(ds.uri):
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


