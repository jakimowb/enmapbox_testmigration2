import inspect
import traceback
from typing import Dict, Any, List, Tuple

from qgis._core import (QgsProcessingContext, QgsProcessingFeedback)

from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from enmapboxprocessing.typing import ClassifierDump
from enmapboxprocessing.utils import Utils
from typeguard import typechecked


@typechecked
class FitClassifierAlgorithmBase(EnMAPProcessingAlgorithm):
    P_DATEST, _DATASET = 'dataset', 'Training dataset'
    P_CLASSIFIER, _CLASSIFIER = 'classifier', 'Classifier'
    P_OUTPUT_CLASSIFIER, _OUTPUT_CLASSIFIER = 'outputClassifier', 'Output classifier'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self._DATASET, f'Training dataset pickle file used for fitting the classifier. '
                            f'If not specified, an unfitted classifier is created.'),
            (self._CLASSIFIER, self.helpParameterCode()),
            (self._OUTPUT_CLASSIFIER, self.PickleFileDestination)
        ]

    def displayName(self) -> str:
        raise NotImplementedError()

    def shortDescription(self) -> str:
        raise NotImplementedError()

    def code(self):
        raise NotImplementedError()

    def helpParameterCode(self) -> str:
        raise NotImplementedError()

    def group(self):
        return Group.Test.value + Group.Classification.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterFile(self.P_DATEST, self._DATASET, extension=self.PickleFileExtension, optional=True)
        self.addParameterString(self.P_CLASSIFIER, self._CLASSIFIER, self.defaultCodeAsString(), True)
        self.addParameterFileDestination(self.P_OUTPUT_CLASSIFIER, self._OUTPUT_CLASSIFIER, self.PickleFileFilter)

    def defaultCodeAsString(self):
        lines = [line for line in inspect.getsource(self.code).split('\n')
                 if not line.strip().startswith('def') and line != ''][:-1]
        lines = '\n'.join([line[8:] for line in lines])
        return lines

    def parameterAsClassifier(self, parameters: Dict[str, Any], name, context: QgsProcessingContext):
        namespace = dict()
        code = self.parameterAsString(parameters, name, context)
        exec(code, namespace)
        return namespace['classifier']

    def checkParameterValues(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        valid, message = super().checkParameterValues(parameters, context)
        if not valid:
            return valid, message
        # check code
        try:
            self.parameterAsClassifier(parameters, self.P_CODE, context)
        except:
            return False, traceback.format_exc()
        return True, ''

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        filenameDataset = self.parameterAsFile(parameters, self.P_DATEST, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_CLASSIFIER, context)
        classifier = self.parameterAsClassifier(parameters, self.P_CLASSIFIER, context)

        with open(filename + '.log', 'w') as logfile:
            feedback, feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(feedback, parameters, context)

            if filenameDataset is not None:
                dump = ClassifierDump(**Utils.pickleLoad(filenameDataset))
                feedback.pushInfo(f'Load training dataset: X=array{list(dump.X.shape)} y=array{list(dump.y.shape)} categories={[c.name for c in dump.categories]}')
                feedback.pushInfo('Fit classifier')
                classifier.fit(dump.X, dump.y.ravel())
            else:
                feedback.pushInfo('Store unfitted classifier')
                dump = ClassifierDump(None, None, None, None, classifier)

            dump = dump.withClassifier(classifier=classifier)
            Utils.pickleDump(dump._asdict(), filename)

            result = {self.P_OUTPUT_CLASSIFIER: filename}
            self.toc(feedback, result)

        return result
