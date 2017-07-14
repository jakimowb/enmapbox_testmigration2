import random, os, pickle
import numpy
from hubdc.model import Open, PixelGrid
import sklearn.base
import enmapbox.apps.core.imageProcessingAlgorithms as ipalg
import enmapbox.apps.core.dataProcessingAlgorithms as dpalg


class FlowObject():

    def pickle(self, filename):
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        with open(filename, 'wb') as f:
            pickle.dump(obj=self, file=f, protocol=1)

    @classmethod
    def unpickle(cls, filename):
        with open(filename, 'rb') as f:
            obj = pickle.load(file=f)
        assert isinstance(obj, cls), 'wrong type ({t1}), expected type: {t2}'.format(t1=type(obj), t2=cls)
        return obj

class Image(FlowObject):

    def __init__(self, filename):
        self.filename = filename


    @property
    def pixelGrid(self):
        return PixelGrid.fromFile(self.filename)

    def sampleByClassification(self, classification):
        assert isinstance(classification, Classification)
        features, fractions, classes, classNames, classLookup = ipalg.sampleImageByClassification(image=self.filename, classification=classification.filename)
        return ProbabilitySample(features=features, labels=fractions, classDefinition=ClassDefinition(classes=classes, names=classNames, lookup=classLookup))


class Mask(Image):
    pass


class Vector(FlowObject):

    def __init__(self, filename, layer=0):
        self.filename = filename
        self.layer = layer

    def classify(self, filename, pixelGrid, ids, idAttribute, classNames=None, classLookup=None, oversampling=1):
        assert isinstance(pixelGrid, PixelGrid)
        alg.classificationFromVector(vector=self.filename, classification=filename, grid=pixelGrid,
                                     ids=ids, idAttribute=idAttribute, classNames=classNames, classLookup=classLookup,
                                     oversampling=oversampling)
        return Classification(filename=filename)


class ClassDefinition(FlowObject):

    @staticmethod
    def fromENVIMeta(filename):
        ds = Open(filename)
        classes = ds.getMetadataItem(key='classes', domain='ENVI', dtype=int)
        names = ds.getMetadataItem(key='class names', domain='ENVI')
        lookup = ds.getMetadataItem(key='class lookup', domain='ENVI', dtype=int)
        return ClassDefinition(classes=classes-1, names=names[1:], lookup=lookup[3:])

    def __init__(self, classes, names=None, lookup=None):

        self.classes = classes
        if names is None:
            names = ['class {}'.format(i+1) for i in range(classes)]
        if lookup is None:
            lookup = [random.randint(1, 255) for i in range(classes * 3)]

        assert len(names) == classes
        assert len(lookup) == classes*3

        self.names = names
        self.lookup = lookup


class Classification(Mask):

    def __init__(self, filename, classDefinition=None):
        Mask.__init__(self, filename)
        if classDefinition is None:
            classDefinition = ClassDefinition.fromENVIMeta(filename)
        self.classDefinition = classDefinition


class UnsupervisedSample(FlowObject):

    def __init__(self, features):
        assert isinstance(features, numpy.ndarray) and features.ndim == 2
        self.features = features


class SupervisedSample(UnsupervisedSample):

    def __init__(self, features, labels, noData):
        UnsupervisedSample.__init__(self, features=features)
        assert isinstance(labels, numpy.ndarray) and features.ndim == 2
        assert self.features.shape[1] == labels.shape[1]
        self.labels = labels
        self.noData = noData


class ClassificationSample(SupervisedSample):

    def __init__(self, features, labels, classDefinition):
        SupervisedSample.__init__(self, features, labels, noData=0)
        assert labels.shape[0] == 1
        assert isinstance(classDefinition, ClassDefinition)
        self.classDefinition = classDefinition


class ProbabilitySample(SupervisedSample):

    def __init__(self, features, labels, classDefinition):
        SupervisedSample.__init__(self, features, labels, noData=-1)
        assert isinstance(classDefinition, ClassDefinition)
        assert labels.shape[0] == classDefinition.classes
        self.classDefinition = classDefinition

    def classify(self, minOverallCoverage=0, minWinnerCoverage=0, progressBar=None):
        labels = dpalg.argmaxProbability(probabilities=self.labels, minOverallCoverage=minOverallCoverage, minWinnerCoverage=minWinnerCoverage, progressBar=progressBar)
        valid = labels != 0
        return ClassificationSample(features=self.features[:,valid[0]], labels=labels[:,valid[0]], classDefinition=self.classDefinition)


class Classifier(FlowObject):

    def __init__(self, sklClassifier):
        assert isinstance(sklClassifier, sklearn.base.ClassifierMixin)
        self.sklClassifier = sklClassifier
        self.sample = None

    def fit(self, sample, progressBar=None):
        assert isinstance(sample, ClassificationSample)
        self.sample = sample
        dpalg.classifierFitData(classifier=self.sklClassifier, features=sample.features, labels=sample.labels, progressBar=progressBar)

    def predictSample(self, sample, progressBar=None):
        assert isinstance(sample, UnsupervisedSample)
        labels = alg.classificationPredictSample(classifier=self.sklClassifier, features=sample.features, progressBar=progressBar)
        return ClassificationSample(features=sample.features, labels=labels, classDefinition=self.sample.classDefinition)

class Report(FlowObject):
    pass