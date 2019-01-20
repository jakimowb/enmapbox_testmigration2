from hubdc.core import *

# create pixel grid covering the whole world with a 1 degree resolution
extent=Extent(xmin=-180.0, ymin=-90.0, xmax=180.0, ymax=90.0, projection=Projection.wgs84())
grid = Grid(extent=extent, resolution=1.0)

# prepare GTiff creation options for compressed and band-sequential writing
driver = GTiffDriver()
options = [driver.Option.COMPRESS.LZW, driver.Option.INTERLEAVE.BAND]
print(options)

# create raster with 3 bands
rasterDataset = driver.create(grid=grid, bands=3, gdalType=gdal.GDT_Byte, filename='raster.tif', options=options)

# write random data
array = np.random.randint(0, 255, size=rasterDataset.shape())
rasterDataset.writeArray(array=array)
# NOT INCLUDED

filename = rasterDataset.filename()
rasterDataset.close()

from qgis.gui import *
from qgis.core import *

app = QgsApplication([], True)
app.initQgis()

layer1 = QgsRasterLayer(filename)
layer2 = QgsVectorLayer(r'C:\source\hub-datacube\doc\source\data\continent.gpkg')

layers = [layer2, layer1]
QgsProject.instance().addMapLayers(layers)
canvas = QgsMapCanvas()
canvas.setLayers(layers)
canvas.setExtent(canvas.fullExtent())
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
