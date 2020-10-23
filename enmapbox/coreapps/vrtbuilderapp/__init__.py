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

import importlib
import typing
import os
from qgis.PyQt.QtWidgets import QMessageBox, QMainWindow
from qgis.PyQt.QtGui import QIcon
from qgis.gui import QgsMapCanvas, QgisInterface, QgsMapTool
import qgis.utils
from enmapbox.gui.applications import EnMAPBoxApplication
from enmapbox.gui.enmapboxgui import EnMAPBox

APP_DIR = os.path.dirname(__file__)
MIN_VERSION = '0.9'

def vrtBuilderPluginInstalled() -> bool:
    """
    Returns True if the Virtual Raster Builder QGIS Plugin is installed
    :return: bool
    """
    qgis.utils.updateAvailablePlugins()
    return importlib.util.find_spec('vrtbuilder') is not None


if vrtBuilderPluginInstalled():
    from vrtbuilder.widgets import VRTBuilderWidget, VRTBuilderMapTools
    from vrtbuilder import LICENSE, PATH_ICON
    try:
        from vrtbuilder import __version__ as VRTBVersion
    except:
        from vrtbuilder import VERSION as VRTBVersion



class VRTBuilderApp(EnMAPBoxApplication):
    def __init__(self, enmapBox, parent=None):
        super(VRTBuilderApp, self).__init__(enmapBox, parent=parent)
        self.name = 'Virtual Raster Builder'

        self.mIsInstalled = vrtBuilderPluginInstalled()
        self.mInstance = None

        if self.mIsInstalled:
            self.version = 'Version {}'.format(VRTBVersion)
            self.licence = LICENSE
            self.mIcon = QIcon(PATH_ICON)
        else:
            self.version = 'Unknown'
            self.licence = 'Unknown'
            self.mIcon = QIcon()

    def icon(self) -> QIcon:
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

    def startGUI(self, *args) -> QMainWindow:

        if vrtBuilderPluginInstalled():

            if MIN_VERSION > VRTBVersion:
                QMessageBox.information(None, 'Outdated Version',
                                        'Please update the Virtual Raster Builder QGIS Plugin.')
                return None
            else:
                w = VRTBuilderWidget()
                # show EnMAP-Box raster sources in VRTBuilder
                self.enmapbox.sigRasterSourceAdded.connect(lambda path: w.addSourceFiles([path]))

                # populate VRT Builder with raster files known to the EnMAP-Box
                w.addSourceFiles(self.enmapbox.dataSources('RASTER'))

                # add created virtual raster to EnMAP-Box
                w.sigRasterCreated.connect(self.enmapbox.addSource)

                w.sigAboutCreateCurrentMapTools.connect(self.onSetWidgetMapTool)

                w.show()
                return w
        else:
            QMessageBox.information(None, 'Missing QGIS Plugin',
                                    'Please install and activate the Virtual Raster Builder QGIS Plugin.')
            return None

    def onSetWidgetMapTool(self):
        w = self.sender()

        if not self.mIsInstalled:
            return
        from vrtbuilder.widgets import VRTBuilderWidget, SpatialExtentMapTool
        assert isinstance(w, VRTBuilderWidget)
        canvases = []

        if isinstance(self.enmapbox, EnMAPBox):
            canvases.extend(self.enmapbox.mapCanvases())

        if isinstance(qgis.utils.iface, QgisInterface):
            canvases.extend(qgis.utils.iface.mapCanvases())

        canvases = set(canvases)
        for mapCanvas in canvases:
            assert isinstance(mapCanvas, QgsMapCanvas)
            w.createCurrentMapTool(mapCanvas)


def enmapboxApplicationFactory(enmapBox):
    """
    Returns a list of EnMAPBoxApplications
    :param enmapBox: the EnMAP-Box instance.
    :return: EnMAPBoxApplication | [list-of-EnMAPBoxApplications]
    """
    return [VRTBuilderApp(enmapBox)]
