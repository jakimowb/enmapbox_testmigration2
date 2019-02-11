from unittest import TestCase
from tempfile import gettempdir
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import enmapboxtestdata
from hubflow.core import *
import hubflow.testdata
import hubdc.testdata

CUIProgressBar.SILENT = False
overwrite = not True
vector = hubflow.testdata.vector()
enmap = hubflow.testdata.enmap()

enmapClassification = hubflow.testdata.enmapClassification(overwrite=overwrite)
vectorClassification = hubflow.testdata.vectorClassification()
vectorMask = hubflow.testdata.vectorMask()
vectorPoints = hubflow.testdata.vectorPoints()
enmapFraction = hubflow.testdata.enmapFraction(overwrite=overwrite)
enmapRegression = hubflow.testdata.enmapRegression(overwrite=overwrite)
enmapMask = enmapClassification.asMask()
speclib = EnviSpectralLibrary(filename=enmapboxtestdata.library)
#speclib2 = EnviSpectralLibrary(filename=enmapboxtestdata.speclib2)


rasterMaps = [enmap, enmapClassification, enmapRegression, enmapFraction, enmapMask]
vectorsMaps = [vector, vectorClassification, vectorMask]
maps = rasterMaps + vectorsMaps

enmapSample = hubflow.testdata.enmapSample()
enmapClassificationSample = hubflow.testdata.enmapClassificationSample()
enmapRegressionSample = hubflow.testdata.enmapRegressionSample()
enmapFractionSample = hubflow.testdata.enmapFractionSample()

samples = [enmapSample, enmapClassificationSample, enmapRegressionSample, enmapFractionSample]

objects = maps + samples + [MapCollection([enmap, enmapMask]),
                            enmap.sensorDefinition().wavebandDefinition(index=0),
                            enmap.sensorDefinition(),
                            speclib,
                            #RasterStack([enmap, enmapMask]),
                            enmapClassification.classDefinition(),
                            Classifier(sklEstimator=RandomForestClassifier()),
                            ClassificationPerformance.fromRaster(prediction=enmapClassification, reference=enmapClassification),
                            FractionPerformance.fromRaster(prediction=enmapFraction, reference=enmapClassification),
                            RegressionPerformance.fromRaster(prediction=enmapRegression, reference=enmapRegression),
                            ClusteringPerformance.fromRaster(prediction=enmapClassification, reference=enmapClassification),
                            Color('red')]

outdir = join(gettempdir(), 'hubflow_test')
openHTML = not True

class Test(TestCase):

    def test_AttributeDefinitionEditor(self):
        filename = splitext(enmapboxtestdata.landcover_polygons)[0] + '.json'
        print(filename)
        definitions = AttributeDefinitionEditor.readFromJson(filename=filename)
        print(definitions)
        print(AttributeDefinitionEditor.makeClassDefinition(definitions=definitions, attribute='level_2_id'))

    def test_ENVI(self):
        ENVI.readHeader(filenameHeader=ENVI.findHeader(filenameBinary=enmapboxtestdata.library))

    def test_WavebandDefinition(self):

        wavebandDefinition = WavebandDefinition.fromFWHM(center=600, fwhm=10)
        print(wavebandDefinition)
        wavebandDefinition.plot()
        wavebandDefinition.resamplingWeights(sensor=SensorDefinition.fromPredefined(name='sentinel2'))

    def test_SensorDefinition(self):

        print(SensorDefinition.predefinedSensorNames())
        print(SensorDefinition.fromPredefined(name='sentinel2'))

        # a) response function from ENVI Speclib

        sentinel2ResponseFunction = EnviSpectralLibrary(filename=r'C:\source\hub-workflow\hubflow\sensors\sentinel2.sli')
        sentinel2Sensor = SensorDefinition.fromEnviSpectralLibrary(library=sentinel2ResponseFunction,
                                                                   isResponseFunction=True)
        print(sentinel2Sensor)
        sentinel2Sensor.plot()

        # b) wl+fwhm from ENVI Speclib
        enmapSensor = SensorDefinition.fromEnviSpectralLibrary(library=EnviSpectralLibrary(filename=speclib.filename()),
                                                               isResponseFunction=False)
        print(enmapSensor)
        enmapSensor.plot()

        # c) wl+fwhm from raster
        enmapSensor = SensorDefinition.fromRaster(raster=enmap)
        print(enmapSensor)
        enmapSensor.plot()

        # resample EnMAP into Sentinel 2
        outraster = sentinel2Sensor.resampleRaster(filename=join(outdir, 'sentinel2.bsq'), raster=enmap,
                                                   resampleAlg=SensorDefinition.RESAMPLE_LINEAR)
        outraster = sentinel2Sensor.resampleRaster(filename=join(outdir, 'sentinel2.bsq'), raster=enmap,
                                                   resampleAlg=SensorDefinition.RESAMPLE_RESPONSE)

        print(outraster)


        if 1: # plot
            pixel = Pixel(10, 10)
            plotWidget = sentinel2Sensor.plot(yscale=2000, pen='g')
            enmap.dataset().plotZProfile(pixel, plotWidget=plotWidget, spectral=True, xscale=1000)
            outraster.dataset().plotZProfile(pixel, plotWidget=plotWidget, spectral=True, symbol='o', symbolPen='r')

    def test_SensorDefinitionResampleArray(self):

        sentinel2ResponseFunction = EnviSpectralLibrary(filename=r'C:\source\hub-workflow\hubflow\sensors\sentinel2.sli')
        sentinel2Sensor = SensorDefinition.fromEnviSpectralLibrary(library=sentinel2ResponseFunction,
                                                                   isResponseFunction=True)

        profiles = [enmap.dataset().zprofile(pixel=Pixel(10,10)),
                    enmap.dataset().zprofile(pixel=Pixel(20, 20)),
                    enmap.dataset().zprofile(pixel=Pixel(30, 30))]
        wavelength = enmap.metadataWavelength()

        import time
        t0 = time.time()
        outprofiles = sentinel2Sensor.resampleProfiles(array=profiles, wavelength=wavelength, wavelengthUnits='nanometers')
        print(time.time()-t0)
        print(outprofiles)

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

    def test_Color(self):
        color = Color('red')
        print(color)
        print(color.name())
        print(color.red())
        print(color.green())
        print(color.blue())
        print(color.colorNames())

    def test_Classification(self):

        c = Classification.fromClassification(filename='/vsimem/c.bsq',
                                              classification=vectorClassification, grid=enmap.grid())
        print(c.noDataValues())



        raster = Raster.fromArray(array=[[[0, 1, 2]]], filename='/vsimem/raster.bsq')
        print(Classification(filename=raster.filename()))

        raster = enmapClassificationSample.raster()
        classification = enmapClassificationSample.classification()
#        classification.toRasterMetadata(raster=raster, classificationSchemeName='level 42')

#        print(Classification.fromRasterMetadata(filename=join(outdir, 'ClassificationFromRasterMetadata.bsq'),
#                                                raster=raster, classificationSchemeName='level 42'))

        # resampling
        print(enmapClassification)
        classification = Classification(filename=enmapClassification.filename(), minOverallCoverage=0., minDominantCoverage=0.)
        print(classification.resample(filename=join(outdir, 'ClassificationResample.bsq'),
                                           grid=enmap.grid().atResolution(5), controls=ApplierControls()))#.setBlockFullSize()))

        # from fraction
        print(Classification.fromClassification(filename=join(outdir, 'ClassificationFromFraction.bsq'),
                                                classification=enmapFraction, masks=[enmapMask]))

        print(Classification.fromFraction(filename=join(outdir, 'ClassificationFromFraction.bsq'),
                                          fraction=enmapFraction, masks=[enmapMask]))



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
                                                classification=vectorClassification, grid=enmap.grid()))

        print(enmapClassification.reclassify(filename=join(outdir, 'classificationReclassify.bsq'),
                                             classDefinition=ClassDefinition(names=['urban', 'rest']),
                                             mapping={1: 1, 2: 1, 3: 2, 4: 2, 5: 2, 6: 2}))

    def test_ClassificationPerformance(self):

        print(enmapClassification)
        obj = ClassificationPerformance.fromRaster(prediction=enmapClassification, reference=enmapClassification)
        print(obj)
        obj.report().saveHTML(filename=join(outdir, 'report.html'), open=openHTML)

    def test_ClassificationSample(self):

        # read from labeled library
        library = EnviSpectralLibrary(filename=enmapboxtestdata.library)
        classificationSample = ClassificationSample(raster=library.raster(),
                                                    classification=Classification.fromEnviSpectralLibrary(
                                                        filename='/vsimem/labels.bsq',
                                                        library=library,
                                                        attribute='level_2'))

        # syntmix

        for includeWithinclassMixtures in [True, False]:
            for includeEndmember in [True, False]:
                print(includeWithinclassMixtures, includeEndmember)
                fractionSample = enmapClassificationSample.synthMix(
                                     filenameFeatures=join(outdir, 'ClassificationSampleSynthMix.features.bsq'),
                                     filenameFractions=join(outdir, 'ClassificationSampleSynthMix.fractions.bsq'),
                                     mixingComplexities={2: 0.7, 3: 0.3}, classLikelihoods='equalized',
                                     n=1000, target=2, includeWithinclassMixtures=includeWithinclassMixtures,
                                     includeEndmember=includeEndmember)
        features, labels = fractionSample.extractAsArray()
        print(features.shape, labels.shape)

        print(enmapClassificationSample)
        features, labels = enmapClassificationSample.extractAsArray()
        print(features.shape, labels.shape)

    def test_ClassDefinition(self):

        classification = Classification.fromArray(array=[[[0, 1, 2]]], filename='/vsimem/c.bsq')
        newNames = ['Class X']
        mapping = {0: 0, 1: 1, 2: 1}
        newDef = ClassDefinition(names=newNames)
        newDef.setNoDataNameAndColor(name='Not specified', color=Color(128, 128, 128))
        print(classification.classDefinition())
        print(newDef)
        reclassified = classification.reclassify(
            filename='/vsimem/c2.bsq', classDefinition=newDef, mapping=mapping)

        print(reclassified.dataset().band(0).categoryNames())
        print(reclassified.dataset().band(0).categoryColors())

        # qml read / write
        print(ClassDefinition.fromQml(filename=enmapboxtestdata.landcover_polygons.replace('.shp', '.qml')))
        print(ClassDefinition.fromQml(filename=enmapboxtestdata.landcover_points.replace('.shp', '.qml')))


        print(ClassDefinition.fromENVIClassification(raster=enmapClassification))
        print(ClassDefinition.fromGDALMeta(raster=enmapClassification))
        print(ClassDefinition(colors=['orange', 'blue', 'grey', 'snow', 'white']))
        print(ClassDefinition(classes=3))
        classDefinition1 = ClassDefinition(classes=3)
        classDefinition2 = ClassDefinition(classes=3)
        self.assertTrue(classDefinition1.equal(classDefinition2, compareColors=False))
        self.assertFalse(classDefinition1.equal(classDefinition2, compareColors=True))
        classDefinition1.color(label=1)
        print(ClassDefinition(colors=['blue'], names=['Class 1']).colorByName(name='Class 1'))
        print(ClassDefinition(colors=['blue'], names=['Class 1']).labelByName(name='Class 1'))
        ClassDefinition(classes=3).labels()

    def test_Classifier(self):

        enmap = Raster(filename=enmapboxtestdata.enmap)
        classification = Classification.fromClassification(classification=vectorClassification,
                                                           grid=enmap.grid(),
                                                           filename='/vsimem/classification.bsq')
        sample = ClassificationSample(raster=enmap, classification=classification)
        rfc = Classifier(sklEstimator=RandomForestClassifier())
        rfc.fit(sample=sample)
        rfc.predict(raster=enmap, filename='/vsimem/rfcClassification.bsq')
        rfc.crossValidation().report().saveHTML(filename=join(outdir, 'report.html'), open=False)

        rfc = Classifier(sklEstimator=RandomForestClassifier())
        print(rfc)
        rfc.fit(sample=enmapClassificationSample)
        enmapClassificationSample.raster().dataset()
        enmapClassificationSample.classification().dataset()

        rfc.pickle(filename=join(outdir, 'classifier.pkl'))
        print(rfc.predict(filename=join(outdir, 'rfcClassification.bsq'), raster=enmap, mask=vector))
        print(rfc.predictProbability(filename=join(outdir, 'rfcProbability.bsq'), raster=enmap, mask=vector))

    def test_Clusterer(self):
        kmeans = Clusterer(sklEstimator=KMeans())
        print(kmeans)
        kmeans.fit(sample=enmapClassificationSample)
        print(kmeans.predict(filename=join(outdir, 'kmeansClustering.bsq'), raster=enmap, mask=vector))
        kmeans.classDefinition()

    def test_ClusteringPerformance(self):
        clusteringPerformance = ClusteringPerformance.fromRaster(prediction=enmapClassification,
                                                                 reference=enmapClassification)
        print(clusteringPerformance)
        clusteringPerformance.report().saveHTML(filename=join(outdir, 'reportClusteringPerformance.html'), open=openHTML)

    def test_FlowObject(self):
        enmap.dataset().gdalDataset()
        enmapClassification.dataset().gdalDataset()
        vector.dataset().ogrLayer()
        enmapMask.dataset().gdalDataset()
        sample = ClassificationSample(raster=enmap, classification=enmapClassification, mask=vector)
        rfc = Classifier(RandomForestClassifier(oob_score=True)).fit(sample)
        #rfc.browse()

    def test_Raster(self):

        # subset bands
        raster = enmap.subsetBands(indices=[1, -1], invert=False, filename=join(outdir, 'sub1.bsq'))
        raster = enmap.subsetBands(indices=[1, -1], invert=True, filename=join(outdir, 'sub2.bsq'))

        print(raster)

        # from array
        raster = Raster.fromArray(array=[[[-1, 1, 2, np.inf, np.nan]]], filename='/vsimem/raster.bsq',
                                  noDataValues=[-9], descriptions=['band 1'])
        print(raster.asMask(noDataValues=[-1]).array())

        raster.dataset().setNoDataValue(-1)
        statistics = raster.statistics(calcMean=True, calcStd=True, calcPercentiles=True, percentiles=[0,50,100],
                                       calcHistogram=True, histogramRanges=[(1,3)], histogramBins=[2])
        print(statistics)
        assert statistics[0].min == 1
        assert statistics[0].max == 2
        assert statistics[0].nvalid == 2
        assert statistics[0].ninvalid == 3
        print(raster)

        # apply mask
        enmapMaskInv = Mask(filename=enmapMask.filename(), invert=not True)
        enmapMaskInv = VectorMask(filename=vectorClassification.filename(), invert=True)

        print(enmapClassification.applyMask(filename=join(outdir, 'ClassificationApplyMask.bsq'), mask=enmapMaskInv))
        cl = Classification(filename=join(outdir, 'ClassificationApplyMask.bsq'))
        #cl.dataset().plotCategoryBand()

        # apply spatial function
        from scipy.ndimage.filters import median_filter
        function = lambda array: median_filter(input=array, size=(3,3))
        print(enmap.applySpatial(join(outdir, 'RasterApplySpatial.bsq'), function=function))

        # convolution
        from astropy.convolution import Gaussian2DKernel, Kernel1D
        # 2d
        kernel = Gaussian2DKernel(x_stddev=1)
        print(enmapRegression.convolve(filename=join(outdir, 'RasterConvolveSpatial.bsq'), kernel=kernel))

        # 1d
        from scipy.signal import  savgol_coeffs
        kernel = Kernel1D(array=savgol_coeffs(window_length=11, polyorder=3, deriv=1))
        print(enmap.convolve(filename=join(outdir, 'RasterConvolveSpectral.bsq'), kernel=kernel))



        # from speclib
        print(Raster.fromEnviSpectralLibrary(filename=join(outdir, 'RasterFromEnviSpectralLibrary.bsq'),
                                             library=speclib))

        print(enmapClassification.uniqueValues(index=0))

        # resampling
        print(enmap)
        print(enmap.resample(filename=join(outdir, 'RasterResample.bsq'), grid=enmap.grid().atResolution(10), resampleAlg=gdal.GRA_Average))


        print(Raster.fromVector(filename=join(outdir, 'RasterFromVector.bsq'), vector=vectorClassification, grid=enmap.grid(),
                                overwrite=overwrite))
        print(enmap.statistics(bandIndicies=None, mask=vector, grid=enmap))

        bandIndicies = 0, 1

        statistics = enmap.statistics(bandIndicies=bandIndicies, calcPercentiles=True, calcHistogram=True, calcMean=True,
                               calcStd=True, mask=enmapMask)
        statistics = enmap.statistics(mask=vector)

        H, xedges, yedges = enmap.scatterMatrix(raster2=enmap, bandIndex1=bandIndicies[0], bandIndex2=bandIndicies[1],
                                                range1=(statistics[0].min, statistics[0].max),
                                                range2=(statistics[1].min, statistics[1].max),
                                                bins=10, mask=vector)
        print(H)

        H, xedges, yedges = enmap.scatterMatrix(raster2=enmap, bandIndex1=bandIndicies[0], bandIndex2=bandIndicies[1],
                                                stratification=enmapClassification,
                                                range1=(statistics[0].min, statistics[0].max),
                                                range2=(statistics[1].min, statistics[1].max),
                                                bins=10, mask=vector)
        print(H)

    # def test_RasterStack(self):
    #     rasterStack = RasterStack(rasters=[enmap, enmap])
    #     for raster in rasterStack.rasters():
    #         print(raster)
    #     print(rasterStack)
    #
    #     import enmapboxtestdata
    #
    #     raster = RasterStack(rasters=[Raster.fromArray(array=[[[1, 1], [1, 1]]], filename='/vsimem/raster1.bsq'),
    #                                        Raster.fromArray(array=[[[2, 2], [2, 2]]], filename='/vsimem/raster2.bsq')])
    #
    #     applier = Applier(progressBar=SilentProgressBar())
    #     applier.setFlowRaster(name='stack', raster=raster)
    #
    #     class MyOperator(ApplierOperator):
    #         def ufunc(self, raster):
    #             array = self.flowRasterArray(name='stack', raster=raster)
    #             print(array)
    #
    #     applier.apply(operatorType=MyOperator, raster=raster)

    def test_MapCollection(self):

        mapCollection = MapCollection(maps=[enmap, enmapClassification, enmapRegression, enmapFraction, vector, vectorClassification])
        filenames = [join(outdir, 'MapCollectionExtractAsRaster_{}.bsq'.format(type(map).__name__)) for map in mapCollection.maps()]
        rasters = mapCollection.extractAsRaster(filenames=filenames, grid=enmap.grid(), masks=[vector], onTheFlyResampling=True)
        for raster in rasters:
            print(raster)

    def test_Mask(self):
        print(enmapClassification.asMask().resample(filename=join(outdir, 'MaskResample.bsq'), grid=enmap))

        print(Mask.fromVector(filename=join(outdir, 'maskFromVector.bsq'), vector=vector, grid=enmap))
        print(Mask.fromRaster(filename=join(outdir, 'maskFromRaster.bsq'), raster=enmapClassification,
#                              trueRanges=[(1, 100)], trueValues=[1, 2, 3],
                              true=[range(1, 100), 1, 2, 3],
#                              falseRanges=[(-9999, 0)], falseValues=[-9999]))
                              false = [range(-9999, 0), -9999]))

    def test_Fraction(self):

        print(enmapFraction)
        fraction = Fraction(filename=enmapFraction.filename(), minOverallCoverage=0, minDominantCoverage=0)
        print(fraction.resample(filename=join(outdir, 'FractionResample.bsq'),
                                grid=enmapClassification.grid(), controls=ApplierControls()))#.setBlockFullSize()))


        print(Fraction.fromClassification(filename=join(outdir, 'enmapFraction.bsq'),
                                          classification=vectorClassification, grid=enmap.grid()))
        print(enmapFraction.asClassColorRGBRaster(filename=join(outdir, 'fractionAsClassColorRGBImage.bsq')))

        print(enmapFraction.subsetClassesByName(filename=join(outdir, 'fractionSubsetClassesByName.bsq'),
                                                   names=enmapFraction.classDefinition().names()))

    def test_FractionPerformance(self):
        fractionPerformance = FractionPerformance.fromRaster(prediction=enmapFraction, reference=enmapClassification)
        print(fractionPerformance)
        fractionPerformance.report().saveHTML(filename=join(outdir, 'reportFractionPerformance.html'), open=openHTML)


    def test_FractionSample(self):

        print(enmapFractionSample)
        features, labels = enmapFractionSample.extractAsArray()
        print(features.shape, labels.shape)

        # init
        fractionSample = FractionSample(raster=enmap, fraction=enmapFraction, grid=enmap.grid())
        print(fractionSample)
        print(fractionSample.raster().dataset().shape())
        print(fractionSample.fraction().dataset().shape())


    def test_Regression(self):

        enmapRegressionSample.raster()
        enmapRegressionSample.regression()
        #print(Regression.fromEnviSpectralLibrary(filename=join(outdir, 'RegressionFromEnviSpectralLibrary.bsq'),
        #                                         library=speclib2, attributes=['Roof', 'Low vegetation']))

        print(enmapRegression.asMask())
        print(enmapRegression.resample(filename=join(outdir, 'RegressionResample.bsq'), grid=enmap.grid().atResolution(10)))


    def test_RegressionPerformance(self):
        print(enmapRegression.filename())
        print(enmapRegression)

        #mask = Vector.fromRandomPointsFromMask(filename=join(outdir, 'random.shp'), mask=enmapMask, n=10)
        #maskInverted = Vector(filename=mask.filename(), initValue=mask.burnValue(), burnValue=mask.initValue())

        if True:
            rfr = Regressor(sklEstimator=RandomForestRegressor())
            rfr.fit(sample=enmapRegressionSample)
            reference = rfr.predict(filename='/vsimem/rfrRegression.bsq', raster=enmap)
        else:
            reference = enmapRegression

        obj = RegressionPerformance.fromRaster(prediction=enmapRegression, reference=reference)
        print(obj)
        obj.report().saveHTML(filename=join(outdir, 'RegressionPerformance.html'), open=openHTML)

    def test_RegressionSample(self):

        sample = RegressionSample(raster=enmap, regression=enmapFraction)

        print(enmapRegressionSample)
        features, labels = enmapRegressionSample.extractAsArray()
        print(features.shape, labels.shape)

        # init
        regressionSample = RegressionSample(raster=enmap, regression=enmapFraction, mask=vector)
        print(regressionSample)

    def test_Regressor(self):

        rfr = Regressor(sklEstimator=RandomForestRegressor())
        print(rfr)
        rfr.fit(sample=enmapRegressionSample)
        print(rfr.predict(filename=join(outdir, 'rfrRegression.bsq'), raster=enmap, mask=vector))

    def test_Sample(self):

        # init
        sample = Sample(raster=enmap, mask=vector)
        print(sample)
        sample.extractAsArray(onTheFlyResampling=True)
        sample.extractAsRaster(filenames=['/vsimem/raster.bsq'], onTheFlyResampling=True)

    def test_Transformer(self):
        pca = Transformer(sklEstimator=PCA())
        print(pca)
        pca.fit(sample=enmapSample)
        pcaTransformation = pca.transform(filename=join(outdir, 'pcaTransformation.bsq'), raster=enmap, mask=vector)
        print(pcaTransformation)
        pcaInverseTransform = pca.inverseTransform(filename=join(outdir, 'pcaInverseTransformation.bsq'),
                                                   raster=pcaTransformation, mask=vector)
        print(pcaInverseTransform)

    def test_Vector(self):

        #vector = Vector(filename=r'C:\output\LandCov_BerlinUrbanGradient_WGS84.gpkg|layername=polygons')
        #Raster.fromVector(filename=r'c:\output\test.bsq', vector=vector, grid=enmap.grid())

        print(vector.uniqueValues(attribute='level_2_id'))
        print(vector.uniqueValues(attribute='level_2'))
        print(vector)
        print(Vector.fromRandomPointsFromMask(filename=join(outdir, 'vectorFromRandomPointsFromMask.gpkg.shp'), mask=enmapMask,
                                              n=10))
        n = [10] * enmapClassification.classDefinition().classes()
        print(
        Vector.fromRandomPointsFromClassification(filename=join(outdir, 'vectorFromRandomPointsFromClassification.gpkg'),
                                                  classification=enmapClassification, n=n))
        Vector.fromVectorDataset(vectorDataset=vector.dataset())
        Vector.fromPoints(filename='/vsimem/vector.shp', points=[Point(0, 0, Projection.wgs84())])
        vector.metadataDict()
        vector.metadataItem(key='a', domain='')
        vector.extent()
        vector.projection()
        vector.grid(resolution=1)
    def test_VectorMask(self):
        print(VectorMask(filename=vector.filename(), invert=False))

    def test_VectorClassification(self):
        print(VectorClassification(filename=enmapboxtestdata.landcover_polygons, classAttribute='level_2_id'))
        print(VectorClassification(filename=enmapboxtestdata.landcover_points, classAttribute='level_2_id'))

    def test_extractPixels(self):
        c = ApplierControls()
        extractPixels(inputs=[enmap, enmapFraction, enmapClassification, enmapRegression, vector, vectorClassification],
                      masks=[enmapMask], grid=enmap.grid(), controls=c)

    def test_applierMultiprocessing(self):

        c = ApplierControls()
        c.setBlockSize(25)
        c.setNumThreads(2)

        rfc = Classifier(sklEstimator=RandomForestClassifier())
        print(rfc)
        rfc.fit(sample=enmapClassificationSample)
        print(rfc.predict(filename=join(outdir, 'rfcClassification.bsq'), raster=enmap, mask=vector, controls=c))


    def test_pickle(self):

        def printDataset(obj):
            if isinstance(obj, Raster): print(obj._rasterDataset)
            elif isinstance(obj, Vector): print(obj._vectorDataset)
            else: pass

        for obj in objects:
            print(type(obj))
            if isinstance(obj, Map): obj.dataset()
            filename = join(outdir, 'pickle.pkl')
            printDataset(obj)
            obj.pickle(filename=filename)
            obj2 = obj.unpickle(filename=filename)
            printDataset(obj2)
            print(obj2)

    def test_repr(self):
        for obj in objects:
            print(type(obj))
            print(obj)

    def test_map_array(self):

        for map in rasterMaps:
            print(type(map))
            print(map.array()[0,30:40,30:40])

    def test_ApplierOptions(self):
        print(ApplierOptions())

    def test_debug(self):
        import hubflow.core

        newNames = ['No Class', 'Class B']
        newColors = [QColor('black'), QColor('yellow')]

        # but this fails
        newDef = hubflow.core.ClassDefinition(names=newNames[1:], colors=newColors[1:])
        newDef.setNoDataNameAndColor(newNames[0], QColor('yellow'))
        print(newDef)

    def test_uniqueValueCounts(self):
        import numpy as np
        x = np.array([np.inf, np.nan, 1, 1, 1, 2, 2, 5.5])
        values = np.unique(x)
        for v in values:
            if np.isnan(v):
                print(v, np.sum(np.isnan(x)))
            else:
                print(v, np.sum(x==v))

class TestEnviSpectralLibrary(TestCase):

    def test(self):

        # init
        speclib = EnviSpectralLibrary(filename=enmapboxtestdata.library)
        print(speclib)
        print(speclib.profiles())
        print(speclib.raster().dataset().metadataDict())

        print(speclib.attributeNames())
        print(speclib.attributeDefinitions())
        print(speclib.attributeTable())

        # speclib from raster
        speclib = EnviSpectralLibrary.fromRaster(filename=join(outdir, 'EnviSpectralLibraryFromRaster.sli'),
                                                 raster=enmap)
        print(speclib)
        print(speclib.raster().dataset().shape())

        raster = speclib.raster(transpose=False)
        print(raster.dataset().shape())
        raster.dataset().plotXProfile(row=Row(y=0, z=0))

        raster = speclib.raster(transpose=True)
        print(raster.dataset().shape())
        raster.dataset().plotZProfile(pixel=Pixel(x=0, y=0), spectral=True)

    def test_fromClassificationSample(self):
        classification = Classification.fromClassification(classification=vectorPoints, grid=enmap.grid(),
                                                           filename='/vsimem/classification.bsq')
        sample = ClassificationSample(raster=enmap, classification=classification)
        outdir = r'c:\test'
        speclib = EnviSpectralLibrary.fromSample(sample=sample, filename=join(outdir, 'speclib.sli'))
        print(speclib)
        classification2 = Classification.fromEnviSpectralLibrary(filename='/vsimem/classification.bsq', library=speclib,
                                                                 attribute='id')
        assert classification.classDefinition().equal(classification2.classDefinition())

    def test_plot(self):
        speclib = EnviSpectralLibrary(filename=enmapboxtestdata.library)

        import pyqtgraph as pg
        import pyqtgraph.exporters
        plot = pg.plot()
        for y in range(speclib.raster().dataset().ysize()):
            speclib.raster().dataset().plotZProfile(pixel=Pixel(x=0, y=y), spectral=True, plotWidget=plot)
        exporter = pyqtgraph.exporters.ImageExporter(plot.plotItem)
        # workaround a bug with float conversion to int
        exporter.params.param('width').setValue(600, blockSignal=exporter.widthChanged)
        exporter.params.param('height').setValue(400, blockSignal=exporter.heightChanged)
        exporter.export(join(outdir, 'plot.png'))

class TestRaster(TestCase):

    def test_saveAs(self):
        raster = Raster(enmapboxtestdata.enmap)
        copy = raster.saveAs(filename='c:/vsimem/raster.tif', driver=None)


if __name__ == '__main__':
    print('output directory: ' + outdir)
