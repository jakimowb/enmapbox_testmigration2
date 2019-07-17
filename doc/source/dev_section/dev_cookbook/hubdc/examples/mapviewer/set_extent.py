from hubdc.core import *
MapViewer.show = lambda self: None # disable show

# START1
import enmapboxtestdata
from hubdc.core import *

rasterDataset = openRasterDataset(filename=enmapboxtestdata.enmap)

mapViewer = rasterDataset.mapViewer()

# change projection
mapViewer.setProjection(projection=Projection.wgs84())
mapViewer.show()
# END1
mapViewer1 = mapViewer
mapViewer = rasterDataset.mapViewer()
# START2
# change extent
mapViewer.setExtent(Extent(xmin=13.29, xmax=13.32, ymin=52.47, ymax=52.49, projection=Projection.wgs84()))
mapViewer.show()
# END2

mapViewer1.save(basename(__file__).replace('.py', '1.png'))
mapViewer.save(basename(__file__).replace('.py', '2.png'))
