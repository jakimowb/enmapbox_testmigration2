from __future__ import absolute_import
from processing.core.Processing import Processing
from enmapbox.apps.core import EnMAPBoxProvider
from enmapboxplugin.EnMAPBoxAlgorithmProvider import EnMAPBoxAlgorithmProvider

class ProcessingPlugin:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        self.provider = EnMAPBoxAlgorithmProvider()
        Processing.addProvider(self.provider)

    def unload(self):
        Processing.removeProvider(self.provider)
