from __future__ import absolute_import
import six, sys, os, gc, re, collections, uuid, logging, pickle
logger = logging.getLogger(__name__)
from qgis.core import *
from qgis.gui import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from enmapbox.utils import *
import numpy as np
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
    def isSpeclib(src):
        uri = None
        src = DataSourceFactory.srcToString(src)
        if isinstance(src, str) and os.path.exists(src):
            from enmapbox.gui.spectrallibraries import SpectralLibraryIO
            for cls in SpectralLibraryIO.__subclasses__():
                if cls.canRead(src):
                    uri = src
                    break
        return uri


    @staticmethod
    def isHubFlowObj(src):
        """
        Returns the source uri if it can be handled as known raster data source.
        :param src: any type
        :return: uri (str) | None
        """

        src = DataSourceFactory.srcToString(src)
        if isinstance(src, str) and os.path.exists(src):
            import hubflow.types
            obj = hubflow.types.FlowObject.unpickle(src, raiseError=False)
            if isinstance(obj, hubflow.types.FlowObject):
                return src
        return None

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
        if src is None:
            return None

        if type(src) in [str, unicode] and (len(src) == 0):
            return None

        if isinstance(src, DataSource):
            return src

        from enmapbox.gui.spectrallibraries import SpectralLibraryVectorLayer, SpectralLibrary
        if isinstance(src, SpectralLibraryVectorLayer):
            return DataSourceFactory.Factory(src.mSpeclib)

        uri = DataSourceFactory.isRasterSource(src)
        if uri is not None:
            return DataSourceRaster(uri, name=name, icon=icon)
        uri = DataSourceFactory.isVectorSource(src)

        if uri is not None:
            return DataSourceVector(uri, name=name, icon=icon)

        uri = DataSourceFactory.isSpeclib(src)
        if uri is not None:
            return DataSourceSpectralLibrary(uri, name=name, icon=icon)

        uri = DataSourceFactory.isHubFlowObj(src)
        if uri is not None:
            return HubFlowDataSource(uri, name=name, icon=icon)

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


    sigMetadataChanged = pyqtSignal()

    def __init__(self, uri, name=None, icon=None):
        """
        :param uri: uri of data source. must be a string
        :param name: name as it appears in the source file list
        """
        assert type(uri) is str
        self.mUuid = uuid.uuid4()
        self.mUri = uri
        self.mIcon = None
        self.mName = ''

        self.updateMetadata(name=name, icon=icon)

    def setUri(self, uri):
        self.mUri = str(uri)
        self.updateMetadata()

    def updateMetadata(self, icon=None, name=None):
        """

        """
        if icon is None:
            provider = QFileIconProvider()
            icon = provider.icon(QFileInfo(self.mUri))
        if name is None:
            name = os.path.basename(self.mUri)
        assert name is not None
        assert isinstance(icon, QIcon)

        self.mIcon = icon
        self.mName = name

    def __eq__(self, other):
        return other is not None and \
               self.uri() == other.uri()

    def uuid(self):
        """
        Returns the Unique Identifier that was created when initializing this object.
        :return: UUID
        """
        return self.mUuid

    def uri(self):
        """Returns the URI string that describes the data source"""
        return str(self.mUri)

    def setIcon(self, icon):
        self.mIcon = icon

    def icon(self):
        """
        Returns the icon associated with the data source
        :return: QIcon
        """
        return QIcon(self.mIcon)

    def setIcon(self, icon):
        assert isinstance(icon, QIcon)
        self.mIcon = icon
        return self

    def setName(self, name):
        """
        Sets the datasource name. Override it to allow and apply for changes of the base-name
        :param name:
        :return: self
        """
        self.mName = name
        return self

    def writeXml(self, element):
        """
        Override this to write
        :param element:
        :return:
        """
        pass

    def __repr__(self):
        return 'DataSource: {} {}'.format(self.mName, str(self.mUri))

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




class DataSourceSpatial(DataSourceFile):
    """
    Abstract class to be implemented by inherited DataSource that support spatial data
    """
    def __init__(self, uri, name=None, icon=None ):
        super(DataSourceSpatial, self).__init__(uri, name, icon)

        lyr = self.createUnregisteredMapLayer()

        from enmapbox.gui.utils import SpatialExtent
        self.spatialExtent = SpatialExtent.fromLayer(lyr)

        assert isinstance(lyr, QgsMapLayer)
        #assert lyr.isValid()



    def createUnregisteredMapLayer(self, *args, **kwds):
        """
        creates and returns a QgsMapLayer from self.src
        the QgsMapLayer should be not registered in the QgsMapLayerRegistry
        to be implemented by inherited classes
        :return:
        """
        raise NotImplementedError()


import hubflow.types
class HubFlowDataSource(DataSourceFile):
    def __init__(self, uri, name=None, icon=None):
        super(HubFlowDataSource, self).__init__(uri, name, icon)
        from hubflow.types import FlowObject

        if not isinstance(icon, QIcon):
            self.mIcon = QIcon(':/enmapbox/icons/alg.png')


        self.loadFlowObject()
        s = ""

    def loadFlowObject(self):
        self.mFlowObj = hubflow.types.FlowObject.unpickle(self.mUri, raiseError=False)
        s = ""

    def flowObject(self):
        if not isinstance(self.mFlowObj, hubflow.types.FlowObject):
            self.loadFlowObject()
        if isinstance(self.mFlowObj, hubflow.types.FlowObject):
            return self.mFlowObj
        else:
            return None


class DataSourceSpectralLibrary(DataSourceFile):

    def __init__(self, uri, name=None, icon=None):
        super(DataSourceSpectralLibrary, self).__init__(uri, name, icon)

        self.mSpeclib = None
        self.nProfiles = None
        self.profileNames = []
        self.updateMetadata()

    def updateMetadata(self, *args, **kwds):
        from enmapbox.gui.spectrallibraries import SpectralLibrary, SpectralProfile
        self.mSpeclib = SpectralLibrary.readFrom(self.mUri)
        assert isinstance(self.mSpeclib, SpectralLibrary)
        #self.nProfiles = len(slib)
        #self.profileNames = []
        #for p in slib:
        #    assert isinstance(p, SpectralProfile)
        #    self.profileNames.append(p.name())


class DataSourceRaster(DataSourceSpatial):

    def __init__(self, uri, name=None, icon=None ):
        super(DataSourceRaster, self).__init__(uri, name, icon)
        self.nSamples = -1
        self.nBands = -1
        self.nLines = -1
        self.dataType = -1
        self.pxSizeX = -1
        self.pxSizeY = -1
        self.mDatasetMetadata = collections.OrderedDict()
        self.mBandMetadata = []
        self.updateMetadata()



    def updateMetadata(self, icon=None, name=None):
        super(DataSourceRaster, self).updateMetadata(icon=icon, name=None)

        ds = gdal.Open(self.mUri)
        assert isinstance(ds, gdal.Dataset)
        self.nSamples, self.nLines = ds.RasterXSize, ds.RasterYSize
        self.nBands = ds.RasterCount
        gt = ds.GetGeoTransform()

        from enmapbox.gui.utils import px2geo
        v = px2geo(QPoint(0, 0), gt) - px2geo(QPoint(1, 1), gt)
        self.pxSize = QSizeF(abs(v.x()), abs(v.y()))


        def fetchMetadata(obj):
            assert type(obj) in [gdal.Dataset, gdal.Band]

            md = collections.OrderedDict()
            domains = obj.GetMetadataDomainList()
            if isinstance(domains , list):
                for domain in sorted(domains):
                    tmp = obj.GetMetadata_Dict(domain)
                    if len(tmp) > 0:
                        md[domain] = tmp
            return md

        self.mDatasetMetadata = fetchMetadata(ds)
        self.mBandMetadata = []
        hasClassInfo = False
        from enmapbox.gui.classificationscheme import ClassInfo, ClassificationScheme
        for b in range(ds.RasterCount):
            band = ds.GetRasterBand(b+1)
            cs = ClassificationScheme.fromRasterImage(ds, b)
            md = fetchMetadata(band)
            if isinstance(cs, ClassificationScheme):
                hasClassInfo = True
                md['__ClassificationScheme__'] = cs

            self.mBandMetadata.append(md)

            if b == 0:
                self.dataType = band.DataType


        if hasClassInfo is not None:
            icon = QIcon(':/enmapbox/icons/filelist_classification.png')
        elif self.dataType in [gdal.GDT_Byte]:
            icon = QIcon(':/enmapbox/icons/filelist_mask.png')
        elif self.dataType in [gdal.GDT_Float32, gdal.GDT_Float64, gdal.GDT_CFloat32, gdal.GDT_CFloat64]:
                icon = QIcon(':/enmapbox/icons/filelist_regression.png')
        else:
            icon = QIcon(':/enmapbox/icons/mIconRasterLayer.png')
        self.setIcon(icon)

    def createUnregisteredMapLayer(self, *args, **kwargs):
        """
        creates and returns a QgsRasterLayer from self.src
        :return:
        """
        baseName = kwargs.get('baseName', self.mName)
        providerKey = kwargs.get('providerKey', 'gdal')
        loadDefaultStyleFlag = kwargs.get('loadDefaultStyleFlag', True)
        return QgsRasterLayer(self.mUri, baseName, providerKey, loadDefaultStyleFlag)


class DataSourceVector(DataSourceSpatial):
    def __init__(self, uri,  name=None, icon=None ):
        super(DataSourceVector, self).__init__(uri, name, icon)

        lyr = self.createUnregisteredMapLayer()
        geomType = lyr.geometryType()

        if geomType in [QGis.Point]:
            self.mIcon = QIcon(':/enmapbox/icons/mIconPointLayer.png')
        elif geomType in [QGis.Line]:
            self.mIcon = QIcon(':/enmapbox/icons/mIconLineLayer.png')
        elif geomType in [QGis.Polygon]:
            self.mIcon = QIcon(':/enmapbox/icons/mIconPolygonLayer.png')

    def createUnregisteredMapLayer(self, *args, **kwargs):
        """
        creates and returns a QgsVectorLayer from self.src
        :return:
        """
        baseName = kwargs.get('baseName', self.mName)
        providerKey = kwargs.get('providerKey', 'ogr')
        loadDefaultStyleFlag = kwargs.get('loadDefaultStyleFlag', True)
        return QgsVectorLayer(self.mUri, baseName, providerKey, loadDefaultStyleFlag)




class DataSourceListModel(QAbstractListModel):


    def __init__(self, *args, **kwds):

        super(DataSourceListModel, self).__init__(*args, **kwds)

        self.mFiles = []
        self.mAddedFiles = []
        self.mFileType = 'ANY'
        self.mAddToEnMAPBox = True

        from enmapbox.gui.enmapboxgui import EnMAPBox
        if isinstance(EnMAPBox.instance(), EnMAPBox):
            EnMAPBox.instance().dataSourceManager.sigDataSourceAdded.connect(self.refreshDataSources)
        self.refreshDataSources()

    def setSourceType(self, fileType):
        from enmapbox.gui.datasourcemanager import DataSourceManager
        assert fileType in DataSourceManager.SOURCE_TYPES
        self.mFileType = fileType
        self.refreshDataSources()

    def addSource(self, uri):
        from enmapbox.gui.datasources import DataSourceFactory, DataSource, DataSourceRaster, DataSourceVector, HubFlowDataSource

        ds = DataSourceFactory.Factory(uri)
        if isinstance(ds, DataSource):
            #is is a DataSource the EnMAP-Box can handle
            #SOURCE_TYPES = ['ALL', 'RASTER', 'VECTOR', 'MODEL']
            if self.mFileType in ['ALL','ANY'] or \
                (self.mFileType == 'RASTER' and isinstance(ds, DataSourceRaster)) or \
                (self.mFileType == 'VECTOR' and isinstance(ds, DataSourceVector)) or \
                (self.mFileType == 'MODEL' and isinstance(ds, HubFlowDataSource)):

                self.mAddedFiles.append(ds.uri())

                from enmapbox.gui.enmapboxgui import EnMAPBox
                if self.mAddToEnMAPBox and isinstance(EnMAPBox.instance(), EnMAPBox):
                    EnMAPBox.instance().addSource(ds)


    def refreshDataSources(self):
        from enmapbox.gui.enmapboxgui import EnMAPBox
        if isinstance(EnMAPBox.instance(), EnMAPBox):
            enmapBox = EnMAPBox.instance()
            uris = enmapBox.dataSourceManager.getUriList(self.mFileType)
            del self.mFiles[:]
            self.mFiles.extend(self.mAddedFiles)
            for uri in uris:
                if uri not in self.mFiles:
                    self.mFiles.append(uri)
            self.layoutChanged.emit()

    def rowCount(self, index):
        return len(self.mFiles)

    def data(self,index, role=Qt.DisplayRole):
        if role is None or not index.isValid():
            return None

        file = self.mFiles[index.row()]
        value = None
        if role == Qt.DisplayRole:
            value = os.path.basename(file)
        elif role == Qt.ToolTipRole:
            value = file
        elif role == Qt.UserRole:
            value = file
        elif role == Qt.EditRole:
            value = file
        elif role == Qt.ForegroundRole:
            if os.path.exists(file):
                value = QColor('black')
            else:
                value = QColor('red')
        return value

    def setData(self, index, value, role=None):
        if role is None or not index.isValid():
            return None


        s = ""

        return False

    def uri2index(self, uri):
        from enmapbox.gui.datasources import DataSource
        if isinstance(uri, DataSource):
            uri = uri.uri()

        uri = str(uri)
        for i in range(self.rowCount(None)):
            index = self.createIndex(0, i)
            modelUri = str(self.data(index, role=Qt.UserRole))
            if uri == modelUri:
                return index
        return None

    def index2uri(self, index):
        if index.isValid():
            return self.mFiles[index.row()]
        else:
            return None
    def flags(self, index ):
        if index.isValid():
            uri = self.index2uri(index)

            flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable

            flags = flags | Qt.ItemIsEditable
            return flags

        return None

