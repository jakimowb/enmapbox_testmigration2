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
import pathlib
from qgis.PyQt.QtWidgets import QApplication
from qgis.PyQt.QtGui import QGuiApplication
from qgis.core import QgsApplication

site.addsitedir(pathlib.Path(__file__).parents[1])
import enmapbox
from enmapbox.testing import start_app, QgisMockup
from enmapbox.externals.qps.resources import findQGISResourceFiles


qApp: QgsApplication = None


def exitAll(*args):
    global qApp

    from qgis.utils import iface
    print('## Close all windows')
    QApplication.closeAllWindows()
    QApplication.processEvents()
    print('## Quit QgsApplication')
    QgsApplication.quit()
    print('## QgsApplication down')
    qApp = None


def run(
        sources: list = None,
        initProcessing=False,
        load_core_apps=False, load_other_apps=False,
        debug: bool = False
):
    """
    Starts the EnMAP-Box GUI.
    """
    global qApp
    qAppExists = isinstance(qApp, QgsApplication)
    if not qAppExists:
        print('## Create a QgsApplication...')
        qApp = start_app(resources=findQGISResourceFiles())
        QGuiApplication.instance().lastWindowClosed.connect(qApp.quit)
        print('## QgsApplication created')
    else:
        print('## QgsApplication exists')

    # initialize resources and background frameworks
    # if started from QGIS, this is done by enmapbox/enmapboxplugin.py
    # initialize Qt resources, QgsEditorWidgetWrapper, QgsProcessingProviders etc.
    # enmapbox.initAll(processing=initProcessing)
    from enmapbox.gui.enmapboxgui import EnMAPBox
    import qgis.utils
    enmapBox = EnMAPBox(qgis.utils.iface, load_core_apps=load_core_apps, load_other_apps=load_other_apps)
    enmapBox.run()
    print('## EnMAP-Box started')
    if True and sources is not None:
        for source in enmapBox.addSources(sourceList=sources):
            try:
                # add as map
                lyr = source.createUnregisteredMapLayer()
                dock = enmapBox.createDock('MAP')
                dock.addLayers([lyr])
            except:
                pass

    if not qAppExists:
        print('Execute QgsApplication')
        enmapBox.sigClosed.connect(exitAll)
        return qApp.exec_()
    else:
        return os.EX_OK


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start the EnMAP-Box')
    parser.add_argument('-d', '--debug', required=False, help='Debug mode with more outputs', action='store_true')
    # parser.add_argument('-x', '--no_exec', required=False, help='Close EnMAP-Box if QApplication is not existent',
    #                    action='store_true')
    args = parser.parse_args()

    run(debug=args.debug, initProcessing=True, load_core_apps=True, load_other_apps=True)
    s = ""
