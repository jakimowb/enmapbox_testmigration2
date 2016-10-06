from hub.datetime import Date
from hub.timing import tic, toc
from lamos.operators.compositing import StatisticsApplier
from lamos.operators.landsat_x import LandsatXComposer, TimeseriesBuilder
from lamos.processing.types import MGRSTilingScheme, WRS2Footprint, MGRSFootprint


def test():

    MGRSFootprint.shpRoot = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gis\reference_systems\mgrs\MGRS_100km_1MIL_Files'
    MGRSTilingScheme.shp = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gis\reference_systems\mgrs\MGRS-WRS2_Tiling_Scheme\MGRS-WRS2_Tiling_Scheme.shp'

    folder1 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\landsat'
    folder2 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4cs\landsatX'
    folder3 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4cs\landsatXMGRS'
    folder3b = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4cs\landsatXMGRS_GTiff'
    folder4 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4cs\landsatTimeseriesMGRS'
    folder4b = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4cs\landsatTimeseriesMGRS_GTiff'
    folder5 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4cs\statisticsMGRS_2'

    WRS2Footprint.createUtmLookup(infolder=folder1)

    wrs2Footprints = ['191026','192026','193026']
    mgrsFootprints = ['33UUP', '33UUQ', '33UVP', '33UVQ']

    start = Date(1985, 1, 1)
    end = Date(2015, 12, 31)

    i=3
    mgrsFootprints = mgrsFootprints[i:i+1]

    composer = LandsatXComposer()
    #composer.composeWRS2Archive(infolder=folder1, outfolder=folder2, footprints=wrs2Footprints)

    tilingScheme = MGRSTilingScheme(pixelSize=30)
    #tilingScheme.tileWRS2Archive(infolder=folder2, outfolder=folder3, buffer=300, wrs2Footprints=wrs2Footprints, mgrsFootprints=mgrsFootprints)

    #MGRSArchive(folder3).saveAsGTiff(outfolder=folder3b, compress='NONE', filter=mgrsFootprints, processes=100)



    tsBuilder = TimeseriesBuilder(start=start, end=end)
    #tsBuilder.build(infolder=folder3b, outfolder=folder4, inextension='.tif', footprints=mgrsFootprints)
    #tsBuilder.build(infolder=folder3, outfolder=folder4, inextension='.vrt', footprints=mgrsFootprints)

    #MGRSArchive(folder4).saveAsGTiff(outfolder=folder4b, compress='NONE', filter=mgrsFootprints, processes=100)

    applier = StatisticsApplier(infolder=folder4b, outfolder=folder5, compressed=False,
                                years=[], months=[], days=[],
                                bufferDays=None, bufferYears=None,
                                footprints=mgrsFootprints, inextension='.tif')

    years = range(start.year, end.year + 1)
    for year in years:


        months = [7]
        days = [1]
        bufferDays = 183
        bufferYears = 0
        for month in months:
                    for day in days:
                        applier.appendDateParameters(year=year, month=month, day=day,
                                                  bufferYears=bufferYears, bufferDays=bufferDays)

        months = [7]
        days = [15]
        bufferDays = 46
        bufferYears = 0
        for month in months:
                    for day in days:
                        applier.appendDateParameters(year=year, month=month, day=day,
                                                  bufferYears=bufferYears, bufferDays=bufferDays)

    applier.controls.setWindowXsize(256)
    applier.controls.setWindowYsize(256)
#    applier.controls.setNumThreads(50)
    applier.apply()


if __name__ == '__main__':

    tic()
    test()
    toc()
