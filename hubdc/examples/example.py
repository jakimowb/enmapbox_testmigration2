"""
Calculate Normalized Difference Vegetation Index (NDVI) for a Landsat 5 scene and cut the result to the German state Brandenburg.
"""

import tempfile
import os
import numpy
from hubdc.applier import Applier, ApplierOperator, ApplierInputRaster, ApplierInputVector, ApplierOutputRaster
from hubdc.testdata import LT51940232010189KIS01, BrandenburgDistricts

# Set up input and output filenames.
applier = Applier()
applier.inputRaster.setRaster(key='red', value=ApplierInputRaster(filename=LT51940232010189KIS01.red))
applier.inputRaster.setRaster(key='nir', value=ApplierInputRaster(filename=LT51940232010189KIS01.nir))
applier.inputVector.setVector(key='brandenburg', value=ApplierInputVector(filename=BrandenburgDistricts.shp))
applier.outputRaster.setRaster(key='ndvi', value=ApplierOutputRaster(filename=os.path.join(tempfile.gettempdir(), 'ndvi.img')))

# Set up the operator to be applied
class NDVIOperator(ApplierOperator):
    def ufunc(operator):

        # read image data
        red = operator.inputRaster.getRaster(key='red').getImageArray()
        nir = operator.inputRaster.getRaster(key='nir').getImageArray()
        brandenburg = operator.inputVector.getVector(key='brandenburg').getImageArray(initValue=0, burnValue=1)

        # calculate ndvi and mask Brandenburg
        ndvi = numpy.float32(nir-red)/(nir+red)
        ndvi[brandenburg==0] = -1

        # write ndvi data
        operator.outputRaster.getRaster(key='ndvi').setImageArray(array=ndvi)

# Apply the operator to the inputs, creating the outputs.
applier.apply(operator=NDVIOperator)
print(applier.outputRaster.getRaster(key='ndvi').filename)
