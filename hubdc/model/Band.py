from osgeo import gdal


class Band():

    def __init__(self, gdalBand):
        assert isinstance(gdalBand, gdal.Band)
        self.gdalBand = gdalBand

    def setNoDataValue(self, value):
        self.gdalBand.SetNoDataValue(float(value))