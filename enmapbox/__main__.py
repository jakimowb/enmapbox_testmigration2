# -*- coding: utf-8 -*-

"""
***************************************************************************
    __main__
    ---------------------
    Date                 : August 2017
    Copyright            : (C) 2017 by Benjamin Jakimow
    Email                : benjamin.jakimow@geo.hu-berlin.de
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
**************************************************************************
"""

import sys
import os
import site
import argparse
from qgis.PyQt.QtWidgets import QApplication
import qgis.testing


def run(sources: list = None, debug: bool = False):
    """
    Starts the EnMAP-Box GUI.
    """
    from enmapbox.testing import initQgisApplication
    from enmapbox.externals.qps.resources import findQGISResourceFiles
    qgisApp = initQgisApplication(resources=findQGISResourceFiles())
    import enmapbox

    enmapbox.DEBUG = debug is True

    # initialize resources and background frameworks
    # if started from QGIS, this is done by enmapbox/enmapboxplugin.py
    # initialize Qt resources, QgsEditorWidgetWrapper, QgsProcessingProviders etc.
    enmapbox.initAll()

    from enmapbox.gui.enmapboxgui import EnMAPBox

    import qgis.utils
    enmapBox = EnMAPBox(qgis.utils.iface)
    enmapBox.run()
    if sources is not None:
        for source in enmapBox.addSources(sourceList=sources):
            try:
                # add as map
                lyr = source.createUnregisteredMapLayer()
                dock = enmapBox.createDock('MAP')
                dock.addLayers([lyr])
            except:
                pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start the EnMAP-Box')
    parser.add_argument('-d', '--debug', required=False, help='Debug mode with more outputs', action='store_true')
    parser.add_argument('-x', '--no_exec', required=False, help='Close EnMAP-Box if QApplication is not existent', action='store_true')
    args = parser.parse_args()

    app_exists = isinstance(QApplication.instance(), QApplication)
    run(debug=args.debug)
    if not app_exists and not args.no_exec:
        QApplication.instance().exec_()
    else:
        print('Finished enmapbox.__main__.py')
