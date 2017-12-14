from operator import xor
import random, os, pickle
from osgeo import gdal, ogr
import numpy
import sklearn.metrics
import sklearn.multioutput

from hubdc.model import openRaster, openVector, Grid
from hubflow.applier import Applier, ApplierOperator
from hubflow.report import *
from hubflow import signals

import spectral
spectral.settings.envi_support_nonlowercase_params = True


class FlowObjectPickleFileError(Exception):
    pass

class FlowObjectTypeError(Exception):
    pass

class FlowObject(object):

    def pickle(self, filename):
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        with open(filename, 'wb') as f:
            pickle.dump(obj=self, file=f, protocol=1)
        signals.sigFileCreated.emit(filename)
        return self

    @classmethod
    def unpickle(cls, filename, raiseError=True):
        try:
            with open(filename, 'rb') as f:
                obj = pickle.load(file=f)
        except:
            if raiseError:
                raise FlowObjectPickleFileError('not a valid pickle file: '+str(filename))
            else:
                return None

        if not isinstance(obj, cls):
            if raiseError:
                raise FlowObjectTypeError('wrong type ({t1}), expected type: {t2}'.format(t1=obj.__class__, t2=cls))
            else:
                return None
        return obj

class Image(FlowObject):

    def __init__(self, filename):
        self.filename = filename

    def __repr__(self):
        return '{cls}(filename={filename})'.format(cls=self.__class__.__name__, filename=str(self.filename))

    @property
    def grid(self):
        return openRaster(self.filename).grid()

    @classmethod
    def fromVector(cls, filename, vector, grid, **kwargs):
        applier = Applier(defaultGrid=grid, **kwargs)
        applier.setFlowVector('vector', vector=vector)
        applier.setOutputRaster('image', filename=filename)
        applier.apply(operator=_ImageFromVector, vector=vector)
        return Image(filename=filename)

    def asMask(self, noData=None):
        return Mask(filename=self.filename, noData=noData)

    def asProbability(self, classDefinition):
        assert 0 # do we need this???
        return Probability(filename=self.filename, classDefinition=classDefinition)

    def basicStatistics(self, bandIndicies=None, mask=None, **kwargs):
        applier = Applier(defaultGrid=self, **kwargs)
        applier.setFlowImage('image', image=self)
        applier.setFlowMask('mask', mask=mask)
        results = applier.apply(operator=_ImageBasicStatistics, image=self, bandIndicies=bandIndicies, mask=mask)

        results = numpy.array(results, dtype=numpy.float64)
        min = numpy.nanmin(results[:, :, 0], axis=0)
        max = numpy.nanmax(results[:, :, 1], axis=0)
        sum = numpy.nansum(results[:, :, 2], axis=0)
        n = numpy.sum(results[:, :, 3], axis=0)
        mean = sum / n
        return min, max, mean, n

    def scatterMatrix(self, image2, bandIndex1, bandIndex2, range1, range2, bins=256, mask=None, stratification=None, **kwargs):

        applier = Applier(defaultGrid=self, **kwargs)
        applier.setFlowImage('image1', image=self)
        applier.setFlowImage('image2', image=image2)
        applier.setFlowMask('mask', mask=mask)
        applier.setFlowClassification('stratification', classification=stratification)

        _, xedges, yedges = numpy.histogram2d(x=[0], y=[0], bins=bins, range=[range1, range2])
        bins = [xedges, yedges]
        results = applier.apply(operator=_ImageScatterMatrix, image1=self, image2=image2,
                                bandIndex1=bandIndex1, bandIndex2=bandIndex2, bins=bins, mask=mask, stratification=stratification)
        H = numpy.sum(numpy.stack(results), axis=0, dtype=numpy.uint64)
        return H, xedges, yedges

class _ImageBasicStatistics(ApplierOperator):
    def ufunc(self, image, bandIndicies, mask):
        array = self.getFlowImageArray('image', image=image, indicies=bandIndicies).astype(dtype=numpy.float64)
        maskValid = self.getFlowMaskArray('mask', mask=mask)

        def bandBasicStatistics(index, band):
            valid = self.getMaskFromBandArray(array=band, noDataSource='image', index=index)
            valid *= maskValid
            band[numpy.logical_not(valid)] = numpy.nan
            min = numpy.nanmin(band)
            max = numpy.nanmax(band)
            sum = numpy.nansum(band)
            n = numpy.sum(valid)
            return min, max, sum, n

        return [bandBasicStatistics(index=i, band=band[None]) for i, band in enumerate(array)]

class _ImageFromVector(ApplierOperator):
    def ufunc(self, vector):
        array = self.getFlowVectorArray('vector', vector=vector)
        self.outputRaster.raster(key='image').setImageArray(array=array)

class _ImageScatterMatrix(ApplierOperator):
    def ufunc(self, image1, image2, bandIndex1, bandIndex2, bins, mask, stratification):

        band1 = self.getFlowImageArray('image1', image=image1, indicies=[bandIndex1])
        band2 = self.getFlowImageArray('image2', image=image2, indicies=[bandIndex2])
        strata = self.getFlowClassificationArray('stratification', classification=stratification)

        valid = self.getMaskFromBandArray(array=band1, noDataSource='image1', index=bandIndex1)
        valid *= self.getMaskFromBandArray(array=band2, noDataSource='image2', index=bandIndex2)
        valid *= self.getFlowMaskArray('mask', mask=mask)

        x = band1[valid]
        y = band2[valid]

        if strata.size == 0:
            H = numpy.histogram2d(x=x, y=y, bins=bins)[0]
        else:
            s = strata[valid]
            HList = list()
            for i in range(1, stratification.classDefinition.classes+1):
                v = s==i
                Hi = numpy.histogram2d(x=x[v], y=y[v], bins=bins)[0]
                HList.append(numpy.array(Hi))
            H = numpy.stack(HList)

        return H

class Mask(Image):

    def __init__(self, filename, noData=None):
        Image.__init__(self, filename)
        if noData==None:
            noData = openRaster(filename=filename).noDataValue(default=0)
        self.noData = noData

    def __repr__(self):
        return '{cls}(filename={filename}, noData={noData})'.format(
            cls=self.__class__.__name__,
            filename=str(self.filename),
            noData=repr(self.noData))

    @staticmethod
    def fromVector(filename, vector, grid, **kwargs):
        return Image.fromVector(filename=filename, vector=vector, grid=grid).asMask()

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

    def __repr__(self):
        return '{cls}(filename={filename}, layer={layer}, initValue={initValue}, burnValue={burnValue}, burnAttribute={burnAttribute}, allTouched={allTouched}, filterSQL={filterSQL}, dtype={dtype})'.format(
            cls=self.__class__.__name__,
            filename=str(self.filename),
            layer=repr(self.layer),
            initValue=repr(self.initValue),
            burnValue=repr(self.burnValue),
            burnAttribute=repr(self.burnAttribute),
            allTouched=repr(self.allTouched),
            filterSQL=repr(self.filterSQL),
            dtype=repr(self.dtype))

    def uniqueValues(self, attribute):
        ds = ogr.Open(self.filename, self.layer)
        layer = ds.GetLayer()
        layer.SetAttributeFilter(self.filterSQL)
        return sorted(set(feature.GetField(attribute) for feature in layer))

class VectorClassification(FlowObject):

    def __init__(self, filename, classDefinition, idAttribute=None, nameAttribute=None, layer=0, minOverallCoverage=1., minWinnerCoverage=0., dtype=numpy.uint8):
        assert isinstance(classDefinition, ClassDefinition)
        self.classDefinition = classDefinition
        self.filename = filename
        self.layer = layer
        assert xor(idAttribute is None, nameAttribute is None)
        if idAttribute is not None:
            self.classAttribute = idAttribute
            self.classAttributeType = 'id'
        if nameAttribute is not None:
            self.classAttribute = nameAttribute
            self.classAttributeType = 'name'
        self.minOverallCoverage = minOverallCoverage
        self.minWinnerCoverage = minWinnerCoverage
        self.dtype = dtype

    def asVector(self):
        return Vector(filename=self.filename, layer=self.layer, initValue=0, burnAttribute=self.classAttribute, dtype=self.dtype)



class ClassDefinition(FlowObject):

    @staticmethod
    def fromENVIMeta(filename):
        ds = openRaster(filename)
        classes = ds.metadataItem(key='classes', domain='ENVI', dtype=int)
        names = ds.metadataItem(key='class names', domain='ENVI')
        lookup = ds.metadataItem(key='class lookup', domain='ENVI', dtype=int)
        return ClassDefinition(classes=classes-1, names=names[1:], lookup=numpy.array(lookup[3:]).reshape((classes-1, 3)))

    def __init__(self, classes=None, names=None, lookup=None):

        assert classes is not None or names is not None
        if classes is None:
            classes = len(names)
        assert classes > 0
        self.classes = classes
        if names is None:
            names = ['class {}'.format(i+1) for i in range(classes)]
        if lookup is None:
            lookup = [(random.randint(1, 255), random.randint(1, 255), random.randint(1, 255)) for i in range(classes)]
        if len(lookup) == classes*3:
            lookup = [[lookup[i*3+k] for k in range(3)] for i in range(classes)]

        assert len(names) == classes
        assert len(lookup) == classes
        for color in lookup:
            assert len(color)==3, color

        self.names = [str(name) for name in names]
        self.lookup = [[int(v) for v in color] for color in lookup]

    def __repr__(self):
        return '{cls}(classes={classes}, names={names}, lookup={lookup})'.format(
            cls=self.__class__.__name__,
            classes=repr(self.classes),
            names=repr(self.names),
            lookup=repr(self.lookup))

    def equal(self, other, compareLookup=True):
        assert isinstance(other, ClassDefinition)
        equal = self.classes == other.classes
        equal &= all([a == b for a, b in zip(self.names, other.names)])
        if compareLookup:
            for color1, color2 in zip(self.lookup, other.lookup):
                for v1, v2 in zip(color1, color2):
                    equal &= v1==v2
        return equal

    def getColor(self, label):
        return self.lookup[label-1]

    def getColorByName(self, name):
        return self.getColor(label=self.names.index((name))+1)

    def getName(self, label):
        return self.names[label - 1]

    def getLabelByName(self, name):
        return self.names.index(name)+1

class Classification(Image):

    def __init__(self, filename, classDefinition=None, minOverallCoverage=0., minWinnerCoverage=0.):
        Image.__init__(self, filename)
        if classDefinition is None:
            classDefinition = ClassDefinition.fromENVIMeta(filename)
        self.classDefinition = classDefinition
        self.noData = 0
        self.dtype = numpy.uint8
        self.minOverallCoverage = minOverallCoverage
        self.minWinnerCoverage = minWinnerCoverage

    def __repr__(self):
        return '{cls}(filename={filename}, classDefinition={classDefinition}, minOverallCoverage={minOverallCoverage}, minWinnerCoverage={minWinnerCoverage})'.format(
            cls=self.__class__.__name__,
            filename=str(self.filename),
            classDefinition=repr(self.classDefinition),
            minOverallCoverage=repr(self.minOverallCoverage),
            minWinnerCoverage=repr(self.minWinnerCoverage))

    @classmethod
    def fromVectorClassification(cls, filename, vectorClassification, grid, oversampling, **kwargs):
        applier = Applier(defaultGrid=grid, **kwargs)
        applier.setFlowClassification('vectorClassification', classification=vectorClassification)
        applier.setOutputRaster('classification', filename=filename)
        applier.apply(operator=_ClassificationFromVectorClassification, vectorClassification=vectorClassification, oversampling=oversampling)
        return Classification(filename=filename)

    def reclassify(self, filename, classDefinition, mapping, **kwargs):
        assert isinstance(classDefinition, ClassDefinition)
        assert isinstance(mapping, dict)
        applier = Applier(defaultGrid=self, **kwargs)
        applier.setFlowImage('inclassification', image=self)
        applier.setOutputRaster('outclassification', filename=filename)
        applier.apply(operator=_ClassificationReclassify, classification=self, classDefinition=classDefinition, mapping=mapping)
        return Classification(filename=filename)

class _ClassificationReclassify(ApplierOperator):

    def ufunc(self, classification, classDefinition, mapping):
        inclassification = self.getFlowClassificationArray('inclassification', classification=classification)
        outclassification = self.getFull(value=0, bands=1, dtype=numpy.uint8)
        for inclass, outclass in mapping.items():
            if inclass in classification.classDefinition.names:
                inclass = classification.classDefinition.names.index(inclass) + 1
            if outclass in classDefinition.names:
                outclass = classDefinition.names.index(outclass) + 1
            outclassification[inclassification == inclass] = outclass
        self.outputRaster.raster(key='outclassification').setImageArray(array=outclassification)
        self.setFlowMetadataClassDefinition(name='outclassification', classDefinition=classDefinition)

class _ClassificationFromVectorClassification(ApplierOperator):
    def ufunc(self, vectorClassification, oversampling):
        array = self.getFlowClassificationArray('vectorClassification', classification=vectorClassification)
        self.outputRaster.raster(key='classification').setImageArray(array=array)
        self.setFlowMetadataClassDefinition(name='classification',
                                            classDefinition=vectorClassification.classDefinition)

class Regression(Image):

    def __init__(self, filename, noData=None, outputNames=None, minOverallCoverage=0.):
        Image.__init__(self, filename)
        if noData is None:
            noData = openRaster(filename).noDataValue()
        if outputNames is None:
            outputNames = [band.description() for band in openRaster(filename).bands()]
        assert noData is not None
        self.noData = noData
        self.outputNames = outputNames
        self.minOverallCoverage = minOverallCoverage

    def __repr__(self):
        return '{cls}(filename={filename}, noData={noData}, outputNames={outputNames}, minOverallCoverage={minOverallCoverage})'.format(
            cls=self.__class__.__name__,
            filename=str(self.filename),
            noData=repr(self.noData),
            outputNames=repr(self.outputNames),
            minOverallCoverage=repr(self.minOverallCoverage))

    def asMask(self):
        return Image.asMask(self, noData=self.noData)

class Probability(Regression):

    def __init__(self, filename, classDefinition=None):
        if classDefinition is None:
            classDefinition = ClassDefinition.fromENVIMeta(filename)
        assert isinstance(classDefinition, ClassDefinition)
        Regression.__init__(self, filename=filename, noData=-1, outputNames=classDefinition.names)
        self.classDefinition = classDefinition

    def __repr__(self):
        return '{cls}(filename={filename}, classDefinition={classDefinition})'.format(
            cls=self.__class__.__name__,
            filename=str(self.filename),
            classDefinition=repr(self.classDefinition))

    @classmethod
    def fromVectorClassification(cls, filename, vectorClassification, grid, oversampling=10, **kwargs):
            applier = Applier(defaultGrid=grid, **kwargs)
            applier.setFlowClassification('vectorClassification', classification=vectorClassification)
            applier.setOutputRaster('probability', filename=filename)
            applier.apply(operator=_ProbabilityFromVectorClassification, vectorClassification=vectorClassification, oversampling=oversampling)
            return Probability(filename=filename)

    def subsetClasses(self, filename, labels, **kwargs):
        indicies = [label-1 for label in labels]
        applier = Applier(defaultGrid=self, **kwargs)
        applier.setFlowImage('probability', image=self)
        applier.setOutputRaster('probabilitySubset', filename=filename)
        applier.apply(operator=_ProbabilitySubsetClasses, indicies=indicies, probability=self)
        return Probability(filename=filename)

    def subsetClassesByName(self, filename, names, **kwargs):
        labels = [self.classDefinition.names.index(name)+1 for name in names]
        return self.subsetClasses(filename=filename, labels=labels, **kwargs)

    def asClassColorRGBImage(self, filename, filterById=None, filterByName=None, **kwargs):
        filter = []
        if filterById is not None:
            filter.extend(filterById)
        if filterByName is not None:
            filter.extend([self.classDefinition.names.index[name] for name in filterByName])
        applier = Applier(defaultGrid=self, **kwargs)
        applier.setFlowImage('probability', image=self)
        applier.setOutputRaster('image', filename=filename)
        applier.apply(operator=_ProbabilityAsClassColorRGBImage, probability=self, filter=filter)
        return Image(filename=filename)

class _ProbabilityAsClassColorRGBImage(ApplierOperator):
    def ufunc(self, filter, probability):
        assert isinstance(probability, Probability)
        colors = numpy.array(probability.classDefinition.lookup).reshape((-1, 3))
        array = self.getFlowImageArray('probability', image=probability)
        rgb = self.getFull(value=0, bands=3, dtype=numpy.float32)
        for id, (band, color) in enumerate(zip(array, colors), start=1):
            if len(filter) > 0 and id not in filter: continue
            rgb += band * color.reshape((3, 1, 1))
        numpy.uint8(numpy.clip(rgb, a_min=0, a_max=255, out=rgb))
        mask = numpy.any(rgb != 0, axis=0)
        numpy.clip(rgb, a_min=1, a_max=255, out=rgb)
        rgb *= mask
        self.outputRaster.raster(key='image').setImageArray(array=numpy.uint8(rgb))

class _ProbabilityFromVectorClassification(ApplierOperator):
    def ufunc(self, vectorClassification, oversampling):
        array = self.getFlowProbabilityArray('vectorClassification', probability=vectorClassification, oversampling=oversampling)
        self.outputRaster.raster(key='probability').setImageArray(array=array)
        self.setFlowMetadataProbabilityDefinition(name='probability', classDefinition=vectorClassification.classDefinition)

class _ProbabilitySubsetClasses(ApplierOperator):
    def ufunc(self, indicies, probability):
        classes = len(indicies)
        lookup = [probability.classDefinition.getColor(label=index+1) for index in indicies]
        names = [probability.classDefinition.getName(label=index+1) for index in indicies]
        classDefinition = ClassDefinition(classes=classes, names=names, lookup=lookup)
        probabilitySubset = self.inputRaster.raster(key='probability').bandArray(indicies=indicies)
        self.outputRaster.raster(key='probabilitySubset').setImageArray(array=probabilitySubset)
        self.setFlowMetadataProbabilityDefinition(name='probabilitySubset', classDefinition=classDefinition)

class UnsupervisedSample(FlowObject):

    def __init__(self, features, metadata=None):
        assert isinstance(features, numpy.ndarray) and features.ndim == 2
        if metadata is None:
            metadata = dict()
        self.features = features
        self.metadata = metadata
        self.nbands , self.nsamples = self.features.shape

    def __repr__(self):
        return '{cls}(features=array{features}, metadata={metadata})'.format(
            cls=self.__class__.__name__,
            features=repr(list(self.features.shape)),
            metadata=repr(self.metadata))

    @staticmethod
    def fromENVISpectralLibrary(filename):
        headers = [filename + '.hdr', filename[:-4] + '.hdr']
        for header in headers:
            if os.path.exists(header):
                library = spectral.envi.open(file=header)
                return UnsupervisedSample(features=library.spectra.T, metadata=library.metadata)
        raise Exception('header file not found')

    @staticmethod
    def fromImageAndMask(image, mask, grid=None, **kwargs):
        applier = Applier(defaultGrid=grid, **kwargs)
        applier.setFlowImage(name='image', image=image)
        applier.setFlowMask('mask', mask=mask)
        results = applier.apply(operator=_UnsupervisedSampleFromImageAndProbability, image=image, mask=mask,
                                description='UnsupervisedSample.fromImageAndMask')
        features = numpy.hstack(results)
        return UnsupervisedSample(features=features)

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

    def classifyByName(self, names, classDefinition):
        assert len(names) == self.nsamples
        assert isinstance(classDefinition, ClassDefinition)
        assert set(names).issubset(set(classDefinition.names))
        labels = [classDefinition.names.index(name)+1 for name in names]
        labels = numpy.atleast_2d(numpy.array(labels, dtype=numpy.uint8))
        return ClassificationSample(features=self.features, labels=labels, metadata=self.metadata, classDefinition=classDefinition)

class _UnsupervisedSampleFromImageAndProbability(ApplierOperator):
    def ufunc(self, image, mask):
        features = self.getFlowImageArray(name='image', image=image)
        labeled = self.getFlowMaskArray('mask', mask=mask)
        return features[:, labeled[0]]

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
        return '{cls}(features=array{features}, labels=array{labels}, classDefinition={classDefinition})'.format(
            cls=self.__class__.__name__,
            features=repr(list(self.features.shape)),
            labels=repr(list(self.labels.shape)),
            classDefinition=repr(self.classDefinition))

    @staticmethod
    def fromENVISpectralLibrary(filename, classificationSchemeName=''):
        sample = UnsupervisedSample.fromENVISpectralLibrary(filename=filename)
        names = sample.metadata[classificationSchemeName + 'class names'][1:]
        classes = len(names)
        lookup = numpy.array(sample.metadata[classificationSchemeName + 'class lookup'][3:]).reshape((classes, 3))
        classDefinition = ClassDefinition(classes=classes, names=names, lookup=lookup)

        labels = numpy.array(sample.metadata[classificationSchemeName + 'class spectra names'])
        for i, name in enumerate(names):
            labels[labels==name] = str(i+1)
        labels = numpy.atleast_2d(numpy.uint8(labels))
        return ClassificationSample(features=sample.features, labels=labels, classDefinition=classDefinition)

    def _saveAsENVISpectralLibraryUpdateHeader(self, header):
        UnsupervisedSample._saveAsENVISpectralLibraryUpdateHeader(self, header=header)
        header['classes'] = self.classDefinition.classes + 1
        header['class names'] = ['Unclassified'] + self.classDefinition.names
        header['class lookup'] = [0, 0, 0] + self.classDefinition.lookup
        header['class spectra names'] = numpy.array(self.classDefinition.names)[self.labels.ravel()-1]

    @classmethod
    def fromImageAndProbability(cls, image, probability, grid, mask=None, **kwargs):
        probabilitySample = ProbabilitySample.fromImageAndProbability(image=image, probability=probability, grid=grid, mask=mask, **kwargs)
        classificationSample = ClassificationSample.fromProbabilitySample(sample=probabilitySample)
        return classificationSample

    @classmethod
    def fromImageAndClassification(cls, image, classification, grid, mask=None, **kwargs):
        return cls.fromImageAndProbability(image=image, probability=classification, grid=grid, mask=mask, **kwargs)

    @classmethod
    def fromProbabilitySample(cls, sample):
        assert isinstance(sample, ProbabilitySample)
        labels = numpy.argmax(sample.labels, axis=0)[None] + 1
        return ClassificationSample(features=sample.features, labels=labels, classDefinition=sample.classDefinition)

    def asProbabilitySample(self):
        probabilityArray = numpy.zeros(shape=(self.classDefinition.classes, self.nsamples), dtype=numpy.float32)
        for index in range(self.classDefinition.classes):
            probabilityArray[index][self.labels[0] == index+1] = 1.
        return ProbabilitySample(features=self.features, labels=probabilityArray, classDefinition=self.classDefinition, metadata=self.metadata)

    def synthMix(self, mixingComplexities, classLikelihoods=None, n=10):

        if classLikelihoods is None:
            classLikelihoods = 'proportional'
        if classLikelihoods is 'proportional':
            classLikelihoods = {i+1 : float(count)/sum(self.histogram) for i, count in enumerate(self.histogram)}
        elif classLikelihoods is 'equalized':
            classLikelihoods = {i+1 : 1./self.classDefinition.classes for i in range(self.classDefinition.classes)}

        assert isinstance(mixingComplexities, dict)
        assert isinstance(classLikelihoods, dict)

        features=self.features
        labels=self.labels
        classes=self.classDefinition.classes

        # cache label indices and setup 0%/100% fractions from class labels
        indices = dict()
        zeroOneFractions = numpy.zeros((classes, features.shape[1]), dtype=numpy.float32)
        for label in range(1, classes + 1):
            indices[label] = numpy.where(labels == label)[1]
            zeroOneFractions[label - 1, indices[label]] = 1.

        # create mixtures
        mixtures = list()
        fractions = list()
        for i in range(n):
            complexity = numpy.random.choice(mixingComplexities.keys(), p=mixingComplexities.values())
            drawnLabels = numpy.random.choice(classLikelihoods.keys(), size=complexity, replace=True, p=classLikelihoods.values())
            drawnIndices = [numpy.random.choice(indices[label]) for label in drawnLabels]
            drawnFeatures = features[:, drawnIndices]
            drawnFractions = zeroOneFractions[:, drawnIndices]
            randomWeights = numpy.atleast_2d(numpy.float32(numpy.random.randint(low=1, high=100, size=complexity)))
            randomWeights /= randomWeights.sum()
            mixtures.append(numpy.sum(drawnFeatures * randomWeights, axis=1))
            fractions.append(numpy.sum(drawnFractions * randomWeights, axis=1))

        mixtures, fractions = numpy.array(mixtures).T, numpy.array(fractions).T
        return ProbabilitySample(features=mixtures, labels=fractions, classDefinition=self.classDefinition)

class RegressionSample(SupervisedSample):

    def __repr__(self):
        return '{cls}(features=array{features}, labels=array{labels}, noData={noData}, outputNames={outputNames})'.format(
            cls=self.__class__.__name__,
            features=repr(list(self.features.shape)),
            labels=repr(list(self.labels.shape)),
            noData=repr(self.noData),
            outputNames=repr(self.outputNames))

    @staticmethod
    def fromImageAndRegression(image, regression, grid, mask=None, **kwargs):
        applier = Applier(defaultGrid=grid, **kwargs)
        applier.setFlowImage(name='image', image=image)
        applier.setFlowRegression(name='regression', regression=regression)
        applier.setFlowMask('mask', mask=mask)
        results = applier.apply(operator=_RegressionSampleFromImageAndProbability, image=image, regression=regression, mask=mask)
        features = numpy.hstack(result[0] for result in results)
        fractions = numpy.hstack(result[1] for result in results)
        return RegressionSample(features=features, labels=fractions, noData=regression.noData, outputNames=regression.outputNames)

class _RegressionSampleFromImageAndProbability(ApplierOperator):
    def ufunc(self, image, regression, mask):
        features = self.getFlowImageArray(name='image', image=image)
        fractions = self.getFlowRegressionArray(name='regression', regression=regression)
        labeled = fractions != regression.noData
        labeled *= self.getFlowMaskArray('mask', mask=mask)
        return features[:, labeled[0]], fractions[:, labeled[0]]

class ProbabilitySample(RegressionSample):

    def __init__(self, features, labels, classDefinition, metadata=None):
        assert isinstance(classDefinition, ClassDefinition)
        assert labels.shape[0] == classDefinition.classes
        RegressionSample.__init__(self, features, labels, noData=-1, metadata=metadata, outputNames=classDefinition.names)
        self.classDefinition = classDefinition

    def __repr__(self):
        return '{cls}(features=array{features}, labels=array{labels}, classDefinition={classDefinition})'.format(
            cls=self.__class__.__name__,
            features=repr(list(self.features.shape)),
            labels=repr(list(self.labels.shape)),
            classDefinition=repr(self.classDefinition))

    @classmethod
    def fromImageAndClassification(cls, image, classification, mask=None, **kwargs):
        return cls.fromImageAndProbability(image=image, probability=classification, mask=mask, **kwargs)

    @staticmethod
    def fromImageAndProbability(image, probability, grid, mask=None, **kwargs):
        applier = Applier(defaultGrid=grid, **kwargs)
        applier.setFlowImage(name='image', image=image)
        applier.setFlowProbability(name='probability', probability=probability)
        applier.setFlowMask('mask', mask=mask)
        results = applier.apply(operator=_ProbabilitySampleFromImageAndProbability, image=image, probability=probability, mask=mask)
        features = numpy.hstack(result[0] for result in results)
        fractions = numpy.hstack(result[1] for result in results)
        return ProbabilitySample(features=features, labels=fractions, classDefinition=probability.classDefinition)

    def subsetClassesByName(self, names):
        labels = [self.classDefinition.getLabelByName(name) for name in names]
        return self.subsetClasses(labels=labels)

    def subsetClasses(self, labels):
        indicies = [label-1 for label in labels]
        classDefinition = ClassDefinition(classes=len(indicies),
                                          names=[self.classDefinition.getName(index+1) for index in indicies],
                                          lookup=[self.classDefinition.getColor(index+1) for index in indicies])
        return ProbabilitySample(features=self.features, labels=self.labels[indicies], classDefinition=classDefinition)

class _ProbabilitySampleFromImageAndProbability(ApplierOperator):
    def ufunc(self, image, probability, mask):
        features = self.getFlowImageArray(name='image', image=image)
        fractions = self.getFlowProbabilityArray(name='probability', probability=probability)
        labeled = numpy.any(fractions != -1, axis=0, keepdims=True)
        labeled *= self.getFlowMaskArray('mask', mask=mask)
        return features[:, labeled[0]], fractions[:, labeled[0]]

class Estimator(FlowObject):

    SAMPLE_TYPE = SupervisedSample
    PREDICT_TYPE = Image

    def __init__(self, sklEstimator):
        self.sklEstimator = sklEstimator
        self.sample = None

    def __repr__(self):
        return '{cls}(sklEstimator={sklEstimator})'.format(cls=self.__class__.__name__, sklEstimator=repr(self.sklEstimator))

    def _fit(self, sample):
        assert isinstance(sample, self.SAMPLE_TYPE)
        self.sample = sample

        X = numpy.float64(sample.features.T)

        if hasattr(sample, 'labels'):
            if sample.labels.shape[0] == 1 and not isinstance(self.sklEstimator, sklearn.multioutput.MultiOutputEstimator):
                y = sample.labels.ravel()
            else:
                y = sample.labels.T
        else:
            y = None

        self.sklEstimator.fit(X=X, y=y)
        return self

    def _predict(self, filename, image, mask=None, **kwargs):
        applier = Applier(defaultGrid=image, **kwargs)
        applier.setFlowImage('image', image=image)
        applier.setFlowMask('mask', mask=mask)
        applier.setOutputRaster('prediction', filename=filename)
        applier.apply(operator=_EstimatorPredict, image=image, estimator=self, mask=mask)
        prediction = self.PREDICT_TYPE(filename=filename)
        assert isinstance(prediction, Image)
        return prediction

    def _transform(self, filename, image, inverse=False, mask=None, **kwargs):
        applier = Applier(defaultGrid=image, **kwargs)
        applier.setFlowImage('image', image=image)
        applier.setFlowMask('mask', mask=mask)
        applier.setOutputRaster('transformation', filename=filename)
        applier.apply(operator=_EstimatorTransform, estimator=self, image=image, mask=mask, inverse=inverse)
        return Image(filename=filename)

    def _inverseTransform(self, filename, image, mask=None, **kwargs):
        return self._transform(filename=filename, image=image, inverse=True, mask=mask, **kwargs)

class _EstimatorPredict(ApplierOperator):
    def ufunc(self, estimator, image, mask):
        self.features = self.getFlowImageArray('image', image=image)
        etype, dtype, noutputs = self.getInfos(estimator)
        noData = estimator.sample.noData
        prediction = self.getFull(value=noData, bands=noutputs, dtype=dtype)

        valid = self.getMaskFromImageArray(array=self.features, noDataSource='image')
        valid *= self.getFlowMaskArray('mask', mask=mask)

        X = numpy.float64(self.features[:, valid[0]].T)
        y = estimator.sklEstimator.predict(X=X)
        prediction[:, valid[0]] = y.reshape(X.shape[0], -1).T

        self.outputRaster.raster(key='prediction').setImageArray(array=prediction)

        if etype == 'classifier':
            self.setFlowMetadataClassDefinition('prediction', classDefinition=estimator.sample.classDefinition)
        if etype == 'clusterer':
            self.setFlowMetadataClassDefinition('prediction', classDefinition=ClassDefinition(classes=estimator.sklEstimator.n_clusters))
        if etype == 'regressor':
            if isinstance(estimator.sample, ProbabilitySample):
                self.setFlowMetadataProbabilityDefinition('prediction', classDefinition=estimator.sample.classDefinition)
            else:
                self.outputRaster.raster(key='prediction').setNoDataValue(value=noData)
        self.setFlowMetadataBandNames('prediction', bandNames=estimator.sample.outputNames)

    def getInfos(self, estimator):
        etype = estimator.sklEstimator._estimator_type
        if etype in ['classifier', 'clusterer']:
            noutputs = 1
            dtype = numpy.uint8
        elif etype == 'regressor':
            X0 = numpy.float64(numpy.atleast_2d(self.features[:, 0, 0]))
            y0 = estimator.sklEstimator.predict(X=X0)
            noutputs = max(y0.shape)
            dtype = numpy.float32
        else:
            raise Exception('unexpected estimator type')
        return etype, dtype, noutputs

class _EstimatorTransform(ApplierOperator):
    def ufunc(self, estimator, image, mask, inverse):
        if inverse:
            sklTransform = estimator.sklEstimator.inverse_transform
        else:
            sklTransform = estimator.sklEstimator.transform

        noData = numpy.finfo(numpy.float32).min
        features = self.getFlowImageArray('image', image=image)

        X0 = numpy.float64(numpy.atleast_2d(features[:, 0, 0]))
        _, noutputs = sklTransform(X=X0).shape

        transformation = self.getFull(value=noData, bands=noutputs, dtype=numpy.float32)

        valid = self.getMaskFromImageArray(array=features, noDataSource='image')
        valid *= self.getFlowMaskArray('mask', mask=mask)

        X = numpy.float64(features[:, valid[0]].T)
        y = sklTransform(X=X)
        transformation[:, valid[0]] = numpy.float32(y.reshape(-1, noutputs).T)

        self.outputRaster.raster(key='transformation').setImageArray(array=transformation)
        self.outputRaster.raster(key='transformation').setNoDataValue(value=noData)

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
        self.yP = yP
        self.yT = yT
        self.mij = numpy.int64(sklearn.metrics.confusion_matrix(yT, yP, labels=range(1, classDefinitionT.classes+1)).T)
        self.m = numpy.int64(yP.size)
        self.Wi = classProportions
        self.adjusted = False
        self._assessPerformance()

    def __repr__(self):
        return '{cls}(yP=array{yP}, yT=array{yT}, classDefinitionP={classDefinitionP}, classDefinitionT={classDefinitionT}, classProportions={classProportions})'.format(
            cls=self.__class__.__name__,
            yP=repr(list(self.yP.shape)),
            yT=repr(list(self.yT.shape)),
            classDefinitionP=repr(self.classDefinitionP),
            classDefinitionT=repr(self.classDefinitionT),
            classProportions=repr(list(self.Wi)))

    @classmethod
    def fromClassification(self, prediction, reference, **kwargs):
        assert isinstance(prediction, Classification)
        assert isinstance(reference, Classification)
        yP = UnsupervisedSample.fromImageAndMask(image=prediction, mask=reference.asMask(), grid=reference, **kwargs).features[0]
        yT = UnsupervisedSample.fromImageAndMask(image=reference, mask=reference.asMask(), grid=reference, **kwargs).features[0]
        return ClassificationPerformance(yP=yP, yT=yT, classDefinitionP=prediction.classDefinition, classDefinitionT=reference.classDefinition)

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
        self.n = self.yT[0].size

        self.explained_variance_score = [sklearn.metrics.explained_variance_score(self.yT[i], self.yP[i]) for i, _ in enumerate(outputNamesT)]
        self.mean_absolute_error = [sklearn.metrics.mean_absolute_error(self.yT[i], self.yP[i]) for i, _ in enumerate(outputNamesT)]
        self.mean_squared_error = [sklearn.metrics.mean_squared_error(self.yT[i], self.yP[i]) for i, _ in enumerate(outputNamesT)]
        self.median_absolute_error = [sklearn.metrics.median_absolute_error(self.yT[i], self.yP[i]) for i, _ in enumerate(outputNamesT)]
        self.r2_score = [sklearn.metrics.r2_score(self.yT[i], self.yP[i]) for i, _ in enumerate(outputNamesT)]

    def __repr__(self):
        return '{cls}(yP=array{yP}, yT=array{yT}, outputNamesT={outputNamesT}, outputNamesP={outputNamesP})'.format(
            cls=self.__class__.__name__,
            yP=repr(list(self.yP.shape)),
            yT=repr(list(self.yT.shape)),
            outputNamesT=repr(self.outputNamesT),
            outputNamesP=repr(self.outputNamesP))

    @classmethod
    def fromRegression(self, prediction, reference, **kwargs):
        assert isinstance(prediction, Regression)
        assert isinstance(reference, Regression)
        yP = UnsupervisedSample.fromImageAndMask(image=prediction, mask=reference.asMask(), grid=reference, **kwargs).features
        yT = UnsupervisedSample.fromImageAndMask(image=reference, mask=reference.asMask(), grid=reference, **kwargs).features
        return RegressionPerformance(yP=yP, yT=yT, outputNamesP=prediction.outputNames, outputNamesT=reference.outputNames)

    def report(self):
        import matplotlib
        # matplotlib.use('QT4Agg')
        from matplotlib import pyplot

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
                       'Root MSE (RMSE)',
                       'Median absolute error (MedAE)',
                       'Coefficient of determination (R^2)']]

        data =numpy.array([numpy.round(numpy.array(self.explained_variance_score).astype(float), 4),
                           numpy.round(numpy.array(self.mean_absolute_error).astype(float), 4),
                           numpy.round(numpy.array(self.mean_squared_error).astype(float), 4),
                           numpy.round(numpy.sqrt(numpy.array(self.mean_squared_error)).astype(float), 4),
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
