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

import os, collections
from qgis.gui import QgsFileWidget
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from osgeo import gdal, ogr, osr
""""
Use the QtDesigner to open the example.ui file.  
The example.ui can get compiled and loaded at runtime.
"""""
from enmapbox.gui.utils import loadUIFormClass
from enmapbox.gui.widgets.trees import TreeModel, TreeNode
from __init__ import APP_DIR

#path to the *.ui file that was created/edited in the QDesigner
pathUi = os.path.join(APP_DIR, 'metadataeditor.ui')

class MetadataItemTreeNode(TreeNode):

    def __init__(self, key, value, valueType=None, allowToWrite=True):
        self.mMDKey = key
        self.mMDValue0 = value
        self.mMDValue1 = value
        self.mAllowToWrite = allowToWrite

    def setMDValue(self, value):
        self.mMDValue1 = value


class MetadataClassificationItemTreeNode(MetadataItemTreeNode):
    pass

class RasterBandTreeNode(TreeNode):
    pass

class RasterSourceTreeNode(TreeNode):
    pass
class MetadataDomainTreeNode(TreeNode):
    pass

class VectorLayerTreeNode(TreeNode):

    pass

class MetadataTreeModel(TreeModel):

    def __init__(self, parent=None):
        super(MetadataTreeModel, self).__init__(parent)

        self.mSource = None

        self.mRootNode0 = None



    def differences(self):

        #todo: return nodes that are different to the original node
        return []

    def parseSource(self, path):

        ds = gdal.Open(path)
        if isinstance(ds, gdal.Dataset):
            return self.parseRasterMD(ds)
        ds = ogr.Open(path)
        if isinstance(ds, ogr.DataSource):
            return self.parseVectorMD(ds)

    def parseRasterMD(self, ds):
        assert isinstance(ds, gdal.Dataset)
        root = TreeNode(None)

        domains = ds.GetMetadataDomainList()
        nDS = RasterSourceTreeNode(root, 'Dataset')
        for domain in domains:

            nDomain = TreeNode(root, name=domain)
            md = ds.GetMetadata(domain=domain)
            for k, v in md.items():
                nItem = MetadataItemTreeNode(nDomain, k, v)


        return nDS


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
            self.mRootNode.insertChildNodes(0, clonedNodes)


    def source(self):
        return self.mSource





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


        self.buttonBox.button(QDialogButtonBox.Close).clicked.connect(lambda: self.close())
        self.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.reject)
        self.buttonBox.button(QDialogButtonBox.Apply).clicked.connect(self.applyChanges)
        self.buttonBox.button(QDialogButtonBox.Reset).clicked.connect(self.resetChanges)

    def setSource(self, uri):
        self.mMetadataModel.setSource(uri)

    def cancelChanges(self):
        pass

    def applyChanges(self):
        pass

    def resetChanges(self):
        self.mMetadataModel.setSource(self.mMetadataModel.source())

    def rejectChanged(self):
        pass





