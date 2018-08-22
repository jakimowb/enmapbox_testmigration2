# -*- coding: utf-8 -*-

"""
***************************************************************************
    exampleapp/sandbox.py

    An exemplary sandbox to play around and test how and if things work.
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
import sys, os

import enmapbox

"""
Sandbox examples that show how to run own EnMAP-box applications without starting a QGIS GUI Instance

"""
import qgis
def sandboxWithEnMapBox(loadPF=False):
    """
    A minimum example that shows how to load the EnMAP-Box
    :param loadPF: Set on True to initialize the QGIS Processing Framework as well (takes longer)
    :return:
    """
    """Minimum example to the this application"""
    from enmapbox.gui.utils import initQgisApplication, sandboxPureGui
    qgsApp = initQgisEnvironment()
    import enmapbox.gui
    enmapbox.LOAD_PROCESSING_FRAMEWORK = False
    from enmapbox.gui.enmapboxgui import EnMAPBox
    EB = EnMAPBox(None)
    EB.run()


    qgsApp.exec_()
    qgsApp.quit()



if __name__ == '__main__':
    sandboxWithEnMapBox(False)

