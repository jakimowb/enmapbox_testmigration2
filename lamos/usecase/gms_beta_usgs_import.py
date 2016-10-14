import sys
sys.path.append(r'C:\Work\source\QGISPlugIns\enmap-box')
sys.path.append(r'C:\Work\source\site-packages')


import os
import argparse
from lamos.processing.types import MGRSTilingScheme, WRS2Footprint, MGRSFootprint, MGRSArchive
from lamos.operators.landsat_x import LandsatXComposer
from hub.timing import tic, toc

def run(infolder, outfolder, tmpfolder, processes):

    # path to shapefiles with WRS2 and MGRS Geometries
    MGRSFootprint.shpRoot = r'C:\Work\data\gms\gis\MGRS_100km_1MIL_Files'
    MGRSTilingScheme.shp = r'C:\Work\data\gms\gis\MGRS-WRS2_Tiling_Scheme\MGRS-WRS2_Tiling_Scheme.shp'

    # in/out folders
    folder1 = infolder
    folder2 = os.path.join(tmpfolder, 'landsatX_VRT')
    folder3 = os.path.join(tmpfolder, 'landsatXMGRS_VRT')
    folder4 = outfolder

    # find UTM zone for each WRS2 footprint in the given archive
    WRS2Footprint.createUtmLookup(infolder=folder1)

    # define which footprints to use
    wrs2Footprints = ['193024','194024']
    mgrsFootprints = ['32UPC','32UQC','33UTT','33UUT']

    # create sensor x products
    composer = LandsatXComposer()
    composer.composeWRS2Archive(infolder=folder1, outfolder=folder2, footprints=wrs2Footprints, processes=processes)

    # cut sensor x products
    tilingScheme = MGRSTilingScheme(pixelSize=30)
    tilingScheme.tileWRS2Archive(infolder=folder2, outfolder=folder3, buffer=300, wrs2Footprints=wrs2Footprints, mgrsFootprints=mgrsFootprints, processes=processes)

    # save as ENVI
    MGRSArchive(folder3).saveAsENVI(folder4, processes=processes)

if __name__ == '__main__':

    try:
        infolder, outfolder, tmpfolder, processes = sys.argv
    except:
        infolder = r'C:\Work\data\gms\landsat'
        outfolder = r'C:\Work\data\gms\landsatXMGRS_ENVI'
        tmpfolder = r'C:\Work\data\gms\tmp'
        processes=10

    tic()
    run(infolder=infolder, outfolder=outfolder, tmpfolder=tmpfolder, processes=processes)
    toc()
