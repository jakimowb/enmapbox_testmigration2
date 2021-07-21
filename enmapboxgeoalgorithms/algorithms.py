from shutil import rmtree
from tempfile import gettempdir

from qgis.core import *

from enmapbox.externals.qps.speclib import EnviSpectralLibraryIO

from enmapboxprocessing.algorithm.algorithms import algorithms
from hubdsm.processing.aggregatebands import AggregateBands
from hubdsm.processing.changemap import ChangeMap
from hubdsm.processing.classificationstatistics import ClassificationStatistics
from hubdsm.processing.importdesisl2a import ImportDesisL2A
from hubdsm.processing.importprismal2d import ImportPrismaL2D
from hubdsm.processing.saveasenvi import SaveAsEnvi
from hubdsm.processing.subsetrasterbands import SubsetRasterBands
from hubdsm.processing.importenmapl1b import ImportEnmapL1B
from hubdsm.processing.importenmapl1c import ImportEnmapL1C
from hubdsm.processing.importenmapl2a import ImportEnmapL2A
from hubdsm.processing.uniquebandvaluecounts import UniqueBandValueCounts
from hubdsm.processing.savelayerasclassification import SaveLayerAsClassification

from hubflow.core import *
from enmapboxgeoalgorithms.provider import (EnMAPAlgorithm, EnMAPAlgorithmParameterValueError, Help, Link, Cookbook,
                                            ALGORITHMS)
from enmapboxgeoalgorithms.estimators import parseClassifiers, parseClusterers, parseRegressors, parseTransformers

ALGORITHMS.append(UniqueBandValueCounts())
ALGORITHMS.append(ImportEnmapL1B())
ALGORITHMS.append(ImportEnmapL1C())
ALGORITHMS.append(ImportEnmapL2A())
ALGORITHMS.append(ImportPrismaL2D())
ALGORITHMS.append(ImportDesisL2A())
ALGORITHMS.append(SaveLayerAsClassification())
ALGORITHMS.append(SubsetRasterBands())
ALGORITHMS.append(AggregateBands())
ALGORITHMS.append(ClassificationStatistics())
ALGORITHMS.append(SaveAsEnvi())
ALGORITHMS.append(ChangeMap())

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


# todo
class CreateGrid(EnMAPAlgorithm):
    def displayName(self):
        return 'Create Pixel Grid'

    def description(self):
        return 'Create an pixel grid, i.e. empty raster from given extent, resolution and projection.'

    def group(self):
        return self.GROUP_AUXILLIARY

    P_PROJECTION = 'projection'
    P_EXTENT = 'extent'

    def defineCharacteristics(self):
        #        self.addParameter(QgsProcessingParameterCrs(name=self.P_PROJECTION, description='Projection', optional=False))
        #        self.addParameter(QgsProcessingParameterExtent(name=self.P_EXTENT, description='Extent'))#, optional=False))
        self.addParameterFloat()
        self.addParameterOutputRaster()

    def processAlgorithm_(self):
        assert 0
        filename = Raster.fromArray()
        return {self.P_OUTPUT_CLASSIFICATION: filename}


# ALGORITHMS.append(CreateGrid())


class CreateTestClassification(EnMAPAlgorithm):
    def displayName(self):
        return 'Create Test Classification Map'

    def description(self):
        return 'Create a classification map at 30 m resolution by rasterizing the landcover polygons.'

    def group(self):
        return self.GROUP_TESTDATA

    def defineCharacteristics(self):
        self.addParameterOutputClassification()

    def processAlgorithm_(self):
        import enmapboxtestdata
        filename = enmapboxtestdata.createClassification(filename=self.getParameterOutputClassification(),
            gridOrResolution=Raster(enmapboxtestdata.enmap).grid())
        return {self.P_OUTPUT_CLASSIFICATION: filename}


ALGORITHMS.append(CreateTestClassification())


class CreateTestFraction(EnMAPAlgorithm):
    def displayName(self):
        return 'Create Test Fraction Map'

    def description(self):
        return 'Create a fraction map at 30 m resolution by rasterizing the landcover polygons.'

    def group(self):
        return self.GROUP_TESTDATA

    def defineCharacteristics(self):
        self.addParameterOutputFraction()

    def processAlgorithm_(self):
        import enmapboxtestdata
        filename = enmapboxtestdata.createFraction(filename=self.getParameterOutputFraction(),
            gridOrResolution=Raster(enmapboxtestdata.enmap).grid())
        return {self.P_OUTPUT_FRACTION: filename}


ALGORITHMS.append(CreateTestFraction())


class CreateTestClassifier(EnMAPAlgorithm):
    def displayName(self):
        return 'Create Test Classifier (RandomForest)'

    def description(self):
        return 'Create a fitted RandomForestClassifier using enmap testdata.'

    def group(self):
        return self.GROUP_TESTDATA

    def defineCharacteristics(self):
        self.addParameterOutputClassifier()

    def processAlgorithm_(self):
        import enmapboxtestdata
        filename = self.getParameterOutputEstimator(name=self.P_OUTPUT_CLASSIFIER)
        enmapboxtestdata.createClassifier().pickle(filename=filename)
        return {self.P_OUTPUT_CLASSIFIER: filename}


ALGORITHMS.append(CreateTestClassifier())


class CreateTestRegressor(EnMAPAlgorithm):
    def displayName(self):
        return 'Create Test Regressor (RandomForest)'

    def description(self):
        return 'Create a fitted RandomForestRegressor using enmap testdata.'

    def group(self):
        return self.GROUP_TESTDATA

    def defineCharacteristics(self):
        self.addParameterOutputRegressor()

    def processAlgorithm_(self):
        import enmapboxtestdata
        filename = self.getParameterOutputEstimator(name=self.P_OUTPUT_REGRESSOR)
        enmapboxtestdata.createRegressor().pickle(filename=filename)
        return {self.P_OUTPUT_REGRESSOR: filename}


ALGORITHMS.append(CreateTestRegressor())


class CreateTestClusterer(EnMAPAlgorithm):
    def displayName(self):
        return 'Create Test Clusterer (KMeans)'

    def description(self):
        return 'Create a fitted KMeans clusterer using enmap testdata.'

    def group(self):
        return self.GROUP_TESTDATA

    def defineCharacteristics(self):
        self.addParameterOutputClusterer()

    def processAlgorithm_(self):
        import enmapboxtestdata
        filename = self.getParameterOutputEstimator(name=self.P_OUTPUT_CLUSTERER)
        enmapboxtestdata.createClusterer().pickle(filename=filename)
        return {self.P_OUTPUT_CLUSTERER: filename}


ALGORITHMS.append(CreateTestClusterer())


class CreateTestTransformer(EnMAPAlgorithm):
    def displayName(self):
        return 'Create Test Transformer (PCA)'

    def description(self):
        return 'Create a fitted PCA transformer using enmap testdata.'

    def group(self):
        return self.GROUP_TESTDATA

    def defineCharacteristics(self):
        self.addParameterOutputTransformer()

    def processAlgorithm_(self):
        import enmapboxtestdata
        filename = self.getParameterOutputEstimator(name=self.P_OUTPUT_TRANSFORMER)
        enmapboxtestdata.createTransformer().pickle(filename=filename)
        return {self.P_OUTPUT_TRANSFORMER: filename}


ALGORITHMS.append(CreateTestTransformer())


class ImportLibrary(EnMAPAlgorithm):
    def displayName(self):
        return 'Import Library'

    def description(self):
        return 'Import Library profiles as single line Raster.'

    def group(self):
        return self.GROUP_IMPORT_DATA

    def defineCharacteristics(self):
        self.addParameterLibrary()
        self.addParameterOutputRaster()

    def processAlgorithm_(self):
        library = self.getParameterLibrary()
        filename = self.getParameterOutputRaster()
        Raster.fromEnviSpectralLibrary(filename=filename, library=library)
        return {self.P_OUTPUT_RASTER: filename}


ALGORITHMS.append(ImportLibrary())


class ImportLibraryClassificationAttribute(EnMAPAlgorithm):
    def displayName(self):
        return 'Import Library Classification Attribute'

    def description(self):
        return 'Import Library classification attribute as single line Classification.'

    def group(self):
        return self.GROUP_IMPORT_DATA

    P_ATTRIBUTE = 'attribute'

    def defineCharacteristics(self):
        self.addParameterLibrary()
        self.addParameterString(name=self.P_ATTRIBUTE, description='Classification Attribute',
            help='Attribute name as specified in the library CSV attribute file.')
        self.addParameterOutputClassification()

    def processAlgorithm_(self):
        library = self.getParameterLibrary()
        attribute = self.getParameterString(self.P_ATTRIBUTE)

        filename = self.getParameterOutputClassification()
        Classification.fromEnviSpectralLibrary(filename=filename, library=library, attribute=attribute)
        return {self.P_OUTPUT_CLASSIFICATION: filename}


ALGORITHMS.append(ImportLibraryClassificationAttribute())

'''class ImportLibraryRegressionAttribute(EnMAPAlgorithm):
    def displayName(self):
        return 'Import Library Regression Attributes'

    def description(self):
        return 'Import Library regression attributes as single line Regression.'

    def group(self):
        return self.GROUP_AUXILLIARY

    P_ATTRIBUTES = 'attributes'

    def defineCharacteristics(self):
        self.addParameterLibrary()
        self.addParameterString(name=self.P_ATTRIBUTES, description='Regression Attributes',
                                help='List of attribute names as specified in the library CSV attribute file.')
        self.addParameterOutputRegression()

    def processAlgorithm_(self):

        library = self.getParameterLibrary()
        attributes = [s.strip() for s in self.getParameterString(self.P_ATTRIBUTES).split(',')]
        filename = self.getParameterOutputRegression()
        Regression.fromEnviSpectralLibrary(filename=filename, library=library, attributes=attributes)
        return {self.P_OUTPUT_REGRESSION: filename}


ALGORITHMS.append(ImportLibraryRegressionAttribute())


class ImportLibraryFractionAttribute(EnMAPAlgorithm):
    def displayName(self):
        return 'Import Library Fraction Attributes'

    def description(self):
        return 'Import Library fraction attributes as single line Fraction.'

    def group(self):
        return self.GROUP_AUXILLIARY

    P_ATTRIBUTES = 'attributes'

    def defineCharacteristics(self):
        self.addParameterLibrary()
        self.addParameterString(name=self.P_ATTRIBUTES, description='Fraction Attributes',
                                help='List of attribute names as specified in the library CSV attribute file.')
        self.addParameterOutputFraction()

    def processAlgorithm_(self):

        library = self.getParameterLibrary()
        attributes = [s.strip() for s in self.getParameterString(self.P_ATTRIBUTES).split(',')]
        filename = self.getParameterOutputFraction()
        Regression.fromEnviSpectralLibrary(filename=filename, library=library, attributes=attributes)
        return {self.P_OUTPUT_FRACTION: filename}


ALGORITHMS.append(ImportLibraryFractionAttribute())'''


class OpenTestMaps(EnMAPAlgorithm):
    def group(self):
        return self.GROUP_TESTDATA

    def displayName(self):
        return 'Open Test Maps'

    def description(self):
        return 'Opens testdata into current QGIS project (LandCov_BerlinUrbanGradient.shp, HighResolution_BerlinUrbanGradient.bsq, EnMAP_BerlinUrbanGradient.bsq, SpecLib_BerlinUrbanGradient.sli).'

    def name(self):
        return 'OpenTestdataForModel'

    def defineCharacteristics(self):
        self.addParameterOutputRaster('enmap', 'EnMAP (30m; 177 bands)',
            help='File name: EnMAP_BerlinUrbanGradient.bsq\n'
                 'Simulated EnMAP data (based on 3.6m HyMap imagery) acquired in August 2009 over south eastern part of Berlin covering an area of 4.32 km^2 (2.4 x 1.8 km). It has a spectral resolution of 177 bands and a spatial resolution of 30m.')
        self.addParameterOutputRaster('hymap', 'HyMap (3.6m; Blue, Green, Red, NIR bands)',
            help='File name: HighResolution_BerlinUrbanGradient.bsq\n'
                 'HyMap image acquired in August 2009 over south eastern part of Berlin covering an area of 4.32 km^2 (2.4 x 1.8 km). This dataset was reduced to 4 bands (0.483, 0.558, 0.646 and 0.804 micrometers). The spatial resolution is 3.6m.')
        self.addParameterOutputVector('landcover', 'LandCover Layer',
            help='File name: LandCov_BerlinUrbanGradient.shp\n'
                 'Polygon shapefile containing land cover information on two classification levels. Derived from very high resolution aerial imagery and cadastral datasets.\n'
                 'Level 1 classes: Impervious; Other; Vegetation; Soil\n'
                 'Level 2 classes: Roof; Low vegetation; Other; Pavement; Tree; Soil')

    def processAlgorithm_(self):
        import enmapboxtestdata
        return {'enmap': enmapboxtestdata.enmap,
                'hymap': enmapboxtestdata.hires,
                'landcover': enmapboxtestdata.landcover_polygons}


ALGORITHMS.append(OpenTestMaps())


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


class RasterApplyMask(EnMAPAlgorithm):
    def displayName(self):
        return 'Apply Mask to Raster'

    def description(self):
        return 'Pixels that are masked out are set to the raster no data value.'

    def group(self):
        return self.GROUP_MASKING

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterInvertableMask(optional=False)
        self.addParameterOutputRaster(description='Masked Raster')

    def processAlgorithm_(self):
        raster = self.getParameterRaster()
        filename = self.getParameterOutputRaster()
        raster.applyMask(filename=filename, mask=self.getParameterInvertableMask(), progressBar=self._progressBar)
        return {self.P_OUTPUT_RASTER: filename}


ALGORITHMS.append(RasterApplyMask())


class RasterFromVector(EnMAPAlgorithm):
    def displayName(self):
        return 'Raster from Vector'

    def description(self):
        return Help(text='Converts vector to raster (using {}).',
            links=[Link(url='http://gdal.org/python/osgeo.gdal-module.html#RasterizeOptions',
                name='gdal rasterize')])

    def group(self):
        return self.GROUP_CREATE_RASTER

    P_INIT_VALUE = 'initValue'
    P_BURN_VALUE = 'burnValue'
    P_BURN_ATTRIBUTE = 'burnAttribute'
    P_ALL_TOUCHED = 'allTouched'
    P_FILTER_SQL = 'filterSQL'

    def defineCharacteristics(self):
        self.addParameterGrid()
        self.addParameterVector()
        self.addParameterFloat(self.P_INIT_VALUE, 'Init Value', defaultValue=0,
            help='Pre-initialization value for the output raster before burning. Note that this value is not marked as the nodata value in the output raster.')
        self.addParameterFloat(self.P_BURN_VALUE, 'Burn Value', defaultValue=1,
            help='Fixed value to burn into each pixel, which is covered by a feature (point, line or polygon).')
        self.addParameterField(self.P_BURN_ATTRIBUTE, 'Burn Attribute', type=QgsProcessingParameterField.Numeric,
            parentLayerParameterName=self.P_VECTOR, optional=True,
            help='Specify numeric vector field to use as burn values.')
        self.addParameterBoolean(self.P_ALL_TOUCHED, 'All touched', defaultValue=False,
            help='Enables the ALL_TOUCHED rasterization option so that all pixels touched by lines or polygons will be updated, not just those on the line render path, or whose center point is within the polygon.')
        self.addParameterString(self.P_FILTER_SQL, 'Filter SQL', defaultValue='', optional=True,
            help='Create SQL based feature selection, so that only selected features will be used for burning.\n'
                 "Example: Level_2 = 'Roof' will only burn geometries where the Level_2 attribute value is equal to 'Roof', others will be ignored. This allows you to subset the vector dataset on-the-fly.")
        self.addParameterDataType()
        self.addParameterNoDataValue(optional=True)
        self.addParameterOutputRaster()

    def processAlgorithm_(self):
        grid = self.getParameterGrid()
        filterSQL = self.getParameterString(self.P_FILTER_SQL)
        if filterSQL == '':
            filterSQL = None
        vector = self.getParameterVector(initValue=self.getParameterFloat(self.P_INIT_VALUE),
            burnValue=self.getParameterFloat(self.P_BURN_VALUE),
            burnAttribute=self.getParameterField(self.P_BURN_ATTRIBUTE),
            allTouched=self.getParameterBoolean(self.P_ALL_TOUCHED),
            filterSQL=filterSQL,
            dtype=self.getParameterDataType())

        filename = self.getParameterOutputRaster()
        Raster.fromVector(filename=filename, vector=vector, grid=grid, noDataValue=self.getParameterNoDataValue(),
            progressBar=self._progressBar)
        return {self.P_OUTPUT_RASTER: filename}


ALGORITHMS.append(RasterFromVector())


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


class RasterWavebandSubsetting(EnMAPAlgorithm):
    def displayName(self):
        return 'Subset Raster Wavebands'

    def description(self):
        return 'Subset raster bands that best match the given wavelength.'

    def group(self):
        return self.GROUP_RESAMPLING

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterWavelength()
        self.addParameterOutputRaster()

    def processAlgorithm_(self):
        raster = self.getParameterRaster()
        outraster = raster.subsetWavebands(filename=self.getParameterOutputRaster(),
            wavelength=self.getParameterWavelength())
        return {self.P_OUTPUT_RASTER: outraster.filename()}


ALGORITHMS.append(RasterWavebandSubsetting())


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


class RegressionSampleFromArtmo(EnMAPAlgorithm):
    def group(self): return self.GROUP_IMPORT_DATA

    def displayName(self): return 'Import ARTMO lookup table'

    def description(self):
        return 'Creates a raster and a regression from the profiles and biophysical parameters in the lookup table.'

    def defineCharacteristics(self):
        self.addParameterFile(description='ARTMO lookup table')
        self.addParameterFloat(description='Reflectance scale factor', defaultValue=1.,
            help='Reflectance scale factor. Keep the default to have the data in the [0, 1]. Use a value of 10000 to scale the data into the [0, 10000] range.')
        self.addParameterOutputRaster()
        self.addParameterOutputRegression()

    def processAlgorithm_(self):
        sample = RegressionSample.fromArtmo(filenameRaster=self.getParameterOutputRaster(),
            filenameRegression=self.getParameterOutputRegression(),
            filenameArtmo=self.getParameterFile(),
            filenameArtmoMeta=self.getParameterFile().replace('.txt', '_meta.txt'),
            scale=self.getParameterFloat())
        return {self.P_OUTPUT_REGRESSION: sample.regression().filename(),
                self.P_OUTPUT_RASTER: sample.raster().filename()}


ALGORITHMS.append(RegressionSampleFromArtmo())


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


class SpatialResamplingRaster(EnMAPAlgorithm):
    def displayName(self):
        return 'Spatial Resampling (Raster)'

    def description(self):
        return 'Resamples a Raster into a target grid.'

    def group(self):
        return self.GROUP_RESAMPLING

    def defineCharacteristics(self):
        self.addParameterGrid()
        self.addParameterRaster()
        self.addParameterGDALResamplingAlg()
        self.addParameterOutputRaster()

    def processAlgorithm_(self):
        raster = self.getParameterRaster()
        outraster = raster.resample(filename=self.getParameterOutputRaster(),
            grid=self.getParameterGrid(),
            resampleAlg=self.getParameterGDALResamplingAlg(),
            progressBar=self._progressBar)
        return {self.P_OUTPUT_RASTER: outraster.filename()}


ALGORITHMS.append(SpatialResamplingRaster())


class SpatialResamplingMask(EnMAPAlgorithm):
    def displayName(self):
        return 'Spatial Resampling (Mask)'

    def description(self):
        return 'Resamples a Mask into a target grid.'

    def group(self):
        return self.GROUP_RESAMPLING

    def defineCharacteristics(self):
        self.addParameterGrid()
        self.addParameterMask()
        self.addParameterMinOverallCoverage()
        self.addParameterOutputMask()

    def processAlgorithm_(self):
        mask = self.getParameterMask(minOverallCoverage=self.getParameterMinOverallCoverage())
        outmask = mask.resample(filename=self.getParameterOutputMask(),
            grid=self.getParameterGrid(),
            progressBar=self._progressBar)
        return {self.P_OUTPUT_MASK: outmask.filename()}


ALGORITHMS.append(SpatialResamplingMask())


class SpatialResamplingClassification(EnMAPAlgorithm):
    def displayName(self):
        return 'Spatial Resampling (Classification)'

    def description(self):
        return 'Resamples a Classification into a target grid.'

    def group(self):
        return self.GROUP_RESAMPLING

    def defineCharacteristics(self):
        self.addParameterGrid()
        self.addParameterClassification()
        self.addParameterMinCoverages()
        self.addParameterOutputClassification()

    def processAlgorithm_(self):
        classification = self.getParameterClassification(minOverallCoverage=self.getParameterMinOverallCoverage(),
            minDominantCoverage=self.getParameterMinDominantCoverage())
        outclassification = classification.resample(filename=self.getParameterOutputClassification(),
            grid=self.getParameterGrid(),
            progressBar=self._progressBar)
        return {self.P_OUTPUT_CLASSIFICATION: outclassification.filename()}


ALGORITHMS.append(SpatialResamplingClassification())


class SpatialResamplingRegression(EnMAPAlgorithm):
    def displayName(self):
        return 'Spatial Resampling (Regression)'

    def description(self):
        return 'Resamples a Regression into a target grid.'

    def group(self):
        return self.GROUP_RESAMPLING

    def defineCharacteristics(self):
        self.addParameterGrid()
        self.addParameterRegression()
        self.addParameterMinOverallCoverage()
        self.addParameterOutputRegression()

    def processAlgorithm_(self):
        regression = self.getParameterRegression(minOverallCoverage=self.getParameterMinOverallCoverage())
        outregression = regression.resample(filename=self.getParameterOutputRegression(),
            grid=self.getParameterGrid(),
            progressBar=self._progressBar)
        return {self.P_OUTPUT_REGRESSION: outregression.filename()}


ALGORITHMS.append(SpatialResamplingRegression())


class SpatialResamplingFraction(EnMAPAlgorithm):
    def displayName(self):
        return 'Spatial Resampling (Fraction)'

    def description(self):
        return 'Resamples a Fraction into a target grid.'

    def group(self):
        return self.GROUP_RESAMPLING

    def defineCharacteristics(self):
        self.addParameterGrid()
        self.addParameterFraction()
        self.addParameterMinOverallCoverage()
        self.addParameterOutputFraction()

    def processAlgorithm_(self):
        fraction = self.getParameterFraction(minOverallCoverage=self.getParameterMinOverallCoverage(),
            minDominantCoverage=self.getParameterMinDominantCoverage())
        outfraction = fraction.resample(filename=self.getParameterOutputFraction(),
            grid=self.getParameterGrid(),
            progressBar=self._progressBar)
        return {self.P_OUTPUT_FRACTION: outfraction.filename()}


ALGORITHMS.append(SpatialResamplingFraction())


class SensorDefinitionResampleRaster(EnMAPAlgorithm):
    def displayName(self):
        return 'Spectral Resampling'

    def group(self):
        return self.GROUP_RESAMPLING

    def description(self):
        return 'Spectrally resample a raster.'

    SENSOR_NAMES = ['select sensor'] + SensorDefinition.predefinedSensorNames()
    P_OPTION1 = 'option1'
    P_OPTION2 = 'option2'
    P_OPTION3 = 'option3'

    def defineCharacteristics(self):
        self.addParameterRaster(help='Select raster file which should be resampled.')
        self.addParameterEnum(name=self.P_OPTION1,
            description='[Options 1] Spectral characteristic from predefined sensor',
            options=self.SENSOR_NAMES, optional=True)
        self.addParameterRaster(name=self.P_OPTION2, description='[Option 2] Spectral characteristic from Raster',
            help='Raster with defined wavelength and fwhm',
            optional=True)
        self.addParameterLibrary(name=self.P_OPTION3,
            description='[Option 3] Spectral characteristic from response function files.',
            optional=True)
        self.resampleAlgNames = ['Linear Interpolation', 'Response Function Convolution']
        self.resampleAlgOptions = [SensorDefinition.RESAMPLE_LINEAR, SensorDefinition.RESAMPLE_RESPONSE]
        self.addParameterEnum(description='Resampling Algorithm', options=self.resampleAlgNames, defaultValue=0)
        self.addParameterOutputRaster()

    def processAlgorithm_(self):
        raster = self.getParameterRaster()
        option1 = self.getParameterEnum(name=self.P_OPTION1)
        option2 = self.getParameterRaster(name=self.P_OPTION2)
        option3 = self.getParameterLibrary(name=self.P_OPTION3)

        self._progressBar.setText(repr(option1))
        self._progressBar.setText(repr(option2))
        self._progressBar.setText(repr(option3))

        if option1 != 0:
            sensor = SensorDefinition.fromPredefined(name=self.SENSOR_NAMES[option1])
        #            library = EnviSpectralLibrary(filename=self.SENSOR_RESPONSES[option1])
        #            sensor = SensorDefinition.fromEnviSpectralLibrary(library=library)
        elif isinstance(option2, Raster):
            sensor = SensorDefinition.fromRaster(raster=option2)
        elif isinstance(option3, EnviSpectralLibrary):
            sensor = SensorDefinition.fromEnviSpectralLibrary(library=option3)
        else:
            raise EnMAPAlgorithmParameterValueError('missing spectral characteristic')

        self._progressBar.setText(repr(sensor))

        filename = self.getParameterOutputRaster()
        resampleAlg = self.resampleAlgOptions[self.getParameterEnum()]
        sensor.resampleRaster(filename=filename, raster=raster, resampleAlg=resampleAlg, progressBar=self._progressBar)
        return {self.P_OUTPUT_RASTER: filename}


ALGORITHMS.append(SensorDefinitionResampleRaster())


class SensorDefinitionResampleRasterToSensor(EnMAPAlgorithm):
    def displayName(self):
        return 'Spectral Resampling to Sensor'

    def group(self):
        return self.GROUP_RESAMPLING

    def description(self):
        return 'Spectrally resample a raster to a sensor.'

    SENSOR_NAMES = SensorDefinition.predefinedSensorNames()
    SENSOR_NAMES_DISPLAYED = [name.replace('_', ' ') for name in SENSOR_NAMES]
    P_TARGET_SENSOR = 'targetSensor'

    def defineCharacteristics(self):
        self.addParameterRaster(help='Raster to be resampled.')
        self.addParameterEnum(
            name=self.P_TARGET_SENSOR, description='Sensor', options=self.SENSOR_NAMES_DISPLAYED,
            help='Predefined target sensor'
        )
        self.resampleAlgNames = ['Linear Interpolation', 'Response Function Convolution']
        self.resampleAlgOptions = [SensorDefinition.RESAMPLE_LINEAR, SensorDefinition.RESAMPLE_RESPONSE]
        self.addParameterEnum(description='Resampling Algorithm', options=self.resampleAlgNames, defaultValue=1)
        self.addParameterOutputRaster()

    def processAlgorithm_(self):
        raster = self.getParameterRaster()
        sensor = SensorDefinition.fromPredefined(
            name=self.SENSOR_NAMES[self.getParameterEnum(name=self.P_TARGET_SENSOR)]
        )
        self._progressBar.setText(repr(sensor))
        filename = self.getParameterOutputRaster()
        resampleAlg = self.resampleAlgOptions[self.getParameterEnum()]
        sensor.resampleRaster(filename=filename, raster=raster, resampleAlg=resampleAlg, progressBar=self._progressBar)
        return {self.P_OUTPUT_RASTER: filename}


ALGORITHMS.append(SensorDefinitionResampleRasterToSensor())


class SensorDefinitionResampleRasterToRaster(EnMAPAlgorithm):
    def displayName(self):
        return 'Spectral Resampling to Raster'

    def group(self):
        return self.GROUP_RESAMPLING

    def description(self):
        return 'Spectrally resample a raster to a raster.'

    P_TARGET_RASTER = 'targetRaster'

    def defineCharacteristics(self):
        self.addParameterRaster(help='Select raster to be resampled.')
        self.addParameterRaster(
            name=self.P_TARGET_RASTER, description='Target Raster',
            help='Raster with defined wavelength and (optional) fwhm'
        )
        self.resampleAlgNames = ['Linear Interpolation', 'FWHM-based Convolution (if possible)']
        self.resampleAlgOptions = [SensorDefinition.RESAMPLE_LINEAR, SensorDefinition.RESAMPLE_RESPONSE]
        self.addParameterEnum(description='Resampling Algorithm', options=self.resampleAlgNames, defaultValue=1)
        self.addParameterOutputRaster()

    def processAlgorithm_(self):
        raster = self.getParameterRaster()
        targetRaster = self.getParameterRaster(name=self.P_TARGET_RASTER)
        sensor = SensorDefinition.fromRaster(raster=targetRaster)
        self._progressBar.setText(repr(sensor))
        filename = self.getParameterOutputRaster()
        resampleAlg = self.resampleAlgOptions[self.getParameterEnum()]
        if self.getParameterEnum() == 1:
            if targetRaster.dataset().metadataItem(key='fwhm', domain='ENVI') is None:
                resampleAlg = self.resampleAlgOptions[0]  # use linear if FWHM is not available
        sensor.resampleRaster(filename=filename, raster=raster, resampleAlg=resampleAlg, progressBar=self._progressBar)
        return {self.P_OUTPUT_RASTER: filename}


ALGORITHMS.append(SensorDefinitionResampleRasterToRaster())


class SensorDefinitionResampleRasterToResponseFunctionLibrary(EnMAPAlgorithm):
    def displayName(self):
        return 'Spectral Resampling to Response Function Library'

    def group(self):
        return self.GROUP_RESAMPLING

    def description(self):
        return 'Spectrally resample a raster using a response function library.'

    P_TARGET_LIBRARY = 'targetLibrary'

    def defineCharacteristics(self):
        self.addParameterRaster(help='Select raster to be resampled.')
        self.addParameterVector(
            name=self.P_TARGET_LIBRARY,
            description='Response Function Library.',
            help='Library with bandwise response function profiles.'
        )
        self.resampleAlgNames = ['Linear Interpolation', 'Response Function Convolution']
        self.resampleAlgOptions = [SensorDefinition.RESAMPLE_LINEAR, SensorDefinition.RESAMPLE_RESPONSE]
        self.addParameterEnum(description='Resampling Algorithm', options=self.resampleAlgNames, defaultValue=1)
        self.addParameterOutputRaster()

    def processAlgorithm_(self):
        raster = self.getParameterRaster()
        targetLibrary = self.getParameterVectorLibrary(name=self.P_TARGET_LIBRARY)
        tmpfilename = join(gettempdir(), 'responseFunctionLibrary.sli')
        tmpfilenames = EnviSpectralLibraryIO.write(speclib=targetLibrary, path=tmpfilename)
        targetEnviLibrary = EnviSpectralLibrary(filename=tmpfilename)
        sensor = SensorDefinition.fromEnviSpectralLibrary(library=targetEnviLibrary, isResponseFunction=True)
        for tmpfilename in tmpfilenames:
            remove(tmpfilename)
        self._progressBar.setText(repr(sensor))
        filename = self.getParameterOutputRaster()
        resampleAlg = self.resampleAlgOptions[self.getParameterEnum()]
        sensor.resampleRaster(filename=filename, raster=raster, resampleAlg=resampleAlg, progressBar=self._progressBar)
        return {self.P_OUTPUT_RASTER: filename}


ALGORITHMS.append(SensorDefinitionResampleRasterToResponseFunctionLibrary())


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
