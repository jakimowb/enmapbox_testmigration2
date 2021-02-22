import unittest
from typing import Dict

from qgis._core import QgsApplication, QgsProcessingFeedback

from processing.core.Processing import Processing
from enmapbox.testing import start_app
from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm

qgsApp = start_app()

# activate QGIS log in PyCharm
def printQgisLog(tb, error, level):
    print(tb)

QgsApplication.instance().messageLog().messageReceived.connect(printQgisLog)

#Processing.initialize()


class TestCase(unittest.TestCase):

    @staticmethod
    def runalg(alg: EnMAPProcessingAlgorithm, parameters: Dict):
        print(f'\n{"#" * 80}')
        # alg.initAlgorithm(configuration=None)
        print(alg.__class__.__name__,
            '({} -> {}), {}, {}'.format(alg.group(), alg.displayName(), alg.groupId(), alg.name()))
        print('parameters = {}'.format(repr(parameters)))
        return Processing.runAlgorithm(alg, parameters=parameters, feedback=QgsProcessingFeedback())
