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

import os
from PyQt4.QtGui import QIcon, QMenu, QAction
from enmapbox.gui.applications import EnMAPBoxApplication
from exampleapp import APP_DIR
from vrtbuilder.widgets import VRTBuilderWidget
from vrtbuilder import VERSION, LICENSE, PATH_ICON

class VRTBuilderApp(EnMAPBoxApplication):

    def __init__(self, enmapBox, parent=None):
        super(VRTBuilderApp, self).__init__(enmapBox, parent=parent)
        self.name = 'Raster Builder'
        self.version = 'Version {}'.format(VERSION)
        self.licence = LICENSE

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
        w.sigRasterCreated.connect(self.enmapbox.addSource)
        w.addSourceFiles(self.enmapbox.dataSources('RASTER'))
        w.show()

    def geoAlgorithms(self):
        return [] #remove this line to load geoAlgorithms

