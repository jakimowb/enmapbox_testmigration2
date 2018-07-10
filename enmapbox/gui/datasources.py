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
import sys, os, re, collections, uuid

from qgis.core import *
from qgis.gui import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtXml import *
from enmapbox.gui.utils import *
import numpy as np
from osgeo import gdal, ogr


def rasterProvider(uri:str) -> str:
    """
    Return the raster provider key with which the uri can be opened as QgsRasterLayer
    :param uri: str
    :return: str, Provider key, e.g. "gdal"
    """
    #'DB2', 'WFS', 'arcgisfeatureserver', 'arcgismapserver', 'delimitedtext', 'gdal', 'geonode', 'gpx', 'mdal', 'memory', 'mesh_memory', 'mssql', 'ogr', 'oracle', 'ows', 'postgres', 'spatialite', 'virtual', 'wcs', 'wms']

    providers = []
    if os.path.isfile(uri) or uri.startswith('/vsimem'):
        providers.append('gdal')
    if re.search('url=', uri):
        providers.append('wms')
        providers.append('wcs')

    for p in providers:
        lyr = QgsRasterLayer(uri, '', p)
        if lyr.isValid():
            return lyr.providerType()
    return None


def vectorProvider(uri:str) -> str:
    """
    Returns the vector data provider keys whith which the uri can be opened as QgsVectorLayer
    :param uri: str
    :return: str, Provider key, e.g. "ogr"
    """
    #'DB2', 'WFS', 'arcgisfeatureserver', 'arcgismapserver', 'delimitedtext', 'gdal', 'geonode', 'gpx', 'mdal', 'memory', 'mesh_memory', 'mssql', 'ogr', 'oracle', 'ows', 'postgres', 'spatialite', 'virtual', 'wcs', 'wms']


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

class DataSourceFactory(object):

    SUBDATASETPREFERENCES = {}

    @staticmethod
    def srcToString(src)->str:
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
    def isVectorSource(src)->str:
        """
        Returns the source uri if it can be handled as known vector data source.
        :param src: any type
        :return: uri (str) | None
        """
        if isinstance(src, QgsVectorLayer) and src.isValid():
            return DataSourceFactory.isVectorSource(src.dataProvider())
        if isinstance(src, QgsVectorDataProvider):
            return DataSourceFactory.srcToString(src.dataSourceUri()).split('|')[0]
        if isinstance(src, QgsLayerTreeLayer):
            return DataSourceFactory.isVectorSource(src.layer())
        if isinstance(src, ogr.DataSource):
            return DataSourceFactory.isVectorSource(src.GetName())
        if isinstance(src, str):
            src = DataSourceFactory.srcToString(src)
            if vectorProvider(src):
                return src

        return None

    @staticmethod
    def isRasterSource(src)->str:
        """
        Returns the source uri string if it can be handled as known raster data source.
        :param src: any type
        :return: uri (str) | None
        """

        gdal.UseExceptions()
        if isinstance(src, QgsRasterLayer) and src.isValid():
            return DataSourceFactory.isRasterSource(src.dataProvider())
        if isinstance(src, QgsRasterDataProvider):
            return DataSourceFactory.isRasterSource(src.dataSourceUri())
        if isinstance(src, QgsLayerTreeLayer):
            return DataSourceFactory.isRasterSource(src.layer())
        if isinstance(src, gdal.Dataset):
            if 'DERIVED_SUBDATASETS' in src.GetMetadataDomainList():
                return DataSourceFactory.isRasterSource(src.GetDescription())
            else:
                return DataSourceFactory.isRasterSource(src.GetFileList()[0])
            """
            subDataSets = src.GetSubDatasets()

            if len(subDataSets) == 0:
                uri = src.GetFileList()[0]
            else:
                #this is a container format (S2 Driver, HDF)

                #1. describe the container type
                import collections
                subdatasets = collections.OrderedDict()
                for s in subDataSets:
                    subsetPath, description = s
                    itemKey = subsetPath.replace(src.GetFileList()[0], '')
                    subdatasets[itemKey] = subsetPath
                containerType = '{}::{}'.format(src.GetDriver().ShortName,
                                             ':'.join(subdatasets.keys()))

                #known key? than use this sub-dataset
                if containerType in DataSourceFactory.SUBDATASETPREFERENCES.keys():
                    itemKey = DataSourceFactory.SUBDATASETPREFERENCES[containerType]
                    uri = subdatasets[itemKey]

                else:
                    #ask how to handle subdatasets
                    itemKey, accepted = QInputDialog.getItem(None,"Select a subdataset",'Please select a subdataset',
                                                             subdatasets.keys(), editable=False)
                    if accepted:
                        uri = subdatasets[itemKey]
            """


        src = DataSourceFactory.srcToString(src)
        if rasterProvider(src):
            return src
        else:
            return None


    @staticmethod
    def isSpeclib(src)->str:
        uri = None
        src = DataSourceFactory.srcToString(src)
        if not src is None and os.path.exists(src):
            from enmapbox.gui.spectrallibraries import AbstractSpectralLibraryIO
            for cls in AbstractSpectralLibraryIO.__subclasses__():
                if cls.canRead(src):
                    uri = src
                    break
        return uri


    @staticmethod
    def isHubFlowObj(src)->str:
        """
        Returns the source uri if it can be handled as known data source.
        :param src: any type
        :return: uri (str) | None
        """

        src = DataSourceFactory.srcToString(src)
        if not src is None and os.path.exists(src):
            import hubflow.core
            obj = hubflow.core.FlowObject.unpickle(src, raiseError=False)
            if isinstance(obj, hubflow.core.FlowObject):
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
    def Factory(src, name=None, icon=None)->list:
        """
        Factory method / switch to return the best suited DataSource Instance(s) to an unknown source
        :param source: anything
        :param name: name, optional
        :param icon: QIcon, optional
        :return: [list-of-datasources]
        """

        if isinstance(src, list):
            sources = []
            for s in src:
                sources.extend(DataSourceFactory.Factory(s, name=name, icon=icon))
            return sources
        else:

            if src is None or isinstance(src, str) and len(src) == 0:
                return []

            elif isinstance(src, DataSource):
                return [src]

            elif type(src) in [str, QUrl]:
                src = DataSourceFactory.srcToString(src)

            # is it a Raster?
            uri = DataSourceFactory.isRasterSource(src)
            if uri:
                pkey = rasterProvider(uri)
                rasterUris = []
                if pkey == 'gdal':
                    # check for raster containers, like HDFs, and handle them separately
                    ds = gdal.Open(src)
                    subs = ds.GetSubDatasets()
                    if ds.RasterCount > 0:
                        rasterUris.append(uri)
                    if len(subs) > 0:
                        rasterUris.extend([s[0] for s in subs])
                else:
                    rasterUris.append(src)
                return [DataSourceRaster(r, name=name, icon=icon, providerKey=pkey) for r in rasterUris]

            # is it a Vector?
            uri = DataSourceFactory.isVectorSource(src)
            if uri is not None:
                vectorUris = []
                vectorUris.append(uri)
                return [DataSourceVector(r, name=name, icon=icon) for r in vectorUris]

            # is it a Speclib?
            uri = DataSourceFactory.isSpeclib(src)
            if uri is not None:
                return [DataSourceSpectralLibrary(uri, name=name, icon=icon)]

            #is it a hub flow object?
            uri = DataSourceFactory.isHubFlowObj(src)
            if uri is not None:
                return [HubFlowDataSource(uri, name=name, icon=icon)]

            #other file formats
            src = DataSourceFactory.srcToString(src)
            if not src is None:
                if os.path.isfile(src):
                    ext = os.path.splitext(src)[1].lower()
                    if ext in ['.csv', '.txt']:
                        return [DataSourceTextFile(src, name=name, icon=icon)]
                    if ext in ['.xml', '.html']:
                        return [DataSourceXMLFile(src, name=name, icon=icon)]
                    return [DataSourceFile(src, name=name, icon=icon)]

            return []



class DataSource(object):
    """Base class to describe file/stream/IO sources as used in EnMAP-GUI context"""


    sigMetadataChanged = pyqtSignal()

    def __init__(self, uri, name=None, icon=None):
        """
        :param uri: uri of data source. must be a string
        :param name: name as it appears in the source file list
        """
        assert isinstance(uri, str)
        self.mUuid = uuid.uuid4()
        self.mUri = ''
        self.mIcon = None
        self.mName = ''
        self.setUri(uri)
        self.mMetadata = {}


    def isSameSource(self, dataSource)->bool:
        assert isinstance(dataSource, DataSource)
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

        if os.path.isfile(self.mUri):
            return QFileInfo(self.mUri).lastModified()
        else:
            return QDateTime(0,0,0,0,0,0)


    def isNewVersionOf(self, dataSource)->bool:
        """
        Checks of if THIS data source is a newer version of 'dataSource'
        :param dataSource: DataSource
        :return: True | False
        """
        if type(dataSource) != type(self):
            return False
        assert isinstance(dataSource, DataSourceFile)
        if self.mUri != dataSource.mUri:
            return False
        return self.modificationTime() > dataSource.modificationTime()

    def updateMetadata(self, icon=None, name=None):
        """
        Updates metadata from the file source.
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
        return 'DataSource: {} {}'.format(self.mName, self.mUri)

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
        super(DataSourceSpatial, self).__init__(uri, name, icon)

        self.mProvider = None
        self.spatialExtent = None

    def createUnregisteredMapLayer(self, *args, **kwds)->QgsMapLayer:
        """
        creates and returns a QgsMapLayer from self.src
        the QgsMapLayer should be not registered in the QgsMapLayerRegistry
        to be implemented by inherited classes
        :return:
        """
        raise NotImplementedError()


    def modificationTime(self)->QDateTime:
        s = ""


class HubFlowDataSource(DataSourceFile):
    def __init__(self, uri, name=None, icon=None):
        super(HubFlowDataSource, self).__init__(uri, name, icon)

        if not isinstance(icon, QIcon):
            self.mIcon = QIcon(':/enmapbox/icons/alg.svg')


        self.loadFlowObject()
        s = ""

    def loadFlowObject(self):
        import hubflow.core
        self.mFlowObj = hubflow.core.FlowObject.unpickle(self.mUri, raiseError=False)


    def flowObject(self):
        import hubflow.core
        if not isinstance(self.mFlowObj, hubflow.core.FlowObject):
            self.loadFlowObject()
        if isinstance(self.mFlowObj, hubflow.core.FlowObject):
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
        self.mSpeclib.setName(os.path.basename(self.mUri))
        self.setName(self.mSpeclib.name())
        #self.nProfiles = len(slib)
        #self.profileNames = []
        #for p in slib:
        #    assert isinstance(p, SpectralProfile)
        #    self.profileNames.append(p.name())


class DataSourceRaster(DataSourceSpatial):

    def __init__(self, uri:str, name:str=None, icon=None, providerKey:str=None):
        super(DataSourceRaster, self).__init__(uri, name, icon, providerKey)
        self.nSamples = -1
        self.nBands = -1
        self.nLines = -1
        self.mDataType = -1
        self.mPxSize = QSizeF()
        self.mProvider=providerKey
        self.mDatasetMetadata = collections.OrderedDict()
        self.mBandMetadata = []
        self.updateMetadata()


    def modificationTime(self)->QDateTime:


        if self.mProvider == 'gdal':
            dataSet = gdal.Open(self.mUri)
            times = []
            if isinstance(dataSet, gdal.Dataset):
                    for path in dataSet.GetFileList():
                        if os.path.exists(path):
                            times.append(QFileInfo(path).lastModified())

            if len(times) > 0:
                return max(times)

        #Fallback
        return super(DataSourceRaster, self).modificationTime()



    def updateMetadata(self, icon=None, name=None):
        super(DataSourceRaster, self).updateMetadata(icon=icon, name=None)

        lyr = self.createUnregisteredMapLayer()

        assert lyr.isValid()

        #these attributes are to be set
        self.spatialExtent = SpatialExtent.fromLayer(lyr)
        self.mBandMetadata.clear()
        self.mDatasetMetadata.clear()
        self.nBands = self.nSamples = self.nLines = -1
        self.mDataType = None

        hasClassInfo = False

        if self.mProvider == 'gdal':
            ds = gdal.Open(self.mUri)
            assert isinstance(ds, gdal.Dataset)
            self.nSamples, self.nLines = ds.RasterXSize, ds.RasterYSize
            self.nBands = ds.RasterCount

            gt = ds.GetGeoTransform()

            from enmapbox.gui.utils import px2geo
            v = px2geo(QPoint(0, 0), gt) - px2geo(QPoint(1, 1), gt)
            self.mPxSize = QSizeF(abs(v.x()), abs(v.y()))


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
                    self.mDataType = band.DataType

        else:
            #Fallback
            lyr = self.createUnregisteredMapLayer()
            self.mPxSize = QSizeF(lyr.rasterUnitsPerPixelX(), lyr.rasterUnitsPerPixelY())
            self.nBands = lyr.bandCount()
            self.nSamples = lyr.width()
            self.nLines = lyr.height()
            self.mDatasetMetadata['Description'] = lyr.dataProvider().description()
            self.mDatasetMetadata['Source'] = lyr.dataProvider().dataSourceUri()
            #according to qgis.h the Qgis.DataType value is a "modified and extended copy of GDALDataType".
            self.mDataType = int(lyr.dataProvider().dataType(1))

        #update the datassource icon
        if hasClassInfo is True:
            icon = QIcon(':/enmapbox/icons/filelist_classification.svg')
        elif self.mDataType in [gdal.GDT_Byte] and ds.RasterCount == 1:
            icon = QIcon(':/enmapbox/icons/filelist_mask.svg')
        elif self.nBands == 1:
            icon = QIcon(':/enmapbox/icons/filelist_regression.svg')
        else:
            icon = QIcon(':/enmapbox/icons/filelist_image.svg')
        self.setIcon(icon)

    def createUnregisteredMapLayer(self)->QgsRasterLayer:
        """
        Creates a QgsRasterLayer from self.mUri and self.mProvider
        :return: QgsRasterLayer
        """
        return QgsRasterLayer(self.mUri, self.mName, self.mProvider)


class DataSourceVector(DataSourceSpatial):
    def __init__(self, uri,  name=None, icon=None, providerKey:str=None):
        super(DataSourceVector, self).__init__(uri, name, icon, providerKey)

        lyr = self.createUnregisteredMapLayer()
        geomType = lyr.geometryType()

        if geomType in [QgsWkbTypes.PointGeometry]:
            self.mIcon = QIcon(':/enmapbox/icons/mIconPointLayer.svg')
        elif geomType in [QgsWkbTypes.LineGeometry]:
            self.mIcon = QIcon(':/enmapbox/icons/mIconLineLayer.svg')
        elif geomType in [QgsWkbTypes.PolygonGeometry]:
            self.mIcon = QIcon(':/enmapbox/icons/mIconPolygonLayer.svg')

    def createUnregisteredMapLayer(self)->QgsVectorLayer:
        """
        creates and returns a QgsVectorLayer from self.src
        :return:
        """
        return QgsVectorLayer(self.mUri, self.mName, self.mProvider)


    def updateMetadata(self, *args, **kwds):
        super(DataSourceVector, self).updateMetadata(*args, **kwds)
        lyr = self.createUnregisteredMapLayer()

        s = ""


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

        dataSources = DataSourceFactory.Factory(uri)
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
