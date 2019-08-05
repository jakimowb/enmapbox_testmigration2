# -*- coding: utf-8 -*-

"""
***************************************************************************
    exampleapp/enmapboxintegration.py

    This file shows how to integrate your own algorithms and user interfaces into the EnMAP-Box.
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
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QMenu, QAction
from enmapbox.gui.applications import EnMAPBoxApplication
from lmuvegetationapps import APP_DIR

class LMU_EnMAPBoxApp(EnMAPBoxApplication):
    def __init__(self, enmapBox, parent=None):
        super(LMU_EnMAPBoxApp, self).__init__(enmapBox,parent=parent)
        self.name = 'Agricultural Applications'
        self.version = 'Version 0.42'
        self.licence = 'BSD-3'

    def icon(self):
        pathIcon = os.path.join(APP_DIR, 'icon.png')
        return QIcon(pathIcon)

    def menu(self, appMenu):
        """
        Specify menu, submenus and actions
        :return: the QMenu or QAction to be added to the "Applications" menu.
        """

        if True:
            # this way you can add your QMenu/QAction to
            # any other EnMAP-Box Menu
            appMenu = self.enmapbox.menu('Applications')

        menu = QMenu(self.name, appMenu)
        menu.setIcon(self.icon())

        a = menu.addAction('Interactive Visualization of Vegetation Reflectance Models (IVVRM)')
        a.triggered.connect(self.start_GUI_IVVRM)

        b = menu.addAction('Create Look-up-table')
        b.triggered.connect(self.start_GUI_LUT)

        c = menu.addAction('Invert Look-up-table')
        c.triggered.connect(self.start_GUI_Inv)

        d = menu.addAction('Vegetation Indices Toolbox')
        d.triggered.connect(self.start_GUI_VIT)

        e = menu.addAction('Plant Water Retrieval (PWR)')
        e.triggered.connect(self.start_GUI_PWR)

        e = menu.addAction('Analyze Spectral Integral (ASI)')
        e.triggered.connect(self.start_GUI_ASI)

        appMenu.addMenu(menu)
        return menu

    def start_GUI_IVVRM(self, *args):
        from lmuvegetationapps.IVVRM_GUI import MainUiFunc
        m = MainUiFunc()
        m.show()
        # #the the EnMAP-Box know if you create any new file
        # gui1.sigFileCreated.connect(self.enmapbox.addSource)

    def start_GUI_LUT(self, *args):
        from lmuvegetationapps.LUT_GUI import MainUiFunc
        m = MainUiFunc()
        m.show()

    def start_GUI_Inv(self, *args):
        from lmuvegetationapps.Global_Inversion_GUI import MainUiFunc
        m = MainUiFunc()
        m.show()

    def start_GUI_VIT(self, *args):
        from lmuvegetationapps.VIT_GUI import MainUiFunc
        m = MainUiFunc()
        m.show()

    def start_GUI_PWR(self, *args):
        from lmuvegetationapps.PWR_GUI import MainUiFunc
        m = MainUiFunc()
        m.show()

    def start_GUI_ASI(self, *args):
        from lmuvegetationapps.ASI import MainUiFunc
        m = MainUiFunc()
        m.show()

    def start_GUI_iREIP(self, *args):
        from lmuvegetationapps.iREIP import MainUiFunc
        m = MainUiFunc()
        m.show()


### Interfaces to use algorithms in algorithms.py within
### QGIS Processing Framework


