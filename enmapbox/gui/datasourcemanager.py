import six, sys, os, gc, re, collections, uuid, logging
logger = logging.getLogger(__name__)
from qgis.core import *
from qgis.gui import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from enmapbox.gui.utils import PanelWidgetBase, loadUI
from osgeo import gdal, ogr
from enmapbox.gui.treeviews import *
from enmapbox.gui.datasources import *



class DataSourceGroupTreeNode(TreeNode):

    def __init__(self, parent, groupName, classDef):
        assert inspect.isclass(classDef)
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

    @staticmethod
    def readXml(element):

        if element.tagName() != 'data_source_group_tree_node':
            return None


        name = None
        classDef = None
        node = DataSourceGroupTreeNode(None, name, classDef)

        TreeNode.attachCommonPropertiesFromXML(node, element)

        return node


class DataSourceTreeNode(TreeNode):

    def __init__(self, parent, dataSource):
        super(DataSourceTreeNode, self).__init__(parent, '<empty>')
        self.disconnectDataSource()
        self.dataSource = None
        if dataSource:
            self.connectDataSource(dataSource)

    def connectDataSource(self, dataSource):
        from enmapbox.gui.datasources import DataSource
        assert isinstance(dataSource, DataSource)
        self.setName(dataSource.name)
        self.dataSource = dataSource
        self.setTooltip(dataSource.uri)
        self._icon = dataSource.getIcon()
        self.setCustomProperty('uuid', str(self.dataSource.uuid))
        self.setCustomProperty('uri', self.dataSource.uri)

    def disconnectDataSource(self):
        self.dataSource = None
        self.setName('<empty>')
        self._icon = None
        for k in self.customProperties():
            self.removeCustomProperty(k)

    @staticmethod
    def readXml(element):
        if element.tagName() != 'datasource-tree-node':
            return None

        cp = QgsObjectCustomProperties()
        cp.readXml(element)

        from enmapbox.gui.datasources import DataSourceFactory
        dataSource = DataSourceFactory.Factory(cp.value('uri'), name=element.attribute('name'))
        node = DataSourceTreeNode(None, dataSource)
        TreeNode.attachCommonPropertiesFromXML(node, element)

        return node

    def writeXML(self, parentElement):
        super(DataSourceTreeNode, self).writeXML(parentElement)
        elem = parentElement.lastChild().toElement()
        elem.setTagName('datasource-tree-node')
        elem.setAttribute('uuid', str(self.dataSource.uuid))


class SpatialDataSourceTreeNode(DataSourceTreeNode):

    def __init__(self, *args, **kwds):
        super(SpatialDataSourceTreeNode,self).__init__( *args, **kwds)

    def connectDataSource(self, dataSource):
        assert isinstance(dataSource, DataSourceSpatial)
        super(SpatialDataSourceTreeNode, self).connectDataSource(dataSource)

        ext = dataSource.spatialExtent
        assert isinstance(ext, SpatialExtent)
        CRSTreeNode(self, ext.crs())
        FileSizesTreeNode(self, dataSource)


class VectorDataSourceTreeNode(SpatialDataSourceTreeNode):

    def __init__(self, *args, **kwds):
        super(VectorDataSourceTreeNode,self).__init__( *args, **kwds)

class RasterDataSourceTreeNode(SpatialDataSourceTreeNode):

    def __init__(self, *args, **kwds):
        super(RasterDataSourceTreeNode,self).__init__( *args, **kwds)

    def connectDataSource(self, dataSource):
        assert isinstance(dataSource, DataSourceRaster)
        super(RasterDataSourceTreeNode, self).connectDataSource(dataSource)

        self.lyr = QgsRasterLayer(dataSource.getUri())
        QgsMapLayerRegistry.instance().addMapLayer(self.lyr)
        self.n1 = self.addLayer(self.lyr)
        self.n1.setName('TEST LAYR')
        self.n2 = QgsSimpleLegendNode(self.n1, 'subgroup')

        n = TreeNode(self, 'Size')
        TreeNode(n, 'Image {} x {} x {}'.format(dataSource.nSamples,
                                          dataSource.nLines,
                                          dataSource.nBands),
                 tooltip = 'Samples x Lines x Bands'
                 )
        TreeNode(n, 'Pixel {} x {} {}'.format(dataSource.pxSizeX,
                                              dataSource.pxSizeY,
                QgsUnitTypes.encodeUnit(dataSource.spatialExtent.crs().mapUnits())
                                              ),
                 )

class FileDataSourceTreeNode(DataSourceTreeNode):

    def __init__(self, *args, **kwds):
        super(FileDataSourceTreeNode,self).__init__( *args, **kwds)


class ProcessingTypeTreeNode(DataSourceTreeNode):

    def __init__(self, *args, **kwds):
        super(ProcessingTypeTreeNode, self).__init__(*args, **kwds)
        self.pfType = None

    def connectDataSource(self, processingTypeDataSource):
        super(ProcessingTypeTreeNode, self).connectDataSource(processingTypeDataSource)
        assert isinstance(self.dataSource, ProcessingTypeDataSource)
        self.pfType = processingTypeDataSource.pfType

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

                TreeNode(grp, '{} {}'.format(i, name), icon=icon)

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

    def dragEnterEvent(self, event):
        assert isinstance(event, QDragEnterEvent)
        #no removal, copy only
        #event.setDropAction(Qt.CopyAction)



class DataSourcePanelUI(PanelWidgetBase, loadUI('datasourcepanel.ui')):
    def __init__(self, parent=None):
        super(DataSourcePanelUI, self).__init__(parent)
        self.dataSourceManager = None
        assert isinstance(self.dataSourceTreeView, DataSourceTreeView)

        self.dataSourceTreeView.setDragDropMode(QAbstractItemView.DragDrop)

    def connectDataSourceManager(self, dataSourceManager):
        assert isinstance(dataSourceManager, DataSourceManager)
        self.dataSourceManager = dataSourceManager
        self.model = DataSourceManagerTreeModel(self, self.dataSourceManager)
        self.dataSourceTreeView.setModel(self.model)
        self.dataSourceTreeView.setMenuProvider(TreeViewMenuProvider(self.dataSourceTreeView))


class DataSourceManagerTreeModel(TreeModel):

    def __init__(self, parent, dataSourceManager):

        super(DataSourceManagerTreeModel, self).__init__(parent)
        assert isinstance(dataSourceManager, DataSourceManager)

        if True:
            self.setFlag(QgsLayerTreeModel.ShowLegend, True) #no effect
            self.setFlag(QgsLayerTreeModel.ShowSymbology, True) #no effect
            # self.setFlag(QgsLayerTreeModel.ShowRasterPreviewIcon, True)
            self.setFlag(QgsLayerTreeModel.ShowLegendAsTree, True)
            self.setFlag(QgsLayerTreeModel.AllowNodeReorder, True)
            self.setFlag(QgsLayerTreeModel.AllowNodeRename, True)
            self.setFlag(QgsLayerTreeModel.AllowNodeChangeVisibility, True)
            self.setFlag(QgsLayerTreeModel.AllowLegendChangeState, True)

        self.dataSourceManager = dataSourceManager
        self.dataSourceManager.sigDataSourceAdded.connect(self.addDataSource)
        self.dataSourceManager.sigDataSourceRemoved.connect(self.removeDataSource)

        for ds in self.dataSourceManager.sources:
            self.addDataSource(ds)

    def columnCount(self, index):
        return 2



    def mimeTypes(self):
        # specifies the mime types handled by this model
        types = []
        types.append(MimeDataHelper.MIME_DATASOURCETREEMODELDATA)
        types.append(MimeDataHelper.MIME_LAYERTREEMODELDATA)
        types.append(MimeDataHelper.MIME_URILIST)
        return types

    def dropMimeData(self, data, action, row, column, parent):
        parentNode = self.index2node(parent)
        assert isinstance(data, QMimeData)

        isL1Node = parentNode.parent() == self.rootNode

        result = False
        if action == Qt.MoveAction:
            # collect nodes
            nodes = []

            if data.hasFormat("application/enmapbox.datasourcetreemodeldata"):
                return False  # do not allow moving within DataSourceTree

            # add new data from external
            elif data.hasFormat('text/uri-list'):
                for url in data.urls():
                    self.dataSourceManager.addSource(url)

            # add new from QGIS
            elif data.hasFormat("application/qgis.layertreemodeldata"):
                result = QgsLayerTreeModel.dropMimeData(self, data, action, row, column, parent)
                s = ""

            nodes = [n for n in nodes if n is not None]

            # insert nodes, if possible
            if len(nodes) > 0:
                if row == -1 and column == -1:
                    parentNode = parentNode.parent()
                parentNode.insertChildNodes(-1, nodes)
                result = True

        return result

    def mimeData(self, indexes):
        indexes = sorted(indexes)
        if len(indexes) == 0:
            return None

        nodesFinal = self.indexes2nodes(indexes, True)
        mimeData = QMimeData()
        # define application/enmapbox.datasourcetreemodeldata
        doc = QDomDocument()
        uriList = list()

        rootElem = doc.createElement("datasource_tree_model_data");
        exportedNodes = []

        for node in nodesFinal:
            if isinstance(node, DataSourceTreeNode):

                exportedNodes.append(node)

            elif isinstance(node, DataSourceGroupTreeNode):
                for n in node.children():
                    exportedNodes.append(n)

        for node in exportedNodes:
            node.writeXML(rootElem)
            uriList.append(QUrl(node.dataSource.uri))

        doc.appendChild(rootElem)
        txt = doc.toString()
        mimeData.setData("application/enmapbox.datasourcetreemodeldata", txt)

        # set text/uri-list
        if len(uriList) > 0:
            mimeData.setUrls(uriList)
        MH = MimeDataHelper(mimeData)
        return mimeData

    def getSourceGroup(self, dataSource):
        """Returns the source group relate to a data source"""
        assert isinstance(dataSource, DataSource)

        groups = [(DataSourceRaster, 'Raster Data'),
                  (DataSourceVector, 'Vector Data'),
                  (ProcessingTypeDataSource, 'Models'),
                  (DataSourceFile, 'Files'),
                  (DataSource, 'Other sources')]

        srcGrp = None
        for groupType, groupName in groups:
            if isinstance(dataSource, groupType):
                srcGrp = [c for c in self.rootNode.children() if c.name() == groupName]
                if len(srcGrp) == 0:
                    # create new group node and add it to the model
                    srcGrp = DataSourceGroupTreeNode(self.rootNode, groupName, groupType)
                elif len(srcGrp) == 1:
                    srcGrp = srcGrp[0]
                else:
                    raise Exception()
                break
        if srcGrp is None:
            s = ""
        return srcGrp

    def addDataSource(self, dataSource):
        assert isinstance(dataSource, DataSource)
        dataSourceNode = TreeNodeProvider.CreateNodeFromDataSource(dataSource, None)
        sourceGroup = self.getSourceGroup(dataSource)
        sourceGroup.addChildNode(dataSourceNode)
        dataSourceNode.setExpanded(False)
        s = ""

    def removeDataSource(self, dataSource):
        assert isinstance(dataSource, DataSource)
        sourceGroup = self.getSourceGroup(dataSource)
        to_remove = [node for node in sourceGroup.children() \
                     if isinstance(node, DataSourceTreeNode) and
                        node.dataSource == dataSource]
        for node in to_remove:
            sourceGroup.removeChildNode(node)

    def supportedDragActions(self):
        return Qt.CopyAction

    def supportedDropActions(self):
        return Qt.CopyAction

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        # specify TreeNode specific actions
        node = self.index2node(index)
        column = index.column()
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable

        if isinstance(node, TreeNode):

            if isinstance(node, DataSourceGroupTreeNode):
                flags |= Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
            elif isinstance(node, DataSourceTreeNode):
                flags |= Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled

        elif type(node) in [QgsLayerTreeLayer, QgsLayerTreeGroup]:
                flags |= Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
        return flags

    def contextMenu(self, node):
        menu = QMenu()
        if isinstance(node, DataSourceGroupTreeNode):
            a = menu.addAction('Clear')
            a.triggered.connect(lambda : self.dataSourceManager.removeSources(node.dataSources()))

        if isinstance(node, DataSourceTreeNode):
            a = menu.addAction('Remove')
            a.triggered.connect(lambda: self.dataSourceManager.removeSource(node.dataSource))

        if isinstance(node, ProcessingTypeTreeNode):
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
        assert isinstance(model, ProcessingTypeDataSource)
        pfType = model.pfType

        #this step should be done without writing anything on hard disk
        pathHTML = pfType.report().saveHTML().filename
        self.dataSourceManager.enmapbox.dockManager.createDock('WEBVIEW', url=pathHTML)


class DataSourceManager(QObject):

    """
    Keeps overview on different data sources handled by EnMAP-Box.
    Similar like QGIS data registry, but manages non-spatial data sources (text files etc.) as well.
    """

    sigDataSourceAdded = pyqtSignal(DataSource)
    sigDataSourceRemoved = pyqtSignal(DataSource)

    def __init__(self, enmapBoxInstance):
        super(DataSourceManager, self).__init__()
        from enmapbox.gui.enmapboxgui import EnMAPBox
        assert isinstance(enmapBoxInstance, EnMAPBox)
        self.enmapbox = enmapBoxInstance
        self.sources = set()

        QgsMapLayerRegistry.instance().layersAdded.connect(self.updateFromQgsMapLayerRegistry)
        self.updateFromQgsMapLayerRegistry()

        #signals
        self.processing = None
        try:
            import enmapbox.processing
            self.processing = enmapbox.processing
            self.processing.sigFileCreated.connect(lambda file: self.addSource(file))
        except:
            pass
        self.updateFromProcessingFramework()


    def updateFromProcessingFramework(self):
        if self.processing:
            import logging
            logging.debug('Todo: Fix processing implementation')
            return
            for p,n in zip(self.processing.MODEL_URIS,
                           self.processing.MODEL_NAMES):
                self.addSource(p, name=n)

    def updateFromQgsMapLayerRegistry(self, mapLayers=None):
        """
        Add data sources registered in the QgsMapLayerRegistry to the data source manager
        :return: True, if a new source was added
        """
        if mapLayers is None:
            mapLayers = QgsMapLayerRegistry.instance().mapLayers().values()

        for lyr in mapLayers:
            self.addSource(lyr)

    def getUriList(self, sourcetype='All'):
        """
        Returns URIs of registered data sources
        :param sourcetype: uri filter: 'ALL' (default),'RASTER''VECTOR' or 'MODEL' to return only uri's related to these sources
        :return: uri as string (str), e.g. a file path
        """
        sourcetype = sourcetype.upper()
        if isinstance(sourcetype, type):
            return [ds.getUri() for ds in self.sources if type(ds) is sourcetype]

        assert sourcetype in ['ALL','RASTER''VECTOR','MODEL']
        if sourcetype == 'ALL':
            return [ds.getUri() for ds in self.sources]
        elif sourcetype == 'VECTOR':
            return [ds.getUri() for ds in self.sources if isinstance(ds, DataSourceVector)]
        elif sourcetype == 'RASTER':
            return [ds.getUri() for ds in self.sources if isinstance(ds, DataSourceVector)]
        elif sourcetype == 'MODEL':
            return [ds.getUri() for ds in self.sources if isinstance(ds, ProcessingTypeDataSource)]



    @pyqtSlot(str)
    @pyqtSlot('QString')
    def addSource(self, src, name=None, icon=None):
        """
        Adds a new data source.
        :param src: any object
        :param name:
        :param icon:
        :return: a DataSource instance, if successfully added
        """
        ds = DataSourceFactory.Factory(src, name=name, icon=icon)


        if isinstance(ds, DataSource):
            # check if source is already registered
            for src in self.sources:
                logger.debug(str(ds.uri))
                if os.path.abspath(src.uri) == os.path.abspath(ds.uri):
                    return src #return object reference of an already existing source

            self.sources.add(ds)
            self.sigDataSourceAdded.emit(ds)

        return ds

    def removeSources(self, dataSourceList):
        for dataSource in dataSourceList:
            self.removeSource(dataSource)

    def removeSource(self, dataSource):
        assert isinstance(dataSource, DataSource)
        if dataSource in self.sources:
            self.sources.remove(dataSource)
            self.sigDataSourceRemoved.emit(dataSource)
        else:
            logger.debug('can not remove {}'.format(dataSource))

    def getSourceTypes(self):
        return sorted(list(set([type(ds) for ds in self.sources])))


