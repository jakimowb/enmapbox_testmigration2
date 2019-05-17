import enmapboxtestdata
from hubdc.core import *


rasterDataset = openRasterDataset(enmapboxtestdata.enmap)

viewer = MapViewer()
layer = viewer.addLayer(rasterDataset.mapLayer())
layer.singleBandGrayRenderer(index=0, min=179, max=1026)
#layer.singleBandGrayRenderer(index=0, percent=5)


viewer.show(size=(300,100))

exit(0)

app = QgsApplication([], True)
app.initQgis()

band = 1
layer = QgsRasterLayer(enmapboxtestdata.createClassification(5, oversampling=1).filename())
renderer = QgsSingleBandGrayRenderer(layer.dataProvider(), band)
layer.setRenderer(renderer)

renderer = layer.renderer()
provider = layer.dataProvider()

layer_extent = layer.extent()
uses_band = renderer.usesBands()
myType = renderer.dataType(uses_band[0])
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
