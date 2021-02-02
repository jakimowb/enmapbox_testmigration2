from typing import List, Union, Optional

from PyQt5.QtGui import QColor
from osgeo import gdal

from enmapboxprocessing.typing import Array3d, Array2d, MetadataValue, MetadataDomain, Metadata, QgisDataType, Category
from typeguard import typechecked
from qgis._core import QgsRasterDataProvider, QgsRectangle, QgsPointXY, QgsPoint, QgsRasterLayer, QgsFeedback

from enmapboxprocessing.utils import Utils


@typechecked
class RasterWriter(object):

    def __init__(self, gdalDataset: gdal.Dataset):
        self.gdalDataset = gdalDataset
        self._source: str = self.gdalDataset.GetDescription()

    def writeArray(self, array: Array3d, xOffset=0, yOffset=0, bandList: List[int] = None):
        if bandList is None:
            assert len(array) == self.bandCount()
            bandList = range(1, self.bandCount() + 1)
        for bandNo, array2d in zip(bandList, array):
            self.writeArray2d(array2d, bandNo, xOffset, yOffset)

    def writeArray2d(self, array: Array2d, bandNo: int, xOffset=0, yOffset=0):
        gdalBand: gdal.Band = self.gdalDataset.GetRasterBand(bandNo)
        gdalBand.WriteArray(array, xOffset, yOffset)

    def fill(self, value: float, bandNo: int = None):
        if bandNo is None:
            bands = range(1, self.bandCount() + 1)
        else:
            bands = [bandNo]
        for bandNo in bands:
            self._gdalObject(bandNo).Fill(value)

    def setNoDataValue(self, noDataValue: float = None, bandNo: int = None):
        if noDataValue is None:
            return
        if bandNo is None:
            for bandNo in range(1, self.bandCount() + 1):
                self.gdalDataset.GetRasterBand(bandNo).SetNoDataValue(noDataValue)
        else:
            self.gdalDataset.GetRasterBand(bandNo).SetNoDataValue(noDataValue)

    def setMetadataItem(self, key: str, value: MetadataValue, domain: str = '', bandNo: int = None):
        if value is None:
            return
        self._gdalObject(bandNo).SetMetadataItem(key, Utils.metadateValueToString(value), domain)

    def setMetadataDomain(self, metadata: MetadataDomain, domain: str = '', bandNo: int = None):
        self.gdalDataset.SetMetadata({}, domain)  # clear existing domain first
        for key, value in metadata.items():
            if key.replace(' ', '_') == 'file_compression':
                continue
            self.setMetadataItem(key, value, domain, bandNo)

    def setMetadata(self, metadata: Metadata, bandNo: int = None):
        for domain, metadata_ in metadata.items():
            self.setMetadataDomain(metadata_, domain, bandNo)

    def setBandName(self, bandName: str, bandNo: int):
        self.gdalBand(bandNo).SetDescription(bandName)

    def setCategoryNames(self, names: List[str] = None, bandNo: int = None):
        if bandNo is None:
            bandNo = 1
        gdalBand = self.gdalBand(bandNo)
        gdalBand.SetCategoryNames(names)

    def setCategoryColors(self, colors: List[QColor] = None, bandNo: int = None):
        if bandNo is None:
            bandNo = 1
        gdalBand = self.gdalBand(bandNo)

        colorTable = gdal.ColorTable()
        for i, color in enumerate(colors):
            colorTable.SetColorEntry(i, (color.red(), color.green(), color.blue()))
        gdalBand.SetColorTable(colorTable)

    def bandCount(self) -> int:
        return self.gdalDataset.RasterCount

    def source(self) -> str:
        return self._source

    def dataType(self, bandNo: int = None) -> QgisDataType:
        if bandNo is None:
            bandNo = 1
        dataType = self.gdalDataset.GetRasterBand(bandNo).DataType
        return Utils.gdalDataTypeToQgisDataType(dataType)

    def _gdalObject(self, bandNo: int = None) -> Union[gdal.Dataset, gdal.Band]:
        if bandNo is None:
            return self.gdalDataset
        else:
            gdalBand: gdal.Band = self.gdalDataset.GetRasterBand(bandNo)
            assert gdalBand is not None
            return gdalBand

    def gdalBand(self, bandNo: int = None) -> gdal.Band:
        return self._gdalObject(bandNo)
