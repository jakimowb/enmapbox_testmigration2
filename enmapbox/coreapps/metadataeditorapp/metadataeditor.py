# -*- coding: utf-8 -*-

"""
***************************************************************************
    exampleapp/userinterfaces.py

    Some exemplary (graphical) user interfaces, making use of the Qt framework.
    ---------------------
    Date                 : Juli 2017
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


import sys, os, pathlib
from enmapbox.gui import *
from enmapbox.gui.utils import loadUIFormClass, guessDataProvider
from metadataeditorapp.metadatakeys import *
from osgeo import gdal, ogr, osr



from metadataeditorapp import APP_DIR

#path to the *.ui file that was created/edited in the QDesigner
pathUi = os.path.join(APP_DIR, 'metadataeditor.ui')

DEFAULT_DOMAIN = '<default>'

IMMUTABLE_DOMAINS = ['IMAGE_STRUCTURE', 'SUBDATASETS', 'DERIVED_SUBDATASETS']

ALL_IMMUTABLE = 'all_immutable'

MD_DOMAIN_INFO = {}
MD_DOMAIN_INFO[''] = 'This is the default metadata domain.'
MD_DOMAIN_INFO['IMAGE_STRUCTURE'] = 'Information of interest closely tied to the particular file format and storage mechanism.'
MD_DOMAIN_INFO['ENVI'] = 'The ENVI Metdata domain. See see http://www.harrisgeospatial.com/docs/enviheaderfiles.html for details.'
MD_DOMAIN_INFO['SUBDATASETS'] = 'The SUBDATASETS domain holds a list of child datasets. Normally this is used to provide pointers to a list of images stored within a single multi image file.'
MD_DOMAIN_INFO['RPC'] = 'Metadata describing the Rational Polynomial Coefficient geometry model for the image'
MD_DOMAIN_INFO['IMAGERY'] = 'Specific information for satellite or aerial imagery.'



class MetadataItemTreeNode(TreeNode):
    """
    TreeNode that described a single metadata item.
    """
    def __init__(self, parentNode:TreeNode, layerBandIndex:int, domain:str=None, isImmutable=False, **kwds):
        super(MetadataItemTreeNode, self).__init__(parentNode, **kwds)
        self.mLayerBandIndex = layerBandIndex
        self.mDomain = domain
        self.mToDelete = False
        self.mToCreate = False
        self.mIsImmutable = isImmutable
        self.mInitialValue = kwds.get('value')
        self.setValue(self.mInitialValue)
        self.mDataType = type(self.mInitialValue)

    def resetValue(self, *args):
        """
        Resets the value
        """
        self.setValue(self.mInitialValue)

    def layerBandIndex(self)->int:
        """
        Returns the vector layer or raster band index or None, if the metadata
        is linked to the top-level object (gdal.Dataset | ogr.DataSource)
        :return: int
        """
        return self.mLayerBandIndex

    def domain(self)->str:
        """
        Returns the metadata domain
        :return: str
        """
        return self.mDomain

    def isModified(self)->bool:
        """
        Returns True if the value got modified
        :return:
        """
        return self.mToDelete or self.mToCreate or self.mInitialValue != self.value()

    def setToDelete(self, b:bool):
        """
        :param b:
        :return:
        """
        assert isinstance(b, bool)
        if self.mToDelete != b:
            self.mToDelete = b
            self.sigUpdated.emit(self)


    def isToDelete(self)->bool:
        """
        Returns whether this metadata item is to be deleted.
        :return: bool
        """
        return self.mToDelete


    def isImmutable(self)->bool:
        """
        Returns True if the value can not be changed
        :return: bool
        """
        return self.mIsImmutable

    def setValue(self, value):
        if hasattr(self, 'mIsImmutable'):
            if not self.mIsImmutable:
                super(MetadataItemTreeNode, self).setValue(value)
        else:
            super(MetadataItemTreeNode, self).setValue(value)

class MetadataClassificationSchemeTreeNode(MetadataItemTreeNode):

    def __init__(self, parentNode, dataSet, *args, **kwds):
        kwds['name'] = kwds.get('name', 'Classification')
        kwds['icon'] = kwds.get('icon', QIcon(r':/qps/ui/icons/classinfo.svg'))

        super(MetadataClassificationSchemeTreeNode, self).__init__(parentNode, *args, **kwds)
        self.updateNode()

    def classificationScheme(self)->ClassificationScheme:
        """
        Returns the ClassificationScheme
        :return: ClassificationScheme
        """
        cs = self.value()
        if isinstance(cs, ClassificationScheme):
            return cs
        else:
            return None

    def setClassificationScheme(self, cs:ClassificationScheme):
        """
        Sets the ClassificationScheme
        :param cs:  ClassificationScheme
        """
        self.setValue(cs)

    def setValue(self, value):
        super(MetadataClassificationSchemeTreeNode, self).setValue(value)
        self.updateNode()

    def updateNode(self, *args):
        l = len(self.childNodes())
        self.removeChildNodes(0, l)

        cs = self.classificationScheme()
        if isinstance(cs, ClassificationScheme):
            for i, classInfo in enumerate(cs):
                assert isinstance(classInfo, ClassInfo)
                TreeNode(self,name='Class {}'.format(classInfo.label()), values=classInfo.name() , icon=classInfo.icon())


class MetadataItemCRSTreeNode(MetadataItemTreeNode):

    def __init__(self, parentNode, *args, **kwds):

        kwds['name'] = kwds.get('name', 'CRS')
        kwds['toolTip'] = kwds.get('toolTip', 'Coordinate Reference System')
        kwds['icon'] = kwds.get('icon', QIcon(r':/images/themes/default/propertyicons/CRS.svg'))
        kwds['value'] = kwds.get('value', kwds.get('crs'))
        super(MetadataItemCRSTreeNode, self).__init__(parentNode, *args, domain=None, **kwds)


    def setValue(self, value:QgsCoordinateReferenceSystem):
        super(MetadataItemCRSTreeNode, self).setValue(value)

        self.removeChildNodes(0, self.childCount())
        crs = self.crs()
        if isinstance(crs, QgsCoordinateReferenceSystem):
            TreeNode(self, 'Description', value=crs.description())
            TreeNode(self, 'WKT', value=crs.toWkt())
            TreeNode(self, 'Ellipsoid', values=crs.ellipsoidAcronym())


    def setCrs(self,crs:QgsCoordinateReferenceSystem):
        self.setValue(crs)

    def crs(self)->QgsCoordinateReferenceSystem:
        crs = self.value()
        if isinstance(crs, QgsCoordinateReferenceSystem):
            return crs
        else:
            return None

    def value(self)->QgsCoordinateReferenceSystem:
        crs = super(MetadataItemCRSTreeNode, self).value()
        if not isinstance(crs, QgsCoordinateReferenceSystem):
            return None
        return crs


class RasterBandTreeNode(MetadataItemTreeNode):

    def __init__(self, parentNode, band, **kwds):
        assert isinstance(band, gdal.Band)

        bandIndex = band.GetBand() - 1
        kwds['name'] = kwds.get('name', 'Band {}'.format(band.GetBand()))
        kwds['value'] = bandIndex
        kwds['icon'] = kwds.get('icon', QIcon(r':/images/themes/default/mIconRasterLayer.svg'))
        kwds['value'] = band.GetDescription()
        super(RasterBandTreeNode, self).__init__(parentNode, layerBandIndex=bandIndex, **kwds)

        self.mBandIndex = bandIndex

    def bandIndex(self)->int:
        """Returns the band index"""
        return self.mBandIndex

    def description(self)->str:
        """
        Returns the band description
        :return: str
        """
        return self.value()

    def setDescription(self, description:str):
        """Sets the band description."""
        self.setValue(description)

class VectorLayerTreeNode(MetadataItemTreeNode):

    def __init__(self, parentNode, layer, layerIndex, **kwds):
        assert isinstance(layer, ogr.Layer)
        kwds['icon'] = kwds.get('icon', layerIcon(layer))
        kwds['name'] = kwds.get('name', 'Layer {}'.format(layerIndex + 1))
        kwds['value'] = kwds.get('value', layer.GetDescription())
        kwds['isImmutable'] = True # no way to change a layer name :-(
        super(VectorLayerTreeNode, self).__init__(parentNode, layerIndex, **kwds)
        self.mLayerIndex = layerIndex


    def layerIndex(self)->int:
        """Returns the layer index"""
        return self.mLayerIndex

class RasterSourceTreeNode(TreeNode):

    def __init__(self, parentNode, dataSet, **kwds):
        assert isinstance(dataSet, gdal.Dataset)
        kwds['icon'] = kwds.get('icon', QIcon(r':/images/themes/default/mIconRaster.svg'))
        super(RasterSourceTreeNode, self).__init__(parentNode, **kwds)
        self.mSource = dataSet.GetFileList()[0]
        self.mDriver = dataSet.GetDriver()


class VectorSourceTreeNode(TreeNode):

    def __init__(self, parentNode, dataSource, **kwds):
        assert isinstance(dataSource, ogr.DataSource)

        kwds['name'] = kwds.get('name', os.path.basename(dataSource.GetDescription()))

        icon = None
        for layer in dataSource:
            icon = layerIcon(layer)
            break

        kwds['icon'] = kwds.get('icon', icon)
        super(VectorSourceTreeNode, self).__init__(parentNode, **kwds)
        self.mSource = dataSource.GetDescription()
        self.mDriver = dataSource.GetDriver()

def layerIcon(layer:ogr.Layer)->QIcon:
    """
    Returns an icon according to a layer's geometry type
    :param layer: ogr.Layer
    :return: QIcon
    """
    geomType = ogr.GeometryTypeToName(layer.GetGeomType())
    if re.search('point', geomType, re.I):
        return QIcon(r':/images/themes/default/mIconPointLayer.svg')
    elif re.search('line', geomType, re.I):
        return QIcon(r':/images/themes/default/mIconLineLayer.svg')
    return QIcon(r':/images/themes/default/mIconVector.svg')



class MetadataDomainTreeNode(TreeNode):

    def __init__(self, parentNode, domain, *args, **kwds ):
        assert isinstance(domain, str)
        nodeName = domain if domain != '' else DEFAULT_DOMAIN
        kwds['name'] = nodeName
        super(MetadataDomainTreeNode, self).__init__(parentNode, *args, **kwds)
        self.mDomain = domain

        if self.mToolTip is None and self.mDomain in MD_DOMAIN_INFO.keys():
            self.setToolTip(MD_DOMAIN_INFO[self.mDomain])

        #self.sigAddedChildren.connect(self.update)
        #self.sigRemovedChildren.connect(self.update)
        #self.update()

    #def update(self):
#
    #    n = self.childCount()
    #    if n == 0:
    #        self.setValues('not metadata items')
    #    else:
    #        self.setValues('{} metadata items'.format(n))



class MetadataDomainModel(OptionListModel):

    def __init__(self, *args, **kwds):
        super(MetadataDomainModel, self).__init__( *args, **kwds)


    def addDomain(self, domainName):

        if domainName == '':
            domainName = DEFAULT_DOMAIN
            tooltip = 'Default Metadata domain'
        else:
            tooltip = 'Metadata domain "{}"'.format(domainName)
        d = Option(domainName, domainName, toolTip=tooltip)
        self.addOption(d)


    def domains(self):
        return [o.value for o in self.options()]




class MetadataTreeModel(TreeModel):

    def __init__(self, parent=None):
        super(MetadataTreeModel, self).__init__(parent)

        self.cnKey = 'Key'
        self.cnDomain = 'Domain'
        self.cnValue = 'Value'
        self.mSource = None

        self.mDomains = MetadataDomainModel()
        self.mRootNode0 = None

        self.mColumnNames.clear()
        self.mColumnNames.extend([self.cnKey, self.cnValue, self.cnDomain])

    def domainModel(self):
        return self.mDomains



    def differences(self, node)->list:
        """
        Returns MetadataItemTreeNode with changed values, new MetadataItemTreeNode or 
        MetadataItemTreeNode to be deleted.
        :param node: TreeNode, by default the models rootNode
        :return: [list-of-changed-MetadataItemTreeNodes]
        """

        if node is None:
            node = self.mRootNode

        assert isinstance(node, TreeNode)

        changedNodes = []
        if isinstance(node, MetadataItemTreeNode):
            if node.isModified() and not node.isImmutable():
                changedNodes.append(node)

        for childNode in node.childNodes():
            changedNodes += self.differences(childNode)
        return changedNodes

    def parseSource(self, path: str):
        #print('PARSE {}'.format(path))
        # clear metadata domains
        self.mDomains.clear()

        ds = self.openSource(path)

        if isinstance(ds, gdal.Dataset):
            return self.parseRasterMD(ds)
        if isinstance(ds, ogr.DataSource):
            return self.parseVectorMD(ds)

        return [TreeNode(None, path, values=['unable to read metadata'])]


    def openSource(self, path:str, update=False):
        """
        Adds a data source
        :param path: uri of data source
        """

        assert isinstance(path, str)

        order = ['gdal', 'ogr']
        if re.search(r'(shp|gpkg|kml|kmz)$', path):
            order = ['ogr', 'gdal']
        for t in order:
            try:
                GA = gdal.GA_Update if update else gdal.GA_ReadOnly
                if t == 'gdal':

                    ds = gdal.Open(path, GA)
                    if isinstance(ds, gdal.Dataset):
                        return ds
                elif t == 'ogr':

                    ds = ogr.Open(path, GA)
                    if isinstance(ds, ogr.DataSource):
                        return ds
            except Exception as ex:
                raise ex
        return None

    def parseDomainMetadata(self, parentNode:TreeNode, obj, layerBandIndex:int):
        assert isinstance(parentNode, TreeNode)
        assert isinstance(obj, (gdal.MajorObject, ogr.MajorObject))
        domains = obj.GetMetadataDomainList()

        if domains is None:
            domains = []
        for domain in sorted(domains):
            self.mDomains.addDomain(domain)

            md = obj.GetMetadata(domain=domain)
            if isinstance(md, dict):
                for name, value in md.items():
                    MetadataItemTreeNode(parentNode, layerBandIndex, domain, value=value, name=name)

    def parseRasterMD(self, ds: gdal.Dataset) -> TreeNode:
        """
        Reads a gdal.Dataset and returns a Tree of Medatadata
        :param ds:
        :return:
        """
        assert isinstance(ds, gdal.Dataset)
        root = TreeNode(None)

        files = ds.GetFileList()
        basename = os.path.basename(files[0])
        # nDS = RasterSourceTreeNode(root, name='Dataset', values=basename)

        nodes = []

        #nDS = RasterSourceTreeNode(root, ds,
        #                           name='Dataset',
        #                           toolTip='Raster Data Source.')

        nFiles = TreeNode(root, 'File(s)',
                          icon=QIcon(r':/images/themes/default/mActionFileNew.svg'),
                          values=len(files),
                          toolTip='Physical files related to this Raster Data Source.')
        for i, f in enumerate(files):
            TreeNode(nFiles, name='{}'.format(i + 1), values=os.path.basename(f))


        crs = QgsCoordinateReferenceSystem(ds.GetProjection())

        MetadataItemCRSTreeNode(root, 0, crs=crs)

        MetadataClassificationSchemeTreeNode(root, ds, 0, value=ClassificationScheme.fromRasterImage(ds))



        nGeneral = TreeNode(root, 'Metadata (Dataset)', icon=QIcon(r':/images/themes/default/propertyicons/editmetadata.svg'))
        self.parseDomainMetadata(nGeneral, ds, None)

        nBands = TreeNode(root, 'Metadata (Bands)', icon=QIcon(r':/images/themes/default/propertyicons/editmetadata.svg'))

        nb = ds.RasterCount

        formatString = r'Band {{:0{}}}'.format(len(str(nb)))

        for bandIndex in range(nb):
            band = ds.GetRasterBand(bandIndex + 1)
            assert isinstance(band, gdal.Band)
            name = formatString.format(bandIndex + 1)
            nBand = RasterBandTreeNode(nBands, band, name=name)
            self.parseDomainMetadata(nBand, band, bandIndex)

        return root

    def parseVectorMD(self, ds: ogr.DataSource) -> TreeNode:
        """
        Reads metadata from an ogr vector data set
        :param ds:
        :return:
        """
        assert isinstance(ds, ogr.DataSource)
        root = TreeNode(None)


        nFiles = TreeNode(root, 'File(s)', values=ds.GetName(), icon=QIcon(r':/images/themes/default/mActionFileNew.svg'))
        nGeneral = TreeNode(root, 'Metadata (Datasource)', icon=QIcon(r':/images/themes/default/propertyicons/editmetadata.svg'))
        self.parseDomainMetadata(nGeneral, ds, None)

        nLayers = TreeNode(root, 'Metadata (Layers)', icon=QIcon(r':/images/themes/default/propertyicons/editmetadata.svg'))

        for i in range(ds.GetLayerCount()):
            lyr = ds.GetLayerByIndex(i)
            assert isinstance(lyr, ogr.Layer)

            nodeLayer = VectorLayerTreeNode(nLayers, lyr, i)

            srs = lyr.GetSpatialRef()
            if isinstance(srs, osr.SpatialReference):
                crs = QgsCoordinateReferenceSystem(srs.ExportToWkt())
            else:
                crs = QgsCoordinateReferenceSystem('')

            nCRS = MetadataItemCRSTreeNode(nodeLayer,i, crs=crs, isImmutable=True)
            self.parseDomainMetadata(nodeLayer, lyr, i)

        return root

    def setSource(self, path:str):
        """
        Sets the source path
        :param path: str
        """
        assert isinstance(path, str)
        root = self.parseSource(path)
        self.mSource = path
        l = self.mRootNode.childCount()
        self.mRootNode.removeChildNodes(0, l)

        if isinstance(root, TreeNode):
            self.beginResetModel()
            self.mRootNode.blockSignals(True)
            self.mRootNode.appendChildNodes(root.childNodes())
            self.mRootNode.blockSignals(False)
            self.endResetModel()

    def setData(self, index:QModelIndex, value, role=Qt.EditRole):
        """

        :param index: QModelIndex
        :param value: any
        :param role:  Qt.ItemDataRole, default=Qt.EditRole
        :return:
        """
        if not index.isValid():
            return None
        if not role == Qt.EditRole:
            return None

        cName = self.idx2columnName(index)
        node = self.idx2node(index)

        if not isinstance(node, MetadataItemTreeNode):
            return False
        else:
            node.setValue(value)
            # key = node.metadataKey()
            # key.setValue(value)
            self.dataChanged.emit(index, index)
            return True

        return False

    def source(self)->str:
        """
        Returns the source uri
        :return: str
        """
        return self.mSource

    def flags(self, index:QModelIndex):

        cName = self.idx2columnName(index)

        node = index.internalPointer()
        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        if isinstance(node, MetadataItemTreeNode):
            if cName == self.cnValue:
                if node.isImmutable() == False \
                        and type(node) not in [MetadataClassificationSchemeTreeNode, MetadataItemCRSTreeNode]:
                    flags = flags | Qt.ItemIsEditable

        else:
            flags = super(MetadataTreeModel, self).flags(index)
        return flags

    def data(self, index, role):
        #return super(MetadataTreeModel, self).data(index, role)


        node = index.internalPointer()

        if role == Qt.UserRole:
            return node

        cName = self.columnNames()[index.column()]
        if isinstance(node, MetadataItemTreeNode):
            isEditable = not node.isImmutable()

            if cName == self.cnKey:
                if role == Qt.DisplayRole:
                    return node.name()

                if role == Qt.BackgroundColorRole:
                    if node.isToDelete():
                        return QBrush(QColor('red'))
                    else:
                        return super(MetadataTreeModel, self).data(index, role)
                if role == Qt.DecorationRole:
                    return super(MetadataTreeModel, self).data(index, role)

            if cName == self.cnDomain:
                if role == Qt.DisplayRole:
                    return node.domain()

            if cName == self.cnValue:
                if role == Qt.DisplayRole:

                    if isinstance(node, MetadataItemCRSTreeNode):
                        crs = node.crs()
                        if isinstance(crs, QgsCoordinateReferenceSystem):
                            return crs.description()
                        else:
                            return None

                    elif isinstance(node, MetadataClassificationSchemeTreeNode):
                        cs = node.classificationScheme()
                        if isinstance(cs, ClassificationScheme) and len(cs) > 0:
                            return '{} classes'.format(len(cs))
                        else:
                            return None
                    else:
                        return node.value()

                if role == Qt.EditRole:
                    return node.value()
                if role == Qt.FontRole:
                    font = QFont()
                    font.setItalic(isEditable)
                    return font
                elif role == Qt.BackgroundRole and isEditable:
                    return QBrush(QColor('yellow'))

        else: # other node types without a domain name
            if cName == self.cnDomain:
                return None
            if cName == self.cnValue:
                idx = self.index(index.row(), 1, parent=index.parent())
                return super(MetadataTreeModel, self).data(idx, role)
            if cName == self.cnKey:
                return super(MetadataTreeModel, self).data(index, role)
        return None

    def writeMetadata(self):
        """
        Write changes in Metadata
        :return:
        """
        differences = self.differences(self.mRootNode)

        if len(differences) > 0:
            ds = self.openSource(self.mSource, update=True)
            assert isinstance(ds, (gdal.Dataset, ogr.DataSource))
            bandIndices = set([n.layerBandIndex() for n in differences if isinstance(n, MetadataItemTreeNode)])
            for bandIndex in bandIndices:
                if bandIndex is None:
                    obj = ds
                else:
                    if isinstance(ds, gdal.Dataset):
                        obj = ds.GetRasterBand(bandIndex + 1)
                    elif isinstance(ds, ogr.DataSource):
                        obj = ds.GetLayerByIndex(bandIndex)

                for node in [n for n in differences if n.layerBandIndex() == bandIndex]:
                    assert isinstance(node, MetadataItemTreeNode)

                    if type(node) == MetadataItemTreeNode:
                        if node.isToDelete():
                            obj.SetMetadataItem(node.name(), None, node.domain())
                        else:
                            obj.SetMetadataItem(node.name(), str(node.value()), node.domain())
                    elif isinstance(node, MetadataClassificationSchemeTreeNode):
                        if isinstance(ds, gdal.Dataset) and isinstance(obj, gdal.Band):


                            cs = node.classificationScheme()

                            if isinstance(cs, ClassificationScheme) and not node.isToDelete():
                                cs.saveToRasterBand(obj)
                            else:
                                obj.SetCategoryNames([])
                                obj.SetColorTable(None)

                    elif isinstance(node, MetadataItemCRSTreeNode):
                        if isinstance(ds, gdal.Dataset):
                            ds.SetProjection(node.crs().toWkt())
                        elif isinstance(ds, ogr.DataSource) and isinstance(obj, ogr.Layer):
                            obj.GetGeometryColumn()

                    elif isinstance(node, RasterBandTreeNode) and isinstance(obj, gdal.Band):
                        obj.SetDescription(str(node.value()))

                    elif isinstance(node, VectorLayerTreeNode) and isinstance(obj, ogr.Layer):
                        obj.SetDescription(str(node.value()))
            ds.FlushCache()
            ds = None





class MetadataFilterModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(MetadataFilterModel, self).__init__(parent)

        self.setRecursiveFilteringEnabled(True)


    def mimeTypes(self):
        return self.sourceModel().mimeTypes()

    def dropMimeData(self, mimeData, action, row, col, parentIndex):
        return self.sourceModel().dropMimeData(mimeData, action, row, col, parentIndex)

    def supportedDropActions(self):
        return self.sourceModel().supportedDropActions()

    def filterAcceptsRow(self, sourceRow, sourceParent):

        reg = self.filterRegExp()
        if reg.isEmpty():
            return True
        else:


            idx = self.sourceModel().index(sourceRow, 0, parent=sourceParent)
            node = idx.internalPointer()

            if isinstance(node, TreeNode):
                #if node.childCount() == 0:
                values = [node.name()] + node.values()
                for value in values:
                    if reg.indexIn(str(value)) >= 0:
                        return True
                #else:
                #    for row in range(node.childCount()):
                #        if self.filterAcceptsRow(row, idx):
                #            return True
        return False

    def filterAcceptsColumn(self, sourceColumn, sourceParent):
        return sourceColumn in [0, 1]



class MetadataTreeViewWidgetDelegates(QStyledItemDelegate):
    """
    Provides special widgets to edit Metadata treeNodes
    """
    def __init__(self, treeView, parent=None):
        assert isinstance(treeView, QTreeView)
        super(MetadataTreeViewWidgetDelegates, self).__init__(parent=parent)
        self.mTreeView = treeView
        self.mTreeView.doubleClicked.connect(self.onDoubleClick)


    def model(self)->QAbstractItemModel:
        return self.mTreeView.model()

    def onDoubleClick(self, idx):
        node = self.model().data(idx, role=Qt.UserRole)

        if not isinstance(node, MetadataItemTreeNode):
            return
        if node.isImmutable():
            return

        if isinstance(node, MetadataClassificationSchemeTreeNode):
            self.onEditClassificationScheme(idx)

        if isinstance(node, MetadataItemCRSTreeNode):
            crs = node.crs()
            d = QgsProjectionSelectionDialog()
            if isinstance(crs, QgsCoordinateReferenceSystem):
                d.setCrs(crs)
            d.setMessage('Select the Coordinate Reference System')
            d.setShowNoProjection(True)
            if d.exec_() == QDialog.Accepted:
                self.model().setData(idx, d.crs())





    def onEditClassificationScheme(self, index:QModelIndex):

        node = self.model().data(index, role=Qt.UserRole)
        assert isinstance(node, MetadataClassificationSchemeTreeNode)

        value = node.classificationScheme()

        scheme = ClassificationSchemeDialog.getClassificationScheme(classificationScheme=value)
        if isinstance(scheme, ClassificationScheme):
            self.model().setData(index, scheme)


    def columnName(self, index:QModelIndex):
        return self.model().headerData(index.column(), Qt.Horizontal, role=Qt.DisplayRole)

    def createEditor(self, parent, option, index):

        w = None
        cname = self.columnName(index)
        node = self.model().data(index, role=Qt.UserRole)
        if isinstance(node, MetadataItemTreeNode):
            key = node.metadataKey()
            value = node.metadataValue()
            assert isinstance(key, MDKeyAbstract)

            if isinstance(key, MDKeyCoordinateReferenceSystem):
                w = QgsProjectionSelectionWidget(parent)

            elif isinstance(key, MDKeyDomainString):
                if isinstance(key.mOptions, list) and len(key.mOptions) > 0:
                    w = QComboBox(parent)
                    for o in key.mOptions:
                        w.addItem(o)

                elif isinstance(key.mListLength, int ) and key.mListLength > 0 and isinstance(value, list):
                    w = QComboBox(parent)
                    w.setInsertPolicy(QComboBox.InsertAtCurrent)
                    w.setEditable(True)
                    for i, v in enumerate(value):
                        w.addItem(str(v))

                elif key.mType in [int, float] and (key.mMin is not None or key.mMax is not None):
                    mMin = key.mMin if key.mMin is not None else -2147483648
                    mMax = key.mMax if key.mMax is not None else 2147483647

                    mMin = key.mType(mMin)
                    mMax = key.mType(mMax)

                    if isinstance(key.mType, int):
                        w = QSpinBox(parent)
                    elif isinstance(key.mType, float):
                        w = QDoubleSpinBox(parent)

                    w.setMinimum(mMin)
                    w.setMaximum(mMax)
                elif key.mType == np.datetime64:
                    dt = str(key.mValue0.dtype)
                    if re.search(r'datetime64\[(Y|M|W|D)\]', dt):
                        w = QDateEdit(parent)
                        w.setCalendarPopup(True)
                    else:
                        w = QDateTimeEdit(parent)
                        w.setCalendarPopup(True)

        if not isinstance(w, QWidget):
            w = QItemDelegate().createEditor(parent, option, index)
        return w

    def editorEvent(self, event, model, option, index):
        assert isinstance(index, QModelIndex)
        assert isinstance(option, QStyleOptionViewItem)
        assert isinstance(event, QEvent)

        if isinstance(event, QMouseEvent):
            if event.button() == Qt.RightButton:

                pass
        return False

    def setEditorData(self, editor, index:QModelIndex):
        cname = self.columnName(index)

        node = self.model().data(index, role=Qt.UserRole)

        if isinstance(node, MetadataItemTreeNode):
            value = node.metadataValue()
            key = node.mMDKey
            assert isinstance(key, MDKeyAbstract)

            if isinstance(editor, QLineEdit):
                editor.setText(value)

            elif isinstance(editor, QSpinBox):
                editor.setValue(value)

            elif isinstance(editor, QgsProjectionSelectionWidget):
                editor.setCrs(value)

            elif isinstance(editor, QComboBox):
                if isinstance(value, list):
                    editor.clear()
                    for v in value:
                        editor.addItem(str(v))
                else:
                    i = editor.findText(value)
                    if i >= 0:
                        editor.setCurrentIndex(i)

            elif type(editor) in [QSpinBox, QDoubleSpinBox]:
                editor.setValue(value)
            elif type(editor) in [QDateTimeEdit]:
                editor.setDateTime(QDateTime.fromString(str(value), Qt.ISODate))
            elif type(editor) in [QDateEdit]:
                editor.setDate(QDate.fromString(str(value), Qt.ISODate))
            elif type(editor) in [QTimeEdit]:
                editor.setTime(QTime.fromString(str(value), Qt.ISODate))
            else:
                s = ""



    def setModelData(self, w, model, index):
        model = self.model()
        node = model.data(index, role=Qt.UserRole)
        try:
            if isinstance(node, MetadataItemTreeNode):
                key = node.mMDKey
                assert isinstance(key, MDKeyAbstract)

                if isinstance(w, QLineEdit):
                    #node.setMetadataValue(w.text())
                    model.setData(index, w.text())
                elif isinstance(w, QgsProjectionSelectionWidget):
                    model.setData(index, w.crs())
                    #node.setMetadataValue(w.crs())
                elif isinstance(w, QComboBox):
                    if w.isEditable() and isinstance(key, MDKeyDomainString) and key.mListLength > 0:
                        values = [w.itemData(i, role=Qt.DisplayRole)
                                     for i in range(w.count())
                                     ]
                        model.setData(index, values)
                    else:
                        model.setData(index, w.currentText())
                    #node.setMetadataValue(w.currentText())
                elif type(w) in [QSpinBox, QDoubleSpinBox]:
                    model.setData(index, w.value())
                    #node.setMetadataValue(w.value())
                elif isinstance(w, QDateEdit):
                    model.setData(index, np.datetime64(w.date().toString(Qt.ISODate)))
                elif isinstance(w, QTimeEdit):
                    model.setData(index, np.datetime64(w.time().toString(Qt.ISODate)))
                elif isinstance(w, QDateTimeEdit):
                    model.setData(index, np.datetime64(w.dateTime().toString(Qt.ISODate)))
                else:
                    s = ""
            else:
                s  =""
        except AssertionError as ex:
            QMessageBox.critical(w, 'Error', ex.message)
        except Exception as ex:
            QMessageBox.critical(w, 'Error', ex.message)


class MetadataItemDialog(QDialog):

    def __init__(self, parent=None):
        super(MetadataItemDialog, self).__init__(parent)

        l = QVBoxLayout()
        self.setLayout(l)





class MetadataEditorDialog(QDialog):
    """Constructor."""
    def __init__(self, parent=None):
        super(MetadataEditorDialog, self).__init__(parent, Qt.Window)
        path = pathlib.Path(__file__).parent / 'metadataeditor.ui'
        loadUi(path, self)
        assert isinstance(self.treeView, TreeView)
        self.mSourceModel = OptionListModel()
        self.mMetadataModel = MetadataTreeModel(parent=self.treeView)
        self.mMetadataFilterModel = MetadataFilterModel()
        self.mMetadataFilterModel.setSourceModel(self.mMetadataModel)
        self.treeView.setModel(self.mMetadataFilterModel)
        self.treeView.selectionModel().selectionChanged.connect(self.onSelectionChanged)
        self.treeView.customContextMenuRequested.connect(self.onCustomContextMenu)

        def onFilterChanged():
            txt = self.tbKeyFilter.text()
            if self.optionUseRegex.isChecked():
                self.mMetadataFilterModel.setFilterRegExp(QRegExp(txt))
            else:
                self.mMetadataFilterModel.setFilterWildcard(txt)

        self.tbKeyFilter.textChanged.connect(onFilterChanged)

        self.mMetadataModel.dataChanged.connect(self.onDataChanged)

        self.cbSource.setModel(self.mSourceModel)



        def onSourceChanged(idx:int):
            if idx >= 0:
                path = self.mSourceModel.optionValues()[idx]
                self.treeView.setEnabled(False)
                #print('Set mMetadataModel.setSource {}'.format(path))
                self.mMetadataModel.setSource(path)
                #print('Set mMetadataModel.setSource ... done')
                self.treeView.setEnabled(True)

            self.onDataChanged()
            s = ""


        self.cbSource.currentIndexChanged[int].connect(onSourceChanged)
        #    lambda i : self.mMetadataModel.setSource(self.mSourceModel.optionValues()[i]))


        self.mDomains = OptionListModel()
        self.mDomains.insertOptions(Option(None, '<All>'))
        #self.cbDomainFilter.setModel(self.mDomains)
        d = self.mMetadataModel.domainModel()


        d.sigOptionsInserted.connect(self.mDomains.insertOptions)
        d.sigOptionsRemoved.connect(self.mDomains.removeOptions)


        self.treeView.header().setResizeMode(QHeaderView.ResizeToContents)

        self.delegate = MetadataTreeViewWidgetDelegates(self.treeView)

        self.buttonBox.button(QDialogButtonBox.Close).clicked.connect(lambda: self.close())
        #self.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.reject)
        self.buttonBox.button(QDialogButtonBox.Save).clicked.connect(self.saveChanges)
        self.buttonBox.button(QDialogButtonBox.Reset).clicked.connect(self.resetChanges)

        self.actionSetDataSource.triggered.connect(self.onSetDataSource)
        self.actionCollapse.triggered.connect(lambda : self.treeView.collapseAll())
        self.actionExpand.triggered.connect(lambda : self.treeView.expandToDepth(3))
        self.actionAddMetadataItem.triggered.connect(lambda : print('add metadata triggered'))

        self.actionAddMetadataItem.setEnabled(False)

        self.actionRemoveMetadataItem.triggered.connect(lambda : self.setDeleteFlag(self.selectedNodes(), True))
        self.optionUseRegex.toggled.connect(onFilterChanged)

        self.btnSelectSource.setDefaultAction(self.actionSetDataSource)
        self.btnCollapse.setDefaultAction(self.actionCollapse)
        self.btnExpand.setDefaultAction(self.actionExpand)
        self.btnAddMetadataItem.setDefaultAction(self.actionAddMetadataItem)
        self.btnRemoveMetadataItem.setDefaultAction(self.actionRemoveMetadataItem)
        self.btnUseRegex.setDefaultAction(self.optionUseRegex)


    def onSelectionChanged(self, selected:QItemSelection, deselected:QItemSelection):

        self.actionRemoveMetadataItem.setEnabled(len(selected) > 0)
        s = ""



    def onSetDataSource(self, *args):
        result, filter = QFileDialog.getOpenFileName(self, 'Open data source')
        if len(result) > 0:
            self.addSources([result])

    def setDeleteFlag(self, nodes:list, b: bool):
        for n in nodes:
            assert isinstance(n, MetadataItemTreeNode)
            n.setToDelete(b)

    def selectedNodes(self):
        """
        Returns the list of currently selected TreeNodes
        :return: [list-of-TreeNodes]
        """
        nodes = []

        for idx in self.treeView.selectionModel().selectedRows():
            node = self.treeView.model().data(idx, role=Qt.UserRole)
            if isinstance(node, MetadataItemTreeNode):
                nodes.append(node)
        return nodes

    def onCustomContextMenu(self, point):
        assert isinstance(point, QPoint)


        index = self.treeView.indexAt(point)
        assert isinstance(index, QModelIndex)
        if not index.isValid():
            return False

        node = self.treeView.model().data(index, role=Qt.UserRole)

        selectedNodes = self.selectedNodes()

        if node not in selectedNodes:
            selectedNodes = [node]

        if isinstance(node, MetadataItemTreeNode):
            m = QMenu()
            a = m.addAction('Copy')

            if isinstance(node, MetadataItemTreeNode) and node.isImmutable() == False:

                a = m.addAction('Reset')
                a.triggered.connect(node.resetValue)

                a = m.addAction('Delete')
                a.setIcon(QIcon(r':/images/themes/default/mActionDeleteSelected.svg'))
                a.triggered.connect(lambda : self.setDeleteFlag(selectedNodes, True))

                a = m.addAction('Undelete')
                a.triggered.connect(lambda: self.setDeleteFlag(selectedNodes, False))

                #edit ClassificationSchema in a separate dialog
                if isinstance(node, MetadataClassificationSchemeTreeNode) or \
                    isinstance(node.parentNode(), MetadataClassificationSchemeTreeNode):
                    schemaNode = node if isinstance(node, MetadataClassificationSchemeTreeNode) \
                                        else node.parentNode()

                    a = m.addAction('Edit Classification Scheme')
                    a.triggered.connect(lambda : self.onEditClassificationScheme(schemaNode))

            m.exec_(self.treeView.mapToGlobal(point))
            #m.popup(event.pos())


    def onDataChanged(self, *args):

        #print('check diffs')
        return
        differences = self.mMetadataModel.differences(None)
        if len(differences) > 0:
            self.buttonBox.button(QDialogButtonBox.Reset).setEnabled(True)
            self.buttonBox.button(QDialogButtonBox.Save).setEnabled(True)
        else:
            self.buttonBox.button(QDialogButtonBox.Reset).setEnabled(False)
            self.buttonBox.button(QDialogButtonBox.Save).setEnabled(False)
        s = ""

    def addSources(self, listOfSourceUris:list):
        if not isinstance(listOfSourceUris, list):
            listOfSourceUris = [listOfSourceUris]

        uriList = []
        b1 = gdal.GetUseExceptions()
        b2 = ogr.GetUseExceptions()
        gdal.DontUseExceptions()
        ogr.DontUseExceptions()
        for src in listOfSourceUris:
            if isinstance(src, str):
                guess = guessDataProvider(src)
                if guess in ['ogr','gdal']:
                    uriList.append(src)
            elif isinstance(src, QgsVectorLayer) and src.providerType() == 'ogr':
                uriList.append(src.source())

            elif isinstance(src, QgsRasterLayer) and src.providerType() == 'gdal':
                uriList.append(src.source())

            elif isinstance(src, gdal.Dataset) and len(src.GetSubDatasets()) == 0:
                uriList.append(src.GetFileList()[0])

            elif isinstance(src, ogr.DataSource):
                raise NotImplementedError()
                uriList.append(ogr)

            else:
                print('Datasource not supported for medata editing: {}'.format(src), file=sys.stderr)
        if b1:
            gdal.UseExceptions()
        if b2:
            ogr.UseExceptions()

        options = [Option(source, os.path.basename(source), toolTip=source) for source in uriList]
        self.mSourceModel.addOptions(options)




    def setSource(self, uri:str):
        self.addSources(uri)

        sources = self.mSourceModel.optionValues()
        if uri not in sources:
            self.setSource(uri)
        else:
            i = sources.index(uri)
            self.cbSource.setCurrentIndex(i)



    def saveChanges(self):

        self.mMetadataModel.writeMetadata()
        self.mMetadataModel.setSource(self.mMetadataModel.source())
        s = ""

    def resetChanges(self):
        """
        Re-reads all metadata from the source
        :return:
        """
        self.mMetadataModel.setSource(self.mMetadataModel.source())


    def rejectChanged(self):
        pass






