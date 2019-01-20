import enmapboxtestdata
from hubdc.core import *

rasterDataset = RasterDataset.fromArray(array=[[[0, 1, 2, 3]]], filename='raster.bsq', driver=EnviDriver())
band = rasterDataset.band(index=0)
band.setCategoryNames(names=['unclassified', 'class 1', 'class 2', 'class 3'])
band.setCategoryColors(colors=[(0,0,0), (255, 0, 0), (0, 255, 0), (0, 0, 255)]) # list of rgb or rgba tuples

print(band.categoryNames())
print(band.categoryColors())
# NOT INCLUDED

from qgis.gui import *
from qgis.core import *

app = QgsApplication([], True)
app.initQgis()

filename = rasterDataset.filename()
rasterDataset.close()
band = 1

layer = QgsRasterLayer(filename)
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

rasterDataset.close()
