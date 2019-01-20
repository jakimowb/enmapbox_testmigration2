from os.path import basename
import enmapboxtestdata
from qgis.gui import *
from qgis.core import *

app = QgsApplication([], True)
app.initQgis()

lyr1 = QgsRasterLayer(enmapboxtestdata.enmap)
renderer = lyr1.renderer()
assert isinstance(renderer, QgsMultiBandColorRenderer)
#renderer.setRedBand(1)
#renderer.setBlueBand(2)
#renderer.setGreenBand(3)
#renderer.redContrastEnhancement().setMinimumValue(0)
#renderer.redContrastEnhancement().setMaximumValue(2000)

layers = [lyr1]
QgsProject.instance().addMapLayers(layers)
canvas = QgsMapCanvas()
canvas.setLayers(layers)
canvas.setExtent(canvas.fullExtent())
#canvas.setExtent(QgsRectangle (double xMin, double yMin=0, double xMax=0, double yMax=0)
canvas.setDestinationCrs(lyr1.crs())
canvas.waitWhileRendering()


if 1:
    app.processEvents()
    canvas.saveAsImage(basename(__file__).replace('.py', '.png'))
    import time
    time.sleep(5)
else:
    canvas.show()
    app.exec_()