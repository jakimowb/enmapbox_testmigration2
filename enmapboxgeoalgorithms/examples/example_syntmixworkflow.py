import objbrowser

from os.path import join
from tempfile import gettempdir
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.multioutput import MultiOutputRegressor
from sklearn.preprocessing import StandardScaler
from hubflow.core import *

import enmapboxtestdata

def synthMixRegressionWorkflow():

    wd = r'c:\myOutputs'
    overwrite = True

    print('\n### SyntMixRegression Workflow ###'
          '\nOutput directory: {}'.format(wd))

    # create training data
    # - import ENVI speclib
    speclibFilename = enmapboxtestdata.library # r'c:\my.sli
    unsupervisedSample = Sample.fromENVISpectralLibrary(filename=speclibFilename)

    # - label spectra
    classDefinition = ClassDefinition(names=unsupervisedSample.metadata['level 2 class names'][1:],
                                      colors=unsupervisedSample.metadata['level 2 class lookup'][3:])

    classificationSample = unsupervisedSample.classifyByName(names=unsupervisedSample.metadata['level 2 class spectra names'],
                                                             classDefinition=classDefinition)

    # - generate synthetic mixtures
    probabilitySample = classificationSample.synthMix(mixingComplexities={2:0.5, 3:0.3, 4:0.2}, classLikelihoods='proportional', n=1000)

    # fit model and predict fraction image
    image = Raster(filename=enmapboxtestdata.enmap)

    useRF = True
    if useRF:
        regressor = Regressor(sklEstimator=RandomForestRegressor())
    else:
        svr = SVR()
        param_grid = {'epsilon': [0.], 'kernel': ['rbf'],
                      'gamma': [0.001, 0.01, 0.1, 1, 10, 100, 1000],
                      'C': [0.001, 0.01, 0.1, 1, 10, 100, 1000]}
        tunedSVR = GridSearchCV(cv=3, estimator=svr, scoring='neg_mean_absolute_error', param_grid=param_grid)
        scaledAndTunedSVR = make_pipeline(StandardScaler(), tunedSVR)
        estimator = MultiOutputRegressor(scaledAndTunedSVR)

        regressor = Regressor(sklEstimator=MultiOutputRegressor(estimator=estimator))

    regressor.fit(sample=probabilitySample)
    regressor.pickle(filename=join(wd, 'regressor.pkl'))
    fractions = regressor.predict(predictionFilename=join(wd, 'fractions.img'), image=image, overwrite=overwrite)
    fractions.asProbability(classDefinition=classDefinition).asClassColorRGBRaster(imageFilename=join(wd, 'fractionsRGB.img'), overwrite=overwrite)

if __name__ == '__main__':
    synthMixRegressionWorkflow()