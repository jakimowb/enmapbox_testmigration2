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
import re, os
import numpy as np


from osgeo import gdal, osr, gdalconst, ogr

jp = os.path.join

dirRoot = r'S:\temp\temp_akpona\bj_clean'
pathSrc = jp(dirRoot, 'BA59su_RGB')
pathRot = jp(dirRoot, 'BA59_rot')
#pathRot = jp(dirRoot, 'BA59_rot.noSRS.bsq')
pathRef = jp(dirRoot, r'Landsat_RGB.bsq')
pathShp = jp(dirRoot, *['vector','masked_tiepoints.shp'])

dirDst = jp(dirRoot, 'BJ_OUTPUTS')
if not os.path.isdir(dirDst):
    os.mkdir(dirDst)
pathDst = jp(dirDst, 'output.bj.bsq')
pathGCP = jp(dirDst, 'gcps.bj.points')
pathGCPShape = jp(dirDst, 'gcps.bj.shp')
noDataDst = None
resampleAlg = gdalconst.GRA_Cubic

for p in [pathSrc, pathRef, pathRot]:
    assert os.path.exists(p)

dsRef = gdal.Open(pathRef)
assert isinstance(dsRef, gdal.Dataset)
srs = osr.SpatialReference()
assert isinstance(srs, osr.SpatialReference)
srs.ImportFromWkt(dsRef.GetProjection())

#
#definition of helper functions
#
def rotationMatrix(a):
    theta = np.radians(a)
    c,s = np.cos(theta), np.sin(theta)
    return np.matrix([[c,-s],[s,c]]) #rotation matrix to rotate from original image to rotated image


def rotateImageVirtually(pathSrc, pathDst, ang, format='VRT'):
    """
    Rotates an image by angle ang
    :param pathSrc:
    :param pathDst:
    :param ang:
    :param format:
    :return:
    """

    #https://gis.stackexchange.com/questions/229952/rotate-envi-hyperspectral-imagery-with-gdal/229962
    assert pathSrc != pathDst
    opt = gdal.TranslateOptions(
        format=format
    )
    dsDst = gdal.Translate(pathDst, pathSrc, options=opt)
    assert isinstance(dsDst, gdal.Dataset)

    rad = np.radians(ang)

    gt = dsDst.GetGeoTransform()
    gt_rot = [gt[0],
              np.cos(rad)*gt[1],
              -1* np.sin(rad) * gt[1],
              gt[3],
              np.sin(rad) * gt[5],
              np.cos(rad) * gt[5]
              ]
    dsDst.SetGeoTransform(gt_rot)

    return dsDst



def geo2px(x,y, gt):
    # see http://www.gdal.org/gdal_datamodel.html
    px = (x - gt[0]) / gt[1]  # x pixel
    py = (y - gt[3]) / gt[5]  # y pixel
    return px, py


def px2geo(x,y, gt):
    """
    Converts a pixel coordinate into a geo-coordinate
    :param x: pixel position x
    :param y: pixel position x
    :param gt: geo-transformation array, as derived from gdal.Dataset.GetGeoTransform()
    :return: geo_x, geo_y
    """

    #see http://www.gdal.org/gdal_datamodel.html
    gx = gt[0] + x * gt[1] + y * gt[2]
    gy = gt[3] + x * gt[4] + y * gt[5]
    return gx, gy

#convert GCP list to QGIS GCP list
def gcpsFromShp(pathShp, pathSrc):
    dsSrc = gdal.Open(pathSrc)
    dsShp = ogr.Open(pathShp)
    assert isinstance(dsSrc, gdal.Dataset)

    gt = dsSrc.GetGeoTransform()


    assert isinstance(dsShp, ogr.DataSource)
    lyr = dsShp.GetLayer(0)
    assert isinstance(lyr, ogr.Layer)
    ldef = lyr.GetLayerDefn()
    assert isinstance(ldef, ogr.FeatureDefn)

    for i in range(ldef.GetFieldCount()):
        fdef = ldef.GetFieldDefn(i)
        assert isinstance(fdef, ogr.FieldDefn)
        print(fdef.GetName(), fdef.GetTypeName())

    gcps = []


    for feature in lyr:
        assert isinstance(feature, ogr.Feature)
        fid = feature.GetFID()
        pid = feature.GetFieldAsInteger64(str('POINT_ID'))

        #image pixel
        px_x = feature.GetFieldAsInteger64(str('X_IM'))
        px_y = feature.GetFieldAsInteger64(str('Y_IM'))

        #convert the image pixel coordinate into the image projection system

        src_x, src_y = px2geo(px_x, px_y, gt)

        #UTM coordinate
        geo_x = feature.GetFieldAsDouble(str('X_UTM'))
        geo_y = feature.GetFieldAsDouble(str('Y_UTM'))

        pt_x = feature.GetGeometryRef().GetX()
        pt_y = feature.GetGeometryRef().GetY()
        #geo_x = pt_x
        #geo_y = pt_y


        #utm shifts
        shift_x_m = 0
        shift_y_m = 0
        shift_x_px = feature.GetFieldAsDouble(str('X_SHIFT_PX'))
        shift_y_px = feature.GetFieldAsDouble(str('Y_SHIFT_PX'))
        if True:
            shift_x_m = feature.GetFieldAsDouble(str('X_SHIFT_M'))
            shift_y_m = feature.GetFieldAsDouble(str('Y_SHIFT_M'))

        #pt_x = feature.GetGeometryRef().GetX()
        #pt_y = feature.GetGeometryRef().GetY()

        gcp = gdal.GCP()
        gcp.GCPX = geo_x + shift_x_m
        gcp.GCPY = geo_y + shift_y_m
        gcp.GCPZ = 0

        gcp.GCPPixel = src_x
        gcp.GCPLine  = src_y


        gcps.append(gcp)
    s = ""
    return gcps

def gcpsToShapefile(gcps, pathShp, srs):
    if not isinstance(srs, osr.SpatialReference):
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(srs)
    assert isinstance(srs, osr.SpatialReference)

    drv = ogr.GetDriverByName(str('Memory'))
    assert isinstance(drv, ogr.Driver)

    ds = drv.CreateDataSource(str(''))
    assert isinstance(ds, ogr.DataSource)

    lyr = ds.CreateLayer(str('gcps'), srs=srs, geom_type=ogr.wkbPoint)
    assert isinstance(lyr, ogr.Layer)
    lyr.CreateField(ogr.FieldDefn(str('id'), ogr.OFTString))
    lyr.CreateField(ogr.FieldDefn(str('geo_x'), ogr.OFTReal))
    lyr.CreateField(ogr.FieldDefn(str('geo_y'), ogr.OFTReal))
    lyr.CreateField(ogr.FieldDefn(str('geo_z'), ogr.OFTReal))
    lyr.CreateField(ogr.FieldDefn(str('px_x'), ogr.OFTReal))
    lyr.CreateField(ogr.FieldDefn(str('px_y'), ogr.OFTReal))
    lyr.CreateField(ogr.FieldDefn(str('info'), ogr.OFTString))
    for gcp in gcps:
        assert isinstance(gcp, gdal.GCP)

        feature = ogr.Feature(lyr.GetLayerDefn())
        assert isinstance(feature, ogr.Feature)
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(gcp.GCPX, gcp.GCPY)

        feature.SetGeometry(point)
        feature.SetField(str('id'), gcp.Id)
        feature.SetField(str('info'), gcp.Id)
        feature.SetField(str('geo_x'), gcp.GCPX)
        feature.SetField(str('geo_y'), gcp.GCPY)
        feature.SetField(str('geo_z'), gcp.GCPZ)
        feature.SetField(str('px_x'), gcp.GCPPixel)
        feature.SetField(str('px_y'), gcp.GCPLine)
        lyr.CreateFeature(feature)

    #save to shapefile

    drvShp = ogr.GetDriverByName(str('ESRI Shapefile'))
    assert isinstance(drvShp, ogr.Driver)
    drvShp.CopyDataSource(ds, pathShp)


def gcpsToQGISgcpslist(gcps, path):
    """
    Writes a list og gdal GCPS as QGIS points file
    :param gcps:
    :param path:
    :return:
    """
    lines = ["mapX,mapY,pixelX,pixelY,enable"]
    for gcp in gcps:
        assert isinstance(gcp, gdal.GCP)



        lines.append(','.join(['{:0.17f}'.format(v) for v in [gcp.GCPX, gcp.GCPY, gcp.GCPPixel, gcp.GCPLine]]+['1']))

    open(path, 'w').writelines('\n'.join(lines))




def copyImage(pathSrc, pathDst, format='VRT'):

    dsSrc = gdal.Open(pathSrc)
    assert isinstance(dsSrc, gdal.Dataset)

    opt = gdal.TranslateOptions(format=format, outputSRS=dsSrc.GetProjection())
    dsDst = gdal.Translate(pathDst, dsSrc, options=opt)
    dsDst.SetProjection(dsSrc.GetProjection())
    assert isinstance(dsDst, gdal.Dataset)

    if False:
        for domain in dsSrc.GetMetadataDomainList():
            dsDst.SetMetadata(dsSrc.GetMetadata(domain), domain)

    if False:
        for b in range(dsSrc.RasterCount):
            srcBand = dsSrc.GetRasterBand(b+1)
            dstBand = dsDst.GetRasterBand(b+1)
            assert isinstance(srcBand, gdal.Band)
            assert isinstance(dstBand, gdal.Band)
            for domain in srcBand.GetMetadataDomainList():
                dstBand.SetMetadata(srcBand.GetMetadata(domain), domain)


    return dsDst
#
#
#

def correctImage(pathSrc, pathRef, pathDst, gcps, noDataDst=None):
    drvDst = gdal.GetDriverByName(str('ENVI'))


    pathTmp = pathDst + '.temp.src.tif'
    dsSrc = copyImage(pathSrc, pathTmp, format='GTiff')
    wkt = dsSrc.GetProjection()
    gcps2 = []
    gt = dsSrc.GetGeoTransform()
    for gcp in gcps:
        gcp2 = gdal.GCP()
        gcp2.GCPX = gcp.GCPX
        gcp2.GCPY = gcp.GCPY
        gcp2.GCPZ = gcp.GCPZ

        gcp2.GCPPixel, gcp2.GCPLine = geo2px(gcp.GCPPixel, gcp.GCPLine, gt)
        gcps2.append(gcp2)

    gcps = gcps2

    dsSrc.SetGCPs(gcps, wkt)
    dsSrc.FlushCache()

    #dsSrc = gdal.Open(pathSrc)
    dsRef = gdal.Open(pathRef)  # the reference file
    assert isinstance(dsSrc, gdal.Dataset)
    assert isinstance(dsRef, gdal.Dataset)
    assert isinstance(drvDst, gdal.Driver)

    # set the source file GCPs + Projection
    # gcp_srs_wkt = dsRef.GetProjection()
    # dsSrc.SetProjection(dsRef.GetProjection())
    dsDst = drvDst.Create(pathDst,
                          dsRef.RasterXSize, dsRef.RasterYSize,
                          bands=dsSrc.RasterCount,  # use the source file's number of bands and data type
                          eType=dsSrc.GetRasterBand(1).DataType
                          )

    assert isinstance(dsDst, gdal.Dataset)
    # if noDataDst is None:
    #    noDataDst = dsSrc.GetRasterBand(1).GetNoDataValue()
    dsDst.SetProjection(dsRef.GetProjection())
    dsDst.SetGeoTransform(dsRef.GetGeoTransform())

    # copy band-metadata and
    for b in range(dsSrc.RasterCount):
        bandSrc = dsSrc.GetRasterBand(b + 1)
        bandDst = dsDst.GetRasterBand(b + 1)
        assert isinstance(bandSrc, gdal.Band)
        assert isinstance(bandDst, gdal.Band)
        for domain in bandSrc.GetMetadataDomainList():
            bandDst.SetMetadata(bandSrc.GetMetadata(domain), domain)

    def warpCallback(progress, msg, data):
        print('{:0.2f}% ...'.format(progress * 100))
        s = ""

    to = None  # ['GCPS_OK=TRUE'] #[]
    wo = None  # ['INIT_DEST=-1']
    warpOptions = gdal.WarpOptions(
        resampleAlg=resampleAlg,
       # srcSRS=gcp_srs_wkt,
        dstSRS=dsDst.GetProjection(),
        srcNodata=None, dstNodata=noDataDst, multithread=False,
        tps=False,
        rpc=False, geoloc=False,
        polynomialOrder=3,
        warpOptions=wo,
        transformerOptions=to,
        callback=warpCallback
    )
    gdal.Warp(dsDst, dsSrc, options=warpOptions)

    dsNew = gdal.Open(str(pathDst))
    assert isinstance(dsNew, gdal.Dataset)
    print('Warping finished')


#read the shifted GCPS (=the corrected ones) from the ACOSICS shapefile

pathRotBack = jp(dirRoot, 'rotback.vrt')
rotateImageVirtually(pathRot, pathRotBack, 29)

gcps = gcpsFromShp(pathShp, pathRot)
#write the shifted gcps as shapefile (for control)
gcpsToQGISgcpslist(gcps, pathGCP)
#write the shifted gcps as shapefile (for control)
gcpsToShapefile(gcps, pathGCPShape, srs)

#do the georeferencation
correctImage(pathRot, pathRef, pathDst,gcps, noDataDst=None)

#rotateImageVirtually(pathSrc, pathRotBJ, -29)
s  =""






exit()


#read the rotation image info
dsRot = gdal.Open(pathRot)
assert isinstance(dsRot, gdal.Dataset)


hdr = ''.join(open([f for f in dsRot.GetFileList() if f.endswith('.hdr')][0]).readlines())

#read the rotation angle
rotAngle = float(re.search('(?<=Angle:).*(?= degrees)', hdr).group())
rotAngle = -180.0
mapinfo = re.search('(?<={UTM, ).*(?= North)', hdr).group().split(',')
mapinfo = [float(v) for v in mapinfo if len(v) > 0]

xshift = mapinfo[0]
yshift = mapinfo[1]


#rotation


#returns a coordinate x, y as numpy vector
px = lambda x,y:np.asarray([x,y]).reshape(2,1)
#returns a numpy vector coordinate as string
pr = lambda px : '{},{}'.format(px[0,0], px[1,0])

if False:
    #example how to the rotation is performed
    a = px(418,0)
    #a = px(0,0)

    print('unrotated    ' + pr(a))
    print('rotated      ' + pr(R*a))
    print('rotated-back ' + pr(S*R*a))

    exit()



#1. read the GCPs
lines = open(pathGCP).readlines()
lines = [l.strip() for l in lines] #remove whitespaces

# remove lines different to format
# mapX,mapY,pixelX,pixelY,enable
# 504085.5423,4312668.982,503904.1062,4308823.177,1
# GCP(x=0.0, y=0.0, z=0.0, pixel=0.0, line=0.0, info, id)
lines = [l for l in lines if re.search('^\d.*', l)]
gcps = []
gcpsRot = []

for i, line in enumerate(lines):
    line = re.split('[,;]', line)
    lines = [l.strip() for l in lines]

    if False:
        #mapX,mapY,pixelX,pixelY,enable
        #mapX, mapY, mapZ, pixelXrot, pixelYrot = [float(n) if n != '' else 0
        #                                    for n in line]

        mapX, mapY, pixelXrot, pixelYrot, enable = [float(n) if n != '' else 0
                                                  for n in line]
        mapZ = 0
        gcpID = 'id{}'.format(i)
        if enable != 1:
            continue
    if True:
        #FID, POINT_ID, X_IM, Y_IM, X_UTM, Y_UTM, X_SHIFT_PX, Y_SHIFT_PX, X_SHIFT_M, Y_SHIFT_M, ABS_SHIFT, ANGLE,, , , , , , , , , , , , , ,
        FID, POINT_ID, X_IM, Y_IM, X_UTM, Y_UTM, X_SHIFT_PX, Y_SHIFT_PX, X_SHIFT_M, Y_SHIFT_M, ABS_SHIFT, ANGLE = [float(n) for n in line if n != '']
        mapX, mapY, mapZ = X_UTM, Y_UTM, 0
        pixelXrot, pixelYrot = X_IM, Y_IM

        mapX, mapY, mapZ = X_UTM + X_SHIFT_M, Y_UTM + Y_SHIFT_M, 0
        #pixelXrot, pixelYrot = X_IM + X_SHIFT_PX, Y_IM + Y_SHIFT_PX
        gcpID = 'id{}'.format(POINT_ID)


    #pixelXrot -= xshift
    #pixelYrot -= yshift
    gcpsRot.append(gdal.GCP(mapX, mapY, mapZ,
                   pixelXrot, pixelYrot,
                   str('info'), str(gcpID)))

    pxOrig = S * px(pixelXrot, pixelYrot)
    pixelX = float(pxOrig[0,0])
    pixelY = float(pxOrig[1,0]) * -1

    #pixelX -= xshift
    #pixelY -= yshift

    gcp = gdal.GCP(mapX, mapY, mapZ,
                   pixelX, pixelY,
                   #X_IM, Y_IM,
                   str('info'), str(gcpID))
    gcps.append(gcp)




#3. Create the empty target dataset dsDst
