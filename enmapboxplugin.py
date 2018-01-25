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
import os, sys, logging, site, traceback
from qgis.gui import QgisInterface
from qgis.core import QgsMessageLog
from PyQt4.QtCore import QTimer
from PyQt4.QtGui import QAction


_MSGLOG_TAG = 'EnMAP-Box'


class EnMAPBoxPlugin(object):

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




        #run a dependency check
        self.initialDependencyCheck()

        from enmapbox import messageLog
        dirPlugin = os.path.dirname(__file__)
        site.addsitedir(dirPlugin)

        try:
            import enmapboxgeoalgorithms.algorithms
            enmapboxgeoalgorithms.algorithms.EnMAPProvider = None
        except Exception as ex:
            messageLog(str(ex))


        # add the EnMAP-Box Provider
        from enmapbox.algorithmprovider import EnMAPBoxAlgorithmProvider
        from processing.core.Processing import Processing
        self.enmapBoxProvider = EnMAPBoxAlgorithmProvider()

        Processing.addProvider(self.enmapBoxProvider)

        from enmapboxgeoalgorithms.algorithms import ALGORITHMS
        self.enmapBoxProvider.appendAlgorithms(ALGORITHMS)

    def initialDependencyCheck(self):
        """
        Runs a check for availability of package dependencies and give an readible error message
        :return:
        """

        pluginDir = os.path.dirname(__file__)
        missing = []
        from enmapbox import DEPENDENCIES, messageLog
        for package in DEPENDENCIES:
            try:
                __import__(package)

            except Exception as ex:
                missing.append(package)
        if len(missing) > 0:

            n = len(missing)

            #pathRequirements = os.path.join(pluginDir, 'requirements.txt')
            #pipCmd1 = 'install -r {}'.format(pathRequirements)
            #pipCmd2 = 'install --user -r {}'.format(pathRequirements)
            #shortText = ['Unable to import {} package(s):\n'.format(n, ', '.join(missing))]

            longText = ['Unable to import: {}'.format(', '.join(missing)),
                        'Please run your local package manager(s) with root rights to install them.',
                        'More information available under:\nhttp://enmap-box.readthedocs.io/en/latest/Installation.html']
            shortText = '\n'.join(longText)

            longText.append('\nThis Python:\nExecutable: {}'.format(sys.executable))
            longText.append('PYTHONPATH :\n{}'.format('\n'.join(sorted(sys.path))))
            env = []
            for k in sorted(os.environ.keys()):
                env.append('{} ={}'.format(k, os.environ[k]))
            longText.append('ENVIRON: \n{}'.format('\n'.join(env)))

            longText = '\n'.join(longText)
            messageLog(longText)

            from PyQt4.QtGui import QMessageBox
            mb = QMessageBox()
            mb.setWindowTitle('Missing packages')
            mb.setText('Unable to import {} package(s)'.format(n))
            mb.setInformativeText(shortText)
            mb.setDetailedText(longText)
            mb.setMinimumWidth(250)
            mb.setStandardButtons(QMessageBox.Ok | QMessageBox.Ignore)
            result = mb.exec_()
            if result == QMessageBox.Ok:
                raise Exception(longText)
            elif result == QMessageBox.Ignore:
                pass


    def initGui(self):
        self.toolbarActions = []

        from enmapbox.gui.ui.resources import qInitResources
        qInitResources()

        from enmapbox.gui.enmapboxgui import EnMAPBox
        self.enmapBox = None
        action = QAction(EnMAPBox.getIcon(), u'EnMAP-Box', self.iface)
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

        else:
            #print('FOUND BOX')
            self.enmapBox.ui.show()

    def unload(self):
        from enmapbox.gui.enmapboxgui import EnMAPBox
        for action in self.toolbarActions:
            self.iface.removeToolBarIcon(action)

        from processing.core.Processing import Processing
        Processing.removeProvider(self.enmapBoxProvider)

        if isinstance(EnMAPBox.instance(), EnMAPBox):
            EnMAPBox.instance().close()

        EnMAPBox._instance = None



