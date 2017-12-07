# -*- coding: utf-8 -*-
"""
***************************************************************************
    gcpexample
    ---------------------
    Date                 : November 2017
    Copyright            : (C) 2017 by Benjamin Jakimow
    Email                : benjamin.jakimow@geo.hu-berlin.de
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
# noinspection PyPep8Naming
from __future__ import unicode_literals, absolute_import
import re
import numpy as np


from osgeo import gdal, osr, gdalconst
pathSrc = r'T:\ao\georef\EnMAP_RGB_53su.bsq'
pathRef = r'T:\ao\georef\Landsat_RGB_BA.bsq'
pathDst = r'T:\ao\georef\transformedBJ-13.bsq'
pathGCP = r'T:\ao\georef\gcps\BA53.csv'
noDataDst = None

dsSrc = gdal.Open(pathSrc)
assert isinstance(dsSrc, gdal.Dataset)


#rotation
theta = np.radians(29)
c,s = np.cos(theta), np.sin(theta)
R = np.matrix([[c,-s],[s,c]])
S = R.transpose()

px = lambda x,y:np.asarray([x,y]).reshape(2,1)
pr = lambda px : '{},{}'.format(px[0,0], px[1,0])
#example
a = px(2003,3207)
b = px(0,0)

print('unrotated    ' + pr(a))
print('rotated      ' + pr(R*a))
print('rotated-back ' + pr(S*R*a))

ul = px(0,0)
ur = px(0, dsSrc.RasterXSize)
ll = px(dsSrc.RasterYSize*-1, 0)
lr = px(dsSrc.RasterYSize*-1, dsSrc.RasterXSize)
_ul = R*ul
_ur = R*ur
_ll = R*ll
_lr = R*lr

_data = np.hstack([_ul,_ur,_ll,_lr])
_ns = _data[0,:].max() - _data[0,:].min()
_nl = _data[1,:].max() - _data[1,:].min()
yshift = _data[1,1]
yshift = 204

s =""


#1. read the GCPs
lines = open(pathGCP).readlines()
lines = [l.strip() for l in lines] #remove whitespaces

# remove lines different to format
# mapX,mapY,pixelX,pixelY,enable
# 504085.5423,4312668.982,503904.1062,4308823.177,1
# GCP(x=0.0, y=0.0, z=0.0, pixel=0.0, line=0.0, info, id)
lines = [l for l in lines if re.search('^\d.*', l)]
gcps = []


for i, line in enumerate(lines):
    line = re.split('[,;]', line)
    lines = [l.strip() for l in lines]

    mapX, mapY, mapZ, pixelXrot, pixelYrot = [float(n) if n != '' else 0
                                        for n in line]

    pixelYrot -= yshift
    pxOrig = S * np.asarray([pixelXrot,-1 * pixelYrot]).reshape(2,1)
    pixelX = float(pxOrig[0,0])
    pixelY = float(pxOrig[1,0]) * -1

    gcp = gdal.GCP(mapX, mapY, mapZ, pixelX, pixelY,
                   str('info'), str('id{}'.format(i)))
    gcps.append(gcp)

#2. set GCPs to source dataset
srsGCP = osr.SpatialReference()
srsGCP.ImportFromEPSG(32610)
dsSrc.SetGCPs(gcps, srsGCP.ExportToWkt())


if False:
    drv = dsSrc.GetDriver()
    assert isinstance(drv, gdal.Driver)
    gt = gdal.GCPsToGeoTransform(gcps)
    to = gdal.TranslateOptions(format=dsSrc.GetDriver().ShortName)
    dsDst = gdal.Translate(pathDst, pathSrc, options=to)
    assert isinstance(dsDst, gdal.Dataset)


    dsDst.SetGCPs([], None)
    dsDst.SetGeoTransform(gt)
    dsDst.SetProjection(dsSrc.GetProjection())
    dsDst.FlushCache()
    dsDst = None
    exit()
#gdal.GCPsToGeoTransform(gcps)


#3. Create the empty target dataset dsDst
drvDst = gdal.GetDriverByName(str('ENVI'))

dsRef = gdal.Open(pathRef) #the reference file
assert isinstance(dsRef, gdal.Dataset)
assert isinstance(drvDst, gdal.Driver)
dsDst = drvDst.Create(pathDst,
                      dsRef.RasterXSize, dsRef.RasterYSize,
                      bands=dsSrc.RasterCount, #use the source file's number of bands and data type
                      eType=dsSrc.GetRasterBand(1).DataType
                      )

if noDataDst is None:
    noDataDst = dsSrc.GetRasterBand(1).GetNoDataValue()

assert isinstance(dsDst, gdal.Dataset)
dsDst.SetProjection(dsRef.GetProjection())
dsDst.SetGeoTransform(dsRef.GetGeoTransform())

#copy band-metadata and
for b in range(dsSrc.RasterCount):
    bandSrc = dsSrc.GetRasterBand(b+1)
    bandDst = dsDst.GetRasterBand(b+1)
    assert isinstance(bandSrc, gdal.Band)
    assert isinstance(bandDst, gdal.Band)
    for domain in bandSrc.GetMetadataDomainList():
        bandDst.SetMetadata(bandSrc.GetMetadata(domain), domain)

#3. Warp

def warpCallback(progress, msg, data ):
    print('{:0.2f}% ...'.format(progress*100))
    s  =""

if False:
    to = None# ['GCPS_OK=TRUE'] #[]
    wo = None#['INIT_DEST=-1']
    warpOptions = gdal.WarpOptions(
             resampleAlg = gdalconst.GRA_NearestNeighbour,
             srcSRS=srsGCP.ExportToWkt(),
             dstSRS=dsDst.GetProjection(),
             srcNodata = None, dstNodata = noDataDst, multithread = False,
             tps = False,
             rpc = False, geoloc = False,
             polynomialOrder = 3,
             warpOptions=wo,
             transformerOptions = to,
             callback=warpCallback
             )

    gdal.Warp(dsDst, dsSrc, options=warpOptions)
else:
    to = None  # ['GCPS_OK=TRUE'] #[]
    wo = None  # ['INIT_DEST=-1']
    warpOptions = gdal.WarpOptions(
        resampleAlg=gdalconst.GRA_NearestNeighbour,
        srcSRS=srsGCP.ExportToWkt(),
        dstSRS=dsDst.GetProjection(),
        srcNodata=None, dstNodata=noDataDst, multithread=False,
        tps=False,
        rpc=False, geoloc=False,
        polynomialOrder=2,
        warpOptions=wo,
        transformerOptions=to,
        callback=warpCallback
    )
    gdal.Warp(pathDst, dsSrc, options=warpOptions)

dsNew = gdal.Open(str(pathDst))
assert isinstance(dsNew, gdal.Dataset)
band = dsNew.GetRasterBand(1)
assert isinstance(band, gdal.Band)
arr = band.ReadAsArray()
print((arr.min(), arr.max()))
s = ""
print('Warping finished')