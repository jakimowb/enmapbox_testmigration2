from lamos.types import MGRSTilingScheme, WRS2Footprint, MGRSFootprint, MGRSArchive
from lamos.operators.landsat_x import LandsatXComposer, TimeseriesBuilder
from lamos.operators.compositing import CompositingApplier, StatisticsApplier
from hub.timing import tic, toc
from hub.datetime import Date


def test():

    MGRSFootprint.shpRoot = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gis\reference_systems\mgrs\MGRS_100km_1MIL_Files'
    MGRSTilingScheme.shp = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gis\reference_systems\mgrs\MGRS-WRS2_Tiling_Scheme\MGRS-WRS2_Tiling_Scheme.shp'

    folder1 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\landsat'
    folder2 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gms\landsatX'
    folder3 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gms\landsatXMGRS'
    folder4 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gms\landsatTimeseriesMGRS'
    folder4b = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gms\landsatTimeseriesMGRS_ENVI'
    folder5 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gms\productsMGRS'

    WRS2Footprint.createUtmLookup(infolder=folder1)

    wrs2Footprints = ['192023','193023','194023','192024','193024','194024']
    mgrsFootprints = ['33UUU', '33UVU', '33UUT', '33UVT']

    start = Date(2014, 1, 1)
    end = Date(2016, 6, 30)

    composer = LandsatXComposer(start=start, end=end)
    composer.composeWRS2Archive(infolder=folder1, outfolder=folder2, footprints=wrs2Footprints, processes=20)

    tilingScheme = MGRSTilingScheme(pixelSize=30)
    tilingScheme.tileWRS2Archive(infolder=folder2, outfolder=folder3, buffer=300, wrs2Footprints=wrs2Footprints, mgrsFootprints=mgrsFootprints, processes=20)

    tsBuilder = TimeseriesBuilder(start=start, end=None)
    tsBuilder.build(infolder=folder3, outfolder=folder4, footprints=mgrsFootprints)

    MGRSArchive(folder4).saveAsENVI(folder4b, compress=True, filter=mgrsFootprints, processes=20)

    return
    applier = StatisticsApplier(infolder=folder4b, outfolder=folder5, of='ENVI',
                                footprints=mgrsFootprints, inextension='.img')
    bufferYears = 0
    for year in range(start.year, end.year+1):
        applier.appendDateParameters(date1=Date(year, 1, 1), date2=Date(year, 12, 31), bufferYears=bufferYears)
    applier.controls.setWindowXsize(256)
    applier.controls.setWindowYsize(256)
    applier.controls.setNumThreads(10)
    applier.apply()

    # - Treffen mit Dirk -
    # 3, 6, 12 Monatskomposite


if __name__ == '__main__':

    tic()
    test()
    toc()
