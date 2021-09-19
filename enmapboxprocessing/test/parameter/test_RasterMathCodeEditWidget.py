from typing import Dict, Any

from qgis._core import QgsProcessingParameterString, QgsProcessingFeedback, QgsProcessingContext

from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from enmapboxprocessing.algorithm.rastermathalgorithm.parameter.processingparameterrastermathcodeeditwidget import \
    ProcessingParameterRasterMathCodeEditWidgetWrapper
from typeguard import typechecked


@typechecked
class TestRasterMathCodeEditWidgetAlgorithm(EnMAPProcessingAlgorithm):
    P_CODE, _CODE = 'code', 'Code'

    @classmethod
    def displayName(cls) -> str:
        return 'RasterMathCodeEditWidget'

    def shortDescription(self) -> str:
        return 'RasterMathCodeEditWidget'

    def group(self):
        return Group.Test.value + Group.Experimental.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        options_param = QgsProcessingParameterString(self.P_CODE, 'Code')
        options_param.setMetadata({'widget_wrapper': {'class': ProcessingParameterRasterMathCodeEditWidgetWrapper}})
        self.addParameter(options_param)

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        color = self.parameterAsString(parameters, self.P_CODE, context)
        print(color)
        return {}
