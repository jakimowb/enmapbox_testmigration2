from __future__ import print_function
import os
from os.path import join
import numpy
from enmapbox.processing.estimators import Classifiers, unpickle

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

def trainClassifier(featuresFAList, labelsFAList):

    for fa in featuresFAList: assert isinstance(fa, ImageFA)
    for fa in labelsFAList: assert isinstance(fa, ImageFA)

    featureList = [readCube(fa.filename) for fa in featuresFAList]
    labelsList = [readCube(fa.filename) for fa in labelsFAList]

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
        #for year in range(2015, 2015+1):
        start = Date(2015, 1, 1)
        end = Date(2016, 6, 30)
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


def test_gms_beta():

    folderLandsatVRT = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gms\landsatXMGRS'
    folderLandsatGTiff = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gms\landsatXMGRS_GTiff'
    if 0: # use VRT
        folderLandsat = folderLandsatVRT
    else:
        folderLandsat = folderLandsatGTiff
    folderLandsatExtracted = folderLandsat+'_extracted'

    folder4 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gms\landsatTimeseriesMGRS'
    folder4b = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gms\landsatTimeseriesMGRS_ENVI'
    folder5 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gms\productsMGRS'
    folderLucas = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gms\lucasMGRS'
    folderLucasExtracted = folderLucas + '_extracted'

    folderStack = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gms\stackMGRS'
    folderStackExtracted = folderStack + '_extracted'

    folderRFC = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gms\rfcMGRS'
    filenameRFC = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gms\rfc.model'

    filename1 = r'\\141.20.140.91\SAN_Projects\Geomultisens\data\testdata\reference_data\eu27_lucas_2012_subset1.shp'
    filename2 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gms\lucas_lc4.pkl'
    filename3 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gms\lucas_lc4.json'


    print('create metrics for training samples')
    mgrsFootprints = ['33UUU', '33UVU', '33UUT', '33UVT']

    if 0: # 1=train rfc, 0=load rfc from file
        extractedFeatureStackFAList = list()
        extractedLucasImageFAList = list()
        for mgrsFootprint in mgrsFootprints:
            subfolders = join(mgrsFootprint[0:2], mgrsFootprint)
            print(mgrsFootprint)

            # sample lucas locations
            landsatCollectionFA = LandsatCollectionFA(join(folderLandsat, subfolders))
            lucasFA = ProductFA(join(folderLucas, subfolders, 'lucas'))
            lucasImageFA = ImageFA(join(folderLucas, subfolders, 'lucas', 'lucas_lc4.img'))
            extractedLandsatCollectionFA = landsatCollectionFA.extractByMask(maskFA=lucasImageFA, dirname=join(folderLandsatExtracted, subfolders), processes=1)
            extractedLucasFA = lucasFA.extractByMask(maskFA=lucasImageFA, dirname=join(folderLucasExtracted, subfolders, 'lucas'))
            extractedLucasImageFA = ImageFA(join(folderLucasExtracted, subfolders, 'lucas', 'lucas_lc4.img'))
            extractedFeatureStackFA = ImageFA(join(folderStackExtracted, subfolders, 'stack', 'stack.img'))

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
        rfc = trainClassifier(featuresFAList=extractedFeatureStackFAList, labelsFAList=extractedLucasImageFAList)
        rfc.pickle(filename=filenameRFC)

    rfc = unpickle(filename=filenameRFC)
    classificationMeta = GDALMeta(filename=join(folderLucas, '33', '33UUU', 'lucas', 'lucas_lc4.img'))


    print('create metrics for complete archive and apply RFC')
    for mgrsFootprint in mgrsFootprints:
        subfolders = join(mgrsFootprint[0:2], mgrsFootprint)
        print(mgrsFootprint)

        # create feature stack and sample lucas data
        workflowA = ClassificationWorkflowA()
        workflowA.infiles.landsatCollection = LandsatCollectionFA(join(folderLandsat, subfolders))\
            .filterDate(start=Date(1960,1,1), end=Date.fromYearDoy(2990, 130))
        #workflowA.infiles.lucas = ImageFA(join(r'C:\Work\data\gms\lucasMGRS', subfolders, 'lucas\lucas_lc4.img'))
        #workflow.outfiles.timeseriesMetricsCollectionBA = ProductCollectionFA(r'C:\Work\data\gms\new_timeseriesMetrics\32\32UPC')
        #workflowA.outfiles.featureStack = ImageFA(join(folderStack, subfolders, 'stack', 'stack.tif'))
        workflowA.outfiles.classification = ImageFA(join(folderRFC, subfolders, 'rfc', 'classification.img'))
        workflowA.inargs.applyModel = True
        workflowA.inargs.rfc = rfc
        workflowA.inargs.classificationMeta = classificationMeta

        workflowA.controls.setNumThreads(10)
        #workflowA.controls.setWindowXsize(64)
        #workflowA.controls.setWindowYsize(64)
        workflowA.controls.setOutputDriverGTiff()
        #workflowA.controls.setOutputDriverENVI()
        workflowA.run()



if __name__ == '__main__':
    tic()
    test_gms_beta()
    toc()
    #32.59 min for 10 Threads on 1 Footprint