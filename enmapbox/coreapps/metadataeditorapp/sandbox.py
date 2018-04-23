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
def sandboxShowAppInEnMapBox(loadPF=False):
    """
    A minimum example that shows how to load the EnMAP-Box
    :param loadPF: Set on True to initialize the QGIS Processing Framework (takes longer).
    This is required if your app contributes GeoAlgorithms to the EnMAPBoxAlgorithmProvider.
    """
    """Minimum example to the this application"""

    import enmapbox.gui

    enmapbox.gui.LOAD_PROCESSING_FRAMEWORK = loadPF
    from enmapbox.gui.enmapboxgui import EnMAPBox
    EB = EnMAPBox(None)
    EB.run()
    EB.openExampleData(mapWindows=2)

    #now load your App into the EnMAP-Box
    import os
    appDir = os.path.dirname(__file__)
    EB.addApplication(appDir)



def sandboxShowAppGuiOnly():
    """
    Show & Test the GUI, without any EnMAP-Box / QGIS
    :return:
    """
    from metadataeditorapp.metadataeditor import MetadataEditorDialog
    from enmapboxtestdata import enmap, hymap
    ui = MetadataEditorDialog()
    ui.addSources(hymap)
   # ui.setSource(enmap)
    ui.show()

if __name__ == '__main__':


    from enmapbox.gui.utils import initQgisApplication

    #this will initialize the QApplication/QgsApplication which runs in the background
    #see https://qgis.org/api/classQgsApplication.html for details
    qgsApp = initQgisApplication()

    if False:
        sandboxShowAppGuiOnly()
    if True:
        sandboxShowAppInEnMapBox(True)


    #start the GUI thread
    qgsApp.exec_()

