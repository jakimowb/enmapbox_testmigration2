from hubdc.docutils import createDocPrint

print = createDocPrint(__file__)

# START
from hubdc.core import *

projection = Projection.wgs84()

# to well known text
print(projection.wkt())

# to OSR spatial reference
print(type(projection.osrSpatialReference()))
# END