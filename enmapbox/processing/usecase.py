from __future__ import print_function

__author__ = 'janzandr'
import os
from enmapbox.processing.types import Type, Meta, VectorClassification, PixelGrid, Image, Mask, Probability, Classification, Regression, SupervisedSample, PixelExtractor, Regressor, Classifier, Clusterer, Transformer
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
    pixelGrid = Image(r'C:\Work\data\EnMAPUrbanGradient2009\01_image_products\EnMAP02_Berlin_Urban_Gradient_2009.bsq').pixelGrid
    blank = pixelGrid.createImage(bands=5, filename=r'C:\Work\data\___test.img', of='ENVI', ot='Byte', fill=0)

def workflow_colloquium2016():

    enmap = Image(r'C:\Work\data\EnMAPUrbanGradient2009\01_image_products\EnMAP02_Berlin_Urban_Gradient_2009.bsq')
    vector = VectorClassification(filename=r'C:\Work\data\EnMAPUrbanGradient2009\02_additional_data\land_cover\LandCov_Vec_Berlin_Urban_Gradient_2009.shp',
                                  idField='ID_L2', nameField='Level_2', colorField = 'RGB_L2', parse=True)

    pixelGridTagret = enmap.pixelGrid
    pixelGridOversampled = pixelGridTagret.newResolution(resolution=3)

    # create class occurence image at finer resolution
    occurrenceC = vector.asClassification(pixelGrid=pixelGridOversampled, filename=r'c:\work\data\__class_occurrenceC.tif')
    occurrenceP = occurrenceC.asProbability(filename=r'c:\work\data\__class_occurrenceP.tif')

    occurrenceP_RGB = occurrenceP.rgbClassColorComposite(filename=r'c:\work\data\__class_occurrenceP_rgb.tif')

    # create class fraction image at target resolution
    fraction = occurrenceP.resample(filename=r'c:\work\data\__class_fraction.vrt', pixelGrid=enmap.pixelGrid)
    fractionRGB = fraction.rgbClassColorComposite(filename=r'c:\work\data\__class_fraction_rgb.img')

    # create classification sample and map
    '''trainC = fraction.argmaxProbabilityClassification(filename=r'c:\work\data\__class_win50_cum50.img', minWinProb=0.5, minCumProb=0.5)
    rfc_proba = Classifiers.RandomForestClassifier(n_estimators=100).fit(image=enmap, labels=trainC).predictProbability(image=enmap, filename=r'c:\work\data\__rfc_proba')
    rfc_probaRGB = rfc_proba.rgbClassColorComposite(filename=r'c:\work\data\__rfc_proba_rgb')
    rfc_map = rfc_proba.argmaxProbabilityClassification(filename=r'c:\work\data\__rfc_class')'''

    # create regression sample and map
    trainC = fraction.argmaxProbabilityClassification(filename=r'c:\work\data\__class_win00_cum90.img', minWinProb=0., minCumProb=0.9)
    trainR = fraction.applyMask(mask=trainC, value=-1, filename=r'c:\work\data\__regress_win00_cum90.img')
    trainR.rgbClassColorComposite(filename=r'c:\work\data\__regress_win00_cum90_rgb')

    rfr = Regressors.RandomForestRegressor(n_estimators=100)
    rfr.fit(image=enmap, labels=trainR)
    rfr_fraction = rfr.predict(image=enmap, filename=r'c:\work\data\__rfr_fraction').asProbability()
    frf_fractionRGB = rfr_fraction.rgbClassColorComposite(filename=r'c:\work\data\__rfr_fraction_rgb')
    rfr_map = rfr_fraction.argmaxProbabilityClassification(filename=r'c:\work\data\__rfr_class')

    # craete maps

    print('done')



def workflow_colloquium2016_short():

    enmap = Image(filename='EnMAP02_Berlin_Urban_Gradient_2009.bsq')
    vector = VectorClassification(filename='LandCov_Vec_Berlin_Urban_Gradient_2009.shp')

    pixelGridEnMAP = enmap.pixelGrid
    pixelGridOversampled = pixelGridEnMAP.newResolution(resolution=3)

    train = vector.createOccurrence(pixelGrid=pixelGridEnMAP, oversamplingRate=10)\
        .resample(pixelGrid=enmap.pixelGrid)\
        .argmaxProbabilityClassification(minWinProb=0.5, minCumProb=0.5)

    classification = Classifiers.RandomForestClassifier(n_estimators=100).fit(image=enmap, labels=train)\
        .predictProbability(image=enmap)\
        .rfc_proba.argmaxProbabilityClassification()

def workflow_colloquium2016_short2():

    enmap = Image(filename='EnMAP02_Berlin_Urban_Gradient_2009.bsq')
    vector = VectorClassification(filename='LandCov_Vec_Berlin_Urban_Gradient_2009.shp')

    pixelGridEnmap = enmap.pixelGrid
    pixelGridOversampled = pixelGridEnmap.newResolution(resolution=3)

    fractions = vector.asClassification(pixelGrid=pixelGridOversampled)\
        .asProbability()\
        .resample(pixelGrid=pixelGridEnmap)
    mask = fractions.argmaxProbabilityClassification(minCumProb=0.9)
    train = fractions.applyMask(mask=mask)

    mappedFractions = Regressors.RandomForestRegressor(n_estimators=100)\
        .fit(image=enmap, labels=train)\
        .predict(image=enmap)
    mappedLandCover = mappedFractions.asProbability().argmaxProbabilityClassification()



    a=mappedLandCover

def image():
    image = Image(os.path.join(inroot, 'Hymap_Berlin-A_Image'))
    #image = Image(r'C:\Work\data\test\cfmask.tif')

    image.info()

def importENVISpeclib():
    pseudoImage = Image.fromENVISpectralLibrary(r'C:\Work\data\ClassificationSpeclib')
    pseudoImage.info()

def classification():


    image = Image(os.path.join(inroot, 'Hymap_Berlin-A_Image'))
    mask =  Image(os.path.join(inroot, 'Hymap_Berlin-A_Mask'))
    labels = Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-Training-Sample'))

    Classifiers.RandomForestClassifier(n_estimators=100).fit(image, labels)\
        .predictProbability(image, filename=r'c:\work\_prob.tif')\
        .rgbClassColorComposite(filename=r'c:\work\_rgb.tif')
    return

    classifiers = [Classifiers.RandomForestClassifier(n_estimators=100)]
    #classifiers = [Classifiers.DummyClassifier()]
    #classifiers = [Classifiers.SVCTuned()]
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

def probabilityToRGB():


    image = Image(os.path.join(inroot, 'Hymap_Berlin-A_Image'))
    train = Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-Training-Sample'))

    classifier = Classifiers.RandomForestClassifier(oob_score=True, n_estimators=100).fit(image, train)
    probability = classifier.predictProbability(image, filename=r'c:\work\data\___rfc_prob.img')
    classification = probability.argmaxProbabilityClassification(filename=r'c:\work\data\___rfc_class.img')
    rgb = probability.rgbClassColorComposite(filename=r'c:\work\data\___rfc_rgb.img')

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
    classification = propability.argmaxProbabilityClassification()

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

def recode_classification_scheme():

    classification1 = Classification(os.path.join(inroot, r'C:\Work\data\Hymap_Berlin-A_Classification-GroundTruth'))

    # existing classification scheme from classification1
    # - get the following infos from the file
    #   class_names = ['unclassified', 'vegetation', 'built-up', 'impervious', 'pervious', 'water']
    #   class lookup = [0, 0, 0, 0, 255, 0, 255, 0, 0, 255, 255, 0, 0, 255, 255, 0, 0, 255]

    classes1, class_names1, class_lookup1 = classification1.meta.getClassificationMetadata()

    # do the recoding in an interactive dialog
    # in this example, we want to map the existing classification scheme into the new classification scheme:
    #   class_names =  ['unclassified', 'artifical', 'nature']
    #   class lookup = [0, 0, 0,        255, 0, 0,   0, 255, 0]
    #
    # ids are mapped this way:
    # - unclassified (0) -> unclassified (0)
    # - vegetation (1) -> nature (2)
    # - built-up (2) -> artifical (1)
    # - impervious (3) -> artifical (1)
    # - pervious(4) -> nature (2)
    # - water (5) -> nature (2)

    def dialog(class_names, class_lookup):

        new_class_names  = ['unclassified', 'artifical', 'nature']
        new_class_lookup = [0,0,0,          255,0,0,     0,255,0]
        new_ids = {0:0, 1:2, 2:1, 3:1, 4:2, 5:2} # keys are the old IDs and the values are new IDs

        return new_class_names, new_class_lookup, new_ids


    class_names2, class_lookup2, ids2 = dialog(class_names1, class_lookup1)

    classification2 = classification1.recode(class_names2, class_lookup2, ids2, filename=r'c:\work\data\__classRecoded.img')


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

def warp_stack():
    from os.path import join
    from hub.file import filesearch
    from hub.gdal.util import gdalbuildvrt, gdalwarp
    from hub.gdal.api import GDALMeta

    # set paths
    root = r'C:\Users\janzandr\Desktop\class_full22112016'
    outfile = join(root, 'mosaick.vrt')
    infilesUTM = filesearch(dir=root, pattern='classification.bsq')
    infilesEPSG3035 = [infile.replace('.bsq', '_warped.vrt') for infile in infilesUTM]

    # warp to EPSG:3035
    for infileUTM, infileEPSG3035 in zip(infilesUTM, infilesEPSG3035):
        gdalwarp(outfile=infileEPSG3035, infile=infileUTM, options='-of VRT -t_srs EPSG:3035 -overwrite -tr 30 30')

    # mosaick
    gdalbuildvrt(outfile=outfile, infiles=infilesEPSG3035)

    # set meta data
    inmeta = GDALMeta(infilesUTM[0]) # take meta from first file
    outmeta = GDALMeta(outfile)
    outmeta.setClassificationMetadata(*inmeta.getClassificationMetadata())
    outmeta.writeMeta()


if __name__ == '__main__':

    #tic()
    #importENVISpeclib()
    #test_type()
    workflow_colloquium2016()
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
    #probabilityToRGB()
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
    #recode_classification_scheme()

    #toc()