# -*- coding: utf-8 -*-

"""
***************************************************************************
    hubtimeseriesviewer/enmapboxintegration.py


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

import os, sys
from PyQt4.QtGui import QIcon, QMenu, QAction
from enmapbox.gui.applications import EnMAPBoxApplication
from hubtimeseriesviewerapp import APP_DIR

import qgis.utils
qgis.utils.updateAvailablePlugins()

PLUGIN_INSTALLED = qgis.utils.loadPlugin('timeseriesviewer')

s = ""

class HUBTimeSeriesViewerApp(EnMAPBoxApplication):


    def __init__(self, enmapBox, parent=None):

        super(HUBTimeSeriesViewerApp, self).__init__(enmapBox,parent=parent)

        import timeseriesviewer
        self.name = timeseriesviewer.TITLE
        self.version = timeseriesviewer.VERSION
        self.licence = timeseriesviewer.LICENSE

    def icon(self):
        import timeseriesviewer
        return timeseriesviewer.icon()

    def menu(self, appMenu):
        """
        Specify menu, submenus and actions
        :return:
        """
        #appMenu = self.enmapbox.menu('Tools')
        a = appMenu.addAction(self.name)
        a.setIcon(self.icon())
        a.triggered.connect(self.startGUI)

        return None


    def startGUI(self, *args):
        from timeseriesviewer.main import TimeSeriesViewer
        self.tsv = TimeSeriesViewer(self.enmapbox.iface)
        self.tsv.run()
