from osgeo import gdal
from hubdc import PixelGrid, Applier, ApplierInput, ApplierOutput, ApplierOperator

def script():

    # use grid from input file, but enlarge the resolution to 300 meter
    grid = PixelGrid(projection='EPSG:3035', xRes=100, yRes=100, xMin=4400000, xMax=4440000, yMin=3150000, yMax=3200000)

    # init _applier
    applier = Applier(grid=grid, ufuncClass=NDVI, nworker=1, nwriter=1, windowxsize=256, windowysize=256)

    # add inputs: Landsat red and nir images
    redFilenames = [r'C:\Work\data\gms\landsat\194\024\LC81940242015235LGN00\LC81940242015235LGN00_sr_band4.img',
                    r'C:\Work\data\gms\landsat\194\024\LE71940242015275NSG00\LE71940242015275NSG00_sr_band3.img',
                    r'C:\Work\data\gms\landsat\194\024\LT51940242010189KIS01\LT51940242010189KIS01_sr_band3.img']
    nirFilenames = [r'C:\Work\data\gms\landsat\194\024\LC81940242015235LGN00\LC81940242015235LGN00_sr_band5.img',
                    r'C:\Work\data\gms\landsat\194\024\LE71940242015275NSG00\LE71940242015275NSG00_sr_band4.img',
                    r'C:\Work\data\gms\landsat\194\024\LT51940242010189KIS01\LT51940242010189KIS01_sr_band4.img']

    applier['red'] = ApplierInput(filename=redFilenames, resampleAlg=gdal.GRA_Average, errorThreshold=0.)
    applier['nir'] = ApplierInput(filename=nirFilenames, resampleAlg=gdal.GRA_Average, errorThreshold=0.)

    # add output
    applier['ndvi'] = ApplierOutput(r'c:\output\ndvi.tif', format='ENVI', creationOptions=['INTERLEAVE=BSQ'])

    # run
    applier.run()


class NDVI(ApplierOperator):

    def ufunc(self):
        from numpy import float32
        red = self.getImageList('red', dtype=float32)
        nir = self._getImage('nir', dtype=float32)
        ndvi = (nir-red)/(nir+red)
        self.setImage('ndvi', array=ndvi)

if __name__ == '__main__':
    script()
