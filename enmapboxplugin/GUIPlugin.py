import os, site, sys, traceback, logging


from qgis.gui import QgisInterface
from qgis.core import QgsPluginLayerRegistry
from PyQt4.QtCore import QTimer, QCoreApplication
from PyQt4.QtGui import QAction

from enmapbox.utils.environment.DependencyChecker import DependencyChecker
requiredNoneStandardModules = ['pyqtgraph']

class GUIPlugin:
    def __init__(self, iface):
        DependencyChecker.importAllDependencies(requiredNoneStandardModules)
        self.iface = iface
        assert isinstance(iface, QgisInterface)

        #ensure that python console is activated. this is required to redirect
        #printouts like that from debugger to stdout / stderr
        import console.console as CONSOLE
        if CONSOLE._console is None:
            CONSOLE._console = CONSOLE.PythonConsole(iface.mainWindow())
            QTimer.singleShot(0, CONSOLE._console.activate)

        #set the logger
        import enmapbox.gui
        if enmapbox.gui.DEBUG:
            logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)


    def initGui(self):
        self.logger.debug('initGui...')
        self.toolbarActions = []
        self.pluginLayerTypes = dict()

        self.enmapBox = None
        from enmapbox.gui.enmapboxgui import EnMAPBox
        action = QAction(EnMAPBox.getIcon(), u'EnMAP-Box', self.iface)
        action.triggered.connect(self.run)
        self.toolbarActions.append(action)
        for action in self.toolbarActions:
            self.iface.addToolBarIcon(action)


        for key, plugin in self.pluginLayerTypes.items():
            self.logger.debug('add plugin layer {}'.format(key))
            QgsPluginLayerRegistry.instance().addPluginLayerType(plugin)

        self.logger.debug('initGui done')

    def run(self):
        from enmapbox.gui.enmapboxgui import EnMAPBox
        self.enmapBox = EnMAPBox.instance()
        if not self.enmapBox:
            self.enmapBox = EnMAPBox(self.iface)
        self.enmapBox.run()

    def unload(self):
        from enmapbox.gui.enmapboxgui import EnMAPBox
        for action in self.toolbarActions:
            self.logger.debug('remove toolbar action {}'.format(action))
            self.iface.removeToolBarIcon(action)

        for key, plugin in self.pluginLayerTypes.items():
            self.logger.debug('remove plugins layer {}'.format(key))
            QgsPluginLayerRegistry.instance().removePluginLayerType(key)

        if isinstance(self.enmapBox, EnMAPBox):
            #try:
            #    self.enmapBox.ui.close()
           # except:
            #    pass
            self.enmapBox = None
            EnMAPBox._instance = None

    def tr(self, message):
        return QCoreApplication.translate('EnMAPBoxPlugin', message)

