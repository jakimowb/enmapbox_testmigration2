from os.path import basename
from typing import Dict, Any, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback)
from sklearn.inspection import permutation_importance

from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from enmapboxprocessing.reportwriter import MultiReportWriter, HtmlReportWriter, CsvReportWriter
from enmapboxprocessing.typing import ClassifierDump
from enmapboxprocessing.utils import Utils
from typeguard import typechecked


@typechecked
class ClassifierPermutationFeatureImportanceAlgorithm(EnMAPProcessingAlgorithm):
    P_CLASSIFIER, _CLASSIFIER = 'classifier', 'Classifier'
    P_SAMPLE, _SAMPLE = 'sample', 'Sample'
    P_SCORING, _SCORING = 'scoring', 'Scoring'
    O_SCORING = ['accuracy', 'balanced_accuracy', 'top_k_accuracy', 'average_precision', 'neg_brier_score', 'f1',
                 'f1_micro', 'f1_macro', 'f1_weighted', 'f1_samples', 'neg_log_loss', 'precision', 'recall', 'jaccard',
                 'roc_auc', 'roc_auc_ovr', 'roc_auc_ovo', 'roc_auc_ovr_weighted', 'roc_auc_ovo_weighted']
    P_REPEATS, _REPEATS = 'repeats', 'Number of repeats'
    P_SEED, _SEED = 'seed', 'Random seed'
    P_OUTPUT_REPORT, _OUTPUT_REPORT = 'outputReport', 'Output report'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self._CLASSIFIER, 'Classifier (*.pkl) file.'),
            (self._SAMPLE, 'Sample (*.pkl) file.'),
            (self._SCORING,
             f'Scorer to use. See {self.htmlLink("https://scikit-learn.org/stable/modules/model_evaluation.html#scoring-parameter", "The scoring parameter: defining model evaluation rules")} for further information.'),
            (self._REPEATS, 'Number of times to permute a feature.'),
            (self._SEED, 'The seed for the random generator can be provided.'),
            (self._OUTPUT_REPORT, 'Output report *.html file.')
        ]

    def displayName(self) -> str:
        return 'Classifier permutation feature importance'

    def shortDescription(self) -> str:
        return 'Permutation feature importance is a model inspection technique that is especially useful for non-linear or opaque estimators. ' \
               'The permutation feature importance is defined to be the decrease in a model score when a single feature value is randomly shuffled. ' \
               'This procedure breaks the relationship between the feature and the target, thus the drop in the model score is indicative of how much the model depends on the feature. ' \
               'This technique benefits from being model agnostic and can be calculated many times with different permutations of the feature.\n' \
               f'See {self.htmlLink("https://scikit-learn.org/stable/modules/permutation_importance.html#permutation-importance", "Permutation feature importance")} for further information.'

    def group(self):
        return Group.Test.value + Group.Classification.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterFile(self.P_CLASSIFIER, self._CLASSIFIER, extension='pkl')
        self.addParameterFile(self.P_SAMPLE, self._SAMPLE, extension='pkl')
        self.addParameterEnum(
            self.P_SCORING, self._SCORING, self.O_SCORING, False, self.O_SCORING.index('f1_macro'), advanced=True
        )
        self.addParameterInt(self.P_REPEATS, self._REPEATS, 10, False, 1, advanced=True)
        self.addParameterInt(self.P_SEED, self._SEED, None, True, 1, advanced=True)
        self.addParameterFileDestination(self.P_OUTPUT_REPORT, self._OUTPUT_REPORT, 'Report file (*.html)')

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        filenameClassifier = self.parameterAsFile(parameters, self.P_CLASSIFIER, context)
        filenameSample = self.parameterAsFile(parameters, self.P_SAMPLE, context)
        scoring = self.O_SCORING[self.parameterAsInt(parameters, self.P_SCORING, context)]
        repeats = self.parameterAsInt(parameters, self.P_REPEATS, context)
        seed = self.parameterAsInt(parameters, self.P_SEED, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_REPORT, context)

        with open(filename + '.log', 'w') as logfile:
            feedback, feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(feedback, parameters, context)

            classifier = ClassifierDump(**Utils.pickleLoad(filenameClassifier)).classifier
            dump = ClassifierDump(**Utils.pickleLoad(filenameSample))
            X, y, features = dump.X, dump.y, dump.features

            feedback.pushInfo(f'Load classifier: {classifier}')
            feedback.pushInfo(f'Load sample data: X=array{list(X.shape)} y=array{list(dump.y.shape)}')

            feedback.pushInfo('Evaluate permutation feature importance')
            r = permutation_importance(
                estimator=classifier, X=X, y=y.ravel(), scoring=scoring, n_repeats=repeats, random_state=seed
            )
            ordered = r.importances_mean.argsort()  # [::-1]

            # create plot
            figsizeX = 20
            figsizeY = len(features) * 0.15 + 1
            fig, ax = plt.subplots(figsize=(figsizeX, figsizeY))
            plt.xlabel(f'decrease in {scoring} score')
            ax.boxplot(r.importances[ordered].T,
                vert=False, labels=np.array(features)[ordered]
            )
            ax.set_title("Permutation Importances")
            fig.tight_layout()
            filenameFig = filename + '.fig.png'
            fig.savefig(filenameFig, format='png')

            ordered = ordered[::-1]
            values = np.array([r.importances_mean[ordered], r.importances_std[ordered]]).T.round(4).tolist()

            with \
                    open(filename, 'w') as fileHtml, \
                    open(filename + '.csv', 'w') as fileCsv:
                report = MultiReportWriter([HtmlReportWriter(fileHtml), CsvReportWriter(fileCsv)])
                report.writeHeader('Permutation importances')
                report.writeParagraph('Scoring function:', scoring)
                report.writeParagraph('Number of repeats:', repeats)
                report.writeImage(basename(filenameFig))
                report.writeTable(
                    values,
                    'Permutation feature importance',
                    ['mean', 'standard deviation'],
                    np.array(features)[ordered].tolist(),
                )
                report.writeParagraph(
                    f'See {self.htmlLink("https://scikit-learn.org/stable/modules/permutation_importance.html#permutation-importance", "Permutation feature importance")} for further information.'
                )

            result = {self.P_OUTPUT_REPORT: filename}
            self.toc(feedback, result)

        return result
