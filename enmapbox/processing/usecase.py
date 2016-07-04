from __future__ import print_function

__author__ = 'janzandr'
import eb, os
from enmapbox import processing

from enmapbox.processing.env import PrintProgress as Progress

root = r'c:\work\outputs'

def sample():

    image = processing.Image(r'C:\Work\data\Hymap_Berlin-A_Image')
    testingLabels = processing.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Validation-Sample')
    sample = processing.ClassificationSample(image, testingLabels)
    print(sample.labelData.shape)
    print(sample.imageData.shape)


def classification():

    image = processing.Image(r'C:\Work\data\Hymap_Berlin-A_Image')
    mask =  processing.Image(r'C:\Work\data\Hymap_Berlin-A_Mask')
    trainingLabels = processing.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Training-Sample')
#    testingLabels = eb.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Validation-Sample')


    classifier = enmapbox.eb.estimators.Classifiers.RandomForestClassifier()
    classifier = classifier.fit(image, trainingLabels)
    prediction = classifier.predict(image, mask)
    print(prediction)
    return



    classifiers = enmapbox.eb.estimators.all(enmapbox.eb.estimators.Classifiers)


    classifiers = [enmapbox.eb.estimators.Classifiers.RandomForestClassifier()]

    for classifier in classifiers:
        assert isinstance(classifier, processing.Classifier)
        Progress.setInfo(classifier.name())
        classifier = classifier.fit(image, trainingLabels, progress=Progress)
        classifier.report().saveHTML().open()
        continue
        classifier.predict(image, mask, filename=os.path.join(root, classifier.name()), progress=Progress)
        try:
            classifier.predictProbability(image, mask, filename=os.path.join(root, classifier.name()+'Proba'), progress=Progress)
        except:
            pass


def regression():

    image = processing.Image(r'C:\Work\data\Hymap_Berlin-B_Image')
    mask = processing.Image(r'C:\Work\data\Hymap_Berlin-B_Mask')
    trainingLabels = processing.Regression(r'C:\Work\data\Hymap_Berlin-B_Regression-Training-Sample')
    testingLabels = processing.Regression(r'C:\Work\data\Hymap_Berlin-B_Regression-Validation-Sample')

    regressors = enmapbox.eb.estimators.all(enmapbox.eb.estimators.Regressors)

    for regressor in regressors:
        assert isinstance(regressor, processing.Regressor)
        Progress.setInfo(regressor.name())
        regressor = regressor.fit(image, trainingLabels)
        regressor.predict(image, mask, filename=os.path.join(root, regressor.name()))


def clusterer():

    image = processing.Image(r'C:\Work\data\Hymap_Berlin-A_Image')
    mask = processing.Image(r'C:\Work\data\Hymap_Berlin-A_Mask')
    trainingLabels = processing.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Training-Sample')
    testingLabels = processing.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Validation-Sample')

    clusterers = enmapbox.eb.estimators.all(enmapbox.eb.estimators.Clusterers)
    clusterers = [enmapbox.eb.estimators.Clusterers.KMeans(n_clusters=5, with_mean=False, with_std=False)]

    for clusterer in clusterers:
        assert isinstance(clusterer, processing.Clusterer)
        Progress.setInfo(clusterer.name())
        clusterer.fit(image, trainingLabels).report().saveHTML().open()
        #clusterer.predict(image, mask, filename=os.path.join(root, clusterer.name()))


def transformer():

    image = processing.Image(r'C:\Work\data\Hymap_Berlin-A_Image')
    mask = processing.Mask(r'C:\Work\data\Hymap_Berlin-A_Mask')
    trainingLabels = processing.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Training-Sample')

    transformers = enmapbox.eb.estimators.all(enmapbox.eb.estimators.Transformers)
    transformers = [enmapbox.eb.estimators.Transformers.KernelPCA()]

    for transformer in transformers:

        assert isinstance(transformer, processing.Transformer)
        Progress.setInfo(transformer.name())
        transformer.fit(image, trainingLabels).report().saveHTML().open()
        transformedImage = transformer.transform(image, mask, filename=os.path.join(root, transformer.name()))
        inverseTransformedImage = transformer.transformInverse(transformedImage, mask, filename=os.path.join(root, transformer.name()+'Inverse'))


def uncertaintyClassifier():

    image = processing.Image(r'C:\Work\data\Hymap_Berlin-A_Image')
    mask =  processing.Image(r'C:\Work\data\Hymap_Berlin-A_Mask')
    trainingLabels = processing.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Training-Sample')

    svc = enmapbox.eb.estimators.Classifiers.SVCTuned()

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

    image = processing.Image(r'C:\Work\data\Hymap_Berlin-B_Image')
    mask = processing.Image(r'C:\Work\data\Hymap_Berlin-B_Mask')
    trainingLabels = processing.Regression(r'C:\Work\data\Hymap_Berlin-B_Regression-Training-Sample')

    svr = enmapbox.eb.estimators.Regressors.SVRTuned()
    uncertaintyRegressor = svr.UncertaintyRegressor()
    uncertaintyRegressor.fit(image, trainingLabels).report().saveHTML().open()
    uncertaintyRegressor.predict(image, mask, filename=r'c:\work\_svrUncertainty')

def classificationAccAss():

    testingLabels = processing.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Validation-Sample')
    prediction = processing.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Estimation')

    accAss = prediction.assessClassificationPerformance(testingLabels)
    accAss.report().saveHTML().open()


def classificationAccAssAdjusted():

    testingLabels = processing.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Validation-Sample')
    prediction = processing.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Estimation')
    stratification = processing.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-GroundTruth')
    accAss = prediction.assessClassificationPerformance(testingLabels, stratification)
    accAss.report().saveHTML().open()


def regressionAccAss():

    testingLabels = processing.Regression(r'C:\Work\data\Hymap_Berlin-B_Regression-Validation-Sample')
    prediction = processing.Regression(r'C:\Work\data\Hymap_Berlin-B_Regression-Estimation')
    accAss = prediction.assessRegressionPerformance(testingLabels)
    accAss.report().saveHTML().open()


def clusteringAccAss():

    testingLabels = processing.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Validation-Sample')
    prediction = processing.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Estimation')

    accAss = prediction.assessClusteringPerformance(testingLabels)
    accAss.report().saveHTML().open()


def probabilityAccAss():


    image = processing.Image(r'C:\Work\data\Hymap_Berlin-A_Image')
    trainingLabels = processing.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Training-Sample')
    testingLabels = processing.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Validation-Sample')

    classifier = enmapbox.eb.estimators.Classifiers.RandomForestClassifier().fit(image, trainingLabels)
    probability = classifier.predictProbability(image, testingLabels)
    accAss = probability.assessProbabilityPerformance(testingLabels)
    accAss.report().saveHTML().open()


def statisticsAndHistogramForImage():

    image = processing.Image(r'C:\Work\data\Hymap_Berlin-A_Image')
    mask =  processing.Mask(r'C:\Work\data\Hymap_Berlin-A_Classification-Validation-Sample')
    mask = None

    statistics = image.statistics(mask)
    statistics.report().saveHTML().open()

def statisticsAndHistogramforClassification():

    classification = processing.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Validation-Sample')
    mask = None
    statistics = classification.statistics(mask)
    statistics.report().saveHTML().open()


def importENVISpeclib():

    speclib = processing.Image.fromENVISpectralLibrary(r'C:\Work\EnMAP-Box\enmapProject\lib\hubAPI\resource\testData\speclib\ClassificationSpeclib')
    print(speclib.filename)
    speclib = speclib.saveAs(r'c:\work\speclib')
    speclib.report().saveHTML().open()


def saveImageAs():

    image = processing.Image(r'C:\Work\data\Hymap_Berlin-A_Image')
    image.report().saveHTML().open()
    image.saveAs(r'c:\work\saved').report().saveHTML().open()


def stackImages():

    imageA = processing.Image(r'C:\Work\data\Hymap_Berlin-A_Image')
    imageB = processing.Image(r'C:\Work\data\Hymap_Berlin-B_Image')
    stack = imageA.stack([imageB])
    stack.report().saveHTML().open()
#    image.saveAs(r'c:\work\saved').report().saveHTML().open()

def projectImageToPixelGrid():

    imageA = processing.Image(r'C:\Work\data\Hymap_Berlin-A_Image')
    imageB = processing.Image(r'C:\Work\data\Hymap_Berlin-B_Image')
    imageSpot = processing.Image(r'C:\Work\data\Spot_Berlin')
    pixelGrid = imageSpot.PixelGrid
    newImage = pixelGrid.project(imageA)#, imageB.BoundingBox)
    newImage.report().saveHTML().open()

if __name__ == '__main__':

    #sample()
    #eb.env.cleanupTempdir()
    #classification()
    #regression()
    #clusterer()
    #transformer()
    #performance()
    #uncertaintyClassifier()
    #uncertaintyRegressor()
    #classificationAccAss()
    #classificationAccAssAdjusted()
    #regressionAccAss()
    #clusteringAccAss()
    #probabilityAccAss()
    #statisticsAndHistogramForImage()
    #statisticsAndHistogramforClassification()
    #mportENVISpeclib()
    #saveImageAs()
    #stackImages()
    projectImageToPixelGrid()