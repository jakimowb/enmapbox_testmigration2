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


import os, collections, copy, re
from qgis.gui import QgsFileWidget
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from osgeo import gdal, ogr, osr

import numpy as np
from enmapbox.gui.utils import loadUIFormClass
from enmapbox.gui.widgets.trees import TreeModel, TreeNode
from metadataeditorV2.metadatakeys import *
from __init__ import APP_DIR

#path to the *.ui file that was created/edited in the QDesigner
pathUi = os.path.join(APP_DIR, 'metadataeditor.ui')

DEFAULT_DOMAIN = '<default>'

ALL_IMMUTABLE = 'all_immutable'

MD_KEY_PROPERTIES = {}
MD_KEY_PROPERTIES['IMAGE_STRUCTURE']=[ALL_IMMUTABLE] #all metadata tag in domain 'IMAGE' are immutable
#see http://www.harrisgeospatial.com/docs/enviheaderfiles.html for details
MD_KEY_PROPERTIES['ENVI']=[
    MDKeyDomainString('ENVI', 'bands', valueType=int, valueMin=1, isImmutable=True),
    MDKeyDomainString('ENVI', 'samples', valueType=int, valueMin=1, isImmutable=True),
    MDKeyDomainString('ENVI', 'lines', valueType=int, valueMin=1, isImmutable=True),
    MDKeyDomainString('ENVI', 'interleave', options=['bsq', 'bil', 'bip'], isImmutable=True),
    MDKeyDomainString('ENVI', 'wavelength units', options= [
                    'Micrometers','um','Nanometers','nm','Millimeters','mm','Centimeters','cm',
                    'Meters','m','Wavenumber','Angstroms','GHz','MHz','Index','Unknown'])
    ]

class MetadataItemTreeNode(TreeNode):

    def __init__(self, parentNode, key=None, value=None):
        super(MetadataItemTreeNode, self).__init__(parentNode, name=key)

        assert isinstance(key, MDKeyAbstract)
        self.setName(key.mName)
        self.mMDKey = key
        self.mMDValue0 = value
        self.setMetadataValue(value)


    def metadataKey(self):
        return self.metadataKey()


    def setMetadataKey(self, key):
        assert isinstance(key, MDKeyDomainString)
        self.mMDKey = key
        self.setName(key.mName)

    def setMetadataValue(self, value):
        """
        :param value:
        :return: None (if success) or Exception
        """

        assert isinstance(self.mMDKey, MDKeyAbstract)

        if value is None:
            self.setValues([])
        else:
            if isinstance(self.mMDKey, MDKeyDomainString):
                value = self.mMDKey.mType(value)
            self.setValues(value)
        return None

    def metadataValue(self):
        if len(self.values()) > 0:
            return self.values()[0]
        else:
            return None

    def resetMetadataValue(self):
        self.setMetadataValue(self.mMDValue0)

    def isImmutable(self):
        return self.mMDKey.mIsImmutable

    def clone(self, *args, **kwds):

        return super(MetadataItemTreeNode, self).clone(key=self.mMDKey)


class MetadataClassificationItemTreeNode(MetadataItemTreeNode):
    pass

class RasterBandTreeNode(TreeNode):

    def __init__(self, parentNode, bandIndex=None):
        super(RasterBandTreeNode, self).__init__(parentNode)
        self.mBandIndex = bandIndex
        if bandIndex is not None:
            self.setName('Band {}'.format(bandIndex+1))


class RasterSourceTreeNode(TreeNode):
    pass

class MetadataDomainTreeNode(TreeNode):
    pass

class VectorLayerTreeNode(TreeNode):

    pass

class MetadataTreeModel(TreeModel):

    def __init__(self, parent=None):
        super(MetadataTreeModel, self).__init__(parent)

        self.cnKey = 'Domain/Key'
        self.cnValue = 'Value'
        self.mSource = None

        self.mRootNode0 = None

        self.mColumnNames = [self.cnKey, self.cnValue]

    def differences(self, rootNode=None):
        if rootNode is None:
            rootNode = self.mRootNode

        #todo: return only nodes with changed metadata values
        return []


    def parseSource(self, path):

        ds = gdal.Open(path)
        if isinstance(ds, gdal.Dataset):
            return self.parseRasterMD(ds)
        ds = ogr.Open(path)
        if isinstance(ds, ogr.DataSource):
            return self.parseVectorMD(ds)

        return [TreeNode(None, path, values=['unable to read metadata'])]

    def parseDomainMetadata(self,parentNode, obj):
        assert isinstance(parentNode, TreeNode)

        domains = sorted(obj.GetMetadataDomainList())
        for domain in domains:
            if domain == '':
                domain = DEFAULT_DOMAIN
            nDomain = TreeNode(parentNode, name=domain)
            md = obj.GetMetadata(domain=domain)
            if domain not in MD_KEY_PROPERTIES.keys():
                MD_KEY_PROPERTIES[domain] = []
            all_immutable = ALL_IMMUTABLE in MD_KEY_PROPERTIES[domain]

            def findKey(name, value):
                for k in MD_KEY_PROPERTIES[domain]:
                    if isinstance(k, MDKeyDomainString) and k.mName == name:
                        return k
                return MDKeyDomainString.fromString(domain, name, value)

            for keyName, v in md.items():
                mdKey = findKey(keyName, v)
                if all_immutable:
                    mdKey.mIsImmutable = True
                    MD_KEY_PROPERTIES[domain].append(mdKey)
                MetadataItemTreeNode(nDomain, mdKey, v)

    def parseRasterMD(self, ds):
        """
        Reads a gdal.Dataset and returns a Tree of Medatadata
        :param ds:
        :return:
        """
        assert isinstance(ds, gdal.Dataset)
        root = TreeNode(None)


        files = ds.GetFileList()
        basename = os.path.basename(files[0])
        #nDS = RasterSourceTreeNode(root, name='Dataset', values=basename)

        nodes = []

        TreeNode(root, 'Dataset', values=basename, tooltip=files[0])

        mdKeyDescription = MDKeyDescription()
        MetadataItemTreeNode(root, key=mdKeyDescription, value=mdKeyDescription.readValue(ds))

        mdKeyClassification = MDKeyClassification()
        MetadataItemTreeNode(root, key=mdKeyClassification, value=mdKeyClassification.readValue(ds))

        nFiles = TreeNode(root, 'Source Files')
        for i, f in enumerate(files):
            TreeNode(nFiles,name=os.path.basename(f),values=f)

        nGeneral = TreeNode(root, 'Metadata (Dataset)')

        self.parseDomainMetadata(nGeneral, ds)

        nBands = TreeNode(root, 'Metadata (Bands)')
        for b in range(ds.RasterCount):
            band = ds.GetRasterBand(b+1)
            nBand = RasterBandTreeNode(nBands, b)

            assert isinstance(band, gdal.Band)
            MetadataItemTreeNode(nBand, key=mdKeyDescription, value=mdKeyDescription.readValue(band))

            self.parseDomainMetadata(nBand, band)

        return root


    def parseVectorMD(self, ds):
        assert isinstance(ds, ogr.DataSource)
        root = TreeNode(None)

    def setSource(self, path):
        self.mRootNode0 = self.parseSource(path)

        if isinstance(self.mRootNode0, TreeNode):
            assert isinstance(self.mRootNode, TreeNode)
            l = len(self.mRootNode.childNodes())
            self.mRootNode.removeChildNodes(0, l)
            clonedNodes = [c.clone() for c in self.mRootNode0.childNodes()]
            self.mRootNode.appendChildNodes(clonedNodes)


    def source(self):
        return self.mSource

    def flags(self, index):
        flags = super(MetadataTreeModel, self).flags(index)
        cName = self.idx2columnName(index)
        node = self.idx2node(index)
        if isinstance(node, MetadataItemTreeNode) and cName == self.cnValue:
            if node.isImmutable() == False:
                flags = flags | Qt.ItemIsEditable
            else:
                s = ""
        return flags

    def data(self, index, role):

        node = self.idx2node(index)
        cName = self.columnNames()[index.column()]
        if not (cName == self.cnValue and isinstance(node, MetadataItemTreeNode)):
            return super(MetadataTreeModel, self).data(index, role)
        else:

            value = node.metadataValue()

            flags = self.flags(index)
            isEditable = bool(flags & Qt.ItemIsEditable)

            data = None
            if cName == self.cnValue:
                if role == Qt.DisplayRole:
                    data = value
                if role == Qt.EditRole:
                    data = value
                if role == Qt.FontRole:
                    font = QFont()
                    font.setItalic(isEditable)
                    data = font

                elif role == Qt.BackgroundRole and isEditable:
                    data = QBrush(QColor('yellow'))
                elif role == Qt.EditRole:
                    s = ""

            return data

    def writeMetadata(self):

        differences = self.differences(self)
        for node in differences:
            assert isinstance(node, MetadataItemTreeNode)
            key = node.metadataKey()



class MetadataEditorDialog(QDialog, loadUIFormClass(pathUi)):
    """Constructor."""
    def __init__(self, parent=None):
        super(MetadataEditorDialog, self).__init__(parent)
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
        self.treeView.setModel(self.mMetadataModel)
        self.treeView.header().setResizeMode(QHeaderView.ResizeToContents)

        self.buttonBox.button(QDialogButtonBox.Close).clicked.connect(lambda: self.close())
        self.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.reject)
        self.buttonBox.button(QDialogButtonBox.Save).clicked.connect(self.saveChanges)
        self.buttonBox.button(QDialogButtonBox.Reset).clicked.connect(self.resetChanges)

    def setSource(self, uri):
        self.mMetadataModel.setSource(uri)

    def cancelChanges(self):
        pass

    def saveChanges(self):
        pass

    def resetChanges(self):
        self.mMetadataModel.setSource(self.mMetadataModel.source())

    def rejectChanged(self):
        pass





