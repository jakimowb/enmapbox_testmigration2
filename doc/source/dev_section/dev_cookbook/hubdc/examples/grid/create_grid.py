from hubdc.docutils import createDocPrint

print = createDocPrint(__file__)

# START
from hubflow.core import *

# create a grid in WGS84 for the whole world with 1 degree resolution
extent=Extent(xmin=-180.0, ymin=-90.0, xmax=180.0, ymax=90.0, projection=Projection.wgs84())
grid = Grid(extent=extent, resolution=1.0)
print(grid)
# END
