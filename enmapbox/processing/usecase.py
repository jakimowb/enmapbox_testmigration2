from __future__ import print_function

__author__ = 'janzandr'
import os
import enmapbox.processing
import enmapbox.processing.estimators

from enmapbox.processing.env import PrintProgress as Progress

root = r'c:\work\outputs'

def sample():

    image = enmapbox.processing.Image(r'C:\Work\data\Hymap_Berlin-A_Image')
    testingLabels = enmapbox.processing.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Validation-Sample')
    sample = enmapbox.processing.ClassificationSample(image, testingLabels)
    print(sample.labelData.shape)
    print(sample.imageData.shape)


def classification():


    image = enmapbox.processing.Image(r'C:\Work\data\Hymap_Berlin-A_Image')
    mask =  enmapbox.processing.Image(r'C:\Work\data\Hymap_Berlin-A_Mask')
    trainingLabels = enmapbox.processing.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Training-Sample')
#    testingLabels = eb.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Validation-Sample')


    classifier = enmapbox.processing.estimators.Classifiers.RandomForestClassifier()
    classifier = classifier.fit(image, trainingLabels)
    prediction = classifier.predict(image, mask)
    print(prediction)
    return



    classifiers = enmapbox.processing.estimators.all(enmapbox.processing.estimators.Classifiers)


    classifiers = [enmapbox.processing.estimators.Classifiers.RandomForestClassifier()]

    for classifier in classifiers:
        assert isinstance(classifier, enmapbox.processing.Classifier)
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

    image = enmapbox.processing.Image(r'C:\Work\data\Hymap_Berlin-B_Image')
    mask = enmapbox.processing.Image(r'C:\Work\data\Hymap_Berlin-B_Mask')
    trainingLabels = enmapbox.processing.Regression(r'C:\Work\data\Hymap_Berlin-B_Regression-Training-Sample')
    testingLabels = enmapbox.processing.Regression(r'C:\Work\data\Hymap_Berlin-B_Regression-Validation-Sample')

    regressors = enmapbox.processing.estimators.all(enmapbox.processing.estimators.Regressors)

    for regressor in regressors:
        assert isinstance(regressor, enmapbox.processing.Regressor)
        Progress.setInfo(regressor.name())
        regressor = regressor.fit(image, trainingLabels)
        regressor.predict(image, mask, filename=os.path.join(root, regressor.name()))


def clusterer():

    image = enmapbox.processing.Image(r'C:\Work\data\Hymap_Berlin-A_Image')
    mask = enmapbox.processing.Image(r'C:\Work\data\Hymap_Berlin-A_Mask')
    trainingLabels = enmapbox.processing.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Training-Sample')
    testingLabels = enmapbox.processing.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Validation-Sample')

    clusterers = enmapbox.processing.estimators.all(enmapbox.processing.estimators.Clusterers)
    clusterers = [enmapbox.processing.estimators.Clusterers.KMeans(n_clusters=5, with_mean=False, with_std=False)]

    for clusterer in clusterers:
        assert isinstance(clusterer, enmapbox.processing.Clusterer)
        Progress.setInfo(clusterer.name())
        clusterer.fit(image, trainingLabels).report().saveHTML().open()
        #clusterer.predict(image, mask, filename=os.path.join(root, clusterer.name()))


def transformer():

    image = enmapbox.processing.Image(r'C:\Work\data\Hymap_Berlin-A_Image')
    mask = enmapbox.processing.Mask(r'C:\Work\data\Hymap_Berlin-A_Mask')
    trainingLabels = enmapbox.processing.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Training-Sample')

    transformers = enmapbox.processing.estimators.all(enmapbox.processing.estimators.Transformers)
    transformers = [enmapbox.processing.estimators.Transformers.KernelPCA()]

    for transformer in transformers:

        assert isinstance(transformer, enmapbox.processing.Transformer)
        Progress.setInfo(transformer.name())
        transformer.fit(image, trainingLabels).report().saveHTML().open()
        transformedImage = transformer.transform(image, mask, filename=os.path.join(root, transformer.name()))
        inverseTransformedImage = transformer.transformInverse(transformedImage, mask, filename=os.path.join(root, transformer.name()+'Inverse'))


def uncertaintyClassifier():

    image = enmapbox.processing.Image(r'C:\Work\data\Hymap_Berlin-A_Image')
    mask =  enmapbox.processing.Image(r'C:\Work\data\Hymap_Berlin-A_Mask')
    trainingLabels = enmapbox.processing.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Training-Sample')

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

    image = enmapbox.processing.Image(r'C:\Work\data\Hymap_Berlin-B_Image')
    mask = enmapbox.processing.Image(r'C:\Work\data\Hymap_Berlin-B_Mask')
    trainingLabels = enmapbox.processing.Regression(r'C:\Work\data\Hymap_Berlin-B_Regression-Training-Sample')

    svr = enmapbox.processing.estimators.Regressors.SVRTuned()
    uncertaintyRegressor = svr.UncertaintyRegressor()
    uncertaintyRegressor.fit(image, trainingLabels).report().saveHTML().open()
    uncertaintyRegressor.predict(image, mask, filename=r'c:\work\_svrUncertainty')

def classificationAccAss():

    testingLabels = enmapbox.processing.Classification(r'C:\Program Files\EnMAP-Box\enmapProject\lib\hubAPI\resource\testData\image\Hymap_Berlin-A_Classification-Validation-Sample')
    prediction = enmapbox.processing.Classification(r'C:\Program Files\EnMAP-Box\enmapProject\lib\hubAPI\resource\testData\image\Hymap_Berlin-A_Classification-Estimation')

    accAss = prediction.assessClassificationPerformance(testingLabels)
    accAss.report().saveHTML().open()


def classificationAccAssAdjusted():

    testingLabels = enmapbox.processing.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Validation-Sample')
    prediction = enmapbox.processing.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Estimation')
    stratification = enmapbox.processing.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-GroundTruth')
    accAss = prediction.assessClassificationPerformance(testingLabels, stratification)
    accAss.report().saveHTML().open()


def regressionAccAss():

    testingLabels = enmapbox.processing.Regression(r'C:\Work\data\Hymap_Berlin-B_Regression-Validation-Sample')
    prediction = enmapbox.processing.Regression(r'C:\Work\data\Hymap_Berlin-B_Regression-Estimation')
    accAss = prediction.assessRegressionPerformance(testingLabels)
    accAss.report().saveHTML().open()


def clusteringAccAss():

    testingLabels = enmapbox.processing.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Validation-Sample')
    prediction = enmapbox.processing.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Estimation')

    accAss = prediction.assessClusteringPerformance(testingLabels)
    accAss.report().saveHTML().open()


def probabilityAccAss():


    image = enmapbox.processing.Image(r'C:\Work\data\Hymap_Berlin-A_Image')
    trainingLabels = enmapbox.processing.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Training-Sample')
    testingLabels = enmapbox.processing.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Validation-Sample')

    classifier = enmapbox.processing.estimators.Classifiers.RandomForestClassifier().fit(image, trainingLabels)
    probability = classifier.predictProbability(image, testingLabels)
    accAss = probability.assessProbabilityPerformance(testingLabels)
    accAss.report().saveHTML().open()


def statisticsAndHistogramForImage():

    image = enmapbox.processing.Image(r'C:\Work\data\Hymap_Berlin-A_Image')
    mask =  enmapbox.processing.Mask(r'C:\Work\data\Hymap_Berlin-A_Classification-Validation-Sample')
    mask = None

    statistics = image.statistics(mask)
    statistics.report().saveHTML().open()

def statisticsAndHistogramforClassification():

    classification = enmapbox.processing.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Validation-Sample')
    mask = None
    statistics = classification.statistics(mask)
    statistics.report().saveHTML().open()


def importENVISpeclib():

    speclib = enmapbox.processing.Image.fromENVISpectralLibrary(r'C:\Work\EnMAP-Box\enmapProject\lib\hubAPI\resource\testData\speclib\ClassificationSpeclib')
    print(speclib.filename)
    speclib = speclib.saveAs(r'c:\work\speclib')
    speclib.report().saveHTML().open()


def saveImageAs():

    image = enmapbox.processing.Image(r'C:\Work\data\Hymap_Berlin-A_Image')
    image.report().saveHTML().open()
    image.saveAs(r'c:\work\saved').report().saveHTML().open()


def stackImages():

    imageA = enmapbox.processing.Image(r'C:\Work\data\Hymap_Berlin-A_Image')
    imageB = enmapbox.processing.Image(r'C:\Work\data\Hymap_Berlin-B_Image')
    stack = imageA.stack([imageB])
    stack.report().saveHTML().open()
#    image.saveAs(r'c:\work\saved').report().saveHTML().open()

def projectImageToPixelGrid():

    imageA = enmapbox.processing.Image(r'C:\Work\data\Hymap_Berlin-A_Image')
    imageB = enmapbox.processing.Image(r'C:\Work\data\Hymap_Berlin-B_Image')
    imageSpot = enmapbox.processing.Image(r'C:\Work\data\Spot_Berlin')
    pixelGrid = imageSpot.PixelGrid
    newImage = pixelGrid.project(imageA)#, imageB.BoundingBox)
    newImage.report().saveHTML().open()

if __name__ == '__main__':

    #sample()
    #enmapbox.processing.env.cleanupTempdir()
    #classification()
    #regression()
    #clusterer()
    #transformer()
    #performance()
    #uncertaintyClassifier()
    #uncertaintyRegressor()
    classificationAccAss()
    #classificationAccAssAdjusted()
    #regressionAccAss()
    #clusteringAccAss()
    #probabilityAccAss()
    #statisticsAndHistogramForImage()
    #statisticsAndHistogramforClassification()
    #mportENVISpeclib()
    #saveImageAs()
    #stackImages()
    #projectImageToPixelGrid()