from __future__ import division
from lamos.types import SensorXComposer, Product, Image, ImageStack, WRS2Archive, MGRSArchive, Archive, MGRSTilingScheme
from lamos.workflows.landsat_homogenization import LandsatXComposer, TimeseriesBuilder
from hub.timing import tic, toc

def test():

    landsatFolder = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\landsat'
    landsatXFolder = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\dirk_landsatX'
    wrs2Footprints = ['193024']
    mgrsFootprints = ['32UPB']

    landsatArchive = WRS2Archive(landsatFolder, filterFootprints=wrs2Footprints)
    composer = LandsatXComposer()
    lsXArchive = composer.composeArchive(archive=landsatArchive,
                                         folder=landsatXFolder,
                                         footprints=wrs2Footprints)
    lsXArchive.info()


def test_tiling():

    lsXWRS2Archive = WRS2Archive(r'C:\Work\data\gms\landsatX')
    tilingScheme = MGRSTilingScheme(pixelSize=30)
    lsXMGRSArchive = tilingScheme.tileWRS2Archive(archive=lsXWRS2Archive,
                                                  folder=r'c:\work\data\gms\landsatXMGRS',
                                                  buffer=300,
                                                  wrs2Footprints=['193024'], mgrsFootprints=['32UPB', '32UPC'])
    lsXMGRSArchive.info()


def test_buildTimeseries():

    lsXMGRSArchive = MGRSArchive(r'c:\work\data\gms\landsatXMGRS')
    tsBuilder = TimeseriesBuilder(names=['blue', 'green', 'red', 'nir', 'swir1', 'swir2'],
                                  bands=[1,2,3,4,5,6])
    lstsMGRSArchive = tsBuilder.buildArchive(lsXMGRSArchive, r'c:\work\data\gms\landsatTimeseriesMGRS', envi=False,
                                             footprints=['32UPB'])
    lstsMGRSArchive.info()


if __name__ == '__main__':

    tic()
    test()
    toc()
