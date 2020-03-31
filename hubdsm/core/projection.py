# from __future__ import annotations
from dataclasses import dataclass
from osgeo import osr


@dataclass(frozen=True)
class Projection(object):
    """Data structure for projections."""
    wkt: str

    def __post_init__(self):
        assert isinstance(self.wkt, str)

    def __eq__(self, other: 'Projection'):
        return self.osrSpatialReference.IsSame(other.osrSpatialReference)

    @classmethod
    def fromEpsg(cls, epsg: int) -> 'Projection':
        """Create projection by given authority ID."""
        projection = osr.SpatialReference()
        projection.ImportFromEPSG(int(epsg))
        return Projection(wkt=projection.ExportToWkt())

    @classmethod
    def fromWgs84(cls) -> 'Projection':
        """Create WGS 84 projection, also see http://spatialreference.org/ref/epsg/wgs-84/"""
        return cls.fromEpsg(epsg=4326)  # not working in Conda QGIS 3.10.2
        # return Projection(wkt='GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AXIS["Latitude",NORTH],AXIS["Longitude",EAST],AUTHORITY["EPSG","4326"]]')

    @property
    def osrSpatialReference(self) -> osr.SpatialReference:
        """Return osr.SpatialReference."""
        srs = osr.SpatialReference()
        srs.ImportFromWkt(self.wkt)
        return srs
