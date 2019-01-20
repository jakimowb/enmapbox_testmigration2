import enmapboxtestdata
from hubdc.core import *

vectorDataset = openVectorDataset(filename=enmapboxtestdata.landcover_polygons)
grid = vectorDataset.grid(resolution=5)
rasterDataset = vectorDataset.rasterize(grid, noDataValue=-9999, initValue=-9999,
                                        burnAttribute='level_3_id',
                                        filename='raster.tif', driver=GTiffDriver())
# NOT INCLUDED

from qgis.gui import *
from qgis.core import *

app = QgsApplication([], True)
app.initQgis()

filename = rasterDataset.filename()
rasterDataset.close()
band = 1

layer = QgsRasterLayer(filename)
renderer = QgsSingleBandGrayRenderer(layer.dataProvider(), band)
layer.setRenderer(renderer)

renderer = layer.renderer()
provider = layer.dataProvider()

layer_extent = layer.extent()
myType = renderer.dataType(band)
stats = provider.bandStatistics(bandNo=band, stats=QgsRasterBandStats.All, extent=layer_extent, sampleSize=0)

contrastEnhancement = QgsContrastEnhancement(myType)
contrastEnhancement.setContrastEnhancementAlgorithm(QgsContrastEnhancement.StretchToMinimumMaximum, True)
contrastEnhancement.setMinimumValue(stats.minimumValue)
contrastEnhancement.setMaximumValue(stats.maximumValue+1)

layer.renderer().setContrastEnhancement(contrastEnhancement)

layers = [layer]
QgsProject.instance().addMapLayers(layers)
canvas = QgsMapCanvas()
canvas.setLayers(layers)
#canvas.setExtent(canvas.fullExtent())
canvas.setExtent(QgsRectangle(383382, 5818224, 385304, 5819664))
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
