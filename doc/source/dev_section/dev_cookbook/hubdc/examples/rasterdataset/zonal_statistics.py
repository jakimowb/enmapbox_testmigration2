from hubdc.docutils import createDocPrint

print = createDocPrint(__file__)

# START
import enmapboxtestdata
from hubdc.core import *
import numpy as np

rasterDataset = openRasterDataset(filename=enmapboxtestdata.enmap)
vectorDataset = openVectorDataset(filename=enmapboxtestdata.landcover_polygons)

# rasterize zones attribute
zonesRasterDataset = vectorDataset.rasterize(grid=rasterDataset.grid(),
                                             burnAttribute='level_3_id')

# calculate zonal statistics for the first raster band
values = rasterDataset.band(index=0).readAsArray()
zones = zonesRasterDataset.band(index=0).readAsArray()

for i in np.unique(zones):
    mean = np.mean(values[zones == i]) # subset pixels for current zone and calculate mean
    print('Zone {} mean: {}'.format(i+1, mean))
# END