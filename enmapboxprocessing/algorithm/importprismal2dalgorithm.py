from os.path import basename
from typing import Dict, Any, List, Tuple

import numpy as np
from osgeo import gdal
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsProcessingException, QgsRectangle,
                        QgsCoordinateReferenceSystem)

from enmapboxprocessing.driver import Driver
from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from enmapboxprocessing.rasterwriter import RasterWriter
from typeguard import typechecked


@typechecked
class ImportPrismaL2DAlgorithm(EnMAPProcessingAlgorithm):
    P_FILE, _FILE = 'file', 'File'
    P_SPECTRAL_REGION, _SPECTRAL_REGION = 'spectralRegion', 'Spectral Region'
    O_SPECTRAL_REGION = ['VNIR/SWIR combined', 'VNIR only', 'SWIR only', ]
    VnirSwirRegion, VnirRegion, SwirRegion, = range(len(O_SPECTRAL_REGION))
    P_OUTPUT_SPECTRAL_CUBE, _OUTPUT_SPECTRAL_CUBE = 'outputPrismaL2D_spectralCube', 'Output VNIR/SWIR Cube raster layer'
    P_OUTPUT_PAN_CUBE, _OUTPUT_PAN_CUBE = 'outputPrismaL2D_panCube', 'Output PAN raster layer'

    P_OUTPUT_SPECTRAL_GEOLOCATION, _OUTPUT_SPECTRAL_GEOLOCATION = 'outputPrismaL2D_spectralGeolocationFields', \
                                                                  'Output VNIR/SWIR Geolocation Fields raster layer'
    P_OUTPUT_SPECTRAL_GEOMETRIC, _OUTPUT_SPECTRAL_GEOMETRIC = 'outputPrismaL2D_spectralGeometricFields', \
                                                              'Output VNIR/SWIR Geometric Fields raster layer'
    P_OUTPUT_SPECTRAL_ERROR, _OUTPUT_SPECTRAL_ERROR = 'outputPrismaL2D_spectralErrorMatrix', \
                                                      'Output VNIR/SWIR Error Matrix raster layer'
    P_OUTPUT_PAN_GEOLOCATION, _OUTPUT_PAN_GEOLOCATION = 'outputPrismaL2D_panGeolocationFields', \
                                                        'Output PAN Geolocation Fields raster layer'
    P_OUTPUT_PAN_ERROR, _OUTPUT_PAN_ERROR = 'outputPrismaL2D_panErrorMatrix', \
                                            'Output PAN Error Matrix raster layer'

    def displayName(self):
        return 'Import PRISMA L2D product'

    def shortDescription(self):
        link = EnMAPProcessingAlgorithm.htmlLink(
            'http://prisma.asi.it/missionselect/docs.php', 'PRISMA Documentation Area'
        )
        return 'Import PRISMA L2D product from HE5 file to QGIS/GDAL conform GTiff/VRT file format ' \
               'with proper coordinate reference system.' \
               'Note that for the spectral cube and error matrix, the interleave is transposed ' \
               'and stored as GTiff to enable proper visualization in QGIS.' \
               'All other sub-datasets are stored as light-weight VRT files.\n' \
               f'For further details visit the {link}.'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self._FILE, 'The HE5 product file.\n'
                         'Instead of executing this algorithm, '
                         'you may drag&drop the HE5 file directly from your system file browser onto '
                         'the EnMAP-Box map view area.'),
            (self._SPECTRAL_REGION, 'Spectral region to be imported.'),
            (self._OUTPUT_SPECTRAL_CUBE, 'VNIR/SWIR Cube GTiff raster file destination.'),
            (self._OUTPUT_PAN_CUBE, 'PAN VRT raster file destination.'),
            (self._OUTPUT_SPECTRAL_GEOLOCATION, 'VNIR/SWIR Geolocation Fields VRT raster file destination. '
                                                'Includes Latitude and Longitude bands.'),
            (self._OUTPUT_SPECTRAL_GEOMETRIC, 'VNIR/SWIR Geometric Fields VRT raster file destination. '
                                              'Includes Observing Angle, Relative Azimuth Angle and '
                                              'Solar Zenith Angle bands.'),
            (self._OUTPUT_SPECTRAL_ERROR, 'VNIR/SWIR Pixel Error Matrix GTiff raster file destination.'),
            (self._OUTPUT_PAN_GEOLOCATION, 'PAN Geolocation Fields VRT raster file destination. '
                                           'Includes Latitude and Longitude bands.'),
            (self._OUTPUT_PAN_ERROR, 'PAN Pixel Error Matrix VRT raster file destination.'),
        ]

    def group(self):
        return Group.Test.value + Group.ImportData.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterFile(self.P_FILE, self._FILE, extension='he5')
        self.addParameterEnum(self.P_SPECTRAL_REGION, self._SPECTRAL_REGION, self.O_SPECTRAL_REGION, False, 0)
        self.addParameterRasterDestination(self.P_OUTPUT_SPECTRAL_CUBE, self._OUTPUT_SPECTRAL_CUBE)
        self.addParameterVrtDestination(self.P_OUTPUT_PAN_CUBE, self._OUTPUT_PAN_CUBE)

        self.addParameterVrtDestination(
            self.P_OUTPUT_SPECTRAL_GEOLOCATION, self._OUTPUT_SPECTRAL_GEOLOCATION, None, True, False
        )
        self.addParameterVrtDestination(
            self.P_OUTPUT_SPECTRAL_GEOMETRIC, self._OUTPUT_SPECTRAL_GEOMETRIC, None, True, False
        )
        self.addParameterRasterDestination(
            self.P_OUTPUT_SPECTRAL_ERROR, self._OUTPUT_SPECTRAL_ERROR, None, True, False
        )

        self.addParameterVrtDestination(
            self.P_OUTPUT_PAN_GEOLOCATION, self._OUTPUT_PAN_GEOLOCATION, None, True, False
        )
        self.addParameterVrtDestination(
            self.P_OUTPUT_PAN_ERROR, self._OUTPUT_PAN_ERROR, None, True, False
        )

    def defaultParameters(self, file: str):
        return {
            self.P_FILE: file,
            self.P_OUTPUT_SPECTRAL_CUBE: file.replace('.he5', '_SPECTRAL.tif'),
            self.P_OUTPUT_PAN_CUBE: file.replace('.he5', '_PAN.vrt'),
            self.P_OUTPUT_SPECTRAL_GEOLOCATION: file.replace('.he5', '_SPECTRAL_GEOLOCATION.vrt'),
            self.P_OUTPUT_SPECTRAL_GEOMETRIC: file.replace('.he5', '_SPECTRAL_GEOMETRIC.vrt'),
            self.P_OUTPUT_SPECTRAL_ERROR: file.replace('.he5', '_SPECTRAL_ERROR.tif'),
            self.P_OUTPUT_PAN_GEOLOCATION: file.replace('.he5', '_PAN_GEOLOCATION.vrt'),
            self.P_OUTPUT_PAN_ERROR: file.replace('.he5', '_PAN_ERROR.vrt')
        }

    def isValidFile(self, file: str) -> bool:
        return basename(file).startswith('PRS_L2D') & \
               basename(file).endswith('.he5')

    def openDataset(self, he5Filename: str, key: str) -> gdal.Dataset:
        source = f'HDF5:"""{he5Filename}"""://{key}'
        ds: gdal.Dataset = gdal.Open(source)
        if ds is None:
            raise QgsProcessingException(f'unable to open PRISMA subdataset: {he5Filename}')
        return ds

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        he5Filename = self.parameterAsFile(parameters, self.P_FILE, context)
        spectralRegion = self.parameterAsEnum(parameters, self.P_SPECTRAL_REGION, context)
        filenameSpectralCube = self.parameterAsOutputLayer(parameters, self.P_OUTPUT_SPECTRAL_CUBE, context)
        filenameSpectralGeolocation = self.parameterAsOutputLayer(
            parameters, self.P_OUTPUT_SPECTRAL_GEOLOCATION, context
        )
        filenameSpectralGeometric = self.parameterAsOutputLayer(parameters, self.P_OUTPUT_SPECTRAL_GEOMETRIC, context)
        filenameSpectralError = self.parameterAsOutputLayer(parameters, self.P_OUTPUT_SPECTRAL_ERROR, context)

        filenamePanCube = self.parameterAsOutputLayer(parameters, self.P_OUTPUT_PAN_CUBE, context)
        filenamePanGeolocation = self.parameterAsOutputLayer(parameters, self.P_OUTPUT_PAN_GEOLOCATION, context)
        filenamePanError = self.parameterAsOutputLayer(parameters, self.P_OUTPUT_PAN_ERROR, context)

        with open(filenameSpectralCube + '.log', 'w') as logfile:
            feedback, feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(feedback, parameters, context)

            # check filename
            # e.g. 'PRS_L2D_STD_20201107101404_20201107101408_0001.he5'
            if not self.isValidFile(he5Filename):
                message = f'not a valid PRISMA L2D product: {he5Filename}'
                raise QgsProcessingException(message)

            self.writeSpectralCube(filenameSpectralCube, he5Filename, spectralRegion)
            self.writeSpectralGeolocationFields(filenameSpectralGeolocation, he5Filename)
            self.writeSpectralGeometricFields(filenameSpectralGeometric, he5Filename)
            self.writeSpectralErrorMatrix(filenameSpectralError, he5Filename, spectralRegion)

            self.writePanCube(filenamePanCube, he5Filename)
            self.writePanGeolocationFields(filenamePanGeolocation, he5Filename)
            self.writePanErrorMatrix(filenamePanError, he5Filename)

            result = {
                self.P_OUTPUT_SPECTRAL_CUBE: filenameSpectralCube,
                self.P_OUTPUT_SPECTRAL_GEOLOCATION: filenameSpectralGeolocation,
                self.P_OUTPUT_SPECTRAL_GEOMETRIC: filenameSpectralGeolocation,
                self.P_OUTPUT_SPECTRAL_ERROR: filenameSpectralError,
                self.P_OUTPUT_PAN_CUBE: filenamePanCube,
                self.P_OUTPUT_PAN_GEOLOCATION: filenamePanGeolocation,
                self.P_OUTPUT_PAN_ERROR: filenamePanError,
            }

            self.toc(feedback, result)

        return result

    def writeSpectralCube(self, filenameSpectralCube, he5Filename, spectralRegion):
        parseFloatList = lambda text: [float(item) for item in text.split()]
        array = list()
        metadata = dict()
        wavelength = list()
        fwhm = list()
        # - VNIR
        if spectralRegion in [self.VnirSwirRegion, self.VnirRegion]:
            dsVnir = self.openDataset(he5Filename, 'HDFEOS/SWATHS/PRS_L2D_HCO/Data_Fields/VNIR_Cube')
            arrayVnir = dsVnir.ReadAsArray()
            metadataVnir = dsVnir.GetMetadata('')
            selectedVnir = [v != 0 for v in parseFloatList(metadataVnir['List_Cw_Vnir'])]
            arrayVnir = np.transpose(arrayVnir, [1, 0, 2])[selectedVnir][::-1]
            wavelengthVnir = list(reversed(
                [float(v) for v, flag in zip(parseFloatList(metadataVnir['List_Cw_Vnir']), selectedVnir)
                 if flag]
            ))
            fwhmVnir = list(reversed(
                [float(v) for v, flag in zip(parseFloatList(metadataVnir['List_Fwhm_Vnir']), selectedVnir)
                 if flag]
            ))
            array.extend(arrayVnir)
            wavelength.extend(wavelengthVnir)
            fwhm.extend(fwhmVnir)
            metadata.update(metadataVnir)
        # - SWIR
        if spectralRegion in [self.VnirSwirRegion, self.SwirRegion]:
            dsSwir = self.openDataset(he5Filename, 'HDFEOS/SWATHS/PRS_L2D_HCO/Data_Fields/SWIR_Cube')
            arraySwir = dsSwir.ReadAsArray()
            metadataSwir = dsSwir.GetMetadata('')
            selectedSwir = [v != 0 for v in parseFloatList(metadataSwir['List_Cw_Swir'])]
            arraySwir = np.transpose(arraySwir, [1, 0, 2])[selectedSwir][::-1]
            wavelengthSwir = list(reversed(
                [float(v) for v, flag in zip(parseFloatList(metadataSwir['List_Cw_Swir']), selectedSwir)
                 if flag]
            ))
            fwhmSwir = list(reversed(
                [float(v) for v, flag in zip(parseFloatList(metadataSwir['List_Fwhm_Swir']), selectedSwir)
                 if flag]
            ))
            array.extend(arraySwir)
            wavelength.extend(wavelengthSwir)
            fwhm.extend(fwhmSwir)
            metadata.update(metadataSwir)
        # - mask no data region
        mask = np.all(np.equal(array, 0), axis=0)
        array = np.clip(array, 1, None)
        array[:, mask] = 0
        assert len(wavelength) == len(array)
        assert len(fwhm) == len(array)
        crs, extent, geoTransform = self.spatialInfo(metadata, 30)
        driver = Driver(filenameSpectralCube, 'GTiff', self.DefaultGTiffCreationOptions)
        writer = driver.createFromArray(array, extent, crs)
        writer.setNoDataValue(0)
        writer.setMetadataDomain(metadata)
        for bandNo in range(1, writer.bandCount() + 1):
            wl = wavelength[bandNo - 1]
            writer.setBandName(f'Band {bandNo} ({wl} Nanometers)', bandNo)
            writer.setWavelength(wl, bandNo)
            writer.setFwhm(fwhm[bandNo - 1], bandNo)
            writer.setScale(1. / 65535., bandNo)

    def writeSpectralErrorMatrix(self, filenameSpectralError, he5Filename, spectralRegion):
        if filenameSpectralError is None:
            return
        parseFloatList = lambda text: [float(item) for item in text.split()]
        array = list()
        metadata = dict()
        wavelength = list()
        # - VNIR
        if spectralRegion in [self.VnirSwirRegion, self.VnirRegion]:
            dsVnir = self.openDataset(he5Filename, 'HDFEOS/SWATHS/PRS_L2D_HCO/Data_Fields/VNIR_PIXEL_L2_ERR_MATRIX')
            arrayVnir = dsVnir.ReadAsArray()
            metadataVnir = dsVnir.GetMetadata('')
            selectedVnir = [v != 0 for v in parseFloatList(metadataVnir['List_Cw_Vnir'])]
            arrayVnir = np.transpose(arrayVnir, [1, 0, 2])[selectedVnir][::-1]
            wavelengthVnir = list(reversed(
                [float(v) for v, flag in zip(parseFloatList(metadataVnir['List_Cw_Vnir']), selectedVnir)
                 if flag]
            ))
            array.extend(arrayVnir)
            wavelength.extend(wavelengthVnir)
            metadata.update(metadataVnir)
        # - SWIR
        if spectralRegion in [self.VnirSwirRegion, self.SwirRegion]:
            dsSwir = self.openDataset(he5Filename, 'HDFEOS/SWATHS/PRS_L2D_HCO/Data_Fields/SWIR_PIXEL_L2_ERR_MATRIX')
            arraySwir = dsSwir.ReadAsArray()
            metadataSwir = dsSwir.GetMetadata('')
            selectedSwir = [v != 0 for v in parseFloatList(metadataSwir['List_Cw_Swir'])]
            arraySwir = np.transpose(arraySwir, [1, 0, 2])[selectedSwir][::-1]
            wavelengthSwir = list(reversed(
                [float(v) for v, flag in zip(parseFloatList(metadataSwir['List_Cw_Swir']), selectedSwir)
                 if flag]
            ))
            array.extend(arraySwir)
            wavelength.extend(wavelengthSwir)
            metadata.update(metadataSwir)
        # - mask no data region
        assert len(wavelength) == len(array)
        crs, extent, geoTransform = self.spatialInfo(metadata, 30)
        driver = Driver(filenameSpectralError, 'GTiff', self.DefaultGTiffCreationOptions)
        writer = driver.createFromArray(array, extent, crs)
        writer.setMetadataDomain(metadata)
        for bandNo in range(1, writer.bandCount() + 1):
            wl = wavelength[bandNo - 1]
            writer.setBandName(f'Pixel Error Band {bandNo} ({wl} Nanometers)', bandNo)
            writer.setWavelength(wl, bandNo)

    def writeSpectralGeolocationFields(self, filenameSpectralGeolocation, he5Filename):
        if filenameSpectralGeolocation is None:
            return
        ds1 = self.openDataset(he5Filename, 'HDFEOS/SWATHS/PRS_L2D_HCO/Geolocation_Fields/Longitude')
        ds2 = self.openDataset(he5Filename, 'HDFEOS/SWATHS/PRS_L2D_HCO/Geolocation_Fields/Latitude')
        metadata = ds1.GetMetadata('')
        crs, extent, geoTransform = self.spatialInfo(metadata, 30)
        ds: gdal.Dataset = gdal.BuildVRT(filenameSpectralGeolocation, [ds1, ds2], separate=True)
        ds.SetProjection(crs.toWkt())
        ds.SetGeoTransform(geoTransform)
        writer = RasterWriter(ds)
        writer.setMetadataDomain(metadata)
        writer.setBandName('Longitude', 1)
        writer.setBandName('Latitude', 2)

    def writeSpectralGeometricFields(self, filenameSpectralGeometric, he5Filename):
        if filenameSpectralGeometric is None:
            return
        ds1 = self.openDataset(he5Filename, 'HDFEOS/SWATHS/PRS_L2D_HCO/Geometric_Fields/Observing_Angle')
        ds2 = self.openDataset(he5Filename, 'HDFEOS/SWATHS/PRS_L2D_HCO/Geometric_Fields/Rel_Azimuth_Angle')
        ds3 = self.openDataset(he5Filename, 'HDFEOS/SWATHS/PRS_L2D_HCO/Geometric_Fields/Solar_Zenith_Angle')
        metadata = ds1.GetMetadata('')
        crs, extent, geoTransform = self.spatialInfo(metadata, 30)
        ds: gdal.Dataset = gdal.BuildVRT(filenameSpectralGeometric, [ds1, ds2, ds3], separate=True)
        ds.SetProjection(crs.toWkt())
        ds.SetGeoTransform(geoTransform)
        writer = RasterWriter(ds)
        writer.setMetadataDomain(metadata)
        writer.setNoDataValue(0)
        writer.setBandName('Observing Angle', 1)
        writer.setBandName('Relative Azimuth Angle', 2)
        writer.setBandName('Solar Zinith Angle', 3)

    def writePanCube(self, filenamePanCube, he5Filename):
        if filenamePanCube is None:
            return
        ds1 = self.openDataset(he5Filename, 'HDFEOS/SWATHS/PRS_L2D_PCO/Data_Fields/Cube')
        metadata = ds1.GetMetadata('')
        crs, extent, geoTransform = self.spatialInfo(metadata, 5)
        ds: gdal.Dataset = gdal.BuildVRT(filenamePanCube, [ds1], separate=True)
        ds.SetProjection(crs.toWkt())
        ds.SetGeoTransform(geoTransform)
        writer = RasterWriter(ds)
        writer.setMetadataDomain(metadata)
        writer.setNoDataValue(0)
        writer.setBandName('Panchromatic', 1)

    def writePanGeolocationFields(self, filenamePanGeolocation, he5Filename):
        if filenamePanGeolocation is None:
            return
        ds1 = self.openDataset(he5Filename, 'HDFEOS/SWATHS/PRS_L2D_PCO/Geolocation_Fields/Longitude')
        ds2 = self.openDataset(he5Filename, 'HDFEOS/SWATHS/PRS_L2D_PCO/Geolocation_Fields/Latitude')
        metadata = ds1.GetMetadata('')
        crs, extent, geoTransform = self.spatialInfo(metadata, 5)
        ds: gdal.Dataset = gdal.BuildVRT(filenamePanGeolocation, [ds1, ds2], separate=True)
        ds.SetProjection(crs.toWkt())
        ds.SetGeoTransform(geoTransform)
        writer = RasterWriter(ds)
        writer.setMetadataDomain(metadata)
        writer.setBandName('Longitude', 1)
        writer.setBandName('Latitude', 2)

    def writePanErrorMatrix(self, filenamePanError, he5Filename):
        if filenamePanError is None:
            return
        ds1 = self.openDataset(he5Filename, 'HDFEOS/SWATHS/PRS_L2D_PCO/Data_Fields/PIXEL_L2_ERR_MATRIX')
        metadata = ds1.GetMetadata('')
        crs, extent, geoTransform = self.spatialInfo(metadata, 5)
        ds: gdal.Dataset = gdal.BuildVRT(filenamePanError, [ds1], separate=True)
        ds.SetProjection(crs.toWkt())
        ds.SetGeoTransform(geoTransform)
        writer = RasterWriter(ds)
        writer.setMetadataDomain(metadata)
        writer.setBandName('PAN Band Pixel Error', 1)

    def spatialInfo(self, metadata, res):
        extent = QgsRectangle(
            float(metadata['Product_ULcorner_easting']) - res / 2,
            float(metadata['Product_LRcorner_northing']) - res / 2,
            float(metadata['Product_LRcorner_easting']) + res / 2,
            float(metadata['Product_ULcorner_northing']) + res / 2
        )
        crs = QgsCoordinateReferenceSystem.fromEpsgId(int(metadata['Epsg_Code']))
        geoTransform = (extent.xMinimum(), res, -0., extent.yMaximum(), -0., -res)
        return crs, extent, geoTransform
