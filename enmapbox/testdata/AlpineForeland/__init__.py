#!/usr/bin/env python
"""
This file is auto-generated.
Do not edit manually, as changes might get overwritten.
"""
__author__ = "auto-generated by make\make.py"
__date__ = "2017-02-17T11:08:59"

import sys, os

thisDir = os.path.dirname(__file__)
# File path attributes:
# Raster files:
AF_AdminBorders = os.path.join(thisDir,r'AF_AdminBorders.bip')
AF_Image = os.path.join(thisDir,r'AF_Image.bip')
AF_LAI = os.path.join(thisDir,r'AF_LAI.bsq')
AF_LAI_Training = os.path.join(thisDir,r'AF_LAI_Training.bip')
AF_LAI_Validation = os.path.join(thisDir,r'AF_LAI_Validation.bip')
AF_LC = os.path.join(thisDir,r'AF_LC.bsq')
AF_LC_Training = os.path.join(thisDir,r'AF_LC_Training.bip')
AF_LC_Validation = os.path.join(thisDir,r'AF_LC_Validation.bip')
AF_Mask = os.path.join(thisDir,r'AF_Mask.bsq')
AF_MaskVegetation = os.path.join(thisDir,r'AF_MaskVegetation.bsq')



# self-test to check each file path attribute
for a in dir(sys.modules[__name__]):
    v = getattr(sys.modules[__name__], a)
    if type(v) == str and os.path.isabs(v):
        if not os.path.exists(v):
            sys.stderr.write('Missing package attribute file: {}={}'.format(a, v))

# cleanup
del thisDir 