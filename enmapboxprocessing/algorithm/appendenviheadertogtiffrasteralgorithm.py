from os.path import exists
from typing import Dict, Any, List, Tuple

from osgeo import gdal
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsProcessingException)

from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from enmapboxprocessing.rasterreader import RasterReader
from typeguard import typechecked


@typechecked
class AppendEnviHeaderToGTiffRasterAlgorithm(EnMAPProcessingAlgorithm):
    P_RASTER, _RASTER = 'raster', 'GeoTiff raster layer'

    def displayName(self):
        return 'Append ENVI header to GeoTiff raster layer'

    def shortDescription(self):
        return 'Places an ENVI *.hdr header file next to the GeoTiff raster layer, ' \
               'to enable full compatibility to the ENVI software. ' \
               'The header file stores wavelength, FWHM and bad band multiplier information.'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self._RASTER, 'Source GeoTiff raster layer.'),
        ]

    def group(self):
        return Group.Test.value + Group.RasterCreation.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterRasterLayer(self.P_RASTER, self._RASTER)

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        raster = self.parameterAsRasterLayer(parameters, self.P_RASTER, context)

        if not exists(raster.source()):
            raise QgsProcessingException(f'Raster layer source is not a valid filename: {raster.source()}')
        ds: gdal.Dataset = gdal.Open(raster.source())
        driver: gdal.Driver = ds.GetDriver()
        if not driver.ShortName == 'GTiff':
            raise QgsProcessingException('Raster layer is not a GeoTiff')
        reader = RasterReader(ds)

        text = 'ENVI\n' \
               'file type = TIFF\n' \
               f'samples = {reader.width()}\n' \
               f'lines = {reader.height()}\n' \
               f'bands = {reader.bandCount()}\n'

        if reader.isSpectralRasterLayer(quickCheck=True):
            wavelength = [str(reader.wavelength(bandNo)) for bandNo in range(1, reader.bandCount() + 1)]
            fwhm = [str(reader.fwhm(bandNo)) for bandNo in range(1, reader.bandCount() + 1)]
            bbl = [str(reader.badBandMultiplier(bandNo)) for bandNo in range(1, reader.bandCount() + 1)]
            text += 'wavelength units = Nanometer\n' \
                    'wavelength = {' + ', '.join(wavelength) + '}\n'
            if fwhm[0] != 'None':
                text += 'fwhm = {' + ', '.join(fwhm) + '}\n'
            if bbl[0] != 'None':
                text += 'bbl = {' + ', '.join(bbl) + '}\n'

        if ds.GetRasterBand(1).GetNoDataValue() is not None:
            text += f'data ignore value = {ds.GetRasterBand(1).GetNoDataValue()}\n'

        with open(raster.source() + '.hdr', 'w') as file:
            file.write(text)

        return {}
