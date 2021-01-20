import unittest
from typing import Dict

from qgis.core import QgsApplication
from qgis.core import QgsProcessingFeedback
from processing.core.Processing import Processing


from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm

# init QGIS
qgsApp = QgsApplication([], True)
qgsApp.initQgis()


# activate QGIS log in PyCharm
def printQgisLog(tb, error, level):
    print(tb)


QgsApplication.instance().messageLog().messageReceived.connect(printQgisLog)

Processing.initialize()


class TestCase(unittest.TestCase):

    @staticmethod
    def runalg(alg: EnMAPProcessingAlgorithm, parameters: Dict):
        print(f'\n{"#" * 80}')
        # alg.initAlgorithm(configuration=None)
        print(alg.__class__.__name__,
            '({} -> {}), {}, {}'.format(alg.group(), alg.displayName(), alg.groupId(), alg.name()))
        print('parameters = {}'.format(repr(parameters)))
        return Processing.runAlgorithm(alg, parameters=parameters, feedback=QgsProcessingFeedback())
