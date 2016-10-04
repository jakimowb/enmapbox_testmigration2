from __future__ import print_function

import os

from hub.timing import tic, toc
from lamos.operators.dummy import DummyReadApplier
from lamos.processing.types import MGRSTilingScheme, MGRSFootprint, MGRSArchive


def test():
    folder1 = r'c:\work\data\gms\landsatTimeseriesMGRS'
    folder2 = r'c:\work\data\gms\landsatTimeseriesMGRS_GTiff'
    folder3 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4ad\landsatTimeseriesMGRS'
    folder4 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4ad\landsatTimeseriesMGRS_GTiff'

    applier = DummyReadApplier(infolder=folder3, inextension='.vrt', footprints='41ULS')
    #applier = DummyReadApplier(infolder=folder4, inextension='.img', footprints='41ULS')
    applier.controls.setWindowXsize(256*100)
    applier.controls.setWindowYsize(256)
    applier.controls.setNumThreads(1000)
    applier.apply()

def test_gdal_read():
    folder1 = r'c:\work\data\gms\landsatTimeseriesMGRS'
    folder2 = r'c:\work\data\gms\landsatTimeseriesMGRS_GTiff'
    from hub.file import filesearch
    from hub.gdal.api import readCube
    files = filesearch(folder1, '*.vrt')
    for file in files:
        print(file)
        print(readCube(file).shape)

def test_saveAs():
    folder1 = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4ad\landsatTimeseriesMGRS_Test'
    folder2a = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4ad\landsatTimeseriesMGRS_TestENVI5000'

    MGRSArchive(folder1).saveAsENVI(folder2a, filter='41ULS')


if __name__ == '__main__':

    MGRSFootprint.shpRoot = r'C:\Work\data\gms\gis\MGRS_100km_1MIL_Files'
    MGRSTilingScheme.shp = r'C:\Work\data\gms\gis\MGRS-WRS2_Tiling_Scheme\MGRS-WRS2_Tiling_Scheme.shp'
    MGRSFootprint.shpRoot = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gis\reference_systems\mgrs\MGRS_100km_1MIL_Files'
    MGRSTilingScheme.shp = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gis\reference_systems\mgrs\MGRS-WRS2_Tiling_Scheme\MGRS-WRS2_Tiling_Scheme.shp'

    #gdal.SetConfigOption('GDAL_CACHE_MAX', '10')

    MB = 8 * 1024 * 1024
    GB = MB * 1024
    os.environ['GDAL_CACHEMAX'] = '5000'

    tic()
    #gdal.SetCacheMax(5*GB)
    #print(gdal.GetCacheMax()/MB)
    test_saveAs()
    toc()


# saveAs 5000MB:

# dims = 3353 x 3353 x 237 [byte]
# interleave = bsq

# CFMASK
# VRT all x all:               139 sec, 117 sec, 117 sec
# VRT 256 x 256:               942 sec
# VRT 256 x 256 x 10 Threads:  960 sec


# BSQ uncompressed:        40, 39, 42 sec
# BSQ 256 x 256:          41, 38, 36 sec

