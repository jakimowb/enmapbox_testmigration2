from hubdc.model import *


class UTMTilingScheme(object):

    ZONES = range(1,60)
    BANDS = 'efghjklmnpqrstuvwx'

    @classmethod
    def zoneExtent(cls, zone):
        assert zone in cls.ZONES
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

    @classmethod
    def bandExtent(cls, band):
        assert band in cls.BANDS
        ymin = cls.BANDS.index(band)*8 - 64
        return SpatialExtent(xmin=-180, xmax=180, ymin=ymin, ymax=ymin+8, projection=Projection.WGS84())

    @classmethod
    def bandByLatitude(cls, y):
        assert y >= -64 and y < 84
        off = -8
        i = int((y + 64) / 8.)
        return cls.BANDS[i]

    @classmethod
    def bandByPoint(cls, point):
        assert isinstance(point, SpatialPoint)
        wgs84Point = point.reproject(targetProjection=Projection.WGS84())
        return cls.bandByLatitude(y=wgs84Point.y())

    @classmethod
    def bandsByExtent(cls, extent):
        assert isinstance(extent, SpatialExtent)
        upperBand = cls.bandByPoint(extent.upperLeft())
        lowerBand = cls.bandByPoint(extent.lowerRight())
        indices = range(cls.BANDS.index(upperBand), cls.BANDS.index(lowerBand) + 1)
        return [cls.BANDS[index] for index in indices]

    @classmethod
    def mgrsGrids(cls, zone, band, resolution, anchor):

        assert isinstance(resolution, Resolution)
        assert isinstance(anchor, Point)

        # extent in WGS84 projection
        zoneExtent = cls.zoneExtent(zone=zone)
        bandExtent = cls.bandExtent(band=band)
        zoneBandExtent = zoneExtent.intersection(other=bandExtent)

        # corner coordinates in UTM projection
        wgs84Points = zoneBandExtent.corners()
        utmPoints = [point.reproject(targetProjection=Projection.UTM(zone=zone)) for point in wgs84Points]

        # calculate contained MGRS footprints
        xs = [point.x() for point in utmPoints]
        ys = [point.y() for point in utmPoints]
        xmin = functools.reduce(min, xs)
        xmax = functools.reduce(max, xs)
        ymin = functools.reduce(min, ys)
        ymax = functools.reduce(max ,ys)

        s = 100000
        xstart = int(xmin / s) * s
        xend = int(xmax / s) * s
        ystart = int(ymin / s) * s
        yend = int(ymax / s ) * s
        if xstart > xmin: xstart -= s
        if xend < xmax: xend += s
        if ystart > ymin: ystart -= s
        if yend < ymax: yend += s

        grids = list()
        for iy, y in enumerate(range(ystart, yend, s)):
            for ix, x in enumerate(range(xstart, xend, s)):
                #grid = Grid(extent=Extent(xmin=x, xmax=x+s, ymin=y, ymax=y+s),
                #            resolution=resolution,
                #            projection=Projection.UTM(zone=zone))
                #grid = grid.anchor(p=anchor)
                #if not any([p.withinExtent(zoneExtent) for p in grid.spatialExtent().corners()]):
                #    continue
                #gridTrimmed = grid.spatialExtent().intersection(other=zoneBandextent)
                #grids.append((gridTrimmed, iy, ix))

                # todo: create Polygon class for reprojecting/intersecting extens; Extent.reproject() is not suitable!
                mgrsExtentUTM = SpatialExtent(xmin=x, xmax=x + s, ymin=y, ymax=y + s, projection=Projection.UTM(zone=zone))
                mgrsPolygonWGS84 = mgrsExtentUTM.polygon().reproject(targetProjection=Projection.WGS84())
                zoneBandPolygon = zoneBandExtent.polygon()
                if not zoneBandPolygon.intersects(other=mgrsPolygonWGS84):
                    continue
                mgrsPolygonTrimmedWSG84 = zoneBandPolygon.intersection(other=mgrsPolygonWGS84)
                mgrsPolygonTrimmedUTM = mgrsPolygonTrimmedWSG84.reproject(targetProjection=Projection.UTM(zone=zone))
                mgrsExtentTrimmedUTM = SpatialExtent.fromPolygon(polygon=mgrsPolygonTrimmedUTM)

                grid = Grid(extent=mgrsExtentTrimmedUTM, resolution=resolution)
                grid = grid.anchor(point=anchor)
                grids.append((grid, iy, ix))
        return grids

for grid, iy, ix in UTMTilingScheme.mgrsGrids(zone=32, band='u', resolution=Resolution(x=30, y=30), anchor=Point(x=5, y=5)):
    print(grid.extent())

#for y in range(-64, 80, 8):
#    band = UTMTilingScheme.bandByLatitude(y=y)
#    print(y,UTMTilingScheme.bandByLatitude(y=y))

