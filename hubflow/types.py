from operator import xor
import random, os, pickle
import gdal
import numpy
import sklearn.metrics
import spectral
from hubdc.applier import ApplierInputOptions
from hubdc.model import Open, OpenLayer, PixelGrid
import hubflow.ip_algorithms as ipalg
import hubflow.dp_algorithms as dpalg
from hubflow.report import *
from hubflow import signals
import matplotlib
matplotlib.use('Qt4Agg')
try:
    from matplotlib import pyplot
except:
    pass

spectral.settings.envi_support_nonlowercase_params = True


class FlowObject():

    def pickle(self, filename):
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        with open(filename, 'wb') as f:
            pickle.dump(obj=self, file=f, protocol=1)
        signals.sigFileCreated.emit(filename)

    @classmethod
    def unpickle(cls, filename):
        with open(filename, 'rb') as f:
            obj = pickle.load(file=f)
        assert isinstance(obj, cls), 'wrong type ({t1}), expected type: {t2}'.format(t1=type(obj), t2=cls)
        return obj

    def browse(self):
        from objbrowser import ObjectBrowser
        from objbrowser.attribute_model import ATTR_MODEL_REPR, ATTR_MODEL_NAME, DEFAULT_ATTR_COLS


        objects = dict()
        objects[self.__class__.__name__.split('.')[-1]] = self
        ObjectBrowser.browse(objects,
                             attribute_columns = DEFAULT_ATTR_COLS,
                             attribute_details = (ATTR_MODEL_REPR,),
                             show_callable_attributes = None,
                             show_special_attributes = None,
                             auto_refresh=None,
                             refresh_rate=None,
                             reset = False)
        return

class Image(FlowObject):

    def __init__(self, filename):
        self.filename = filename

    @property
    def pixelGrid(self):
        return PixelGrid.fromFile(self.filename)

    def asMask(self, ufunc=None):
        return Mask(filename=self.filename, ufunc=ufunc)

    def asProbability(self, classDefinition):
        return Probability(filename=self.filename, classDefinition=classDefinition)

    def sampleByClassification(self, classification, mask=None, **kwargs):
        sample = ipalg.imageSample(image=self, labels=classification, mask=mask, **kwargs)
        assert isinstance(sample, ProbabilitySample)
        return sample

    def sampleByRegression(self, regression, mask=None, **kwargs):
        sample = ipalg.imageSample(image=self, labels=regression, mask=mask, **kwargs)
        assert isinstance(sample, RegressionSample)
        return sample

    def sampleByProbability(self, probability, mask=None, **kwargs):
        sample = ipalg.imageSample(image=self, labels=probability, mask=mask, **kwargs)
        assert isinstance(sample, ProbabilitySample)
        return sample

    def sampleByMask(self, mask, **kwargs):
        sample = ipalg.imageSample(image=self, labels=mask, mask=None, **kwargs)
        assert isinstance(sample, UnsupervisedSample)
        return sample

    def basicStatistics(self, bandIndicies=None, mask=None, **kwargs):
        return ipalg.imageBasicStatistics(image=self, bandIndicies=bandIndicies, mask=mask, **kwargs)

    def scatterMatrix(self, image2, bandIndex1, bandIndex2, range1, range2, bins=256, mask=None, stratification=None, **kwargs):
        return ipalg.imageScatterMatrix(image1=self, image2=image2, bandIndex1=bandIndex1, bandIndex2=bandIndex2,
                                        range1=range1, range2=range2, bins=bins, mask=mask, stratification=stratification, **kwargs)

class Mask(Image):

    def __init__(self, filename, ufunc=None):
        Image.__init__(self, filename)
        self.ufunc = ufunc
        self.noData = 0

class Vector(FlowObject):

    def __init__(self, filename, layer=0, initValue=0, burnValue=1, burnAttribute=None, allTouched=False, filterSQL=None, dtype=numpy.float32):
        self.filename = filename
        self.layer = layer
        self.initValue = initValue
        self.burnValue = burnValue
        self.burnAttribute = burnAttribute
        self.allTouched = allTouched
        self.filterSQL = filterSQL
        self.dtype = dtype

    def rasterize(self, imageFilename, grid, **kwargs):
        return ipalg.vectorRasterize(vector=self, imageFilename=imageFilename, grid=grid, **kwargs)

    def uniqueValues(self, attribute, **kwargs):
        return ipalg.vectorUniqueValues(vector=self, attribute=attribute, **kwargs)

class VectorClassification(Vector):

    def __init__(self, filename, classDefinition, idAttribute, layer=0, allTouched=False, filterSQL=None, minOverallCoverage=0.5, minWinnerCoverage=0.5):
        Vector.__init__(self, filename=filename, layer=layer, initValue=0, burnAttribute=idAttribute, allTouched=allTouched, filterSQL=filterSQL, dtype=numpy.uint8)
        assert isinstance(classDefinition, ClassDefinition)
        self.classDefinition = classDefinition
        self.idAttribute = idAttribute
        self.minOverallCoverage = minOverallCoverage
        self.minWinnerCoverage = minWinnerCoverage

    def rasterizeAsClassification(self, classificationFilename, grid, oversampling=1, **kwargs):
        return ipalg.vectorClassificationRasterizeAsClassification(vectorClassification=self, classificationFilename=classificationFilename, grid=grid, oversampling=oversampling, **kwargs)

    def rasterizeAsProbability(self, probabilityFilename, grid, oversampling=1, **kwargs):
        return ipalg.vectorClassificationRasterizeAsProbability(vectorClassification=self, probabilityFilename=probabilityFilename, grid=grid, oversampling=oversampling, **kwargs)


class ClassDefinition(FlowObject):

    @staticmethod
    def fromENVIMeta(filename):
        ds = Open(filename)
        classes = ds.getMetadataItem(key='classes', domain='ENVI', dtype=int)
        names = ds.getMetadataItem(key='class names', domain='ENVI')
        lookup = ds.getMetadataItem(key='class lookup', domain='ENVI', dtype=int)
        return ClassDefinition(classes=classes-1, names=names[1:], lookup=lookup[3:])

    def equal(self, other, compareLookup=True):
        assert isinstance(other, ClassDefinition)
        equal = self.classes == other.classes
        equal &= all([a == b for a, b in zip(self.names, other.names)])
        equal &= not compareLookup or all([a == b for a, b in zip(self.lookup, other.lookup)])
        return equal

    def __init__(self, classes=None, names=None, lookup=None):

        assert classes is not None or names is not None
        if classes is None:
            classes = len(names)
        self.classes = classes
        if names is None:
            names = ['class {}'.format(i+1) for i in range(classes)]
        if lookup is None:
            lookup = [random.randint(1, 255) for i in range(classes * 3)]

        assert len(names) == classes
        assert len(lookup) == classes*3

        self.names = names
        self.lookup = [int(v) for v in lookup]

    def __repr__(self):
        return '{cls}(classes={classes}, names={names}, lookup={lookup})'.format(
            cls=self.__class__.__name__,
            classes=repr(self.classes),
            names=repr(self.names),
            lookup=repr(self.lookup))

    def getColor(self, id=None, name=None):
        if id is None:
            id = self.names.index((name))
        return self.lookup[id*3:id*3+3]

class Classification(Image):

    def __init__(self, filename, classDefinition=None, minOverallCoverage=0.5, minWinnerCoverage=0.5):
        Image.__init__(self, filename)
        if classDefinition is None:
            classDefinition = ClassDefinition.fromENVIMeta(filename)
        self.classDefinition = classDefinition
        self.noData = 0
        self.minOverallCoverage = minOverallCoverage
        self.minWinnerCoverage = minWinnerCoverage

    def assessClassificationPerformance(self, classification, **kwargs):
        assert isinstance(classification, Classification)
        yP = self.sampleByMask(mask=classification.asMask(), grid=classification.pixelGrid,
                               imageOptions=ApplierInputOptions(resampleAlg=gdal.GRA_NearestNeighbour), **kwargs).features[0]
        yT = classification.sampleByMask(mask=classification.asMask(), grid=classification.pixelGrid,
                               imageOptions=ApplierInputOptions(resampleAlg=gdal.GRA_NearestNeighbour), **kwargs).features[0]

        return ClassificationPerformance(yP=yP, yT=yT, classDefinitionP=self.classDefinition, classDefinitionT=classification.classDefinition)


class Regression(Image):

    def __init__(self, filename, noData=None, outputNames=None):
        Image.__init__(self, filename)
        if noData is None:
            noData = Open(filename).getNoDataValue()
        if outputNames is None:
            outputNames = [band.getDescription() for band in Open(filename)]
        assert noData is not None
        self.noData = noData
        self.outputNames = outputNames

    def assessRegressionPerformance(self, regression, **kwargs):
        assert isinstance(regression, Regression)
        yP = self.sampleByMask(mask=regression.asMask(), grid=regression.pixelGrid,
                               imageOptions=ApplierInputOptions(resampleAlg=gdal.GRA_NearestNeighbour), **kwargs).features
        yT = regression.sampleByMask(mask=regression.asMask(), grid=regression.pixelGrid,
                               imageOptions=ApplierInputOptions(resampleAlg=gdal.GRA_NearestNeighbour), **kwargs).features

        return RegressionPerformance(yT=yT, yP=yP, outputNamesT=regression.outputNames, outputNamesP=self.outputNames)


class Probability(Regression):

    def __init__(self, filename, classDefinition=None):
        if classDefinition is None:
            classDefinition = ClassDefinition.fromENVIMeta(filename)
        Regression.__init__(self, filename=filename, noData=-1, outputNames=classDefinition.names)
        self.classDefinition = classDefinition

    def asClassColorRGBImage(self, imageFilename, filterById=None, filterByName=None, **kwargs):
        return ipalg.probabilityAsClassColorRGBImage(probability=self, imageFilename=imageFilename,
                                                     filterById=filterById, filterByName=filterByName, **kwargs)


class UnsupervisedSample(FlowObject):

    def __init__(self, features, metadata=None):
        assert isinstance(features, numpy.ndarray) and features.ndim == 2
        self.features = features
        self.metadata = metadata
        self.nbands , self.nsamples = self.features.shape

    def __repr__(self):
        return '{cls}(features=array{features}'.format(cls=self.__class__.__name__, features=repr(list(self.features.shape)))

    @staticmethod
    def fromENVISpectralLibrary(filename):
        headers = [filename + '.hdr', filename[:-4] + '.hdr']
        for header in headers:
            if os.path.exists(header):
                library = spectral.envi.open(file=header)
                return UnsupervisedSample(features=library.spectra.T, metadata=library.metadata)
        raise Exception('header file not found')

    def saveAsENVISpectralLibrary(self, filename):
        metadata = self.metadata.copy()
        if 'spectra names' not in metadata:
            metadata['spectra names'] = ['profile '+str(i+1) for i in range(self.features.shape[1])]
        if 'wavelength' not in metadata:
            metadata['wavelength'] = range(self.features.shape[0])
            metadata['wavelength units'] = 'indices'

        library = spectral.envi.SpectralLibrary(data=self.features.T, header=metadata, params=None)
        fileBaseName = filename.replace('.hdr', '').replace('.sli', '').replace('.esl', '')
        library.save(fileBaseName=fileBaseName)

        header = spectral.envi.read_envi_header(file=fileBaseName+'.hdr')
        self._saveAsENVISpectralLibraryUpdateHeader(header)
        spectral.envi.write_envi_header(fileName=fileBaseName+'.hdr', header_dict=header, is_library=True)

    def _saveAsENVISpectralLibraryUpdateHeader(self, header):
        for key in ['data ignore value', 'wavelength', 'wavelength units']:
            if key not in self.metadata:
                del header[key]

    def scaleFeaturesInplace(self, factor):
        self.features = self.features*factor

    def classifyByClassName(self, names, classDefinition):
        assert len(names) == self.nsamples
        assert isinstance(classDefinition, ClassDefinition)
        labels = numpy.atleast_2d(numpy.array(dpalg.classifyNames(names, classNames=classDefinition.names, indexBase=1), dtype=numpy.uint8))
        return ClassificationSample(features=self.features, labels=labels, metadata=self.metadata, classDefinition=classDefinition)

class SupervisedSample(UnsupervisedSample):

    def __init__(self, features, labels, noData, outputNames, metadata=None):
        UnsupervisedSample.__init__(self, features=features, metadata=metadata)

        assert isinstance(labels, numpy.ndarray) and features.ndim == 2
        assert self.features.shape[1] == labels.shape[1]
        self.labels = labels
        self.noData = noData
        self.outputNames = outputNames

class ClassificationSample(SupervisedSample):

    def __init__(self, features, labels, classDefinition, metadata=None, outputName='classification'):
        SupervisedSample.__init__(self, features, labels, noData=0, metadata=metadata, outputNames=[outputName])
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

    @staticmethod
    def fromENVISpectralLibrary(filename):
        sample = UnsupervisedSample.fromENVISpectralLibrary(filename=filename)
        classDefinition = ClassDefinition(classes=int(sample.metadata['classes'])-1,
                                          names=list(map(str, sample.metadata['class names'][1:])),
                                          lookup=list(map(int, sample.metadata['class lookup'][3:])))

        labels = numpy.array(sample.metadata['class spectra names'])
        for i, name in enumerate(sample.metadata['class names']):
            labels[labels==name] = str(i)
        labels = numpy.atleast_2d(numpy.uint8(labels))
        return ClassificationSample(features=sample.features, labels=labels, classDefinition=classDefinition)

    def _saveAsENVISpectralLibraryUpdateHeader(self, header):
        UnsupervisedSample._saveAsENVISpectralLibraryUpdateHeader(self, header=header)
        header['classes'] = self.classDefinition.classes + 1
        header['class names'] = ['Unclassified'] + self.classDefinition.names
        header['class lookup'] = [0, 0, 0] + self.classDefinition.lookup
        header['class spectra names'] = numpy.array(self.classDefinition.names)[self.labels.ravel()-1]

    def synthMix(self, mixingComplexities, classLikelihoods=None, n=10):
        if classLikelihoods is None:
            classLikelihoods = 'proportional'
        if classLikelihoods is 'proportional':
            classLikelihoods = {i+1 : float(count)/sum(self.histogram) for i, count in enumerate(self.histogram)}
        elif classLikelihoods is 'equalized':
            classLikelihoods = {i+1 : 1./self.classDefinition.classes for i in range(self.classDefinition.classes)}

        mixtures, fractions = dpalg.synthMix(features=self.features, labels=self.labels, classes=self.classDefinition.classes, mixingComplexities=mixingComplexities, classLikelihoods=classLikelihoods, n=n)
        return ProbabilitySample(features=mixtures, labels=fractions, classDefinition=self.classDefinition)

class RegressionSample(SupervisedSample):

    def __repr__(self):
        return '{cls}(features=array{features}, labels=array{labels}, noData={noData}, outputNames={outputNames}'.format(
            cls=self.__class__.__name__,
            features=repr(list(self.features.shape)),
            labels=repr(list(self.labels.shape)),
            noData=repr(self.noData),
            outputNames=repr(self.outputNames)
        )


class ProbabilitySample(RegressionSample):

    def __init__(self, features, labels, classDefinition, metadata=None):
        assert isinstance(classDefinition, ClassDefinition)
        assert labels.shape[0] == classDefinition.classes
        RegressionSample.__init__(self, features, labels, noData=-1, metadata=metadata, outputNames=classDefinition.names)
        self.classDefinition = classDefinition

    def __repr__(self):
        return '{cls}(features=array{features}, labels=array{labels}, classDefinition={classDefinition}'.format(
            cls=self.__class__.__name__,
            features=repr(list(self.features.shape)),
            labels=repr(list(self.labels.shape)),
            classDefinition=repr(self.classDefinition))

    @staticmethod
    def fromENVISpectralLibrary(filename):
        sample = UnsupervisedSample.fromENVISpectralLibrary(filename=filename)
        classDefinition = ClassDefinition(classes=int(sample.metadata['classes'])-1,
                                          names=list(map(str, sample.metadata['class names'][1:])),
                                          lookup=list(map(int, sample.metadata['class lookup'][3:])))

        probabilities = numpy.array([sample.metadata['probabilities '+name] for name in classDefinition.names], dtype=numpy.float32)
        return ProbabilitySample(features=sample.features, labels=probabilities, classDefinition=classDefinition)

    def classifyByProbability(self, minOverallCoverage=0, minWinnerCoverage=0, progressBar=None):
        labels = dpalg.argmaxProbability(probabilities=self.labels, minOverallCoverage=minOverallCoverage, minWinnerCoverage=minWinnerCoverage, progressBar=progressBar)
        valid = labels != 0
        return ClassificationSample(features=self.features[:, valid[0]], labels=labels[:, valid[0]], classDefinition=self.classDefinition)

    def subsetClassesByNames(self, names):
        ids = [self.classDefinition.names.index(name) for name in names]
        return self.subsetClasses(ids=ids)

    def subsetClasses(self, ids):
        lookup = [self.classDefinition.getColor(id) for id in ids]
        names = [self.classDefinition.names[id] for id in ids]
        return ProbabilitySample(features=self.features, labels=self.labels[ids],
                                 classDefinition=ClassDefinition(classes=len(ids), names=names, lookup=lookup))

    def _saveAsENVISpectralLibraryUpdateHeader(self, header):
        UnsupervisedSample._saveAsENVISpectralLibraryUpdateHeader(self, header=header)
        header['classes'] = self.classDefinition.classes + 1
        header['class names'] = ['Unclassified'] + self.classDefinition.names
        header['class lookup'] = [0, 0, 0] + self.classDefinition.lookup
        for i, name in enumerate(self.classDefinition.names):
            header['probabilities ' + name] = self.labels[i]
            header['probabilities Unclassified'] = 1. - numpy.sum(self.labels, axis=0)

class Estimator(FlowObject):

    SAMPLE_TYPE = SupervisedSample
    PREDICT_TYPE = Image

    def __init__(self, sklEstimator):
        self.sklEstimator = sklEstimator
        self.sample = None

    def _fit(self, sample, progressBar=None):
        assert isinstance(sample, self.SAMPLE_TYPE), (sample, self.SAMPLE_TYPE)
        self.sample = sample
        dpalg.estimatorFitData(estimator=self.sklEstimator, features=sample.features, labels=sample.labels, progressBar=progressBar)
        return self

    def _predict(self, predictionFilename, image, mask=None, **kwargs):
        return ipalg.estimatorPredict(estimator=self, predictionFilename=predictionFilename, image=image, mask=mask, **kwargs)

    def _transform(self, filename, image, inverse=False, mask=None, vmask=None, progressBar=None):
        assert 0
        assert isinstance(image, Image)
        if mask is None: mask = Mask(None)
        if vmask is None: vmask = Vector(None)
        assert isinstance(mask, Mask)
        assert isinstance(vmask, Vector)

        ipalg.estimatorTransform(transformation=filename, noData=self.sample.noData, estimator=self.sklEstimator, image=image.filename,
                                 inverse=inverse,
                                 mask=mask.filename, maskFunc=mask.ufunc,
                                 vmask=vmask.filename, vmaskAllTouched=vmask.allTouched, vmaskFilterSQL=vmask.filterSQL,
                                 progressBar=progressBar)

        return Image(filename=filename)

    def _inverseTransform(self, filename, image, inverse=True, mask=None, vmask=None, progressBar=None):
        assert 0
        return self._transform(filename=filename, image=image, inverse=inverse, mask=mask, vmask=vmask, progressBar=progressBar)

class Classifier(Estimator):
    SAMPLE_TYPE = ClassificationSample
    PREDICT_TYPE = Classification
    fit = Estimator._fit
    predict = Estimator._predict

class Regressor(Estimator):
    SAMPLE_TYPE = RegressionSample
    PREDICT_TYPE = Regression
    fit = Estimator._fit
    predict = Estimator._predict

class Transformer(Estimator):
    SAMPLE_TYPE = UnsupervisedSample
    PREDICT_TYPE = Image
    fit = Estimator._fit
    transform = Estimator._transform
    inverseTransform = Estimator._inverseTransform

class Clusterer(Estimator):
    SAMPLE_TYPE = UnsupervisedSample
    PREDICT_TYPE = Classification
    fit = Estimator._fit
    predict = Estimator._predict
    transform = Estimator._transform

class ClassificationPerformance(FlowObject):

    def __init__(self, yP, yT, classDefinitionP, classDefinitionT, classProportions=None):
        assert isinstance(yP, numpy.ndarray) and yP.ndim==1
        assert isinstance(yT, numpy.ndarray) and yT.shape==yP.shape
        assert isinstance(classDefinitionP, ClassDefinition)
        assert isinstance(classDefinitionT, ClassDefinition)
        assert classDefinitionT.classes == classDefinitionP.classes

        self.classDefinitionT = classDefinitionT
        self.classDefinitionP = classDefinitionP

        import sklearn.metrics
        self.mij = numpy.int64(sklearn.metrics.confusion_matrix(yT, yP, labels=range(1, classDefinitionT.classes+1)).T)
        self.m = numpy.int64(yP.size)
        self.Wi = classProportions
        self.adjusted = False
        self._assessPerformance()

    def _assessPerformance(self):

        old_error_state = numpy.geterr()
        numpy.seterr(divide='ignore', invalid='ignore', over='raise', under='raise')

        # get some stats from the confusion matrix mij
        self.mi_ = numpy.sum(self.mij, axis=0, dtype=numpy.float64) # class-wise sum over all prediction
        self.m_j = numpy.sum(self.mij, axis=1, dtype=numpy.float64) # class-wise sum over references
        self.mii = numpy.diag(self.mij) # main diagonal -> class-wise correctly classified samples

        # estimate mapped class proportions from the reference sample, if not provided by the user
        if self.Wi is None:
            self.Wi = self.mi_/self.m  # note that in this case pij is reduced to pij=mij/m

        # pij is the proportion of area estimate
        # pij = Wi*mij/mi_
        self.pij = numpy.zeros_like(self.mij, dtype=numpy.float64)
        for i in range(self.classDefinitionT.classes):
            for j in range(self.classDefinitionT.classes):
                self.pij[i,j] = self.Wi[i]*self.mij[i,j]/self.mi_[i]

        self.pi_ = numpy.sum(self.pij, axis=0, dtype=numpy.float64)
        self.p_j = numpy.sum(self.pij, axis=1, dtype=numpy.float64)
        self.pii = numpy.diag(self.pij)

        # calculate performance measures
        self.ProducerAccuracy = self._fix(self.mii/self.mi_)
        self.UserAccuracy = self._fix(self.mii / self.m_j)

        self.F1Accuracy = self._fix(2 * self.UserAccuracy * self.ProducerAccuracy / (self.UserAccuracy + self.ProducerAccuracy))
        self.ConditionalKappaAccuracy = self._fix((self.m * self.mii - self.mi_ * self.m_j) / (self.m * self.mi_ - self.mi_ * self.m_j))
        self.OverallAccuracy = self._fix(self.mii.sum() / float(self.m))
        self.KappaAccuracy = self._fix((self.m * self.mii.sum() - numpy.sum(self.mi_ * self.m_j)) / (self.m**2 - numpy.sum(self.mi_ * self.m_j)))

        # calculate squared standard errors (SSE)

        self.OverallAccuracySSE = 0.
        for i in range(self.classDefinitionT.classes): self.OverallAccuracySSE += self.pij[i, i] * (self.Wi[i] - self.pij[i, i]) / (self.Wi[i] * self.m)

        a1 = self.mii.sum()/self.m
        a2 = (self.mi_*self.m_j).sum() / self.m**2
        a3 = (self.mii*(self.mi_+self.m_j)).sum() / self.m**2
        a4 = 0.
        for i in range(self.classDefinitionT.classes):
            for j in range(self.classDefinitionT.classes):
                a4 += self.mij[i,j]*(self.mi_[j]+self.m_j[i])**2
        a4 /= self.m**3
        b1 = a1*(1-a1)/(1-a2)**2
        b2 = 2*(1-a1)*(2*a1*a2-a3)/(1-a2)**3
        b3 = (1-a1)**2*(a4-4*a2**2)/(1-a2)**4
        self.KappaAccuracySSE = (b1+b2+b3)/self.m

        self.ProducerAccuracySSE = numpy.zeros(self.classDefinitionT.classes, dtype=numpy.float64)
        for i in range(self.classDefinitionT.classes):
            sum = 0.
            for j in range(self.classDefinitionT.classes):
                if i == j: continue
                sum += self.pij[i,j]*(self.Wi[j]-self.pij[i,j])/(self.Wi[j]*self.m)
                self.ProducerAccuracySSE[i] = self.pij[i,i]*self.p_j[i]**(-4) * (self.pij[i,i]*sum + (self.Wi[i]-self.pij[i,i])*(self.p_j[i]-self.pij[i,i])**2/(self.Wi[i]*self.m))

        self.UserAccuracySSE = numpy.zeros(self.classDefinitionT.classes, dtype=numpy.float64)
        for i in range(self.classDefinitionT.classes):
            self.UserAccuracySSE[i] = self.pij[i ,i]*(self.Wi[i]-self.pij[i,i])/(self.Wi[i]**2*self.m)

        self.F1AccuracySSE = self._fix(2 * self.UserAccuracySSE * self.ProducerAccuracySSE / (self.UserAccuracySSE + self.ProducerAccuracySSE))

        self.ConditionalKappaAccuracySSE = self.m*(self.mi_-self.mii) / (self.mi_*(self.m-self.m_j))**3 * ((self.mi_-self.mii)*(self.mi_*self.m_j-self.m*self.mii)+self.m*self.mii*(self.m-self.mi_-self.m_j+self.mii) )

        self.ClassProportion = self.m_j/self.m
        self.ClassProportionSSE = numpy.zeros(self.classDefinitionT.classes, dtype=numpy.float64)
        for j in range(self.classDefinitionT.classes):
            for i in range(self.classDefinitionT.classes):
                self.ClassProportionSSE[j] += self.Wi[i]**2 * ( (self.mij[i,j]/self.mi_[i])*(1-self.mij[i,j]/self.mi_[i]) )/(self.mi_[i]-1)

        numpy.seterr(**old_error_state)

    def _confidenceIntervall(self, mean, sse, alpha):
        import scipy.stats
        se = numpy.sqrt(numpy.clip(sse, 0, numpy.inf))
        lower = scipy.stats.norm.ppf(alpha / 2.)*se + mean
        upper = scipy.stats.norm.ppf(1 - alpha / 2.)*se + mean
        return lower, upper

    def _fix(self, a, fill=0):
        if isinstance(a, numpy.ndarray):
            a[numpy.logical_not(numpy.isfinite(a))] = 0
        else:
            if not numpy.isfinite(a):
                a = 0
        return a

    def report(self):

        report = Report('Classification Performance')

        #if self.adjusted:
        #    report.append(ReportHeading('Stratification'))

        #    colHeaders = [['DN','Stratum', 'Stratum Size', 'Stratum Sample Size', 'Adjustment Weight']]
        #    colSpans = [[1,1,1,1,1]]
        #    data = numpy.transpose([numpy.array(range(0, self.strataClasses))+1, self.strataClassNames, self.strataSizes, self.strataSampleSizes, numpy.round(self.strataWeights,2) ])
        #    report.append(ReportTable(data, '', colHeaders=colHeaders, colSpans=colSpans))

        report.append(ReportHeading('Class Overview'))
        colHeaders = None
        rowSpans = [[1,2],[1,1,1]]
        colSpans = [[1,1,1,1,1]]
        rowHeaders = [['','Class Names'],['Class ID','Reference', 'Prediction']]
        data = [numpy.hstack((range(1, self.classDefinitionT.classes + 1))), self.classDefinitionT.names, self.classDefinitionP.names]
        report.append(ReportTable(data, '', colHeaders=colHeaders, rowHeaders=rowHeaders, colSpans=colSpans, rowSpans=rowSpans))

        # Confusion Matrix Table
        report.append(ReportHeading('Confusion Matrix'))
        rowSpans = None
        classNumbers = []
        for i in range(self.classDefinitionT.classes): classNumbers.append('('+str(i+1)+')')
        colHeaders = [['Reference Class'],classNumbers + ['Sum']]
        colSpans = [[self.classDefinitionT.classes],numpy.ones(self.classDefinitionT.classes+1,dtype=int)]
        classNamesColumn = []
        for i in range(self.classDefinitionT.classes): classNamesColumn.append('('+str(i+1)+') '+self.classDefinitionT.names[i])
        rowHeaders = [classNamesColumn+['Sum']]
        data = numpy.vstack(((numpy.hstack((self.mij,self.m_j[:, None]))),numpy.hstack((self.mi_,self.m)))).astype(int)

        report.append(ReportTable(data, '', colHeaders, rowHeaders, colSpans, rowSpans))

        # Accuracies Table
        report.append(ReportHeading('Accuracies'))
        colHeaders = [['Measure', 'Estimate [%]', '95 % Confidence Interval [%]']]
        colSpans = [[1,1,2]]
        rowHeaders = None
        data = [['Overall Accuracy',numpy.round(self.OverallAccuracy*100,2),numpy.round(self._confidenceIntervall(self.OverallAccuracy, self.OverallAccuracySSE, 0.05)[0]*100),round(self._confidenceIntervall(self.OverallAccuracy, self.OverallAccuracySSE, 0.05)[1]*100,2)],
                ['Kappa Accuracy',numpy.round(self.KappaAccuracy*100,2),numpy.round(self._confidenceIntervall(self.KappaAccuracy, self.KappaAccuracySSE, 0.05)[0]*100,2),numpy.round(self._confidenceIntervall(self.KappaAccuracy, self.KappaAccuracySSE, 0.05)[1]*100,2)],
                ['Mean F1 Accuracy',numpy.round(numpy.mean(self.F1Accuracy)*100,2),'-','-']]
        report.append(ReportTable(data, '', colHeaders, rowHeaders, colSpans, rowSpans))

        # Class-wise Accuracies Table
        report.append(ReportHeading('Class-wise Accuracies'))
        colSpans = [[1,3,3,3],[1,1,2,1,2,1,2]]
        colHeaders = [['','User\'s Accuracy [%]','Producer\'s Accuracy [%]','F1 Accuracy'],['Map class','Estimate','95 % Interval','Estimate','95% Interval','Estimate','95% Interval']]
        data = [classNamesColumn,numpy.round(self.UserAccuracy*100,2)
               ,numpy.round(self._confidenceIntervall(self.UserAccuracy, self.UserAccuracySSE, 0.05)[0]*100,2)
               ,numpy.round(self._confidenceIntervall(self.UserAccuracy, self.UserAccuracySSE, 0.05)[1]*100,2)
               ,numpy.round(self.ProducerAccuracy*100,2)
               ,numpy.round(self._confidenceIntervall(self.ProducerAccuracy, self.ProducerAccuracySSE, 0.05)[0]*100,2)
               ,numpy.round(self._confidenceIntervall(self.ProducerAccuracy, self.ProducerAccuracySSE, 0.05)[1]*100,2)
               ,numpy.round(self.F1Accuracy*100,2)
               ,numpy.round(self._confidenceIntervall(self.F1Accuracy, self.F1AccuracySSE, 0.05)[0]*100,2)
               ,numpy.round(self._confidenceIntervall(self.F1Accuracy, self.F1AccuracySSE, 0.05)[1]*100,2)]
        data = [list(x) for x in zip(*data)]
        report.append(ReportTable(data, '', colHeaders, rowHeaders, colSpans, rowSpans))

        # Proportion Matrix Table
        report.append(ReportHeading('Proportion Matrix'))
        colHeaders = [['Reference Class'],classNumbers + ['Sum']]
        colSpans = [[self.classDefinitionT.classes],numpy.ones(self.classDefinitionT.classes+1,dtype=int)]
        rowHeaders = [classNamesColumn+['Sum']]
        data = numpy.vstack(((numpy.hstack((self.pij*100,self.p_j[:, None]*100))),numpy.hstack((self.pi_*100,100))))
        report.append(ReportTable(numpy.round(data,2), '', colHeaders, rowHeaders, colSpans, rowSpans))
        return report

class RegressionPerformance(FlowObject):

    def __init__(self, yT, yP, outputNamesT, outputNamesP):
        self.yP = yP
        self.yT = yT
        self.outputNamesT = outputNamesT
        self.outputNamesP = outputNamesP
        self.residuals = self.yP - self.yT
        self.n = self.yT.size

        self.explained_variance_score = [sklearn.metrics.explained_variance_score(self.yT[i], self.yP[i]) for i, _ in enumerate(outputNamesT)]
        self.mean_absolute_error = [sklearn.metrics.mean_absolute_error(self.yT[i], self.yP[i]) for i, _ in enumerate(outputNamesT)]
        self.mean_squared_error = [sklearn.metrics.mean_squared_error(self.yT[i], self.yP[i]) for i, _ in enumerate(outputNamesT)]
        #self.mean_squared_logarithmic_error = [sklearn.metrics.mean_squared_log_error(self.yT[i], self.yP[i]) for i, _ in enumerate(outputNamesT)]
        self.median_absolute_error = [sklearn.metrics.median_absolute_error(self.yT[i], self.yP[i]) for i, _ in enumerate(outputNamesT)]
        self.r2_score = [sklearn.metrics.r2_score(self.yT[i], self.yP[i]) for i, _ in enumerate(outputNamesT)]

    def report(self):

        report = Report('Regression Performance')

        report.append(ReportHeading('Outputs Overview'))
        colHeaders = [['Outputs']]
        colSpans = [[len(self.outputNamesT)]]
        rowHeaders = [['Reference', 'Prediction']]
        data = [self.outputNamesT, self.outputNamesP]

        report.append(ReportTable(data, '', colHeaders=colHeaders, colSpans=colSpans, rowHeaders=rowHeaders))

        report.append(ReportHeading('Metrics'))

        report.append(ReportParagraph('Number of samples: {}'.format(self.n)))

        colHeaders = [['Outputs'], self.outputNamesT]
        colSpans =   [[len(self.outputNamesT)], [1]*len(self.outputNamesT)]
        rowHeaders = [['Explained variance score',
                       'Mean absolute error (MAE)',
                       'Mean squared error (MSE)',
                       'Median absolute error (MedAE)',
                       'Coefficient of determination (R^2)']]

        data =numpy.array([numpy.round(numpy.array(self.explained_variance_score).astype(float), 4),
                           numpy.round(numpy.array(self.mean_absolute_error).astype(float), 4),
                           numpy.round(numpy.array(self.mean_squared_error).astype(float), 4),
                           numpy.round(numpy.array(self.median_absolute_error).astype(float), 4),
                           numpy.round(numpy.array(self.r2_score).astype(float), 4)])

        report.append(ReportTable(data, colHeaders=colHeaders, colSpans=colSpans, rowHeaders=rowHeaders, attribs_align='left'))

        report.append(ReportHyperlink(url=r'http://scikit-learn.org/stable/modules/model_evaluation.html#regression-metrics',
                                      text='See Scikit-Learn documentation for details.'))

        report.append(ReportHeading('Scatter and Residuals Plots'))

        for i, name in enumerate(self.outputNamesT):
            fig, ax = pyplot.subplots(facecolor='white',figsize=(7, 7))
            # prepare 2x2 grid for plotting scatterplot on lower left, and adjacent histograms
            gs = matplotlib.gridspec.GridSpec(2, 2, width_ratios=[3, 1], height_ratios=[1, 3])

            ax0 = pyplot.subplot(gs[0,0])
            ax0.hist(self.yT[i], bins=100, edgecolor='None', )
            pyplot.xlim([numpy.min(self.yT[i]), numpy.max(self.yT[i])])
            pyplot.tick_params(which = 'both', direction = 'out', length=10, pad=10)
            # hide ticks and ticklabels
            ax0.set_xticklabels([])
            ax0.set_ylabel('counts')
            ax0.set_title(name)
            ax0.xaxis.set_ticks_position('bottom')
            ax0.yaxis.set_ticks_position('left')

            # plot only every second tick, starting with the second
            #for label in ax0.get_yticklabels()[1::2]: label.set_visible(False)
            #plot only first and last ticklabel
            #for label in ax0.get_yticklabels()[1:-1]: label.set_visible(False)

            ax1 = pyplot.subplot(gs[1,1])
            ax1.hist(self.yP[i], orientation='horizontal', bins=100, edgecolor='None')
            pyplot.tick_params(which = 'both', direction = 'out', length=10, pad=10)
            pyplot.ylim([numpy.min(self.yT[i]), numpy.max(self.yT[i])])
            # hide ticks and ticklabels
            ax1.set_yticklabels([])
            ax1.set_xlabel('counts')
            ax1.yaxis.set_ticks_position('left')
            ax1.xaxis.set_ticks_position('bottom')
            # plot only every second tick, starting with the second
            #for label in ax1.get_xticklabels()[1::2]: label.set_visible(False)
            #plot only first and last ticklabel
            #for label in ax1.get_xticklabels()[1:-1]: label.set_visible(False)

            ax2 = pyplot.subplot(gs[1,0])
            ax2.scatter(self.yT[i], self.yP[i], s=10, edgecolor='', color='navy')
            pyplot.xlim([numpy.min(self.yT[i]), numpy.max(self.yT[i])])
            pyplot.ylim([numpy.min(self.yT[i]), numpy.max(self.yT[i])])
            pyplot.tick_params(which = 'both', direction = 'out')
            pyplot.xlabel('Observed')
            pyplot.ylabel('Predicted')

            # 1:1 line
            pyplot.plot([numpy.min(self.yT[i]), numpy.max(self.yT[i])], [numpy.min(self.yT[i]), numpy.max(self.yT[i])], 'k-')

            # Colorbar
            #cbaxes = fig.add_axes([0.05, 0.1, 0.05, 0.35])
            #cBar = pyplot.colorbar(sct, ticklocation='left', extend='neither', drawedges=False,cax = cbaxes)
            #cBar.ax.set_ylabel('label')

            fig.tight_layout()
            report.append(ReportPlot(fig))
            pyplot.close()

            fig, ax = pyplot.subplots(facecolor='white',figsize=(7, 5))
            ax.hist(self.residuals[i], bins=100, edgecolor='None')
            ax.set_title(name)
            ax.set_xlabel('Predicted - Observed')
            ax.set_ylabel('Counts')
            fig.tight_layout()
            report.append(ReportPlot(fig))
            pyplot.close()

        return report