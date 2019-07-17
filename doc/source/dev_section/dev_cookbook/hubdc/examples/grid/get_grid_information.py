from hubdc.docutils import createDocPrint

print = createDocPrint(__file__)

from hubflow.core import *
extent = Extent(xmin=-180.0, ymin=-90.0, xmax=180.0, ymax=90.0, projection=Projection.wgs84())
grid = Grid(extent=extent, resolution=1.0)

# START
print(grid.shape())
print(grid.size())
print(grid.geoTransform())
# END
