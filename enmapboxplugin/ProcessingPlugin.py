from __future__ import absolute_import
from processing.core.Processing import Processing

class ProcessingPlugin:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):

        from .processing.EnMAPBoxAlgorithmProvider import EnMAPBoxAlgorithmProvider
        self.provider = EnMAPBoxAlgorithmProvider()
        Processing.addProvider(self.provider)

    def unload(self):
        Processing.removeProvider(self.provider)
