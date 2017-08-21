from osgeo import gdal, ogr
from os.path import exists
import numpy
import hubflow.types
from hubflow.applier import Applier, ApplierOperator
from hubdc.applier import PixelGrid, CUIProgressBar, ApplierInputOptions

def getProgressBar(currentProgressBar):
    if currentProgressBar is None:
        return CUIProgressBar()
    else:
        return currentProgressBar

def vectorRasterize(vector, imageFilename, grid, **kwargs):

    assert isinstance(vector, hubflow.types.Vector)
    assert isinstance(grid, PixelGrid)

    applier = Applier(controls=kwargs.get('controls', None))
    applier.controls.setReferenceGrid(grid)
    applier.controls.setProgressBar(kwargs.get('progressBar', None))
    applier.setFlowVector('vector', vector=vector)
    applier.setOutput('image', filename=imageFilename, options=kwargs.get('imageOptions', None))
    applier.apply(operator=VectorRasterize, overwrite=kwargs.get('overwrite', True), vector=vector)
    return hubflow.types.Image(filename=imageFilename)

class VectorRasterize(ApplierOperator):

    def ufunc(self, vector):

        array = self.getFlowVectorArray('vector', vector=vector)
        self.setArray('image', array=array)

def vectorUniqueValues(vector, attribute, **kwargs):

    assert isinstance(vector, hubflow.types.Vector)
    ds = ogr.Open(vector.filename, vector.layer)
    layer = ds.GetLayer()
    layer.SetAttributeFilter(vector.filterSQL)
    return list(set(feature.GetField(attribute) for feature in layer))

def vectorClassificationRasterizeAsClassification(vectorClassification, classificationFilename, grid, oversampling=1, **kwargs):

    assert isinstance(vectorClassification, hubflow.types.VectorClassification)
    assert isinstance(grid, PixelGrid)

    applier = Applier(controls=kwargs.get('controls', None))
    applier.controls.setReferenceGrid(grid)
    applier.controls.setProgressBar(kwargs.get('progressBar', None))

    applier.setVector('vectorClassification', filename=vectorClassification.filename, layer=vectorClassification.layer)
    applier.setOutput('classification', filename=classificationFilename, options=kwargs.get('classificationOptions', None))
    applier.apply(operator=VectorClassificationRasterizeAsClassification, overwrite=kwargs.get('overwrite', True),
                  vectorClassification=vectorClassification, oversampling=oversampling)

    return hubflow.types.Classification(filename=classificationFilename)

class VectorClassificationRasterizeAsClassification(ApplierOperator):

    def ufunc(self, vectorClassification, oversampling):

        noData = 0
        ids = range(1, vectorClassification.classDefinition.classes + 1)
        classification = self.getVectorCategoricalArray('vectorClassification', ids=ids, noData=noData,
                                                        minOverallCoverage=vectorClassification.minOverallCoverage,
                                                        minWinnerCoverage=vectorClassification.minWinnerCoverage,
                                                        oversampling=oversampling, burnAttribute=vectorClassification.idAttribute,
                                                        allTouched=vectorClassification.allTouched, filterSQL=vectorClassification.filterSQL)
        self.setArray('classification', array=classification, dtype=numpy.uint8)
        self.setMetadataClassDefinition('classification', classes=vectorClassification.classDefinition.classes,
                                        classNames=vectorClassification.classDefinition.names,
                                        classLookup=vectorClassification.classDefinition.lookup)

def vectorClassificationRasterizeAsProbability(vectorClassification, probabilityFilename, grid, oversampling=1, **kwargs):

    assert isinstance(vectorClassification, hubflow.types.VectorClassification)
    assert isinstance(grid, PixelGrid)

    applier = Applier(controls=kwargs.get('controls', None))
    applier.controls.setReferenceGrid(grid)
    applier.controls.setProgressBar(kwargs.get('progressBar', None))

    applier.setVector('vectorClassification', filename=vectorClassification.filename, layer=vectorClassification.layer)
    applier.setOutput('probability', filename=probabilityFilename, options=kwargs.get('probabilityOptions', None))
    applier.apply(operator=VectorClassificationRasterizeAsProbability, overwrite=kwargs.get('overwrite', True),
                  vectorClassification=vectorClassification, oversampling=oversampling)

    return hubflow.types.Probability(filename=probabilityFilename)

class VectorClassificationRasterizeAsProbability(ApplierOperator):

    def ufunc(self, vectorClassification, oversampling):

        ids = range(1, vectorClassification.classDefinition.classes + 1)
        probability = self.getVectorCategoricalFractionArray('vectorClassification', ids=ids,
                                                             minOverallCoverage=vectorClassification.minOverallCoverage,
                                                             oversampling=oversampling,
                                                             burnAttribute=vectorClassification.idAttribute,
                                                             allTouched=vectorClassification.allTouched, filterSQL=vectorClassification.filterSQL)
        self.setArray('probability', array=probability, dtype=numpy.float32)
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
    applier = Applier(controls=kwargs.get('controls', None))
    applier.controls.setProgressBar(kwargs.get('progressBar', None))
    applier.setInput('probability', filename=probability.filename, options=kwargs.get('probabilityOptions', None))
    applier.setOutput('image', filename=imageFilename, options=kwargs.get('imageOptions', None))
    applier.apply(operator=ProbabilityAsClassColorRGBImage, overwrite=kwargs.get('overwrite', True), probability=probability, filter=filter)
    return hubflow.types.Image(filename=imageFilename)

class ProbabilityAsClassColorRGBImage(ApplierOperator):

    def ufunc(self, filter, probability):
        assert isinstance(probability, hubflow.types.Probability)
        colors = numpy.array(probability.classDefinition.lookup).reshape((-1, 3))
        array = self.getArray('probability')
        rgb = self.getFull(value=0, bands=3, dtype=numpy.float32)
        for id, (band, color) in enumerate(zip(array, colors), start=1):
            if len(filter)>0 and id not in filter: continue
            rgb += band*color.reshape((3,1,1))
        numpy.uint8(numpy.clip(rgb, a_min=0, a_max=255, out=rgb))
        mask = numpy.any(rgb!=0, axis=0)
        numpy.clip(rgb, a_min=1, a_max=255, out=rgb)
        rgb *= mask
        self.setArray('image', array=rgb, dtype=numpy.uint8)

def imageSample(image, labels, mask=None, **kwargs):

    assert isinstance(image, hubflow.types.Image), image
    assert isinstance(labels, (hubflow.types.Classification, hubflow.types.Regression, hubflow.types.Mask)), labels

    applier = Applier(controls=kwargs.get('controls', None))
    applier.controls.setProgressBar(kwargs.get('progressBar', None))
    applier.controls.setReferenceGrid(kwargs.get('grid', image.pixelGrid))
    applier.setInput('image', filename=image.filename, options=kwargs.get('imageOptions'))
    applier.setInput('labels', filename=labels.filename, noData=labels.noData, resampleAlg=gdal.GRA_Average)
    applier.setFlowMask('mask', mask=mask)
    results = applier.apply(operator=ImageSampleByClassification, overwrite=kwargs.get('overwrite', True), labels=labels, mask=mask)
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
    assert isinstance(image, hubflow.types.Image)

    applier = Applier(controls=kwargs.get('controls', None))
    applier.controls.setProgressBar(kwargs.get('progressBar', None))
    applier.controls.setReferenceGridByImage(image.filename)

    applier.setInput('image', filename=image.filename)
    applier.setFlowMask('mask', mask=mask)

    applier.setOutput('prediction', filename=predictionFilename)
    applier.apply(operator=EstimatorPredict, overwrite=kwargs.get('overwrite', True),
                  estimator=estimator, mask=mask)
    prediction = estimator.PREDICT_TYPE(filename=predictionFilename)
    assert isinstance(prediction, hubflow.types.Image)
    return prediction

class EstimatorPredict(ApplierOperator):

    def ufunc(self, estimator, mask):
        self.features = self.getArray('image')
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

        def bandBasicStatistics(index, band):
            valid = self.getMaskArray('image', indicies=[index], array=band) * maskValid
            band[numpy.logical_not(valid)] = numpy.nan
            return numpy.nanmin(band), numpy.nanmax(band), numpy.sum(valid)

        return [bandBasicStatistics(index=i, band=band[None]) for i, band in enumerate(image)]

def imageScatterMatrix(image1, image2, bandIndex1, bandIndex2, range1, range2, bins,
                       mask=None, maskFunc=None,
                       vmask=None, vmaskAllTouched=True, vmaskFilterSQL=None,
                       stratification=None, strataDefinition=None,
                       imageOptions=None, image2Options=None, maskOptions=None, stratificationOptions=None,
                       controls=None, progressBar=None):

    applier = Applier(controls=controls)
    applier.controls.setProgressBar(progressBar)
    if controls is None:
        applier.controls.setReferenceGridByImage(image1)

    applier.setInput('image1', filename=image1, options=imageOptions)
    applier.setInput('image2', filename=image2, options=image2Options)
    if mask is not None: applier.setInput('mask', filename=mask, resampleAlg=gdal.GRA_Mode, options=maskOptions)
    if vmask is not None: applier.setVector('vmask', filename=vmask)
    if stratification is not None: applier.setInput('stratification', filename=stratification, options=stratificationOptions)

    _, xedges, yedges = numpy.histogram2d(x=[0], y=[0], bins=bins, range=[range1, range2])
    bins = [xedges, yedges]
    args = (bandIndex1, bandIndex2, bins, mask, maskFunc, vmask, vmaskAllTouched, vmaskFilterSQL, stratification, strataDefinition)
    results = applier.apply(operator=ImageScatterMatrix, args=args)
    H = numpy.sum(numpy.stack(results), axis=0, dtype=numpy.uint64)
    return H, xedges, yedges

class ImageScatterMatrix(ApplierOperator):

    def ufunc(self, args):

        bandIndex1, bandIndex2, bins, mask, maskFunc, vmask, vmaskAllTouched, vmaskFilterSQL, stratification, strataDefinition = args

        band1 = self.getArray('image1', indicies=[bandIndex1])
        band2 = self.getArray('image2', indicies=[bandIndex2])

        valid = self.getMaskArray('image1', array=band1)
        valid *= self.getMaskArray('image2', array=band2)
        if mask is not None:
            valid *= self.getMaskArray('mask', noData=0, ufunc=maskFunc)
        if vmask is not None:
            valid *= self.getVectorArray('vmask', allTouched=vmaskAllTouched, filterSQL=vmaskFilterSQL, dtype=numpy.uint8) == 1
        x = band1[valid]
        y = band2[valid]
        if stratification is not None:
            strata = self.getClassificationArray('stratification', minWinnerCoverage=0.5)
            s = strata[valid]

        if stratification is None:
            H = numpy.histogram2d(x=x, y=y, bins=bins)[0]
        else:
            HList = list()
            for i in range(1, strataDefinition.classes+1):
                v = s==i
                Hi = numpy.histogram2d(x=x[v], y=y[v], bins=bins)[0]
                HList.append(numpy.array(Hi))
            H = numpy.stack(HList)

        return H