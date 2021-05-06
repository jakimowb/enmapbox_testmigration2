from typing import Dict, Any, List, Tuple

import numpy as np
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsProcessingException)

from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from enmapboxprocessing.typing import ClassifierDump
from enmapboxprocessing.utils import Utils
from typeguard import typechecked


@typechecked
class RandomSamplesFromClassificationDatasetAlgorithm(EnMAPProcessingAlgorithm):
    P_DATASET, _DATASET = 'dataset', 'Classification dataset'
    P_N, _N = 'n', 'Number of samples per category'
    P_REPLACE, _REPLACE = 'replace', 'Draw with replacement'
    P_PROPORTIONAL, _PROPORTIONAL = 'proportional', 'Draw proportional'
    P_SEED, _SEED = 'seed', 'Random seed'
    P_OUTPUT_DATASET, _OUTPUT_DATASET = 'outputDatasetRandomSample', 'Output dataset'
    P_OUTPUT_COMPLEMENT, _OUTPUT_COMPLEMENT = 'outputDatasetRandomSampleComplement', 'Output dataset complement'

    def displayName(self) -> str:
        return 'Random samples from classification dataset'

    def shortDescription(self) -> str:
        return 'Split a dataset by randomly drawing samples.'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self._DATASET, f'Classification dataset pickle file with feature data X and target data y to draw from.'),
            (self._N,
             'Number of samples to draw from each category. '
             'Set a single value N to draw N points for each category. '
             'Set a list of values N1, N2, ... Ni, ... to draw Ni points for category i.'),
            (self._REPLACE, 'Whether to draw samples with replacement.'),
            (self._PROPORTIONAL,
             'Whether to interprete number of samples N or Ni as percentage to be drawn from each category.'),
            (self._SEED, 'The seed for the random generator can be provided.'),
            (self._OUTPUT_DATASET, self.PickleFileDestination + 'Stores sampled data.'),
            (self._OUTPUT_COMPLEMENT, self.PickleFileDestination + 'Stores remaining data that was not sampled.')
        ]

    def group(self):
        return Group.Test.value + Group.DatasetCreation.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterFile(self.P_DATASET, self._DATASET, extension=self.PickleFileExtension)
        self.addParameterString(self.P_N, self._N)
        self.addParameterBoolean(self.P_REPLACE, self._REPLACE, False, advanced=True)
        self.addParameterBoolean(self.P_PROPORTIONAL, self._PROPORTIONAL, False, advanced=True)
        self.addParameterInt(self.P_SEED, self._SEED, None, True, 1, advanced=True)
        self.addParameterFileDestination(self.P_OUTPUT_DATASET, self._OUTPUT_DATASET, self.PickleFileFilter)
        self.addParameterFileDestination(self.P_OUTPUT_COMPLEMENT, self._OUTPUT_COMPLEMENT, self.PickleFileFilter)

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        filenameSample = self.parameterAsFile(parameters, self.P_DATASET, context)
        N = self.parameterAsValues(parameters, self.P_N, context)
        replace = self.parameterAsBoolean(parameters, self.P_REPLACE, context)
        proportional = self.parameterAsBoolean(parameters, self.P_PROPORTIONAL, context)
        seed = self.parameterAsInt(parameters, self.P_SEED, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_DATASET, context)
        filename2 = self.parameterAsFileOutput(parameters, self.P_OUTPUT_COMPLEMENT, context)

        with open(filename + '.log', 'w') as logfile:
            feedback, feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(feedback, parameters, context)

            dump = ClassifierDump(**Utils.pickleLoad(filenameSample))
            feedback.pushInfo(
                f'Load dataset: X=array{list(dump.X.shape)} y=array{list(dump.y.shape)} categories={[c.name for c in dump.categories]}')

            # draw samples
            if seed is not None:
                np.random.seed(seed)

            indices = list()
            if len(N) == 1:
                N = N * len(dump.categories)
            if len(N) != len(dump.categories):
                raise QgsProcessingException(
                    f'Number of sample sizes ({len(N)}) not matching number of categories ({len(dump.categories)}).')
            for c, Ni in zip(dump.categories, N):
                valid = np.where(dump.y == c.value)[0]
                n = len(valid)
                if proportional:
                    Ni = int(round(n * Ni / 100))  # derive absolute Ni
                if not replace:
                    Ni = min(n, Ni)
                feedback.pushInfo(f'Draw {Ni} of {n} samples [{c.name}]')
                if Ni == 0:
                    break
                drawn = np.random.choice(valid, Ni, replace=replace)
                indices.extend(drawn)

            # store sample
            dump2 = dump.withSample(dump.X[indices], dump.y[indices]).withClassifier(None)
            Utils.pickleDump(dump2._asdict(), filename)

            # store conmplement
            indices2 = np.full((dump.X.shape[0],), True, bool)
            indices2[indices] = False
            dump2 = dump.withSample(dump.X[indices2], dump.y[indices2]).withClassifier(None)
            Utils.pickleDump(dump2._asdict(), filename2)

            result = {self.P_OUTPUT_DATASET: filename, self.P_OUTPUT_COMPLEMENT: filename2}
            self.toc(feedback, result)

        return result
