from osgeo import gdal
from hubdc.model.PixelGrid import PixelGrid


class Band():

    def __init__(self, gdalBand, pixelGrid):
        assert isinstance(gdalBand, gdal.Band)
        assert isinstance(pixelGrid, PixelGrid)

        self.gdalBand = gdalBand
        self.pixelGrid = pixelGrid

    def readAsArray(self, dtype=None, ** kwargs):
        array = self.gdalBand.ReadAsArray(**kwargs)
        if dtype is not None:
            array = array.astype(dtype)
        return array

    def writeArray(self, array, pixelGrid=None):

        pixelGrid = self.pixelGrid if pixelGrid is None else pixelGrid
        assert isinstance(pixelGrid, PixelGrid)
        assert self.pixelGrid.equalProjection(pixelGrid), 'selfProjection: '+self.pixelGrid.projection+'\notherProjection: '+pixelGrid.projection
        assert self.pixelGrid.equalPixSize(pixelGrid)

        xoff=int(round((pixelGrid.xMin - self.pixelGrid.xMin)/self.pixelGrid.xRes, 0))
        yoff=int(round((self.pixelGrid.yMax - pixelGrid.yMax)/self.pixelGrid.yRes, 0))
        self.gdalBand.WriteArray(array, xoff=xoff, yoff=yoff)

    def setNoDataValue(self, value):
        self.gdalBand.SetNoDataValue(float(value))

    def getNoDataValue(self):
        return self.gdalBand.GetNoDataValue()

    def setDescription(self, value):
        self.gdalBand.SetDescription(value)

    def getMetadataDomainList(self):
        domains = self.gdalBand.GetMetadataDomainList()
        return domains if domains is not None else []
