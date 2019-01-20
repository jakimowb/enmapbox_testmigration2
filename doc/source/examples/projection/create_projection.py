from hubdc.core import *

# from well known text
print(Projection(wkt='GEOGCS["WGS84", DATUM["WGS_1984", SPHEROID["WGS84",6378137,298.257223563, AUTHORITY["EPSG","7030"]], AUTHORITY["EPSG","6326"]], PRIMEM["Greenwich",0, AUTHORITY["EPSG","8901"]], UNIT["degree",0.0174532925199433, AUTHORITY["EPSG","9122"]], AUTHORITY["EPSG","4326"]]'))

# from EPSG code
print(Projection.fromEpsg(epsg=4326))

# some predefined projections
print(Projection.wgs84())
print(Projection.wgs84WebMercator())
print(Projection.utm(zone=33, north=True))
print(Projection.utm(zone=33, north=False))
