from os.path import basename
from typing import Dict, Any, List, Tuple

import numpy as np
from osgeo import gdal
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsProcessingException, QgsRectangle,
                        QgsCoordinateReferenceSystem)

from enmapboxprocessing.driver import Driver
from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from typeguard import typechecked


@typechecked
class ImportPrismaL2DAlgorithm(EnMAPProcessingAlgorithm):
    P_FILE, _FILE = 'file', 'File'
    P_OUTPUT_RASTER, _OUTPUT_RASTER = 'outputPrismaL2DRaster', 'Output raster layer'

    def displayName(self):
        return 'Import PRISMA L2D product'

    def shortDescription(self):
        return 'Prepare a spectral raster layer from the given product. ' \
               'Wavelength and FWHM information is set and data is scaled into the 0 to 10000 range.'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self._FILE, 'The HE5 product file.\n'
                         'Instead of executing this algorithm, '
                         'you may drag&drop the HE5 file directly from your system file browser onto '
                         'the EnMAP-Box map view area.'),
            (self._OUTPUT_RASTER, self.RasterFileDestination)
        ]

    def group(self):
        return Group.Test.value + Group.ImportData.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterFile(self.P_FILE, self._FILE, extension='he5')
        self.addParameterRasterDestination(self.P_OUTPUT_RASTER, self._OUTPUT_RASTER)

    def  defaultParameters(self, file: str):
        return {
                    self.P_FILE: file,
                    self.P_OUTPUT_RASTER: file.replace('.he5', '_SR.tif'),
                }

    def isValidFile(self, file: str) -> bool:
        return basename(file).startswith('PRS_L2D') & \
               basename(file).endswith('.he5')

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        he5Filename = self.parameterAsFile(parameters, self.P_FILE, context)
        filename = self.parameterAsOutputLayer(parameters, self.P_OUTPUT_RASTER, context)

        with open(filename + '.log', 'w') as logfile:
            feedback, feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(feedback, parameters, context)

            # check filename
            # e.g. 'PRS_L2D_STD_20201107101404_20201107101408_0001.he5'
            if not self.isValidFile(he5Filename):
                message = f'not a valid PRISMA L2D product: {he5Filename}'
                feedback.reportError(message, True)
                raise QgsProcessingException(message)

            # read metadata
            ds: gdal.Dataset = gdal.Open(he5Filename)
            meta = ds.GetMetadata()
            offsetVnir = np.float32(meta['L2ScaleVnirMin'])
            gainVnir = np.float32((float(meta['L2ScaleVnirMax']) - float(meta['L2ScaleVnirMin'])) / 65535 * 10000)
            selectedVnir = np.array(meta['List_Cw_Vnir'].split()) != '0'
            offsetSwir = np.float32(meta['L2ScaleSwirMin'])
            gainSwir = np.float32((float(meta['L2ScaleSwirMax']) - float(meta['L2ScaleSwirMin'])) / 65535 * 10000)
            selectedSwir = np.array(meta['List_Cw_Swir'].split()) != '0'

            # read data, fix interleave, reverse band order and scale
            import h5py
            with h5py.File(he5Filename, 'r') as file:
                arrayVnir = file['/HDFEOS/SWATHS/PRS_L2D_HCO/Data Fields/VNIR_Cube'][()]
                arraySwir = file['/HDFEOS/SWATHS/PRS_L2D_HCO/Data Fields/SWIR_Cube'][()]
            arrayVnir = offsetVnir + np.transpose(arrayVnir, [1, 0, 2])[selectedVnir][::-1] * gainVnir
            arraySwir = offsetSwir + np.transpose(arraySwir, [1, 0, 2])[selectedSwir][::-1] * gainSwir
            array = list(arrayVnir.astype(np.int16)) + list(arraySwir.astype(np.int16))

            # mask no data region
            noDataValue = -9999
            mask = np.all(np.equal(array, 0), axis=0)
            for a in array:
                a[mask] = noDataValue

            # write data
            extent = QgsRectangle(
                float(meta['Product_ULcorner_easting']) - 15, float(meta['Product_LRcorner_northing']) - 15,
                float(meta['Product_ULcorner_northing']) + 15, float(meta['Product_LRcorner_easting']) + 15
            )
            extent = QgsRectangle(
                float(meta['Product_ULcorner_easting']) - 15, float(meta['Product_LRcorner_northing']) - 15,
                float(meta['Product_LRcorner_easting']) + 15, float(meta['Product_ULcorner_northing']) + 15
            )

            crs = QgsCoordinateReferenceSystem.fromEpsgId(int(meta['Epsg_Code']))
            driver = Driver(filename, 'GTiff')
            writer = driver.createFromArray(array, extent, crs)

            # set metadata
            wavelengthVnir = list(reversed([float(v)
                                            for v, flag in zip(meta['List_Cw_Vnir'].split(), selectedVnir)
                                            if flag]))
            wavelengthSwir = list(reversed([float(v)
                                            for v, flag in zip(meta['List_Cw_Swir'].split(), selectedSwir)
                                            if flag]))
            wavelength = wavelengthVnir + wavelengthSwir
            fwhmVnir = list(reversed([float(v)
                                      for v, flag in zip(meta['List_Fwhm_Vnir'].split(), selectedVnir)
                                      if flag]))
            fwhmSwir = list(reversed([float(v)
                                      for v, flag in zip(meta['List_Fwhm_Swir'].split(), selectedSwir)
                                      if flag]))
            fwhm = fwhmVnir + fwhmSwir

            assert len(wavelength) == len(array)
            assert len(fwhm) == len(array)
            for bandNo in range(1, writer.bandCount() + 1):
                wl = wavelength[bandNo - 1]
                writer.setBandName(f'band {bandNo} ({wl} Nanometers)', bandNo)
                writer.setWavelength(wl, bandNo)
                writer.setFwhm(fwhm[bandNo - 1], bandNo)
            writer.setNoDataValue(noDataValue)
            result = {self.P_OUTPUT_RASTER: filename}
            self.toc(feedback, result)

        return result
