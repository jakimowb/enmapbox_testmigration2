# -*- coding: utf-8 -*-

"""
***************************************************************************
    scatterplottapp/enmapboxintegration.py

    Integratation of metadata editor into EnMAP-Box.
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

import os

from PyQt5.QtGui import QIcon
from scatterplotapp import APP_DIR

from enmapbox.gui.applications import EnMAPBoxApplication


class ScatterplotApp(EnMAPBoxApplication):

    def __init__(self, enmapBox, parent=None):
        super(ScatterplotApp, self).__init__(enmapBox, parent=parent)
        self.name = 'Scatterplot'
        self.version = 'Version 0.1'
        self.licence = 'GPL-3'

    def icon(self):
        pathIcon = os.path.join(APP_DIR, 'icon.png')
        return QIcon(pathIcon)

    def menu(self, appMenu):
        """
        Specify menu, submenus and actions
        :return: the QMenu or QAction to be added to the "Applications" menu.
        """
        appMenu = self.enmapbox.menu('Tools')

        #add a QAction that starts your GUI
        a = appMenu.addAction('Scatterplot')
        #assert isinstance(a, QAction)
        a.setIcon(self.icon())
        a.triggered.connect(self.startGUI)
        return a


    def startGUI(self, *args):
        from scatterplotapp.scatterplott import Win
        ui = Win(self.enmapbox.ui)
        ui.show()
        #uiDialog = QDialog(self.enmapbox.ui)
        #uiDialog.setWindowTitle('Dummy')
        #uiDialog.show()
