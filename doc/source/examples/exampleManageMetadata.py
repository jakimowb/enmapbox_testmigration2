from hubdc.applier import *
from hubdc.testdata import LT51940232010189KIS01
import enmapboxtestdata

applier = Applier()
applier.inputRaster.setRaster(key='in', value=ApplierInputRaster(filename=enmapboxtestdata.enmap))
applier.outputRaster.setRaster(key='out', value=ApplierOutputRaster(filename='/vsimem/out.bsq'))

class Operator(ApplierOperator):
    def ufunc(self):
        '''
        >>> 2
        2
        '''

        # copy raster data
        array = self.inputRaster.raster(key='in').array()
        self.outputRaster.raster(key='out').setArray(array=array)

        # copy ENVI/wavelength metadata
        wavelength = self.inputRaster.raster(key='in').metadataItem(key='wavelength', domain='ENVI')
        self.outputRaster.raster(key='out').setMetadataItem(key='wavelength', value=wavelength, domain='ENVI')

applier.apply(operatorType=Operator)
