"""
Calculate the Normalized Difference Vegetation Index (NDVI) for a Landsat 5 scene.
Mask the resulting image to the shape of Brandenburg (a federated state of Germany).
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
        red = operator.inputRaster.raster(key='red').imageArray()
        nir = operator.inputRaster.raster(key='nir').imageArray()
        brandenburg = operator.inputVector.vector(key='brandenburg').imageArray(initValue=0, burnValue=1)

        # calculate ndvi and mask Brandenburg
        ndvi = numpy.float32(nir-red)/(nir+red)
        ndvi[brandenburg==0] = -1

        # write ndvi data
        operator.outputRaster.raster(key='ndvi').setImageArray(array=ndvi)

# Apply the operator to the inputs, creating the outputs.
applier.apply(operatorType=NDVIOperator)
print(applier.outputRaster.raster(key='ndvi').filename)

# Python prints something like:
# >>> c:\users\USER\appdata\local\temp\ndvi.img