import json
import os
import pathlib
import pickle
import re
import typing
from os.path import splitext

from PyQt5.QtCore import QUrl, QSortFilterProxyModel, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QContextMenuEvent, QColor, QPixmap
from PyQt5.QtWidgets import QMenu, QAction, QApplication
from PyQt5.QtXml import QDomElement
from osgeo import gdal, ogr
from qgis._core import QgsMimeDataUtils, QgsVectorLayer, QgsRasterDataProvider, QgsLayerTreeLayer, \
    QgsVectorDataProvider, QgsMapLayerType, QgsLayerTreeGroup, QgsProject, QgsRasterRenderer, QgsWkbTypes, QgsUnitTypes, \
    QgsCoordinateReferenceSystem
from qgis._gui import QgsGui, QgsDataItemGuiProviderRegistry, QgsDataItemGuiContext, QgsMessageBar, QgsSublayersDialog, \
    QgisInterface, QgsMapCanvas

import qgis
from enmapbox import messageLog, debugLog
from enmapbox.externals.qps.layerproperties import subLayerDefinitions, defaultRasterRenderer
from enmapbox.externals.qps.speclib.core import is_spectral_library
from enmapbox.externals.qps.utils import bandClosestToWavelength, defaultBands, fileSizeString, SpatialExtent, \
    QGIS_DATATYPE_NAMES
from enmapbox.gui.datasources import rasterProvider, vectorProvider
from enmapbox.gui.mapcanvas import MapDock
from enmapbox.gui.utils import dataTypeName
from enmapboxprocessing.algorithm.appendenviheadertogtiffrasteralgorithm import AppendEnviHeaderToGTiffRasterAlgorithm
from enmapboxprocessing.algorithm.saverasterlayerasalgorithm import SaveRasterAsAlgorithm
from enmapboxprocessing.algorithm.translaterasteralgorithm import TranslateRasterAlgorithm
from qgis.core import QgsBrowserModel, QgsDataCollectionItem, QgsDataItem, QgsLayerItem, QgsMapLayer, QgsRasterLayer, \
    QgsApplication, QgsDataItemProviderRegistry, QgsDataItemProvider, Qgis

from enmapbox.externals.qps.models import TreeModel, TreeNode, TreeView
from enmapbox.testing import EnMAPBoxTestCase, TestObjects
from qgis.PyQt.QtCore import Qt

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


class RasterBandTreeNode(TreeNode):

    def __init__(self, rasterLayer: QgsRasterLayer, bandIndex, *args, **kwds):
        super().__init__(*args, **kwds)
        assert isinstance(rasterLayer, QgsRasterLayer)
        assert bandIndex >= 0
        assert bandIndex < rasterLayer.bandCount()
        # self.mDataSource = dataSource
        self.mBandIndex = bandIndex

        if False:
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


class ClassificationNodeLayer(TreeNode):

    def __init__(self, classificationScheme, name='Classification Scheme'):
        super(ClassificationNodeLayer, self).__init__()
        self.setName(name)
        to_add = []
        for i, ci in enumerate(classificationScheme):
            to_add.append(TreeNode(name='{}'.format(i), values=ci.name(), icon=ci.icon()))
        self.appendChildNodes(to_add)


class ColorTreeNode(TreeNode):

    def __init__(self, color: QColor):
        assert isinstance(color, QColor)

        pm = QPixmap(QSize(20, 20))
        pm.fill(color)
        icon = QIcon(pm)
        name = color.name()
        value = color.getRgbF()
        super(ColorTreeNode, self).__init__(name=name, value=value, icon=icon)



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

    def updateNodes(self, dataItem: QgsDataItem) -> dict:
        self.removeAllChildNodes()
        data = dict()
        if not isinstance(dataItem, QgsDataItem):
            return data


        childs = []
        value = []

        if os.path.exists(dataItem.path()):

            try:
                size = os.path.getsize(dataItem.path())
                size = fileSizeString(size)
                value.append(size)
                childs += [TreeNode('File', size)]
            except:
                pass
        lyr = None
        if isinstance(dataItem, QgsLayerItem):

            if dataItem.mapLayerType() == QgsMapLayerType.VectorLayer:
                lyr = QgsVectorLayer(dataItem.path(), dataItem.name(), dataItem.providerKey())
            elif dataItem.mapLayerType() == QgsMapLayerType.RasterLayer:
                lyr = QgsRasterLayer(dataItem.path(), dataItem.name(), dataItem.providerKey())

        if isinstance(lyr, QgsMapLayer) and lyr.isValid():

            ext = SpatialExtent.fromLayer(lyr)
            mu = QgsUnitTypes.encodeUnit(ext.crs().mapUnits())

            data['map_layer'] = lyr
            data['map_units'] = mu
            data['extent'] = ext

            childs += [TreeNode('Width', value='{:0.2f} {}'.format(ext.width(), mu), toolTip='Spatial width'),
                       TreeNode('Height', value='{:0.2f} {}'.format(ext.height(), mu, toolTip='Spatial height'))
                       ]

            if isinstance(lyr, QgsRasterLayer):
                dp: QgsRasterDataProvider = lyr.dataProvider()
                value.append(f'{lyr.width()}'
                             f'x{lyr.height()}'
                             f'x{lyr.bandCount()}'
                             f'x{dp.dataTypeSize(1)} ({QGIS_DATATYPE_NAMES.get(dp.dataType(1), "unknown type")})')

                childs += [TreeNode('Pixel',
                                    value=f'{lyr.rasterUnitsPerPixelX()}x'
                                          f'{lyr.rasterUnitsPerPixelY()} '
                                          f'{QgsUnitTypes.encodeUnit(lyr.crs().mapUnits())}',
                                    toolTip='Size of single pixel / ground sampling resolution'),
                           TreeNode('Samples', value=lyr.width(), toolTip='Samples/columns in X direction'),
                           TreeNode('Lines', value=lyr.height(), toolTip='Lines/rows in Y direction'),
                           TreeNode('Bands', value=lyr.bandCount(), toolTip='Raster bands'),
                           TreeNode('Data Type',
                                    value=dataTypeName(dp.dataType(1)),
                                    toolTip=dataTypeName(dp.dataType(1), verbose=True))
                           ]
            elif isinstance(lyr, QgsVectorLayer):
                value.append('{} features'.format(lyr.featureCount()))

        self.setValue(' '.join([str(v) for v in value]))
        self.appendChildNodes(childs)
        return data


class DataSource(TreeNode):

    def __init__(self, dataItem: QgsDataItem, **kwds):
        assert isinstance(dataItem, QgsDataItem)

        super().__init__(dataItem.name(), icon=dataItem.icon(), toolTip=dataItem.path(), **kwds)

        self.mDataItem: QgsDataItem = dataItem

        self.mNodeSize: DataSourceSizesTreeNode = DataSourceSizesTreeNode()
        self.mNodePath: TreeNode = TreeNode('Path')
        self.appendChildNodes([self.mNodePath, self.mNodeSize])

    def source(self) -> str:
        return self.mDataItem.path()

    def dataItem(self) -> QgsDataItem:
        return self.mDataItem

    def updateNodes(self, **kwds) -> dict:

        dataItem: QgsDataItem = self.dataItem()
        self.setName(dataItem.name())
        self.setToolTip(dataItem.toolTip())
        self.setIcon(dataItem.icon())

        self.mNodePath.setValue(dataItem.path())
        data = dict()
        data.update(self.mNodeSize.updateNodes(self.dataItem()))
        return data

class SpatialDataSource(DataSource):

    def __init__(self, dataItem: QgsLayerItem):

        super().__init__(dataItem)
        assert isinstance(dataItem, QgsLayerItem)

        self.nodeExtXmu: TreeNode = TreeNode('Width')
        self.nodeExtYmu: TreeNode = TreeNode('Height')
        self.nodeCRS: CRSLayerTreeNode = CRSLayerTreeNode(QgsCoordinateReferenceSystem())
        self.mNodeSize.appendChildNodes([self.nodeExtXmu, self.nodeExtYmu])
        self.appendChildNodes(self.nodeCRS)

    def updateNodes(self) -> dict:
        data = super().updateNodes()

        ext = data.get('spatial_extent', None)
        if isinstance(ext, SpatialExtent):
            mu = QgsUnitTypes.toString(ext.crs().mapUnits())
            self.nodeCRS.setCrs(ext.crs())
            self.nodeExtXmu.setValue('{} {}'.format(ext.width(), mu))
            self.nodeExtYmu.setValue('{} {}'.format(ext.height(), mu))
        else:
            self.nodeCRS.setCrs(QgsCoordinateReferenceSystem())
            self.nodeExtXmu.setValue(None)
            self.nodeExtYmu.setValue(None)
        return data


class VectorDataSource(SpatialDataSource):

    def __init__(self, dataItem: QgsLayerItem):
        super().__init__(dataItem)
        assert isinstance(dataItem, QgsLayerItem)
        assert dataItem.mapLayerType() == QgsMapLayerType.VectorLayer


class RasterDataSource(SpatialDataSource):

    def __init__(self, dataItem: QgsLayerItem):
        super(RasterDataSource, self).__init__(dataItem)
        assert isinstance(dataItem, QgsLayerItem)
        assert dataItem.mapLayerType() == QgsMapLayerType.RasterLayer

        self.mNodeBands: TreeNode = TreeNode('Bands', toolTip='Number of Raster Bands')
        self.appendChildNodes(self.mNodeBands)
        self.updateNodes()

    def updateNodes(self) -> dict:
        data = super().updateNodes()

        self.mNodeBands.removeAllChildNodes()

        lyr = data.get('map_layer', None)
        if isinstance(lyr, QgsRasterLayer):
            self.mNodeBands.setValue(lyr.bandCount())
            bandNodes = []
            for b in range(lyr.bandCount()):
                bandName = lyr.bandName(b + 1)
                bandNode = RasterBandTreeNode(lyr, b, name=str(b + 1), value=bandName)
                bandNodes.append(bandNode)
            self.mNodeBands.appendChildNodes(bandNodes)

class ModelDataSource(DataSource):

    def __init__(self, dataItem: QgsDataItem):
        super().__init__(dataItem)
        assert dataItem.providerKey() == 'special:pkl'


class FileDataSource(DataSource):

    def __init__(self, dataItem: QgsLayerItem):
        assert isinstance(dataItem, QgsLayerItem)
        assert dataItem.type() == QgsLayerItem.NoType
        assert dataItem.providerKey() == 'speclia:file'
        super(FileDataSource, self).__init__(dataItem)


class DataSourceSet(TreeNode):

    def __init__(self, *args, name: str = '<source set>', **kwds):
        super().__init__(*args, name=name, **kwds)

        self.mSetName = name
        self.updateName()

    def clear(self):
        """Removes all datasources
        """
        self.removeAllChildNodes()

    def updateName(self):

        self.setName(f'{self.mSetName} ({len(self.childNodes())})')

    def sources(self) -> typing.List[str]:
        sources = []
        for s in self.dataSources():
            sources.append(s.source())
        return sources

    def dataSources(self) -> typing.List[DataSource]:
        return self.childNodes()

    def addDataSources(self, dataSources: typing.Union[DataSource, typing.List[DataSource]]):
        if isinstance(dataSources, DataSource):
            dataSources = [dataSources]

        existing = self.sources()

        for s in dataSources:
            assert isinstance(s, DataSource)
            assert self.isValidSource(s)
        # ensure unique source names
        dataSources = [s for s in dataSources if s.source() not in existing]

        self.appendChildNodes(dataSources)
        self.updateName()

    def isValidSource(self, source) -> bool:
        raise NotImplementedError


class ModelDataSourceSet(DataSourceSet):
    def __init__(self, *args, **kwds):
        super().__init__(*args,
                         name='Models',
                         icon=QgsApplication.getThemeIcon('processingAlgorithm.svg')
                         )

    def isValidSource(self, source) -> bool:
        return isinstance(source, ModelDataSource)


class VectorDataSourceSet(DataSourceSet):

    def __init__(self, *args, **kwds):
        super().__init__(*args,
                         name='Vectors',
                         icon=QgsApplication.getThemeIcon('mIconVector.svg')
                         )

    def isValidSource(self, source) -> bool:
        return isinstance(source, VectorDataSource)


class FileDataSourceSet(DataSourceSet):

    def __init__(self, *args, **kwds):
        super(FileDataSourceSet, self).__init__(*args,
                                                name='Other Files',
                                                icon=QIcon(r':/trolltech/styles/commonstyle/images/file-128.png')
                                                )

        def isValidSource(self, source) -> bool:
            return isinstance(source, FileDataSource)


class RasterDataSourceSet(DataSourceSet):

    def __init__(self, *args, **kwds):
        super(RasterDataSourceSet, self).__init__(*args,
                                                  name='Rasters',
                                                  icon=QgsApplication.getThemeIcon('mIconRaster.svg')
                                                  )

    def isValidSource(self, source) -> bool:
        return isinstance(source, RasterDataSource)


class DataSourceFactory(object):

    @staticmethod
    def create(source: any, provider: str = None, name: str = None) -> typing.List[DataSource]:
        """
        Searches the input for DataSources
        """
        results = []
        if isinstance(source, list):
            for s in source:
                results.extend(DataSourceFactory.create(source, provider=provider, name=name))
        else:
            dataItem: QgsDataItem = None
            if isinstance(source, QgsMapLayer):
                dataItem = QgsLayerItem.typeFromMapLayer(source)

            if dataItem is None:
                if isinstance(source, pathlib.Path):
                    source = source.as_posix()
                elif isinstance(source, QUrl):
                    source = source.toString(QUrl.PreferLocalFile | QUrl.RemoveQuery)

                if isinstance(source, str):

                    if name is None:
                        name = pathlib.Path(source).name

                    if re.search(r'\.(pkl)$', source, re.I):
                        dataItem = QgsDataItem(Qgis.BrowserItemType.Custom, None, name, source, 'special:pkl')

                    if not isinstance(dataItem, QgsDataItem):
                        if re.search(r'\.(bsq|tiff?|hdf|bil|bip|grib|xml)$', source, re.I):
                            mapLayerTypes = [QgsRasterLayer, QgsVectorLayer]
                        else:
                            mapLayerTypes = [QgsVectorLayer, QgsRasterLayer]

                        for mapLayerType in mapLayerTypes:
                            try:
                                lyr = mapLayerType(source, name)
                                if isinstance(lyr, QgsMapLayer) and lyr.isValid():
                                    dtype = QgsLayerItem.typeFromMapLayer(lyr)
                                    dataItem = QgsLayerItem(None, lyr.name(), lyr.source(),
                                                            lyr.source(), dtype, lyr.providerType())
                                    break
                            except:
                                pass

                    if dataItem is None:
                        if pathlib.Path(source).is_file():
                            dataItem = QgsDataItem(Qgis.BrowserItemType.Custom, None, name, source, 'special:file')
                            s = ""
                if isinstance(dataItem, QgsDataItem):
                    if isinstance(dataItem, QgsLayerItem):
                        if dataItem.mapLayerType() == QgsMapLayer.RasterLayer:
                            results.append(RasterDataSource(dataItem))
                        elif dataItem.mapLayerType() == QgsMapLayer.VectorLayer:
                            results.append(VectorDataSource(dataItem))
                    elif dataItem.providerKey() == 'special:pkl':
                        results.append(ModelDataSource(dataItem))
                    elif dataItem.providerKey() == 'special:files':
                        results.append(FileDataSource(dataItem))

        return results

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


class DataSourceManager(TreeModel):

    def __init__(self, *args, **kwds):

        super().__init__(*args, **kwds)
        self.mRasters: RasterDataSourceSet = RasterDataSourceSet()
        self.mVectors: VectorDataSourceSet = VectorDataSourceSet()
        self.mModels: ModelDataSourceSet = ModelDataSourceSet()
        self.mFiles: FileDataSourceSet = FileDataSourceSet()
        self.rootNode().appendChildNodes([self.mRasters, self.mVectors, self.mModels, self.mFiles])

        # self.mModels: DataSourceCollectionItem = None
        # self.mOthers: DataSourceCollectionItem = None

    def clear(self):
        """
        Removes all data sources
        """
        for sourceSet in self.sourceSets():
            sourceSet.clear()

    def importQGISLayers(self):
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
                    layers.append(layerTree.layer())

        if len(layers) > 0:
            self.addSources(DataSourceFactory.create(layers))

    def sourceSets(self) -> typing.List[DataSourceSet]:
        return [c for c in self.rootNode().childNodes() if isinstance(c, DataSourceSet)]

    def addSources(self, sources: typing.Union[DataSource, typing.List[DataSource]]):

        if isinstance(sources, DataSource):
            sources = [sources]

        for source in sources:
            added = False
            for sourceSet in self.sourceSets():
                if sourceSet.isValidSource(source):
                    sourceSet.addDataSources(source)
                    added = True
                    break


class DataSourceManagerProxyModel(QSortFilterProxyModel):

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.setRecursiveFilteringEnabled(True)
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)


class DataSourceManagerTreeView(TreeView):
    """
    A TreeView to show EnMAP-Box Data Sources
    """
    sigPopulateContextMenu = pyqtSignal(QMenu)

    def __init__(self, *args, **kwds):
        super(DataSourceManagerTreeView, self).__init__(*args, **kwds)
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
        dataSources = self.selectedDataSources()
        srcURIs = list(set([s.source() for s in dataSources]))

        from enmapbox.gui.enmapboxgui import EnMAPBox
        enmapbox = EnMAPBox.instance()

        DSM: DataSourceManager = self.model().sourceModel().dataSourceManager
        if not isinstance(DSM, DataSourceManager):
            return

        mapDocks = []
        if isinstance(enmapbox, EnMAPBox):
            mapDocks = enmapbox.dockManager().docks('MAP')

        m: QMenu = QMenu()
        m.setToolTipsVisible(True)

        if isinstance(node, DataSourceSet):
            a = m.addAction('Remove')
            assert isinstance(a, QAction)
            a.setToolTip('Removes all datasources from this node')
            a.triggered.connect(lambda *args, node=node, dsm=DSM:
                                DSM.removeSources(node.dataSources()))

        if isinstance(node, DataSource):
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


            def appendRasterActions(sub: QMenu, src: RasterDataSource, target):
                assert isinstance(src, RasterDataSource)
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

            if isinstance(src, RasterDataSource):
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

                parameters = {TranslateRasterAlgorithm.P_RASTER: src.source()}
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

            if isinstance(src, VectorDataSource):
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


        if isinstance(node, RasterBandTreeNode):
            a = m.addAction('Band statistics')
            a.setEnabled(False)

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

    def openInMap(self, dataSource: typing.Union[VectorDataSource, RasterDataSource],
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

        if not isinstance(dataSource, (VectorDataSource, RasterDataSource)):
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
        if isinstance(model, DataSourceManager):
            model.dataSourceManager.clear()

    def selectedDataSources(self) -> typing.List[DataSource]:

        sources = []
        for n in self.selectedNodes():
            if isinstance(n, DataSource) and n not in sources:
                sources.append(n)
        return sources

    def openInSpeclibEditor(self, speclib: QgsVectorLayer):
        """
        Opens a SpectralLibrary in a new SpectralLibraryDock
        :param speclib: SpectralLibrary

        """
        from enmapbox.gui.enmapboxgui import EnMAPBox
        from enmapbox.gui.docks import SpectralLibraryDock
        EnMAPBox.instance().dockManager().createDock(SpectralLibraryDock, speclib=speclib)

    def openInAttributeEditor(self, vectorLayer: QgsVectorLayer):
        from enmapbox.gui.enmapboxgui import EnMAPBox
        from enmapbox.gui.docks import AttributeTableDock
        EnMAPBox.instance().dockManager().createDock(AttributeTableDock, layer=vectorLayer)


class DataSourceV2Tests(EnMAPBoxTestCase):

    def setUp(self):
        super().setUp()

    def test_DataSourceModel(self):
        from enmapbox.exampledata import enmap, landcover_polygons, library
        from testdata import classifier_pkl
        from testdata.asd import filenames_binary
        sources = [enmap,
                   landcover_polygons,
                   library,
                   library,
                   classifier_pkl,
                   classifier_pkl,
                   filenames_binary[0]]

        model = DataSourceManager()

        proxy = DataSourceManagerProxyModel()
        proxy.setSourceModel(model)

        tv = DataSourceManagerTreeView()
        tv.setModel(proxy)

        for source in sources:
            dataSources = DataSourceFactory.create(source)
            self.assertIsInstance(dataSources, list)
            model.addSources(dataSources)
        self.showGui(tv)
