from processing.core.Processing import Processing
from processing.core.AlgorithmProvider import AlgorithmProvider
from enmapboxgeoalgorithms.algorithms import ALGORITHMS
from enmapboxgeoalgorithms import ENMAPBOXGEOALGORITHMS_VERSION

def classFactory(iface):
    return Plugin(iface)

class Plugin:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        self.provider = Provider()
        Processing.addProvider(self.provider)

    def unload(self):
        Processing.removeProvider(self.provider)

class Provider(AlgorithmProvider):

    def getName(self):
        return 'EnMAP-Box TestProvider (v'+ENMAPBOXGEOALGORITHMS_VERSION+')'

    def getDescription(self):
        return 'EnMAP-Box TestProvider (v'+ENMAPBOXGEOALGORITHMS_VERSION+')'

    def _loadAlgorithms(self):
        self.algs.extend(ALGORITHMS)
