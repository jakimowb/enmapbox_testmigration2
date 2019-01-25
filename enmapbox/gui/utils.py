# -*- coding: utf-8 -*-

"""
***************************************************************************
    enmapbox/gui/utils.py

    ---------------------
    Date                 : January 2019
    Copyright            : (C) 2018 by Benjamin Jakimow
    Email                : benjamin.jakimow@geo.hu-berlin.de
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 3 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

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
    EnMAP_Logo = ':/enmapbox/gui/ui/icons/enmapbox.svg'
    Map_Link_Remove = ':/enmapbox/gui/ui/icons/link_open.svg'
    Map_Link = ':/enmapbox/gui/ui/icons/link_basic.svg'
    Map_Link_Center = ':/enmapbox/gui/ui/icons/link_center.svg'
    Map_Link_Extent = ':/enmapbox/gui/ui/icons/link_mapextent.svg'
    Map_Link_Scale = ':/enmapbox/gui/ui/icons/link_mapscale.svg'
    Map_Link_Scale_Center = ':/enmapbox/gui/ui/icons/link_mapscale_center.svg'
    Map_Zoom_In = ':/enmapbox/gui/ui/icons/mActionZoomOut.svg'
    Map_Zoom_Out = ':/enmapbox/gui/ui/icons/mActionZoomIn.svg'
    Map_Pan = ':/enmapbox/gui/ui/icons/mActionPan.svg'
    Map_Touch = ':/enmapbox/gui/ui/icons/mActionTouch.svg'
    File_RasterMask = ':/enmapbox/gui/ui/icons/filelist_mask.svg'
    File_RasterRegression = ':/enmapbox/gui/ui/icons/filelist_regression.svg'
    File_RasterClassification = ':/enmapbox/gui/ui/icons/filelist_classification.svg'
    File_Raster = ':/enmapbox/gui/ui/icons/filelist_image.svg'
    File_Vector_Point = ':/enmapbox/gui/ui/icons/mIconPointLayer.svg'
    File_Vector_Line = ':/enmapbox/gui/ui/icons/mIconLineLayer.svg'
    File_Vector_Polygon = ':/enmapbox/gui/ui/icons/mIconPolygonLayer.svg'

    Dock = ':/enmapbox/gui/ui/icons/viewlist_dock.svg'
    MapDock = ':/enmapbox/gui/ui/icons/viewlist_mapdock.svg'
    SpectralDock = ':/enmapbox/gui/ui/icons/viewlist_spectrumdock.svg'

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

