# -*- coding: utf-8 -*-

"""
***************************************************************************
    minimumexample/exampleapp.py

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

import os
from PyQt5.QtGui import QIcon, QMenu, QAction
from enmapbox.gui.applications import EnMAPBoxApplication

VERSION = '0.0.1'
LICENSE = 'GNU GPL-3'
APP_DIR = os.path.dirname(__file__)

class ExampleEnMAPBoxApp(EnMAPBoxApplication):
    """
    This Class derived from an EnMAPBoxApplication.

    """
    def __init__(self, enmapBox, parent=None):
        super(ExampleEnMAPBoxApp, self).__init__(enmapBox, parent=parent)

        #specify the name of this app
        self.name = 'My First EnMAPBox App'

        #specify a version string

        self.version = VERSION

        #specify a licence under which you distribute this application
        self.licence = LICENSE

    def icon(self):
        """
        This function returns the QIcon of your Application
        :return: QIcon()
        """
        return QIcon(os.path.join(APP_DIR, 'icon.png'))

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
        # appMenu = self.enmapbox.menu('Tools')

        menu = appMenu.addMenu('My Example App')
        menu.setIcon(self.icon())

        #add a QAction that starts a process of your application.
        #In this case it will open your GUI.
        a = menu.addAction('Show ExampleApp GUI')
        a.triggered.connect(self.startGUI)

        appMenu.addMenu(menu)

        return menu

    def geoAlgorithms(self):
        """
        This function returns the QGIS Processing Framework GeoAlgorithms specified by your application
        :return: [list-of-GeoAlgorithms]
        """
        #return [] #remove this line to load geoAlgorithms
        from algorithms import MyEnMAPBoxAppGeoAlgorithm
        return [MyEnMAPBoxAppGeoAlgorithm()]

    def startGUI(self, *args):

        w = QWidget()
        w.setTitle(self.name)
        l = QVBoxLayout()
        l.addWidget(QLabel('Hello World'))
        btn = QPushButton('Click me')
        btn.clicked.connect(lambda : print('Hello World'))
        w.setLayout(Q)
        w.show()





