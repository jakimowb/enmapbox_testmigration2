from osgeo import osr

def equalProjection(p1, p2):
    sr1 = osr.SpatialReference(wkt=str(p1) if p1 is not None else '')
    sr2 = osr.SpatialReference(wkt=str(p2) if p2 is not None else '')
    return bool(sr1.IsSame(sr2))

