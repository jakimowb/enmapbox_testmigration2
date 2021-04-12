from typing import Dict, Any, List, Tuple

import numpy as np
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsProcessingException)

from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from enmapboxprocessing.typing import ClassifierDump
from enmapboxprocessing.utils import Utils
from typeguard import typechecked


@typechecked
class SelectFeatureSubsetFromSampleAlgorithm(EnMAPProcessingAlgorithm):
    P_SAMPLE, _SAMPLE = 'sample', 'Sample'
    P_FEATURE_LIST, _FEATURE_LIST = 'featureList', 'Selected features'
    P_OUTPUT_SAMPLE, _OUTPUT_SAMPLE = 'outputSample', 'Output sample'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self._SAMPLE, f'Sample (*.pkl) file.'),
            (self._FEATURE_LIST,
             'List of selected features given by name (e.g. ´Feature 1´) or position (integer >=1).'),
            (self._OUTPUT_SAMPLE, 'Output sample *.pkl file.')
        ]

    def displayName(self) -> str:
        return 'Select feature subset from classification sample'

    def shortDescription(self) -> str:
        return 'Select a feature subset from given sample.'

    def group(self):
        return Group.Test.value + Group.Classification.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterFile(self.P_SAMPLE, self._SAMPLE, extension='pkl')
        self.addParameterString(self.P_FEATURE_LIST, self._FEATURE_LIST)
        self.addParameterFileDestination(self.P_OUTPUT_SAMPLE, self._OUTPUT_SAMPLE, 'Output sample file (*.pkl)')

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        filenameSample = self.parameterAsFile(parameters, self.P_SAMPLE, context)
        values = self.parameterAsValues(parameters, self.P_FEATURE_LIST, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_SAMPLE, context)

        with open(filename + '.log', 'w') as logfile:
            feedback, feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(feedback, parameters, context)

            dump = ClassifierDump(**Utils.pickleLoad(filenameSample))
            feedback.pushInfo(
                f'Load sample data: X=array{list(dump.X.shape)} y=array{list(dump.y.shape)} categories={[c.name for c in dump.categories]}')

            indices = list()
            for value in values:
                if isinstance(value, str):
                    if not value in dump.features:
                        raise QgsProcessingException(f"Feature '{value}' not found in sample.")
                    value = dump.features.index(value) + 1
                if not isinstance(value, int):
                    raise QgsProcessingException(
                        f'Feature must be given by name (string) or position (integer): {value}, {type(value)}.'
                    )
                index = value - 1
                if not (0 <= index < len(dump.features)):
                    raise QgsProcessingException(
                        f'Feature position {value} out of valid range [1, {len(dump.features)}]'
                    )
                indices.append(index)

            dumpDict = dump._asdict()
            dumpDict['X'] = dump.X[:, indices]
            dumpDict['features'] = [dump.features[index] for index in indices]
            Utils.pickleDump(dumpDict, filename)

            result = {self.P_OUTPUT_SAMPLE: filename}
            self.toc(feedback, result)

        return result
