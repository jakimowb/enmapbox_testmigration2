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

import inspect, pickle

from enmapbox import DIR_TESTDATA
from enmapbox.gui.treeviews import TreeNode, CRSTreeNode, TreeView, TreeModel, CheckableTreeNode, TreeViewMenuProvider, ClassificationNode, ColorTreeNode
from enmapbox.gui.datasources import *
from enmapbox.gui.utils import *
from enmapbox.gui.mimedata import MDF_DATASOURCETREEMODELDATA, MDF_LAYERTREEMODELDATA, MDF_URILIST
from enmapbox.gui.mapcanvas import MapDock

HUBFLOW = True

HIDDEN_DATASOURCE = '__HIDDEN__DATASOURCE'
try:
    import hubflow.core
    s = ""

except Exception as ex:
    messageLog('Unable to import hubflow API. Error "{}"'.format(ex), level=Qgis.Warning)
    HUBFLOW = False

class DataSourceManager(QObject):
    _testInstance = None

    @staticmethod
    def instance():
        from enmapbox.gui.enmapboxgui import EnMAPBox
        if isinstance(EnMAPBox.instance(), EnMAPBox):
            return EnMAPBox.instance().dataSourceManager
        else:
            return DataSourceManager._testInstance

    """
    Keeps overview on different data sources handled by EnMAP-Box.
    Similar like QGIS data registry, but manages non-spatial data sources (text files etc.) as well.
    """

    sigDataSourceAdded = pyqtSignal(DataSource)
    sigDataSourceRemoved = pyqtSignal(DataSource)

    SOURCE_TYPES = ['ALL', 'ANY', 'RASTER', 'VECTOR', 'SPATIAL', 'MODEL']

    def __init__(self):
        super(DataSourceManager, self).__init__()
        DataSourceManager._testInstance = self
        self.mSources = list()

        self.mQgsLayerTreeGroup = None
        # self.qgsLayerTreeGroup()

        # todo: react on QgsProject changes, e.g. when project is closed
        # QgsProject.instance().layersAdded.connect(self.updateFromQgsProject)
        # noinspection PyArgumentList

        try:
            from hubflow import signals
            signals.sigFileCreated.connect(self.addSource)
        except Exception as ex:
            messageLog(ex)

        self.updateFromQgsProject()

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

    def sources(self, sourceTypes=None) -> list:
        """
        Returns the managed DataSources
        :param sourceTypes: the sourceType(s) to return
            a) str like 'VECTOR' (see DataSourceManage.SOURCE_TYPES)
            b) class type derived from DataSource
            c) a list of a or b to filter multpiple source types
        :return:
        """
        results = self.mSources[:]

        if sourceTypes:
            if not isinstance(sourceTypes, list):
                sourceTypes = [sourceTypes]
            filterTypes = []
            for sourceType in sourceTypes:
                if sourceType in self.SOURCE_TYPES:
                    if sourceType == 'VECTOR':
                        sourceType = DataSourceVector
                    elif sourceType == 'RASTER':
                        sourceType = DataSourceRaster
                    elif sourceType == 'MODEL':
                        sourceType = HubFlowDataSource
                    else:
                        sourceType = None
                if isinstance(sourceType, type(DataSource)):
                    filterTypes.append(sourceType)
            results = [r for r in results if type(r) in filterTypes]
        return results

    def updateFromProcessingFramework(self):
        if self.processing:
            # import logging
            # logging.debug('Todo: Fix processing implementation')
            return
            for p, n in zip(self.processing.MODEL_URIS,
                            self.processing.MODEL_NAMES):
                self.addSource(p, name=n)

    def updateFromQgsProject(self, mapLayers=None):
        """
        Add data sources registered in the QgsProject to the data source manager
        :return: List of added new DataSources
        """
        if mapLayers is None:
            mapLayers = QgsProject.instance().mapLayers().values()

        added = [self.addSource(lyr) for lyr in mapLayers]
        return [a for a in added if isinstance(a, DataSource)]

    def getUriList(self, sourcetype='ALL') -> list:
        """
        Returns URIs of registered data sources
        :param sourcetype: uri filter: 'ALL' (default),'RASTER', 'VECTOR', 'SPATIAL' (raster+vector) or 'MODEL' to return only uri's related to these sources
        :return: uri as string (str), e.g. a file path
        """
        sourcetype = sourcetype.upper()
        if isinstance(sourcetype, type):
            return [ds.uri() for ds in self.mSources if type(ds) is sourcetype]

        assert sourcetype in DataSourceManager.SOURCE_TYPES
        if sourcetype in ['ALL', 'ANY']:
            return [ds.uri() for ds in self.mSources]
        elif sourcetype == 'VECTOR':
            return [ds.uri() for ds in self.mSources if isinstance(ds, DataSourceVector)]
        elif sourcetype == 'RASTER':
            return [ds.uri() for ds in self.mSources if isinstance(ds, DataSourceRaster)]
        elif sourcetype == 'SPATIAL':
            return [ds.uri() for ds in self.mSources if isinstance(ds, DataSourceSpatial)]
        elif sourcetype == 'MODEL':
            return [ds.uri() for ds in self.mSources if isinstance(ds, HubFlowDataSource)]
        else:
            return []

    def onMapLayerRegistryLayersAdded(self, lyrs:list):
        """
        Response to added layers in the QGIS layer registry
        :param lyrs: [list-of-added-QgsMapLayer]
        """
        lyrsToAdd = []
        for l in lyrs:
            assert isinstance(l, QgsMapLayer)

        #todo: do we need to filter something here?

        """
        for lyr in lyrs:
            if isinstance(lyr, QgsVectorLayer):
                if lyr.dataProvider().dataSourceUri().startswith('memory?'):
                    continue
            lyrsToAdd.append(lyr)
        """
        lyrsToAdd = lyrs
        self.addSources(lyrsToAdd)

    def addSources(self, sources) -> list:
        added = []
        for s in sources:
            added.extend(self.addSource(s))
        added = [a for a in added if isinstance(a, DataSource)]

        return added

    @pyqtSlot(str)
    @pyqtSlot('QString')
    def addSource(self, newDataSource, name=None, icon=None):
        """
        Adds a new data source.
        :param newDataSource: any object
        :param name:
        :param icon:
        :return: a list of successfully added DataSource instances.
                 Usually this will be a list with a single DataSource instance only, but in case of container datasets multiple instances might get returned.
        """
        newDataSources = DataSourceFactory.Factory(newDataSource, name=name, icon=icon)

        toAdd = []
        for dsNew in newDataSources:
            assert isinstance(dsNew, DataSource)
            if not isinstance(dsNew, DataSourceFile):
                toAdd.append(dsNew)

            else:

                sameSources = [d for d in self.mSources if dsNew.isSameSource(d)]
                if len(sameSources) == 0:
                    toAdd.append(dsNew)
                else:
                    older = []
                    newer = []
                    for d in sameSources:
                        if dsNew.isNewVersionOf(d):
                            older.append(dsNew)
                        else:
                            newer.append(d)
                    # do not add this source in case there is a newer one
                    if len(newer) == 0:
                        self.removeSources(older)
                        toAdd.append(dsNew)
                    else:
                        toAdd.extend(newer)  # us ethe reference of the existing one

        for ds in toAdd:
            if ds not in self.mSources:
                self.mSources.append(ds)
                self.sigDataSourceAdded.emit(ds)

        return toAdd

    def addDataSourceByDialog(self):
        """
        Shows a fileOpen dialog to select new data sources
        :return:
        """

        from enmapbox import enmapboxSettings
        SETTINGS = enmapboxSettings()
        lastDataSourceDir = SETTINGS.value('lastsourcedir', None)

        if lastDataSourceDir is None:
            lastDataSourceDir = DIR_TESTDATA

        if not os.path.exists(lastDataSourceDir):
            lastDataSourceDir = None

        uris = QFileDialog.getOpenFileNames(None, "Open a data source(s)", lastDataSourceDir)
        self.addSources(uris)

        if len(uris) > 0:
            SETTINGS.setValue('lastsourcedir', os.path.dirname(uris[-1]))

    def importSourcesFromQGISRegistry(self):
        """
        Adds datasources known to QGIS which do not exist here
        """
        p = QgsProject.instance()
        assert isinstance(p, QgsProject)
        layers = list(p.mapLayers().values())

        self.addSources(layers)



    def exportSourcesToQGISRegistry(self, showLayers:bool=False):
        """
        Adds spatial datasources to QGIS
        :param showLayers: False, set on True to show added layers in QGIS Layer Tree
        """


        allLayers = list(QgsProject.instance().mapLayers().values())
        visbileLayers = qgisLayerTreeLayers()

        allSources = [l.source() for l in allLayers]
        visibleSources = [l.source() for l in visbileLayers]
        iface = qgisAppQgisInterface()

        for dataSource in self.sources():
            if isinstance(dataSource, DataSourceSpatial):
                l = dataSource.createUnregisteredMapLayer()
                if not l.isValid():
                    print('INVALID LAYER FROM DATASOURCE: {} {}'.format(l, l.source()), file=sys.stderr)
                    continue
                if l.source() not in allSources:
                    QgsProject.instance().addMapLayer(l, showLayers)
                else:
                    if iface and showLayers and l.source() not in visibleSources:
                        i = allSources.index(l.source())
                        knownLayer = allLayers[i]
                        assert isinstance(knownLayer, QgsMapLayer)
                        iface.layerTreeView().model().rootGroup().addLayer(knownLayer)


    def clear(self):
        """
        Removes all data source from DataSourceManager
        :return: [list-of-removed-DataSources]
        """
        return self.removeSources(list(self.mSources))

    def removeSources(self, dataSourceList: list = None) -> list:
        """
        Removes a list of data sources.
        :param dataSourceList: [list-of-datasources]
        :return: self
        """
        if dataSourceList is None:
            dataSourceList = self.sources()
        removed = [self.removeSource(dataSource) for dataSource in dataSourceList]
        return [r for r in removed if isinstance(r, DataSource)]

    def removeSource(self, dataSource):
        """
        Removes the datasource from the DataSourceManager
        :param dataSource: the DataSource to be removed
        :return: the removed DataSource. None if dataSource was not in the DataSourceManager
        """
        assert isinstance(dataSource, DataSource)
        if dataSource in self.mSources:
            self.mSources.remove(dataSource)
            self.sigDataSourceRemoved.emit(dataSource)
            return dataSource
        else:
            messageLog('can not remove {}'.format(dataSource))

    def sourceTypes(self):
        """
        Returns the list of source-types handled by this DataSourceManager
        :return: [list-of-source-types]
        """
        return sorted(list(set([type(ds) for ds in self.mSources])), key=lambda t: t.__name__)


class DataSourceGroupTreeNode(TreeNode):

    def __init__(self, parent, groupName, classDef, icon=None):
        assert inspect.isclass(classDef)

        if icon is None:
            icon = QApplication.style().standardIcon(QStyle.SP_DirOpenIcon)

        super(DataSourceGroupTreeNode, self).__init__(parent, groupName, icon=icon)
        self.childClass = classDef

    def dataSources(self):
        return [d.dataSource for d in self.children()
                if isinstance(d, DataSourceTreeNode)]

    def addChildNode(self, node):
        """Ensure child types"""
        assert isinstance(node, DataSourceTreeNode)
        assert isinstance(node.dataSource, self.childClass)
        super(DataSourceGroupTreeNode, self).addChildNode(node)

    def writeXML(self, parentElement):
        elem = super(DataSourceGroupTreeNode, self).writeXML(parentElement)
        elem.setTagName('data_source_group_tree_node')
        elem.setAttribute('datasourcetype', str(self.childClass))
        return elem

    def dataSources(self):
        return [child.dataSource for child in self.children()]


    @staticmethod
    def readXml(element):

        if element.tagName() != 'data_source_group_tree_node':
            return None


        name = None
        classDef = None
        node = DataSourceGroupTreeNode(None, name, classDef)

        TreeNode.attachCommonPropertiesFromXML(node, element)

        return node


class DataSourceSizesTreeNode(TreeNode):
    """
    A node to show the different aspects of dataSource sizes
    Sub-Nodes:
        spatial extent in map unit
        pixel sizes (if raster source)
        pixel extent (if raster source)
    """
    def __init__(self, parent, dataSource):
        assert isinstance(dataSource, DataSourceFile)
        super(DataSourceSizesTreeNode, self).__init__(parent, 'Size')

        fileSize = os.path.getsize(dataSource.uri())
        fileSize = fileSizeString(fileSize)

        n = TreeNode(self, 'File', value=fileSize, icon=dataSource.icon())
        if isinstance(dataSource, DataSourceSpatial):
            ext = dataSource.mSpatialExtent
            mu = QgsUnitTypes.encodeUnit(ext.crs().mapUnits())

            n = TreeNode(self, 'Spatial Extent')
            TreeNode(n, 'Width', value='{} {}'.format(ext.width(), mu))
            TreeNode(n, 'Heigth', value='{} {}'.format(ext.height(), mu))

        if isinstance(dataSource, DataSourceRaster):
            n = TreeNode(self, 'Pixels')
            TreeNode(n, 'Samples (x)', value='{}'.format(dataSource.nSamples))
            TreeNode(n, 'Lines (y)', value='{}'.format(dataSource.nLines))
            TreeNode(n, 'Bands (z)', value='{}'.format(dataSource.nBands))



class DataSourceTreeNode(TreeNode, KeepRefs):

    def __init__(self, parent:TreeNode, dataSource:DataSource):

        self.dataSource = None
        self.nodeSize = None

        super(DataSourceTreeNode, self).__init__(parent, '<empty>')
        KeepRefs.__init__(self)
        self.disconnectDataSource()
        if dataSource:
            self.connectDataSource(dataSource)

    def connectDataSource(self, dataSource):
        from enmapbox.gui.datasources import DataSource
        assert isinstance(dataSource, DataSource)
        self.dataSource = dataSource
        self.setName(dataSource.name())

        self.setTooltip(dataSource.uri())
        self.setIcon(dataSource.icon())
        self.setCustomProperty('uuid', str(self.dataSource.mUuid))
        self.setCustomProperty('uri', self.dataSource.uri())
        uri = self.dataSource.uri()
        if os.path.isfile(uri):
            self.mSrcSize = os.path.getsize(self.dataSource.uri())
            self.nodeSize = TreeNode(self, 'File size', value=fileSizeString(self.mSrcSize))
        else:
            self.mSrcSize = -1


    def disconnectDataSource(self):
        self.dataSource = None
        if self.nodeSize:
            self.removeChildNode(self.nodeSize)
            self.nodeSize = None

        self.setName(None)
        self.setIcon(None)
        self.setTooltip(None)
        for k in self.customProperties():
            self.removeCustomProperty(k)

    @staticmethod
    def readXml(element):
        if element.tagName() != 'datasource-tree-node':
            return None

        cp = QgsObjectCustomProperties()
        cp.readXml(element)

        from enmapbox.gui.datasources import DataSourceFactory
        dataSources = DataSourceFactory.Factory(cp.value('uri'), name=element.attribute('name'))
        if len(dataSources) == 1:
            node = DataSourceTreeNode(None, dataSources[0])
            TreeNode.attachCommonPropertiesFromXML(node, element)
        else:
            #todo: check if this case can get true
            pass

        return node

    def writeXML(self, parentElement):
        super(DataSourceTreeNode, self).writeXML(parentElement)
        elem = parentElement.lastChild().toElement()
        elem.setTagName('datasource-tree-node')
        elem.setAttribute('uuid', '{}'.format(self.dataSource.uuid()))


class SpatialDataSourceTreeNode(DataSourceTreeNode):

    def __init__(self, *args, **kwds):
        self.nodeCRS = None
        #extent in map units (mu)
        self.nodeExtXmu = None
        self.nodeExtYmu = None
        super(SpatialDataSourceTreeNode,self).__init__( *args, **kwds)


    def connectDataSource(self, dataSource):
        assert isinstance(dataSource, DataSourceSpatial)
        super(SpatialDataSourceTreeNode, self).connectDataSource(dataSource)
        ext = dataSource.mSpatialExtent
        mu = QgsUnitTypes.toString(ext.crs().mapUnits())
        assert isinstance(ext, SpatialExtent)
        assert self.nodeCRS is None
        self.nodeCRS = CRSTreeNode(self, ext.crs())
        self.nodeExtXmu = TreeNode(self.nodeSize, 'Width', value='{} {}'.format(ext.width(), mu))
        self.nodeExtYmu = TreeNode(self.nodeSize, 'Height', value='{} {}'.format(ext.height(), mu))

    def disconnectDataSource(self):
        super(SpatialDataSourceTreeNode, self).disconnectDataSource()
        if self.nodeCRS:
            self.removeChildNode(self.nodeCRS)
            self.removeChildNode(self.nodeExtXmu)
            self.removeChildNode(self.nodeExtYmu)
            self.nodeCRS = None
            self.nodeExtXmu = None
            self.nodeExtYmu = None


class VectorDataSourceTreeNode(SpatialDataSourceTreeNode):
    def __init__(self, *args, **kwds):
        super(VectorDataSourceTreeNode,self).__init__( *args, **kwds)
        self.nodeFeatures = None
        self.nodeFields = None

    def connectDataSource(self, dataSource:DataSourceVector):
        super(VectorDataSourceTreeNode, self).connectDataSource(dataSource)

        lyr = self.dataSource.createUnregisteredMapLayer()
        assert lyr.isValid()
        nFeat = lyr.featureCount()
        nFields = lyr.fields().count()

        geomType = ['Point','Line','Polygon','Unknown','Null'][lyr.geometryType()]
        wkbType = QgsWkbTypes.displayString(int(lyr.wkbType()))
        #self.nodeSize.setValue('{} x {}'.format(nFeat, fileSizeString(self.mSrcSize)))
        self.nodeFeatures = TreeNode(self, 'Features',
                                   value='{}'.format(nFeat))
        TreeNode(self.nodeFeatures, 'Geometry Type', value=geomType)

        TreeNode(self.nodeFeatures, 'WKB Type', value=wkbType)

        self.nodeFields = TreeNode(self, 'Fields',
                                   tooltip='Attribute fields related to each feature',
                                   value='{}'.format(nFields))
        for i in range(nFields):
            field = lyr.fields().at(i)
            node = TreeNode(self.nodeFields, field.name(),
                            value='{} {}'.format(field.typeName(), field.length()))

        s = ""


class RasterBandTreeNode(TreeNode):

    def __init__(self,  dataSource, bandIndex, *args, **kwds):
        super(RasterBandTreeNode, self).__init__( *args, **kwds)
        assert isinstance(dataSource, DataSourceRaster)
        assert bandIndex >= 0
        assert bandIndex < dataSource.nBands
        self.mDataSource = dataSource
        self.mBandIndex = bandIndex

        md = self.mDataSource.mBandMetadata[bandIndex]
        from enmapbox.gui.classificationscheme import ClassificationScheme, ClassInfo
        classScheme = md.get('__ClassificationScheme__')
        if isinstance(classScheme, ClassificationScheme):
            for ci in classScheme:
                assert isinstance(ci, ClassInfo)
                TreeNode(self, str(ci.label()),ci.name(), icon=ci.icon())




class RasterDataSourceTreeNode(SpatialDataSourceTreeNode):
    def __init__(self, *args, **kwds):
        #extents in pixel
        self.nodeExtXpx = None
        self.nodeExtYpx = None
        self.nodeBands = None
        self.nodePxSize = None
        super(RasterDataSourceTreeNode,self).__init__( *args, **kwds)

        s = ""



    def connectDataSource(self, dataSource):
        assert isinstance(dataSource, DataSourceRaster)
        super(RasterDataSourceTreeNode, self).connectDataSource(dataSource)

        self.setIcon(dataSource.icon())
        mu = QgsUnitTypes.toString(dataSource.spatialExtent().crs().mapUnits())


        self.nodeExtXpx = TreeNode(self.nodeSize, 'Samples',
                                   tooltip='Data Source Width in Pixel',
                                   value='{} px'.format(dataSource.nSamples))
        self.nodeExtYpx = TreeNode(self.nodeSize, 'Lines',
                                   tooltip='Data Source Height in Pixel',
                                   value='{} px'.format(dataSource.nLines))

        pxSize = dataSource.mPxSize
        self.nodePxSize = TreeNode(self.nodeSize, 'Pixel',
                                   tooltip='Spatial size of single pixel',
                                   value='{}x{}{}'.format(pxSize.width(), mu, pxSize.height()))

        self.nodeSize.setValue('{}x{}x{}'.format(dataSource.nSamples,
                                                 dataSource.nLines,
                                                 dataSource.nBands))

        self.nodeBands = TreeNode(self, 'Bands',
                                  tooltip='Number of Raster Bands',
                                  value='{}'.format(dataSource.nBands))


        for b, bandName in enumerate(dataSource.mBandNames):
            bandNode = RasterBandTreeNode(dataSource, b, self.nodeBands, bandName, value=bandName)





    def disconnectDataSource(self):
        if self.nodeExtXpx is not None:
            self.nodeExtXpx = self._removeSubNode(self.nodeExtXpx)
            self.nodeExtYpx = self._removeSubNode(self.nodeExtYpx)
            self.nodeBands = self._removeSubNode(self.nodeBands)
            self.nodePxSize = self._removeSubNode(self.nodePxSize)
        pass

class FileDataSourceTreeNode(DataSourceTreeNode):

    def __init__(self, *args, **kwds):
        super(FileDataSourceTreeNode,self).__init__( *args, **kwds)

class SpeclibProfilesTreeNode(TreeNode):

    def __init__(self, parent, speclib, **kwds):
        super(SpeclibProfilesTreeNode, self).__init__(parent, 'Profiles', **kwds)
        from enmapbox.gui.spectrallibraries import SpectralLibrary
        assert isinstance(speclib, SpectralLibrary)
        self.mSpeclib = speclib
        speclib.committedFeaturesAdded.connect(self.update)
        speclib.committedFeaturesRemoved.connect(self.update)
        self.update()
        assert isinstance(self.mSpeclib, SpectralLibrary)


    def update(self, *args):
        self.setValue(len(self.mSpeclib))

    def fetchCount(self):
        from enmapbox.gui.spectrallibraries import SpectralLibrary
        if isinstance(self.mSpeclib, SpectralLibrary):
            return len(self.mSpeclib)
        else:
            return 0

    def fetchNext(self):
        from enmapbox.gui.spectrallibraries import SpectralLibrary
        if isinstance(self.mSpeclib, SpectralLibrary):
            for p in self.mSpeclib:
                TreeNode(self, p.name())

class SpeclibDataSourceTreeNode(FileDataSourceTreeNode):
    def __init__(self, *args, **kwds):
        super(SpeclibDataSourceTreeNode, self).__init__(*args, **kwds)

        self.profileNode = None
        self.mSpeclib = None

    def connectDataSource(self, dataSource):
        assert isinstance(dataSource, DataSourceSpectralLibrary)
        super(SpeclibDataSourceTreeNode, self).connectDataSource(dataSource)

        from enmapbox.gui.spectrallibraries import SpectralLibrary

        assert isinstance(self.dataSource.mSpeclib, SpectralLibrary)

        self.profileNode = SpeclibProfilesTreeNode(self, dataSource.mSpeclib)
        #self.profileNode.mSpeclib = dataSource.mSpeclib
        #self.profiles= TreeNode(self, 'Profiles',
        #                            tooltip='Spectral profiles',
        #                            value='{}'.format(len(self.dataSource.mSpeclib)))
        #for name in dataSource.profileNames:
        #    TreeNode(self.profiles, name)

class HubFlowObjectTreeNode(DataSourceTreeNode):

    def __init__(self, *args, **kwds):
        super(HubFlowObjectTreeNode, self).__init__(*args, **kwds)
        self.flowObject = None

    def connectDataSource(self, processingTypeDataSource):
        super(HubFlowObjectTreeNode, self).connectDataSource(processingTypeDataSource)
        assert isinstance(self.dataSource, HubFlowDataSource)


        if isinstance(self.dataSource.flowObject(), hubflow.core.FlowObject):

            moduleName = self.dataSource.flowObject().__class__.__module__
            className = self.dataSource.flowObject().__class__.__name__
            #self.setValue('{}.{}'.format(moduleName, className))
            self.setName(className)
            self.setTooltip('{}.{}'.format(moduleName, className))
            self.fetchInternals(self.dataSource.flowObject(), parentTreeNode=self)

    @staticmethod
    def fetchInternals(obj:object, parentTreeNode:TreeNode=None, fetchedObjectIds:set=None)->TreeNode:
        """
        Represents a python object as TreeNode structure.
        :param obj: any type of python object
                    lists, sets and dictionaries will be shown as subtree
                    basic builtin objects (float, int, str, numpy.arrays) are show as str(obj) value
        :param parentTreeNode: the parent Node. Need to have a name
        :param fetchedObjectIds: reminder of already used objects. necessary to avoid circular references
        :return: TreeNode
        """
        if parentTreeNode is None:
            parentTreeNode = TreeNode(None, '\t')
        assert isinstance(parentTreeNode, TreeNode)

        pName = parentTreeNode.name()

        if fetchedObjectIds is None:
            fetchedObjectIds = set()

        assert isinstance(fetchedObjectIds, set)
        if id(obj) in fetchedObjectIds:
            # do not return any node for objects already described.
            # this is necessary to avoid circular references

            parentTreeNode.setValue(str(obj))
            return parentTreeNode


        fetchedObjectIds.add(id(obj))

        if 'feature_importances_' in pName:
            s = ""
        fetch = HubFlowObjectTreeNode.fetchInternals


        if isinstance(obj, hubflow.core.FlowObject):
            # for all FlowObjects
            moduleName = obj.__class__.__module__
            className = obj.__class__.__name__

            parentTreeNode.setValue('{}.{}'.format(moduleName, className))
            #ClassDefinitions
            if isinstance(obj, hubflow.core.ClassDefinition):
                from enmapbox.gui.classificationscheme import ClassificationScheme, ClassInfo
                csi = ClassificationScheme()

                for label in range(obj.classes()):
                    ci = ClassInfo(label=label, name=obj.name(label+1), color=QColor(obj.color(label+1)))
                    csi.addClass(ci)
                ClassificationNode(parentTreeNode, csi, name='Classes')

            fetch(obj.__dict__, parentTreeNode=parentTreeNode, fetchedObjectIds=fetchedObjectIds)


        elif isinstance(obj, dict):
            """
            Show dictionary
            """
            s = ""
            for key in sorted(obj.keys()):
                value = obj[key]
                name = str(key)
                if name.startswith('__'):
                    continue


                if re.search('_(vector|raster).*', name):
                    s = ""
                node = TreeNode(parentTreeNode, name)
                fetch(value, parentTreeNode=node, fetchedObjectIds=fetchedObjectIds)

        elif isinstance(obj, np.ndarray):

            if obj.ndim == 1:
                fetch(list(obj), parentTreeNode=parentTreeNode, fetchedObjectIds=fetchedObjectIds)
            else:
                parentTreeNode.setValue(str(obj))


        elif isinstance(obj, list) or isinstance(obj, set):
            """Show enumerations"""

            for i, item in enumerate(obj):
                node = TreeNode(parentTreeNode, str(i+1))
                fetch(item, parentTreeNode=node, fetchedObjectIds=fetchedObjectIds)
                if i > 100:
                    node = TreeNode(parentTreeNode, '...')
                    break
        elif isinstance(obj, QColor):
            ColorTreeNode(parentTreeNode, obj)

        elif not hasattr(obj, '__dict__'):
            parentTreeNode.setValue(str(obj))

        elif isinstance(obj, object):
            #a __class__
            moduleName = obj.__class__.__module__
            className = obj.__class__.__name__

            attributes = []
            for a in obj.__dict__.keys():
                if a.startswith('__'):
                    continue
                if moduleName.startswith('hubflow') or not a.startswith('_'):
                    attributes.append(a)

            for t in inspect.getmembers(obj, lambda o: isinstance(o, np.ndarray)):
                if t[0] not in attributes:
                    attributes.append(t[0])

            for name in sorted(attributes):
                node = TreeNode(parentTreeNode, name)
                fetch(getattr(obj, name, None), parentTreeNode=node, fetchedObjectIds=fetchedObjectIds)
                s =""


        else:
            #show the object's 'natural' printout as node value
            parentTreeNode.setValue(str(obj))

        return parentTreeNode


    def __addInfo(self, obj):
        metaData = self.pfType.getMetadataDict()

        handled = list()
        if 'class lookup' in metaData.keys() and \
           'class names' in metaData.keys():

            colors = np.asarray(metaData['class lookup']).astype(int)
            colors = colors.reshape((-1,3))

            grp = TreeNode(self, 'Class Info')

            names = metaData['class names']
            for i, name in enumerate(names):
                pixmap = QPixmap(100, 100)
                color = list(colors[i,:])
                pixmap.fill(QColor(*color))
                icon = QIcon(pixmap)

                TreeNode(grp, '{}'.format(i), value='{}'.format(name), icon=icon)

            handled.extend(['class lookup', 'class names'])

        # show metaData in generic child-nodes
        for k,v in metaData.items():
            if k in handled:
                continue

            grpNode = TreeNode(self, str(k))
            if isinstance(v, list) or isinstance(v, np.ndarray):
                for v2 in v:
                    TreeNode(grpNode, str(v2))
            else:
                TreeNode(grpNode, str(v))

    def contextMenu(self):
        m = QMenu()
        return m


class DataSourceTreeView(TreeView):

    def __init__(self, *args, **kwds):
        super(DataSourceTreeView, self).__init__(*args, **kwds)
        self.setAcceptDrops(True)



class DataSourcePanelUI(PanelWidgetBase, loadUI('datasourcepanel.ui')):
    def __init__(self, parent=None):
        super(DataSourcePanelUI, self).__init__(parent)
        self.dataSourceManager = None
        assert isinstance(self.dataSourceTreeView, DataSourceTreeView)

        self.dataSourceTreeView.setDragDropMode(QAbstractItemView.DragDrop)

        #init actions


        self.actionAddDataSource.triggered.connect(lambda : self.dataSourceManager.addDataSourceByDialog())
        self.actionRemoveDataSource.triggered.connect(lambda: self.dataSourceManager.removeSources(self.selectedDataSources()))
        self.actionRemoveDataSource.setEnabled(False) #will be enabled with selection of node
        def onSync():
            self.dataSourceManager.importSourcesFromQGISRegistry()
            self.dataSourceManager.exportSourcesToQGISRegistry(showLayers=True)
        self.actionSyncWithQGIS.triggered.connect(onSync)

        hasQGIS = qgisAppQgisInterface() is not None
        self.actionSyncWithQGIS.setEnabled(hasQGIS)


        self.btnAddSource.setDefaultAction(self.actionAddDataSource)
        self.btnSync.setDefaultAction(self.actionSyncWithQGIS)
        self.btnRemoveSource.setDefaultAction(self.actionRemoveDataSource)
        self.btnCollapse.clicked.connect(lambda :self.expandSelectedNodes(self.dataSourceTreeView, False))
        self.btnExpand.clicked.connect(lambda :self.expandSelectedNodes(self.dataSourceTreeView, True))
        #self.onSelectionChanged(None, None)

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

    def connectDataSourceManager(self, dataSourceManager):
        assert isinstance(dataSourceManager, DataSourceManager)
        self.dataSourceManager = dataSourceManager
        self.model = DataSourceManagerTreeModel(self, self.dataSourceManager)
        self.dataSourceTreeView.setModel(self.model)
        self.dataSourceTreeView.setMenuProvider(DataSourceManagerTreeModelMenuProvider(self.dataSourceTreeView))
        self.dataSourceTreeView.setDragEnabled(True)
        self.dataSourceTreeView.setAcceptDrops(True)

        self.dataSourceTreeView.selectionModel().selectionChanged.connect(self.onSelectionChanged)

    def onSelectionChanged(self, selected, deselected):

        s = self.selectedDataSources()
        self.actionRemoveDataSource.setEnabled(len(s) > 0)


    def selectedDataSources(self)->list:
        """
        :return: [list-of-selected-DataSources]
        """
        sources = []
        for n in self.dataSourceTreeView.selectedNodes():
            if isinstance(n, DataSourceTreeNode):
                sources.append(n.dataSource)
        return sources

LUT_DATASOURCTYPES = collections.OrderedDict()
LUT_DATASOURCTYPES[DataSourceRaster] = ('Raster Data', QIcon(':/enmapbox/icons/mIconRasterLayer.svg'))
LUT_DATASOURCTYPES[DataSourceVector] = ('Vector Data', QIcon(':/enmapbox/icons/mIconLineLayer.svg'))
LUT_DATASOURCTYPES[HubFlowDataSource] = ('Models', QIcon(':/enmapbox/icons/alg.svg'))
LUT_DATASOURCTYPES[DataSourceSpectralLibrary] = ('Spectral Libraries',QIcon(':/enmapbox/icons/speclib.svg'))
LUT_DATASOURCTYPES[DataSourceFile] = ('Other Files',QIcon(':/trolltech/styles/commonstyle/images/file-128.png'))
LUT_DATASOURCTYPES[DataSource] = ('Other sources',QIcon(':/trolltech/styles/commonstyle/images/standardbutton-open-32.png'))


class DataSourceManagerTreeModel(TreeModel):

    def __init__(self, parent, dataSourceManager:DataSourceManager):

        super(DataSourceManagerTreeModel, self).__init__(parent)
        assert isinstance(dataSourceManager, DataSourceManager)

        if True:
            self.setFlag(QgsLayerTreeModel.ShowLegend, True) #no effect
            #self.setFlag(QgsLayerTreeModel.ShowSymbology, True) #no effect
            # self.setFlag(QgsLayerTreeModel.ShowRasterPreviewIcon, True)
            self.setFlag(QgsLayerTreeModel.ShowLegendAsTree, True)
            self.setFlag(QgsLayerTreeModel.AllowNodeReorder, True)
            self.setFlag(QgsLayerTreeModel.AllowNodeRename, True)
            self.setFlag(QgsLayerTreeModel.AllowNodeChangeVisibility, True)
            self.setFlag(QgsLayerTreeModel.AllowLegendChangeState, True)

        self.dataSourceManager = dataSourceManager
        self.dataSourceManager.sigDataSourceAdded.connect(self.addDataSource)
        self.dataSourceManager.sigDataSourceRemoved.connect(self.removeDataSource)

        for ds in self.dataSourceManager.mSources:
            self.addDataSource(ds)
        s = ""

    def columnCount(self, index):
        return 2



    def mimeTypes(self):
        # specifies the mime types handled by this model
        types = []

        types.append(MDF_DATASOURCETREEMODELDATA)
        types.append(MDF_LAYERTREEMODELDATA)
        types.append(MDF_URILIST)
        return types

    def dropMimeData(self, data, action, row, column, parent):
        parentNode = self.index2node(parent)
        assert isinstance(data, QMimeData)

        result = False
        if action in [Qt.MoveAction, Qt.CopyAction]:
            # collect nodes
            nodes = []

            if data.hasFormat("application/enmapbox.datasourcetreemodeldata"):
                return False  # do not allow moving within DataSourceTree

            # add new data from external sources
            elif data.hasFormat('text/uri-list'):
                for url in data.urls():
                    self.dataSourceManager.addSource(url)

            # add data dragged from QGIS
            elif data.hasFormat("application/qgis.layertreemodeldata"):

                doc = QDomDocument()
                doc.setContent(data.data('application/qgis.layertreemodeldata'))
                rootElem = doc.documentElement()
                elem = rootElem.firstChildElement()
                added = []
                while not elem.isNull():
                    node = QgsLayerTreeNode.readXml(elem)
                    #QGIS3:  node = QgsLayerTreeNode.readXml(elem, QgsProject.instance())
                    added.extend(self.dataSourceManager.addSource(node))
                    elem = elem.nextSiblingElement()
                #print('Added ds'.format(added))
                return any([isinstance(ds, DataSource) for ds in added])

                #result = QgsLayerTreeModel.dropMimeData(self, data, action, row, column, parent)

        return result

    def mimeData(self, indexes:list)->QMimeData:
        indexes = sorted(indexes)
        if len(indexes) == 0:
            return None

        nodesFinal = self.indexes2nodes(indexes, True)
        mimeData = QMimeData()
        # define application/enmapbox.datasourcetreemodeldata
        exportedNodes = []

        #collect nodes to be exported as mimeData
        for node in nodesFinal:
            #avoid doubling
            if node in exportedNodes:
                continue
            if isinstance(node, DataSourceTreeNode):
                exportedNodes.append(node)

            elif isinstance(node, DataSourceGroupTreeNode):
                for n in node.children():
                    exportedNodes.append(n)

        uriList = list()
        uuidList =list()
        dataSourceRefs = []
        speclib = list()

        for node in exportedNodes:
            dataSource = node.dataSource
            assert isinstance(dataSource, DataSource)
            uriList.append(dataSource.uri())
            uuidList.append(dataSource.uuid())

            if isinstance(dataSource, DataSourceSpectralLibrary):
                mimeDataSpeclib = dataSource.spectralLibrary().mimeData()
                for f in mimeDataSpeclib.formats():
                    if f not in mimeData.formats():
                        mimeData.setData(f, mimeDataSpeclib.data(f))

        mimeData.setData(MDF_DATASOURCETREEMODELDATA, pickle.dumps(uuidList))

        mimeData.setUrls([QUrl.fromLocalFile(uri) if os.path.isfile(uri) else QUrl(uri) for uri in uriList])
        return mimeData


    def getSourceGroup(self, dataSource):
        """Returns the source group relate to a data source"""
        assert isinstance(dataSource, DataSource)


        for groupDataType, t in LUT_DATASOURCTYPES.items():
            if isinstance(dataSource, groupDataType):
                groupName, groupIcon = t
                break
        if groupName is None:
            groupName, groupIcon = LUT_DATASOURCTYPES[DataSource]
            groupDataType = DataSource
        srcGrp = [c for c in self.rootNode.children() if c.name() == groupName]
        if len(srcGrp) == 0:
                # group node does not exist.
                # create new group node and add it to the model
                srcGrp = DataSourceGroupTreeNode(self.rootNode, groupName, groupDataType)
                srcGrp.setIcon(groupIcon)
                srcGrp.setExpanded(True)

        elif len(srcGrp) == 1:
            srcGrp = srcGrp[0]
        return srcGrp



    def addDataSource(self, dataSource:DataSource):
        """
        Adds a DataSource and creates an TreeNode for
        :param dataSource: DataSource
        """
        assert isinstance(dataSource, DataSource)
        dataSourceNode = CreateNodeFromDataSource(dataSource, None)
        sourceGroup = self.getSourceGroup(dataSource)
        sourceGroup.addChildNode(dataSourceNode)
        dataSourceNode.setExpanded(False)
        s = ""

    def removeDataSource(self, dataSource):
        assert isinstance(dataSource, DataSource)
        sourceGroup = self.getSourceGroup(dataSource)
        to_remove = []

        for node in sourceGroup.children():
            if node.dataSource == dataSource:
                to_remove.append(node)

        for node in to_remove:
            sourceGroup.removeChildNode(node)

    def supportedDragActions(self):
        return Qt.CopyAction

    def supportedDropActions(self):
        return Qt.CopyAction

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsDropEnabled

        # specify TreeNode specific actions
        node = self.index2node(index)
        column = index.column()
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDropEnabled

        if isinstance(node, DataSourceTreeNode):
            flags |= Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled

        elif type(node) in [QgsLayerTreeLayer, QgsLayerTreeGroup]:
            flags |= Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled

        if isinstance(node, CheckableTreeNode):
            flags |= Qt.ItemIsUserCheckable

        return flags

    def contextMenu(self, node):
        menu = QMenu()
        if isinstance(node, DataSourceGroupTreeNode):
            a = menu.addAction('Clear')
            a.triggered.connect(lambda : self.dataSourceManager.removeSources(node.dataSources()))

        if isinstance(node, DataSourceTreeNode):
            a = menu.addAction('Remove')
            a.triggered.connect(lambda: self.dataSourceManager.removeSource(node.dataSource))

        if isinstance(node, HubFlowObjectTreeNode):
            a = menu.addAction('Show report')
            a.triggered.connect(lambda : self.onShowModelReport(node.dataSource))

        #append node-defined context menu
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

    def onShowModelReport(self, model):
        assert isinstance(model, HubFlowDataSource)
        pfType = model.pfType

        #this step should be done without writing anything on hard disk
        pathHTML = pfType.report().saveHTML().filename
        from enmapbox.gui.enmapboxgui import EnMAPBox
        EnMAPBox.instance().dockManager.createDock('WEBVIEW', url=pathHTML)


class DataSourceManagerTreeModelMenuProvider(TreeViewMenuProvider):
    """
    This class defines which context menues will be shown for for which TreeNodes
    """

    def __init__(self, treeView):
        super(DataSourceManagerTreeModelMenuProvider, self).__init__(treeView)
        assert isinstance(self.treeView.model(), DataSourceManagerTreeModel)

    def createContextMenu(self):
        col = self.currentIndex().column()
        node = self.currentNode()
        model = self.treeView.model()
        assert isinstance(model, DataSourceManagerTreeModel)

        selectionModel = self.treeView.selectionModel()
        assert isinstance(selectionModel, QItemSelectionModel)

        selectedNodes = [self.model.index2node(i) for i in selectionModel.selectedIndexes()]
        dataSources = list(set([n.dataSource for n in selectedNodes if isinstance(n, DataSourceTreeNode)]))
        srcURIs = list(set([s.uri() for s in dataSources]))
        m = QMenu()

        if isinstance(node, DataSourceGroupTreeNode):
            a = m.addAction('Clear')
            assert isinstance(a, QAction)
            a.setToolTip('Removes all datasources from this node')
            a.triggered.connect(lambda: model.dataSourceManager.removeSources(node.dataSources()))

        if isinstance(node, DataSourceTreeNode):
            src = node.dataSource

            if isinstance(src, DataSource):
                a = m.addAction('Remove')
                a.triggered.connect(lambda : model.dataSourceManager.removeSources(dataSources))
                a = m.addAction('Copy URI / path')
                a.triggered.connect(lambda: QApplication.clipboard().setText('\n'.join(srcURIs)))
                #a = m.addAction('Rename')
                #a.setEnabled(False)
                #todo: implement rename function
                #a.triggered.connect(node.dataSource.rename)

            if isinstance(src, DataSourceSpatial):
                a = m.addAction('Save as..')

            if isinstance(src, DataSourceRaster):
                a = m.addAction('Raster statistics')
                sub = m.addMenu('Open in new map...')
                a = sub.addAction('Default Colors')
                a.triggered.connect(lambda: self.onOpenInNewMap(src, rgb='DEFAULT'))
                a = sub.addAction('True Color')
                a.setToolTip('Red-Green-Blue true colors')
                a.triggered.connect(lambda: self.onOpenInNewMap(src, rgb='R,G,B'))

                a = sub.addAction('CIR')
                a.setToolTip('nIR Red Green')
                a.triggered.connect(lambda: self.onOpenInNewMap(src, rgb='NIR,R,G'))

                a = sub.addAction('SWIR')
                a.setToolTip('nIR swIR Red')
                a.triggered.connect(lambda: self.onOpenInNewMap(src, rgb='NIR,SWIR,R'))

            if isinstance(src, DataSourceVector):
                a = m.addAction('Open in new map')
                a.triggered.connect(lambda: self.onOpenInNewMap(src))

            if isinstance(src, DataSourceSpectralLibrary):
                a = m.addAction('Save as...')
                a.setEnabled(False)

                a = m.addAction('Open')
                a.setEnabled(False)

        if isinstance(node, RasterBandTreeNode):
            a = m.addAction('Band statistics')
            a.setEnabled(False)

            a = m.addAction('Open in new map')
            a.triggered.connect(lambda : self.onOpenInNewMap(node.mDataSource, rgb=[node.mBandIndex]))


        if col == 1 and node.value() != None:
            a = m.addAction('Copy')
            a.triggered.connect(lambda : QApplication.clipboard().setText(str(node.value())))


        if isinstance(node, TreeNode):
            m2 = node.contextMenu()
            for a in m2.actions():
                a.setParent(None)
                m.addAction(a)
                a.setParent(m)
        return m

    def onOpenInNewMap(self, dataSource, rgb=None):
        from enmapbox.gui.enmapboxgui import EnMAPBox
        emb = EnMAPBox.instance()

        if not isinstance(emb, EnMAPBox):
            return None

        if isinstance(dataSource, DataSourceSpatial):
            lyr = dataSource.createUnregisteredMapLayer()
            dock = emb.createDock('MAP')
            assert isinstance(dock, MapDock)
            from enmapbox.gui.utils import bandClosestToWavelength, defaultBands
            if isinstance(lyr, QgsRasterLayer):
                r = lyr.renderer()
                if isinstance(r, QgsRasterRenderer):
                    ds = gdal.Open(lyr.source())
                    if isinstance(rgb, str):
                        if re.search('DEFAULT', rgb):
                            rgb = defaultBands(ds)
                        else:
                            rgb = [bandClosestToWavelength(ds,s) for s in rgb.split(',')]
                            s = ""
                    assert isinstance(rgb, list)

                    stats = [ds.GetRasterBand(b+1).ComputeRasterMinMax() for b in rgb]

                    def setCE_MinMax(ce, st):
                        assert isinstance(ce, QgsContrastEnhancement)
                        ce.setContrastEnhancementAlgorithm(QgsContrastEnhancement.StretchToMinimumMaximum)
                        ce.setMinimumValue(st[0])
                        ce.setMaximumValue(st[1])

                    if len(rgb) == 3:
                        if isinstance(r, QgsMultiBandColorRenderer):
                            r.setRedBand(rgb[0]+1)
                            r.setGreenBand(rgb[1]+1)
                            r.setBlueBand(rgb[2]+1)
                            setCE_MinMax(r.redContrastEnhancement(), stats[0])
                            setCE_MinMax(r.greenContrastEnhancement(), stats[1])
                            setCE_MinMax(r.blueContrastEnhancement(), stats[2])

                        if isinstance(r, QgsSingleBandGrayRenderer):
                            r.setGrayBand(rgb[0])
                            setCE_MinMax(r.contrastEnhancement(), stats[0])

                    elif len(rgb) == 1:

                        if isinstance(r, QgsMultiBandColorRenderer):
                            r.setRedBand(rgb[0]+1)
                            r.setGreenBand(rgb[0]+1)
                            r.setBlueBand(rgb[0]+1)
                            setCE_MinMax(r.redContrastEnhancement(), stats[0])
                            setCE_MinMax(r.greenContrastEnhancement(), stats[0])
                            setCE_MinMax(r.blueContrastEnhancement(), stats[0])

                        if isinstance(r, QgsSingleBandGrayRenderer):
                            r.setGrayBand(rgb[0]+1)
                            setCE_MinMax(r.contrastEnhancement(), stats[0])
                            s = ""

                    #get
                    s = ""

            elif isinstance(lyr, QgsVectorLayer):

                pass

            dock.setLayers([lyr])


    def onSaveAs(self, dataSource):

        pass


def CreateNodeFromDataSource(dataSource:DataSource, parent=None)->DataSourceTreeNode:
    """
    Generates a DataSourceTreeNode
    :param dataSource:
    :param parent:
    :return:
    """
    if not isinstance(dataSource, DataSource):
        return None

    #hint: take care of class inheritance order
    if isinstance(dataSource, HubFlowDataSource):
        node = HubFlowObjectTreeNode(parent, dataSource)
    elif isinstance(dataSource, DataSourceRaster):
        node = RasterDataSourceTreeNode(parent, dataSource)
    elif isinstance(dataSource, DataSourceVector):
        node = VectorDataSourceTreeNode(parent, dataSource)
    elif isinstance(dataSource, DataSourceSpectralLibrary):
        node = SpeclibDataSourceTreeNode(parent, dataSource)
    elif isinstance(dataSource, DataSourceFile):
        node = FileDataSourceTreeNode(parent, dataSource)
    else:
        node = DataSourceTreeNode(parent, dataSource)

    return node
