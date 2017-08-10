import random, os, pickle
import numpy
import spectral
from hubdc.model import Open, PixelGrid
import hubflow.ip_algorithms as ipalg
import hubflow.dp_algorithms as dpalg

spectral.settings.envi_support_nonlowercase_params = True

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

    def basicStatistics(self, bandIndicies=None, mask=None, vmask=None,
                        imageOptions=None, maskOptions=None,
                        controls=None, progressBar=None):

        return ipalg.imageBasicStatistics(image=self.filename, bandIndicies=bandIndicies,
                                          mask=mask.filename, maskFunc=mask.ufunc,
                                          vmask=vmask.filename, vmaskAllTouched=vmask.allTouched, vmaskFilterSQL=vmask.filterSQL,
                                          imageOptions=imageOptions, maskOptions=maskOptions,
                                          controls=controls, progressBar=progressBar)


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

    def __init__(self, features, metadata):
        assert isinstance(features, numpy.ndarray) and features.ndim == 2
        #if metadata is None:
        #    metadata = dict()

        self.features = features
        self.metadata = metadata
        self.nbands , self.nsamples = self.features.shape

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

    def __init__(self, features, labels, noData, metadata=None, outputNames=None):
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

    def synthMix(self, mixingComplexities=None, classLikelihoods=None, n=10):
        if mixingComplexities is None:
            mixingComplexities = {2:0.5, 3:0.3, 4:0.2}
        if classLikelihoods is None:
            classLikelihoods = 'proportional'

        if classLikelihoods is 'proportional':
            classLikelihoods = [float(count)/sum(self.histogram) for count in self.histogram]
        elif classLikelihoods is 'equalized':
            classLikelihoods = [1./self.classDefinition.classes for i in range(self.classDefinition.classes)]

        mixtures, fractions = dpalg.synthMix(features=self.features, labels=self.labels, classes=self.classDefinition.classes, mixingComplexities=mixingComplexities, classLikelihoods=classLikelihoods, n=n)
        return ProbabilitySample(features=mixtures, labels=fractions, classDefinition=self.classDefinition)

class RegressionSample(SupervisedSample):
    pass

class ProbabilitySample(RegressionSample):

    def __init__(self, features, labels, classDefinition):
        assert isinstance(classDefinition, ClassDefinition)
        assert labels.shape[0] == classDefinition.classes
        SupervisedSample.__init__(self, features, labels, noData=-1, outputNames=classDefinition.names)
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
        assert isinstance(sample, self.SAMPLE_TYPE)
        self.sample = sample
        dpalg.estimatorFitData(estimator=self.sklEstimator, features=sample.features, labels=sample.labels, progressBar=progressBar)
        return self

    def _predict(self, filename, image, mask=None, vmask=None, progressBar=None):
        assert isinstance(image, Image)
        if mask is None: mask = Mask(None)
        if vmask is None: vmask = VectorMask(None)
        assert isinstance(mask, Mask)
        assert isinstance(vmask, VectorMask)

        classDefinition = getattr(self.sample, 'classDefinition', ClassDefinition(classes=0))
        ipalg.estimatorPredict(prediction=filename, noData=self.sample.noData, estimator=self.sklEstimator, image=image.filename,
                               mask=mask.filename, maskFunc=mask.ufunc,
                               vmask=vmask.filename, vmaskAllTouched=vmask.allTouched, vmaskFilterSQL=vmask.filterSQL,
                               outputNames=self.sample.outputNames,
                               classes=classDefinition.classes, classNames=classDefinition.names, classLookup=classDefinition.lookup,
                               progressBar=progressBar)

        return self.PREDICT_TYPE(filename=filename)

    def _transform(self, filename, image, inverse=False, mask=None, vmask=None, progressBar=None):
        assert isinstance(image, Image)
        if mask is None: mask = Mask(None)
        if vmask is None: vmask = VectorMask(None)
        assert isinstance(mask, Mask)
        assert isinstance(vmask, VectorMask)

        ipalg.estimatorTransform(transformation=filename, noData=self.sample.noData, estimator=self.sklEstimator, image=image.filename,
                                 inverse=inverse,
                                 mask=mask.filename, maskFunc=mask.ufunc,
                                 vmask=vmask.filename, vmaskAllTouched=vmask.allTouched, vmaskFilterSQL=vmask.filterSQL,
                                 progressBar=progressBar)

        return Image(filename=filename)

    def _inverseTransform(self, filename, image, inverse=True, mask=None, vmask=None, progressBar=None):
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


class Report(FlowObject):
    pass


"""
    def asSpectralLibrary(self, spectraNames=None, wavelength=None, wavelengthUnits=None, fwhm=None, header=None):

        if header is None:
            header = dict()
        assert isinstance(header, dict)
        header['spectra names'] = spectraNames if spectraNames is not None else ['profile {}'.format(i+1) for i in range(self.nsamples)]
        header['wavelength'] = wavelength if wavelength is not None else range(self.features.shape[0])
        header['wavelength units'] = wavelengthUnits if wavelengthUnits is not None else 'indicies'
        if fwhm is not None:
            header['fwhm'] = fwhm

        library = spectral.envi.SpectralLibrary(data=numpy.float32(self.features.T), header=header, params=None)
        return SpectralLibrary(library=library)
"""