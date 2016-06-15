import qgis
from qgis.core import *
app = QgsApplication([], True)
QgsApplication.initQgis()
import processing
from processing.core.Processing import Processing
import os

Processing.initialize()

print 'Hello QGIS!'

import processing,os
root = r'D:\work\AR\svn\EnMAP-Box\enmapProject\lib\hubAPI\resource\testData\image'
xfile = os.path.join(root, 'Hymap_Berlin-A_Image')
yfile = os.path.join(root, 'Hymap_Berlin-A_Classification-Training-Sample')
mfile = os.path.join(root, 'Hymap_Berlin-A_Mask')
pfile = r'a:\classification.img'
modelfile = r'a:\model.svc'
print processing.alglist('imageML')
print processing.alghelp('enmapbox:imagemlfit')
result = processing.runalg('enmapbox:imagemlfit', xfile, yfile, mfile, 'LinearSVC()', modelfile)
print(result)

# Exit QGIS
QgsApplication.exitQgis()
QgsApplication.exit()
