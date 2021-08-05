from os.path import basename
from typing import Dict, Any, List, Tuple
from xml.etree import ElementTree

from osgeo import gdal
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsProcessingException)

from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group

from typeguard import typechecked


@typechecked
class ImportEnmapL1CAlgorithm(EnMAPProcessingAlgorithm):
    P_FILE, _FILE = 'file', 'Metadata file'
    P_OUTPUT_RASTER, _OUTPUT_RASTER = 'outputEnmapL1CRaster', 'Output raster layer'

    def displayName(self):
        return 'Import EnMAP L1C product'

    def shortDescription(self):
        return 'Prepare a spectral raster layer from the given product. ' \
               'Wavelength and FWHM information is set and data is scaled according to data gain/offset values.'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self._FILE, 'The metadata XML file associated with the product.'),
            (self._OUTPUT_RASTER, self.RasterFileDestination)
        ]

    def group(self):
        return Group.Test.value + Group.ImportData.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterFile(self.P_FILE, self._FILE, extension='xml')
        self.addParameterVrtDestination(self.P_OUTPUT_RASTER, self._OUTPUT_RASTER)

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        xmlFilename = self.parameterAsFile(parameters, self.P_FILE, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_RASTER, context)

        with open(filename + '.log', 'w') as logfile:
            feedback, feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(feedback, parameters, context)

            # check filename
            # e.g. 'ENMAP01-____L1C-DT000326721_20170626T102020Z_001_V000204_20200406T180016Z-METADATA.XML'
            if not (basename(xmlFilename).startswith('ENMAP') &
                    basename(xmlFilename).endswith('METADATA.XML') &
                    ('L1C' in basename(xmlFilename))):
                message = f'not a valid EnMAP L1C product: {xmlFilename}'
                feedback.reportError(message, True)
                raise QgsProcessingException(message)

            # read metadata
            root = ElementTree.parse(xmlFilename).getroot()
            wavelength = [item.text for item in
                          root.findall('specific/bandCharacterisation/bandID/wavelengthCenterOfBand')]
            fwhm = [item.text for item in root.findall('specific/bandCharacterisation/bandID/FWHMOfBand')]
            gains = [item.text for item in root.findall('specific/bandCharacterisation/bandID/GainOfBand')]
            offsets = [item.text for item in root.findall('specific/bandCharacterisation/bandID/OffsetOfBand')]

            # create VRTs
            ds = gdal.Open(xmlFilename.replace('-METADATA.XML', '-SPECTRAL_IMAGE.TIF'))
            options = gdal.TranslateOptions(format='VRT')
            ds: gdal.Dataset = gdal.Translate(destName=filename, srcDS=ds, options=options)
            ds.SetMetadataItem('wavelength', '{' + ', '.join(wavelength[:ds.RasterCount]) + '}', 'ENVI')
            ds.SetMetadataItem('wavelength_units', 'nanometers', 'ENVI')
            ds.SetMetadataItem('fwhm', '{' + ', '.join(fwhm[:ds.RasterCount]) + '}', 'ENVI')

            rasterBands = [ds.GetRasterBand(i + 1) for i in range(ds.RasterCount)]
            rasterBand: gdal.Band
            for i, rasterBand in enumerate(rasterBands):
                rasterBand.SetScale(float(gains[i]))
                rasterBand.SetOffset(float(offsets[i]))
                rasterBand.FlushCache()

            result = {self.P_OUTPUT_RASTER: filename}
            self.toc(feedback, result)

        return result
