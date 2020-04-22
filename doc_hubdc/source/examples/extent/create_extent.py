from hubdc.docutils import createDocPrint

print = createDocPrint(__file__)

# START
from hubflow.core import *

# create a extent in WGS84 for the whole world
extent=Extent(xmin=-180.0, ymin=-90.0, xmax=180.0, ymax=90.0, projection=Projection.wgs84())
print(extent)
# END
