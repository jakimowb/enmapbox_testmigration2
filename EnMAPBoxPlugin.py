# -*- coding: utf-8 -*-

"""
***************************************************************************
    EnMAPBoxPlugin.py
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
from __future__ import absolute_import
import os, sys, logging, traceback
from qgis.gui import QgisInterface
from PyQt4.QtCore import QTimer
from PyQt4.QtGui import QAction


class EnMAPBoxPlugin:

    def __init__(self, iface):
        # make site-packages available to python
        assert isinstance(iface, QgisInterface)
        self.iface = iface

        # ensure that python console is activated. this is required to redirect
        # printouts like that from debugger to stdout / stderr
        import console.console as CONSOLE
        if CONSOLE._console is None:
            CONSOLE._console = CONSOLE.PythonConsole(iface.mainWindow())
            QTimer.singleShot(0, CONSOLE._console.activate)

        # set the logger
        import enmapbox.gui
        if enmapbox.gui.DEBUG:
            logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)

    def initGui(self):
        self.logger.debug('initGui...')
        self.toolbarActions = []

        from enmapbox.gui.enmapboxgui import EnMAPBox

        self.enmapBox = None


        action = QAction(EnMAPBox.getIcon(), u'EnMAP-Box', self.iface)
        action.triggered.connect(self.run)
        self.toolbarActions.append(action)
        for action in self.toolbarActions:
            self.iface.addToolBarIcon(action)

    def unload(self):
        from enmapbox.gui.enmapboxgui import EnMAPBox
        for action in self.toolbarActions:
            self.iface.removeToolBarIcon(action)

        if isinstance(self.enmapBox, EnMAPBox):
            self.enmapBox = None
            EnMAPBox._instance = None

    def run(self):
        from enmapbox.gui.enmapboxgui import EnMAPBox
        self.enmapBox = EnMAPBox.instance()
        if not isinstance(self.enmapBox, EnMAPBox):
            self.enmapBox = EnMAPBox(self.iface)
        self.enmapBox.run()

