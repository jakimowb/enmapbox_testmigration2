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
import collections
import pickle
import json
import warnings
import weakref
import os
import sys
import re
import typing
import pathlib
import uuid

from qgis.core import QgsFields, QgsDataItem

from qgis.PyQt.QtCore import QVariant, pyqtSignal, QDateTime, QFileInfo, QUrl, QSizeF
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QFileIconProvider
from qgis.PyQt.QtXml import QDomElement

from osgeo import gdal, ogr

from qgis.core import QgsMapLayer, QgsRasterLayer, QgsVectorLayer, \
    QgsSettings, QgsWkbTypes, Qgis, \
    QgsProviderRegistry, QgsRasterDataProvider, QgsVectorDataProvider, \
    QgsLayerTreeLayer, QgsMimeDataUtils, QgsProject
from qgis.gui import QgsSublayersDialog
from enmapbox.gui.utils import SpatialExtent, SpatialPoint, guessDataProvider
from enmapbox.gui import subLayerDefinitions, openRasterLayerSilent, \
    SpectralLibrary, ClassificationScheme
from enmapbox import debugLog, messageLog
from ..externals.qps.layerproperties import defaultRasterRenderer
from ..externals.qps.speclib.core import is_spectral_library
from ..externals.qps.utils import parseWavelength



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
        # 1. clean list of instances
        DataSource.__refs__ = [r for r in DataSource.__refs__ if r() is not None]
        for r in DataSource.__refs__:
            if r is not None:
                yield r()

    @classmethod
    def fromUUID(self, uuid: uuid.UUID):
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

        self.mMetadata = {}
        self.mDataItem: QgsDataItem = None

        if os.path.isfile(self.mUri):
            self.mModificationTime = QFileInfo(self.mUri).lastModified()
        else:
            self.mModificationTime = QDateTime(0, 0, 0, 0, 0, 0)

        self.__refs__.append(weakref.ref(self))

    def isSameSource(self, dataSource) -> bool:
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

    def modificationTime(self) -> QDateTime:
        """
        Optimally returns the last time the data of the data source has been changed.
        :return: QDateTime
        """
        return self.mModificationTime

    def isNewVersionOf(self, dataSource) -> bool:
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

    def __eq__(self, other) -> bool:
        if not isinstance(other, DataSource):
            return None
        else:
            return self.uri() == other.uri()

    def uuid(self) -> str:
        """
        Returns the Unique Identifier that was created when initializing this object.
        :return: UUID
        """
        return self.mUuid

    def uri(self) -> str:
        """Returns the URI string that describes the data source"""
        return self.mUri

    def setIcon(self, icon):
        """
        Sets the DataSource Icon
        :param icon: valid constructor argument to QIcon(), i.e. QPixmap, QIconm str, QIconEngine
        """
        self.mIcon = icon

    def icon(self) -> QIcon:
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

    def name(self) -> str:
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

    def __init__(self, uri: str, name: str = None, icon=None):
        assert os.path.isfile(uri)
        super(DataSourceFile, self).__init__(uri, name, icon)


class DataSourceTextFile(DataSourceFile):
    """
    Class to handle editable local text files
    """

    def __init__(self, uri, name=None, icon=None):
        super(DataSourceTextFile, self).__init__(uri, name, icon)


class DataSourceSpatial(DataSource):
    """
    Abstract class to describe spatial data from local files but also web sources
    """

    def __init__(self,
                 uri: str,
                 name: str = None,
                 icon: QIcon = None,
                 providerKey: str = None,
                 layer: QgsMapLayer = None):

        if isinstance(layer, QgsMapLayer):
            uri = layer.source()
            if name in [None, '']:
                if layer.providerType() == 'WFS':
                    hasTypeName = re.search(r'typename=([^ ]+)', layer.source())
                    if hasTypeName:
                        name = 'WFS:{}'.format(hasTypeName.group(1))
                    else:
                        name = 'WFS:{}'.format(layer.name())
                elif layer.providerType() == 'wms':
                    name = 'WMS:{}'.format(layer.name())
                elif layer.name() != '':
                    name = layer.name()
                else:
                    name = os.path.basename(uri)
            providerKey = layer.dataProvider().name()
        else:
            if name in [None, '']:
                name = os.path.basename(uri)

        assert isinstance(providerKey, str) and providerKey in QgsProviderRegistry.instance().providerList()

        super(DataSourceSpatial, self).__init__(uri, name=name, icon=icon)

        self.mProvider = providerKey
        self.mLayer = None
        self.mLayerId = None

    def mapLayerId(self) -> str:
        return self.mLayerId

    def mapLayer(self) -> QgsMapLayer:
        return self.mLayer

    def setMapLayer(self, layer: QgsMapLayer):
        assert isinstance(layer, QgsMapLayer)

        self.mLayer = layer
        self.mLayerId = layer.id()

    def setName(self, name: str):
        super().setName(name)
        self.mLayer.setName(name)

    def provider(self) -> str:
        """
        Returns the provider name
        :return: str
        """
        return self.mProvider

    def spatialExtent(self) -> SpatialExtent:
        """
        Returns the SpatialExtent of this data source.
        :return: SpatailExtent
        """
        return SpatialExtent.fromLayer(self.mapLayer())

    def createUnregisteredMapLayer(self, *args, **kwds) -> QgsMapLayer:
        """
        creates and returns a QgsMapLayer from self.src
        the QgsMapLayer should not be registered in the QgsMapLayerRegistry
        to be implemented by inherited classes
        :return:
        """
        raise NotImplementedError()


class HubFlowDataSource(DataSource):

    def __init__(self, obj, uri: str = None, name: str = None, icon: QIcon = None):
        if isinstance(uri, str):
            id = uri
        else:
            id = f'{obj}:{id(obj)}'

        if name in [None, '']:
            name = os.path.basename(id)

        super(HubFlowDataSource, self).__init__(id, name, icon)

        if not isinstance(icon, QIcon):
            self.mIcon = QIcon(':/enmapbox/gui/ui/icons/processingAlgorithm.svg')

        self.mFlowObj = obj

        s = ""

    def flowObject(self) -> object:
        return self.mFlowObj


class DataSourceRaster(DataSourceSpatial):

    def __init__(self, uri: str, name: str = None, icon=None, providerKey: str = None, layer: QgsRasterLayer = None):

        if isinstance(layer, QgsRasterLayer):
            uri = layer.source()

        super(DataSourceRaster, self).__init__(uri, name=name, icon=icon, providerKey=providerKey, layer=layer)

        self.mDefaultRenderer = None

        if not isinstance(layer, QgsRasterLayer):
            layer = self.createUnregisteredMapLayer()
        assert isinstance(layer, QgsRasterLayer)
        assert layer.isValid()

        self.setMapLayer(layer)
        self.mLayer: QgsRasterLayer = layer

        # self.mDataType = -1
        # self.mPxSize = QSizeF()
        # self.mDatasetMetadata = collections.OrderedDict()
        self.mBandMetadata = []

        self.mDatasetMetadata = {}

        self.mWaveLengths = []
        self.mWaveLengthUnits = []
        self.updateMetadata()

    def mapLayer(self) -> QgsRasterLayer:
        return self.mLayer

    def pixelSize(self) -> QSizeF:
        return QSizeF(self.mLayer.rasterUnitsPerPixelX(), self.mLayer.rasterUnitsPerPixelY())

    def dataType(self) -> Qgis.DataType:
        """
        Returns the data type of the first band.
        :return: Qgis.DataType
        """
        return self.mLayer.dataProvider().dataType(1)

    def nSamples(self) -> int:
        """Returns the number of samples / columns / pixels in y direction"""
        return self.mLayer.width()

    def nLines(self) -> int:
        """Returns the number of lines / rows / pixels in y direction"""
        return self.mLayer.height()

    def nBands(self) -> int:
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

        # these attributes are to be set

        self.mBandMetadata.clear()
        self.mDatasetMetadata.clear()
        # self.nBands = self.nSamples = self.nLines = -1
        # self.mDataType = None

        try:
            self.mWaveLengths, self.mWaveLengthUnits = parseWavelength(self.mapLayer())
        except Exception as ex:
            self.mWaveLengths = []
            self.mWaveLengthUnits = []

        hasClassInfo = isinstance(ClassificationScheme.fromMapLayer(self.mLayer), ClassificationScheme)

        if self.mProvider == 'gdal':
            ds = gdal.Open(self.mUri)
            assert isinstance(ds, gdal.Dataset)

            # self.nSamples, self.nLines = ds.RasterXSize, ds.RasterYSize
            # self.nBands = ds.RasterCount

            # gt = ds.GetGeoTransform()

            # v = px2geo(QPoint(0, 0), gt) - px2geo(QPoint(1, 1), gt)
            # self.mPxSize = QSizeF(abs(v.x()), abs(v.y()))

            def fetchMetadata(obj):
                assert type(obj) in [gdal.Dataset, gdal.Band]

                md = collections.OrderedDict()
                domains = obj.GetMetadataDomainList()
                if isinstance(domains, list):
                    for domain in sorted(domains):
                        tmp = obj.GetMetadata_Dict(domain)
                        if len(tmp) > 0:
                            md[domain] = tmp
                return md

            self.mDatasetMetadata = fetchMetadata(ds)

            for b in range(ds.RasterCount):
                band = ds.GetRasterBand(b + 1)
                assert isinstance(band, gdal.Band)
                # bandName = band.GetDescription()
                # if len(bandName) == 0:
                #    bandName = 'Band {}'.format(b+1)
                # self.mBandNames.append(bandName)

                cs = ClassificationScheme.fromRasterImage(ds, b)
                md = fetchMetadata(band)
                if isinstance(cs, ClassificationScheme):
                    hasClassInfo = True
                    md['__ClassificationScheme__'] = cs

                self.mBandMetadata.append(md)

                # if b == 0:
                #    self.mDataType = band.DataType

        else:
            # Fallback
            # lyr = self.createUnregisteredMapLayer()
            # self.mPxSize = QSizeF(lyr.rasterUnitsPerPixelX(), lyr.rasterUnitsPerPixelY())
            # self.nBands = lyr.bandCount()
            # self.nSamples = lyr.width()
            # self.nLines = lyr.height()
            self.mDatasetMetadata['Description'] = self.mapLayer().dataProvider().description()
            self.mDatasetMetadata['Source'] = self.mapLayer().source()
            # according to qgis.h the Qgis.DataType value is a "modified and extended copy of GDALDataType".
            # self.mDataType = int(lyr.dataProvider().dataType(1))

            for b in range(self.nBands()):
                bandMeta = {}
                self.mBandMetadata.append(bandMeta)
                # self.mBandNames.append(lyr.bandName(b+1))

        # update the datassource icon
        if hasClassInfo is True:
            icon = QIcon(':/enmapbox/gui/ui/icons/filelist_classification.svg')
        elif self.dataType() in [Qgis.Byte] and self.nBands() == 1:
            icon = QIcon(':/enmapbox/gui/ui/icons/filelist_mask.svg')
        elif self.nBands() == 1:
            icon = QIcon(':/enmapbox/gui/ui/icons/filelist_regression.svg')
        else:
            icon = QIcon(':/enmapbox/gui/ui/icons/filelist_image.svg')
        self.setIcon(icon)

    def isNewVersionOf(self, dataSource) -> bool:
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

    def createUnregisteredMapLayer(self) -> QgsRasterLayer:
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

        msg, success = lyr.loadDefaultStyle()
        if not success:
            # no default style defined? Find one based on the raster data properties
            # set default renderer
            r = defaultRasterRenderer(lyr)
            r.setInput(lyr.dataProvider())
            lyr.setRenderer(r)

        if False:
            if isinstance(self.mapLayer(), QgsRasterLayer) and not isinstance(self.mDefaultRenderer, QgsRasterRenderer):
                self.mDefaultRenderer = defaultRasterRenderer(self.mapLayer(),
                                                              bandIndices=defaultBands(self.mapLayer()))
                self.mDefaultRenderer.setInput(self.mapLayer().dataProvider())

            if isinstance(self.mDefaultRenderer, QgsRasterRenderer):
                r = self.mDefaultRenderer.clone()
                r.setInput(lyr.dataProvider())
                lyr.setRenderer(r)

        if isPrompt:
            QgsSettings().setValue(key, v)

        return lyr


class DataSourceVector(DataSourceSpatial):
    def __init__(self, uri, name=None, icon=None, providerKey: str = None, layer: QgsVectorLayer = None):

        super(DataSourceVector, self).__init__(uri, name, icon, providerKey, layer=layer)
        if not isinstance(layer, QgsVectorLayer):
            layer = self.createUnregisteredMapLayer()
        assert isinstance(layer, QgsVectorLayer)

        self.setMapLayer(layer)
        self.updateMetadata()

    def geometryType(self) -> QgsWkbTypes:
        """
        Returns the QgsWkbTypes.GeometryType
        :return: QgsWkbTypes.GeometryType
        """
        return self.mapLayer().geometryType()

    def isSpectralLibrary(self) -> bool:
        return is_spectral_library(self.mLayer)

    def createUnregisteredMapLayer(self) -> QgsVectorLayer:
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

        loptions = QgsVectorLayer.LayerOptions(True, False)
        if self.mProvider == 'memory':
            # we cannot clone memory layers
            # see https://github.com/qgis/QGIS/issues/34134
            lyr = self.mLayer
        else:
            lyr = QgsVectorLayer(self.mUri, self.mName, self.mProvider, options=loptions)
            msg, success = lyr.loadDefaultStyle()
            if not success:
                warnings.warn(f'DataSourceVector.createUnregisteredMapLayer() loadDefaultStyle():\n{msg}')
        if isPrompt:
            QgsSettings().setValue(key, v)

        return lyr

    def updateMetadata(self, *args, **kwds):
        super(DataSourceVector, self).updateMetadata(*args, **kwds)

        icon = QIcon(r':/images/themes/default/mIconVector.svg')

        if self.isSpectralLibrary():
            icon = QIcon(r':/qps/ui/icons/speclib.svg')
        else:
            gt = self.geometryType()
            if gt in [QgsWkbTypes.PointGeometry]:
                icon = QIcon(':/enmapbox/gui/ui/icons/mIconPointLayer.svg')
            elif gt in [QgsWkbTypes.LineGeometry]:
                icon = QIcon(':/images/themes/default/mIconLineLayer.svg')
            elif gt in [QgsWkbTypes.PolygonGeometry]:
                icon = QIcon(':/images/themes/default/mIconPolygonLayer.svg')

        self.mIcon = icon


class DataSourceFactory(object):
    SUBDATASETPREFERENCES = {}

    @staticmethod
    def srcToString(src) -> str:
        """
        Extracts the source uri that can be used to open a new QgsMapLayer
        :param src: QUrl | str
        :return: str
        """
        if isinstance(src, QUrl):
            src = src.toString(QUrl.PreferLocalFile | QUrl.RemoveQuery)
        if isinstance(src, str):
            # identify GDAL subdataset strings
            if re.search('(HDF|SENTINEL).*:.*:.*', src):
                src = src
            elif os.path.isfile(src):
                src = pathlib.Path(src).as_posix()
            else:
                pass
        else:
            src = None
        return src

    @staticmethod
    def isVectorSource(src) -> typing.Tuple[str, str]:
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
    def isRasterSource(src) -> typing.Tuple[str, str, str]:
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
    def isSpeclib(src) -> typing.Tuple[str, str]:
        """
        :param src: path or object that might be a SpectralLibrary
        :return: (uri, None) if True
        """
        uri = None
        if is_spectral_library(src):
            uri = src.source()
        else:
            if not isinstance(src, str):
                src = DataSourceFactory.srcToString(src)

            if isinstance(src, str):
                if os.path.exists(src):
                    lyr = QgsVectorLayer(src)
                    if is_spectral_library(lyr):
                        uri = src
                else:
                    s = ""
        return uri, None

    @staticmethod
    def isHubFlowObj(src) -> typing.Tuple[bool, object]:
        """
        Returns the source uri if it can be handled as known hubflow data source.
        :param src: any type
        :return: uri, 'hubflow' | None, None
        """
        #from hubflow.core import \
        #    FlowObject, Map
        ## all hubflow Object, except spatial types, like Rasters or Vectors
        ## as they are handeled with QGIS API
        #if isinstance(src, FlowObject) and not isinstance(src, Map):
        #    return True, src

        src = DataSourceFactory.srcToString(src)
        if isinstance(src, str) and os.path.exists(src):
            pkl_obj = None
            error = None
            try:
                if src.endswith('.pkl'):
                    with open(src, 'rb') as f:
                        pkl_obj = pickle.load(f)
                elif src.endswith('.json'):
                    with open(src, 'r', encoding='utf-8') as f:
                        pkl_obj = json.load(f)
            except pickle.UnpicklingError as ex1:
                error = f'isHubFlowObj:: UnpicklingError: Unable to unpickle {src}:\nReason:{ex1}'
            except Exception as ex:
                error = f'isHubFlowObj:: Unable to load {src}: {ex}'

            if error:
                if src.endswith('.pkl'):
                    # in case of *.pkl it is very likely that we should be able to open them with pickle.load
                    messageLog(error, level=Qgis.Warning)
                else:
                    debugLog(error)

            if pkl_obj is not None:
                return True, pkl_obj
        return False, None

    @staticmethod
    def fromXML(domElement: QDomElement):
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
    def create(src, name=None, icon=None) -> typing.List[DataSource]:
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

            if src in [None, '', QVariant()]:
                return []

            elif isinstance(src, DataSource):
                return [src]
            elif isinstance(src, QgsMimeDataUtils.Uri):
                if src.layerType == 'raster':
                    return [DataSourceRaster(src.uri, name=src.name, providerKey=src.providerKey)]
                elif src.layerType == 'vector':
                    return [DataSourceVector(src.uri, name=src.name, providerKey=src.providerKey)]
            elif isinstance(src, QgsVectorLayer):
                return [DataSourceVector(None, layer=src)]
            elif isinstance(src, QgsRasterLayer):
                return [DataSourceRaster(None, layer=src)]
            elif isinstance(src, pathlib.Path):
                src = str(src)
            elif type(src) in [str, QUrl]:
                src = DataSourceFactory.srcToString(src)
                if False: # activate to add in-memory layers
                    lyr = QgsProject.instance().mapLayers().get(src)
                    if isinstance(lyr, QgsMapLayer):
                        return DataSourceFactory.create(lyr)

            if src in [None, type(None)]:
                return []

            # DataSource.instances()

            # run checks on input sources
            if isinstance(src, gdal.Dataset) or isinstance(src, QgsRasterLayer):
                sourceTestFunctions = [DataSourceFactory.checkForRaster]
            elif isinstance(src, ogr.DataSource) or isinstance(src, QgsVectorLayer):
                sourceTestFunctions = [DataSourceFactory.checkForVector]
            elif type(src).__name__ in ['module']:
                return []
            else:  # run all tests
                sourceTestFunctions = [DataSourceFactory.checkForRaster,
                                       DataSourceFactory.checkForVector,
                                       DataSourceFactory.checkForHubFlow,
                                       DataSourceFactory.checkOtherFiles]

                # re-order by most-likely none-raster source type according to source uri
                if isinstance(src, str):
                    guess = guessDataProvider(src)
                    if isinstance(guess, str):
                        if guess == 'ogr':
                            sourceTestFunctions.insert(0, sourceTestFunctions.pop(
                                sourceTestFunctions.index(DataSourceFactory.checkForVector)))
                        elif guess == 'enmapbox_textfile':
                            sourceTestFunctions.insert(0, sourceTestFunctions.pop(
                                sourceTestFunctions.index(DataSourceFactory.checkOtherFiles)))
                        elif guess == 'enmapbox_pkl':
                            sourceTestFunctions.insert(0, sourceTestFunctions.pop(
                                sourceTestFunctions.index(DataSourceFactory.checkForHubFlow)))
                        elif guess == 'WFS':
                            sourceTestFunctions.insert(0, sourceTestFunctions.pop(
                                sourceTestFunctions.index(DataSourceFactory.checkForVector)))
                    # files where we are sure we can not load
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
                                subLayerUri = subLayers[ldef.layerId]
                                parts = subLayerUri.split(lyr.dataProvider().sublayerSeparator())

                                rasterUris.append(parts[0])

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
    def checkForHubFlow(src, **kwds) -> typing.List[HubFlowDataSource]:
        """
        if possible, returns a HubFlowDataSource from src
        :param self:
        :param src:
        :param kwds:
        :return: HubFlowDataSource
        """
        uri = None
        if isinstance(src, (str, pathlib.Path)):
            uri = str(pathlib.Path(src))
        isHubFlow, obj = DataSourceFactory.isHubFlowObj(src)
        if isHubFlow:
            return [HubFlowDataSource(obj, uri=uri, **kwds)]
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
