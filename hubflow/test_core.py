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
        # obj.report().saveHTML(filename=join(outdir, 'report.html'))


    def test_ClassificationSample(self):

        classificationSample = ClassificationSample.fromENVISpectralLibrary(enmapboxtestdata.speclib,
                                                                            classificationSchemeName='level 2 ')
        print(classificationSample)
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
        clusteringPerformance.report().saveHTML(filename=join(outdir, 'reportClusteringPerformance.html'))

    def test_Image(self):
        print(Raster.fromVector(filename=join(outdir, 'imageFromVector.bsq'), vector=vector, grid=hymap.grid,
                                overwrite=overwrite))
        print(enmap.basicStatistics(bandIndicies=None, mask=vector, grid=enmap))

        i1, i2 = 0, 1
        (min1, min2), (max1, max2), (mean1, mean2), (n1, n2) = enmap.basicStatistics(bandIndicies=[i1, i2], mask=vector)
        H, xedges, yedges = enmap.scatterMatrix(raster2=enmap, bandIndex1=i1, bandIndex2=i2, range1=[min1, max1],
                                                range2=[min2, max2], bins=10,
                                                mask=vector, stratification=hymapClassification)
        print(H)


    def test_Mask(self):
        print(hymapClassification.asMask().resample(filename=join(outdir, 'MaskResample.bsq'), grid=enmap))
        print(hymapClassification)

        print(Mask.fromVector(filename=join(outdir, 'maskFromVector.bsq'), vector=vector, grid=enmap))
        print(Mask.fromRaster(filename=join(outdir, 'maskFromRaster.bsq'), raster=enmapClassification,
                              trueRanges=[(1, 100)]))


    def test_Probability(self):

        print(Probability.fromClassification(filename=join(outdir, 'enmapProbability.bsq'),
                                             classification=vectorClassification, grid=enmap.grid))

        print(enmapProbability.asClassColorRGBRaster(filename=join(outdir, 'probabilityAsClassColorRGBImage.bsq')))


        print(enmapProbability.subsetClassesByName(filename=join(outdir, 'probabilitySubsetClassesByName.bsq'),
                                                   names=enmapProbability.classDefinition.names))


    def test_ProbabilityPerformance(self):
        probabilityPerformance = ProbabilityPerformance.fromRaster(prediction=enmapProbability, reference=enmapClassification)
        print(probabilityPerformance)
        probabilityPerformance.report().saveHTML(filename=join(outdir, 'reportProbabilityPerformance.html'))


    def test_ProbabilitySample(self):

        print(ProbabilitySample.fromClassificationSample(sample=enmapClassificationSample))
        print(ProbabilitySample.fromRasterAndProbability(raster=enmap, probability=hymapProbability, grid=enmap,
                                                         mask=vector, mask2=enmapMask))
        print(ProbabilitySample.fromRasterAndProbability(raster=enmap, probability=hymapClassification, grid=enmap))
        print(ProbabilitySample.fromRasterAndProbability(raster=enmap, probability=vectorClassification, grid=enmap))
        print(ProbabilitySample.fromRasterAndClassification(raster=enmap, classification=hymapClassification, grid=enmap))
        print(enmapProbabilitySample.subsetClasses(labels=[1, 3]))
        print(enmapProbabilitySample.subsetClassesByName(names=enmapProbabilitySample.classDefinition.names))
        print()

    def test_Raster(self):
        bandIndicies = None#[0, 1]
        basicStatistics = hymap.basicStatistics(bandIndicies=bandIndicies)

        return
        histograms = hymap.histogram(bandIndicies=bandIndicies, basicStatistics=basicStatistics)
        return
        raster = Raster.fromSample(filename=join(outdir, 'RasterFromSample.bsq'), sample=enmapClassificationSample)
        print(enmap.applyMask(filename=join(outdir, 'RasterApplyMask.bsq'), mask=enmapMask, fillValue=42))

    def test_Regression(self):
        print(enmapProbability.asMask())


    def test_RegressionPerformance(self):
        obj = RegressionPerformance.fromRaster(prediction=enmapProbability, reference=enmapProbability)
        print(obj)
        # obj.report().saveHTML(filename=join(outdir, 'report.html'))


    def test_RegressionSample(self):
        print(RegressionSample.fromRasterAndRegression(raster=enmap, regression=hymapProbability, grid=enmap, mask=vector))
        print(RegressionSample.fromProbabilitySample(sample=enmapProbabilitySample))


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
        print(join(outdir, 'speclib.sli'))
        unsupervisedSample.scaleFeaturesInplace(factor=10000)
        print(unsupervisedSample.classifyByName(names=unsupervisedSample.metadata['level 2 class spectra names'],
                                                classDefinition=hubflow.testdata.classDefinitionL2))
        print(UnsupervisedSample.fromRasterAndMask(raster=enmap, mask=vector, grid=enmap))


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
        pass

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
