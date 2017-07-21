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
from PyQt4.QtGui import QIcon, QMenu, QAction
from enmapbox.gui.applications import EnMAPBoxApplication
from the_lmu_app import APP_DIR
class LMU_EnMAPBoxApp(EnMAPBoxApplication):

    def __init__(self, enmapBox, parent=None):
        super(LMU_EnMAPBoxApp, self).__init__(enmapBox,parent=parent)
        self.name = 'Eine LMU EnMAPBox Application'
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

        #add a QAction that starts your GUI
        a = menu.addAction('GUI 1')
        a.triggered.connect(self.startGUI1)

        # add another QAction
        a = menu.addAction('GUI 2')
        from exampleapp.userinterfaces import MyNDVIUserInterface
        #todo: connect this action with something meaningful
        #a.triggered.connect(self.startNDVIGui)

        appMenu.addMenu(menu)

        return menu


    def startGUI1(self, *args):
        # from .userinterfaces import GUI1
        # ui = GUI1(parent=self.enmapbox.ui)
        # ui.show()
        #
        # #the the EnMAP-Box know if you create any new file
        # ui.sigFileCreated.connect(self.enmapbox.addSource)

        from GUI_ISD import UiFunc, gui
        gui1 = UiFunc(parent=self.enmapbox.ui)
        gui.show()
        #the the EnMAP-Box know if you create any new file
        gui1.sigFileCreated.connect(self.enmapbox.addSource)

    def geoAlgorithms(self):
        return [LMU_GeoAlgorithm()]



### Interfaces to use algorithms in algorithms.py within
### QGIS Processing Framework

from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import ParameterRaster
from processing.core.outputs import OutputRaster
class LMU_GeoAlgorithm(GeoAlgorithm):

        def defineCharacteristics(self):
            self.name = 'Dummy Algorithm'
            self.group = 'LMU Apps'

            self.addParameter(ParameterRaster('infile', 'Input Image'))
            self.addOutput(OutputRaster('outfile', 'Output Image'))

        def processAlgorithm(self, progress):
            from .algorithms import dummyAlgorithm
            #map processing framework parameters to that of you algorithm
            infile = self.getParameterValue('infile')
            outfile = self.getOutputValue('outfile')

            raise NotImplementedError()


        def help(self):
            return True, 'Calculates the NDVI using GDAL'


