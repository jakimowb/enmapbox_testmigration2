from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from hubflow.types import *
from hubdc.applier import ApplierControls

def script():
    ApplierControls.DEFAULT_NWORKER = 6
    ApplierControls.DEFAULT_WINDOWXSIZE = 512
    ApplierControls.DEFAULT_WINDOWYSIZE = 512

    # draw all labeled samples

    image = Image(filename=r'C:\subset_image\subset_pca')
    classification = Classification(filename=r'C:\subset_image\training_worldview3_pca')

    if 1:  # draw from image
        probabilitySample = image.sampleByClassification(classification=classification,
                                                         mask=image.asMask())  # use image as mask to not draw samples from the noData region
        classificationSample = probabilitySample.classifyByProbability(minOverallCoverage=0.99, minWinnerCoverage=0.99)
        classificationSample.pickle(filename=r'C:\subset_image\sample.pkl')
    else:  # load from file
        classificationSample = ClassificationSample.unpickle(filename=r'C:\subset_image\sample.pkl')

    # draw 1000 random (stratified) samples
    X, y = classificationSample.features.T, classificationSample.labels.ravel()
    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=1000, stratify=y)
    smallClassificationSample = ClassificationSample(features=X_train.T, labels=numpy.atleast_2d(y_train),
                                                     classDefinition=classificationSample.classDefinition)

    # fit RFC and predict
    rfc = Classifier(sklEstimator=RandomForestClassifier())
    rfc.fit(sample=smallClassificationSample)
    rfc.predict(filename=r'C:\subset_image\rfcClassification.img', image=image, mask=image.asMask())

    # fit SVC (tune hyperparameters with grid search and cross-validation) and predict
    svc = Classifier(sklEstimator=GridSearchCV(estimator=make_pipeline(StandardScaler(), SVC()),
                                               param_grid=dict(svc__C=[10 ** i for i in range(-2, 4)],
                                                               svc__gamma=[10 ** i for i in range(-2, 4)]),
                                               scoring='f1_weighted', cv=3, n_jobs=6))
    svc.fit(sample=smallClassificationSample)
    svc.predict(filename=r'C:\subset_image\svcClassification.img', image=image, mask=image.asMask())

if __name__ == '__main__':
    script()