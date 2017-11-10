"""
Calculate Normalized Difference Vegetation Index (NDVI) for a Landsat 5 scene and cut the result to the German state Brandenburg.
"""

import tempfile
import os
import numpy
from hubdc.applier import Applier, ApplierOperator, ApplierInputRaster, ApplierInputVector, ApplierOutputRaster, ApplierInputRasterArchive, ApplierInputRasterGroup
from hubdc.examples.testdata import LT51940232010189KIS01, BrandenburgDistricts

# Set up input and output filenames.
applier = Applier()
applier.controls.setProjection()
path194 = applier.inputRaster.setGroup('194', value=ApplierInputRasterGroup())
row023 = path194.setGroup(key='023', value=ApplierInputRasterGroup())
row024 = path194.setGroup(key='024', value=ApplierInputRasterGroup())

# add first dataset
scene = row023.setGroup(key='LC81940232015235LGN00', value=ApplierInputRasterGroup())
scene.setRaster(key='LC81940232015235LGN00_cfmask', value=ApplierInputRaster(filename=r'C:\Work\data\gms\landsat\194\023\LC81940232015235LGN00\LC81940232015235LGN00_cfmask.img'))

# ...

# add last dataset
scene = row024.setGroup(key='LT51940242010189KIS01', value=ApplierInputRasterGroup())
scene.setRaster(key='LT51940242010189KIS01_cfmask', value=ApplierInputRaster(filename=r'C:\Work\data\gms\landsat\194\024\LT51940242010189KIS01\LT51940242010189KIS01_cfmask.img'))

applier.inputRaster.setGroup(key='landsat', value=ApplierInputRasterGroup.fromFolder(folder=r'C:\Work\data\gms\landsat',
                                                                                     extensions=['img'],
                                                                                     filter=lambda root, basename, extension: basename.endswith('cfmask')))

class Operator(ApplierOperator):
    def ufunc(operator):
        # access individual dataset
        cfmask = operator.inputRaster.getGroup(key='194').getGroup(key='023').getGroup(key='LC81940232015235LGN00').getRaster(key='LC81940232015235LGN00_cfmask')
        array = cfmask.getImageArray()

        # iterate over all datasets
        for path in operator.inputRaster.getGroups():
            for row in path.getGroups():
                for scene in row.getGroups():
                    key = scene.findRaster(endswith='cfmask')
                    cfmask = scene.getRaster(key=key)
                    array = cfmask.getImageArray()

        # flat iterate over all datasets
        for cfmask in operator.inputRaster.getFlatRasters():
            array = cfmask.getImageArray()

applier.apply(operator=Operator)
