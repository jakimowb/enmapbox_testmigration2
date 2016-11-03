from __future__ import print_function

__author__ = 'janzandr'
import os
from enmapbox.processing.types import Type, Vector, Image, Mask, Classification, Regression, SupervisedSample, PixelExtractor, Regressor, Classifier, Clusterer, Transformer
from enmapbox.processing.estimators import Classifiers, Regressors, Transformers, Clusterers
from hub.timing import tic, toc
from copy import deepcopy

from enmapbox.processing.environment import PrintProgress as Progress

if os.environ['USERNAME'] == 'janzandr':
    inroot = r'c:\work\data'
    outroot = r'c:\work\outputs'
elif os.environ['USERNAME'] == 'enmap-box':
    inroot = r'C:\Program Files\EnMAP-Box\enmapProject\lib\hubAPI\resource\testData\image'
    #inroot = r'C:\Users\enmap-box\Desktop'
    #inroot = r'C:\Program Files\EnMAP-Box\enmapProject\enmapBox\resource\testData\image'
    outroot = r'C:\Users\enmap-box\Desktop\outputs'

def sample():

    image = Image(os.path.join(inroot, 'Hymap_Berlin-A_Image'))
    test = Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-Validation-Sample'))
    sample = SupervisedSample.fromMask(image, test)
    print(sample.isClassificationSample())
    print(sample.labelSample.filename)
    print(sample.featureSample.filename)

def test_type():


    image = Type()
    image.report().saveHTML().open()

    return
    labels = Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-Training-Sample'))
    classifier = Classifiers.SVCTuned()
    classifier = classifier.fit(image, labels)
    print(classifier.getMetadataDict())

def pixel_grid():

    hymap = Image(r'C:\Work\data\EnMAPUrbanGradient2009\01_image_products\HyMap01_Berlin_Urban_Gradient_2009.bsq')
    enmap = Image(r'C:\Work\data\EnMAPUrbanGradient2009\01_image_products\EnMAP02_Berlin_Urban_Gradient_2009.bsq')
    vector = Vector(r'C:\Work\data\EnMAPUrbanGradient2009\02_additional_data\land_cover\LandCov_Vec_Berlin_Urban_Gradient_2009.shp')

    # ToDo: use only the polygon extents to calculate fractions, otherwise edge pixel will be wrong!
    print('ToDO: handle edges corretly!')

    # rasterize vector file with oversampling and resample back to original resolution to produce cover fractions
    options = '''-where "Level_2"='Tree' -burn 1 -init 0 -a_nodata 0 -of GTiff -ot Byte'''
    pixelGrid = deepcopy(enmap.pixelGrid)
    pixelGrid.xRes /= 20
    pixelGrid.yRes /= 20
    #rasterOversampled = vector.rasterize(outfile=r'c:\work\data\raster.img', pixelGrid=pixelGrid, options=options)
    rasterOversampled = Image(r'c:\work\data\raster.img')

    rasterFractions = rasterOversampled.translate(filename=r'c:\work\data\rasterEnMAP.vrt', pixelGrid=enmap.pixelGrid)

    # create classification file from
    #raster = vector.rasterize(outfile=r'c:\work\data\raster5.img', pixelGrid=enmap.pixelGrid, options=options, oversamplingRate=20)


    #raster.info()

def image():
    image = Image(os.path.join(inroot, 'Hymap_Berlin-A_Image'))
    #image = Image(r'C:\Work\data\test\cfmask.tif')

    image.info()

def importENVISpeclib():
    pseudoImage = Image.importENVISpectralLibrary(r'C:\Work\data\ClassificationSpeclib')
    pseudoImage.info()

def classification():


    image = Image(os.path.join(inroot, 'Hymap_Berlin-A_Image'))
    mask =  Image(os.path.join(inroot, 'Hymap_Berlin-A_Mask'))
    labels = Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-Training-Sample'))

    #classifiers = [Classifiers.RandomForestClassifier(n_estimators=100)]
    #classifiers = [Classifiers.DummyClassifier()]
    classifiers = [Classifiers.SVCTuned()]
    # classifiers = all(Classifiers)

    for classifier in classifiers:
        assert isinstance(classifier, Classifier)
        Progress.setInfo(classifier.name())
        classifier = classifier.fit(image, labels, progress=Progress)
        classifier.report().saveHTML().open()
        classifier.pickle(filename=r'c:\work\rfc.model')
        continue
        classifier.predict(image, mask, filename=os.path.join(outroot, classifier.name()), progress=Progress)
        try:
            classifier.predictProbability(image, mask, filename=os.path.join(outroot, classifier.name()+'Proba'), progress=Progress)
        except:
            pass


def regression():

    image = Image(os.path.join(inroot, 'Hymap_Berlin-B_Image'))
    mask = Image(os.path.join(inroot, 'Hymap_Berlin-B_Mask'))
    trainingLabels = Regression(os.path.join(inroot, 'Hymap_Berlin-B_Regression-Training-Sample'))
    testingLabels = Regression(os.path.join(inroot, 'Hymap_Berlin-B_Regression-Validation-Sample'))

    #regressors = all(Regressors)
    #regressors = [Regressors.DummyRegressor()]
   # regressors = [Regressors.LinearSVRTuned()]
    regressors = [Regressors.RandomForestRegressor(oob_score=True)]

    for regressor in regressors:
        assert isinstance(regressor, Regressor)
        Progress.setInfo(regressor.name())
        regressor = regressor.fit(image, trainingLabels)
        regressor.report().saveHTML().open()
        regressor.predict(image, mask, filename=os.path.join(outroot, regressor.name()))


def clusterer():

    image = Image(os.path.join(inroot, 'Hymap_Berlin-A_Image'))
    mask = Image(os.path.join(inroot, 'Hymap_Berlin-A_Mask'))
    train = Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-Training-Sample'))
    test = Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-Validation-Sample'))

    #clusterers = all(Clusterers)
    clusterers = [Clusterers.KMeans(n_clusters=5)]
    #clusterers = [Clusterers.KMeans(n_clusters=5, with_mean=True, with_std=True)]

    for clusterer in clusterers:
        assert isinstance(clusterer, Clusterer)
        Progress.setInfo(clusterer.name())
        clusterer.fit(image, train).info()
        clusterer.predict(image, mask, filename=os.path.join(outroot, clusterer.name()))


def transformer():

    image = Image(os.path.join(inroot, 'Hymap_Berlin-A_Image'))
    mask = Mask(os.path.join(inroot, 'Hymap_Berlin-A_Mask'))
    trainingLabels = Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-Training-Sample'))

    #transformers = all(Transformers)
    #transformers = [Transformers.RobustScaler()]
    transformers = [Transformers.PCA(n_components=0.99999)]

    for transformer in transformers:

        assert isinstance(transformer, Transformer)
        Progress.setInfo(transformer.name())
        transformer.fit(image, trainingLabels).info()
        transformedImage = transformer.transform(image, mask, filename=os.path.join(outroot, transformer.name()))
        inverseTransformedImage = transformer.transformInverse(transformedImage, mask, filename=os.path.join(outroot, transformer.name()+'Inverse'))

def showEstimator():

    image = Image(os.path.join(inroot, 'Hymap_Berlin-A_Image'))
    labels = Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-Training-Sample'))
    pca = Transformers.PCA()
    pca.info()

def uncertaintyClassifier():

    image = Image(r'C:\Work\data\Hymap_Berlin-A_Image')
    mask =  Image(r'C:\Work\data\Hymap_Berlin-A_Mask')
    trainingLabels = Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Training-Sample')

    svc = Classifiers.SVCTuned()

    # false negatives
    uncertaintyClassifier = svc.UncertaintyClassifierFN()
    uncertaintyClassifier.fit(image, trainingLabels)
    uncertaintyClassifier.predict(image, filename=r'c:\work\_svcUncertaintyClassificationFN')
    uncertaintyClassifier.predictProbability(image, filename=r'c:\work\_svcUncertaintyProbabilityFN')

    # false positives
    uncertaintyClassifier = svc.UncertaintyClassifierFP()
    uncertaintyClassifier.fit(image, trainingLabels)
    uncertaintyClassifier.predict(image, filename=r'c:\work\_svcUncertaintyClassificationFP')
    uncertaintyClassifier.predictProbability(image, filename=r'c:\work\_svcUncertaintyProbabilityFP')


def uncertaintyRegressor():

    image = Image(r'C:\Work\data\Hymap_Berlin-B_Image')
    mask = Image(r'C:\Work\data\Hymap_Berlin-B_Mask')
    trainingLabels = Regression(r'C:\Work\data\Hymap_Berlin-B_Regression-Training-Sample')

    svr = Regressors.SVRTuned()
    uncertaintyRegressor = svr.UncertaintyRegressor()
    uncertaintyRegressor.fit(image, trainingLabels).report().saveHTML().open()
    uncertaintyRegressor.predict(image, mask, filename=r'c:\work\_svrUncertainty')

def classificationAccAss():

    testingLabels = Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-Validation-Sample'))
    prediction = Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-Estimation'))

    accAss = prediction.assessClassificationPerformance(classification=testingLabels, useRandomAccessReader=False)
    accAss.info()


def classificationAccAssAdjusted():

    test = Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-Validation-Sample'))
    prediction = Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-Estimation'))
    stratification = Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-GroundTruth'))
    accAss = prediction.assessClassificationPerformance(classification=test, stratification=stratification, useRandomAccessReader=False)
    accAss.report().saveHTML().open()


def regressionAccAss():
    testingLabels = Regression(os.path.join(inroot, 'Hymap_Berlin-B_Regression-Validation-Sample'))
    prediction = Regression(os.path.join(inroot, 'Hymap_Berlin-B_Regression-Estimation'))
    accAss = prediction.assessRegressionPerformance(prediction)
    accAss.report().saveHTML().open()


def clusteringAccAss():

    testingLabels = Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-Validation-Sample'))
    prediction = Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-Estimation'))

    accAss = prediction.assessClusteringPerformance(testingLabels)
    accAss.info()


def probabilityAccAss():


    image = Image(os.path.join(inroot, 'Hymap_Berlin-A_Image'))

    trainingLabels = Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-Training-Sample'))
    testingLabels = Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-Validation-Sample'))

    classifier = Classifiers.RandomForestClassifier().fit(image, trainingLabels)
    probability = classifier.predictProbability(image, testingLabels)
    accAss = probability.assessProbabilityPerformance(testingLabels)
    accAss.report().saveHTML().open()


def statisticsForImage():

    #image = Image(os.path.join(inroot, 'AF_Image'))
    image = Image(os.path.join(inroot, 'Hymap_Berlin-B_Image'))
    image.statistics().info()

def statisticsForClassification():

    #image = Classification(os.path.join(inroot,  'AF_LC'))
    image = Classification(os.path.join(inroot,  'Hymap_Berlin-A_Classification-Training-Sample'))
    image.statistics().info()

def saveImageAs():

    image = Image(r'C:\Work\data\Hymap_Berlin-A_Image')
    image.saveAs(r'c:\work\saved').info()


def stackImages():

    imageA = Image(r'C:\Work\data\Hymap_Berlin-A_Image')
    imageB = Image(r'C:\Work\data\Hymap_Berlin-B_Image')
    stack = imageA.stack([imageB])
    stack.info()
#    image.saveAs(r'c:\work\saved').report().saveHTML().open()

def projectImageToPixelGrid():

    imageA = Image(r'C:\Work\data\Hymap_Berlin-A_Image')
    imageB = Image(r'C:\Work\data\Hymap_Berlin-B_Image')
    imageSpot = Image(r'C:\Work\data\Spot_Berlin')
    pixelGrid = imageSpot.PixelGrid
    newImage = pixelGrid.project(imageA)#, imageB.BoundingBox)
    newImage.report().saveHTML().open()

def maximumProbability():

    image = Image(os.path.join(inroot, 'Hymap_Berlin-A_Image'))
    trainingLabels = Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-Training-Sample'))
    mask = Mask(r'C:\Work\data\Hymap_Berlin-A_Mask')
    classifier = Classifiers.RandomForestClassifier()
    classifier = classifier.fit(image, labels=trainingLabels)
    propability = classifier.predictProbability(image, mask=mask)
    classification = propability.argmax()

def pixel_extractor():

    image = Image(os.path.join(inroot, 'Hymap_Berlin-A_Image'))
    train = Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-Training-Sample'))

    labelSample1 = PixelExtractor(train).extractByMask(train)
    labelSample2 = PixelExtractor(train).extractByPixelLocation(train.getLocations())
    for y1,y2 in zip(labelSample1.dataSample.data, labelSample2.dataSample.data):
        print(y1,y2)

    return
    y1 = PixelExtractor(image).extractByMask(train).maskData

    y2 = PixelExtractor(train).extractByPixelLocation(imageSample.locations).imageData.flatten()
    import numpy
    print(numpy.all(y1==y2))


def pixel_extractor_image():

    image = Image(os.path.join(inroot, 'Hymap_Berlin-A_Image'))
    mask = Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-Training-Sample'))
    image.extractByMask(mask).info()



def ar_debug():

    from enmapbox.processing.types import unpickle
    image = Image(os.path.join(inroot, 'Hymap_Berlin-A_Image'))
    trainingLabels = Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-Training-Sample'))
    mask = Mask(r'C:\Work\data\Hymap_Berlin-A_Mask')
    trf = Transformers.PCA()
    trf = trf.fit(image, labels=None)
    transformation = trf.transform(image)

def ar_debug2():

    import numpy, gdal
    filename = r'C:\Work\data\test\myimage.img'
    samples = 500
    lines = 200
    bands = 3
    data = numpy.full((100,100), 1, dtype=numpy.int32)

    # create file, set some meta infos to the ENVI domain and close it
    driver = gdal.GetDriverByName('ENVI')
    ds = driver.Create(filename, samples, lines, bands, gdal.GDT_Int16)
    ds.SetMetadataItem('my_scalar', 'Hello World', 'ENVI')
    myArray = '{'+str([1,2,3,4,5])[1:-1]+'}'
    ds.SetMetadataItem('my_array', myArray, 'ENVI')
    ds = None

    # open it again, write data to xyoff = 0,0 and close it
    ds = gdal.Open(filename, gdal.OF_UPDATE)
    for rb in [ds.GetRasterBand(i+1) for i in range(bands)]:
        rb.WriteArray(array=data, xoff=0, yoff=0)
        rb.FlushCache()
    ds = None

    # open it again, write data to xyoff = 100,100 and close it
    ds = gdal.Open(filename, gdal.OF_UPDATE)
    for rb in [ds.GetRasterBand(i + 1) for i in range(bands)]:
        rb.WriteArray(array=data, xoff=100, yoff=100)
        rb.FlushCache()
    ds = None

def ar_debug3():

    import gdal

    # get geo infos from source file
    filename = r'C:\Work\data\gms\processed_mgrs_tiles\Landsat-8\OLI_TIRS\43\43SBD\LC81510322013152LGN00\OLI_TIRS__LC81510322013152LGN00__43SBD_mask_clouds_L2C.bsq'
    ds = gdal.Open(filename)
    projectionRef = ds.GetProjectionRef()
    geoTransform = ds.GetGeoTransform()
    ds = None

    # create new image
    filename = r'C:\Work\data\gms\processed_mgrs_tiles\Landsat-8\OLI_TIRS\43\43SBD\LC81510322013152LGN00\test.img'
    samples, lines, bands, type = 100, 100, 5, gdal.GDT_Int16
    driver = gdal.GetDriverByName('ENVI')
    ds = driver.Create(filename, samples, lines, bands, type)
    ds.SetProjection(projectionRef)
    ds.SetGeoTransform(geoTransform)
    ds = None

if __name__ == '__main__':

    #tic()
    #importENVISpeclib()
    #test_type()
    pixel_grid()
    #image()
    #sample()
    #enmapbox.processing.env.cleanupTempdir()
    #classification()
    #regression()
    #clusterer()
    #transformer()
    #showEstimator()
    #uncertaintyClassifier()
    #uncertaintyRegressor()
    #classificationAccAss()
    #classificationAccAssAdjusted()
    #regressionAccAss()
    #clusteringAccAss()
    #probabilityAccAss()
    #statisticsForImage()
    #statisticsForClassification()
    #importENVISpeclib()
    #saveImageAs()
    #stackImages()
    #projectImageToPixelGrid()
    #maximumProbability()
    #ar_debug3()
    #pixel_extractor()
    #pixel_extractor_image()

    #toc()