from hubdc.model import *


class UTMTilingScheme(object):
    @staticmethod
    def extent(zone):
        assert isinstance(zone, int)
        assert zone >= 1 and zone <= 60
        xmin = -180 + 6 * (zone - 1)
        return SpatialExtent(xmin=xmin, xmax=xmin + 6, ymin=-90, ymax=90, projection=Projection.WGS84())

    @staticmethod
    def zoneByLongitude(x):
        assert x >= -180 and x <= 180
        zone = int((x + 180) / 6. + 1)
        zone = min(zone, 60) # handle just the special case of x == 180
        return zone

    @classmethod
    def zoneByPoint(cls, point):
        assert isinstance(point, SpatialPoint)
        wgs84Point = point.reproject(targetProjection=Projection.WGS84())
        return cls.zoneByLongitude(x=wgs84Point.x())

    @classmethod
    def zonesByExtent(cls, extent):
        assert isinstance(extent, SpatialExtent)
        leftZone = cls.zoneByPoint(extent.upperLeft())
        rightZone = cls.zoneByPoint(extent.lowerRight())
        return range(leftZone, rightZone + 1)
