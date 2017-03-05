from __future__ import absolute_import
import six, sys, os, gc, re, collections, uuid, logging
logger = logging.getLogger(__name__)
from qgis.core import *
from qgis.gui import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from enmapbox.utils import *

from osgeo import gdal, ogr

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
    def srcToString(src):
        if isinstance(src, QUrl):
            if src.isLocalFile():
                src = str(src.toLocalFile())
            else:
                src = str(src.path())
        if isinstance(src, unicode):
            src = str(src)

        if isinstance(src, str):
            src = os.path.abspath(src)
        else:
            src = None
        return src

    @staticmethod
    def isVectorSource(src):
        """
        Returns the source uri if it can be handled as known vector data source.
        :param src: any type
        :return: uri (str) | None
        """
        uri = None
        if isinstance(src, QgsVectorLayer) and src.isValid():
            uri = DataSourceFactory.isVectorSource(src.dataProvider())
        if isinstance(src, QgsVectorDataProvider):
            uri = str(src.dataSourceUri()).split('|')[0]
        if isinstance(src, ogr.DataSource):

            uri = src.GetName()

        src = DataSourceFactory.srcToString(src)
        if isinstance(src, str):
            # todo: check different providers, not only ogr
            try:
                result = DataSourceFactory.isVectorSource(ogr.Open(src))
                if result is not None:
                    uri = result
            except Exception:
                s = ""
                pass

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

        src = DataSourceFactory.srcToString(src)
        if isinstance(src, str):

            try:
                uri = DataSourceFactory.isRasterSource(gdal.Open(src))
            except RuntimeError, e:
                uri = None

        assert uri is None or isinstance(uri, str)
        return uri

    @staticmethod
    def isEnMapBoxPkl(src):
        """
        Returns the source uri if it can be handled as known raster data source.
        :param src: any type
        :return: uri (str) | None
        """

        uri = None
        src = DataSourceFactory.srcToString(src)
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
    def fromXML(domElement):
        """
        :param domElements:
        :return:
        """
        assert isinstance(domElement, QDomElement)
        tagName = domElement.tagName()
        if tagName == 'dock-tree-node':
            s = ""
        elif tagName == 'custom':
            return None
        else:
            return None

        s = ""


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

        uri = DataSourceFactory.isRasterSource(src)
        if uri is not None:
            return DataSourceRaster(uri, name=name, icon=icon)
        uri = DataSourceFactory.isVectorSource(src)
        if uri is not None:
            return DataSourceVector(uri, name=name, icon=icon)

        uri = DataSourceFactory.isEnMapBoxPkl(src)
        if uri is not None:
            return ProcessingTypeDataSource(uri, name=name, icon=icon)

        src = DataSourceFactory.srcToString(src)
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
                logger.debug('MAP LAYER: {}'.format(mapLyr))
                return DataSourceFactory.Factory(reg.mapLayer(src), name)

        logger.warning('Can not open {}'.format(str(src)))
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
            provider = QFileIconProvider()
            icon = provider.icon(QFileInfo(uri))

        if name is None:
            name = os.path.basename(uri)

        assert name is not None
        assert isinstance(icon, QIcon)

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

        lyr = self.createUnregisteredMapLayer()

        from enmapbox.gui.utils import SpatialExtent
        self.spatialExtent = SpatialExtent.fromLayer(lyr)

        assert isinstance(lyr, QgsMapLayer)
        assert lyr.isValid()

        self.mapLayers = list()


    def createUnregisteredMapLayer(self, *args, **kwds):
        """
        creates and returns a QgsMapLayer from self.src
        the QgsMapLayer should be not registered in the QgsMapLayerRegistry
        to be implemented by inherited classes
        :return:
        """
        raise NotImplementedError()


    def createRegisteredMapLayer(self, *args, **kwds):
        """
        Returns a new registered map layer from this data source
        :return:
        """


        ml = self.createUnregisteredMapLayer(*args, **kwds)
        ml.setName(self.name)

        #not reuqired any more, will be done by map canvas
        #QgsMapLayerRegistry.instance().addMapLayer(ml, False)
        self.mapLayers.append(ml)
        return ml

class ProcessingTypeDataSource(DataSourceFile):
    def __init__(self, uri, name=None, icon=None):
        super(ProcessingTypeDataSource, self).__init__(uri, name, icon)
        from enmapbox.processing import types
        from enmapbox.processing.types import Estimator
        if not isinstance(icon, QIcon):
            self.icon = QIcon(':/enmapbox/icons/alg.png')

        self.pfType = types.unpickle(uri)

    def report(self):
        return self.pfType.report()


    def metadataDict(self):
        return self.pfType.getMetadataDict()


class DataSourceRaster(DataSourceSpatial):

    def __init__(self, uri, name=None, icon=None ):
        super(DataSourceRaster, self).__init__(uri, name, icon)

        self._refLayer = self.createUnregisteredMapLayer(self.uri)
        #lyr =QgsRasterLayer(self.uri, self.name, False)
        dp = self._refLayer.dataProvider()


        #change icon
        if dp.bandCount() == 1:
            dt = dp.dataType(1)
            cat_types = [QGis.CInt16, QGis.CInt32, QGis.Byte, QGis.UInt16, QGis.UInt32, QGis.Int16, QGis.Int32]
            if dt in cat_types:
                if len(dp.colorTable(1)) != 0:
                    self.icon = QIcon(':/enmapbox/icons/filelist_classification.png')
                else:
                    self.icon = QIcon(':/enmapbox/icons/filelist_mask.png')
            elif dt in [QGis.Float32, QGis.Float64, QGis.CFloat32, QGis.CFloat64]:
                self.icon = QIcon(':/enmapbox/icons/filelist_regression.png')
        else:
            self.icon = QIcon(':/enmapbox/icons/mIconRasterLayer.png')

    def createUnregisteredMapLayer(self, *args, **kwargs):
        """
        creates and returns a QgsRasterLayer from self.src
        :return:
        """
        return QgsRasterLayer(self.uri, *args, **kwargs)


class DataSourceVector(DataSourceSpatial):
    def __init__(self, uri,  name=None, icon=None ):
        super(DataSourceVector, self).__init__(uri, name, icon)

        lyr = self.createUnregisteredMapLayer()
        geomType = lyr.geometryType()

        if geomType in [QGis.WKBPoint, QGis.WKBPoint25D]:
            self.icon = QIcon(':/enmapbox/icons/mIconPointLayer.png')
        elif geomType in [QGis.WKBLineString, QGis.WKBMultiLineString25D]:
            self.icon = QIcon(':/enmapbox/icons/mIconLineLayer.png')
        elif geomType in [QGis.WKBPolygon, QGis.WKBPoint25D]:
            self.icon = QIcon(':/enmapbox/icons/mIconPolygonLayer.png')

    def createUnregisteredMapLayer(self, *args, **kwargs):
        """
        creates and returns a QgsVectorLayer from self.src
        :return:
        """
        if len(args) == 0 and len(kwargs) == 0:
            return QgsVectorLayer(self.uri, None, 'ogr')
        else:
            return QgsVectorLayer(self.uri, **kwargs)



