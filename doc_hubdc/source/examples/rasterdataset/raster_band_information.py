from hubdc.docutils import createDocPrint

print = createDocPrint(__file__)

# START
import enmapboxtestdata
from hubdc.core import *

rasterDataset = openRasterDataset(filename=enmapboxtestdata.createClassification(30))
rasterBand = rasterDataset.band(index=0)
print('no data value: {}'.format(rasterBand.noDataValue()))
print('description: {}'.format(rasterBand.description()))
print('category names: {}'.format(rasterBand.categoryNames()))
print('category colors: {}'.format(rasterBand.categoryColors()))
# END