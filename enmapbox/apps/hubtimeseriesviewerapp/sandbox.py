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
    from enmapbox.gui.sandbox import initQgisEnvironment, sandboxPureGui
    qgsApp = initQgisEnvironment()

    import sys, os
    p = os.environ.get('QGIS_PLUGINPATH')
    if p is None:
        p = r'D:\Repositories\QGIS_Plugins'
    else:
        p = ';'.join(p, r'D:\Repositories\QGIS_Plugins')
    os.environ['QGIS_PLUGINPATH'] = p

    sys.path.append(r'D:\Repositories\QGIS_Plugins')
    pluginDir= os.path.dirname(__import__('hub-timeseriesviewer').__file__)
    sys.path.append(pluginDir)
    sandboxPureGui(loadProcessingFramework=False)

    qgsApp.exec_()
    qgsApp.quit()



if __name__ == '__main__':
    sandboxWithEnMapBox(False)

