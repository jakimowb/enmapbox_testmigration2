import enmapboxtestdata
from hubdc.core import *

rasterDataset = openRasterDataset(filename=enmapboxtestdata.enmap)
rasterBandDataset = rasterDataset.band(index=0)
print(rasterBandDataset)
