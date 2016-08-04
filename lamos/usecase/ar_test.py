from lamos.types import MGRSTilingScheme, WRS2Footprint, MGRSFootprint, MGRSArchive
from lamos.operators.landsat_x import LandsatXComposer, TimeseriesBuilder
from lamos.operators.ndvi import NDVIApplier
from lamos.operators.mean import MeanApplier
from lamos.operators.compositing import CompositingApplier, StatisticsApplier
from hub.timing import tic, toc
from hub.datetime import Date

def test():

    MGRSFootprint.shpRoot = r'C:\Work\data\gms\gis\MGRS_100km_1MIL_Files'
    MGRSTilingScheme.shp = r'C:\Work\data\gms\gis\MGRS-WRS2_Tiling_Scheme\MGRS-WRS2_Tiling_Scheme.shp'

    folder1 = r'C:\Work\data\gms\landsat'
    folder2 = r'C:\Work\data\gms\landsatX'
    folder3 = r'C:\Work\data\gms\landsatXMGRS'
    folder3b = r'C:\Work\data\gms\landsatXMGRS_GTiff'
    folder4 = r'C:\Work\data\gms\landsatTimeseriesMGRS'
    folder4b = r'C:\Work\data\gms\landsatTimeseriesMGRS_GTiff'

    folder5 = r'C:\Work\data\gms\productsMGRS'
    folder5b = r'C:\Work\data\gms\productsMGRS_ENVI'

    WRS2Footprint.createUtmLookup(infolder=folder1)

    wrs2Footprints = ['193024','194024']
    mgrsFootprints = ['32UPC','32UQC','33UTT','33UUT']
    #mgrsFootprints = ['33UTT']

    composer = LandsatXComposer()
    composer.composeWRS2Archive(infolder=folder1, outfolder=folder2, footprints=wrs2Footprints, processes=10)

    tilingScheme = MGRSTilingScheme(pixelSize=30)
    tilingScheme.tileWRS2Archive(infolder=folder2, outfolder=folder3, buffer=300, wrs2Footprints=wrs2Footprints, mgrsFootprints=mgrsFootprints, processes=10)

    #MGRSArchive(folder3).saveAsGTiff(folder3b, processes=10)

    tsBuilder = TimeseriesBuilder(start=None, end=None)
    #tsBuilder.build(infolder=folder3b, outfolder=folder4, inextension='.tif', footprints=mgrsFootprints)
    tsBuilder.build(infolder=folder3, outfolder=folder4, inextension='.vrt', footprints=mgrsFootprints, processes=10)

    MGRSArchive(folder4).saveAsENVI(folder4b, compress=False, processes=10)

    applier = CompositingApplier(infolder=folder4b, outfolder=folder5,
                                 footprints=mgrsFootprints, inextension='.img', of='ENVI')
    # - add yearly composites
    bufferYears = 30
    for year in [2000, 2001]:
        applier.appendDateParameters(date1=Date(year, 1, 1), date2=Date(year, 12, 31), bufferYears=bufferYears)

    # - add 3 month composites
    '''bufferYears = 30
    for year in [2000, 2001]:
        applier.appendDateParameters(date1=Date(year, 1, 1), date2=Date(year, 3, 31), bufferYears=bufferYears)
        applier.appendDateParameters(date1=Date(year, 4, 1), date2=Date(year, 6, 30), bufferYears=bufferYears)
        applier.appendDateParameters(date1=Date(year, 7, 1), date2=Date(year, 9, 30), bufferYears=bufferYears)
        applier.appendDateParameters(date1=Date(year, 10, 1), date2=Date(year, 12, 31), bufferYears=bufferYears)'''

    applier.controls.setWindowXsize(256)
    applier.controls.setWindowYsize(256)
#    applier.controls.setNumThreads(10)
    applier.apply()

    applier = StatisticsApplier(infolder=folder4b, outfolder=folder5,
                                footprints=mgrsFootprints, inextension='.img', of='ENVI')

    # - add yearly composites
    bufferYears = 30
    for year in [2000, 2001]:
        applier.appendDateParameters(date1=Date(year, 1, 1), date2=Date(year, 12, 31), bufferYears=bufferYears)

    # - add 3 month composites
    '''bufferYears = 30
    for year in [2000, 2001]:
        applier.appendDateParameters(date1=Date(year, 1, 1), date2=Date(year, 3, 31), bufferYears=bufferYears)
        applier.appendDateParameters(date1=Date(year, 4, 1), date2=Date(year, 6, 30), bufferYears=bufferYears)
        applier.appendDateParameters(date1=Date(year, 7, 1), date2=Date(year, 9, 30), bufferYears=bufferYears)
        applier.appendDateParameters(date1=Date(year, 10, 1), date2=Date(year, 12, 31), bufferYears=bufferYears)

    applier.controls.setWindowXsize(256)
    applier.controls.setWindowYsize(256)
    applier.controls.setNumThreads(10)
    applier.apply()'''


if __name__ == '__main__':

    tic()
    test()
    toc()
