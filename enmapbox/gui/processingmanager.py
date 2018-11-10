# -*- coding: utf-8 -*-

"""
***************************************************************************
    processingmanager.py
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

import six, sys, os, gc, re, collections, uuid

from qgis.core import *
from qgis.gui import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from enmapbox.gui.utils import PanelWidgetBase, loadUI
from osgeo import gdal, ogr
from enmapbox.gui.treeviews import *
from enmapbox.gui.datasources import *
from enmapbox import LOAD_PROCESSING_FRAMEWORK

"""
This module describes the EnMAP-GUI <-> Processing Framework interactions
"""
ProcessingAlgorithmsPanelUI = None

def canImportProcessingFramework():
    """
    Checks if the QGIS Processing Framework can be loaded.
    :return:
    """
    try:
        from processing.gui.ProcessingToolbox import ProcessingToolbox
        return True
    except:
        return False


if LOAD_PROCESSING_FRAMEWORK and canImportProcessingFramework():
    from processing.gui.ProcessingToolbox import ProcessingToolbox as UI_BASE
    _PF_AVAILABLE = True
else:
    from PyQt5.QtGui import QDockWidget as UI_BASE
    _PF_AVAILABLE = False


class ProcessingAlgorithmsPanelUI(UI_BASE):
    def __init__(self, parent=None):
        UI_BASE.__init__(self)
        self.setParent(parent)
        if not _PF_AVAILABLE:
            w = QFrame()
            w.setLayout(QVBoxLayout())
            w.layout().addWidget(QLabel('QGIS was initialized without\nQIS Processing Framework.'))
            self.setWidget(w)

        self.setWindowTitle('QGIS Processing Toolbox')
        """
        algList.providerRemoved.connect(self.removeProvider)
        algList.providerAdded.connect(self.addProvider)
        algList.providerUpdated.connect(self.updateProvider)
        settingsWatcher.settingsChanged.connect(self.fillTree)
        """

    def connectProcessingAlgManager(self, manager):
        if isinstance(manager, ProcessingAlgorithmsManager):
            self.manager = manager
            #register signals not handled via the QGIS processing framework but the ProcessingAlgorithmsManager

        else:
            self.manager = None

#global ProcessingAlgorithmsPanelUI


class ProcessingAlgorithmsManager(QObject):

    """
    Keeps overview on QGIS Processing Framework algorithms.
    """
    def __init__(self, enmapBoxInstance):
        super(ProcessingAlgorithmsManager, self).__init__()
        from enmapbox.gui.enmapboxgui import EnMAPBox

        self.commander = None
        self.toolbox = None
        self.processingRegistry = QgsApplication.instance().processingRegistry()

        if _PF_AVAILABLE:
            self.processingRegistry.providerRemoved.connect(self.onProviderRemoved)
            self.processingRegistry.providerAdded.connect(self.onProviderAdded)


            #connect EnMAP-Box processing framework specifics

            #from enmapboxplugin.processing.Signals import Signals
            #Signals = Signals.signals
            #Signals.imageCreated.connect(self.onFileCreated)
            #Signals.pickleCreated.connect(self.onFileCreated)
            #Signals.htmlCreated.connect(self.onFileCreated)
            from processing.gui.ProcessingToolbox import ProcessingToolbox
            self.toolbox = ProcessingToolbox()
            self.toolbox.addProvider('enmapbox')
            if isinstance(enmapBoxInstance, EnMAPBox):
                self.enmapBox = enmapBoxInstance
                # 1. create new menu entry
                menu = self.enmapBox.ui.menuProcessing
                import processing
                from processing.ProcessingPlugin import ProcessingPlugin

                def pfwIcon(name):
                    return QIcon(jp(os.path.dirname(processing.__file__), 'image', name))

                from processing.modeler.CreateNewModelAction import CreateNewModelAction
                # a = menu.addAction(pfwIcon('alg.png'),'Toolbox')
                a = menu.addAction(pfwIcon('model.png'), 'Graphical Modeler')
                a.setToolTip('Open Graphical Modeler')
                assert isinstance(a, QAction)
                a.triggered.connect(self.openModeler)



    def isInitialized(self):
        return self.processingRegistry is not None

    def onProviderRemoved(self, key):
        messageLog('Provider removed {}'.format(key))

    def onProviderAdded(self, key):
        messageLog('Provider added {}'.format(key))



    def onFileCreated(self, path):
        messageLog('File created from processing framework:\n{}'.format(path))
        if self.enmapBox:
            self.enmapBox.dataSourceManager.addSource(path)

    def onHtmlCreated(self, path):
        messageLog('HTML report created from processing framework:\n{}'.format(path))
        if self.enmapBox:
            src = self.enmapBox.dataSourceManager.addSource(path)
            self.enmapBox.dockManager.createDock('TEXT', initSrc=src)

    def enmapBoxProvider(self)->QgsProcessingProvider:
        """
        Returns the EnMAPBoxAlgorithmProvider or None, if it was not initialized
        """
        if self.isInitialized() and self.enmapBox:
            from enmapbox.algorithmprovider import ID
            return self.processingRegistry.providerById(ID)
        else:
            return None


    def openToolbox(self):
        if self.toolbox.isVisible():
            self.toolbox.hide()
        else:
            self.toolbox.show()

    def openModeler(self):
        from processing.modeler.ModelerDialog import ModelerDialog
        dlg = ModelerDialog()
        dlg.show()



    def openHistory(self):
        from processing.gui.HistoryDialog import HistoryDialog
        dlg = HistoryDialog()
        dlg.show()

    def openConfig(self):
        from processing.gui.ConfigDialog import ConfigDialog
        dlg = ConfigDialog(self.toolbox)
        dlg.show()


if __name__ == '__main__':
    from enmapbox.gui.utils import *
    app = initQgisApplication()
    from enmapbox.gui.enmapboxgui import EnMAPBox
    from enmapbox.algorithmprovider import EnMAPBoxAlgorithmProvider

    p = EnMAPBoxAlgorithmProvider()

    emb = EnMAPBox(None)
    reg = QgsApplication.processingRegistry()
    reg.addProvider(p)
    PAM = ProcessingAlgorithmsManager(emb)
    PAM.openConfig()

    app.exec_()