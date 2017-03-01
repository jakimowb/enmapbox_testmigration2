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

"""
This module describes the EnMAP-GUI <-> Processing Framework interactions
"""
from processing.gui.Postprocessing import handleAlgorithmResults
from processing.core.Processing import Processing
from processing.core.ProcessingLog import ProcessingLog
from processing.core.ProcessingConfig import ProcessingConfig, settingsWatcher
from processing.gui.MessageDialog import MessageDialog
from processing.gui.AlgorithmDialog import AlgorithmDialog
from processing.gui.BatchAlgorithmDialog import BatchAlgorithmDialog
from processing.gui.EditRenderingStylesDialog import EditRenderingStylesDialog
from processing.gui.ConfigDialog import ConfigDialog
from processing.gui.MessageBarProgress import MessageBarProgress
from processing.gui.AlgorithmExecutor import runalg
from processing.core.alglist import algList


from processing.gui.ProcessingToolbox import ProcessingToolbox


class ProcessingAlgorithmsPanelUI(ProcessingToolbox, PanelWidgetBase):
    def __init__(self, parent=None):
        super(ProcessingAlgorithmsPanelUI, self).__init__()
        PanelWidgetBase.__init__(self, parent)
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
            #register signals not handled via QGIS processing framework but the ProcessingAlgorithmsManager

        else:
            self.manager = None



class ProcessingAlgorithmsManager(QObject):

    """
    Keeps overview on QGIS Processing Framework algorithms.
    """


    def __init__(self, enmapBoxInstance):
        super(ProcessingAlgorithmsManager, self).__init__()
        from enmapbox.gui.enmapboxgui import EnMAPBox
        assert isinstance(enmapBoxInstance, EnMAPBox)

        self.enmapbox = enmapBoxInstance
        from processing.core.Processing import Processing

        algList.providerRemoved.connect(self.onProviderRemoved)
        algList.providerAdded.connect(self.onProviderAdded)
        algList.providerUpdated.connect(self.onProviderUpdated)
        settingsWatcher.settingsChanged.connect(self.fillTree)

    def filterProviders(self, providerList, activated=True):

        assert isinstance(providerList, list)
        assert all([p is str for p in providerList])

        if activated:
            for provider in Processing.providers:
                if provider not in providerList:
                    provider
        Processing.activateProvider()
        s = ""

    def onProviderRemoved(self, key):
        logger.debug('Provider removed {}'.format(key))

    def onProviderAdded(self, key):
        logger.debug('Provider added {}'.format(key))

    def onProviderUpdated(self):
        logger.debug('Provider updated {}'.format(key))

    def onFileCreated(self, path):
        logger.debug('File created from processing framework:\n{}'.format(path))




