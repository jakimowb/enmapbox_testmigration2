from random import randint
from typing import Dict, Any, List, Tuple

import numpy as np
from PyQt5.QtGui import QColor
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsFeature, QgsProcessingParameterField)

from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from enmapboxprocessing.typing import checkSampleShape, ClassifierDump, Category
from enmapboxprocessing.utils import Utils
from typeguard import typechecked


@typechecked
class PrepareClassificationSampleFromTable(EnMAPProcessingAlgorithm):
    P_TABLE, _TABLE = 'table', 'Vector table'
    P_FEATURES, _FEATURES = 'features', 'Fields with features'
    P_LABELS, _LABELS = 'labels', 'Field with class label'
    P_NAMES, _NAMES = 'names', 'Field with class name'
    P_COLORS, _COLORS = 'colors', 'Field with class color'
    P_OUTPUT_SAMPLE, _OUTPUT_SAMPLE = 'outputSample', 'Output classification sample'

    @classmethod
    def displayName(cls) -> str:
        return 'Prepare classification sample (from vector table)'

    def shortDescription(self) -> str:
        return 'Store sample as a binary Pickle (*.pkl) file.'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self._TABLE, self.helpParameterVector()),
            (self._FEATURES, 'Fields used as features.'),
            (self._LABELS, 'Field used as class label.'),
            (self._NAMES, 'Field used as class name.'),
            (self._COLORS, 'Field used as class color.'),
            (self._OUTPUT_SAMPLE, 'Output sample destination *.pkl file.')
        ]

    def group(self):
        return Group.Test.value + Group.Classification.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterVectorLayer(self.P_TABLE, self._TABLE)
        self.addParameterField(
            self.P_FEATURES, self._FEATURES, None, self.P_TABLE, QgsProcessingParameterField.Any, True
        )
        self.addParameterField(self.P_LABELS, self._LABELS, None, self.P_TABLE, QgsProcessingParameterField.String)
        self.addParameterField(
            self.P_NAMES, self._NAMES, None, self.P_TABLE, QgsProcessingParameterField.String, False, True
        )
        self.addParameterField(
            self.P_COLORS, self._COLORS, None, self.P_TABLE, QgsProcessingParameterField.String, False, True
        )
        self.addParameterFileDestination(self.P_OUTPUT_SAMPLE, self._OUTPUT_SAMPLE, 'Pickle (*.pkl)')

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        table = self.parameterAsLayer(parameters, self.P_TABLE, context)
        featureFields = self.parameterAsFields(parameters, self.P_FEATURES, context)
        classField = self.parameterAsField(parameters, self.P_LABELS, context)
        nameField = self.parameterAsField(parameters, self.P_NAMES, context)
        colorField = self.parameterAsField(parameters, self.P_COLORS, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_SAMPLE, context)

        with open(filename + '.log', 'w') as logfile:
            feedback, feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(feedback, parameters, context)

            feedback.pushInfo('Read data')

            # prepare categories
            labels = list()
            categories = list()
            n = table.featureCount()
            feature: QgsFeature
            for i, feature in enumerate(table.getFeatures()):
                feedback.setProgress(i / n * 100)
                label = feature.attribute(classField)
                if not label in labels:  # prepare category only for new label
                    labels.append(label)
                    if nameField is not None:
                        name = feature.attribute(nameField)
                    else:
                        name = str(label)
                    if colorField is not None:
                        color = feature.attribute(colorField).strip()
                        if QColor.isValidColor(color):
                            color = QColor(color)
                        else:
                            rgb = eval(color)
                            if len(rgb) == 3 and all([isinstance(v, int) for v in rgb]):
                                color = QColor(*rgb)
                            else:
                                color = QColor('black')  # set invalid colors to black
                    else:
                        color = QColor(randint(0, 2 ** 24 - 1))  # set missing colors to random color
                    categories.append(Category(label, name, color.name()))
            classIdByValue = {value: i + 1 for i, (value, label, color) in enumerate(categories) if label != ''}

            # prepare data
            n = table.featureCount()
            X = np.zeros(shape=(n, len(featureFields)), dtype=np.float32)
            y = np.zeros(shape=(n, 1), dtype=np.float32)
            feature: QgsFeature
            for i, feature in enumerate(table.getFeatures()):
                feedback.setProgress(i / n * 100)
                yi = classIdByValue.get(feature.attribute(classField), np.nan)
                y[i, 0] = yi
                for k, featureField in enumerate(featureFields):
                    Xik = feature.attribute(featureField)
                    if Xik is None:
                        Xik = np.nan
                    X[i, k] = Xik
            checkSampleShape(X, y)

            dump = ClassifierDump(categories=categories, features=featureFields, X=X, y=y)
            dumpDict = dump._asdict()
            Utils.pickleDump(dumpDict, filename)

            result = {self.P_OUTPUT_SAMPLE: filename}
            self.toc(feedback, result)
        return result
