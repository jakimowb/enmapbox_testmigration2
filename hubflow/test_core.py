import matplotlib
matplotlib.use('QT5Agg')
from matplotlib import pyplot

from unittest import TestCase
from tempfile import gettempdir
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import hubflow.testdata
import enmapboxtestdata
from hubflow.core import *
import hubdc.testdata

overwrite = not True
vector = hubflow.testdata.vector()
hymap = hubflow.testdata.hymap()
enmap = hubflow.testdata.enmap()

hymapClassification = hubflow.testdata.hymapClassification(overwrite=overwrite)
enmapClassification = hubflow.testdata.enmapClassification(overwrite=overwrite)
vectorClassification = hubflow.testdata.vectorClassification()
hymapProbability = hubflow.testdata.hymapProbability(overwrite=overwrite)
enmapProbability = hubflow.testdata.enmapProbability(overwrite=overwrite)
enmapRegression = hubflow.testdata.enmapRegression(overwrite=overwrite)
enmapMask = enmapClassification.asMask()

enmapProbabilitySample = hubflow.testdata.enmapProbabilitySample(overwrite=overwrite)
enmapClassificationSample = hubflow.testdata.enmapClassificationSample(overwrite=overwrite)
enmapUnsupervisedSample = hubflow.testdata.enmapUnsupervisedSample(overwrite=overwrite)

outdir = join(gettempdir(), 'hubflow_test')


class Test(TestCase):
    def test_StringParser(self):
        p = StringParser()
        self.assertIsNone(p.list(''))
        self.assertListEqual(p.list('[]'), [])
        self.assertListEqual(p.list('[1]'), [1])
        self.assertListEqual(p.list('1'), [1])
        self.assertListEqual(p.list('[1, 2, 3]'), [1, 2, 3])
        self.assertListEqual(p.list('{1, 2, 3}'), [1, 2, 3])
        self.assertListEqual(p.list('(1, 2, 3)'), [1, 2, 3])
        self.assertListEqual(p.list('1 2 3'), [1, 2, 3])
        self.assertListEqual(p.list('1, 2, 3'), [1, 2, 3])
        self.assertListEqual(p.list('a b c'), ['a', 'b', 'c'])
        self.assertListEqual(p.list('1 2-4 5'), [1, 2, 3, 4, 5])
        self.assertListEqual(p.list('-4--2'), [-4, -3, -2])
        #self.assertListEqual(p.list('\eval range(3)'), [0, 1, 2])

        self.assertListEqual(p.list('1-3 7-10', extendRanges=False), [(1, 3), (7, 10)])
        self.assertListEqual(p.list('1 5-10', extendRanges=False), [1, (5, 10)])

    def test_Classification(self):

        # from probability
        print(Classification.fromClassification(filename=join(outdir, 'ClassificationFromProbability.bsq'),
                                                classification=enmapProbability, masks=[enmapMask]))

        def ufunc(array, meta):
            carray = np.copy(array)
            for old, new in zip([0, 1, 2, 3, 4, 255], [1, 2, 3, 4, 5, 0]):
                carray[array == old] = new
            return carray

        classDefinition = ClassDefinition(names=['land', 'water', 'shadow','snow', 'cloud'],
                                          colors=['orange', 'blue', 'grey', 'snow', 'white'])

        print(Classification.fromRasterAndFunction(filename=join(outdir, 'ClassificationFromRasterAndFunction.bsq'),
                                                   raster=Raster(filename=hubdc.testdata.LT51940232010189KIS01.cfmask),
                                                   ufunc=ufunc, classDefinition=classDefinition))

        print(Classification.fromClassification(filename=join(outdir, 'hymapLandCover.bsq'),
                                                classification=vectorClassification, grid=hymap.grid))

        print(hymapClassification.reclassify(filename=join(outdir, 'classificationReclassify.bsq'),
                                             classDefinition=hubflow.testdata.classDefinitionL1,
                                             mapping=enmapboxtestdata.landcoverClassDefinition.level2.mappingToLevel1ByName))


    def test_ClassificationPerformance(self):
        obj = ClassificationPerformance.fromRaster(prediction=enmapClassification, reference=enmapClassification)
        print(obj)
        obj.report().saveHTML(filename=join(outdir, 'report.html'), open=False)


    def test_ClassificationSample(self):

        classificationSample = ClassificationSample.fromENVISpectralLibrary(enmapboxtestdata.speclib,
                                                                            classificationSchemeName='level 2 ')

        print(classificationSample)

        classificationSample.saveAsENVISpectralLibrary(filename=join(outdir, 'speclibClassification.sli'),
                                                       prefix='level 42')
        classificationSample2 = ClassificationSample.fromENVISpectralLibrary(filename=join(outdir, 'speclibClassification.sli'),
                                                                             classificationSchemeName='level 42')

        print(classificationSample.synthMix(mixingComplexities={2: 0.7, 3: 0.3}, classLikelihoods='equalized', n=10))

        print(
            ClassificationSample.fromRasterAndClassification(raster=enmapClassification, classification=hymapClassification,
                                                             n=10, grid=enmap, mask=vector))
        print(ClassificationSample.fromRasterAndClassification(raster=enmapProbability, classification=hymapClassification,
                                                               grid=enmap, mask=vector))
        print(ClassificationSample.fromRasterAndClassification(raster=enmap, classification=hymapClassification, grid=enmap,
                                                               mask=vector))
        print(
            ClassificationSample.fromRasterAndProbability(raster=enmap, probability=hymapProbability, grid=enmap,
                                                          mask=vector))
        print(ClassificationSample.fromProbabilitySample(sample=enmapProbabilitySample))

        print(enmapClassificationSample.asProbabilitySample())

    def test_ClassDefinition(self):
        print(ClassDefinition.fromENVIClassification(raster=enmapClassification))
        print(ClassDefinition.fromGDALMeta(raster=enmapClassification))
        print(ClassDefinition(colors=['orange', 'blue', 'grey', 'snow', 'white']))
        print(ClassDefinition(classes=3))
        classDefinition1 = ClassDefinition(classes=3)
        classDefinition2 = ClassDefinition(classes=3)
        self.assertTrue(classDefinition1.equal(classDefinition2, compareColors=False))
        self.assertFalse(classDefinition1.equal(classDefinition2, compareColors=True))
        classDefinition1.color(label=1)

    def test_Classifier(self):
        rfc = Classifier(sklEstimator=RandomForestClassifier())
        print(rfc)
        rfc.fit(sample=enmapClassificationSample)
        print(rfc.predict(filename=join(outdir, 'rfcClassification.bsq'), raster=enmap, mask=vector))
        print(rfc.predictProbability(filename=join(outdir, 'rfcProbability.bsq'), raster=enmap, mask=vector))

    def test_Clusterer(self):
        kmeans = Clusterer(sklEstimator=KMeans())
        print(kmeans)
        kmeans.fit(sample=enmapClassificationSample)
        print(kmeans.predict(filename=join(outdir, 'kmeansClustering.bsq'), raster=enmap, mask=vector))

    def test_ClusteringPerformance(self):
        clusteringPerformance = ClusteringPerformance.fromRaster(prediction=enmapClassification, reference=enmapClassification)
        print(clusteringPerformance)
        clusteringPerformance.report().saveHTML(filename=join(outdir, 'reportClusteringPerformance.html'), open=False)

    def test_FlowObject(self):
        obj = FlowObject()
        obj.pickle(filename=join(outdir, 'FlowObject.pkl'))
        obj2 = FlowObject.unpickle(join(outdir, 'FlowObject.pkl'))

    def test_Raster(self):

        print(Raster.fromVector(filename=join(outdir, 'rasterFromVector.bsq'), vector=vectorClassification, grid=hymap.grid,
                                overwrite=overwrite))
        print(enmap.statistics(bandIndicies=None, mask=vector, grid=enmap))

        bandIndicies = 0, 1

        statistics = enmap.statistics(bandIndicies=bandIndicies, calcPercentiles=True, calcHistogram=True, calcMean=True,
                               calcStd=True, mask=enmapMask)
        statistics = enmap.statistics(mask=vector)

        H, xedges, yedges = enmap.scatterMatrix(raster2=enmap, bandIndex1=bandIndicies[0], bandIndex2=bandIndicies[1],
                                                range1=(statistics[0]['min'], statistics[0]['max']),
                                                range2=(statistics[1]['min'], statistics[1]['max']),
                                                bins=10, mask=vector)
        print(H)

        raster = Raster.fromSample(filename=join(outdir, 'RasterFromSample.bsq'), sample=enmapClassificationSample)
        print(enmap.applyMask(filename=join(outdir, 'RasterApplyMask.bsq'), mask=enmapMask, fillValue=42))


    def test_RasterStack(self):
        rasterStack = RasterStack(rasters=[enmap, hymap])
        for raster in rasterStack.rasters():
            print(raster)
        print(rasterStack)


    def test_Mask(self):
        print(hymapClassification.asMask().resample(filename=join(outdir, 'MaskResample.bsq'), grid=enmap))
        print(hymapClassification)

        print(Mask.fromVector(filename=join(outdir, 'maskFromVector.bsq'), vector=vector, grid=enmap))
        print(Mask.fromRaster(filename=join(outdir, 'maskFromRaster.bsq'), raster=enmapClassification,
                              trueRanges=[(1, 100)], trueValues=[1,2,3],
                              falseRanges=[(-9999, 0)], falseValues=[-9999]))


    def test_Probability(self):

        print(Probability.fromClassification(filename=join(outdir, 'enmapProbability.bsq'),
                                             classification=vectorClassification, grid=enmap.grid))

        print(enmapProbability.asClassColorRGBRaster(filename=join(outdir, 'probabilityAsClassColorRGBImage.bsq')))


        print(enmapProbability.subsetClassesByName(filename=join(outdir, 'probabilitySubsetClassesByName.bsq'),
                                                   names=enmapProbability.classDefinition.names))


    def test_ProbabilityPerformance(self):
        probabilityPerformance = ProbabilityPerformance.fromRaster(prediction=enmapProbability, reference=enmapClassification)
        print(probabilityPerformance)
        probabilityPerformance.report().saveHTML(filename=join(outdir, 'reportProbabilityPerformance.html'), open=False)


    def test_ProbabilitySample(self):

        # export to and import from ENVI Speclib
        probabilitySample = ProbabilitySample.fromRasterAndProbability(raster=enmap, probability=enmapProbability,
                                                                       grid=enmap)
        probabilitySample.saveAsENVISpectralLibrary(filename=join(outdir, 'speclibProbability.sli'))
        probabilitySample2 = ProbabilitySample.fromENVISpectralLibrary(filename=join(outdir, 'speclibProbability.sli'))
        print(join(outdir, 'speclibProbability.sli'))

        print(ProbabilitySample.fromClassificationSample(sample=enmapClassificationSample))
        print(ProbabilitySample.fromRasterAndProbability(raster=enmap, probability=hymapProbability, grid=enmap,
                                                         mask=vector, mask2=enmapMask))
        print(ProbabilitySample.fromRasterAndProbability(raster=enmap, probability=hymapClassification, grid=enmap))
        print(ProbabilitySample.fromRasterAndProbability(raster=enmap, probability=vectorClassification, grid=enmap))
        print(ProbabilitySample.fromRasterAndClassification(raster=enmap, classification=hymapClassification, grid=enmap))
        print(enmapProbabilitySample.subsetClasses(labels=[1, 3]))
        print(enmapProbabilitySample.subsetClassesByName(names=enmapProbabilitySample.classDefinition.names))

        print(enmapProbabilitySample.saveLabelsAsRaster(filename=join(outdir, 'ProbabilitySample_SaveLabelsAsRaster.bsq')))


    def test_Regression(self):
        print(enmapProbability.asMask())


    def test_RegressionPerformance(self):
        obj = RegressionPerformance.fromRaster(prediction=enmapProbability, reference=enmapProbability)
        obj.report().saveHTML(filename=join(outdir, 'RegressionPerformance.html'), open=False)


    def test_RegressionSample(self):

        regressionSample = RegressionSample.fromRasterAndRegression(raster=enmap, regression=hymapProbability, grid=enmap, mask=vector)
        print(regressionSample)

        # export to and import from ENVI Speclib
        regressionSample.saveAsENVISpectralLibrary(filename=join(outdir, 'speclibRegression.sli'))
        targetNames = ['Roof', 'Pavement', 'Low vegetation', 'Tree', 'Soil', 'Other']
        noDataValues = [-1] * len(targetNames)
        regressionSample2 = RegressionSample.fromENVISpectralLibrary(filename=join(outdir, 'speclibRegression.sli'),
                                                                     outputNames=targetNames, noDataValues=noDataValues)
        regressionSample3 = RegressionSample.fromENVISpectralLibrary(filename=join(outdir, 'speclibRegression.sli'))
        print(join(outdir, 'speclibRegression.sli'))

        print(RegressionSample.fromProbabilitySample(sample=enmapProbabilitySample))

        print(regressionSample.saveLabelsAsRaster(filename=join(outdir, 'RegressionSample_SaveLabelsAsRaster.bsq')))


    def test_Regressor(self):
        rfr = Regressor(sklEstimator=RandomForestRegressor())
        print(rfr)
        rfr.fit(sample=enmapProbabilitySample)
        print(rfr.predict(filename=join(outdir, 'rfrRegression.bsq'), raster=enmap, mask=vector))


    def test_Transformer(self):
        pca = Transformer(sklEstimator=PCA())
        print(pca)
        pca.fit(sample=enmapUnsupervisedSample)
        pcaTransformation = pca.transform(filename=join(outdir, 'pcaTransformation.bsq'), raster=enmap, mask=vector)
        print(pcaTransformation)
        pcaInverseTransform = pca.inverseTransform(filename=join(outdir, 'pcaInverseTransformation.bsq'),
                                                   raster=pcaTransformation, mask=vector)
        print(pcaInverseTransform)


    def test_UnsupervisedSample(self):
        print(enmapboxtestdata.speclib)
        unsupervisedSample = UnsupervisedSample.fromENVISpectralLibrary(filename=enmapboxtestdata.speclib)
        print(unsupervisedSample)
        unsupervisedSample.saveAsENVISpectralLibrary(filename=join(outdir, 'speclib.sli'))
        unsupervisedSample2 = unsupervisedSample.fromENVISpectralLibrary(filename=join(outdir, 'speclib.sli'))
        unsupervisedSample.scaleFeaturesInplace(factor=10000)
        print(unsupervisedSample.classifyByName(names=unsupervisedSample.metadata['level 2 class spectra names'],
                                                classDefinition=hubflow.testdata.classDefinitionL2))
        print(UnsupervisedSample.fromRasterAndMask(raster=enmap, mask=vector, grid=enmap))

        print(unsupervisedSample.saveFeaturesAsRaster(filename=join(outdir, 'UnsupervisedSample_SaveFeaturesAsRaster.bsq')))


    def test_Vector(self):
        print(vector.uniqueValues(attribute=hubflow.testdata.landcoverAttributes.Level_2_ID))
        print(vector.uniqueValues(attribute=hubflow.testdata.landcoverAttributes.Level_2))
        print(vector)
        print(Vector.fromRandomPointsFromMask(filename=join(outdir, 'vectorFromRandomPointsFromMask.gpkg.shp'), mask=enmapMask,
                                              n=10))
        n = [10] * enmapClassification.classDefinition.classes
        # n[0] = 10
        print(
        Vector.fromRandomPointsFromClassification(filename=join(outdir, 'vectorFromRandomPointsFromClassification.gpkg'),
                                                  classification=enmapClassification, n=n))


    def test_VectorClassification(self):
        classDefinition = ClassDefinition(names=enmapboxtestdata.landcoverClassDefinition.level2.names,
                                          colors=enmapboxtestdata.landcoverClassDefinition.level2.lookup)
        print(VectorClassification(filename=enmapboxtestdata.landcover,
                                   classDefinition=classDefinition,
                                   idAttribute=enmapboxtestdata.landcoverAttributes.Level_2_ID))
        print(VectorClassification(filename=enmapboxtestdata.landcover,
                                   classDefinition=classDefinition,
                                   nameAttribute=enmapboxtestdata.landcoverAttributes.Level_2))


    def test_extractPixels(self):
        c = ApplierControls()
        c.setBlockSize(25)
        extractPixels(inputs=[enmap, enmapProbability, enmapClassification, enmapRegression, vector, vectorClassification],
                      masks=[enmapMask], grid=enmap.grid, controls=c)


if __name__ == '__main__':
    print('output directory: ' + outdir)
    #Test().test_UnsupervisedSample()
#    test_Mask()

    #run()
