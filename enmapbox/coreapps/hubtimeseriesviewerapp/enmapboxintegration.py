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

import os, sys, importlib
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QMenu, QAction
from enmapbox.gui.applications import EnMAPBoxApplication


import qgis.utils
qgis.utils.updateAvailablePlugins()
PLUGIN_INSTALLED = importlib.find_spec('timeseriesviewer') is not None
#PLUGIN_INSTALLED = qgis.utils.loadPlugin('timeseriesviewer')
s = ""

class HUBTimeSeriesViewerApp(EnMAPBoxApplication):


    def __init__(self, enmapBox, parent=None):

        super(HUBTimeSeriesViewerApp, self).__init__(enmapBox,parent=parent)
        if PLUGIN_INSTALLED:
            import timeseriesviewer
            self.name = timeseriesviewer.TITLE
            self.version = timeseriesviewer.VERSION
            self.licence = 'GNU GPL-3'

    def icon(self):
        if PLUGIN_INSTALLED:
            import timeseriesviewer
            return timeseriesviewer.icon()
        else:
            return None

    def menu(self, appMenu):
        if PLUGIN_INSTALLED:
            a = appMenu.addAction(self.name)
            a.setIcon(self.icon())
            a.triggered.connect(self.startGUI)
            return a
        return None

    def startGUI(self, *args):
        from timeseriesviewer.main import TimeSeriesViewer
        self.tsv = TimeSeriesViewer(self.enmapbox.iface)
        self.tsv.run()
