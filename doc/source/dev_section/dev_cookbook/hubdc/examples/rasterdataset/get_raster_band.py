from hubdc.docutils import createDocPrint
print = createDocPrint(__file__)

# START
import enmapboxtestdata
from hubdc.core import *

rasterDataset = openRasterDataset(filename=enmapboxtestdata.enmap)
rasterBandDataset = rasterDataset.band(index=0)
print(rasterBandDataset)
# END