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

    def browse(self):

        from objbrowser import browse
        objects = dict()
        objects[self.__class__.__name__.split('.')[-1]] = self
        browse(objects,
               show_callable_attributes=False,
               show_special_attributes=False,
               reset=True)


class Image(FlowObject):

    def __init__(self, filename):
        self.filename = filename


    @property
    def pixelGrid(self):
        return PixelGrid.fromFile(self.filename)

    def asMask(self, ufunc=None):
        return Mask(filename=self.filename, ufunc=ufunc)

    def sampleByClassification(self, classification, mask=None, vmask=None):
        assert isinstance(classification, Classification)
        if mask is None: mask = Mask(None)
        if vmask is None: vmask = VectorMask(None)
        assert isinstance(mask, Mask)
        assert isinstance(vmask, VectorMask)

        features, fractions, classes, classNames, classLookup = ipalg.sampleImageByClassification(image=self.filename, classification=classification.filename,
                                                                                                  mask=mask.filename, maskFunc=mask.ufunc,
                                                                                                  vmask=vmask.filename, vmaskAllTouched=vmask.allTouched, vmaskFilterSQL=vmask.filterSQL)
        return ProbabilitySample(features=features, labels=fractions, classDefinition=ClassDefinition(classes=classes, names=classNames, lookup=classLookup))

class Mask(Image):

    def __init__(self, filename, ufunc=None):
        Image.__init__(self, filename)
        self.ufunc = ufunc

class Vector(FlowObject):

    def __init__(self, filename, layer=0):
        self.filename = filename
        self.layer = layer

    def classify(self, filename, pixelGrid, ids, idAttribute, classNames=None, classLookup=None, oversampling=1):
        assert isinstance(pixelGrid, PixelGrid)
        ipalg.classificationFromVector(vector=self.filename, classification=filename, grid=pixelGrid,
                                     ids=ids, idAttribute=idAttribute, classNames=classNames, classLookup=classLookup,
                                     oversampling=oversampling)
        return Classification(filename=filename)

class VectorMask(Vector):

    def __init__(self, filename, layer=0, allTouched=True, filterSQL=None):
        Vector.__init__(self, filename, layer)
        self.allTouched = allTouched
        self.filterSQL = filterSQL

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

    def __repr__(self):
        return '{cls}(classes={classes}, names={names}, lookup={lookup})'.format(
            cls=self.__class__.__name__,
            classes=repr(self.classes),
            names=repr(self.names),
            lookup=repr(self.lookup))


class Classification(Image):

    def __init__(self, filename, classDefinition=None):
        Image.__init__(self, filename)
        if classDefinition is None:
            classDefinition = ClassDefinition.fromENVIMeta(filename)
        self.classDefinition = classDefinition


class Probability(Image):

    def __init__(self, filename, classDefinition=None):
        Image.__init__(self, filename)
        if classDefinition is None:
            classDefinition = ClassDefinition.fromENVIMeta(filename)
        self.classDefinition = classDefinition


class Regression(Image):
    pass


class UnsupervisedSample(FlowObject):

    def __init__(self, features):
        assert isinstance(features, numpy.ndarray) and features.ndim == 2
        self.features = features

class SupervisedSample(UnsupervisedSample):

    def __init__(self, features, labels, noData, outputNames=None):
        UnsupervisedSample.__init__(self, features=features)
        assert isinstance(labels, numpy.ndarray) and features.ndim == 2
        assert self.features.shape[1] == labels.shape[1]
        self.labels = labels
        self.noData = noData
        self.outputNames = outputNames

class ClassificationSample(SupervisedSample):

    def __init__(self, features, labels, classDefinition, outputName='classification'):
        SupervisedSample.__init__(self, features, labels, noData=0, outputNames=[outputName])
        assert labels.shape[0] == 1
        assert isinstance(classDefinition, ClassDefinition)
        self.classDefinition = classDefinition
        self.histogram = numpy.histogram(labels, bins=self.classDefinition.classes, range=[1, self.classDefinition.classes+1])[0]

    def __repr__(self):
        return '{cls}(features=array{features}, labels=array{labels}, classDefinition={classDefinition}'.format(
            cls=self.__class__.__name__,
            features=repr(list(self.features.shape)),
            labels=repr(list(self.labels.shape)),
            classDefinition=repr(self.classDefinition))


class RegressionSample(SupervisedSample):
    pass

class ProbabilitySample(RegressionSample):

    def __init__(self, features, labels, classDefinition):
        assert isinstance(classDefinition, ClassDefinition)
        assert labels.shape[0] == classDefinition.classes
        SupervisedSample.__init__(self, features, labels, noData=-1, outputNames=classDefinition.names)
        self.classDefinition = classDefinition

    def classify(self, minOverallCoverage=0, minWinnerCoverage=0, progressBar=None):
        labels = dpalg.argmaxProbability(probabilities=self.labels, minOverallCoverage=minOverallCoverage, minWinnerCoverage=minWinnerCoverage, progressBar=progressBar)
        valid = labels != 0
        return ClassificationSample(features=self.features[:,valid[0]], labels=labels[:,valid[0]], classDefinition=self.classDefinition)

    def __repr__(self):
        return '{cls}(features=array{features}, labels=array{labels}, classDefinition={classDefinition}'.format(
            cls=self.__class__.__name__,
            features=repr(list(self.features.shape)),
            labels=repr(list(self.labels.shape)),
            classDefinition=repr(self.classDefinition))

class Estimator(FlowObject):

    SAMPLE_TYPE = SupervisedSample
    PREDICT_TYPE = Image

    def __init__(self, sklEstimator):
        self.sklEstimator = sklEstimator
        self.sample = None

    def fit(self, sample, progressBar=None):
        assert isinstance(sample, self.SAMPLE_TYPE)
        self.sample = sample
        dpalg.estimatorFitData(estimator=self.sklEstimator, features=sample.features, labels=sample.labels, progressBar=progressBar)
        return self

    def predict(self, filename, image, mask=None, vmask=None, progressBar=None):
        assert isinstance(image, Image)
        if mask is None: mask = Mask(None)
        if vmask is None: vmask = VectorMask(None)
        assert isinstance(mask, Mask)
        assert isinstance(vmask, VectorMask)

        classDefinition = getattr(self.sample, 'classDefinition', ClassDefinition(classes=0))
        ipalg.estimatorPredictImage(prediction=filename, noData=self.sample.noData, estimator=self.sklEstimator, image=image.filename,
                                    mask=mask.filename, maskFunc=mask.ufunc,
                                    vmask=vmask.filename, vmaskAllTouched=vmask.allTouched, vmaskFilterSQL=vmask.filterSQL,
                                    outputNames=self.sample.outputNames,
                                    classes=classDefinition.classes, classNames=classDefinition.names, classLookup=classDefinition.lookup,
                                    progressBar=progressBar)

        return self.PREDICT_TYPE(filename=filename)



class Classifier(Estimator):
    SAMPLE_TYPE = ClassificationSample
    PREDICT_TYPE = Classification


class Regressor(Estimator):
    SAMPLE_TYPE = RegressionSample
    PREDICT_TYPE = Regression


class Report(FlowObject):
    pass
