from typing import List, Union, Optional

from PyQt5.QtGui import QColor
from osgeo import gdal

from enmapboxprocessing.typing import Array3d, Array2d, MetadataValue, MetadataDomain, Metadata, QgisDataType, Number
from enmapboxprocessing.utils import Utils
from typeguard import typechecked


@typechecked
class RasterWriter(object):

    def __init__(self, gdalDataset: gdal.Dataset):
        self.gdalDataset = gdalDataset
        self._source: str = self.gdalDataset.GetDescription()

    def writeArray(self, array: Array3d, xOffset=0, yOffset=0, bandList: List[int] = None, overlap: int = None):
        if bandList is None:
            assert len(array) == self.bandCount()
            bandList = range(1, self.bandCount() + 1)
        for bandNo, array2d in zip(bandList, array):
            self.writeArray2d(array2d, bandNo, xOffset, yOffset, overlap)

    def writeArray2d(self, array: Array2d, bandNo: int, xOffset=0, yOffset=0, overlap: int = None):
        if overlap is not None:
            height, width = array.shape
            array = array[overlap:height - overlap, overlap:width - overlap]
        self.gdalBand(bandNo).WriteArray(array, xOffset, yOffset)

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
                self.gdalBand(bandNo).SetNoDataValue(noDataValue)
        else:
            self.gdalBand(bandNo).SetNoDataValue(noDataValue)

    def setOffset(self, offset: float = None, bandNo: int = None, overwrite=False):
        if offset is None:
            return
        if bandNo is None:
            for bandNo in range(1, self.bandCount() + 1):
                self.setOffset(offset, bandNo, overwrite)
        else:
            if not overwrite:
                if self.gdalBand(bandNo).GetOffset() is not None:
                    offset += self.gdalBand(bandNo).GetOffset()
            self.gdalBand(bandNo).SetOffset(offset)

    def setScale(self, scale: float = None, bandNo: int = None, overwrite=False):
        if scale is None:
            return
        if bandNo is None:
            for bandNo in range(1, self.bandCount() + 1):
                self.setScale(scale, bandNo, overwrite)
        else:
            if not overwrite:
                if self.gdalBand(bandNo).GetScale() is not None:
                    scale *= self.gdalBand(bandNo).GetScale()
            self.gdalBand(bandNo).SetScale(scale)

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

    def setWavelength(self, wavelength: Optional[Number], bandNo: int):
        if bandNo is None:
            return
        self.setMetadataItem('wavelength', wavelength, '', bandNo)
        self.setMetadataItem('wavelength_units', 'nanometers', '', bandNo)

    def setFwhm(self, fwhm: Optional[Number], bandNo: int):
        if bandNo is None:
            return
        self.setMetadataItem('fwhm', fwhm, '', bandNo)
        self.setMetadataItem('wavelength_units', 'nanometers', '', bandNo)

    def setBadBandMultiplier(self, badBandMultiplier: Optional[int], bandNo: int):
        if bandNo is None:
            return
        self.setMetadataItem('bad_band_multiplier', badBandMultiplier, '', bandNo)

    def bandCount(self) -> int:
        return self.gdalDataset.RasterCount

    def source(self) -> str:
        return self._source

    def dataType(self, bandNo: int = None) -> QgisDataType:
        if bandNo is None:
            bandNo = 1
        gdalDataType = self.gdalDataset.GetRasterBand(bandNo).DataType
        return Utils.gdalDataTypeToQgisDataType(gdalDataType)

    def dataTypeSize(self, bandNo: int = None) -> int:
        if bandNo is None:
            bandNo = 1
        qgisDataType = self.dataType(bandNo)
        dtype = Utils.qgisDataTypeToNumpyDataType(qgisDataType)
        return dtype().itemsize

    def width(self) -> int:
        return self.gdalDataset.RasterXSize

    def height(self) -> int:
        return self.gdalDataset.RasterYSize

    def _gdalObject(self, bandNo: int = None) -> Union[gdal.Dataset, gdal.Band]:
        if bandNo is None:
            return self.gdalDataset
        else:
            gdalBand: gdal.Band = self.gdalDataset.GetRasterBand(bandNo)
            assert gdalBand is not None
            return gdalBand

    def gdalBand(self, bandNo: int = None) -> gdal.Band:
        return self._gdalObject(bandNo)

    def close(self):
        self.gdalDataset.FlushCache()
        self.gdalDataset = None
