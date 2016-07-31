from lamos.types import MGRSTilingScheme, WRS2Footprint, MGRSFootprint, MGRSArchive
from lamos.operators.landsat_x import LandsatXComposer, TimeseriesBuilder
from lamos.operators.compositing import StatisticsApplier
from lamos.operators.dummy import DummyReadApplier

from hub.timing import tic, toc
from hub.datetime import Date


def test():

    MGRSFootprint.shpRoot = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gis\reference_systems\mgrs\MGRS_100km_1MIL_Files'
    MGRSTilingScheme.shp = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gis\reference_systems\mgrs\MGRS-WRS2_Tiling_Scheme\MGRS-WRS2_Tiling_Scheme.shp'

    folder1  = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\landsat'
    folder2  = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4cs\small\landsatX'
    folder3 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4cs\small\landsatXMGRS'
    folder3b = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4cs\small\landsatXMGRS_GTiff'
    folder4 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4cs\small\landsatTimeseriesMGRS'
    folder4bsq = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4cs\small\landsatTimeseriesMGRS_GTiff'
    folder4bip = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4cs\small\landsatTimeseriesMGRS_GTiff_BIP'

    folder5  = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4cs\small\statisticsMGRS'

    WRS2Footprint.createUtmLookup(infolder=folder1)

#    wrs2Footprints = ['191026','192026','193026']
#    mgrsFootprints = ['33UUP', '33UUQ', '33UVP', '33UVQ']


    wrs2Footprints = ['191026']
    mgrsFootprints = ['33UVQ']
    start = None#Date(2015, 1, 1)
    end = None#Date(2015, 12, 31)

    composer = LandsatXComposer(start=start, end=end)
#    composer.composeWRS2Archive(infolder=folder1, outfolder=folder2, footprints=wrs2Footprints)

    tilingScheme = MGRSTilingScheme(pixelSize=30)
 #   tilingScheme.tileWRS2Archive(infolder=folder2, outfolder=folder3, buffer=300, wrs2Footprints=wrs2Footprints, mgrsFootprints=mgrsFootprints)

    #return
    #MGRSArchive(folder3).saveAsGTiff(outfolder=folder3b, processes=20)
    #return
    tsBuilder = TimeseriesBuilder()
    #tsBuilder.build(infolder=folder3b, outfolder=folder4, inextension='.tif', footprints=mgrsFootprints)


    MGRSArchive(folder4).saveAsGTiff(outfolder=folder4bsq, processes=20, compress='None')


    applier = DummyReadApplier(infolder=folder4, inextension='.vrt', footprints=mgrsFootprints)
    applier.controls.setWindowXsize(256*20)
    applier.controls.setWindowYsize(256)
    #applier.controls.setNumThreads(10)

    applier.apply()
    # 4 - > 82sm (100Z), 87 (all)
    # 4b -> 40s (BSQ compressed) 12s (BSQ uncompressed) 9s (Tiles 256x256)
    #

    return

    years = [2015]
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
