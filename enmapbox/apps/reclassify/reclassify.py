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

import collections, sys, os
from osgeo import gdal
from enmapbox.gui.classificationscheme import ClassInfo, ClassificationScheme
from PyQt4.QtGui import QColor
from PyQt4.QtCore import QSize
import numpy as np

def setClassInfo(pathTarget, classificationScheme, bandIndex=0):
    assert isinstance(classificationScheme, ClassificationScheme)

    classNames = classificationScheme.classNames()
    ct = gdal.ColorTable()
    assert isinstance(ct, gdal.ColorTable)
    for i, color in enumerate(classificationScheme.classColors()):
        assert isinstance(color, QColor)
        ct.SetColorEntry(color.toRgb())

    ds = gdal.Open(pathTarget, gdal.GA_Update)
    assert isinstance(ds, gdal.Dataset)
    assert bandIndex >= 0 and ds.RasterCount > bandIndex
    band = ds.GetRasterBand(bandIndex+2)
    assert isinstance(band, gdal.Band)
    band.SetCategoryNames(classNames)
    band.SetColorTable(ct)


def reclassify(pathSrc, pathDst, labelLookup, bandIndex=0, tileSize=None, co=None):

    assert os.path.isfile(pathSrc)
    dsIn = gdal.Open(pathSrc)
    assert isinstance(dsIn, gdal.Dataset)
    assert isinstance(labelLookup, dict)

    classNames = "todo"
    classColorTable = "todo"

    if tileSize is None:
        tileSize = QSize(1000,1000)
    else:
        assert isinstance(tileSize, QSize)
        assert tileSize.width() > 0 and tileSize.height() > 0

    assert bandIndex > 0
    for classInfo in labelLookup.values():
        assert isinstance(classInfo, ClassInfo)

    eType = dsIn.GetRasterBand(1).DataType
    ns, nl, nb = (dsIn.RasterXSize, dsIn.RasterYSize, dsIn.RasterCount)

    dsOut = dsIn.GetDriver().Create(pathDst, ns, nl, nb, eType=eType, options=co)

    assert isinstance(dsOut, gdal.Dataset)

    dsOut.SetProjection(dsIn.GetProjection())
    dsOut.SetGeoTransform(dsIn.GetGeoTransform())

    for b in range(nb):
        bandIn = dsIn.GetRasterBand(b+1)
        bandOut = dsOut.GetRasterBand(b+1)
        assert isinstance(bandIn, gdal.Band)
        assert isinstance(bandOut, gdal.Band)
        bandOut.SetMetadata(bandIn.GetMetadata())
        if b == bandIndex:
            bandOut.SetCategoryNames(classNames)
            bandOut.SetColorTable(classColorTable)
        else:
            bandOut.SetCategoryNames(bandIn.GetCategoryNames())
            bandOut.SetColorTable(bandIn.GetColorTable())
        yOff = 0
        uniques = set()
        while yOff < nl:
            win_ysize = min([tileSize.height(), nl - yOff])
            xOff = 0
            while xOff < ns:
                win_xsize = min([tileSize.width(), ns - xOff])

                data = bandIn.ReadAsArray(xoff=xOff, yoff=yOff, win_xsize=win_xsize, win_ysize=win_ysize)
                if b == bandIndex:
                    mask = np.zeros(data.shape)
                    for labelSrc in np.unique(data):
                        dstClass = labelLookup[labelSrc]
                        assert isinstance(dstClass, ClassInfo)
                        dstClass.mLabel

                bandOut.WriteArray(data,xoff = xOff, yoff=yOff)
                xOff += tileSize.width()
            yOff += tileSize.height()
            bandOut.FlushCache()
        dsOut.FlushCache()


def reclassify(pathSrc, pathDst):
    pass