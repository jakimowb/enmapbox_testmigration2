import objbrowser

from os.path import join
from tempfile import gettempdir
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.multioutput import MultiOutputRegressor
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.svm import SVR, LinearSVR
from sklearn.kernel_ridge import KernelRidge

from hubflow.core import *

import enmapboxtestdata

def synthMixRegressionWorkflow():

    outdir = join(gettempdir(), 'hubflow_synthMixRegressionWorkflow')
    overwrite = True

    print('\n### SyntMixRegression Workflow ###'
          '\nOutput directory: {}'.format(outdir))

    # create training data
    # - import ENVI speclib
    unsupervisedSample = Sample.fromENVISpectralLibrary(filename=enmapboxtestdata.library)

    # - label spectra
    classDefinition = ClassDefinition(names=unsupervisedSample.metadata['level 2 class names'][1:],
                                      colors=unsupervisedSample.metadata['level 2 class lookup'][3:])

    classificationSample = unsupervisedSample.classifyByName(names=unsupervisedSample.metadata['level 2 class spectra names'],
                                                             classDefinition=classDefinition)

    # - scale spectra into image data range
    classificationSample.scaleFeaturesInplace(factor=10000.)

    # - generate synthetic mixtures
    probabilitySample = classificationSample.synthMix(mixingComplexities={2:0.5, 3:0.3, 4:0.2}, classLikelihoods='proportional', n=1000)

    # - subset output classes to be modeled
    #probabilitySample = probabilitySample.subsetClassesByNames(names=['Roof', 'Tree'])
    probabilitySample.pickle(filename=join(outdir, 'train.pkl'))

    # fit model and predict fraction image
    image = Raster(filename=enmapboxtestdata.enmap)

    useSVRInstaedOfRFR = False
    if useSVRInstaedOfRFR:
        # todo: SVR is not working correctly
        #assert 0
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
    fractions.asProbability(classDefinition=classDefinition).asClassColorRGBRaster(imageFilename=join(outdir, 'fractionsRGB.img'), overwrite=overwrite)

    # create testing data
    vectorClassification = VectorClassification(filename=enmapboxtestdata.landcover, classDefinition=classDefinition, idAttribute='Level_2_ID',
                                                minOverallCoverage=1., minWinnerCoverage=0.5)

    # - rasterize ground truth classification into probabilities
    gtFractions = vectorClassification.rasterizeAsProbability(probabilityFilename=join(outdir, 'gtFractions.img'), grid=image.grid,
                                                              oversampling=10, overwrite=overwrite)
    gtFractions.asClassColorRGBRaster(imageFilename=join(outdir, 'gtFractionsRGB.img'), overwrite=overwrite)

    # accuracy assessment
    fractions.assessRegressionPerformance(regression=gtFractions).report().saveHTML(filename=join(outdir, 'report.html'), open=True)

def classificationWorkflow():

    outdir = join(gettempdir(), 'hubflow_classificationWorkflow')
    overwrite = True

    print('\n### Classification Workflow ###'
          '\nOutput directory: {}'.format(outdir))

    # create training data
    image = Raster(filename=enmapboxtestdata.enmap)

    # - rasterize land cover into classification image
    speclib = Sample.fromENVISpectralLibrary(filename=enmapboxtestdata.library)
    classDefinition = ClassDefinition(names=speclib.metadata['level 2 class names'][1:],
                                      colors=speclib.metadata['level 2 class lookup'][3:])
    vectorClassification = VectorClassification(filename=enmapboxtestdata.landcover, classDefinition=classDefinition,
                                                idAttribute='Level_2_ID', minWinnerCoverage=0.5)
    gtClassification = vectorClassification.rasterizeAsClassification(classificationFilename=join(outdir, 'gtClassification.img'), grid=image.grid,
                                                                      oversampling=10, overwrite=overwrite)

    # - sample from image
    fractionsSample = image.sampleByClassification(classification=gtClassification)
    classificationSample = fractionsSample.argmaxProbability(minWinnerCoverage=0.5)
    classificationSample.pickle(filename=join(outdir, 'train.pkl'))

    # fit model and predict classification image
    classifier = Classifier(sklEstimator=RandomForestClassifier())
    classifier.fit(sample=classificationSample)
    classifier.pickle(filename=join(outdir, 'classifier.pkl'))
    classification = classifier.predict(predictionFilename=join(outdir, 'classification.img'), image=image, overwrite=overwrite)

    # accuracy assessment on training data
    classification.assessClassificationPerformance(classification=gtClassification).report().saveHTML(filename=join(outdir, 'report.html'), open=True)

def debug_synthMixRegressionWorkflow():
    outdir = join(gettempdir(), 'hubflow_synthMixRegressionWorkflow')
    overwrite = True

    print('\n### SyntMixRegression Workflow ###'
          '\nOutput directory: {}'.format(outdir))

    image = Raster(filename=enmapboxtestdata.enmap)
    #image = Image(filename=r'F:\newdata\hymap_specsubset.bsq')  # hymap_specsubset_scaled.bsq
    #image = Image(filename=r'F:\newdata\enmap_subset_noSchleife.bsq')  # hymap_specsubset_scaled.bsq

    # create training data
    # - import ENVI speclib
    unsupervisedSample = Sample.fromENVISpectralLibrary(filename=enmapboxtestdata.library)
    #unsupervisedSample = UnsupervisedSample.fromENVISpectralLibrary(filename=r'F:\newdata\lib_subset.sli')

    # - label spectra
    classDefinition = ClassDefinition(names=unsupervisedSample.metadata['level 1 class names'][1:],
                                      colors=unsupervisedSample.metadata['level 1 class lookup'][3:])

    classificationSample = unsupervisedSample.classifyByName(names=unsupervisedSample.metadata['level 1 class spectra names'],
                                                             classDefinition=classDefinition)

    # - scale spectra into image data range
    x = classificationSample.features*1
    classificationSample.scaleFeaturesInplace(factor=10000.)

    # - generate synthetic mixtures
    probabilitySamplePure = classificationSample.asProbabilitySample()
    probabilitySampleMixed = classificationSample.synthMix(mixingComplexities={2:0.7, 3:0.3}, classLikelihoods='proportional', n=1000)
    probabilitySample = FractionSample(features=numpy.hstack((probabilitySamplePure.features, probabilitySampleMixed.features)),
                                       labels=numpy.hstack((probabilitySamplePure.labels, probabilitySampleMixed.labels)),
                                       classDefinition=probabilitySamplePure.classDefinition)
    probabilitySample = probabilitySampleMixed

    # - subset output classes to be modeled
    #probabilitySample = probabilitySample.subsetClassesByName(names=['Tree'])

    # create testing data
    vectorClassification = VectorClassification(filename=enmapboxtestdata.landcover, classDefinition=classDefinition, idAttribute='Level_1_ID',
                                                minOverallCoverage=1.)

    # - rasterize ground truth classification into probabilities
    gtFractions = vectorClassification.rasterizeAsProbability(probabilityFilename=join(outdir, 'gtFractions.img'), grid=image.grid,
                                                              minOverallCoverage=0.8, oversampling=10, overwrite=overwrite)
    #gtFractions = gtFractions.subsetClassesByName(filename=join(outdir, 'fractions1Class.img'), names=['Tree'])
    gtFractionsSample = image.sampleByRegression(regression=gtFractions)

    # fit model and predict fraction image
    svr = SVR(epsilon=0.05, tol=0.00001, verbose=True, shrinking=True)
    tunedSVR = GridSearchCV(cv=3, estimator=svr, scoring='mean_absolute_error', verbose=True, n_jobs=-1,
                            param_grid = {'kernel': ['rbf'],
                                          'gamma': [0.001, 0.01, 0.1, 1, 10, 100, 1000][::1],
                                          'C': [0.001, 0.01, 0.1, 1, 10, 100, 1000][::1]})
    scaledAndTuned = make_pipeline(MinMaxScaler(), tunedSVR)

    from sklearn.gaussian_process.kernels import RBF
    krr = KernelRidge()
    tunedKRR = GridSearchCV(cv=3, estimator=krr, scoring='mean_absolute_error', verbose=True, n_jobs=-1,
                            param_grid = {"alpha": [1e0, 1e-1, 1e-2, 1e-3],
                                          "kernel": [RBF(scale) for scale in numpy.logspace(-3, 3, 5)]})

    scaledAndTuned = make_pipeline(MinMaxScaler(), tunedKRR)
    #scaledAndTuned = tunedKRR

    #scaledAndTunedSVR = make_pipeline(MinMaxScaler(), SVR(kernel='rbf', C=10000, gamma=0.0000001))

    #scaledAndTunedSVR = LinearSVR(C=100000, epsilon=0., tol=0.00001)
    #scaledAndTunedSVR = make_pipeline(MinMaxScaler(), RandomForestRegressor())
    #scaledAndTuned = RandomForestRegressor()

    #regressor = Regressor(sklEstimator=MultiOutputRegressor(estimator=scaledAndTuned))
#todo: MultiOutput!!!
    regressor = Regressor(sklEstimator=scaledAndTuned)

    if 1:
        regressor.fit(sample=probabilitySample)
    else:
        regressor.fit(sample=gtFractionsSample)

    fractions = regressor.predict(predictionFilename=join(outdir, 'fractions.img'), image=image, overwrite=overwrite)
    fractions.asProbability(classDefinition=classDefinition).asClassColorRGBRaster(imageFilename=join(outdir, 'fractionsRGB.img'), overwrite=overwrite)


    # accuracy assessment
    fractions.assessRegressionPerformance(regression=gtFractions).report().saveHTML(filename=join(outdir, 'report2.html'), open=True)

def hymapRegressionWorkflow():
    datadir = r'C:\EnMAP-Box\SourceCode\lib\hubAPI\_resource\testData\image'
    outdir = join(gettempdir(), 'hubflow_hymapRegression')
    overwrite = True
    print('\nOutput directory: {}'.format(outdir))

    # create training data
    image = Raster(join(datadir, 'Hymap_Berlin-B_Image'))
    train = Regression(join(datadir, 'Hymap_Berlin-B_Regression-Training-Sample'))
    test = Regression(join(datadir, 'Hymap_Berlin-B_Regression-Validation-Sample'))
    trainSample = image.sampleByRegression(regression=train)

    # fit model and predict
    if 1:
        svr = SVR(epsilon=0.00001, tol=0.00001)
        tunedSVR = GridSearchCV(cv=10, estimator=svr, scoring='mean_absolute_error', n_jobs=-1,
                                param_grid = {'kernel': ['rbf'],
                                              'gamma': [0.001, 0.01, 0.1, 1, 10, 100, 1000],
                                              'C': [0.001, 0.01, 0.1, 1, 10, 100, 1000]})
        scaledAndTuned = make_pipeline(MinMaxScaler(), tunedSVR)
    else:
        krr = KernelRidge()
        tunedKRR = GridSearchCV(cv=10, estimator=krr, scoring='mean_absolute_error', verbose=True, n_jobs=-1,
                                param_grid={'kernel': ['rbf'],
                                            'gamma': [0.001, 0.01, 0.1, 1, 10, 100, 1000],
                                            'alpha': [0.001, 0.01, 0.1, 1, 10, 100, 1000]})
        scaledAndTuned = make_pipeline(MinMaxScaler(), tunedKRR)

    #regressor = Regressor(sklEstimator=MultiOutputRegressor(estimator=scaledAndTunedSVR))
    regressor = Regressor(sklEstimator=scaledAndTuned)

    regressor.fit(sample=trainSample)
    prediction = regressor.predict(predictionFilename=join(outdir, 'fractions.img'), image=image, overwrite=overwrite)


    # accuracy assessment
    prediction.assessRegressionPerformance(regression=test).report().saveHTML(filename=join(outdir, 'report2.html'), open=True)

if __name__ == '__main__':
    #synthMixRegressionWorkflow()
    #classificationWorkflow()
    debug_synthMixRegressionWorkflow()
    #hymapRegressionWorkflow()
