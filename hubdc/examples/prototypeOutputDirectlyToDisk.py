from osgeo import gdal
from hubdc import PixelGrid, Applier, ApplierInput, ApplierOutput, ApplierOperator

def script():

    # use grid from input file, but enlarge the resolution to 300 meter
    grid = PixelGrid.fromFile(r'C:\Work\data\gms\LC81940242015235LGN00_sr.img')
    grid.xRes = grid.yRes = 3000
    applier = Applier(grid=grid, ufuncClass=MyOperator, nworker=1, nwriter=1, windowxsize=256, windowysize=256)
    applier['in'] = ApplierInput(filename=r'C:\Work\data\gms\LC81940242015235LGN00_sr.img', resampleAlg=gdal.GRA_NearestNeighbour, errorThreshold=0.)
    applier['out'] = ApplierOutput(filename=r'c:\output\LC81940242015235LGN00_sr.img', format='ENVI', creationOptions=['INTERLEAVE=BSQ'])
    applier.run()

class MyOperator(ApplierOperator):

    def ufunc(self):
        srLC8 = self.getData('in')
        self.setData('out', array=srLC8)

    def umeta(self):
        self.setMetadataItem('out', key='my value', value=42, domain='ENVI')

if __name__ == '__main__':
    script()
