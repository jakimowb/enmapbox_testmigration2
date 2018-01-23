from hubdc.applier import PixelGrid, Applier
from hubdc.applier import ApplierOperator

def script():

    #filename = r'H:\EuropeanDataCube\landsat\194\024\LC81940242015235LGN00\LC81940242015235LGN00_sr_band1.img'
    filename = r'C:\Work\data\gms\landsat\194\024\LC81940242015235LGN00\LC81940242015235LGN00_cfmask.img'

    applier = Applier()
    #applier.controls.setWindowFullSize()
    applier.setInput('in', filename=filename)
    applier.setOutputRaster('out', filename=r'c:\output\out.tif', format='ENVI')
    applier.apply(operator=SimpleIO)

class SimpleIO(ApplierOperator):

    def ufunc(self):
        array = self.getArray('in', overlap=10)
        self.setArray('out', array=array, overlap=10)

if __name__ == '__main__':
    script()
