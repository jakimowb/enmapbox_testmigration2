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


import os
APP_DIR = os.path.dirname(__file__)


def enmapboxApplicationFactory(enmapBox):
    """
    Returns a list of EnMAPBoxApplications
    :param enmapBox: the EnMAP-Box instance.
    :return: [list-of-EnMAPBoxApplications]
    """
    import hubtimeseriesviewerapp.enmapboxintegration

    if hubtimeseriesviewerapp.enmapboxintegration.PLUGIN_INSTALLED:

        from hubtimeseriesviewerapp.enmapboxintegration import HUBTimeSeriesViewerApp
        #returns a list of EnMAPBoxApplications
        return [HUBTimeSeriesViewerApp(enmapBox)]

    else:
        from qgis.core import QgsMessageLog

        #QgsMessageLog.instance().logMessage('HUB TimeSeriesViewer QGIS Plugin is not installed.',
        #                                    level=QgsMessageLog.INFO)
        return []
