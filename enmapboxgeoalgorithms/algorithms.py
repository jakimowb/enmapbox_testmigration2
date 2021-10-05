from tempfile import gettempdir

from enmapboxgeoalgorithms.estimators import parseClusterers, parseRegressors, parseTransformers
from enmapboxgeoalgorithms.provider import (EnMAPAlgorithm, EnMAPAlgorithmParameterValueError, Cookbook,
                                            ALGORITHMS)
from enmapboxprocessing.algorithm.algorithms import algorithms
from hubdsm.processing.aggregatebands import AggregateBands
from hubdsm.processing.changemap import ChangeMap
from hubdsm.processing.classificationstatistics import ClassificationStatistics
from hubdsm.processing.saveasenvi import SaveAsEnvi
from hubdsm.processing.savelayerasclassification import SaveLayerAsClassification
from hubdsm.processing.uniquebandvaluecounts import UniqueBandValueCounts
from hubflow.core import *

ALGORITHMS.append(UniqueBandValueCounts())
ALGORITHMS.append(SaveLayerAsClassification())
ALGORITHMS.append(AggregateBands())
ALGORITHMS.append(ClassificationStatistics())
ALGORITHMS.append(SaveAsEnvi())
# ALGORITHMS.append(ChangeMap())  # outdated in v3.9, needs to overhauled

ALGORITHMS.extend(algorithms())


class ClassificationFromFraction(EnMAPAlgorithm):
    def displayName(self):
        return 'Classification from Fraction'

    def description(self):
        return 'Creates classification from class fraction. Winner class is equal to the class with maximum class fraction.'

    def group(self):
        return self.GROUP_CREATE_RASTER

    def defineCharacteristics(self):
        self.addParameterFraction()
        self.addParameterMinCoverages()
        self.addParameterOutputClassification()

    def processAlgorithm_(self):
        fraction = self.getParameterFraction(minOverallCoverage=self.getParameterMinOverallCoverage(),
                                             minDominantCoverage=self.getParameterMinDominantCoverage())
        filename = self.getParameterOutputClassification()
        Classification.fromClassification(filename=filename, classification=fraction, progressBar=self._progressBar)
        return {self.P_OUTPUT_CLASSIFICATION: filename}


ALGORITHMS.append(ClassificationFromFraction())


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


class ClustererFit(EstimatorFit):
    def group(self):
        return self.GROUP_CLUSTERING

    def cookbookRecipes(self):
        return [Cookbook.R_CLUSTERING]

    def cookbookDescription(self):
        return 'See the following Cookbook Recipes on how to use clusterers:'

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterMask()
        self.addParameterCode()
        self.addParameterOutputClusterer(name=self.P_OUTPUT_ESTIMATOR)

    def sample(self):
        return Sample(raster=self.getParameterRaster(), mask=self.getParameterMask())

    def estimator(self, sklEstimator):
        return Clusterer(sklEstimator=sklEstimator)


for name, (code, helpAlg, helpCode, postCode) in parseClusterers().items():
    ALGORITHMS.append(ClustererFit(name=name, code=code, helpAlg=helpAlg, helpCode=helpCode, postCode=postCode))


class ClustererPredict(EnMAPAlgorithm):
    def displayName(self):
        return 'Predict Clustering'

    def description(self):
        return 'Applies a clusterer to a raster.'

    def group(self):
        return self.GROUP_CLUSTERING

    def defineCharacteristics(self):
        self.addParameterRaster(help='Select raster file which should be clustered.')
        self.addParameterMask()
        self.addParameterClusterer()
        self.addParameterOutputClassification(description='Clustering')

    def cookbookRecipes(self):
        return [Cookbook.R_CLUSTERING]

    def processAlgorithm_(self):
        estimator = self.getParameterClusterer()
        raster = self.getParameterRaster()
        mask = self.getParameterMask()
        filename = self.getParameterOutputClassification()
        estimator.predict(filename=filename, raster=raster, mask=mask, progressBar=self._progressBar)
        return {self.P_OUTPUT_CLASSIFICATION: filename}


ALGORITHMS.append(ClustererPredict())


class ClusteringPerformanceFromRaster(EnMAPAlgorithm):
    def displayName(self):
        return 'Clustering Performance'

    def description(self):
        return 'Assesses the performance of a clusterer.'

    def group(self):
        return self.GROUP_ACCURACY_ASSESSMENT

    P_PREDICTION = 'prediction'
    P_REFERENCE = 'reference'

    def defineCharacteristics(self):
        self.addParameterClassification(self.P_PREDICTION, 'Prediction',
                                        help='Specify clustering raster to be evaluated.')
        self.addParameterClassification(self.P_REFERENCE, 'Reference',
                                        help='Specify reference clustering raster (i.e. ground truth).')
        self.addParameterOutputReport()

    def processAlgorithm_(self):
        prediction = self.getParameterClassification(self.P_PREDICTION)
        reference = self.getParameterClassification(self.P_REFERENCE)
        if not prediction.grid().equal(reference.grid()):
            raise EnMAPAlgorithmParameterValueError('prediction and reference grid must match')

        performance = ClusteringPerformance.fromRaster(prediction=prediction, reference=reference,
                                                       progressBar=self._progressBar,
                                                       grid=prediction.grid())
        filename = self.getParameterOutputReport()
        performance.report().saveHTML(filename=filename, open=True)
        return {self.P_OUTPUT_REPORT: filename}


ALGORITHMS.append(ClusteringPerformanceFromRaster())


class FractionFromVectorClassification(EnMAPAlgorithm):
    def displayName(self):
        return 'Fraction from Vector'

    def description(self):
        return 'Derives class fraction raster from a vector file with sufficient class information. ' \
               'Note: rasterization of complex multipart vector geometries can be very slow, use "QGIS > Vector > Geometry Tools > Multiparts to Singleparts..." in this case beforehand.'

    def group(self):
        return self.GROUP_CREATE_RASTER

    def defineCharacteristics(self):
        self.addParameterGrid()
        self.addParameterVectorClassification(minCoveragesDefaultValues=(0.5, 0.5), hideMinDominantCoverage=True,
                                              oversamplingDefaultValue=5)
        self.addParameterOutputFraction()

    def processAlgorithm_(self):
        filename = self.getParameterOutputFraction()
        Fraction.fromClassification(filename=filename,
                                    classification=self.getParameterVectorClassification(),
                                    grid=self.getParameterGrid(),
                                    oversampling=self.getParameterOversampling(),
                                    progressBar=self._progressBar)
        return {self.P_OUTPUT_FRACTION: filename}


ALGORITHMS.append(FractionFromVectorClassification())


class FractionPerformanceFromRaster(EnMAPAlgorithm):
    def displayName(self):
        return 'ROC Curve and AUC Performance'

    def description(self):
        return 'Assesses the performance of class fractions in terms of AUC and ROC curves.'

    def group(self):
        return self.GROUP_ACCURACY_ASSESSMENT

    P_PREDICTION = 'prediction'
    P_REFERENCE = 'reference'

    def defineCharacteristics(self):
        self.addParameterRaster(self.P_PREDICTION, 'Prediction',
                                help='Specify class fraction raster to be evaluated.')
        self.addParameterRaster(self.P_REFERENCE, 'Reference',
                                help='Specify reference classification raster (i.e. ground truth).')
        self.addParameterOutputReport()

    def processAlgorithm_(self):
        prediction = self.getParameterFraction('prediction')
        reference = self.getParameterClassification('reference')
        if not prediction.grid().equal(reference.grid()):
            raise EnMAPAlgorithmParameterValueError('prediction and reference grid must match')
        performance = FractionPerformance.fromRaster(prediction=prediction, reference=reference,
                                                     progressBar=self._progressBar)
        filename = self.getParameterOutputReport()
        performance.report().saveHTML(filename=filename, open=True)
        return {self.P_OUTPUT_REPORT: filename}


ALGORITHMS.append(FractionPerformanceFromRaster())


class RasterApplySpatial(EnMAPAlgorithm):
    def __init__(self, name, name2, code, helpAlg, helpCode, postCode):
        self._name = name
        self._name2 = name2
        self._code = code
        self._helpAlg = helpAlg
        self._helpCode = helpCode
        self._postCode = postCode
        super().__init__()

    def description(self):
        return self._helpAlg

    def group(self):
        return self.GROUP_CONVOLUTION

    def createInstance(self):
        return type(self)(name=self._name, name2=self._name2, code=self._code, helpAlg=self._helpAlg,
                          helpCode=self._helpCode, postCode=self._postCode)

    def displayName(self):
        name = self._name.title().replace('_', ' ')
        return 'Spatial {} {}'.format(self._name2, name)

    def code(self):
        return self._code

    P_CODE = 'code'

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterString(self.P_CODE, 'Code', defaultValue=self._code, multiLine=True, help=self._helpCode)
        self.addParameterOutputRaster()

    def function(self):
        namespace = dict()
        code = self.getParameterString(self.P_CODE)
        exec(code, namespace)
        assert 'function' in namespace
        return namespace['function']

    def processAlgorithm_(self):
        function = self.function()
        raster = self.getParameterRaster()
        outraster = raster.applySpatial(filename=self.getParameterOutputRaster(),
                                        function=function)
        return {self.P_OUTPUT_RASTER: outraster.filename()}

    def cookbookRecipes(self):
        return [Cookbook.R_FILTERING, Cookbook.R_GENERICFILTER]

    def cookbookDescription(self):
        return 'See the following Cookbook Recipes on how to apply filters:'


class RasterUniqueValues(EnMAPAlgorithm):
    def displayName(self):
        return 'Unique Values from Raster'

    def description(self):
        return 'This algorithm returns unique values from a raster band as a list. The output will be shown in the log window and can the copied from there accordingly.'

    def group(self):
        return self.GROUP_AUXILLIARY

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterBand(optional=True, defaultValue=0)

    def processAlgorithm_(self):
        raster = self.getParameterRaster()
        band = self.getParameterBand()
        if band < 1:
            indices = range(raster.dataset().zsize())
        else:
            indices = [band - 1]

        for index in indices:
            values = raster.uniqueValues(index=index)
            self._progressBar.setText('Band {} unique values: {}'.format(index + 1, ', '.join(map(str, values))))

        return {}


ALGORITHMS.append(RasterUniqueValues())


class RasterSetNoDataValue(EnMAPAlgorithm):
    def displayName(self):
        return 'Set Raster no data value'

    def description(self):
        return 'Set the raster no data value. Note that the raster has to be re-opened.'

    def group(self):
        return self.GROUP_AUXILLIARY

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterFloat(description='No data value', help='Value used as the new raster no data value.')

    def processAlgorithm_(self):
        raster = self.getParameterRaster()
        raster.dataset().setNoDataValue(value=self.getParameterFloat())
        return {}


ALGORITHMS.append(RasterSetNoDataValue())


class RasterStatistics(EnMAPAlgorithm):
    def displayName(self):
        return 'Raster Band Statistics'

    def description(self):
        return 'This algorithm returns raster band statistics. The output will be shown in the log window and can the copied from there accordingly.'

    def group(self):
        return self.GROUP_AUXILLIARY

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterBand(optional=True)

    def processAlgorithm_(self):
        raster = self.getParameterRaster()
        if self.getParameterBand() is None:
            indices = list(range(raster.dataset().zsize()))
        else:
            indices = [self.getParameterBand() - 1]
        for index in indices:
            values = raster.statistics(bandIndices=[index],
                                       calcPercentiles=True, calcHistogram=True, calcMean=True, calcStd=True,
                                       percentiles=[25, 50, 75])[0]

            self._progressBar.setText('Band {}: {}'.format(index + 1, raster.dataset().band(index).description()))
            self._progressBar.setText('Min: {}'.format(values.min))
            self._progressBar.setText('Max: {}'.format(values.max))
            self._progressBar.setText('Mean: {}'.format(values.mean))
            self._progressBar.setText('StdDev: {}'.format(values.std))
            self._progressBar.setText('p25: {}'.format(values.percentiles[0].value))
            self._progressBar.setText('median: {}'.format(values.percentiles[1].value))
            self._progressBar.setText('p75: {}'.format(values.percentiles[2].value))
            self._progressBar.setText('')

        return {}


ALGORITHMS.append(RasterStatistics())


class MapViewMetadata(EnMAPAlgorithm):
    def displayName(self):
        return 'View Map Metadata'

    def description(self):
        return 'Prints all Map metadata to log.'

    def group(self):
        return self.GROUP_AUXILLIARY

    def defineCharacteristics(self):
        self.addParameterMap()

    def processAlgorithm_(self):
        map = self.getParameterMap()

        domainName = lambda key: key if key != '' else '<default>'

        if isinstance(map, Raster):
            for key, value in map.dataset().metadataDict().items():
                self._progressBar.setText(text='\n===============\nDataset Domain: {}'.format(domainName(key)))
                for k, v in value.items():
                    self._progressBar.setText(text='{} = {}'.format(k, v))
            for i, band in enumerate(map.dataset().bands()):
                for key, value in band.metadataDict().items():
                    self._progressBar.setText(
                        text='\n===============\nBand {} Domain: {}'.format(i + 1, domainName(key)))
                    for k, v in value.items():
                        self._progressBar.setText(text='{} = {}'.format(k, v))
        elif isinstance(map, Vector):
            for key, value in map.dataset().metadataDict().items():
                self._progressBar.setText(text='\n===============\nLayer Domain: {}'.format(domainName(key)))
                for k, v in value.items():
                    self._progressBar.setText(text='{} = {}'.format(k, v))

        else:
            assert 0
        return {}


ALGORITHMS.append(MapViewMetadata())


class RegressionFromVectorRegression(EnMAPAlgorithm):
    def group(self): return self.GROUP_CREATE_RASTER

    def displayName(self): return 'Regression from Vector'

    def description(self):
        return 'Creates a regression from a vector field with target values.'

    def defineCharacteristics(self):
        self.addParameterGrid()
        self.addParameterVectorRegression()
        self.addParameterOutputRegression()

    def processAlgorithm_(self):
        regression = Regression.fromVectorRegression(filename=self.getParameterOutputRegression(),
                                                     vectorRegression=self.getParameterVectorRegression(),
                                                     grid=self.getParameterGrid(),
                                                     progressBar=self._progressBar)
        return {self.P_OUTPUT_REGRESSION: regression.filename()}


ALGORITHMS.append(RegressionFromVectorRegression())


class RegressionPerformanceFromRaster(EnMAPAlgorithm):
    def displayName(self):
        return 'Regression Performance'

    def description(self):
        return 'Assesses the performance of a regression.'

    def group(self):
        return 'Accuracy Assessment'

    P_PREDICTION = 'prediction'
    P_REFERENCE = 'reference'

    def defineCharacteristics(self):
        self.addParameterRegression(self.P_PREDICTION, 'Prediction',
                                    help='Specify regression raster to be evaluated.')
        self.addParameterRegression(self.P_REFERENCE, 'Reference',
                                    help='Specify reference regression raster (i.e. ground truth).')
        self.addParameterInvertableMask()
        self.addParameterOutputReport()

    def processAlgorithm_(self):
        prediction = self.getParameterRegression(self.P_PREDICTION)
        reference = self.getParameterRegression(self.P_REFERENCE)
        mask = self.getParameterInvertableMask()
        if not prediction.grid().equal(reference.grid()):
            raise EnMAPAlgorithmParameterValueError('prediction and reference grid must match')
        performance = RegressionPerformance.fromRaster(prediction=prediction, reference=reference, mask=mask,
                                                       grid=prediction.grid(),
                                                       progressBar=self._progressBar)

        filename = self.getParameterOutputReport()
        performance.report().saveHTML(filename=filename, open=True)
        return {self.P_OUTPUT_REPORT: filename}


ALGORITHMS.append(RegressionPerformanceFromRaster())


class RegressorPerformanceCrossValidation(EnMAPAlgorithm):
    def displayName(self):
        return 'Cross-validated Regressor Performance'

    def description(self):
        return 'Assesses the performance of a regressor using n-fold cross-validation.'

    def group(self):
        return 'Accuracy Assessment'

    P_NFOLD = 'nfold'

    def defineCharacteristics(self):
        self.addParameterRegressor()
        self.addParameterInteger(name=self.P_NFOLD, description='Number of folds', minValue=2, maxValue=100,
                                 defaultValue=10)
        self.addParameterOutputReport()

    def processAlgorithm_(self):
        regressor = self.getParameterRegressor()
        nfold = self.getParameterInteger(name=self.P_NFOLD)
        performance = regressor.performanceCrossValidation(nfold=nfold)
        filename = self.getParameterOutputReport()
        performance.report().saveHTML(filename=filename, open=True)
        return {self.P_OUTPUT_REPORT: filename}


ALGORITHMS.append(RegressorPerformanceCrossValidation())


class RegressorPerformanceTraining(EnMAPAlgorithm):
    def displayName(self):
        return 'Regressor Fit/Training Performance'

    def description(self):
        return 'Assesses the fit performance of a regressor using the training data.'

    def group(self):
        return 'Accuracy Assessment'

    def defineCharacteristics(self):
        self.addParameterRegressor()
        self.addParameterOutputReport()

    def processAlgorithm_(self):
        regressor = self.getParameterRegressor()
        performance = regressor.performanceTraining()
        filename = self.getParameterOutputReport()
        performance.report().saveHTML(filename=filename, open=True)
        return {self.P_OUTPUT_REPORT: filename}


ALGORITHMS.append(RegressorPerformanceTraining())


class RegressorFit(EstimatorFit):
    def group(self):
        return self.GROUP_REGRESSION

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterRegression()
        self.addParameterMask()
        self.addParameterCode()
        self.addParameterOutputRegressor(self.P_OUTPUT_ESTIMATOR)

    def sample(self):
        return RegressionSample(raster=self.getParameterRaster(),
                                regression=self.getParameterRegression(),
                                mask=self.getParameterMask())

    def estimator(self, sklEstimator):
        return Regressor(sklEstimator=sklEstimator)

    def cookbookRecipes(self):
        return [Cookbook.R_REGRESSION]

    def cookbookDescription(self):
        return 'See the following Cookbook Recipes on how to use regressors:'


for name, (code, helpAlg, helpCode, postCode) in parseRegressors().items():
    ALGORITHMS.append(RegressorFit(name=name, code=code, helpAlg=helpAlg, helpCode=helpCode, postCode=postCode))


class RegressorPredict(EnMAPAlgorithm):
    def displayName(self):
        return 'Predict Regression'

    def group(self):
        return self.GROUP_REGRESSION

    def description(self):
        return 'Applies a regressor to an raster.'

    def defineCharacteristics(self):
        self.addParameterRaster(help='Select raster file which should be regressed.')
        self.addParameterMask()
        self.addParameterRegressor()
        self.addParameterOutputRegression()

    def processAlgorithm_(self):
        estimator = self.getParameterRegressor()
        raster = self.getParameterRaster()
        mask = self.getParameterMask()
        filename = self.getParameterOutputRegression()
        estimator.predict(filename=filename, raster=raster, mask=mask, progressBar=self._progressBar)
        return {self.P_OUTPUT_REGRESSION: filename}

    def cookbookRecipes(self):
        return [Cookbook.R_REGRESSION]


ALGORITHMS.append(RegressorPredict())


class TransformerFit(EstimatorFit):
    def group(self):
        return self.GROUP_TRANSFORMATION

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterMask()
        self.addParameterCode()
        self.addParameterOutputTransformer(name=self.P_OUTPUT_ESTIMATOR)

    def sample(self):
        return Sample(raster=self.getParameterRaster(),
                      mask=self.getParameterMask())

    def estimator(self, sklEstimator):
        return Transformer(sklEstimator=sklEstimator)

    def cookbookRecipes(self):
        return [Cookbook.R_TRANSFORMATION]

    def cookbookDescription(self):
        return 'See the following Cookbook Recipes on how to use transformers:'


for name, (code, helpAlg, helpCode, postCode) in parseTransformers().items():
    ALGORITHMS.append(TransformerFit(name=name, code=code, helpAlg=helpAlg, helpCode=helpCode, postCode=postCode))


class TransformerTransform(EnMAPAlgorithm):
    def displayName(self):
        return 'Transform Raster'

    def group(self):
        return self.GROUP_TRANSFORMATION

    def description(self):
        return 'Applies a transformer to an raster.'

    def defineCharacteristics(self):
        self.addParameterRaster(help='Select raster file which should be regressed.')
        self.addParameterMask()
        self.addParameterTransformer()
        self.addParameterOutputRaster(description='Transformation')

    def processAlgorithm_(self):
        estimator = self.getParameterTransformer()
        raster = self.getParameterRaster()
        mask = self.getParameterMask()
        filename = self.getParameterOutputRaster()
        estimator.transform(filename=filename, raster=raster, mask=mask, progressBar=self._progressBar)
        return {self.P_OUTPUT_RASTER: filename}

    def cookbookRecipes(self):
        return [Cookbook.R_TRANSFORMATION]


ALGORITHMS.append(TransformerTransform())


class TransformerInverseTransform(EnMAPAlgorithm):
    def displayName(self):
        return 'InverseTransform Raster'

    def description(self):
        return "Performs an inverse transformation on an previously transformed raster (i.e. output of 'Transformation -> Transform Raster'). " \
               "Works only for transformers that have an 'inverse_transform(X)' method. See scikit-learn documentations."

    def group(self):
        return self.GROUP_TRANSFORMATION

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterMask()
        self.addParameterTransformer()
        self.addParameterOutputRaster(description='Inverse Transformation')

    def processAlgorithm_(self):
        estimator = self.getParameterTransformer()
        raster = self.getParameterRaster()
        mask = self.getParameterMask()
        filename = self.getParameterOutputRaster()
        estimator.inverseTransform(filename=filename, raster=raster, mask=mask, progressBar=self._progressBar)
        return {self.P_OUTPUT_RASTER: filename}


ALGORITHMS.append(TransformerInverseTransform())


class VectorFromRandomPointsFromClassification(EnMAPAlgorithm):
    def displayName(self):
        return 'Random Points from Classification'

    def description(self):
        return 'Randomly samples a user defined amount of points/pixels from a classification raster and returns them as a vector dataset.'

    def group(self):
        return self.GROUP_RANDOM

    def defineCharacteristics(self):
        self.addParameterClassification()
        self.addParameterNumberOfPointsPerClass()
        self.addParameterOutputVector()

    def processAlgorithm_(self):
        classification = self.getParameterClassification()

        def funcClassTotals():
            counts = classification.statistics()
            return counts

        n = self.getParameterNumberOfPointsPerClass(classes=classification.classDefinition().classes(),
                                                    funcClassTotals=funcClassTotals)
        filename = self.getParameterOutputVector()
        Vector.fromRandomPointsFromClassification(filename=filename, classification=classification, n=n,
                                                  progressBar=self._progressBar)
        return {self.P_OUTPUT_VECTOR: filename}


ALGORITHMS.append(VectorFromRandomPointsFromClassification())


class VectorFromRandomPointsFromMask(EnMAPAlgorithm):
    def displayName(self):
        return 'Random Points from Mask'

    def description(self):
        return 'Randomly draws defined number of points from Mask and returns them as vector dataset.'

    def group(self):
        return self.GROUP_RANDOM

    P_N = 'n'

    def defineCharacteristics(self):
        self.addParameterInvertableMask(allowVector=False, optional=False)
        self.addParameterNumberOfPoints(defaultValue=100)
        self.addParameterOutputVector()

    def processAlgorithm_(self):
        filename = self.getParameterOutputVector()
        mask = self.getParameterInvertableMask()

        def funcTotal():
            array = mask.array()
            return np.sum(array)

        Vector.fromRandomPointsFromMask(filename=filename,
                                        mask=mask, n=self.getParameterNumberOfPoints(funcTotal=funcTotal),
                                        progressBar=self._progressBar)
        return {self.P_OUTPUT_VECTOR: filename}


ALGORITHMS.append(VectorFromRandomPointsFromMask())


class VectorUniqueValues(EnMAPAlgorithm):
    def displayName(self):
        return 'Unique Values from Vector Attribute '

    def description(self):
        return 'This algorithm returns unique values from vector attributes as a list, which is also usable as Class Definition in other algorithms. The output will be shown in the log window and can the copied from there accordingly.'

    def group(self):
        return self.GROUP_AUXILLIARY

    def defineCharacteristics(self):
        self.addParameterVector()
        self.addParameterField()

    def processAlgorithm_(self):
        vector = self.getParameterVector()
        values = vector.uniqueValues(attribute=self.getParameterField())
        self._progressBar.setText('Unique value: {}'.format(repr(values)))
        return {}


ALGORITHMS.append(VectorUniqueValues())


class ExtractSamples(EnMAPAlgorithm):
    def displayName(self):
        return 'Extract samples from raster and mask'

    def description(self):
        return 'Extract samples from raster and mask.'

    def group(self): return self.GROUP_CREATE_SAMPLE

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterInvertableMask()
        self.addParameterOutputRaster()

    def processAlgorithm_(self):
        sample = Sample(raster=self.getParameterRaster(),
                        mask=self.getParameterInvertableMask())
        outraster, = sample.extractAsRaster(filenames=[self.getParameterOutputRaster()], progressBar=self._progressBar)
        return {self.P_OUTPUT_RASTER: outraster.filename()}


ALGORITHMS.append(ExtractSamples())


class ExtractClassificationSamples(EnMAPAlgorithm):
    def displayName(self):
        return 'Extract classification samples from raster and classification'

    def description(self):
        return 'Extract classification samples from raster and classification.'

    def group(self): return self.GROUP_CREATE_SAMPLE

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterClassification()
        self.addParameterInvertableMask()
        self.addParameterOutputRaster()
        self.addParameterOutputClassification()

    def processAlgorithm_(self):
        sample = ClassificationSample(raster=self.getParameterRaster(),
                                      classification=self.getParameterClassification(),
                                      mask=self.getParameterInvertableMask())
        outraster, outclassification = sample.extractAsRaster(filenames=[self.getParameterOutputRaster(),
                                                                         self.getParameterOutputClassification()],
                                                              progressBar=self._progressBar)
        return {self.P_OUTPUT_RASTER: outraster.filename(),
                self.P_OUTPUT_CLASSIFICATION: outclassification.filename()}


ALGORITHMS.append(ExtractClassificationSamples())


class ExtractRegressionSamples(EnMAPAlgorithm):
    def displayName(self):
        return 'Extract regression samples from raster and regression'

    def description(self):
        return 'Extract regression samples from raster and regression.'

    def group(self): return self.GROUP_CREATE_SAMPLE

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterRegression()
        self.addParameterInvertableMask()
        self.addParameterOutputRaster()
        self.addParameterOutputRegression()

    def processAlgorithm_(self):
        sample = RegressionSample(raster=self.getParameterRaster(),
                                  regression=self.getParameterRegression(),
                                  mask=self.getParameterInvertableMask())
        outraster, outregression = sample.extractAsRaster(filenames=[self.getParameterOutputRaster(),
                                                                     self.getParameterOutputRegression()],
                                                          progressBar=self._progressBar)
        return {self.P_OUTPUT_RASTER: outraster.filename(),
                self.P_OUTPUT_REGRESSION: outregression.filename()}


ALGORITHMS.append(ExtractRegressionSamples())


class ExtractFractionSamples(EnMAPAlgorithm):
    def displayName(self):
        return 'Extract fraction samples from raster and fraction'

    def description(self):
        return 'Extract fraction samples from raster and fraction.'

    def group(self): return self.GROUP_CREATE_SAMPLE

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterFraction()
        self.addParameterInvertableMask()
        self.addParameterOutputRaster()
        self.addParameterOutputFraction()

    def processAlgorithm_(self):
        sample = FractionSample(raster=self.getParameterRaster(),
                                fraction=self.getParameterFraction(),
                                mask=self.getParameterInvertableMask())
        outraster, outfraction = sample.extractAsRaster(filenames=[self.getParameterOutputRaster(),
                                                                   self.getParameterOutputFraction()],
                                                        progressBar=self._progressBar)
        return {self.P_OUTPUT_RASTER: outraster.filename(),
                self.P_OUTPUT_FRACTION: outfraction.filename()}


ALGORITHMS.append(ExtractFractionSamples())


class ExtractOrdinationFeilhauerEtAll2014(EnMAPAlgorithm):

    def displayName(self):
        return 'Extract ordination sample'

    def description(self):
        return 'Extract a regression samples where the regression labels are ordinated. See {} for details.'.format(
            r'http://dx.doi.org/10.1111/avsc.12115')

    def group(self): return self.GROUP_CREATE_SAMPLE

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterVector()
        self.addParameterOutputRaster()
        self.addParameterOutputRegression()
        self.addParameterOutputVector(description='Vector for DataPlotly')

    def processAlgorithm_(self):
        raster = self.getParameterRaster()
        plots = self.getParameterVector()
        outraster, species = plots.extractPixel(raster=raster,
                                                filenameRaster=self.getParameterOutputRaster(),
                                                filenameRegression='/vsimem/ExtractOrdinationFeilhauerEtAll2014/regression.bsq')

        outregression, outvector, explainedVariance = species.ordinationFeilhauerEtAl2014(
            filename=self.getParameterOutputRegression(),
            filenameVector=self.getParameterOutputVector())
        self._progressBar.setText('Explained variance:\n{}'.format(repr(explainedVariance)))
        gdal.Unlink(species.filename())

        return {self.P_OUTPUT_RASTER: outraster.filename(),
                self.P_OUTPUT_REGRESSION: outregression.filename(),
                self.P_OUTPUT_VECTOR: outvector.filename(),
                }


ALGORITHMS.append(ExtractOrdinationFeilhauerEtAll2014())


class DecorrelationStretch(EnMAPAlgorithm):
    def displayName(self):
        return 'Decorrelation Stretch'

    def description(self):
        return 'This algorithm applies decorrelation stretching (aka detrended stretching) to 3 selected bands for enhanced display as a trichromatic composite.'

    def group(self):
        return self.GROUP_POSTPROCESSING

    P_RED = 'redBand'
    P_GREEN = 'greenBand'
    P_BLUE = 'blueBand'

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterBand(self.P_RED, description='Red Band')
        self.addParameterBand(self.P_GREEN, description='Green Band')
        self.addParameterBand(self.P_BLUE, description='Blue Band')
        self.addParameterOutputRaster()

    def processAlgorithm_(self):
        raster = self.getParameterRaster()
        indices = [self.getParameterBand(name) - 1 for name in [self.P_RED, self.P_GREEN, self.P_BLUE]]
        filename = self.getParameterOutputRaster()

        from sklearn.decomposition import PCA
        from sklearn.preprocessing import RobustScaler
        from hubflow.core import Transformer, Sample

        tmpfilenames = list([join(gettempdir(), 'DecorrelationStretch', 'subset.vrt')])
        subset = raster.subsetBands(filename=tmpfilenames[-1], indices=indices)
        pca = Transformer(PCA(n_components=3))
        pca.fit(sample=Sample(raster=subset))
        tmpfilenames.append(join(gettempdir(), 'DecorrelationStretch', 'pc.bsq'))
        pcRaster = pca.transform(filename=tmpfilenames[1], raster=subset)
        scaler = Transformer(RobustScaler(quantile_range=(2, 98)))
        scaler.fit(sample=Sample(raster=pcRaster))
        tmpfilenames.append(join(gettempdir(), 'DecorrelationStretch', 'pcRasterStretched.bsq'))
        pcRasterStretched = scaler.transform(filename=tmpfilenames[-1], raster=pcRaster)
        pca.inverseTransform(filename=filename, raster=pcRasterStretched)
        return {self.P_OUTPUT_RASTER: filename}


ALGORITHMS.append(DecorrelationStretch())
