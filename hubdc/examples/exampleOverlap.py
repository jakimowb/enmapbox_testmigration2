import tempfile
import os
from scipy.ndimage import uniform_filter

from hubdc.applier import Applier, ApplierOperator, ApplierInputRaster, ApplierOutputRaster
from hubdc.examples.testdata import LT51940232010189KIS01

applier = Applier()
applier.inputRaster.setRaster(key='image', value=ApplierInputRaster(filename=LT51940232010189KIS01.band3))
applier.outputRaster.setRaster(key='outimage', value=ApplierOutputRaster(filename=os.path.join(tempfile.gettempdir(), 'smoothed.img')))

class SmoothOperator(ApplierOperator):
    def ufunc(operator):

        # does a spatial 11x11 uniform filter.
        # Note: for a 3x3 the overlap is 1, 5x5 overlap is 2, ..., 11x11 overlap is 5, etc
        overlap = 5
        array = operator.inputRaster.getRaster(key='image').getImageArray(overlap=overlap)
        arraySmoothed = uniform_filter(array, size=11, mode='constant')
        operator.outputRaster.getRaster(key='outimage').setImageArray(array=arraySmoothed, overlap=overlap)

applier.apply(operator=SmoothOperator)
print(applier.outputRaster.getRaster(key='outimage').filename)
