from lamos.types import MGRSTilingScheme, WRS2Footprint, MGRSFootprint, MGRSArchive
from lamos.operators.landsat_x import LandsatXComposer, TimeseriesBuilder
from lamos.operators.compositing import StatisticsApplier
from hub.timing import tic, toc
from hub.datetime import Date
import os, gdal

def test():

    MGRSFootprint.shpRoot = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gis\reference_systems\mgrs\MGRS_100km_1MIL_Files'
    MGRSTilingScheme.shp = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gis\reference_systems\mgrs\MGRS-WRS2_Tiling_Scheme\MGRS-WRS2_Tiling_Scheme.shp'

    folder1 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\landsat'
    folder2 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4cs\landsatX'
    folder3 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4cs\landsatXMGRS'
    folder3b = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4cs\landsatXMGRS_GTiff'
    folder4 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4cs\landsatTimeseriesMGRS'
    folder4b = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4cs\landsatTimeseriesMGRS_GTiff'
    folder5 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4cs\statisticsMGRS'

    WRS2Footprint.createUtmLookup(infolder=folder1)

    wrs2Footprints = ['191026','192026','193026']
    mgrsFootprints = ['33UUP', '33UUQ', '33UVP', '33UVQ']

    start = Date(1985, 1, 1)
    end = Date(2015, 12, 31)

    i=3
    mgrsFootprints = mgrsFootprints[i:i+1]

    composer = LandsatXComposer()
    #composer.composeWRS2Archive(infolder=folder1, outfolder=folder2, footprints=wrs2Footprints, processes=50)

    tilingScheme = MGRSTilingScheme(pixelSize=30)
    #tilingScheme.tileWRS2Archive(infolder=folder2, outfolder=folder3, buffer=300, wrs2Footprints=wrs2Footprints, mgrsFootprints=mgrsFootprints, processes=50)

    #MGRSArchive(folder3).saveAsGTiff(outfolder=folder3b, compress='NONE', filter=mgrsFootprints, processes=100)


    tsBuilder = TimeseriesBuilder(start=start, end=end)
    #tsBuilder.build(infolder=folder3b, outfolder=folder4, inextension='.tif', footprints=mgrsFootprints)
    #tsBuilder.build(infolder=folder3, outfolder=folder4, inextension='.vrt', footprints=mgrsFootprints, processes=50)

    #MGRSArchive(folder4).saveAsGTiff(outfolder=folder4b, compress='NONE', filter=mgrsFootprints, processes=5)


    #MGRSArchive(folder4).saveAsENVI(outfolder=folder4b, filter=mgrsFootprints, processes=10)

    applier = StatisticsApplier(infolder=folder4b, outfolder=folder5,
                                footprints=mgrsFootprints, inextension='.tif', of='ENVI',
                                percentiles=[5,25,50,75,95], variables=['tcb','tcg','tcw'], mean=False, stddev=False)

    bufferYears = 1
    years = range(start.year, end.year + 1)
    for year in years:
        applier.appendDateParameters(date1=Date(year, 1, 1), date2=Date(year, 12, 31), bufferYears=bufferYears)

    applier.controls.setWindowXsize(256)
    applier.controls.setWindowYsize(256)
    applier.apply()


if __name__ == '__main__':

    tic()
    test()
    toc()
