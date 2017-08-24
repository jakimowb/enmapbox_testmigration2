# -*- coding: utf-8 -*-

"""
***************************************************************************
    exampleapp/enmapboxintegration.py

    This module defines the interactions between an application and
    the EnMAPBox.
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
from __future__ import absolute_import
import os
from PyQt4.QtGui import QIcon, QMenu, QAction
from enmapbox.gui.applications import EnMAPBoxApplication
from synthmix import APP_DIR

class SynthMixEnMAPBoxApp(EnMAPBoxApplication):

    def __init__(self, enmapBox, parent=None):
        super(SynthMixEnMAPBoxApp, self).__init__(enmapBox, parent=parent)
        self.name = 'SynthMix'
        self.version = 'Version 0.8.15'
        self.licence = 'BSD-3'

    def icon(self):
        pathIcon = os.path.join(APP_DIR, 'icon.png')
        return QIcon(pathIcon)

    """
    def menu(self, appMenu):

        #Specify menu, submenus and actions
        #:return: the QMenu or QAction to be added to the "Applications" menu.

        if False:
            # this way you can add your QMenu/QAction to
            # any other EnMAP-Box Menu
            appMenu = self.enmapbox.menu('Tools')

        menu = appMenu.addMenu('Example App')
        menu.setIcon(self.icon())

        #add a QAction that starts your GUI
        a = menu.addAction('Show ExampleApp GUI')
        a.triggered.connect(self.startGUI)

        appMenu.addMenu(menu)

        return menu


    def startGUI(self, *args):
        from exampleapp.userinterfaces import ExampleGUI
        ui = ExampleGUI(self.enmapbox.ui)
        ui.show()

    def startNDVIGui(self, *args):
        from exampleapp.userinterfaces import MyNDVIUserInterface
        ui = MyNDVIUserInterface(self.enmapbox.ui)

        #let the EnMAP Box know if a new file is created
        ui.sigFileCreated.connect(self.enmapbox.addSource)
        ui.show()
    """
    def geoAlgorithms(self):
        #return the SynthMixGeoAlgorithms

        return []



### Interfaces to use algorithms in algorithms.py within
### QGIS Processing Framework

from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import ParameterRaster
from processing.core.outputs import OutputRaster
class SynthMixGeoAlgorithm(GeoAlgorithm):

        def defineCharacteristics(self):
            self.name = 'SynthMix'
            self.group = 'SynthMix'
            self.addParameter(ParameterRaster('infile', 'Spectral Image'))
            self.addOutput(OutputRaster('outfile', '<output todo>'))

        def processAlgorithm(self, progress):
            #map processing framework parameters to that of you algorithm
            infile = self.getParameterValue('infile')
            outfile = self.getOutputValue('outfile')

            #define
            #todo:


        def help(self):
            return True, '<todo: describe synthmix>'


