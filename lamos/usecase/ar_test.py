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
    composer.composeWRS2Archive(infolder=folder1, outfolder=folder2, footprints=wrs2Footprints)

    tilingScheme = MGRSTilingScheme(pixelSize=30)
    tilingScheme.tileWRS2Archive(infolder=folder2, outfolder=folder3, buffer=300, wrs2Footprints=wrs2Footprints, mgrsFootprints=mgrsFootprints)

    MGRSArchive(folder3).saveAsGTiff(folder3b, processes=10)

    tsBuilder = TimeseriesBuilder(start=None, end=None)
    tsBuilder.build(infolder=folder3b, outfolder=folder4, inextension='.tif', footprints=mgrsFootprints)

    MGRSArchive(folder4).saveAsGTiff(folder4b, compress='NONE', interleave='PIXEL', processes=10)

    years = [2000]
    months = [7]
    days = [1]
    bufferDays = 190
    bufferYears = 30

    applier = CompositingApplier(infolder=folder4b, outfolder=folder5, compressed=False,
                                 years=years, months=months, days=days,
                                 bufferDays=bufferDays, bufferYears=bufferYears,
                                 footprints=mgrsFootprints, inextension='.tif')
    applier.controls.setWindowXsize(256)
    applier.controls.setWindowYsize(256)
    applier.controls.setNumThreads(10)
    #applier.apply()

    applier = StatisticsApplier(infolder=folder4b, outfolder=folder5, compressed=False,
                                 years=years, months=months, days=days,
                                 bufferDays=bufferDays, bufferYears=bufferYears,
                                 footprints=mgrsFootprints, inextension='.tif')
    applier.controls.setWindowXsize(256)
    applier.controls.setWindowYsize(256)
    applier.controls.setNumThreads(10)
    applier.apply()


if __name__ == '__main__':

    tic()
    test()
    toc()
