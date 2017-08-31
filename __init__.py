from processing.core.Processing import Processing
from processing.core.AlgorithmProvider import AlgorithmProvider
from enmapboxgeoalgorithms import ENMAPBOXGEOALGORITHMS_VERSION
from enmapboxgeoalgorithms.algorithms import ALGORITHMS

def classFactory(iface):
    return EnMAPPlugin(iface)

class EnMAPPlugin(object):
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        self.provider = EnMAPProvider()
        Processing.addProvider(self.provider)

    def unload(self):
        Processing.removeProvider(self.provider)

class EnMAPProvider(AlgorithmProvider):

    def getName(self):
        return 'EBTest'

    def getDescription(self):
        return 'EnMAP-Box TestProvider (v'+ENMAPBOXGEOALGORITHMS_VERSION+')'

    def _loadAlgorithms(self):
        self.algs.extend(ALGORITHMS)
