from __future__ import print_function
from lamos.types import MGRSTilingScheme, MGRSFootprint, MGRSArchive
from lamos.operators.dummy import DummyReadApplier
from hub.timing import tic, toc
import os

def test_read_ts_tif():
    infolder = r'c:\work\data\gms\landsatTimeseriesMGRS_SavedAsGTiff'
    mgrsFootprints = ['33UTT']
    applier = DummyReadApplier(infolder=infolder, inextension='.img', footprints=mgrsFootprints)
    applier.controls.setWindowXsize(10000)
    applier.controls.setWindowYsize(10)
    applier.controls.setNumThreads(40)
    applier.apply()

def test_read_ts_vrt():
    infolder = r'c:\work\data\gms\landsatTimeseriesMGRS'
    mgrsFootprints = ['33UTT']
    applier = DummyReadApplier(infolder=infolder, inextension='.vrt', footprints=mgrsFootprints)
    applier.controls.setWindowXsize(10000)
    applier.controls.setWindowYsize(100)
    applier.controls.setNumThreads(5)
    applier.apply()

def test_read_ts_vrt2():
    infolder = r'c:\work\data\gms\landsatTimeseriesMGRS'
    infolder2 = r'c:\work\data\gms\landsatTimeseriesMGRS_SavedAsGTiff'

    mgrsFootprints = ['33UTT']

    # save as GTiff frist
    archive = MGRSArchive(infolder)
    archive.saveAsGTiff(outfolder=infolder2, filter=mgrsFootprints)

    # read GTiffs
    applier = DummyReadApplier(infolder=infolder2, inextension='.img', footprints=mgrsFootprints)
    applier.controls.setWindowXsize(10000)
    applier.controls.setWindowYsize(100)
    applier.controls.setNumThreads(40)

    applier.apply()


def test():
    archive = MGRSArchive(r'c:\work\data\gms\landsatTimeseriesMGRS')
    # archive = MGRSArchive(r'c:\work\data\gms\landsatXMGRS')
    mgrsFootprints = ['33UTT']
    for interleave in ['BAND', 'PIXEL']:
        for compress in ['DEFLATE', 'LZW']:
            for predictor in ['1', '2']:
                outfolder = archive.folder + '_' + interleave + '_' + compress + predictor
                print(outfolder)
                if not os.path.exists(outfolder):
                    archive.saveAsGTiff(outfolder=outfolder, filter=mgrsFootprints,
                                        compress=compress, interleave=interleave, predictor=predictor)

                applier = DummyReadApplier(infolder=outfolder, inextension='.img', footprints=mgrsFootprints)
                applier.controls.setWindowXsize(10000)
                applier.controls.setWindowYsize(100)
                applier.apply()


if __name__ == '__main__':

    MGRSFootprint.shpRoot = r'C:\Work\data\gms\gis\MGRS_100km_1MIL_Files'
    MGRSTilingScheme.shp = r'C:\Work\data\gms\gis\MGRS-WRS2_Tiling_Scheme\MGRS-WRS2_Tiling_Scheme.shp'

    tic()
    #test()
    test_read_ts_tif()    # 1s
    #test_read_ts_vrt()   # 100 lines -> 166s, 165s       all -> 69s, 69
                        # 100*40 lines -> 167s
                        # 100*5 lines -> 164s

    #test_read_ts_vrt2()  # 100 lines -> 87s, 86s         all -> 86s
                            # 100*40 lines -> 87s

    toc()
