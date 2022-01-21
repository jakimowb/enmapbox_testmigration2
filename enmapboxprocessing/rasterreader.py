from math import isnan
from typing import Iterable, List, Union, Optional, Tuple

import numpy as np
from PyQt5.QtCore import QSizeF, QDateTime
from osgeo import gdal
from qgis._core import (QgsRasterLayer, QgsRasterDataProvider, QgsCoordinateReferenceSystem, QgsRectangle,
                        QgsRasterRange, QgsPoint, QgsRasterBlockFeedback, QgsRasterBlock, QgsPointXY,
                        QgsProcessingFeedback, QgsProject)

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
            self.layer = source
            self.provider: QgsRasterDataProvider = self.layer.dataProvider()
        elif isinstance(source, QgsRasterDataProvider):
            self.layer = QgsRasterLayer()  # invalid layer!; all QGIS PAM items will get lost
            self.provider = source
        elif isinstance(source, str):
            self.layer = QgsRasterLayer(source)
            self.provider: QgsRasterDataProvider = self.layer.dataProvider()
        elif isinstance(source, gdal.Dataset):
            self.layer = QgsRasterLayer(source.GetDescription())
            self.provider: QgsRasterDataProvider = self.layer.dataProvider()
        else:
            assert 0

        if isinstance(source, gdal.Dataset):
            gdalDataset = source
        else:
            gdalDataset: gdal.Dataset = gdal.Open(self.provider.dataSourceUri(), gdal.GA_ReadOnly)

        self.gdalDataset = gdalDataset
        assert self.gdalDataset is not None

    def bandCount(self):
        return self.provider.bandCount()

    def bandNumbers(self):
        for bandNo in range(1, self.provider.bandCount() + 1):
            yield bandNo

    def bandName(self, bandNo: int) -> str:
        return ': '.join(self.layer.bandName(bandNo).split(': ')[1:])  # removes the "Band 042: " prefix

    def userBandName(self, bandNo: int) -> Optional[str]:
        return self.metadataItem('name', '', bandNo)

    def setUserBandName(self, bandName: str, bandNo: int):
        self.setMetadataItem('name', bandName, '', bandNo)

    def bandOffset(self, bandNo: int) -> float:
        return self.provider.bandOffset(bandNo)

    def userBandOffset(self, bandNo: int, default: float = None) -> Optional[float]:
        offset = self.metadataItem('offset', '', bandNo)
        if offset is None:
            offset = default
        if offset is None:
            return None
        return float(offset)

    def setUserBandOffset(self, offset, bandNo: int):
        self.setMetadataItem('offset', offset, '', bandNo)

    def bandScale(self, bandNo: int) -> float:
        return self.provider.bandScale(bandNo)

    def userBandScale(self, bandNo: int, default: float = None) -> Optional[float]:
        scale = self.metadataItem('scale', '', bandNo)
        if scale is None:
            scale = default
        if scale is None:
            return None
        return float(scale)

    def setUserBandScale(self, scale, bandNo: int):
        self.setMetadataItem('scale', scale, '', bandNo)

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

    def offset(self, bandNo) -> Optional[float]:
        return self.provider.bandOffset(bandNo)

    def scale(self, bandNo) -> Optional[float]:
        return self.provider.bandScale(bandNo)

    def noDataValue(self, bandNo: int = None) -> Optional[float]:
        if bandNo is None:
            bandNo = 1
        return self.sourceNoDataValue(bandNo)

    def sourceNoDataValue(self, bandNo: int):
        return self.provider.sourceNoDataValue(bandNo)

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
            userBandScale = self.userBandScale(bandNo)
            userBandOffset = self.userBandOffset(bandNo)
            if userBandOffset is not None or userBandScale is not None:
                array = array.astype(np.float32)
                maskArray = self.maskArray(array[None], [bandNo], False)[0]
                if userBandScale is not None:
                    array[maskArray] *= userBandScale
                if userBandOffset is not None:
                    array[maskArray] += userBandOffset

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

    def propertyKey(self, key: str, domain: str, bandNo: int = None):
        key = key.replace(' ', '_')
        if bandNo is None:
            propertyKey = f'QGISPAM/dataset/{domain}/{key}'
        else:
            propertyKey = f'QGISPAM/band/{bandNo}/{domain}/{key}'
        return propertyKey

    def propertyKeyComponents(self, propertyKey: str) -> Tuple[str, str, Optional[int]]:
        if propertyKey.startswith('QGISPAM/dataset'):
            _, _, domain, key = propertyKey.split('/')
            bandNo = None
        elif propertyKey.startswith('QGISPAM/band'):
            _, _, bandNo, domain, key = propertyKey.split('/')
            bandNo = int(bandNo)
        else:
            raise ValueError('invalid QGIS PAM property key')
        key = key.replace(' ', '_')
        return key, domain, bandNo

    def setMetadataItem(self, key: str, value: MetadataValue, domain: str = '', bandNo: int = None):
        """Set metadata item as custom layer property. This shadows GDAL PAM metadata items."""
        propertyKey = self.propertyKey(key, domain, bandNo)
        self.layer.setCustomProperty(propertyKey, value)

    def removeMetadataItem(self, key: str, domain: str = '', bandNo: int = None):
        """Remove metadata item from QGIS PAM. It may still exist in GDAL PAM."""
        self.layer.removeCustomProperty(self.propertyKey(key, domain, bandNo))

    def removeMetadataDomain(self, domain: str, bandNo: int = None):
        """Remove metadata domain from QGIS PAM. It may still exist in GDAL PAM."""
        for propertyKey in self.layer.customPropertyKeys():
            if not propertyKey.startswith('QGISPAM'):
                continue
            _, domain2, _ = self.propertyKeyComponents(propertyKey)
            if domain == domain2:
                self.layer.removeCustomProperty(propertyKey)

    def metadataItem(
            self, key: str, domain: str = '', bandNo: int = None, ignoreQgisPam=False
    ) -> Optional[MetadataValue]:

        # check QGIS PAM (i.e. custom layer properties) first
        if not ignoreQgisPam:
            if self.layer is not None:
                propertyKey = self.propertyKey(key, domain, bandNo)
                if propertyKey in self.layer.customPropertyKeys():
                    value = self.layer.customProperty(propertyKey)
                    return value

        # if not found, check GDAL PAM afterwards
        string = self._gdalObject(bandNo).GetMetadataItem(key, domain)
        if string is None:
            string = self._gdalObject(bandNo).GetMetadataItem(key.replace(' ', '_'), domain)
        if string is None:
            return None
        return Utils.stringToMetadateValue(string)

    def metadataDomain(self, domain: str = '', bandNo: int = None, ignoreQgisPam=False) -> MetadataDomain:

        # get GDAL PAM metadata first
        metadata = {
            key: Utils.stringToMetadateValue(value)
            for key, value in self._gdalObject(bandNo).GetMetadata(domain).items()
        }

        # overwrite with QGIS PAM afterwards
        if ignoreQgisPam:
            return metadata

        for propertyKey in self.layer.customPropertyKeys():
            if not propertyKey.startswith('QGISPAM'):
                continue

            key, domain2, bandNo2 = self.propertyKeyComponents(propertyKey)

            if domain != domain2 or bandNo != bandNo2:
                continue

            metadata[key] = self.layer.customProperty(propertyKey)

        return metadata

    def metadata(self, bandNo: int = None) -> Metadata:
        #domains = self._gdalObject(bandNo).GetMetadataDomainList()
        domains = self.metadataDomainKeys(bandNo)
        return {domain: self.metadataDomain(domain, bandNo) for domain in domains}

    def metadataDomainKeys(self, bandNo: int = None, ignoreQgisPam=False) -> List[str]:

        # get GDAL PAM domains
        domains: List = self._gdalObject(bandNo).GetMetadataDomainList()
        if domains is None:
            domains = []
        if ignoreQgisPam:
            return domains

        # add QGIS PAM domains
        for propertyKey in self.layer.customPropertyKeys():
            if not propertyKey.startswith('QGISPAM'):
                continue

            _, domain, bandNo2 = self.propertyKeyComponents(propertyKey)

            if bandNo != bandNo2:
                continue

            if domain not in domains:
                domains.append(domain)

        return domains

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

    def findWavelength(self, wavelength: Optional[float], units: str = None) -> Optional[int]:
        if wavelength is None:
            return None
        if units is not None:
            wavelength = wavelength * Utils.wavelengthUnitsConversionFactor(units, 'nm')

        bandNos = list()
        distances = list()
        for bandNo in range(1, self.bandCount() + 1):
            wavelength_ = self.wavelength(bandNo)
            if wavelength_ is None:
                continue
            bandNos.append(bandNo)
            distances.append(abs(wavelength_ - wavelength))
        if len(bandNos) == 0:
            return None

        return bandNos[np.argmin(distances)]

    def findTime(self, centerTime: Optional[QDateTime]) -> Optional[int]:
        if centerTime is None:
            return None

        bandNos = list()
        distances = list()
        for bandNo in range(1, self.bandCount() + 1):
            centerTime_ = self.centerTime(bandNo)
            if centerTime_ is None:
                continue
            bandNos.append(bandNo)
            distances.append(abs(centerTime_.msecsTo(centerTime)))
        if len(bandNos) == 0:
            return None

        return bandNos[np.argmin(distances)]

    def wavelengthUnits(self, bandNo: int) -> Optional[str]:
        """Return wavelength units."""

        # check band-level domains
        for domain in ['', 'ENVI']:
            units = self.metadataItem('wavelength_units', domain, bandNo)
            if units is not None:
                return Utils.wavelengthUnitsLongName(units)

        # check dataset-level domains
        for domain in ['', 'ENVI']:
            units = self.metadataItem('wavelength_units', domain)
            if units is not None:
                return Utils.wavelengthUnitsLongName(units)

        return None

    def wavelength(self, bandNo: int, units: str = None) -> Optional[float]:
        """Return band center wavelength in nanometers. Optionally, specify destination units."""

        if units is None:
            units = self.Nanometers

        wavelength_units = self.wavelengthUnits(bandNo)
        if wavelength_units is None:
            return None

        conversionFactor = Utils.wavelengthUnitsConversionFactor(wavelength_units, units)

        # check band-level domains
        for domain in ['', 'ENVI']:
            wavelength = self.metadataItem('wavelength', domain, bandNo)
            if wavelength is not None:
                return conversionFactor * float(wavelength)

        # check dataset-level domains
        for domain in ['', 'ENVI']:
            wavelengths = self.metadataItem('wavelength', domain)
            if wavelengths is not None:
                wavelength = wavelengths[bandNo - 1]
                return conversionFactor * float(wavelength)

        return None

    def setWavelength(self, wavelength: float, bandNo: int, units: str = None, fwhm: float = None):

        if units is None:
            units = self.Nanometers

        self.setMetadataItem('wavelength', float(wavelength), '', bandNo)
        self.setMetadataItem('wavelength_units', units, '', bandNo)

        if fwhm is not None:
            self.setMetadataItem('fwhm', float(fwhm), '', bandNo)

    def fwhm(self, bandNo: int, units: str = None) -> Optional[float]:
        """Return band FWHM in nanometers. Optionally, specify destination units."""

        if units is None:
            units = self.Nanometers

        wavelength_units = self.wavelengthUnits(bandNo)
        if wavelength_units is None:
            return None

        conversionFactor = Utils.wavelengthUnitsConversionFactor(wavelength_units, units)

        # check band-level domains
        for domain in ['', 'ENVI']:
            fwhm = self.metadataItem('fwhm', domain, bandNo)
            if fwhm is not None:
                return conversionFactor * float(fwhm)

        # check dataset-level domains
        for domain in ['', 'ENVI']:
            fwhm = self.metadataItem('fwhm', domain)
            if fwhm is not None:
                fwhm = fwhm[bandNo - 1]
                return conversionFactor * float(fwhm)

        return None

    def badBandMultiplier(self, bandNo: int) -> int:
        """Return bad band multiplier, 0 for bad band and 1 for good band."""

        # check band-level domains
        for domain in ['', 'ENVI']:
            badBandMultiplier = self.metadataItem('bad_band_multiplier', domain, bandNo)
            if badBandMultiplier is not None:
                return int(badBandMultiplier)

        # check dataset-level domains
        for domain in ['', 'ENVI']:
            bbl = self.metadataItem('bbl', domain)
            if bbl is not None:
                badBandMultiplier = bbl[bandNo - 1]
                return int(badBandMultiplier)

        return 1

    def setBadBandMultiplier(self, badBandMultiplier: int, bandNo: int):
        self.setMetadataItem('bad_band_multiplier', badBandMultiplier, '', bandNo)

    def startTime(self, bandNo: int = None) -> Optional[QDateTime]:
        """Return raster / band start time."""

        # check band-level domain
        if bandNo is not None:
            dateTime = self.metadataItem('start_time', '', bandNo)
            if dateTime == 'None':
                return None
            if dateTime is not None:
                return Utils.parseDateTime(dateTime)

        # check dataset-level default-domain
        dateTime = self.metadataItem('start_time')
        if dateTime is not None:
            return Utils.parseDateTime(dateTime)

        # check dataset-level IMAGERY-domain
        dateTime = self.metadataItem('ACQUISITIONDATETIME', 'IMAGERY')
        if dateTime is not None:
            return Utils.parseDateTime(dateTime)

        # check dataset-level ENVI-domain
        dateTime = self.metadataItem('acquisition_time', 'ENVI')
        if dateTime is not None:
            return Utils.parseDateTime(dateTime)

        return None

    def endTime(self, bandNo: int = None) -> Optional[QDateTime]:
        """Return raster / band end time."""

        # check band-level domain
        if bandNo is not None:
            dateTime = self.metadataItem('end_time', '', bandNo)
            if dateTime == 'None':
                return None
            if dateTime is not None:
                return Utils.parseDateTime(dateTime)

        # check dataset-level default-domain
        dateTime = self.metadataItem('end_time')
        if dateTime is not None:
            return Utils.parseDateTime(dateTime)

        return None

    def centerTime(self, bandNo: int = None) -> Optional[QDateTime]:
        """Return raster / band center time."""

        startTime = self.startTime(bandNo)
        if startTime is None:
            return None

        endTime = self.endTime(bandNo)
        if endTime is None:
            return startTime

        msecs = startTime.msecsTo(endTime)
        return startTime.addMSecs(int(msecs / 2))

    def setTime(self, startTime: Optional[QDateTime], endTime: QDateTime = None, bandNo: int = None):
        if startTime is None:
            self.layer.setCustomProperty(self.propertyKey('start_time', '', bandNo), 'None')
        else:
            self.setMetadataItem('start_time', startTime.toString('yyyy-MM-ddTHH:mm:ss'), '', bandNo)
        if endTime is None:
            self.layer.setCustomProperty(self.propertyKey('end_time', '', bandNo), 'None')
        else:
            self.setMetadataItem('end_time', endTime.toString('yyyy-MM-ddTHH:mm:ss'), '', bandNo)

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

    @staticmethod
    def flushQgisPam(layer: QgsRasterLayer):
        """Write  all custom layer properties to the GDAL source."""

        if layer.dataProvider().name() != 'gdal':
            return

        # collect all infos
        reader = RasterReader(layer)
        bandNumbers = list(reader.bandNumbers())
        datasetMetadata = reader.metadata()
        bandMetadata = [reader.metadata(bandNo) for bandNo in bandNumbers]
        userBandNames = [reader.userBandName(bandNo) for bandNo in bandNumbers]
        userBandOffsets = [reader.userBandOffset(bandNo) for bandNo in bandNumbers]
        userBandScales = [reader.userBandScale(bandNo) for bandNo in bandNumbers]
        bandOffsets = [reader.bandOffset(bandNo) for bandNo in bandNumbers]
        bandScales = [reader.bandScale(bandNo) for bandNo in bandNumbers]
        del reader

        # Flush all project layers that share the same source.
        # This shall prevent QGIS from overwriting our following external edits.
        # Fingers crossed!
        for alayer in QgsProject.instance().mapLayers().values():
            if alayer.source() == layer.source():
                Utils.setLayerDataSource(layer, 'GDAL', layer.source())

        # Set metadata via GDAL API. This is external to QGIS!
        from enmapboxprocessing.rasterwriter import RasterWriter
        ds = gdal.Open(layer.source())
        writer = RasterWriter(ds)
        writer.setMetadata(datasetMetadata)
        for i in range(layer.bandCount()):
            bandNo = i +1
            writer.setMetadata(bandMetadata[i], bandNo)
            if userBandNames[i] is not None:
                writer.setBandName(userBandNames[i], bandNo)
            if userBandOffsets[i] is not None or userBandScales[i] is not None:
                if userBandScales[i] is None:
                    userBandScale = 1.
                else:
                    userBandScale = userBandScales[i]
                if userBandOffsets[i] is None:
                    userBandOffset = 1.
                else:
                    userBandOffset = userBandOffsets[i]
                offset = bandOffsets[i] * userBandScale + userBandOffset
                writer.setOffset(offset, bandNo)
            if userBandScales[i] is not None:
                scale = bandScales[i] * userBandScales[i]
                writer.setScale(scale, bandNo)
        del writer, ds

        # Reload all project layers that share the same source.
        # QGIS should now be aware of the new band names, data offset/scale values and other metadata items.
        for alayer in QgsProject.instance().mapLayers().values():
            if alayer.source() == layer.source():
                Utils.setLayerDataSource(layer, 'GDAL', layer.source())
