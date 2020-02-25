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
import os, sys, site, importlib, pathlib

from qgis.core import QgsApplication, QgsProcessingProvider, QgsProcessingAlgorithm, Qgis
from qgis.gui import QgisInterface
from qgis.PyQt.QtCore import QTimer, QOperatingSystemVersion
from qgis.PyQt.QtWidgets import QAction

import numpy as np



class EnMAPBoxPlugin(object):

    def __init__(self, iface):
        # make site-packages available to python
        assert isinstance(iface, QgisInterface)
        self.iface = iface


        if QOperatingSystemVersion.current().name() == 'macOS':
            # os.environ['SKLEARN_SITE_JOBLIB']='True'True
            # fix for issue #221
            os.environ['JOBLIB_MULTIPROCESSING'] = '0'

        pathes = sys.path[:]
        dirPlugin = os.path.dirname(__file__)
        site.addsitedir(dirPlugin)
        import enmapbox

        site.addsitedir(enmapbox.DIR_SITEPACKAGES)

        #run a dependency check
        self.initialDependencyCheck()

        # initialize resources etc.
        enmapbox.initAll()

        # add the EnMAP-Box Provider
        enmapbox.initEnMAPBoxProcessingProvider()

        #assert self.enmapBoxProvider == QgsApplication.instance().processingRegistry().providerById('enmapbox')

        self.mAddedSysPaths = [p for p in sys.path if p not in pathes]

    def initialDependencyCheck(self):
        """
        Runs a check for availability of package dependencies and give an readible error message
        :return:
        """
        from enmapbox import DEPENDENCIES, messageLog, DIR_REPO
        from enmapbox.dependencycheck import missingPackages, missingPackageInfo
        missing = missingPackages(DEPENDENCIES)
        if len(missing) > 0:
            raise Exception(missingPackageInfo(missing))

    def initGui(self):

        self.toolbarActions = []

        from enmapbox.gui.enmapboxgui import EnMAPBox
        import enmapbox
        self.enmapBox = None
        action = QAction(enmapbox.icon(), 'EnMAP-Box', self.iface)
        self.iface.addPluginToRasterMenu('EnMAP-Box', action)

        action.triggered.connect(self.run)
        self.toolbarActions.append(action)
        for action in self.toolbarActions:
            self.iface.addToolBarIcon(action)

    def run(self):
        from enmapbox.gui.enmapboxgui import EnMAPBox
        self.enmapBox = EnMAPBox.instance()
        if not isinstance(self.enmapBox, EnMAPBox):
            #print('STARTED NEW BOX')
            self.enmapBox = EnMAPBox(self.iface)
            assert self.enmapBox == EnMAPBox.instance()
            self.enmapBox.run()
            s = ""
        else:
            #print('FOUND BOX')
            self.enmapBox.ui.show()

    def unload(self):
        from enmapbox.gui.enmapboxgui import EnMAPBox
        for action in self.toolbarActions:
            self.iface.removeToolBarIcon(action)

        if isinstance(EnMAPBox.instance(), EnMAPBox):
            EnMAPBox.instance().close()
        EnMAPBox._instance = None

        from enmapbox.algorithmprovider import ID
        QgsApplication.instance().processingRegistry().removeProvider(ID)





