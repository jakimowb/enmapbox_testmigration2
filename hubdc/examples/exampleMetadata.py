"""
Reads the ENVI/wavelength metadata item from an input dataset and passes it to an output dataset.
"""

import tempfile
import os
import numpy
from hubdc.applier import Applier, ApplierOperator, ApplierInputRaster, ApplierOutputRaster
from hubdc.examples.testdata import LT51940232010189KIS01

applier = Applier()
applier.inputRaster.setRaster(key='image', value=ApplierInputRaster(filename=LT51940232010189KIS01.band3))
applier.outputRaster.setRaster(key='outimage', value=ApplierOutputRaster(filename=os.path.join(tempfile.gettempdir(), 'outimage.img')))

class CopyMetadataOperator(ApplierOperator):

    def ufunc(operator):

        # copy raster data
        array = operator.inputRaster.getRaster(key='image').getImageArray()
        operator.outputRaster.getRaster(key='outimage').setImageArray(array=array)

        # copy ENVI/wavelength metadata
        wavelength = operator.inputRaster.getRaster(key='image').getMetadataItem(key='wavelength', domain='ENVI')
        operator.outputRaster.getRaster(key='outimage').setMetadataItem(key='wavelength', value=wavelength, domain='ENVI')

applier.apply(operator=CopyMetadataOperator)
print(applier.outputRaster.getRaster(key='outimage').filename)
