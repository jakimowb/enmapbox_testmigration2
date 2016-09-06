from __future__ import print_function

__author__ = 'janzandr'
import os
from enmapbox.processing.types import Image, Mask, Classification
import enmapbox.processing.estimators

from enmapbox.processing.environment import PrintProgress as Progress

if os.environ['USERNAME'] == 'janzandr':
    inroot = r'c:\work\data'
    outroot = r'c:\work\outputs'
elif os.environ['USERNAME'] == 'enmap-box':
    #inroot = r'C:\Program Files\EnMAP-Box\enmapProject\lib\hubAPI\resource\testData\image'
    inroot = r'C:\Users\enmap-box\Desktop'
    outroot = r'C:\Users\enmap-box\Desktop\outputs'

def sample():

    image = enmapbox.processing.types.Image(os.path.join(inroot, 'Hymap_Berlin-A_Image'))
    testingLabels = enmapbox.processing.types.Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-Validation-Sample'))
    sample = enmapbox.processing.types.ClassificationSample(image, testingLabels)
    print(sample.labelData.shape)
    print(sample.imageData.shape)

def image():
    image = Image(os.path.join(inroot, 'Hymap_Berlin-A_Image'))
    #image = Image(r'C:\Work\data\test\cfmask.tif')

    image.info()

def importENVISpeclib():
    pseudoImage = Image.importENVISpectralLibrary(r'C:\Work\data\ClassificationSpeclib')
    pseudoImage.info()

def classification():


    image = enmapbox.processing.types.Image(os.path.join(inroot, 'Hymap_Berlin-A_Image'))
    mask =  enmapbox.processing.types.Image(os.path.join(inroot, 'Hymap_Berlin-A_Mask'))
    labels = enmapbox.processing.types.Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-Training-Sample'))

    classifiers = [enmapbox.processing.estimators.Classifiers.RandomForestClassifier(n_estimators=100)]
    #classifiers = [enmapbox.processing.estimators.Classifiers.LinearSVCTuned()]
    #classifiers = [enmapbox.processing.estimators.Classifiers.SVCTuned(C=[1, 10, 100], gamma=[0.001, 100,1000])]
    # classifiers = enmapbox.processing.estimators.all(enmapbox.processing.estimators.Classifiers)

    for classifier in classifiers:
        assert isinstance(classifier, enmapbox.processing.types.Classifier)
        Progress.setInfo(classifier.name())
        classifier = classifier.fit(image, labels, progress=Progress)
        classifier.report().saveHTML().open()
        continue
        classifier.predict(image, mask, filename=os.path.join(outroot, classifier.name()), progress=Progress)
        try:
            classifier.predictProbability(image, mask, filename=os.path.join(outroot, classifier.name()+'Proba'), progress=Progress)
        except:
            pass


def regression():

    image = enmapbox.processing.types.Image(os.path.join(inroot, 'Hymap_Berlin-B_Image'))
    mask = enmapbox.processing.types.Image(os.path.join(inroot, 'Hymap_Berlin-B_Mask'))
    trainingLabels = enmapbox.processing.types.Regression(os.path.join(inroot, 'Hymap_Berlin-B_Regression-Training-Sample'))
    testingLabels = enmapbox.processing.types.Regression(os.path.join(inroot, 'Hymap_Berlin-B_Regression-Validation-Sample'))

    #regressors = enmapbox.processing.estimators.all(enmapbox.processing.estimators.Regressors)
    #regressors = [enmapbox.processing.estimators.Regressors.LinearSVRTuned()]
    #regressors = [enmapbox.processing.estimators.Regressors.SVRTuned()]
    regressors = [enmapbox.processing.estimators.Regressors.RandomForestRegressor(oob_score=True)]

    for regressor in regressors:
        assert isinstance(regressor, enmapbox.processing.types.Regressor)
        Progress.setInfo(regressor.name())
        regressor = regressor.fit(image, trainingLabels)
        regressor.report().saveHTML().open()
        regressor.predict(image, mask, filename=os.path.join(outroot, regressor.name()))


def clusterer():

    image = enmapbox.processing.types.Image(os.path.join(inroot, 'Hymap_Berlin-A_Image'))
    mask = enmapbox.processing.types.Image(os.path.join(inroot, 'Hymap_Berlin-A_Mask'))
    train = enmapbox.processing.types.Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-Training-Sample'))
    test = enmapbox.processing.types.Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-Validation-Sample'))

    #clusterers = enmapbox.processing.estimators.all(enmapbox.processing.estimators.Clusterers)
    clusterers = [enmapbox.processing.estimators.Clusterers.KMeans(n_clusters=5, with_mean=False, with_std=False)]
    #clusterers = [enmapbox.processing.estimators.Clusterers.KMeans(n_clusters=5, with_mean=True, with_std=True)]

    for clusterer in clusterers:
        assert isinstance(clusterer, enmapbox.processing.types.Clusterer)
        Progress.setInfo(clusterer.name())
        clusterer.fit(image, train).report().saveHTML().open()
        clusterer.predict(image, mask, filename=os.path.join(outroot, clusterer.name()))


def transformer():

    image = enmapbox.processing.types.Image(os.path.join(inroot, 'Hymap_Berlin-A_Image'))
    mask = enmapbox.processing.types.Mask(os.path.join(inroot, 'Hymap_Berlin-A_Mask'))
    trainingLabels = enmapbox.processing.types.Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-Training-Sample'))

    #transformers = enmapbox.processing.estimators.all(enmapbox.processing.estimators.Transformers)
    #transformers = [enmapbox.processing.estimators.Transformers.KernelPCA()]
    transformers = [enmapbox.processing.estimators.Transformers.PCA()]

    for transformer in transformers:

        assert isinstance(transformer, enmapbox.processing.types.Transformer)
        Progress.setInfo(transformer.name())
        transformer.fit(image, trainingLabels).report().saveHTML().open()
        transformedImage = transformer.transform(image, mask, filename=os.path.join(outroot, transformer.name()))
        inverseTransformedImage = transformer.transformInverse(transformedImage, mask, filename=os.path.join(outroot, transformer.name()+'Inverse'))

def showEstimator():

    image = enmapbox.processing.types.Image(os.path.join(inroot, 'Hymap_Berlin-A_Image'))
    labels = enmapbox.processing.types.Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-Training-Sample'))
    pca = enmapbox.processing.estimators.Transformers.PCA()
    pca.info()

def uncertaintyClassifier():

    image = enmapbox.processing.types.Image(r'C:\Work\data\Hymap_Berlin-A_Image')
    mask =  enmapbox.processing.types.Image(r'C:\Work\data\Hymap_Berlin-A_Mask')
    trainingLabels = enmapbox.processing.types.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Training-Sample')

    svc = enmapbox.processing.estimators.Classifiers.SVCTuned()

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

    image = enmapbox.processing.types.Image(r'C:\Work\data\Hymap_Berlin-B_Image')
    mask = enmapbox.processing.types.Image(r'C:\Work\data\Hymap_Berlin-B_Mask')
    trainingLabels = enmapbox.processing.types.Regression(r'C:\Work\data\Hymap_Berlin-B_Regression-Training-Sample')

    svr = enmapbox.processing.estimators.Regressors.SVRTuned()
    uncertaintyRegressor = svr.UncertaintyRegressor()
    uncertaintyRegressor.fit(image, trainingLabels).report().saveHTML().open()
    uncertaintyRegressor.predict(image, mask, filename=r'c:\work\_svrUncertainty')

def classificationAccAss():

    testingLabels = enmapbox.processing.types.Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-Validation-Sample'))
    prediction = enmapbox.processing.types.Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-Estimation'))

    accAss = prediction.assessClassificationPerformance(testingLabels)
    accAss.info() #.report().saveHTML().open()


def classificationAccAssAdjusted():

    testingLabels = enmapbox.processing.types.Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-Validation-Sample'))
    prediction = enmapbox.processing.types.Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-Estimation'))
    stratification = enmapbox.processing.types.Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-GroundTruth'))
    accAss = prediction.assessClassificationPerformance(testingLabels, stratification)
    accAss.report().saveHTML().open()


def regressionAccAss():

    testingLabels = enmapbox.processing.types.Regression(os.path.join(inroot, 'Hymap_Berlin-B_Regression-Validation-Sample'))
    prediction = enmapbox.processing.types.Regression(os.path.join(inroot, 'Hymap_Berlin-B_Regression-Estimation'))
    accAss = prediction.assessRegressionPerformance(testingLabels)
    accAss.report().saveHTML().open()


def clusteringAccAss():

    testingLabels = enmapbox.processing.types.Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-Validation-Sample'))
    prediction = enmapbox.processing.types.Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-Estimation'))

    accAss = prediction.assessClusteringPerformance(testingLabels)
    accAss.report().saveHTML().open()


def probabilityAccAss():


    image = enmapbox.processing.types.Image(r'C:\Work\data\Hymap_Berlin-A_Image')
    trainingLabels = enmapbox.processing.types.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Training-Sample')
    testingLabels = enmapbox.processing.types.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Validation-Sample')

    classifier = enmapbox.processing.estimators.Classifiers.RandomForestClassifier().fit(image, trainingLabels)
    probability = classifier.predictProbability(image, testingLabels)
    accAss = probability.assessProbabilityPerformance(testingLabels)
    accAss.report().saveHTML().open()


def statisticsForImage():

    image = Image(os.path.join(inroot, 'Hymap_Berlin-A_Image'))
    image.statistics().info()

def statisticsForClassification():

    image = Classification(os.path.join(inroot,  'Hymap_Berlin-A_Classification-Training-Sample'))
    image.statistics().info()

def saveImageAs():

    image = enmapbox.processing.types.Image(r'C:\Work\data\Hymap_Berlin-A_Image')
    image.report().saveHTML().open()
    image.saveAs(r'c:\work\saved').report().saveHTML().open()


def stackImages():

    imageA = enmapbox.processing.types.Image(r'C:\Work\data\Hymap_Berlin-A_Image')
    imageB = enmapbox.processing.types.Image(r'C:\Work\data\Hymap_Berlin-B_Image')
    stack = imageA.stack([imageB])
    stack.report().saveHTML().open()
#    image.saveAs(r'c:\work\saved').report().saveHTML().open()

def projectImageToPixelGrid():

    imageA = enmapbox.processing.types.Image(r'C:\Work\data\Hymap_Berlin-A_Image')
    imageB = enmapbox.processing.types.Image(r'C:\Work\data\Hymap_Berlin-B_Image')
    imageSpot = enmapbox.processing.types.Image(r'C:\Work\data\Spot_Berlin')
    pixelGrid = imageSpot.PixelGrid
    newImage = pixelGrid.project(imageA)#, imageB.BoundingBox)
    newImage.report().saveHTML().open()

def maximumProbability():

    image = enmapbox.processing.types.Image(os.path.join(inroot, 'Hymap_Berlin-A_Image'))
    trainingLabels = enmapbox.processing.types.Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-Training-Sample'))
    mask = enmapbox.processing.types.Mask(r'C:\Work\data\Hymap_Berlin-A_Mask')
    classifier = enmapbox.processing.estimators.Classifiers.RandomForestClassifier()
    classifier = classifier.fit(image, labels=trainingLabels)
    propability = classifier.predictProbability(image, mask=mask)
    classification = propability.argmax()


def ar_debug():

    from enmapbox.processing.types import unpickle
    image = enmapbox.processing.types.Image(os.path.join(inroot, 'Hymap_Berlin-A_Image'))
    trainingLabels = enmapbox.processing.types.Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-Training-Sample'))
    mask = enmapbox.processing.types.Mask(r'C:\Work\data\Hymap_Berlin-A_Mask')
    noMask = enmapbox.processing.types.NoMask()
    trf = enmapbox.processing.estimators.Transformers.PCA()
    trf = trf.fit(image, labels=None)
    transformation = trf.transform(image)

if __name__ == '__main__':

    #importENVISpeclib()
    #image()
    #sample()
    #enmapbox.processing.env.cleanupTempdir()
    #classification()
    #regression()
    #clusterer()
    #transformer()
    #showEstimator()
    #performance()
    #uncertaintyClassifier()
    #uncertaintyRegressor()
    #classificationAccAss()
    #classificationAccAssAdjusted()
    #regressionAccAss()
    #clusteringAccAss()
    #probabilityAccAss()
    #statisticsForImage()
    statisticsForClassification()
    #mportENVISpeclib()
    #saveImageAs()
    #stackImages()
    #projectImageToPixelGrid()
    #maximumProbability()
    #ar_debug()
