import numpy
import gdal
from hubdc.applier import Applier, ApplierOperator, PixelGrid, CUIProgressBar

def getProgressBar(currentProgressBar):
    if currentProgressBar is None:
        return CUIProgressBar()
    else:
        return currentProgressBar

def classificationFromVector(classification, vector, grid,
                             ids, idAttribute, classNames=None, classLookup=None,
                             layer = 0, oversampling=10, minOverallCoverage=0.01, minWinnerCoverage=0.5,
                             format=None, creationOptions=None, dtype=numpy.uint8, progressBar=None):

    assert isinstance(grid, PixelGrid)
    progressBar = getProgressBar(progressBar)

    applier = Applier()
    applier.controls.setProgressBar(progressBar)
    applier.controls.setReferenceGrid(grid)

    applier.setVector('vector', layer=layer, filename=vector)
    applier.setOutput('classification', filename=classification, format=format, creationOptions=creationOptions)

    class ClassificationFromVector(ApplierOperator):
        def ufunc(self):
            noData = 0
            classification = self.getVectorCategoricalArray('vector', ids=ids, noData=noData, minOverallCoverage=minOverallCoverage, minWinnerCoverage=minWinnerCoverage,
                                                            oversampling=oversampling, burnAttribute=idAttribute)
            self.setArray('classification', array=classification, dtype=dtype)
            self.setMetadataClassDefinition('classification', classes=len(ids), classNames=classNames, classLookup=classLookup)

    applier.apply(operator=ClassificationFromVector)

def sampleImageByClassification(image, classification, mask=None, maskFunc=None, vmask=None, vmaskAllTouched=False, vmaskFilterSQL=None, progressBar=None):

    applier = Applier()
    applier.controls.setProgressBar(progressBar)
    applier.controls.setReferenceGridByImage(image)

    applier.setInput('image', filename=image)
    applier.setInput('classification', filename=classification)
    if mask is not None:
        applier.setInput('mask', filename=mask)

    class SampleRasterByClassification(ApplierOperator):
        def ufunc(self):
            features = self.getArray('image')
            fractions = self.getProbabilityArray('classification')
            labeled = numpy.sum(fractions, axis=0, keepdims=True) != 0
            if mask is not None:
                labeled *= self.getMaskArray('mask', noData=0, ufunc=maskFunc)
            if vmask is not None:
                labeled *= self.getVectorArray('vmask', allTouched=vmaskAllTouched, filterSQL=vmaskFilterSQL, dtype=numpy.uint8) == 1

            classes, classNames, classLookup = self.getMetadataClassDefinition('classification')
            return features[:, labeled[0]], fractions[:, labeled[0]], classes, classNames, classLookup

    results = applier.apply(operator=SampleRasterByClassification)

    features = numpy.hstack(result[0] for result in results)
    fractions = numpy.hstack(result[1] for result in results)
    classes, classNames, classLookup = results[0][2:]

    return features, fractions, classes, classNames, classLookup


def estimatorPredict(prediction, noData, estimator, image,
                     mask=None, maskFunc=None,
                     vmask=None, vmaskAllTouched=True, vmaskFilterSQL=None,
                     outputNames=None,
                     classes=None, classNames=None, classLookup=None, progressBar=None):

    applier = Applier()
    applier.controls.setProgressBar(progressBar)
    applier.controls.setReferenceGridByImage(image)

    applier.setInput('image', filename=image)
    if mask is not None: applier.setInput('mask', filename=mask, resampleAlg=gdal.GRA_Mode)
    if vmask is not None: applier.setVector('vmask', filename=vmask)

    applier.setOutput('prediction', filename=prediction)

    class PredictImage(ApplierOperator):
        def ufunc(self):
            features = self.getArray('image')

            if estimator._estimator_type in ['classifier', 'clusterer']:
                noutputs = 1
                dtype = numpy.uint8
            elif estimator._estimator_type == 'regressor':
                X0 = numpy.float64(numpy.atleast_2d(features[:, 0, 0]))
                y0 = estimator.predict(X=X0)
                noutputs = max(y0.shape)
                dtype = numpy.float32
            else:
                raise Exception('unexpected estimator type')

            prediction = self.getFull(value=noData, bands=noutputs, dtype=dtype)

            valid = self.getMaskArray('image', array=features)
            if mask is not None:
                valid *= self.getMaskArray('mask', noData=0, ufunc=maskFunc)
            if vmask is not None:
                valid *= self.getVectorArray('vmask', allTouched=vmaskAllTouched, filterSQL=vmaskFilterSQL, dtype=numpy.uint8)==1

            def predict(features):
                X = numpy.float64(features.T)
                y = estimator.predict(X=X)
                return y.reshape(X.shape[0], -1).T

            self.applySampleFunction(inarray=features, outarray=prediction, mask=valid,
                                     ufunc=predict)

            self.setArray('prediction', array=prediction)

            if estimator._estimator_type == 'classifier':
                self.setMetadataClassDefinition('prediction', classes=classes, classNames=classNames, classLookup=classLookup)
            if estimator._estimator_type in 'clusterer':
                self.setMetadataClassDefinition('prediction', classes=estimator.n_clusters)
            if estimator._estimator_type == 'regressor':
                self.setNoDataValue('prediction', value=noData)
            self.setMetadataBandNames('prediction', bandNames=outputNames)

    applier.apply(operator=PredictImage)

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

def imageBasicStatistics(image, bandIndicies=None,
                         mask=None, maskFunc=None,
                         vmask=None, vmaskAllTouched=True, vmaskFilterSQL=None,
                         imageOptions=None, maskOptions=None,
                         controls=None, progressBar=None):

    applier = Applier(controls=controls)
    applier.controls.setProgressBar(progressBar)
    if controls is None:
        applier.controls.setReferenceGridByImage(image)

    applier.setInput('image', filename=image, options=imageOptions)
    if mask is not None: applier.setInput('mask', filename=mask, resampleAlg=gdal.GRA_Mode, options=maskOptions)
    if vmask is not None: applier.setVector('vmask', filename=vmask)

    results = applier.apply(operator=ImageBasicStatistics, args=(bandIndicies, mask, maskFunc, vmask, vmaskAllTouched, vmaskFilterSQL))
    results = numpy.array(results)
    min = numpy.nanmin(results[:,:,0], axis=0)
    max = numpy.nanmax(results[:,:,1], axis=0)
    n = numpy.sum(results[:,:,2], axis=0)
    return min, max, n

class ImageBasicStatistics(ApplierOperator):

    def ufunc(self, args):

        bandIndicies, mask, maskFunc, vmask, vmaskAllTouched, vmaskFilterSQL = args

        image = self.getArray('image', indicies=bandIndicies, dtype=numpy.float64)
        maskValid = numpy.True_
        if mask is not None:
            maskValid *= self.getMaskArray('mask', noData=0, ufunc=maskFunc)
        if vmask is not None:
            maskValid *= self.getVectorArray('vmask', allTouched=vmaskAllTouched, filterSQL=vmaskFilterSQL,
                                         dtype=numpy.uint8) == 1

        def bandBasicStatistics(band):
            valid = self.getMaskArray('image', array=band) * maskValid
            band[numpy.logical_not(valid[0])] = numpy.nan
            return numpy.nanmin(band), numpy.nanmax(band), numpy.sum(valid)

        return [bandBasicStatistics(band) for band in image]
