from os.path import splitext

from osgeo import gdal
from qgis._core import QgsRectangle, QgsCoordinateReferenceSystem, QgsProcessingFeedback

from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.rasterwriter import RasterWriter
from enmapboxprocessing.typing import Array3d, QgisDataType, CreationOptions
from typeguard import typechecked

from enmapboxprocessing.utils import Utils


@typechecked
class Driver(object):

    def __init__(
            self, filename: str, format: str = None, options: CreationOptions = None,
            feedback: QgsProcessingFeedback = None
    ):
        assert filename is not None
        if format is None:
            format = self.defaultFormat(filename)
        if options is None:
            options = list()
        self.filename = filename
        self.format = format
        self.options = options
        self.feedback = feedback

    def create(
            self, dataType: QgisDataType, width: int, height: int, nBands: int, extent: QgsRectangle = None,
            crs: QgsCoordinateReferenceSystem = None
    ) -> RasterWriter:

        if extent is None:
            extent = QgsRectangle(0, 0, width, height)
        if crs is None:
            crs = QgsCoordinateReferenceSystem('EPSG:4326')

        gdalDataType = Utils.qgisDataTypeToGdalDataType(dataType)
        xResolution = extent.width() / width
        yResolution = extent.height() / height
        gdalGeoTransform = extent.xMinimum(), xResolution, -0., extent.yMaximum(), -0., -yResolution

        info = f'Create Raster [{width}x{height}x{nBands}]({Utils.qgisDataTypeName(dataType)})' \
               f' -co {" ".join(self.options)}' \
               f' {self.filename}'
        if self.feedback is not None:
            self.feedback.pushInfo(info)

        gdalDriver: gdal.Driver = gdal.GetDriverByName(self.format)
        gdalDataset: gdal.Dataset = gdalDriver.Create(self.filename, width, height, nBands, gdalDataType, self.options)
        assert gdalDataset is not None
        gdalDataset.SetProjection(crs.toWkt())
        gdalDataset.SetGeoTransform(gdalGeoTransform)
        return RasterWriter(gdalDataset)

    def createFromArray(
            self, array: Array3d, extent: QgsRectangle = None,
            crs: QgsCoordinateReferenceSystem = None,
    ) -> RasterWriter:
        nBands = len(array)
        height, width = array[0].shape
        dataType = Utils.numpyDataTypeToQgisDataType(array[0].dtype)
        raster = self.create(dataType=dataType, width=width, height=height, nBands=nBands, extent=extent, crs=crs)
        raster.writeArray(array)
        return raster

    def createLike(
            self, raster: RasterReader, dataType: QgisDataType = None,
            nBands: int = None
    ) -> RasterWriter:
        provider = raster.provider
        if nBands is None:
            nBands = provider.bandCount()
        if dataType is None:
            dataType = raster.provider.dataType(bandNo=1)
        raster2 = self.create(dataType, provider.xSize(), provider.ySize(), nBands, provider.extent(), provider.crs())
        return raster2

    @classmethod
    def defaultFormat(cls, filename: str) -> str:
        extension = splitext(filename)[1]
        format = cls.formatFromExtension(extention=extension)
        return format

    @staticmethod
    def formatFromExtension(extention: str) -> str:
        extention = extention.lower()
        if extention in ['.tif', '.tiff']:
            format = 'GTiff'
        elif extention == '.vrt':
            format = 'VRT'
        else:
            format = 'ENVI'
        return format
