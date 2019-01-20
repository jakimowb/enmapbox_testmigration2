import enmapboxtestdata
from hubdc.core import *

rasterDataset = openRasterDataset(filename=enmapboxtestdata.enmap)
rasterBand = rasterDataset.band(index=0)
print('no data value: {}'.format(rasterBand.noDataValue()))
print('description: {}'.format(rasterBand.description()))
print('category names: {}'.format(rasterBand.categoryNames()))
print('category colors: {}'.format(rasterBand.categoryColors()))
