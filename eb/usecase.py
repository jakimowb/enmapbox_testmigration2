from __future__ import print_function

__author__ = 'janzandr'
import eb, eb.estimators, os

from eb.env import PrintProgress as Progress

root = r'c:\work\outputs'

def classification():

    image = eb.Image(r'C:\Program Files\EnMAP-Box\enmapProject\lib\hubAPI\resource\testData\image\Hymap_Berlin-A_Image')
    mask =  eb.Image(r'C:\Program Files\EnMAP-Box\enmapProject\lib\hubAPI\resource\testData\image\Hymap_Berlin-A_Mask')
    trainingLabels = eb.Classification(r'C:\Program Files\EnMAP-Box\enmapProject\lib\hubAPI\resource\testData\image\Hymap_Berlin-A_Classification-Training-Sample')
    testingLabels = eb.Classification(r'C:\Program Files\EnMAP-Box\enmapProject\lib\hubAPI\resource\testData\image\Hymap_Berlin-A_Classification-Validation-Sample')

    classifier = eb.estimators.Classifiers.RandomForestClassifier()
    classifier = classifier.fit(image, trainingLabels)
    prediction = classifier.predict(image, mask)
    print(prediction)


    #classifiers = eb.estimators.all(eb.estimators.Classifiers)
    classifiers = [eb.estimators.Classifiers.RandomForestClassifier()]

    for classifier in classifiers:
        assert isinstance(classifier, eb.Classifier)
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

    image = eb.Image(r'C:\Work\data\Hymap_Berlin-B_Image')
    mask = eb.Image(r'C:\Work\data\Hymap_Berlin-B_Mask')
    trainingLabels = eb.Regression(r'C:\Work\data\Hymap_Berlin-B_Regression-Training-Sample')
    testingLabels = eb.Regression(r'C:\Work\data\Hymap_Berlin-B_Regression-Validation-Sample')

    regressors = eb.estimators.all(eb.estimators.Regressors)

    for regressor in regressors:
        assert isinstance(regressor, eb.Regressor)
        Progress.setInfo(regressor.name())
        regressor = regressor.fit(image, trainingLabels)
        regressor.predict(image, mask, filename=os.path.join(root, regressor.name()))


def clusterer():

    image = eb.Image(r'C:\Work\data\Hymap_Berlin-A_Image')
    mask = eb.Image(r'C:\Work\data\Hymap_Berlin-A_Mask')
    trainingLabels = eb.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Training-Sample')
    testingLabels = eb.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Validation-Sample')

    clusterers = eb.estimators.all(eb.estimators.Clusterers)
    clusterers = [eb.estimators.Clusterers.KMeans(n_clusters=5, with_mean=False, with_std=False)]

    for clusterer in clusterers:
        assert isinstance(clusterer, eb.Clusterer)
        Progress.setInfo(clusterer.name())
        clusterer.fit(image, trainingLabels).report().saveHTML().open()
        #clusterer.predict(image, mask, filename=os.path.join(root, clusterer.name()))


def transformer():

    image = eb.Image(r'C:\Work\data\Hymap_Berlin-A_Image')
    mask = eb.Mask(r'C:\Work\data\Hymap_Berlin-A_Mask')
    trainingLabels = eb.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Training-Sample')

    transformers = eb.estimators.all(eb.estimators.Transformers)
    transformers = [eb.estimators.Transformers.KernelPCA()]

    for transformer in transformers:

        assert isinstance(transformer, eb.Transformer)
        Progress.setInfo(transformer.name())
        transformer.fit(image, trainingLabels).report().saveHTML().open()
        transformedImage = transformer.transform(image, mask, filename=os.path.join(root, transformer.name()))
        inverseTransformedImage = transformer.transformInverse(transformedImage, mask, filename=os.path.join(root, transformer.name()+'Inverse'))

def performance():

    image = eb.Image(r'C:\Work\data\Hymap_Berlin-A_Image')
    mask =  eb.Image(r'C:\Work\data\Hymap_Berlin-A_Mask')
    trainingLabels = eb.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Training-Sample')
    testingLabels = eb.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Validation-Sample')

    classifier = eb.estimators.Classifiers.RandomForestClassifier()
    classifier.fit(image, trainingLabels)
    classification = classifier.predict(image, mask)
    classification.assessClassificationPerformance(testingLabels).report().saveHTML().open()

def uncertaintyClassifier():

    image = eb.Image(r'C:\Work\data\Hymap_Berlin-A_Image')
    mask =  eb.Image(r'C:\Work\data\Hymap_Berlin-A_Mask')
    trainingLabels = eb.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Training-Sample')

    svc = eb.estimators.Classifiers.SVCTuned()

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

    image = eb.Image(r'C:\Work\data\Hymap_Berlin-B_Image')
    mask = eb.Image(r'C:\Work\data\Hymap_Berlin-B_Mask')
    trainingLabels = eb.Regression(r'C:\Work\data\Hymap_Berlin-B_Regression-Training-Sample')

    svr = eb.estimators.Regressors.SVRTuned()
    uncertaintyRegressor = svr.UncertaintyRegressor()
    uncertaintyRegressor.fit(image, trainingLabels).report().saveHTML().open()
    uncertaintyRegressor.predict(image, mask, filename=r'c:\work\_svrUncertainty')

def classificationAccAss():

    testingLabels = eb.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Validation-Sample')
    prediction = eb.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Estimation')

    accAss = prediction.assessClassificationPerformance(testingLabels)
    accAss.report().saveHTML().open()


def classificationAccAssAdjusted():

    testingLabels = eb.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Validation-Sample')
    prediction = eb.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Estimation')
    stratification = eb.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-GroundTruth')
    accAss = prediction.assessClassificationPerformance(testingLabels, stratification)
    accAss.report().saveHTML().open()


def statisticsClassification():

    classification = eb.Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Validation-Sample')
    statistics = classification.statistics()
    statistics.report().saveHTML().open()

if __name__ == '__main__':
    #eb.env.cleanupTempdir()
    classification()
    #regression()
    #clusterer()
    #transformer()
    #performance()
    #uncertaintyClassifier()
    #uncertaintyRegressor()
    #classificationAccAss()
    #classificationAccAssAdjusted()

    #  print(eb.env.tempdir)