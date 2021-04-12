from typing import Dict, Any, List, Tuple

from qgis._core import QgsProcessingContext, QgsProcessingFeedback

from enmapboxprocessing.algorithm.classificationperformancestratifiedalgorithm import \
    ClassificationPerformanceStratifiedAlgorithm
from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from typeguard import typechecked


@typechecked
class ClassificationPerformanceSimpleAlgorithm(EnMAPProcessingAlgorithm):
    P_CLASSIFICATION, _CLASSIFICATION = 'classification', 'Classification'
    P_REFERENCE, _REFERENCE = 'reference', 'Reference sample'
    P_OUTPUT_REPORT, _OUTPUT_REPORT = 'outReport', 'Output report'

    @classmethod
    def displayName(cls) -> str:
        return 'Classification performance (for simple random sampling)'

    def shortDescription(self) -> str:
        return 'Estimates map accuracy and area proportions for (simple) random sampling. ' \
               'We use the formulars for the stratified random sampling described in ' \
               'Stehman (2014): https://doi.org/10.1080/01431161.2014.930207. ' \
               'Note that (simple) random sampling is a special case of stratified random sampling, ' \
               'with exactly one stratum. ' \
               '\nReference and map classes are matched by name.'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self._CLASSIFICATION, self.helpParameterRasterClassification()),
            (self._REFERENCE, 'Random reference sample. '
                              f'{self.helpParameterMapClassification()} '),
            (self._OUTPUT_REPORT, self.helpParameterReportDestination())
        ]

    def group(self):
        return Group.Test.value + Group.AccuracyAssessment.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterRasterLayer(self.P_CLASSIFICATION, self._CLASSIFICATION)
        self.addParameterMapLayer(self.P_REFERENCE, self._REFERENCE)
        self.addParameterFileDestination(
            self.P_OUTPUT_REPORT, self._OUTPUT_REPORT, 'HTML file (*.html)'
        )

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        classification = self.parameterAsRasterLayer(parameters, self.P_CLASSIFICATION, context)
        reference = self.parameterAsLayer(parameters, self.P_REFERENCE, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_REPORT, context)

        with open(filename + '.log', 'w') as logfile:
            feedback, feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(feedback, parameters, context)

            alg = ClassificationPerformanceStratifiedAlgorithm()
            alg.initAlgorithm()
            parameters = {
                alg.P_CLASSIFICATION: classification,
                alg.P_REFERENCE: reference,
                alg.P_USE_MAP_STRATA: False,
                alg.P_OUTPUT_REPORT: filename,
            }
            result = self.runAlg(alg, parameters, None, feedback2, context, True)

            self.toc(feedback, result)

        return result
