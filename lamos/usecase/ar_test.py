from lamos.processing.types import MGRSTilingScheme, WRS2Footprint, MGRSFootprint, MGRSArchive
from lamos.operators.landsat_x import LandsatXComposer, TimeseriesBuilder
from lamos.operators.compositing import CompositingApplier, StatisticsApplier
from lamos.operators.ml import ClassifierPredictApplier, SampleReadApplier
from lamos.operators.stack import StackApplier

from hub.timing import tic, toc
from hub.datetime import Date

import sys

def test():

    MGRSFootprint.shpRoot = r'C:\Work\data\gms\gis\MGRS_100km_1MIL_Files'
    MGRSTilingScheme.shp = r'C:\Work\data\gms\gis\MGRS-WRS2_Tiling_Scheme\MGRS-WRS2_Tiling_Scheme.shp'

    folder1 = r'C:\Work\data\gms\landsat'
    folder2 = r'C:\Work\data\gms\landsatX'
    folder3 = r'C:\Work\data\gms\_test\landsatXMGRS'
    folder4 = r'C:\Work\data\gms\_test\landsatTimeseriesMGRS'
    folder4a = r'C:\Work\data\gms\_test\landsatTimeseriesMGRS_ENVI'
    folder4b = r'C:\Work\data\gms\_test\landsatTimeseriesMGRS_GTiff'

    folder5 = r'C:\Work\data\gms\_test\productsMGRS2'
    folder6 = r'C:\Work\data\gms\_test\stacksMGRS'

    folderLucas = r'C:\Work\data\gms\lucasMGRS'


    WRS2Footprint.createUtmLookup(infolder=folder1)

    wrs2Footprints = ['193024','194024']
    mgrsFootprints = ['32UPC','32UQC','33UTT','33UUT']
    mgrsFootprints = ['33UUT']

    composer = LandsatXComposer()
    #composer.composeWRS2Archive(infolder=folder1, outfolder=folder2, footprints=wrs2Footprints, processes=10)

    tilingScheme = MGRSTilingScheme(pixelSize=30)
    #tilingScheme.tileWRS2Archive(infolder=folder2, outfolder=folder3, buffer=300, wrs2Footprints=wrs2Footprints, mgrsFootprints=mgrsFootprints, processes=10)

    #MGRSArchive(folder3).saveAsGTiff(folder3b, processes=10)

    tsBuilder = TimeseriesBuilder(start=None, end=None)
    #tsBuilder.build(infolder=folder3, outfolder=folder4, inextension='.vrt', footprints=mgrsFootprints, processes=1)

    #MGRSArchive(folder4).saveAsENVI(folder4a, processes=10)
    MGRSArchive(folder4).saveAsGTiff(folder4b, processes=10)

    #applier = CompositingApplier(infolder=folder4b, outfolder=folder5,
    #                             footprints=mgrsFootprints, inextension='.img', of='ENVI')
    # - add yearly composites
    #bufferYears = 30
    #for year in [2000]:
    #    applier.appendDateParameters(date1=Date(year, 1, 1), date2=Date(year, 12, 31), bufferYears=bufferYears)

    # - add 3 month composites
    '''bufferYears = 30
    for year in [2000, 2001]:
        applier.appendDateParameters(date1=Date(year, 1, 1), date2=Date(year, 3, 31), bufferYears=bufferYears)
        applier.appendDateParameters(date1=Date(year, 4, 1), date2=Date(year, 6, 30), bufferYears=bufferYears)
        applier.appendDateParameters(date1=Date(year, 7, 1), date2=Date(year, 9, 30), bufferYears=bufferYears)
        applier.appendDateParameters(date1=Date(year, 10, 1), date2=Date(year, 12, 31), bufferYears=bufferYears)'''

    #applier.controls.setWindowXsize(256)
    #applier.controls.setWindowYsize(256)
#    applier.controls.setNumThreads(10)
    #applier.apply()


    applier = StatisticsApplier(infolder=folder4b, outfolder=folder5,
                                footprints=mgrsFootprints, inextension='.tif', of='ENVI',
                                percentiles=[5,25,50,75,95], variables=[], mean=False, stddev=False)

    # - add yearly composites
    bufferYears = 30
    for year in [2000, 2001, 2002, 2003, 2004, 2005, 2006,2007,2008,2009,2010,2011,2012,2013,2014,2015]:
        applier.appendDateParameters(date1=Date(year, 1, 1), date2=Date(year, 12, 31), bufferYears=bufferYears)

    # - add 3 month composites
    '''bufferYears = 30
    for year in [2000, 2001]:
        applier.appendDateParameters(date1=Date(year, 1, 1), date2=Date(year, 3, 31), bufferYears=bufferYears)
        applier.appendDateParameters(date1=Date(year, 4, 1), date2=Date(year, 6, 30), bufferYears=bufferYears)
        applier.appendDateParameters(date1=Date(year, 7, 1), date2=Date(year, 9, 30), bufferYears=bufferYears)
        applier.appendDateParameters(date1=Date(year, 10, 1), date2=Date(year, 12, 31), bufferYears=bufferYears)'''

    applier.controls.setWindowXsize(64)
    applier.controls.setWindowYsize(64)
#    applier.controls.setNumThreads(10)
    from osgeo import gdal
    #gdal.SetCacheMax(100)
    applier.apply()


    return
    stacker = StackApplier(outfolder=folder6, outproduct='stack', outimage='stack', footprints=mgrsFootprints)
    stacker.appendFeatures(infolder=folder5, inproduct='composite', inimage='2000-01-01_to_2000-12-31_61y', inextension='.img', inbands=None)
    for key in ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'ndvi', 'nbr']:
        stacker.appendFeatures(infolder=folder5, inproduct='statistics', inimage=key+'_2000-01-01_to_2000-12-31_61y', inextension='.img', inbands=None)
    stacker.apply()

    sampleReader = SampleReadApplier(labelFolder=folderLucas, labelImage='lucas_lc4', footprints=mgrsFootprints)
    sampleReader.appendFeatures()
    samples = sampleReader.apply()

    rfc = randomForestFrandomForestit(samples)

    predictor = ClassifierPredictApplier(infolder=folder1, inextension='.img', outfolder=folder3, classifier=rfc)
    predictor.apply()

if __name__ == '__main__':

    tic()
    test()
    toc()
