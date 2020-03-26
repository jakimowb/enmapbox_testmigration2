from os.path import join
from unittest import TestCase

import numpy as np

from enmapboxprocessing.algorithms.classificationstatistics import ClassificationStatistics
from enmapboxprocessing.enmapalgorithm import EnMAPAlgorithm

from hubdsm.core.gdalrasterdriver import GdalRasterDriver, ENVI_DRIVER

import qgis.PyQt
from qgis.core import *

# init QGIS
from processing.core.Processing import Processing
from qgis.core import QgsApplication

from hubdsm.core.raster import Raster

qgsApp = QgsApplication([], True)
qgsApp.initQgis()


# activate QGIS log in PyCharm
def printQgisLog(tb, error, level):
    print(tb)


QgsApplication.instance().messageLog().messageReceived.connect(printQgisLog)

# load Enmap-Box TestProvider
from enmapboxprocessing.algorithms import *

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
        filename = ENVI_DRIVER.createFromArray(array=np.atleast_3d([0, 1, 2, 3, 2, 1, 0]), filename='/vsimem/r.bsq').filename
        qgsRasterLayer = QgsRasterLayer(filename)
        assert qgsRasterLayer.isValid()
        alg = ClassificationStatistics()
        io = {alg.P_RASTER: qgsRasterLayer}
        runalg(alg=alg, io=io)
