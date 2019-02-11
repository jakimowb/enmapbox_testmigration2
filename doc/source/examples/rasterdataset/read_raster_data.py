from hubdc.docutils import createDocPrint
print = createDocPrint(__file__)

# START
import enmapboxtestdata
from hubdc.core import *

rasterDataset = openRasterDataset(filename=enmapboxtestdata.enmap)

# read dataset

# - all bands as 3d array
print(rasterDataset.readAsArray().shape)
# - single band as 2d array
print(rasterDataset.band(index=0).readAsArray().shape)
# - pixel (z) profile as 1d array
print(rasterDataset.zprofile(pixel=Pixel(x=100, y=100)).shape)
# - column (x) profile as 1d array
print(rasterDataset.xprofile(row=Row(y=100, z=0)).shape)
# - row (y) profile as 1d array
print(rasterDataset.yprofile(column=Column(x=100, z=0)).shape)

# read dataset for given target grid (may include on-the-fly resampling and/or reprojection)

grid = Grid(extent=Extent(xmin=13, xmax=13.5, ymin=52, ymax=52.5, projection=Projection.wgs84()), resolution=0.001)
# - all bands as 3d array
print(rasterDataset.array(grid=grid, resampleAlg=gdal.GRA_Cubic).shape)
# - single band as 2d array
print(rasterDataset.band(index=0).array(grid=grid, resampleAlg=gdal.GRA_Cubic).shape)
# END
