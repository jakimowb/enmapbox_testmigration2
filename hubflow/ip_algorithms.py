from osgeo import gdal, ogr
from os.path import exists
import numpy
import hubflow.types
from hubflow.applier import Applier, ApplierOperator
from hubdc.applier import PixelGrid, CUIProgressBar, ProgressBarDelegate

def getProgressBar(currentProgressBar):
    if currentProgressBar is None:
        return CUIProgressBar()
    else:
        return ProgressBarDelegate(progressBar=currentProgressBar)

def vectorRasterize(vector, imageFilename, grid, **kwargs):

    assert isinstance(vector, hubflow.types.Vector)
    assert isinstance(grid, PixelGrid)

    applier = Applier(defaultGrid=grid, **kwargs)
    applier.setFlowVector('vector', vector=vector)
    applier.setOutput('image', filename=imageFilename)
    applier.apply(operator=VectorRasterize, vector=vector)
    return hubflow.types.Image(filename=imageFilename)

class VectorRasterize(ApplierOperator):

    def ufunc(self, vector):

        array = self.getFlowVectorArray('vector', vector=vector)
        self.setArray('image', array=array)

def maskFromVector(vector, maskFilename, grid, **kwargs):

    assert isinstance(vector, hubflow.types.Vector)
    assert isinstance(grid, PixelGrid)

    assert 0 #todo

    #use soft mask

    applier = Applier(defaultGrid=grid, **kwargs)
    applier.setFlowVector('vector', vector=vector)
    applier.setOutput('mask', filename=maskFilename)
    applier.apply(operator=MaskFromVector, vector=vector)
    return hubflow.types.Mask(filename=maskFilename)

class MaskFromVector(ApplierOperator):

    def ufunc(self, vector):
        array = self.getFlowVectorArray('vector', vector=vector)
        self.setArray('image', array=array)


def vectorUniqueValues(vector, attribute):

    assert isinstance(vector, hubflow.types.Vector)
    ds = ogr.Open(vector.filename, vector.layer)
    layer = ds.GetLayer()
    layer.SetAttributeFilter(vector.filterSQL)
    return list(set(feature.GetField(attribute) for feature in layer))

def vectorClassificationRasterizeAsClassification(vectorClassification, classificationFilename, grid, oversampling=1, **kwargs):

    applier = Applier(defaultGrid=grid, **kwargs)
    applier.setFlowClassification('vectorClassification', classification=vectorClassification)
    applier.setOutput('classification', filename=classificationFilename)
    applier.apply(operator=VectorClassificationRasterizeAsClassification, vectorClassification=vectorClassification, oversampling=oversampling)
    return hubflow.types.Classification(filename=classificationFilename)

class VectorClassificationRasterizeAsClassification(ApplierOperator):

    def ufunc(self, vectorClassification, oversampling):
        array = self.getFlowClassificationArray('vectorClassification', classification=vectorClassification)
        self.setArray('classification', array=array, dtype=numpy.uint8)
        self.setMetadataClassDefinition('classification', classes=vectorClassification.classDefinition.classes,
                                        classNames=vectorClassification.classDefinition.names,
                                        classLookup=vectorClassification.classDefinition.lookup)

def vectorClassificationRasterizeAsProbability(vectorClassification, probabilityFilename, grid, oversampling=1, **kwargs):

    applier = Applier(defaultGrid=grid, **kwargs)
    applier.setFlowClassification('vectorClassification', classification=vectorClassification)
    applier.setOutput('probability', filename=probabilityFilename)
    applier.apply(operator=VectorClassificationRasterizeAsProbability, vectorClassification=vectorClassification, oversampling=oversampling)
    return hubflow.types.Probability(filename=probabilityFilename)

class VectorClassificationRasterizeAsProbability(ApplierOperator):

    def ufunc(self, vectorClassification, oversampling):

        array = self.getFlowProbabilityArray('vectorClassification', probability=vectorClassification, oversampling=oversampling)
        self.setArray('probability', array=array, dtype=numpy.float32)
        self.setMetadataProbabilityDefinition('probability', classes=vectorClassification.classDefinition.classes,
                                              classNames=vectorClassification.classDefinition.names,
                                              classLookup=vectorClassification.classDefinition.lookup)

def probabilityAsClassColorRGBImage(probability, imageFilename, filterById=None, filterByName=None, **kwargs):

    assert isinstance(probability, hubflow.types.Probability)
    filter = []
    if filterById is not None:
        filter.extend(filterById)
    if filterByName is not None:
        filter.extend([probability.classDefinition.names.index[name] for name in filterByName])
    applier = Applier(defaultGrid=probability, **kwargs)
    applier.setFlowImage('probability', image=probability)
    applier.setOutput('image', filename=imageFilename)
    applier.apply(operator=ProbabilityAsClassColorRGBImage, probability=probability, filter=filter)
    return hubflow.types.Image(filename=imageFilename)

class ProbabilityAsClassColorRGBImage(ApplierOperator):

    def ufunc(self, filter, probability):
        assert isinstance(probability, hubflow.types.Probability)
        colors = numpy.array(probability.classDefinition.lookup).reshape((-1, 3))
        array = self.getFlowImageArray('probability', image=probability)
        rgb = self.getFull(value=0, bands=3, dtype=numpy.float32)
        for id, (band, color) in enumerate(zip(array, colors), start=1):
            if len(filter)>0 and id not in filter: continue
            rgb += band*color.reshape((3,1,1))
        numpy.uint8(numpy.clip(rgb, a_min=0, a_max=255, out=rgb))
        mask = numpy.any(rgb!=0, axis=0)
        numpy.clip(rgb, a_min=1, a_max=255, out=rgb)
        rgb *= mask
        self.setArray('image', array=rgb, dtype=numpy.uint8)

def probabilitySubsetClassesByNames(probability, filename, names, **kwargs):

    assert isinstance(probability, hubflow.types.Probability)
    indicies = [probability.classDefinition.names.index(name) for name in names]
    applier = Applier(defaultGrid=probability, **kwargs)
    applier.setFlowImage('probability', image=probability)
    applier.setOutput('probability2', filename=filename)
    applier.apply(operator=ProbabilitySubsetClassesByNames, indicies=indicies, probability=probability)
    return hubflow.types.Probability(filename=filename)


class ProbabilitySubsetClassesByNames(ApplierOperator):
    def ufunc(self, indicies, probability):
        assert isinstance(probability, hubflow.types.Probability)
        probability2 = self.getArray('probability', indicies=indicies)
        self.setArray('probability2', array=probability2)
        self.setFlowMetadataProbabilityDefinition('probability2', probability.classDefinition.subsetClassesByLabel(
            labels=[index + 1 for index in indicies]))

def imageSample(image, labels, mask=None, **kwargs):

    # todo make 3 different functions!
    # todo consider minOverallCoverage=1. for the regression

    assert isinstance(image, hubflow.types.Image), image
    assert isinstance(labels, (hubflow.types.Classification, hubflow.types.Regression, hubflow.types.Mask)), labels

    applier = Applier(defaultGrid=image, **kwargs)
    applier.setInput('image', filename=image.filename)
    applier.setInput('labels', filename=labels.filename, noData=labels.noData, resampleAlg=gdal.GRA_Average)
    applier.setFlowMask('mask', mask=mask)
    results = applier.apply(operator=ImageSampleByClassification, labels=labels, mask=mask)
    features = numpy.hstack(result[0] for result in results)
    fractions = numpy.hstack(result[1] for result in results)
    if isinstance(labels, (hubflow.types.Classification, hubflow.types.Probability)):
        sample = hubflow.types.ProbabilitySample(features=features, labels=fractions, classDefinition=labels.classDefinition)
    elif isinstance(labels, hubflow.types.Regression):
        sample = hubflow.types.RegressionSample(features=features, labels=fractions, noData=labels.noData, outputNames=labels.outputNames)
    elif isinstance(labels, hubflow.types.Mask):
        sample = hubflow.types.UnsupervisedSample(features=features)
    else:
        raise Exception('wrong labels type')
    return sample

class ImageSampleByClassification(ApplierOperator):
    def ufunc(self, labels, mask):
        features = self.getArray('image')
        if isinstance(labels, hubflow.types.Classification):
            labels_ = self.getProbabilityArray('labels')
        elif isinstance(labels, (hubflow.types.Regression, hubflow.types.Probability)):
            labels_ = self.getArray('labels', dtype=numpy.float32)
        elif isinstance(labels, hubflow.types.Mask):
            labels_ = self.getArray('labels', dtype=numpy.float32)
        else:
            raise Exception('wrong labels type')

        labeled = numpy.any(labels_!=labels.noData, axis=0, keepdims=True)
        labeled *= self.getFlowMaskArray('mask', mask=mask)
        return features[:, labeled[0]], labels_[:, labeled[0]]


def estimatorPredict(estimator, predictionFilename, image, mask=None, **kwargs):

    assert isinstance(estimator, hubflow.types.Estimator)

    applier = Applier(defaultGrid=image, **kwargs)
    applier.setFlowImage('image', image=image)
    applier.setFlowMask('mask', mask=mask)
    applier.setOutput('prediction', filename=predictionFilename)
    applier.apply(operator=EstimatorPredict, image=image, estimator=estimator, mask=mask)
    prediction = estimator.PREDICT_TYPE(filename=predictionFilename)
    assert isinstance(prediction, hubflow.types.Image)
    return prediction

class EstimatorPredict(ApplierOperator):

    def ufunc(self, estimator, image, mask):
        self.features = self.getFlowImageArray('image', image=image)
        etype, dtype, noutputs = self.getInfos(estimator)
        noData = estimator.sample.noData
        prediction = self.getFull(value=noData, bands=noutputs, dtype=dtype)

        valid = self.getMaskArray('image', array=self.features)
        valid *= self.getFlowMaskArray('mask', mask=mask)

        def predict(features):
            X = numpy.float64(features.T)
            y = estimator.sklEstimator.predict(X=X)
            return y.reshape(X.shape[0], -1).T

        self.applySampleFunction(inarray=self.features, outarray=prediction, mask=valid, ufunc=predict)
        self.setArray('prediction', array=prediction)

        if etype == 'classifier':
            self.setFlowMetadataClassDefinition('prediction', classDefinition=estimator.sample.classDefinition)
        if etype == 'clusterer':
            self.setFlowMetadataClassDefinition('prediction', classDefinition=hubflow.types.ClassDefinition(classes=estimator.n_clusters))
        if etype == 'regressor':
            if isinstance(estimator.sample, hubflow.types.ProbabilitySample):
                self.setFlowMetadataProbabilityDefinition('prediction', classDefinition=estimator.sample.classDefinition)
            else:
                self.setNoDataValue('prediction', value=noData)
        self.setMetadataBandNames('prediction', bandNames=estimator.sample.outputNames)

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


def estimatorTransform(transformation, noData, estimator, image,
                       inverse=False,
                       mask=None, maskFunc=None,
                       vmask=None, vmaskAllTouched=True, vmaskFilterSQL=None,
                       dtype=numpy.float32, progressBar=None):

    applier = Applier()
    applier.controls.setProgressBar(progressBar)
    applier.controls.setReferenceGridByImage(image)

    applier.setInput('image', filename=image)
    if mask is not None: applier.setInput('mask', filename=mask, resampleAlg=gdal.GRA_Mode)
    if vmask is not None: applier.setVector('vmask', filename=vmask)

    applier.setOutput('transformation', filename=transformation)

    class TransformImage(ApplierOperator):
        def ufunc(self):
            image = self.getArray('image')

            sklTransform = estimator.inverse_transform if inverse else estimator.transform
            X0 = numpy.float64(numpy.atleast_2d(image[:, 0, 0]))
            _, noutputs = sklTransform(X=X0).shape

            transformation = self.getFull(value=noData, bands=noutputs, dtype=dtype)

            valid = self.getMaskArray('image', array=image)
            if mask is not None:
                valid *= self.getMaskArray('mask', noData=0, ufunc=maskFunc)
            if vmask is not None:
                valid *= self.getVectorArray('vmask', allTouched=vmaskAllTouched, filterSQL=vmaskFilterSQL, dtype=numpy.uint8) == 1

            def transform(features):
                X = numpy.float64(features.T)
                y = sklTransform(X=X)
                return y.reshape(-1, noutputs).T

            self.applySampleFunction(inarray=image, outarray=transformation, mask=valid, ufunc=transform)

            self.setArray('transformation', array=transformation)
            self.setNoDataValue('transformation', value=noData)

    applier.apply(operator=TransformImage)

def imageBasicStatistics(image, bandIndicies=None, mask=None, **kwargs):

    applier = Applier(defaultGrid=image, **kwargs)
    applier.setFlowImage('image', image=image)
    applier.setFlowMask('mask', mask=mask)
    results = applier.apply(operator=ImageBasicStatistics, image=image, bandIndicies=bandIndicies, mask=mask)

    results = numpy.array(results, dtype=numpy.float64)
    min = numpy.nanmin(results[:,:,0], axis=0)
    max = numpy.nanmax(results[:, :, 1], axis=0)
    sum = numpy.nansum(results[:, :, 2], axis=0)
    n = numpy.sum(results[:,:,3], axis=0)
    mean = sum/n
    return min, max, mean, n

class ImageBasicStatistics(ApplierOperator):

    def ufunc(self, image, bandIndicies, mask):

        array = self.getFlowImageArray('image', image=image, indicies=bandIndicies, dtype=numpy.float64)
        maskValid = self.getFlowMaskArray('mask', mask=mask)

        def bandBasicStatistics(index, band):
            valid = self.getMaskArray('image', indicies=[index], array=band) * maskValid
            band[numpy.logical_not(valid)] = numpy.nan
            min = numpy.nanmin(band)
            max = numpy.nanmax(band)
            sum = numpy.nansum(band)
            n = numpy.sum(valid)
            return min, max, sum, n

        return [bandBasicStatistics(index=i, band=band[None]) for i, band in enumerate(array)]

def imageScatterMatrix(image1, image2, bandIndex1, bandIndex2, range1, range2, bins,
                       mask=None, stratification=None, **kwargs):

    applier = Applier(defaultGrid=image1, **kwargs)
    applier.setFlowImage('image1', image=image1)
    applier.setFlowImage('image2', image=image2)
    applier.setFlowMask('mask', mask=mask)
    applier.setFlowClassification('stratification', classification=stratification)

    _, xedges, yedges = numpy.histogram2d(x=[0], y=[0], bins=bins, range=[range1, range2])
    bins = [xedges, yedges]
    results = applier.apply(operator=ImageScatterMatrix, image1=image1, image2=image2,
                            bandIndex1=bandIndex1, bandIndex2=bandIndex2, bins=bins, mask=mask, stratification=stratification)
    H = numpy.sum(numpy.stack(results), axis=0, dtype=numpy.uint64)
    return H, xedges, yedges

class ImageScatterMatrix(ApplierOperator):

    def ufunc(self, image1, image2, bandIndex1, bandIndex2, bins, mask, stratification):

        band1 = self.getFlowImageArray('image1', image=image1, indicies=[bandIndex1])
        band2 = self.getFlowImageArray('image2', image=image2, indicies=[bandIndex2])
        strata = self.getFlowClassificationArray('stratification', classification=stratification)

        valid = self.getMaskArray('image1', array=band1)
        valid *= self.getMaskArray('image2', array=band2)
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

def classificationReclassify(filename, classification, classDefinition, mapping, **kwargs):
    assert isinstance(classification, hubflow.types.Classification)
    assert isinstance(classDefinition, hubflow.types.ClassDefinition)
    assert isinstance(mapping, dict)

    applier = Applier(defaultGrid=classification, **kwargs)
    applier.setFlowImage('inclassification', image=classification)
    applier.setOutput('outclassification', filename=filename)
    applier.apply(operator=ClassificationReclassify, classification=classification, classDefinition=classDefinition, mapping=mapping)

class ClassificationReclassify(ApplierOperator):

    def ufunc(self, classification, classDefinition, mapping):

        inclassification = self.getFlowImageArray('inclassification', image=classification)
        outclassification = self.getFull(value=0, bands=1, dtype=numpy.uint8)
        for inclass, outclass in mapping.items():
            if inclass in classification.classDefinition.names: inclass = classification.classDefinition.names.index(inclass) + 1
            if outclass in classDefinition.names: outclass = classDefinition.names.index(outclass) + 1
            outclassification[inclassification==inclass] = outclass
        self.setArray('outclassification', array=outclassification)
        self.setFlowMetadataClassDefinition('outclassification', classDefinition=classDefinition)
