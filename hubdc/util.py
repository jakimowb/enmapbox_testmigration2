from osgeo import osr


def projectionFromEPSG(epsg):
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(2927)
    return srs.ExportToWkt()