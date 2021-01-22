import inspect
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
class FitClassifierAlgorithmBase(EnMAPProcessingAlgorithm):
    P_RASTER = 'raster'
    P_CLASSIFICATION = 'classification'
    P_CODE = 'code'
    P_OUTPUT_CLASSIFIER = 'classifier'

    def displayName(self) -> str:
        raise NotImplementedError()

    def shortDescription(self) -> str:
        raise NotImplementedError()

    def helpParameterCode(self) -> str:
        raise NotImplementedError()

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self.P_RASTER, 'Raster with training data features.'),
            (self.P_CLASSIFICATION, 'Classification with training data labels. '
                                    f'{self.helpParameterMapClassification()} '
                                    f'Note that the classification layer is resampled/reprojected/rasterized '
                                    f'internally to match the raster grid.'),
            (self.P_CODE, self.helpParameterCode()),
            (self.P_OUTPUT_MODEL, 'Output model destination (*.pkl file). '
                                  'This file can be used for applying the classifier to an image using '
                                  '<i>Classification / Predict Classification<\i> and '
                                  '<i>Classification / Predict Class Probability<\i>.')
        ]

    def group(self):
        return Group.Test.value + Group.Classification.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterRasterLayer(self.P_RASTER, 'Raster')
        self.addParameterMapLayer(self.P_CLASSIFICATION, 'Label')
        self.addParameterString(self.P_CODE, 'Code', self.codeAsString(), True, advanced=True)
        self.addParameterFileDestination(
            self.P_OUTPUT_CLASSIFIER, 'Output Classifier', 'Model file (*.pkl)', f'{self.P_OUTPUT_CLASSIFIER}')

    #def code(self) -> ClassifierMixin:
    #    raise NotImplementedError()

    def codeAsString(self):
        lines = [line for line in inspect.getsource(self.code).split('\n')
                 if not line.strip().startswith('def') and line != ''][:-1]
        lines = '\n'.join([line[8:] for line in lines])
        return lines

    def makeClassifier(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> ClassifierMixin:
        namespace = dict()
        code = self.parameterAsString(parameters, self.P_CODE, context)
        exec(code, namespace)
        return namespace['classifier']

    def checkParameterCode(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        try:
            self.makeClassifier(parameters, context)
        except Exception as error:
            return False, traceback.format_exc()
        return True, ''

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
        code = self.parameterAsString(parameters, self.P_CODE, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_CLASSIFIER, context)
        classifier = self.makeClassifier()

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