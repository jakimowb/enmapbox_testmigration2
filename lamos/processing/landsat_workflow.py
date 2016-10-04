from __future__ import print_function
import os
from os.path import join
import numpy
from enmapbox.processing.estimators import Classifiers

from enmapbox.processing.workflow import (GDALMeta, Date, Workflow,
                                          ImageFA, ImageBA,
                                          FilenameAssociationsCollection, BlockAssociationsCollection,
                                          ProductFA, ProductBA,
                                          ProductCollectionFA, ProductCollectionBA)
from lamos.processing.workflow import LandsatFA, LandsatBA, LandsatCollectionFA, LandsatCollectionBA
from hub.nan1d.percentiles import nanpercentiles
from hub.timing import tic, toc
from hub.gdal.api import readCube

def assertType(obj, type):
    assert isinstance(obj, type) # makes PyCharm aware of the type!
    return obj

def calculateTimeseriesMetrics(info, timeseriesBA, percentiles, start, end, mean=True, stddev=True):

    assert isinstance(timeseriesBA, ProductBA)
    assert isinstance(start, Date)
    assert isinstance(end, Date)

    timeseriesMetricsBA = ProductBA(productName='timeseries_metrics')
    imageKeyPostfix = '_'+str(start)+'_to_'+str(end)
    target = start+(end-start)/2
    bands, lines, samples = len(percentiles) + mean + stddev, info.blockheight, info.blockwidth

    # define metrics metadata
    def percentileName(p):
        if p == 0: return 'min'
        elif p == 50: return 'median'
        elif p == 100: return 'max'
        else: return 'p' + str(p)

    outmeta = GDALMeta()
    noDataValue = numpy.iinfo(numpy.int16).min
    bandNames = [percentileName(p) for p in percentiles]
    if mean: bandNames.append('mean')
    if stddev: bandNames.append('stddev')
    outmeta.setNoDataValue(noDataValue)
    outmeta.setMetadataItem('acquisition time', str(target))
    outmeta.setBandNames(bandNames)

    # define counts metadata
    countsMeta = GDALMeta()
    countsMeta.setMetadataItem('acquisition time', str(target))
    countsMeta.setBandNames(['clear observation count'])

    # prepare clear observation masks
    fmask, fmaskMeta =  timeseriesBA.getBlock('fmask')
    invalidValues = fmask >= 2
    invalidPixel = numpy.all(invalidValues, axis=0)

    # create count image
    counts = numpy.sum(numpy.logical_not(invalidValues), axis=0, dtype=numpy.int16, keepdims=True)

    if counts.size == 0: # handle empty collection case
        counts = numpy.zeros((1, lines, samples), dtype=numpy.int16)

    timeseriesMetricsBA.addBlock(key='count'+imageKeyPostfix, cube=counts, meta=countsMeta)

    # create metrics images
    for key, (cube, meta) in timeseriesBA.items():
        if key == 'fmask': continue
        cube = cube.astype(numpy.float32)
        cube[invalidValues] = numpy.NaN

        # create output cube
        # - percentiles
        statistics = nanpercentiles(cube, percentiles=percentiles)
        # - moments
        if mean:
            statistics.append(numpy.nanmean(cube, axis=0, dtype=numpy.float32, keepdims=True))
        if stddev:
            statistics.append(numpy.nanstd(cube, axis=0, dtype=numpy.float32, keepdims=True))

        for i, band in enumerate(statistics):
            band = band.astype(numpy.int16)
            band[invalidPixel[None]] = noDataValue
            statistics[i] = band

        outcube = numpy.vstack(statistics)
        if outcube.size == 0:  # handle empty collection case
            outcube = numpy.full((bands, lines, samples), fill_value=noDataValue, dtype=numpy.int16)

        timeseriesMetricsBA.addBlock(key=key+imageKeyPostfix, cube=outcube, meta=outmeta)

    return timeseriesMetricsBA

'''def drawSample(info, featuresBA, labelsBA):

    features = featuresBA.cube
    labels = labelsBA.cube
    valid = labels != 0
    featuresVector = features[:, valid[0]]
    labelsVector = labels[valid]
    sample = (featuresVector, labelsVector)
    return sample'''

def trainClassifier(sample):

    featureList, labelsList = sample
    features = numpy.hstack(featureList)[:,:,0]
    labels = numpy.vstack(labelsList)[:,0]

    rfc = Classifiers.RandomForestClassifier(oob_score=True, n_estimators=100, class_weight='balanced', n_jobs=1)
    rfc.sklEstimator.fit(X=features.T, y=labels)
    return rfc

def applyClassifier(rfc, featuresBA, classificationMeta):

    featuresStack = featuresBA.cube
    shape = featuresStack.shape
    featuresStack = featuresStack.reshape((shape[0], -1))
    classification = rfc.sklEstimator.predict(X=featuresStack.T)
    classification = classification.reshape(shape[1:])
    classificationBA = ImageBA().addBlock(cube=classification, meta=classificationMeta)

    return classificationBA


class ClassificationWorkflowA(Workflow):

    def apply(self, info):

        # assert inputs
        landsatCollectionBA = assertType(self.inputs.landsatCollection, LandsatCollectionBA)
        #lucasBA = assertType(self.inputs.lucas, ImageBA)
        if self.inargs.applyModel:
            rfc = assertType(self.inargs.rfc, Classifiers.RandomForestClassifier)
            classificationMeta = assertType(self.inargs.classificationMeta, GDALMeta)

        timeseriesMetricsCollectionBA = ProductCollectionBA()

        percentiles = [0,25,50,75,100]
        for year in range(2015, 2015+1):
            start = Date(year, 1, 1)
            end = Date(year, 12, 31)
            filteredLandsatCollectionBA = landsatCollectionBA.filterDate(start=start, end=end)
            timeseriesBA = filteredLandsatCollectionBA.getTimeseriesProduct(productName='timeseries')
            timeseriesMetricsBA = calculateTimeseriesMetrics(info, timeseriesBA, percentiles=percentiles, mean=True, stddev=True,
                                                             start=start, end=end)
            # collect outputs
            timeseriesMetricsCollectionBA.append(timeseriesMetricsBA)

        # prepare feature stack
        featureStackBA = timeseriesMetricsCollectionBA.getStack(productName='stack')

        # apply model
        if self.inargs.applyModel:
            classificationBA = applyClassifier(rfc, featureStackBA, classificationMeta)

        # prepare outputs
        self.outputs.featureStack = featureStackBA
        self.outputs.timeseriesMetricsCollection = timeseriesMetricsCollectionBA
        if self.inargs.applyModel:
            self.outputs.classification = classificationBA


class ClassificationWorkflowB(Workflow):

    def apply(self, info):

        # assert inputs
        rfc = assertType(self.inargs.rfc, Classifiers.RandomForestClassifier)
        classificationMeta = assertType(self.inargs.classificationMeta, GDALMeta)
        featureStackBA = assertType(self.inputs.featureStack, ImageBA)

        # apply classifier
        classificationBA = applyClassifier(rfc, featureStackBA, classificationMeta)

        self.outputs.classification = classificationBA

def testClassificationWorkflow():

    print('create metrics for trainings sample')
    mgrsFootprints = ['33UUT','33UUT']
    extractedFeatureStackFAList = list()
    extractedLucasImageFAList = list()
    for mgrsFootprint in mgrsFootprints:
        subfolders = join(mgrsFootprint[0:2], mgrsFootprint)
        print(mgrsFootprint)

        # sample lucas locations
        landsatCollectionFA = LandsatCollectionFA(join(r'C:\Work\data\gms\landsatXMGRS_ENVI', subfolders))
        lucasFA = ProductFA(join(r'C:\Work\data\gms\lucasMGRS', subfolders, 'lucas'))
        lucasImageFA = ImageFA(join(r'C:\Work\data\gms\lucasMGRS', subfolders, 'lucas\lucas_lc4.img'))
        extractedLandsatCollectionFA = landsatCollectionFA.extractByMask(maskFA=lucasImageFA, dirname=join(r'C:\Work\data\gms\landsatXMGRS_ENVI_extracted', subfolders))
        extractedLucasFA = lucasFA.extractByMask(maskFA=lucasImageFA, dirname=join(r'C:\Work\data\gms\lucasMGRS_extracted', subfolders, 'lucas'))
        extractedLucasImageFA = ImageFA(join(r'C:\Work\data\gms\lucasMGRS_extracted', subfolders, 'lucas\lucas_lc4.img'))
        extractedFeatureStackFA = ImageFA(join(r'C:\Work\data\gms\stack_extracted', subfolders, 'stack\stack.img'))

        # for lucas samples: create feature stack
        workflowA = ClassificationWorkflowA()
        workflowA.infiles.landsatCollection = extractedLandsatCollectionFA
        workflowA.infiles.lucas = extractedLucasImageFA
        workflowA.outfiles.featureStack = extractedFeatureStackFA
        workflowA.inargs.applyModel = False
        workflowA.controls.setOutputDriverENVI()
        workflowA.run()

        extractedFeatureStackFAList.append(extractedFeatureStackFA)
        extractedLucasImageFAList.append(extractedLucasImageFA)

    # train classifier
    print('train RFC')
    sample = ([readCube(extractedFeatureStackFA.filename) for extractedFeatureStackFA in extractedFeatureStackFAList],
              [readCube(extractedLucasImageFA.filename) for extractedLucasImageFA in extractedLucasImageFAList])
    rfc = trainClassifier(sample)
    classificationMeta = GDALMeta(filename=workflowA.infiles.lucas.filename)

    print('create metrics for complete archive and apply RFC')
    mgrsFootprints = ['32UPC', '32UQC', '33UTT', '33UUT']
    for mgrsFootprint in mgrsFootprints:
        subfolders = join(mgrsFootprint[0:2], mgrsFootprint)
        print(mgrsFootprint)

        # create feature stack and sample lucas data
        workflowA = ClassificationWorkflowA()
        workflowA.infiles.landsatCollection = LandsatCollectionFA(join(r'C:\Work\data\gms\landsatXMGRS_ENVI', subfolders))\
            .filterDate(start=Date(1960,1,1), end=Date.fromYearDoy(2990, 130))
        #workflowA.infiles.lucas = ImageFA(join(r'C:\Work\data\gms\lucasMGRS', subfolders, 'lucas\lucas_lc4.img'))
        #workflow.outfiles.timeseriesMetricsCollectionBA = ProductCollectionFA(r'C:\Work\data\gms\new_timeseriesMetrics\32\32UPC')
        workflowA.outfiles.featureStack = ImageFA(join(r'C:\Work\data\gms\new_timeseriesMetrics', subfolders, 'stack\stack.tif'))
        workflowA.outfiles.classification = ImageFA(join(r'C:\Work\data\gms\new_timeseriesMetrics', subfolders, 'rfc\classification.img'))
        workflowA.inargs.applyModel = True
        workflowA.inargs.rfc = rfc
        workflowA.inargs.classificationMeta = classificationMeta

        workflowA.controls.setNumThreads(1)
        workflowA.controls.setOutputDriverGTiff()
        workflowA.run()

    # and apply model
    '''workflowB = ClassificationWorkflowB()
    workflowB.infiles.featureStack = workflowA.outfiles.featureStack
    workflowB.outfiles.classification = ImageFA(r'C:\Work\data\gms\new_timeseriesMetrics\?\rfc\classification.img')
    workflowB.inargs.rfc = rfc
    workflowB.inargs.classificationMeta = GDALMeta(filename=workflowA.infiles.lucas.filename)

    workflowB.controls.setNumThreads(1)
    workflowB.controls.setOutputDriverENVI()
    workflowB.run()'''



if __name__ == '__main__':
    tic()
    testClassificationWorkflow()
    toc()