from __future__ import print_function

__author__ = 'janzandr'
import os
import enmapbox.processing.types
import enmapbox.processing.estimators

from enmapbox.processing.environment import PrintProgress as Progress

if os.environ['USERNAME'] == 'janzandr':
    inroot = r'c:\work\data'
    outroot = r'c:\work\outputs'
elif os.environ['USERNAME'] == 'enmap-box':
    inroot = r'C:\Program Files\EnMAP-Box\enmapProject\lib\hubAPI\resource\testData\image'



def sample():

    image = enmapbox.processing.types.Image(os.path.join(inroot, 'Hymap_Berlin-A_Image'))
    testingLabels = enmapbox.processing.types.Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-Validation-Sample'))
    sample = enmapbox.processing.types.ClassificationSample(image, testingLabels)
    print(sample.labelData.shape)
    print(sample.imageData.shape)


def classification():


    image = enmapbox.processing.types.Image(os.path.join(inroot, 'Hymap_Berlin-A_Image'))
    mask =  enmapbox.processing.types.Image(os.path.join(inroot, 'Hymap_Berlin-A_Mask'))
    trainingLabels = enmapbox.processing.types.Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-Training-Sample'))
    #image = enmapbox.processing.types.Image(r'C:\Program Files\EnMAP-Box\enmapProject\enmapBox\resource\testData\image\AF_Image')
    #trainingLabels = enmapbox.processing.types.Classification(r'C:\Program Files\EnMAP-Box\enmapProject\enmapBox\resource\testData\image\AF_LC_Training')
    #mask = enmapbox.processing.types.Image(r'C:\Program Files\EnMAP-Box\enmapProject\enmapBox\resource\testData\image\AF_Mask')

    #testingLabels = eb.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Validation-Sample')


   # classifier = enmapbox.processing.estimators.Classifiers.RandomForestClassifier()
   # classifier = classifier.fit(image, trainingLabels)
   # prediction = classifier.predict(image, mask)
    #print(prediction)

  #  return


    #classifiers = [enmapbox.processing.estimators.Classifiers.RandomForestClassifier()]
    classifiers = [enmapbox.processing.estimators.Classifiers.LinearSVCTuned()]
    #classifiers = [enmapbox.processing.estimators.Classifiers.SVCTuned(C=[1, 10, 100], gamma=[0.001, 100,1000])]
    # classifiers = enmapbox.processing.estimators.all(enmapbox.processing.estimators.Classifiers)



    for classifier in classifiers:
        assert isinstance(classifier, enmapbox.processing.types.Classifier)
        Progress.setInfo(classifier.name())
        classifier = classifier.fit(image, trainingLabels, progress=Progress)
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
    regressors = [enmapbox.processing.estimators.Regressors.LinearSVRTuned()]


    for regressor in regressors:
        assert isinstance(regressor, enmapbox.processing.types.Regressor)
        Progress.setInfo(regressor.name())
        regressor = regressor.fit(image, trainingLabels)
        regressor.predict(image, mask, filename=os.path.join(outroot, regressor.name()))


def clusterer():

    image = enmapbox.processing.types.Image(os.path.join(inroot, 'Hymap_Berlin-A_Image'))
    mask = enmapbox.processing.types.Image(os.path.join(inroot, 'Hymap_Berlin-A_Mask'))
    trainingLabels = enmapbox.processing.types.Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-Training-Sample'))
    testingLabels = enmapbox.processing.types.Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-Validation-Sample'))

    #clusterers = enmapbox.processing.estimators.all(enmapbox.processing.estimators.Clusterers)
    clusterers = [enmapbox.processing.estimators.Clusterers.KMeans(n_clusters=5, with_mean=False, with_std=False)]

    for clusterer in clusterers:
        assert isinstance(clusterer, enmapbox.processing.types.Clusterer)
        Progress.setInfo(clusterer.name())
        clusterer.fit(image, trainingLabels).report().saveHTML().open()
        #clusterer.predict(image, mask, filename=os.path.join(outroot, clusterer.name()))


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


def statisticsAndHistogramForImage():

    image = enmapbox.processing.types.Image(r'C:\Work\data\Hymap_Berlin-A_Image')
    mask =  enmapbox.processing.types.Mask(r'C:\Work\data\Hymap_Berlin-A_Classification-Validation-Sample')
    mask = None

    statistics = image.statistics(mask)
    statistics.report().saveHTML().open()

def statisticsAndHistogramforClassification():

    classification = enmapbox.processing.types.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Validation-Sample')
    mask = None
    statistics = classification.statistics(mask)
    statistics.report().saveHTML().open()


def importENVISpeclib():

    speclib = enmapbox.processing.types.Image.fromENVISpectralLibrary(r'C:\Work\EnMAP-Box\enmapProject\lib\hubAPI\resource\testData\speclib\ClassificationSpeclib')
    print(speclib.filename)
    speclib = speclib.saveAs(r'c:\work\speclib')
    speclib.report().saveHTML().open()


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


def ar_debug():

    from enmapbox.processing.types import unpickle
    image = enmapbox.processing.types.Image(os.path.join(inroot, 'Hymap_Berlin-A_Image'))
    trainingLabels = enmapbox.processing.types.Classification(os.path.join(inroot, 'Hymap_Berlin-A_Classification-Training-Sample'))
    classifier = enmapbox.processing.estimators.Classifiers.LinearSVC()
    classifier = classifier.fit(image, trainingLabels)
    classifier.pickle(r'C:\Users\janzandr\AppData\Local\Temp\processing\1ad642222af14226a7d4238739be2d2b\model.file2')
    c2 = unpickle(r'C:\Users\janzandr\AppData\Local\Temp\processing\1ad642222af14226a7d4238739be2d2b\model.file2')


if __name__ == '__main__':

    #sample()
    #enmapbox.processing.env.cleanupTempdir()
    #classification()
    regression()
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
    #projectImageToPixelGrid()
    #ar_debug()
