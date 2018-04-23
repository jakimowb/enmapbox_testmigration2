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
from enmapbox.gui import LOAD_PROCESSING_FRAMEWORK


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



def hasQPFExtensions():
    """
    Checks if the QPF Extensions are instantiated.
    :return: True | False
    """
    result = False
    try:
        from processing.tools import dataobjects
        result = hasattr(dataobjects, '_getRasterLayers')
    except :
        pass
    return result


def removeEnMAPBoxOnlyLayers():
    """
    Tries to identify raster and vector layers that have been used by the EnMAP-Box only and
    removes them from the QgsMapLayerRegistry to remove any file handles on them.
    :return:
    """

    if hasQPFExtensions():
        from processing.tools import dataobjects
        qgsLayers = dataobjects._getRasterLayers() + dataobjects._getVectorLayers()

        REG = QgsProject.instance()
        to_remove = []
        for lyr in REG.mapLayers().values():
            if lyr not in qgsLayers and lyr.customProperty('__enmapbox__') == True:
                to_remove.append(lyr)
        if len(to_remove) > 0:
            REG.removeMapLayers(to_remove)



def installQPFExtensions(force=False):
    """
    Modifies the QGIS Processing Framework to recognize EnMAP-Box data sources as well.
    Call `removeQPFExtensions` to return to previous state.
    """
    if not force and hasQPFExtensions():
        return
    try:
        from processing.tools import dataobjects
    except:
        return

    def qpfPrefix():
        from enmapbox.gui import settings
        return settings.value('EMB_QPF_LAYERNAME_PREFIX', '[EnMAP-Box]')

    def registerMergeSort(embLayers, qgsLayers, sorting):

        #removeEnMAPBoxOnlyLayers()

        REG = QgsProject.instance()
        for lyr in embLayers:
            assert isinstance(lyr, QgsMapLayer)
            lyr.setCustomProperty('__enmapbox__',True)
        REG.addMapLayers(embLayers, False)

        qgsLayers = embLayers + qgsLayers
        if sorting:
            qgsLayers = sorted(qgsLayers, key=lambda layer: layer.name().lower())
        return qgsLayers


    dataobjects._getRasterLayers = dataobjects.getRasterLayers
    dataobjects._getVectorLayers = dataobjects.getVectorLayers
    dataobjects._getTables = dataobjects.getTables



    def getRasterLayersNEW(sorting=True):
        qgsLayers = dataobjects._getRasterLayers(sorting=sorting)
        qgsSources = set([str(l.source()) for l in qgsLayers])

        from enmapbox.gui.enmapboxgui import EnMAPBox
        if not isinstance(EnMAPBox.instance(), EnMAPBox):
            return qgsLayers

        embLayers = []
        for ds in EnMAPBox.instance().dataSourceManager.sources('RASTER'):
            assert isinstance(ds, DataSourceRaster)
            if ds.uri() not in qgsSources:
                embLayers.append(
                    ds.createUnregisteredMapLayer(baseName='{} {}'.format(qpfPrefix(), ds.mName))
                )

        return registerMergeSort(embLayers, qgsLayers, sorting)

    def getVectorLayersNEW(shapetype=[-1], sorting=True):
        qgsLayers = dataobjects._getVectorLayers(sorting=sorting)
        qgsSources = set([str(l.source()) for l in qgsLayers])

        from enmapbox.gui.enmapboxgui import EnMAPBox
        if not isinstance(EnMAPBox.instance(), EnMAPBox):
            return qgsLayers

        embLayers = []
        for ds in EnMAPBox.instance().dataSourceManager.sources('VECTOR'):
            if ds.uri() not in qgsSources:
                assert isinstance(ds, DataSourceVector)
                lyr = ds.createUnregisteredMapLayer(baseName='{} {}'.format(qpfPrefix(), ds.mName))
                if dataobjects.canUseVectorLayer(lyr, shapetype):
                    embLayers.append(lyr)

        return registerMergeSort(embLayers, qgsLayers, sorting)



    def getTablesNEW(sorting=True):
        qgsLayers = dataobjects._getTables(sorting=sorting)
        qgsSources = set([str(l.source()) for l in qgsLayers])

        from enmapbox.gui.enmapboxgui import EnMAPBox
        if not isinstance(EnMAPBox.instance(), EnMAPBox):
            return qgsLayers

        embLayers = []
        for ds in EnMAPBox.instance().dataSourceManager.sources('VECTOR'):
            if ds.uri() not in qgsSources:
                embLayers.append(ds.createUnregisteredMapLayer(baseName='{} {}'.format(qpfPrefix(), ds.mName)))

        return registerMergeSort(embLayers, qgsLayers, sorting)

    #replace old with overwritten functions
    dataobjects.getVectorLayers = getVectorLayersNEW
    dataobjects.getRasterLayers = getRasterLayersNEW
    dataobjects.getTables = getTablesNEW
    logger.debug('QPF EXTENSIONS INSTALLED')


def removeQPFExtensions():
    """
    Removes the QGIS Processing Framework modification.
    :return:
    """
    if hasQPFExtensions():
        try:

            from processing.tools import dataobjects
            dataobjects.getRasterLayers = dataobjects._getRasterLayers
            dataobjects.getVectorLayers = dataobjects._getVectorLayers
            dataobjects.getTables = dataobjects._getTables
            removeEnMAPBoxOnlyLayers()
            del dataobjects._getRasterLayers
            del dataobjects._getVectorLayers
            del dataobjects._getTables
            logger.debug('QPF EXTENSIONS REMOVED')

        except Exception as ex:
            print(str(ex))


class ProcessingAlgorithmsPanelUI(UI_BASE):
    def __init__(self, parent=None):
        UI_BASE.__init__(self)
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

    def enmapBoxProvider(self):
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