from math import isnan
from typing import Iterable, List, Union, Optional

import numpy as np
from PyQt5.QtCore import QSizeF
from osgeo import gdal
from qgis._core import (QgsRasterLayer, QgsRasterDataProvider, QgsCoordinateReferenceSystem, QgsRectangle,
                        QgsRasterRange, QgsPoint, QgsRasterBlockFeedback, QgsRasterBlock, QgsPointXY,
                        QgsProcessingFeedback)

from enmapboxprocessing.gridwalker import GridWalker
from enmapboxprocessing.rasterblockinfo import RasterBlockInfo
from enmapboxprocessing.typing import (QgisDataType, RasterSource, Array3d, Metadata, MetadataValue,
                                       MetadataDomain)
from enmapboxprocessing.utils import Utils
from typeguard import typechecked


@typechecked
class RasterReader(object):

    Nanometers = 'Nanometers'
    Micrometers = 'Micrometers'

    def __init__(self, source: RasterSource):

        if isinstance(source, QgsRasterLayer):
            provider = source.dataProvider()
        elif isinstance(source, QgsRasterDataProvider):
            provider = source
        elif isinstance(source, str):
            self._sourceLayer = QgsRasterLayer(source)
            provider = self._sourceLayer.dataProvider()
        elif isinstance(source, gdal.Dataset):
            self._sourceLayer = QgsRasterLayer(source.GetDescription())
            provider = self._sourceLayer.dataProvider()
        else:
            assert 0

        if isinstance(source, gdal.Dataset):
            gdalDataset = source
        else:
            gdalDataset: gdal.Dataset = gdal.Open(provider.dataSourceUri(), gdal.GA_ReadOnly)

        self.provider: QgsRasterDataProvider = provider
        self.gdalDataset = gdalDataset
        assert self.gdalDataset is not None

    def bandCount(self):
        return self.provider.bandCount()

    def bandName(self, bandNo: int) -> str:
        return self.gdalBand(bandNo).GetDescription()

    def crs(self) -> QgsCoordinateReferenceSystem:
        return self.provider.crs()

    def dataType(self, bandNo: int = None) -> QgisDataType:
        if bandNo is None:
            bandNo = 1
        return self.provider.dataType(bandNo)

    def dataTypeSize(self, bandNo: int = None) -> int:
        if bandNo is None:
            bandNo = 1
        return self.provider.dataTypeSize(bandNo)

    def extent(self) -> QgsRectangle:
        return self.provider.extent()

    def noDataValue(self, bandNo: int = None) -> Optional[float]:
        if bandNo is None:
            bandNo = 1
        return self.gdalBand(bandNo).GetNoDataValue()

    def offset(self, bandNo) -> Optional[float]:
        return self.gdalBand(bandNo).GetOffset()

    def scale(self, bandNo) -> Optional[float]:
        return self.gdalBand(bandNo).GetScale()

    def setUserNoDataValue(self, bandNo: int, noData: Iterable[QgsRasterRange]):
        return self.provider.setUserNoDataValue(bandNo, noData)

    def userNoDataValues(self, bandNo: int = None) -> List[QgsRasterRange]:
        if bandNo is None:
            bandNo = 1
        return self.provider.userNoDataValues(bandNo)

    def setUseSourceNoDataValue(self, bandNo: int, use: bool):
        return self.provider.setUseSourceNoDataValue(bandNo, use)

    def sourceHasNoDataValue(self, bandNo: int = None):
        if bandNo is None:
            bandNo = 1
        return self.provider.sourceHasNoDataValue(bandNo)

    def useSourceNoDataValue(self, bandNo: int = None) -> bool:
        if bandNo is None:
            bandNo = 1
        return self.provider.useSourceNoDataValue(bandNo)

    def source(self) -> str:
        return self.provider.dataSourceUri()

    def width(self) -> int:
        return self.provider.xSize()

    def height(self) -> int:
        return self.provider.ySize()

    def rasterUnitsPerPixelX(self) -> float:
        return self.provider.extent().width() / self.provider.xSize()

    def rasterUnitsPerPixelY(self) -> float:
        return self.provider.extent().height() / self.provider.ySize()

    def rasterUnitsPerPixel(self) -> QSizeF:
        return QSizeF(self.rasterUnitsPerPixelX(), self.rasterUnitsPerPixelY())

    def walkGrid(self, blockSizeX: int, blockSizeY: int, feedback: QgsProcessingFeedback = None):
        pixelSizeX = self.rasterUnitsPerPixelX()
        pixelSizeY = self.rasterUnitsPerPixelY()
        extent = self.extent()
        for blockExtent in GridWalker(extent, blockSizeX, blockSizeY, pixelSizeX, pixelSizeY, feedback):
            xOffset = int(round((blockExtent.xMinimum() - extent.xMinimum()) / pixelSizeX))
            yOffset = int(round((extent.yMaximum() - blockExtent.yMaximum()) / pixelSizeY))
            width = min(blockSizeX, int(round((blockExtent.xMaximum() - blockExtent.xMinimum()) / pixelSizeX)))
            height = min(blockSizeY, int(round((blockExtent.yMaximum() - blockExtent.yMinimum()) / pixelSizeY)))
            yield RasterBlockInfo(blockExtent, xOffset, yOffset, width, height)

    def arrayFromBlock(
            self, block: RasterBlockInfo, bandList: List[int] = None, overlap: int = None,
            feedback: QgsRasterBlockFeedback = None
    ):
        return self.arrayFromBoundingBoxAndSize(
            block.extent, block.width, block.height, bandList, overlap, feedback
        )

    def arrayFromBoundingBoxAndSize(
            self, boundingBox: QgsRectangle, width: int, height: int, bandList: List[int] = None,
            overlap: int = None, feedback: QgsRasterBlockFeedback = None
    ) -> Array3d:
        if bandList is None:
            bandList = range(1, self.provider.bandCount() + 1)
        if overlap is not None:
            xres = boundingBox.width() / width
            yres = boundingBox.height() / height
            boundingBox = QgsRectangle(
                boundingBox.xMinimum() - overlap * xres,
                boundingBox.yMinimum() - overlap * yres,
                boundingBox.xMaximum() + overlap * xres,
                boundingBox.yMaximum() + overlap * yres
            )
            width = width + 2 * overlap
            height = height + 2 * overlap
        arrays = list()
        for bandNo in bandList:
            assert 0 < bandNo <= self.bandCount()
            block: QgsRasterBlock = self.provider.block(bandNo, boundingBox, width, height, feedback)
            array = Utils.qgsRasterBlockToNumpyArray(block=block)
            arrays.append(array)
        return arrays

    def arrayFromPixelOffsetAndSize(
            self, xOffset: int, yOffset: int, width: int, height: int, bandList: List[int] = None, overlap: int = None,
            feedback: QgsRasterBlockFeedback = None
    ) -> Array3d:
        if self.crs().isValid():
            p1 = QgsPoint(xOffset, yOffset)
            p2 = QgsPoint(xOffset + width, yOffset + height)
            p1 = QgsPointXY(self.provider.transformCoordinates(p1, QgsRasterDataProvider.TransformImageToLayer))
            p2 = QgsPointXY(self.provider.transformCoordinates(p2, QgsRasterDataProvider.TransformImageToLayer))
        else:
            assert self.rasterUnitsPerPixel() == QSizeF(1, 1)
            p1 = QgsPointXY(xOffset, - yOffset)
            p2 = QgsPointXY(xOffset + width, -(yOffset + height))
        boundingBox = QgsRectangle(p1, p2)
        return self.arrayFromBoundingBoxAndSize(boundingBox, width, height, bandList, overlap, feedback)

    def array(
            self, xOffset: int = None, yOffset: int = None, width: int = None, height: int = None,
            bandList: List[int] = None, boundingBox: QgsRectangle = None, overlap: int = None,
            feedback: QgsRasterBlockFeedback = None
    ) -> Array3d:

        if boundingBox is None:
            if xOffset is None and width is None:
                xOffset = 0
                width = self.provider.xSize()
            if yOffset is None and height is None:
                yOffset = 0
                height = self.provider.ySize()
            array = self.arrayFromPixelOffsetAndSize(xOffset, yOffset, width, height, bandList, overlap, feedback)
        else:
            rasterUnitsPerPixelX = self.provider.extent().width() / self.provider.xSize()
            rasterUnitsPerPixelY = self.provider.extent().height() / self.provider.ySize()
            if width is None:
                width = int(round(boundingBox.width() / rasterUnitsPerPixelX))
            if height is None:
                height = int(round(boundingBox.height() / rasterUnitsPerPixelY))
            array = self.arrayFromBoundingBoxAndSize(boundingBox, width, height, bandList, overlap, feedback)
        return array

    def maskArray(
            self, array: Array3d, bandList: List[int] = None, maskNotFinite=True, defaultNoDataValue: float = None
    ) -> Array3d:
        if bandList is None:
            bandList = range(1, self.provider.bandCount() + 1)
        assert len(bandList) == len(array)
        maskArray = list()
        for i, a in enumerate(array):
            bandNo = i + 1
            m = np.full_like(a, True, dtype=bool)
            if self.provider.sourceHasNoDataValue(bandNo) and self.provider.useSourceNoDataValue(bandNo):
                noDataValue = self.provider.sourceNoDataValue(bandNo)
                if not isnan(noDataValue):
                    m[a == noDataValue] = False
            else:
                if defaultNoDataValue is not None:
                    m[a == defaultNoDataValue] = False
            rasterRange: QgsRasterRange
            for rasterRange in self.provider.userNoDataValues(bandNo):
                if rasterRange.bounds() == QgsRasterRange.IncludeMinAndMax:
                    contained = np.greater_equal(a, rasterRange.min())
                    np.less_equal(a, rasterRange.max(), out=contained)
                if rasterRange.bounds() == QgsRasterRange.IncludeMinAndMax:
                    contained = np.greater_equal(a, rasterRange.min())
                    np.less_equal(a, rasterRange.max(), out=contained)
                elif rasterRange.bounds() == QgsRasterRange.IncludeMin:
                    contained = np.greater_equal(a, rasterRange.min())
                    np.less(a, rasterRange.max(), out=contained)
                elif rasterRange.bounds() == QgsRasterRange.IncludeMax:
                    contained = np.greater(a, rasterRange.min())
                    np.less_equal(a, rasterRange.max(), out=contained)
                elif rasterRange.bounds() == QgsRasterRange.Exclusive:
                    contained = np.greater(a, rasterRange.min())
                    np.less(a, rasterRange.max(), out=contained)
                else:
                    assert 0
                m[contained] = False
                if maskNotFinite:
                    m[np.logical_not(np.isfinite(a))] = False
            maskArray.append(m)
        return maskArray

    def metadataItem(self, key: str, domain: str = '', bandNo: int = None) -> Optional[MetadataValue]:
        string = self._gdalObject(bandNo).GetMetadataItem(key, domain)
        if string is None:
            string = self._gdalObject(bandNo).GetMetadataItem(key.replace(' ', '_'), domain)
        if string is None:
            return None
        return Utils.stringToMetadateValue(string)

    def metadataDomain(self, domain: str = '', bandNo: int = None) -> MetadataDomain:
        return {
            key: Utils.stringToMetadateValue(value)
            for key, value in self._gdalObject(bandNo).GetMetadata(domain).items()
        }

    def metadata(self, bandNo: int = None) -> Metadata:
        domains = self._gdalObject(bandNo).GetMetadataDomainList()
        return {domain: self.metadataDomain(domain, bandNo) for domain in domains}

    def isSpectralRasterLayer(self, quickCheck=True):
        if quickCheck:
            return self.wavelength(1) is not None
        else:
            for bandNo in range(1, self.bandCount() + 1):
                if self.wavelength(bandNo) is None:
                    return False
            return True

    def findBandName(self, bandName: str) -> int:
        for bandNo in range(1, self.bandCount() + 1):
            if self.bandName(bandNo) == bandName:
                return bandNo
        raise ValueError(f'unknown band name: {bandName}')

    def findWavelength(self, wavelength: Optional[float]) -> Optional[int]:
        bandNos = list()
        distances = list()
        for bandNo in range(1, self.bandCount() + 1):
            wavelength_ = self.wavelength(bandNo)
            if wavelength is None:
                continue
            bandNos.append(bandNo)
            distances.append(abs(wavelength_ - wavelength))
        if len(bandNos) == 0:
            return None

        return bandNos[np.argmin(distances)]

    def wavelengthUnits(self, bandNo: int) -> Optional[str]:
        """Return wavelength units."""
        units = self.metadataItem('wavelength units', '', bandNo)
        if units is None:
            units = self.metadataItem('wavelength units', 'ENVI')
            if units is None:
                return None

        # normalise string
        if units.lower() in ['micrometers', 'um']:
            return self.Micrometers
        elif units.lower() in ['nanometers', 'nm']:
            return self.Nanometers
        else:
            raise ValueError(f'unsupported wavelength units: {units}')

    def wavelength(self, bandNo: int, units: str = None) -> Optional[float]:
        """Return band center wavelength in nanometers. Optionally, specify destination units."""
        wavelength = self.metadataItem('wavelength', '', bandNo)
        if wavelength is None:
            wavelengths = self.metadataItem('wavelength', 'ENVI')
            if wavelengths is None:
                return None
            else:
                wavelength = wavelengths[bandNo - 1]
                wavelength_units = self.metadataItem('wavelength_units', 'ENVI')
        else:
            wavelength_units = self.metadataItem('wavelength_units', '', bandNo)

        # convert to nanometers
        if wavelength_units.lower() in ['micrometers', 'um']:
            scale = 1000.
        elif wavelength_units.lower() in ['nanometers', 'nm']:
            scale = 1.
        else:
            raise ValueError(f'unsupported wavelength units: {wavelength_units}')
        wavelength = float(wavelength) * scale

        # convert to destination units
        if units is not None:
            if units.lower() in ['micrometers', 'um']:
                scale = 1 / 1000.
            elif units.lower() in ['nanometers', 'nm']:
                scale = 1.
            else:
                raise ValueError(f'unsupported wavelength units: {units}')
            wavelength *= scale

        return wavelength

    def fwhm(self, bandNo: int, units: str = None) -> Optional[float]:
        """Return band FWHM in nanometers. Optionally, specify destination units."""
        fwhm = self.metadataItem('fwhm', '', bandNo)
        if fwhm is None:
            fwhms = self.metadataItem('fwhm', 'ENVI')
            if fwhms is None:
                return None
            else:
                fwhm = fwhms[bandNo - 1]
                wavelength_units = self.metadataItem('wavelength_units', 'ENVI')
        else:
            wavelength_units = self.metadataItem('wavelength_units', '', bandNo)

        # convert to nanometers
        if wavelength_units.lower() in ['micrometers', 'um']:
            scale = 1000.
        elif wavelength_units.lower() in ['nanometers', 'nm']:
            scale = 1.
        else:
            raise ValueError(f'unsupported wavelength units: {wavelength_units}')
        fwhm = float(fwhm) * scale

        # convert to destination units
        if units is not None:
            if units.lower() in ['micrometers', 'um']:
                scale = 1 / 1000.
            elif units.lower() in ['nanometers', 'nm']:
                scale = 1.
            else:
                raise ValueError(f'unsupported wavelength units: {units}')
            fwhm *= scale

        return fwhm


    def badBandMultiplier(self, bandNo: int) -> Optional[int]:
        """Return bad band multiplier, typically 0 for bad bands and 1 for good bands."""
        badBandMultiplier = self.metadataItem('bad band multiplier', '', bandNo)
        if badBandMultiplier is None:
            bbl = self.metadataItem('bbl', 'ENVI')
            if bbl is None:
                return 1
            else:
                badBandMultiplier = bbl[bandNo - 1]
        return int(badBandMultiplier)

    def lineMemoryUsage(self, nBands: int = None, dataTypeSize: int = None) -> int:
        if nBands is None:
            nBands = self.bandCount()
        if dataTypeSize is None:
            dataTypeSize = self.dataTypeSize()
        return self.width() * nBands * dataTypeSize

    def _gdalObject(self, bandNo: int = None) -> Union[gdal.Band, gdal.Dataset]:
        if bandNo is None:
            gdalObject = self.gdalDataset
        else:
            gdalObject = self.gdalDataset.GetRasterBand(bandNo)
        return gdalObject

    def gdalBand(self, bandNo: int) -> gdal.Band:
        return self.gdalDataset.GetRasterBand(bandNo)
