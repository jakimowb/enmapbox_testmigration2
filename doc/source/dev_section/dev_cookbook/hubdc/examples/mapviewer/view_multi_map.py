from hubdc.core import *
MapViewer.show = lambda self: None # disable show

# START
import enmapboxtestdata
from hubdc.core import *

vectorDataset = openVectorDataset(filename=enmapboxtestdata.landcover_points)
rasterDataset = openRasterDataset(filename=enmapboxtestdata.enmap)

mapViewer = MapViewer()
mapViewer.addLayer(vectorDataset.mapLayer())
mapViewer.addLayer(rasterDataset.mapLayer())
mapViewer.show()
# END

mapViewer.save(basename(__file__).replace('.py', '.png'))
