# -*- coding: utf-8 -*-
# noinspection PyPep8Naming
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
import os
import sys
import site
import pathlib
import warnings
import typing

from PyQt5.QtCore import Qt
from qgis.core import Qgis
from qgis.gui import QgisInterface
from qgis.PyQt.QtCore import QOperatingSystemVersion
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon


class EnMAPBoxPlugin(object):

    def __init__(self, iface):
        # make site-packages available to python

        self.pluginToolbarActions: typing.List[QAction] = []
        self.rasterMenuActions: typing.List[QAction] = []
        if QOperatingSystemVersion.current().name() == 'macOS':
            # os.environ['SKLEARN_SITE_JOBLIB']='True'True
            # fix for issue #221
            os.environ['JOBLIB_MULTIPROCESSING'] = '0'

        pathes = sys.path[:]

        import enmapbox
        enmapbox.initPythonPaths()
        # run a minimum dependency check
        self.initialDependencyCheck()

        # initialize resources, processing provider etc.
        enmapbox.initAll()

        self.mAddedSysPaths = [p for p in sys.path if p not in pathes]

    def initialDependencyCheck(self):
        """
        Runs a check for availability of package dependencies and summarized error messages
        :return:
        """
        from enmapbox import DEPENDENCIES, messageLog, DIR_REPO
        from enmapbox.dependencycheck import missingPackageInfo, requiredPackages
        missing = [p for p in requiredPackages() if not p.isInstalled()]
        if len(missing) > 0:
            info = missingPackageInfo(missing, html=False)
            # warnings.warn(info, ImportWarning)
            messageLog(info, level=Qgis.Warning)

    def initGui(self):

        import enmapbox
        from qgis.utils import iface
        if isinstance(iface, QgisInterface):
            self.enmapBox = None

            actionStartBox = QAction(enmapbox.icon(), 'EnMAP-Box', iface)
            actionStartBox.triggered.connect(self.run)
            actionAbout = QAction(QIcon(':/enmapbox/gui/ui/icons/metadata.svg'),
                                  'About')
            actionAbout.triggered.connect(self.showAboutDialog)
            self.rasterMenuActions.append(actionStartBox)
            self.rasterMenuActions.append(actionAbout)
            self.pluginToolbarActions.append(actionStartBox)

            for action in self.rasterMenuActions:
                iface.addPluginToRasterMenu('EnMAP-Box', action)

            for action in self.pluginToolbarActions:
                iface.addToolBarIcon(action)

            # init stand-alone apps, that can operate in QGIS GUI without EnMAP-Box
            self.initStandAloneAppGuis(iface)

        else:
            print('EnMAPBoxPlugin.initGui() called without iface')

    def showAboutDialog(self):
        from enmapbox.gui.about import AboutDialog
        d = AboutDialog()
        d.exec()

    def initProcessing(self):
        """
        Init enmapbox for processing provider only
        :return:
        :rtype:
        """
        import enmapbox
        enmapbox.initPythonPaths()

    def run(self):
        from enmapbox.gui.enmapboxgui import EnMAPBox
        self.enmapBox = EnMAPBox.instance()
        if not isinstance(self.enmapBox, EnMAPBox):
            from qgis.utils import iface
            self.enmapBox = EnMAPBox(iface)
            assert self.enmapBox == EnMAPBox.instance()
            self.enmapBox.run()
        else:
            self.enmapBox.ui.show()

    def unload(self):
        from enmapbox.gui.enmapboxgui import EnMAPBox, messageLog
        from qgis.utils import iface
        if isinstance(iface, QgisInterface):

            for action in self.pluginToolbarActions:
                iface.removeToolBarIcon(action)

            for action in self.rasterMenuActions:
                iface.removePluginRasterMenu('EnMAP-Box', action)

        import enmapbox
        enmapbox.unloadAll()

        if isinstance(EnMAPBox.instance(), EnMAPBox):
            EnMAPBox.instance().close()
        EnMAPBox._instance = None

    def initStandAloneAppGuis(self, iface: QgisInterface):
        """
        We started to move external QGIS Plugins into the EnMAP-Box as applications.
        E.g. the GEE Time Series Explorer plugin.
        Those apps can now be used inside the EnMAP-Box GUI, but also in QGIS GUI as stand-alone.
        Therefore, we need to add toolbar icons.
        Note that an app can't do this on it's own, because apps only get initialized on box startup.
        """

        self.initGeeTimeseriesExplorerGui(iface)

    def initGeeTimeseriesExplorerGui(self, iface: QgisInterface):

        from geetimeseriesexplorerapp.externals.ee_plugin.provider import register_data_provider
        from geetimeseriesexplorerapp import GeeTimeseriesExplorerApp
        from geetimeseriesexplorerapp.geetemporalprofiledockwidget import GeeTemporalProfileDockWidget
        from geetimeseriesexplorerapp.geetimeseriesexplorerdockwidget import GeeTimeseriesExplorerDockWidget

        # register the GEETSE_EE data provider
        register_data_provider()

        # add main dock and toolbar button
        self.geeTimeseriesExplorerMainDock = GeeTimeseriesExplorerDockWidget(parent=iface.parent())
        iface.addDockWidget(Qt.RightDockWidgetArea, self.geeTimeseriesExplorerMainDock)
        self.geeTimeseriesExplorerMainDock.setWindowIcon(GeeTimeseriesExplorerApp.icon())
        self.geeTimeseriesExplorerMainDock.hide()

        self.geeTimeseriesExplorerActionToggleMainDock = QAction(
            GeeTimeseriesExplorerApp.icon(), 'GEE Time Series Explorer', iface.mainWindow()
        )
        self.geeTimeseriesExplorerActionToggleMainDock.triggered.connect(self.geeTimeseriesExplorerToggleMainDockVisibility)
        iface.addToolBarIcon(self.geeTimeseriesExplorerActionToggleMainDock)

        # add profile dock and toolbar button
        icon = GeeTimeseriesExplorerApp.iconProfilePlot()
        self.geeTimeseriesExplorerProfileDock = GeeTemporalProfileDockWidget(
            self.geeTimeseriesExplorerMainDock, parent=iface.parent()
        )
        iface.addDockWidget(Qt.TopDockWidgetArea, self.geeTimeseriesExplorerProfileDock)
        self.geeTimeseriesExplorerProfileDock.setWindowIcon(icon)
        self.geeTimeseriesExplorerProfileDock.hide()

        self.actionToggleProfileDock = QAction(icon, 'GEE Temporal Profile Viewer', iface.mainWindow())
        self.actionToggleProfileDock.triggered.connect(self.geeTimeseriesExplorerToggleProfileDockVisibility)
        iface.addToolBarIcon(self.actionToggleProfileDock)

        # set some members
        self.geeTimeseriesExplorerMainDock.setProfileDock(self.geeTimeseriesExplorerProfileDock)
        self.geeTimeseriesExplorerMainDock.setEnmapBox(None)
        self.geeTimeseriesExplorerMainDock.setQgisInterface(iface)

    def geeTimeseriesExplorerToggleMainDockVisibility(self):
        self.geeTimeseriesExplorerMainDock.setVisible(not self.geeTimeseriesExplorerMainDock.isVisible())
        self.geeTimeseriesExplorerProfileDock.setVisible(self.geeTimeseriesExplorerMainDock.isVisible())

    def geeTimeseriesExplorerToggleProfileDockVisibility(self):
        visible = not self.geeTimeseriesExplorerProfileDock.isVisible()
        self.geeTimeseriesExplorerProfileDock.setVisible(visible)
        self.geeTimeseriesExplorerProfileDock.mIdentify.setChecked(visible)
