# -*- coding: utf-8 -*-

"""
***************************************************************************
    __init__
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
import os.path
j = lambda f:os.path.join(os.path.dirname(__file__), f)
EnMAP = j('EnMAP02_Berlin_Urban_Gradient_2009_testData_compressed.bsq')
VHR = j('HighResolution_Berlin_Urban_Gradient_2009_testData_compressed.bsq')
LandCover = j('LandCov_Vec_Berlin_Urban_Gradient_2009_subset.shp')
Speclib = j('SpecLib_Berlin_Urban_Gradient_2009_244bands.sli')

