# -*- coding: utf-8 -*-
# noinspection PyPep8Naming
"""
***************************************************************************
    datasourcemanager.py
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
import inspect
import os
import pickle
import re
import sys
import typing
import uuid
import warnings
import webbrowser
from os.path import splitext

import numpy as np
from PyQt5.QtCore import Qt, QMimeData, QModelIndex, QSize, QUrl, QObject, QSortFilterProxyModel
from PyQt5.QtGui import QIcon, QContextMenuEvent, QPixmap
from PyQt5.QtWidgets import QAbstractItemView, QStyle, QAction, QTreeView, QFileDialog, QDialog

import qgis.utils
from enmapbox import DIR_EXAMPLEDATA, messageLog
from enmapbox.externals.qps.speclib.core import EDITOR_WIDGET_REGISTRY_KEY as EWTYPE_SPECLIB, is_spectral_library
from enmapbox.externals.qps.utils import bandClosestToWavelength, QGIS_DATATYPE_NAMES
from enmapbox.gui import \
    ClassificationScheme, TreeNode, TreeView, ClassInfo, TreeModel, PyObjectTreeNode, \
    qgisLayerTreeLayers, qgisAppQgisInterface, SpectralLibrary, SpatialExtent, fileSizeString, defaultBands, \
    defaultRasterRenderer, loadUi
from enmapbox.gui.dataviews.docks import MapDock
from enmapbox.gui.mimedata import \
    MDF_DATASOURCETREEMODELDATA, MDF_QGIS_LAYERTREEMODELDATA, MDF_RASTERBANDS, \
    QGIS_URILIST_MIMETYPE, MDF_URILIST, extractMapLayers
from enmapbox.gui.utils import enmapboxUiPath, dataTypeName
from enmapboxprocessing.algorithm.appendenviheadertogtiffrasteralgorithm import AppendEnviHeaderToGTiffRasterAlgorithm
from enmapboxprocessing.algorithm.saverasterlayerasalgorithm import SaveRasterAsAlgorithm
from enmapboxprocessing.algorithm.translaterasteralgorithm import TranslateRasterAlgorithm
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import QApplication, QMenu
from qgis.core import \
    QgsMapLayer, QgsRasterLayer, QgsVectorLayer, QgsCoordinateReferenceSystem, \
    QgsRasterRenderer, QgsProject, QgsUnitTypes, QgsWkbTypes, \
    QgsLayerTreeGroup, QgsLayerTreeLayer, QgsRasterDataProvider, Qgis, QgsField, QgsFieldModel
from qgis.gui import \
    QgisInterface, QgsMapCanvas, QgsDockWidget

warnings.warn('Do not use this module', DeprecationWarning)

HUBFLOW = True
HUBFLOW_MAX_VALUES = 1024
SOURCE_TYPES = ['ALL', 'ANY', 'RASTER', 'VECTOR', 'SPATIAL', 'MODEL', 'SPECLIB']

try:
    import hubflow.core
except Exception as ex:
    msg = 'Unable to import hubflow API. Error "{}"'.format(ex)

    messageLog(msg, level=Qgis.Warning)

    HUBFLOW = False


def reprNL(obj, replacement: str = ' ') -> str:
    """
    Return an object's repl value without newlines
    :param obj:
    :param replacement:
    :return:
    """
    return repr(obj).replace('\n', replacement)


class DataSourceManager(QObject):
    """
       Keeps control on different data sources handled by EnMAP-Box.
       Similar like QGIS data registry, but manages non-spatial data sources (text files, spectral libraries etc.) as well.
    """

    _instance = None

    @staticmethod
    def instance():
        from enmapbox.gui.enmapboxgui import EnMAPBox
        if isinstance(EnMAPBox.instance(), EnMAPBox):
            return EnMAPBox.instance().dataSourceManager
        else:
            return DataSourceManager._instance

    sigDataSourceAdded = pyqtSignal(DataSource)
    sigDataSourceRemoved = pyqtSignal(DataSource)

    def __init__(self):
        """
        Constructor
        """
        super(DataSourceManager, self).__init__()
        DataSourceManager._instance = self
        self.mSources = list()
        self.mShowSpatialSourceInQgsAndEnMAPBox = True

    def close(self):
        DataSourceManager._instance = None

    def onLayersWillBeRemoved(self, lid):
        to_remove = [ds for ds in self.sources() if isinstance(ds, DataSourceSpatial) and ds.mapLayerId() == lid]
        self.removeSources(to_remove)

    def __iter__(self) -> typing.Iterator[DataSource]:
        return iter(self.mSources)

    def __len__(self) -> int:
        return len(self.mSources)

    def findSourceFromUUID(self, uuID) -> DataSource:
        if isinstance(uuID, str):
            uuID = uuid.uuid4(uuID)

        assert isinstance(uuID, uuid.UUID)
        """
        Finds the DataSource with uuid
        :param uuid: UUID4
        :return: None or DataSource
        """
        for source in self.mSources:
            assert isinstance(source, DataSource)
            if source.uuid() == uuID:
                return source
        return None

    def mapLayers(self) -> typing.List[QgsMapLayer]:
        """
        Returns the map layers related to EnMAP-Box sources
        :return: list of QgsMapLayers
        """
        layers = []
        for s in self:
            if isinstance(s, DataSourceSpatial) and isinstance(s.mapLayer(), QgsMapLayer):
                layers.append(s.mapLayer())
        return layers

    def sources(self, sourceTypes=None) -> typing.List[DataSource]:
        """
        Returns the managed DataSources
        :param sourceTypes: filter to return specific DataSource types only
            a) str like 'VECTOR' (see SOURCE_TYPES)
            b) class type derived from DataSource
            c) a list of a or b to filter multiple source types, e.g. ['VECTOR', 'RASTER']
        :return: [list-of-DataSources]
        """

        if sourceTypes is None:
            return self.mSources[:]
        else:
            if not isinstance(sourceTypes, list):
                sourceTypes = [sourceTypes]

            filterTypes = set()
            for sourceType in sourceTypes:
                if isinstance(sourceType, type(DataSource)):
                    filterTypes.add(sourceType)
                elif sourceType in SOURCE_TYPES:
                    filterTypes.add(sourceType)

            if 'ALL' in filterTypes:
                return self.mSources[:]

            results = []
            for source in self.mSources:
                if type(source) in filterTypes:
                    results.append(source)
                elif isinstance(source, (DataSourceSpatial)) and 'SPATIAL' in filterTypes:
                    results.append(source)
                elif isinstance(source, DataSourceVector):
                    if 'VECTOR' in filterTypes:
                        results.append(source)
                    elif source.isSpectralLibrary() and 'SPECLIB' in filterTypes:
                        results.append(source)
                elif isinstance(source, DataSourceRaster) and 'RASTER' in filterTypes:
                    results.append(source)
                elif isinstance(source, HubFlowDataSource) and 'MODEL' in filterTypes:
                    results.append(source)
                elif isinstance(source, DataSourceFile) and 'FIILE' in filterTypes:
                    results.append(source)

        return results

    def classificationSchemata(self) -> list:
        """
        Reads all DataSource and returns a list of found classification schemata
        :return: [list-if-ClassificationSchemes]
        """
        results = []

        for src in self:
            scheme = None
            assert isinstance(src, DataSource)
            if isinstance(src, DataSourceRaster):
                scheme = ClassificationScheme.fromRasterImage(src.uri())

            elif isinstance(src, DataSourceVector):
                lyr = src.createUnregisteredMapLayer()
                scheme = ClassificationScheme.fromFeatureRenderer(lyr)

            if isinstance(scheme, ClassificationScheme):
                scheme.setName(src.uri())
                results.append(scheme)

        return results

    def layerSources(self) -> typing.List[str]:
        return [ds.mapLayer().source() for ds in self.sources() if isinstance(ds, DataSourceSpatial)]

    def layerIds(self) -> typing.List[str]:
        return [ds.mapLayerId() for ds in self.sources() if isinstance(ds, DataSourceSpatial)]

    def uriList(self, sourceTypes='ALL') -> typing.List[str]:
        """
        Returns URIs of registered data sources
        :param sourcetype: uri filter as used in sources(sourceTypes=<types>).
        :return: uri as string (str), e.g. a file path
        """
        return [ds.uri() for ds in self.sources(sourceTypes=sourceTypes)]

    def addSources(self, sources: list) -> list:
        """
        Adds a list of new data sources
        :param sources: list of potential data sources, i.e. QgsDataSources
        :return: [list-of-added-DataSources]
        """
        assert isinstance(sources, list)
        added = []
        for s in sources:
            added.extend(self.addSource(s))
        added = [a for a in added if isinstance(a, DataSource)]

        return added

    def addSource(self, newDataSource, name=None, icon=None) -> typing.List[DataSource]:
        """
        Adds a new data source.
        :param newDataSource: any object
        :param name:
        :param icon:
        :return: a list of successfully added DataSource instances.
                 Usually this will be a list with a single DataSource instance only.
                 In case of container datasets multiple instances might get returned.
        """
        # do not add paths if they are already known
        knownStrings = self.uriList() + self.layerIds() + self.layerSources()
        if isinstance(newDataSource, str):
            if newDataSource in knownStrings:
                return []

            layers = [ds.mapLayerId() for ds in self.sources() if isinstance(ds, DataSourceSpatial)]
            layers += [ds.mapLayer().source() for ds in self.sources() if isinstance(ds, DataSourceSpatial)]
            if newDataSource in layers:
                return []

        if isinstance(newDataSource, QgsMapLayer):
            if not newDataSource.isValid() or \
                    newDataSource.source() in knownStrings or \
                    newDataSource.id() in knownStrings:
                return []

        try:
            newDataSources = DataSourceFactory.create(newDataSource, name=name, icon=icon)
        except RuntimeError as err:
            newDataSources = []

        toAdd = []
        for dsNew in newDataSources:
            assert isinstance(dsNew, DataSource)
            sameSources = [d for d in self.mSources if dsNew.isSameSource(d)]
            if len(sameSources) == 0:
                toAdd.append(dsNew)
            else:
                # we have similar sources.

                older = []
                newer = []

                for d in sameSources:
                    if dsNew.isNewVersionOf(d):
                        older.append(d)

                # remove older versions
                if len(older) > 0:
                    self.removeSources(older)
                    QApplication.processEvents()
                    toAdd.append(dsNew)

        for ds in toAdd:
            if ds not in self.mSources:
                self.mSources.append(ds)
                self.sigDataSourceAdded.emit(ds)

        return toAdd

    def addSentinel2ByDialog(self, *args):
        filter = ['Sentinel-2 Metadata (MTD_MSIL*.xml)',
                  'XML files (*.xml)',
                  'All files (*.*)'
                  ]
        self.addSubDatasetsByDialog(title='Add Sentinel-2 Data', filter=';;'.join(filter))

    def addSubDatasetsByDialog(self, *args, title='Add Sub-Datasets', filter: str = 'All files (*.*)'):
        from enmapbox.externals.qps.subdatasets import SubDatasetSelectionDialog
        from enmapbox import enmapboxSettings
        SETTINGS = enmapboxSettings()
        defaultRoot = SETTINGS.value('lastsourcedir', None)

        if defaultRoot is None:
            defaultRoot = DIR_EXAMPLEDATA

        if not os.path.exists(defaultRoot):
            defaultRoot = None

        d = SubDatasetSelectionDialog()
        d.setWindowTitle(title)
        d.setFileFilter(filter)
        d.setDefaultRoot(defaultRoot)
        result = d.exec_()

        if result == QDialog.Accepted:
            subdatasets = d.selectedSubDatasets()
            layers = []
            loptions = QgsRasterLayer.LayerOptions(loadDefaultStyle=False)
            for i, s in enumerate(subdatasets):
                lyr = QgsRasterLayer(s, options=loptions)
                if i == 0:
                    paths = d.fileWidget.splitFilePaths(d.fileWidget.filePath())
                    SETTINGS.setValue('lastsourcedir', os.path.dirname(paths[0]))

                layers.append(lyr)
            self.addSources(layers)

    def addDataSourceByDialog(self):
        """
        Shows a fileOpen dialog to select new data sources
        :return:
        """

        from enmapbox import enmapboxSettings
        SETTINGS = enmapboxSettings()
        lastDataSourceDir = SETTINGS.value('lastsourcedir', None)

        if lastDataSourceDir is None:
            lastDataSourceDir = DIR_EXAMPLEDATA

        if not os.path.exists(lastDataSourceDir):
            lastDataSourceDir = None

        uris, filter = QFileDialog.getOpenFileNames(None, "Open a data source(s)", lastDataSourceDir)
        self.addSources(uris)

        if len(uris) > 0:
            SETTINGS.setValue('lastsourcedir', os.path.dirname(uris[-1]))

    def importSourcesFromQGISRegistry(self):
        """
        Adds datasources known to QGIS which do not exist here
        """
        layers = []

        from qgis.utils import iface
        if isinstance(iface, QgisInterface):
            root = iface.layerTreeView().layerTreeModel().rootGroup()
            assert isinstance(root, QgsLayerTreeGroup)

            for layerTree in root.findLayers():
                assert isinstance(layerTree, QgsLayerTreeLayer)
                s = ""
                grp = layerTree
                # grp.setCustomProperty('nodeHidden', 'true' if bHide else 'false')
                lyr = layerTree.layer()

                if isinstance(lyr, QgsMapLayer) and lyr.isValid() and not grp.customProperty('nodeHidden'):
                    layers.append(layerTree.layer().clone())

        if len(layers) > 0:
            self.addSources(layers)

    def exportSourcesToQGISRegistry(self, showLayers: bool = False):
        """
        Adds spatial datasources to QGIS
        :param showLayers: False, set on True to show added layers in QGIS Layer Tree
        """

        allQgsLayers = list(QgsProject.instance().mapLayers().values())
        allQgsSources = [l.source() for l in allQgsLayers]
        visibleQgsLayers = qgisLayerTreeLayers()
        visibleQgsSources = [l.source() for l in visibleQgsLayers]

        iface = qgisAppQgisInterface()

        for dataSource in self.sources():
            if isinstance(dataSource, DataSourceSpatial):
                l = dataSource.createUnregisteredMapLayer()
                if not l.isValid():
                    print('INVALID LAYER FROM DATASOURCE: {} {}'.format(l, l.source()), file=sys.stderr)
                    continue
                if l.source() not in allQgsSources:
                    QgsProject.instance().addMapLayer(l, showLayers)
                else:
                    if iface and showLayers and l.source() not in visibleQgsSources:
                        i = allQgsSources.index(l.source())
                        knownLayer = allQgsLayers[i]
                        assert isinstance(knownLayer, QgsMapLayer)
                        iface.layerTreeView().model().rootGroup().addLayer(knownLayer)

    def clear(self, deleteMapLayers=True) -> typing.List[DataSource]:
        """
        Removes all data source from DataSourceManager
        :return: [list-of-removed-DataSources]
        """

        dataSources = self.removeSources(list(self.mSources))
        if deleteMapLayers:
            for ds in dataSources:
                if isinstance(ds, DataSourceRaster):
                    # ds.mLayer.dataProvider.setInput(None)

                    pass
                    # del ds.mLayer
        return dataSources

    def removeSources(self, dataSourceList: list = None) -> typing.List[DataSource]:
        """
        Removes a list of data sources.
        :param dataSourceList: [list-of-datasources]
        :return: self
        """
        if dataSourceList is None:
            dataSourceList = self.sources()
        removed = [self.removeSource(dataSource) for dataSource in dataSourceList]
        return [r for r in removed if isinstance(r, DataSource)]

    def removeSource(self, dataSource) -> DataSource:
        """
        Removes the DataSource from the DataSourceManager
        :param dataSource: the DataSource or its uri (str) or a QgsMapLayer to be removed
        :return: the removed DataSource. None if dataSource was not in the DataSourceManager
        """
        to_remove = []
        if isinstance(dataSource, QgsMapLayer):
            for ds in self:
                if isinstance(ds, DataSourceSpatial) and \
                   isinstance(ds.mapLayer(), QgsMapLayer) and \
                   ds.mapLayer().id() == dataSource.id():
                    to_remove.append(ds)

        elif isinstance(dataSource, str):
            for ds in self:
                if ds.uri() == dataSource:
                    to_remove.append(ds)
        elif isinstance(dataSource, DataSource):
            if dataSource in self:
                to_remove.append(dataSource)

        assert len(to_remove) <= 1
        if len(to_remove) == 1:
            ds = to_remove[0]
            assert isinstance(ds, DataSource)
            self.mSources.remove(ds)

            self.sigDataSourceRemoved.emit(ds)
            return ds
        else:
            return None

    def sourceTypes(self):
        """
        Returns the list of source-types handled by this DataSourceManager
        :return: [list-of-source-types]
        """
        return sorted(list(set([type(ds) for ds in self.mSources])), key=lambda t: t.__name__)


class DataSourceGroupTreeNode(TreeNode):

    def __init__(self, groupName: str, classDef, icon=None):
        assert inspect.isclass(classDef)
        assert isinstance(groupName, str)
        if icon is None:
            style = QApplication.style()
            if isinstance(style, QStyle):
                icon = style.standardIcon(QStyle.SP_DirOpenIcon)
            else:
                icon = QIcon(r':/qt-project.org/styles/commonstyle/images/dirclosed-32.png')

        super(DataSourceGroupTreeNode, self).__init__(name=groupName, icon=icon)
        self.mFlag1stSource = False
        self.mGroupName = groupName
        self.mChildClass = classDef
        self.sigAddedChildren.connect(self.onChildsChanged)
        self.sigRemovedChildren.connect(self.onChildsChanged)

    def groupName(self) -> str:
        return self.mGroupName

    def onChildsChanged(self, *args):

        n = len(self.childNodes())
        name = '{} ({})'.format(self.mGroupName, n)
        self.setName(name)

        if n > 0 and self.mFlag1stSource == False:
            pass

    def dataSources(self) -> list:
        """
        Returns the DataSource instances part of this group.
        :return: [list-of-DataSources]
        """
        return [d.mDataSource for d in self.childNodes()
                if isinstance(d, DataSourceTreeNode)]


class DataSourceSizesTreeNode(TreeNode):
    """
    A node to show the different aspects of dataSource sizes
    Sub-Nodes:
        spatial extent in map unit
        pixel sizes (if raster source)
        pixel extent (if raster source)
    """

    def __init__(self):
        super().__init__('Size')

    def update_size(self, dataSource):
        self.removeAllChildNodes()

        if not isinstance(dataSource, DataSource):
            return

        childs = []
        value = []
        try:
            size = os.path.getsize(dataSource.uri())
            size = fileSizeString(size)
            value.append(size)
            childs += [TreeNode('File', size)]
        except:
            pass

        if isinstance(dataSource, DataSourceSpatial):
            ext = dataSource.spatialExtent()
            mu = QgsUnitTypes.encodeUnit(ext.crs().mapUnits())

            childs += [TreeNode('Width', value='{:0.2f} {}'.format(ext.width(), mu), toolTip='Spatial width'),
                       TreeNode('Height', value='{:0.2f} {}'.format(ext.height(), mu, toolTip='Spatial height'))
                       ]

        if isinstance(dataSource, DataSourceRaster):
            if isinstance(dataSource.mLayer, QgsRasterLayer) and \
                    isinstance(dataSource.mLayer.dataProvider(), QgsRasterDataProvider):
                lyr = dataSource.mLayer
                dp: QgsRasterDataProvider = dataSource.mLayer.dataProvider()
                value.append(f'{dataSource.nSamples()}'
                             f'x{dataSource.nLines()}'
                             f'x{dataSource.nBands()}'
                             f'x{dp.dataTypeSize(1)} ({QGIS_DATATYPE_NAMES.get(dp.dataType(1), "unknown type")})')

                childs += [TreeNode('Pixel',
                                    value=f'{lyr.rasterUnitsPerPixelX()}x'
                                          f'{lyr.rasterUnitsPerPixelY()} '
                                          f'{QgsUnitTypes.encodeUnit(lyr.crs().mapUnits())}',
                                    toolTip='Size of single pixel / ground sampling resolution'),
                           TreeNode('Samples', value=dataSource.nSamples(), toolTip='Samples/columns in X direction'),
                           TreeNode('Lines', value=dataSource.nLines(), toolTip='Lines/rows in Y direction'),
                           TreeNode('Bands', value=dataSource.nBands(), toolTip='Raster bands'),
                           TreeNode('Data Type',
                                    value=dataTypeName(dp.dataType(1)),
                                    toolTip=dataTypeName(dp.dataType(1), verbose=True))
                           ]
        if isinstance(dataSource, DataSourceVector):
            value.append('{} features'.format(dataSource.mLayer.featureCount()))

        self.setValue(' '.join([str(v) for v in value]))
        self.appendChildNodes(childs)


class DataSourceTreeNode(TreeNode):

    def __init__(self, *args, **kwds):

        super().__init__(*args, **kwds)

        self.mDataSource: DataSource = None
        self.mNodeSize: DataSourceSizesTreeNode = DataSourceSizesTreeNode()
        self.mNodePath: TreeNode = TreeNode('Path')
        self.appendChildNodes([self.mNodePath, self.mNodeSize])

    def connectDataSource(self, dataSource: DataSource):
        """
        Connects a DataSource with this DataSourceTreeNode
        :param dataSource: DataSource
        """
        assert isinstance(dataSource, DataSource)
        self.mDataSource = dataSource
        self.updateNodes()

    def updateNodes(self):

        ds = self.dataSource()
        if isinstance(ds, DataSource):
            self.setName(ds.name())
            self.setToolTip(ds.uri())
            self.setIcon(ds.icon())
            uri = ds.uri()
            self.mNodePath.setValue(uri)
        else:
            self.setName('<disconnected>')
            self.mNodePath.setValue(None)

        self.mNodeSize.update_size(ds)

    def dataSource(self) -> DataSource:
        """
        Returns the DataSource this DataSourceTreeNode represents.
        :return: DataSource
        """
        return self.mDataSource

    def disconnectDataSource(self):
        self.mDataSource = None
        self.updateNodes()

    def writeXML(self, parentElement):
        super(DataSourceTreeNode, self).writeXML(parentElement)
        elem = parentElement.lastChild().toElement()
        elem.setTagName('datasource-tree-node')
        elem.setAttribute('uuid', '{}'.format(self.mDataSource.uuid()))


class SpatialDataSourceTreeNode(DataSourceTreeNode):

    def __init__(self, *args, **kwds):
        # extent in map units (mu)

        super().__init__(*args, **kwds)
        self.nodeExtXmu: TreeNode = TreeNode('Width')
        self.nodeExtYmu: TreeNode = TreeNode('Height')
        self.nodeCRS: CRSLayerTreeNode = CRSLayerTreeNode(QgsCoordinateReferenceSystem())
        self.mNodeSize.appendChildNodes([self.nodeExtXmu, self.nodeExtYmu])
        self.appendChildNodes(self.nodeCRS)

    def connectDataSource(self, dataSource):
        assert isinstance(dataSource, DataSourceSpatial)
        super(SpatialDataSourceTreeNode, self).connectDataSource(dataSource)

    def updateNodes(self):
        super().updateNodes()

        ds = self.dataSource()
        if isinstance(ds, DataSourceSpatial):
            ext = ds.spatialExtent()
            mu = QgsUnitTypes.toString(ext.crs().mapUnits())
            assert isinstance(ext, SpatialExtent)

            self.nodeCRS.setCrs(ext.crs())
            self.nodeExtXmu.setValue('{} {}'.format(ext.width(), mu))
            self.nodeExtYmu.setValue('{} {}'.format(ext.height(), mu))

        else:
            self.nodeCRS.setCrs(QgsCoordinateReferenceSystem())
            self.nodeExtXmu.setValue(None)
            self.nodeExtYmu.setValue(None)


class VectorDataSourceTreeNode(SpatialDataSourceTreeNode):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.nodeFeatures: TreeNode = TreeNode('Features', values=[0])
        self.nodeGeomType = TreeNode('Geometry Type')
        self.nodeWKBType = TreeNode('WKB Type')

        self.nodeFields: TreeNode = TreeNode('Fields',
                                             toolTip='Attribute fields related to each feature',
                                             values=[0])

        self.nodeFeatures.appendChildNodes([self.nodeGeomType, self.nodeWKBType])
        self.appendChildNodes([self.nodeFeatures, self.nodeFields])

    def connectDataSource(self, dataSource: DataSourceVector):
        super(VectorDataSourceTreeNode, self).connectDataSource(dataSource)
        self.updateNodes()

    def updateNodes(self):
        super().updateNodes()

        ds = self.dataSource()
        if isinstance(ds, DataSourceVector):
            lyr: QgsVectorLayer = ds.createUnregisteredMapLayer()
            assert lyr.isValid()

            nFeat = lyr.featureCount()
            nFields = lyr.fields().count()
            self.nodeFields.setValue(nFields)
            geomType = ['Point', 'Line', 'Polygon', 'Unknown', 'Null'][lyr.geometryType()]
            wkbType = QgsWkbTypes.displayString(int(lyr.wkbType()))

            if is_spectral_library(lyr):
                self.setIcon(QIcon(r':/qps/ui/icons/speclib.svg'))
            else:
                if re.search('polygon', wkbType, re.I):
                    self.setIcon(QIcon(r':/images/themes/default/mIconPolygonLayer.svg'))
                elif re.search('line', wkbType, re.I):
                    self.setIcon(QIcon(r':/images/themes/default/mIconLineLayer.svg'))
                elif re.search('point', wkbType, re.I):
                    self.setIcon(QIcon(r':/images/themes/default/mIconPointLayer.svg'))
                elif lyr.wkbType() in [QgsWkbTypes.NoGeometry, QgsWkbTypes.Unknown]:
                    self.setIcon(QIcon(r':/images/themes/default/mActionOpenTable.svg'))

            self.nodeWKBType.setValue(wkbType)
            self.nodeGeomType.setValue(geomType)

            # self.nodeSize.setValue('{} x {}'.format(nFeat, fileSizeString(self.mSrcSize)))
            self.nodeFeatures.setValue(nFeat)

            field_nodes: typing.List[TreeNode] = []
            fieldModel = QgsFieldModel()
            fieldModel.setLayer(lyr)
            for i, f in enumerate(lyr.fields()):
                f: QgsField
                # fieldItem = QgsFieldsItem(None, f)
                n = TreeNode(f.name())
                l = f.length()
                if l > 0:
                    n.setValue('{} {}'.format(f.typeName(), l))
                else:
                    n.setValue(f.typeName())
                idx = fieldModel.indexFromName(f.name())
                ewType = fieldModel.data(idx, QgsFieldModel.EditorWidgetType)
                if ewType == EWTYPE_SPECLIB:
                    n.setIcon(QIcon(r':/qps/ui/icons/profile.svg'))
                else:
                    n.setIcon(fieldModel.data(idx, Qt.DecorationRole))
                field_nodes.append(n)

            self.nodeFields.removeAllChildNodes()
            self.nodeFields.appendChildNodes(field_nodes)

    def dataSource(self) -> DataSourceVector:
        return self.mDataSource


class ClassificationNodeLayer(TreeNode):

    def __init__(self, classificationScheme, name='Classification Scheme'):
        super(ClassificationNodeLayer, self).__init__()
        self.setName(name)
        to_add = []
        for i, ci in enumerate(classificationScheme):
            to_add.append(TreeNode(name='{}'.format(i), values=ci.name(), icon=ci.icon()))
        self.appendChildNodes(to_add)


class CRSLayerTreeNode(TreeNode):
    def __init__(self, crs: QgsCoordinateReferenceSystem):
        assert isinstance(crs, QgsCoordinateReferenceSystem)
        super().__init__(crs.description())
        self.setName('CRS')
        self.setIcon(QIcon(':/images/themes/default/propertyicons/CRS.svg'))
        self.setToolTip('Coordinate Reference System')
        self.mCrs = None
        self.nodeDescription = TreeNode('Name', toolTip='Description')
        self.nodeAuthID = TreeNode('AuthID', toolTip='Authority ID')
        self.nodeAcronym = TreeNode('Acronym', toolTip='Projection Acronym')
        self.nodeMapUnits = TreeNode('Map Units')
        self.setCrs(crs)

        self.appendChildNodes([self.nodeDescription, self.nodeAuthID, self.nodeAcronym, self.nodeMapUnits])

    def setCrs(self, crs):
        assert isinstance(crs, QgsCoordinateReferenceSystem)
        self.mCrs = crs
        if self.mCrs.isValid():
            self.setValues(crs.description())
            self.nodeDescription.setValues(crs.description())
            self.nodeAuthID.setValues(crs.authid())
            self.nodeAcronym.setValues(crs.projectionAcronym())
            # self.nodeDescription.setItemVisibilityChecked(Qt.Checked)
            self.nodeMapUnits.setValues(QgsUnitTypes.toString(self.mCrs.mapUnits()))
        else:
            self.setValues(None)
            self.nodeDescription.setValue('N/A')
            self.nodeAuthID.setValue('N/A')
            self.nodeAcronym.setValue('N/A')
            self.nodeMapUnits.setValue('N/A')

    def contextMenu(self):
        menu = QMenu()
        a = menu.addAction('Copy EPSG Code')
        a.setToolTip('Copy the authority id ("{}") of this CRS.'.format(self.mCrs.authid()))
        a.triggered.connect(lambda: QApplication.clipboard().setText(self.mCrs.authid()))

        a = menu.addAction('Copy WKT')
        a.setToolTip('Copy the well-known-type representation of this CRS.')
        a.triggered.connect(lambda: QApplication.clipboard().setText(self.mCrs.toWkt()))

        a = menu.addAction('Copy Proj4')
        a.setToolTip('Copy the Proj4 representation of this CRS.')
        a.triggered.connect(lambda: QApplication.clipboard().setText(self.mCrs.toProj4()))
        return menu


class ColorTreeNode(TreeNode):

    def __init__(self, color: QColor):
        assert isinstance(color, QColor)

        pm = QPixmap(QSize(20, 20))
        pm.fill(color)
        icon = QIcon(pm)
        name = color.name()
        value = color.getRgbF()
        super(ColorTreeNode, self).__init__(name=name, value=value, icon=icon)


class RasterBandTreeNode(TreeNode):

    def __init__(self, dataSource, bandIndex, *args, **kwds):
        super().__init__(*args, **kwds)
        assert isinstance(dataSource, DataSourceRaster)
        assert bandIndex >= 0
        assert bandIndex < dataSource.nBands()
        self.mDataSource = dataSource
        self.mBandIndex = bandIndex

        md = self.mDataSource.mBandMetadata[bandIndex]
        classScheme = md.get('__ClassificationScheme__')
        if isinstance(classScheme, ClassificationScheme):
            to_add = []
            for ci in classScheme:
                assert isinstance(ci, ClassInfo)
                classNode = TreeNode(name=str(ci.label()))
                classNode.setValue(ci.name())
                classNode.setIcon(ci.icon())
                to_add.append(classNode)
            self.appendChildNodes(to_add)


class RasterDataSourceTreeNode(SpatialDataSourceTreeNode):
    def __init__(self, *args, **kwds):
        # extents in pixel
        super().__init__(*args, **kwds)

        self.mNodeBands: TreeNode = TreeNode('Bands', toolTip='Number of Raster Bands')
        self.appendChildNodes(self.mNodeBands)

    def connectDataSource(self, dataSource):
        assert isinstance(dataSource, DataSourceRaster)
        super().connectDataSource(dataSource)

    def updateNodes(self):
        super().updateNodes()

        ds = self.dataSource()
        if isinstance(ds, DataSourceRaster):
            self.setIcon(ds.icon())
            self.mNodeBands.removeAllChildNodes()
            self.mNodeBands.setValue(ds.nBands())

            bandNodes = []
            for b in range(ds.mapLayer().bandCount()):
                bandName = ds.mapLayer().bandName(b + 1)
                bandNode = RasterBandTreeNode(ds, b, name=str(b + 1), value=bandName)

                bandNodes.append(bandNode)
            self.mNodeBands.appendChildNodes(bandNodes)


class FileDataSourceTreeNode(DataSourceTreeNode):

    def __init__(self, *args, **kwds):
        super(FileDataSourceTreeNode, self).__init__(*args, **kwds)

    def populateContextMenu(self, menu: QMenu):
        """
        Implement this to add a TreeNode specific context menu
        :param menu:
        :return:
        """
        super().populateContextMenu(menu)

        path = self.mDataSource.uri()
        if re.search('(html|json)$', path):
            a = menu.addAction('Open in Browser')
            a.triggered.connect(lambda *args, p=path: webbrowser.open(path))
        else:
            a = menu.addAction('Open in Editor')
            a.triggered.connect(lambda *args, p=path: webbrowser.open(path))


class HubFlowPyObjectTreeNode(PyObjectTreeNode):

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.setValue(str(self.mPyObject))

    def populateContextMenu(self, menu: QMenu):
        def copyToClipboard():
            state = np.get_printoptions()['threshold']
            np.set_printoptions(threshold=np.inf)
            QApplication.clipboard().setText(str(self.mPyObject))
            np.set_printoptions(threshold=state)

        if isinstance(self.mPyObject, np.ndarray):
            a = menu.addAction('Copy Array')
            a.setToolTip('Copy Numpy Array to Clipboard.')
            a.triggered.connect(copyToClipboard)


class HubFlowObjectTreeNode(DataSourceTreeNode):

    def __init__(self, *args, **kwds):
        super(HubFlowObjectTreeNode, self).__init__(*args, **kwds)
        self.mFlowObj: object = None
        self.mFlowNode: HubFlowPyObjectTreeNode = None
        # self.appendChildNodes(self.nodePyObject)

    def connectDataSource(self, processingTypeDataSource):

        super(HubFlowObjectTreeNode, self).connectDataSource(processingTypeDataSource)
        assert isinstance(self.mDataSource, HubFlowDataSource)

        if isinstance(self.mFlowNode, PyObjectTreeNode):
            self.removeChildNodes([self.mFlowNode])

        ds = self.dataSource()
        if isinstance(ds, HubFlowDataSource):
            self.mFlowObj = ds.flowObject()
            moduleName = self.mFlowObj.__class__.__module__
            className = self.mFlowObj.__class__.__name__

            self.setName(ds.name())
            self.setToolTip('{} - {}.{}'.format(ds.name(), moduleName, className))

            self.mFlowNode = HubFlowPyObjectTreeNode(name=className, obj=self.mFlowObj)
            self.appendChildNodes(self.mFlowNode)

    def contextMenu(self):
        m = QMenu()
        return m


class DataSourceTreeView(TreeView):
    """
    A TreeView to show EnMAP-Box Data Sources
    """
    sigPopulateContextMenu = pyqtSignal(QMenu)

    def __init__(self, *args, **kwds):
        super(DataSourceTreeView, self).__init__(*args, **kwds)
        self.setAcceptDrops(True)

    def contextMenuEvent(self, event: QContextMenuEvent):
        """
        Creates and shows the context menu created with a right-mouse-click.
        :param event: QContextMenuEvent
        """
        idx = self.currentIndex()
        assert isinstance(event, QContextMenuEvent)

        col = idx.column()

        selectedNodes = self.selectedNodes()
        node = self.selectedNode()
        dataSources = list(set([n.mDataSource for n in selectedNodes if isinstance(n, DataSourceTreeNode)]))
        srcURIs = list(set([s.uri() for s in dataSources]))

        from enmapbox.gui.enmapboxgui import EnMAPBox
        enmapbox = EnMAPBox.instance()

        DSM: DataSourceManager = self.model().sourceModel().dataSourceManager
        if not isinstance(DSM, DataSourceManager):
            return

        mapDocks = []
        if isinstance(enmapbox, EnMAPBox):
            mapDocks = enmapbox.mDockManager.docks('MAP')

        m: QMenu = QMenu()
        m.setToolTipsVisible(True)

        if isinstance(node, DataSourceGroupTreeNode):
            a = m.addAction('Remove')
            assert isinstance(a, QAction)
            a.setToolTip('Removes all datasources from this node')
            a.triggered.connect(lambda *args, node=node, dsm=DSM:
                                DSM.removeSources(node.dataSources()))

        if isinstance(node, DataSourceTreeNode):
            src = node.mDataSource

            if isinstance(src, DataSource):
                a = m.addAction('Remove')
                a.triggered.connect(lambda *args, dataSources=dataSources, dsm=DSM:
                                    dsm.removeSources(dataSources))
                a = m.addAction('Copy URI / path')
                a.triggered.connect(lambda *args, srcURIs=srcURIs:
                                    QApplication.clipboard().setText('\n'.join(srcURIs)))
                # a = m.addAction('Rename')
                # a.setEnabled(False)
                # todo: implement rename function
                # a.triggered.connect(node.dataSource.rename)

            if isinstance(src, DataSourceSpatial):
                pass
                # a = m.addAction('Save as..')

            def appendRasterActions(sub: QMenu, src: DataSourceRaster, target):
                assert isinstance(src, DataSourceRaster)
                a = sub.addAction('Default Colors')
                a.triggered.connect(lambda *args, s=src, t=target:
                                    self.openInMap(s, t, rgb='DEFAULT'))

                b = src.mWaveLengthUnits is not None

                a = sub.addAction('True Color')
                a.setToolTip('Red-Green-Blue true colors')
                a.triggered.connect(lambda *args, s=src, t=target:
                                    self.openInMap(s, t, rgb='R,G,B'))
                a.setEnabled(b)
                a = sub.addAction('CIR')
                a.setToolTip('nIR Red Green')
                a.triggered.connect(lambda *args, s=src, t=target:
                                    self.openInMap(s, t, rgb='NIR,R,G'))
                a.setEnabled(b)

                a = sub.addAction('SWIR')
                a.setToolTip('nIR swIR Red')
                a.triggered.connect(lambda *args, s=src, t=target:
                                    self.openInMap(s, t, rgb='NIR,SWIR,R'))
                a.setEnabled(b)

            if isinstance(src, DataSourceRaster):
                sub = m.addMenu('Open in new map...')
                appendRasterActions(sub, src, None)

                sub = m.addMenu('Open in existing map...')
                if len(mapDocks) > 0:
                    for mapDock in mapDocks:
                        assert isinstance(mapDock, MapDock)
                        subsub = sub.addMenu(mapDock.title())
                        appendRasterActions(subsub, src, mapDock)
                else:
                    sub.setEnabled(False)
                sub = m.addMenu('Open in QGIS')
                if isinstance(qgis.utils.iface, QgisInterface):
                    appendRasterActions(sub, src, QgsProject.instance())
                else:
                    sub.setEnabled(False)

                # AR: add some useful processing algo shortcuts
                parameters = {SaveRasterAsAlgorithm.P_RASTER: src.uri()}
                a: QAction = m.addAction('Save as')
                a.setIcon(QIcon(':/images/themes/default/mActionFileSaveAs.svg'))
                a.triggered.connect(
                    lambda src: EnMAPBox.instance().showProcessingAlgorithmDialog(
                        SaveRasterAsAlgorithm(), parameters, parent=self
                    )
                )

                parameters = {TranslateRasterAlgorithm.P_RASTER: src.uri()}
                a: QAction = m.addAction('Translate')
                a.setIcon(QIcon(':/images/themes/default/mActionFileSaveAs.svg'))
                a.triggered.connect(
                    lambda src: EnMAPBox.instance().showProcessingAlgorithmDialog(
                        TranslateRasterAlgorithm(), parameters, parent=self
                    )
                )

                if splitext(src.uri())[1].lower() in ['.tif', '.tiff']:
                    parameters = {AppendEnviHeaderToGTiffRasterAlgorithm.P_RASTER: src.uri()}
                    a: QAction = m.addAction('Append ENVI header')
                    a.setIcon(QIcon(':/images/themes/default/mActionFileSaveAs.svg'))
                    a.triggered.connect(
                        lambda src: EnMAPBox.instance().showProcessingAlgorithmDialog(
                            AppendEnviHeaderToGTiffRasterAlgorithm(), parameters, parent=self
                        )
                    )

            if isinstance(src, DataSourceVector):
                if isinstance(src.mapLayer(), QgsVectorLayer):
                    if src.mapLayer().wkbType() != QgsWkbTypes.NoGeometry:
                        a = m.addAction('Open in new map')
                        a.triggered.connect(lambda *args, s=src: self.openInMap(s, None))

                        sub = m.addMenu('Open in existing map...')
                        if len(mapDocks) > 0:
                            for mapDock in mapDocks:
                                assert isinstance(mapDock, MapDock)
                                a = sub.addAction(mapDock.title())
                                a.triggered.connect(
                                    lambda checked, s=src, d=mapDock:
                                    self.openInMap(s, d))
                        else:
                            sub.setEnabled(False)

                    if src.isSpectralLibrary():
                        a = m.addAction('Open Spectral Library Viewer')
                        a.triggered.connect(
                            lambda *args, s=src: self.openInSpeclibEditor(src.createUnregisteredMapLayer()))

                    a = m.addAction('Open Attribute Table')
                    a.triggered.connect(lambda *args, s=src: self.openInAttributeEditor(s.mapLayer()))

                    a = m.addAction('Open in QGIS')
                    if isinstance(qgis.utils.iface, QgisInterface):
                        a.triggered.connect(lambda *args, s=src:
                                            self.openInMap(s, QgsProject.instance()))
                    else:
                        a.setEnabled(False)

            if isinstance(src, DataSourceFile):
                s = ""
                pass

        if isinstance(node, RasterBandTreeNode):
            #a = m.addAction('Band statistics')
            #a.setEnabled(False)

            a = m.addAction('Open in new map')
            a.triggered.connect(lambda *args, n=node: self.openInMap(n.mDataSource, rgb=[n.mBandIndex]))

        if col == 1 and node.value() != None:
            a = m.addAction('Copy')
            a.triggered.connect(lambda *args, n=node: QApplication.clipboard().setText(str(n.value())))

        if isinstance(node, TreeNode):
            node.populateContextMenu(m)

        a = m.addAction('Remove all DataSources')
        a.setToolTip('Removes all data source.')
        a.triggered.connect(self.onRemoveAllDataSources)

        self.sigPopulateContextMenu.emit(m)

        m.exec_(self.viewport().mapToGlobal(event.pos()))

    def openInMap(self, dataSource: DataSourceSpatial,
                  target: typing.Union[QgsMapCanvas, QgsProject, MapDock] = None,
                  rgb=None,
                  sampleSize: int = 256):
        """
        Add a DataSourceSpatial as QgsMapLayer to a mapCanvas.
        :param target:
        :param sampleSize:
        :param dataSource: DataSourceSpatial
        :param rgb:
        """

        if not isinstance(dataSource, DataSourceSpatial):
            return

        LOAD_DEFAULT_STYLE: bool = isinstance(rgb, str) and re.search('DEFAULT', rgb, re.I)

        if target is None:
            from enmapbox.gui.enmapboxgui import EnMAPBox
            emb = EnMAPBox.instance()
            if not isinstance(emb, EnMAPBox):
                return None
            dock = emb.createDock('MAP')
            assert isinstance(dock, MapDock)
            target = dock.mapCanvas()

        if isinstance(target, MapDock):
            target = target.mapCanvas()

        assert isinstance(target, (QgsMapCanvas, QgsProject))

        # loads the layer with default style (wherever it is defined)
        lyr = dataSource.createUnregisteredMapLayer()

        if isinstance(lyr, QgsRasterLayer) \
                and not LOAD_DEFAULT_STYLE \
                and isinstance(lyr.dataProvider(), QgsRasterDataProvider) \
                and lyr.dataProvider().name() == 'gdal':

            r = lyr.renderer()
            if isinstance(r, QgsRasterRenderer):
                bandIndices: typing.List[int] = None
                if isinstance(rgb, str):
                    if LOAD_DEFAULT_STYLE:
                        bandIndices = defaultBands(lyr)
                    else:
                        bandIndices = [bandClosestToWavelength(lyr, s) for s in rgb.split(',')]

                elif isinstance(rgb, list):
                    bandIndices = rgb

                if isinstance(bandIndices, list):
                    r = defaultRasterRenderer(lyr, bandIndices=bandIndices, sampleSize=sampleSize)
                    r.setInput(lyr.dataProvider())
                    lyr.setRenderer(r)

        elif isinstance(lyr, QgsVectorLayer):

            pass

        if isinstance(target, QgsMapCanvas):
            allLayers = target.layers()
            allLayers.append(lyr)
            target.setLayers(allLayers)
        elif isinstance(target, QgsProject):
            target.addMapLayer(lyr)

    def onSaveAs(self, dataSource):
        """
        Todo: save raster / vector sources
        """
        pass

    def onRemoveAllDataSources(self):
        model = self.model().sourceModel()
        if isinstance(model, DataSourceManagerTreeModel):
            model.dataSourceManager.clear()

    def openInSpeclibEditor(self, speclib: QgsVectorLayer):
        """
        Opens a SpectralLibrary in a new SpectralLibraryDock
        :param speclib: SpectralLibrary

        """
        from enmapbox.gui.enmapboxgui import EnMAPBox
        from enmapbox.gui.dataviews.docks import SpectralLibraryDock
        EnMAPBox.instance().dockManager().createDock(SpectralLibraryDock, speclib=speclib)

    def openInAttributeEditor(self, vectorLayer: QgsVectorLayer):
        from enmapbox.gui.enmapboxgui import EnMAPBox
        from enmapbox.gui.dataviews.docks import AttributeTableDock
        EnMAPBox.instance().dockManager().createDock(AttributeTableDock, layer=vectorLayer)


class DataSourcePanelUI(QgsDockWidget):
    def __init__(self, parent=None):
        super(DataSourcePanelUI, self).__init__(parent)
        loadUi(enmapboxUiPath('datasourcepanel.ui'), self)
        self.mDataSourceManager: DataSourceManager = None
        self.mDataSourceTreeModel: DataSourceManagerTreeModel = None
        self.mDataSourceProxyModel: DataSourceManagerProxyModel = DataSourceManagerProxyModel()
        assert isinstance(self.dataSourceTreeView, DataSourceTreeView)
        self.dataSourceTreeView.setUniformRowHeights(True)
        self.dataSourceTreeView.setDragDropMode(QAbstractItemView.DragDrop)

        # init actions
        self.actionAddDataSource.triggered.connect(lambda: self.mDataSourceManager.addDataSourceByDialog())
        self.actionRemoveDataSource.triggered.connect(
            lambda: self.mDataSourceManager.removeSources(self.selectedDataSources()))
        self.actionRemoveDataSource.setEnabled(False)  # will be enabled with selection of node

        # self.mDataSourceManager.exportSourcesToQGISRegistry(showLayers=True)
        self.actionSyncWithQGIS.triggered.connect(self.onSyncToQGIS)

        self.tbFilterText.textChanged.connect(self.setFilter)
        hasQGIS = qgisAppQgisInterface() is not None
        self.actionSyncWithQGIS.setEnabled(hasQGIS)

        self.initActions()

    def setFilter(self, pattern: str):
        self.mDataSourceProxyModel.setFilterWildcard(pattern)

    def onSyncToQGIS(self, *args):
        if isinstance(self.mDataSourceManager, DataSourceManager):
            self.mDataSourceManager.importSourcesFromQGISRegistry()

    def initActions(self):

        self.btnAddSource.setDefaultAction(self.actionAddDataSource)
        self.btnSync.setDefaultAction(self.actionSyncWithQGIS)
        self.btnRemoveSource.setDefaultAction(self.actionRemoveDataSource)
        self.btnCollapse.clicked.connect(lambda: self.expandSelectedNodes(self.dataSourceTreeView, False))
        self.btnExpand.clicked.connect(lambda: self.expandSelectedNodes(self.dataSourceTreeView, True))

    def expandSelectedNodes(self, treeView, expand):
        assert isinstance(treeView, QTreeView)

        treeView.selectAll()
        indices = treeView.selectedIndexes()
        if len(indices) == 0:
            treeView.selectAll()
            indices += treeView.selectedIndexes()
            treeView.clearSelection()
        for idx in indices:
            treeView.setExpanded(idx, expand)

    def connectDataSourceManager(self, dataSourceManager: DataSourceManager):
        """
        Initializes the panel with a DataSourceManager
        :param dataSourceManager: DataSourceManager
        """
        assert isinstance(dataSourceManager, DataSourceManager)
        self.mDataSourceManager = dataSourceManager
        self.mDataSourceTreeModel = DataSourceManagerTreeModel(self, self.mDataSourceManager)
        self.mDataSourceProxyModel.setSourceModel(self.mDataSourceTreeModel)
        self.dataSourceTreeView.setModel(self.mDataSourceProxyModel)
        self.dataSourceTreeView.selectionModel().selectionChanged.connect(self.onSelectionChanged)

    def onSelectionChanged(self, selected, deselected):

        s = self.selectedDataSources()
        self.actionRemoveDataSource.setEnabled(len(s) > 0)

    def selectedDataSources(self) -> list:
        """
        :return: [list-of-selected-DataSources]
        """
        sources = []
        model = self.dataSourceTreeView.model()
        for idx in self.dataSourceTreeView.selectionModel().selectedIndexes():
            assert isinstance(idx, QModelIndex)
            node = idx.data(Qt.UserRole)
            if isinstance(node, DataSourceTreeNode):
                if node.dataSource() not in sources:
                    sources.append(node.dataSource())
            elif isinstance(node, DataSourceGroupTreeNode):
                for s in node.dataSources():
                    if s not in sources:
                        sources.append(s)
        return sources


LUT_DATASOURCTYPES = collections.OrderedDict()
LUT_DATASOURCTYPES[DataSourceRaster] = \
    ('Raster Data',
     QIcon(':/images/themes/default/mIconRaster.svg'),
     'Raster data sources')
LUT_DATASOURCTYPES[DataSourceVector] = \
    ('Vector Data',
     QIcon(':/images/themes/default/mIconVector.svg'),
     'Vector data sources')
LUT_DATASOURCTYPES[HubFlowDataSource] = \
    ('Models',
     QIcon(':/images/themes/default/processingAlgorithm.svg'),
     'Model files and objects')
LUT_DATASOURCTYPES[DataSourceFile] = ('Other Files',
                                      QIcon(':/trolltech/styles/commonstyle/images/file-128.png'),
                                      None)
LUT_DATASOURCTYPES[DataSource] = ('Other sources',
                                  QIcon(':/trolltech/styles/commonstyle/images/standardbutton-open-32.png'),
                                  None)


class DataSourceManagerTreeModel(TreeModel):

    def __init__(self, parent, dataSourceManager: DataSourceManager):

        super(DataSourceManagerTreeModel, self).__init__(parent)
        assert isinstance(dataSourceManager, DataSourceManager)
        self.setColumnNames(['Source', 'Value'])
        self.dataSourceManager = dataSourceManager
        self.dataSourceManager.sigDataSourceAdded.connect(self.addDataSource)
        self.dataSourceManager.sigDataSourceRemoved.connect(self.removeDataSource)

        for ds in self.dataSourceManager.mSources:
            self.addDataSource(ds)

    def columnCount(self, index):
        return 2

    def mimeTypes(self):
        # specifies the mime types handled by this model
        types = []
        types.append(MDF_DATASOURCETREEMODELDATA)
        types.append(MDF_QGIS_LAYERTREEMODELDATA)
        types.append(QGIS_URILIST_MIMETYPE)
        types.append(MDF_URILIST)
        return types

    def dropMimeData(self, data, action, row, column, parent):
        parentNode = self.idx2node(parent)
        assert isinstance(data, QMimeData)

        result = False
        added = []
        if action in [Qt.MoveAction, Qt.CopyAction]:
            # collect nodes
            nodes = []

            if data.hasFormat(MDF_DATASOURCETREEMODELDATA):
                return False  # do not allow moving within DataSourceTree

            # add new data from external sources
            elif data.hasFormat(MDF_URILIST):
                for url in data.urls():
                    added.extend(self.dataSourceManager.addSource(url))

            # add data dragged from QGIS
            elif data.hasFormat(MDF_QGIS_LAYERTREEMODELDATA) or data.hasFormat(QGIS_URILIST_MIMETYPE):

                lyrs = extractMapLayers(data)

                added.extend([self.dataSourceManager.addSource(l) for l in lyrs])
        #                return  any(added)

        # if len(lyrs) > 0:

        # doc = QDomDocument()
        # doc.setContent(data.data(MDF_QGIS_LAYERTREEMODELDATA))
        # rootElem = doc.documentElement()
        # elem = rootElem.firstChildElement()
        # added = []
        # while not elem.isNull():
        #    node = QgsLayerTreeNode.readXml(elem, QgsProject.instance())
        #    added.extend(self.dataSourceManager.addSource(node))
        #    elem = elem.nextSiblingElement()
        # return any([isinstance(ds, DataSource) for ds in added])

        # result = QgsLayerTreeModel.dropMimeData(self, data, action, row, column, parent)

        return len(added) > 0

    def mimeData(self, indexes: list) -> QMimeData:
        indexes = sorted(indexes)
        if len(indexes) == 0:
            return None

        nodesFinal = self.indexes2nodes(indexes)
        mimeData = QMimeData()
        # define application/enmapbox.datasourcetreemodeldata
        exportedNodes = []

        # collect nodes to be exported as mimeData
        for node in nodesFinal:
            # avoid doubling
            if node in exportedNodes:
                continue
            if isinstance(node, DataSourceTreeNode) and node not in exportedNodes:
                exportedNodes.append(node)

            elif isinstance(node, DataSourceGroupTreeNode):
                for n in node.childNodes():
                    if n not in exportedNodes:
                        exportedNodes.append(n)

            elif isinstance(node, RasterBandTreeNode):
                if node not in exportedNodes:
                    exportedNodes.append(node)

        uriList = list()
        uuidList = list()

        bandInfo = list()

        for node in exportedNodes:
            if isinstance(node, RasterBandTreeNode):
                uri = node.mDataSource.uri()
                provider = node.mDataSource.provider()
                band = node.mBandIndex
                baseName = '{}:{}'.format(node.mDataSource.name(), node.name())
                bandInfo.append((uri, baseName, provider, band))

            elif isinstance(node, DataSourceTreeNode):
                dataSource = node.mDataSource
                assert isinstance(dataSource, DataSource)
                uriList.append(dataSource.uri())
                uuidList.append(dataSource.uuid())

                if False:
                    if isinstance(dataSource, DataSourceSpectralLibrary):
                        from ..externals.qps.speclib.core import MIMEDATA_SPECLIB_LINK
                        mimeDataSpeclib = dataSource.speclib().mimeData(formats=[MIMEDATA_SPECLIB_LINK])
                        for f in mimeDataSpeclib.formats():
                            if f not in mimeData.formats():
                                mimeData.setData(f, mimeDataSpeclib.data(f))

        if len(uuidList) > 0:
            mimeData.setData(MDF_DATASOURCETREEMODELDATA, pickle.dumps(uuidList))

        if len(bandInfo) > 0:
            mimeData.setData(MDF_RASTERBANDS, pickle.dumps(bandInfo))

        urls = [QUrl.fromLocalFile(uri) if os.path.isfile(uri) else QUrl(uri) for uri in uriList]
        if len(urls) > 0:
            mimeData.setUrls(urls)
        return mimeData

    def sourceGroups(self) -> list:
        return [n for n in self.rootNode().childNodes() if isinstance(n, DataSourceGroupTreeNode)]

    def sourceGroup(self, dataSource: DataSource) -> DataSourceGroupTreeNode:
        """
        Returns the DataSourceGroupTreeNode related to a given data source.
        :param dataSource: DataSource
        :return: DataSourceGroupTreeNode
        """
        """"""
        assert isinstance(dataSource, DataSource)

        for groupDataType, t in LUT_DATASOURCTYPES.items():
            if isinstance(dataSource, groupDataType):
                groupName, groupIcon, groupToolTip = t
                break
        if groupName is None:
            groupName, groupIcon, groupToolTip = LUT_DATASOURCTYPES[DataSource]
            if groupToolTip is None:
                groupToolTip = groupName
            groupDataType = DataSource

        srcGroups = self.sourceGroups()
        srcGrp = [c for c in srcGroups if c.groupName() == groupName]
        if len(srcGrp) == 0:
            # group node does not exist.
            # create new group node and add it to the model
            srcGrp = DataSourceGroupTreeNode(groupName, groupDataType)
            srcGrp.setToolTip(groupToolTip)
            srcGrp.setIcon(groupIcon)

            self.rootNode().appendChildNodes(srcGrp)
        elif len(srcGrp) == 1:
            srcGrp = srcGrp[0]
        return srcGrp

    def addDataSource(self, dataSource: DataSource):
        """
        Adds a DataSource and creates an TreeNode for
        :param dataSource: DataSource
        """
        assert isinstance(dataSource, DataSource)
        sourceGroupNode = self.sourceGroup(dataSource)
        assert isinstance(sourceGroupNode, DataSourceGroupTreeNode)
        assert sourceGroupNode.parentNode() == self.rootNode()

        dataSourceNode = createNodeFromDataSource(dataSource, sourceGroupNode)

    def removeDataSource(self, dataSource):

        assert isinstance(dataSource, DataSource)
        sourceGroup = self.sourceGroup(dataSource)
        to_remove = []

        for node in sourceGroup.childNodes():
            assert isinstance(node, DataSourceTreeNode)

            if node.dataSource() == dataSource:
                to_remove.append(node)

        sourceGroup.removeChildNodes(to_remove)

    def supportedDragActions(self):
        return Qt.CopyAction

    def supportedDropActions(self):
        return Qt.CopyAction

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsDropEnabled

        # specify TreeNode specific actions
        node = self.idx2node(index)

        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDropEnabled

        if isinstance(node, (DataSourceTreeNode, RasterBandTreeNode, DataSourceGroupTreeNode)):
            flags = flags | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled

        elif type(node) in [QgsLayerTreeLayer, QgsLayerTreeGroup]:
            flags = flags | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled

        if isinstance(node, TreeNode) and node.isCheckable():
            flags = flags | Qt.ItemIsUserCheckable

        return flags

    def contextMenu(self, node):
        menu = QMenu()
        if isinstance(node, DataSourceGroupTreeNode):
            a = menu.addAction('Clear')
            a.triggered.connect(lambda: self.dataSourceManager.removeSources(node.dataSources()))

        if isinstance(node, DataSourceTreeNode):
            a = menu.addAction('Remove')
            a.triggered.connect(lambda: self.dataSourceManager.removeSource(node.dataSource))

        if isinstance(node, HubFlowObjectTreeNode):
            a = menu.addAction('Show report')
            a.triggered.connect(lambda: self.onShowModelReport(node.dataSource))

        if isinstance(node, VectorDataSourceTreeNode):
            a = menu.addAction('Open')
            dataSource: DataSourceVector = node.dataSource()
            if isinstance(dataSource, DataSourceVector):
                if dataSource.isSpectralLibrary():
                    a.triggered.connect(lambda ds=dataSource: self.onOpenSpeclib(ds.createUnregisteredMapLayer()))
                else:
                    a.triggered.connect(lambda ds=dataSource: self.onOpenVectorLayer(ds.createUnregisteredMapLayer()))

        # append node-defined context menu
        menu2 = node.contextMenu()

        if menu2 is not None:
            menu2.setTitle('CRS Options')
            menu2.setVisible(True)
            menu.addMenu(menu2)
            """
            for a in menu2.actions():
                menu.addAction(a)
            """
        menu.setVisible(True)
        return menu

    def onOpenSpeclib(self, speclib: SpectralLibrary):
        from enmapbox.gui.enmapboxgui import EnMAPBox
        EnMAPBox.instance().dockManager().createDock('SPECLIB', speclib=speclib)

    def onOpenVectorLayer(self, layer: QgsVectorLayer):
        from enmapbox.gui.enmapboxgui import EnMAPBox
        EnMAPBox.instance().dockManager().createDock('MAP', layer)

    def onShowModelReport(self, model):
        assert isinstance(model, HubFlowDataSource)
        pfType = model.pfType

        # this step should be done without writing anything on hard disk
        pathHTML = pfType.report().saveHTML().filename
        from enmapbox.gui.enmapboxgui import EnMAPBox
        EnMAPBox.instance().dockManager().createDock('WEBVIEW', url=pathHTML)


class DataSourceManagerProxyModel(QSortFilterProxyModel):

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.setRecursiveFilteringEnabled(True)
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)


def createNodeFromDataSource(dataSource: DataSource, parent: TreeNode = None) -> DataSourceTreeNode:
    """
    Generates a DataSourceTreeNode
    :param dataSource:
    :param parent:
    :return:
    """

    if not isinstance(dataSource, DataSource):
        return None

    # hint: take care of class inheritance order. inherited classes first
    if isinstance(dataSource, HubFlowDataSource):
        node = HubFlowObjectTreeNode()
    elif isinstance(dataSource, DataSourceRaster):
        node = RasterDataSourceTreeNode()
    elif isinstance(dataSource, DataSourceVector):
        node = VectorDataSourceTreeNode()
    elif isinstance(dataSource, DataSourceFile):
        node = FileDataSourceTreeNode()
    else:
        node = DataSourceTreeNode()
    node.connectDataSource(dataSource)

    if isinstance(node, DataSourceTreeNode) and isinstance(parent, TreeNode):
        parent.appendChildNodes(node)
    return node
