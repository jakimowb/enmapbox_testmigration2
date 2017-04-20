from osgeo import gdal
from hubdc import PixelGrid, Applier, ApplierInput, ApplierOutput, ApplierOperator


def script():
    # define grid
    grid = PixelGrid(projection='EPSG:3035', xRes=100, yRes=100, xMin=4400000, xMax=4440000, yMin=3150000,
                     yMax=3200000)

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


def script2():

    # define input and output filenames and warping options
    applier = Applier(ufuncClass=NDVI, nworker=1, nwriter=1, windowxsize=256, windowysize=256)
    applier['red'] = ApplierInput(
        r'C:\Work\data\gms\landsat\194\024\LC81940242015235LGN00\LC81940242015235LGN00_sr_band4.img',
        resampleAlg=gdal.GRA_Bilinear, errorThreshold=0., bandSubset=[1,4,7,8])
    applier['nir'] = ApplierInput(
        r'C:\Work\data\gms\landsat\194\024\LC81940242015235LGN00\LC81940242015235LGN00_sr_band5.img',
        resampleAlg=gdal.GRA_Bilinear, errorThreshold=0.)

    applier['ndvi'] = ApplierOutput(r'c:\output\ndvi.tif', format='ENVI',
                                    creationOptions=[])  # , creationOptions=['COMPRESS=LZW', 'INTERLEAVE=BAND', 'TILED=YES', 'BLOCKXSIZE=256', 'BLOCKYSIZE=256', 'SPARSE_OK=TRUE', 'NUM_THREADS=ALL_CPUS', 'BIGTIFF=YES'])
    applier.run()


class NDVI(ApplierOperator):

    def ufunc1(self):

        # calculate NDVI
        from numpy import float32
        red = self.getDataset('red').getBand(bandNumber=1).readAsArray(dtype=float32)
        nir = self.getDataset('nir').getBand(bandNumber=1).readAsArray(dtype=float32)
        ndvi = (nir-red)/(nir+red)

        # create output dataset and set metadata
        ndviDS = self.setDataset('ndvi', array=ndvi)
        ndviDS.setENVIAcquisitionTime('2015-08-23')

    def ufunc(self):

        # calculate NDVI
        from numpy import float32
        red = self.getImage('red', bandIndex=0, dtype=float32)
        nir = self.getImage('nir', bandIndex=0, dtype=float32)
        ndvi = (nir-red)/(nir+red)
        self.setImage('ndvi', array=ndvi)
        self.setMetadataItem('ndvi', key='acquisition time', value='2015-08-23', domain='ENVI')

if __name__ == '__main__':
    script()


