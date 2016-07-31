from lamos.types import MGRSTilingScheme, WRS2Footprint, MGRSFootprint, MGRSArchive
from lamos.operators.landsat_x import LandsatXComposer, TimeseriesBuilder
from lamos.operators.compositing import StatisticsApplier
from hub.timing import tic, toc
from hub.datetime import Date


def test():

    MGRSFootprint.shpRoot = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gis\reference_systems\mgrs\MGRS_100km_1MIL_Files'
    MGRSTilingScheme.shp = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gis\reference_systems\mgrs\MGRS-WRS2_Tiling_Scheme\MGRS-WRS2_Tiling_Scheme.shp'

    folder1 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\landsat'
    folder2 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4cs\landsatX'
    folder3 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4cs\landsatXMGRS'
    folder4 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4cs\landsatTimeseriesMGRS'
    folder4b = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4cs\landsatTimeseriesMGRS_GTiff'
    folder5 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4cs\statisticsMGRS'

    WRS2Footprint.createUtmLookup(infolder=folder1)

    wrs2Footprints = ['191026','192026','193026']
    mgrsFootprints = ['33UUP', '33UUQ', '33UVP', '33UVQ']
#                      17.08 h  16.42 h  3.21 h   2.73 h
    i=3
    mgrsFootprints = mgrsFootprints[i:i+1]

    composer = LandsatXComposer()
    #composer.composeWRS2Archive(infolder=folder1, outfolder=folder2, footprints=wrs2Footprints)

    tilingScheme = MGRSTilingScheme(pixelSize=30)
    #tilingScheme.tileWRS2Archive(infolder=folder2, outfolder=folder3, buffer=300, wrs2Footprints=wrs2Footprints, mgrsFootprints=mgrsFootprints)

    tsBuilder = TimeseriesBuilder(start=Date(1985, 1, 1), end=None)
#    tsBuilder.build(infolder=folder3, outfolder=folder4, envi=True, compressed=False, footprints=mgrsFootprints)

    years = range(1985, 2015+1)
    months = [7]
    days = [1]
    bufferDays = 183
    bufferYears = 0

    applier = StatisticsApplier(infolder=folder4, outfolder=folder5, compressed=False,
                                 years=years, months=months, days=days,
                                 bufferDays=bufferDays, bufferYears=bufferYears,
                                 footprints=mgrsFootprints, inextension='.img')
    applier.controls.setWindowXsize(10000)
    applier.controls.setWindowYsize(10)
    applier.controls.setNumThreads(20)
    applier.apply()


if __name__ == '__main__':

    tic()
    test()
    toc()
