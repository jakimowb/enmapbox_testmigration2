from typing import Dict, Any, List, Tuple

from qgis._core import QgsProcessingContext, QgsProcessingFeedback, Qgis

from enmapboxprocessing.driver import Driver
from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from typeguard import typechecked


@typechecked
class CreateGridAlgorithm(EnMAPProcessingAlgorithm):
    P_CRS, _CRS = 'crs', 'CRS'
    P_EXTENT, _EXTENT = 'extent', 'Extent'
    P_UNIT, _UNIT = 'unit', 'Size units'
    O_UNIT = ['Pixels', 'Georeferenced units']
    PixelUnits, GeoreferencedUnits = range(2)
    P_WIDTH, _WIDTH = 'width', 'Width / horizontal resolution'
    P_HEIGHT, _HEIGHT = 'hight', 'Height / vertical resolution'
    P_OUTPUT_RASTER, _OUTPUT_RASTER = 'outRaster', 'Output VRT raster'

    def displayName(self):
        return 'Create Grid'

    def shortDescription(self):
        return 'Create an empty (VRT) raster that can be used as a pixel grid.'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self._CRS, 'Target coordinate reference system.'),
            (self._EXTENT, 'Target extent.'),
            (self._UNIT, 'Units to use when defining target raster size/resolution.'),
            (self._WIDTH, f'Target width if size units is {self.PixelUnits}, '
                          f'or horizontal resolution if size units is {self.GeoreferencedUnits}.'),
            (self._HEIGHT, f'Target height if size units is {self.PixelUnits}, '
                           f'or vertical resolution if size units is {self.GeoreferencedUnits}.'),
            (self._OUTPUT_RASTER, self.helpParameterRasterDestination())
        ]

    def group(self):
        return Group.Test.value + Group.CreateRaster.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterCrs(self.P_CRS, self._CRS)
        self.addParameterExtent(self.P_EXTENT, self._EXTENT)
        self.addParameterEnum(self.P_UNIT, self._UNIT, self.O_UNIT)
        self.addParameterFloat(self.P_WIDTH, self._WIDTH, 0, minValue=0)
        self.addParameterFloat(self.P_HEIGHT, self._HEIGHT, 0, minValue=0)
        self.addParameterRasterDestination(self.P_OUTPUT_RASTER, self._OUTPUT_RASTER)

    def checkParameterValues(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        unit = self.parameterAsEnum(parameters, self.P_UNIT, context)
        if unit == self.PixelUnits:
            if self.parameterAsInt(parameters, self.P_WIDTH, context) < 1:
                return False, 'Width must be greater than or equal to 1 pixel.'
            if self.parameterAsInt(parameters, self.P_HEIGHT, context) < 1:
                return False, 'Height must be greater than or equal to 1 pixel.'
        if unit == self.GeoreferencedUnits:
            if self.parameterAsDouble(parameters, self.P_WIDTH, context) == 0:
                return False, 'Horizontal resolution must be greater than 0.'
            if self.parameterAsDouble(parameters, self.P_HEIGHT, context) == 0:
                return False, 'Vertical resolution must be greater than 0.'
        return True, ''

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:

        crs = self.parameterAsCrs(parameters, self.P_CRS, context)
        extent = self.parameterAsExtent(parameters, self.P_EXTENT, context, crs=crs)
        unit = self.parameterAsEnum(parameters, self.P_UNIT, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_RASTER, context)
        if unit == self.PixelUnits:
            width = self.parameterAsInt(parameters, self.P_WIDTH, context)
            height = self.parameterAsInt(parameters, self.P_HEIGHT, context)
        elif unit == self.GeoreferencedUnits:
            xres = self.parameterAsDouble(parameters, self.P_WIDTH, context)
            width = int(round(extent.width() / xres, 0))
            yres = self.parameterAsDouble(parameters, self.P_HEIGHT, context)
            height = int(round(extent.height() / yres, 0))
        else:
            assert 0

        with open(filename + '.log', 'w') as logfile:
            feedback, feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(feedback, parameters, context)
            Driver(filename, self.VrtFormat, None, feedback).create(Qgis.Byte, width, height, 1, extent, crs)
            result = {self.P_OUTPUT_RASTER: filename}
            self.toc(feedback, result)

        return result
