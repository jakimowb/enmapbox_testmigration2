from typing import Dict, Any, List, Tuple

import numpy as np
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsCategorizedSymbolRenderer,
                        QgsFeature, QgsProcessingParameterField)

from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from enmapboxprocessing.typing import checkSampleShape, Category, ClassifierDump
from enmapboxprocessing.utils import Utils
from typeguard import typechecked


@typechecked
class PrepareClassificationSampleFromVectorAndFields(EnMAPProcessingAlgorithm):
    P_VECTOR, _VECTOR = 'vector', 'Categorized vector layer'
    P_FIELDS, _FIELDS = 'fields', 'Fields with features'
    P_OUTPUT_SAMPLE, _OUTPUT_SAMPLE = 'outputSample', 'Output classification sample'

    @classmethod
    def displayName(cls) -> str:
        return 'Prepare classification sample (from categorized vector)'

    def shortDescription(self) -> str:
        return 'Store sample as a binary Pickle (*.pkl) file.'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self._VECTOR, f'{self.helpParameterVectorClassification()} Categories are used as labels.'),
            (self._FIELDS, 'Fields used as features.'),
            (self._OUTPUT_SAMPLE, 'Output sample destination *.pkl file.')
        ]

    def group(self):
        return Group.Test.value + Group.Classification.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterVectorLayer(self.P_VECTOR, self._VECTOR)
        self.addParameterField(
            self.P_FIELDS, self._FIELDS, None, self.P_VECTOR, QgsProcessingParameterField.Any, True
        )
        self.addParameterFileDestination(self.P_OUTPUT_SAMPLE, self._OUTPUT_SAMPLE, 'Pickle (*.pkl)')

    def checkParameterValues(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        valid, message = self.checkParameterVectorClassification(parameters, self.P_VECTOR, context)
        if not valid:
            return valid, message
        return True, ''

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        vector = self.parameterAsLayer(parameters, self.P_VECTOR, context)
        fields = self.parameterAsFields(parameters, self.P_FIELDS, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_SAMPLE, context)

        with open(filename + '.log', 'w') as logfile:
            feedback, feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(feedback, parameters, context)

            feedback.pushInfo('Read data')
            # prepare categories
            renderer: QgsCategorizedSymbolRenderer = vector.renderer()
            categories = Utils.categoriesFromCategorizedSymbolRenderer(renderer)
            classIdByValue = {value: i + 1 for i, (value, label, color) in enumerate(categories) if label != ''}
            categories = [Category(classIdByValue[value], label, color)
                          for i, (value, label, color) in enumerate(categories) if label != '']
            classField = renderer.classAttribute()
            # prepare data
            n = vector.featureCount()
            X = np.zeros(shape=(n, len(fields)), dtype=np.float32)
            y = np.zeros(shape=(n, 1), dtype=np.float32)
            feature: QgsFeature
            for i, feature in enumerate(vector.getFeatures()):
                feedback.setProgress(i / n * 100)
                yi = classIdByValue.get(feature.attribute(classField), np.nan)
                y[i, 0] = yi
                for k, field in enumerate(fields):
                    Xik = feature.attribute(field)
                    if Xik is None:
                        Xik = np.nan
                    X[i, k] = Xik
            checkSampleShape(X, y)

            dump = ClassifierDump(categories=categories, features=fields, X=X, y=y)
            dumpDict = dump._asdict()
            Utils.pickleDump(dumpDict, filename)

            result = {self.P_OUTPUT_SAMPLE: filename}
            self.toc(feedback, result)
        return result
