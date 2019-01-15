# -*- coding: utf-8 -*-

"""
***************************************************************************
    enmapbox/gui/utils.py
    ---------------------
    Date                 : August 2017
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

import os, sys, importlib, re, fnmatch, io, zipfile, warnings

from qgis.core import *
from qgis.core import QgsFeature, QgsPointXY, QgsRectangle
from qgis.gui import *
from qgis.gui import QgisInterface, QgsDockWidget, QgsPluginManagerInterface
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtCore import QMimeData
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtXml import *
from qgis.PyQt.QtXml import QDomDocument
from qgis.PyQt import uic
from osgeo import gdal
import numpy as np

from enmapbox import messageLog, DIR_REPO, DIR_UIFILES


from qps.utils import *
from enmapbox import DIR_UIFILES
UI_DIRECTORIES.append(DIR_UIFILES)

def guessDataProvider(src:str)->str:
    """
    Get an uri and guesses the QgsDataProvider for
    :param uri: str
    :return: str, provider key like 'gdal', 'ogr' or None
    """
    if re.search(r'\.(bsq|tiff?|jp2|jp2000|j2k|png)', src, re.I):
        return 'gdal'
    elif re.search(r'\.(sli|esl)$', src, re.I):  # probably a spectral library
        return 'enmapbox_speclib'
    elif re.search(r'\.(shp|gpkg|kml)$', src, re.I):  # probably a vector file
        return 'ogr'
    elif re.search(r'\.(txt|csv)$', src, re.I):  # probably normal text file
        return 'enmapbox_textfile'
    elif re.search(r'\.pkl$', src, re.I):
        return 'enmapbox_pkl'
    elif re.search(r'url=https?.*wfs', src, re.I):
        return 'WFS'
    return None







class IconProvider:
    """
    Provides icons
    """
    EnMAP_Logo = ':/enmapbox/icons/enmapbox.svg'
    Map_Link_Remove = ':/enmapbox/icons/link_open.svg'
    Map_Link = ':/enmapbox/icons/link_basic.svg'
    Map_Link_Center = ':/enmapbox/icons/link_center.svg'
    Map_Link_Extent = ':/enmapbox/icons/link_mapextent.svg'
    Map_Link_Scale = ':/enmapbox/icons/link_mapscale.svg'
    Map_Link_Scale_Center = ':/enmapbox/icons/link_mapscale_center.svg'
    Map_Zoom_In = ':/enmapbox/icons/mActionZoomOut.svg'
    Map_Zoom_Out = ':/enmapbox/icons/mActionZoomIn.svg'
    Map_Pan = ':/enmapbox/icons/mActionPan.svg'
    Map_Touch = ':/enmapbox/icons/mActionTouch.svg'
    File_RasterMask = ':/enmapbox/icons/filelist_mask.svg'
    File_RasterRegression = ':/enmapbox/icons/filelist_regression.svg'
    File_RasterClassification = ':/enmapbox/icons/filelist_classification.svg'
    File_Raster = ':/enmapbox/icons/filelist_image.svg'
    File_Vector_Point = ':/enmapbox/icons/mIconPointLayer.svg'
    File_Vector_Line = ':/enmapbox/icons/mIconLineLayer.svg'
    File_Vector_Polygon = ':/enmapbox/icons/mIconPolygonLayer.svg'

    Dock = ':/enmapbox/icons/viewlist_dock.svg'
    MapDock = ':/enmapbox/icons/viewlist_mapdock.svg'
    SpectralDock = ':/enmapbox/icons/viewlist_spectrumdock.svg'

    @staticmethod
    def resourceIconsPaths():
        import inspect
        return inspect.getmembers(IconProvider, lambda a: not (inspect.isroutine(a)) and a.startswith(':'))

    @staticmethod
    def icon(path):
        if path is None:
            path = IconProvider.EnMAP_Logo

        assert isinstance(path, str)
        icon = None
        if path in IconProvider.resourceIconsPaths():
            icon = QIcon(path)
        else:
            provider = QFileIconProvider()
            icon = provider.icon(QFileInfo(path))

        return icon

    @staticmethod
    def test():
        required = set(['png', 'svg'])
        available = set([p for p in QImageReader.supportedImageFormats()])
        missing = required - available

        for name, uri in IconProvider.resourceIconsPaths():
            icon = QIcon(uri)
            w = h = 16
            s = icon.actualSize(QSize(w, h))

