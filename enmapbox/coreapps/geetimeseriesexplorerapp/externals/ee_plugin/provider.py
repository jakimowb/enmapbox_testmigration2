# -*- coding: utf-8 -*-
"""
Create and init the Earth Engine Qgis data provider
"""
from math import nan
from typing import List, Dict, Optional

import numpy as np
import json
from logging import warn

from qgis._core import QgsRectangle
from qgis.core import (
    QgsRasterDataProvider, QgsRasterIdentifyResult, QgsProviderRegistry,
    QgsProviderMetadata, QgsMessageLog, Qgis, QgsRaster, QgsRasterInterface,
    QgsVectorDataProvider, QgsDataProvider
)

from enmapboxprocessing.utils import Utils
from typeguard import typechecked

BAND_TYPES = {
    'int8': Qgis.Int16,
    'int16': Qgis.Int16,
    'int32': Qgis.Int32,
    'int64': Qgis.Int32,
    'uint8': Qgis.UInt16,
    'uint16': Qgis.UInt16,
    'uint32': Qgis.UInt32,
    'byte': Qgis.Byte,
    'short': Qgis.Int16,
    'int': Qgis.Int16,
    'long': Qgis.Int32,
    'float': Qgis.Float32,
    'double': Qgis.Float64
}

@typechecked
class EarthEngineRasterDataProvider(QgsRasterDataProvider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # create WMS provider
        self.wms = QgsProviderRegistry.instance().createProvider('wms', *args, **kwargs)
        self.ee_object = None

        self._singlePixelCache = dict()  # cache for reading single pixel profiles via block()

        from geetimeseriesexplorerapp.geetimeseriesexplorerdockwidget import CollectionJson, CollectionInfo
        self.collectionJson: Optional[CollectionJson] = None
        self.collectionInfo: Optional[CollectionInfo] = None

    @classmethod
    def description(cls):
        return 'Google Earth Engine Raster Data Provider'

    @classmethod
    def providerKey(cls):
        return 'EE'

    @classmethod
    def createProvider(cls, uri, providerOptions, flags=None):
        # compatibility with Qgis < 3.16, ReadFlags only available since 3.16
        if Qgis.QGIS_VERSION_INT >= 31600:
            flags = QgsDataProvider.ReadFlags()
            return EarthEngineRasterDataProvider(uri, providerOptions, flags)
        else:
            return EarthEngineRasterDataProvider(uri, providerOptions)

    def set_ee_object(self, ee_object):
        self.ee_object = ee_object
        self.ee_info = ee_object.getInfo()

    def setInformation(self, collectionJson, collectionInfo):
        from geetimeseriesexplorerapp.geetimeseriesexplorerdockwidget import CollectionJson, CollectionInfo
        assert isinstance(collectionJson, CollectionJson)
        assert isinstance(collectionInfo, CollectionInfo)
        self.collectionJson = collectionJson
        self.collectionInfo = collectionInfo

    def wavelength(self, bandNo: int) -> float:
        """Return band wavelength in nanometers. For non-spectral bands, nan is returned."""
        if self.collectionJson is None:
            return nan
        return self.collectionJson.bandWavelength(bandNo)

    def capabilities(self):
        caps = QgsRasterInterface.Size | QgsRasterInterface.Identify | QgsRasterInterface.IdentifyValue
        return QgsRasterDataProvider.ProviderCapabilities(caps)

    def name(self):
        return self.wms.name()

    def isValid(self):
        return self.wms.isValid()

    def extent(self) -> QgsRectangle:
        return self.wms.extent()

    def crs(self):
        return self.wms.crs()

    def clone(self):
        return self.wms.clone()

    def setDataSourceUri(self, uri):
        return self.wms.setDataSourceUri(uri)

    def reloadData(self):
        return self.wms.reloadData()

    def htmlMetadata(self):
        return json.dumps(self.ee_object.getInfo())

    def bandCount(self):

        try:
            if self.ee_object:
                bandCount = len(self.ee_info['bands'])
            else:
                bandCount = 1  # fall back to default if ee_object is not set
        except:
            bandCount = 1

        return bandCount


    def dataType(self, band_no):
        if not self.ee_object:
            return self.wms.dataType(band_no)

        return self.sourceDataType(band_no)

    def generateBandName(self, band_no):
        try:
            return self.ee_info['bands'][band_no - 1]['id']
        except:
            return ''

    def sourceDataType(self, band_no):
        try:
            return BAND_TYPES[self.ee_info['bands'][band_no - 1]['data_type']['precision']]
        except:
            return Qgis.UnknownDataType

    def identify(self, point, format, boundingBox=None, width=None, height=None, dpi=None) -> QgsRasterIdentifyResult:
        import ee
        from geetimeseriesexplorerapp.externals.ee_plugin import utils

        point = utils.geom_to_geo(point)
        point_ee = ee.Geometry.Point([point.x(), point.y()])

        scale = 1
        values = self.ee_object.reduceRegion(ee.Reducer.first(), point_ee, scale).getInfo()

        band_indices = range(1, self.bandCount() + 1)
        band_names = [self.generateBandName(band_no) for band_no in band_indices]
        band_values = [values[band_name] for band_name in band_names]

        results = dict(zip(band_indices, band_values))
        identifyResult = QgsRasterIdentifyResult(QgsRaster.IdentifyFormatValue, results)

        print('IDENTIFY', values, results)

        return identifyResult

    def block(self, bandNo, boundingBox, width, height, feedback=None):
        import ee
        from geetimeseriesexplorerapp.externals.ee_plugin import utils

        if width == 1 and height == 1:

            key = str(boundingBox), width, height
            results = self._singlePixelCache.get(key)
            if results is None:
                results = {key: value if value is not None else nan
                           for key, value in self.identify(boundingBox.center(), None).results().items()}

                self._singlePixelCache[key] = results
            array = np.array([[results[bandNo]]])

        else:
            boundingBox: QgsRectangle = utils.geom_to_geo(boundingBox)
            eeRectangle = ee.Geometry.Rectangle(
                [boundingBox.xMinimum(), boundingBox.yMinimum(), boundingBox.xMaximum(), boundingBox.yMaximum()]
            )

            eeImage = self.ee_object
            eeImage = eeImage.select(bandNo - 1)
            eeImage = eeImage.clipToBoundsAndScale(eeRectangle, width, height)  # down-scale image
            properties = []
            defaultValue = 0
            sample = eeImage.sampleRectangle(eeRectangle, properties, defaultValue).getInfo()
            array = np.array(list(sample['properties'].values()))[0]

            # we may have to deal with one pixel extra in each direction
            array = array[:height, :width]

        # scale to reflectance
        offset = self.collectionJson.bandOffset(bandNo)
        scale = self.collectionJson.bandScale(bandNo)
        if scale is not None:
            array = array * scale
        if offset is not None:
            array = array + offset

        assert array.shape == (height, width)
        dataType = None
        block = Utils.numpyArrayToQgsRasterBlock(array, dataType)

        array2 = Utils.qgsRasterBlockToNumpyArray(block)
        #assert np.all(array==array2)
        return block

    def xSize(self):
        try:
            return int(
                (self.extent().xMaximum() - self.extent().xMinimum()) / self.collectionJson.groundSamplingDistance()
            )
        except:
            return 0

    def ySize(self):
        try:
            return int(
                (self.extent().yMaximum() - self.extent().yMinimum()) / self.collectionJson.groundSamplingDistance()
            )
        except:
            return 0

class EarthEngineVectorDataProvider(QgsVectorDataProvider):
    # TODO
    pass


class EarthEngineRasterCollectionDataProvider(QgsRasterDataProvider):
    # TODO
    pass


class EarthEngineVectorCollectionDataProvider(QgsVectorDataProvider):
    # TODO
    pass


def register_data_provider():
    metadata = QgsProviderMetadata(
        EarthEngineRasterDataProvider.providerKey(),
        EarthEngineRasterDataProvider.description(),
        EarthEngineRasterDataProvider.createProvider)
    registry = QgsProviderRegistry.instance()
    registry.registerProvider(metadata)
    QgsMessageLog.logMessage('EE provider registered')
