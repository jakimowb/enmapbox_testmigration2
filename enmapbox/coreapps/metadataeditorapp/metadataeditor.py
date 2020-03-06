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
from enmapbox.externals.qps.layerconfigwidgets.gdalmetadata import GDALMetadataModelConfigWidget

class MetadataEditorDialog(QDialog):
    """Constructor."""
    def __init__(self, parent=None):
        super(MetadataEditorDialog, self).__init__(parent, Qt.Window)
        path = pathlib.Path(__file__).parent / 'metadataeditor.ui'
        loadUi(path, self)
        assert isinstance(self.cbSource, QgsMapLayerComboBox)

        self.mdWidget = GDALMetadataModelConfigWidget()
        assert isinstance(self.mdWidget, GDALMetadataModelConfigWidget)
        self.frame.setLayout(QVBoxLayout())
        self.frame.layout().addWidget(self.mdWidget)

        self.cbSource.layerChanged.connect(self.mdWidget.setLayer)
        QgsProject.instance().layersAdded.connect(self.removeDuplicateSources)
        QgsProject.instance().layersRemoved.connect(self.removeDuplicateSources)
        self.removeDuplicateSources()

    def removeDuplicateSources(self):

        sources = []
        excluded = []
        for layer in QgsProject.instance().mapLayers().values():
            if isinstance(layer, QgsMapLayer) and layer.isValid() and layer.source() not in sources:
                sources.append(layer.source())
            else:
                excluded.append(layer)
        self.cbSource.setExceptedLayerList(excluded)



