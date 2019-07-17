from hubdc.docutils import createDocPrint

print = createDocPrint(__file__)

# START
import enmapboxtestdata
from hubdc.core import *

vectorDataset = openVectorDataset(filename=enmapboxtestdata.landcover_polygons)
grid = vectorDataset.grid(resolution=5)
rasterDataset = vectorDataset.rasterize(grid, noDataValue=-9999, initValue=-9999,
                                        burnAttribute='level_3_id',
                                        filename='raster.tif', driver=GTiffDriver())
# END
rasterDataset.flushCache()
viewer = rasterDataset.mapViewer()
viewer.setExtent(Extent(xmin=383293, ymin=5818720, xmax=385215, ymax=5820161, projection=rasterDataset.projection()))
viewer.save(basename(__file__.replace('.py', '.png')))
