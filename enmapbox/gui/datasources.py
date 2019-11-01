# -*- coding: utf-8 -*-
# noinspection PyPep8Naming
"""
***************************************************************************
    datasources.py
    ---------------------
    Date                 : August 2017
    Copyright            : (C) 2017 by Benjamin Jakimow
    Email                : benjamin.jakimow@geo.hu-berlin.de
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
import collections, uuid, pathlib, typing, time
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from enmapbox.gui import *
from enmapbox.gui import subLayerDefinitions, openRasterLayerSilent
from enmapbox.gui.utils import *
from ..externals.qps.layerproperties import defaultRasterRenderer
from osgeo import gdal, ogr

def rasterProvider(uri:str) -> str:
    """
    Return the raster provider key with which the uri can be opened as QgsRasterLayer
    :param uri: str
    :return: str, Provider key, e.g. "gdal"
    """
    #'DB2', 'WFS', 'arcgisfeatureserver', 'arcgismapserver', 'delimitedtext', 'gdal', 'geonode', 'gpx', 'mdal', 'memory', 'mesh_memory', 'mssql', 'ogr', 'oracle', 'ows', 'postgres', 'spatialite', 'virtual', 'wcs', 'wms']

    if uri in [None, type(None)]:
        return None


    providers = []

    if os.path.isfile(uri) or uri.startswith('/vsimem'):
        providers.append('gdal')
    if re.search('url=', uri):
        providers.append('wms')
        providers.append('wcs')

    for p in providers:
        loptions = QgsRasterLayer.LayerOptions(loadDefaultStyle=False)
        lyr = QgsRasterLayer(uri, '', p, options=loptions)
        if lyr.isValid() or len(lyr.subLayers()) > 0:
            return lyr.providerType()
    return None


def vectorProvider(uri:str) -> str:
    """
    Returns the vector data provider keys whith which the uri can be opened as QgsVectorLayer
    :param uri: str
    :return: str, Provider key, e.g. "ogr"
    """
    #'DB2', 'WFS', 'arcgisfeatureserver', 'arcgismapserver', 'delimitedtext', 'gdal', 'geonode', 'gpx', 'mdal', 'memory', 'mesh_memory', 'mssql', 'ogr', 'oracle', 'ows', 'postgres', 'spatialite', 'virtual', 'wcs', 'wms']
    if uri in [None, type(None)]:
        return None

    providers = ['ogr', 'WFS', 'spatialite', 'gpx', 'delimitedtext']

    #change order of providers assuming a faster match
    if not os.path.isfile(uri):
        providers.append(providers.pop(0))
    if re.search('url=', uri):
        providers.insert(0,providers.pop(providers.index('WFS')))

    for p in providers:
        lyr = QgsVectorLayer(uri, '', p)
        if lyr.isValid():
            return lyr.providerType()
    return None

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

class DataSource(object):
    """Base class to describe file/stream/IO sources"""

    sigMetadataChanged = pyqtSignal()

    __refs__ = []
    @classmethod
    def instances(cls):
        """
        Returns all DataSource instances
        :return: [list-of-DataSources]
        """
        #1. clean list of instances
        DataSource.__refs__ = [r for r in DataSource.__refs__ if r() is not None]
        for r in DataSource.__refs__:
            if r is not None:
                yield r()

    @classmethod
    def fromUUID(self, uuid:uuid.UUID):
        """
        Returns the DataSource with given uuid
        :param uuid: UUID
        :return:
        """
        for ds in DataSource.instances():
            assert isinstance(ds, DataSource)
            if ds.uuid() == uuid:
                return ds
        return None

    def __init__(self, uri, name='', icon=None):
        """
        :param uri: uri of data source. must be a string
        :param name: name as it appears in the source file list
        """
        assert isinstance(uri, str)
        self.mUuid = uuid.uuid4()
        self.mUri = ''
        self.mIcon = icon
        self.mName = name
        self.setUri(uri)
        self.mMetadata = {}

        if os.path.isfile(self.mUri):
            self.mModificationTime = QFileInfo(self.mUri).lastModified()
        else:
            self.mModificationTime = QDateTime(0,0,0,0,0,0)

        self.__refs__.append(weakref.ref(self))

    def isSameSource(self, dataSource)->bool:
        """
        Returns True if the dataSource points to the same source
        :param dataSource: DataSource
        :return: bool
        """
        assert isinstance(dataSource, DataSource)

        try:
            p1 = pathlib.Path(self.mUri).as_posix()
            p2 = pathlib.Path(dataSource.mUri).as_posix()
            return p1 == p2
        except:
            pass
        return self.mUri == dataSource.mUri

    def setUri(self, uri:str):
        """
        Sets the unified ressource identifier (uri) of this data source
        """
        assert isinstance(uri, str)
        self.mUri = uri

    def modificationTime(self)->QDateTime:
        """
        Optimally returns the last time the data of the data source has been changed.
        :return: QDateTime
        """
        return self.mModificationTime


    def isNewVersionOf(self, dataSource)->bool:
        """
        Checks of if THIS data source is a newer version of 'dataSource'
        :param dataSource: DataSource
        :return: True | False
        """
        if type(dataSource) != type(self):
            return False
        if self.mUri != dataSource.mUri:
            return False
        return self.modificationTime() > dataSource.modificationTime()

    def updateMetadata(self, icon=None, name=None):
        """
        Updates metadata from the file source.
        """
        if icon is None:
            icon = self.icon()

        if name is None:
            name = self.name()


        if icon is None:
            provider = QFileIconProvider()
            icon = provider.icon(QFileInfo(self.mUri))

        if name is None:
            name = os.path.basename(self.mUri)
        assert name is not None
        assert isinstance(icon, QIcon)

        self.setName(name)
        self.setIcon(icon)

    def __eq__(self, other):
        return other is not None and \
               self.uri() == other.uri()

    def uuid(self):
        """
        Returns the Unique Identifier that was created when initializing this object.
        :return: UUID
        """
        return self.mUuid

    def uri(self)->str:
        """Returns the URI string that describes the data source"""
        return self.mUri

    def setIcon(self, icon):
        """
        Sets the DataSource Icon
        :param icon: valid constructor argument to QIcon(), i.e. QPixmap, QIconm str, QIconEngine
        """
        self.mIcon = icon

    def icon(self)->QIcon:
        """
        Returns the icon associated with the data source
        :return: QIcon
        """
        return QIcon(self.mIcon)

    def setIcon(self, icon):
        """
        Sets the DataSource Icon
        :param icon:
        :return:
        """
        assert isinstance(icon, QIcon)
        self.mIcon = icon
        return self

    def setName(self, name):
        """
        Sets the datasource name. Override it to allow and apply for changes of the base-name
        :param name:
        :return: self
        """
        assert isinstance(name, str)
        self.mName = name
        return self

    def name(self)->str:
        """
        :return: name of DataSource
        """
        return self.mName

    def writeXml(self, element):
        """
        Override this to write
        :param element:
        :return:
        """
        assert isinstance(element, QDomElement)
        doc = element.ownerDocument()
        node = doc.createElement('enmpabox_datasource')
        element.appendChild(node)
        node.setAttribute('type', self.__class__.__name__)
        node.setAttribute('name', str(self.name()))
        node.setAttribute('uuid', str(self.uuid()))
        node.setAttribute('source', str(self.uri()))

    def __hash__(self):
        return hash(str(self))

    def __repr__(self):

        return '{}: {} {}'.format(self.__class__.__name__, self.mName, self.mUri)

class DataSourceFile(DataSource):
    """
    Description of local files
    """
    def __init__(self, uri:str, name:str=None, icon=None):
        assert os.path.isfile(uri)
        super(DataSourceFile, self).__init__(uri, name, icon)


class DataSourceTextFile(DataSourceFile):
    """
    Class to handle editable local text files
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
    Abstract class to describe spatial data from local files but also web sources
    """
    def __init__(self, uri, name=None, icon=None, providerKey:str=None):

        super(DataSourceSpatial, self).__init__(uri, name=name, icon=icon)
        assert isinstance(providerKey, str) and providerKey in QgsProviderRegistry.instance().providerList()

        self.mProvider = providerKey
        self.mLayer = None

    def mapLayer(self)->QgsMapLayer:
        return self.mLayer

    def provider(self)->str:
        """
        Returns the provider name
        :return: str
        """
        return self.mProvider

    def spatialExtent(self)->SpatialExtent:
        """
        Returns the SpatialExtent of this data source.
        :return: SpatailExtent
        """
        return SpatialExtent.fromLayer(self.createUnregisteredMapLayer())


    def createUnregisteredMapLayer(self, *args, **kwds)->QgsMapLayer:
        """
        creates and returns a QgsMapLayer from self.src
        the QgsMapLayer should not be registered in the QgsMapLayerRegistry
        to be implemented by inherited classes
        :return:
        """
        raise NotImplementedError()





class HubFlowDataSource(DataSource):

    @staticmethod
    def createID(obj)->str:
        import hubflow.core
        assert isinstance(obj, hubflow.core.FlowObject)
        attr = getattr(obj, 'filename', None)
        uri = attr() if callable(attr) else ''

        return 'hubflow:{}:{}:{}'.format(obj.__class__.__name__, id(obj), uri)

    def __init__(self, obj, name=None, icon=None):
        id = HubFlowDataSource.createID(obj)
        super(HubFlowDataSource, self).__init__(id, name, icon)

        if not isinstance(icon, QIcon):
            self.mIcon = QIcon(':/enmapbox/gui/ui/icons/processingAlgorithm.svg')

        self.mFlowObj = obj

        s = ""

    def flowObject(self):
        return self.mFlowObj




class DataSourceSpectralLibrary(DataSourceSpatial):

    def __init__(self, uri, name=None, icon=None):
        if icon is None:
            icon = QIcon(':/qps/ui/icons/speclib.svg')
        super(DataSourceSpectralLibrary, self).__init__(uri, name, icon, providerKey='ogr')

        self.mSpeclib = SpectralLibrary.readFrom(self.mUri)
        if not isinstance(self.mSpeclib, SpectralLibrary):
            raise Exception('Unable to read SpectraLibrary from {}'.format(self.mUri))

        self.mSpeclib.setCustomProperty('ENMAPBOX_DATASOURCE', True)
        self.nProfiles = 0
        self.profileNames = []
        self.updateMetadata()

    def createUnregisteredMapLayer(self, *args, **kwds)->QgsVectorLayer:
        return QgsVectorLayer(self.mSpeclib.source(), self.mSpeclib.name(), self.mProvider)
        #return self.spectralLibrary()

    def updateMetadata(self, *args, **kwds):
        if isinstance(self.mSpeclib, SpectralLibrary):
            self.mSpeclib.setName(os.path.basename(self.mUri))
            self.setName(self.mSpeclib.name())

            self.nProfiles = len(self.mSpeclib)
            self.profileNames = []
            for p in self.mSpeclib.profiles():
                assert isinstance(p, SpectralProfile)
                self.profileNames.append(p.name())

    def speclib(self)->SpectralLibrary:
        """
        :return: SpectralLibrary
        """
        return self.mSpeclib


class DataSourceRaster(DataSourceSpatial):

    def __init__(self, uri:str, name:str=None, icon=None, providerKey:str=None):

        super(DataSourceRaster, self).__init__(uri, name=name, icon=icon, providerKey=providerKey)

        self.mDefaultRenderer = None
        self.mLayer = self.createUnregisteredMapLayer()
        assert isinstance(self.mLayer, QgsRasterLayer)
        self.mLayer.setCustomProperty('ENMAPBOX_DATASOURCE',True)

        #self.mDataType = -1
        #self.mPxSize = QSizeF()
        #self.mDatasetMetadata = collections.OrderedDict()
        self.mBandMetadata = []

        self.mDatasetMetadata = {}

        self.mWaveLengths = []
        self.mWaveLengthUnits = []
        self.updateMetadata()

    def mapLayer(self)->QgsRasterLayer:
        return self.mLayer

    def pixelSize(self)->QSizeF:
        return QSizeF(self.mLayer.rasterUnitsPerPixelX(), self.mLayer.rasterUnitsPerPixelY())

    def dataType(self)->Qgis.DataType:
        """
        Returns the data type of the first band.
        :return: Qgis.DataType
        """
        return self.mLayer.dataProvider().dataType(1)

    def nSamples(self)->int:
        """Returns the number of samples / columns / pixels in y direction"""
        return self.mLayer.width()

    def nLines(self)->int:
        """Returns the number of lines / rows / pixels in y direction"""
        return self.mLayer.height()

    def nBands(self)->int:
        return self.mLayer.bandCount()



    def updateMetadata(self, icon=None, name=None):
        super(DataSourceRaster, self).updateMetadata(icon=icon, name=None)

        self.mLayer.reload()

        if name is None and self.mProvider == 'wms':
            self.setName('WMS:' + self.name())

        if self.mProvider == 'gdal':
            dataSet = gdal.Open(self.mUri)
            if isinstance(dataSet, gdal.Dataset):
                statsInfo = gdal.VSIStatL(dataSet.GetFileList()[0])
                if isinstance(statsInfo, gdal.StatBuf):
                    dt = QDateTime()
                    dt.setSecsSinceEpoch(statsInfo.mtime)
                else:
                    print('Unable to get file create time')
                    dt = QDateTime.currentDateTime()

                self.mModificationTime = dt


        #these attributes are to be set

        self.mBandMetadata.clear()
        self.mDatasetMetadata.clear()
        #self.nBands = self.nSamples = self.nLines = -1
        #self.mDataType = None
        self.mWaveLengths, self.mWaveLengthUnits =  parseWavelength(self.mapLayer())


        hasClassInfo = False

        if self.mProvider == 'gdal':
            ds = gdal.Open(self.mUri)
            assert isinstance(ds, gdal.Dataset)
            #self.nSamples, self.nLines = ds.RasterXSize, ds.RasterYSize
            #self.nBands = ds.RasterCount

            #gt = ds.GetGeoTransform()


            #v = px2geo(QPoint(0, 0), gt) - px2geo(QPoint(1, 1), gt)
            #self.mPxSize = QSizeF(abs(v.x()), abs(v.y()))


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


            for b in range(ds.RasterCount):
                band = ds.GetRasterBand(b+1)
                assert isinstance(band, gdal.Band)
                #bandName = band.GetDescription()
                #if len(bandName) == 0:
                #    bandName = 'Band {}'.format(b+1)
                #self.mBandNames.append(bandName)

                cs = ClassificationScheme.fromRasterImage(ds, b)
                md = fetchMetadata(band)
                if isinstance(cs, ClassificationScheme):
                    hasClassInfo = True
                    md['__ClassificationScheme__'] = cs

                self.mBandMetadata.append(md)

                #if b == 0:
                #    self.mDataType = band.DataType

        else:
            #Fallback
            #lyr = self.createUnregisteredMapLayer()
            #self.mPxSize = QSizeF(lyr.rasterUnitsPerPixelX(), lyr.rasterUnitsPerPixelY())
            #self.nBands = lyr.bandCount()
            #self.nSamples = lyr.width()
            #self.nLines = lyr.height()
            self.mDatasetMetadata['Description'] = self.mapLayer().dataProvider().description()
            self.mDatasetMetadata['Source'] = self.mapLayer().source()
            #according to qgis.h the Qgis.DataType value is a "modified and extended copy of GDALDataType".
            #self.mDataType = int(lyr.dataProvider().dataType(1))

            for b in range(self.nBands()):
                bandMeta = {}
                self.mBandMetadata.append(bandMeta)
                #self.mBandNames.append(lyr.bandName(b+1))

        #update the datassource icon
        if hasClassInfo is True:
            icon = QIcon(':/enmapbox/gui/ui/icons/filelist_classification.svg')
        elif self.dataType() in [Qgis.Byte] and self.nBands() == 1:
            icon = QIcon(':/enmapbox/gui/ui/icons/filelist_mask.svg')
        elif self.nBands() == 1:
            icon = QIcon(':/enmapbox/gui/ui/icons/filelist_regression.svg')
        else:
            icon = QIcon(':/enmapbox/gui/ui/icons/filelist_image.svg')
        self.setIcon(icon)


    def isNewVersionOf(self, dataSource)->bool:
        """
        Checks of if THIS raster data source is a newer version of 'dataSource'
        :param dataSource: DataSource
        :return: True | False
        """

        if type(dataSource) != type(self):
            return False
        if self.mUri != dataSource.mUri:
            return False


        if super(DataSourceRaster, self).isNewVersionOf(dataSource):
            assert isinstance(dataSource, DataSourceRaster)
            return self.nSamples() == dataSource.nSamples() \
                and self.nLines() == dataSource.nLines() \
                and self.nBands() == dataSource.nBands() \
                and self.pixelSize() == dataSource.pixelSize() \
                and self.dataType() == dataSource.dataType()


    def createUnregisteredMapLayer(self)->QgsRasterLayer:
        """
        Creates a QgsRasterLayer from self.mUri and self.mProvider. Avoids time-consuming initialization routines.
        :return: QgsRasterLayer
        """
        key = '/Projections/defaultBehavior'
        v = QgsSettings().value(key)
        isPrompt = v == 'prompt'

        if isPrompt:
            # do not ask!
            QgsSettings().setValue(key, 'useProject')

        loptions = QgsRasterLayer.LayerOptions(loadDefaultStyle=False)
        lyr = QgsRasterLayer(self.mUri, self.mName, self.mProvider, options=loptions)

        if False:
            if isinstance(self.mapLayer(), QgsRasterLayer) and not isinstance(self.mDefaultRenderer, QgsRasterRenderer):

                self.mDefaultRenderer = defaultRasterRenderer(self.mapLayer(), bandIndices=defaultBands(self.mapLayer()))
                self.mDefaultRenderer.setInput(self.mapLayer().dataProvider())

            if isinstance(self.mDefaultRenderer, QgsRasterRenderer):
                r = self.mDefaultRenderer.clone()
                r.setInput(lyr.dataProvider())
                lyr.setRenderer(r)

        if isPrompt:
            QgsSettings().setValue(key, v)

        return lyr


class DataSourceVector(DataSourceSpatial):
    def __init__(self, uri,  name=None, icon=None, providerKey:str=None):
        super(DataSourceVector, self).__init__(uri, name, icon, providerKey)

        if name is None:
            try:
                if providerKey == 'WFS':
                    self.setName('WFS:'+ uri)
                else:
                    self.setName(os.path.basename(uri))
            except Exception as ex:
                self.setName(str(uri))


        self.mLayer = self.createUnregisteredMapLayer()

        self.updateMetadata()


    def geometryType(self)->QgsWkbTypes:
        """
        Returns the QgsWkbTypes.GeometryType
        :return: QgsWkbTypes.GeometryType
        """
        return self.mapLayer().geometryType()

    def createUnregisteredMapLayer(self)->QgsVectorLayer:
        """
        creates and returns a QgsVectorLayer from self.src
        :return:
        """

        key = '/Projections/defaultBehavior'
        v = QgsSettings().value(key)
        isPrompt = v == 'prompt'

        if isPrompt:
            # do not ask!
            QgsSettings().setValue(key, 'useProject')

        loptions = QgsVectorLayer.LayerOptions(False, False)
        lyr = QgsVectorLayer(self.mUri, self.mName, self.mProvider, options=loptions)

        if isPrompt:
            QgsSettings().setValue(key, v)

        return lyr




    def updateMetadata(self, *args, **kwds):
        super(DataSourceVector, self).updateMetadata(*args, **kwds)

        gt = self.geometryType()
        if gt in [QgsWkbTypes.PointGeometry]:
            self.mIcon = QIcon(':/enmapbox/gui/ui/icons/mIconPointLayer.svg')
        elif gt in [QgsWkbTypes.LineGeometry]:
            self.mIcon = QIcon(':/images/themes/default/mIconLineLayer.svg')
        elif gt in [QgsWkbTypes.PolygonGeometry]:
            self.mIcon = QIcon(':/images/themes/default/mIconPolygonLayer.svg')


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

        dataSources = DataSourceFactory.create(uri)
        for ds in dataSources:
            assert isinstance(ds, DataSource)
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
            uris = enmapBox.dataSourceManager.uriList(self.mFileType)
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



class DataSourceFactory(object):

    SUBDATASETPREFERENCES = {}

    @staticmethod
    def srcToString(src)->str:
        """
        Extracts the source uri that can be used to open a new QgsMapLayer
        :param src: QUrl | str
        :return: str
        """
        if isinstance(src, QUrl):
            if src.isLocalFile():
                src = src.toLocalFile()
            else:
                src = src.path()
        if isinstance(src, str):
            #identify GDAL subdataset strings
            if re.search('(HDF|SENTINEL).*:.*:.*', src):
                src = src
            elif os.path.isfile(src):
                src = os.path.abspath(src)
            else:
                pass
        else:
            src = None
        return src

    @staticmethod
    def isVectorSource(src)->typing.Tuple[str,str]:
        """
        Tests if 'src' is a vector data source. If True, returns the uri and provider key
        :param src: any type
        :return: uri and provider key (str, str)
        """
        if isinstance(src, QgsVectorLayer) and src.isValid():
            return DataSourceFactory.isVectorSource(src.dataProvider())
        if isinstance(src, QgsVectorDataProvider):
            return DataSourceFactory.srcToString(src.dataSourceUri()).split('|')[0], src.name()
        if isinstance(src, QgsLayerTreeLayer):
            return DataSourceFactory.isVectorSource(src.layer())
        if isinstance(src, ogr.DataSource):
            return DataSourceFactory.isVectorSource(src.GetName()), 'ogr'
        if isinstance(src, str):
            src = DataSourceFactory.srcToString(src)
            provider = vectorProvider(src)
            if isinstance(provider, str):
                return src, provider

        return None, None

    @staticmethod
    def isRasterSource(src)->typing.Tuple[str, str, str]:
        """
        Returns the source uri, name and provider keys if it can be handled as known raster data source.
        :param src: any type
        :return: (str, str, str) or None
        """

        gdal.UseExceptions()

        if isinstance(src, QgsRasterLayer) and src.isValid():
            return src.source(), src.name(), src.providerType()

        if isinstance(src, QgsRasterDataProvider) and src.isValid():
            return src.dataSourceUri(), os.path.basename(src.dataSourceUri()), src.name()

        if isinstance(src, QgsLayerTreeLayer):
            return DataSourceFactory.isRasterSource(src.layer())

        if isinstance(src, gdal.Dataset):
            if 'DERIVED_SUBDATASETS' in src.GetMetadataDomainList():
                return DataSourceFactory.isRasterSource(src.GetDescription())
            else:
                return DataSourceFactory.isRasterSource(src.GetFileList()[0])
        if isinstance(src, str):
            src = DataSourceFactory.srcToString(src)
            provider = rasterProvider(src)
            if isinstance(provider, str):
                return src, os.path.basename(src), provider

        return None, None, None


    @staticmethod
    def isSpeclib(src)->typing.Tuple[str, str]:
        """
        :param src: path or object that might be a SpectralLibrary
        :return: (uri, None) if True
        """
        uri = None
        if isinstance(src, SpectralLibrary):
            uri = src.source()
        else:
            if not isinstance(src, str):
                src = DataSourceFactory.srcToString(src)

            if isinstance(src, str):
                if os.path.exists(src):

                    for cls in AbstractSpectralLibraryIO.__subclasses__():
                        if cls.canRead(src):
                            uri = src
                            break
                else:
                    s = ""
        return uri, None


    @staticmethod
    def isHubFlowObj(src)->typing.Tuple[bool, object]:
        """
        Returns the source uri if it can be handled as known hubflow data source.
        :param src: any type
        :return: uri, 'hubflow' | None, None
        """
        import hubflow.core
        if isinstance(src, hubflow.core.FlowObject):
            return True, src

        src = DataSourceFactory.srcToString(src)
        if not src is None and os.path.exists(src):
            obj = hubflow.core.FlowObject.unpickle(src, raiseError=False)
            if isinstance(obj, hubflow.core.FlowObject):
               return True, obj
        return False, None

    @staticmethod
    def fromXML(domElement:QDomElement):
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
    def Factory(*args, **kwds):
        warnings.warn(DeprecationWarning('Use DataSourceFactory.create(...) instead'))
        return DataSourceFactory.create(*args, **kwds)

    @staticmethod
    def create(src, name=None, icon=None)->typing.List[DataSource]:
        """
        Returns the best suited DataSource Instance(s) to an unknown source
        :param source: anything
        :param name: name, optional
        :param icon: QIcon, optional
        :return: [list-of-DataSources]
        """

        if isinstance(src, list):
            sources = []
            for s in src:
                sources.extend(DataSourceFactory.create(s, name=name, icon=icon))
            return sources
        else:

            if src is None or isinstance(src, str) and len(src) == 0:
                return []

            elif isinstance(src, DataSource):
                return [src]
            elif isinstance(src, QgsMimeDataUtils.Uri):
                if src.layerType == 'raster':
                    return [DataSourceRaster(src.uri, name=src.name, providerKey=src.providerKey)]
                elif src.layerType == 'vector':
                    return [DataSourceVector(src.uri, name=src.name, providerKey=src.providerKey)]


            elif type(src) in [str, QUrl]:
                src = DataSourceFactory.srcToString(src)


            if src in [None, type(None)]:
                return []

            #DataSource.instances()

            #run checks on input sources
            if isinstance(src, SpectralLibrary):
                sourceTestFunctions = [DataSourceFactory.checkForSpeclib]
            elif isinstance(src, gdal.Dataset) or isinstance(src, QgsRasterLayer):
                sourceTestFunctions = [DataSourceFactory.checkForRaster]
            elif isinstance(src, ogr.DataSource) or isinstance(src, QgsVectorLayer):
                sourceTestFunctions = [DataSourceFactory.checkForVector, DataSourceFactory.checkForSpeclib]
            elif type(src).__name__ in ['module']:
                return []
            else: #run all tests
                sourceTestFunctions = [DataSourceFactory.checkForRaster,
                                       DataSourceFactory.checkForVector,
                                       DataSourceFactory.checkForSpeclib,
                                       DataSourceFactory.checkForHubFlow,
                                       DataSourceFactory.checkOtherFiles]

                #re-order by most-likely none-raster source type according to source uri
                if isinstance(src, str):
                    guess = guessDataProvider(src)
                    if isinstance(guess, str):
                        if guess == 'enmapbox_speclib':
                            sourceTestFunctions.insert(0, sourceTestFunctions.pop(sourceTestFunctions.index(DataSourceFactory.checkForSpeclib)))
                        elif guess == 'ogr':
                            sourceTestFunctions.insert(0, sourceTestFunctions.pop(sourceTestFunctions.index(DataSourceFactory.checkForVector)))
                        elif guess == 'enmapbox_textfile':
                            sourceTestFunctions.insert(0, sourceTestFunctions.pop(sourceTestFunctions.index(DataSourceFactory.checkOtherFiles)))
                        elif guess == 'enmapbox_pkl':
                            sourceTestFunctions.insert(0, sourceTestFunctions.pop(sourceTestFunctions.index(DataSourceFactory.checkForHubFlow)))
                        elif guess == 'WFS':
                            sourceTestFunctions.insert(0, sourceTestFunctions.pop(sourceTestFunctions.index(DataSourceFactory.checkForVector)))
                    #files where we are sure we can not load them
                    elif os.path.isfile(src) and re.search(r'\.(py)$', src):
                        return []

            for sourceTestFunction in sourceTestFunctions:
                sources = sourceTestFunction(src, name=name, icon=icon)
                if len(sources) > 0:
                    return sources


            return []




    @staticmethod
    def checkForRaster(src, **kwds) -> typing.List[DataSourceRaster]:
        """
        Returns one ore more DataSourceRaster found in src
        :param src: any object
        :param kwds: DataSourceRaster-keywords
        :return: [list-of-DataSourceRaster]
        """
        uri, name, pkey = DataSourceFactory.isRasterSource(src)

        # disable CRS asking

        if uri:
            rasterUris = []
            names = []

            lyr = openRasterLayerSilent(uri, name, pkey)

            if not lyr.isValid():

                # sublayer loading
                subLayers = lyr.subLayers()

                if len(subLayers) > 0:
                    subLayerDefs = subLayerDefinitions(lyr)
                    d = QgsSublayersDialog(QgsSublayersDialog.Gdal, lyr.name())
                    d.setWindowTitle('Select Raster Sources to Add...')
                    d.populateLayerTable(subLayerDefs)

                    # open this dialog only in case we are not in a CI test

                    if os.environ.get('CI') is None:
                        if d.exec_():
                            for ldef in d.selection():
                                assert isinstance(ldef, QgsSublayersDialog.LayerDefinition)
                                names.append(ldef.layerName)
                                rasterUris.append(subLayers[ldef.layerId])

            else:

                rasterUris.append(uri)
                names.append(lyr.name())

            # create a DataSourceRaster for each source
            results = []
            for uri, name in zip(rasterUris, names):

                ds = DataSourceRaster(uri, name=name, providerKey=pkey)
                results.append(ds)
            return results
        return []

    @staticmethod
    def checkForVector(src, **kwds) -> typing.List[DataSourceVector]:
        """
        Returns one or more DataSourceVector that can be found in src
        :param src: any
        :param kwds: DataSourceVector keywords
        :return: [list-of-DataSourceVector]
        """
        uri, pkey = DataSourceFactory.isVectorSource(src)
        if uri:
            return [DataSourceVector(uri, providerKey=pkey, **kwds)]
        return []

    @staticmethod
    def checkForSpeclib(src, **kwds) -> typing.List[DataSourceSpectralLibrary]:
        """
        Returns a DataSourceSpectralLibrary from src, if possible
        :param src: any type
        :param kwds: DataSourceSpectralLibrary keywords
        :return: [list-of-DataSourceSpectralLibrary]
        """
        uri, pkey = DataSourceFactory.isSpeclib(src)
        if uri:
            return [DataSourceSpectralLibrary(uri, **kwds)]
        return []

    @staticmethod
    def checkForHubFlow(src, **kwds) -> typing.List[HubFlowDataSource]:
        """
        if possible, returns a HubFlowDataSource from src
        :param self:
        :param src:
        :param kwds:
        :return: HubFlowDataSource
        """
        isHubFlow, obj = DataSourceFactory.isHubFlowObj(src)
        if isHubFlow:
            return [HubFlowDataSource(obj, **kwds)]
        return []

    @staticmethod
    def checkOtherFiles(src, **kwds) -> typing.List[DataSourceFile]:
        """
        Returns a DataSourceFile instance from src
        :param self:
        :param src:
        :param kwds:
        :return:
        """
        src = DataSourceFactory.srcToString(src)
        if not src is None:

            if os.path.isfile(src):

                if not isinstance(kwds.get('name'), str):
                    kwds['name'] = os.path.basename(src)

                ext = os.path.splitext(src)[1].lower()
                if ext in ['.csv', '.txt']:
                    return [DataSourceTextFile(src, **kwds)]
                if ext in ['.xml', '.html']:
                    return [DataSourceXMLFile(src, **kwds)]
                return [DataSourceFile(src, **kwds)]
        return []

