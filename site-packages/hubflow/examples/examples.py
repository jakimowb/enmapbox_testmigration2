import gdal
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot
from hubdc.applier import ApplierControls, ApplierInputOptions
from hubflow.types import *
import enmapboxtestdata

imageFilename = enmapboxtestdata.enmap
image2Filename = enmapboxtestdata.hymap
vectorFilename = enmapboxtestdata.landcover
speclibFilename = enmapboxtestdata.speclib
speclib2Filename = r'c:\output\speclib.sli'

classification3mFilename = r'c:\output\classification3m.img'
classificationFilename = r'c:\output\classification.img'
probabilityFilename = r'c:\output\probability.img'
regressionFilename = r'c:\output\regression.img'
transformationFilename = r'c:\output\transformation.img'
inverseTransformationFilename =  r'c:\output\inverseTransformation.img'
clusteringFilename = r'c:\output\clustering.img'

probabilitySampleFilename = r'c:\output\probabilitySample.pkl'
classificationSampleFilename = r'c:\output\classificationSample.pkl'
classifierFilename = r'c:\output\classifier.pkl'
regressorFilename = r'c:\output\regressor.pkl'
transformerFilename = r'c:\output\transformer.pkl'
clustererFilename = r'c:\output\clusterer.pkl'

def vector_classify():
    image = Image(filename=imageFilename)
    vector = Vector(filename=vectorFilename)
    classification = vector.rasterizeAsClassification(filename=classification3mFilename,
                                                      pixelGrid=image.pixelGrid.newResolution(xRes=3, yRes=3),
                                                      ids=[1,2,3,4,5,6], idAttribute='Level_2_ID',
                                                      classNames=['Roof',  'Pavement',   'Grass',   'Tree',   'Soil',    'Other'],
                                                      classLookup=[168,0,0, 156,156,156,  151,229,0, 35,114,0, 136,89,67, 236,214,0])

def image_sampleByClassification():
    image = Image(filename=imageFilename)
    classification = Classification(filename=classification3mFilename)
    probabilitySample = image.sampleByClassification(classification=classification)
    probabilitySample.pickle(filename=probabilitySampleFilename)

def probabilitySample_classify():
    probabilitySample = ProbabilitySample.unpickle(filename=probabilitySampleFilename)
    classificationSample = probabilitySample.classifyByProbability(minOverallCoverage=0.75, minWinnerCoverage=0.5)
    classificationSample.pickle(filename=classificationSampleFilename)

def unsupervisedSample_classifyByName():
    unsupervisedSample = UnsupervisedSample.fromENVISpectralLibrary(filename=enmapboxtestdata.speclib)
    classDefinition = ClassDefinition(names=unsupervisedSample.metadata['level 2 class names'][1:],
                                      lookup=unsupervisedSample.metadata['level 2 class lookup'][3:])
    classificationSample = unsupervisedSample.classifyByClassName(names=unsupervisedSample.metadata['level 2 spectra names'],
                                                                  classDefinition=classDefinition)
    classificationSample.scaleFeaturesInplace(factor=10000.)
    classificationSample.pickle(filename=classificationSampleFilename)

def classificationSample_synthMix():
    classificationSample = ClassificationSample.unpickle(filename=classificationSampleFilename)
#    probabilitySample = classificationSample.synthMix(mixingComplexities={2: 0.5, 3: 0.3, 4: 0.2},
#                                                      classLikelihoods='proportional', n=100)
    probabilitySample = classificationSample.synthMix(mixingComplexities={2: 1.}, classLikelihoods={1:1.}, n=100)
    probabilitySample.pickle(filename=probabilitySampleFilename)

def unsupervisedSample_saveAsSpectralLibrary():
    probabilitySample = UnsupervisedSample.fromENVISpectralLibrary(filename=speclibFilename)
    probabilitySample.browse()
    #probabilitySample.saveAsENVISpectralLibrary(filename=speclib2Filename)

def classificationSample_saveAsSpectralLibrary():
    classificationSample = ClassificationSample.unpickle(filename=classificationSampleFilename)
    classificationSample.saveAsENVISpectralLibrary(filename=speclib2Filename)
    ClassificationSample.fromENVISpectralLibrary(filename=speclib2Filename)

def probabilitySample_saveAsSpectralLibrary():
    probabilitySample = ProbabilitySample.unpickle(filename=probabilitySampleFilename)
    probabilitySample.saveAsENVISpectralLibrary(filename=speclib2Filename)
    ProbabilitySample.fromENVISpectralLibrary(filename=speclib2Filename)

def probabilitySample_subsetClassesByNames():
    probabilitySample = ProbabilitySample.unpickle(filename=probabilitySampleFilename)
    probabilitySample = probabilitySample.subsetClassesByName(names=['Roof', 'Tree'])
    probabilitySample.pickle(filename=probabilitySampleFilename)

def classifier_fit():
    from sklearn.ensemble import RandomForestClassifier
    classificationSample = ClassificationSample.unpickle(filename=classificationSampleFilename)
    classifier = Classifier(sklEstimator=RandomForestClassifier(class_weight='balanced'))
    classifier.fit(sample=classificationSample)
    classifier.pickle(filename=classifierFilename)

def classifier_predict():
    classifier = Classifier.unpickle(filename=classifierFilename)
    image = Image(filename=imageFilename)
    mask = Mask(filename=classification3mFilename, ufunc=lambda array: array > 3)
    vmask = VectorMask(filename=vectorFilename, allTouched=True, filterSQL="LEVEL_1 = 'Impervious'")
    classifier.predict(filename=classificationFilename, image=image)#, vmask=vmask)
    #classifier.predict(filename=classificationFilename, image=image, mask=mask)

def classifier_predictProbability():
    assert 0
    classifier = Classifier.unpickle(filename=classifierFilename)
    image = Image(filename=imageFilename)
    mask = Mask(filename=classification3mFilename, ufunc=lambda array: array > 3)
    vmask = VectorMask(filename=vectorFilename, allTouched=True, filterSQL="LEVEL_1 = 'Impervious'")
    classifier.predictProbability(filename=probabilityFilename, image=image)#, vmask=vmask)
    #classifier.predict(filename=classificationFilename, image=image, mask=mask)

def regressor_fit():
    from sklearn.ensemble import RandomForestRegressor

    regressionSample = RegressionSample.unpickle(filename=probabilitySampleFilename)
    regressor = Regressor(sklEstimator=RandomForestRegressor())
    regressor.fit(sample=regressionSample)
    regressor.pickle(filename=regressorFilename)

def regressor_predict():
    regressor = Regressor.unpickle(filename=regressorFilename)
    image = Image(filename=imageFilename)
    mask = Mask(filename=classification3mFilename)
    vmask = VectorMask(filename=vectorFilename, allTouched=True)
    regressor.predict(filename=regressionFilename, image=image, mask=mask)

def transformer_fit():
    from sklearn.decomposition import PCA
    unsupervisdedSample = UnsupervisedSample.unpickle(filename=classificationSampleFilename)
    transformer = Transformer(sklEstimator=PCA(n_components=3))
    transformer.fit(sample=unsupervisdedSample)
    transformer.pickle(filename=transformerFilename)

def transformer_transform():
    transformer = Transformer.unpickle(filename=transformerFilename)
    image = Image(filename=imageFilename)
    mask = Mask(filename=classification3mFilename)
    vmask = VectorMask(filename=vectorFilename, allTouched=True)
    transformer.transform(filename=transformationFilename, image=image, mask=mask, vmask=vmask)

def transformer_inverseTransform():
    transformer = Transformer.unpickle(filename=transformerFilename)
    image = Image(filename=transformationFilename)
    mask = Mask(filename=classification3mFilename)
    vmask = VectorMask(filename=vectorFilename, allTouched=True)
    transformer.inverseTransform(filename=inverseTransformationFilename, image=image, mask=mask, vmask=vmask)

def svc_fit():
    from sklearn.pipeline import make_pipeline
    from sklearn.model_selection import GridSearchCV
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import RobustScaler, StandardScaler
    from sklearn.svm import SVC

    # Scikit-Learn stuff
    svc = GridSearchCV(estimator=SVC(),
                       param_grid=dict(C=[10**i for i in range(-2,4)],
                                       gamma=[10**i for i in range(-2,4)]),
                       scoring='f1_weighted', cv=3)

    estimator = make_pipeline(StandardScaler(), svc)


    # EnMAP-Box Flow-API stuff
    classificationSample = ClassificationSample.unpickle(filename=classificationSampleFilename)
    classifier = Classifier(sklEstimator=estimator)
    classifier.fit(sample=classificationSample)
    classifier.pickle(filename=classifierFilename)

def svr_fit():
    from sklearn.svm import SVR
    from sklearn.multioutput import MultiOutputRegressor
    regressionSample = RegressionSample.unpickle(filename=probabilitySampleFilename)
    regressor = Regressor(sklEstimator=MultiOutputRegressor(estimator=SVR()))
    regressor.fit(sample=regressionSample)
    regressor.pickle(filename=regressorFilename)

def baggingRegressor_fit():
    from sklearn.ensemble import RandomForestRegressor, BaggingRegressor
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.svm import SVR
    from sklearn.pipeline import make_pipeline
    from sklearn.model_selection import GridSearchCV
    from sklearn.preprocessing import StandardScaler
    from sklearn.multioutput import MultiOutputRegressor

    base_estimator = GridSearchCV(estimator=make_pipeline(StandardScaler(), SVR(epsilon=0.001)), cv=3,
                                  param_grid=dict(svr__C=[10**i for i in range(-3,3)],
                                                  svr__gamma=[10**i for i in range(-3,3)]))

    #base_estimator = RandomForestRegressor(n_estimators=10)
    #base_estimator = make_pipeline(StandardScaler(), GaussianProcessRegressor())
    ensemble_estimator = BaggingRegressor(base_estimator=base_estimator, n_estimators=10, max_samples=1000)
    multi_estimator = MultiOutputRegressor(estimator=ensemble_estimator, n_jobs=-1)

    #multi_estimator = MultiOutputRegressor(base_estimator, n_jobs=-1)

    regressionSample = RegressionSample.unpickle(filename=probabilitySampleFilename)
    regressor = Regressor(sklEstimator=multi_estimator)
    regressor.fit(sample=regressionSample)
    regressor.pickle(filename=regressorFilename)

def clusterer_fit():
    from sklearn.cluster import KMeans
    unsupervisedSample = UnsupervisedSample.unpickle(filename=classificationSampleFilename)
    clusterer = Clusterer(sklEstimator=KMeans())
    clusterer.fit(sample=unsupervisedSample)
    clusterer.pickle(filename=clustererFilename)

def clusterer_predict():
    clusterer = Clusterer.unpickle(filename=clustererFilename)
    image = Image(filename=imageFilename)
    mask = Mask(filename=classification3mFilename)
    vmask = VectorMask(filename=vectorFilename, allTouched=True)
    clusterer.predict(filename=clusteringFilename, image=image, mask=mask, vmask=vmask)

def browse():

    image = Image(filename=imageFilename)
    vector = Vector(filename=vectorFilename)
    mask = Mask(filename=classification3mFilename, ufunc=lambda array: array > 3)
    vmask = VectorMask(filename=vectorFilename, allTouched=True, filterSQL="LEVEL_1 = 'Impervious'")

    classification = Classification(filename=classification3mFilename)
    #probability = Probability(filename=regressionFilename)
    regression = Regression(filename=regressionFilename)

    classificationSample = ClassificationSample.unpickle(filename=classificationSampleFilename)
    probabilitySample = ProbabilitySample.unpickle(filename=probabilitySampleFilename)
    regressionSample = RegressionSample.unpickle(filename=probabilitySampleFilename)

    classifier = Classifier.unpickle(filename=classifierFilename)
    regressor = Regressor.unpickle(filename=regressorFilename)

    import objbrowser
    objects = dict()
    objects['FlowDataTypes'] = [image, vector, mask, vmask, classification, regression,
                                classificationSample, probabilitySample, regressionSample, classifier, regressor]
    objbrowser.browse(objects, show_callable_attributes=False, show_special_attributes=False, reset=True)


if __name__ == '__main__':
    #vector_classify()
    #image_sampleByClassification()
    #probabilitySample_classify()
    #unsupervisedSample_classifyByName()
    #classificationSample_synthMix()
    #unsupervisedSample_saveAsSpectralLibrary()
    #classificationSample_saveAsSpectralLibrary()
    #probabilitySample_saveAsSpectralLibrary()
    #probabilitySample_subsetClassesByNames()
    #classifier_fit()
    #svc_fit()
    #classifier_predict()
    #regressor_fit()
    #svr_fit()
    #baggingRegressor_fit()
    #regressor_predict()
    #transformer_fit()
    #transformer_transform()
    #transformer_inverseTransform()
    #clusterer_fit()
    #clusterer_predict()

    image_basicStatistics()
    #image_scatterMatrix()
    #browse()
