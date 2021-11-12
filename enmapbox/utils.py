# -*- coding: utf-8 -*-

"""
***************************************************************************
    enmapbox/utils.py
    This module provides a unified access and shortcuts to frequently used
    helping functions in managing raster and vector data and other
    EnMAP-Box components.
    ---------------------
    Date                 : November 2021
    Copyright            : (C) 2021 by Benjamin Jakimow
    Email                : benjamin.jakimow@geo.hu-berlin.de
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
**************************************************************************
"""
import typing

from qgis.core import QgsRasterLayer

from enmapbox.gui.utils import loadUi
from enmapbox.gui.utils import file_search


def bandNumber(raster: typing.Union[str, QgsRasterLayer], wavelength_region: str, strict: bool = False) -> int:
    # todo: link-in functionality
    pass
    """
    :param raster: raster image 
    :param wavelength_region: a string that specifies the wavelength regions, e.g. 'R', 'G', 'B' for Red, Green or Blue
    :param strict: if True, returns a band only if a band was found whose spectral response intersects 
                            with wavelength_region.
                   if False, returns the band closest to the wavelength region
                 
    :return: int band number (1st band = 1) to be used e.g. in QgsRasterLayer
    """
