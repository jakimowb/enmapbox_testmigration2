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
import pathlib
from qgis.PyQt.QtWidgets import QVBoxLayout, QDialogButtonBox, QDialog
from qgis.PyQt.QtCore import Qt
from enmapbox.qgispluginsupport.qps.layerconfigwidgets.gdalmetadata import GDALMetadataModelConfigWidget
from enmapbox.gui.utils import loadUi
from enmapbox.gui.enmapboxgui import EnMAPBox, SpatialDataSource

from qgis.core import QgsProject, QgsMapLayer
from qgis.gui import QgsMapLayerComboBox


class MetadataEditorDialog(QDialog):
    """Constructor."""
    def __init__(self, parent=None):
        super(MetadataEditorDialog, self).__init__(parent, Qt.Window)
        path = pathlib.Path(__file__).parent / 'metadataeditor.ui'
        loadUi(path, self)
        assert isinstance(self.cbSource, QgsMapLayerComboBox)

        self.mdWidget: GDALMetadataModelConfigWidget = GDALMetadataModelConfigWidget()
        self.mdWidget.metadataModel.setIsEditable(True)
        self.frame.setLayout(QVBoxLayout())
        self.frame.layout().addWidget(self.mdWidget)

        self.cbSource.layerChanged.connect(self.mdWidget.setLayer)
        QgsProject.instance().layersAdded.connect(self.removeDuplicateSources)
        QgsProject.instance().layersRemoved.connect(self.removeDuplicateSources)
        self.removeDuplicateSources()
        self.mdWidget.setLayer(self.cbSource.currentLayer())
        self.buttonBox.button(QDialogButtonBox.Close).clicked.connect(self.close)
        self.buttonBox.button(QDialogButtonBox.Save).clicked.connect(self.mdWidget.apply)

    def removeDuplicateSources(self):

        sources = []
        excluded = []

        existingLayers = QgsProject.instance().mapLayers().values()
        emb = EnMAPBox.instance()

        if isinstance(emb, EnMAPBox):
            dataSourceLayers = [source.asMapLayer()
                                for source in emb.dataSourceManager().dataSources()
                                if isinstance(source, SpatialDataSource)]
            existingLayers = sorted(existingLayers, key=lambda lyr: lyr in dataSourceLayers)

        for layer in existingLayers:
            if isinstance(layer, QgsMapLayer) and layer.isValid() and layer.source() not in sources:
                sources.append(layer.source())
            else:
                excluded.append(layer)
        self.cbSource.setExceptedLayerList(excluded)



