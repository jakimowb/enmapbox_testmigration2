from __future__ import print_function
from lamos.types import MGRSTilingScheme, MGRSFootprint, MGRSArchive
from lamos.operators.dummy import DummyReadApplier
from hub.timing import tic, toc
import os, gdal

def test():
    folder1 = r'c:\work\data\gms\landsatTimeseriesMGRS'
    folder2 = r'c:\work\data\gms\landsatTimeseriesMGRS_GTiff'

    applier = DummyReadApplier(infolder=folder1, inextension='.vrt', footprints='33UUT')
    #applier = DummyReadApplier(infolder=folder2, inextension='.img')
    applier.controls.setWindowXsize(256)
    applier.controls.setWindowYsize(256)
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




if __name__ == '__main__':

    MGRSFootprint.shpRoot = r'C:\Work\data\gms\gis\MGRS_100km_1MIL_Files'
    MGRSTilingScheme.shp = r'C:\Work\data\gms\gis\MGRS-WRS2_Tiling_Scheme\MGRS-WRS2_Tiling_Scheme.shp'
    #gdal.SetConfigOption('GDAL_CACHE_MAX', '10')

    MB = 8 * 1024 * 1024
    GB = MB * 1024


    tic()
    #test_gdal_read()
    toc()

    tic()
    gdal.SetCacheMax(64*MB)
    print(gdal.GetCacheMax()/MB)
    test()
    toc()
    raise '1'
    tic()
    gdal.SetCacheMax(5*GB)
    print(gdal.GetCacheMax()/MB)
    test()
    toc()

    tic()
    gdal.SetCacheMax(1*GB)
    print(gdal.GetCacheMax()/MB)
    test()
    toc()

    tic()
    gdal.SetCacheMax(512*MB)
    print(gdal.GetCacheMax()/MB)
    test()
    toc()

    tic()
    gdal.SetCacheMax(256 * MB)
    print(gdal.GetCacheMax()/MB)
    test()
    toc()

    tic()
    gdal.SetCacheMax(128 * MB)
    print(gdal.GetCacheMax()/MB)
    test()
    toc()

