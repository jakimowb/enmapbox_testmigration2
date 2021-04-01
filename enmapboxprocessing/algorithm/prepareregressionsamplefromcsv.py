from random import randint
from typing import Dict, Any, List, Tuple

import numpy as np
from PyQt5.QtGui import QColor
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsCategorizedSymbolRenderer,
                        QgsFeature, QgsProcessingParameterField)

from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from enmapboxprocessing.typing import checkSampleShape, Category, ClassifierDump, RegressionDump
from enmapboxprocessing.utils import Utils
from typeguard import typechecked


@typechecked
class PrepareRegressionSampleFromCsv(EnMAPProcessingAlgorithm):
    P_FEATURES, _FEATURES = 'features', 'Text file with features'
    P_LABELS, _LABELS = 'labels', 'Text file with labels'
    P_OUTPUT_SAMPLE, _OUTPUT_SAMPLE = 'outputSample', 'Output classification sample'

    @classmethod
    def displayName(cls) -> str:
        return 'Prepare regression sample (from text files)'

    def shortDescription(self) -> str:
        return f'Read sample from two text file with tabulated values and store it as a binary Pickle (*.pkl) file. ' \
               f'The format matches the output of the {self.htmlLink("https://force-eo.readthedocs.io/en/latest/components/higher-level/smp/index.html", "FORCE Higher Level Sampling Submodule")}.'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self._FEATURES, 'Text file with plain feature values (no headers). One row represents the feature vector of one sample.'),
            (self._LABELS, 'Text file with plain label values (no headers). One row represents the class label of one sample.'),
            (self._OUTPUT_SAMPLE, 'Output sample destination *.pkl file.')
        ]

    def group(self):
        return Group.Test.value + Group.Regression.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterFile(self.P_FEATURES, self._FEATURES)
        self.addParameterFile(self.P_LABELS, self._LABELS)
        self.addParameterFileDestination(self.P_OUTPUT_SAMPLE, self._OUTPUT_SAMPLE, 'Pickle (*.pkl)')

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        filenameFeatures = self.parameterAsFile(parameters, self.P_FEATURES, context)
        filenameLabels = self.parameterAsFile(parameters, self.P_LABELS, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_SAMPLE, context)

        with open(filename + '.log', 'w') as logfile:
            feedback, feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(feedback, parameters, context)

            # read data
            X = list()
            with open(filenameFeatures) as file:
                for line in file.readlines():
                    X.append(line.split())
            X = np.array(X, dtype=np.float32)
            features = [f'feature {i + 1}' for i in range(X.shape[1])]

            y = list()
            with open(filenameLabels) as file:
                for line in file.readlines():
                    y.append(line.split())
            y = np.array(y, dtype=np.float32)

            # prepare
            targets = ['target 1']

            dump = RegressionDump(targets=targets, features=features, X=X, y=y)
            Utils.pickleDump(dump._asdict(), filename)

            result = {self.P_OUTPUT_SAMPLE: filename}
            self.toc(feedback, result)
        return result
