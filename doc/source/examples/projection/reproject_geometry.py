from hubdc.core import *

utm = Projection.utm(zone=33)
wgs84 = Projection.wgs84()

point = Point(x=380000, y=5800000, projection=utm)
extent = Extent(xmin=380000, xmax=390000, ymin=5800000, ymax=5830000, projection=utm)
geometry = Geometry(wkt='POLYGON((380000 5830000,390000 5830000,390000 5800000,380000 5800000,380000 5830000))', projection=utm)

print(point.reproject(projection=wgs84))
print(extent.reproject(projection=wgs84))
print(geometry.reproject(projection=wgs84))

