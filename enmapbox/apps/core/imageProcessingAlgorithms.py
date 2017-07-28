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


def estimatorPredictImage(prediction, noData, estimator, image,
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

            if estimator._estimator_type == 'classifier':
                noutputs = 1
                dtype = numpy.uint8
            if estimator._estimator_type == 'regressor':
                noutputs = estimator.n_outputs_
                dtype = numpy.float32

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
            if estimator._estimator_type == 'regressor':
                self.setNoDataValue('prediction', value=noData)
            self.setMetadataBandNames('prediction', bandNames=outputNames)

    applier.apply(operator=PredictImage)