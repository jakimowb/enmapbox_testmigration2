# -*- coding: utf-8 -*-

"""
***************************************************************************
    hubreclassify/enmapboxintegration.py

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
from PyQt4.QtGui import QIcon, QMenu, QAction
from enmapbox.gui.applications import EnMAPBoxApplication
from exampleapp import APP_DIR
class ReclassifyTool(EnMAPBoxApplication):

    def __init__(self, enmapBox, parent=None):
        super(ReclassifyTool, self).__init__(enmapBox, parent=parent)
        self.name = 'My EnMAPBox App'
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

        if False:
            # this way you can add your QMenu/QAction to
            # any other EnMAP-Box Menu
            appMenu = self.enmapbox.menu('Tools')

        menu = QMenu(self.name, appMenu)
        menu.setIcon(self.icon())

        #add a QAction that starts your GUI
        a = menu.addAction('Show My GUI')
        a.triggered.connect(self.startGUI)

        # add another QAction
        a = menu.addAction('Calculate NDVI')
        from exampleapp.userinterfaces import MyNDVIUserInterface
        a.triggered.connect(self.startNDVIGui)

        #add a Submenu
        subMenu = menu.addMenu('Submenu')
        #add QAction to run another process
        a = subMenu.addAction('Start Process')
        from algorithms import dummyAlgorithm
        a.triggered.connect(lambda : dummyAlgorithm('My', 'App Action', 'got triggered'))


        appMenu.addMenu(menu)

        return menu


    def startGUI(self, *args):
        from exampleapp.userinterfaces import MyAppUserInterface
        ui = MyAppUserInterface(self.enmapbox.ui)
        ui.show()

    def startNDVIGui(self, *args):
        from exampleapp.userinterfaces import MyNDVIUserInterface
        ui = MyNDVIUserInterface(self.enmapbox.ui)

        #let the EnMAP Box know if a new file is created
        ui.sigFileCreated.connect(self.enmapbox.addSource)
        ui.show()

    def geoAlgorithms(self):
        return [MyEnMAPBoxAppGeoAlgorithm()]



### Interfaces to use algorithms in algorithms.py within
### QGIS Processing Framework

from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import ParameterRaster
from processing.core.outputs import OutputRaster
class MyEnMAPBoxAppGeoAlgorithm(GeoAlgorithm):

        def defineCharacteristics(self):
            self.name = 'NDVI (using GDAL)'
            self.group = 'My Example App'

            self.addParameter(ParameterRaster('infile', 'Spectral Image'))
            self.addOutput(OutputRaster('outfile', 'NDVI'))

        def processAlgorithm(self, progress):
            from .algorithms import ndvi
            #map processing framework parameters to that of you algorithm
            infile = self.getParameterValue('infile')
            outfile = self.getOutputValue('outfile')
            ndvi(infile, outfile, progress=progress)

        def help(self):
            return True, 'Calculates the NDVI using GDAL'


