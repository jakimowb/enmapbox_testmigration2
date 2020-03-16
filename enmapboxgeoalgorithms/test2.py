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
from enmapboxgeoalgorithms.algorithms import *

Processing.initialize()

alg = ClassificationStatistics()

io = {alg.P_CLASSIFICATION: enmapClassification}

Processing.runAlgorithm(alg, parameters=io)
