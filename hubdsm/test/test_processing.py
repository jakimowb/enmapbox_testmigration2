from os.path import join
from unittest import TestCase

import numpy as np

from hubdsm.processing.uniquebandvaluecounts import UniqueBandValueCounts
from hubdsm.processing.enmapalgorithm import EnMAPAlgorithm
from hubdsm.core.gdalrasterdriver import ENVI_DRIVER

from qgis.core import *

# init QGIS
from processing.core.Processing import Processing
from qgis.core import QgsApplication

qgsApp = QgsApplication([], True)
qgsApp.initQgis()


# activate QGIS log in PyCharm
def printQgisLog(tb, error, level):
    print(tb)


QgsApplication.instance().messageLog().messageReceived.connect(printQgisLog)

# load Enmap-Box TestProvider

Processing.initialize()


# provider = EnMAPProvider()
# QgsApplication.processingRegistry().addProvider(provider)

class ProcessingFeedback(QgsProcessingFeedback):
    pass
#    def pushConsoleInfo(self, info):
#        print(info)

#    def setProgressText(self, info):
#        print(info)


def runalg(alg: EnMAPAlgorithm, io: dict):
    assert isinstance(alg, EnMAPAlgorithm)
    print('\n##############')
    alg.defineCharacteristics()
    print(alg.__class__.__name__,
        '({} -> {}), {}, {}'.format(alg.group(), alg.displayName(), alg.groupId(), alg.name()))
    print('parameters = {}'.format(repr(io)))
    return Processing.runAlgorithm(alg, parameters=io, feedback=ProcessingFeedback())


outdir = r'c:\unittests\enmapboxalgorithms'

class TestClassificationStatistics(TestCase):

    def test_onLayerWithoutCategoricalRenderer(self):
        filename=join(outdir, 'r.bsq')
        rasterDataset = ENVI_DRIVER.createFromArray(array=np.atleast_3d([-1, 2, 3, 50, 50]), filename=filename)
        rasterDataset.flushCache()
        qgsRasterLayer = QgsRasterLayer(filename)
        assert qgsRasterLayer.isValid()
        alg = UniqueBandValueCounts()
        io = {alg.P_RASTER: qgsRasterLayer, alg.P_BAND: 1}
        runalg(alg=alg, io=io)
