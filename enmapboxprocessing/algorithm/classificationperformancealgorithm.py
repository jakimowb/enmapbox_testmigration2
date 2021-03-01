import inspect
import traceback
from collections import defaultdict
from math import ceil
from typing import Dict, Any, List, Tuple, Union

import numpy as np
from osgeo import gdal
from sklearn.base import ClassifierMixin
from processing.core.Processing import Processing

from enmapboxprocessing.algorithm.predictclassificationalgorithm import PredictClassificationAlgorithm
from enmapboxprocessing.algorithm.predictclassprobabilityalgorithm import PredictClassPropabilityAlgorithm
from enmapboxprocessing.algorithm.translateclassificationalgorithm import TranslateClassificationAlgorithm
from enmapboxprocessing.processingfeedback import ProcessingFeedback
from hubflow.core import ClassificationPerformance
from typeguard import typechecked
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsVectorLayer, QgsRasterLayer,
                        QgsPalettedRasterRenderer, QgsMapLayer, QgsCategorizedSymbolRenderer,
                        QgsFeatureRequest, QgsFeature, QgsCoordinateTransform, QgsProject, QgsGeometry, QgsPointXY,
                        QgsPoint, QgsRasterDataProvider, QgsProcessingParameterRasterDestination,
                        QgsProcessingParameterField, QgsProcessingException)

from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from enmapboxprocessing.algorithm.rasterizeclassificationalgorithm import RasterizeClassificationAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.typing import SampleX, SampleY, Categories, checkSampleShape
from enmapboxprocessing.utils import Utils


@typechecked
class ClassificationPerformanceAlgorithm(EnMAPProcessingAlgorithm):
    P_CLASSIFICATION = 'classification'
    P_REFERENCE = 'reference'
    P_OUTPUT_REPORT = 'outReport'

    def displayName(self) -> str:
        return 'Classification Performance'

    def shortDescription(self) -> str:
        return 'Assesses the accuracy of a classification by comparing it to a reference classification. ' \
               '\nClasses are matched by name, and only those classes specified by the reference classification are ' \
               'considered. '

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self.P_CLASSIFICATION, self.helpParameterClassification()),
            (self.P_REFERENCE, 'Classification with reference labels. '
                               f'{self.helpParameterMapClassification()} '
                               f'The layer is resampled, reprojected and rasterized internally to match the '
                               f'classification grid, if required.'),
            (self.P_OUTPUT_REPORT, self.helpParameterReportDestination())
        ]

    def group(self):
        return Group.Test.value + Group.AccuracyAssessment.value

    def checkCategories(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        classification = self.parameterAsRasterLayer(parameters, self.P_CLASSIFICATION, context)
        reference = self.parameterAsLayer(parameters, self.P_REFERENCE, context)
        if isinstance(reference, QgsVectorLayer):
            categoriesReference = Utils.categoriesFromCategorizedSymbolRenderer(reference.renderer())
        elif isinstance(reference, QgsRasterLayer):
            categoriesReference = Utils.categoriesFromPalettedRasterRenderer(reference.renderer())
        else:
            assert 0
        categoriesPrediction = Utils.categoriesFromPalettedRasterRenderer(classification.renderer())
        for idR, nameR, colorR in categoriesReference:
            for idP, nameP, colorP in categoriesPrediction:
                if nameR == nameP:
                    return True, ''  # good, we found the reference category
            return False, f'Reference class "{nameR}" not found in classification.'

    def checkParameterValues(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        checks = [
            self.checkParameterRasterClassification(parameters, self.P_CLASSIFICATION, context),
            self.checkParameterMapClassification(parameters, self.P_REFERENCE, context),
        ]
        for valid, message in checks:
            if not valid:
                return valid, message
        return self.checkCategories(parameters, context)

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterRasterLayer(self.P_CLASSIFICATION, 'Classification')
        self.addParameterMapLayer(self.P_REFERENCE, 'Reference')
        self.addParameterFileDestination(self.P_OUTPUT_REPORT, 'Output Report', 'HTML file (*.html)')

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        classification = self.parameterAsRasterLayer(parameters, self.P_CLASSIFICATION, context)
        reference = self.parameterAsLayer(parameters, self.P_REFERENCE, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_REPORT, context)

        with open(filename + '.log', 'w') as logfile:
            feedback, feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(feedback, parameters, context)

            # resample/rasterize reference to classification grid
            if isinstance(reference, QgsVectorLayer):
                feedback.pushInfo('Rasterize reference')
                alg = RasterizeClassificationAlgorithm()
                alg.initAlgorithm()
                parameters = {
                    alg.P_VECTOR: reference,
                    alg.P_GRID: classification,
                    alg.P_CREATION_PROFILE: alg.TiledAndCompressedGTiffProfile,
                    alg.P_OUTPUT_RASTER: Utils.tmpFilename(filename, 'reference.tif')
                }
                Processing.runAlgorithm(alg, parameters, None, feedback2, context)
                reference = QgsRasterLayer(parameters[alg.P_OUTPUT_RASTER])
            elif isinstance(reference, QgsRasterLayer):
                feedback.pushInfo('Resample reference')
                alg = TranslateClassificationAlgorithm()
                alg.initAlgorithm()
                parameters = {
                    alg.P_CLASSIFICATION: reference,
                    alg.P_GRID: classification,
                    alg.P_CREATION_PROFILE: alg.VrtProfile,
                    alg.P_OUTPUT_RASTER: Utils.tmpFilename(filename, 'reference.vrt')
                }
                Processing.runAlgorithm(alg, parameters, None, feedback, context)
                reference = QgsRasterLayer(parameters[alg.P_OUTPUT_RASTER])
            else:
                raise ValueError(f'invalid layer: {reference}')

            feedback.pushInfo('Read data')
            arrayReference = RasterReader(reference).array()[0]
            arrayPrediction = RasterReader(classification).array()[0]
            categoriesReference = Utils.categoriesFromPalettedRasterRenderer(reference.renderer())
            categoriesPrediction = Utils.categoriesFromPalettedRasterRenderer(classification.renderer())
            # - get valid reference location
            valid = np.full_like(arrayReference, False, np.bool)
            for category in categoriesReference:
                id, name, color = category
                np.logical_or(valid, arrayReference == id, out=valid)
            yR = arrayReference[valid].astype(np.float32)
            yP = arrayPrediction[valid].astype(np.float32)
            yPRemapped = np.zeros_like(yP)
            # - remap class ids by name
            for idP, nameP, colorP in categoriesPrediction:
                for idR, nameR, colorR in categoriesReference:
                    if nameR == nameP:
                        yPRemapped[yP == idP] = idR

            # calculate performance
            feedback.pushInfo('Assess performance and create report')
            assert 0  # todo match data by class names

            ClassificationPerformance

            result = {self.P_OUTPUT_REPORT: filename}
            self.toc(feedback, result)

        return result


''''
@typechecked
class ClassificationPerformance(object):
    def __init__(self, yP, yT, categories: Categories, n: int):
        assert isinstance(yP, np.ndarray) and yP.ndim == 1
        assert isinstance(yT, np.ndarray) and yT.shape == yP.shape
        assert isinstance(classDefinitionP, ClassDefinition)
        assert isinstance(classDefinitionT, ClassDefinition)
        assert classDefinitionT.classes() == classDefinitionP.classes()

        self.classDefinitionT = classDefinitionT
        self.classDefinitionP = classDefinitionP
        self.N = N

        import sklearn.metrics
        self.yP = yP
        self.yT = yT
        self.mij = np.int64(
            sklearn.metrics.confusion_matrix(yT, yP, labels=range(1, classDefinitionT.classes() + 1)).T)
        self.m = np.int64(yP.size)
        self.classProportions = self.Wi = classProportions
        self._assessPerformance()

    def __getstate__(self):
        return OrderedDict([('yP', self.yP),
                            ('yT', self.yT),
                            ('classDefinitionP', self.classDefinitionP),
                            ('classDefinitionT', self.classDefinitionT),
                            ('classProportions', self.classProportions),
                            ('N', self.N)])

    @staticmethod
    def fromRaster(prediction, reference, mask=None, **kwargs):
        assert isinstance(prediction, Classification)
        assert isinstance(reference, Classification)
        stratification = prediction
        classes = stratification.classDefinition().classes()
        histogram = stratification.statistics(calcHistogram=True,
            histogramBins=[classes],
            histogramRanges=[(1, classes + 1)], **kwargs)
        classProportions = [float(count) / sum(histogram) for i, count in enumerate(histogram)]
        N = sum(histogram)

        yP, yT = MapCollection(maps=[prediction, reference]).extractAsArray(masks=[prediction, reference, mask])

        return ClassificationPerformance(yP=yP[0], yT=yT[0],
            classDefinitionP=prediction.classDefinition(),
            classDefinitionT=reference.classDefinition(),
            classProportions=classProportions,
            N=N)

    def _assessPerformance(self):

        old_error_state = np.geterr()
        np.seterr(divide='ignore', invalid='ignore', over='raise', under='raise')

        # get some stats from the confusion matrix mij
        self.mi_ = np.sum(self.mij, axis=0, dtype=np.float64)  # class-wise sum over all prediction
        self.m_j = np.sum(self.mij, axis=1, dtype=np.float64)  # class-wise sum over references
        self.mii = np.diag(self.mij)  # main diagonal -> class-wise correctly classified samples

        # estimate mapped class proportions from the reference sample, if not provided by the user
        if self.Wi is None:
            self.Wi = self.mi_ / self.m  # note that in this case pij is reduced to pij=mij/m

        # pij is the proportion of area estimate
        # pij = Wi*mij/mi_
        self.pij = np.zeros_like(self.mij, dtype=np.float64)
        for i in range(self.classDefinitionT.classes()):
            for j in range(self.classDefinitionT.classes()):
                self.pij[i, j] = self.Wi[i] * self.mij[i, j] / self.mi_[i]

        self.pi_ = np.sum(self.pij, axis=0, dtype=np.float64)
        self.p_j = np.sum(self.pij, axis=1, dtype=np.float64)
        self.pii = np.diag(self.pij)

        # calculate performance measures
        self.ProducerAccuracy = self._fix(self.mii / self.mi_)
        self.UserAccuracy = self._fix(self.mii / self.m_j)

        self.F1Accuracy = self._fix(
            2 * self.UserAccuracy * self.ProducerAccuracy / (self.UserAccuracy + self.ProducerAccuracy))
        self.ConditionalKappaAccuracy = self._fix(
            (self.m * self.mii - self.mi_ * self.m_j) / (self.m * self.mi_ - self.mi_ * self.m_j))
        self.OverallAccuracy = self._fix(self.mii.sum() / float(self.m))
        self.KappaAccuracy = self._fix(
            (self.m * self.mii.sum() - np.sum(self.mi_ * self.m_j)) / (self.m ** 2 - np.sum(self.mi_ * self.m_j)))

        # calculate squared standard errors (SSE)

        self.OverallAccuracySSE = 0.
        for i in range(self.classDefinitionT.classes()):
            self.OverallAccuracySSE += self.pij[i, i] * (
                    self.Wi[i] - self.pij[i, i]) / (self.Wi[i] * self.m)

        a1 = self.mii.sum() / self.m
        a2 = (self.mi_ * self.m_j).sum() / self.m ** 2
        a3 = (self.mii * (self.mi_ + self.m_j)).sum() / self.m ** 2
        a4 = 0.
        for i in range(self.classDefinitionT.classes()):
            for j in range(self.classDefinitionT.classes()):
                a4 += self.mij[i, j] * (self.mi_[j] + self.m_j[i]) ** 2
        a4 /= self.m ** 3
        b1 = a1 * (1 - a1) / (1 - a2) ** 2
        b2 = 2 * (1 - a1) * (2 * a1 * a2 - a3) / (1 - a2) ** 3
        b3 = (1 - a1) ** 2 * (a4 - 4 * a2 ** 2) / (1 - a2) ** 4
        self.KappaAccuracySSE = (b1 + b2 + b3) / self.m

        self.ProducerAccuracySSE = np.zeros(self.classDefinitionT.classes(), dtype=np.float64)
        for i in range(self.classDefinitionT.classes()):
            sum = 0.
            for j in range(self.classDefinitionT.classes()):
                if i == j:
                    continue
                sum += self.pij[i, j] * (self.Wi[j] - self.pij[i, j]) / (self.Wi[j] * self.m)
                self.ProducerAccuracySSE[i] = self.pij[i, i] * self.p_j[i] ** (-4) * (
                        self.pij[i, i] * sum + (self.Wi[i] - self.pij[i, i]) * (self.p_j[i] - self.pij[i, i]) ** 2 / (
                        self.Wi[i] * self.m))

        self.UserAccuracySSE = np.zeros(self.classDefinitionT.classes(), dtype=np.float64)
        for i in range(self.classDefinitionT.classes()):
            self.UserAccuracySSE[i] = self.pij[i, i] * (self.Wi[i] - self.pij[i, i]) / (self.Wi[i] ** 2 * self.m)

        self.F1AccuracySSE = self._fix(
            2 * self.UserAccuracySSE * self.ProducerAccuracySSE / (self.UserAccuracySSE + self.ProducerAccuracySSE))

        self.ConditionalKappaAccuracySSE = self.m * (self.mi_ - self.mii) / (self.mi_ * (self.m - self.m_j)) ** 3 * (
                (self.mi_ - self.mii) * (self.mi_ * self.m_j - self.m * self.mii) + self.m * self.mii * (
                self.m - self.mi_ - self.m_j + self.mii))

        self.ClassProportion = self.m_j / self.m
        self.ClassProportionSSE = np.zeros(self.classDefinitionT.classes(), dtype=np.float64)
        for j in range(self.classDefinitionT.classes()):
            for i in range(self.classDefinitionT.classes()):
                self.ClassProportionSSE[j] += self.Wi[i] ** 2 * (
                        (self.mij[i, j] / self.mi_[i]) * (1 - self.mij[i, j] / self.mi_[i])) / (self.mi_[i] - 1)

        np.seterr(**old_error_state)

    def _confidenceIntervall(self, mean, sse, alpha):
        import scipy.stats
        se = np.sqrt(np.clip(sse, 0, np.inf))
        lower = scipy.stats.norm.ppf(alpha / 2.) * se + mean
        upper = scipy.stats.norm.ppf(1 - alpha / 2.) * se + mean
        return lower, upper

    def _fix(self, a, fill=0):
        if isinstance(a, np.ndarray):
            a[np.logical_not(np.isfinite(a))] = fill
        elif not np.isfinite(a):
            a = fill
        return a

    def reportTitle(self):
        return 'Classification Performance'

    def appendReportHeader(self, report):
        assert isinstance(report, Report)
        pass

    def report(self):

        report = Report(title=self.reportTitle())

        self.appendReportHeader(report=report)

        report.append(ReportHeading('Class Overview'))
        colHeaders = None
        rowSpans = [[1, 2], [1, 1, 1]]
        rowHeaders = [['', 'Class Names'], ['Class ID', 'Reference', 'Prediction']]
        data = [np.hstack((range(1, self.classDefinitionT.classes() + 1))), self.classDefinitionT.names(),
                self.classDefinitionP.names()]

        report.append(ReportTable(data, '', colHeaders=colHeaders, rowHeaders=rowHeaders,
            colSpans=None, rowSpans=rowSpans))

        # Confusion Matrix Table
        report.append(ReportHeading('Confusion Matrix'))
        classNumbers = []
        for i in range(self.classDefinitionT.classes()):
            classNumbers.append('(' + str(i + 1) + ')')
        colHeaders = [['Reference Class'], classNumbers + ['Sum']]
        colSpans = [[self.classDefinitionT.classes()], np.ones(self.classDefinitionT.classes() + 1, dtype=int)]
        classNamesColumn = []
        for i in range(self.classDefinitionT.classes()):
            classNamesColumn.append(
                '(' + str(i + 1) + ') ' + self.classDefinitionT.names()[i])
        rowHeaders = [classNamesColumn + ['Sum']]
        data = np.vstack(((np.hstack((self.mij, self.m_j[:, None]))), np.hstack((self.mi_, self.m)))).astype(
            int)

        report.append(ReportTable(data, '', colHeaders=colHeaders, rowHeaders=rowHeaders, colSpans=colSpans))

        # Accuracies Table
        report.append(ReportHeading('Accuracies'))
        colHeaders = [['Measure', 'Estimate [%]', '95 % Confidence Interval [%]']]
        colSpans = [[1, 1, 2]]
        rowHeaders = None
        data = [['Overall Accuracy', np.round(self.OverallAccuracy * 100, 2),
                 np.round(self._confidenceIntervall(self.OverallAccuracy, self.OverallAccuracySSE, 0.05)[0] * 100),
                 round(self._confidenceIntervall(self.OverallAccuracy, self.OverallAccuracySSE, 0.05)[1] * 100, 2)],
                ['Kappa Accuracy', np.round(self.KappaAccuracy * 100, 2),
                 np.round(self._confidenceIntervall(self.KappaAccuracy, self.KappaAccuracySSE, 0.05)[0] * 100, 2),
                 np.round(self._confidenceIntervall(self.KappaAccuracy, self.KappaAccuracySSE, 0.05)[1] * 100, 2)],
                ['Mean F1 Accuracy', np.round(np.mean(self.F1Accuracy) * 100, 2), '-', '-']]
        report.append(ReportTable(data, '', colHeaders, rowHeaders, colSpans, rowSpans))

        # Class-wise Accuracies Table
        report.append(ReportHeading('Class-wise Accuracies'))
        colSpans = [[1, 3, 3, 3], [1, 1, 2, 1, 2, 1, 2]]
        colHeaders = [['', 'User\'s Accuracy [%]', 'Producer\'s Accuracy [%]', 'F1 Accuracy'],
                      ['Map class', 'Estimate', '95 % Interval', 'Estimate', '95% Interval', 'Estimate',
                       '95% Interval']]
        data = [classNamesColumn, np.round(self.UserAccuracy * 100, 2)
            , np.round(self._confidenceIntervall(self.UserAccuracy, self.UserAccuracySSE, 0.05)[0] * 100, 2)
            , np.round(self._confidenceIntervall(self.UserAccuracy, self.UserAccuracySSE, 0.05)[1] * 100, 2)
            , np.round(self.ProducerAccuracy * 100, 2)
            , np.round(self._confidenceIntervall(self.ProducerAccuracy, self.ProducerAccuracySSE, 0.05)[0] * 100, 2)
            , np.round(self._confidenceIntervall(self.ProducerAccuracy, self.ProducerAccuracySSE, 0.05)[1] * 100, 2)
            , np.round(self.F1Accuracy * 100, 2)
            , np.round(self._confidenceIntervall(self.F1Accuracy, self.F1AccuracySSE, 0.05)[0] * 100, 2)
            , np.round(self._confidenceIntervall(self.F1Accuracy, self.F1AccuracySSE, 0.05)[1] * 100, 2)]
        data = [list(x) for x in zip(*data)]
        report.append(ReportTable(data, '', colHeaders=colHeaders, rowHeaders=rowHeaders, colSpans=colSpans))

        # Proportion Matrix Table
        report.append(ReportHeading('Proportion Matrix'))
        colHeaders = [['Reference Class'], classNumbers + ['Sum']]
        colSpans = [[self.classDefinitionT.classes()], np.ones(self.classDefinitionT.classes() + 1, dtype=int)]
        rowHeaders = [classNamesColumn + ['Sum']]
        data = np.vstack(
            ((np.hstack((self.pij, self.p_j[:, None]))), np.hstack((self.pi_, 1))))
        report.append(ReportTable(np.round(data, 4), '', colHeaders=colHeaders, rowHeaders=rowHeaders,
            colSpans=colSpans))

        # Class-wise Area Estimates
        report.append(ReportHeading('Class-wise Proportion and Area Estimates'))
        colSpans = [[1, 3, 3], [1, 1, 2, 1, 2]]
        colHeaders = [['', 'Proportion', 'Area [px]'],
                      ['Map class', 'Estimate', '95 % Interval', 'Estimate', '95 % Interval']]
        data = [classNamesColumn,
                np.round(self.ClassProportion, 4),
                np.round(self._confidenceIntervall(self.ClassProportion, self.ClassProportionSSE, 0.05)[0], 4),
                np.round(self._confidenceIntervall(self.ClassProportion, self.ClassProportionSSE, 0.05)[1], 4),
                np.round(self.ClassProportion * self.N, 1),
                np.round(self._confidenceIntervall(self.ClassProportion, self.ClassProportionSSE, 0.05)[0] * self.N, 1),
                np.round(self._confidenceIntervall(self.ClassProportion, self.ClassProportionSSE, 0.05)[1] * self.N, 1)]
        data = [list(x) for x in zip(*data)]
        report.append(ReportTable(data, '', colHeaders=colHeaders, colSpans=colSpans))

        return report
'''

# implementation is based on:
# Stehman, S. V., 2014.
# Estimating area and map accuracy for stratified random sampling when the strata are different from the map classes.
# Int. J. Remote Sens. 35, 4923-4939.
# https://doi.org/10.1080/01431161.2014.930207
@typechecked
def aa_stratified(stratum: List, reference: List, map, h, N_h, classes=None):
    assert len(stratum) == len(reference) == len(map)
    assert len(h) == len(N_h)

    # check if stratum samples match stratum labels corresponding to stratum size
    for stratum_i in stratum:
        assert stratum_i in h

    # determine class labels
    if classes is None:
        classes = np.unique(map)

    stratum = np.array(stratum)
    reference = np.array(reference)
    map = np.array(map)
    h = np.array(h)
    N_h = np.array(N_h, dtype=np.float64)

    stats = defaultdict(list)
    stats['classes'] = list(classes)

    # adjusted confusion matrix area proportions (sums to 1).
    cmp = np.zeros((len(classes), len(classes)))
    for i in range(len(classes)):
        for j in range(len(classes)):
            y_u = np.logical_and(map == classes[i], reference == classes[j])
            cmp[i, j] = aa_estimator_stratified(stratum, y_u, h, N_h)[0]
    stats['confusion_matrix_proportions'] = cmp

    # adjusted confusion matrix counts
    stats['confusion_matrix_counts'] = cmp * len(reference)

    # overall accuracy
    oa, oa_se = aa_estimator_stratified(stratum, map == reference, h, N_h)
    stats['overall_accuracy'] = oa
    stats['overall_accuracy_se'] = oa_se

    for i in range(len(classes)):
        # area proportion
        R, R_SE = aa_estimator_stratified(stratum, reference == classes[i], h, N_h)
        stats['area_proportion'].append(R)
        stats['area_proportion_se'].append(R_SE)

        # user's accuracy
        x_u = map == classes[i]
        y_u = np.logical_and(reference == classes[i], map == classes[i])
        ua, ua_se = aa_estimator_stratified_ratio(stratum, x_u, y_u, h, N_h)
        stats['users_accuracy'].append(ua)
        stats['users_accuracy_se'].append(ua_se)

        # producer's accuracy
        x_u = reference == classes[i]
        y_u = np.logical_and(reference == classes[i], map == classes[i])
        pa, pa_se = aa_estimator_stratified_ratio(stratum, x_u, y_u, h, N_h)
        stats['producers_accuracy'].append(pa)
        stats['producers_accuracy_se'].append(pa_se)

        # f1
        stats['f1'].append(2 * ua * pa / (ua + pa))
        stats['f1_se'].append(np.sqrt(np.add(
            (ua_se * (2 * pa / (ua + pa) - 2 * ua * pa / (ua + pa) ** 2)) ** 2,
            (pa_se * (2 * ua / (ua + pa) - 2 * ua * pa / (ua + pa) ** 2)) ** 2
        )))

    return stats


@typechecked
def aa_estimator_stratified(
        stratum: np.ndarray, y_u: np.ndarray, h: np.ndarray, N_h: np.ndarray, finitePopulationCorrection=False
):
    Y = 0.
    n_h = np.zeros_like(N_h)
    for i in range(len(h)):
        indices = np.where(stratum == h[i])[0]
        y_u_mean = np.mean(y_u[indices])
        Y += N_h[i] * y_u_mean
        n_h[i] = len(indices)
    R = Y / np.sum(N_h)

    R_VAR = 0.
    for i in range(len(h)):
        indices = np.where(stratum == h[i])[0]
        if finitePopulationCorrection:
            f = (1. - n_h[i] / N_h[i])
        else:
            f = 1.
        s2yh = np.var(y_u[indices], ddof=1)
        R_VAR += N_h[i] ** 2 * f * s2yh / n_h[i]
    R_VAR /= np.sum(N_h) ** 2
    R_SE = np.sqrt(R_VAR)
    return R, R_SE


@typechecked
def aa_estimator_stratified_ratio(
        stratum: np.ndarray, x_u: np.ndarray, y_u: np.ndarray, h: np.ndarray, N_h: np.ndarray,
        finitePopulationCorrection=False
):
    X = 0.
    Y = 0.
    n_h = np.zeros_like(N_h)
    for i in range(len(h)):
        indices = np.where(stratum == h[i])[0]
        x_u_mean = np.mean(x_u[indices])
        y_u_mean = np.mean(y_u[indices])
        Y += N_h[i] * y_u_mean
        X += N_h[i] * x_u_mean
        n_h[i] = len(indices)
    R = Y / X

    R_VAR = 0.
    for i in range(len(h)):
        indices = np.where(stratum == h[i])[0]
        if finitePopulationCorrection:
            f = (1. - n_h[i] / N_h[i])
        else:
            f = 1.
        s2xh = np.var(x_u[indices], ddof=1)
        s2yh = np.var(y_u[indices], ddof=1)
        sxyh = np.cov(x_u[indices], y_u[indices], ddof=1)[0][1]
        R_VAR += N_h[i] ** 2 * f * (s2yh + R ** 2 * s2xh - 2 * R * sxyh) / n_h[i]
    R_VAR /= X ** 2
    R_SE = np.sqrt(R_VAR)
    return R, R_SE
