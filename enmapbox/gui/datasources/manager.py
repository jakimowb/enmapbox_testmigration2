import os
import pathlib
import pickle
import re
import typing
import warnings
from os.path import splitext

from qgis.core import QgsMimeDataUtils
from PyQt5.QtCore import QMimeData, QModelIndex, Qt, QUrl, QSortFilterProxyModel, pyqtSignal
from PyQt5.QtGui import QContextMenuEvent, QIcon
from PyQt5.QtWidgets import QMenu, QAction, QApplication, QAbstractItemView, QTreeView

import qgis
from qgis.core import Qgis

from enmapbox.externals.qps.layerproperties import defaultRasterRenderer
from enmapbox.externals.qps.models import TreeModel, TreeView, TreeNode
from enmapbox.externals.qps.utils import defaultBands, bandClosestToWavelength, loadUi, qgisAppQgisInterface
from .metadata import RasterBandTreeNode
from .datasources import DataSource, SpatialDataSource, VectorDataSource, RasterDataSource, \
    ModelDataSource, FileDataSource
from enmapbox.gui.datasources.datasourcesets import DataSourceSet, ModelDataSourceSet, VectorDataSourceSet, \
    FileDataSourceSet, RasterDataSourceSet
# from enmapbox.gui.dataviews.docks import SpectralLibraryDock
# from enmapbox.gui.mapcanvas import MapDock
# from enmapbox.gui.mimedata import MDF_URILIST, MDF_QGIS_LAYERTREEMODELDATA, QGIS_URILIST_MIMETYPE, extractMapLayers, \
#    MDF_RASTERBANDS
from qgis.gui import QgisInterface, QgsMapCanvas, QgsDockWidget

from qgis.core import QgsLayerTreeGroup, QgsLayerTreeLayer, QgsMapLayer, QgsProject, QgsWkbTypes, QgsRasterLayer, \
    QgsRasterDataProvider, QgsRasterRenderer, QgsVectorLayer, QgsDataItem, QgsLayerItem, Qgis

from enmapbox.gui.utils import enmapboxUiPath
from enmapboxprocessing.algorithm.appendenviheadertogtiffrasteralgorithm import AppendEnviHeaderToGTiffRasterAlgorithm
from enmapboxprocessing.algorithm.saverasterlayerasalgorithm import SaveRasterAsAlgorithm
from enmapboxprocessing.algorithm.translaterasteralgorithm import TranslateRasterAlgorithm
from ..mimedata import MDF_URILIST, QGIS_URILIST_MIMETYPE, extractMapLayers

from ...externals.qps.speclib.core import is_spectral_library


class DataSourceManager(TreeModel):
    sigDataSourcesRemoved = pyqtSignal(list)
    sigDataSourcesAdded = pyqtSignal(list)

    def __init__(self, *args, **kwds):

        super().__init__(*args, **kwds)
        self.mRasters: RasterDataSourceSet = RasterDataSourceSet()
        self.mVectors: VectorDataSourceSet = VectorDataSourceSet()
        self.mModels: ModelDataSourceSet = ModelDataSourceSet()
        self.mFiles: FileDataSourceSet = FileDataSourceSet()
        self.rootNode().appendChildNodes([self.mRasters, self.mVectors, self.mModels, self.mFiles])

        from enmapbox import EnMAPBox
        self.mEnMAPBoxInstance: EnMAPBox = None

    def __len__(self):
        return len(self.dataSources())

    def enmapBoxInstance(self) -> 'EnMAPBox':
        return self.mEnMAPBoxInstance

    def setEnMAPBoxInstance(self, enmapbox):
        self.mEnMAPBoxInstance = enmapbox

    def dropMimeData(self, mimeData: QMimeData, action, row: int, column: int, parent: QModelIndex):

        assert isinstance(mimeData, QMimeData)

        result = False
        toAdd = []
        if action in [Qt.MoveAction, Qt.CopyAction]:
            # collect nodes
            nodes = []

            # add new data from external sources
            from enmapbox.gui.mimedata import MDF_QGIS_LAYERTREEMODELDATA
            if mimeData.hasFormat(MDF_URILIST):
                for url in mimeData.urls():
                    toAdd.extend(DataSourceFactory.create(url))

            # add data dragged from QGIS
            elif mimeData.hasFormat(MDF_QGIS_LAYERTREEMODELDATA) or mimeData.hasFormat(QGIS_URILIST_MIMETYPE):

                lyrs = extractMapLayers(mimeData)
                toAdd.extend(DataSourceFactory.create(lyrs))
        added = []
        if len(toAdd) > 0:
            added = self.addDataSources(toAdd)

        return len(added) > 0

    def mimeData(self, indexes: list) -> QMimeData:
        indexes = sorted(indexes)
        if len(indexes) == 0:
            return None

        bandNodes: typing.List[RasterBandTreeNode] = []
        dataSources: typing.List[DataSource] = []
        for node in self.indexes2nodes(indexes):
            if isinstance(node, DataSource):
                dataSources.append(node)
            elif isinstance(node, DataSourceSet):
                dataSources.extend(node.dataSources())
            elif isinstance(node, RasterBandTreeNode):
                bandNodes.append(node)

        mimeData = QMimeData()

        dataSources = list(set(dataSources))
        sourceList = [d.source() for d in dataSources]

        bandInfo = list()
        for node in bandNodes:
            ds: RasterDataSource = node.parentNode()
            if isinstance(ds, RasterDataSource):
                source = ds.dataItem().path()
                provider = ds.dataItem().providerKey()
                band = node.mBandIndex
                baseName = '{}:{}'.format(node.mDataSource.name(), node.name())
                bandInfo.append((source, baseName, provider, band))

        if len(bandInfo) > 0:
            from enmapbox.gui.mimedata import MDF_RASTERBANDS
            mimeData.setData(MDF_RASTERBANDS, pickle.dumps(bandInfo))

        urls = [QUrl.fromLocalFile(s) if os.path.isfile(s) else QUrl(s) for s in sourceList]
        if len(urls) > 0:
            mimeData.setUrls(urls)
        return mimeData

    def mimeTypes(self):
        # specifies the mime types handled by this model
        types = []
        # types.append(MDF_DATASOURCETREEMODELDATA)
        from enmapbox.gui.mimedata import MDF_QGIS_LAYERTREEMODELDATA, QGIS_URILIST_MIMETYPE, MDF_URILIST
        types.append(MDF_QGIS_LAYERTREEMODELDATA)
        types.append(QGIS_URILIST_MIMETYPE)
        types.append(MDF_URILIST)
        return types

    def clear(self):
        """
        Removes all data sources
        """
        self.removeDataSources(self.dataSources())

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
            self.addDataSources(DataSourceFactory.create(layers))

    def dataSourceSets(self) -> typing.List[DataSourceSet]:
        return [c for c in self.rootNode().childNodes() if isinstance(c, DataSourceSet)]

    def sources(self, *args):
        warnings.warn(DeprecationWarning('Use .dataSources() instead.'), stacklevel=2)
        return self.dataSources(*args)

    def dataSources(self, filter=None) -> typing.List[DataSource]:
        l = list()
        for ds in self.dataSourceSets():
            l.extend(ds.dataSources())

        if filter:
            from .datasources import LUT_DATASOURCETYPES, DataSourceTypes
            assert filter in LUT_DATASOURCETYPES.keys(), f'Unknown datasource filter "{filter}"'
            if filter == DataSourceTypes.SpectralLibrary:
                l = [ds for ds in l if isinstance(ds, VectorDataSource) and ds.isSpectralLibrary()]
            else:
                cls = LUT_DATASOURCETYPES[filter]
                l = [ds for ds in l if isinstance(ds, cls)]
        return l

    def findDataSources(self, inputs) -> typing.List[DataSource]:
        if not isinstance(inputs, list):
            inputs = [inputs]
        allDataSources = self.dataSources()

        foundSources = []
        for input in inputs:

            if isinstance(input, DataSource) and input in allDataSources:
                foundSources.append(allDataSources[allDataSources.index(input)])  # return reference in own list
            elif isinstance(input, QgsMapLayer):

                for ds in allDataSources:
                    dataItem = ds.dataItem()
                    if isinstance(ds, SpatialDataSource) \
                            and dataItem.path() == input.source() \
                            and dataItem.providerKey() == input.providerType():
                        foundSources.append(ds)
            elif isinstance(input, str):
                for ds in allDataSources:
                    if ds.dataItem().path() == input:
                        foundSources.append(ds)

        return foundSources

    def removeSources(self, *args, **kwds):
        warnings.warn('Use .removeDataSources', DeprecationWarning, stacklevel=2)

        return self.removeDataSources(*args, **kwds)

    def removeDataSources(self,
                          dataSources: typing.Union[DataSource, typing.List[DataSource]]) -> typing.List[DataSource]:

        ownedSources = self.findDataSources(dataSources)
        removed = []

        for dsSet in self.dataSourceSets():
            removed.extend(dsSet.removeDataSources(ownedSources))
        if len(removed) > 0:
            self.sigDataSourcesRemoved.emit(removed)
        return removed

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return Qt.ItemIsDropEnabled

        flags = super(DataSourceManager, self).flags(index)
        node = index.data(Qt.UserRole)
        if isinstance(node, (DataSource, RasterBandTreeNode)):
            flags = flags | Qt.ItemIsDropEnabled | Qt.ItemIsDragEnabled
        return flags

    def addSources(self, *args, **kwds):
        warnings.warn(DeprecationWarning('Use addDataSources instead'), stacklevel=2)
        self.addDataSources(*args, **kwds)

    def addSource(self, *args, **kwds):
        self.addSources(*args, **kwds)

    def addDataSources(self,
                       sources: typing.Union[DataSource, typing.List[DataSource]],
                       provider: str = None,
                       name: str = None) -> typing.List[DataSource]:
        sources = DataSourceFactory.create(sources, provider=provider, name=name)
        if isinstance(sources, DataSource):
            sources = [sources]
        added = []
        for source in sources:
            for sourceSet in self.dataSourceSets():
                if sourceSet.isValidSource(source):
                    newSources = sourceSet.addDataSources(source)
                    if len(newSources) > 0:
                        added.extend(newSources)
                        break
        if len(added) > 0:
            self.sigDataSourcesAdded.emit(added)
        return added


class DataSourceManagerProxyModel(QSortFilterProxyModel):

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.setRecursiveFilteringEnabled(True)
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)


class DataSourceManagerTreeView(TreeView):
    """
    A TreeView to show EnMAP-Box Data Sources
    """
    sigPopulateContextMenu = pyqtSignal(QMenu, TreeNode)

    def __init__(self, *args, **kwds):
        super(DataSourceManagerTreeView, self).__init__(*args, **kwds)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)

    def dataSourceManager(self) -> DataSourceManager:
        model = self.model()
        if isinstance(model, QSortFilterProxyModel):
            model = model.sourceModel()
        return model

    def enmapboxInstance(self) -> 'EnMAPBox':
        dsm = self.dataSourceManager()
        if isinstance(dsm, DataSourceManager):
            return dsm.enmapBoxInstance()
        return None

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

        DSM: DataSourceManager = self.dataSourceManager()
        if not isinstance(DSM, DataSourceManager):
            return

        enmapbox: EnMAPBox = self.enmapboxInstance()
        mapDocks = []
        if isinstance(enmapbox, EnMAPBox):
            mapDocks = enmapbox.dockManager().docks('MAP')

        m: QMenu = QMenu()
        m.setToolTipsVisible(True)

        aRemove = m.addAction('Remove')
        if isinstance(node, DataSourceSet):
            assert isinstance(aRemove, QAction)
            aRemove.setToolTip('Removes all datasources from this node')
            aRemove.triggered.connect(lambda *args, n=node, dsm=DSM:
                                      DSM.removeDataSources(n.dataSources()))

        elif isinstance(node, DataSource):
            aRemove.triggered.connect(lambda *args, ds=dataSources, dsm=DSM:
                                      dsm.removeDataSources(ds))
            aCopy = m.addAction('Copy URI / path')
            aCopy.triggered.connect(lambda *args, u=srcURIs:
                                    QApplication.clipboard().setText('\n'.join(u)))

            # todo: implement rename function

            def appendRasterActions(subMenu: QMenu, src: RasterDataSource, target):
                assert isinstance(src, RasterDataSource)
                subAction = subMenu.addAction('Default Colors')
                subAction.triggered.connect(lambda *args, s=src, t=target:
                                            self.openInMap(s, t, rgb='DEFAULT'))

                b = src.mWavelengthUnits is not None

                subAction = subMenu.addAction('True Color')
                subAction.setToolTip('Red-Green-Blue true colors')
                subAction.triggered.connect(lambda *args, s=src, t=target:
                                            self.openInMap(s, t, rgb='R,G,B'))
                subAction.setEnabled(b)
                subAction = subMenu.addAction('CIR')
                subAction.setToolTip('nIR Red Green')
                subAction.triggered.connect(lambda *args, s=src, t=target:
                                            self.openInMap(s, t, rgb='NIR,R,G'))
                subAction.setEnabled(b)

                subAction = subMenu.addAction('SWIR')
                subAction.setToolTip('nIR swIR Red')
                subAction.triggered.connect(lambda *args, s=src, t=target:
                                            self.openInMap(s, t, rgb='NIR,SWIR,R'))
                subAction.setEnabled(b)

            if isinstance(node, RasterDataSource):
                sub = m.addMenu('Open in new map...')
                appendRasterActions(sub, node, None)

                sub = m.addMenu('Open in existing map...')
                if len(mapDocks) > 0:
                    for mapDock in mapDocks:
                        from ..dataviews.docks import MapDock
                        assert isinstance(mapDock, MapDock)
                        subsub = sub.addMenu(mapDock.title())
                        appendRasterActions(subsub, node, mapDock)
                else:
                    sub.setEnabled(False)
                sub = m.addMenu('Open in QGIS')
                if isinstance(qgis.utils.iface, QgisInterface):
                    appendRasterActions(sub, node, QgsProject.instance())
                else:
                    sub.setEnabled(False)

                # AR: add some useful processing algo shortcuts
                parameters = {SaveRasterAsAlgorithm.P_RASTER: node.source()}
                a: QAction = m.addAction('Save as')
                a.setIcon(QIcon(':/images/themes/default/mActionFileSaveAs.svg'))
                a.triggered.connect(
                    lambda src: EnMAPBox.instance().showProcessingAlgorithmDialog(
                        SaveRasterAsAlgorithm(), parameters, parent=self
                    )
                )

                parameters = {TranslateRasterAlgorithm.P_RASTER: node.source()}
                a: QAction = m.addAction('Translate')
                a.setIcon(QIcon(':/images/themes/default/mActionFileSaveAs.svg'))
                a.triggered.connect(
                    lambda src: EnMAPBox.instance().showProcessingAlgorithmDialog(
                        TranslateRasterAlgorithm(), parameters, parent=self
                    )
                )

                if splitext(node.source())[1].lower() in ['.tif', '.tiff']:
                    parameters = {AppendEnviHeaderToGTiffRasterAlgorithm.P_RASTER: node.source()}
                    a: QAction = m.addAction('Append ENVI header')
                    a.setIcon(QIcon(':/images/themes/default/mActionFileSaveAs.svg'))
                    a.triggered.connect(
                        lambda src: EnMAPBox.instance().showProcessingAlgorithmDialog(
                            AppendEnviHeaderToGTiffRasterAlgorithm(), parameters, parent=self
                        )
                    )

            if isinstance(node, VectorDataSource):

                if node.wkbType() not in [QgsWkbTypes.NoGeometry, QgsWkbTypes.Unknown, QgsWkbTypes.UnknownGeometry]:
                    a = m.addAction('Open in new map')
                    a.triggered.connect(lambda *args, s=node: self.openInMap(s, None))

                    sub = m.addMenu('Open in existing map...')
                    if len(mapDocks) > 0:
                        for mapDock in mapDocks:
                            from ..dataviews.docks import MapDock
                            assert isinstance(mapDock, MapDock)
                            a = sub.addAction(mapDock.title())
                            a.triggered.connect(
                                lambda checked, s=node, d=mapDock:
                                self.openInMap(s, d))
                    else:
                        sub.setEnabled(False)

                a = m.addAction('Open Spectral Library Viewer')
                a.triggered.connect(
                    lambda *args, s=node: self.openInSpeclibEditor(node.asMapLayer()))

                a = m.addAction('Open Attribute Table')
                a.triggered.connect(lambda *args, s=node: self.openInAttributeEditor(s.asMapLayer()))

            if isinstance(node, SpatialDataSource):
                a = m.addAction('Open in QGIS')
                if isinstance(qgis.utils.iface, QgisInterface):
                    a.triggered.connect(lambda *args, s=node:
                                        self.openInMap(s, QgsProject.instance()))
        else:
            aRemove.setEnabled(False)

        if isinstance(node, RasterBandTreeNode):
            a = m.addAction('Band statistics')
            a.setEnabled(False)

            a = m.addAction('Open in new map')
            a.triggered.connect(lambda *args, n=node: self.openInMap(node, rgb=[n.mBandIndex]))

        if col == 1 and node.value() != None:
            a = m.addAction('Copy')
            a.triggered.connect(lambda *args, n=node: QApplication.clipboard().setText(str(n.value())))

        if isinstance(node, TreeNode):
            node.populateContextMenu(m)

        a = m.addAction('Remove all DataSources')
        a.setToolTip('Removes all data source.')
        a.triggered.connect(self.onRemoveAllDataSources)

        self.sigPopulateContextMenu.emit(m, node)

        m.exec_(self.viewport().mapToGlobal(event.pos()))

    def openInMap(self, dataSource: typing.Union[VectorDataSource, RasterDataSource],
                  target: typing.Union[QgsMapCanvas, QgsProject, 'MapDock'] = None,
                  rgb=None,
                  sampleSize: int = 256):
        """
        Add a SpatialDataSource as QgsMapLayer to a mapCanvas.
        :param target:
        :param sampleSize:
        :param dataSource: SpatialDataSource
        :param rgb:
        """

        if not isinstance(dataSource, (VectorDataSource, RasterDataSource)):
            return
        from ..dataviews.docks import MapDock
        LOAD_DEFAULT_STYLE: bool = isinstance(rgb, str) and re.search('DEFAULT', rgb, re.I)

        if target is None:
            emb = self.enmapboxInstance()
            from enmapbox import EnMAPBox
            if not isinstance(emb, EnMAPBox):
                return None
            dock = emb.createDock('MAP')

            assert isinstance(dock, MapDock)
            target = dock.mapCanvas()

        if isinstance(target, MapDock):
            target = target.mapCanvas()

        assert isinstance(target, (QgsMapCanvas, QgsProject))

        # loads the layer with default style (wherever it is defined)
        lyr = dataSource.asMapLayer()

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
        dsm: DataSourceManager = self.dataSourceManager()
        if dsm:
            dsm.clear()

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
        from enmapbox import EnMAPBox
        from enmapbox.gui.dataviews.docks import SpectralLibraryDock

        emb = self.enmapboxInstance()
        if isinstance(emb, EnMAPBox):
            emb.createDock(SpectralLibraryDock, speclib=speclib)

    def openInAttributeEditor(self, vectorLayer: QgsVectorLayer):
        from enmapbox.gui.dataviews.docks import AttributeTableDock
        from enmapbox import EnMAPBox
        emb = self.enmapboxInstance()
        if isinstance(emb, EnMAPBox):
            emb.dockManager().createDock(AttributeTableDock, layer=vectorLayer)


class DataSourceManagerPanelUI(QgsDockWidget):
    def __init__(self, parent=None):
        super(DataSourceManagerPanelUI, self).__init__(parent)
        loadUi(enmapboxUiPath('datasourcemanagerpanel.ui'), self)
        self.mDataSourceManager: DataSourceManager = None
        self.mDataSourceManagerProxyModel: DataSourceManagerProxyModel = DataSourceManagerProxyModel()
        assert isinstance(self.mDataSourceManagerTreeView, DataSourceManagerTreeView)
        self.mDataSourceManagerTreeView.setUniformRowHeights(True)
        self.mDataSourceManagerTreeView.setDragDropMode(QAbstractItemView.DragDrop)

        self.btnCollapse.clicked.connect(lambda: self.mDataSourceManagerTreeView.expandSelectedNodes(False))
        self.btnExpand.clicked.connect(lambda: self.mDataSourceManagerTreeView.expandSelectedNodes(True))

        # init actions
        self.actionAddDataSource.triggered.connect(lambda: self.mDataSourceManager.addDataSourceByDialog())
        self.actionRemoveDataSource.triggered.connect(
            lambda: self.mDataSourceManager.removeDataSources(self.selectedDataSources()))
        self.actionRemoveDataSource.setEnabled(False)  # will be enabled with selection of node

        # self.mDataSourceManager.exportSourcesToQGISRegistry(showLayers=True)
        self.actionSyncWithQGIS.triggered.connect(self.onSyncToQGIS)

        self.tbFilterText.textChanged.connect(self.setFilter)
        hasQGIS = qgisAppQgisInterface() is not None
        self.actionSyncWithQGIS.setEnabled(hasQGIS)

        self.initActions()

    def dataSourceManagerTreeView(self) -> DataSourceManagerTreeView:
        return self.mDataSourceManagerTreeView

    def setFilter(self, pattern: str):
        self.mDataSourceManagerProxyModel.setFilterWildcard(pattern)

    def onSyncToQGIS(self, *args):
        if isinstance(self.mDataSourceManager, DataSourceManager):
            self.mDataSourceManager.importQGISLayers()

    def initActions(self):

        self.btnAddSource.setDefaultAction(self.actionAddDataSource)
        self.btnSync.setDefaultAction(self.actionSyncWithQGIS)
        self.btnRemoveSource.setDefaultAction(self.actionRemoveDataSource)
        self.btnCollapse.clicked.connect(lambda: self.dataSourceManagerTreeView().expandSelectedNodes(False))
        self.btnExpand.clicked.connect(lambda: self.dataSourceManagerTreeView().expandSelectedNodes(True))

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
        self.mDataSourceManagerProxyModel.setSourceModel(self.mDataSourceManager)
        self.mDataSourceManagerTreeView.setModel(self.mDataSourceManagerProxyModel)
        self.mDataSourceManagerTreeView.selectionModel().selectionChanged.connect(self.onSelectionChanged)

    def onSelectionChanged(self, selected, deselected):

        s = self.selectedDataSources()
        self.actionRemoveDataSource.setEnabled(len(s) > 0)

    def selectedDataSources(self) -> typing.List[DataSource]:
        """
        :return: [list-of-selected-DataSources]
        """
        sources = set()

        for idx in self.dataSourceManagerTreeView().selectionModel().selectedIndexes():
            assert isinstance(idx, QModelIndex)
            node = idx.data(Qt.UserRole)
            if isinstance(node, DataSource):
                sources.add(node)
            elif isinstance(node, DataSourceSet):
                for s in node:
                    sources.add(s)
        return list(sources)


class DataSourceFactory(object):

    @staticmethod
    def create(source: any, provider: str = None, name: str = None) -> typing.List[DataSource]:
        """
        Searches the input for DataSources
        """
        results = []
        if isinstance(source, list):
            for s in source:
                results.extend(DataSourceFactory.create(s, provider=provider, name=name))
        else:
            if isinstance(source, DataSource):
                return [source]

                s = ""
            dataItem: QgsDataItem = None

            if isinstance(source, QgsMimeDataUtils.Uri):
                if not source.isValid():
                    return []
                else:
                    if source.layerType == 'raster':
                        dtype = QgsLayerItem.Raster
                        dataItem = QgsLayerItem(None, source.name, source.uri,
                                                source.uri, dtype, source.providerKey)
                    elif source.layerType == 'vector':
                        dtype = QgsLayerItem.Vector
                        dataItem = QgsLayerItem(None, source.name, source.uri,
                                                source.uri, dtype, source.providerKey)
                    else:
                        source = source.uri
                        provider = source.providerKey
                        name = source.name



            elif isinstance(source, QgsMapLayer):
                dtype = QgsLayerItem.typeFromMapLayer(source)
                dataItem = QgsLayerItem(None, source.name(), source.source(),
                                        source.source(), dtype, source.providerType())

            if dataItem is None:
                if isinstance(source, pathlib.Path):
                    source = source.as_posix()
                elif isinstance(source, QUrl):
                    source = source.toString(QUrl.PreferLocalFile | QUrl.RemoveQuery)

                if isinstance(source, str):
                    source = pathlib.Path(source).as_posix()

                    if name is None:
                        name = pathlib.Path(source).name

                    if re.search(r'\.(pkl)$', source, re.I):
                        if Qgis.versionInt() < 32000:
                            dataItem = QgsDataItem(QgsDataItem.Custom, None, name, source, 'special:pkl')
                        else:
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
                                    if is_spectral_library(lyr):
                                        dataItem.setIcon(QIcon(r':/qps/ui/icons/speclib.svg'))

                                    break
                            except:
                                pass

                    if dataItem is None:
                        if pathlib.Path(source).is_file():
                            if Qgis.versionInt() < 32000:
                                dataItem = QgsDataItem(QgsDataItem.Custom, None, name, source, 'special:file')
                            else:
                                dataItem = QgsDataItem(Qgis.BrowserItemType.Custom, None, name, source, 'special:file')

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
