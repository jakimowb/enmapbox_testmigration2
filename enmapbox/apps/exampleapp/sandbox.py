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
This sandbox can be used to run your EnMAP-Box Application without starting a (heavy) QGIS Instance.
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
    sandboxPureGui(loadProcessingFramework=loadPF)

    qgsApp.exec_()
    qgsApp.quit()


def sandboxGuiOnly():
    """
    Show & Test the GUI, without any EnMAP-Box / QGIS
    :return:
    """
    from enmapbox.gui.utils import initQgisApplication
    qgsApp = initQgisApplication()
    from userinterfaces import ExampleGUI
    ui1 = ExampleGUI()
    ui1.show()
    qgsApp.exec_()
    qgsApp.quit()

if __name__ == '__main__':
    if False: sandboxGuiOnly()
    if True: sandboxWithEnMapBox(True)

