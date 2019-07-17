from hubdc.docutils import createDocPrint

print = createDocPrint(__file__)

# START
import enmapboxtestdata
from hubdc.core import *

rasterDataset = openRasterDataset(filename=enmapboxtestdata.enmap)
vectorDataset = openVectorDataset(filename=enmapboxtestdata.landcover_polygons)
grid = rasterDataset.grid().clip(extent=vectorDataset.extent())
clipped = rasterDataset.translate(grid=grid, filename='raster.tif', driver=GTiffDriver())
# END

viewer = MapViewer()
viewer.addLayer(vectorDataset.mapLayer())
viewer.addLayer(clipped.mapLayer().initMultiBandColorRenderer(37, 22, 4))
viewer.setExtent(Extent(xmin=383293, ymin=5818720, xmax=385215, ymax=5820161, projection=clipped.projection()))
viewer.save(basename(__file__.replace('.py', '.png')))
