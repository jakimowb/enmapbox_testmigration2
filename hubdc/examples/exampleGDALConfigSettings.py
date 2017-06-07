from hubdc import PixelGrid, Applier, ApplierOperator
import hubdc.applier.Applier

def script():

    #filename = r'H:\EuropeanDataCube\landsat\194\024\LC81940242015235LGN00\LC81940242015235LGN00_sr_band1.img'
    filename = r'C:\Work\data\gms\LC81940242015235LGN00_sr_band1.img'

    hubdc.applier.Applier.DEFAULT_GDAL_CACHEMAX = 5000 * 2**20
    hubdc.applier.Applier.DEFAULT_GDAL_SWATH_SIZE = 5000 * 2 ** 20
    hubdc.applier.Applier.DEFAULT_GDAL_DISABLE_READDIR_ON_OPEN = True
    hubdc.applier.Applier.DEFAULT_GDAL_MAX_DATASET_POOL_SIZE = 1000

    grid = PixelGrid(projection='EPSG:3035', xRes=100, yRes=100, xMin=4400000, xMax=4440000, yMin=3150000, yMax=3200000)
    applier = Applier(grid=grid, nworker=0, nwriter=1, windowxsize=256, windowysize=256)
    applier.setInput('in', filename=filename)
    applier.setOutput('out', filename=r'c:\output\out.tif', format='ENVI')
    applier.run(ufuncClass=SimpleIO)

class SimpleIO(ApplierOperator):

    def ufunc(self):
        self.setData('out', array=self.getArray('in'))

if __name__ == '__main__':
    script()
