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

class DataSourcePanelUI(PanelWidgetBase, loadUI('datasourcepanel.ui')):
    def __init__(self, parent=None):
        super(DataSourcePanelUI, self).__init__(parent)
        self.dataSourceManager = None
        assert isinstance(self.dataSourceTreeView, TreeView)

    def connectDataSourceManager(self, dataSourceManager):
        assert isinstance(dataSourceManager, DataSourceManager)
        self.dataSourceManager = dataSourceManager
        self.dataSourceTreeView.setModel(DataSourceManagerTreeModel(self, self.dataSourceManager))
        self.dataSourceTreeView.setMenuProvider(TreeViewMenuProvider(self.dataSourceTreeView))


class DataSourceManagerTreeModel(TreeModel):

    def __init__(self, parent, dataSourceManager):

        super(DataSourceManagerTreeModel, self).__init__(parent)
        assert isinstance(dataSourceManager, DataSourceManager)
        self.dataSourceManager = dataSourceManager
        self.dataSourceManager.sigDataSourceAdded.connect(self.addDataSource)
        self.dataSourceManager.sigDataSourceRemoved.connect(self.removeDataSource)

        for ds in self.dataSourceManager.sources:
            self.addDataSource(ds)

    def mimeTypes(self):
        # specifies the mime types handled by this model
        types = []
        types.append("text/uri-list")
        types.append("application/qgis.layertreemodeldata")
        types.append("application/enmapbox.datasourcetreemodeldata")
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

        return mimeData

    def getSourceGroup(self, dataSource):
        """Returns the source group relate to a data source"""
        assert isinstance(dataSource, DataSource)

        groups = [(DataSourceRaster, 'Raster Data'),
                  (DataSourceVector, 'Vector Data'),
                  (DataSourceModel, 'Models'),
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

    def removeDataSource(self, dataSource):
        assert isinstance(dataSource, DataSource)
        sourceGroup = self.getSourceGroup(dataSource)
        to_remove = [c for c in sourceGroup.children() if c.source == dataSource]
        if len(to_remove) > 0:
            sourceGroup.removeChildNodes(to_remove)

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        # specify TreeNode specific actions
        node = self.index2node(index)
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable

        if isinstance(node, DataSourceGroupTreeNode):
            flags |= Qt.ItemIsDropEnabled
        elif isinstance(node, DataSourceTreeNode):
            flags |= Qt.ItemIsDragEnabled
        else:
            flags = Qt.NoItemFlags
        return flags

    def contextMenu(self, node):
        menu = QMenu()
        #todo: add node specific menu actions
        return menu


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
            return [ds.getUri() for ds in self.sources if isinstance(ds, DataSourceModel)]



    @pyqtSlot(str)
    @pyqtSlot('QString')
    def addSource(self, src, name=None, icon=None):
        """
        Adds a new data source.
        :param src: any object
        :param name:
        :param icon:
        :return: a DataSource instance, if sucessfully added
        """
        ds = DataSourceFactory.Factory(src, name=name, icon=icon)


        if isinstance(ds, DataSource):
            # check if source is already registered
            for src in self.sources:
                if os.path.abspath(src.uri) == os.path.abspath(ds.uri):
                    return src #return object reference of an already existing source

            self.sources.add(ds)
            self.sigDataSourceAdded.emit(ds)

            if isinstance(ds, DataSourceModel):
                enmapbox.processing.registerModel(ds.uri)

        return ds

    def removeSource(self, src):
        assert isinstance(src, DataSource)
        if src in self.sources:
            self.sources.remove(src)
            self.sigDataSourceRemoved.emit(src)
        else:
            logger.debug('can not remove {}'.format(src))

    def getSourceTypes(self):
        return sorted(list(set([type(ds) for ds in self.sources])))


