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


import sys, os
from enmapbox.gui import *
from enmapbox.gui.utils import loadUIFormClass, guessDataProvider
from metadataeditorapp.metadatakeys import *




from metadataeditorapp import APP_DIR

#path to the *.ui file that was created/edited in the QDesigner
pathUi = os.path.join(APP_DIR, 'metadataeditor.ui')

DEFAULT_DOMAIN = '<default>'

ALL_IMMUTABLE = 'all_immutable'

MD_DOMAIN_INFO = {}
MD_DOMAIN_INFO[''] = 'This is the default metadata domain.'
MD_DOMAIN_INFO['IMAGE_STRUCTURE'] = 'Information of interest closely tied to the particular file format and storage mechanism.'
MD_DOMAIN_INFO['ENVI'] = 'The ENVI Metdata domain. See see http://www.harrisgeospatial.com/docs/enviheaderfiles.html for details.'
MD_DOMAIN_INFO['SUBDATASETS'] = 'The SUBDATASETS domain holds a list of child datasets. Normally this is used to provide pointers to a list of images stored within a single multi image file.'
MD_DOMAIN_INFO['RPC'] = 'Metadata describing the Rational Polynomial Coefficient geometry model for the image'
MD_DOMAIN_INFO['IMAGERY'] = 'Specific information for satellite or aerial imagery.'



class MetadataItemTreeNode(TreeNode):
    def __init__(self, parentNode, key, **kwds):
        assert isinstance(key, MDKeyAbstract)
        if 'name' not in kwds.keys():
            kwds['name'] = key.name()
        if 'toolTip' not in kwds.keys():
            kwds['toolTip'] = key.tooltip()
        super(MetadataItemTreeNode, self).__init__(parentNode, **kwds)

        self.mMDKey = key
        self.setMetadataValue(key.value())

    def updateNode(self):
        """
        Calling this routine refreshes the information shown by the TreeNode
        and, if necessary, its sub-nodes.
        """
        self.setValues(str(self.mMDKey.value()))

    def metadataKey(self)->MDKeyAbstract:
        """
        Returns the MDKey connected with this TreeNode
        :return:
        """
        return self.mMDKey

    def metadataValue(self):
        return self.mMDKey.value()

    def setMetadataValue(self, value):
        """
        Sets the MDKEy value to `value` and updates the TreeNode information.
        :param value:
        :return:
        """
        old = self.metadataValue()
        if value != old:
            self.mMDKey.setValue(value)
            #self.sigUpdated.emit(self)
            self.updateNode()

    def resetMetadataValue(self):
        self.setMetadataValue(self.mMDKey.mValue0)
        self.sigUpdated.emit(self)

    def isImmutable(self):
        return self.mMDKey.isImmutable()

    def clone(self, *args, **kwds):

        n = super(MetadataItemTreeNode, self).clone(key=self.mMDKey)
        if isinstance(self.mMDKey, MDKeyCoordinateReferenceSystem):
            s = ""

        return n


class MetadataClassificationSchemeTreeNode(MetadataItemTreeNode):

    def __init__(self, parentNode, dataSet, **kwds):
        key = MDKeyClassification(dataSet)
        super(MetadataClassificationSchemeTreeNode, self).__init__(parentNode, key, **kwds)

        self.mMDKey.mValue.sigClassesAdded.connect(self.updateNode)
        self.mMDKey.mValue.sigClassesRemoved.connect(self.updateNode)
        #self.mMDKey.mValue.sigClassInfoChanged.connect(self.updateNode)
        self.updateNode()

    def updateNode(self, *args):
        l = len(self.childNodes())
        self.removeChildNodes(0, l)

        classScheme = self.mMDKey.value()
        assert isinstance(classScheme, ClassificationScheme)
        if len(classScheme) == 0:
            self.setValues('None')
        else:
            self.setValues('{} classes'.format(len(classScheme)))

            for i, classInfo in enumerate(classScheme):
                assert isinstance(classInfo, ClassInfo)
                TreeNode(self,name='Class {}'.format(classInfo.label()), values=classInfo.name() , icon=classInfo.icon())


class CoordinateReferencesSystemTreeNode(MetadataItemTreeNode):

    def __init__(self, parentNode, dataSet, **kwds):
        key = MDKeyCoordinateReferenceSystem(dataSet)
        super(CoordinateReferencesSystemTreeNode, self).__init__(parentNode, key, **kwds)
        self.updateNode()


    def updateNode(self):
        """
        Calling this routine will refresh the information shown by the TreeNode
        and, if necessary, its sub-nodes.
        """

        self.removeChildNodes(0, self.childCount())
        crs = self.mMDKey.value()
        if isinstance(crs, QgsCoordinateReferenceSystem):
            self.setValues(str(crs.description()))
            TreeNode(self, 'Description', values=crs.description())
            TreeNode(self, 'WKT', values=crs.toWkt())
            TreeNode(self, 'Ellipsoid', values=crs.ellipsoidAcronym())
        else:
            self.setValues('None')

class RasterBandTreeNode(MetadataItemTreeNode):

    def __init__(self, parentNode, band, **kwds):
        assert isinstance(band, gdal.Band)

        key = MDKeyDescription(band)
        super(RasterBandTreeNode, self).__init__(parentNode, key, **kwds)
        if not kwds.get('name'):
            self.setName('Band {}'.format(band.GetBand()))

        self.mBandIndex = band.GetBand() - 1

    def bandIndex(self)->int:
        """Returns the band index"""
        return self.mBandIndex

class VectorLayerTreeNode(MetadataItemTreeNode):

    def __init__(self, parentNode, layer, layerIndex, **kwds):
        assert isinstance(layer, ogr.Layer)
        key = MDKeyDescription(layer)
        super(VectorLayerTreeNode, self).__init__(parentNode, key, **kwds)
        if not kwds.get('name'):
            self.setName('Layer {}'.format(layer.GetDescription()))
        self.mLayerIndex = layerIndex

    def layerIndex(self)->int:
        """Returns the layer index"""
        return self.mLayerIndex

class RasterSourceTreeNode(MetadataItemTreeNode):

    def __init__(self, parentNode, dataSet, **kwds):
        assert isinstance(dataSet, gdal.Dataset)
        key = MDKeyDescription(dataSet)
        super(RasterSourceTreeNode, self).__init__(parentNode, key, **kwds)
        self.mSource = dataSet.GetFileList()[0]


class VectorSourceTreeNode(MetadataItemTreeNode):

    def __init__(self, parentNode, dataSource, **kwds):
        assert isinstance(dataSource, ogr.DataSource)
        key = MDKeyDescription(dataSource)
        super(VectorSourceTreeNode, self).__init__(parentNode, key, **kwds)


class MetadataDomainTreeNode(TreeNode):

    def __init__(self, parentNode, domain, *args, **kwds ):
        assert isinstance(domain, str)
        nodeName = domain if domain != '' else DEFAULT_DOMAIN
        kwds['name'] = nodeName
        super(MetadataDomainTreeNode, self).__init__(parentNode, *args, **kwds)
        self.mDomain = domain

        if self.mToolTip is None and self.mDomain in MD_DOMAIN_INFO.keys():
            self.setToolTip(MD_DOMAIN_INFO[self.mDomain])

        self.sigAddedChildren.connect(self.update)
        self.sigRemovedChildren.connect(self.update)
        self.update()

    def update(self):

        n = self.childCount()
        if n == 0:
            self.setValues('not metadata items')
        else:
            self.setValues('{} metadata items'.format(n))



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

        self.cnKey = 'Domain/Key'
        self.cnValue = 'Value'
        self.mSource = None

        self.mDomains = MetadataDomainModel()
        self.mRootNode0 = None

        self.mColumnNames = [self.cnKey, self.cnValue]

    def domainModel(self):
        return self.mDomains

    def differences(self, rootNode)->list:
        """
        Returns the TreeNodes with changed values
        :param rootNode: TreeNode, by default the models rootNode
        :return: [list-of-changed-MDKeys]
        """
        if rootNode is None:
            rootNode = self.mRootNode

        assert isinstance(rootNode, TreeNode)

        nodes = []
        if isinstance(rootNode, MetadataItemTreeNode):
            key = rootNode.mMDKey
            assert isinstance(key, MDKeyAbstract)
            if key.valueHasChanged():
                nodes.append(rootNode)
        for childNode in rootNode.childNodes():
            nodes += self.differences(childNode)
        return nodes

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


    def openSource(self, path:str):
        order = ['gdal', 'ogr']
        if re.search(r'(shp|gpkg|kml|kmz)$', path):
            order = ['ogr', 'gdal']
        for t in order:
            try:
                if t == 'gdal':
                    ds = gdal.Open(path)
                    if isinstance(ds, gdal.Dataset):
                        return ds
                elif t == 'ogr':
                    ds = ogr.Open(path)
                    if isinstance(ds, ogr.DataSource):
                        return ds
            except Exception as ex:
                pass
        return None

    def parseDomainMetadata(self, parentNode, obj):
        assert isinstance(parentNode, TreeNode)

        domains = obj.GetMetadataDomainList()
        if domains is None:
            domains = []
        for domain in sorted(domains):
            self.mDomains.addDomain(domain)

            nodeName = DEFAULT_DOMAIN if domain == '' else domain

            nDomain = MetadataDomainTreeNode(parentNode, domain=domain, name=nodeName)
            md = obj.GetMetadata(domain=domain)
            for name in md.keys():
                key = MDKeyDomainString.fromDomain(obj, domain, name)
                MetadataItemTreeNode(nDomain, key)

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

        nDS = RasterSourceTreeNode(root, ds,
                                   name='Dataset',
                                   toolTip='Raster Data Source.')

        nFiles = TreeNode(root, 'Source Files',
                          values=len(files),
                          toolTip='Physical files related to this Raster Data Source.')
        for i, f in enumerate(files):
            TreeNode(nFiles, name='{}'.format(i + 1), values=os.path.basename(f))

        nCRS = CoordinateReferencesSystemTreeNode(root, ds)

        MetadataClassificationSchemeTreeNode(root, ds)

        nGeneral = TreeNode(root, 'Metadata (Dataset)')
        self.parseDomainMetadata(nGeneral, ds)

        nBands = TreeNode(root, 'Metadata (Bands)')
        for b in range(ds.RasterCount):
            band = ds.GetRasterBand(b + 1)
            assert isinstance(band, gdal.Band)

            nBand = RasterBandTreeNode(nBands, band)
            self.parseDomainMetadata(nBand, band)

        return root

    def parseVectorMD(self, ds: ogr.DataSource) -> TreeNode:
        assert isinstance(ds, ogr.DataSource)
        root = TreeNode(None)

        dsNode = VectorSourceTreeNode(root, ds)
        nFiles = TreeNode(root, 'Source', values=ds.GetName())
        nGeneral = TreeNode(root, 'Metadata (Datasource)')
        self.parseDomainMetadata(nGeneral, ds)

        nLayers = TreeNode(root, 'Metadata (Layers)')

        for i in range(ds.GetLayerCount()):
            lyr = ds.GetLayerByIndex(i)
            assert isinstance(lyr, ogr.Layer)

            nLayer = VectorLayerTreeNode(nLayers, lyr, i)
            self.parseDomainMetadata(nLayer, lyr)

        return root

    def setSource(self, path):
        root = self.parseSource(path)
        self.mSource = path
        l = self.mRootNode.childCount()
        self.mRootNode.removeChildNodes(0, l)
        if isinstance(root, TreeNode):
            self.mRootNode.appendChildNodes(root.childNodes())

        """
        if isinstance(self.mRootNode0, TreeNode):
            assert isinstance(self.mRootNode, TreeNode)
            l = len(self.mRootNode.childNodes())
            self.mRootNode.removeChildNodes(0, l)
            clonedNodes = [c.clone() for c in self.mRootNode0.childNodes()]
            self.mRootNode.appendChildNodes(clonedNodes)

        """

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return None
        if not role == Qt.EditRole:
            return None

        cName = self.idx2columnName(index)
        node = self.idx2node(index)

        if not isinstance(node, MetadataItemTreeNode):
            return False
        else:
            node.setMetadataValue(value)
            # key = node.metadataKey()
            # key.setValue(value)
            self.dataChanged.emit(index, index)
            return True

        return False

    def source(self):
        return self.mSource

    def flags(self, index):
        flags = super(MetadataTreeModel, self).flags(index)
        cName = self.idx2columnName(index)
        node = self.idx2node(index)
        if isinstance(node, MetadataItemTreeNode) and cName == self.cnValue:
            if node.isImmutable() == False \
                    and type(node) not in [MetadataClassificationSchemeTreeNode]:
                flags = flags | Qt.ItemIsEditable
            else:
                s = ""

        if isinstance(node.parentNode(), MetadataClassificationSchemeTreeNode):
            s = ""

        return flags

    def data(self, index, role):

        node = self.idx2node(index)
        cName = self.columnNames()[index.column()]
        if not (cName == self.cnValue and isinstance(node, MetadataItemTreeNode)):
            return super(MetadataTreeModel, self).data(index, role)
        else:
            value = node.metadataValue()
            key = node.mMDKey

            flags = self.flags(index)
            isEditable = bool(flags & Qt.ItemIsEditable) \
                         or type(node) in [MetadataClassificationSchemeTreeNode]
            data = None
            if cName == self.cnValue:
                if role == Qt.DisplayRole:
                    if isinstance(key, MDKeyCoordinateReferenceSystem):
                        if value is None:
                            data == 'Undefined'
                        else:
                            try:
                                data = value.description()
                            except Exception as e:
                                pass

                    elif isinstance(key, MDKeyClassification):
                        data = str(node.values()[0])

                    else:
                        data = str(value)

                if role == Qt.EditRole:
                    data = value
                if role == Qt.FontRole:
                    font = QFont()
                    font.setItalic(isEditable)
                    data = font

                elif role == Qt.BackgroundRole and isEditable:
                    data = QBrush(QColor('yellow'))
                elif role == Qt.EditRole:
                    data = value

            return data

    def writeMetadata(self):

        differences = self.differences(self.mRootNode)
        if len(differences) > 0:
            ds = self.openSource(self.mSource)
            for t in differences:

                assert isinstance(t, TreeNode)

                if isinstance(t, MetadataClassificationSchemeTreeNode):
                    t.metadataKey().writeValueToSource(ds)
                elif isinstance(t, RasterBandTreeNode):

                    band = ds.GetRasterBand(t.bandIndex()+1)
                    t.metadataKey().writeValueToSource(band)
                elif isinstance(t, VectorLayerTreeNode):
                    layer = ds.GetLayerByIndex(t.layerIndex())
                    t.metadataKey().writeValueToSource(layer)

                else:
                    s = ""

            ds = None





class MetadataFilterModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(MetadataFilterModel, self).__init__(parent)

    def mimeTypes(self):
        return self.sourceModel().mimeTypes()

    def dropMimeData(self, mimeData, action, row, col, parentIndex):
        return self.sourceModel().dropMimeData(mimeData, action, row, col, parentIndex)

    def supportedDropActions(self):
        return self.sourceModel().supportedDropActions()

    def filterAcceptsRow(self, sourceRow, sourceParent):
        node = self.sourceModel().idx2node(sourceParent).childNodes()[sourceRow]

        #if type(node) not in [SourceRasterFileNode, SourceRasterBandNode]:
        #    return True

        s0 = self.sourceModel().index(sourceRow, 0, sourceParent).data()
        s1 = self.sourceModel().index(sourceRow, 1, sourceParent).data()

        reg = self.filterRegExp()
        if reg.isEmpty():
            return True
        else:
            if isinstance(node, MetadataItemTreeNode):
                pattern = reg.pattern().replace(':', '')
                reg.setPattern(pattern)

            return reg.indexIn(s0) >= 0 or reg.indexIn(s1) >= 0

    def filterAcceptsColumn(self, sourceColumn, sourceParent):
        node = self.sourceModel().idx2node(sourceParent)
        #if not isinstance(node, SourceRasterBandNode):
        if not isinstance(node, TreeNode):
            return True
        else:
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
        self.mTreeView.customContextMenuRequested.connect(self.onCustomContextMenu)

    def treeModel(self)->MetadataTreeModel:
        model = self.mTreeView.model()

        #assert isinstance(model, MetadataTreeModel)
        return model


    def onDoubleClick(self, idx):
        indexM, node, modelM = self.inm(idx)
        if isinstance(node, MetadataClassificationSchemeTreeNode):
            self.onEditClassificationScheme(node)
        return



        classInfo = modelM.getClassInfoFromIndex(indexM)
        if idx.column() == modelM.columnNames.index(model.cCOLOR):

            w1 = QColorDialog(classInfo.mColor, self.treeView)
            w1.exec_()
            if w1.result() == QDialog.Accepted:
                c = w1.getColor()
                modelM.setData(indexM, c, role=Qt.EditRole)


    def onCustomContextMenu(self, point):
        assert isinstance(point, QPoint)


        index = self.mTreeView.indexAt(point)
        assert isinstance(index, QModelIndex)
        cname = self.getColumnName(index)
        index, node, model = self.inm(index)

        if index.isValid():
            m = QMenu()
            a = m.addAction('Copy')

            if isinstance(node, MetadataItemTreeNode) and node.isImmutable() == False:
                key = node.mMDKey

                a = m.addAction('Reset')
                a.triggered.connect(node.resetMetadataValue)

                #edit ClassificationSchema in a separate dialog
                if isinstance(node, MetadataClassificationSchemeTreeNode) or \
                    isinstance(node.parentNode(), MetadataClassificationSchemeTreeNode):
                    schemaNode = node if isinstance(node, MetadataClassificationSchemeTreeNode) \
                                        else node.parentNode()

                    a = m.addAction('Edit Classification Scheme')
                    a.triggered.connect(lambda : self.onEditClassificationScheme(schemaNode))

            m.exec_(self.mTreeView.mapToGlobal(point))
            #m.popup(event.pos())

    def onEditClassificationScheme(self, node):

        assert isinstance(node, MetadataClassificationSchemeTreeNode)
        assert isinstance(node.mMDKey, MDKeyClassification)

        value = node.metadataValue()

        model = self.treeModel().sourceModel()
        #assert isinstance(model, MetadataTreeModel)


        scheme = ClassificationSchemeDialog.getClassificationScheme(classificationScheme=value)
        if isinstance(scheme, ClassificationScheme):
            index = model.node2idx(node)
            model.setData(index, scheme)


    def inm(self, index):
        """
        Returns the Index, Node, and TreeModel referece by index. Accounts for QAbstractProxyModels
        :param index: QModelIndex
        :return: QModelIndex, TreeNode, TreeModel
        """
        model = self.treeModel()
        if isinstance(model, QAbstractProxyModel):
            indexM = model.mapToSource(index)
            modelM = model.sourceModel()
            return indexM, modelM.idx2node(indexM), modelM

        else:
            return index, model.idx2node(index), model

    def getColumnName(self, index):
        assert index.isValid()
        index, node, model = self.inm(index)
        return model.idx2columnName(index)
    """
    def sizeHint(self, options, index):
        s = super(ExpressionDelegate, self).sizeHint(options, index)
        exprString = self.tableView.model().data(index)
        l = QLabel()
        l.setText(exprString)
        x = l.sizeHint().width() + 100
        s = QSize(x, s.height())
        return self._preferedSize
    """
    def createEditor(self, parent, option, index):

        cname = self.getColumnName(index)
        indexM, node, modelM = self.inm(index)

        w = QItemDelegate().createEditor(parent, option, index)

        if isinstance(node, MetadataItemTreeNode) and cname == modelM.cnValue:
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



        return w

    def editorEvent(self, event, model, option, index):
        assert isinstance(index, QModelIndex)
        assert isinstance(option, QStyleOptionViewItem)
        assert isinstance(event, QEvent)
#        assert isinstance(model, MetadataTreeModel)
        indexM, node, modelM = self.inm(index)
        cname = self.getColumnName(index)


        if isinstance(event, QMouseEvent):
            if event.button() == Qt.RightButton:

                pass
        return False

    def setEditorData(self, editor, index):
        cname = self.getColumnName(index)
        indexM, node, modelM = self.inm(index)

        if cname == modelM.cnValue and isinstance(node, MetadataItemTreeNode):
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
        cname = self.getColumnName(index)
        indexM, node, modelM = self.inm(index)

        try:
            if index.isValid() and isinstance(node, MetadataItemTreeNode):
                key = node.mMDKey
                assert isinstance(key, MDKeyAbstract)

                if isinstance(w, QLineEdit):
                    #node.setMetadataValue(w.text())
                    modelM.setData(indexM, w.text())
                elif isinstance(w, QgsProjectionSelectionWidget):
                    modelM.setData(indexM, w.crs())
                    #node.setMetadataValue(w.crs())
                elif isinstance(w, QComboBox):
                    if w.isEditable() and isinstance(key, MDKeyDomainString) and key.mListLength > 0:
                        values = [w.itemData(i, role=Qt.DisplayRole)
                                     for i in range(w.count())
                                     ]
                        modelM.setData(indexM, values)
                    else:
                        modelM.setData(indexM, w.currentText())
                    #node.setMetadataValue(w.currentText())
                elif type(w) in [QSpinBox, QDoubleSpinBox]:
                    modelM.setData(indexM, w.value())
                    #node.setMetadataValue(w.value())
                elif isinstance(w, QDateEdit):
                    modelM.setData(indexM, np.datetime64(w.date().toString(Qt.ISODate)))
                elif isinstance(w, QTimeEdit):
                    modelM.setData(indexM, np.datetime64(w.time().toString(Qt.ISODate)))
                elif isinstance(w, QDateTimeEdit):
                    modelM.setData(indexM, np.datetime64(w.dateTime().toString(Qt.ISODate)))
                else:
                    s = ""
            else:
                s  =""
        except AssertionError as ex:
            QMessageBox.critical(w, 'Error', ex.message)
        except Exception as ex:
            QMessageBox.critical(w, 'Error', ex.message)



class MetadataSelectionModel(QItemSelectionModel):
    def __init__(self, model, parent=None):
        assert isinstance(model, MetadataTreeModel)
        super(MetadataSelectionModel, self).__init__(model, parent)

        self.mModel = model
        self.selectionChanged.connect(self.onTreeSelectionChanged)


    def onTreeSelectionChanged(self, selected, deselected):
        sourceFiles = self.selectedSourceFiles()
        features = set([self.mLyr.path2feature(path) for path in sourceFiles])
        self.setMapHighlights(features)

    def selectedSourceFileNodes(self):
        indexes = self.selectedIndexes()
        selectedFileNodes = self.mModel.idx2node(indexes)
        return [n for n in selectedFileNodes if isinstance(n, VRTRasterInputSourceBandNode)]

    def selectedSourceFiles(self):
        return set(n.sourceBand().mPath for n in self.selectedSourceFileNodes())




class MetadataEditorDialog(QDialog, loadUIFormClass(pathUi)):
    """Constructor."""
    def __init__(self, parent=None):
        super(MetadataEditorDialog, self).__init__(parent, Qt.Window)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect

        # Important!!!!!!!!! this will initiate all the QWidgets etc. specified in the *.ui file
        self.setupUi(self)

        # Connect widgets, add logic that can not be expressed in the QDesigner and needs to be "hard-coded"

        assert isinstance(self.treeView, QTreeView)

        self.mMetadataModel = MetadataTreeModel(parent=self.treeView)
        self.mMetadataFilterModel = MetadataFilterModel()
        self.mMetadataFilterModel.setSourceModel(self.mMetadataModel)

        def onFilterChanged():
            txt = self.tbKeyFilter.text()
            if self.cbFilterRegex.isChecked():
                self.mMetadataFilterModel.setFilterRegExp(QRegExp(txt))
            else:
                self.mMetadataFilterModel.setFilterWildcard(txt)

        self.tbKeyFilter.textChanged.connect(onFilterChanged)
        self.cbFilterRegex.toggled.connect(onFilterChanged)

        self.mMetadataModel.dataChanged.connect(self.onDataChanged)
        self.mSourceModel = OptionListModel()
        self.cbSource.setModel(self.mSourceModel)


        def onSourceChanged(idx:int):
            if idx >= 0:
                path = self.mSourceModel.optionValues()[idx]
                self.treeView.setEnabled(False)
                self.mMetadataModel.setSource(path)
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


        #self.treeView.setModel(self.mMetadataModel)
        self.treeView.setModel(self.mMetadataFilterModel)
        #self.treeView.header().setResizeMode(QHeaderView.ResizeToContents)

        self.delegate = MetadataTreeViewWidgetDelegates(self.treeView)
        self.treeView.setItemDelegate(self.delegate)

        self.buttonBox.button(QDialogButtonBox.Close).clicked.connect(lambda: self.close())
        #self.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.reject)
        self.buttonBox.button(QDialogButtonBox.Save).clicked.connect(self.saveChanges)
        self.buttonBox.button(QDialogButtonBox.Reset).clicked.connect(self.resetChanges)

        self.btnSelectSource.setDefaultAction(self.actionSetDataSource)
        self.actionSetDataSource.triggered.connect(self.onSetDataSource)

    def onSetDataSource(self, *args):
        result, filter = QFileDialog.getOpenFileName(self, 'Open data source')
        if len(result) > 0:
            self.addSources([result])

    def onDataChanged(self, *args):
        #print('check diffs')
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
        self.onDataChanged()
        pass

    def resetChanges(self):
        """
        Re-reads all metadata from the source
        :return:
        """
        self.mMetadataModel.setSource(self.mMetadataModel.source())
        self.onDataChanged()

    def rejectChanged(self):
        pass






