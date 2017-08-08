from __future__ import absolute_import
from enmapbox.utils.environment.DependencyChecker import DependencyChecker
modules = ['matplotlib', 'sklearn']
modules.extend(['HTML', 'pyqtgraph', 'markup', 'rios', 'tabulate'])
from processing.core.Processing import Processing

class ProcessingPlugin:
    def __init__(self, iface):
        #this will be called from within EnMAPBoxPlugin._tryPlugin(ProcessingPlugin)
        #anything that can fail should fail here, so that ._tryPlugin can return something meaningful
        DependencyChecker.importAllDependencies(modules)

        self.iface = iface
        from .processing.SignalsManager import SignalsManager
        SignalsManager.connectHTMLCreatedToWebBrowser()

    def initGui(self):
        from .processing.EnMAPBoxAlgorithmProvider import EnMAPBoxAlgorithmProvider
        self.provider = EnMAPBoxAlgorithmProvider()
        Processing.addProvider(self.provider)

    def unload(self):
        Processing.removeProvider(self.provider)
