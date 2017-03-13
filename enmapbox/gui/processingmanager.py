import six, sys, os, gc, re, collections, uuid, logging
logger = logging.getLogger(__name__)
from qgis.core import *
from qgis.gui import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from enmapbox.gui.utils import PanelWidgetBase, loadUI
from osgeo import gdal, ogr
from enmapbox.gui.treeviews import *
from enmapbox.gui.datasources import *
from enmapbox.gui import LOAD_PROCESSING_FRAMEWORK

"""
This module describes the EnMAP-GUI <-> Processing Framework interactions
"""
ProcessingAlgorithmsPanelUI = None
if LOAD_PROCESSING_FRAMEWORK:
    from processing.gui.ProcessingToolbox import ProcessingToolbox


    class ProcessingAlgorithmsPanelUI(ProcessingToolbox):
        def __init__(self, parent=None):

            ProcessingToolbox.__init__(self)

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
        assert isinstance(enmapBoxInstance, EnMAPBox)

        self.enmapBox = enmapBoxInstance

        if LOAD_PROCESSING_FRAMEWORK:
            from processing.core.Processing import Processing
            from processing.core.alglist import algList

            algList.providerRemoved.connect(self.onProviderRemoved)
            algList.providerAdded.connect(self.onProviderAdded)
            algList.providerUpdated.connect(self.onProviderUpdated)

            #connect EnMAP-Box processing framework specifics
            from enmapboxplugin.processing.Signals import Signals
            Signals = Signals.signals
            Signals.imageCreated.connect(self.onFileCreated)
            Signals.pickleCreated.connect(self.onFileCreated)
            Signals.htmlCreated.connect(self.onFileCreated)



    def onProviderRemoved(self, key):
        logger.debug('Provider removed {}'.format(key))

    def onProviderAdded(self, key):
        logger.debug('Provider added {}'.format(key))

    def onProviderUpdated(self, key):
        logger.debug('Provider updated {}'.format(key))

    def onFileCreated(self, path):
        logger.debug('File created from processing framework:\n{}'.format(path))
        self.enmapBox.dataSourceManager.addSource(path)

    def onHtmlCreated(self, path):
        logger.debug('HTML report created from processing framework:\n{}'.format(path))
        src = self.enmapBox.dataSourceManager.addSource(path)
        self.enmapBox.dockManager.createDock('TEXT', initSrc=src)

