from enmapbox.apps.core.flowprovider import *
import enmaptestdata

imageFilename = enmaptestdata.enmap
vectorFilename = enmaptestdata.landcover
classification3mFilename = r'c:\output\classification3m.img'
classification30mFilename = r'c:\output\classification30m.img'
regression30mFilename = r'c:\output\regression30m.img'
probabilitySample30mFilename = r'c:\output\probabilitySample30m.pkl'
classificationSample30mFilename = r'c:\output\classificationSample30m.pkl'
classifierFilename = r'c:\output\classifier.pkl'
regressorFilename = r'c:\output\regressor.pkl'


def vector_classify():
    image = Image(filename=imageFilename)
    vector = Vector(filename=vectorFilename)
    classification = vector.classify(filename=classification3mFilename,
                                     pixelGrid=image.pixelGrid.newResolution(xRes=3, yRes=3),
                                     ids=[1,2,3,4,5,6], idAttribute='Level_2_ID',
                                     classNames=['Roof',  'Pavement',   'Grass',   'Tree',   'Soil',    'Other'],
                                     classLookup=[168,0,0, 156,156,156,  151,229,0, 35,114,0, 136,89,67, 236,214,0])

def image_sampleByClassification():
    image = Image(filename=imageFilename)
    classification = Classification(filename=classification3mFilename)
    probabilitySample = image.sampleByClassification(classification=classification)
    probabilitySample.pickle(filename=probabilitySample30mFilename)
    print(probabilitySample)
    probabilitySample.browse()

def probabilitySample_classify():
    probabilitySample = ProbabilitySample.unpickle(filename=probabilitySample30mFilename)
    classificationSample = probabilitySample.classify(minOverallCoverage=0.75, minWinnerCoverage=0.5)
    classificationSample.pickle(filename=classificationSample30mFilename)
    print(classificationSample)
    classificationSample.browse()

def classifier_fit():
    from sklearn.ensemble import RandomForestClassifier
    classificationSample = ClassificationSample.unpickle(filename=classificationSample30mFilename)
    classifier = Classifier(sklEstimator=RandomForestClassifier())
    classifier.fit(sample=classificationSample)
    classifier.pickle(filename=classifierFilename)
    classifier.browse()

def classifier_predict():
    classifier = Classifier.unpickle(filename=classifierFilename)
    image = Image(filename=imageFilename)
    mask = Mask(filename=classification3mFilename, ufunc=lambda array: array > 3)
    vmask = VectorMask(filename=vectorFilename, allTouched=True, filterSQL="LEVEL_1 = 'Impervious'")
    classifier.predict(filename=classification30mFilename, image=image)#, vmask=vmask)
    #classifier.predict(filename=classification30mFilename, image=image, mask=mask)

def regressor_fit():
    from sklearn.ensemble import RandomForestRegressor
    regressionSample = RegressionSample.unpickle(filename=probabilitySample30mFilename)
    regressor = Regressor(sklEstimator=RandomForestRegressor())
    regressor.fit(sample=regressionSample)
    regressor.pickle(filename=regressorFilename)

def regressor_predict():
    regressor = Regressor.unpickle(filename=regressorFilename)
    image = Image(filename=imageFilename)
    mask = Mask(filename=classification3mFilename)
    vmask = VectorMask(filename=vectorFilename, allTouched=True)
    regressor.predict(filename=regression30mFilename, image=image, mask=mask)

def svc_fit():
    from sklearn.pipeline import make_pipeline
    from sklearn.model_selection import GridSearchCV
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    from sklearn.svm import SVC

    # Scikit-Learn stuff
    estimator = make_pipeline(PCA(n_components=0.95),
                              StandardScaler(),
                              SVC())

    classifier = GridSearchCV(estimator=estimator,
                              param_grid=dict(svc__C=[10**i for i in range(-2,4)],
                                              svc__gamma=[10**i for i in range(-2,4)]),
                              scoring='f1_weighted', cv=3, n_jobs=4)

    # EnMAP-Box Flow-API stuff
    classificationSample = ClassificationSample.unpickle(filename=classificationSample30mFilename)
    classifier = Classifier(sklEstimator=classifier)
    classifier.fit(sample=classificationSample)
    classifier.pickle(filename=classifierFilename)
    classifier.browse()

def browse():

    image = Image(filename=imageFilename)
    vector = Vector(filename=vectorFilename)
    mask = Mask(filename=classification3mFilename, ufunc=lambda array: array > 3)
    vmask = VectorMask(filename=vectorFilename, allTouched=True, filterSQL="LEVEL_1 = 'Impervious'")

    classification = Classification(filename=classification3mFilename)
    #probability = Probability(filename=regression30mFilename)
    regression = Regression(filename=regression30mFilename)

    classificationSample = ClassificationSample.unpickle(filename=classificationSample30mFilename)
    probabilitySample = ProbabilitySample.unpickle(filename=probabilitySample30mFilename)
    regressionSample = RegressionSample.unpickle(filename=probabilitySample30mFilename)

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
    #classifier_fit()
    #svc_fit()
    classifier_predict()
    #regressor_fit()
    #regressor_predict()
    #browse()
