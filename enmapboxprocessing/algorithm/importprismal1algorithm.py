from os.path import basename
from typing import Dict, Any, List, Tuple

import numpy as np
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsProcessingException)

from enmapboxprocessing.driver import Driver
from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from typeguard import typechecked


@typechecked
class ImportPrismaL1Algorithm(EnMAPProcessingAlgorithm):
    P_FILE, _FILE = 'file', 'File'
    P_OUTPUT_RASTER, _OUTPUT_RASTER = 'outputPrismaL1Raster', 'Output raster layer'

    def displayName(self):
        return 'Import PRISMA L1 product'

    def shortDescription(self):
        return 'Prepare a spectral raster layer from the given product. ' \
               'Wavelength and FWHM information is set.'

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

    def isValidFile(self, file: str) -> bool:
        return basename(file).startswith('PRS_L1') & \
               basename(file).endswith('.he5')

    def defaultParameters(self, xmlFilename: str):
        return {
            self.P_FILE: xmlFilename,
            self.P_OUTPUT_RASTER: xmlFilename.replace('.he5', '_SR.tif'),
        }

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        he5Filename = self.parameterAsFile(parameters, self.P_FILE, context)
        filename = self.parameterAsOutputLayer(parameters, self.P_OUTPUT_RASTER, context)

        with open(filename + '.log', 'w') as logfile:
            feedback, feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(feedback, parameters, context)

            # check filename
            # e.g. 'PRS_L1_STD_OFFL_20201107101404_20201107101408_0001.he5'
            if not self.isValidFile(he5Filename):
                message = f'not a valid PRISMA L1 product: {he5Filename}'
                feedback.reportError(message, True)
                raise QgsProcessingException(message)

            # read data and metadata (we aren't using GDAL, because it had problems reading the HE5 files)
            import h5py
            meta = dict()
            with h5py.File(he5Filename, 'r') as file:
                arrayVnir = file['/HDFEOS/SWATHS/PRS_L1_HCO/Data Fields/VNIR_Cube'][()]
                arraySwir = file['/HDFEOS/SWATHS/PRS_L1_HCO/Data Fields/SWIR_Cube'][()]
                meta = {key: file.attrs[key] for key in file.attrs.keys()}

            selectedVnir = meta['List_Cw_Vnir'] != 0
            selectedSwir = meta['List_Cw_Swir'] != 0

            # fix interleave, reverse band order and scale
            arrayVnir = np.transpose(arrayVnir, [1, 0, 2])[selectedVnir][::-1]
            arraySwir = np.transpose(arraySwir, [1, 0, 2])[selectedSwir][::-1]
            array = list(arrayVnir.astype(np.int16)) + list(arraySwir.astype(np.int16))

            # mask no data region
            noDataValue = -9999
            mask = np.all(np.equal(array, 0), axis=0)
            for a in array:
                a[mask] = noDataValue

            # write data
            driver = Driver(filename, 'GTiff')
            writer = driver.createFromArray(array)

            # set metadata
            wavelengthVnir = list(reversed([float(v)
                                            for v, flag in zip(meta['List_Cw_Vnir'], selectedVnir)
                                            if flag]))
            wavelengthSwir = list(reversed([float(v)
                                            for v, flag in zip(meta['List_Cw_Swir'], selectedSwir)
                                            if flag]))
            wavelength = wavelengthVnir + wavelengthSwir
            fwhmVnir = list(reversed([float(v)
                                      for v, flag in zip(meta['List_Fwhm_Vnir'], selectedVnir)
                                      if flag]))
            fwhmSwir = list(reversed([float(v)
                                      for v, flag in zip(meta['List_Fwhm_Swir'], selectedSwir)
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
