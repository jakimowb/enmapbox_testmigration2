from typing import Dict, Any, List, Tuple

import numpy as np
from sklearn.model_selection import cross_val_predict
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsRasterLayer)

from enmapboxprocessing.algorithm.classificationperformancesimplealgorithm import \
    ClassificationPerformanceSimpleAlgorithm
from enmapboxprocessing.driver import Driver
from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from enmapboxprocessing.typing import ClassifierDump
from enmapboxprocessing.utils import Utils
from typeguard import typechecked


@typechecked
class ClassifierPerformanceAlgorithm(EnMAPProcessingAlgorithm):
    P_CLASSIFIER, _CLASSIFIER = 'classifier', 'Classifier'
    P_NFOLD, _NFOLD = 'nfold', 'Number of cross-validation folds'
    P_OUTPUT_REPORT, _OUTPUT_REPORT = 'outputReport', 'Output report'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self._CLASSIFIER, f'Classifier (*.pkl) file.'),
            (self._NFOLD, f'Evaluate n-fold cross-validation performance. '
                          f'Set n=1 to evaluate training data performance.'),
            (self._OUTPUT_REPORT, 'Output report *.html file.')
        ]

    def displayName(self) -> str:
        return 'Classifier performance'

    def shortDescription(self) -> str:
        return 'Evaluates classifier performance.'

    def group(self):
        return Group.Test.value + Group.Classification.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterFile(self.P_CLASSIFIER, self._CLASSIFIER, extension='pkl')
        self.addParameterInt(self.P_NFOLD, self._NFOLD, 3, False, 1, 100)
        self.addParameterFileDestination(self.P_OUTPUT_REPORT, self._OUTPUT_REPORT, 'Report file (*.html)')

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        filenameSample = self.parameterAsFile(parameters, self.P_CLASSIFIER, context)
        nfold = self.parameterAsInt(parameters, self.P_NFOLD, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_REPORT, context)

        with open(filename + '.log', 'w') as logfile:
            feedback, feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(feedback, parameters, context)

            dump = ClassifierDump(**Utils.pickleLoad(filenameSample))
            feedback.pushInfo(f'Load classifier: {dump.classifier}')
            feedback.pushInfo(f'Load sample data: X{list(dump.X.shape)} y{list(dump.y.shape)}')

            if nfold == 1:
                feedback.pushInfo('Evaluate training data performance')
                y2 = dump.classifier.predict(dump.X)
                y2 = np.reshape(y2, (1, -1, 1))
                # prepare raster layers
                reference = Driver(Utils.tmpFilename(filename, 'reference.tif')).createFromArray([dump.y])
                prediction = Driver(Utils.tmpFilename(filename, 'prediction.tif')).createFromArray(y2)
                reference.close()
                reference = QgsRasterLayer(reference.source())
                renderer = Utils.palettedRasterRendererFromCategories(reference.dataProvider(), 1, dump.categories)
                reference.setRenderer(renderer)
                reference.saveDefaultStyle()
                prediction.close()
                prediction = QgsRasterLayer(prediction.source())
                renderer = Utils.palettedRasterRendererFromCategories(prediction.dataProvider(), 1, dump.categories)
                prediction.setRenderer(renderer)
                prediction.saveDefaultStyle()
                # eval
                alg = ClassificationPerformanceSimpleAlgorithm()
                alg.initAlgorithm()
                parameters = {
                    alg.P_CLASSIFICATION: prediction,
                    alg.P_REFERENCE: reference,
                    alg.P_OUTPUT_REPORT: filename,
                }
                self.runAlg(alg, parameters, None, feedback2, context, True)
            else:
                feedback.pushInfo('Evaluate cross-validation performance')
                y2 = cross_val_predict(dump.classifier, X=dump.X, y=dump.y.ravel(), cv=nfold)
                y2 = np.reshape(y2, (1, -1, 1))
                # prepare raster layers
                reference = Driver(Utils.tmpFilename(filename, 'reference.tif')).createFromArray([dump.y])
                prediction = Driver(Utils.tmpFilename(filename, 'prediction.tif')).createFromArray(y2)
                reference.close()
                reference = QgsRasterLayer(reference.source())
                renderer = Utils.palettedRasterRendererFromCategories(reference.dataProvider(), 1, dump.categories)
                reference.setRenderer(renderer)
                reference.saveDefaultStyle()
                prediction.close()
                prediction = QgsRasterLayer(prediction.source())
                renderer = Utils.palettedRasterRendererFromCategories(prediction.dataProvider(), 1, dump.categories)
                prediction.setRenderer(renderer)
                prediction.saveDefaultStyle()
                # eval
                alg = ClassificationPerformanceSimpleAlgorithm()
                alg.initAlgorithm()
                parameters = {
                    alg.P_CLASSIFICATION: prediction,
                    alg.P_REFERENCE: reference,
                    alg.P_OUTPUT_REPORT: filename,
                }
                self.runAlg(alg, parameters, None, feedback2, context, True)

            result = {self.P_OUTPUT_REPORT: filename}
            self.toc(feedback, result)

        return result
