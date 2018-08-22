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

import sys, os, site

import enmapbox


def run():
    """
    Starts the EnMAP-Box GUI.
    :return:
    """

    from enmapbox.gui.utils import initQgisApplication
    qgisApp = initQgisApplication()

    from enmapbox.gui.enmapboxgui import EnMAPBox
    import enmapbox.gui
    enmapbox.DEBUG = False
    enmapbox.LOAD_PROCESSING_FRAMEWORK = True
    enmapbox.LOAD_EXTERNAL_APPS = True

    from qgis.utils import iface
    enmapbox = EnMAPBox(iface)
    enmapbox.run()
    qgisApp.exec_()


if __name__ == '__main__':
    thisDir = os.path.dirname(__file__)
    if thisDir in sys.path:
        sys.path.remove(thisDir)

    args = sys.argv[1:]


    run()
