"""
Calculate the Normalized Difference Vegetation Index (NDVI) for a Landsat 5 scene.
Mask the resulting image to the shape of Brandenburg (a federated state of Germany).
"""

import tempfile
import os
import numpy
from hubdc.applier import *
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
        red = operator.inputRaster.raster(key='red').array()
        nir = operator.inputRaster.raster(key='nir').array()
        brandenburg = operator.inputVector.vector(key='brandenburg').array(initValue=0, burnValue=1)

        # calculate ndvi, clip to 0-1 and mask Brandenburg
        ndvi = numpy.float32(nir-red)/(nir+red)
        np.clip(ndvi, 0, 1, out=ndvi)
        ndvi[brandenburg==0] = 0

        # write ndvi data
        operator.outputRaster.raster(key='ndvi').setArray(array=ndvi)
        operator.outputRaster.raster(key='ndvi').setNoDataValue(0)

# Apply the operator to the inputs, creating the outputs.
applier.apply(operatorType=NDVIOperator)
print(applier.outputRaster.raster(key='ndvi').filename())

# Python prints something like:
# >>> c:\users\USER\appdata\local\temp\ndvi.img