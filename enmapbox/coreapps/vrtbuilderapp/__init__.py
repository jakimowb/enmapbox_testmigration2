# -*- coding: utf-8 -*-

"""
***************************************************************************
    vrtbuilderapp

    An EnMAP-Box Application to start the Virtual Raster Builder QGIS Plugin
    see https://bitbucket.org/jakimowb/virtual-raster-builder for details
    ---------------------
    Date                 : October 2017
    Copyright            : (C) 2017 by Benjamin Jakimow
    Email                : benjamin.jakimow@geo.hu-berlin.de
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 3 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

import os, importlib
APP_DIR = os.path.dirname(__file__)
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.PyQt.QtGui import QIcon
import qgis.utils
from enmapbox.gui.applications import EnMAPBoxApplication

def qgisPluginInstalled()->bool:
    """
    Returns True if the Virtual Raster Builder QGIS Plugin is installed
    :return: bool
    """
    qgis.utils.updateAvailablePlugins()
    return importlib.util.find_spec('vrtbuilder') is not None

class VRTBuilderApp(EnMAPBoxApplication):
    def __init__(self, enmapBox, parent=None):
        super(VRTBuilderApp, self).__init__(enmapBox, parent=parent)
        self.name = 'Virtual Raster Builder'

        self.mIsInstalled = qgisPluginInstalled()
        self.mapTools = []

        if self.mIsInstalled:

            from vrtbuilder import VERSION, LICENSE, PATH_ICON
            self.version = 'Version {}'.format(VERSION)
            self.licence = LICENSE
            self.mIcon = QIcon(PATH_ICON)
        else:
            self.version = 'Unknown'
            self.licence = 'Unknown'
            self.mIcon = QIcon()



    def icon(self)->QIcon:
        return QIcon(self.mIcon)

    def menu(self, appMenu):
        """
        Specify menu, submenus and actions
        :return: the QMenu or QAction to be added to the "Applications" menu.
        """
        appMenu = self.enmapbox.menu('Tools')
        a = appMenu.addAction(self.name)
        a.setIcon(self.icon())
        a.triggered.connect(self.startGUI)
        return None

    def startGUI(self, *args):

        if qgisPluginInstalled():
            from vrtbuilder.widgets import VRTBuilderWidget

            w = VRTBuilderWidget()
            # show EnMAP-Box raster sources in VRTBuilder
            self.enmapbox.sigRasterSourceAdded.connect(lambda path: w.addSourceFiles([path]))

            # populate VRT Builder with raster files known to the EnMAP-Box
            w.addSourceFiles(self.enmapbox.dataSources('RASTER'))

            # add created virtual raster to EnMAP-Box
            w.sigRasterCreated.connect(self.enmapbox.addSource)
            w.actionSelectSpatialExtent.triggered.connect(lambda: self.onSelectSpatialExtent(w))
            w.show()
        else:
            QMessageBox.information(None, 'Missing QGIS Plugin', 'Please install and activate the Virtual Raster Builder QGIS Plugin.')



    def onSelectSpatialExtent(self, w):

        if self.mIsInstalled:
            from vrtbuilder.widgets import VRTBuilderWidget
            assert isinstance(w, VRTBuilderWidget)
            from enmapbox.gui.enmapboxgui import EnMAPBox
            from vrtbuilder.widgets import MapToolSpatialExtent
            del self.mapTools[:]
            if isinstance(self.enmapbox, EnMAPBox):
                for mapCanvas in self.enmapbox.mapCanvases():
                    t = MapToolSpatialExtent(mapCanvas)
                    t.sigSpatialExtentSelected.connect(w.setBounds)
                    mapCanvas.setMapTool(t)
                    self.mapTools.append(t)


def enmapboxApplicationFactory(enmapBox):
    """
    Returns a list of EnMAPBoxApplications
    :param enmapBox: the EnMAP-Box instance.
    :return: EnMAPBoxApplication | [list-of-EnMAPBoxApplications]
    """
    return [VRTBuilderApp(enmapBox)]

