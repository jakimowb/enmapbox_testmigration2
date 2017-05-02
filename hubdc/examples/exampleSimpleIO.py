from osgeo import gdal
from hubdc import PixelGrid, Applier, ApplierInput, ApplierOutput, ApplierOperator

def script():

    grid = PixelGrid(projection='EPSG:3035', xRes=100, yRes=100, xMin=4400000, xMax=4440000, yMin=3150000, yMax=3200000)
    applier = Applier(grid=grid, ufuncClass=SimpleIO, nworker=1, nwriter=1, windowxsize=256, windowysize=256)
    applier['in'] = ApplierInput(filename=r'C:\Work\data\gms\landsat\194\024\LC81940242015235LGN00\LC81940242015235LGN00_cfmask.img')
    applier['out'] = ApplierOutput(r'c:\output\out.tif', format='GTiff')
    applier.run()

class SimpleIO(ApplierOperator):

    def ufunc(self):
        self.setData('out', array=self.getData('in'))

    def umeta(self, *args, **kwargs):
        self.setMetadataItem('out', 'my value', 42, 'ENVI')

if __name__ == '__main__':
    script()
