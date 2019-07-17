from hubdc.docutils import createDocPrint
print = createDocPrint(__file__)

# START
import enmapboxtestdata
from hubdc.core import *
from osgeo import gdal

# init with GDAL Dataset
gdalDataset = gdal.Open(enmapboxtestdata.enmap)
rasterDataset = RasterDataset(gdalDataset=gdalDataset)
print(rasterDataset)

# get the GDAL Dataset handle from a RasterDataset
print(rasterDataset.gdalDataset())
# END
