import inspect
import traceback
from math import ceil
from typing import Dict, Any, List, Tuple, Union

import numpy as np
from osgeo import gdal
from processing.core.Processing import Processing
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsVectorLayer, QgsRasterLayer,
                        QgsPalettedRasterRenderer, QgsMapLayer, QgsCategorizedSymbolRenderer,
                        QgsFeatureRequest, QgsFeature, QgsCoordinateTransform, QgsProject, QgsGeometry, QgsPointXY,
                        QgsPoint, QgsRasterDataProvider, QgsProcessingParameterField)

from enmapboxprocessing.algorithm.classificationperformancesimplealgorithm import \
    ClassificationPerformanceSimpleAlgorithm
from enmapboxprocessing.algorithm.predictclassificationalgorithm import PredictClassificationAlgorithm
from enmapboxprocessing.algorithm.predictclassprobabilityalgorithm import PredictClassPropabilityAlgorithm
from enmapboxprocessing.algorithm.translateclassificationalgorithm import TranslateClassificationAlgorithm
from enmapboxprocessing.algorithm.vectortoclassificationalgorithm import VectorToClassificationAlgorithm
from enmapboxprocessing.driver import Driver
from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from enmapboxprocessing.processingfeedback import ProcessingFeedback
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.reportwriter import MultiReportWriter, HtmlReportWriter, CsvReportWriter
from enmapboxprocessing.typing import SampleX, SampleY, Categories, checkSampleShape, Category, ClassifierDump
from enmapboxprocessing.utils import Utils
from typeguard import typechecked


@typechecked
class FitClassifierAlgorithmBase(EnMAPProcessingAlgorithm):
    P_LABELS, _LABELS = 'labels', 'Training data labels'
    P_FEATURES, _FEATURES = 'features', 'Training data features'
    P_LABELS_FIELD, _LABELS_FIELD = 'labelsField', 'Labels from field'
    P_FEATURE_FIELDS, _FEATURE_FIELDS = 'featureFields', 'Features from fields'
    P_CODE, _CODE = 'code', 'Code'
    P_SUBSAMPLE_SIZE, _SUBSAMPLE_SIZE = 'subsampleSize', 'Subsample size'
    P_SUBSAMPLE_REPLACE, _SUBSAMPLE_REPLACE = 'subsampleReplace', 'Subsample with replacement'
    P_SAVE_DATA, _SAVE_DATA = 'saveData', 'Save training data'
    P_RASTERIZE_POINTS, _RASTERIZE_POINTS = 'rasterizePoints', 'Rasterize points'
    P_SAVE_AS_JSON, _SAVE_AS_JSON = 'saveAsJson', 'Save model as JSON file'
    P_EVAL_TRAIN_PERFORMANCE, _EVAL_TRAIN_PERFORMANCE = 'evalTrainPerformance', 'Evaluate training data performance'
    P_EVAL_CROSS_PERFORMANCE, _EVAL_CROSS_PERFORMANCE = 'evalCrossPerformance', \
                                                        'Evaluate n-fold cross-validation performance'
    P_EVAL_PERMUTATION_FEATURE_IMPORTANCE, _EVAL_PERMUTATION_FEATURE_IMPORTANCE = 'evalPermutationFeatureImportance', 'Evaluate permutation feature importance'
    P_RASTER, _RASTER = 'rasterForPrediction', 'Raster for prediction'
    P_MASK, _MASK = 'maskForPrediction', 'Mask for prediction'
    P_COLORIZE_PROBABILITY, _COLORIZE_PROBABILITY = 'colorizeProbability', 'Colorize output probability'
    P_MAXIMUM_MEMORY_USAGE = 'maximumMemoryUsage'
    P_OUTPUT_CLASSIFICATION, _OUTPUT_CLASSIFICATION = 'outClassification', 'Output classification'
    P_OUTPUT_PROBABILITY, _OUTPUT_PROBABILITY = 'outClassProbability', 'Output class probability'
    P_OUTPUT_CLASSIFIER, _OUTPUT_CLASSIFIER = 'outClassifier', 'Output classifier'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            ('Training data input sources',
            'Data used for fitting the classifier can be provided in various ways:\n'
            f'1. Categories from raster ({self.htmlBold(self._LABELS)}) and features from raster ({self.htmlBold(self._FEATURES)}).\n'
            f'2. Categories from vector ({self.htmlBold(self._LABELS)}) and features from raster ({self.htmlBold(self._FEATURES)}).\n'
            f'3. Categories from vector ({self.htmlBold(self._LABELS)}) and features from fields ({self.htmlBold(self._FEATURE_FIELDS)}).\n'
            f'4. A vector table ({self.htmlBold(self._LABELS)}) with categories ({self.htmlBold(self._LABELS_FIELD)}) and features ({self.htmlBold(self._FEATURE_FIELDS)}) from fields.\n'
            f'5. Two text file (*.csv *.txt) with tabulated values[nsamples, 1] ({self.htmlBold(self._LABELS)}) and values[nsamples, nfeatures] ({self.htmlBold(self._FEATURES)}). '
            f'This matches the output format of the {self.htmlLink("https://force-eo.readthedocs.io/en/latest/components/higher-level/smp/index.html", "FORCE Higher Level Sampling Submodule")}. \n'
            f'6. A binary Pickle file (*.pkl) including a dictionary with numpy arrays X[nsamples, nfeatures] and y[nsamples, 1] (specify either {self.htmlBold(self._LABELS)} or {self.htmlBold(self._FEATURES)}). '
            f'You can for example use any previously trained model file to re-use the stored training data.\n'
            f'7. A JSON file (*.json) including a dictionary with lists of lists X[nsamples, nfeatures] and y[nsamples, 1] (specify either {self.htmlBold(self._LABELS)} or {self.htmlBold(self._FEATURES)}). '
            f'You can for example use any previously trained model (saved as JSON) file to re-use the stored training data.\n'
            f'To select non-spatial files (Pickle, JSON, Text or CSV), use the "..." buttons.'),

            (self._LABELS,
             f'Training data locations with categorical labels. {self.helpParameterMapClassification()} '
             f'The classification layer is resampled, reprojected and rasterized internally to match the raster grid, if required.\n'
             f'Note: you can safely ignore the {self.htmlBold("Could not load layer/table. Dependent field could not be populated.")} warning, when selecting a raster layer.'),
            (self._FEATURES,
             'Raster used for sampling training data features.'),
            (self._LABELS_FIELD,
             'Field to be used as training data labels (instead of using renderer categories).'),
            (self._FEATURE_FIELDS,
             'Fields to be used as training data features (instead of sampling from raster).'),
            (self._CODE, self.helpParameterCode()),
            (self._SUBSAMPLE_SIZE,
             'Use i) all data for training, if value is "not set", '
             'ii) a random subsample with given class size for values greater equal 1, '
             'or iii) a random subsample with given class propotion for values between 0 and 1.'),
            (self._SUBSAMPLE_REPLACE,
             'Whether to perform random subsampling with replacement. This can be usefull to ensure balanced class sizes.'),
            (self._SAVE_DATA,
             'Whether to store the training data features (X) and labels (y) inside the model file.'),
            (self._RASTERIZE_POINTS,
             'Whether to rasterize points instead of point-wise reading. Only relevant for point geometries. Line and polygon geometries are always rasterized.'),
            (self._SAVE_AS_JSON,
             f'Whether to additionally store the model as a human-readable JSON sidecar {self.htmlBold("*.pkl.json")} file.'),
            (self._EVAL_TRAIN_PERFORMANCE,
             f'Whether to evaluate the training data performance and store it as a HTML sidecar {self.htmlBold("*.pkl.trainPerformance.html")} file.'),
            (self._EVAL_CROSS_PERFORMANCE,
             f'Specify an integer n to evaluate n-fold cross-validation performance and store it as a HTML sidecar {self.htmlBold("*.pkl.crossPerformance.html")} file.\n'
             f'See {self.htmlLink("https://scikit-learn.org/stable/modules/cross_validation.html#obtaining-predictions-by-cross-validation", "Obtaining predictions by cross-validation")} '
             f'and {self.htmlLink("https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.cross_val_predict.html", ">cross_val_predict")} for further information.'),
            (self._EVAL_PERMUTATION_FEATURE_IMPORTANCE,
             f'Whether to evaluate permutation feature importance and store it as a HTML sidecar {self.htmlBold("*.pkl.permutationFeatureImportance.html")} file.\n'
             f'See {self.htmlLink("https://scikit-learn.org/stable/modules/permutation_importance.html", "Permutation feature importance")} for further information.'),
            (self._COLORIZE_PROBABILITY,
             f'Whether to additionally output a RGB color composite when predicting class probability output and store it as a GeoTiff sidecar {self.htmlBold("*.rgb.tif")} file.'),
            (self._RASTER, self.helpParameterRaster()),
            (self._MASK, self.helpParameterMapMask()),
            (self._MAXIMUM_MEMORY_USAGE, self.helpParameterMaximumMemoryUsage()),
            (self._OUTPUT_CLASSIFICATION,
             f'Specify a raster destination to apply the model and predict classification output for the given raster ({self.htmlBold(self._RASTER)}).'),
            (self._OUTPUT_PROBABILITY,
             f'Specify a raster destination to apply the model and predict class probability output for the given raster ({self.htmlBold(self._RASTER)}).'),
            (self._OUTPUT_CLASSIFIER, 'Output classifier model destination *.pkl file.')
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
        self.addParameterMapLayer(self.P_LABELS, self._LABELS, optional=True)
        self.addParameterRasterLayer(self.P_FEATURES, self._FEATURES, optional=True)
        self.addParameterField(
            self.P_LABELS_FIELD, self._LABELS_FIELD, None, self.P_LABELS,
            QgsProcessingParameterField.Any, optional=True
        )
        self.addParameterField(
            self.P_FEATURE_FIELDS, self._FEATURE_FIELDS, None, self.P_LABELS,
            QgsProcessingParameterField.Any,  # allow any, because CSV fields are always concidered as text
            True, optional=True
        )
        self.addParameterString(self.P_CODE, self._CODE, self.defaultCodeAsString(), True, advanced=True)
        self.addParameterFloat(self.P_SUBSAMPLE_SIZE, self._SUBSAMPLE_SIZE, optional=True, minValue=0, advanced=True)
        self.addParameterBoolean(self.P_SUBSAMPLE_REPLACE, self._SUBSAMPLE_REPLACE, False, advanced=True)
        self.addParameterBoolean(self.P_SAVE_DATA, self._SAVE_DATA, defaultValue=True, advanced=True)
        self.addParameterBoolean(self.P_RASTERIZE_POINTS, self._RASTERIZE_POINTS, defaultValue=False, advanced=True)
        self.addParameterBoolean(self.P_SAVE_AS_JSON, self._SAVE_AS_JSON, False, False, True)
        self.addParameterBoolean(self.P_EVAL_TRAIN_PERFORMANCE, self._EVAL_TRAIN_PERFORMANCE, False, advanced=True)
        self.addParameterInt(self.P_EVAL_CROSS_PERFORMANCE, self._EVAL_CROSS_PERFORMANCE, None, True, 3, 100, True)
        self.addParameterBoolean(
            self.P_EVAL_PERMUTATION_FEATURE_IMPORTANCE, self._EVAL_PERMUTATION_FEATURE_IMPORTANCE, False, advanced=True
        )
        self.addParameterRasterLayer(self.P_RASTER, self._RASTER, optional=True, advanced=True)
        self.addParameterMapLayer(self.P_MASK, self._MASK, optional=True, advanced=True)
        self.addParameterMaximumMemoryUsage(self.P_MAXIMUM_MEMORY_USAGE, advanced=True)

        self.addParameterRasterDestination(
            self.P_OUTPUT_CLASSIFICATION, self._OUTPUT_CLASSIFICATION, None, True, False, True
        )
        self.addParameterRasterDestination(
            self.P_OUTPUT_PROBABILITY, self._OUTPUT_PROBABILITY, None, True, False, True
        )
        self.addParameterFileDestination(
            self.P_OUTPUT_CLASSIFIER, self._OUTPUT_CLASSIFIER, 'Model file (*.pkl)', None, True, True
        )

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

    def checkParameterCode(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        try:
            self.parameterAsClassifier(parameters, self.P_CODE, context)
        except:
            return False, traceback.format_exc()
        return True, ''

    def checkParameterFeatures(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        raster = self.parameterAsRasterLayer(parameters, self.P_FEATURES, context)
        fields = self.parameterAsFields(parameters, self.P_FEATURE_FIELDS, context)

        if raster is None:
            if fields is not None:
                pass  # ok, features are given by attributes
            else:
                filename = self.parameterAsFile(parameters, self.P_CLASSIFICATION, context)
                if filename.endswith('.pkl'):
                    pass  # ok, sample is given by Pickle dump
                elif filename.endswith('.json'):
                    pass  # ok, sample is given by JSON dump
                else:
                    return (
                        False, 'Select either a raster layer (Raster), a list of fields (Features), '
                               'a JSON (*.json) or Pickle (*.pkl) file including (X, y) data, to be used as '
                               'training data features.'
                    )
        if raster is not None and fields is not None:
            if raster.bandCount() != len(fields):
                return False, 'Number of bands (Raster) must match number of selected fields (Feature fields).'
        return True, ''

    def checkParameterLabels(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        filename = self.parameterAsFile(parameters, self.P_CLASSIFICATION, context)
        if filename.endswith('.pkl'):
            return True, ''  # ok, sample is given by Pickle dump
        elif filename.endswith('.json'):
            return True, ''  # ok, sample is given by JSON dump
        else:
            valid, _ = self.checkParameterMapClassification(parameters, self.P_CLASSIFICATION, context)
            if valid:
                return True, ''
        return (
            False, 'Select either a categorized raster/vector layer, or a JSON (*.json) or Pickle (*.pkl) file '
                   'including (X, y) data, to be used as training data labels.'
        )

    def checkParameterRaster(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        if self.parameterAsRasterLayer(parameters, self.P_FEATURES, context) is None:
            if self.parameterAsFileOutput(parameters, self.P_OUTPUT_CLASSIFICATION, context) is not None:
                return False, 'Missing parameter value: (Raster)'
            if self.parameterAsFileOutput(parameters, self.P_OUTPUT_PROBABILITY, context) is not None:
                return False, 'Missing parameter value: (Raster)'
        return True, ''

    def checkParameterValues(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        checks = [
            self.checkParameterRaster(parameters, context),
            self.checkParameterLabels(parameters, context),
            self.checkParameterFeatures(parameters, context),
            self.checkParameterCode(parameters, context)
        ]
        for valid, message in checks:
            if not valid:
                return valid, message
        return super().checkParameterValues()

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        evalPermutationFeatureImportance = self.parameterAsBoolean(
            parameters, self.P_EVAL_PERMUTATION_FEATURE_IMPORTANCE, context
        )
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_CLASSIFIER, context)
        classifier = self.parameterAsClassifier(parameters, self.P_CODE, context)

        with open(filename + '.log', 'w') as logfile:
            feedback, feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(feedback, parameters, context)

            if evalPermutationFeatureImportance:
                from sklearn.inspection import permutation_importance
                feedback.pushInfo('Evaluate permutation feature importance')
                r = permutation_importance(classifier, X, y.ravel(), n_repeats=10, random_state=0)
                ordered = r.importances_mean.argsort()[::-1]
                values = np.array([r.importances_mean[ordered], r.importances_std[ordered]]).T.round(4).tolist()

                with \
                        open(filename + '.permutationFeatureImportance.html', 'w') as fileHtml, \
                        open(filename + '.permutationFeatureImportance.csv', 'w') as fileCsv:
                    report = MultiReportWriter([HtmlReportWriter(fileHtml), CsvReportWriter(fileCsv)])
                    report.writeHeader('Permutation feature importances')
                    report.writeTable(
                        values,
                        'Permutation feature importance over 10 repeats',
                        ['Mean', 'standard deviation'],
                        np.array(featureNames)[ordered].tolist(),
                    )

            if not saveData:
                X = y = None

            dump = ClassifierDump(classifier=classifier, categories=categories, features=featureNames, X=X, y=y)
            dumpDict = dump._asdict()
            Utils.pickleDump(dumpDict, filename)
            result = {self.P_OUTPUT_CLASSIFIER: filename}

            if dumpAsJson:
                Utils.jsonDump(dumpDict, filename + '.json')

            self.toc(feedback, result)

        return result
