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

from ..externals.qps.utils import *

def enmapboxUiPath(name:str)->pathlib.Path:
    """
    Translate a base name `name` into the absolute path of an ui-file
    :param name: str
    :type name: pathlib.Path
    :return:
    :rtype:
    """
    from enmapbox import DIR_UIFILES
    path = pathlib.Path(DIR_UIFILES) / name
    assert path.is_file()
    return path


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

