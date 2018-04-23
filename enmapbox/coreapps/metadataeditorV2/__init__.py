# -*- coding: utf-8 -*-

"""
***************************************************************************
    exampleapp/__init__.py

    Exemplary EnMAP-Box Application.
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
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtGui import *

APP_DIR = os.path.dirname(__file__)
APP_NAME = 'Metdata Editor'
VERSION = '0.8.15'
LICENSE = 'GPL-3'

from enmapbox.gui.applications import EnMAPBoxApplication
class MetaDataEditorApp(EnMAPBoxApplication):
    """
    This Class inherits from an EnMAPBoxApplication
    """

    def __init__(self, enmapBox, parent=None):
        super(MetaDataEditorApp, self).__init__(enmapBox, parent=parent)

        # specify the name of this app
        self.name = APP_NAME

        # specify a version string

        self.version = VERSION

        # specify a licence under which you distribute this application
        self.licence = LICENSE

    def icon(self):
        """
        This function returns the QIcon of your Application
        :return: QIcon()
        """
        return QIcon(':/enmapbox/icons/enmapbox.png')

    def menu(self, appMenu):
        """
        Returns a QMenu that will be added to the parent `appMenu`
        :param appMenu:
        :return: QMenu
        """
        assert isinstance(appMenu, QMenu)
        """
        Specify menu, submenus and actions that become accessible from the EnMAP-Box GUI
        :return: the QMenu or QAction to be added to the "Applications" menu.
        """

        # this way you can add your QMenu/QAction to an other menu entry, e.g. 'Tools'
        appMenu = self.enmapbox.menu('Tools')

        a = appMenu.addAction(APP_NAME)
        assert isinstance(a, QAction)
        a.triggered.connect(self.startGUI)

        return None

    def startGUI(self):
        from metadataeditorV2.metadataeditor import MetadataEditorDialog
        d = MetadataEditorDialog(parent=self.enmapbox.ui)
        sources = self.enmapbox.dataSources('SPATIAL')
        d.addSources(sources)
        d.show()



def enmapboxApplicationFactory(enmapBox):
    """
    Returns a list of EnMAPBoxApplications
    :param enmapBox: the EnMAP-Box instance.
    :return: EnMAPBoxApplication | [list-of-EnMAPBoxApplications]
    """

    from exampleapp.enmapboxintegration import ExampleEnMAPBoxApp

    # returns a list of EnMAP-Box Applications. Usually only one is returned,
    # but you might provide as many as you like.
    return [ExampleEnMAPBoxApp(enmapBox)]






if __name__ == '__main__':


    from enmapbox.gui.utils import initQgisApplication

    #this will initialize the QApplication/QgsApplication which runs in the background
    #see https://qgis.org/api/classQgsApplication.html for details
    qgsApp = initQgisApplication()


    if False: #test GUI without EnMAP-Box
        from metadataeditorV2.metadataeditor import MetadataEditorDialog
        d = MetadataEditorDialog()
        d.show()
    else:
        from enmapbox.gui.enmapboxgui import EnMAPBox

        EB = EnMAPBox(None)
        EB.run()
        EB.openExampleData(mapWindows=2)
        app = MetaDataEditorApp(EB)

        EB.addApplication(app)

    #start the GUI thread
    qgsApp.exec_()