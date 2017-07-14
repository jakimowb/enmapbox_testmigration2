import numpy
from hubdc.applier import Applier, ApplierOperator, PixelGrid, CUIProgressBar

def getProgressBar(currentProgressBar):
    if currentProgressBar is None:
        return CUIProgressBar()
    else:
        return currentProgressBar

def classificationFromVector(vector, classification, grid,
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

def sampleImageByClassification(image, classification, progressBar=None):

    applier = Applier()
    applier.controls.setProgressBar(progressBar)
    applier.controls.setReferenceGridByImage(image)

    applier.setInput('raster', filename=image)
    applier.setInput('classification', filename=classification)

    class SampleRasterByClassification(ApplierOperator):
        def ufunc(self):
            features = self.getArray('raster')
            fractions = self.getProbabilityArray('classification')
            labeled = fractions.sum(axis=0) != 0
            classes, classNames, classLookup = self.getMetadataClassDefinition('classification')
            return features[:, labeled], fractions[:, labeled], classes, classNames, classLookup

    results = applier.apply(operator=SampleRasterByClassification)

    features = numpy.hstack(result[0] for result in results)
    fractions = numpy.hstack(result[1] for result in results)
    classes, classNames, classLookup = results[0][2:]

    return features, fractions, classes, classNames, classLookup
