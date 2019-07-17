import enmapboxtestdata
from hubdc.core import *

rasterDataset = openRasterDataset(filename=enmapboxtestdata.enmap)

# define target grid with extent of original raster, but in WGS 84 projection and 0.0001 degree resolution
grid = Grid(extent=rasterDataset.extent().reproject(Projection.wgs84()), resolution=0.0001)

# reproject raster into target grid
warped = rasterDataset.warp(grid=grid, filename='raster.bsq', driver=EnviDriver())
