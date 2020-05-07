# -*- coding: utf-8 -*-
import numpy as np
from hubflow.core import *
import gdal
# Zone Martin:
import numpy as np
import time

sample_size = 50000
LUT_size = 2000
n_features = 10

mydata_array = np.random.uniform(low=0, high=1500, size=(n_features, sample_size))
myLUT = np.random.uniform(low=0, high=1500, size=(n_features, LUT_size))

start = time.time()
result = np.zeros(shape=(sample_size, n_features))
for isample in range(sample_size):
    mydata = mydata_array[:, isample]  # Get current sample
    delta = np.sum(np.abs(mydata[:, np.newaxis] - myLUT), axis=0)
    L1_subset = np.argpartition(delta, 50)[:50]  # get n best performing LUT-entries
    L1_subset = L1_subset[np.argsort(delta[L1_subset])]
    result[isample, :] = np.median(myLUT[:, L1_subset], axis=1)
    if isample % 100 == 0:
        print("Finished {:d} of {:d} samples; took {:.5f} seconds so far!".format(isample, sample_size, time.time()-start))

print("Calculation took {:6.5f} seconds".format(time.time() - start))

exit()

import joblib

### Tiling
raster = openRasterDataset(filename=enmapboxtestdata.enmap)

result = MemDriver().create(grid=raster.grid(),
                            bands=raster.zsize(),
                            gdalType=gdal.GDT_Float32)

for subgrid, i, iy, ix in raster.grid().subgrids(size=256):

    array = raster.array(grid=subgrid)
    result.writeArray(array=array, grid=subgrid)

###
exit()


w4ter_absorption_bands = list()
last = -2
start = -1

for item in flat_list:
    if item != last+1:
        if start != -1:
            w4ter_absorption_bands.append(range(start, last + 1))
            # p.append([start, last])
        start = item
    last = item

w4ter_absorption_bands.append(range(start, last+1))

print(flat_list)
print(w4ter_absorption_bands)