from osgeo import gdal
from hubdc import PixelGrid, Applier, ApplierInput, ApplierOutput, ApplierOperator

def script2():

    # define grid
    grid = PixelGrid(projection='EPSG:3035', xRes=100, yRes=100, xMin=4400000, xMax=4440000, yMin=3150000, yMax=3200000)

    # define input and output filenames and warping options
    applier = Applier(grid=grid, ufuncClass=NDVI, nworker=1, nwriter=1, windowxsize=256, windowysize=256)
    applier['red'] = ApplierInput(
        r'C:\Work\data\gms\landsat\194\024\LC81940242015235LGN00\LC81940242015235LGN00_sr_band4.img',
        resampleAlg=gdal.GRA_Bilinear, errorThreshold=0.)
    applier['nir'] = ApplierInput(
        r'C:\Work\data\gms\landsat\194\024\LC81940242015235LGN00\LC81940242015235LGN00_sr_band5.img',
        resampleAlg=gdal.GRA_Bilinear, errorThreshold=0.)

    applier['ndvi'] = ApplierOutput(r'c:\output\ndvi.tif', format='ENVI',
                                    creationOptions=[])  # , creationOptions=['COMPRESS=LZW', 'INTERLEAVE=BAND', 'TILED=YES', 'BLOCKXSIZE=256', 'BLOCKYSIZE=256', 'SPARSE_OK=TRUE', 'NUM_THREADS=ALL_CPUS', 'BIGTIFF=YES'])
    applier.run()


def script():

    # use grid from input file, but enlarge the resolution to 300 meter
    grid = PixelGrid.fromFile(r'C:\Work\data\gms\LC81940242015235LGN00_sr.img')
    grid.xRes = grid.yRes = 300

    # init _applier
    applier = Applier(grid=grid, ufuncClass=NDVI, nworker=1, nwriter=1, windowxsize=256, windowysize=256)

    # add input: Landsat 8 SR Stack
    applier['LC8_sr'] = ApplierInput(filename=r'C:\Work\data\gms\LC81940242015235LGN00_sr.img',
                                     resampleAlg=gdal.GRA_Average,
                                     errorThreshold=0.)

    # add output
    applier['ndvi'] = ApplierOutput(r'c:\output\ndvi.tif', format='ENVI', creationOptions=['INTERLEAVE=BSQ'])

    # run
    applier.run()


class NDVI(ApplierOperator):

    def ufunc(self):
        from numpy import float32
        red, nir = self._getImage('LC8_sr', [3, 4], dtype=float32)
        ndvi = (nir-red)/(nir+red)
        self.setImage('ndvi', array=ndvi)
        self.setMetadataItem('ndvi', key='acquisition time', value='2015-08-23', domain='ENVI')

if __name__ == '__main__':
    script()
