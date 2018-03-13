# -*- coding: utf-8 -*-

"""
***************************************************************************
    metadataeditor/enmapboxintegration.py

    Integratation of metadata editor into EnMAP-Box.
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
from __future__ import absolute_import, unicode_literals
import os

from PyQt5.QtGui import QIcon
from imagestatisticsapp import APP_DIR

from enmapbox.gui.applications import EnMAPBoxApplication


class ImageStatisticsApp(EnMAPBoxApplication):

    def __init__(self, enmapBox, parent=None):
        super(ImageStatisticsApp, self).__init__(enmapBox, parent=parent)
        self.name = 'Image Statistics'
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
        a = appMenu.addAction('Image Statistics')
        #assert isinstance(a, QAction)
        a.setIcon(self.icon())
        a.triggered.connect(self.startGUI)
        return a

    def startGUI(self, *args):
        from imagestatisticsapp.imagestatistics import Win
        ui = Win(self.enmapbox.ui)
        ui.show()

