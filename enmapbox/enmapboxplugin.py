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
import os, sys, site
from qgis.core import QgsApplication, QgsProcessingProvider, QgsProcessingAlgorithm, Qgis
from qgis.gui import QgisInterface
from qgis.PyQt.QtCore import QTimer
from qgis.PyQt.QtWidgets import QAction

import numpy as np



class EnMAPBoxPlugin(object):

    def __init__(self, iface):
        # make site-packages available to python
        assert isinstance(iface, QgisInterface)
        self.iface = iface

        dirPlugin = os.path.dirname(__file__)
        site.addsitedir(dirPlugin)
        import enmapbox

        site.addsitedir(enmapbox.DIR_SITEPACKAGES)

        #run a dependency check
        self.initialDependencyCheck()

        # initialize resources etc.
        enmapbox.initEnMAPBoxResources()
        enmapbox.initEditorWidgets()


        # add the EnMAP-Box Provider
        enmapbox.initEnMAPBoxProcessingProvider()
        #assert self.enmapBoxProvider == QgsApplication.instance().processingRegistry().providerById('enmapbox')

    def initialDependencyCheck(self):
        """
        Runs a check for availability of package dependencies and give an readible error message
        :return:
        """

        missing = []
        from enmapbox import DEPENDENCIES, messageLog, DIR_REPO
        for package in DEPENDENCIES:
            try:
                __import__(package)

            except Exception as ex:
                missing.append(package)
        if len(missing) > 0:

            longText = ['Unable to import the following python package(s):']
            longText.append('<b>{}</b>'.format(', '.join(missing)))
            longText.append('<p>Please install missing packages using the local package manager like pip3 and root access:')
            pathRequirementsTxt = os.path.join(DIR_REPO, 'requirements.txt')
            longText.append('<code>python3 -m pip install -r {}</code>'.format(pathRequirementsTxt))
            longText.append('More information available under:')
            longText.append('<a href="http://enmap-box.readthedocs.io/en/latest/Installation.html">http://enmap-box.readthedocs.io/en/latest/Installation.html</a> </p>')

            #longText.append('This Python:')
            #longText.append('Executable: {}'.format(sys.executable))
            #longText.append('ENVIRON:')
            #for k in sorted(os.environ.keys()):
            #    longText.append('\t{} ={}'.format(k, os.environ[k]))

            longText = '<br/>\n'.join(longText)
            messageLog(longText)
            raise Exception(longText)


    def initGui(self):

        self.toolbarActions = []

        from enmapbox.gui.ui.resources import qInitResources
        qInitResources()

        from enmapbox.gui.enmapboxgui import EnMAPBox

        self.enmapBox = None
        action = QAction(EnMAPBox.getIcon(), u'EnMAP-Box', self.iface)
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





