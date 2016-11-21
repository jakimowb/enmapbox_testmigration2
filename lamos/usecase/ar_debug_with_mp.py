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

    folder3 = r'C:\Work\data\gms\20161115\hub_compressed_small' #r'C:\Work\data\gms\landsatXMGRS'
    folder4 = r'C:\Work\data\gms\20161115\_landsatTimeseriesMGRS'
    folder5 = r'C:\Work\data\gms\20161115\_productsMGRS'

    mgrsFootprints = ['33UUU']

    tsBuilder = TimeseriesBuilder(start=None, end=None)
    tsBuilder.build(infolder=folder3, outfolder=folder4, inextension='.tif', footprints=mgrsFootprints, processes=1)

    applier = StatisticsApplier(infolder=folder4, outfolder=folder5,
                                footprints=mgrsFootprints, inextension='.vrt', of='ENVI',
                                percentiles=[5,25,50,75,95], variables=[], mean=False, stddev=False)

    # - add yearly composites
    bufferYears = 30
    for year in [2000]:#, 2001]:
        applier.appendDateParameters(date1=Date(year, 1, 1), date2=Date(year, 12, 31), bufferYears=bufferYears)

    applier.controls.setWindowXsize(50)
    applier.controls.setWindowYsize(50)
#    applier.controls.setNumThreads(10)
    applier.apply()

if __name__ == '__main__':

    tic()
    test()
    toc()
