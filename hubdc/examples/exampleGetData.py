from osgeo import gdal
from hubdc import PixelGrid, Applier, ApplierInput, ApplierOutput, ApplierOperator

def script():

    # use grid from input file, but enlarge the resolution to 300 meter
    grid = PixelGrid.fromFile(r'C:\Work\data\gms\LC81940242015235LGN00_sr.img')
    grid.xRes = grid.yRes = 3000
    applier = Applier(grid=grid, ufuncClass=MyOperator, nworker=1, nwriter=1, windowxsize=256, windowysize=256)
    applier['LC8'] = ApplierInput(filename=r'C:\Work\data\gms\LC81940242015235LGN00_sr.img',
                                     resampleAlg=gdal.GRA_Average,
                                     errorThreshold=0.)
    applier['LC8_LC8'] = ApplierInput(filename=[r'C:\Work\data\gms\LC81940242015235LGN00_sr.img',
                                                r'C:\Work\data\gms\LC81940242015235LGN00_sr.img'],
                                      resampleAlg=gdal.GRA_Average,
                                      errorThreshold=0.)

    applier['LC8_LE7'] = ApplierInput(filename=[r'C:\Work\data\gms\LC81940242015235LGN00_sr.img',
                                                r'C:\Work\data\gms\LE71940242015275NSG00_sr.img'],
                                      resampleAlg=gdal.GRA_Average,
                                      errorThreshold=0.)

    applier['ndvi'] = ApplierOutput(r'c:\output\ndvi.tif', format='ENVI', creationOptions=['INTERLEAVE=BSQ'])

    applier.run()

class MyOperator(ApplierOperator):

    def ufunc(self):
        from numpy import float32
        #srLC8, srLE7 = self.getData('LC8_LE7', dtype=float32)

        #rgbLC8, rgbLE7 = self.getData('LC8_LE7', [[1, 2, 3], [2, 3, 4]], dtype=float32)
        #rgbLC8a, rgbLC8b = self.getData('LC8_LC8', [[1, 2, 3],[1, 2, 3]], dtype=float32)
        #rgbLC8a, rgbLC8b = self.getData('LC8_LC8', [1, 2, 3], dtype=float32)

        #blueLC8a, blueLC8b = self.getData('LC8_LC8', 1, dtype=float32)
        #blueLC8a, blueLC8b = self.getData('LC8_LC8', [1], dtype=float32)
        #blueLC8a, blueLC8b = self.getData('LC8_LC8', [[1], [1]], dtype=float32)

        # generator style
        rednir = self.getArray('LC8_LE7', [[3, 4], [2, 3]], dtype=float32, generator=True)
        ndvi = ((nir-red)/(nir+red) for red, nir in rednir)

        # test metadata
        self.setData('ndvi', array=ndvi)
        self.setMetadataItem('ndvi', 'my string', 'Hello World', 'ENVI')
        self.setMetadataItem('ndvi', 'my number', 42, 'ENVI')
        self.setMetadataItem('ndvi', 'my int list', [1,2,3,4,5], 'ENVI')

if __name__ == '__main__':
    script()
