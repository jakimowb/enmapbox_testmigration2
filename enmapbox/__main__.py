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
***************************************************************************
"""
from __future__ import absolute_import
import sys, os
from qgis.core import *

def run():
    from enmapbox.gui.enmapboxgui import EnMAPBox
    from enmapbox.gui.sandbox import initQgisEnvironment
    from qgis.utils import iface
    import enmapbox.gui
    enmapbox.gui.LOAD_PROCESSING_FRAMEWORK = True
    enmapbox.gui.LOAD_EXTERNAL_APPS = True
    qgisApp = initQgisEnvironment()
    enmapbox = EnMAPBox(iface)
    enmapbox.run()
    qgisApp.exec_()


if __name__ == '__main__':
    sys.path.remove(os.path.dirname(__file__))
    args = sys.argv[1:]

    #todo: add command line options

    run()
