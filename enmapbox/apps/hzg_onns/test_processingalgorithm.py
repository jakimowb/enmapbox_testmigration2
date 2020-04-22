from os.path import join, dirname
from qgis.core import QgsProcessingFeedback, QgsApplication
from processing.core.Processing import Processing
from hzg_onns.processingalgorithm import OnnsProcessingAlgorithm
import enmapboxtestdata

# init QGIS
qgsApp = QgsApplication([], True)
qgsApp.initQgis()
qgsApp.messageLog().messageReceived.connect(lambda *args: print(args[0]))

# init processing framework
Processing.initialize()

# run algorithm
alg = OnnsProcessingAlgorithm()
io = {alg.P_FILE: r'C:\Users\Hieronym\Documents\Martin\Talks_Travel\2019_02_Berlin_EnMAP_Box\ONNSv08\Baltic_20160720_C2R_subset.nc',
      alg.P_OUTPUT_FOLDER: r'C:\Users\Hieronym\Documents\Martin\Talks_Travel\2019_02_Berlin_EnMAP_Box\ONNSv08\output\\'}

result = Processing.runAlgorithm(alg, parameters=io)

print(result)
