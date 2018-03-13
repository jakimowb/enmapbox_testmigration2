# -*- coding: utf-8 -*-

"""
***************************************************************************
    vrtbuilderapp/enmapboxintegration.py

    This module defines the interactions between an application and
    the EnMAPBox.
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
# noinspection PyPep8Naming

from PyQt5.QtGui import QIcon
from enmapbox.gui.applications import EnMAPBoxApplication
from vrtbuilder.widgets import VRTBuilderWidget
from vrtbuilder import VERSION, LICENSE, PATH_ICON


class VRTBuilderApp(EnMAPBoxApplication):
    def __init__(self, enmapBox, parent=None):
        super(VRTBuilderApp, self).__init__(enmapBox, parent=parent)
        self.name = 'Raster Builder'
        self.version = 'Version {}'.format(VERSION)
        self.licence = LICENSE
        self.mapTools = []

    def icon(self):
        return QIcon(PATH_ICON)

    def menu(self, appMenu):
        """
        Specify menu, submenus and actions
        :return: the QMenu or QAction to be added to the "Applications" menu.
        """
        appMenu = self.enmapbox.menu('Tools')
        a = appMenu.addAction('Raster Builder')
        a.setIcon(QIcon(PATH_ICON))
        a.triggered.connect(self.startGUI)
        return None

    def startGUI(self, *args):
        w = VRTBuilderWidget()

        # show EnMAP-Box raster sources in VRTBuilder
        self.enmapbox.sigRasterSourceAdded.connect(lambda path: w.addSourceFiles([path]))

        # populate VRT Builder with raster files known by EnMAP-Box
        w.addSourceFiles(self.enmapbox.dataSources('RASTER'))

        # add created files to EnMAP-Box
        w.sigRasterCreated.connect(self.enmapbox.addSource)
        w.actionSelectSpatialExtent.triggered.connect(lambda: self.onSelectSpatialExtent(w))
        w.show()

    def onSelectSpatialExtent(self, w):
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



    def geoAlgorithms(self):
        return []  # remove this line to load geoAlgorithms
