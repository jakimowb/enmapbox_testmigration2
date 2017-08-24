from os.path import join
from tempfile import gettempdir
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.multioutput import MultiOutputRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR, LinearSVR

from hubflow.types import *
import enmapboxtestdata

def synthMixRegressionWorkflow():

    outdir = join(gettempdir(), 'hubflow_synthMixRegressionWorkflow')
    overwrite = True

    print('\n### SyntMixRegression Workflow ###'
          '\nOutput directory: {}'.format(outdir))

    # create training data
    # - import ENVI speclib
    unsupervisedSample = UnsupervisedSample.fromENVISpectralLibrary(filename=enmapboxtestdata.speclib)

    # - label spectra
    classDefinition = ClassDefinition(names=unsupervisedSample.metadata['level 2 class names'][1:],
                                      lookup=unsupervisedSample.metadata['level 2 class lookup'][3:])

    classificationSample = unsupervisedSample.classifyByClassName(names=unsupervisedSample.metadata['level 2 class spectra names'],
                                                                  classDefinition=classDefinition)

    # - scale spectra into image data range
    classificationSample.scaleFeaturesInplace(factor=10000.)

    # - generate synthetic mixtures
    probabilitySample = classificationSample.synthMix(mixingComplexities={2:0.5, 3:0.3, 4:0.2}, classLikelihoods='proportional', n=1000)

    # - subset output classes to be modeled
    #probabilitySample = probabilitySample.subsetClassesByNames(names=['Roof', 'Tree'])
    probabilitySample.pickle(filename=join(outdir, 'train.pkl'))

    # fit model and predict fraction image
    image = Image(filename=enmapboxtestdata.enmap)

    useSVRInstaedOfRFR = False
    if useSVRInstaedOfRFR:
        # todo: SVR is not working correctly
        assert 0
        svr = make_pipeline(StandardScaler(), SVR(epsilon=0.0001, tol=0.0001))
        tunedSVR = GridSearchCV(cv=3, estimator=svr, param_grid = {'svr__kernel': ['rbf'],
                                                                   'svr__gamma': [0.001, 0.01, 0.1, 1, 10, 100, 1000],
                                                                   'svr__C': [0.001, 0.01, 0.1, 1, 10, 100, 1000]})

        regressor = Regressor(sklEstimator=MultiOutputRegressor(estimator=tunedSVR))
    else:
        regressor = Regressor(sklEstimator=RandomForestRegressor())

    regressor.fit(sample=probabilitySample)
    regressor.pickle(filename=join(outdir, 'regressor.pkl'))
    fractions = regressor.predict(predictionFilename=join(outdir, 'fractions.img'), image=image, overwrite=overwrite)
    fractions.asProbability(classDefinition=classDefinition).asClassColorRGBImage(imageFilename=join(outdir, 'fractionsRGB.img'), overwrite=overwrite)

    # create testing data
    vectorClassification = VectorClassification(filename=enmapboxtestdata.landcover, classDefinition=classDefinition, idAttribute='Level_2_ID')

    # - rasterize ground truth classification into probabilities
    gtFractions = vectorClassification.rasterizeAsProbability(probabilityFilename=join(outdir, 'gtFractions.img'), grid=image.pixelGrid,
                                                              minOverallCoverage=0.8, oversampling=10, overwrite=overwrite)
    gtFractions.asClassColorRGBImage(imageFilename=join(outdir, 'gtFractionsRGB.img'), overwrite=overwrite)

    # accuracy assessment
    fractions.assessRegressionPerformance(regression=gtFractions).report().saveHTML(filename=join(outdir, 'report.html'), open=True)

def classificationWorkflow():

    outdir = join(gettempdir(), 'hubflow_classificationWorkflow')
    overwrite = True

    print('\n### Classification Workflow ###'
          '\nOutput directory: {}'.format(outdir))

    # create training data
    image = Image(filename=enmapboxtestdata.enmap)

    # - rasterize land cover into classification image
    speclib = UnsupervisedSample.fromENVISpectralLibrary(filename=enmapboxtestdata.speclib)
    classDefinition = ClassDefinition(names=speclib.metadata['level 2 class names'][1:],
                                      lookup=speclib.metadata['level 2 class lookup'][3:])
    vectorClassification = VectorClassification(filename=enmapboxtestdata.landcover, classDefinition=classDefinition,
                                                idAttribute='Level_2_ID', minWinnerCoverage=0.5)
    gtClassification = vectorClassification.rasterizeAsClassification(classificationFilename=join(outdir, 'gtClassification.img'), grid=image.pixelGrid,
                                                                      oversampling=10, overwrite=overwrite)

    # - sample from image
    fractionsSample = image.sampleByClassification(classification=gtClassification)
    classificationSample = fractionsSample.classifyByProbability(minWinnerCoverage=0.5)
    classificationSample.pickle(filename=join(outdir, 'train.pkl'))

    # fit model and predict classification image
    classifier = Classifier(sklEstimator=RandomForestClassifier())
    classifier.fit(sample=classificationSample)
    classifier.pickle(filename=join(outdir, 'classifier.pkl'))
    classification = classifier.predict(predictionFilename=join(outdir, 'classification.img'), image=image, overwrite=overwrite)

    # accuracy assessment on training data
    classification.assessClassificationPerformance(classification=gtClassification).report().saveHTML(filename=join(outdir, 'report.html'), open=True)


if __name__ == '__main__':
    synthMixRegressionWorkflow()
    classificationWorkflow()