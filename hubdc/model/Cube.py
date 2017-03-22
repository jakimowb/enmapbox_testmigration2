from osgeo import gdal
from rios.imageio import NumpyTypeToGDALType, GDALTypeToNumpyType
from hubdc.model.PixelGrid import PixelGrid
from hubdc.model.Dataset import Dataset
from hubdc.model.DatasetList import DatasetList
from hubdc.util import projectionFromEPSG


class Cube(object):

    def __init__(self, projection=None, xRes=None, yRes=None, xMin=None, xMax=None, yMin=None, yMax=None,
                 pixelGrid=None):

        if pixelGrid is None:
            if projection.startswith('EPSG:'):
                projection = projectionFromEPSG(epsg=int(projection[-4:]))
            pixelGrid = PixelGrid(projection=projection, xRes=xRes, yRes=yRes, xMin=xMin, xMax=xMax, yMin=yMin, yMax=yMax)

        assert isinstance(pixelGrid, PixelGrid)
        self.pixelGrid = pixelGrid

    def create(self, bands=1, eType=gdal.GDT_Float32, dstName='', format='MEM', creationOptions=[]):

        driver = gdal.GetDriverByName(format)
        ysize, xsize = self.pixelGrid.getDimensions()
        gdalDataset = driver.Create(dstName, xsize, ysize, bands, eType, creationOptions)
        gdalDataset.SetProjection(self.pixelGrid.projection)
        gdalDataset.SetGeoTransform(self.pixelGrid.makeGeoTransform())
        return Dataset(gdalDataset=gdalDataset)

    def createArray(self, array, dstName='', format='MEM', creationOptions=[]):
        bands = len(array)
        eType = NumpyTypeToGDALType(array[0].dtype)
        ds = self.create(bands=bands, eType=eType, dstName=dstName, format=format, creationOptions=creationOptions)
        ds.writeArray(array)
        assert ds.shape == array.shape
        return ds

    def warp(self, ds, dstName='', format='MEM', creationOptions=[], **kwargs):
        return ds.warp(dstPixelGrid=self.pixelGrid, dstName=dstName, format=format, creationOptions=creationOptions, **kwargs)

    def buildVRT(self, dsl, dstName, **kwargs):
        assert isinstance(dsl, DatasetList)
        options = gdal.BuildVRTOptions(resolution='user',
                                       outputBounds=tuple(getattr(self.pixelGrid, key) for key in ('xMin', 'yMin', 'xMax', 'yMax')),
                                       xRes=self.pixelGrid.xRes, yRes=self.pixelGrid.yRes, **kwargs)
        gdalDS = gdal.BuildVRT(destName=dstName, srcDSOrSrcDSTab=[ds.gdalDataset for ds in dsl])#, options=options)
        return Dataset(gdalDS)

    def generateSubcubes(self, windowxsize=256, windowysize=256):
        ysize, xsize = self.pixelGrid.getDimensions()
        tile = 0
        yoff = 0
        while yoff < ysize:
            xoff = 0
            while xoff < xsize:
                pixelGridTile = self.pixelGrid.subsetPixelWindow(xoff=xoff, yoff=yoff, width=windowxsize, height=windowysize)
                pixelGridTile = pixelGridTile.intersection(self.pixelGrid)
                yield Cube(pixelGrid=pixelGridTile)
                xoff += windowxsize
            yoff += windowysize