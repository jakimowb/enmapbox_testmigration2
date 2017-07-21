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
    sandboxPureGui(loadProcessingFramework=loadPF)

    qgsApp.exec_()
    qgsApp.quit()


def sandboxGuiOnly():
    """
    Show & Test the GUI, without any EnMAP-Box / QGIS
    :return:
    """
    from enmapbox.gui.sandbox import initQgisEnvironment
    qgsApp = initQgisEnvironment()

    from GUI_ISD import UiFunc, gui
    _ = UiFunc()
    gui.show()
    qgsApp.exec_()
    qgsApp.quit()

if __name__ == '__main__':
    if True:
        sandboxGuiOnly()
    else:
        sandboxWithEnMapBox(loadPF=True)

