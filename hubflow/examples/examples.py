from hubflow.types import *
import enmaptestdata

imageFilename = enmaptestdata.enmap
vectorFilename = enmaptestdata.landcover

classification3mFilename = r'c:\output\classification3m.img'
classificationFilename = r'c:\output\classification.img'
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
    classification = vector.classify(filename=classification3mFilename,
                                     pixelGrid=image.pixelGrid.newResolution(xRes=3, yRes=3),
                                     ids=[1,2,3,4,5,6], idAttribute='Level_2_ID',
                                     classNames=['Roof',  'Pavement',   'Grass',   'Tree',   'Soil',    'Other'],
                                     classLookup=[168,0,0, 156,156,156,  151,229,0, 35,114,0, 136,89,67, 236,214,0])

def image_sampleByClassification():
    image = Image(filename=imageFilename)
    classification = Classification(filename=classification3mFilename)
    probabilitySample = image.sampleByClassification(classification=classification)
    probabilitySample.pickle(filename=probabilitySampleFilename)
    print(probabilitySample)

def probabilitySample_classify():
    probabilitySample = ProbabilitySample.unpickle(filename=probabilitySampleFilename)
    classificationSample = probabilitySample.classify(minOverallCoverage=0.75, minWinnerCoverage=0.5)
    classificationSample.pickle(filename=classificationSampleFilename)

def classifier_fit():
    from sklearn.ensemble import RandomForestClassifier
    classificationSample = ClassificationSample.unpickle(filename=classificationSampleFilename)
    classifier = Classifier(sklEstimator=RandomForestClassifier())
    classifier.fit(sample=classificationSample)
    classifier.pickle(filename=classifierFilename)

def classifier_predict():
    classifier = Classifier.unpickle(filename=classifierFilename)
    image = Image(filename=imageFilename)
    mask = Mask(filename=classification3mFilename, ufunc=lambda array: array > 3)
    vmask = VectorMask(filename=vectorFilename, allTouched=True, filterSQL="LEVEL_1 = 'Impervious'")
    classifier.predict(filename=classificationFilename, image=image)#, vmask=vmask)
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
    classificationSample = ClassificationSample.unpickle(filename=classificationSampleFilename)
    classifier = Classifier(sklEstimator=classifier)
    classifier.fit(sample=classificationSample)
    classifier.pickle(filename=classifierFilename)

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
    #classifier_fit()
    #svc_fit()
    #classifier_predict()
    #regressor_fit()
    #regressor_predict()
    #transformer_fit()
    #transformer_transform()
    #transformer_inverseTransform()
    clusterer_fit()
    clusterer_predict()
    #browse()
