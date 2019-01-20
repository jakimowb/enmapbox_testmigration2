from hubdc.core import *
import numpy as np

array = np.array([[ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                  [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                  [ 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1],
                  [ 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1],
                  [ 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1],
                  [ 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1],
                  [ 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1],
                  [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                  [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                  [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]])

rasterDataset = RasterDataset.fromArray(array=array, filename='raster.tif', driver=GTiffDriver())
# NOT INCLUDED

filename = rasterDataset.filename()
rasterDataset.close()

from qgis.gui import *
from qgis.core import *

app = QgsApplication([], True)
app.initQgis()

layer = QgsRasterLayer(filename)
renderer = layer.renderer()
assert isinstance(renderer, QgsSingleBandGrayRenderer)
contrastEnhancement = renderer.contrastEnhancement()
contrastEnhancement.setContrastEnhancementAlgorithm(QgsContrastEnhancement.StretchToMinimumMaximum, True)
contrastEnhancement.setMinimumValue(0)
contrastEnhancement.setMaximumValue(1)

layers = [layer]
QgsProject.instance().addMapLayers(layers)
canvas = QgsMapCanvas()
canvas.setLayers(layers)
canvas.setExtent(canvas.fullExtent())
canvas.setDestinationCrs(layer.crs())
canvas.waitWhileRendering()

if True:
    app.processEvents()
    canvas.saveAsImage(basename(__file__).replace('.py', '.png'))
    import time
    time.sleep(5)
else:
    canvas.extentsChanged.connect(lambda: print(canvas.extent()))
    canvas.show()
    app.exec_()
