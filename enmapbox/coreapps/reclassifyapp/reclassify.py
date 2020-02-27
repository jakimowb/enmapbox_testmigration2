# -*- coding: utf-8 -*-

"""
***************************************************************************
    reclassify.py

    Algorithms to reclassify raster classification images
    ---------------------
    Date                 : Juli 2017
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

import os, re
from osgeo import gdal
from enmapbox.gui import ClassificationScheme
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QSize
import numpy as np
import hubflow.core

from enmapbox.gui.utils import gdalDataset as getDataset

def setClassInfo(targetDataset, classificationScheme, bandIndex=0):
    assert isinstance(classificationScheme, ClassificationScheme)

    classNames = classificationScheme.classNames()
    ct = gdal.ColorTable()
    assert isinstance(ct, gdal.ColorTable)
    for i, color in enumerate(classificationScheme.classColors()):
        assert isinstance(color, QColor)
        ct.SetColorEntry(color.toRgb())

    if isinstance(targetDataset, gdal.Dataset):
        ds = targetDataset
    else:
        ds = gdal.Open(targetDataset, gdal.GA_Update)

    assert isinstance(ds, gdal.Dataset)
    assert bandIndex >= 0 and ds.RasterCount > bandIndex
    band = ds.GetRasterBand(bandIndex+2)
    assert isinstance(band, gdal.Band)
    band.SetCategoryNames(classNames)
    band.SetColorTable(ct)


def reclassify(pathSrc:str, pathDst:str, dstClassScheme:ClassificationScheme, labelLookup:dict,
               drvDst = None,
               bandIndices=0, tileSize=None, co=None):
    """
    Internal wrapper to reclassify raster images based on hub-flow API.
    :param pathSrc: str, path of source image
    :param pathDst: str, path of destination image
    :param dstClassScheme: ClassificationScheme
    :param labelLookup: dict() as lookup table
    :param drvDst: gdal.Driver with driver of output image
    :param bandIndices: - not used -
    :param tileSize: - not used -
    :param co: - not used -
    :return: gdal.Dataset of written re-classified image
    """
    #assert os.path.isfile(pathSrc)
    assert isinstance(dstClassScheme, ClassificationScheme)
    assert isinstance(labelLookup, dict)


    import hubflow.core
    classification = hubflow.core.Classification(pathSrc)

    names = dstClassScheme.classNames()
    colors = dstClassScheme.classColors()

    if len(names) == 0:
        # nothing to reclassify
        return None

    # hubflow requires to handel the `unclassified` class (label = 0, always first position) separately
    newDef = hubflow.core.ClassDefinition(names=names[1:], colors=[c.name() for c in colors[1:]])
    newDef.setNoDataNameAndColor(names[0], colors[0])


    classification.reclassify(filename=pathDst,
                          classDefinition=newDef,
                          mapping=labelLookup)
    return gdal.Open(pathDst)


def guessRasterDriver(path:str)->hubflow.core.RasterDriver:
    """
    Converts a file path into the corresponding a raster driver
    :param path: str, file path
    :return: hubflow.core.RasterDriver, ENVIBSQDriver by default.
    """
    assert isinstance(path, str)

    if re.search(r'\.(bsq|bil|bip)$', path, re.I):
        return hubflow.core.EnviDriver
    elif re.search(r'\.g?tiff?$', path, re.I):
        return hubflow.core.GTiffDriver()
    elif re.search(r'\.vrt$', path,  re.I):
        return hubflow.core.VrtDriver()
    elif re.search(r'\.(img|hfa)', path , re.I):
        return hubflow.core.ErdasDriver()
    return hubflow.core.EnviDriver()


def depr_reclassify(pathSrc, pathDst, labelLookup,
               drvDst = None,
               dstClassScheme = None,
               bandIndices=0, tileSize=None, co=None):
    """
    Reclassifies the class labels of the source dataset (pathSrc)
    :param pathSrc: path or gdal.Dataset of source data
    :param pathDst: path to destination gdal.Dataset
    :param drvDst: gdal.Driver of destination dataset. Default = driver of source dataset
    :param labelLookup: dict() of structure {sourceLabelValue:destinationLabelValue}
    :param dstClassScheme: the (entire) ClassificationScheme of the destination file.
        Default = class labels from 0 to max(labelLookup.values()) with
        class names 'unclassified', 'Class 1', ... , 'Class n') and
        class colors 'black', <random colors>'

    :param bandIndices: raster band indices (zero-based) that are to be reclassified
    :param tileSize: internal tile size that is used to reclassify larger images
    :param co: drvDst specific creating options.
    :return: the created gdal.Dataset
    """
    dsSrc = getDataset(pathSrc)
    assert isinstance(labelLookup, dict)

    if not isinstance(drvDst, gdal.Driver):
        drvDst = dsSrc.GetDriver()

    if bandIndices is None:
        bandIndices = [0]
    elif not isinstance(bandIndices, list):
        bandIndices = [bandIndices]
    assert max(bandIndices) < dsSrc.RasterCount

    if dstClassScheme is None:
        dstClassScheme = ClassificationScheme()
        dstClassScheme.createClasses(max(labelLookup.values))

    if co is None:
        co = []
    if not isinstance(co, list):
        co = [co]

    classNames = dstClassScheme.classNames()
    classColorTable = dstClassScheme.gdalColorTable()

    if tileSize is None:
        tileSize = QSize(1000,1000)
    else:
        assert isinstance(tileSize, QSize)
        assert tileSize.width() > 0 and tileSize.height() > 0

    lmin, lmax = dstClassScheme.range()
    for labelSrc, labelDst in labelLookup.items():
        assert labelDst >= lmin and labelDst <= lmax, 'Label lookup value {} is out of classification range'.format(labelDst)

    eType = dsSrc.GetRasterBand(1).DataType
    ns, nl, nb = (dsSrc.RasterXSize, dsSrc.RasterYSize, dsSrc.RasterCount)

    dsDst = drvDst.Create(pathDst, ns, nl, nb, eType=eType, options=co)

    assert isinstance(dsDst, gdal.Dataset)
    dsDst.SetDescription(dsSrc.GetDescription())
    dsDst.SetMetadata(dsSrc.GetMetadata())
    dsDst.SetProjection(dsSrc.GetProjection())
    dsDst.SetGeoTransform(dsSrc.GetGeoTransform())

    for b in range(dsSrc.RasterCount):
        bandIn = dsSrc.GetRasterBand(b+1)
        bandOut = dsDst.GetRasterBand(b+1)
        assert isinstance(bandIn, gdal.Band)
        assert isinstance(bandOut, gdal.Band)

        #copy band metadata
        bandOut.SetMetadata(bandIn.GetMetadata())
        if bandIn.GetNoDataValue():
            bandOut.SetNoDataValue(bandIn.GetNoDataValue())

        #set class-specific information
        if b in bandIndices:
            bandOut.SetCategoryNames(classNames)
            bandOut.SetColorTable(classColorTable)
        else:
            bandOut.SetCategoryNames(bandIn.GetCategoryNames())
            bandOut.SetColorTable(bandIn.GetColorTable())

        yOff = 0
        while yOff < nl:
            win_ysize = min([tileSize.height(), nl - yOff])
            xOff = 0
            while xOff < ns:
                win_xsize = min([tileSize.width(), ns - xOff])

                data = bandIn.ReadAsArray(xoff=xOff, yoff=yOff, win_xsize=win_xsize, win_ysize=win_ysize)

                if b in bandIndices:
                    #re-classify
                    for labelSrc in np.unique(data):
                        if labelSrc in labelLookup.keys():
                            dstClass = labelLookup[labelSrc]
                        else:
                            dstClass = 0
                        data = np.where(data == labelSrc, dstClass, data)
                bandOut.WriteArray(data,xoff = xOff, yoff=yOff)
                xOff += tileSize.width()
            yOff += tileSize.height()
            bandOut.FlushCache()
        dsDst.FlushCache()
        return dsDst

