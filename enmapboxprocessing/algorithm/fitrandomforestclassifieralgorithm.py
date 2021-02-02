from typing import Dict, Any, List, Tuple

import processing
from osgeo import gdal
from sklearn.base import ClassifierMixin

from enmapboxprocessing.algorithm.fitclassifieralgorithmbase import FitClassifierAlgorithmBase
from enmapboxprocessing.algorithm.rasterizeclassificationalgorithm import RasterizeClassificationAlgorithm
from enmapboxprocessing.utils import Utils
from typeguard import typechecked
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsVectorLayer, QgsRectangle,
                        QgsCoordinateReferenceSystem, QgsRasterLayer, QgsPalettedRasterRenderer, QgsMapLayer,
                        QgsCategorizedSymbolRenderer)

from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group


@typechecked
class FitRandomForestClassifierAlgorithm(FitClassifierAlgorithmBase):

    def displayName(self) -> str:
        return 'Fit RandomForestClassifier'

    def shortDescription(self) -> str:
        return 'A random forest classifier.' \
               '\nA random forest is a meta estimator that fits a number of decision tree classifiers on various ' \
               'sub-samples of the dataset and uses averaging to improve the predictive accuracy and control ' \
               'over-fitting. The sub-sample size is controlled with the max_samples parameter if bootstrap=True ' \
               '(default), otherwise the whole dataset is used to build each tree.'

    def helpParameterCode(self) -> str:
        return 'Scikit-learn python code. ' \
               'See <a href="' \
               'http://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html' \
               '">RandomForestClassifier</a> for information on different parameters.'

    def code(self) -> ClassifierMixin:
        from sklearn.ensemble import RandomForestClassifier
        classifier = RandomForestClassifier(n_estimators=100, bootstrap=True, oob_score=True, max_samples=None)
        return classifier
