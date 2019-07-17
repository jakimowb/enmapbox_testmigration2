import enmapboxtestdata
from hubdc.core import *

vectorDataset = openVectorDataset(filename=enmapboxtestdata.landcover_points)
rasterDataset = openRasterDataset(filename=enmapboxtestdata.enmap)

mapViewer = MapViewer()
mapViewer.addLayer(vectorDataset.mapLayer())
mapViewer.addLayer(rasterDataset.mapLayer())
mapViewer.save('image.png')
