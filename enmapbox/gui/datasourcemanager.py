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
from __future__ import absolute_import, unicode_literals
import sys, os, logging
logger = logging.getLogger(__name__)
from qgis.core import *
from qgis.gui import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from enmapbox.gui.utils import PanelWidgetBase, loadUI
from osgeo import gdal, ogr
from enmapbox.gui.treeviews import *
from enmapbox.gui.datasources import *
from enmapbox.gui.utils import *


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
            ext = dataSource.spatialExtent
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

    def __init__(self, parent, dataSource):

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
        else:
            self.mSrcSize = -1
        self.nodeSize = TreeNode(self, 'Size', value=fileSizeString(self.mSrcSize))

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
        dataSource = DataSourceFactory.Factory(cp.value('uri'), name=element.attribute('name'))
        node = DataSourceTreeNode(None, dataSource)
        TreeNode.attachCommonPropertiesFromXML(node, element)

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
        ext = dataSource.spatialExtent
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

    def connectDataSource(self, dataSource):
        assert isinstance(dataSource, DataSourceVector)
        super(VectorDataSourceTreeNode, self).connectDataSource(dataSource)

        lyr = self.dataSource.createUnregisteredMapLayer()
        nFeat = lyr.featureCount()
        nFields = lyr.fields().count()

        geomType = ['Point','Line','Polygon','Unknown','Null'][lyr.geometryType()]
        wkbType = QgsWKBTypes.displayString(int(lyr.wkbType()))
        self.nodeSize.setValue('{} x {}'.format(nFeat, fileSizeString(self.mSrcSize)))
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

        mu = QgsUnitTypes.toString(dataSource.spatialExtent.crs().mapUnits())


        self.nodeExtXpx = TreeNode(self.nodeSize, 'Samples',
                                   tooltip='Data Source Width in Pixel',
                                   value='{} px'.format(dataSource.nSamples))
        self.nodeExtYpx = TreeNode(self.nodeSize, 'Lines',
                                   tooltip='Data Source Height in Pixel',
                                   value='{} px'.format(dataSource.nLines))

        self.nodePxSize = TreeNode(self.nodeSize, 'Pixel',
                                   tooltip='Spatial size of single pixel',
                                   value='{} {} x {} {}'.format(dataSource.pxSizeX, mu, dataSource.pxSizeY, mu))

        self.nodeSize.setValue('{}x{}x{}'.format(dataSource.nSamples,
                                                 dataSource.nLines,
                                                 dataSource.nBands))

        self.nodeBands = TreeNode(self, 'Bands',
                                  tooltip='Number of Raster Bands',
                                  value='{}'.format(dataSource.nBands))


        ds = gdal.Open(dataSource.uri())



        for b in range(ds.RasterCount):
            band = ds.GetRasterBand(b+1)
            assert isinstance(band, gdal.Band)
            if b == 0:

                if band.GetCategoryNames() is not None:
                    self.setIcon(QIcon(':/enmapbox/icons/filelist_classification.png'))
                elif ds.RasterCount == 1 and band.DataType == gdal.GDT_Byte:
                    self.setIcon(QIcon(':/enmapbox/icons/filelist_mask.png'))
                else:
                    self.setIcon(QIcon(':/enmapbox/icons/filelist_image.png'))

            name = band.GetDescription()

            if len(name) == 0:
                name = ''
            bandNode = RasterBandTreeNode(dataSource, b, self.nodeBands, 'Band {}'.format(b+1), value=name)


        ds = None



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
        self.mSpeclib = speclib
        assert isinstance(self.mSpeclib, SpectralLibrary)


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

        from enmapbox.gui.spectrallibraries import SpectralLibrary, SpectralProfile

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

        self.flowObject = self.dataSource.flowObject()

        objects = set()

        def fetchInternals(parent, obj, objects):
            assert isinstance(parent, TreeNode)
            if id(obj) in objects:
                return
            else:
                objects.add(id(obj))

            if isinstance(obj, hubflow.types.ClassDefinition):
                from enmapbox.gui.classificationscheme import ClassificationScheme, ClassInfo
                csi = ClassificationScheme()
                colors = np.asarray(obj.lookup).reshape((obj.classes,3))
                for label in range(obj.classes):
                    ci = ClassInfo(label=label, name=obj.names[label], color=QColor(*colors[label,:]))
                    csi.addClass(ci)
                ClassificationNode(parent, csi, name='ClassDefinition')

            elif isinstance(obj, dict):
                for k, i in obj.items():
                    name = str(k)
                    if name.startswith('_'):
                        continue
                    node = TreeNode(parent, name)
                    if isinstance(i, list) or \
                        isinstance(i, set):
                        node.setValue(str(len(i)))
                        fetchInternals(node, i, objects)
                    elif isinstance(i, np.ndarray):
                        text = '{} {} {}...'.format(i.shape, i.dtype, re.split('[\n]', str(i))[0])
                        node.setValue(text)
                    else:
                        fetchInternals(node, i, objects)

            elif isinstance(obj, list) or isinstance(obj, set):
                for i, item in enumerate(obj):
                    node = TreeNode(parent, str(i))
                    if isinstance(item, hubflow.types.FlowObject) or \
                       isinstance(item, dict) or \
                       isinstance(item, list):
                        fetchInternals(node, item, objects)
                    else:
                        text = str(item)
                        node.setValue(text.replace('\n',' '))
                    if i > 100:
                        break
            elif isinstance(obj, hubflow.types.FlowObject):
                parent.setName(obj.__class__.__name__)
                fetchInternals(parent, obj.__dict__, objects)
            else:
                parent.setValue(str(obj))


        if isinstance(self.flowObject, hubflow.types.FlowObject):

            self.setValue(self.flowObject.__class__.__name__)
            #todo: type specific icon

            fetchInternals(self, self.flowObject.__dict__, objects)




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
        self.dataSourceTreeView.setMenuProvider(DataSourceManagerTreeModelMenuProvider(self.dataSourceTreeView))


LUT_DATASOURCTYPES = collections.OrderedDict()
LUT_DATASOURCTYPES[DataSourceRaster] = ('Raster Data', QIcon(':/enmapbox/icons/mIconRasterLayer.png'))
LUT_DATASOURCTYPES[DataSourceVector] = ('Vector Data', QIcon(':/enmapbox/icons/mIconLineLayer.png'))
LUT_DATASOURCTYPES[HubFlowDataSource] = ('Models', QIcon(':/enmapbox/icons/alg.png'))
LUT_DATASOURCTYPES[DataSourceSpectralLibrary] = ('Spectral Libraries',QIcon(':/enmapbox/icons/speclib.png'))
LUT_DATASOURCTYPES[DataSourceFile] = ('Other Files',QIcon(':/trolltech/styles/commonstyle/images/file-128.png'))
LUT_DATASOURCTYPES[DataSource] = ('Other sources',QIcon(':/trolltech/styles/commonstyle/images/standardbutton-open-32.png'))


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

        for ds in self.dataSourceManager.mSources:
            self.addDataSource(ds)

    def columnCount(self, index):
        return 2



    def mimeTypes(self):
        # specifies the mime types handled by this model
        types = []
        types.append(MimeDataHelper.MDF_DATASOURCETREEMODELDATA)
        types.append(MimeDataHelper.MDF_LAYERTREEMODELDATA)
        types.append(MimeDataHelper.MDF_URILIST)
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

            # add new data from external sources
            elif data.hasFormat('text/uri-list'):
                for url in data.urls():
                    self.dataSourceManager.addSource(url)

            # add data dragged from QGIS
            elif data.hasFormat("application/qgis.layertreemodeldata"):
                result = QgsLayerTreeModel.dropMimeData(self, data, action, row, column, parent)

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
        exportedNodes = []
        pythonObjects = []
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

        doc = QDomDocument()
        uriList = list()
        rootElem = doc.createElement("datasource_tree_model_data");
        for node in exportedNodes:
            node.writeXML(rootElem)
            uriList.append(QUrl(node.dataSource.uri()))

        #set application/enmapbox.datasourcetreemodeldata
        doc.appendChild(rootElem)
        txt = doc.toString()
        mimeData.setData("application/enmapbox.datasourcetreemodeldata", QByteArray(txt.encode('utf-8')))

        specLibNodes = [n for n in exportedNodes if isinstance(n, SpeclibDataSourceTreeNode)]
        if len(specLibNodes) > 0:
            from enmapbox.gui.spectrallibraries import SpectralLibrary
            sl = SpectralLibrary()
            for node in specLibNodes:
                slib = SpectralLibrary.readFrom(node.dataSource.uri())
                sl.addSpeclib(slib)

            if len(sl) > 0:
                mimeData.setData(MimeDataHelper.MDF_SPECTRALLIBRARY, sl.asPickleDump())
                pythonObjects.append(sl)

        if len(pythonObjects) > 0:
            MimeDataHelper.setObjectReferences(mimeData, pythonObjects)

        # set text/uri-list
        if len(uriList) > 0:
            mimeData.setUrls(uriList)
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



    def addDataSource(self, dataSource):
        assert isinstance(dataSource, DataSource)
        dataSourceNode = TreeNodeProvider.CreateNodeFromDataSource(dataSource, None)
        sourceGroup = self.getSourceGroup(dataSource)
        sourceGroup.addChildNode(dataSourceNode)
        dataSourceNode.setExpanded(True)
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
            return Qt.NoItemFlags

        # specify TreeNode specific actions
        node = self.index2node(index)
        column = index.column()
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable

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
                a.triggered.connect(lambda : model.dataSourceManager.removeSource(src))
                a = m.addAction('Copy URI / path')
                a.triggered.connect(lambda: QApplication.clipboard().setText(src.uri()))
                a = m.addAction('Rename')
                a.setEnabled(False)
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
                    assert isinstance(rgb, list)
                    if len(rgb) == 3:
                        if isinstance(r, QgsMultiBandColorRenderer):
                            r.setRedBand(rgb[0])
                            r.setGreenBand(rgb[1])
                            r.setBlueBand(rgb[2])
                        if isinstance(r, QgsSingleBandGrayRenderer):
                            r.setGrayBand(rgb[0])

                    elif len(rgb) == 1:

                        if isinstance(r, QgsMultiBandColorRenderer):
                            r.setRedBand(rgb[0])
                            r.setGreenBand(rgb[0])
                            r.setBlueBand(rgb[0])
                        if isinstance(r, QgsSingleBandGrayRenderer):
                            r.setGrayBand(rgb[0])

            elif isinstance(lyr, QgsVectorLayer):

                pass

            dock.setLayers([lyr])


    def onSaveAs(self, dataSource):

        pass

class DataSourceManager(QObject):

    """
    Keeps overview on different data sources handled by EnMAP-Box.
    Similar like QGIS data registry, but manages non-spatial data sources (text files etc.) as well.
    """

    sigDataSourceAdded = pyqtSignal(DataSource)
    sigDataSourceRemoved = pyqtSignal(DataSource)

    SOURCE_TYPES = ['ALL','ANY', 'RASTER', 'VECTOR', 'MODEL']

    def __init__(self):
        super(DataSourceManager, self).__init__()

        self.mSources = list()
        self.mSubsetSelection = {}
        self.mQgsLayerTreeGroup = None
        #self.qgsLayerTreeGroup()

        #todo: react on QgsMapLayerRegistry changes, e.g. when project is closed
        #QgsMapLayerRegistry.instance().layersAdded.connect(self.updateFromQgsMapLayerRegistry)
        # noinspection PyArgumentList
        from qgis.core import QgsMapLayerRegistry
        QgsMapLayerRegistry.instance().layersAdded.connect(self.onMapLayerRegistryLayersAdded)
        QgsMapLayerRegistry.instance().removeAll.connect(self.removeSources)
        try:
            from hubflow import signals
            signals.sigFileCreated.connect(self.addSource)
        except Exception as ex:
            logger.exception(ex)

        self.updateFromQgsMapLayerRegistry()


    def qgsLayerTreeGroup(self):
        return None
        if not isinstance(self.mQgsLayerTreeGroup,QgsLayerTreeGroup):
            self.mQgsLayerTreeGroup = QgsLayerTreeGroup('EnMAPBox Sources', False)
            QgsProject.instance().layerTreeRoot().addChildNode(self.mQgsLayerTreeGroup)
        return self.mQgsLayerTreeGroup

    def __len__(self):
        return len(self.mSources)

    def sources(self, sourceTypes=None):
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
            #import logging
            #logging.debug('Todo: Fix processing implementation')
            return
            for p,n in zip(self.processing.MODEL_URIS,
                           self.processing.MODEL_NAMES):
                self.addSource(p, name=n)

    def updateFromQgsMapLayerRegistry(self, mapLayers=None):
        """
        Add data sources registered in the QgsMapLayerRegistry to the data source manager
        :return: List of added new DataSources
        """
        if mapLayers is None:
            mapLayers = QgsMapLayerRegistry.instance().mapLayers().values()

        added = [self.addSource(lyr) for lyr in mapLayers]
        return [a for a in added if isinstance(a, DataSource)]


    def getUriList(self, sourcetype='All'):
        """
        Returns URIs of registered data sources
        :param sourcetype: uri filter: 'ALL' (default),'RASTER''VECTOR' or 'MODEL' to return only uri's related to these sources
        :return: uri as string (str), e.g. a file path
        """
        sourcetype = sourcetype.upper()
        if isinstance(sourcetype, type):
            return [ds.uri() for ds in self.mSources if type(ds) is sourcetype]

        assert sourcetype in DataSourceManager.SOURCE_TYPES
        if sourcetype == ['ALL','ANY']:
            return [ds.uri() for ds in self.mSources]
        elif sourcetype == 'VECTOR':
            return [ds.uri() for ds in self.mSources if isinstance(ds, DataSourceVector)]
        elif sourcetype == 'RASTER':
            return [ds.uri() for ds in self.mSources if isinstance(ds, DataSourceRaster)]
        elif sourcetype == 'MODEL':
            return [ds.uri() for ds in self.mSources if isinstance(ds, HubFlowDataSource)]
        else:
            return []

    def onMapLayerRegistryLayersAdded(self, lyrs):
        #remove layers that should not be added automatically
        lyrsToAdd = []
        for lyr in lyrs:
            if isinstance(lyr, QgsVectorLayer):
                if lyr.dataProvider().dataSourceUri().startswith('memory?'):
                    continue
            lyrsToAdd.append(lyr)

        self.addSources(lyrsToAdd)



    def addSources(self, sources):
        added = []
        for s in sources:
            added.append(self.addSource(s))
        added = [a for a in added if isinstance(a, DataSource)]
        self.mSubsetSelection.clear()
        return added

    @pyqtSlot(unicode)
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

            for src in self.mSources:
                assert isinstance(src, DataSource)
                if ds.isSameSource(src):
                    if isinstance(ds, DataSourceFile):
                        if ds.isNewVersionOf(src):
                            #remove old version
                            self.removeSource(src)
                        else:
                            return src #return object reference of an already existing source
                    else:
                        return src #return object reference of an already existing source
            #this datasource is new
            self.mSources.append(ds)
            self.sigDataSourceAdded.emit(ds)

        return ds

    def clear(self):
        """
        Removes all data source from DataSourceManager
        :return: [list-of-removed-DataSources]
        """
        return self.removeSources(list(self.mSources))


    def removeSources(self, dataSourceList):
        """
        Removes a list of data sources.
        :param dataSourceList: [list-of-datasources]
        :return: self
        """
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
            logger.debug('can not remove {}'.format(dataSource))


    def sourceTypes(self):
        """
        Returns the list of source-types handled by this DataSourceManage
        :return: [list-of-source-types]
        """
        return sorted(list(set([type(ds) for ds in self.mSources])))


