import enmapboxtestdata
from hubdc.core import *

rasterDataset = openRasterDataset(filename=enmapboxtestdata.enmap)
vectorDataset = openVectorDataset(filename=enmapboxtestdata.landcover_polygons)
extent = rasterDataset.extent()
point = extent.upperLeft()
geometry = extent.geometry()

# from raster dataset
projection = rasterDataset.projection()

# from vector dataset
projection = vectorDataset.projection()

# from extent
projection = extent.projection()

# from point
projection = point.projection()

# from geometry
projection = geometry.projection()
