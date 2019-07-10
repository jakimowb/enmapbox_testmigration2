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

import inspect, pickle, json

from enmapbox import DIR_TESTDATA, messageLog
from enmapbox.gui import ClassificationScheme, TreeNode, TreeView
from enmapbox.gui.utils import *
from enmapbox.gui.mimedata import *
from enmapbox.gui.mapcanvas import MapDock
from enmapbox.gui.datasources import *
HUBFLOW = True
HUBFLOW_MAX_VALUES = 1024
SOURCE_TYPES = ['ALL', 'ANY', 'RASTER', 'VECTOR', 'SPATIAL', 'MODEL', 'SPECLIB']

HIDDEN_DATASOURCE = '__HIDDEN__DATASOURCE'
try:
    import hubflow.core
    s = ""

except Exception as ex:
    messageLog('Unable to import hubflow API. Error "{}"'.format(ex), level=Qgis.Warning)
    HUBFLOW = False


def reprNL(obj, replacement=' '):
    """
    Repturn repl withouth newline
    :param obj:
    :param replacement:
    :return:
    """
    return repr(obj).replace('\n',replacement)

class DataSourceManager(QObject):
    """
       Keeps control on different data sources handled by EnMAP-Box.
       Similar like QGIS data registry, but manages non-spatial data sources (text files, spectral libraries etc.) as well.
    """

    _testInstance = None

    @staticmethod
    def instance():
        from enmapbox.gui.enmapboxgui import EnMAPBox
        if isinstance(EnMAPBox.instance(), EnMAPBox):
            return EnMAPBox.instance().dataSourceManager
        else:
            return DataSourceManager._testInstance



    sigDataSourceAdded = pyqtSignal(DataSource)
    sigDataSourceRemoved = pyqtSignal(DataSource)



    def __init__(self):
        """
        Constructor
        """
        super(DataSourceManager, self).__init__()
        DataSourceManager._testInstance = self
        self.mSources = list()


        try:
            from hubflow import signals
            signals.sigFileCreated.connect(self.addSource)
        except Exception as ex:
            messageLog(ex)


    def registerQgsProject(self, qgsProject:QgsProject):
        """
        Registers a QgsProject instance and listens to changes of its QgsMapLayerStore
        :param qgsProject: QgsProject
        """
        assert isinstance(qgsProject, QgsProject)

        qgsProject.layersAdded.connect(self.addSources)

        # todo: what happens when layers are removed from the QgsProject?


    def __iter__(self):
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

    def sources(self, sourceTypes=None) -> list:
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
                    if sourceType == 'ALL':
                        return self.mSources[:]
                    elif sourceType == 'VECTOR':
                        filterTypes.add(DataSourceVector)
                        filterTypes.add(DataSourceSpectralLibrary)
                    elif sourceType == 'SPATIAL':
                        filterTypes.add(DataSourceVector)
                        filterTypes.add(DataSourceRaster)
                        filterTypes.add(DataSourceSpectralLibrary)
                    elif sourceType == 'RASTER':
                        filterTypes.add(DataSourceRaster)
                    elif sourceType == 'MODEL':
                        filterTypes.add(HubFlowDataSource)
                    elif sourceType == 'SPECLIB':
                        filterTypes.add(DataSourceSpectralLibrary)

            results = [r for r in self.mSources if type(r) in filterTypes]

        return results

    def classificationSchemata(self)->list:
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

    def updateFromQgsProject(self, mapLayers=None):
        """
        Add data sources registered in the QgsProject to the data source manager
        :return: List of added new DataSources
        """
        if mapLayers is None:
            mapLayers = QgsProject.instance().mapLayers().values()

        added = [self.addSource(lyr, name=lyr.name()) for lyr in mapLayers]
        return [a for a in added if isinstance(a, DataSource)]

    def uriList(self, sourceTypes='ALL') -> list:
        """
        Returns URIs of registered data sources
        :param sourcetype: uri filter as used in sources(sourceTypes=<types>).
        :return: uri as string (str), e.g. a file path
        """
        return [ds.uri() for ds in self.sources(sourceTypes=sourceTypes)]


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
        """
        Adds a list of new data sources
        :param sources: list of potential data sources, i.e. QgsDataSources
        :return: [list-of-added-DataSources]
        """
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
            sameSources = [d for d in self.mSources if dsNew.isSameSource(d)]
            if len(sameSources) == 0:
                toAdd.append(dsNew)
            else:
                #we have similar sources.
                older = []
                newer = []

                for d in sameSources:
                    if dsNew.isNewVersionOf(d):
                        older.append(d)
                    if d.isNewVersionOf(dsNew):
                        newer.append(d)

                sameOrNewer = [d for d in sameSources if d not in older]

                # remove older versions
                if len(older) > 0:
                    self.removeSources(older)

                if len(sameOrNewer) == 0:
                    toAdd.append(dsNew)


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

    def removeSource(self, dataSource:DataSource):
        """
        Removes the DataSource from the DataSourceManager
        :param dataSource: the DataSource or datataource uri (str) to be removed
        :return: the removed DataSource. None if dataSource was not in the DataSourceManager
        """
        if isinstance(dataSource, str):
            self.removeSources([ds for ds in self.mSources if ds.uri() == dataSource])
        else:
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

    def __init__(self, parentNode, groupName:str, classDef, icon=None):
        assert inspect.isclass(classDef)
        assert isinstance(groupName, str)
        if icon is None:
            icon = QApplication.style().standardIcon(QStyle.SP_DirOpenIcon)

        super(DataSourceGroupTreeNode, self).__init__(parentNode, name=groupName, icon=icon)
        self.mFlag1stSource = False
        self.mGroupName = groupName
        self.mChildClass = classDef
        self.sigAddedChildren.connect(self.onChildsChanged)
        self.sigRemovedChildren.connect(self.onChildsChanged)

    def groupName(self)->str:
        return self.mGroupName

    def onChildsChanged(self, *args):

        n = len(self.childNodes())
        name = '{} ({})'.format(self.mGroupName, n)
        self.setName(name)

        if n > 0 and self.mFlag1stSource == False:
            pass

    def dataSources(self)->list:
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
    def __init__(self, parent, dataSource):
        assert isinstance(dataSource, DataSourceFile)
        super(DataSourceSizesTreeNode, self).__init__(parent, 'Size')

        fileSize = os.path.getsize(dataSource.uri())
        fileSize = fileSizeString(fileSize)

        n = TreeNode(self, 'File', values=fileSize, icon=dataSource.icon())
        if isinstance(dataSource, DataSourceSpatial):
            ext = dataSource.mSpatialExtent
            mu = QgsUnitTypes.encodeUnit(ext.crs().mapUnits())

            n = TreeNode(self, 'Spatial Extent')
            TreeNode(n, 'Width', values='{} {}'.format(ext.width(), mu))
            TreeNode(n, 'Heigth', values='{} {}'.format(ext.height(), mu))

        if isinstance(dataSource, DataSourceRaster):
            n = TreeNode(self, 'Pixels')
            TreeNode(n, 'Samples (x)', values='{}'.format(dataSource.nSamples))
            TreeNode(n, 'Lines (y)', values='{}'.format(dataSource.nLines))
            TreeNode(n, 'Bands (z)', values='{}'.format(dataSource.nBands))



class DataSourceTreeNode(TreeNode, KeepRefs):

    def __init__(self, parent:TreeNode, dataSource:DataSource):

        self.mDataSource = None
        self.mNodeSize = None

        super(DataSourceTreeNode, self).__init__(parent, '<empty>')
        KeepRefs.__init__(self)

        self.disconnectDataSource()
        if dataSource:
            self.connectDataSource(dataSource)

    def connectDataSource(self, dataSource:DataSource):
        """
        Connects a DataSource with this DataSourceTreeNode
        :param dataSource: DataSource
        """
        assert isinstance(dataSource, DataSource)
        self.mDataSource = dataSource
        self.setName(dataSource.name())

        self.setToolTip(dataSource.uri())
        self.setIcon(dataSource.icon())

        uri = self.mDataSource.uri()
        if os.path.isfile(uri):
            self.mSrcSize = os.path.getsize(self.mDataSource.uri())
            self.mNodeSize = TreeNode(self, 'File size', values=fileSizeString(self.mSrcSize))
        else:
            self.mNodeSize = TreeNode(self, 'Size', values='unknown')
            self.mSrcSize = -1

    def dataSource(self)->DataSource:
        """
        Returns the DataSource this DataSourceTreeNode represents.
        :return: DataSource
        """
        return self.mDataSource

    def disconnectDataSource(self):
        self.mDataSource = None
        if self.mNodeSize:
            self.removeChildNode(self.mNodeSize)
            self.mNodeSize = None

        self.setName(None)
        self.setIcon(None)
        self.setToolTip(None)

    def writeXML(self, parentElement):
        super(DataSourceTreeNode, self).writeXML(parentElement)
        elem = parentElement.lastChild().toElement()
        elem.setTagName('datasource-tree-node')
        elem.setAttribute('uuid', '{}'.format(self.mDataSource.uuid()))


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
        self.nodeCRS = CRSLayerTreeNode(self, ext.crs())
        self.nodeExtXmu = TreeNode(self.mNodeSize, 'Width', values='{} {}'.format(ext.width(), mu))
        self.nodeExtYmu = TreeNode(self.mNodeSize, 'Height', values='{} {}'.format(ext.height(), mu))

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

        lyr = self.mDataSource.createUnregisteredMapLayer()
        assert lyr.isValid()
        nFeat = lyr.featureCount()
        nFields = lyr.fields().count()

        geomType = ['Point','Line','Polygon','Unknown','Null'][lyr.geometryType()]
        wkbType = QgsWkbTypes.displayString(int(lyr.wkbType()))

        if re.search('polygon', wkbType, re.I):
            self.setIcon(QIcon(r':/images/themes/default/mIconPolygonLayer.svg'))
        elif re.search('line', wkbType, re.I):
            self.setIcon(QIcon(r':/images/themes/default/mIconLineLayer.svg'))
        elif re.search('point', wkbType, re.I):
            self.setIcon(QIcon(r':/images/themes/default/mIconPointLayer.svg'))

        #self.nodeSize.setValue('{} x {}'.format(nFeat, fileSizeString(self.mSrcSize)))
        self.nodeFeatures = TreeNode(self, 'Features',
                                          values='{}'.format(nFeat))
        TreeNode(self.nodeFeatures, 'Geometry Type', values=geomType)

        TreeNode(self.nodeFeatures, 'WKB Type', values=wkbType)

        self.nodeFields = TreeNode(self, 'Fields',
                                        toolTip='Attribute fields related to each feature',
                                        values='{}'.format(nFields))
        for i in range(nFields):
            field = lyr.fields().at(i)
            node = TreeNode(self.nodeFields, field.name(),
                                 values='{} {}'.format(field.typeName(), field.length()))

        s = ""


class ClassificationNodeLayer(TreeNode):

    def __init__(self, parent, classificationScheme, name='Classification Scheme'):
        super(ClassificationNodeLayer, self).__init__(parent, name)
        self.setName(name)
        for i, ci in enumerate(classificationScheme):
            TreeNode(parent, '{}'.format(i), values=ci.name(), icon=ci.icon())

class CRSLayerTreeNode(TreeNode):
    def __init__(self, parent, crs):
        assert isinstance(crs, QgsCoordinateReferenceSystem)
        super(CRSLayerTreeNode, self).__init__(parent, crs.description())
        self.setName('CRS')
        self.setIcon(QIcon(':/images/themes/default/propertyicons/CRS.svg'))
        self.setToolTip('Coordinate Reference System')
        self.mCrs = None
        self.nodeDescription = TreeNode(self, 'Name', toolTip='Description')
        self.nodeAuthID = TreeNode(self, 'AuthID', toolTip='Authority ID')
        self.nodeAcronym = TreeNode(self, 'Acronym', toolTip='Projection Acronym')
        self.nodeMapUnits = TreeNode(self, 'Map Units')
        self.setCrs(crs)


    def setCrs(self, crs):
        assert isinstance(crs, QgsCoordinateReferenceSystem)
        self.mCrs = crs
        if self.mCrs.isValid():
            self.setValues(crs.description())
            self.nodeDescription.setValues(crs.description())
            self.nodeAuthID.setValues(crs.authid())
            self.nodeAcronym.setValues(crs.projectionAcronym())
            #self.nodeDescription.setItemVisibilityChecked(Qt.Checked)
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

    def __init__(self, parentNode, color:QColor):
        assert isinstance(color, QColor)


        pm = QPixmap(QSize(20, 20))
        pm.fill(color)
        icon = QIcon(pm)
        name = color.name()
        value = color.getRgbF()
        super(ColorTreeNode, self).__init__(parentNode, name=name, value=value, icon=icon)


class RasterBandTreeNode(TreeNode):

    def __init__(self,  dataSource, bandIndex, *args, **kwds):
        super(RasterBandTreeNode, self).__init__( *args, **kwds)
        assert isinstance(dataSource, DataSourceRaster)
        assert bandIndex >= 0
        assert bandIndex < dataSource.nBands
        self.mDataSource = dataSource
        self.mBandIndex = bandIndex

        md = self.mDataSource.mBandMetadata[bandIndex]
        classScheme = md.get('__ClassificationScheme__')
        if isinstance(classScheme, ClassificationScheme):
            for ci in classScheme:
                assert isinstance(ci, ClassInfo)
                TreeNode(self, str(ci.label()), ci.name(), icon=ci.icon())




class RasterDataSourceTreeNode(SpatialDataSourceTreeNode):
    def __init__(self, *args, **kwds):
        #extents in pixel
        self.mNodeExtXpx = None
        self.mNodeExtYpx = None
        self.mNodeBands = None
        self.mNodePxSize = None
        super(RasterDataSourceTreeNode,self).__init__( *args, **kwds)

    def connectDataSource(self, dataSource):
        assert isinstance(dataSource, DataSourceRaster)
        super(RasterDataSourceTreeNode, self).connectDataSource(dataSource)

        self.setIcon(dataSource.icon())
        mu = QgsUnitTypes.toString(dataSource.spatialExtent().crs().mapUnits())


        self.mNodeExtXpx = TreeNode(self.mNodeSize, 'Samples',
                                    toolTip='Data Source Width in Pixel',
                                    values='{} px'.format(dataSource.nSamples))
        self.mNodeExtYpx = TreeNode(self.mNodeSize, 'Lines',
                                    toolTip='Data Source Height in Pixel',
                                    values='{} px'.format(dataSource.nLines))

        pxSize = dataSource.mPxSize
        self.mNodePxSize = TreeNode(self.mNodeSize, 'Pixel',
                                    toolTip='Spatial size of single pixel',
                                    values='{}x{}{}'.format(pxSize.width(), mu, pxSize.height()))

        self.mNodeSize.setValue('{}x{}x{}'.format(dataSource.nSamples,
                                                  dataSource.nLines,
                                                  dataSource.nBands))

        self.mNodeBands = TreeNode(self, 'Bands',
                                   toolTip='Number of Raster Bands',
                                   values='{}'.format(dataSource.nBands))


        for b, bandName in enumerate(dataSource.mBandNames):
            bandNode = RasterBandTreeNode(dataSource, b, self.mNodeBands, str(b+1), bandName)





    def disconnectDataSource(self):
        if self.mNodeExtXpx is not None:
            self.mNodeExtXpx = self._removeSubNode(self.mNodeExtXpx)
            self.mNodeExtYpx = self._removeSubNode(self.mNodeExtYpx)
            self.mNodeBands = self._removeSubNode(self.mNodeBands)
            self.mNodePxSize = self._removeSubNode(self.mNodePxSize)
        pass

class FileDataSourceTreeNode(DataSourceTreeNode):

    def __init__(self, *args, **kwds):
        super(FileDataSourceTreeNode,self).__init__( *args, **kwds)


class SpeclibProfilesTreeNode(TreeNode):

    def __init__(self, parent, speclib, **kwds):
        super(SpeclibProfilesTreeNode, self).__init__(parent, 'Profiles', **kwds)
        self.setIcon(QIcon(':/qps/ui/icons/profile.svg'))
        assert isinstance(speclib, SpectralLibrary)
        self.mSpeclib = speclib
        speclib.committedFeaturesAdded.connect(self.update)
        speclib.committedFeaturesRemoved.connect(self.update)
        self.update()
        assert isinstance(self.mSpeclib, SpectralLibrary)


    def update(self, *args):
        self.setValue(len(self.mSpeclib))

    def fetchCount(self):
        if isinstance(self.mSpeclib, SpectralLibrary):
            return len(self.mSpeclib)
        else:
            return 0

    def fetchNext(self):
        if isinstance(self.mSpeclib, SpectralLibrary):
            for p in self.mSpeclib:
                TreeNode(self, p.name())

class SpeclibDataSourceTreeNode(FileDataSourceTreeNode):
    def __init__(self, *args, **kwds):
        super(SpeclibDataSourceTreeNode, self).__init__(*args, **kwds)
        self.setIcon(QIcon(r':/qps/ui/icons/speclib.svg'))
        self.profileNode = None
        self.mSpeclib = None

    def speclib(self)->SpectralLibrary:
        """
        Returns the SpectralLibrary
        :return: SpectralLibrary
        """
        return self.mSpeclib

    def connectDataSource(self, dataSource):
        assert isinstance(dataSource, DataSourceSpectralLibrary)
        super(SpeclibDataSourceTreeNode, self).connectDataSource(dataSource)
        assert isinstance(self.mDataSource.mSpeclib, SpectralLibrary)

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
        assert isinstance(self.mDataSource, HubFlowDataSource)


        if isinstance(self.mDataSource.flowObject(), hubflow.core.FlowObject):

            moduleName = self.mDataSource.flowObject().__class__.__module__
            className = self.mDataSource.flowObject().__class__.__name__
            #self.setValue('{}.{}'.format(moduleName, className))
            self.setName(className)
            self.setToolTip('{}.{}'.format(moduleName, className))
            self.fetchInternals(self.mDataSource.flowObject(), parentTreeNode=self)

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

        import hubflow.core
        if isinstance(obj, hubflow.core.FlowObject):
            # for all FlowObjects
            moduleName = obj.__class__.__module__
            className = obj.__class__.__name__

            parentTreeNode.setValue('{}.{}'.format(moduleName, className))
            #ClassDefinitions
            if isinstance(obj, hubflow.core.ClassDefinition):
                csi = ClassificationScheme()
                classes = []
                classes.append(ClassInfo(name = obj.noDataName(), color=obj.noDataColor()._qColor))
                import hubflow.core
                for name, color in zip(obj.names(), obj.colors()):
                    classes.append(ClassInfo(name=name, color=color._qColor))
                csi.insertClasses(classes)
                ClassificationNodeLayer(parentTreeNode, csi, name='Classes')

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
                node = TreeNode(parentTreeNode, name, values=reprNL(value))
                fetch(value, parentTreeNode=node, fetchedObjectIds=fetchedObjectIds)

        elif isinstance(obj, np.ndarray):

            if obj.ndim == 1:
                fetch(list(obj), parentTreeNode=parentTreeNode, fetchedObjectIds=fetchedObjectIds)
            else:
                parentTreeNode.setValue(str(obj))


        elif isinstance(obj, (list, set, tuple)):
            """Show enumerations"""

            for i, item in enumerate(obj):
                node = TreeNode(parentTreeNode, str(i + 1), values=reprNL(item))
                fetch(item, parentTreeNode=node, fetchedObjectIds=fetchedObjectIds)
                if i > HUBFLOW_MAX_VALUES:
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
                attr = getattr(obj, name, None)
                if attr is None:
                    try:
                        attr = obj.__dict__[name]
                    except:
                        pass

                node = TreeNode(parentTreeNode, name, values=reprNL(attr))
                fetch(attr, parentTreeNode=node, fetchedObjectIds=fetchedObjectIds)
                s =""


        else:
            #show the object's 'natural' printout as node value
            parentTreeNode.setValue(reprNL(obj))

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

                TreeNode(grp, '{}'.format(i), values='{}'.format(name), icon=icon)

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
    """
    A TreeView to show EnMAP-Box Data Sources
    """

    def __init__(self, *args, **kwds):
        super(DataSourceTreeView, self).__init__(*args, **kwds)
        self.setAcceptDrops(True)


    def contextMenuEvent(self, event:QContextMenuEvent):
        """
        Creates and shows the context menu created on right-mouse-click.
        :param event: QContextMenuEvent
        """
        idx = self.currentIndex()
        assert isinstance(event, QContextMenuEvent)

        if not idx.isValid():
            return
        col = idx.column()
        model = self.model()
        assert isinstance(model, DataSourceManagerTreeModel)



        selectedNodes = self.selectedNodes()
        node = self.selectedNode()
        dataSources = list(set([n.mDataSource for n in selectedNodes if isinstance(n, DataSourceTreeNode)]))
        srcURIs = list(set([s.uri() for s in dataSources]))

        qgisIFACE = qgisAppQgisInterface()

        from enmapbox.gui.enmapboxgui import EnMAPBox
        enmapbox = EnMAPBox.instance()

        mapDocks = []
        if isinstance(enmapbox, EnMAPBox):
            mapDocks = enmapbox.dockManager.docks('MAP')

        m = QMenu()

        if isinstance(node, DataSourceGroupTreeNode):
            a = m.addAction('Clear')
            assert isinstance(a, QAction)
            a.setToolTip('Removes all datasources from this node')
            a.triggered.connect(lambda: model.dataSourceManager.removeSources(node.dataSources()))

        if isinstance(node, DataSourceTreeNode):
            src = node.mDataSource

            if isinstance(src, DataSource):
                a = m.addAction('Remove')
                a.triggered.connect(lambda: model.dataSourceManager.removeSources(dataSources))
                a = m.addAction('Copy URI / path')
                a.triggered.connect(lambda: QApplication.clipboard().setText('\n'.join(srcURIs)))
                # a = m.addAction('Rename')
                # a.setEnabled(False)
                # todo: implement rename function
                # a.triggered.connect(node.dataSource.rename)

            if isinstance(src, DataSourceSpatial):
                pass
                #a = m.addAction('Save as..')

            def appendRasterActions(sub: QMenu, src: DataSourceRaster, mapDock: MapDock):
                assert isinstance(src, DataSourceRaster)
                a = sub.addAction('Default Colors')
                a.triggered.connect(lambda: self.openInMap(src, mapCanvas=mapDock, rgb='DEFAULT'))

                b = src.mWaveLengthUnits is not None

                a = sub.addAction('True Color')
                a.setToolTip('Red-Green-Blue true colors')
                a.triggered.connect(lambda: self.openInMap(src, mapCanvas=mapDock, rgb='R,G,B'))
                a.setEnabled(b)

                a = sub.addAction('CIR')
                a.setToolTip('nIR Red Green')
                a.triggered.connect(lambda: self.openInMap(src, mapCanvas=mapDock, rgb='NIR,R,G'))
                a.setEnabled(b)

                a = sub.addAction('SWIR')
                a.setToolTip('nIR swIR Red')
                a.triggered.connect(lambda: self.openInMap(src, mapCanvas=mapDock, rgb='NIR,SWIR,R'))
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
                if isinstance(qgisIFACE, QgisInterface):
                    appendRasterActions(sub, src, qgisIFACE.mapCanvas())
                else:
                    sub.setEnabled(False)

            if isinstance(src, DataSourceVector):
                a = m.addAction('Open in new map')
                a.triggered.connect(lambda: self.openInMap(src, mapCanvas=None))

                sub = m.addMenu('Open in existing map...')
                if len(mapDocks) > 0:
                    for mapDock in mapDocks:
                        assert isinstance(mapDock, MapDock)
                        a = sub.addAction(mapDock.title())
                        a.triggered.connect(
                            lambda checked, src=src, mapDock=mapDock: self.openInMap(src, mapCanvas=mapDock))
                else:
                    sub.setEnabled(False)

                a = m.addAction('Open in QGIS')
                if isinstance(qgisIFACE, QgisInterface):
                    a.triggered.connect(lambda: self.openInMap(src, mapCanvas=qgisIFACE.mapCanvas()))
                else:
                    a.setEnabled(False)

            if isinstance(src, DataSourceSpectralLibrary):
                a = m.addAction('Open Editor')
                a.triggered.connect(lambda: self.onOpenSpeclib(src.speclib()))

        if isinstance(node, RasterBandTreeNode):
            a = m.addAction('Band statistics')
            a.setEnabled(False)

            a = m.addAction('Open in new map')
            a.triggered.connect(lambda: self.openInMap(node.mDataSource, rgb=[node.mBandIndex]))

        if col == 1 and node.value() != None:
            a = m.addAction('Copy')
            a.triggered.connect(lambda: QApplication.clipboard().setText(str(node.value())))

        if isinstance(node, TreeNode):
            m2 = node.contextMenu()
            if isinstance(m2, QMenu):
                for a in m2.actions():
                    a.setParent(None)
                    m.addAction(a)
                    a.setParent(m)
        m.exec_(self.viewport().mapToGlobal(event.pos()))

    def openInMap(self, dataSource: DataSourceSpatial, mapCanvas=None, rgb=None, sampleSize=256):
        """
        Add a DataSourceSpatial as QgsMapLayer to a mapCanvas.
        :param mapCanvas: QgsMapCanvas. Creates a new MapDock if set to none.
        :param dataSource: DataSourceSpatial
        :param rgb:
        """

        if not isinstance(dataSource, DataSourceSpatial):
            return

        if mapCanvas is None:
            from enmapbox.gui.enmapboxgui import EnMAPBox
            emb = EnMAPBox.instance()
            if not isinstance(emb, EnMAPBox):
                return None
            dock = emb.createDock('MAP')
            assert isinstance(dock, MapDock)
            mapCanvas = dock.mCanvas

        if isinstance(mapCanvas, MapDock):
            mapCanvas = mapCanvas.mapCanvas()

        assert isinstance(mapCanvas, QgsMapCanvas)

        lyr = dataSource.createUnregisteredMapLayer()

        from enmapbox.gui.utils import bandClosestToWavelength, defaultBands
        if isinstance(lyr, QgsRasterLayer):
            r = lyr.renderer()
            if isinstance(r, QgsRasterRenderer):
                ds = gdal.Open(lyr.source())
                if isinstance(rgb, str):
                    if re.search('DEFAULT', rgb):
                        rgb = defaultBands(ds)
                    else:
                        rgb = [bandClosestToWavelength(ds, s) for s in rgb.split(',')]

                assert isinstance(rgb, list)
                r = defaultRasterRenderer(lyr, bandIndices=rgb, sampleSize=sampleSize)
                lyr.setRenderer(r)


        elif isinstance(lyr, QgsVectorLayer):

            pass

        qgisIFACE = qgisAppQgisInterface()
        if isinstance(qgisIFACE, QgisInterface) and mapCanvas in qgisIFACE.mapCanvases():
            QgsProject.instance().addMapLayer(lyr)

        allLayers = mapCanvas.layers()
        allLayers.append(lyr)

        mapCanvas.setLayers(allLayers)

    def onSaveAs(self, dataSource):

        pass

    def onOpenSpeclib(self, speclib: SpectralLibrary):
        """
        Opens a SpectralLibrary in a new SpectralLibraryDock
        :param speclib: SpectralLibrary

        """
        from enmapbox.gui.enmapboxgui import EnMAPBox
        EnMAPBox.instance().dockManager.createDock('SPECLIB', speclib=speclib)


class DataSourcePanelUI(QgsDockWidget, loadUI('datasourcepanel.ui')):
    def __init__(self, parent=None):
        super(DataSourcePanelUI, self).__init__(parent)
        self.setupUi(self)
        self.mDataSourceManager = None
        assert isinstance(self.dataSourceTreeView, DataSourceTreeView)

        self.dataSourceTreeView.setDragDropMode(QAbstractItemView.DragDrop)

        #init actions


        self.actionAddDataSource.triggered.connect(lambda : self.mDataSourceManager.addDataSourceByDialog())
        self.actionRemoveDataSource.triggered.connect(lambda: self.mDataSourceManager.removeSources(self.selectedDataSources()))
        self.actionRemoveDataSource.setEnabled(False) #will be enabled with selection of node
        def onSync():
            self.mDataSourceManager.importSourcesFromQGISRegistry()
            self.mDataSourceManager.exportSourcesToQGISRegistry(showLayers=True)
        self.actionSyncWithQGIS.triggered.connect(onSync)

        hasQGIS = qgisAppQgisInterface() is not None
        self.actionSyncWithQGIS.setEnabled(hasQGIS)

        self.initActions()

    def initActions(self):

        self.btnAddSource.setDefaultAction(self.actionAddDataSource)
        self.btnSync.setDefaultAction(self.actionSyncWithQGIS)
        self.btnRemoveSource.setDefaultAction(self.actionRemoveDataSource)
        self.btnCollapse.clicked.connect(lambda :self.expandSelectedNodes(self.dataSourceTreeView, False))
        self.btnExpand.clicked.connect(lambda :self.expandSelectedNodes(self.dataSourceTreeView, True))


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

    def connectDataSourceManager(self, dataSourceManager:DataSourceManager):
        """
        Initializes the panel with a DataSourceManager
        :param dataSourceManager: DataSourceManager
        """
        assert isinstance(dataSourceManager, DataSourceManager)
        self.mDataSourceManager = dataSourceManager
        self.mDataSourceTreeModel = DataSourceManagerTreeModel(self, self.mDataSourceManager)
        self.dataSourceTreeView.setModel(self.mDataSourceTreeModel)
        self.dataSourceTreeView.selectionModel().selectionChanged.connect(self.onSelectionChanged)

    def onSelectionChanged(self, selected, deselected):

        s = self.selectedDataSources()
        self.actionRemoveDataSource.setEnabled(len(s) > 0)




    def selectedDataSources(self)->list:
        """
        :return: [list-of-selected-DataSources]
        """
        sources = []
        model = self.mDataSourceTreeModel
        assert isinstance(model, DataSourceManagerTreeModel)
        for idx in self.dataSourceTreeView.selectionModel().selectedIndexes():
            assert isinstance(idx, QModelIndex)
            n = model.idx2node(idx)
            if isinstance(n, DataSourceTreeNode):
                if n.dataSource() not in sources:
                    sources.append(n.dataSource())
            elif isinstance(n, DataSourceGroupTreeNode):
                for s in n.dataSources():
                    if s not in sources:
                        sources.append(s)
        return sources

LUT_DATASOURCTYPES = collections.OrderedDict()
LUT_DATASOURCTYPES[DataSourceRaster] = ('Raster Data', QIcon(':/enmapbox/gui/ui/icons/mIconRasterLayer.svg'))
LUT_DATASOURCTYPES[DataSourceVector] = ('Vector Data', QIcon(':/images/themes/default/mIconVector.svg'))
LUT_DATASOURCTYPES[HubFlowDataSource] = ('Models', QIcon(':/images/themes/default/processingAlgorithm.svg'))
LUT_DATASOURCTYPES[DataSourceSpectralLibrary] = ('Spectral Libraries', QIcon(':/qps/ui/icons/speclib.svg'))
LUT_DATASOURCTYPES[DataSourceFile] = ('Other Files', QIcon(':/trolltech/styles/commonstyle/images/file-128.png'))
LUT_DATASOURCTYPES[DataSource] = ('Other sources', QIcon(':/trolltech/styles/commonstyle/images/standardbutton-open-32.png'))


class DataSourceManagerTreeModel(TreeModel):

    def __init__(self, parent, dataSourceManager:DataSourceManager):

        super(DataSourceManagerTreeModel, self).__init__(parent)
        assert isinstance(dataSourceManager, DataSourceManager)
        self.mColumnNames[0] = 'Source'
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
        types.append(MDF_LAYERTREEMODELDATA)
        types.append(MDF_URILIST)
        return types

    def dropMimeData(self, data, action, row, column, parent):
        parentNode = self.idx2node(parent)
        assert isinstance(data, QMimeData)

        result = False

        if action in [Qt.MoveAction, Qt.CopyAction]:
            # collect nodes
            nodes = []

            if data.hasFormat(MDF_DATASOURCETREEMODELDATA):
                return False  # do not allow moving within DataSourceTree

            # add new data from external sources
            elif data.hasFormat(MDF_URILIST):
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
                    node = QgsLayerTreeNode.readXml(elem, QgsProject.instance())
                    added.extend(self.dataSourceManager.addSource(node))
                    elem = elem.nextSiblingElement()
                return any([isinstance(ds, DataSource) for ds in added])

                #result = QgsLayerTreeModel.dropMimeData(self, data, action, row, column, parent)

        return result

    def mimeData(self, indexes:list)->QMimeData:
        indexes = sorted(indexes)
        if len(indexes) == 0:
            return None

        nodesFinal = self.indexes2nodes(indexes)
        mimeData = QMimeData()
        # define application/enmapbox.datasourcetreemodeldata
        exportedNodes = []

        # collect nodes to be exported as mimeData
        for node in nodesFinal:
            #avoid doubling
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
        uuidList =list()

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

                if isinstance(dataSource, DataSourceSpectralLibrary):
                    from ..externals.qps.speclib.spectrallibraries import MIMEDATA_TEXT, MIMEDATA_SPECLIB, MIMEDATA_URL, MIMEDATA_SPECLIB_LINK
                    mimeDataSpeclib = dataSource.speclib().mimeData(formats=[MIMEDATA_SPECLIB_LINK])
                    for f in mimeDataSpeclib.formats():
                        if f not in mimeData.formats():
                            mimeData.setData(f, mimeDataSpeclib.data(f))

        if len(uuidList) > 0:
            mimeData.setData(MDF_DATASOURCETREEMODELDATA, pickle.dumps(uuidList))

        if len(bandInfo) > 0:
            mimeData.setData(MDF_RASTERBANDS, pickle.dumps(bandInfo))

        mimeData.setUrls([QUrl.fromLocalFile(uri) if os.path.isfile(uri) else QUrl(uri) for uri in uriList])
        return mimeData

    def sourceGroups(self)->list:
        return [n for n in self.rootNode().childNodes() if isinstance(n, DataSourceGroupTreeNode)]

    def sourceGroup(self, dataSource:DataSource)->DataSourceGroupTreeNode:
        """
        Returns the DataSourceGroupTreeNode related to a given data source.
        :param dataSource: DataSource
        :return: DataSourceGroupTreeNode
        """
        """"""
        assert isinstance(dataSource, DataSource)


        for groupDataType, t in LUT_DATASOURCTYPES.items():
            if isinstance(dataSource, groupDataType):
                groupName, groupIcon = t
                break
        if groupName is None:
            groupName, groupIcon = LUT_DATASOURCTYPES[DataSource]
            groupDataType = DataSource

        srcGroups = self.sourceGroups()
        srcGrp = [c for c in srcGroups if c.groupName() == groupName]
        if len(srcGrp) == 0:
                # group node does not exist.
                # create new group node and add it to the model
                srcGrp = DataSourceGroupTreeNode(self.rootNode(), groupName, groupDataType)
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
        sourceGroupNode = self.sourceGroup(dataSource)
        assert isinstance(sourceGroupNode, DataSourceGroupTreeNode)
        assert sourceGroupNode.parentNode() == self.rootNode()

        dataSourceNode = CreateNodeFromDataSource(dataSource, sourceGroupNode)


        #sourceGroupNode.appendChildNodes([sourceGroupNode])
        dataSourceNode.setExpanded(False)
        s = ""

    def removeDataSource(self, dataSource):
        assert isinstance(dataSource, DataSource)
        sourceGroup = self.sourceGroup(dataSource)
        to_remove = []

        for node in sourceGroup.childNodes():
            assert isinstance(node, DataSourceTreeNode)

            if node.dataSource() == dataSource:
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
        node = self.idx2node(index)

        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDropEnabled

        if isinstance(node, (DataSourceTreeNode, RasterBandTreeNode, DataSourceGroupTreeNode)):
            flags |= Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled

        elif type(node) in [QgsLayerTreeLayer, QgsLayerTreeGroup]:
            flags |= Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled

        if isinstance(node, TreeNode) and node.isCheckable():
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

        if isinstance(node, SpeclibDataSourceTreeNode):
            a = menu.addAction('Open')
            a.triggered.connect(lambda : self.onOpenSpeclib(node.speclib()))
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

    def onOpenSpeclib(self, speclib:SpectralLibrary):
        from enmapbox.gui.enmapboxgui import EnMAPBox
        EnMAPBox.instance().dockManager.createDock('SPECLIB', speclib=speclib)

    def onShowModelReport(self, model):
        assert isinstance(model, HubFlowDataSource)
        pfType = model.pfType

        #this step should be done without writing anything on hard disk
        pathHTML = pfType.report().saveHTML().filename
        from enmapbox.gui.enmapboxgui import EnMAPBox
        EnMAPBox.instance().dockManager.createDock('WEBVIEW', url=pathHTML)


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
