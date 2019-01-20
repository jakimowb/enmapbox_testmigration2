import enmapboxtestdata
from hubdc.core import *

rasterDataset = openRasterDataset(filename=enmapboxtestdata.enmap)
vectorDataset = openVectorDataset(filename=enmapboxtestdata.landcover_polygons)
grid = rasterDataset.grid().clip(extent=vectorDataset.extent())
clipped = rasterDataset.translate(grid=grid, filename='raster.tif', driver=GTiffDriver())
# NOT INCLUDED

filename = clipped.filename()
clipped.close()

from qgis.gui import *
from qgis.core import *

app = QgsApplication([], True)
app.initQgis()

# raster layer
layer1 = QgsRasterLayer(filename)
renderer = layer1.renderer()
assert isinstance(renderer, QgsMultiBandColorRenderer)
renderer.setRedBand(38)
renderer.setGreenBand(23)
renderer.setBlueBand(5)

# vector layer
layer2 = QgsVectorLayer(vectorDataset.filename())

layers = [layer2, layer1]
QgsProject.instance().addMapLayers(layers)
canvas = QgsMapCanvas()
canvas.setLayers(layers)
#canvas.setExtent(canvas.fullExtent())
canvas.setExtent(QgsRectangle(383293, 5818720, 385215, 5820161))
canvas.setDestinationCrs(layer1.crs())
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
