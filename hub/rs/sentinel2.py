__author__ = 'janzandr'
import glob
import os
import xml.etree.ElementTree as ET

import numpy
from hub.timing import *

import emb.hub.gdal.util


def importL1C(outfile, infolder, epsg):

    # parse XML
    xmlfile = glob.glob(infolder+'\S2A*.xml')[0]
 #   source = open(xmlfile, "rb")

    tree = ET.parse(xmlfile)
    root = tree.getroot()
    bnames =  numpy.array([elem.text for elem in root.iter('BAND_NAME')])
    bnames2 = numpy.array([bname if len(bname) == 3 else 'B0'+bname[-1] for bname in bnames]) # fix bnames to length of 3
#    wl = numpy.array([elem.text for elem in root.iter('CENTRAL')])
#    resolutions = numpy.array([elem.text for elem in root.iter('RESOLUTION')])
    resolutions = numpy.array([60, 10, 10, 10, 20, 20, 20, 10, 20, 60, 60, 20, 20])

    # create single band mosaick VRTs
    outfilesSingle = []
    for bname in bnames2:

        # find all jp2 files for the band
        jp2files = emb.hub.file.filesearch(os.path.join(infolder, 'GRANULE'), '*' + bname + '.jp2')

        # warp all granuals to single projection
        tmpfolder = os.path.join(os.path.dirname(outfile), 'tmp')
        warpedjp2files = [os.path.join(tmpfolder, os.path.basename(jp2file)).replace('.jp2', '.vrt') for jp2file in jp2files]
        for jp2file, warpedjp2file in zip(jp2files,warpedjp2files):
            emb.hub.gdal.util.gdalwarp(warpedjp2file, jp2file, '-of VRT -overwrite -wm 2000 -s_srs epsg:' + str(epsg))

        outfileSingle = outfile+'_'+bname+'.vrt'

        emb.hub.gdal.util.mosaic(outfileSingle, warpedjp2files)
#        hub.envi.vrt2mos(outfileSingle)
        outfilesSingle.append(outfileSingle)

    # create multi band stack for each resolution
    for targetResolution in [10,20]: #[10,20,60]:
        invrts = numpy.array(outfilesSingle)[resolutions == targetResolution]
        outvrt = outfile+'_'+str(targetResolution)+'m.vrt'
        outenvi = outfile+'_'+str(targetResolution)+'m.img'
        emb.hub.gdal.util.gdalbuildvrt(outvrt, invrts, '-separate')
        emb.hub.gdal.util.gdal_translate(outenvi, outvrt, '-of ENVI')
#        hub.gdal.util.gdalwarp(outenvi, outvrt, '-of ENVI  -overwrite -wm 2000')


    return

    # create multi band stack with all bands for 30m resolution
#    invrts = outfilesSingle
#    outvrt = outfile+'_30m_resampled.vrt'
#    outenvi = outfile+'_30m.img'
#    hub.gdal.util.gdalbuildvrt(outvrt, invrts, '-separate')
#    hub.gdal.util.gdal_translate(outenvi, outvrt, '-of ENVI -tr 30 30 -r average -srcwin 3000 3000 500 500')
#    hub.gdal.util.gdalwarp(outenvi, outvrt, '-of ENVI -tr 30 30 -r near -overwrite -wm 2000')

if __name__ == '__main__':

    jp2dir = r'h:\s2\jp2'
    envidir = r'h:\s2\envi'

    indirnames = os.listdir(jp2dir)
    infolders  = [os.path.join(jp2dir,  indirname) for indirname in indirnames]
    outfolders = [os.path.join(envidir, indirname) for indirname in indirnames]
    epsg = '32633'

    for infolder, outfolder in zip(infolders, outfolders):
        tic()
        outfile = os.path.join(outfolder, 'vrt')
        importL1C(outfile, infolder, epsg)
        toc()

