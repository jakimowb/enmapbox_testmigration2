import enmapboxtestdata
from hubdc.core import *

rasterDataset = openRasterDataset(filename=enmapboxtestdata.enmap)

# read data
array = rasterDataset.readAsArray()

# replace no data value
oldNoDataValue = rasterDataset.noDataValue()
newNoDataValue = -1
array[array==oldNoDataValue] = newNoDataValue

# write data
newRasterDataset = RasterDataset.fromArray(array=array, grid=rasterDataset.grid(),
                                           filename='raster.tif', driver=GTiffDriver())
newRasterDataset.setNoDataValue(value=newNoDataValue)
