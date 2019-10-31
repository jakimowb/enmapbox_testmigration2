# -*- coding: utf-8 -*-

"""
***************************************************************************
    hubtimeseriesviewer/__init__.py

    Package definition of HUB TimeSeriesViewer for EnMAP-Box
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
import qgis.utils
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QMenu, QAction
from enmapbox.gui.applications import EnMAPBoxApplication

APP_DIR = os.path.dirname(__file__)

def timeseriesviewerPluginInstalled()->bool:
    qgis.utils.updateAvailablePlugins()
    return importlib.util.find_spec('eotimeseriesviewer') is not None


class EOTimeSeriesViewerApp(EnMAPBoxApplication):


    def __init__(self, enmapBox, parent=None):

        super(EOTimeSeriesViewerApp, self).__init__(enmapBox, parent=parent)
        self.mPluginInstalled = timeseriesviewerPluginInstalled()
        if self.mPluginInstalled:
            import eotimeseriesviewer
            self.name = eotimeseriesviewer.TITLE
            self.version = eotimeseriesviewer.__version__
            self.licence = 'GNU GPL-3'


    def icon(self):
        if self.mPluginInstalled:
            import eotimeseriesviewer
            return eotimeseriesviewer.icon()
        else:
            return None

    def menu(self, appMenu):
        if self.mPluginInstalled:
            a = appMenu.addAction(self.name)
            a.setIcon(self.icon())
            a.triggered.connect(self.startGUI)
            return a
        return None

    def startGUI(self, *args):
        from eotimeseriesviewer.main import TimeSeriesViewer
        self.tsv = TimeSeriesViewer()
        self.tsv.show()



def enmapboxApplicationFactory(enmapBox):
    """
    Returns a list of EnMAPBoxApplications
    :param enmapBox: the EnMAP-Box instance.
    :return: [list-of-EnMAPBoxApplications]
    """

    if timeseriesviewerPluginInstalled():
        return [EOTimeSeriesViewerApp(enmapBox)]
    else:
        print('EO Time Series Viewer QGIS Plugin is not installed')
        return []
