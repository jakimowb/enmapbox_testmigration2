from __future__ import print_function
import hub.file
from enmapbox.processing.estimators import Classifiers
from hub.datetime import Date
from hub.timing import tic, toc
from lamos.operators.compositing import StatisticsApplier
from lamos.operators.importer import LucasImportApplier
from lamos.operators.landsat_x import LandsatXComposer, TimeseriesBuilder
from lamos.operators.ml import SampleReadApplier, ClassifierPredictApplier, exportSampleAsJSON
from lamos.operators.stack import StackApplier
from lamos.operators.importer import LucasImportApplier
from lamos.operators.ml import SampleReadApplier, ClassifierPredictApplier, exportSampleAsJSON
from lamos.processing.types import MGRSFootprint, MGRSTilingScheme, MGRSArchive, WRS2Footprint
import hub.file
from hub.timing import tic, toc
from hub.datetime import Date
from enmapbox.processing.estimators import Classifiers
from os.path import join


def test(i=None):

    MGRSFootprint.shpRoot = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gis\reference_systems\mgrs\MGRS_100km_1MIL_Files'
    MGRSTilingScheme.shp = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gis\reference_systems\mgrs\MGRS-WRS2_Tiling_Scheme\MGRS-WRS2_Tiling_Scheme.shp'

    root = r'\\141.20.140.91\SAN_RSData\S_Africa'
    root2 = r'\\141.20.140.91\NAS_Work\es_south_africa'
    folder1 = join(root, 'landsat')
    folder2 = join(root, '_1_landsatX')
    folder3 = join(root, '_2_landsatXMGRS')
    folder3b = join(root, '_3_landsatXMGRS_GTiff')

    folder4 = join(root, '_4_landsatTimeseriesMGRS')
    folder5 = join(root2, '_5_productsMGRS')

    #WRS2Footprint.createUtmLookup(infolder=folder1)

    wrs2Footprints = None # ['192023','193023','194023','192024','193024','194024']
    mgrsFootprints = ['34JGQ', '34JFR', '34JGR', '34JFS', '34JGS', '34JHS', '34JGT', '35JKJ', '35JLJ', '35JKK', '35JLK', '35JMK', '35JKL', '35JLL', '35JML', '35JNL', '35JJM', '35JKM', '35JLM', '35JMM', '35JNM', '35JPM', '35JLN', '35JMN', '35JNN', '35JPN']
    #mgrsFootprints = ['35JJM']

    if i is not None:
        mgrsFootprints = mgrsFootprints[i:i+1]
        assert len(mgrsFootprints) > 0

    start = None #Date(2011, 1, 1)
    end = None #Date(2013, 12, 31)

    composer = LandsatXComposer(start=start, end=end)
    #composer.composeWRS2Archive(infolder=folder1, outfolder=folder2, footprints=wrs2Footprints, processes=100)

    tilingScheme = MGRSTilingScheme(pixelSize=30)
    #tilingScheme.tileWRS2Archive(infolder=folder2, outfolder=folder3, buffer=300, wrs2Footprints=wrs2Footprints, mgrsFootprints=mgrsFootprints, processes=100)
    # 42 min

    # MGRSArchive(folder3).saveAsGTiff(folder3b, filter=mgrsFootprints, processes=50)
    # 7 h

    tsBuilder = TimeseriesBuilder(start=start, end=None)
    #tsBuilder.build(infolder=folder3b, outfolder=folder4, inextension='.tif', footprints=mgrsFootprints, processes=50)
    # 24 min

    variables = ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'ndvi', 'nbr', 'msavi2', 'tcg', 'tcb', 'tcw']
    percentiles = [0, 5, 25, 50, 75, 95, 100]
    mean = True
    stddev = True
    applier = StatisticsApplier(infolder=folder4, outfolder=folder5, of='GTiff', footprints=mgrsFootprints, inextension='.vrt',
                                percentiles=percentiles, variables=variables, mean=mean, stddev=stddev)
    # timeperiods dry
    for year in range(1985, 2016 + 1):
        start = Date.fromYearDoy(year, 140)
        end = Date.fromYearDoy(year, 263)
        bufferYears = 0
        applier.appendDateParameters(date1=start, date2=end, bufferYears=bufferYears)

    # timeperiods wet
    for year in range(1988, 2013 + 1, 5):
        start = Date.fromYearDoy(year, 293)
        end = Date.fromYearDoy(year + 1, 90)
        bufferYears = 2
        applier.appendDateParameters(date1=start, date2=end, bufferYears=bufferYears)

    applier.controls.setWindowXsize(256)
    applier.controls.setWindowYsize(256)
    #applier.controls.setNumThreads(10)
    applier.apply()


if __name__ == '__main__':

    from osgeo import gdal
    gdal.SetCacheMax(10) # MB

    tic()
    test(26)
    import gdal

    print('cacheMax:', gdal.GetCacheMax()/1024/1024/1024)
    print('cacheUsed:', gdal.GetCacheUsed())
    print('cacheUsed/Max[%]:',100.*gdal.GetCacheUsed()/gdal.GetCacheMax())

    toc()

    if 0:
        for year in range(1985, 2016+1):
            start = Date.fromYearDoy(year, 140)
            end = Date.fromYearDoy(year, 263)
            buffer = 1
            #print(str(start), 'to', str(end), 'buffer='+str(buffer))

        for year in range(1988, 2013+1, 5):
            start = Date.fromYearDoy(year, 293)
            end = Date.fromYearDoy(year+1, 90)
            buffer = 2
            print(str(start), 'to', str(end), 'buffer=' + str(buffer))


