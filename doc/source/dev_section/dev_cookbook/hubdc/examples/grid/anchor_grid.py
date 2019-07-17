from hubdc.docutils import createDocPrint

print = createDocPrint(__file__)

# START
from hubflow.core import *
import enmapboxtestdata

# Get raster grid.
rasterDataset = openRasterDataset(enmapboxtestdata.enmap)
print(rasterDataset.grid())

# Reproject that grid into WGS84 with 0.005 degree resolution.
extentWgs84 = rasterDataset.grid().extent().reproject(projection=Projection.wgs84())
gridWgs84 = Grid(extent=extentWgs84, resolution=0.005)
print(gridWgs84)

# Anchor the grid to (0, 0) degrees.
# This ensures that the upper left and lower right point coordinates are multiples of the 0.005 degree resolution

gridWgs84Anchored = gridWgs84.anchor(Point(x=0, y=0, projection=Projection.wgs84()))
print(gridWgs84Anchored)
# END