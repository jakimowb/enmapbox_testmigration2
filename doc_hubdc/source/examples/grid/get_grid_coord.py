from hubdc.docutils import createDocPrint

print = createDocPrint(__file__)

# START
from hubflow.core import *

extent=Extent(xmin=-180.0, ymin=-90.0, xmax=180.0, ymax=90.0, projection=Projection.wgs84())
grid = Grid(extent=extent, resolution=10)
print(grid)
print(grid.size())

# Get x center coordinats.
print(grid.xMapCoordinates())

# Get y center coordinats.
print(grid.yMapCoordinates())
# END
