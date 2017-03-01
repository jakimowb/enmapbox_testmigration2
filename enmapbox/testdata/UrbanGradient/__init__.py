#!/usr/bin/env python
"""
This file is auto-generated.
Do not edit manually, as changes might get overwritten.
"""
__author__ = "auto-generated by make\make.py"
__date__ = "2017-02-28T13:25:19"

import sys, os

thisDir = os.path.dirname(__file__)
# File path attributes:
# Raster files:
EnMAP01_Berlin_Urban_Gradient_2009_bsq = os.path.join(thisDir,r'EnMAP01_Berlin_Urban_Gradient_2009.bsq')
EnMAP02_Berlin_Urban_Gradient_2009_bsq = os.path.join(thisDir,r'EnMAP02_Berlin_Urban_Gradient_2009.bsq')
HyMap01_Berlin_Urban_Gradient_2009_bsq = os.path.join(thisDir,r'HyMap01_Berlin_Urban_Gradient_2009.bsq')
HyMap02_Berlin_Urban_Gradient_2009_bsq = os.path.join(thisDir,r'HyMap02_Berlin_Urban_Gradient_2009.bsq')
LandCov_Class_Berlin_Urban_Gradient_2009_bsq = os.path.join(thisDir,r'LandCov_Class_Berlin_Urban_Gradient_2009.bsq')
LandCov_Layer_Level1_Berlin_Urban_Gradient_2009_bsq = os.path.join(thisDir,r'LandCov_Layer_Level1_Berlin_Urban_Gradient_2009.bsq')
LandCov_Layer_Level2_Berlin_Urban_Gradient_2009_bsq = os.path.join(thisDir,r'LandCov_Layer_Level2_Berlin_Urban_Gradient_2009.bsq')


# Vector files:
LandCov_Vec_Berlin_Urban_Gradient_2009_shp = os.path.join(thisDir,r'LandCov_Vec_Berlin_Urban_Gradient_2009.shp')
LandCov_Vec_polygons_Berlin_Urban_Gradient_2009_shp = os.path.join(thisDir,r'LandCov_Vec_polygons_Berlin_Urban_Gradient_2009.shp')



# self-test to check each file path attribute
for a in dir(sys.modules[__name__]):
    v = getattr(sys.modules[__name__], a)
    if type(v) == str and os.path.isabs(v):
        if not os.path.exists(v):
            sys.stderr.write('Missing package attribute file: {}={}'.format(a, v))

# cleanup
del thisDir 