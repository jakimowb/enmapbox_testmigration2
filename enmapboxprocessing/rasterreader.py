from math import isnan
from typing import Iterable, List, Union, Optional

from enmapboxprocessing.rasterblockinfo import RasterBlockInfo
from typeguard import typechecked
import numpy as np
from PyQt5.QtCore import QSizeF
from osgeo import gdal
from qgis._core import (QgsRasterLayer, QgsRasterDataProvider, QgsCoordinateReferenceSystem, QgsRectangle,
                        QgsRasterRange, QgsPoint, QgsRasterBlockFeedback, QgsRasterBlock, QgsPointXY,
                        QgsProcessingFeedback)

from enmapboxprocessing.typing import (QgisDataType, RasterSource, Array3d, Metadata, MetadataValue,
                                       MetadataDomain)
from enmapboxprocessing.utils import Utils

from enmapboxprocessing.gridwalker import GridWalker


@typechecked
class RasterReader(object):

    def __init__(self, source: RasterSource):

        if isinstance(source, QgsRasterLayer):
            provider = source.dataProvider()
        elif isinstance(source, QgsRasterDataProvider):
            provider = source
        elif isinstance(source, str):
            self._sourceLayer = QgsRasterLayer(source)
            provider = self._sourceLayer.dataProvider()
        elif isinstance(source, gdal.Dataset):
            provider = QgsRasterLayer(source.GetDescription())
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

    def noDataValue(self, bandNo: int = None):
        if bandNo is None:
            bandNo = 1
        return self.gdalDataset.GetRasterBand(bandNo).GetNoDataValue()

    def bandName(self, bandNo: int):
        return self.gdalBand(bandNo).GetDescription()

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

    def arrayFromBlock(self, block: RasterBlockInfo, bandList: List[int] = None, feedback: QgsRasterBlockFeedback = None):
        return self.arrayFromBoundingBoxAndSize(block.extent, block.width, block.height, bandList, feedback)

    def arrayFromBoundingBoxAndSize(
            self, boundingBox: QgsRectangle, width: int, height: int, bandList: List[int] = None,
            feedback: QgsRasterBlockFeedback = None
    ) -> Array3d:
        if bandList is None:
            bandList = range(1, self.provider.bandCount() + 1)
        arrays = list()
        for bandNo in bandList:
            assert 0 < bandNo <= self.bandCount()
            block: QgsRasterBlock = self.provider.block(bandNo, boundingBox, width, height, feedback)
            array = Utils.qgsRasterBlockToNumpyArray(block=block)
            arrays.append(array)
        return arrays

    def arrayFromPixelOffsetAndSize(
            self, xOffset: int, yOffset: int, width: int, height: int, bandList: List[int] = None,
            feedback: QgsRasterBlockFeedback = None
    ) -> Array3d:
        p1 = QgsPointXY(
            self.provider.transformCoordinates(QgsPoint(xOffset, yOffset), QgsRasterDataProvider.TransformImageToLayer)
        )
        p2 = QgsPointXY(
            self.provider.transformCoordinates(
                QgsPoint(xOffset + width, yOffset + height), QgsRasterDataProvider.TransformImageToLayer)
        )
        boundingBox = QgsRectangle(p1, p2)
        return self.arrayFromBoundingBoxAndSize(boundingBox, width, height, bandList, feedback)

    def array(
            self, xOffset: int = None, yOffset: int = None, width: int = None, height: int = None,
            bandList: List[int] = None, boundingBox: QgsRectangle = None, feedback: QgsRasterBlockFeedback = None
    ) -> Array3d:

        if boundingBox is None:
            if xOffset is None and width is None:
                xOffset = 0
                width = self.provider.xSize()
            if yOffset is None and height is None:
                yOffset = 0
                height = self.provider.ySize()
            array = self.arrayFromPixelOffsetAndSize(xOffset, yOffset, width, height, bandList, feedback)
        else:
            rasterUnitsPerPixelX = self.provider.extent().width() / self.provider.xSize()
            rasterUnitsPerPixelY = self.provider.extent().height() / self.provider.ySize()
            if width is None:
                width = int(round(boundingBox.width() / rasterUnitsPerPixelX))
            if height is None:
                height = int(round(boundingBox.height() / rasterUnitsPerPixelY))
            array = self.arrayFromBoundingBoxAndSize(boundingBox, width, height, bandList, feedback)
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
