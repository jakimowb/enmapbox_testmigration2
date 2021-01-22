import traceback
from os.path import splitext, basename
from time import time
from typing import Dict, Any, List, Tuple
from warnings import warn

import numpy as np
import sklearn
from osgeo import gdal
from sklearn.base import ClassifierMixin
from sklearn.ensemble import RandomForestClassifier

from enmapboxprocessing.algorithm.fitestimatoralgorithm import FitClassifierAlgorithmBase
from enmapboxprocessing.algorithm.rasterizeclassificationalgorithm import RasterizeClassificationAlgorithm
from enmapboxprocessing.algorithm.translaterasteralgorithm import TranslateRasterAlgorithm
from enmapboxprocessing.driver import Driver
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.rasterwriter import RasterWriter
from enmapboxprocessing.typing import CreationOptions
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
        return 'Fit a Random Forest Classifier.'

    def helpParameterCode(self) -> str:
        return 'Scikit-learn python code. ' \
               'See <a href="' \
               'http://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html' \
               '">RandomForestClassifier</a> for information on different parameters.'

    def code(self) -> ClassifierMixin:
        from sklearn.ensemble import RandomForestClassifier
        classifier = RandomForestClassifier(n_estimators=100, oob_score=True)
        return classifier

    def checkParameterValues(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        checks = [
            self.checkParameterMapClassification(parameters, self.P_CLASSIFICATION, context),
            self.checkParameterCode(parameters, context)
        ]
        for valid, message in checks:
            if not valid:
                return valid, message
        return True, ''

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        raster = self.parameterAsRasterLayer(parameters, self.P_RASTER, context)
        classification = self.parameterAsLayer(parameters, self.P_CLASSIFICATION, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_CLASSIFIER, context)
        classifier = self.makeClassifier(parameters, context)

        self.processQgis(
            raster, classification, classifier, filename, feedback
        )
        return {self.P_OUTPUT_CLASSIFIER: filename}

    @classmethod
    def processQgis(
            cls, raster: QgsRasterLayer, classification: QgsMapLayer, classifier: ClassifierMixin, filename: str,
            feedback: QgsProcessingFeedback = None
    ):

        if isinstance(classification, QgsRasterLayer):
            assert 0
        elif isinstance(classification, QgsVectorLayer):
            RasterizeClassificationAlgorithm
            assert 0
        else:
            assert 0


""""
class EstimatorFit(EnMAPAlgorithm):
    def __init__(self, name, code, helpAlg, helpCode, postCode=None):
        self._name = name
        self._code = code
        self._postCode = postCode
        self._helpAlg = helpAlg
        self._helpCode = helpCode
        super().__init__()

    def description(self):
        return self._helpAlg

    def createInstance(self):
        return type(self)(name=self._name, code=self._code, helpAlg=self._helpAlg, helpCode=self._helpCode,
            postCode=self._postCode)

    def displayName(self):
        return 'Fit ' + self._name

    def code(self):
        return self._code

    def postCode(self):
        return self._postCode

    P_CODE = 'code'

    def addParameterCode(self):
        self.addParameterString(self.P_CODE, 'Code', defaultValue=self._code, multiLine=True, help=self._helpCode)

    def sklEstimator(self):
        namespace = dict()
        code = self.getParameterString(self.P_CODE)
        exec(code, namespace)
        assert 'estimator' in namespace
        sklEstimator = namespace['estimator']
        return sklEstimator

    def processAlgorithm_(self):
        estimator = self.estimator(sklEstimator=self.sklEstimator())
        try:
            estimator.fit(sample=self.sample())
        except Exception as error:
            if 'Grids do not match and on the fly resampling is turned off.' in str(error):
                raise EnMAPAlgorithmParameterValueError(str(error))
            else:
                raise
        filename = self.getParameterOutputEstimator()
        estimator._initPickle()
        estimator.pickle(filename=filename, progressBar=self._progressBar)

        if self.postCode() is not None:
            exec(self.postCode(), {'estimator': estimator.sklEstimator(),
                                   'estimatorFilename': filename})

        return {self.P_OUTPUT_ESTIMATOR: filename}

    def sample(self):
        pass

    def estimator(self, sklEstimator):
        pass


class ClassifierFit(EstimatorFit):
    def group(self):
        return self.GROUP_CLASSIFICATION

    def defineCharacteristics(self):
        self.addParameterRaster(description='Raster', help='Raster with training data features.')
        self.addParameterClassification(description='Labels', help='Classification with training data labels.')
        self.addParameterMask()
        self.addParameterCode()
        self.addParameterOutputClassifier(name=self.P_OUTPUT_ESTIMATOR)

    def sample(self):
        return ClassificationSample(raster=self.getParameterRaster(),
            classification=self.getParameterClassification(),
            mask=self.getParameterMask())

    def estimator(self, sklEstimator):
        return Classifier(sklEstimator=sklEstimator)

    def cookbookRecipes(self):
        return [Cookbook.R_CLASSIFICATION, Cookbook.R_GRAPHICALMODELER]

    def cookbookDescription(self):
        return 'See the following Cookbook Recipes on how to use classifiers:'
"""