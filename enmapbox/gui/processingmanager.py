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
        self.commander = None
        self.toolbox = None

        self.algList = None
        if LOAD_PROCESSING_FRAMEWORK:
            from processing.core.Processing import Processing
            from processing.core.alglist import algList
            self.algList = algList
            self.algList.providerRemoved.connect(self.onProviderRemoved)
            self.algList.providerAdded.connect(self.onProviderAdded)
            self.algList.providerUpdated.connect(self.onProviderUpdated)

            #connect EnMAP-Box processing framework specifics
            from enmapboxplugin.processing.Signals import Signals
            Signals = Signals.signals
            Signals.imageCreated.connect(self.onFileCreated)
            Signals.pickleCreated.connect(self.onFileCreated)
            Signals.htmlCreated.connect(self.onFileCreated)

            self.toolbox = ProcessingToolbox()

            # 1. create new menu entry
            menu = self.enmapBox.ui.menuProcessing
            import processing
            from processing.ProcessingPlugin import ProcessingPlugin

            def pfwIcon(name):
                return QIcon(jp(os.path.dirname(processing.__file__), 'image', name))

            from processing.modeler.CreateNewModelAction import CreateNewModelAction
            # a = menu.addAction(pfwIcon('alg.png'),'Toolbox')
            a = menu.addAction(pfwIcon('model.png'), 'Graphical Modeler')
            assert isinstance(a, QAction)
            a.triggered.connect(self.openModeler)

    def isInitialized(self):
        return self.algList is not None

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

    def enmapBoxProvider(self):
        if self.isInitialized():
            return self.algList.getProviderFromName('EnMAP-Box')
        else:
            return None

    def addAlgorithms(self, providerName, geoAlgorithms):
        from processing.core.GeoAlgorithm import GeoAlgorithm
        from processing.core.AlgorithmProvider import AlgorithmProvider

        if isinstance(providerName, AlgorithmProvider):
            p = providerName
        else:
            p = self.algList.getProviderFromName(providerName)

        pAlgs = self.algList.algs[p.getName()]
        if isinstance(p, AlgorithmProvider):
            for ga in geoAlgorithms:
                assert isinstance(ga, GeoAlgorithm)
                #todo: remove from previous provider
                ga.provider = p
                pAlgs[ga.commandLineName()] = ga
            self.algList.providerUpdated.emit(p.getName())

    def openCommander(self):
        from processing.gui.CommanderWindow import CommanderWindow
        if self.commander is None:
            self.commander = CommanderWindow(
                self.iface.mainWindow(),
                self.iface.mapCanvas())
        self.commander.prepareGui()
        self.commander.show()

    def openToolbox(self):
        if self.toolbox.isVisible():
            self.toolbox.hide()
        else:
            self.toolbox.show()

    def openModeler(self):
        from processing.modeler.ModelerDialog import ModelerDialog
        dlg = ModelerDialog()
        dlg.exec_()
        if dlg.update:
            self.algList.reloadProvider('model')

    def openResults(self):
        from processing.gui.ResultsDialog import ResultsDialog
        dlg = ResultsDialog()
        dlg.show()
        dlg.exec_()

    def openHistory(self):
        from processing.gui.HistoryDialog import HistoryDialog
        dlg = HistoryDialog()
        dlg.exec_()

    def openConfig(self):
        from processing.gui.ConfigDialog import ConfigDialog
        dlg = ConfigDialog(self.toolbox)
        dlg.exec_()


