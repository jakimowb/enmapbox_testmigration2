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
    def mgrsGrids(cls, zone, band, resolution, anchor, roi=None):

        assert isinstance(resolution, Resolution)
        assert isinstance(anchor, Point)
        if roi is not None:
            assert isinstance(roi, SpatialGeometry)
            roiUTM = roi.reproject(targetProjection=Projection.UTM(zone=zone))

        # extent in WGS84 projection
        zoneExtent = cls.zoneExtent(zone=zone)
        bandExtent = cls.bandExtent(band=band)
        zoneBandExtent = zoneExtent.intersection(other=bandExtent)

        # extent in UTM projection
        zoneBandExtentUTM = zoneBandExtent.reproject(targetProjection=Projection.UTM(zone=zone))


        xmin = zoneBandExtentUTM.xmin()
        xmax = zoneBandExtentUTM.xmax()
        ymin = zoneBandExtentUTM.ymin()
        ymax = zoneBandExtentUTM.ymax()

        s = 100000
        xstart = int(xmin / s) * s
        xend = int(xmax / s) * s
        ystart = int(ymin / s) * s
        yend = int(ymax / s ) * s
        if xstart > xmin: xstart -= s
        if xend < xmax: xend += s
        if ystart > ymin: ystart -= s
        if yend < ymax: yend += s

        grids = dict()
        for iy, ymin in enumerate(range(ystart, yend, s)):
            for ix, xmin in enumerate(range(xstart, xend, s)):
                mgrsExtentUTM = SpatialExtent(xmin=xmin, xmax=xmin + s, ymin=ymin, ymax=ymin + s, projection=Projection.UTM(zone=zone))
                mgrsGeometryUTM = mgrsExtentUTM.geometry()
                mgrsGeometryWGS84 = mgrsGeometryUTM.reproject(targetProjection=Projection.WGS84())

                zoneBandGeometry = zoneBandExtent.geometry()

                # skip all grids outside the utm zone
                if not zoneBandGeometry.intersects(other=mgrsGeometryWGS84):
                    continue
                mgrsGeometryTrimmedWSG84 = zoneBandGeometry.intersection(other=mgrsGeometryWGS84)
                mgrsGeometryTrimmedUTM = mgrsGeometryTrimmedWSG84.reproject(targetProjection=Projection.UTM(zone=zone))

                # skip all grids outside the roi
                if roi is not None:
                    if not roiUTM.intersects(other=mgrsGeometryTrimmedUTM):
                        continue
                mgrsExtentTrimmedUTM = SpatialExtent.fromGeometry(geometry=mgrsGeometryTrimmedUTM)

                grid = Grid(extent=mgrsExtentTrimmedUTM, resolution=resolution)
                grid = grid.anchor(point=anchor)
                grids[(iy, ix)] = grid
        return grids

